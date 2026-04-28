from typing import List
from uuid import UUID
from datetime import datetime, timedelta, date, time as dt_time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.api.dependencies import get_current_active_user
from app.models import Order, User
from app.models.crm import CrmContact, CrmTask
from app.models.order_activity_log import OrderActivityLog
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


@router.get("/analytics")
async def get_crm_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get CRM Analytics: funnel, conversion, top managers, and avg time per stage."""
    company_id = current_user.company_id
    
    # 1. Funnel
    stages = ["new", "payment", "processing", "production", "done"]
    funnel_data = []
    for s in stages:
        res = db.query(
            func.count(Order.id),
            func.coalesce(func.sum(Order.total_amount), 0)
        ).filter(
            Order.company_id == company_id,
            Order.crm_stage == s,
        ).first()
        funnel_data.append({
            "stage": s,
            "count": res[0],
            "total": float(res[1])
        })

    # 2. Conversion
    conversion_data = []
    for i in range(len(funnel_data) - 1):
        curr = funnel_data[i]
        nxt = funnel_data[i+1]
        percent = 0
        # Simple ratio: next stage count / current stage count
        if curr["count"] > 0:
            percent = round((nxt["count"] / curr["count"]) * 100)
        conversion_data.append({
            "from": curr["stage"],
            "to": nxt["stage"],
            "percent": min(percent, 100)
        })

    # 3. Top Managers (by total amount of 'done' orders)
    top_managers = db.query(
        User.name,
        func.count(Order.id),
        func.coalesce(func.sum(Order.total_amount), 0)
    ).join(User, Order.manager_id == User.id).filter(
        Order.company_id == company_id,
        Order.crm_stage == "done"
    ).group_by(User.id, User.name).order_by(func.sum(Order.total_amount).desc()).limit(5).all()

    managers_list = [
        {"name": m[0], "count": m[1], "total": float(m[2])}
        for m in top_managers
    ]

    # 4. Avg Stage Days
    avg_days_data = []
    for s in stages:
        res = db.query(
            func.avg(func.extract('epoch', func.now() - Order.order_date))
        ).filter(
            Order.company_id == company_id,
            Order.crm_stage == s
        ).scalar()
        
        days = round((res or 0) / 86400, 1)
        avg_days_data.append({"stage": s, "days": days})

    return {
        "funnel": funnel_data,
        "conversion": conversion_data,
        "top_managers": managers_list,
        "avg_stage_days": avg_days_data
    }


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
        communication_type=data.communication_type,
        note=data.note,
        manager_id=current_user.id,
        contacted_at=datetime.utcnow(),
    )
    db.add(contact)
    db.add(OrderActivityLog(
        order_id=order_id,
        company_id=order.company_id,
        action_type="contact",
        manager_id=current_user.id,
    ))

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
        order.crm_stage = "payment"
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


# ─── SLA Status ───────────────────────────────────────────────────────────────

@router.get("/orders/sla-status")
async def get_sla_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Return SLA status for all active orders of the company.
    Response: { order_id: { sla_level: "ok"|"warning"|"critical"|"urgent", hours_since_activity: float } }
    """
    from app.services.sla_service import get_sla_status_for_company
    return get_sla_status_for_company(db, current_user.company_id)
