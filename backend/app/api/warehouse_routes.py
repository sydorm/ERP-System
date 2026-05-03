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
    from app.models import AccumulationRegister, RegisterType, Product
    from sqlalchemy import func

    results = db.query(
        AccumulationRegister.warehouse_id,
        AccumulationRegister.product_id,
        AccumulationRegister.variant_id,
        Product.name.label("product_name"),
        Product.cost,
        Product.min_stock,
        Product.category,
        func.sum(AccumulationRegister.quantity).label("quantity"),
    ).join(
        Product, Product.id == AccumulationRegister.product_id
    ).filter(
        AccumulationRegister.company_id == current_user.company_id,
        AccumulationRegister.register_type == RegisterType.STOCK,
    ).group_by(
        AccumulationRegister.warehouse_id,
        AccumulationRegister.product_id,
        AccumulationRegister.variant_id,
        Product.name,
        Product.cost,
        Product.min_stock,
        Product.category
    ).all()

    variant_skus: dict = {}
    variant_labels: dict = {}
    v_active: dict = {}
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
            v_active[vid] = v.is_active

    out = []
    for r in results:
        vid = str(r.variant_id) if r.variant_id else None
        label = variant_labels.get(vid, "") if vid else ""
        
        # Enhanced characteristic fields for Task 2
        char_name = ""
        char_value = ""
        if vid:
            from app.models.attribute import Attribute
            vvs = vv_by_variant.get(vid, [])
            if vvs:
                vv = vvs[0] # Take first characteristic for simplicity in stock list
                char_value = vv.text_value or ""
                if vv.option_id:
                     from app.models.attribute import AttributeOption
                     opt = db.query(AttributeOption).filter(AttributeOption.id == vv.option_id).first()
                     if opt: char_value = opt.value
                
                attr = db.query(Attribute).filter(Attribute.id == vv.attribute_id).first()
                if attr: char_name = attr.name

        cost_price = 0.0
        
        # 1. Try finding actual purchase price from latest receipt
        from app.models.purchase_receipt import PurchaseReceipt, PurchaseReceiptLine
        latest_receipt = db.query(PurchaseReceiptLine.price).join(
            PurchaseReceipt, PurchaseReceipt.id == PurchaseReceiptLine.receipt_id
        ).filter(
            PurchaseReceiptLine.product_id == r.product_id,
            PurchaseReceiptLine.variant_id == r.variant_id,
            PurchaseReceipt.status == "posted"
        ).order_by(
            PurchaseReceipt.receipt_date.desc(),
            PurchaseReceiptLine.created_at.desc()
        ).first()

        if latest_receipt:
            cost_price = float(latest_receipt[0])
        else:
            # 2. Try variant price override if it exists
            if vid:
                from app.models.variant import ProductVariant
                variant_obj = db.query(ProductVariant.cost_override).filter(ProductVariant.id == r.variant_id).first()
                if variant_obj and variant_obj[0]:
                    cost_price = float(variant_obj[0])
                    
            # 3. Fallback to standard product cost
            if cost_price == 0.0:
                cost_price = float(r.cost or 0)

        # Task 3: Filter inactive duplicates or zero stock
        if vid and not v_active.get(vid, True):
             if float(r.quantity or 0) <= 0:
                 continue
             # If there's an active variant for same product, this might be the duplicate
             # For now, just skip inactive variants as per Task 3 request
             continue

        out.append({
            "warehouse_id": str(r.warehouse_id) if r.warehouse_id else None,
            "product_id": str(r.product_id) if r.product_id else None,
            "product_name": r.product_name,
            "variant_label": label,
            "characteristic_name": char_name,
            "characteristic_value": char_value,
            "quantity": float(r.quantity or 0),
            "cost": cost_price,
            "min_stock": float(r.min_stock or 0),
            "category": r.category
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

@router.get("/warehouses/movements")
async def get_inventory_movements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get inventory movements/history"""
    from app.models import AccumulationRegister, RegisterType, Product, Warehouse
    
    results = db.query(
        AccumulationRegister.id,
        AccumulationRegister.created_at,
        AccumulationRegister.quantity,
        AccumulationRegister.document_type,
        AccumulationRegister.document_id,
        Product.name.label("product_name"),
        Warehouse.name.label("warehouse_name")
    ).join(
        Product, Product.id == AccumulationRegister.product_id
    ).join(
        Warehouse, Warehouse.id == AccumulationRegister.warehouse_id
    ).filter(
        AccumulationRegister.company_id == current_user.company_id,
        AccumulationRegister.register_type == RegisterType.STOCK
    ).order_by(
        AccumulationRegister.created_at.desc()
    ).limit(100).all()
    
    return [
        {
            "id": str(r.id),
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "quantity": float(r.quantity) if r.quantity is not None else 0.0,
            "document_type": r.document_type,
            "document_id": str(r.document_id) if r.document_id else None,
            "product_name": r.product_name,
            "warehouse_name": r.warehouse_name
        }
        for r in results
    ]

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
