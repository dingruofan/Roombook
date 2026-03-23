from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "请先登录后再访问。"
login_manager.login_message_category = "warning"
login_manager.session_protection = "strong"