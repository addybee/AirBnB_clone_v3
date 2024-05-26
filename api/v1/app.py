#!/usr/bin/python3
"""
A Flask application module for handling API requests.

This module sets up a Flask application, registers a blueprint for handling
API routes, and ensures that the storage session is properly closed after each
request. It retrieves configuration from environment variables to set the host
and port for the server.

Attributes:
    app (Flask): The Flask application instance.
"""


from api.v1.views import app_views
from flask import Flask
from models import storage
from os import getenv


app = Flask(__name__)
app.register_blueprint(app_views)


@app.teardown_appcontext
def close_session(error):
    """ closes the storage session after request is completed """
    storage.close()


if __name__ == '__main__':
    host = getenv('HBNB_API_HOST', '0.0.0.0')
    port = int(getenv('HBNB_API_PORT', 5000))
    app.run(host=host, port=port, threaded=True)
