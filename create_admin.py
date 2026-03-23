from app import create_app
from app.extensions import db
from app.models.user import User


def create_admin() -> None:
    app = create_app()
    with app.app_context():
        existing = User.query.filter_by(username="admin1").first()
        if existing:
            return

        user = User(
            username="admin1",
            full_name="系统管理员",
            email="admin1@example.com",
            role="admin",
        )
        user.set_password("admin1")
        db.session.add(user)
        db.session.commit()


if __name__ == "__main__":
    create_admin()