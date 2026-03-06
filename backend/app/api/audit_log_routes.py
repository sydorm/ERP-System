from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import uuid

from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])

@router.get("/{entity_type}/{entity_id}", response_model=List[AuditLogResponse])
def get_entity_audit_logs(
    entity_type: str,
    entity_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get audit history for a specific entity (e.g., an Order or Invoice)
    """
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id)
        .order_by(desc(AuditLog.created_at))
        .all()
    )
    
    # Simple join in python for user info to avoid complex DB joins on a JSONb table for now
    user_cache = {}
    result = []
    
    for log in logs:
        log_dict = {
            "id": log.id,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "action": log.action,
            "user_id": log.user_id,
            "changes": log.changes,
            "created_at": log.created_at,
            "user_name": None,
            "user_email": None
        }
        
        if log.user_id:
            if log.user_id not in user_cache:
                user = db.query(User).filter(User.id == log.user_id).first()
                if user:
                    user_cache[log.user_id] = f"{user.first_name or ''} {user.last_name or ''}".strip()
                    user_cache[f"{log.user_id}_email"] = user.email
            
            log_dict["user_name"] = user_cache.get(log.user_id)
            log_dict["user_email"] = user_cache.get(f"{log.user_id}_email")
            
        result.append(AuditLogResponse(**log_dict))
        
    return result
