# tests/test_create_customer_route.py
"""
Route tests for POST /customers
NOTE: This version matches the current minimal route behavior that only
validates required fields and returns a JSON payload with 201.
Once the route persists to the DB (using Customers.create()), we can
extend these tests to also verify DB side-effects.
"""

import os
import json
from unittest import TestCase

from wsgi import app
from service.models import db, Customers  # keep imports consistent with team
# from .factories import CustomersFactory  # not needed yet, reserved for later

BASE_URL = "/customers"

class TestCreateCustomerRoute(TestCase):
    """POST /customers route tests (minimal version)"""

    @classmethod
    def setUpClass(cls):
        app.testing = True

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        # keep DB clean (harmless even if route doesn't persist yet)
        db.session.query(Customers).delete()
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    ##################################################################
    # Happy path
    ##################################################################
    def test_create_customer_success(self):
        """It should return 201 and a customer JSON when payload is valid"""
        payload = {
            "first_name": "Jane",
            "last_name": "Doe",
            "address": "1 Test Ave",
        }
        resp = self.client.post(
            BASE_URL,
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        # basic shape checks (the current route returns a JSON with these keys)
        self.assertIsInstance(data, dict)
        for key in ("id", "first_name", "last_name", "address"):
            self.assertIn(key, data)

        self.assertEqual(data["first_name"], payload["first_name"])
        self.assertEqual(data["last_name"], payload["last_name"])
        self.assertEqual(data["address"], payload["address"])

    ##################################################################
    # Missing required fields -> 400
    ##################################################################
    def test_create_customer_missing_first_name(self):
        payload = {"last_name": "Doe", "address": "1 Ave"}
        resp = self.client.post(
            BASE_URL, data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(resp.status_code, 400)

    def test_create_customer_missing_last_name(self):
        payload = {"first_name": "Jane", "address": "1 Ave"}
        resp = self.client.post(
            BASE_URL, data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(resp.status_code, 400)

    def test_create_customer_missing_address(self):
        payload = {"first_name": "Jane", "last_name": "Doe"}
        resp = self.client.post(
            BASE_URL, data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(resp.status_code, 400)
