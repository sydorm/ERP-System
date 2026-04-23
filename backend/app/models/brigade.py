import enum
import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Enum as saEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel

class Brigade(BaseModel):
    __tablename__ = "brigades"
    
    name = Column(String(255), nullable=False)
    stage_id = Column(UUID(as_uuid=True), ForeignKey("dictionary_items.id"), nullable=True) # References PRODUCTION_STAGE dictionary item
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    members = relationship("BrigadeMember", back_populates="brigade", cascade="all, delete-orphan")
    stage = relationship("DictionaryItem", foreign_keys=[stage_id])

class BrigadeMember(BaseModel):
    __tablename__ = "brigade_members"
    
    brigade_id = Column(UUID(as_uuid=True), ForeignKey("brigades.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    role_type = Column(String(50), default="main") # 'main' or 'reserve'
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    brigade = relationship("Brigade", back_populates="members")
    employee = relationship("Employee")
