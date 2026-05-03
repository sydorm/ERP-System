from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.purchase_order import PurchaseOrder, PurchaseOrderLine, PurchaseOrderStatus, PurchaseTemplate, PurchaseTemplateLine
from app.models.user import User
from app.schemas.purchase_order import (
    PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderResponse,
    PurchaseTemplateCreate, PurchaseTemplateResponse
)
from app.api.dependencies import get_current_active_user
from app.services.sequence_service import SequenceService
from app.models import Product, AccumulationRegister, RegisterType, Counterparty
from app.models.production import ProductionOrder, ProductionOrderMaterial
from sqlalchemy import func

router = APIRouter()

@router.get("/purchase-orders/last")
async def get_last_orders(limit: int = 5, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Stub for getting last purchase orders. Returns empty list as requested.
    """
    return []

@router.get("/purchase-orders/procurement-alerts")
async def get_procurement_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Find products where (current stock - reservations) < min_stock
    """
    # 1. Get all products with track_inventory=True and min_stock > 0
    products = db.query(Product).filter(
        Product.company_id == current_user.company_id,
        Product.is_deleted == False
    ).all()
    
    if not products:
        return {"critical": [], "soon": [], "drafts": []}
        
    product_ids = [p.id for p in products]
    
    # 2. Get current stock levels from AccumulationRegister
    stock_levels = db.query(
        AccumulationRegister.product_id,
        func.sum(AccumulationRegister.quantity).label("total_qty")
    ).filter(
        AccumulationRegister.company_id == current_user.company_id,
        AccumulationRegister.product_id.in_(product_ids),
        AccumulationRegister.register_type == RegisterType.STOCK
    ).group_by(AccumulationRegister.product_id).all()
    
    stock_map = {str(s.product_id): float(s.total_qty) for s in stock_levels}
    
    # 3. Get Reservations from active Production Orders
    # Reservations = Sum(required_quantity - issued_quantity) for active orders
    reservations = db.query(
        ProductionOrderMaterial.component_id,
        func.sum(ProductionOrderMaterial.required_quantity - ProductionOrderMaterial.issued_quantity).label("reserved_qty")
    ).join(ProductionOrder).filter(
        ProductionOrder.company_id == current_user.company_id,
        ProductionOrder.status.in_(["draft", "released", "in_progress"]),
        ProductionOrderMaterial.component_id.in_(product_ids)
    ).group_by(ProductionOrderMaterial.component_id).all()
    
    res_map = {str(r.component_id): float(r.reserved_qty) for r in reservations}
    
    # 4. Filter products needing order
    critical = []
    soon = []
    
    for p in products:
        current_qty = stock_map.get(str(p.id), 0.0)
        reserved_qty = res_map.get(str(p.id), 0.0)
        real_balance = current_qty - reserved_qty
        
        min_stock = float(p.min_stock) if p.min_stock else 0.0
        optimal_stock = float(p.optimal_stock) if p.optimal_stock else 0.0
        
        if min_stock == 0 and optimal_stock == 0:
            continue

        if real_balance < min_stock:
            # CRITICAL
            to_order = optimal_stock - real_balance
            if to_order <= 0:
                to_order = min_stock - real_balance
            if to_order < 0: to_order = 0
            
            critical.append({
                "product_id": p.id,
                "sku": p.sku,
                "name": p.name,
                "unit": p.unit_of_measure,
                "current_stock": current_qty,
                "reserved": reserved_qty,
                "real_balance": real_balance,
                "min_stock": min_stock,
                "optimal_stock": optimal_stock,
                "to_order": to_order,
                "default_supplier_id": p.default_supplier_id,
                "delivery_days": p.delivery_days
            })
        elif real_balance < (min_stock * 1.5): # Threshold for "Soon"
            # SOON
            soon.append({
                "product_id": p.id,
                "sku": p.sku,
                "name": p.name,
                "unit": p.unit_of_measure,
                "current_stock": current_qty,
                "reserved": reserved_qty,
                "real_balance": real_balance,
                "min_stock": min_stock,
                "optimal_stock": optimal_stock,
                "to_order": optimal_stock - real_balance if optimal_stock > real_balance else 0,
                "default_supplier_id": p.default_supplier_id,
                "delivery_days": p.delivery_days
            })
            
    # 5. Get Drafts
    drafts_list = db.query(PurchaseOrder).filter(
        PurchaseOrder.company_id == current_user.company_id,
        PurchaseOrder.status == "draft"
    ).all()
    
    drafts = []
    for d in drafts_list:
        drafts.append({
            "id": d.id,
            "order_number": d.order_number,
            "supplier_id": d.supplier_id,
            "total_amount": float(d.total_amount),
            "line_count": len(d.lines)
        })

    return {
        "critical": critical,
        "soon": soon,
        "drafts": drafts
    }

@router.get("/purchase-orders", response_model=List[PurchaseOrderResponse])
async def list_purchase_orders(
    supplier_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(PurchaseOrder).filter(PurchaseOrder.company_id == current_user.company_id)
    if supplier_id:
        query = query.filter(PurchaseOrder.supplier_id == supplier_id)
    return query.all()

@router.post("/purchase-orders", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    order_data: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 0. Generate Number if empty or "Авто"
    order_num = order_data.order_number
    if not order_num or order_num.lower() in ["авто", "автоматично", "auto"]:
        order_num = SequenceService.get_next_number(db, "purchase_order", "PO-")

    # 1. Create Order
    order = PurchaseOrder(
        order_number=order_num,
        order_date=order_data.order_date,
        expected_date=order_data.expected_date,
        supplier_id=order_data.supplier_id,
        warehouse_id=order_data.warehouse_id,
        currency=order_data.currency,
        total_amount=order_data.total_amount,
        company_id=current_user.company_id,
        created_by=current_user.id,
        notes=order_data.notes,
        status=PurchaseOrderStatus(order_data.status) if order_data.status else PurchaseOrderStatus.DRAFT
    )
    db.add(order)
    db.flush()
    
    # 2. Add Lines
    for line_data in order_data.lines:
        line = PurchaseOrderLine(
            order_id=order.id,
            product_id=line_data.product_id,
            variant_id=line_data.variant_id,
            quantity=line_data.quantity,
            price=line_data.price,
            total=line_data.total,
            attribute_values=line_data.attribute_values
        )
        db.add(line)
    
    db.commit()
    db.refresh(order)
    return order

@router.get("/purchase-orders/{id}", response_model=PurchaseOrderResponse)
async def get_purchase_order(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    order = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == id,
        PurchaseOrder.company_id == current_user.company_id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
    return order

@router.put("/purchase-orders/{id}", response_model=PurchaseOrderResponse)
async def update_purchase_order(
    id: UUID,
    order_data: PurchaseOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    order = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == id,
        PurchaseOrder.company_id == current_user.company_id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
        
    update_data = order_data.dict(exclude_unset=True, exclude={"lines"})
    for key, value in update_data.items():
        if key == "status":
            setattr(order, key, PurchaseOrderStatus(value))
        else:
            setattr(order, key, value)
            
    if order_data.lines is not None:
        db.query(PurchaseOrderLine).filter(PurchaseOrderLine.order_id == id).delete()
        for line_data in order_data.lines:
            line = PurchaseOrderLine(
                order_id=order.id,
                product_id=line_data.product_id,
                variant_id=line_data.variant_id,
                quantity=line_data.quantity,
                price=line_data.price,
                total=line_data.total,
                attribute_values=line_data.attribute_values
            )
            db.add(line)
            
    db.commit()
    db.refresh(order)
    return order

@router.delete("/purchase-orders/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_purchase_order(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    order = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == id,
        PurchaseOrder.company_id == current_user.company_id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
    
    db.delete(order)
    db.commit()
    return None

@router.get("/purchase-orders/last")
async def get_last_orders():
    return {"data": [], "status": "ok"}

@router.get("/purchase-orders/last-price")  
async def get_last_price():
    return {"data": None, "status": "ok"}

@router.get("/purchase-templates", response_model=List[PurchaseTemplateResponse])
async def list_purchase_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(PurchaseTemplate).filter(PurchaseTemplate.company_id == current_user.company_id).all()

@router.post("/purchase-templates", response_model=PurchaseTemplateResponse)
async def create_purchase_template(
    template_data: PurchaseTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    template = PurchaseTemplate(
        name=template_data.name,
        supplier_id=template_data.supplier_id,
        warehouse_id=template_data.warehouse_id,
        notes=template_data.notes,
        company_id=current_user.company_id,
        created_by=current_user.id
    )
    db.add(template)
    db.flush()
    
    for line_data in template_data.lines:
        line = PurchaseTemplateLine(
            template_id=template.id,
            product_id=line_data.product_id,
            variant_id=line_data.variant_id,
            quantity=line_data.quantity,
            attribute_values=line_data.attribute_values
        )
        db.add(line)
    
    db.commit()
    db.refresh(template)
    return template
