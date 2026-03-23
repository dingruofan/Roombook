from app.auth import auth_bp
from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.auth.forms import (
    AdminCreateUserForm,
    AdminEditUserForm,
    AdminResetPasswordForm,
    ChangePasswordForm,
    LoginForm,
)
from app.extensions import db
from app.models.user import User


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("登录成功", "success")
            next_url = request.args.get("next")
            if next_url:
                return redirect(next_url)
            return redirect(url_for("main.index"))

        flash("用户名或密码错误", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("你已退出登录", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/users/create", methods=["GET", "POST"])
@login_required
def create_user():
    if not current_user.is_admin:
        abort(403)

    form = AdminCreateUserForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        if User.query.filter_by(username=username).first():
            flash("用户名已存在。", "warning")
            return render_template("auth/create_user.html", form=form)

        email = (form.email.data or "").strip() or None
        full_name = (form.full_name.data or "").strip() or None

        if email and User.query.filter_by(email=email).first():
            flash("邮箱已存在。", "warning")
            return render_template("auth/create_user.html", form=form)

        user = User(
            username=username,
            full_name=full_name,
            email=email,
            role=form.role.data,
            is_active_user=bool(form.is_active_user.data),
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("用户创建成功。", "success")
        return redirect(url_for("auth.list_users"))

    return render_template("auth/create_user.html", form=form)


@auth_bp.route("/users", methods=["GET"])
@login_required
def list_users():
    if not current_user.is_admin:
        abort(403)

    users = User.query.order_by(User.id.asc()).all()
    return render_template("auth/users.html", users=users)


@auth_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
def edit_user(user_id: int):
    if not current_user.is_admin:
        abort(403)

    user = User.query.get_or_404(user_id)
    form = AdminEditUserForm(obj=user)

    if form.validate_on_submit():
        username = form.username.data.strip()
        email = (form.email.data or "").strip() or None
        full_name = (form.full_name.data or "").strip() or None

        username_exists = User.query.filter(User.username == username, User.id != user.id).first()
        if username_exists:
            flash("用户名已被占用。", "warning")
            return render_template("auth/edit_user.html", form=form, target_user=user)

        if email:
            email_exists = User.query.filter(User.email == email, User.id != user.id).first()
            if email_exists:
                flash("邮箱已被占用。", "warning")
                return render_template("auth/edit_user.html", form=form, target_user=user)

        user.username = username
        user.full_name = full_name
        user.email = email
        user.role = form.role.data
        user.is_active_user = bool(form.is_active_user.data)

        db.session.commit()
        flash("用户信息更新成功。", "success")
        return redirect(url_for("auth.list_users"))

    return render_template("auth/edit_user.html", form=form, target_user=user)


@auth_bp.route("/users/<int:user_id>/reset-password", methods=["GET", "POST"])
@login_required
def reset_user_password(user_id: int):
    if not current_user.is_admin:
        abort(403)

    user = User.query.get_or_404(user_id)
    form = AdminResetPasswordForm()

    if form.validate_on_submit():
        user.set_password(form.new_password.data)
        db.session.commit()
        flash(f"用户 {user.username} 的密码已重置。", "success")
        return redirect(url_for("auth.list_users"))

    return render_template("auth/reset_password.html", form=form, target_user=user)


@auth_bp.route("/password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("当前密码不正确。", "danger")
            return render_template("auth/change_password.html", form=form)

        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash("密码修改成功。", "success")
        return redirect(url_for("main.index"))

    return render_template("auth/change_password.html", form=form)