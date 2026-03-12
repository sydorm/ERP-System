from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.dependencies import get_db, get_current_user
from app.models.attribute import Attribute, AttributeOption, CategoryAttribute
from app.models.variant import ProductVariant, VariantValue
from app.models.user import User
from app.schemas.attribute import AttributeCreate, AttributeUpdate, AttributeResponse, CategoryAttributeBase, CategoryAttributeResponse, AttributeOptionCreate, AttributeOptionResponse
from app.schemas.variant import ProductVariantCreate, ProductVariantResponse

router = APIRouter(prefix="/attributes", tags=["Product Attributes"])

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
    attr_data = attr_in.dict(exclude={"options", "category_codes"})
    db_attr = Attribute(**attr_data, company_id=current_user.company_id)
    db.add(db_attr)
    db.flush()
    
    if attr_in.options:
        for opt in attr_in.options:
            db_opt = AttributeOption(**opt.dict(), attribute_id=db_attr.id)
            db.add(db_opt)
            
    if attr_in.category_codes is not None:
        for code in attr_in.category_codes:
            db_cat_attr = CategoryAttribute(category_code=code, attribute_id=db_attr.id)
            db.add(db_cat_attr)
            
    db.commit()
    db.refresh(db_attr)
    return db_attr

@router.put("/{attribute_id}", response_model=AttributeResponse)
async def update_attribute(
    attribute_id: UUID,
    attr_in: AttributeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    attr = db.query(Attribute).filter(Attribute.id == attribute_id, Attribute.company_id == current_user.company_id).first()
    if not attr:
        raise HTTPException(status_code=404, detail="Attribute not found")
        
    update_data = attr_in.dict(exclude_unset=True, exclude={"category_codes"})
    for field, value in update_data.items():
        setattr(attr, field, value)
        
    if attr_in.category_codes is not None:
        # Replace existing category links
        db.query(CategoryAttribute).filter(CategoryAttribute.attribute_id == attribute_id).delete()
        for code in set(attr_in.category_codes):
            db_cat_attr = CategoryAttribute(category_code=code, attribute_id=attribute_id)
            db.add(db_cat_attr)
            
    db.commit()
    db.refresh(attr)
    return attr

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

@router.delete("/{attribute_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attribute(
    attribute_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    attr = db.query(Attribute).filter(
        Attribute.id == attribute_id,
        Attribute.company_id == current_user.company_id
    ).first()
    if not attr:
        raise HTTPException(status_code=404, detail="Attribute not found")

    # Delete related options first
    db.query(AttributeOption).filter(AttributeOption.attribute_id == attribute_id).delete()
    db.delete(attr)
    db.commit()
    return None

@router.post("/{attribute_id}/options", response_model=AttributeOptionResponse)
async def add_attribute_option(
    attribute_id: UUID,
    option_in: AttributeOptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    attr = db.query(Attribute).filter(Attribute.id == attribute_id, Attribute.company_id == current_user.company_id).first()
    if not attr:
        raise HTTPException(status_code=404, detail="Attribute not found")
    
    db_opt = AttributeOption(**option_in.dict(), attribute_id=attribute_id)
    db.add(db_opt)
    db.commit()
    db.refresh(db_opt)
    return db_opt

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
