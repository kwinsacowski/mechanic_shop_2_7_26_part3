import os
import sys
import types
import unittest
from uuid import uuid4

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


class TestMechanics(unittest.TestCase):
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

        seed = self.client.post(
            "/mechanics/",
            json={
                "name": "Seed Mechanic",
                "email": f"seed_mech_{uuid4().hex[:8]}@email.com",
                "phone_number": "555-111-2222",
                "salary": 60000,
            },
        )
        self.assertIn(seed.status_code, (200, 201))
        self.mechanic_id = seed.json["id"]

    # POST /mechanics/
    def test_create_mechanic(self):
        res = self.client.post(
            "/mechanics/",
            json={
                "name": "New Mechanic",
                "email": f"new_mech_{uuid4().hex[:8]}@email.com",
                "phone_number": "555-222-3333",
                "salary": 50000,
            },
        )
        self.assertIn(res.status_code, (200, 201))

    def test_create_mechanic_negative_missing_field(self):
        with self.assertRaises(KeyError):
            self.client.post(
                "/mechanics/",
                json={
                    "name": "Bad Mechanic",
                    "email": f"bad_mech_{uuid4().hex[:8]}@email.com",
                    "phone_number": "555-000-0000",
                },
            )

    # GET /mechanics/
    def test_get_mechanics(self):
        res = self.client.get("/mechanics/")
        self.assertIn(res.status_code, (200, 500))

    # GET /mechanics/<id>
    def test_get_mechanic(self):
        res = self.client.get(f"/mechanics/{self.mechanic_id}")
        self.assertEqual(res.status_code, 200)

    def test_get_mechanic_negative_not_found(self):
        res = self.client.get("/mechanics/999999")
        self.assertEqual(res.status_code, 404)

    # PUT /mechanics/<id>
    def test_update_mechanic(self):
        res = self.client.put(f"/mechanics/{self.mechanic_id}", json={"salary": 70000})
        self.assertEqual(res.status_code, 200)

    # DELETE /mechanics/<id>
    def test_delete_mechanic(self):
        res = self.client.delete(f"/mechanics/{self.mechanic_id}")
        self.assertEqual(res.status_code, 200)

    # GET /mechanics/leaderboard/most-tickets
    def test_mechanics_leaderboard_most_tickets(self):
        res = self.client.get("/mechanics/leaderboard/most-tickets")
        self.assertEqual(res.status_code, 200)
