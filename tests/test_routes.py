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
from .factories import CustomersFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/customers"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
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

    ########################################################
    # Utility function to bulk create customers
    ############################################################
    def _create_customers_in_db(self, count: int = 1) -> list:
        """Factory method to create customers in bulk directly in the database"""
        customers = []
        for _ in range(count):
            test_customer = CustomersFactory()
            # The create() method is from your Customers model in models.py
            test_customer.create()
            customers.append(test_customer)
        return customers

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------

    def test_get_customer(self):
        """It should Get a single Customer"""
        # get the id of a Customer
        test_customer = self._create_customers_in_db(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertEqual(data["id"], str(test_customer.id))
        self.assertEqual(data["first_name"], test_customer.first_name)
        self.assertEqual(data["last_name"], test_customer.last_name)
        self.assertEqual(data["address"], test_customer.address)

    def test_get_customer_not_found(self):
        """It should not Get a Customer thats not found"""
        test_customer = CustomersFactory()
        customers = test_customer.serialize()
        bad_id = customers["id"]
        response = self.client.get(f"{BASE_URL}/{bad_id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_get_customer_bad_request(self):
        """It should return a 404 for an invalid ID format"""
        response = self.client.get(f"{BASE_URL}/this-is-not-a-uuid")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_method_not_allowed(self):
        """It should not allow a POST request on the /customers/{id} URL"""
        test_customer = self._create_customers_in_db(1)[0]
        response = self.client.post(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # ----------------------------------------------------------
    # TEST DELETE
    # ----------------------------------------------------------

    def test_delete_customer(self):
        """It should Delete an existing Customer"""
        # Create a customer to delete
        test_customer = self._create_customers_in_db(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

        # Verifying that the customer is gone
        response = self.client.get(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_non_existent_customer(self):
        """It should return 404 when deleting a non-existent Customer"""
        test_customer = CustomersFactory()
        customers = test_customer.serialize()
        bad_id = customers["id"]
        response = self.client.delete(f"{BASE_URL}/{bad_id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_delete_customer_bad_request(self):
        """It should return 404 for an invalid ID format in the URL"""
        response = self.client.delete(f"{BASE_URL}/this-is-not-a-uuid")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
