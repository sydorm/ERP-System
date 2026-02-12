from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.session import get_db
from app.models import Product, User
from app.models.variant import ProductVariant, VariantValue
from app.schemas import ProductCreate, ProductUpdate, ProductResponse
from app.api.dependencies import get_current_active_user

router = APIRouter()

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
    query = db.query(Product).filter(Product.company_id == current_user.company_id)
    
    if search:
        search_filter = or_(
            Product.name.ilike(f"%{search}%"),
            Product.sku.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
        
    if category:
        query = query.filter(Product.category == category)
        
    return query.offset(skip).limit(limit).all()


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
            var_data = var_in.dict(exclude={"values"})
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
            var_data = var_in.dict(exclude={"values"})
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
        
    db.delete(product)
    db.commit()
    return None
