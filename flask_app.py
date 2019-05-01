from flask import Flask, request

from config import get_secret
from gracebot import GraceBot

app = Flask(__name__)
bot = GraceBot()

@app.route('/{}'.format(get_secret()), methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    if "message" in update:
        text = update["message"]["text"]
        chat_id = update["message"]["chat"]["id"]
        if '/start' in text or '/help' in text:
            bot.send_welcome(chat_id)
        elif '/latest' in text:
            bot.send_latest(chat_id)

    return "OK"


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8088, debug=True)