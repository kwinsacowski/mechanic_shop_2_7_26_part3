import os
import sys
import types
import unittest

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

# Force a safe test DB if your app reads env vars
os.environ.setdefault("DATABASE_URL", "sqlite:///testing.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from app import create_app
from app.extensions import db


class TestHome(unittest.TestCase):
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

    def test_home_route(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json, dict)
