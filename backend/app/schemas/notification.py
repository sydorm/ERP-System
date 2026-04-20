from pydantic import BaseModel, ConfigDict
from typing import Optional, Any, Dict
from uuid import UUID
from datetime import datetime


class NotificationBase(BaseModel):
    type: str
    title: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    is_read: bool = False


class NotificationResponse(NotificationBase):
    id: UUID
    company_id: UUID
    user_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationUpdate(BaseModel):
    is_read: bool
