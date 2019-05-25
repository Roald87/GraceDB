import json

import requests

_url = "http://localhost:4040/api/tunnels/"


def _get_ngrok() -> str:
    """
    Return the https url of the ngrok tunnel or None if no tunnel is set up.

    Returns
    -------
    str
        Url of ngrok tunnel

    Source
    ------
    https://stackoverflow.com/a/54088479/6329629
    """
    try:
        res = requests.get(_url)
    except requests.exceptions.ConnectionError:
        print('Make sure ngrok is running.')
        return None

    res_unicode = res.content.decode("utf-8")
    res_json = json.loads(res_unicode)

    return res_json


def get_ngrok_url():
    res_json = _get_ngrok()

    for i in res_json["tunnels"]:
        if i['name'] == 'command_line':
            return i['public_url']

def get_port():
    res_json = _get_ngrok()

    for i in res_json["tunnels"]:
        if i['name'] == 'command_line':
            local_address = i['config']['addr']
            port = int(local_address.split(':')[-1])
            return port