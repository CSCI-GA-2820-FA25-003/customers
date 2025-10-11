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
TestCustomers API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Customers
from tests.factories import CustomersFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/customers"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestCustomersService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Customers).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], "Customers Demo REST API Service")

    def test_update_customers(self):
        """It should Update an existing Customers"""
        # create a customers to update
        test_customers = CustomersFactory()
        test_customers.create()

        # response = self.client.post(BASE_URL, json=test_customers.serialize())
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the customers
        new_customers = test_customers.serialize()
        # new_customers = response.get_json()
        logging.debug(new_customers)

        # check for each field being updated individually
        valid_fields = ["first_name", "last_name", "address"]
        for field in valid_fields:
            temp = new_customers.copy()
            temp[field] = "unknown"
            response = self.client.put(f"{BASE_URL}/{temp['id']}", json=temp)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            updated_customers = response.get_json()
            for f in valid_fields:
                if f == field:
                    self.assertEqual(
                        updated_customers[f],
                        "unknown",
                        msg=f"Field {f} not updated correctly when updating {field}",
                    )
                else:
                    self.assertEqual(
                        updated_customers[f],
                        new_customers[f],
                        msg=f"Field {f} changed when updating {field}",
                    )

    def test_update_customers_not_found(self):
        """It should not Update a Customers that is not found"""
        # create a customers to update
        test_customers = CustomersFactory()
        customers = test_customers.serialize()
        response = self.client.put(f"{BASE_URL}/{customers['id']}", json=customers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_customers_bad_request(self):
        """It should not Update a Customers with bad request"""
        # create a customers to update
        test_customers = CustomersFactory()
        test_customers.create()
        # response = self.client.post(BASE_URL, json=test_customers.serialize())
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the customers
        new_customers = test_customers.serialize()
        # new_customers = response.get_json()
        logging.debug(new_customers)

        # check when non-empty field was updated to empty returns bad request
        non_empty_fields = ["first_name", "last_name", "address"]
        for field in non_empty_fields:
            temp = new_customers.copy()
            temp[field] = ""
            response = self.client.put(f"{BASE_URL}/{temp['id']}", json=temp)
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                msg=f"Updating {field} to empty did not return 400",
            )

        # check when missing or empty body returns bad request
        response = self.client.put(f"{BASE_URL}/{new_customers['id']}", json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # check when body with invalid attributes returns bad request
        response = self.client.put(
            f"{BASE_URL}/{new_customers['id']}", json={"foo": "bar"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_customer_no_content_type(self):
        """It should return 415 for a missing Content-Type header"""
        test_customer = CustomersFactory()
        test_customer.create()

        response = self.client.put(
            f"{BASE_URL}/{test_customer.id}",
            # No content_type specified
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_customer_wrong_content_type(self):
        """It should return 415 for an unsupported media type"""
        test_customer = CustomersFactory()
        test_customer.create()

        response = self.client.put(
            f"{BASE_URL}/{test_customer.id}",
            data="hello world",
            content_type="text/plain",  # Not JSON
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
