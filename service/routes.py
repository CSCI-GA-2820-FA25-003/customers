######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Customers Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Customers
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Customers, DataValidationError
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
# CREATE A CUSTOMER
######################################################################
@app.route("/customers", methods=["POST"])
def create_customer():
    """
    Creates a new Customer
    POST /customers
    """
    app.logger.info("Request to create a new Customer")

    # Content-Type must be JSON
    if not request.is_json:
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            description="Content-Type must be application/json",
        )

    data = request.get_json()
    customer = Customers()

    try:
        customer.deserialize(data)
        customer.create()
    except Exception as e:
        app.logger.error("Error creating customer: %s", str(e))
        abort(status.HTTP_400_BAD_REQUEST, description=str(e))

    app.logger.info("Customer created successfully: %s", customer.id)
    resp = jsonify(customer.serialize())
    resp.status_code = status.HTTP_201_CREATED
    resp.headers["Location"] = f"/customers/{customer.id}"
    return resp


@app.route("/customers/<uuid:customers_id>", methods=["PUT"])
def update_customers(customers_id):
    """
    Update a Customers

    This endpoint will update a Customers based the body that is posted
    """
    app.logger.info("Request to Update a customers with id [%s]", customers_id)
    check_content_type("application/json")

    # Attempt to find the Customers and abort if not found
    customers = Customers.find(customers_id)
    if not customers:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Customers with id '{customers_id}' was not found.",
        )

    # Update the Customers with the new data
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    try:
        customers.deserialize(data)
    except DataValidationError as e:
        abort(status.HTTP_400_BAD_REQUEST, f"{e}")

    # Save the updates to the database
    customers.update()

    app.logger.info("Customers with ID: %s updated.", customers.id)
    return jsonify(customers.serialize()), status.HTTP_200_OK


def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"].lower().startswith(content_type):
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# READ A CUSTOMER
######################################################################
@app.route("/customers/<uuid:customer_id>", methods=["GET"])
def get_customers(customer_id):
    """
    Retrieve a single Customer

    This endpoint will return a Customer based on it's id
    """
    app.logger.info("Request to Retrieve a customer with id [%s]", customer_id)

    # Attempt to find the Customer and abort if not found
    customer = Customers.find(customer_id)
    if not customer:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Customer with id '{customer_id}' was not found.",
        )

    app.logger.info(
        "Returning customer: %s %s", customer.first_name, customer.last_name
    )
    return jsonify(customer.serialize()), status.HTTP_200_OK
