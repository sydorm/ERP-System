from pydantic import BaseModel, UUID4
from typing import List, Optional
from decimal import Decimal

# Variant Values
class VariantValueBase(BaseModel):
    attribute_id: UUID4
    option_id: Optional[UUID4] = None
    text_value: Optional[str] = None

class VariantValueCreate(VariantValueBase):
    pass

class VariantValueResponse(VariantValueBase):
    id: UUID4
    
    class Config:
        from_attributes = True

# Product Variants
class ProductVariantBase(BaseModel):
    sku: str
    price_override: Optional[Decimal] = None
    cost_override: Optional[Decimal] = None
    image_url: Optional[str] = None
    is_primary: bool = False
    is_active: bool = True

class ProductVariantCreate(ProductVariantBase):
    product_id: UUID4
    values: List[VariantValueCreate]

class ProductVariantResponse(ProductVariantBase):
    id: UUID4
    product_id: UUID4
    values: List[VariantValueResponse] = []

    class Config:
        from_attributes = True
