from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.dependencies import get_db, get_current_user
from app.models.product import Product
from app.models.variant import ProductVariant
from app.models.specification import ProductSpecification, SpecificationItem, ProductSpecificationStage, BOMLineCharacteristicMapping
from app.models.user import User
from app.schemas.specification import (
    ProductSpecificationCreate,
    ProductSpecificationResponse,
    ProductSpecificationUpdate,
    BOMLineCharacteristicMappingCreate,
    BOMLineCharacteristicMappingResponse
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
        ),
        joinedload(ProductSpecification.stages).options(
            joinedload(ProductSpecificationStage.stage),
            joinedload(ProductSpecificationStage.brigade)
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
            calc_type=item_in.calc_type,
            calc_dimension=item_in.calc_dimension,
            calc_data_points=item_in.calc_data_points,
            calc_dim_config=item_in.calc_dim_config,
            calc_formula=item_in.calc_formula,
            calc_waste_factor=item_in.calc_waste_factor,
            mapping_attr=item_in.mapping_attr,
            material_mapping=item_in.material_mapping
        )
        db.add(db_item)
        db.flush()
        if hasattr(item_in, 'characteristic_mappings') and item_in.characteristic_mappings:
            for m_in in item_in.characteristic_mappings:
                db_m = BOMLineCharacteristicMapping(
                    bom_line_id=db_item.id,
                    component_characteristic_id=m_in.component_characteristic_id,
                    parent_characteristic_id=m_in.parent_characteristic_id
                )
                db.add(db_m)

    # Add stages
    for stage_in in spec_in.stages:
        db_stage = ProductSpecificationStage(
            specification_id=db_spec.id,
            stage_id=stage_in.stage_id,
            duration_hours=stage_in.duration_hours,
            brigade_id=stage_in.brigade_id,
            sort_order=stage_in.sort_order
        )
        db.add(db_stage)

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

    update_data = spec_in.dict(exclude={'items', 'stages'}, exclude_unset=True)
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
                calc_type=item_in.calc_type,
                calc_dimension=item_in.calc_dimension,
                calc_data_points=item_in.calc_data_points,
                calc_dim_config=item_in.calc_dim_config,
                calc_formula=item_in.calc_formula,
                calc_waste_factor=item_in.calc_waste_factor,
                mapping_attr=item_in.mapping_attr,
                material_mapping=item_in.material_mapping
            )
            db.add(db_item)
            db.flush()
            if hasattr(item_in, 'characteristic_mappings') and item_in.characteristic_mappings:
                for m_in in item_in.characteristic_mappings:
                    db_m = BOMLineCharacteristicMapping(
                        bom_line_id=db_item.id,
                        component_characteristic_id=m_in.component_characteristic_id,
                        parent_characteristic_id=m_in.parent_characteristic_id
                    )
                    db.add(db_m)

    # Handle stages logic
    if spec_in.stages is not None:
        db.query(ProductSpecificationStage).filter(ProductSpecificationStage.specification_id == spec_id).delete()
        for stage_in in spec_in.stages:
            db_stage = ProductSpecificationStage(
                specification_id=db_spec.id,
                stage_id=stage_in.stage_id,
                duration_hours=stage_in.duration_hours,
                brigade_id=stage_in.brigade_id,
                sort_order=stage_in.sort_order
            )
            db.add(db_stage)

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

from app.services.specification_service import SpecificationService
from app.schemas.specification import SpecificationCalculationRequest, CalculatedMaterialResponse
from app.models.register import AccumulationRegister, RegisterType
from sqlalchemy import func

