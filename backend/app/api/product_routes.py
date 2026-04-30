from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.session import get_db
from app.models import Product, User, ProductSpecification, SpecificationItem, RegisterType
from app.models.variant import ProductVariant, VariantValue
from app.models.attribute import Attribute, CategoryAttribute
from app.schemas import ProductCreate, ProductUpdate, ProductResponse, ProductAttributeLight
from app.api.dependencies import get_current_active_user
from app.services.posting_service import PostingService

router = APIRouter()

@router.get("/products/statistics")
async def get_products_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get summary statistics for products (Total, In Stock, Low Stock, Out of Stock).
    """
    return PostingService.get_overall_statistics(db, current_user.company_id)

@router.get("/products/{product_id}/stock")
async def get_product_stock(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get stock levels for a product across all warehouses, broken down by variant.
    """
    from app.models import AccumulationRegister, Warehouse
    from sqlalchemy import func

    results = db.query(
        Warehouse.name.label("warehouse"),
        AccumulationRegister.variant_id,
        func.sum(AccumulationRegister.quantity).label("quantity"),
    ).join(
        Warehouse, Warehouse.id == AccumulationRegister.warehouse_id
    ).filter(
        AccumulationRegister.company_id == current_user.company_id,
        AccumulationRegister.product_id == product_id,
        AccumulationRegister.register_type == RegisterType.STOCK,
    ).group_by(
        Warehouse.name,
        AccumulationRegister.variant_id,
    ).all()

    variant_skus: dict = {}
    variant_labels: dict = {}
    variant_ids = [r.variant_id for r in results if r.variant_id]
    if variant_ids:
        from app.models.variant import ProductVariant, VariantValue
        variants = db.query(ProductVariant).filter(ProductVariant.id.in_(variant_ids)).all()
        all_vv = db.query(VariantValue).filter(VariantValue.variant_id.in_(variant_ids)).all()
        vv_by_variant: dict = {}
        for vv in all_vv:
            vv_by_variant.setdefault(str(vv.variant_id), []).append(vv)
        for v in variants:
            vid = str(v.id)
            variant_skus[vid] = v.sku
            text_parts = []
            for vv in vv_by_variant.get(vid, []):
                if vv.text_value:
                    text_parts.append(vv.text_value)
                elif vv.option_id:
                    from app.models.attribute import AttributeOption
                    opt = db.query(AttributeOption).filter(AttributeOption.id == vv.option_id).first()
                    if opt:
                        text_parts.append(opt.value)
            variant_labels[vid] = ", ".join(text_parts) if text_parts else v.sku
    return [
        {
            "warehouse": r.warehouse,
            "variant_id": str(r.variant_id) if r.variant_id else None,
            "variant_sku": variant_skus.get(str(r.variant_id)) if r.variant_id else None,
            "variant_label": variant_labels.get(str(r.variant_id)) if r.variant_id else None,
            "quantity": float(r.quantity),
            "reserved": 0,
            "available": float(r.quantity),
            "minLevel": 5,
        }
        for r in results
    ]

