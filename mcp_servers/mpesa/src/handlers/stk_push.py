import logging
import json
import base64
import os
from datetime import datetime
from typing import Any
import httpx
from src.utils.auth import get_mpesa_access_token

logger = logging.getLogger(__name__)


async def stk_push_handler(arguments: dict[str, Any]) -> str:
    try:
        # Validate required fields
        required_fields = [
            "amount",
            "phone_number",
            "account_reference",
            "transaction_desc",
        ]
        for field in required_fields:
            if field not in arguments or not arguments[field]:
                logger.warning(f"Missing required field: '{field}'")
                raise ValueError(f"Missing required field: '{field}'")

        # Get configuration from environment
        if os.getenv("MPESA_ENVIRONMENT") == "production":
            base_url = os.getenv("MPESA_PRODUCTION_URL")
        else:
            base_url = os.getenv("MPESA_SANDBOX_URL")
            
        logger.info(f"Using base URL: {base_url}")
        
        business_short_code = os.getenv("MPESA_BUSINESS_SHORT_CODE")
        passkey = os.getenv("MPESA_PASSKEY")
        callback_url = os.getenv("MPESA_CALLBACK_URL")
        transaction_type = "CustomerPayBillOnline"

        # Generate technical parameters
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password_string = f"{business_short_code}{passkey}{timestamp}"
        password = base64.b64encode(password_string.encode()).decode()

        # Get access token
        access_token = get_mpesa_access_token()

        # Build payload for M-Pesa API
        payload = {
            "BusinessShortCode": business_short_code,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": transaction_type,
            "Amount": arguments["amount"],
            "PartyA": arguments["phone_number"],
            "PartyB": business_short_code,
            "PhoneNumber": arguments["phone_number"],
            "CallBackURL": callback_url,
            "AccountReference": arguments["account_reference"],
            "TransactionDesc": arguments["transaction_desc"],
        }

        logger.info(f"Sending STK push request with payload: {json.dumps(payload)}")

        # Make request to M-Pesa STK push endpoint
        url = f"{base_url}/mpesa/stkpush/v1/processrequest"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        logger.debug(f"Received response: {json.dumps(data)}")

        # Check if request was successful
        response_code = data.get("ResponseCode")
        if response_code != "0":
            error_msg = data.get("ResponseDescription", "Unknown error")
            logger.warning(f"STK push failed with code {response_code}: {error_msg}")
            return f"STK push failed: {error_msg}"

        # Extract relevant information for user
        result = {
            "status": "success",
            "message": data.get("CustomerMessage", "Payment prompt sent successfully"),
            "merchant_request_id": data.get("MerchantRequestID"),
            "checkout_request_id": data.get("CheckoutRequestID"),
            "amount": arguments["amount"],
            "phone_number": arguments["phone_number"],
            "reference": arguments["account_reference"],
        }

        logger.info(
            f"STK push successful for {arguments['amount']} KES to {arguments['phone_number']}"
        )
        return json.dumps(result, indent=2)

    except ValueError as ve:
        logger.warning(f"Validation error: {str(ve)}")
        return f"Invalid input: {str(ve)}"

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
        return f"HTTP request failed: {e.response.status_code}"

    except Exception as e:
        logger.exception("Unexpected error during STK push request")
        return f"Request failed: {str(e)}"
