from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models.room import Room
from app.rooms import rooms_bp
from app.rooms.forms import RoomForm
from flask import request
from app.models.reservation import Reservation


def _all_reserved(room_id: int):
    reservations = (
        Reservation.query.filter(
            Reservation.room_id == room_id,
            Reservation.status == "active",
        )
        .join(Reservation.user)
        .order_by(Reservation.start_time.asc())
        .all()
    )

    result = []
    for r in reservations:
        # 计算会议时长（小时）
        duration_hours = (r.end_time - r.start_time).total_seconds() / 3600
        
        # 格式化为小数或整数
        if duration_hours.is_integer():
            duration_str = f"{int(duration_hours)}小时"
        else:
            duration_str = f"{duration_hours:.1f}小时"
        
        # 生成完整显示字符串：日期：时间段（时长）| 预定者
        display_str = f"{r.start_time:%Y-%m-%d}：{r.start_time:%H:%M}~{r.end_time:%H:%M} ({duration_str}) | {r.user.full_name or r.user.username}"
        
        result.append({
            "time": f"{r.start_time:%Y-%m-%d}：{r.start_time:%H:%M} ~ {r.end_time:%H:%M}",
            "user": r.user.full_name or r.user.username,
            "title": r.title,
            "duration": duration_str,
            "display": display_str
        })
    
    return result

@rooms_bp.route("/rooms")
@login_required
def list_rooms():
    active = request.args.get("active", "1")
    query = Room.query.order_by(Room.id.desc())

    if active == "1":
        query = query.filter_by(is_active=True)
    elif active == "0":
        query = query.filter_by(is_active=False)

    rooms = query.all()
    reserved_map = {room.id: _all_reserved(room.id) for room in rooms}
    return render_template(
        "rooms/list.html",
        rooms=rooms,
        active_filter=active,
        reserved_map=reserved_map,
    )


@rooms_bp.route("/rooms/create", methods=["GET", "POST"])
@login_required
def create_room():
    if not current_user.is_admin:
        abort(403)

    form = RoomForm()
    if form.validate_on_submit():
        room = Room(
            name=form.name.data.strip(),
            location=(form.location.data or "").strip(),
            capacity=form.capacity.data or 0,
            equipment=(form.equipment.data or "").strip(),
            description=(form.description.data or "").strip(),
            is_active=bool(form.is_active.data),
        )
        db.session.add(room)
        db.session.commit()
        flash("会议室创建成功。", "success")
        target = "1" if room.is_active else "0"
        return redirect(url_for("rooms.list_rooms", active=target))

    if form.errors:
        flash(f"表单校验失败：{form.errors}", "danger")

    return render_template("rooms/create.html", form=form)

@rooms_bp.route("/rooms/<int:room_id>/edit", methods=["GET", "POST"])
@login_required
def edit_room(room_id: int):
    if not current_user.is_admin:
        abort(403)

    room = Room.query.get_or_404(room_id)
    form = RoomForm(obj=room)

    if form.validate_on_submit():
        room.name = form.name.data.strip()
        room.location = (form.location.data or "").strip()
        room.capacity = form.capacity.data or 0
        room.equipment = (form.equipment.data or "").strip()
        room.description = (form.description.data or "").strip()
        room.is_active = bool(form.is_active.data)

        db.session.commit()
        flash("会议室更新成功。", "success")
        return redirect(url_for("rooms.list_rooms", active="all"))

    return render_template("rooms/edit.html", form=form, room=room)