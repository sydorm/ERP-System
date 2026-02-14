from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal
from uuid import UUID
from .variant import ProductVariantCreate, ProductVariantResponse
from .specification import ProductSpecificationResponse

class ProductBase(BaseModel):
    """Base Product schema"""
    sku: str = Field(..., min_length=1, max_length=100, description="Stock Keeping Unit")
    name: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    unit_of_measure: str = Field("шт", min_length=1, max_length=50)
    price: Decimal = Field(default=Decimal("0.00"), ge=0)
    currency: str = Field("UAH", min_length=3, max_length=3)
    cost: Optional[Decimal] = Field(None, ge=0)
    is_active: bool = True

class ProductCreate(ProductBase):
    """Schema for creating a product"""
    variants: Optional[List[ProductVariantCreate]] = None

class ProductUpdate(BaseModel):
    """Schema for updating a product"""
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    unit_of_measure: Optional[str] = Field(None, min_length=1, max_length=50)
    price: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    cost: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None
    variants: Optional[List[ProductVariantCreate]] = None

class ProductResponse(ProductBase):
    """Schema for product response"""
    id: UUID
    company_id: UUID
    variants: List[ProductVariantResponse] = []
    specifications: List[ProductSpecificationResponse] = []

    class Config:
        from_attributes = True
