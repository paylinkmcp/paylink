import logging
import json
import base64
from datetime import datetime
from typing import Any
import httpx
from src.utils.auth import get_mpesa_access_token

logger = logging.getLogger(__name__)

def _normalize_headers(headers: dict[str, str]) -> dict[str, str]:
    """Normalize incoming headers to snake_case and lowercase keys."""
    norm: dict[str, str] = {}
    for k, v in (headers or {}).items():
        if not isinstance(k, str):
            continue
        kk = k.strip().lower().replace("-", "_")
        norm[kk] = v
    return norm

def _hget(headers_norm: dict[str, str], key: str) -> str | None:
    """Get a header by snake_case key; accepts both hyphen and underscore originals."""
    return headers_norm.get(key)

async def stk_push_handler(arguments: dict[str, Any], headers: dict[str, str]) -> str:
    # Normalize headers once
    h = _normalize_headers(headers or {})

    # Safe header debug (no secrets)
    logger.info(
        "M-Pesa header presence: base_url=%s, shortcode=%s, callback=%s, passkey=%s, consumer_key=%s, consumer_secret=%s",
        bool(h.get("mpesa_base_url")),
        bool(h.get("mpesa_business_shortcode")),
        bool(h.get("mpesa_callback_url")),
        bool(h.get("mpesa_passkey")),
        bool(h.get("mpesa_consumer_key")),
        bool(h.get("mpesa_consumer_secret")),
    )

    try:
        # Validate required tool args
        for field in ("amount", "phone_number", "account_reference", "transaction_desc"):
            if not arguments.get(field):
                logger.warning("Missing required field: '%s'", field)
                raise ValueError(f"Missing required field: '{field}'")

        # Read credentials from normalized headers (works for hyphen or underscore from client)
        base_url            = _hget(h, "mpesa_base_url")
        business_short_code = _hget(h, "mpesa_business_shortcode")
        passkey             = _hget(h, "mpesa_passkey")
        callback_url        = _hget(h, "mpesa_callback_url")
        consumer_key        = _hget(h, "mpesa_consumer_key")
        consumer_secret     = _hget(h, "mpesa_consumer_secret")

        if not all([base_url, business_short_code, passkey, callback_url, consumer_key, consumer_secret]):
            raise ValueError("Missing one or more M-Pesa credentials in request headers.")

        logger.info("Using base URL: %s", base_url)

        transaction_type = "CustomerPayBillOnline"

        # Generate technical parameters
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password_string = f"{business_short_code}{passkey}{timestamp}"
        password = base64.b64encode(password_string.encode()).decode()

        # Access token using dynamic credentials
        access_token = await get_mpesa_access_token(consumer_key, consumer_secret, base_url)

        # Ensure amount is a string/int as expected by API
        amount = arguments["amount"]
        # Optional: coerce to int (Safaricom accepts numeric); comment out if you prefer raw
        try:
            amount = int(str(amount))
        except Exception:
            pass

        phone = str(arguments["phone_number"])

        payload = {
            "BusinessShortCode": business_short_code,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": transaction_type,
            "Amount": amount,
            "PartyA": phone,
            "PartyB": business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": callback_url,
            "AccountReference": arguments["account_reference"],
            "TransactionDesc": arguments["transaction_desc"],
        }

        url = f"{base_url}/mpesa/stkpush/v1/processrequest"
        headers_ = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=headers_)
            resp.raise_for_status()
            data = resp.json()

        # Success per API contract: ResponseCode == "0"
        if data.get("ResponseCode") != "0":
            error_msg = data.get("ResponseDescription", "Unknown error")
            logger.warning("STK push failed: code=%s msg=%s", data.get("ResponseCode"), error_msg)
            return json.dumps({"status": "error", "message": error_msg, "raw": data}, indent=2)

        result = {
            "status": "success",
            "message": data.get("CustomerMessage", "Payment prompt sent successfully"),
            "merchant_request_id": data.get("MerchantRequestID"),
            "checkout_request_id": data.get("CheckoutRequestID"),
            "amount": str(amount),
            "phone_number": phone,
            "reference": arguments["account_reference"],
        }

        logger.info("STK push successful for %s KES to %s", result["amount"], result["phone_number"])
        return json.dumps(result, indent=2)

    except ValueError as ve:
        logger.warning("Validation error: %s", ve)
        return json.dumps({"status": "error", "message": f"Invalid input: {ve}"}, indent=2)

    except httpx.HTTPStatusError as e:
        body = e.response.text if e.response is not None else ""
        logger.error("HTTP error %s: %s", e.response.status_code if e.response else "?", body)
        return json.dumps(
            {"status": "error", "message": "HTTP request failed", "code": e.response.status_code if e.response else None, "raw": body},
            indent=2,
        )

    except Exception as e:
        logger.exception("Unexpected error during STK push request")
        return json.dumps({"status": "error", "message": f"Request failed: {e}"}, indent=2)
