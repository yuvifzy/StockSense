"""Local webhook simulator for StockSense onboarding flow.

Run with:
    python test_local.py
"""

import time

import requests


WEBHOOK_URL = "http://localhost:8000/webhook"
PHONE_NUMBER = "919999999999"


def build_meta_payload(message_text: str) -> dict:
    return {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "from": PHONE_NUMBER,
                                    "text": {"body": message_text},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }


def send_message(message_text: str) -> None:
    response = requests.post(
        WEBHOOK_URL, json=build_meta_payload(message_text), timeout=30)
    print(f"Message: {message_text}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    print("-")


def main() -> None:
    messages = [
        "Hi",
        "1",
        "Gupta Test Store",
        "560001",
        "Atta 5kg – 3, Maggi – 12",
    ]

    for index, message_text in enumerate(messages):
        send_message(message_text)
        if index < len(messages) - 1:
            time.sleep(0.5)


if __name__ == "__main__":
    main()
