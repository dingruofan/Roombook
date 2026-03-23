from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange


class RoomForm(FlaskForm):
    name = StringField("会议室名称", validators=[DataRequired(), Length(max=100)])
    location = StringField("位置", validators=[Length(max=100)])
    capacity = IntegerField("容量", validators=[NumberRange(min=0)], default=0)
    equipment = StringField("设备", validators=[Length(max=255)])
    description = TextAreaField("描述")
    is_active = BooleanField("启用", default=True)
    submit = SubmitField("保存")