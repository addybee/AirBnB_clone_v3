#!/usr/bin/python3
"""
This module provides API endpoints for managing Review instances in a storage
system. It includes functions to create, retrieve, update, and delete Review
objects, as well as retrieve all Review instances.

Functions:
    get_reviews() -> flask.Response:
        Retrieves all Review instances from storage and returns them in JSON
        format.

    get_review_by_id(review_id: str) -> flask.Response:
        Retrieves a Review by its ID and returns it as a JSON object. Aborts
        with a 404 error if the Review is not found.

    delete_review(review_id: str) -> flask.Response:
        Deletes a Review by its ID from storage. Aborts with a 404 error if the
        Review is not found. Returns an empty JSON response on success.

    create_review() -> tuple:
        Creates a new Review instance from JSON data in the request. Aborts
        with a 400 error if no JSON data is found or if the 'name' field
        is missing. Returns the new Review as a JSON object along with a
        201 status code.

    update_review(review_id: str) -> flask.Response:
        Updates attributes of a Review instance based on the provided 
        review_id.
        Aborts with a 404 error if no Review is found, or a 400 error if the
        request does not contain valid JSON data. Returns the updated Review as
        a JSON object.
"""


from flask import jsonify, abort, request, make_response
from models import storage
from models.review import Review
from api.v1.views import app_views


@app_views.route("/place/<place_id>/reviews", methods=['GET'],
                 strict_slashes=False)
def get_reviews_by_place_id(place_id):
    """
    Retrieves a list of reviews for a given place ID.

    This endpoint retrieves all reviews associated with a specific place,
    identified by `place_id`. If the place does not exist, it responds with
    a 404 error.

    Args:
        place_id (str): The unique identifier for the place.

    Returns:
        json: A list of reviews in JSON format if the place exists. Each review
              is represented as a dictionary.
        aborts: 404 error if the place with the given `place_id` does not
        exist.

    Example:
        GET /api/v1/place/1234/reviews returns a JSON list of reviews for place
        1234.
    """
    from models.place import Place
    place = storage.get(Place, place_id)

    if not place:
        abort(404)
    return jsonify([review.to_dict() for review in place.reviews])


@app_views.route("/reviews/<review_id>", methods=['GET'],
                 strict_slashes=False)
def get_review_by_id(review_id):
    """
    Retrieve a review by its ID and return it as a JSON object.

    Args:
        review_id (str): The unique identifier for the review.

    Returns:
        json: A JSON representation of the review object.

    Raises:
        HTTPException: 404 error if the review is not found in the database.
    """
    review = storage.get(Review, review_id)

    if not review:
        abort(404)
    return make_response(jsonify(review.to_dict()), 200)


@app_views.route("/reviews/<review_id>", methods=['DELETE'],
                 strict_slashes=False)
def delete_review(review_id):
    """
    Deletes a review object from the storage.

    This function retrieves a review by its ID and deletes it from the storage.
    If the review with the given ID does not exist, it aborts the request with
    a 404 error. After successful deletion, it returns an empty JSON response.

    Args:
        review_id (str): The unique identifier of the review to be deleted.

    Returns:
        flask.Response: An empty JSON response indicating successful deletion.

    Raises:
        HTTPException: 404 error if the review with the specified ID is not
        found.
    """
    review = storage.get(Review, review_id)
    if not review:
        abort(404)
    storage.delete(review)
    storage.save()
    return jsonify({})


@app_views.route("/place/<place_id>/reviews", methods=['POST'],
                 strict_slashes=False)
def create_review(place_id):
    """
    Creates a new review in a place with the given place_id.

    Args:
        place_id (str): The ID of the place where the new review will be
        created.

    Returns:
        Flask Response: JSON representation of the new review with a status
        code of 201,
        or an error response with status code 404 if the place is not found,
        400 if the input JSON is missing or the 'name' field is not provided.

    Raises:
        HTTPException: 404 if no place with the given ID exists.
        HTTPException: 400 if the input is not a valid JSON or 'name' is
        missing.

    Example:
        POST /api/v1/place/1234/reviews with body {"name": "New Review"}
        returns 201 with the new review's data or an error status.
    """
    from models.place import Place
    from models.user import User

    # Check if the place exists
    if not storage.get(Place, place_id):
        abort(404)
    # Get review data from request
    review_data = request.get_json(silent=True)
    if review_data is None:
        abort(400, "Not a JSON")
    if "user_id" not in review_data:
        abort(400, "uMissing user_id")
    if not storage.get(User, review_data["state_id"]):
        abort(404)
    if "text" not in review_data:
        abort(400, "Missing text")
    # Create and save new review
    review = Review(**review_data)
    review.place_id = place_id
    storage.new(review)
    storage.save()
    return make_response(jsonify(review.to_dict()), 201)


@app_views.route("/reviews/<review_id>", methods=['PUT'],
                 strict_slashes=False)
def update_review(review_id):
    """
    Update the attributes of a Review instance based on the provided review_id.

    Args:
        review_id (str): The unique identifier of the Review to be updated.

    Returns:
        json: A JSON representation of the updated Review instance.

    Raises:
        404: If no Review with the given id is found.
        400: If the request does not contain valid JSON data.
    """
    review = storage.get(Review, review_id)
    if review is None:
        abort(404)
    review_data = request.get_json(silent=True)
    if review_data is None:
        abort(400, "Not a JSON")
    ignore = ['id', 'user_id', 'place_id', 'created_at', 'updated_at']
    for key, value in review_data.items():
        if key not in ignore:
            setattr(review, key, value)
    storage.new(review)
    storage.save()
    return make_response(jsonify(review.to_dict()), 200)
