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
Customers Service with Swagger


Paths:
------
GET / - Displays a UI for Selenium testing
GET /customers - Returns a list all of the Customers
GET /customers/{id} - Returns the Customer with a given id number
POST /customers - creates a new Customer record in the database
PUT /customers/{id} - updates a Customer record in the database
DELETE /customers/{id} - deletes a Customer record in the database
PUT /customers/{id}/suspend - suspends a Customer account
PUT /customers/{id}/unsuspend - unsuspends a Customer account
"""

import uuid
from flask import current_app as app  # Import Flask application
from flask_restx import Api, Resource, fields, reqparse
from service.models import Customers, DataValidationError
from service.common import status  # HTTP Status Codes

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(
    app,
    version="1.0.0",
    title="Customers Demo REST API Service",
    description="This is a REST API service for managing customer accounts.",
    default="customers",
    default_label="Customer operations",
    doc="/apidocs",
    prefix="/api",
)


######################################################################
# Configure the Root route before OpenAPI
######################################################################
@app.route("/")
def index():
    """Index page"""
    return app.send_static_file("index.html")


######################################################################
# HEALTH CHECK
######################################################################
@app.route("/health")
def health():
    """Health check endpoint for Kubernetes liveness and readiness probes"""
    app.logger.info("Request for health check")
    return {"status": "OK"}, status.HTTP_200_OK


# Define the model so that the docs reflect what can be sent
create_model = api.model(
    "Customer",
    {
        "first_name": fields.String(
            required=True, description="The first name of the Customer"
        ),
        "last_name": fields.String(
            required=True, description="The last name of the Customer"
        ),
        "address": fields.String(
            required=True, description="The address of the Customer"
        ),
        "suspended": fields.Boolean(
            required=False,
            description="Is the Customer account suspended?",
            default=False,
        ),
    },
)

customer_model = api.inherit(
    "CustomerModel",
    create_model,
    {
        "id": fields.String(
            readOnly=True, description="The unique id assigned internally by service"
        ),
        "created_at": fields.String(
            readOnly=True, description="The date/time the customer was created"
        ),
        "updated_at": fields.String(
            readOnly=True, description="The date/time the customer was last updated"
        ),
    },
)

# query string arguments
customer_args = reqparse.RequestParser()
customer_args.add_argument(
    "first_name",
    type=str,
    location="args",
    required=False,
    help="List Customers by first name",
)
customer_args.add_argument(
    "last_name",
    type=str,
    location="args",
    required=False,
    help="List Customers by last name",
)
customer_args.add_argument(
    "address",
    type=str,
    location="args",
    required=False,
    help="List Customers by address",
)


######################################################################
#  PATH: /customers/{id}
######################################################################
@api.route("/customers/<customer_id>")
@api.param("customer_id", "The Customer identifier")
class CustomerResource(Resource):
    """
    CustomerResource class

    Allows the manipulation of a single Customer
    GET /customers{id} - Returns a Customer with the id
    PUT /customers{id} - Update a Customer with the id
    DELETE /customers{id} -  Deletes a Customer with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A CUSTOMER
    # ------------------------------------------------------------------
    @api.doc("get_customers")
    @api.response(404, "Customer not found")
    @api.marshal_with(customer_model)
    def get(self, customer_id):
        """
        Retrieve a single Customer

        This endpoint will return a Customer based on it's id
        """
        app.logger.info("Request to Retrieve a customer with id [%s]", customer_id)
        try:
            # Validate UUID format before querying
            uuid.UUID(customer_id)
        except (ValueError, TypeError):
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        customer = Customers.find(customer_id)
        if not customer:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        return customer.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING CUSTOMER
    # ------------------------------------------------------------------
    @api.doc("update_customers")
    @api.response(404, "Customer not found")
    @api.response(400, "The posted Customer data was not valid")
    @api.expect(customer_model)
    @api.marshal_with(customer_model)
    def put(self, customer_id):
        """
        Update a Customer

        This endpoint will update a Customer based the body that is posted
        """
        app.logger.info("Request to Update a customer with id [%s]", customer_id)
        try:
            # Validate UUID format before querying
            uuid.UUID(customer_id)
        except (ValueError, TypeError):
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        customer = Customers.find(customer_id)
        if not customer:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        try:
            customer.deserialize(data)
            customer.id = customer_id
            customer.update()
        except DataValidationError as e:
            abort(
                status.HTTP_400_BAD_REQUEST,
                str(e),
            )
        return customer.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A CUSTOMER
    # ------------------------------------------------------------------
    @api.doc("delete_customers")
    @api.response(204, "Customer deleted")
    def delete(self, customer_id):
        """
        Delete a Customer

        This endpoint will delete a Customer based the id specified in the path
        """
        app.logger.info("Request to Delete a customer with id [%s]", customer_id)
        try:
            # Validate UUID format before querying
            uuid.UUID(customer_id)
        except (ValueError, TypeError):
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        customer = Customers.find(customer_id)
        if customer:
            customer.delete()
            app.logger.info("Customer with id [%s] was deleted", customer_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /customers
######################################################################
@api.route("/customers", strict_slashes=False)
class CustomerCollection(Resource):
    """Handles all interactions with collections of Customers"""

    # ------------------------------------------------------------------
    # LIST ALL CUSTOMERS
    # ------------------------------------------------------------------
    @api.doc("list_customers")
    @api.expect(customer_args, validate=True)
    @api.marshal_list_with(customer_model)
    def get(self):
        """Returns all of the Customers"""
        app.logger.info("Request to list Customers...")
        customers = []
        args = customer_args.parse_args()
        # Build a dynamic query by adding filters for each parameter that exists
        query = Customers.query
        applied = []

        if args["first_name"]:
            app.logger.info("Filtering by first_name: %s", args["first_name"])
            query = query.filter(Customers.first_name.ilike(f"%{args['first_name']}%"))
            applied.append(f"first_name={args['first_name']}")
        if args["last_name"]:
            app.logger.info("Filtering by last_name: %s", args["last_name"])
            query = query.filter(Customers.last_name.ilike(f"%{args['last_name']}%"))
            applied.append(f"last_name={args['last_name']}")
        if args["address"]:
            app.logger.info("Filtering by address: %s", args["address"])
            query = query.filter(Customers.address.ilike(f"%{args['address']}%"))
            applied.append(f"address={args['address']}")

        # If any filters were applied, execute the filtered query
        # Otherwise, return all customers
        if applied:
            app.logger.info("Find with filters: %s", ", ".join(applied))
            customers = query.all()
        else:
            app.logger.info("Returning unfiltered list.")
            customers = Customers.all()

        app.logger.info("[%s] Customers returned", len(customers))
        results = [customer.serialize() for customer in customers]
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW CUSTOMER
    # ------------------------------------------------------------------
    @api.doc("create_customers")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_model)
    @api.marshal_with(customer_model, code=201)
    def post(self):
        """
        Creates a Customer
        This endpoint will create a Customer based the data in the body that is posted
        """
        app.logger.info("Request to Create a Customer")
        customer = Customers()
        app.logger.debug("Payload = %s", api.payload)
        try:
            customer.deserialize(api.payload)
            customer.create()
        except DataValidationError as e:
            abort(
                status.HTTP_400_BAD_REQUEST,
                str(e),
            )
        app.logger.info("Customer with new id [%s] created!", customer.id)
        location_url = api.url_for(
            CustomerResource, customer_id=customer.id, _external=True
        )
        return customer.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /customers/{id}/suspend
