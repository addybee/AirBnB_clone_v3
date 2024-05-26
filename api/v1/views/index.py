#!/usr/bin/python3
"""
A simple Flask module to return the status of the application as a JSON
response.
"""


from flask import jsonify


def get_status():
    """Return a JSON response indicating the application status."""
    return jsonify({"status": "OK"})
