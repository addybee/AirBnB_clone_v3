#!/usr/bin/python3
"""Module containing routes for managing associations between places and
amenities.

This module defines routes for creating, deleting, and retrieving associations
between places and amenities in a Flask application. The associations are
managed
via RESTful API endpoints.

Routes:
    - GET /places/<place_id>/amenities: Retrieve amenities associated with
    a place.
    - POST /places/<place_id>/amenities/<amenity_id>: Associate an amenity
    with a place.
    - DELETE /places/<place_id>/amenities/<amenity_id>: Disassociate an amenity
    from a place.

Example:
    To associate an amenity with a place, send a POST request to:
    /places/<place_id>/amenities/<amenity_id>

Attributes:
    None
"""


from flask import jsonify, abort, request, make_response
from models import storage
from models.amenity import Amenity
from models.place import Place
from api.v1.views import app_views


@app_views.route("/places/<place_id>/amenities", methods=['GET'],
                 strict_slashes=False)
def get_amenities_by_place_id(place_id):
    """
    Retrieve all amenities associated with a given place.

    Args:
        place_id (str): The ID of the place for which to retrieve amenities.

    Returns:
        Response: A JSON list of amenities associated with the specified place.

    Raises:
        404: If the place with the given ID does not exist.
    """
    place = storage.get(Place, place_id)

    if not place:
        abort(404)
    return jsonify([amenity.to_dict() for amenity in place.amenities])


@app_views.route("/places/<place_id>/amenities/<amenity_id>",
                 methods=['DELETE'], strict_slashes=False)
def delete_place_amenity(place_id, amenity_id):
    """
    Delete an amenity from a place.

    Args:
        place_id (str): The ID of the place from which to delete the amenity.
        amenity_id (str): The ID of the amenity to delete.

    Returns:
        Response: An empty JSON response with a status code 200.

    Raises:
        404: If the place or amenity with the given ID does not exist, or if
        the amenity is not associated with the place.
    """
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    amenity = storage.get(Amenity, amenity_id)
    if not amenity:
        abort(404)
    if amenity not in place.amenities:
        abort(404)
    place.amenities.remove(amenity)
    storage.save()
    return make_response(jsonify({}), 200)


@app_views.route("/places/<place_id>/amenities/<amenity_id>",
                 methods=['POST'], strict_slashes=False)
def create_place_amenity(place_id, amenity_id):
    """
    Associate an amenity with a place.

    Args:
        place_id (str): The ID of the place to associate the amenity with.
        amenity_id (str): The ID of the amenity to associate with the place.

    Returns:
        Response: A JSON response containing the details of the created
        association with a status code 201 if the association is successfully
        created, or a JSON response containing the details of the existing
        association with a status code 200 if the association already exists.

    Raises:
        404: If the place or amenity with the given ID does not exist.
    """
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    amenity = storage.get(Amenity, amenity_id)
    if not amenity:
        abort(404)
    if amenity in place.amenities:
        return make_response(jsonify(amenity.to_dict()), 200)
    place.amenities.append(amenity)
    storage.new(place)
    storage.save()
    return make_response(jsonify(amenity.to_dict()), 201)
