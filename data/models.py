from datetime import date, datetime

from .database import db


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True, unique=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    api_id = db.Column(db.Integer, index=True, unique=True)
    api_name = db.Column(db.String(255), index=True, unique=True)

    minzdrav_name = db.Column(db.String(255), index=True, unique=True)

    def __repr__(self):
        return f"<Location {self.name}>"


class CaseData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True, default=date.today, nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey("location.id"), nullable=False)
    location = db.relationship("Location", lazy=True)
    confirmed = db.Column(db.Integer, default=0)
    recovered = db.Column(db.Integer, default=0)
    fatal = db.Column(db.Integer, default=0)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<CaseData from {self.date} - {self.location.name}>"
