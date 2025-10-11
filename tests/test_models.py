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
import uuid
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
        time.sleep(0.01)
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

    def test_find_by_address(self):
        """It should Find Customers by address"""
        people = CustomersFactory.create_batch(10)
        for p in people:
            p.create()
        target = people[0].address
        count = len([p for p in people if p.address == target])
        found = Customers.find_by_address(target)
        self.assertEqual(found.count(), count)
        for p in found:
            self.assertEqual(p.address, target)

    def test_find_by_last_name(self):
        """It should Find Customers by last_name"""
        people = CustomersFactory.create_batch(10)
        for p in people:
            p.create()
        target = people[0].last_name

        # Exact match (fuzzy=False)
        rows_exact = Customers.find_by_last_name(target, fuzzy=False)
        for r in rows_exact:
            self.assertEqual(r.last_name, target)

        # Fuzzy test: partial lowercase match should return results
        rows_fuzzy = Customers.find_by_last_name(target[:2].lower(), fuzzy=True)
        self.assertGreaterEqual(rows_fuzzy.count(), 1)

    def test_find_by_first_name(self):
        """It should Find Customers by first_name"""
        people = CustomersFactory.create_batch(6)
        for p in people:
            p.create()
        target = people[0].first_name

        # Exact match (fuzzy=False)
        rows_exact = Customers.find_by_first_name(target, fuzzy=False)
        for r in rows_exact:
            self.assertEqual(r.first_name, target)

        # Fuzzy test: lowercase partial match should still find records
        rows_fuzzy = Customers.find_by_first_name(target[:2].lower(), fuzzy=True)
        self.assertGreaterEqual(rows_fuzzy.count(), 1)

    def test_find_by_name(self):
        """It should support single-token (first/last), exact full-name (two tokens), and first+last ignoring middle"""
        # Seed data
        c1 = Customers(first_name="Alice", last_name="Smith", address="1 Ave")
        c2 = Customers(first_name="Bob", last_name="Jones", address="2 Ave")
        c3 = Customers(first_name="Alice", last_name="Jones", address="3 Ave")
        c1.create()
        c2.create()
        c3.create()

        # --- Case 1: single token -> search both first and last (default fuzzy=True is fine) ---
        rows = Customers.find_by_name("Alice")
        names = {(r.first_name, r.last_name) for r in rows}
        self.assertIn(("Alice", "Smith"), names)
        self.assertIn(("Alice", "Jones"), names)
        self.assertNotIn(("Bob", "Jones"), names)

        # --- Case 2: two tokens -> exact full name match (set fuzzy=False to enforce exact) ---
        rows = Customers.find_by_name("Alice Jones", fuzzy=False)
        names = {(r.first_name, r.last_name) for r in rows}
        self.assertEqual(names, {("Alice", "Jones")})

        # --- Case 3: more than two tokens -> use first and last, ignore middle (still exact with fuzzy=False) ---
        rows = Customers.find_by_name("Alice Middle Jones", fuzzy=False)
        names = {(r.first_name, r.last_name) for r in rows}
        self.assertEqual(names, {("Alice", "Jones")})

        # --- Case 4: empty input -> empty result ---
        self.assertEqual(Customers.find_by_name("").count(), 0)

    def test_find_by_name_exact_vs_fuzzy(self):
        """It should differentiate between fuzzy and exact name search"""
        c1 = Customers(first_name="Charlie", last_name="Brown", address="11 St")
        c2 = Customers(first_name="Charlotte", last_name="Browning", address="22 St")
        c1.create()
        c2.create()

        # Fuzzy search should find both (matches "Char" and "Brown")
        fuzzy_results = Customers.find_by_name("Char Brown", fuzzy=True)
        names = {(r.first_name, r.last_name) for r in fuzzy_results}
        self.assertIn(("Charlie", "Brown"), names)
        self.assertIn(("Charlotte", "Browning"), names)

        # Exact search should find only precise "Charlie Brown"
        exact_results = Customers.find_by_name("Charlie Brown", fuzzy=False)
        exact_names = {(r.first_name, r.last_name) for r in exact_results}
        self.assertEqual(exact_names, {("Charlie", "Brown")})

    def test_find_by_name_single_token_exact_vs_fuzzy(self):
        """Single-token search should differ between fuzzy and exact modes"""
        # Alice / Alicia to differentiate "Ali" fuzzy vs exact
        a1 = Customers(first_name="Alice", last_name="Smith", address="1 Ave")
        a2 = Customers(first_name="Alicia", last_name="Stone", address="2 Ave")
        a1.create()
        a2.create()

        # fuzzy=True with partial lower "ali" should match both
        fuzzy = Customers.find_by_name("ali", fuzzy=True)
        names_fuzzy = {(r.first_name, r.last_name) for r in fuzzy}
        self.assertIn(("Alice", "Smith"), names_fuzzy)
        self.assertIn(("Alicia", "Stone"), names_fuzzy)

        # fuzzy=False with partial "Ali" -> exact only, so none
        exact_partial = Customers.find_by_name("Ali", fuzzy=False)
        self.assertEqual(exact_partial.count(), 0)

        # fuzzy=False with exact "Alice" -> only Alice Smith
        exact_full = Customers.find_by_name("Alice", fuzzy=False)
        names_exact = {(r.first_name, r.last_name) for r in exact_full}
        self.assertEqual(names_exact, {("Alice", "Smith")})

    def test_find_by_name_two_tokens_fuzzy_substrings(self):
        """Two-token fuzzy search should match by substrings on first AND last"""
        a = Customers(first_name="Alice", last_name="Jones", address="1 Ave")
        b = Customers(first_name="Alice", last_name="Smith", address="2 Ave")
        c = Customers(first_name="Bob", last_name="Jones", address="3 Ave")
        a.create()
        b.create()
        c.create()

        # Substring tokens "Ali" and "Jon" should match only Alice Jones if using AND
        res = Customers.find_by_name("Ali Jon", fuzzy=True)
        names = {(r.first_name, r.last_name) for r in res}
        self.assertIn(("Alice", "Jones"), names)
        # AND semantics exclude these:
        self.assertNotIn(("Alice", "Smith"), names)
        self.assertNotIn(("Bob", "Jones"), names)

    def test_find_not_found_returns_none(self):
        """It should return None when id is not found"""
        self.assertIsNone(Customers.find(uuid.uuid4()))

    def test_repr_contains_names(self):
        """__repr__ should include first and last names"""
        c = Customers(first_name="Jane", last_name="Doe", address="1 Ave")
        text = repr(c)
        self.assertIn("Jane", text)
        self.assertIn("Doe", text)

    def test_deserialize_trims_whitespace(self):
        """deserialize should strip whitespace from fields"""
        c = Customers()
        c.deserialize(
            {"first_name": "  Jane  ", "last_name": "  Doe ", "address": "  1 Ave  "}
        )
        self.assertEqual(c.first_name, "Jane")
        self.assertEqual(c.last_name, "Doe")
        self.assertEqual(c.address, "1 Ave")


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


