#!/usr/bin/python3
"""
This module provides API endpoints for managing City instances in a storage
system. It includes functions to create, retrieve, update, and delete City
objects, as well as retrieve all City instances.

Functions:
    get_cities() -> flask.Response:
        Retrieves all City instances from storage and returns them in JSON
        format.

    get_city_by_id(city_id: str) -> flask.Response:
        Retrieves a City by its ID and returns it as a JSON object. Aborts
        with a 404 error if the City is not found.

    delete_city(city_id: str) -> flask.Response:
        Deletes a City by its ID from storage. Aborts with a 404 error if the
        City is not found. Returns an empty JSON response on success.

    create_city() -> tuple:
        Creates a new City instance from JSON data in the request. Aborts
        with a 400 error if no JSON data is found or if the 'name' field
        is missing. Returns the new City as a JSON object along with a
        201 status code.

    update_city(city_id: str) -> flask.Response:
        Updates attributes of a City instance based on the provided city_id.
        Aborts with a 404 error if no City is found, or a 400 error if the
        request does not contain valid JSON data. Returns the updated City as
        a JSON object.
"""


from flask import jsonify, abort, request, make_response
from models import storage
from models.city import City
from api.v1.views import app_views


@app_views.route("/states/<state_id>/cities", methods=['GET'], strict_slashes=False)
def get_cities_by_state_id(state_id):

    from models.state import State
    state = storage.get(State, state_id)

    if not state:
        abort(404)
    return jsonify([city.to_dict() for city in state.cities])


@app_views.route("/cities/<city_id>", methods=['GET'],
                 strict_slashes=False)
def get_city_by_id(city_id):
    """
    Retrieve a city by its ID and return it as a JSON object.

    Args:
        city_id (str): The unique identifier for the city.

    Returns:
        json: A JSON representation of the city object.

    Raises:
        HTTPException: 404 error if the city is not found in the database.
    """
    city = storage.get(City, city_id)

    if not city:
        abort(404)
    return make_response(jsonify(city.to_dict()), 200)


@app_views.route("/cities/<city_id>", methods=['DELETE'],
                 strict_slashes=False)
def delete_city(city_id):
    """
    Deletes a city object from the storage.

    This function retrieves a city by its ID and deletes it from the storage.
    If the city with the given ID does not exist, it aborts the request with
    a 404 error. After successful deletion, it returns an empty JSON response.

    Args:
        city_id (str): The unique identifier of the city to be deleted.

    Returns:
        flask.Response: An empty JSON response indicating successful deletion.

    Raises:
        HTTPException: 404 error if the city with the specified ID is not
        found.
    """
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    storage.delete(city)
    storage.save()
    return jsonify({})


@app_views.route("/states/<state_id>/cities", methods=['POST'], strict_slashes=False)
def create_city(state_id):
    from models.state import State
    
    if not storage.get(State, state_id):
        abort(404)
    city_data = request.get_json(silent=True)
    if city_data is None:
        abort(400, "Not a JSON")
    if "name" not in city_data:
        abort(400, "Missing name")
        
    city = City(**city_data)
    city.state_id = state_id
    storage.new(city)
    storage.save()
    return make_response(jsonify(city.to_dict()), 201)


@app_views.route("/cities/<city_id>", methods=['PUT'],
                 strict_slashes=False)
def update_city(city_id):
    """
    Update the attributes of a City instance based on the provided city_id.

    Args:
        city_id (str): The unique identifier of the City to be updated.

    Returns:
        json: A JSON representation of the updated City instance.

    Raises:
        404: If no City with the given id is found.
        400: If the request does not contain valid JSON data.
    """
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    city_data = request.get_json(silent=True)
    if city_data is None:
        abort(400, "Not a JSON")
    ignore = ['id', 'created_at', 'updated_at']
    for key, value in city_data.items():
        if key not in ignore:
            setattr(city, key, value)
    storage.new(city)
    storage.save()
    return make_response(jsonify(city.to_dict()), 200)
