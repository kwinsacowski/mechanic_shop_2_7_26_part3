from uuid import uuid4
from app.extensions import db
from app.models import Customer

def reset_db(app):
    with app.app_context():
        db.drop_all()
        db.create_all()

def seed_customer(app, password="password123"):
    """Creates and returns (customer, email, password)."""
    email = f"seed_{uuid4().hex[:8]}@email.com"
    with app.app_context():
        c = Customer(
            name="Seed Customer",
            email=email,
            phone_number="555-555-5555",
            password="temp"
        )
        c.set_password(password)
        db.session.add(c)
        db.session.commit()
        return c, email, password
