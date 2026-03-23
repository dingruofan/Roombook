from app.auth import auth_bp
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from app.models.user import User
from app.auth.forms import AdminCreateUserForm, ChangePasswordForm, LoginForm
from app.extensions import db


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
        if User.query.filter_by(username=form.username.data.strip()).first():
            flash("用户名已存在。", "warning")
            return render_template("auth/create_user.html", form=form)

        email = (form.email.data or "").strip() or None
        full_name = (form.full_name.data or "").strip() or None

        user = User(
            username=form.username.data.strip(),
            full_name=full_name,
            email=email,
            role=form.role.data,
            is_active_user=bool(form.is_active_user.data),
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("用户创建成功。", "success")
        return redirect(url_for("rooms.list_rooms"))

    return render_template("auth/create_user.html", form=form)


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