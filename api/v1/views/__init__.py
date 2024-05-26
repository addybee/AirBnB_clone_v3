#!/usr/bin/python3
"""
This module initializes a Flask Blueprint for API version 1 views.
"""


from flask import Blueprint
from api.v1.views.index import *


app_views = Blueprint("app_views", __name__, url_prefix="/api/v1")
app_views.add_url_rule("/status", view_func=get_status, methods=['GET'])
