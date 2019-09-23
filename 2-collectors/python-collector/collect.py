import base64
import hashlib
import json
import logging
import os
import urllib
import uuid
from datetime import datetime

from flask import make_response, redirect as flask_redirect

__version__ = '1.0.0'

NETWORK_COOKIE_NAME = os.environ.get("NETWORK_COOKIE_NAME", "nuid")
NETWORK_COOKIE_DOMAIN = os.environ.get("NETWORK_COOKIE_DOMAIN", ".mlanalytix.com")
NETWORK_COOKIE_EXPIRY = os.environ.get("NETWORK_COOKIE_EXPIRY", 31557600)  # 1 year
DOMAIN_COOKIE_NAME = os.environ.get("DOMAIN_COOKIE_NAME", "cid")


def get_network_cookie(request):
    domain_user_id = request.values.get(DOMAIN_COOKIE_NAME)
    network_user_id = request.cookies.get(NETWORK_COOKIE_NAME)

    if network_user_id:
        return network_user_id

    cookie_value = uuid.uuid4().hex
    if domain_user_id:
        cookie_value = hashlib.sha3_256(str(domain_user_id))

    return cookie_value


def set_network_cookie(response, network_user_id):
    response.set_cookie(
        NETWORK_COOKIE_NAME,
        network_user_id,
        max_age=NETWORK_COOKIE_EXPIRY,
        domain=NETWORK_COOKIE_DOMAIN,
        secure=True,
        httponly=True
    )
    return response


def request_log(request, network_user_id):
    params = {}
    if request.method == 'GET':
        params = request.values.to_dict(flat=False)
    elif request.method == 'POST':
        if request.is_json:
            params = request.get_json()
        else:
            params = urllib.parse.parse_qs(request.data)

    log = {
        "type": "collect",
        "collector_tstamp": datetime.now().timestamp(),
        "v_collector": __version__,
        "request_url": request.url,
        "nuid": network_user_id,
        "headers": dict(request.headers),
        "cookies": request.cookies,
        "params": params,
    }

    logging.info(json.dumps(log))


def generate_pixel():
    pixel = 'R0lGODlhAQABAIAAAP///////yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='
    pixel = base64.b64decode(pixel)
    response = make_response(pixel)
    response.headers['Content-Type'] = 'image/gif'
    response.headers['Access-Control-Allow-Origin'] = "*"
    response.headers['Access-Control-Allow-Methods'] = "GET, POST"
    response.headers['Cache-Control'] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers['Cache-Control'] = "post-check=0, pre-check=0"
    response.headers['Pragma'] = "no-cache"

    return response


def handle_cors():
    return make_response("", 204)


def collect(request):
    if request.method == 'OPTIONS':
        return handle_cors()

    network_user_id = get_network_cookie(request)

    response = generate_pixel()
    response = set_network_cookie(response, network_user_id)
    request_log(request, network_user_id)

    return response


def redirect(request):
    network_user_id = get_network_cookie(request)
    request_log(request, network_user_id)

    return flask_redirect(request.values.get("u"), code=302)
