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
from urllib.parse import quote_plus
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

    ########################################################
    # Utility function to bulk create customers
    ############################################################

    def _create_customers_in_db(self, count: int = 1) -> list:
        """Factory method to create customers in bulk directly in the database"""
        customers = []
        for _ in range(count):
            test_customer = CustomersFactory()
            test_customer.create()
            customers.append(test_customer)
        return customers

    def test_index(self):
        """It should call the home page and return service info"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        # check service metadata
        self.assertEqual(data["name"], "Customers REST API Service")
        self.assertEqual(data["version"], "2.0")
        self.assertEqual(data["status"], "OK")

        # check paths dictionary
        self.assertIn("paths", data)
        self.assertIsInstance(data["paths"], dict)

        paths = data["paths"]
        self.assertEqual(paths["List/Create Customers"], BASE_URL)
        self.assertEqual(
            paths["Read/Update/Delete Customer"], f"{BASE_URL}/<customer_id>"
        )
        self.assertEqual(paths["Suspend Customer"], f"{BASE_URL}/<customer_id>/suspend")
        self.assertEqual(
            paths["Unsuspend Customer"], f"{BASE_URL}/<customer_id>/unsuspend"
        )

    ######################################################################
    #  H E A L T H   C H E C K   T E S T S
    ######################################################################

    def test_health_check(self):
        """It should return health status with HTTP 200 OK"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify response is JSON
        self.assertEqual(response.content_type, "application/json")

        # Verify response body
        data = response.get_json()
        self.assertIsNotNone(data)
        self.assertIn("status", data)
        self.assertEqual(data["status"], "OK")

    def test_health_check_response_format(self):
        """It should return exactly the expected JSON format"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertEqual(data, {"status": "OK"})

    ######################################################################
    #  C R E A T E   C U S T O M E R   T E S T S
    ######################################################################

    def test_create_customer_success(self):
        """It should create a customer successfully"""
        payload = {
            "first_name": "John",
            "last_name": "Doe",
            "address": "123 Main Street",
        }
        resp = self.client.post("/customers", json=payload)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        self.assertEqual(data["first_name"], "John")
        self.assertEqual(data["last_name"], "Doe")
        self.assertEqual(data["address"], "123 Main Street")
        self.assertIn("id", data)
        self.assertIn("Location", resp.headers)

    def test_create_customer_missing_fields(self):
        """It should return 400 if required fields are missing"""
        payload = {"first_name": "John"}  # missing last_name, address
        resp = self.client.post("/customers", json=payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_customer_blank_fields(self):
        """It should return 400 if fields are blank strings"""
        payload = {"first_name": " ", "last_name": "Doe", "address": " "}
        resp = self.client.post("/customers", json=payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_customer_invalid_json(self):
        """It should return 415 if content-type is not application/json"""
        resp = self.client.post(
            "/customers", data="not-json", content_type="text/plain"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    ######################################################################
    #  U P D A T E   C U S T O M E R   T E S T S
    ######################################################################

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

    def test_update_customer_json_charset_content_type(self):
        """It should return 200 for a correct content type with charset"""
        test_customer = CustomersFactory()
        test_customer.create()
        new_customer = test_customer.serialize()
        new_customer["first_name"] = "New Name"

        response = self.client.put(
            f"{BASE_URL}/{test_customer.id}",
            json=new_customer,
            content_type="application/json; charset=utf-8",  # JSON with charset
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    ######################################################################
    #  L I S T   C U S T O M E R   T E S T S
    ######################################################################

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

    # pylint: disable=too-many-arguments
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

    ######################################################################
    #  R E A D   C U S T O M E R   T E S T S
    ######################################################################

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

    ######################################################################
    #  D E L E T E   C U S T O M E R   T E S T S
    ######################################################################

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
        """It should return 204 No Content when deleting a non-existent Customer"""
        test_customer = CustomersFactory()
        customers = test_customer.serialize()
        bad_id = customers["id"]
        response = self.client.delete(f"{BASE_URL}/{bad_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    def test_delete_customer_bad_request(self):
        """It should return 404 for an invalid ID format in the URL"""
        response = self.client.delete(f"{BASE_URL}/this-is-not-a-uuid")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    #  S U S P E N D / U N S U S P E N D   C U S T O M E R   T E S T S
    ######################################################################

    def test_suspend_active_customer(self):
        """It should Suspend an active customer"""
        # Create a customer with suspended=False (default)
        test_customer = self._create_customers_in_db(1)[0]
        self.assertFalse(test_customer.suspended)

        # Suspend the customer
        response = self.client.put(f"{BASE_URL}/{test_customer.id}/suspend")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertTrue(data["suspended"])

        response = self.client.get(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertTrue(data["suspended"])

    def test_suspend_already_suspended_customer(self):
        """It should handle suspending an already suspended customer"""
        # Create and suspend a customer
        test_customer = self._create_customers_in_db(1)[0]
        test_customer.suspend()
        self.assertTrue(test_customer.suspended)

        # Suspend again
        response = self.client.put(f"{BASE_URL}/{test_customer.id}/suspend")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Checking customer remains suspended
        data = response.get_json()
        self.assertTrue(data["suspended"])

    def test_unsuspend_suspended_customer(self):
        """It should Unsuspend a suspended customer"""
        # Create and suspend a customer
        test_customer = self._create_customers_in_db(1)[0]
        test_customer.suspend()
        self.assertTrue(test_customer.suspended)

        # Unsuspend the customer
        response = self.client.put(f"{BASE_URL}/{test_customer.id}/unsuspend")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertFalse(data["suspended"])

        response = self.client.get(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertFalse(data["suspended"])

    def test_unsuspend_already_active_customer(self):
        """It should handle unsuspending an already active customer"""
        # Create a customer (default suspended=False)
        test_customer = self._create_customers_in_db(1)[0]
        self.assertFalse(test_customer.suspended)

        # Unsuspend an already active customer
        response = self.client.put(f"{BASE_URL}/{test_customer.id}/unsuspend")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertFalse(data["suspended"])

    def test_suspend_non_existent_customer(self):
        """It should return 404 when suspending a non-existent customer"""

        test_customer = CustomersFactory()
        non_existent_id = test_customer.id

        response = self.client.put(f"{BASE_URL}/{non_existent_id}/suspend")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    def test_unsuspend_non_existent_customer(self):
        """It should return 404 when unsuspending a non-existent customer"""

        test_customer = CustomersFactory()
        non_existent_id = test_customer.id

        response = self.client.put(f"{BASE_URL}/{non_existent_id}/unsuspend")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])
