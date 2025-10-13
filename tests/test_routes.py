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
from urllib.parse import quote_plus

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

    # Todo: Add your test cases here...

    # ----------------------------------------------------------
    # TEST LIST
    # ----------------------------------------------------------
    def test_get_customer_list(self):
        """It should Get a list of Customers"""
        self._create_customers_in_db(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    # ----------------------------------------------------------
    # TEST QUERY
    # ----------------------------------------------------------

    def test_query_by_firstname(self):
        """It should Query Customers by frist name"""
        customers = self._create_customers_in_db(5)
        test_name = customers[0].first_name
        name_count = len(
            [customer for customer in customers if customer.first_name == test_name]
        )
        response = self.client.get(
            BASE_URL, query_string=f"first_name={quote_plus(test_name)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), name_count)
        for customer in data:
            self.assertEqual(customer["first_name"], test_name)

    def test_query_by_lastname(self):
        """It should Query Customers by last name"""
        customers = self._create_customers_in_db(5)
        test_name = customers[0].last_name
        name_count = len(
            [customer for customer in customers if customer.last_name == test_name]
        )
        response = self.client.get(
            BASE_URL, query_string=f"last_name={quote_plus(test_name)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), name_count)
        for customer in data:
            self.assertEqual(customer["last_name"], test_name)

    def test_query_by_address(self):
        """It should Query Customers by address"""
        customers = self._create_customers_in_db(5)
        test_address = customers[0].address
        address_count = len(
            [customer for customer in customers if customer.address == test_address]
        )
        response = self.client.get(
            BASE_URL, query_string=f"address={quote_plus(test_address)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), address_count)
        for customer in data:
            self.assertEqual(customer["address"], test_address)

    def _expect_and_assert(
        self, customers, resp_json, *, first_name=None, last_name=None, address=None
    ):
        expected = [
            c
            for c in customers
            if (first_name is None or c.first_name == first_name)
            and (last_name is None or c.last_name == last_name)
            and (address is None or c.address == address)
        ]
        self.assertEqual(len(resp_json), len(expected))
        for item in resp_json:
            if first_name is not None:
                self.assertEqual(item["first_name"], first_name)
            if last_name is not None:
                self.assertEqual(item["last_name"], last_name)
            if address is not None:
                self.assertEqual(item["address"], address)

    def test_query_by_first_and_last(self):
        """It should query customers by first name and last name"""
        customers = self._create_customers_in_db(5)
        c = customers[0]
        response = self.client.get(
            BASE_URL,
            query_string=f"first_name={quote_plus(c.first_name)}&last_name={quote_plus(c.last_name)}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self._expect_and_assert(
            customers, data, first_name=c.first_name, last_name=c.last_name
        )

    def test_query_by_first_and_address(self):
        """It should query customers by first name and address"""
        customers = self._create_customers_in_db(5)
        c = customers[0]
        response = self.client.get(
            BASE_URL,
            query_string=f"first_name={quote_plus(c.first_name)}&address={quote_plus(c.address)}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self._expect_and_assert(
            customers, data, first_name=c.first_name, address=c.address
        )

    def test_query_by_last_and_address(self):
        """It should query customers by last name and address"""
        customers = self._create_customers_in_db(5)
        c = customers[0]
        response = self.client.get(
            BASE_URL,
            query_string=f"last_name={quote_plus(c.last_name)}&address={quote_plus(c.address)}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self._expect_and_assert(
            customers, data, last_name=c.last_name, address=c.address
        )

    def test_query_by_all_three(self):
        """It should query customers by first name, last name and address"""
        customers = self._create_customers_in_db(5)
        c = customers[0]
        response = self.client.get(
            BASE_URL,
            query_string=(
                f"first_name={quote_plus(c.first_name)}&"
                f"last_name={quote_plus(c.last_name)}&"
                f"address={quote_plus(c.address)}"
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self._expect_and_assert(
            customers,
            data,
            first_name=c.first_name,
            last_name=c.last_name,
            address=c.address,
        )

    def test_query_with_no_match_returns_empty(self):
        """It should return an empty list when no customers match the query"""
        self._create_customers_in_db(5)
        response = self.client.get(
            BASE_URL,
            query_string="first_name=__NO_SUCH_NAME__&last_name=__NO_SUCH_LAST__",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)
