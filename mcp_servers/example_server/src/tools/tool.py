from mcp.types import Tool


def get_mpesa_tools() -> list[Tool]:
    return [
        Tool(
            name="stk_push",
            description="Initiates M-Pesa Express (STK Push) payment on behalf of a customer. Sends a payment prompt to the customer's phone requesting them to enter their M-Pesa PIN to authorize and complete payment.",
            inputSchema={
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "string",
                        "description": "Amount to be transacted (only whole numbers supported).",
                        "pattern": "^[0-9]+$",
                    },
                    "phone_number": {
                        "type": "string",
                        "description": "Customer's M-Pesa registered phone number to receive the payment prompt (format: 2547XXXXXXXX).",
                        "pattern": "^2547[0-9]{8}$",
                    },
                    "account_reference": {
                        "type": "string",
                        "description": "Reference identifier for the transaction (max 12 characters). This will be displayed to the customer in the payment prompt.",
                        "maxLength": 12,
                    },
                    "transaction_desc": {
                        "type": "string",
                        "description": "Description of what the payment is for (max 13 characters).",
                        "maxLength": 13,
                    },
                },
                "required": [
                    "amount",
                    "phone_number",
                    "account_reference",
                    "transaction_desc",
                ],
            },
        )
    ]
