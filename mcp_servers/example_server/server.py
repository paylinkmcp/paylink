import logging
import os
import sys
import click
import uuid
from mcp.server.lowlevel import Server
from mcp.types import TextContent, Tool
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.server.sse import SseServerTransport
from starlette.types import Receive, Scope, Send
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from collections.abc import AsyncIterator
import contextlib
import uvicorn
from typing import Any
from dotenv import load_dotenv
from starlette.responses import Response
import contextvars
from src.tools.tool import get_mpesa_tools
from src.handlers.stk_push import stk_push_handler
from paylink_tracer import paylink_tracer

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)
MPESA_MCP_SERVER_PORT = int(os.getenv("MPESA_MCP_SERVER_PORT", "5002"))

request_context = contextvars.ContextVar("request_context")

@click.command()
@click.option(
    "--port", default=MPESA_MCP_SERVER_PORT, help="Port to listen on for HTTP"
)
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
        tools = get_mpesa_tools()
        # logger.info(f"Listing tools: {[t.name for t in tools]}")
        return tools

    @app.call_tool()
    @paylink_tracer
    async def call_tool(
        name: str,
        arguments: dict[str, Any],
    ) -> list[TextContent]:
        
        
        headers = request_context.get()
        logger.info(f"Headers on tool call: {headers}")


        try:
            if name == "stk_push":
                # pass headers to handler
                result = await stk_push_handler(arguments)
            else:
                # logger.error(f"Unknown tool name: {name}")
                return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]

            # logger.info(f"Tool '{name}' completed successfully")
            return [TextContent(type="text", text=result)]

        except ValueError as e:
            # logger.warning(f"Invalid input for tool '{name}': {e}")
            return [TextContent(type="text", text=f"Invalid input: {str(e)}")]

        except Exception as e:
            # logger.exception(f"Error running tool '{name}': {e}")
            return [
                TextContent(
                    type="text",
                    text=f"Something went wrong while running tool '{name}'. Error: {str(e)}",
                )
            ]

    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        try:
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )
        except Exception:
            logger.exception("SSE: unhandled error")
        return Response()

    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,
        json_response=json_response,
        stateless=True,
    )

    async def handle_streamable_http(
        scope: Scope, receive: Receive, send: Send
    ) -> None:
        
        # Extract headers from the incoming request
        headers = {k.decode(): v.decode() for k, v in scope.get("headers", [])}
        # store headers in context var
        request_context.set(headers)  
        
        # logger.info(f"Context headers: {headers}")
        
        try:
            await session_manager.handle_request(scope, receive, send)

        except Exception:
            logger.exception("StreamableHTTP: unhandled error")

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        async with session_manager.run():
            # logger.info("Application started with StreamableHTTP Session Manager")
            try:
                yield
            finally:
                logger.info("Application shutting down...")

    routes = [
        Route("/sse", endpoint=handle_sse, methods=["GET"]),
        Mount("/messages/", app=sse.handle_post_message),
        Mount("/mcp", app=handle_streamable_http),
    ]

    starlette_app = Starlette(debug=True, lifespan=lifespan, routes=routes)

    uvicorn.run(starlette_app, host="0.0.0.0", port=port)

    return 0


if __name__ == "__main__":
    main()
