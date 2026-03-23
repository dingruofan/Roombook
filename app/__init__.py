from flask import Flask

from app.config import Config
from app.extensions import db, login_manager, migrate

from app.auth import auth_bp
from app.main import main_bp
from app.rooms import rooms_bp
from app.reservations import reservations_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.models import Reservation, Room, User

    from app.auth import auth_bp
    from app.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(rooms_bp)
    app.register_blueprint(reservations_bp)

    return app


@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User

    return db.session.get(User, int(user_id))