######################################################################
#  A P P   E R R O R   H A N D L E R S   &   W I R I N G
######################################################################
def _status_code(result):
    """Extract status code from handler return (tuple or Response)."""
    if isinstance(result, tuple):
        if len(result) >= 2:
            status = result[1]
            try:
                return int(status)
            except Exception:
                return int(getattr(status, "value", 0))
        return None
    return getattr(result, "status_code", None)


class TestAppErrorHandlers(TestCaseBase):
    """Directly exercise common error handlers and app wiring"""

    def test_error_handlers_status_codes(self):
        from service.common import error_handlers as eh

        self.assertEqual(_status_code(eh.bad_request(Exception("bad"))), 400)
        self.assertEqual(_status_code(eh.not_found(Exception("missing"))), 404)
        self.assertEqual(
            _status_code(eh.method_not_supported(Exception("method"))), 405
        )
        self.assertEqual(
            _status_code(eh.mediatype_not_supported(Exception("type"))), 415
        )
        self.assertEqual(_status_code(eh.internal_server_error(Exception("boom"))), 500)

    def test_request_validation_error_wrapper(self):
        from service.common import error_handlers as eh

        status = _status_code(
            eh.request_validation_error(DataValidationError("invalid"))
        )
        self.assertEqual(status, 400)

    def test_routes_index(self):
        client = app.test_client()
        resp = client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Customers Demo REST API Service", resp.data)

    def test_cli_db_create_runs(self):
        # invoke the Flask CLI command instead of calling the click.Command directly
        runner = app.test_cli_runner()
        result = runner.invoke(args=["db-create"])
        self.assertEqual(result.exit_code, 0)

        # sanity check: table exists and we can insert after recreation
        with app.app_context():
            Customers(first_name="X", last_name="Y", address="Z").create()
            self.assertEqual(len(Customers.all()), 1)

    def test_log_handlers_init_logging(self):
        from service.common.log_handlers import init_logging

        gunicorn_logger = logging.getLogger("gunicorn.error")
        if not gunicorn_logger.handlers:
            gunicorn_logger.addHandler(logging.StreamHandler())
        init_logging(app, "gunicorn.error")
        self.assertTrue(len(app.logger.handlers) >= 1)
