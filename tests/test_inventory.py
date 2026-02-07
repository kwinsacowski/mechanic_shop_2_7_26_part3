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


class TestInventory(unittest.TestCase):
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

        seed = self.client.post("/inventory/", json={"name": "Seed Part", "price": 10.0})
        self.assertIn(seed.status_code, (200, 201))
        self.part_id = seed.json["id"]

    # POST /inventory/
    def test_create_part(self):
        res = self.client.post("/inventory/", json={"name": "Rotor", "price": 50.0})
        self.assertIn(res.status_code, (200, 201))
        self.assertEqual(res.json["name"], "Rotor")

    def test_create_part_negative_missing_fields(self):
        res = self.client.post("/inventory/", json={"name": "No Price"})
        self.assertEqual(res.status_code, 400)

    def test_create_part_negative_price_not_number(self):
        res = self.client.post("/inventory/", json={"name": "Bad", "price": "abc"})
        self.assertEqual(res.status_code, 400)

    # GET /inventory/
    def test_get_parts(self):
        res = self.client.get("/inventory/")
        self.assertEqual(res.status_code, 200)

    # GET /inventory/<id>
    def test_get_part(self):
        res = self.client.get(f"/inventory/{self.part_id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json["id"], self.part_id)

    def test_get_part_negative_not_found(self):
        res = self.client.get("/inventory/999999")
        self.assertEqual(res.status_code, 404)

    # PUT /inventory/<id>
    def test_update_part(self):
        res = self.client.put(f"/inventory/{self.part_id}", json={"price": 99.5})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json["price"], 99.5)

    def test_update_part_negative_price_not_number(self):
        res = self.client.put(f"/inventory/{self.part_id}", json={"price": "nope"})
        self.assertEqual(res.status_code, 400)

    # DELETE /inventory/<id>
    def test_delete_part(self):
        res = self.client.delete(f"/inventory/{self.part_id}")
        self.assertEqual(res.status_code, 200)

    def test_delete_part_negative_not_found(self):
        res = self.client.delete("/inventory/999999")
        self.assertEqual(res.status_code, 404)
