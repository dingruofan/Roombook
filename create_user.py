from app import create_app
from app.extensions import db
from app.models.user import User


def create_admin() -> None:
    app = create_app()
    with app.app_context():
        existing = User.query.filter_by(username="丁若凡").first()
        if existing:
            return

        user = User(
            username="丁若凡",
            full_name="丁若凡",
            email="drf@example.com",
            role="user",
        )
        user.set_password("111991079")
        db.session.add(user)
        db.session.commit()


if __name__ == "__main__":
    create_admin()