######################################################################
@api.route("/customers/<customer_id>/suspend")
@api.param("customer_id", "The Customer identifier")
class SuspendResource(Resource):
    """Suspend actions on a Customer"""

    @api.doc("suspend_customers")
    @api.response(404, "Customer not found")
    @api.marshal_with(customer_model)
    def put(self, customer_id):
        """
        Suspend a Customer

        This endpoint will suspend a Customer account
        """
        app.logger.info("Request to suspend customer with id [%s]", customer_id)
        try:
            # Validate UUID format before querying
            uuid.UUID(customer_id)
        except (ValueError, TypeError):
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        customer = Customers.find(customer_id)
        if not customer:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        customer.suspend()
        app.logger.info("Customer with ID [%s] suspended.", customer_id)
        return customer.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /customers/{id}/unsuspend
######################################################################
@api.route("/customers/<customer_id>/unsuspend")
@api.param("customer_id", "The Customer identifier")
class UnsuspendResource(Resource):
    """Unsuspend actions on a Customer"""

    @api.doc("unsuspend_customers")
    @api.response(404, "Customer not found")
    @api.marshal_with(customer_model)
    def put(self, customer_id):
        """
        Unsuspend a Customer

        This endpoint will unsuspend a Customer account
        """
        app.logger.info("Request to unsuspend customer with id [%s]", customer_id)
        try:
            # Validate UUID format before querying
            uuid.UUID(customer_id)
        except (ValueError, TypeError):
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        customer = Customers.find(customer_id)
        if not customer:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        customer.unsuspend()
        app.logger.info("Customer with ID [%s] unsuspended.", customer_id)
        return customer.serialize(), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)
