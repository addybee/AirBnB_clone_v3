#!/usr/bin/python3
"""
This module provides API endpoints for managing State instances in a storage
system. It includes functions to create, retrieve, update, and delete State
objects, as well as retrieve all State instances.

Functions:
    get_states() -> flask.Response:
        Retrieves all State instances from storage and returns them in JSON
        format.

    get_state_by_id(state_id: str) -> flask.Response:
        Retrieves a State by its ID and returns it as a JSON object. Aborts
        with a 404 error if the State is not found.

    delete_state(state_id: str) -> flask.Response:
        Deletes a State by its ID from storage. Aborts with a 404 error if the
        State is not found. Returns an empty JSON response on success.

    create_state() -> tuple:
        Creates a new State instance from JSON data in the request. Aborts
        with a 400 error if no JSON data is found or if the 'name' field
        is missing. Returns the new State as a JSON object along with a
        201 status code.

    update_state(state_id: str) -> flask.Response:
        Updates attributes of a State instance based on the provided state_id.
        Aborts with a 404 error if no State is found, or a 400 error if the
        request does not contain valid JSON data. Returns the updated State as
        a JSON object.
"""


from flask import jsonify, abort, request, make_response
from models import storage
from models.state import State
from api.v1.views import app_views


@app_views.route("/states", methods=['GET'], strict_slashes=False)
def get_states():
    """
    Retrieves all State instances from storage and returns them in JSON format.
    """
    states = storage.all(State).values()
    return jsonify([state.to_dict() for state in states])


@app_views.route("/states/<string:state_id>", methods=['GET'],
                 strict_slashes=False)
def get_state_by_id(state_id):
    """
    Retrieve a state by its ID and return it as a JSON object.

    Args:
        state_id (str): The unique identifier for the state.

    Returns:
        json: A JSON representation of the state object.

    Raises:
        HTTPException: 404 error if the state is not found in the database.
    """
    state = storage.get(State, state_id)

    if not state:
        abort(404)
    return jsonify(state.to_dict())


@app_views.route("/states/<state_id>", methods=['DELETE'],
                 strict_slashes=False)
def delete_state(state_id):
    """
    Deletes a state object from the storage.

    This function retrieves a state by its ID and deletes it from the storage.
    If the state with the given ID does not exist, it aborts the request with
    a 404 error. After successful deletion, it returns an empty JSON response.

    Args:
        state_id (str): The unique identifier of the state to be deleted.

    Returns:
        flask.Response: An empty JSON response indicating successful deletion.

    Raises:
        HTTPException: 404 error if the state with the specified ID is not
        found.
    """
    state = storage.get(State, state_id)
    if not state:
        abort(404)
    storage.delete(state)
    storage.save()
    return jsonify({})


@app_views.route("/states", methods=['POST'], strict_slashes=False)
def create_state():
    """
    Creates a new State instance from JSON data in the request.

    Returns:
        tuple: A tuple containing the JSON representation of the state and the
               HTTP status code 201.

    Raises:
        HTTPException: 400 with "Not a JSON" if no JSON data is found.
        HTTPException: 400 with "Missing name" if the name field is not
        present.
    """
    state_data = request.get_json(silent=True)
    if state_data is None:
        abort(400, "Not a JSON")
    if "name" not in state_data:
        abort(400, "Missing name")
    state = State(name=state_data['name'])
    storage.new(state)
    storage.save()
    return make_response(jsonify(state.to_dict()), 201)


@app_views.route("/states/<state_id>", methods=['PUT'],
                 strict_slashes=False)
def update_state(state_id):
    """
    Update the attributes of a State instance based on the provided state_id.

    Args:
        state_id (str): The unique identifier of the State to be updated.

    Returns:
        json: A JSON representation of the updated State instance.

    Raises:
        404: If no State with the given id is found.
        400: If the request does not contain valid JSON data.
    """
    state = storage.get(State, state_id)
    if state is None:
        abort(404)
    state_data = request.get_json(silent=True)
    if state_data is None:
        abort(400, "Not a JSON")
    if "name" in state_data:
        state.name = state_data['name']
    storage.new(state)
    storage.save()
    return jsonify(state.to_dict())
