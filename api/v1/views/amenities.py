#!/usr/bin/python3
"""
This module provides API endpoints for managing Amenity instances in a storage
system. It includes functions to create, retrieve, update, and delete Amenity
objects, as well as retrieve all Amenity instances.

Functions:
    get_amenities() -> flask.Response:
        Retrieves all Amenity instances from storage and returns them in JSON
        format.

    get_amenity_by_id(amenity_id: str) -> flask.Response:
        Retrieves a Amenity by its ID and returns it as a JSON object. Aborts
        with a 404 error if the Amenity is not found.

    delete_amenity(amenity_id: str) -> flask.Response:
        Deletes a Amenity by its ID from storage. Aborts with a 404 error if
        the Amenity is not found. Returns an empty JSON response on success.

    create_amenity() -> tuple:
        Creates a new Amenity instance from JSON data in the request. Aborts
        with a 400 error if no JSON data is found or if the 'name' field
        is missing. Returns the new Amenity as a JSON object along with a
        201 status code.

    update_amenity(amenity_id: str) -> flask.Response:
        Updates attributes of a Amenity instance based on the provided
        amenity_id. Aborts with a 404 error if no Amenity is found, or a 400
        error if the request does not contain valid JSON data. Returns the
        updated Amenity as a JSON object.
"""


from flask import jsonify, abort, request, make_response
from models import storage
from models.amenity import Amenity
from api.v1.views import app_views


@app_views.route("/amenities", methods=['GET'], strict_slashes=False)
def get_amenities():
    """
    Retrieves all Amenity instances from storage and returns them in
    JSON format.
    """
    amenities = storage.all(Amenity).values()
    return jsonify([amenity.to_dict() for amenity in amenities])


@app_views.route("/amenities/<amenity_id>", methods=['GET'],
                 strict_slashes=False)
def get_amenity_by_id(amenity_id):
    """
    Retrieve a amenity by its ID and return it as a JSON object.

    Args:
        amenity_id (str): The unique identifier for the amenity.

    Returns:
        json: A JSON representation of the amenity object.

    Raises:
        HTTPException: 404 error if the amenity is not found in the database.
    """
    amenity = storage.get(Amenity, amenity_id)

    if not amenity:
        abort(404)
    return jsonify(amenity.to_dict())


@app_views.route("/amenities/<amenity_id>", methods=['DELETE'],
                 strict_slashes=False)
def delete_amenity(amenity_id):
    """
    Deletes a amenity object from the storage.

    This function retrieves a amenity by its ID and deletes it from storage.
    If the amenity with the given ID does not exist, it aborts the request with
    a 404 error. After successful deletion, it returns an empty JSON response.

    Args:
        amenity_id (str): The unique identifier of the amenity to be deleted.

    Returns:
        flask.Response: An empty JSON response indicating successful deletion.

    Raises:
        HTTPException: 404 error if the amenity with the specified ID is not
        found.
    """
    amenity = storage.get(Amenity, amenity_id)
    if not amenity:
        abort(404)
    storage.delete(amenity)
    storage.save()
    return jsonify({})


@app_views.route("/amenities", methods=['POST'], strict_slashes=False)
def create_amenity():
    """
    Creates a new Amenity instance from JSON data in the request.

    Returns:
        tuple: A tuple containing the JSON representation of the amenity and
               the HTTP status code 201.

    Raises:
        HTTPException: 400 with "Not a JSON" if no JSON data is found.
        HTTPException: 400 with "Missing name" if the name field is not
        present.
    """
    amenity_data = request.get_json(silent=True)
    if amenity_data is None:
        abort(400, "Not a JSON")
    if "name" not in amenity_data:
        abort(400, "Missing name")
    amenity = Amenity(**amenity_data)
    storage.new(amenity)
    storage.save()
    return make_response(jsonify(amenity.to_dict()), 201)


@app_views.route("/amenities/<amenity_id>", methods=['PUT'],
                 strict_slashes=False)
def update_amenity(amenity_id):
    """
    Update the attributes of a Amenity instance based on the provided
    amenity_id.

    Args:
        amenity_id (str): The unique identifier of the Amenity to be updated.

    Returns:
        json: A JSON representation of the updated Amenity instance.

    Raises:
        404: If no Amenity with the given id is found.
        400: If the request does not contain valid JSON data.
    """
    amenity = storage.get(Amenity, amenity_id)
    if amenity is None:
        abort(404)
    amenity_data = request.get_json(silent=True)
    if amenity_data is None:
        abort(400, "Not a JSON")
    ignore = ['id', 'created_at', 'updated_at']
    for key, value in amenity_data.items():
        if key not in ignore:
            setattr(amenity, key, value)
    storage.new(amenity)
    storage.save()
    return make_response(jsonify(amenity.to_dict()), 200)
