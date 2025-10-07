######################################################################
# Copyright 2016, 2024 John J. Rofrano.
# All Rights Reserved. Licensed under the Apache License, Version 2.0
######################################################################

"""
Test cases for Customers Model
"""

# pylint: disable=duplicate-code
import os
import time
import logging
from datetime import datetime
from unittest import TestCase
from unittest.mock import patch

from wsgi import app
from service.models import Customers, DataValidationError, db
from .factories import CustomersFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  B A S E   T E S T   C A S E S
######################################################################
class TestCaseBase(TestCase):
    """Base Test Case for common setup"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Customers).delete()
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()


######################################################################
#  C U S T O M E R S   M O D E L   T E S T   C A S E S
######################################################################
class TestCustomersModel(TestCaseBase):
    """Customers Model CRUD & Validation Tests"""

    def test_create_a_customer(self):
        """It should Create a Customer (not persisted) and assert fields exist"""
        c = Customers(first_name="Jane", last_name="Doe", address="1 New Ave")
        self.assertIsNone(c.id)
        self.assertEqual(c.first_name, "Jane")
        self.assertEqual(c.last_name, "Doe")
        self.assertEqual(c.address, "1 New Ave")
        self.assertIsNone(c.created_at)
        self.assertIsNone(c.updated_at)
        self.assertIn("Customer Jane Doe", str(c))

    def test_add_a_customer(self):
        """It should Create a Customer and add it to the database"""
        customers = Customers.all()
        self.assertEqual(customers, [])
        c = Customers(first_name="Jane", last_name="Doe", address="1 New Ave")
        c.create()
        self.assertIsNotNone(c.id)
        customers = Customers.all()
        self.assertEqual(len(customers), 1)
        self.assertIsInstance(customers[0].created_at, datetime)
        self.assertIsInstance(customers[0].updated_at, datetime)

    def test_read_a_customer(self):
        """It should Read a Customer by id"""
        c = CustomersFactory()
        c.create()
        self.assertIsNotNone(c.id)
        found = Customers.find(c.id)
        self.assertEqual(found.id, c.id)
        self.assertEqual(found.first_name, c.first_name)
        self.assertEqual(found.last_name, c.last_name)
        self.assertEqual(found.address, c.address)

    def test_update_a_customer(self):
        """It should Update a Customer's address and bump updated_at"""
        c = CustomersFactory()
        c.create()
        old_updated_at = c.updated_at
        c.address = "99 Updated Road"
        time.sleep(0.01)  # ensure timestamp difference
        c.update()
        self.assertEqual(Customers.find(c.id).address, "99 Updated Road")
        self.assertGreaterEqual(c.updated_at, old_updated_at)

    def test_update_no_id(self):
        """It should not Update a Customer with no id"""
        c = Customers(first_name="A", last_name="B", address="1 Ave")
        self.assertRaises(DataValidationError, c.update)

    def test_delete_a_customer(self):
        """It should Delete a Customer"""
        c = CustomersFactory()
        c.create()
        self.assertEqual(len(Customers.all()), 1)
        c.delete()
        self.assertEqual(len(Customers.all()), 0)

    def test_list_all_customers(self):
        """It should List all Customers in the database"""
        self.assertEqual(Customers.all(), [])
        for _ in range(5):
            c = CustomersFactory()
            c.create()
        self.assertEqual(len(Customers.all()), 5)

    def test_serialize_a_customer(self):
        """It should serialize a Customer"""
        c = CustomersFactory()
        c.create()
        data = c.serialize()
        self.assertIsNotNone(data)
        self.assertIn("id", data)
        self.assertEqual(data["first_name"], c.first_name)
        self.assertEqual(data["last_name"], c.last_name)
        self.assertEqual(data["address"], c.address)
        self.assertIsNotNone(data["created_at"])
        self.assertIsNotNone(data["updated_at"])

    def test_deserialize_a_customer(self):
        """It should de-serialize a Customer"""
        payload = {
            "first_name": "Jane",
            "last_name": "Doe",
            "address": "1 New Ave",
        }
        c = Customers()
        c.deserialize(payload)
        self.assertIsNone(c.id)
        self.assertEqual(c.first_name, "Jane")
        self.assertEqual(c.last_name, "Doe")
        self.assertEqual(c.address, "1 New Ave")

    def test_deserialize_missing_data(self):
        """It should not deserialize a Customer with missing fields"""
        c = Customers()
        self.assertRaises(DataValidationError, c.deserialize, {"first_name": "A"})
        self.assertRaises(
            DataValidationError, c.deserialize, {"first_name": "A", "last_name": "B"}
        )

    def test_deserialize_bad_data_type(self):
        """It should not deserialize bad data types"""
        c = Customers()
        self.assertRaises(DataValidationError, c.deserialize, "not a dict")

    def test_constraint_address_blank(self):
        """It should reject insert when address is empty or only spaces (DB CHECK)"""
        c = Customers(first_name="Jane", last_name="Doe", address="   ")
        self.assertRaises(DataValidationError, c.create)

    def test_constraint_first_last_null(self):
        """It should reject insert when first_name or last_name is NULL (NOT NULL)"""
        c1 = Customers(first_name=None, last_name="Doe", address="1 Ave")
        c2 = Customers(first_name="Jane", last_name=None, address="1 Ave")
        self.assertRaises(DataValidationError, c1.create)
        self.assertRaises(DataValidationError, c2.create)

    def test_find_by_last_name(self):
        """It should Find Customers by last_name"""
        people = CustomersFactory.create_batch(10)
        for p in people:
            p.create()
        target = people[0].last_name
        expected = len([p for p in people if p.last_name == target])
        found = Customers.find_by_last_name(target)
        self.assertEqual(found.count(), expected)
        for row in found:
            self.assertEqual(row.last_name, target)


######################################################################
#  T E S T   E X C E P T I O N   H A N D L E R S
######################################################################
class TestExceptionHandlers(TestCaseBase):
    """Customers Model Exception Handlers"""

    @patch("service.models.db.session.commit")
    def test_create_exception(self, exception_mock):
        """It should catch a create exception and raise DataValidationError"""
        exception_mock.side_effect = Exception()
        c = CustomersFactory()
        self.assertRaises(DataValidationError, c.create)

    def test_update_exception(self):
        """It should catch an update exception and raise DataValidationError"""
        c = CustomersFactory()
        c.create()
        with patch("service.models.db.session.commit") as commit_mock:
            commit_mock.side_effect = Exception()
            self.assertRaises(DataValidationError, c.update)

    def test_delete_exception(self):
        """It should catch a delete exception and raise DataValidationError"""
        c = CustomersFactory()
        c.create()
        with patch("service.models.db.session.commit") as commit_mock:
            commit_mock.side_effect = Exception()
            self.assertRaises(DataValidationError, c.delete)
