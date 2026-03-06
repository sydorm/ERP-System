from pydantic import BaseModel, UUID4, ConfigDict
from typing import Dict, Any, Optional
from datetime import datetime

class AuditLogBase(BaseModel):
    entity_type: str
    entity_id: UUID4
    action: str
    user_id: Optional[UUID4] = None
    changes: Dict[str, Any]

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogResponse(AuditLogBase):
    id: UUID4
    created_at: datetime
    
    # We might want to join user data later, but for now just include basic fields
    user_name: Optional[str] = None
    user_email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
