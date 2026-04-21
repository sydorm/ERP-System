from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.api.dependencies import get_current_active_user
from app.models import User, Notification
from app.schemas.notification import NotificationResponse, NotificationUpdate

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get notifications for the current user (aggregated from DB and live alerts).
    """
    from datetime import date, time as dt_time
    from app.models import Order, Counterparty, CrmTask
    
    now = datetime.utcnow()
    today_end = datetime.combine(now.date(), dt_time.max)
    tomorrow = now.date() + timedelta(days=1)
    two_hours_ago = now - timedelta(hours=2)
    three_hours_ago = now - timedelta(hours=3)

    result = []

    # 1. Fetch persistent notifications from DB (Status changes, Payments)
    query = db.query(Notification).filter(
        Notification.user_id == current_user.id,
    )
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    stored = query.order_by(desc(Notification.created_at)).limit(limit).all()
    for n in stored:
        # Auto-expiry for old INFO notifications (24h)
        if n.type == 'INFO' and n.created_at < (now - timedelta(days=1)):
            continue
        result.append(NotificationResponse.model_validate(n))

    # 2. Dynamic CRM Tasks (Scheduled Calls)
    # Filter by user.id as manager. We skip company_id filter here to be more robust
    tasks = (
        db.query(CrmTask)
        .join(Order, CrmTask.order_id == Order.id)
        .filter(
            CrmTask.manager_id == current_user.id,
            CrmTask.status == "pending",
            CrmTask.scheduled_at <= today_end
        )
        .all()
    )
    
    for t in tasks:
        order = t.order
        client_name = order.counterparty.name if order.counterparty else "Клієнт"
        result.append(NotificationResponse(
            id=t.id,
            company_id=order.company_id,
            user_id=current_user.id,
            type='CALL',
            title=f"Передзвонити: {client_name}",
            message=f"Замовлення {order.order_number}",
            data={
                "task_id": str(t.id),
                "order_id": str(t.id), # For navigation
                "real_order_id": str(order.id),
                "order_number": order.order_number,
                "client_phone": order.counterparty.phone if order.counterparty else "",
                "scheduled_at": t.scheduled_at.isoformat()
            },
            is_read=False,
            created_at=t.scheduled_at
        ))

    # 3. Deadlines (Overdue and Tomorrow)
    # Overdue
    overdue_orders = (
        db.query(Order)
        .filter(
            Order.manager_id == current_user.id,
            Order.deadline_date < now.date(),
            Order.crm_stage != 'completed',
            Order.crm_stage != 'cancelled'
        ).limit(10).all()
    )
    for o in overdue_orders:
        result.append(NotificationResponse(
            id=o.id, company_id=o.company_id, user_id=current_user.id,
            type='DEADLINE_OVERDUE',
            title=f"Прострочено дедлайн: {o.order_number}",
            message=f"Дедлайн був {o.deadline_date}",
            data={"order_id": str(o.id), "order_number": o.order_number},
            is_read=False, created_at=datetime.combine(o.deadline_date, dt_time.min)
        ))

    # Tomorrow
    soon_orders = (
        db.query(Order)
        .filter(
            Order.manager_id == current_user.id,
            Order.deadline_date == tomorrow,
            Order.crm_stage != 'completed',
            Order.crm_stage != 'cancelled'
        ).limit(10).all()
    )
    for o in soon_orders:
        result.append(NotificationResponse(
            id=o.id, company_id=o.company_id, user_id=current_user.id,
            type='DEADLINE_SOON',
            title=f"Дедлайн завтра: {o.order_number}",
            message=f"Завтра ({tomorrow}) останній термін",
            data={"order_id": str(o.id), "order_number": o.order_number},
            is_read=False, created_at=datetime.combine(o.deadline_date, dt_time.min)
        ))

    # 4. Stale Leads (New > 2h/3h)
    from sqlalchemy import or_

    if current_user.is_superuser:
        # Admins see assigned + unassigned leads after 3 hours
        stale_limit = three_hours_ago
        stale_leads = db.query(Order).filter(
            Order.crm_stage == 'new',
            Order.created_at < stale_limit,
            or_(Order.manager_id == current_user.id, Order.manager_id == None)
        ).limit(10).all()
        title = "Заявка без обробки 3 год"
    else:
        # Managers see ONLY their assigned leads after 2 hours
        stale_limit = two_hours_ago
        stale_leads = db.query(Order).filter(
            Order.crm_stage == 'new',
            Order.created_at < stale_limit,
            Order.manager_id == current_user.id
        ).limit(10).all()
        title = "Нова заявка без обробки 2 год"

    for o in stale_leads:
        result.append(NotificationResponse(
            id=o.id, company_id=o.company_id, user_id=current_user.id,
            type='STALE_LEAD',
            title=f"{title}: {o.order_number}",
            message="Клієнт чекає на реакцію",
            data={"order_id": str(o.id), "order_number": o.order_number},
            is_read=False, created_at=o.created_at
        ))

    # Sort results
    # Priority: CALL/DEADLINE_OVERDUE (1), DEADLINE_SOON/STALE_LEAD (2), Others (3)
    def priority_sort(x):
        p = 3
        if x.type in ['CALL', 'DEADLINE_OVERDUE']: p = 1
        if x.type in ['DEADLINE_SOON', 'STALE_LEAD']: p = 2
        return (p, x.created_at)

    result.sort(key=priority_sort, reverse=False) # Lower priority value first, then time
    
    # After sorting by priority, we restore natural order within priority groups if needed
    # But usually descending time is better. Let's do:
    result.sort(key=lambda x: (1 if x.type in ['CALL', 'DEADLINE_OVERDUE'] else 2 if x.type in ['STALE_LEAD', 'DEADLINE_SOON'] else 3, -x.created_at.timestamp()))

    return result[:limit]


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification


@router.post("/read-all")
async def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    return {"message": "All notifications marked as read"}
