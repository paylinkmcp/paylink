import logging
import os
import click
import contextlib
import contextvars
import uvicorn
from typing import Any
from collections.abc import AsyncIterator

from dotenv import load_dotenv
from starlette.types import Receive, Scope, Send
from starlette.applications import Starlette
from starlette.routing import Route, Mount

from mcp.server.lowlevel import Server
from mcp.types import TextContent, Tool
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.server.sse import SseServerTransport

from src.tools.tool import get_mpesa_tools
from src.handlers.stk_push import stk_push_handler

from paylink_tracer import paylink_tracer,set_trace_context_provider


load_dotenv()

# ------------------------------------------------------------------------------
# Config & globals
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
MPESA_MCP_SERVER_PORT = int(os.getenv("MPESA_MCP_SERVER_PORT", "5002"))

# Per-request context (populated by ASGI handler)
request_context: contextvars.ContextVar[dict] = contextvars.ContextVar("request_context")
trace_context: contextvars.ContextVar[dict] = contextvars.ContextVar("trace_context")

set_trace_context_provider(trace_context)  

# ------------------------------------------------------------------------------
# Header / trace helpers
# ------------------------------------------------------------------------------
def _extract_headers(scope: Scope) -> dict[str, str]:
    """Normalize incoming ASGI headers: lowercase keys, '_' -> '-'."""
    raw = scope.get("headers", []) or []
    out: dict[str, str] = {}
    for k, v in raw:
        kk = k.decode().strip().lower().replace("_", "-")
        out[kk] = v.decode()
    return out


def extract_trace_context(scope: dict, headers: dict) -> dict:
    """Build trace context including the FULL normalized headers for multi-tenant tracing."""
    client = scope.get("client") or ["", ""]
    server = scope.get("server") or ["", ""]
    query_string = scope.get("query_string", b"")
    if isinstance(query_string, bytes):
        query_string = query_string.decode()

    return {
        "request": {
            "method": scope.get("method"),
            "path": scope.get("path"),
            "query_string": query_string,
            "client": {"ip": client[0], "port": client[1] if len(client) > 1 else None},
            "server": {"host": server[0], "port": server[1] if len(server) > 1 else None},
            # ✅ keep ALL normalized headers (includes paylink-api-key / authorization)
            "headers": headers,
        },
        "environment": {
            "mcp_protocol_version": headers.get("mcp-protocol-version"),
            "payment_provider": headers.get("payment-provider"),
        },
    }

# ------------------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------------------
@click.command()
@click.option("--port", default=MPESA_MCP_SERVER_PORT, help="Port to listen on for HTTP")
@click.option(
    "--log-level",
    default="INFO",
    help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
)
@click.option(
    "--json-response",
    is_flag=True,
    default=False,
    help="Enable JSON responses for StreamableHTTP",
)
def main(port: int, log_level: str, json_response: bool) -> int:
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


    app = Server("mpesa_mcp_server")

    @app.list_tools()
    async def list_tools() -> list[Tool]:
        return get_mpesa_tools()

    @app.call_tool()
    @paylink_tracer()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        headers = request_context.get({})
        trace_ctx = trace_context.get({})

        logger.info(f"Trace context on tool call: {trace_ctx}")

        try:
            if name == "stk_push":
                result = await stk_push_handler(arguments, headers)
            else:
                return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]

            # Coerce to text for MCP response
            if not isinstance(result, str):
                import json as _json
                result = _json.dumps(result, ensure_ascii=False)

            return [TextContent(type="text", text=result)]

        except ValueError as e:
            return [TextContent(type="text", text=f"Invalid input: {e}")]
        except Exception as e:
            logger.exception("Tool error")
            return [
                TextContent(
                    type="text",
                    text=f"Something went wrong while running tool '{name}'. Error: {e}",
                )
            ]

    # ------------------------------------------------------------------------------
    # Transports
    # ------------------------------------------------------------------------------
    sse = SseServerTransport("/messages/")

    # Robust ASGI SSE endpoint (avoid request._send)
    async def sse_app(scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            return
        try:
            async with sse.connect_sse(scope, receive, send) as streams:
                await app.run(streams[0], streams[1], app.create_initialization_options())
        except Exception:
            logger.exception("SSE: unhandled error")

    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,
        json_response=json_response,
        stateless=True,
    )

    async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:
        # Normalize & store ALL headers
        headers = _extract_headers(scope)
        tok_req = request_context.set(headers)

        # Build & store full trace context (includes headers)
        tc = extract_trace_context(scope, headers)
        tok_trace = trace_context.set(tc)

        try:
            await session_manager.handle_request(scope, receive, send)
        except Exception:
            logger.exception("StreamableHTTP: unhandled error")
        finally:
            # Prevent context leakage across requests
            trace_context.reset(tok_trace)
            request_context.reset(tok_req)

    @contextlib.asynccontextmanager
    async def lifespan(starlette_app: Starlette) -> AsyncIterator[None]:
        async with session_manager.run():
            try:
                yield
            finally:
                logger.info("Application shutting down...")

    routes = [
        Mount("/sse", app=sse_app),
        Mount("/messages/", app=sse.handle_post_message),
        Mount("/mcp", app=handle_streamable_http),
    ]

    starlette_app = Starlette(debug=True, lifespan=lifespan, routes=routes)

    uvicorn.run(starlette_app, host="0.0.0.0", port=port, log_level=log_level.lower())
    return 0


if __name__ == "__main__":
    main()
