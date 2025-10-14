import os
import logging
import base64
import httpx
from contextvars import ContextVar
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env if present
load_dotenv()

# Context variables for request-scoped data
mpesa_access_token_context: ContextVar[str] = ContextVar("mpesa_access_token")
mpesa_token_expiry_context: ContextVar[datetime] = ContextVar("mpesa_token_expiry")


def _create_basic_auth_header(consumer_key: str, consumer_secret: str) -> str:
    """Create Basic Auth header for M-Pesa API authentication."""
    credentials = f"{consumer_key}:{consumer_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded_credentials}"


def _is_token_expired() -> bool:
    """Check if the current access token has expired."""
    try:
        expiry = mpesa_token_expiry_context.get()
        # Add 60 seconds buffer to avoid edge cases
        return datetime.now() >= (expiry - timedelta(seconds=60))
    except LookupError:
        return True


async def get_mpesa_access_token(
    consumer_key: str, consumer_secret: str, base_url: str, force_refresh: bool = False
) -> str:
    """
    Get a valid M-Pesa access token, refreshing if necessary.

    Args:
        consumer_key: M-Pesa consumer key
        consumer_secret: M-Pesa consumer secret
        base_url: M-Pesa base URL
        force_refresh: If True, force a new token request regardless of expiry

    Returns:
        Valid access token string

    Raises:
        RuntimeError: If unable to obtain credentials or token
        requests.RequestException: If the API request fails
    """
    # Check if we have a valid token in context
    if not force_refresh:
        try:
            if not _is_token_expired():
                return mpesa_access_token_context.get()
        except LookupError:
            pass

    # Prepare the request
    url = f"{base_url}/oauth/v1/generate"
    headers = {
        "Authorization": _create_basic_auth_header(consumer_key, consumer_secret),
        "Content-Type": "application/json",
    }
    params = {"grant_type": "client_credentials"}

    logger.info("Requesting new M-Pesa access token")

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()

        token_data: Dict[str, Any] = response.json()

        if "access_token" not in token_data:
            raise RuntimeError("Invalid response from M-Pesa OAuth endpoint")

        access_token = token_data["access_token"]
        expires_in = int(token_data.get("expires_in", 3600))

        # Calculate expiry time
        expiry_time = datetime.now() + timedelta(seconds=expires_in)

        # Store in context variables
        mpesa_access_token_context.set(access_token)
        mpesa_token_expiry_context.set(expiry_time)

        logger.info(f"M-Pesa access token obtained, expires in {expires_in} seconds")

        return access_token

    except httpx.RequestError as e:
        logger.error(f"Failed to obtain M-Pesa access token: {e}")
        raise RuntimeError(f"Failed to obtain M-Pesa access token: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error when obtaining M-Pesa access token: {e}")
        raise RuntimeError(f"HTTP error when obtaining M-Pesa access token: {e}")
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"Invalid response format from M-Pesa OAuth endpoint: {e}")
        raise RuntimeError(f"Invalid response format from M-Pesa OAuth endpoint: {e}")


if __name__ == "__main__":
    print(get_mpesa_access_token())
