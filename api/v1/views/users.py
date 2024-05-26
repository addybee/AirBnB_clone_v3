#!/usr/bin/python3
"""
This module provides API endpoints for managing User instances in a storage
system. It includes functions to create, retrieve, update, and delete User
objects, as well as retrieve all User instances.

Functions:
    get_users() -> flask.Response:
        Retrieves all User instances from storage and returns them in JSON
        format.

    get_user_by_id(user_id: str) -> flask.Response:
        Retrieves a User by its ID and returns it as a JSON object. Aborts
        with a 404 error if the User is not found.

    delete_user(user_id: str) -> flask.Response:
        Deletes a User by its ID from storage. Aborts with a 404 error if the
        User is not found. Returns an empty JSON response on success.

    create_user() -> tuple:
        Creates a new User instance from JSON data in the request. Aborts
        with a 400 error if no JSON data is found or if the 'name' field
        is missing. Returns the new User as a JSON object along with a
        201 status code.

    update_user(user_id: str) -> flask.Response:
        Updates attributes of a User instance based on the provided user_id.
        Aborts with a 404 error if no User is found, or a 400 error if the
        request does not contain valid JSON data. Returns the updated User as
        a JSON object.
"""


from api.v1.views import app_views
from flask import jsonify, abort, request, make_response
from models import storage
from models.user import User


@app_views.route("/users", methods=['GET'], strict_slashes=False)
def get_users():
    """
    Retrieves all User instances from storage and returns them in JSON format.
    """
    users = storage.all(User).values()
    return jsonify([user.to_dict() for user in users])


@app_views.route("/users/<user_id>", methods=['GET'],
                 strict_slashes=False)
def get_user_by_id(user_id):
    """
    Retrieve a user by its ID and return it as a JSON object.

    Args:
        user_id (str): The unique identifier for the user.

    Returns:
        json: A JSON representation of the user object.

    Raises:
        HTTPException: 404 error if the user is not found in the database.
    """
    user = storage.get(User, user_id)

    if not user:
        abort(404)
    return jsonify(user.to_dict())


@app_views.route("/users/<user_id>", methods=['DELETE'],
                 strict_slashes=False)
def delete_user(user_id):
    """
    Deletes a user object from the storage.

    This function retrieves a user by its ID and deletes it from the storage.
    If the user with the given ID does not exist, it aborts the request with
    a 404 error. After successful deletion, it returns an empty JSON response.

    Args:
        user_id (str): The unique identifier of the user to be deleted.

    Returns:
        flask.Response: An empty JSON response indicating successful deletion.

    Raises:
        HTTPException: 404 error if the user with the specified ID is not
        found.
    """
    user = storage.get(User, user_id)
    if not user:
        abort(404)
    storage.delete(user)
    storage.save()
    return jsonify({})


@app_views.route("/users", methods=['POST'], strict_slashes=False)
def create_user():
    """
    Creates a new User instance from JSON data in the request.

    Returns:
        tuple: A tuple containing the JSON representation of the user and the
               HTTP status code 201.

    Raises:
        HTTPException: 400 with "Not a JSON" if no JSON data is found.
        HTTPException: 400 with "Missing name" if the name field is not
        present.
    """
    user_data = request.get_json(silent=True)
    if user_data is None:
        abort(400, "Not a JSON")
    if "email" not in user_data:
        abort(400, "Missing email")
    if "password" not in user_data:
        abort(400, "Missing password")
    user = User(**user_data)
    storage.new(user)
    storage.save()
    return make_response(jsonify(user.to_dict()), 201)


@app_views.route("/users/<user_id>", methods=['PUT'],
                 strict_slashes=False)
def update_user(user_id):
    """
    Update the attributes of a User instance based on the provided user_id.

    Args:
        user_id (str): The unique identifier of the User to be updated.

    Returns:
        json: A JSON representation of the updated User instance.

    Raises:
        404: If no User with the given id is found.
        400: If the request does not contain valid JSON data.
    """
    user = storage.get(User, user_id)
    if user is None:
        abort(404)
    user_data = request.get_json(silent=True)
    if user_data is None:
        abort(400, "Not a JSON")
    ignore = ['id', 'email', 'created_at', 'updated_at']
    for key, value in user_data.items():
        if key not in ignore:
            setattr(user, key, value)
    storage.new(user)
    storage.save()
    return make_response(jsonify(user.to_dict()), 200)
