#!/usr/bin/python3

"""
A simple Flask module to return the status of the application as a JSON
response.
"""


from api.v1.views import app_views
from flask import jsonify
from models import storage
from api.v1.views import app_views


@app_views.route('/status', methods=['GET'], strict_slashes=False)
def get_status():
    """Return a JSON response indicating the application status."""
    return jsonify({"status": "OK"})


@app_views.route("/stats", methods=['GET'], strict_slashes=False)
def get_index():
    """
    Return a JSON response with counts of various objects in storage.

    The response includes counts of amenities, cities, places, reviews,
    states, and users.
    """
    from models.amenity import Amenity
    from models.city import City
    from models.place import Place
    from models.review import Review
    from models.state import State
    from models.user import User

    return (jsonify({
        "amenities": storage.count(Amenity),
        "cities": storage.count(City),
        "places": storage.count(Place),
        "reviews": storage.count(Review),
        "states": storage.count(State),
        "users": storage.count(Amenity)
    }))
