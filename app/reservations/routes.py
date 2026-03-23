from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models.reservation import Reservation
from app.models.room import Room
from app.reservations import reservations_bp
from app.reservations.forms import ReservationForm
from flask import request

def _room_choices():
    rooms = Room.query.filter_by(is_active=True).order_by(Room.name.asc()).all()
    return [(r.id, f"{r.name}（{r.location or '未设置位置'}）") for r in rooms]


@reservations_bp.route("/reservations/create", methods=["GET", "POST"])
@login_required
def create_reservation():
    form = ReservationForm()
    form.room_id.choices = _room_choices()

    if not form.room_id.choices:
        flash("当前没有可用会议室，请联系管理员先创建。", "warning")
        return redirect(url_for("rooms.list_rooms"))

    if form.validate_on_submit():
        start_time = form.start_time.data
        end_time = form.end_time.data

        reservation = Reservation(
            room_id=form.room_id.data,
            user_id=current_user.id,
            title=form.title.data.strip(),
            description=(form.description.data or "").strip(),
            start_time=start_time,
            end_time=end_time,
            status="active",
        )

        conflicts = Reservation.find_conflicts(
            room_id=form.room_id.data,
            start_time=start_time,
            end_time=end_time,
        )
        if conflicts:
            conflict_text = "；".join(
                f"{c.start_time:%m-%d %H:%M}-{c.end_time:%H:%M}"
                for c in conflicts[:3]
            )
            flash(f"该时间段已被预定：{conflict_text}", "danger")
            return render_template("reservations/form.html", form=form, mode="create")


        if not reservation.validate_time_range():
            flash("开始时间必须早于结束时间。", "danger")
            return render_template("reservations/form.html", form=form, mode="create")

        if Reservation.has_conflict(
            room_id=form.room_id.data,
            start_time=start_time,
            end_time=end_time,
        ):
            flash("该时间段会议室已被预定，请选择其他时间。", "danger")
            return render_template("reservations/form.html", form=form, mode="create")

        db.session.add(reservation)
        db.session.commit()
        flash("预定创建成功。", "success")
        return redirect(url_for("reservations.my_reservations"))

    if form.errors:
        flash(f"表单校验失败：{form.errors}", "danger")

    return render_template("reservations/form.html", form=form, mode="create")


@reservations_bp.route("/reservations/my")
@login_required
def my_reservations():
    page = request.args.get("page", 1, type=int)
    pagination = (
        Reservation.query.filter_by(user_id=current_user.id)
        .order_by(Reservation.start_time.desc())
        .paginate(page=page, per_page=10, error_out=False)
    )
    return render_template(
        "reservations/my.html",
        reservations=pagination.items,
        pagination=pagination,
    )


@reservations_bp.route("/reservations/<int:reservation_id>/edit", methods=["GET", "POST"])
@login_required
def edit_reservation(reservation_id: int):
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.user_id != current_user.id:
        abort(403)

    form = ReservationForm(obj=reservation)
    form.room_id.choices = _room_choices()

    if form.validate_on_submit():
        start_time = form.start_time.data
        end_time = form.end_time.data

        if not (start_time and end_time and start_time < end_time):
            flash("开始时间必须早于结束时间。", "danger")
            return render_template("reservations/form.html", form=form, mode="edit")


        conflicts = Reservation.find_conflicts(
            room_id=form.room_id.data,
            start_time=start_time,
            end_time=end_time,
            exclude_reservation_id=reservation.id,
        )
        if conflicts:
            conflict_text = "；".join(
                f"{c.start_time:%m-%d %H:%M}-{c.end_time:%H:%M}"
                for c in conflicts[:3]
            )
            flash(f"该时间段已被预定：{conflict_text}", "danger")
            return render_template("reservations/form.html", form=form, mode="edit")

        if Reservation.has_conflict(
            room_id=form.room_id.data,
            start_time=start_time,
            end_time=end_time,
            exclude_reservation_id=reservation.id,
        ):
            flash("该时间段会议室已被预定，请选择其他时间。", "danger")
            return render_template("reservations/form.html", form=form, mode="edit")

        reservation.room_id = form.room_id.data
        reservation.title = form.title.data.strip()
        reservation.description = (form.description.data or "").strip()
        reservation.start_time = start_time
        reservation.end_time = end_time
        db.session.commit()

        flash("预定修改成功。", "success")
        return redirect(url_for("reservations.my_reservations"))

    return render_template("reservations/form.html", form=form, mode="edit")


@reservations_bp.route("/reservations/<int:reservation_id>/cancel", methods=["POST"])
@login_required
def cancel_reservation(reservation_id: int):
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.user_id != current_user.id:
        abort(403)

    reservation.status = "cancelled"
    db.session.commit()
    flash("预定已取消。", "success")
    return redirect(url_for("reservations.my_reservations"))