from typing import List
from uuid import UUID
from datetime import datetime, timedelta, date, time as dt_time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies import get_current_active_user
from app.models import Order, User
from app.models.crm import CrmContact, CrmTask
from app.schemas.crm import (
    CrmContactCreate, CrmContactResponse,
    CrmTaskResponse, CrmTaskReschedule,
)

router = APIRouter(prefix="/crm", tags=["CRM"])


def _next_working_day(dt: datetime) -> datetime:
    """Return the next working day at 10:00, skipping weekends."""
    next_dt = dt + timedelta(days=1)
    while next_dt.weekday() >= 5:  # 5=Sat, 6=Sun
        next_dt += timedelta(days=1)
    return next_dt.replace(hour=10, minute=0, second=0, microsecond=0)


# ─── Contact log ──────────────────────────────────────────────────────────────

@router.post("/orders/{order_id}/contacts", response_model=CrmContactResponse,
             status_code=status.HTTP_201_CREATED)
async def log_contact(
    order_id: UUID,
    data: CrmContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.company_id == current_user.company_id,
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    contact = CrmContact(
        order_id=order_id,
        result=data.result,
        note=data.note,
        manager_id=current_user.id,
        contacted_at=datetime.utcnow(),
    )
    db.add(contact)

    responsible = order.manager_id or current_user.id

    if data.result == "no_answer":
        order.contact_attempts = (order.contact_attempts or 0) + 1
        next_dt = _next_working_day(datetime.utcnow())
        order.next_contact_at = next_dt
        db.add(CrmTask(order_id=order_id, scheduled_at=next_dt,
                       status="pending", manager_id=responsible))

    elif data.result == "thinking":
        if data.next_contact_at:
            order.next_contact_at = data.next_contact_at
            db.add(CrmTask(order_id=order_id, scheduled_at=data.next_contact_at,
                           status="pending", manager_id=responsible))

    elif data.result == "refused":
        order.crm_stage = "cancelled"

    elif data.result == "confirmed":
        order.crm_stage = "confirmed"
        order.contact_attempts = 0

    db.commit()
    db.refresh(contact)
    return contact


@router.get("/orders/{order_id}/contacts", response_model=List[CrmContactResponse])
async def get_contacts(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.company_id == current_user.company_id,
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return (
        db.query(CrmContact)
        .filter(CrmContact.order_id == order_id)
        .order_by(CrmContact.contacted_at.desc())
        .all()
    )


# ─── Tasks ────────────────────────────────────────────────────────────────────

@router.get("/tasks/today", response_model=List[CrmTaskResponse])
async def get_today_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Return all pending tasks up to end-of-today for the current manager."""
    today_end = datetime.combine(date.today(), dt_time.max)

    tasks = (
        db.query(CrmTask)
        .join(Order, CrmTask.order_id == Order.id)
        .filter(
            CrmTask.manager_id == current_user.id,
            CrmTask.status == "pending",
            CrmTask.scheduled_at <= today_end,
            Order.company_id == current_user.company_id,
        )
        .order_by(CrmTask.scheduled_at)
        .all()
    )

    result = []
    for t in tasks:
        o = t.order
        cp = o.counterparty if o else None
        result.append(CrmTaskResponse(
            id=t.id,
            order_id=t.order_id,
            scheduled_at=t.scheduled_at,
            status=t.status,
            manager_id=t.manager_id,
            order_number=o.order_number if o else None,
            client_name=cp.name if cp else None,
            client_phone=cp.phone if cp else None,
        ))
    return result


@router.put("/tasks/{task_id}/complete")
async def complete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    task = db.query(CrmTask).filter(CrmTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = "done"
    db.commit()
    return {"ok": True}


@router.put("/tasks/{task_id}/reschedule")
async def reschedule_task(
    task_id: UUID,
    data: CrmTaskReschedule,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    task = db.query(CrmTask).filter(CrmTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.scheduled_at = data.scheduled_at
    # Also update the order's next_contact_at
    order = db.query(Order).filter(Order.id == task.order_id).first()
    if order:
        order.next_contact_at = data.scheduled_at
    db.commit()
    return {"ok": True}
