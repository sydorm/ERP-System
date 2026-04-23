from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from app.schemas.counterparty import CounterpartyResponse
from app.schemas.dictionary import DictionaryItemResponse

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

# --- Production Order Assignment ---
class ProductionOrderAssignmentBase(BaseModel):
    employee_id: Optional[UUID] = None
    stage_id: UUID
    brigade_id: Optional[UUID] = None
    quantity: Optional[float] = None
    planned_hours: float = 0.0
    status: str = "pending"

class ProductionOrderAssignmentCreate(ProductionOrderAssignmentBase):
    pass

class ProductionOrderAssignmentResponse(ProductionOrderAssignmentBase):
    id: UUID
    production_order_id: UUID
    stage: Optional[DictionaryItemResponse] = None
    
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

    source_type: str = "quick"
    source_id: Optional[UUID] = None
    client_id: Optional[UUID] = None
    priority: str = "normal"

class ProductionOrderCreate(ProductionOrderBase):
    lines: List[ProductionOrderLineCreate]
    materials: List[ProductionOrderMaterialCreate] = [] # Optional initially, can be calculated
    assignments: List[ProductionOrderAssignmentCreate] = []

class ProductionOrderUpdate(ProductionOrderBase):
    lines: Optional[List[ProductionOrderLineCreate]] = None
    materials: Optional[List[ProductionOrderMaterialCreate]] = None
    assignments: Optional[List[ProductionOrderAssignmentCreate]] = None
    status: Optional[str] = None

class ProductionOrderResponse(ProductionOrderBase):
    id: UUID
    order_number: Optional[str] = None
    order_date: Optional[datetime] = None
    created_by: Optional[UUID] = None
    completed_at: Optional[datetime] = None
    
    client: Optional[CounterpartyResponse] = None
    
    lines: List[ProductionOrderLineResponse] = []
    materials: List[ProductionOrderMaterialResponse] = []
    assignments: List[ProductionOrderAssignmentResponse] = []
    
    class Config:
        from_attributes = True
