from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.dependencies import get_db, get_current_user
from app.models.product import Product
from app.models.variant import ProductVariant
from app.models.specification import ProductSpecification, SpecificationItem
from app.models.user import User
from app.schemas.specification import (
    ProductSpecificationCreate,
    ProductSpecificationResponse,
    ProductSpecificationUpdate
)

from sqlalchemy.orm import Session, joinedload

router = APIRouter(prefix="/products", tags=["Specifications"])

@router.get("/{product_id}/specifications", response_model=List[ProductSpecificationResponse])
async def list_specifications(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all specifications for a product."""
    specs = db.query(ProductSpecification).options(
        joinedload(ProductSpecification.items).options(
            joinedload(SpecificationItem.component)
        )
    ).filter(
        ProductSpecification.product_id == product_id
    ).order_by(ProductSpecification.created_at.desc()).all()
    return specs


@router.post("/{product_id}/specifications", response_model=ProductSpecificationResponse, status_code=status.HTTP_201_CREATED)
async def create_specification(
    product_id: UUID,
    spec_in: ProductSpecificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new specification (Bill of Materials) for a product."""
    # Verify product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # If this is set as default, unset others
    if spec_in.is_default:
        db.query(ProductSpecification).filter(ProductSpecification.product_id == product_id).update({"is_default": False})

    db_spec = ProductSpecification(
        product_id=product_id,
        name=spec_in.name,
        is_active=spec_in.is_active,
        is_default=spec_in.is_default,
        notes=spec_in.notes
    )
    db.add(db_spec)
    db.flush() # get id

    # Add items
    for item_in in spec_in.items:
        db_item = SpecificationItem(
            specification_id=db_spec.id,
            component_id=item_in.component_id,
            quantity=item_in.quantity,
            unit_of_measure=item_in.unit_of_measure,
            notes=item_in.notes,
            # Merged calculation fields
            is_calculated=item_in.is_calculated,
            calc_dimension=item_in.calc_dimension,
            calc_data_points=[p.dict() for p in item_in.calc_data_points] if item_in.calc_data_points else None,
            calc_formula=item_in.calc_formula,
            calc_waste_factor=item_in.calc_waste_factor
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_spec)
    return db_spec


@router.put("/specifications/{spec_id}", response_model=ProductSpecificationResponse)
async def update_specification(
    spec_id: UUID,
    spec_in: ProductSpecificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a specification and its items."""
    db_spec = db.query(ProductSpecification).filter(ProductSpecification.id == spec_id).first()
    if not db_spec:
        raise HTTPException(status_code=404, detail="Specification not found")

    # If making default, unset others first
    if spec_in.is_default and not db_spec.is_default:
         db.query(ProductSpecification).filter(
             ProductSpecification.product_id == db_spec.product_id,
             ProductSpecification.id != spec_id
         ).update({"is_default": False})

    update_data = spec_in.dict(exclude={'items'}, exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_spec, key, value)

    # Handle items logic (simple replace all for now to keep it macro and fast)
    if spec_in.items is not None:
        db.query(SpecificationItem).filter(SpecificationItem.specification_id == spec_id).delete()
        for item_in in spec_in.items:
            db_item = SpecificationItem(
                specification_id=db_spec.id,
                component_id=item_in.component_id,
                quantity=item_in.quantity,
                unit_of_measure=item_in.unit_of_measure,
                notes=item_in.notes,
                # Merged calculation fields
                is_calculated=item_in.is_calculated,
                calc_dimension=item_in.calc_dimension,
                calc_data_points=[p.dict() for p in item_in.calc_data_points] if item_in.calc_data_points else None,
                calc_formula=item_in.calc_formula,
                calc_waste_factor=item_in.calc_waste_factor
            )
            db.add(db_item)

    db.commit()
    db.refresh(db_spec)
    return db_spec

@router.delete("/specifications/{spec_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_specification(
    spec_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a specification."""
    db_spec = db.query(ProductSpecification).filter(ProductSpecification.id == spec_id).first()
    if not db_spec:
        raise HTTPException(status_code=404, detail="Specification not found")
        
    db.delete(db_spec)
    db.commit()
    return None
