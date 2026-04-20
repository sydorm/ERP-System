from sqlalchemy import Column, String, Boolean, ForeignKey, Text, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel


class Notification(BaseModel):
    __tablename__ = "notifications"

    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # CALL, OVERDUE, DEADLINE_SOON, STALE_LEAD, PAYMENT, STATUS_CHANGE
    type = Column(String(50), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    
    # For linking to objects (e.g., {"order_id": "...", "task_id": "..."})
    data = Column(JSON, nullable=True)
    
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    
    # Explicitly reuse created_at from BaseModel
    
    # Relationships
    user = relationship("User")
    company = relationship("Company")

    def __repr__(self):
        return f"<Notification {self.type} for {self.user_id}>"