@router.post("/specifications/{spec_id}/calculate", response_model=List[CalculatedMaterialResponse])
async def calculate_specification_materials(
    spec_id: UUID,
    dims: SpecificationCalculationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Calculates the materials list for a specification given the parent product dimensions.
    """
    db_spec = db.query(ProductSpecification).options(
        joinedload(ProductSpecification.items).joinedload(SpecificationItem.component)
    ).filter(ProductSpecification.id == spec_id).first()
    
    if not db_spec:
        raise HTTPException(status_code=404, detail="Specification not found")
    
    results = []
    parent_dims = {
        'width_cm': dims.width_cm,
        'height_cm': dims.height_cm,
        'length_cm': dims.length_cm,
        'weight_kg': dims.weight_kg,
        'custom_attributes': dims.custom_attributes
    }
    
    for item in db_spec.items:
        # 1. Resolve Component (Material)
        component = item.component
        variant = None
        
        if item.line_type == 'detail':
            component = SpecificationService.resolve_detail_component(item, parent_dims, db)
            
            # 2. Calculate Dimensions for the detail
            # Length: size_from_attr * size_multiplier OR fixed_length
            target_length = 0.0
            if item.size_from_attr:
                attr_val = parent_dims['custom_attributes'].get(item.size_from_attr, 0)
                target_length = float(attr_val) * float(item.size_multiplier or 1.0)
            elif item.fixed_length:
                target_length = float(item.fixed_length)
                
            target_width = float(item.fixed_width) if item.fixed_width else None
            
            # 3. Find Matching Variant
            if component:
                variant = SpecificationService.find_matching_variant(component, target_length, target_width, db)
        
        # 4. Calculate Quantity
        quantity = SpecificationService.calculate_item_quantity(item, parent_dims)
        
        # 5. Fetch Stock Status
        stock_quantity = 0.0
        stock_query = db.query(func.sum(AccumulationRegister.quantity)).filter(
            AccumulationRegister.company_id == current_user.company_id,
            AccumulationRegister.register_type == RegisterType.STOCK
        )
        
        if variant:
            stock_quantity = stock_query.filter(AccumulationRegister.variant_id == variant.id).scalar() or 0.0
        elif component:
            # If no variant, check total stock for component
            stock_quantity = stock_query.filter(AccumulationRegister.product_id == component.id).scalar() or 0.0

        results.append(CalculatedMaterialResponse(
            component_id=component.id if component else item.component_id,
            component_name=component.name if component else "Unknown",
            variant_id=variant.id if variant else None,
            variant_name=variant.name if variant else None,
            quantity=quantity,
            unit_of_measure=(component.unit_of_measure if component and component.unit_of_measure else item.unit_of_measure) or "шт",
            stock_quantity=Decimal(str(stock_quantity)),
            notes=item.notes
        ))
        
    return results
    return results

@router.get("/bom-lines/{line_id}/characteristic-mapping", response_model=List[BOMLineCharacteristicMappingResponse])
async def get_bom_line_mapping(
    line_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get characteristic mapping for a specific BOM line."""
    return db.query(BOMLineCharacteristicMapping).filter(
        BOMLineCharacteristicMapping.bom_line_id == line_id
    ).all()

@router.post("/bom-lines/{line_id}/characteristic-mapping", response_model=List[BOMLineCharacteristicMappingResponse])
async def save_bom_line_mapping(
    line_id: UUID,
    mappings: List[BOMLineCharacteristicMappingCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save characteristic mappings for a BOM line (replaces existing)."""
    # Verify line exists
    line = db.query(SpecificationItem).filter(SpecificationItem.id == line_id).first()
    if not line:
        raise HTTPException(status_code=404, detail="BOM line not found")

    # Delete existing
    db.query(BOMLineCharacteristicMapping).filter(BOMLineCharacteristicMapping.bom_line_id == line_id).delete()
    
    # Add new
    db_mappings = []
    for m in mappings:
        db_m = BOMLineCharacteristicMapping(
            bom_line_id=line_id,
            component_characteristic_id=m.component_characteristic_id,
            parent_characteristic_id=m.parent_characteristic_id
        )
        db.add(db_m)
        db_mappings.append(db_m)
        
    db.commit()
    for m in db_mappings:
        db.refresh(m)
    return db_mappings
