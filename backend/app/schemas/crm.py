from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class CrmContactCreate(BaseModel):
    result: str  # no_answer / thinking / refused / confirmed
    note: Optional[str] = None
    next_contact_at: Optional[datetime] = None  # required when result == "thinking"


class CrmContactResponse(BaseModel):
    id: UUID
    order_id: UUID
    result: str
    note: Optional[str] = None
    manager_id: Optional[UUID] = None
    contacted_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CrmTaskResponse(BaseModel):
    id: UUID
    order_id: UUID
    scheduled_at: datetime
    status: str
    manager_id: Optional[UUID] = None
    order_number: Optional[str] = None
    client_name: Optional[str] = None
    client_phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CrmTaskReschedule(BaseModel):
    scheduled_at: datetime
