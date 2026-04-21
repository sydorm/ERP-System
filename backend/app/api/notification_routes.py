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
    Get notifications for the current user.
    """
    from datetime import date, time as dt_time
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    today_end = datetime.combine(date.today(), dt_time.max)

    query = db.query(Notification).filter(
        Notification.company_id == current_user.company_id,
        Notification.user_id == current_user.id,
    )
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    stored_notifications = query.order_by(desc(Notification.created_at)).limit(limit).all()
    
    # Filter stored notifications by 24h rule if they are informational
    result = []
    for n in stored_notifications:
        if n.type == 'INFO' and n.created_at < yesterday:
            continue
        result.append(NotificationResponse.model_validate(n))

    # 2. Fetch dynamic CRM Tasks (Scheduled callbacks)
    # We treat pending tasks for today as notifications
    from app.models import Order, Counterparty, CrmTask
    tasks = (
        db.query(CrmTask)
        .join(Order, CrmTask.order_id == Order.id)
        .filter(
            CrmTask.manager_id == current_user.id,
            CrmTask.status == "pending",
            CrmTask.scheduled_at <= today_end,
            Order.company_id == current_user.company_id,
        )
        .all()
    )
    
    for t in tasks:
        # Map task to notification format
        order = t.order
        client_name = order.counterparty.name if order.counterparty else "Клієнт"
        
        result.append(NotificationResponse(
            id=t.id, # We use the task ID as notification ID
            company_id=current_user.company_id,
            user_id=current_user.id,
            type='CALL',
            title=f"Передзвонити: {client_name}",
            message=f"Замовлення {order.order_number}",
            data={
                "task_id": str(t.id),
                "order_id": str(t.order_id),
                "order_number": order.order_number,
                "client_name": client_name,
                "client_phone": order.counterparty.phone if order.counterparty else "",
                "scheduled_at": t.scheduled_at.isoformat()
            },
            is_read=False,
            created_at=t.scheduled_at
        ))

    # Sort combined result by creation/scheduled time
    result.sort(key=lambda x: x.created_at, reverse=True)
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
