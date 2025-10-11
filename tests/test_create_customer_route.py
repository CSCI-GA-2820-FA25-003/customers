# tests/test_create_customer_route.py
from unittest import TestCase
from wsgi import app

BASE_URL = "/customers"


class TestCreateCustomerRoute(TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.valid = {"first_name": "Jane", "last_name": "Doe", "address": "1 Test Ave"}

    def test_create_customer_success(self):
        """POST with required fields should return 201 and valid JSON"""
        resp = self.client.post(BASE_URL, json=self.valid, content_type="application/json")
        self.assertEqual(resp.status_code, 201)

        data = resp.get_json()
        # check basic structure
        for key in ["id", "first_name", "last_name", "address", "created_at"]:
            self.assertIn(key, data)

        self.assertEqual(data["first_name"], self.valid["first_name"])
        self.assertEqual(data["last_name"], self.valid["last_name"])
        self.assertEqual(data["address"], self.valid["address"])

    def test_create_customer_missing_fields(self):
        """Missing any required field should return 400"""
        for key in list(self.valid.keys()):
            payload = self.valid.copy()
            payload.pop(key)
            resp = self.client.post(BASE_URL, json=payload, content_type="application/json")
            self.assertEqual(resp.status_code, 400)
            self.assertIn(f"Missing or empty field: {key}", resp.get_data(as_text=True))
