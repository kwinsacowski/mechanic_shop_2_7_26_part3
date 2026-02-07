from ast import stmt
from flask import request
from app.extensions import db, limiter, cache
from app.models import Customer, ServiceTicket
from app.blueprints.customers import customers_bp
from app.blueprints.customers.schemas import customer_schema, login_schema, customers_schema
from app.utils.auth import encode_token, token_required
from app.blueprints.service_tickets.schemas import service_tickets_schema

@customers_bp.post("/login")
def login_customer():
    data = request.get_json() or {}

    # Validate input using schema
    errors = login_schema.validate(data)
    if errors:
        return {"errors": errors}, 400

    email = data.get("email")
    password = data.get("password")

    customer = Customer.query.filter_by(email=email).first()
    if not customer or not customer.check_password(password):
        return {"message": "Invalid credentials"}, 401


    token = encode_token(customer.id)
    return {"token": token}, 200

@customers_bp.get("/my-tickets")
@token_required
def get_my_tickets(customer_id):
    tickets = ServiceTicket.query.filter_by(customer_id=customer_id).all()
    return service_tickets_schema.dump(tickets), 200

@customers_bp.post("/")
@limiter.limit("5 per minute") # Limit to 5 customer creations per minute, considering multple users servicing multiple customers at one time
def create_customer():
    data = request.get_json() or {}
    required = ["name", "email", "phone_number", "password"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return {"error": f"Missing required field(s): {', '.join(missing)}"}, 400

    customer = Customer(
        name=data["name"],
        email=data["email"],
        phone_number=data["phone_number"],
        password="temp"  # will be overwritten by set_password
    )
    customer.set_password(data["password"])


    db.session.add(customer)
    db.session.commit()
    return customer_schema.dump(customer), 201

@customers_bp.get("/")
@limiter.limit("10 per minute")
@cache.cached(timeout=120, query_string=True)  # IMPORTANT: cache must vary by page/per_page
def get_customers():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    
    pagination = Customer.query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return {
        "items": customers_schema.dump(pagination.items),
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
        "total": pagination.total,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
    }, 200

@customers_bp.get("/<int:id>")
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    return customer_schema.dump(customer), 200

@customers_bp.put("/<int:id>")
@token_required
def update_customer(customer_id, id):
    if customer_id != id:
        return {"message": "Forbidden"}, 403
    
    customer = Customer.query.get_or_404(id)
    data = request.get_json() or {}

    customer.name = data.get("name", customer.name)
    customer.email = data.get("email", customer.email)
    customer.phone_number = data.get("phone_number", customer.phone_number)

    db.session.commit()
    return customer_schema.dump(customer), 200

@customers_bp.delete("/<int:id>")
@token_required
def delete_customer(customer_id, id):
    if customer_id != id:
        return {"message": "Forbidden"}, 403
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return {"message": f"Customer {id} deleted"}, 200
