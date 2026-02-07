from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
    #----Models----#

service_mechanics = db.Table('service_mechanics',
    db.Column('service_ticket_id', db.Integer, db.ForeignKey('service_tickets.id'), primary_key=True),
    db.Column('mechanic_id', db.Integer, db.ForeignKey('mechanics.id'), primary_key=True)
)

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def set_password(self, raw_password: str):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password, raw_password)

    service_tickets = db.relationship('ServiceTicket', backref='customer', lazy=True)

class ServiceTicket(db.Model):
    __tablename__ = 'service_tickets'

    id = db.Column(db.Integer, primary_key=True)
    vin= db.Column(db.String(17), nullable=False)
    service_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    pickup_date = db.Column(db.Date, nullable=True)

    mechanics = db.relationship('Mechanic', secondary=service_mechanics, backref=db.backref('service_tickets', lazy=True))

class Mechanic(db.Model):
    __tablename__ = 'mechanics'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    salary = db.Column(db.Float, nullable=False)

