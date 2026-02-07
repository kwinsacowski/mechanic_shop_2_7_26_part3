from marshmallow import fields
from app.extensions import ma
from app.models import Customer

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    password = fields.String(load_only=True)  # Don't include password in serialized output, but require it for input
    class Meta:
        model = Customer
        load_instance = True
        include_fk = True

class EditServiceTicketSchema(ma.Schema):
    add_pickup_date = ma.Date(required=False, allow_none=True)
    class Meta:
        fields = ("add_pickup_date",)

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

login_schema = CustomerSchema(only=("email", "password"))
EditServiceTicketSchema = EditServiceTicketSchema()