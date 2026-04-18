from sqlalchemy import Column, String, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel


class CrmContact(BaseModel):
    __tablename__ = "crm_contacts"

    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    result = Column(String(50), nullable=False)  # no_answer/thinking/refused/confirmed
    note = Column(Text, nullable=True)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    contacted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    order = relationship("Order", back_populates="contacts")
    manager = relationship("User")

    def __repr__(self):
        return f"<CrmContact {self.result}>"


class CrmTask(BaseModel):
    __tablename__ = "crm_tasks"

    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    status = Column(String(50), nullable=False, default="pending")  # pending/done/cancelled
    manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    order = relationship("Order", back_populates="tasks")
    manager = relationship("User")

    def __repr__(self):
        return f"<CrmTask {self.status} at {self.scheduled_at}>"
