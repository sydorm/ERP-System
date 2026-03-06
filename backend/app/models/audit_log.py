import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.models.base import BaseModel

class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String, index=True, nullable=False) # e.g. "order", "invoice"
    entity_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    action = Column(String, nullable=False) # e.g. "CREATE", "UPDATE", "DELETE", "POST", "UNPOST"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    changes = Column(JSONB, nullable=False, default={}) # {"field_name": {"old": val1, "new": val2}}
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
