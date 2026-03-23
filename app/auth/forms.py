from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional


class LoginForm(FlaskForm):
    username = StringField("用户名", validators=[DataRequired(), Length(max=80)])
    password = PasswordField("密码", validators=[DataRequired(), Length(max=128)])
    submit = SubmitField("登录")


class AdminCreateUserForm(FlaskForm):
    username = StringField("用户名", validators=[DataRequired(), Length(max=80)])
    full_name = StringField("姓名", validators=[Optional(), Length(max=120)])
    email = StringField("邮箱", validators=[Optional(), Email(), Length(max=120)])
    role = SelectField("角色", choices=[("user", "普通用户"), ("admin", "管理员")])
    password = PasswordField("初始密码", validators=[DataRequired(), Length(min=6, max=128)])
    is_active_user = BooleanField("启用账号", default=True)
    submit = SubmitField("创建用户")


class AdminEditUserForm(FlaskForm):
    username = StringField("用户名", validators=[DataRequired(), Length(max=80)])
    full_name = StringField("姓名", validators=[Optional(), Length(max=120)])
    email = StringField("邮箱", validators=[Optional(), Email(), Length(max=120)])
    role = SelectField("角色", choices=[("user", "普通用户"), ("admin", "管理员")])
    is_active_user = BooleanField("启用账号", default=True)
    submit = SubmitField("保存修改")


class AdminResetPasswordForm(FlaskForm):
    new_password = PasswordField("新密码", validators=[DataRequired(), Length(min=6, max=128)])
    submit = SubmitField("重置密码")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("当前密码", validators=[DataRequired(), Length(max=128)])
    new_password = PasswordField("新密码", validators=[DataRequired(), Length(min=6, max=128)])
    submit = SubmitField("保存修改")