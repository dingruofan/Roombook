from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models.room import Room
from app.rooms import rooms_bp
from app.rooms.forms import RoomForm
from flask import request
from app.models.reservation import Reservation
from datetime import datetime
import re


def _all_reserved(room_id: int):
    now = datetime.now()
    reservations = (
        Reservation.query.filter(
            Reservation.room_id == room_id,
            Reservation.status == "active",
            Reservation.end_time > now,
        )
        .join(Reservation.user)
        .order_by(Reservation.start_time.asc())
        .all()
    )

    result = []
    for r in reservations:
        duration_hours = (r.end_time - r.start_time).total_seconds() / 3600
        duration_str = f"{int(duration_hours)}小时" if duration_hours.is_integer() else f"{duration_hours:.1f}小时"
        display_str = f"{r.start_time:%Y-%m-%d}：{r.start_time:%H:%M}~{r.end_time:%H:%M} ({duration_str}) | {r.user.full_name or r.user.username}"
        result.append(
            {
                "display": display_str,
                "title": r.title,
            }
        )
    return result

def _extract_room_number(name: str) -> int:
    # 提取名称中的第一段数字；没有数字时放到最后
    m = re.search(r"\d+", name or "")
    return int(m.group()) if m else 10**9

@rooms_bp.route("/rooms")
@login_required
def list_rooms():
    active = request.args.get("active", "1")
    query = Room.query

    if active == "1":
        query = query.filter_by(is_active=True)
    elif active == "0":
        query = query.filter_by(is_active=False)

    rooms = query.all()
    reserved_map = {room.id: _all_reserved(room.id) for room in rooms}

    # 排序规则：
    # 1) 预订数量降序
    # 2) 名称中数字升序（如 A1, A2, A10）
    # 3) 名称字典序兜底
    rooms_sorted = sorted(
        rooms,
        key=lambda room: (
            -len(reserved_map.get(room.id, [])),
            _extract_room_number(room.name),
            room.name or "",
        ),
    )

    return render_template(
        "rooms/list.html",
        rooms=rooms_sorted,
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