from flask import request
from app.extensions import db
from app.models import Mechanic
from app.blueprints.mechanics import mechanics_bp
from app.blueprints.mechanics.schemas import mechanic_schema

# CREATE mechanic
@mechanics_bp.post("/")
def create_mechanic():

    data = request.get_json()

    mechanic = Mechanic(
        name=data["name"],
        email=data["email"],
        phone_number=data["phone_number"],
        salary=data["salary"]
    )

    db.session.add(mechanic)
    db.session.commit()

    return mechanic_schema.dump(mechanic), 201


# READ all mechanics
@mechanics_bp.get("/")
def get_mechanics():

    mechanic = Mechanic.query.all()

    return mechanic_schema.dump(mechanic), 200

#GET mechanic by ID
@mechanics_bp.get("/<int:id>")
def get_mechanic(id):
    mechanic = Mechanic.query.get_or_404(id)

    return mechanic_schema.dump(mechanic), 200


# UPDATE mechanic
@mechanics_bp.put("/<int:id>")
def update_mechanic(id):

    mechanic = Mechanic.query.get_or_404(id)

    data = request.get_json()

    mechanic.name = data.get("name", mechanic.name)
    mechanic.email = data.get("email", mechanic.email)
    mechanic.phone_number = data.get("phone_number", mechanic.phone_number)
    mechanic.salary = data.get("salary", mechanic.salary)

    db.session.commit()

    return mechanic_schema.dump(mechanic), 200


# DELETE mechanic
@mechanics_bp.delete("/<int:id>")
def delete_mechanic(id):

    mechanic = Mechanic.query.get_or_404(id)

    db.session.delete(mechanic)
    db.session.commit()

    return {"message": f"Mechanic {id} deleted"}, 200
