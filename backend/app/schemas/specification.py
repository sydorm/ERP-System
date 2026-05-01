from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field
from decimal import Decimal
from uuid import UUID
from datetime import datetime

from datetime import datetime
from enum import Enum

class CalculationDimension(str, Enum):
    HEIGHT = "height_mm"
    WIDTH = "width_mm"
    LENGTH = "length_mm"
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

class BOMLineCharacteristicMappingBase(BaseModel):
    component_characteristic_id: UUID
    parent_characteristic_id: UUID

class BOMLineCharacteristicMappingCreate(BOMLineCharacteristicMappingBase):
    pass

class BOMLineCharacteristicMappingResponse(BOMLineCharacteristicMappingBase):
    id: UUID
    bom_line_id: UUID

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
    
    # Detail-specific fields
    line_type: str = "material"
    size_from_attr: Optional[str] = None
    size_multiplier: Optional[Decimal] = Field(default=Decimal("1.0"))
    fixed_length: Optional[Decimal] = None
    fixed_width: Optional[Decimal] = None
    mapping_attr: Optional[str] = None
    material_mapping: Optional[Dict[str, Any]] = None

class SpecificationItemCreate(SpecificationItemBase):
    characteristic_mappings: Optional[List[BOMLineCharacteristicMappingCreate]] = []

class ComponentBasicInfo(BaseModel):
    id: UUID
    name: str
    sku: Optional[str] = None
    unit_of_measure: Optional[str] = None
    
    class Config:
        from_attributes = True

class SpecificationItemResponse(SpecificationItemBase):
    id: UUID
    component: Optional[ComponentBasicInfo] = None
    characteristic_mappings: List[BOMLineCharacteristicMappingResponse] = []
    
    class Config:
        from_attributes = True

class SpecificationStageBase(BaseModel):
    stage_id: UUID
    duration_hours: Decimal = Field(default=Decimal("0.0"), ge=0)
    brigade_id: Optional[UUID] = None # Link to Brigade
    sort_order: int = 0

class SpecificationStageCreate(SpecificationStageBase):
    pass

class DictionaryItemBasicInfo(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True

class BrigadeBasicInfo(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True

class SpecificationStageResponse(SpecificationStageBase):
    id: UUID
    stage: Optional[DictionaryItemBasicInfo] = None
    brigade: Optional[BrigadeBasicInfo] = None
    
    class Config:
        from_attributes = True

class ProductSpecificationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    is_active: bool = True
    is_default: bool = False
    notes: Optional[str] = None

class ProductSpecificationCreate(ProductSpecificationBase):
    items: List[SpecificationItemCreate] = []
    stages: List[SpecificationStageCreate] = []

class ProductSpecificationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    notes: Optional[str] = None
    items: Optional[List[SpecificationItemCreate]] = None
    stages: Optional[List[SpecificationStageCreate]] = None

class ProductSpecificationResponse(ProductSpecificationBase):
    id: UUID
    product_id: UUID
    items: List[SpecificationItemResponse] = []
    stages: List[SpecificationStageResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SpecificationCalculationRequest(BaseModel):
    width_mm: float
    height_mm: float
    length_mm: float
    weight_kg: float = 0.0
    custom_attributes: Optional[Dict[str, float]] = Field(default_factory=dict)

class CalculatedMaterialResponse(BaseModel):
    component_id: UUID
    component_name: str
    variant_id: Optional[UUID] = None
    variant_name: Optional[str] = None
    quantity: Decimal
    unit_of_measure: str
    stock_quantity: Optional[Decimal] = None
    notes: Optional[str] = None

