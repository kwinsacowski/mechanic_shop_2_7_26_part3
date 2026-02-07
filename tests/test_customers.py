import os
import sys
import types
import unittest
from uuid import uuid4

# --- Test-time stubs/overrides ---
try:
    import flask_swagger_ui  # type: ignore
except Exception:
    from flask import Blueprint
    mock = types.ModuleType("flask_swagger_ui")

    def get_swaggerui_blueprint(*args, **kwargs):
        return Blueprint("swaggerui", __name__)

    mock.get_swaggerui_blueprint = get_swaggerui_blueprint
    sys.modules["flask_swagger_ui"] = mock

os.environ.setdefault("DATABASE_URL", "sqlite:///testing.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from app import create_app
from app.extensions import db


class TestCustomers(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI=os.environ["DATABASE_URL"],
        )
        self.client = self.app.test_client()

        with self.app.app_context():
            db.drop_all()
            db.create_all()

        # Seed a customer we can authenticate with
        self.seed_password = "password123"
        self.seed_email = f"seed_{uuid4().hex[:8]}@email.com"

        create_res = self.client.post(
            "/customers/",
            json={
                "name": "Seed Customer",
                "email": self.seed_email,
                "phone_number": "555-123-4567",
                "password": self.seed_password,
            },
        )
        self.assertIn(create_res.status_code, (200, 201))
        self.customer_id = create_res.json.get("id")

        login_res = self.client.post(
            "/customers/login",
            json={"email": self.seed_email, "password": self.seed_password},
        )
        self.assertEqual(login_res.status_code, 200)
        self.token = login_res.json["token"]
        self.auth_headers = {"Authorization": f"Bearer {self.token}"}

    # POST /customers/
    def test_create_customer(self):
        res = self.client.post(
            "/customers/",
            json={
                "name": "Jane Doe",
                "email": f"jane_{uuid4().hex[:8]}@email.com",
                "phone_number": "555-000-0000",
                "password": "strongpass",
            },
        )
        self.assertIn(res.status_code, (200, 201))
        self.assertEqual(res.json["name"], "Jane Doe")
        self.assertNotIn("password", res.json)

    def test_create_customer_negative_missing_fields(self):
        res = self.client.post(
            "/customers/",
            json={"name": "Bad", "email": f"bad_{uuid4().hex[:8]}@email.com"},
        )
        self.assertEqual(res.status_code, 400)

    # POST /customers/login
    def test_login_customer(self):
        res = self.client.post(
            "/customers/login",
            json={"email": self.seed_email, "password": self.seed_password},
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("token", res.json)

    def test_login_customer_negative_invalid_credentials(self):
        res = self.client.post(
            "/customers/login",
            json={"email": self.seed_email, "password": "wrong"},
        )
        self.assertIn(res.status_code, (400, 401))

    def test_login_customer_negative_validation(self):
        with self.assertRaises(AttributeError):
            self.client.post("/customers/login", json={"email": self.seed_email})

    # GET /customers/
    def test_get_customers(self):
        res = self.client.get("/customers/?page=1&per_page=10")
        self.assertEqual(res.status_code, 200)
        self.assertIn("items", res.json)

    # GET /customers/<id>
    def test_get_customer(self):
        res = self.client.get(f"/customers/{self.customer_id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json["id"], self.customer_id)

    def test_get_customer_negative_not_found(self):
        res = self.client.get("/customers/999999")
        self.assertEqual(res.status_code, 404)

    # GET /customers/my-tickets
    def test_get_my_tickets(self):
        res = self.client.get("/customers/my-tickets", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)

    def test_get_my_tickets_negative_missing_token(self):
        res = self.client.get("/customers/my-tickets")
        self.assertEqual(res.status_code, 401)

    # PUT /customers/<id>
    def test_update_customer(self):
        res = self.client.put(
            f"/customers/{self.customer_id}",
            json={"name": "Updated Name"},
            headers=self.auth_headers,
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json["name"], "Updated Name")

    def test_update_customer_negative_forbidden(self):
        other = self.client.post(
            "/customers/",
            json={
                "name": "Other",
                "email": f"other_{uuid4().hex[:8]}@email.com",
                "phone_number": "555-999-9999",
                "password": "password123",
            },
        )
        self.assertIn(other.status_code, (200, 201))
        other_id = other.json["id"]

        res = self.client.put(
            f"/customers/{other_id}",
            json={"name": "Hacked"},
            headers=self.auth_headers,
        )
        self.assertIn(res.status_code, (401, 403))

    # DELETE /customers/<id>
    def test_delete_customer(self):
        res = self.client.delete(f"/customers/{self.customer_id}", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)

    def test_delete_customer_negative_missing_token(self):
        res = self.client.delete(f"/customers/{self.customer_id}")
        self.assertEqual(res.status_code, 401)
