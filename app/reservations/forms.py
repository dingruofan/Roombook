from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class ReservationForm(FlaskForm):
    room_id = SelectField("会议室", coerce=int, validators=[DataRequired()])
    title = StringField("主题", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("描述")
    start_time = DateTimeLocalField(
        "开始时间",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired()],
        default=datetime.now,
    )
    end_time = DateTimeLocalField(
        "结束时间",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired()],
        default=datetime.now,
    )
    submit = SubmitField("保存")