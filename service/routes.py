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

from flask import jsonify, request
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
#  R E S T   A P I   E N D P O I N T S
######################################################################


# LIST ALL CUSTOMERS
######################################################################
@app.route("/customers", methods=["GET"])
def list_customers():
    """Returns all of the customers"""
    app.logger.info("Request for customer list")

    customers = []

    # Parse any arguments from the query string
    id = request.args.get("id")
    first_name = request.args.get("first_name")
    last_name = request.args.get("last_name")

    if id:
        app.logger.info("Find by id: %s", id)
        customers = Customers.find(id)
    elif first_name:
        app.logger.info("Find by first name: %s", first_name)
        customers = Customers.find_by_first_name(first_name)
    elif last_name:
        app.logger.info("Find by last name: %s", last_name)
        customers = Customers.find_by_last_name(last_name)
    else:
        app.logger.info("Find all")
        customers = Customers.all()

    results = [customer.serialize() for customer in customers]
    app.logger.info("Returning %d customers", len(results))
    return jsonify(results), status.HTTP_200_OK
