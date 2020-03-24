from datetime import date

from server import db


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True, unique=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    case_data = db.relationship("CaseData", backref="location", lazy="dynamic")

    def __repr__(self):
        return f"<Location {self.name}>"


class CaseData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True, default=date.today, nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey("location.id"), nullable=False)
    confirmed = db.Column(db.Integer, nullable=False)
    recovered = db.Column(db.Integer, default=0)
    fatal = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<CaseData from {self.date} - {self.location.name}>"
