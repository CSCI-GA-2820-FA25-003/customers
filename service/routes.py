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
from service.models import Customers
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

