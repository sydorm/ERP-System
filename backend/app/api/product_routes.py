from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.session import get_db
from app.models import Product, User, ProductSpecification, SpecificationItem, RegisterType
from app.models.variant import ProductVariant, VariantValue
from app.schemas import ProductCreate, ProductUpdate, ProductResponse
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
    Get stock levels for a product across all warehouses.
    """
    from app.models import AccumulationRegister, Warehouse
    from sqlalchemy import func
    
    results = db.query(
        Warehouse.name.label("warehouse"),
        func.sum(AccumulationRegister.quantity).label("quantity")
    ).join(
        Warehouse, Warehouse.id == AccumulationRegister.warehouse_id
    ).filter(
        AccumulationRegister.company_id == current_user.company_id,
        AccumulationRegister.product_id == product_id,
        AccumulationRegister.register_type == RegisterType.STOCK
    ).group_by(Warehouse.name).all()
    
    return [
        {
            "warehouse": r.warehouse, 
            "quantity": float(r.quantity), 
            "reserved": 0, 
            "available": float(r.quantity), 
            "minLevel": 5
        } for r in results
    ]

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
            Product.sku.ilike(f"%{search}%")
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
    # Check if SKU exists in this company
    existing_product = db.query(Product).filter(
        Product.company_id == current_user.company_id,
        Product.sku == product_in.sku
    ).first()
    
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with SKU '{product_in.sku}' already exists"
        )
        
    product_data = product_in.dict(exclude={"variants"})
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
                
    db.commit()
    db.refresh(product)
    return product


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
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
        
    # If updating SKU, check uniqueness
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

    update_data = product_in.dict(exclude_unset=True, exclude={"variants"})
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
    Get a single product with variants and specifications.
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
    return product

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
        'width_cm': float(product.width_cm or 0),
        'height_cm': float(product.height_cm or 0),
        'length_cm': float(product.length_cm or 0),
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



@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
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
