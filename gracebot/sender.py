import logging

import requests

from config import preliminary_command, retraction_command, secret, update_command
from logconfig import logging_kwargs
from ngrok import get_ngrok_url

logging.basicConfig(**logging_kwargs)  # type: ignore


def post_preliminary(event_id):
    _post_message(event_id, "new event", preliminary_command)


def post_retraction(event_id):
    _post_message(event_id, "retraction", retraction_command)


def post_update(event_id):
    _post_message(event_id, "update", update_command)


def _post_message(event_id: str, message_type: str, command: str):
    message = fake_telegram_update(f"{command} {event_id}")

    res = requests.post(f"{get_ngrok_url()}/{secret}", json=message)
    if res.ok:
        logging.info(f"Send {message_type} message to GraceDbBot")
    else:
        logging.error(f"Failed to POST {message_type} to webhook URL.")


def fake_telegram_update(command: str):
    update_json = {
        "message": {
            "from": {"is_bot": True},
            "chat": {"id": 14306049, "type": "private"},
            "date": 1559503719,
            "text": f"/{command}",
            "entities": [
                {"offset": 0, "length": len(f"/{command}"), "type": "bot_command"}
            ],
        }
    }

    return update_json
