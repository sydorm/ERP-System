from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.dependencies import get_db, get_current_user
from app.models.attribute import Attribute, AttributeOption, CategoryAttribute
from app.models.variant import ProductVariant, VariantValue
from app.models.user import User
from app.schemas.attribute import AttributeCreate, AttributeResponse, CategoryAttributeBase, CategoryAttributeResponse
from app.schemas.variant import ProductVariantCreate, ProductVariantResponse

router = APIRouter(prefix="/api/v1/attributes", tags=["Product Attributes"])

# ATTRIBUTES
@router.get("/", response_model=List[AttributeResponse])
async def get_attributes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Attribute).filter(Attribute.company_id == current_user.company_id).all()

@router.post("/", response_model=AttributeResponse)
async def create_attribute(
    attr_in: AttributeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    attr_data = attr_in.dict(exclude={"options"})
    db_attr = Attribute(**attr_data, company_id=current_user.company_id)
    db.add(db_attr)
    db.flush()
    
    if attr_in.options:
        for opt in attr_in.options:
            db_opt = AttributeOption(**opt.dict(), attribute_id=db_attr.id)
            db.add(db_opt)
            
    db.commit()
    db.refresh(db_attr)
    return db_attr

@router.patch("/{attribute_id}/archive", response_model=AttributeResponse)
async def archive_attribute(
    attribute_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    attr = db.query(Attribute).filter(Attribute.id == attribute_id, Attribute.company_id == current_user.company_id).first()
    if not attr:
        raise HTTPException(status_code=404, detail="Attribute not found")
    
    attr.is_archived = True
    db.commit()
    db.refresh(attr)
    return attr

# CATEGORY LINKS
@router.get("/category/{category_code}", response_model=List[CategoryAttributeResponse])
async def get_category_attributes(
    category_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(CategoryAttribute).filter(CategoryAttribute.category_code == category_code).all()

@router.post("/category", response_model=CategoryAttributeResponse)
async def link_attribute_to_category(
    link_in: CategoryAttributeBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_link = CategoryAttribute(**link_in.dict())
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link

# VARIANTS
variant_router = APIRouter(prefix="/api/v1/variants", tags=["Product Variants"])

@router.post("/variants", response_model=ProductVariantResponse) # Using original router or split
async def create_variant(
    variant_in: ProductVariantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    var_data = variant_in.dict(exclude={"values"})
    db_var = ProductVariant(**var_data)
    db.add(db_var)
    db.flush()
    
    for val in variant_in.values:
        db_val = VariantValue(**val.dict(), variant_id=db_var.id)
        db.add(db_val)
        
    db.commit()
    db.refresh(db_var)
    return db_var
