#!/usr/bin/python3

"""
A simple Flask module to return the status of the application as a JSON
response.
"""

from api.v1.views import app_views
from flask import jsonify


@app_views.route('/status', methods=['GET'], strict_slashes=False)
def get_status():
    """Return a JSON response indicating the application status."""
    return jsonify({"status": "OK"})
