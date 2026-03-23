from datetime import datetime

from app.extensions import db


class Reservation(db.Model):
    __tablename__ = "reservations"

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    start_time = db.Column(db.DateTime, nullable=False, index=True)
    end_time = db.Column(db.DateTime, nullable=False, index=True)

    status = db.Column(db.String(20), nullable=False, default="active")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    room = db.relationship("Room", back_populates="reservations")
    user = db.relationship("User", back_populates="reservations")

    def validate_time_range(self) -> bool:
        return self.start_time < self.end_time

    @classmethod
    def has_conflict(
        cls,
        room_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_reservation_id: int | None = None,
    ) -> bool:
        query = cls.query.filter(
            cls.room_id == room_id,
            cls.status == "active",
            cls.start_time < end_time,
            cls.end_time > start_time,
        )

        if exclude_reservation_id is not None:
            query = query.filter(cls.id != exclude_reservation_id)

        return db.session.query(query.exists()).scalar()

    @classmethod
    def find_conflicts(
        cls,
        room_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_reservation_id: int | None = None,
    ):
        query = cls.query.filter(
            cls.room_id == room_id,
            cls.status == "active",
            cls.start_time < end_time,
            cls.end_time > start_time,
        ).order_by(cls.start_time.asc())

        if exclude_reservation_id is not None:
            query = query.filter(cls.id != exclude_reservation_id)

        return query.all()