from pydantic import BaseModel, UUID4
from typing import List, Optional
import enum

class AttributeType(str, enum.Enum):
    TEXT = "TEXT"
    SELECT = "SELECT"
    NUMBER = "NUMBER"
    COLOR = "COLOR"
    BOOLEAN = "BOOLEAN"

# Attribute Options
class AttributeOptionBase(BaseModel):
    value: str
    color_code: Optional[str] = None
    sort_order: int = 0

class AttributeOptionCreate(AttributeOptionBase):
    pass

class AttributeOptionResponse(AttributeOptionBase):
    id: UUID4
    attribute_id: UUID4

    class Config:
        from_attributes = True

# Attributes
class AttributeBase(BaseModel):
    name: str
    type: AttributeType
    icon: Optional[str] = None
    description: Optional[str] = None
    is_archived: bool = False

class AttributeCreate(AttributeBase):
    options: Optional[List[AttributeOptionCreate]] = None

class AttributeResponse(AttributeBase):
    id: UUID4
    company_id: UUID4
    options: List[AttributeOptionResponse] = []

    class Config:
        from_attributes = True

# Category Mapping
class CategoryAttributeBase(BaseModel):
    category_code: str
    attribute_id: UUID4
    is_required: bool = False

class CategoryAttributeResponse(CategoryAttributeBase):
    id: UUID4
    attribute: AttributeResponse

    class Config:
        from_attributes = True
