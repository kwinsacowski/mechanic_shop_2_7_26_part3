from app.extensions import ma
from app.models import ServiceTicket, Mechanic

class MechanicMiniSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        fields = ("id", "name", "email", "phone_number", "salary")

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    mechanics = ma.Nested(MechanicMiniSchema, many=True)
    class Meta:
        model = ServiceTicket
        load_instance = True

class EditServiceTicketSchema(ma.Schema):
    add_ids = ma.List(ma.Integer(), required=False, load_default=list)
    remove_ids = ma.List(ma.Integer(), required=False, load_default=list)

service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
edit_service_ticket_schema = EditServiceTicketSchema()
