#!/usr/bin/python3
"""
This module provides API endpoints for managing Place instances in a storage
system. It includes functions to create, retrieve, update, and delete Place
objects, as well as retrieve all Place instances.

Functions:
    get_places() -> flask.Response:
        Retrieves all Place instances from storage and returns them in JSON
        format.

    get_place_by_id(place_id: str) -> flask.Response:
        Retrieves a Place by its ID and returns it as a JSON object. Aborts
        with a 404 error if the Place is not found.

    delete_place(place_id: str) -> flask.Response:
        Deletes a Place by its ID from storage. Aborts with a 404 error if the
        Place is not found. Returns an empty JSON response on success.

    create_place() -> tuple:
        Creates a new Place instance from JSON data in the request. Aborts
        with a 400 error if no JSON data is found or if the 'name' field
        is missing. Returns the new Place as a JSON object along with a
        201 status code.

    update_place(place_id: str) -> flask.Response:
        Updates attributes of a Place instance based on the provided place_id.
        Aborts with a 404 error if no Place is found, or a 400 error if the
        request does not contain valid JSON data. Returns the updated Place as
        a JSON object.
"""


from flask import jsonify, abort, request, make_response
from models import storage
from models.place import Place
from api.v1.views import app_views


@app_views.route("/cities/<city_id>/places", methods=['GET'],
                 strict_slashes=False)
def get_places_by_city_id(city_id):
    """
    Retrieves a list of places for a given city ID.

    This endpoint retrieves all places associated with a specific city,
    identified by `city_id`. If the city does not exist, it responds with
    a 404 error.

    Args:
        city_id (str): The unique identifier for the city.

    Returns:
        json: A list of places in JSON format if the city exists. Each place
              is represented as a dictionary.
        aborts: 404 error if the city with the given `city_id` does not
        exist.

    Example:
        GET /api/v1/cities/1234/places returns a JSON list of places for city
        1234.
    """
    from models.city import City
    city = storage.get(City, city_id)

    if not city:
        abort(404)
    return jsonify([place.to_dict() for place in city.places])


@app_views.route("/places/<place_id>", methods=['GET'],
                 strict_slashes=False)
def get_place_by_id(place_id):
    """
    Retrieve a place by its ID and return it as a JSON object.

    Args:
        place_id (str): The unique identifier for the place.

    Returns:
        json: A JSON representation of the place object.

    Raises:
        HTTPException: 404 error if the place is not found in the database.
    """
    place = storage.get(Place, place_id)

    if not place:
        abort(404)
    return make_response(jsonify(place.to_dict()), 200)


@app_views.route("/places/<place_id>", methods=['DELETE'],
                 strict_slashes=False)
def delete_place(place_id):
    """
    Deletes a place object from the storage.

    This function retrieves a place by its ID and deletes it from the storage.
    If the place with the given ID does not exist, it aborts the request with
    a 404 error. After successful deletion, it returns an empty JSON response.

    Args:
        place_id (str): The unique identifier of the place to be deleted.

    Returns:
        flask.Response: An empty JSON response indicating successful deletion.

    Raises:
        HTTPException: 404 error if the place with the specified ID is not
        found.
    """
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    storage.delete(place)
    storage.save()
    return make_response(jsonify({}), 200)


@app_views.route("/cities/<city_id>/places", methods=['POST'],
                 strict_slashes=False)
def create_place(city_id):
    """
    Creates a new place in a city with the given city_id.

    Args:
        city_id (str): The ID of the city where the new place will be
        created.

    Returns:
        Flask Response: JSON representation of the new place with a status
        code of 201,
        or an error response with status code 404 if the city is not found,
        400 if the input JSON is missing or the 'name' field is not provided.

    Raises:
        HTTPException: 404 if no city with the given ID exists.
        HTTPException: 400 if the input is not a valid JSON or 'name' is
        missing.

    Example:
        POST /api/v1/cities/1234/places with body {"name": "New Place"}
        returns 201 with the new place's data or an error status.
    """
    from models.city import City
    from models.user import User

    # Check if the city exists
    if not storage.get(City, city_id):
        abort(404)
    # Get place data from request
    place_data = request.get_json(silent=True)
    if place_data is None:
        abort(400, "Not a JSON")
    if "user_id" not in place_data:
        abort(400, "Missing user_id")
    if not storage.get(User, place_data.get("user_id")):
        abort(404)
    if "name" not in place_data:
        abort(400, "Missing name")

    # Create and save new place
    place = Place(**place_data)
    place.city_id = city_id
    storage.new(place)
    storage.save()
    return make_response(jsonify(place.to_dict()), 201)


@app_views.route("/places/<place_id>", methods=['PUT'],
                 strict_slashes=False)
def update_place(place_id):
    """
    Update the attributes of a Place instance based on the provided place_id.

    Args:
        place_id (str): The unique identifier of the Place to be updated.

    Returns:
        json: A JSON representation of the updated Place instance.

    Raises:
        404: If no Place with the given id is found.
        400: If the request does not contain valid JSON data.
    """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    place_data = request.get_json(silent=True)
    if place_data is None:
        abort(400, "Not a JSON")
    ignore = ['id', 'user_id', 'city_id', 'created_at', 'updated_at']
    for key, value in place_data.items():
        if key not in ignore:
            setattr(place, key, value)
    storage.new(place)
    storage.save()
    return make_response(jsonify(place.to_dict()), 200)


@app_views.route("/places_search", methods=['POST'], strict_slashes=False)
def search_place():
    """
    Search for places based on states, cities, or amenities filters.

    This endpoint accepts a JSON object with optional 'states', 'cities',
    and 'amenities' keys. It returns a list of places that match the filters.
    If no filters are provided, all places are returned.

    The search is inclusive for states and cities but exclusive for amenities,
    meaning all specified amenities must be present in the place.

    Returns:
        A JSON list of places matching the search criteria.

    Raises:
        HTTPException: 400 if the request is not a valid JSON.
    """
    data = request.get_json(silent=True)
    if data is None:
        abort(400, "Not a JSON")

    places = []

    if not data:
        places = storage.all(Place).values()
    else:
        if 'states' in data:
            for state_id in data['states']:
                places.extend(get_places(state_id, "State"))

        if 'cities' in data:
            for city_id in data['cities']:
                places.extend(get_places(city_id, "City"))
        # Deduplicate places using their unique IDs
        places = {place.id: place for place in places}.values()

    if not places:
        places = storage.all(Place).values()

    if 'amenities' in data and data['amenities']:
        places = [place for place in places if
                  set(data['amenities']).issubset(
                      {amenity.id for amenity in place.amenities})]

    return jsonify([place.to_dict() for place in places])


def get_places(id: str, cls: str):
    """
    Retrieve places associated with a given state or city.

    This function fetches an object based on its class and ID, then returns
    a list of places related to the object if it exists. If the object does
    not exist, it aborts the request with a 404 error.

    Args:
        id (str): The ID of the object to retrieve.
        cls (str): The class type of the object ('State' or 'City').

    Returns:
        list: A list of places associated with the state or city.

    Raises:
        HTTPException: 404 if the object is not found.

    Example:
        - get_places("123", "State") returns all places in all cities of
          state with ID "123".
        - get_places("456", "City") returns all places in city with ID "456".
    """
    obj = storage.get(cls, id)
    if obj is None:
        abort(404)
    if cls == "State":
        return [place for city in obj.cities for place in city.places]
    elif cls == "City":
        return [place for place in obj.places]
