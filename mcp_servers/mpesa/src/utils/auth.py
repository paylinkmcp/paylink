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



def _get_env_credentials() -> tuple[str, str]:
    """Get M-Pesa API credentials from environment variables."""
    consumer_key = os.getenv("MPESA_CONSUMER_KEY")
    consumer_secret = os.getenv("MPESA_CONSUMER_SECRET")

    if not consumer_key or not consumer_secret:
        raise RuntimeError(
            "M-Pesa API credentials not found. Set MPESA_CONSUMER_KEY/CONSUMER_KEY and "
            "MPESA_CONSUMER_SECRET/CONSUMER_SECRET environment variables."
        )

    return consumer_key, consumer_secret


def _get_mpesa_base_url() -> str:
    """Get the appropriate M-Pesa API base URL based on environment."""
    # Allow both MPESA_ENVIRONMENT and ENVIRONMENT variables
    env_var = os.getenv("MPESA_ENVIRONMENT", "sandbox")
    is_production = env_var.lower() == "production"

    if is_production:
        return os.getenv("MPESA_PRODUCTION_URL")
    else:
        return os.getenv("MPESA_SANDBOX_URL")


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


def get_mpesa_access_token(force_refresh: bool = False) -> str:
    """
    Get a valid M-Pesa access token, refreshing if necessary.

    Args:
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

    # Get fresh credentials and request new token
    consumer_key, consumer_secret = _get_env_credentials()
    base_url = _get_mpesa_base_url()
    oauth_endpoint = os.getenv("MPESA_OAUTH_ENDPOINT", "/oauth/v1/generate")

    # Prepare the request
    url = f"{base_url}{oauth_endpoint}"
    headers = {
        "Authorization": _create_basic_auth_header(consumer_key, consumer_secret),
        "Content-Type": "application/json",
    }
    params = {"grant_type": "client_credentials"}

    logger.info("Requesting new M-Pesa access token")

    try:
        with httpx.Client(timeout=30) as client:
            response = client.get(url, headers=headers, params=params)
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