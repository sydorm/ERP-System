from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Order, User, Notification
from app.models.order_activity_log import OrderActivityLog

ACTIVE_STAGES = ["new", "payment", "processing", "production"]

SLA_WARNING_HOURS = 3   # yellow timer on card
SLA_CRITICAL_HOURS = 5  # red timer + notify manager
SLA_DIRECTOR_HOURS = 8  # notify director (role=admin)


def _last_activity_per_order(db: Session, order_ids: list) -> dict:
    """Return {order_id_str: last_activity_datetime} using activity log, fallback to order.updated_at."""
    if not order_ids:
        return {}

    log_rows = (
        db.query(OrderActivityLog.order_id, func.max(OrderActivityLog.created_at).label("last_log"))
        .filter(OrderActivityLog.order_id.in_(order_ids))
        .group_by(OrderActivityLog.order_id)
        .all()
    )
    log_map = {str(r.order_id): r.last_log for r in log_rows}

    orders = db.query(Order.id, Order.updated_at, Order.created_at).filter(Order.id.in_(order_ids)).all()
    result = {}
    for o in orders:
        key = str(o.id)
        result[key] = log_map.get(key) or o.updated_at or o.created_at or datetime.utcnow()
    return result


def get_sla_status_for_company(db: Session, company_id) -> dict:
    """
    Return {order_id: {sla_level, hours_since_activity}} for all active orders of a company.
    sla_level: "ok" | "warning" | "critical" | "urgent"
    """
    active_orders = (
        db.query(Order.id)
        .filter(Order.company_id == company_id, Order.crm_stage.in_(ACTIVE_STAGES))
        .all()
    )
    order_ids = [r.id for r in active_orders]
    if not order_ids:
        return {}

    activity_map = _last_activity_per_order(db, order_ids)
    now = datetime.utcnow()
    result = {}
    for oid in order_ids:
        last = activity_map.get(str(oid), now)
        hours = (now - last).total_seconds() / 3600
        if hours >= SLA_DIRECTOR_HOURS:
            level = "urgent"
        elif hours >= SLA_CRITICAL_HOURS:
            level = "critical"
        elif hours >= SLA_WARNING_HOURS:
            level = "warning"
        else:
            level = "ok"
        result[str(oid)] = {"sla_level": level, "hours_since_activity": round(hours, 1)}
    return result


def _already_notified(db: Session, user_id, notif_type: str, order_number: str, within_hours: float) -> bool:
    """True if an unread notification of this type for this order was created recently."""
    cutoff = datetime.utcnow() - timedelta(hours=within_hours)
    return db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False,
        Notification.type == notif_type,
        Notification.title.contains(order_number),
        Notification.created_at >= cutoff,
    ).first() is not None


def run_sla_check(db: Session):
    """
    Called every 30 min by APScheduler.
    Scans all active orders across all companies and creates persistent Notification
    records when SLA thresholds are exceeded.
    """
    now = datetime.utcnow()

    active_orders = (
        db.query(Order)
        .filter(Order.crm_stage.in_(ACTIVE_STAGES))
        .all()
    )
    if not active_orders:
        return

    order_ids = [o.id for o in active_orders]
    activity_map = _last_activity_per_order(db, order_ids)

    for order in active_orders:
        last = activity_map.get(str(order.id), now)
        hours = (now - last).total_seconds() / 3600

        if hours >= SLA_DIRECTOR_HOURS:
            # Notify all admins of the company
            admins = (
                db.query(User)
                .filter(User.company_id == order.company_id, User.role == "admin")
                .all()
            )
            for admin in admins:
                if not _already_notified(db, admin.id, "SLA_URGENT", order.order_number, SLA_DIRECTOR_HOURS):
                    db.add(Notification(
                        company_id=order.company_id,
                        user_id=admin.id,
                        title=f"SLA критичний: {order.order_number}",
                        message=(
                            f"Замовлення без активності {int(hours)} год. "
                            f"Вимагає уваги директора."
                        ),
                        type="SLA_URGENT",
                        is_read=False,
                        data={"order_id": str(order.id), "order_number": order.order_number,
                              "hours": round(hours, 1)},
                    ))

        elif hours >= SLA_CRITICAL_HOURS:
            # Notify assigned manager
            if order.manager_id:
                if not _already_notified(db, order.manager_id, "SLA_CRITICAL", order.order_number, SLA_CRITICAL_HOURS):
                    db.add(Notification(
                        company_id=order.company_id,
                        user_id=order.manager_id,
                        title=f"SLA порушено: {order.order_number}",
                        message=(
                            f"Замовлення без дії {int(hours)} год. "
                            f"Необхідна реакція менеджера."
                        ),
                        type="SLA_CRITICAL",
                        is_read=False,
                        data={"order_id": str(order.id), "order_number": order.order_number,
                              "hours": round(hours, 1)},
                    ))

    db.commit()
