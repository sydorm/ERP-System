from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Warehouse, User
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate, WarehouseResponse
from app.api.dependencies import get_current_active_user

router = APIRouter()

@router.get("/warehouses", response_model=List[WarehouseResponse])
async def get_warehouses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all active warehouses for the company"""
    return db.query(Warehouse).filter(
        Warehouse.company_id == current_user.company_id,
        Warehouse.is_active == True,
        Warehouse.is_deleted == False
    ).all()

@router.get("/warehouses/stock")
async def get_warehouses_stock(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current stock for all warehouses grouped by product and variant"""
    from app.models import AccumulationRegister, RegisterType, Product, ProductVariant
    from sqlalchemy import func

    results = db.query(
        AccumulationRegister.warehouse_id,
        Product.name.label("product_name"),
        ProductVariant.sku.label("variant_sku"),
        ProductVariant.values.label("variant_values"),
        func.sum(AccumulationRegister.quantity).label("quantity"),
    ).join(
        Product, Product.id == AccumulationRegister.product_id
    ).outerjoin(
        ProductVariant, ProductVariant.id == AccumulationRegister.variant_id
    ).filter(
        AccumulationRegister.company_id == current_user.company_id,
        AccumulationRegister.register_type == RegisterType.STOCK,
    ).group_by(
        AccumulationRegister.warehouse_id,
        Product.name,
        ProductVariant.sku,
        ProductVariant.values
    ).all()

    out = []
    for r in results:
        label = ""
        if r.variant_values:
            vals = []
            for v in r.variant_values:
                if isinstance(v, dict) and "value" in v:
                    vals.append(str(v["value"]))
            label = " x ".join(vals)
        elif r.variant_sku:
            label = r.variant_sku

        out.append({
            "warehouse_id": str(r.warehouse_id) if r.warehouse_id else None,
            "product_name": r.product_name,
            "variant_label": label,
            "quantity": float(r.quantity or 0)
        })
    return out

@router.post("/warehouses", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED)
async def create_warehouse(
    warehouse_in: WarehouseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new warehouse"""
    warehouse = Warehouse(
        **warehouse_in.dict(),
        company_id=current_user.company_id
    )
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return warehouse

@router.get("/warehouses/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse(
    warehouse_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific warehouse"""
    warehouse = db.query(Warehouse).filter(
        Warehouse.id == warehouse_id,
        Warehouse.company_id == current_user.company_id
    ).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse

@router.put("/warehouses/{warehouse_id}", response_model=WarehouseResponse)
async def update_warehouse(
    warehouse_id: str,
    warehouse_in: WarehouseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a warehouse"""
    warehouse = db.query(Warehouse).filter(
        Warehouse.id == warehouse_id,
        Warehouse.company_id == current_user.company_id
    ).first()
    
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
        
    for key, value in warehouse_in.dict(exclude_unset=True).items():
        setattr(warehouse, key, value)
        
    db.commit()
    db.refresh(warehouse)
    return warehouse

@router.delete("/warehouses/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_warehouse(
    warehouse_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete (soft) a warehouse"""
    warehouse = db.query(Warehouse).filter(
        Warehouse.id == warehouse_id,
        Warehouse.company_id == current_user.company_id
    ).first()
    
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
        
    # Check references
    from app.models import Order, PurchaseOrder, AccumulationRegister
    is_used = db.query(Order).filter(Order.warehouse_id == warehouse.id).first() or \
              db.query(PurchaseOrder).filter(PurchaseOrder.warehouse_id == warehouse.id).first() or \
              db.query(AccumulationRegister).filter(AccumulationRegister.warehouse_id == warehouse.id).first()
              
    if is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неможливо видалити склад, оскільки на ньому є залишки або він використовується в документах."
        )
        
    warehouse.is_deleted = True
    db.commit()
    return None
