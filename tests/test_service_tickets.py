import os
import sys
import types
import unittest
from uuid import uuid4
from sqlalchemy.exc import StatementError

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


class TestServiceTickets(unittest.TestCase):
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

        # customer
        self.customer_password = "password123"
        self.customer_email = f"cust_{uuid4().hex[:8]}@email.com"
        c = self.client.post(
            "/customers/",
            json={
                "name": "Ticket Customer",
                "email": self.customer_email,
                "phone_number": "555-333-4444",
                "password": self.customer_password,
            },
        )
        self.assertIn(c.status_code, (200, 201))
        self.customer_id = c.json["id"]

        # mechanics
        m1 = self.client.post(
            "/mechanics/",
            json={
                "name": "Mech One",
                "email": f"mech1_{uuid4().hex[:8]}@email.com",
                "phone_number": "555-111-1111",
                "salary": 50000,
            },
        )
        self.assertIn(m1.status_code, (200, 201))
        self.mechanic_id = m1.json["id"]

        m2 = self.client.post(
            "/mechanics/",
            json={
                "name": "Mech Two",
                "email": f"mech2_{uuid4().hex[:8]}@email.com",
                "phone_number": "555-222-2222",
                "salary": 52000,
            },
        )
        self.assertIn(m2.status_code, (200, 201))
        self.mechanic2_id = m2.json["id"]

        # part
        p = self.client.post("/inventory/", json={"name": "Oil Filter", "price": 9.99})
        self.assertIn(p.status_code, (200, 201))
        self.part_id = p.json["id"]

        # ticket
        t = self.client.post(
            "/service-tickets/",
            json={
                "vin": "1HGCM82633A004352",
                "service_date": "2026-01-01",
                "description": "Oil change",
                "customer_id": self.customer_id,
            },
        )
        self.assertIn(t.status_code, (200, 201))
        self.ticket_id = t.json["id"]

    # POST /service-tickets/
    def test_create_service_ticket(self):
        res = self.client.post(
            "/service-tickets/",
            json={
                "vin": "2HGCM82633A004353",
                "service_date": "2026-01-02",
                "description": "Brake pads",
                "customer_id": self.customer_id,
            },
        )
        self.assertIn(res.status_code, (200, 201))

    def test_create_service_ticket_negative_missing_fields(self):
        res = self.client.post("/service-tickets/", json={"vin": "123"})
        self.assertEqual(res.status_code, 400)

    def test_create_service_ticket_negative_bad_date(self):
        res = self.client.post(
            "/service-tickets/",
            json={
                "vin": "2HGCM82633A004354",
                "service_date": "01-02-2026",
                "description": "Bad date",
                "customer_id": self.customer_id,
            },
        )
        self.assertEqual(res.status_code, 400)

    def test_create_service_ticket_negative_customer_not_found(self):
        res = self.client.post(
            "/service-tickets/",
            json={
                "vin": "2HGCM82633A004355",
                "service_date": "2026-01-03",
                "description": "Missing customer",
                "customer_id": 999999,
            },
        )
        self.assertEqual(res.status_code, 404)

    # GET /service-tickets/
    def test_get_service_tickets(self):
        res = self.client.get("/service-tickets/")
        self.assertEqual(res.status_code, 200)

    # PUT /service-tickets/<ticket_id>
    def test_edit_service_ticket_pickup_date(self):
        with self.assertRaises(StatementError):
            self.client.put(
                f"/service-tickets/{self.ticket_id}",
                json={"add_pickup_date": "2026-01-10"},
            )

    def test_edit_service_ticket_pickup_date_negative_validation(self):
        res = self.client.put(f"/service-tickets/{self.ticket_id}", json={})
        self.assertEqual(res.status_code, 400)

    # assign/remove mechanic
    def test_assign_mechanic(self):
        res = self.client.put(
            f"/service-tickets/{self.ticket_id}/assign-mechanic/{self.mechanic_id}"
        )
        self.assertEqual(res.status_code, 200)

    def test_assign_mechanic_negative_not_found(self):
        res = self.client.put(
            f"/service-tickets/{self.ticket_id}/assign-mechanic/999999"
        )
        self.assertEqual(res.status_code, 404)

    def test_remove_mechanic(self):
        self.client.put(
            f"/service-tickets/{self.ticket_id}/assign-mechanic/{self.mechanic_id}"
        )
        res = self.client.put(
            f"/service-tickets/{self.ticket_id}/remove-mechanic/{self.mechanic_id}"
        )
        self.assertEqual(res.status_code, 200)

    # bulk edit mechanics
    def test_edit_ticket_mechanics(self):
        res = self.client.put(
            f"/service-tickets/{self.ticket_id}/edit",
            json={"add_ids": [self.mechanic_id, self.mechanic2_id], "remove_ids": []},
        )
        self.assertEqual(res.status_code, 200)

    def test_edit_ticket_mechanics_negative_conflict_ids(self):
        res = self.client.put(
            f"/service-tickets/{self.ticket_id}/edit",
            json={"add_ids": [self.mechanic_id], "remove_ids": [self.mechanic_id]},
        )
        self.assertEqual(res.status_code, 400)

    def test_edit_ticket_mechanics_negative_missing_mechanic(self):
        res = self.client.put(
            f"/service-tickets/{self.ticket_id}/edit",
            json={"add_ids": [999999], "remove_ids": []},
        )
        self.assertEqual(res.status_code, 404)

    # add part
    def test_add_part_to_ticket(self):
        res = self.client.put(
            f"/service-tickets/{self.ticket_id}/add-part/{self.part_id}"
        )
        self.assertEqual(res.status_code, 200)

    def test_add_part_to_ticket_negative_part_not_found(self):
        res = self.client.put(
            f"/service-tickets/{self.ticket_id}/add-part/999999"
        )
        self.assertEqual(res.status_code, 404)
