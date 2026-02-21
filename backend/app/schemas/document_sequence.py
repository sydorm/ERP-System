from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from uuid import UUID

class DocumentSequenceBase(BaseModel):
    prefix: str = Field(default="", max_length=20)
    next_number: int = Field(default=1, ge=1)
    padding: int = Field(default=5, ge=1, le=10)

class DocumentSequenceUpdate(DocumentSequenceBase):
    pass

class DocumentSequenceResponse(DocumentSequenceBase):
    id: int
    document_type: str
    
    model_config = ConfigDict(from_attributes=True)
