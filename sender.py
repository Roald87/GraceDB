import logging
import time

import requests

import listener
from config import logging_kwargs, preliminary_command, retraction_command, secret, update_command
from ngrok import get_ngrok_url

logging.basicConfig(**logging_kwargs)

def post_preliminairy():
    preliminary_message = fake_telegram_update(preliminary_command)

    res = requests.post(
        f'{get_ngrok_url()}/{secret}',
        json=preliminary_message)
    if res.ok:
        logging.info(f"Send preliminary message to GraceDbBot")
    else:
        logging.error("Failed to POST preliminary to webhook URL.")

def post_update(event_id):
    update_message = fake_telegram_update(f'{update_command} {event_id}')

    res = requests.post(
        f'{get_ngrok_url()}/{secret}',
        json=update_message)
    if res.ok:
        logging.info(f"Send update message to GraceDbBot")
    else:
        logging.error("Failed to POST update to webhook URL.")

def post_retraction(event_id):
    retraction_message = fake_telegram_update(f'{retraction_command} {event_id}')

    res = requests.post(
        f'{get_ngrok_url()}/{secret}',
        json=retraction_message)
    if res.ok:
        logging.info(f"Send retraction message to GraceDbBot")
    else:
        logging.error("Failed to POST retraction to webhook URL.")

def fake_telegram_update(command: str):
    update_json = {
        "message": {
            "from": {
                "is_bot": True,
            },
            "chat": {
                "id": 34702149,
                "type": "private"
            },
            "date": 1559503719,
            "text": f"/{command}",
            "entities": [
                {
                    "offset": 0,
                    "length": len(f"/{command}"),
                    "type": "bot_command",
                }
            ]
        }
    }

    return update_json


if __name__ == "__main__":
    test_events_to_send = [
        listener.test_send_preliminairy,
        listener.test_send_initial,
        listener.test_send_update,
        listener.test_send_retraction,
    ]

    for event in test_events_to_send:
        event()
        time.sleep(5)