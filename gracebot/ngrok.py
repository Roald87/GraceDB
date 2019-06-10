import json
import logging

import requests

_url = "http://localhost:4040/api/tunnels/"


def _get_ngrok_tunnel() -> str:
    """
    Return the details of the ngrok tunnel or None if no tunnel is set up.

    Returns
    -------
    str
        Details of ngrok tunnel.

    Source
    ------
    https://stackoverflow.com/a/54088479/6329629
    """
    try:
        res = requests.get(_url)
    except requests.exceptions.ConnectionError:
        logging.warning("Can't find ngrok tunnel. Make sure it's running.")
        return None

    res_unicode = res.content.decode("utf-8")
    res_json = json.loads(res_unicode)

    for tunnel in res_json["tunnels"]:
        if "ngrok" in tunnel["public_url"]:
            return tunnel


def get_ngrok_url():
    """
    Return the https URL of the ngrok tunnel.

    Returns
    -------
    str
        URL of ngrok tunnel.
    """
    tunnel = _get_ngrok_tunnel()

    return tunnel["public_url"]


def get_port():
    """
    Return the port of the ngrok tunnel.

    Returns
    -------
    int
        Port number of the ngrok tunnel.
    """
    tunnel = _get_ngrok_tunnel()
    local_address = tunnel["config"]["addr"]
    port = int(local_address.split(":")[-1])

    return port
