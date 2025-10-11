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
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Customers Demo REST API Service",
            version="1.0",
            paths=url_for("list_customers", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


# LIST ALL CUSTOMERS
######################################################################
@app.route("/customers", methods=["GET"])
def list_customers():
    """Returns all of the customers (optionally filtered by multiple fields)"""
    app.logger.info("Request for customer list")

    # Parse any arguments from the query string
    first_name = request.args.get("first_name")
    last_name = request.args.get("last_name")
    address = request.args.get("address")

    # Build a dynamic query by adding filters for each parameter that exists
    query = Customers.query
    applied = []

    if first_name:
        query = query.filter(Customers.first_name == first_name)
        applied.append(f"first_name={first_name}")
    if last_name:
        query = query.filter(Customers.last_name == last_name)
        applied.append(f"last_name={last_name}")
    if address:
        query = query.filter(Customers.address == address)
        applied.append(f"address={address}")

    # If any filters were applied, execute the filtered query
    # Otherwise, return all customers
    if applied:
        app.logger.info("Find with filters: %s", ", ".join(applied))
        customers = query.all()
    else:
        app.logger.info("Find all customers")
        customers = Customers.all()

    results = [customer.serialize() for customer in customers]
    app.logger.info("Returning %d customers", len(results))
    return jsonify(results), status.HTTP_200_OK


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
