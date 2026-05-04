from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    favorites = db.relationship("Favorite", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.email}>"

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
        }


class Planet(db.Model):
    __tablename__ = "planet"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    climate = db.Column(db.String(80))
    terrain = db.Column(db.String(80))
    population = db.Column(db.BigInteger)
    diameter = db.Column(db.Integer)
    rotation_period = db.Column(db.Integer)
    orbital_period = db.Column(db.Integer)

    def __repr__(self):
        return f"<Planet {self.name}>"

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "population": self.population,
            "diameter": self.diameter,
            "rotation_period": self.rotation_period,
            "orbital_period": self.orbital_period,
        }


class People(db.Model):
    __tablename__ = "people"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    birth_year = db.Column(db.String(20))
    eye_color = db.Column(db.String(40))
    hair_color = db.Column(db.String(40))
    skin_color = db.Column(db.String(40))
    height = db.Column(db.Integer)
    mass = db.Column(db.Float)
    gender = db.Column(db.String(20))
    homeworld_id = db.Column(db.Integer, db.ForeignKey("planet.id"), nullable=True)

    homeworld = db.relationship("Planet", backref="residents")

    def __repr__(self):
        return f"<People {self.name}>"

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "birth_year": self.birth_year,
            "eye_color": self.eye_color,
            "hair_color": self.hair_color,
            "skin_color": self.skin_color,
            "height": self.height,
            "mass": self.mass,
            "gender": self.gender,
            "homeworld_id": self.homeworld_id,
        }


class Favorite(db.Model):
    __tablename__ = "favorite"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey("planet.id"), nullable=True)
    people_id = db.Column(db.Integer, db.ForeignKey("people.id"), nullable=True)

    planet = db.relationship("Planet", backref="favorited_by")
    people = db.relationship("People", backref="favorited_by")

    def __repr__(self):
        return f"<Favorite user={self.user_id}>"

    def serialize(self):
        result = {"id": self.id, "user_id": self.user_id}
        if self.planet_id:
            result["type"] = "planet"
            result["planet_id"] = self.planet_id
            result["name"] = self.planet.name if self.planet else None
        elif self.people_id:
            result["type"] = "people"
            result["people_id"] = self.people_id
            result["name"] = self.people.name if self.people else None
        return result