@router.post("/products/{product_id}/variants/find-or-create")
async def find_or_create_variant(
    product_id: UUID,
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Find an existing variant matching the given attribute values,
    or create a new one if no match is found.
    Used for materials that skip the variant creation dialog.
    
    Body: { "values": [ { "attribute_id": "...", "option_id": "...", "text_value": "..." }, ... ] }
    """
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.company_id == current_user.company_id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    values = body.get("values") or body.get("attribute_values") or []
    if not values:
        raise HTTPException(status_code=400, detail="No attribute values provided")
    
    # Build a fingerprint from incoming values for comparison
    def make_fingerprint(vals):
        """Create a sorted tuple of (attr_id, option_id_or_text) for matching."""
        parts = []
        for v in vals:
            attr_id = str(v.get("attribute_id", ""))
            key = str(v.get("option_id") or v.get("text_value") or "")
            parts.append((attr_id, key))
        return tuple(sorted(parts))
    
    incoming_fp = make_fingerprint(values)
    
    # Search existing variants
    existing_variants = db.query(ProductVariant).filter(
        ProductVariant.product_id == product_id,
        ProductVariant.is_active == True
    ).all()
    
    for variant in existing_variants:
        variant_vals = []
        for vv in variant.values:
            variant_vals.append({
                "attribute_id": str(vv.attribute_id),
                "option_id": str(vv.option_id) if vv.option_id else None,
                "text_value": vv.text_value
            })
        if make_fingerprint(variant_vals) == incoming_fp:
            # Found matching variant
            return {
                "id": str(variant.id),
                "sku": variant.sku,
                "product_id": str(variant.product_id),
                "created": False
            }
    
    # No match — create new variant
    # Generate SKU suffix from values
    suffix_parts = []
    for v in values:
        txt = v.get("text_value") or ""
        if txt:
            suffix_parts.append(txt.replace("×", "x").replace(" ", ""))
    
    suffix = "-".join(suffix_parts) if suffix_parts else str(len(existing_variants) + 1)
    new_sku = f"{product.sku}-{suffix}"
    
    db_variant = ProductVariant(
        product_id=product_id,
        sku=new_sku,
        is_active=True,
        is_primary=False
    )
    db.add(db_variant)
    db.flush()
    
    for v in values:
        db_val = VariantValue(
            variant_id=db_variant.id,
            attribute_id=v["attribute_id"],
            option_id=v.get("option_id"),
            text_value=v.get("text_value")
        )
        db.add(db_val)
    
    db.commit()
    db.refresh(db_variant)
    
    return {
        "id": str(db_variant.id),
        "sku": db_variant.sku,
        "product_id": str(db_variant.product_id),
        "created": True
    }

@router.get("/products", response_model=List[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List products for the current user's company.
    Supports filtering by search term (name/sku) and category.
    """
    query = db.query(Product).filter(
        Product.company_id == current_user.company_id,
        Product.is_deleted == False
    )
    
    if search:
        search_filter = or_(
            Product.name.ilike(f"%{search}%"),
            Product.sku.ilike(f"%{search}%"),
            Product.variants.any(ProductVariant.sku.ilike(f"%{search}%"))
        )
        query = query.filter(search_filter)
        
    if category:
        query = query.filter(Product.category == category)
        
    products = query.offset(skip).limit(limit).all()
    
    # Enrich with stock balance
    if products:
        product_ids = [p.id for p in products]
        balances = PostingService.get_stock_balances(db, current_user.company_id, product_ids)
        for p in products:
            p.stock_balance = balances.get(str(p.id), 0.0)
            
    return products


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new product.
    Checks for SKU uniqueness within the company.
    """
    # Check if SKU exists in this company (only if SKU is provided)
    if product_in.sku:
        existing_product = db.query(Product).filter(
            Product.company_id == current_user.company_id,
            Product.sku == product_in.sku
        ).first()
        
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with SKU '{product_in.sku}' already exists"
            )
        
    product_data = product_in.dict(exclude={"variants", "price_rule", "product_attributes"})
    product = Product(
        **product_data,
        company_id=current_user.company_id
    )
    
    db.add(product)
    db.flush() # Get product ID
    
    if product_in.variants:
        for var_in in product_in.variants:
            var_data = var_in.dict(exclude={"values", "product_id"})
            db_variant = ProductVariant(**var_data, product_id=product.id)
            db.add(db_variant)
            db.flush()
            
            for val_in in var_in.values:
                db_val = VariantValue(**val_in.dict(), variant_id=db_variant.id)
                db.add(db_val)

    if product_in.price_rule is not None:
        from app.models.variant import ProductPriceRule, ProductPriceMarkup
        # Remove old rule and markups
        db.query(ProductPriceRule).filter(ProductPriceRule.product_id == product.id).delete()
        
        rule_data = product_in.price_rule.dict(exclude={"markups"})
        db_rule = ProductPriceRule(**rule_data, product_id=product.id)
        db.add(db_rule)
        db.flush()
        
        for markup_in in product_in.price_rule.markups:
            db_markup = ProductPriceMarkup(**markup_in.dict(), rule_id=db_rule.id)
            db.add(db_markup)

    if product_in.product_attributes:
        from app.models.product import ProductAttribute
        for attr_in in product_in.product_attributes:
            db_attr = ProductAttribute(**attr_in.dict(), product_id=product.id)
            db.add(db_attr)
                
    db.commit()
    db.refresh(product)
    return product


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a single product by ID.
    """
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.company_id == current_user.company_id,
        Product.is_deleted == False
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
        
    # Enrich with stock balance
    balances = PostingService.get_stock_balances(db, current_user.company_id, [product_id])
    product.stock_balance = balances.get(str(product_id), 0.0)
    
    return product


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing product.
    """
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.company_id == current_user.company_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
        
    # If updating SKU, check uniqueness (only if SKU is provided)
    if product_in.sku and product_in.sku != product.sku:
        existing_sku = db.query(Product).filter(
            Product.company_id == current_user.company_id,
            Product.sku == product_in.sku
        ).first()
        if existing_sku:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with SKU '{product_in.sku}' already exists"
            )

    update_data = product_in.dict(exclude_unset=True, exclude={"variants", "price_rule", "product_attributes"})
    for field, value in update_data.items():
        setattr(product, field, value)
        
    if product_in.variants is not None:
        # Simple sync: remove old variants and add new ones
        # In production, we'd match by ID to preserve history
        db.query(ProductVariant).filter(ProductVariant.product_id == product.id).delete()
        
        for var_in in product_in.variants:
            var_data = var_in.dict(exclude={"values", "product_id"})
            db_variant = ProductVariant(**var_data, product_id=product.id)
            db.add(db_variant)
            db.flush()
            
            for val_in in var_in.values:
                val_data = val_in.dict()
                db_val = VariantValue(**val_data, variant_id=db_variant.id)
                db.add(db_val)

    if product_in.price_rule is not None:
        from app.models.variant import ProductPriceRule, ProductPriceMarkup
        # Remove old rule and markups
        db.query(ProductPriceRule).filter(ProductPriceRule.product_id == product.id).delete()
        
        rule_data = product_in.price_rule.dict(exclude={"markups"})
        db_rule = ProductPriceRule(**rule_data, product_id=product.id)
        db.add(db_rule)
        db.flush()
        
        for markup_in in product_in.price_rule.markups:
            db_markup = ProductPriceMarkup(**markup_in.dict(), rule_id=db_rule.id)
            db.add(db_markup)

    if product_in.product_attributes is not None:
        from app.models.product import ProductAttribute
        db.query(ProductAttribute).filter(ProductAttribute.product_id == product.id).delete()
        for attr_in in product_in.product_attributes:
            db_attr = ProductAttribute(**attr_in.dict(), product_id=product.id)
            db.add(db_attr)

    db.commit()
    db.refresh(product)
    return product

@router.get("/products/{product_id}/attributes", response_model=List[ProductAttributeLight])
async def get_product_attributes(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a light list of attributes relevant to this product.
    Includes attributes linked via category and global attributes.
    """
    product = db.query(Product).filter(Product.id == product_id, Product.company_id == current_user.company_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # 1. Attributes linked specifically via category
    category_attrs = db.query(Attribute).join(CategoryAttribute).filter(
        CategoryAttribute.category_code == product.category,
        Attribute.company_id == current_user.company_id,
        Attribute.is_archived == False
    ).all()
    
    # 2. Global attributes (those with NO category links)
    global_attrs = db.query(Attribute).filter(
        Attribute.company_id == current_user.company_id,
        Attribute.is_archived == False,
        ~Attribute.categories.any()
    ).all()
    
    # Merge and format
    # Using a dict to avoid duplicates if any
    all_attrs_map = {a.id: a for a in (category_attrs + global_attrs)}
    
    results = []
    for attr in all_attrs_map.values():
        results.append({
            "id": attr.id,
            "name": attr.name,
            "type": attr.type.value if hasattr(attr.type, 'value') else str(attr.type),
            "options": [{"id": o.id, "value": o.value} for o in attr.options]
        })
        
    return results

@router.get("/products/{product_id}/calculate-cost")
async def calculate_product_cost(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Calculate the estimated cost of a product based on its default BOM specification.
    Includes material costs (qty * component.cost) and production stage costs (duration * avg_hourly_rate).
    """
    from app.models.specification import ProductSpecification
    from app.services.specification_service import SpecificationService
    from app.models.hr import EmployeeRole
    from sqlalchemy import func

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.company_id == current_user.company_id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Товар не знайдено")

    # Find default specification, or fallback to first active
    spec = db.query(ProductSpecification).filter(
        ProductSpecification.product_id == product_id,
        ProductSpecification.is_active == True
    ).order_by(ProductSpecification.is_default.desc(), ProductSpecification.created_at.desc()).first()

    if not spec:
        return {"cost": 0.0, "materials_cost": 0.0, "stages_cost": 0.0, "detail": "Не знайдено активної специфікації"}

    parent_dims = {
        'width_mm': float(product.width_mm or 0),
        'height_mm': float(product.height_mm or 0),
        'length_mm': float(product.length_mm or 0),
        'weight_kg': float(product.weight_kg or 0),
        'custom_attributes': {} # We don't have variants values readily available here for simple cost check, but could be added
    }

    materials_cost = 0.0
    for item in spec.items:
        if not item.component:
            continue
        qty = SpecificationService.calculate_item_quantity(item, parent_dims)
        comp_cost = float(item.component.cost or item.component.price or 0.0)
        materials_cost += qty * comp_cost

    stages_cost = 0.0
    for stage in spec.stages:
        duration = float(stage.duration_hours or 0.0)
        if duration > 0:
            # Get average rate for this stage from EmployeeRole
            avg_rate = db.query(func.avg(EmployeeRole.rate)).filter(
                EmployeeRole.role_id == stage.stage_id,
                EmployeeRole.is_active == True
            ).scalar()
            
            rate = float(avg_rate or 0.0)
            stages_cost += duration * rate

    total_cost = round(materials_cost + stages_cost, 2)
    
    return {
        "cost": total_cost,
        "materials_cost": round(materials_cost, 2),
        "stages_cost": round(stages_cost, 2),
        "spec_name": spec.name
    }

@router.get("/products/{product_id}/production-stats")
async def get_product_production_stats(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get production statistics and active tasks for a product.
    """
    from app.models.production import ProductionOrder, ProductionOrderLine
    from sqlalchemy import func

    # Check product exists
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.company_id == current_user.company_id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Calculate total produced
    total_produced_result = db.query(func.sum(ProductionOrderLine.produced_quantity)).join(
        ProductionOrder, ProductionOrderLine.production_order_id == ProductionOrder.id
    ).filter(
        ProductionOrder.company_id == current_user.company_id,
        ProductionOrderLine.product_id == product_id,
        ProductionOrder.status == 'completed'
    ).scalar()
    
    total_produced = float(total_produced_result or 0)

    # Fetch active tasks
    active_lines = db.query(ProductionOrderLine, ProductionOrder).join(
        ProductionOrder, ProductionOrderLine.production_order_id == ProductionOrder.id
    ).filter(
        ProductionOrder.company_id == current_user.company_id,
        ProductionOrderLine.product_id == product_id,
        ProductionOrder.status.in_(['draft', 'released', 'in_progress'])
    ).order_by(ProductionOrder.order_date.desc()).all()

    active_tasks = []
    for line, order in active_lines:
        active_tasks.append({
            "id": str(order.id),
            "order_number": order.order_number,
            "status": order.status,
            "quantity": float(line.quantity),
            "produced_quantity": float(line.produced_quantity),
            "due_date": order.due_date.isoformat() if order.due_date else None,
            "priority": order.priority
        })

    # For now, mock actual/planned times based on product params or generic averages
    # In a full implementation, we'd query timesheet/attendance data linked to production orders
    planned = float(product.production_time_hours or 0)
    # mock actual as slightly worse than planned if there is history, else same
    actual = planned * 1.05 if total_produced > 0 and planned > 0 else planned
    
    deviation_hours = actual - planned
    deviation_percent = ((actual - planned) / planned * 100) if planned > 0 else 0

    return {
        "total_produced": total_produced,
        "avg_time_planned": round(planned, 1),
        "avg_time_actual": round(actual, 1),
        "deviation_hours": round(deviation_hours, 1),
        "deviation_percent": round(deviation_percent, 1),
        "active_tasks": active_tasks
    }



@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a product.
    """
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.company_id == current_user.company_id
    ).first()
    
    if not product:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
        
    # Check if used in orders, invoices, or stock
    from app.models import OrderLine, PurchaseOrderLine, AccumulationRegister
    
    is_used = db.query(OrderLine).filter(OrderLine.product_id == product.id).first() or \
              db.query(PurchaseOrderLine).filter(PurchaseOrderLine.product_id == product.id).first() or \
              db.query(AccumulationRegister).filter(AccumulationRegister.product_id == product.id).first()
              
    if is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неможливо видалити товар, оскільки він вже використовується в документах бази."
        )
        
    product.is_deleted = True
    db.commit()
    return None


@router.get("/products/{product_id}/cost-history")
async def get_product_cost_history(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Return the cost price change history for a product."""
    from app.models.product_cost_history import ProductCostHistory
    from app.models.counterparty import Counterparty

    rows = (
        db.query(ProductCostHistory)
        .filter(
            ProductCostHistory.product_id == product_id,
            ProductCostHistory.company_id == current_user.company_id,
        )
        .order_by(ProductCostHistory.created_at.desc())
        .limit(100)
        .all()
    )

    result = []
    for h in rows:
        supplier_name = None
        if h.supplier_id:
            sup = db.query(Counterparty).filter(Counterparty.id == h.supplier_id).first()
            if sup:
                supplier_name = sup.name
        result.append({
            "id": str(h.id),
            "created_at": h.created_at.isoformat() if h.created_at else None,
            "document_type": h.document_type,
            "document_id": str(h.document_id),
            "document_number": h.document_number,
            "supplier_id": str(h.supplier_id) if h.supplier_id else None,
            "supplier_name": supplier_name,
            "old_stock": float(h.old_stock) if h.old_stock is not None else 0,
            "old_cost": float(h.old_cost) if h.old_cost is not None else None,
            "incoming_qty": float(h.incoming_qty),
            "incoming_price": float(h.incoming_price),
            "new_cost": float(h.new_cost),
            "method": h.method,
        })
    return result
