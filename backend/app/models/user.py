"""
User model - represents system users
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, JSON, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class User(BaseModel):
    """
    User model
    Represents a user of the system
    """
    __tablename__ = "users"
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    
    # Status & Permissions
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    role = Column(String(50), default="worker", nullable=False)  # admin, manager, worker
    permissions = Column(JSON, default={}, nullable=False)
    
    # New fields
    phone = Column(String(50), nullable=True)
    blocked_at = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Foreign Keys
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="users")
    employee = relationship("Employee", backref="user")
    created_orders = relationship("Order", back_populates="created_by_user", foreign_keys="Order.created_by", overlaps="manager")
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<User {self.email}>"


class UserLoginLog(BaseModel):
    """
    User login logs
    """
    __tablename__ = "user_login_logs"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ip_address = Column(String(50), nullable=True)
    
    user = relationship("User", backref="login_logs")
