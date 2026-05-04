"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

# ─── Database config ────────────────────────────────────────────────────────
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url.replace(
        "postgres://", "postgresql://"
    )
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


# ─── Error handler ──────────────────────────────────────────────────────────
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


# ─── Sitemap / root ─────────────────────────────────────────────────────────
@app.route("/")
def sitemap():
    return generate_sitemap(app)


# ════════════════════════════════════════════════════════════════════════════
#  PEOPLE
# ════════════════════════════════════════════════════════════════════════════

@app.route("/people", methods=["GET"])
def get_all_people():
    people = People.query.all()
    return jsonify([p.serialize() for p in people]), 200


@app.route("/people/<int:people_id>", methods=["GET"])
def get_person(people_id):
    person = People.query.get(people_id)
    if not person:
        raise APIException("Person not found", status_code=404)
    return jsonify(person.serialize()), 200


@app.route("/people", methods=["POST"])
def create_person():
    body = request.get_json()
    if not body:
        raise APIException("Request body is missing", status_code=400)
    if "name" not in body:
        raise APIException("You must specify a name", status_code=400)

    person = People(
        name=body["name"],
        birth_year=body.get("birth_year"),
        eye_color=body.get("eye_color"),
        hair_color=body.get("hair_color"),
        skin_color=body.get("skin_color"),
        height=body.get("height"),
        mass=body.get("mass"),
        gender=body.get("gender"),
        homeworld_id=body.get("homeworld_id"),
    )
    db.session.add(person)
    db.session.commit()
    return jsonify(person.serialize()), 201


@app.route("/people/<int:people_id>", methods=["PUT"])
def update_person(people_id):
    person = People.query.get(people_id)
    if not person:
        raise APIException("Person not found", status_code=404)

    body = request.get_json()
    if not body:
        raise APIException("Request body is missing", status_code=400)

    for field in ["name", "birth_year", "eye_color", "hair_color",
                  "skin_color", "height", "mass", "gender", "homeworld_id"]:
        if field in body:
            setattr(person, field, body[field])

    db.session.commit()
    return jsonify(person.serialize()), 200


@app.route("/people/<int:people_id>", methods=["DELETE"])
def delete_person(people_id):
    person = People.query.get(people_id)
    if not person:
        raise APIException("Person not found", status_code=404)
    db.session.delete(person)
    db.session.commit()
    return jsonify({"message": f"Person {people_id} deleted successfully"}), 200


# ════════════════════════════════════════════════════════════════════════════
#  PLANETS
# ════════════════════════════════════════════════════════════════════════════

@app.route("/planets", methods=["GET"])
def get_all_planets():
    planets = Planet.query.all()
    return jsonify([p.serialize() for p in planets]), 200


@app.route("/planets/<int:planet_id>", methods=["GET"])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        raise APIException("Planet not found", status_code=404)
    return jsonify(planet.serialize()), 200


@app.route("/planets", methods=["POST"])
def create_planet():
    body = request.get_json()
    if not body:
        raise APIException("Request body is missing", status_code=400)
    if "name" not in body:
        raise APIException("You must specify a name", status_code=400)

    planet = Planet(
        name=body["name"],
        climate=body.get("climate"),
        terrain=body.get("terrain"),
        population=body.get("population"),
        diameter=body.get("diameter"),
        rotation_period=body.get("rotation_period"),
        orbital_period=body.get("orbital_period"),
    )
    db.session.add(planet)
    db.session.commit()
    return jsonify(planet.serialize()), 201


@app.route("/planets/<int:planet_id>", methods=["PUT"])
def update_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        raise APIException("Planet not found", status_code=404)

    body = request.get_json()
    if not body:
        raise APIException("Request body is missing", status_code=400)

    for field in ["name", "climate", "terrain", "population",
                  "diameter", "rotation_period", "orbital_period"]:
        if field in body:
            setattr(planet, field, body[field])

    db.session.commit()
    return jsonify(planet.serialize()), 200


@app.route("/planets/<int:planet_id>", methods=["DELETE"])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        raise APIException("Planet not found", status_code=404)
    db.session.delete(planet)
    db.session.commit()
    return jsonify({"message": f"Planet {planet_id} deleted successfully"}), 200


# ════════════════════════════════════════════════════════════════════════════
#  USERS
# ════════════════════════════════════════════════════════════════════════════

@app.route("/users", methods=["GET"])
def get_all_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200


@app.route("/users/favorites", methods=["GET"])
def get_user_favorites():
    # No auth system yet: using the first user as "current user"
    current_user = User.query.first()
    if not current_user:
        raise APIException("No users in database. Create one via /admin", status_code=404)
    favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    return jsonify([f.serialize() for f in favorites]), 200


# ════════════════════════════════════════════════════════════════════════════
#  FAVORITES
# ════════════════════════════════════════════════════════════════════════════

@app.route("/favorite/planet/<int:planet_id>", methods=["POST"])
def add_favorite_planet(planet_id):
    current_user = User.query.first()
    if not current_user:
        raise APIException("No users in database", status_code=404)

    planet = Planet.query.get(planet_id)
    if not planet:
        raise APIException("Planet not found", status_code=404)

    existing = Favorite.query.filter_by(
        user_id=current_user.id, planet_id=planet_id
    ).first()
    if existing:
        raise APIException("Planet already in favorites", status_code=400)

    favorite = Favorite(user_id=current_user.id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201


@app.route("/favorite/people/<int:people_id>", methods=["POST"])
def add_favorite_people(people_id):
    current_user = User.query.first()
    if not current_user:
        raise APIException("No users in database", status_code=404)

    person = People.query.get(people_id)
    if not person:
        raise APIException("Person not found", status_code=404)

    existing = Favorite.query.filter_by(
        user_id=current_user.id, people_id=people_id
    ).first()
    if existing:
        raise APIException("Person already in favorites", status_code=400)

    favorite = Favorite(user_id=current_user.id, people_id=people_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201


@app.route("/favorite/planet/<int:planet_id>", methods=["DELETE"])
def delete_favorite_planet(planet_id):
    current_user = User.query.first()
    if not current_user:
        raise APIException("No users in database", status_code=404)

    favorite = Favorite.query.filter_by(
        user_id=current_user.id, planet_id=planet_id
    ).first()
    if not favorite:
        raise APIException("Favorite planet not found", status_code=404)

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": f"Favorite planet {planet_id} deleted"}), 200


@app.route("/favorite/people/<int:people_id>", methods=["DELETE"])
def delete_favorite_people(people_id):
    current_user = User.query.first()
    if not current_user:
        raise APIException("No users in database", status_code=404)

    favorite = Favorite.query.filter_by(
        user_id=current_user.id, people_id=people_id
    ).first()
    if not favorite:
        raise APIException("Favorite person not found", status_code=404)

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": f"Favorite person {people_id} deleted"}), 200


# ─── Entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 3001))
    app.run(host="0.0.0.0", port=PORT, debug=True)