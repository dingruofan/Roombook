from app.extensions import db


class Room(db.Model):
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    location = db.Column(db.String(100))
    capacity = db.Column(db.Integer, default=0)
    equipment = db.Column(db.String(255))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)

    reservations = db.relationship("Reservation", back_populates="room", lazy="dynamic")