from datetime import datetime

from app import db


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True, unique=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    def __repr__(self):
        return f"<Location {self.name}>"


class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    confirmed_at = db.Column(db.DateTime, index=True)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    location_id = db.Column(db.Integer, db.ForeignKey("location.id"))

    def __repr__(self):
        return f"<Case #{self.id} - {self.created_at}>"
