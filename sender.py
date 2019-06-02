import logging

import requests

import listener
from config import logging_kwargs, preliminary_command, secret
from ngrok import get_ngrok_url

logging.basicConfig(**logging_kwargs)

def post_preliminairy(alert_contents):
    preliminary_message = fake_telegram_update(
        preliminary_command,
        alert_contents,
    )

    res = requests.post(
        f'{get_ngrok_url()}/{secret}',
        json=preliminary_message)
    if res.ok:
        logging.info(f"Send preliminary message to GraceDbBot")
    else:
        logging.error("Failed to POST to webhook URL.")

def fake_telegram_update(command: str, message: str):
    update_json = {
        "message": {
            "from": {
                "is_bot": True,
            },
            "chat": {
                "id": 34702149,
                "type": "private"
            },
            "date": 1559117900,
            "text": f"/{command}",
            "entities": [
                {
                    "offset": 0,
                    "length": len(f"/{command}"),
                    "type": "bot_command",
                    "url": message
                }
            ]
        }
    }

    return update_json

if __name__ == "__main__":
    listener.send_preliminairy()