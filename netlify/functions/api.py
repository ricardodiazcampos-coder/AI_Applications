"""Punto de entrada serverless: expone la app Flask en Netlify Functions."""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

os.environ.setdefault("NETLIFY", "true")

from serverless_wsgi import handle_request

from app import create_app

flask_app = create_app()


def handler(event, context):
    return handle_request(flask_app, event, context)
