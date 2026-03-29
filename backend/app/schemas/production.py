from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

# --- Production Order Material ---
class ProductionOrderMaterialBase(BaseModel):
    component_id: UUID
    required_quantity: float = Field(..., gt=0)
    issued_quantity: float = 0.0
    unit_of_measure: Optional[str] = None
    cost_estimate: Optional[float] = None

class ProductionOrderMaterialCreate(ProductionOrderMaterialBase):
    pass

class ProductionOrderMaterialUpdate(ProductionOrderMaterialBase):
    pass

class ProductionOrderMaterialResponse(ProductionOrderMaterialBase):
    id: UUID
    production_order_id: UUID
    
    class Config:
        from_attributes = True

# --- Production Order Line ---
class ProductionOrderLineBase(BaseModel):
    product_id: UUID
    variant_id: Optional[UUID] = None
    specification_id: Optional[UUID] = None
    quantity: float = Field(..., gt=0)
    produced_quantity: float = 0.0

class ProductionOrderLineCreate(ProductionOrderLineBase):
    pass

class ProductionOrderLineUpdate(ProductionOrderLineBase):
    pass

class ProductionOrderLineResponse(ProductionOrderLineBase):
    id: UUID
    production_order_id: UUID
    
    class Config:
        from_attributes = True

# --- Production Order ---
class ProductionOrderBase(BaseModel):
    due_date: Optional[datetime] = None
    status: str = "draft"
    base_order_id: Optional[UUID] = None
    company_id: UUID
    warehouse_id: UUID
    comment: Optional[str] = None

class ProductionOrderCreate(ProductionOrderBase):
    lines: List[ProductionOrderLineCreate]
    materials: List[ProductionOrderMaterialCreate] = [] # Optional initially, can be calculated

class ProductionOrderUpdate(ProductionOrderBase):
    lines: Optional[List[ProductionOrderLineCreate]] = None
    materials: Optional[List[ProductionOrderMaterialCreate]] = None
    status: Optional[str] = None

class ProductionOrderResponse(ProductionOrderBase):
    id: UUID
    order_number: str
    order_date: datetime
    created_by: Optional[UUID] = None
    completed_at: Optional[datetime] = None
    
    lines: List[ProductionOrderLineResponse] = []
    materials: List[ProductionOrderMaterialResponse] = []
    
    class Config:
        from_attributes = True
