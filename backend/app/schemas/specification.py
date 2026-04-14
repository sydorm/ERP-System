from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field
from decimal import Decimal
from uuid import UUID
from datetime import datetime

from datetime import datetime
from enum import Enum

class CalculationDimension(str, Enum):
    HEIGHT = "height_cm"
    WIDTH = "width_cm"
    LENGTH = "length_cm"
    AREA = "area"
    VOLUME = "volume"
    CUSTOM = "custom"

class CalculationType(str, Enum):
    FIXED = "fixed"
    INTERPOLATION = "interpolation"
    AREA = "area"
    VOLUME = "volume"
    FORMULA = "formula"

class CalculationPoint(BaseModel):
    input: float
    output: float

class SpecificationCalculationBase(BaseModel):
    dimension: CalculationDimension
    data_points: List[CalculationPoint]
    formula: Optional[str] = None
    waste_factor: Decimal = Field(default=Decimal("0.0"), ge=0, le=1)
    is_active: bool = True

class SpecificationCalculationCreate(SpecificationCalculationBase):
    pass

class SpecificationCalculationResponse(SpecificationCalculationBase):
    id: UUID
    specification_item_id: UUID
    
    class Config:
        from_attributes = True

class SpecificationItemBase(BaseModel):
    component_id: UUID
    quantity: Decimal = Field(default=Decimal("0.0"), ge=0)
    unit_of_measure: Optional[str] = None
    notes: Optional[str] = None
    
    # Merged Smart Calculation Fields
    is_calculated: bool = False
    calc_type: Optional[CalculationType] = CalculationType.FIXED
    calc_dimension: Optional[CalculationDimension] = None
    calc_data_points: Optional[Any] = None
    calc_dim_config: Optional[Any] = None
    calc_formula: Optional[str] = None
    calc_waste_factor: Decimal = Field(default=Decimal("0.0"), ge=0, le=1)

class SpecificationItemCreate(SpecificationItemBase):
    pass

class ComponentBasicInfo(BaseModel):
    id: UUID
    name: str
    sku: str
    unit_of_measure: Optional[str] = None
    
    class Config:
        from_attributes = True

class SpecificationItemResponse(SpecificationItemBase):
    id: UUID
    component: Optional[ComponentBasicInfo] = None
    
    class Config:
        from_attributes = True

class ProductSpecificationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    is_active: bool = True
    is_default: bool = False
    notes: Optional[str] = None

class ProductSpecificationCreate(ProductSpecificationBase):
    items: List[SpecificationItemCreate] = []

class ProductSpecificationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    notes: Optional[str] = None
    items: Optional[List[SpecificationItemCreate]] = None

class ProductSpecificationResponse(ProductSpecificationBase):
    id: UUID
    product_id: UUID
    items: List[SpecificationItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SpecificationCalculationRequest(BaseModel):
    width_cm: float
    height_cm: float
    length_cm: float
    weight_kg: float = 0.0
    custom_attributes: Optional[Dict[str, float]] = Field(default_factory=dict)

class CalculatedMaterialResponse(BaseModel):
    component_id: UUID
    component_name: str
    quantity: Decimal
    unit_of_measure: str
    notes: Optional[str] = None
