from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.api.dependencies import get_current_active_user
from app.models import (
    Order, User, ProductionOrder, PurchaseOrder, 
    Counterparty, CrmTask, AuditLog
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    company_id = current_user.company_id
    
    total_sales = db.query(func.sum(Order.total_amount)).filter(
        Order.company_id == company_id,
        Order.crm_stage != 'cancelled'
    ).scalar() or 0.0
    
    orders_count = db.query(func.count(Order.id)).filter(
        Order.company_id == company_id,
        Order.crm_stage != 'cancelled'
    ).scalar() or 0
    
    active_production = db.query(func.count(ProductionOrder.id)).filter(
        ProductionOrder.company_id == company_id,
        ProductionOrder.status.in_(['released', 'in_progress'])
    ).scalar() or 0
    
    total_purchases = db.query(func.sum(PurchaseOrder.total_amount)).filter(
        PurchaseOrder.company_id == company_id,
        PurchaseOrder.status != 'cancelled'
    ).scalar() or 0.0
    
    clients_count = db.query(func.count(Counterparty.id)).filter(
        Counterparty.company_id == company_id,
        Counterparty.is_deleted == False
    ).scalar() or 0
    
    active_tasks = db.query(func.count(CrmTask.id)).join(Order, CrmTask.order_id == Order.id).filter(
        Order.company_id == company_id,
        CrmTask.status == 'pending'
    ).scalar() or 0
    
    return {
        "total_sales": float(total_sales),
        "orders_count": orders_count,
        "active_production": active_production,
        "total_purchases": float(total_purchases),
        "clients_count": clients_count,
        "active_tasks": active_tasks
    }

@router.get("/managers")
async def get_dashboard_managers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    company_id = current_user.company_id
    
    # Top Managers
    top_managers = db.query(
        (User.first_name + ' ' + User.last_name).label('name'),
        func.count(Order.id),
        func.coalesce(func.sum(Order.total_amount), 0)
    ).join(User, Order.manager_id == User.id).filter(
        Order.company_id == company_id,
        Order.crm_stage == "done"
    ).group_by(User.id, User.first_name, User.last_name).order_by(func.sum(Order.total_amount).desc()).all()

    return [
        {"name": m[0], "orders_count": m[1], "total_amount": float(m[2])}
        for m in top_managers
    ]

@router.get("/funnel")
async def get_dashboard_funnel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    company_id = current_user.company_id
    
    stages = db.query(
        Order.crm_stage,
        func.count(Order.id),
        func.coalesce(func.sum(Order.total_amount), 0)
    ).filter(Order.company_id == company_id).group_by(Order.crm_stage).all()
    
    return [
        {"stage": s[0], "count": s[1], "total": float(s[2])}
        for s in stages
    ]

@router.get("/activity")
async def get_dashboard_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    company_id = current_user.company_id
    
    logs = db.query(AuditLog).join(User, AuditLog.user_id == User.id).filter(
        User.company_id == company_id
    ).order_by(AuditLog.created_at.desc()).limit(20).all()
    
    activity = []
    for log in logs:
        user = db.query(User).filter(User.id == log.user_id).first()
        user_name = f"{user.first_name} {user.last_name}" if user else "Система"
        
        action_map = {
            "CREATE": "Створив",
            "UPDATE": "Оновив",
            "DELETE": "Видалив",
            "POST": "Провів",
            "UNPOST": "Скасував проведення"
        }
        action_str = action_map.get(log.action, log.action)
        
        entity_map = {
            "order": "замовлення",
            "invoice": "рахунок",
            "product": "товар",
            "production_order": "виробниче завдання",
            "purchase_order": "замовлення постачальнику"
        }
        entity_str = entity_map.get(log.entity_type, log.entity_type)
        
        activity.append({
            "user": user_name,
            "action": f"{action_str} {entity_str}",
            "created_at": log.created_at.isoformat()
        })
        
    return activity
