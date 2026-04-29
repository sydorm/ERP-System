from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.api.dependencies import get_current_active_user
from app.models import User
from app.models.business_process import BusinessProcessRule, AutomationLog

router = APIRouter(prefix="/business-process", tags=["Business Process"])


# ─── Pydantic schemas ─────────────────────────────────────────────────────────

class RuleOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    is_active: bool
    source_type: str
    event_type: str
    from_status: Optional[str] = None
    to_status: str
    action_type: str
    mode: str
    prevent_duplicates: bool
    log_execution: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True
    source_type: str
    event_type: str = "status_changed"
    from_status: Optional[str] = None
    to_status: str
    action_type: str
    mode: str = "ask_confirmation"
    prevent_duplicates: bool = True
    log_execution: bool = True


class EventRequest(BaseModel):
    source_type: str
    source_id: UUID
    event_type: str
    to_status: str


class ExecuteRequest(BaseModel):
    rule_id: UUID
    source_type: str
    source_id: UUID


class LogOut(BaseModel):
    id: UUID
    rule_id: Optional[UUID] = None
    event_type: str
    source_type: str
    source_id: UUID
    action_type: Optional[str] = None
    status: str
    message: Optional[str] = None
    created_document_type: Optional[str] = None
    created_document_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Rules CRUD ──────────────────────────────────────────────────────────────

@router.get("/rules", response_model=List[RuleOut])
async def list_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return db.query(BusinessProcessRule).filter(
        BusinessProcessRule.company_id == current_user.company_id
    ).order_by(BusinessProcessRule.created_at).all()


@router.post("/rules", response_model=RuleOut, status_code=status.HTTP_201_CREATED)
async def create_rule(
    data: RuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    rule = BusinessProcessRule(**data.model_dump(), company_id=current_user.company_id)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.put("/rules/{rule_id}", response_model=RuleOut)
async def update_rule(
    rule_id: UUID,
    data: RuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    rule = db.query(BusinessProcessRule).filter(
        BusinessProcessRule.id == rule_id,
        BusinessProcessRule.company_id == current_user.company_id,
    ).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    for k, v in data.model_dump().items():
        setattr(rule, k, v)
    db.commit()
    db.refresh(rule)
    return rule


@router.patch("/rules/{rule_id}/toggle")
async def toggle_rule(
    rule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    rule = db.query(BusinessProcessRule).filter(
        BusinessProcessRule.id == rule_id,
        BusinessProcessRule.company_id == current_user.company_id,
    ).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    rule.is_active = not rule.is_active
    db.commit()
    return {"id": str(rule.id), "is_active": rule.is_active}


# ─── Engine endpoints ─────────────────────────────────────────────────────────

@router.post("/event")
async def evaluate_event(
    req: EventRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Evaluate business process rules for an event.
    Does NOT execute actions — returns what should happen.
    Frontend uses the result to decide whether to show a confirmation modal.
    """
    from app.services.business_process_engine import evaluate_event
    return evaluate_event(
        db,
        current_user.company_id,
        req.source_type,
        req.source_id,
        req.event_type,
        req.to_status,
    )


@router.post("/execute")
async def execute_rule(
    req: ExecuteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Execute a rule action (after user confirmation or automatic mode)."""
    from app.services.business_process_engine import execute_rule
    return execute_rule(
        db,
        current_user.company_id,
        req.rule_id,
        req.source_type,
        req.source_id,
        current_user.id,
    )


@router.post("/skip")
async def skip_rule(
    req: ExecuteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Log that user chose not to execute the rule."""
    from app.services.business_process_engine import skip_rule
    skip_rule(db, current_user.company_id, req.rule_id, req.source_type, req.source_id)
    return {"ok": True}


@router.get("/related-documents")
async def related_documents(
    source_type: str,
    source_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Return list of documents related to the given source document."""
    from app.services.business_process_engine import get_related_documents
    return get_related_documents(db, source_type, source_id)


# ─── Logs ─────────────────────────────────────────────────────────────────────

@router.get("/logs", response_model=List[LogOut])
async def list_logs(
    source_type: Optional[str] = None,
    source_id: Optional[UUID] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    q = db.query(AutomationLog).filter(AutomationLog.company_id == current_user.company_id)
    if source_type:
        q = q.filter(AutomationLog.source_type == source_type)
    if source_id:
        q = q.filter(AutomationLog.source_id == source_id)
    return q.order_by(AutomationLog.created_at.desc()).limit(limit).all()
