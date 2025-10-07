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
YourResourceModel Service

This service implements a REST API that allows you to Create, Read, Update
and Delete YourResourceModel
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import YourResourceModel
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
    Creates a new customer record based on JSON body input.
    Expected fields:
        - first_name
        - last_name
        - email
        - address
        - password
    """
    app.logger.info("Request to create a new customer")

    data = request.get_json()
    required_fields = ["first_name", "last_name", "email", "address", "password"]

    # Check for missing fields
    for field in required_fields:
        if field not in data or not data[field]:
            abort(400, description=f"Missing or empty field: {field}")

    # Example of a mock customer record (no real DB yet)
    customer = {
        "id": 1,
        "first_name": data["first_name"],
        "last_name": data["last_name"],
        "email": data["email"],
        "address": data["address"],
        "created_at": "2025-10-07T00:00:00Z",
    }

    return jsonify(customer), status.HTTP_201_CREATED



######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Todo: Place your REST API code here ...
