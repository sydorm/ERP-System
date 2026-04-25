from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal
from uuid import UUID
from .variant import ProductVariantCreate, ProductVariantResponse, ProductPriceRuleCreate, ProductPriceRuleResponse
from .specification import ProductSpecificationResponse


class ProductAttributeBase(BaseModel):
    attribute_id: UUID
    option_id: Optional[UUID] = None
    text_value: Optional[str] = None
    generates_sku: bool = True


class ProductAttributeCreate(ProductAttributeBase):
    pass


class ProductAttributeResponse(ProductAttributeBase):
    id: UUID
    
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    """Base Product schema"""
    sku: Optional[str] = Field(None, max_length=100, description="Stock Keeping Unit")
    name: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    unit_of_measure: str = Field("шт", min_length=1, max_length=50)
    price: Decimal = Field(default=Decimal("0.00"), ge=0)
    currency: str = Field("UAH", min_length=3, max_length=3)
    cost: Optional[Decimal] = Field(None, ge=0)
    is_active: bool = True
    variant_config: Optional[dict] = None
    
    # Dimensions and Weight
    length_cm: Optional[Decimal] = None
    width_cm: Optional[Decimal] = None
    height_cm: Optional[Decimal] = None
    weight_kg: Optional[Decimal] = None
    
    # Procurement & Stock Management
    min_stock: Optional[Decimal] = Field(Decimal("0.00"), ge=0)
    optimal_stock: Optional[Decimal] = Field(Decimal("0.00"), ge=0)
    default_supplier_id: Optional[UUID] = None
    delivery_days: Optional[int] = Field(0, ge=0)

    # Manufacturing Parameters
    production_time_hours: Optional[Decimal] = None
    complexity_code: Optional[str] = None
    min_production_batch: Optional[int] = 1
    max_production_per_day: Optional[int] = None
    special_production_conditions: Optional[str] = None
    
    # Performer Restrictions
    performer_restriction_type: Optional[str] = "any_role"
    restricted_brigade_id: Optional[UUID] = None
    restricted_employee_id: Optional[UUID] = None

class ProductCreate(ProductBase):
    """Schema for creating a product"""
    variants: Optional[List[ProductVariantCreate]] = None
    price_rule: Optional[ProductPriceRuleCreate] = None
    product_attributes: Optional[List[ProductAttributeCreate]] = None

class ProductUpdate(BaseModel):
    """Schema for updating a product"""
    sku: Optional[str] = Field(None, max_length=100)
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    unit_of_measure: Optional[str] = Field(None, min_length=1, max_length=50)
    price: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    cost: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None
    variant_config: Optional[dict] = None
    
    length_cm: Optional[Decimal] = None
    width_cm: Optional[Decimal] = None
    height_cm: Optional[Decimal] = None
    weight_kg: Optional[Decimal] = None
    
    # Procurement & Stock Management
    min_stock: Optional[Decimal] = None
    optimal_stock: Optional[Decimal] = None
    default_supplier_id: Optional[UUID] = None
    delivery_days: Optional[int] = None

    # Manufacturing Parameters
    production_time_hours: Optional[Decimal] = None
    complexity_code: Optional[str] = None
    min_production_batch: Optional[int] = None
    max_production_per_day: Optional[int] = None
    special_production_conditions: Optional[str] = None
    
    # Performer Restrictions
    performer_restriction_type: Optional[str] = None
    restricted_brigade_id: Optional[UUID] = None
    restricted_employee_id: Optional[UUID] = None
    
    variants: Optional[List[ProductVariantCreate]] = None
    price_rule: Optional[ProductPriceRuleCreate] = None
    product_attributes: Optional[List[ProductAttributeCreate]] = None

class ProductResponse(ProductBase):
    """Schema for product response"""
    id: UUID
    company_id: UUID
    variants: List[ProductVariantResponse] = []
    specifications: List[ProductSpecificationResponse] = []
    price_rule: Optional[ProductPriceRuleResponse] = None
    product_attributes: List[ProductAttributeResponse] = []
    stock_balance: float = 0.0

    class Config:
        from_attributes = True
