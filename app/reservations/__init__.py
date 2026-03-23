# app/reservations/__init__.py
from flask import Blueprint

reservations_bp = Blueprint(
    "reservations",
    __name__,
    template_folder="../templates/reservations",
)

from app.reservations import routes  # noqa: E402,F401