# app/rooms/__init__.py
from flask import Blueprint

rooms_bp = Blueprint("rooms", __name__, template_folder="../templates/rooms")

from app.rooms import routes  # noqa: E402,F401