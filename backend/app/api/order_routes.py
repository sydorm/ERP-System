from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi.responses import StreamingResponse
import csv
from io import StringIO
from datetime import datetime

from app.db.session import get_db
from app.api.dependencies import get_current_active_user
from app.models import Order, OrderLine, User, RegisterType, Product, ProductVariant, VariantValue
from app.models.specification import ProductSpecification
from app.models.register import AccumulationRegister
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderResponse,
    MaterialCheckItem, MaterialCheckResponse
)
from app.services.sequence_service import SequenceService
from app.services.audit_service import AuditService
import uuid

router = APIRouter()


def populate_product_summary(orders: List[Order], db: Session) -> None:
    """Populate product_summary for a list of orders based on their lines."""
    for order in orders:
        product_names = []
        for line in order.lines:
            product = db.query(Product).filter(Product.id == line.product_id).first()
            if product:
                product_names.append(product.name)
        
        if not product_names:
            order.product_summary = "—"
        elif len(product_names) == 1:
            order.product_summary = product_names[0]
        else:
            order.product_summary = f"{product_names[0]} (+{len(product_names)-1})"


@router.get("/orders", response_model=List[OrderResponse])
async def list_orders(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[str] = None,
    crm_stage: Optional[str] = None,
    payment_status: Optional[str] = None,
    priority: Optional[str] = None,
    manager_id: Optional[UUID] = None,
    counterparty_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Order).filter(Order.company_id == current_user.company_id)

    if search:
        query = query.filter(Order.order_number.ilike(f"%{search}%"))
    if status:
        query = query.filter(Order.status == status)
    if crm_stage:
        query = query.filter(Order.crm_stage == crm_stage)
    if payment_status:
        query = query.filter(Order.payment_status == payment_status)
    if priority:
        query = query.filter(Order.priority == priority)
    if manager_id:
        query = query.filter(Order.manager_id == manager_id)
    if counterparty_id:
        query = query.filter(Order.counterparty_id == counterparty_id)

    orders = query.order_by(Order.order_date.desc()).offset(skip).limit(limit).all()
    populate_product_summary(orders, db)
    return orders


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    order_num = order_in.order_number
    if not order_num or order_num.lower() in ["авто", "автоматично", "auto"]:
        order_num = SequenceService.get_next_number(db, "order", "ORD-")

    order = Order(
        order_number=order_num,
        order_date=order_in.order_date,
        counterparty_id=order_in.counterparty_id,
        warehouse_id=order_in.warehouse_id,
        total_amount=order_in.total_amount,
        company_id=current_user.company_id,
        created_by=current_user.id,
        status="draft",
        # CRM fields
        crm_stage=order_in.crm_stage,
        channel=order_in.channel,
        city=order_in.city,
        delivery_type=order_in.delivery_type,
        attributes_values=order_in.attributes_values,
        paid_amount=order_in.paid_amount,
        payment_status=order_in.payment_status,
        prepayment_percent=order_in.prepayment_percent,
        prepayment_amount=order_in.prepayment_amount,
        deadline_date=order_in.deadline_date,
        next_contact_date=order_in.next_contact_date,
        next_contact_at=order_in.next_contact_at,
        priority=order_in.priority,
        manager_id=order_in.manager_id,
        internal_notes=order_in.internal_notes,
        reference_photo=order_in.reference_photo,
        comment=order_in.comment,
        contract=order_in.contract,
        discount_percent=order_in.discount_percent,
    )
    db.add(order)
    db.flush()

    for line_in in order_in.lines:
        if line_in.variant_id is None and line_in.variant_values:
            product = db.query(Product).filter(Product.id == line_in.product_id).first()
            sku_suffix = f"-CUST-{uuid.uuid4().hex[:4].upper()}"
            new_variant = ProductVariant(
                product_id=line_in.product_id,
                sku=f"{product.sku}{sku_suffix}",
                price_override=line_in.price,
                is_active=False
            )
            db.add(new_variant)
            db.flush()
            for val in line_in.variant_values:
                db_val = VariantValue(**val.dict(), variant_id=new_variant.id)
                db.add(db_val)
            db.flush()
            line_in.variant_id = new_variant.id

        line = OrderLine(
            order_id=order.id,
            product_id=line_in.product_id,
            variant_id=line_in.variant_id,
            specification_id=line_in.specification_id,
            quantity=line_in.quantity,
            price=line_in.price,
            total=line_in.total,
            attribute_values=line_in.attribute_values,
            characteristic_width=line_in.characteristic_width,
            characteristic_height=line_in.characteristic_height
        )
        db.add(line)

    db.commit()
    db.refresh(order)

    AuditService.compare_and_log(
        db=db, entity_type="order", entity_id=order.id, user_id=current_user.id,
        action="CREATE", new_obj=AuditService.get_dict(order, relationships=["lines"])
    )

    return order


@router.get("/orders/{id}", response_model=OrderResponse)
async def get_order(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    order = db.query(Order).filter(
        Order.id == id,
        Order.company_id == current_user.company_id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    populate_product_summary([order], db)
    return order


@router.put("/orders/{id}", response_model=OrderResponse)
async def update_order(
    id: UUID,
    order_in: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    order = db.query(Order).filter(
        Order.id == id,
        Order.company_id == current_user.company_id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    old_obj = AuditService.get_dict(order, relationships=["lines"])
    update_data = order_in.dict(exclude_unset=True)

    # Handle payment transaction if paid_amount increases and bank_account_id is provided
    new_paid_amount = update_data.get("paid_amount")
    bank_account_id = update_data.get("bank_account_id")
    
    if new_paid_amount is not None and bank_account_id:
        delta = Decimal(str(new_paid_amount)) - (order.paid_amount or Decimal("0"))
        if delta > 0:
            from app.models.finance import FinancialTransaction, TransactionType
            transaction = FinancialTransaction(
                company_id=current_user.company_id,
                bank_account_id=bank_account_id,
                order_id=order.id,
                transaction_type=TransactionType.IN,
                amount=delta,
                description=f"Оплата замовлення {order.order_number}",
                category="SALES"
            )
            db.add(transaction)

    # Apply updates
    for field, value in update_data.items():
        if field not in ["bank_account_id", "lines"]: # meta-fields or special handling
            setattr(order, field, value)

    if order_in.lines is not None:
        db.query(OrderLine).filter(OrderLine.order_id == id).delete()
        for line_in in order_in.lines:
            if line_in.variant_id is None and line_in.variant_values:
                product = db.query(Product).filter(Product.id == line_in.product_id).first()
                sku_suffix = f"-CUST-{uuid.uuid4().hex[:4].upper()}"
                new_variant = ProductVariant(
                    product_id=line_in.product_id,
                    sku=f"{product.sku}{sku_suffix}",
                    price_override=line_in.price,
                    is_active=False
                )
                db.add(new_variant)
                db.flush()
                for val in line_in.variant_values:
                    db_val = VariantValue(**val.dict(), variant_id=new_variant.id)
                    db.add(db_val)
                db.flush()
                line_in.variant_id = new_variant.id

            line = OrderLine(
                order_id=id,
                product_id=line_in.product_id,
                variant_id=line_in.variant_id,
                specification_id=line_in.specification_id,
                quantity=line_in.quantity,
                price=line_in.price,
                total=line_in.total
            )
            db.add(line)

    db.commit()
    db.refresh(order)
    populate_product_summary([order], db)

    new_obj = AuditService.get_dict(order, relationships=["lines"])
    AuditService.compare_and_log(
        db=db, entity_type="order", entity_id=order.id, user_id=current_user.id,
        action="UPDATE", old_obj=old_obj, new_obj=new_obj
    )

    return order


@router.patch("/orders/bulk-update")
async def bulk_update_orders(
    ids: List[UUID] = Query(...),
    data: dict = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update multiple orders at once (e.g., change manager or stage)."""
    if not ids or not data:
        raise HTTPException(status_code=400, detail="Ids and data are required")

    orders = db.query(Order).filter(
        Order.id.in_(ids),
        Order.company_id == current_user.company_id
    ).all()

    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")

    # Allowed fields for bulk update
    allowed_fields = {"manager_id", "crm_stage", "status"}
    update_payload = {k: v for k, v in data.items() if k in allowed_fields}

    if not update_payload:
        raise HTTPException(status_code=400, detail="No valid fields provided for update")

    for order in orders:
        for field, value in update_payload.items():
            setattr(order, field, value)
            
        # Special logic for stage transitions
        if "crm_stage" in update_payload:
            stage = update_payload["crm_stage"]
            if stage == "done":
                order.status = "completed"
            elif stage == "production":
                order.status = "confirmed"

    db.commit()
    return {"status": "success", "updated_count": len(orders)}


@router.patch("/orders/{id}/stage", response_model=OrderResponse)
async def update_order_stage(
    id: UUID,
    stage: str = Query(..., description="New CRM stage"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Move an order to a new CRM pipeline stage (for Kanban drag & drop)."""
    valid_stages = {"new", "payment", "processing", "production", "done"}
    if stage not in valid_stages:
        raise HTTPException(status_code=400, detail=f"Invalid stage. Must be one of: {valid_stages}")

    order = db.query(Order).filter(
        Order.id == id,
        Order.company_id == current_user.company_id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Rule 1: Payment
    if stage == "payment":
        if not order.counterparty_id:
            raise HTTPException(status_code=422, detail="Для переходу в 'Оплата' вкажіть клієнта")
        if not order.lines:
            raise HTTPException(status_code=422, detail="Для переходу в 'Оплата' додайте виріб")
        if not order.total_amount or float(order.total_amount) <= 0:
            raise HTTPException(status_code=422, detail="Для переходу в 'Оплата' вкажіть суму")

    # Rule 2: Processing (В роботі)
    if stage == "processing":
        if not order.counterparty_id:
            raise HTTPException(status_code=422, detail="Клієнт не заповнений")
        if not order.deadline_date:
            raise HTTPException(status_code=422, detail="Вкажіть дату готовності перед передачею заявки в роботу")
        if not order.total_amount or float(order.total_amount) <= 0:
            raise HTTPException(status_code=422, detail="Сума замовлення має бути більше 0")

    # Rule 3: Production
    if stage == "production":
        if order.crm_stage != "processing":
            raise HTTPException(status_code=422, detail="Перехід у Виробництво дозволений тільки зі статусу 'В роботі'")
        if not order.deadline_date:
            raise HTTPException(status_code=422, detail="Вкажіть дату готовності перед передачею у виробництво")

    order.crm_stage = stage
    if stage == "done":
        order.status = "completed"
    elif stage == "production":
        order.status = "confirmed"

    db.commit()
    db.refresh(order)
    return order


@router.get("/orders/{id}/material-check", response_model=MaterialCheckResponse)
async def check_order_materials(
    id: UUID,
    product_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Check BOM materials availability for an order.
    If product_id is provided, checks that product's default spec.
    Otherwise checks all order lines.
    """
    order = db.query(Order).filter(
        Order.id == id,
        Order.company_id == current_user.company_id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Determine which products to check
    if product_id:
        target_product_ids = [(product_id, Decimal("1"))]
    else:
        target_product_ids = [(line.product_id, line.quantity) for line in order.lines]

    if not target_product_ids:
        return MaterialCheckResponse(
            order_id=id, product_id=product_id,
            has_issues=False, items=[]
        )

    # Aggregate required materials from BOM
    required: dict[UUID, dict] = {}
    for pid, qty in target_product_ids:
        spec = db.query(ProductSpecification).filter(
            ProductSpecification.product_id == pid,
            ProductSpecification.is_default == True,
            ProductSpecification.is_active == True,
        ).first()
        if not spec:
            continue
        for item in spec.items:
            cid = item.component_id
            if cid not in required:
                component = db.query(Product).filter(Product.id == cid).first()
                required[cid] = {
                    "component_id": cid,
                    "component_name": component.name if component else "—",
                    "component_sku": component.sku if component else "—",
                    "unit_of_measure": item.unit_of_measure or (component.unit_of_measure if component else "шт"),
                    "required_qty": Decimal("0"),
                }
            required[cid]["required_qty"] += Decimal(str(item.quantity)) * qty

    # Get stock levels from AccumulationRegister
    items_out = []
    has_issues = False

    for cid, info in required.items():
        stock_row = db.query(
            func.coalesce(func.sum(AccumulationRegister.quantity), 0)
        ).filter(
            AccumulationRegister.company_id == current_user.company_id,
            AccumulationRegister.register_type == RegisterType.STOCK,
            AccumulationRegister.product_id == cid,
        ).scalar()

        available = Decimal(str(stock_row or 0))
        req = info["required_qty"]

        if available >= req:
            st = "ok"
        elif available > 0:
            st = "low"
            has_issues = True
        else:
            st = "missing"
            has_issues = True

        items_out.append(MaterialCheckItem(
            component_id=cid,
            component_name=info["component_name"],
            component_sku=info["component_sku"],
            unit_of_measure=info["unit_of_measure"],
            required_qty=req,
            available_qty=available,
            status=st,
        ))

    return MaterialCheckResponse(
        order_id=id,
        product_id=product_id,
        has_issues=has_issues,
        items=items_out,
    )


@router.post("/orders/{id}/send-to-production")
async def send_order_to_production(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Save order as confirmed + auto-create a ProductionOrder linked to it.
    Returns { order, production_order }.
    """
    from app.models.specification import ProductSpecification
    from app.models.production import ProductionOrder, ProductionOrderLine, ProductionOrderMaterial
    from app.models.warehouse import Warehouse
    from app.services.sequence_service import SequenceService

    order = db.query(Order).filter(
        Order.id == id,
        Order.company_id == current_user.company_id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.crm_stage = "production"
    order.status    = "confirmed"

    # Get default warehouse
    warehouse = db.query(Warehouse).filter(
        Warehouse.company_id == current_user.company_id,
        Warehouse.is_deleted == False
    ).order_by(Warehouse.is_default.desc()).first()
    if not warehouse:
        raise HTTPException(status_code=400, detail="No warehouse found for this company")

    # Build production order number
    prod_num = SequenceService.get_next_number(db, "production_order", "PRD-")

    prod_order = ProductionOrder(
        order_number=prod_num,
        status="draft",
        base_order_id=order.id,
        company_id=current_user.company_id,
        warehouse_id=warehouse.id,
        created_by=current_user.id,
        due_date=order.deadline_date,
        comment=f"Авто-створено з CRM замовлення {order.order_number}",
    )
    db.add(prod_order)
    db.flush()

    for line in order.lines:
        # Find default active spec for this product
        spec = db.query(ProductSpecification).filter(
            ProductSpecification.product_id == line.product_id,
            ProductSpecification.is_default == True,
            ProductSpecification.is_active == True,
        ).first()

        db_line = ProductionOrderLine(
            production_order_id=prod_order.id,
            product_id=line.product_id,
            variant_id=line.variant_id,
            specification_id=spec.id if spec else None,
            quantity=line.quantity,
        )
        db.add(db_line)

        # Auto-expand BOM into materials
        if spec:
            parent_dims = {
                'width_cm': 0, 'height_cm': 0, 'length_cm': 0, 'weight_kg': 0,
                'custom_attributes': order.attributes_values or {}
            }
            # Try to get dims from line's variant if available
            if line.variant:
                parent_dims['width_cm'] = float(line.variant.width_cm or 0)
                parent_dims['height_cm'] = float(line.variant.height_cm or 0)
                parent_dims['length_cm'] = float(line.variant.length_cm or 0)
                parent_dims['weight_kg'] = float(line.variant.weight_kg or 0)

            from app.services.specification_service import SpecificationService
            for item in spec.items:
                component = item.component
                variant = None
                
                if item.line_type == 'detail':
                    component = SpecificationService.resolve_detail_component(item, parent_dims, db)
                    
                    target_length = 0.0
                    if item.size_from_attr:
                        attr_val = parent_dims['custom_attributes'].get(item.size_from_attr, 0)
                        target_length = float(attr_val) * float(item.size_multiplier or 1.0)
                    elif item.fixed_length:
                        target_length = float(item.fixed_length)
                        
                    target_width = float(item.fixed_width) if item.fixed_width else None
                    
                    if component:
                        variant = SpecificationService.find_matching_variant(component, target_length, target_width, db)

                qty = SpecificationService.calculate_item_quantity(item, parent_dims)

                db_mat = ProductionOrderMaterial(
                    production_order_id=prod_order.id,
                    component_id=component.id if component else item.component_id,
                    variant_id=variant.id if variant else None,
                    required_quantity=qty * line.quantity,
                    unit_of_measure=item.unit_of_measure or (component.unit_of_measure if component else "шт"),
                )
                db.add(db_mat)

    db.commit()
    db.refresh(order)
    db.refresh(prod_order)

    return {"order_id": str(order.id), "production_order_id": str(prod_order.id), "production_order_number": prod_order.order_number}


@router.delete("/orders/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    order = db.query(Order).filter(
        Order.id == id,
        Order.company_id == current_user.company_id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    old_obj = AuditService.get_dict(order, relationships=["lines"])
    AuditService.compare_and_log(
        db=db, entity_type="order", entity_id=order.id, user_id=current_user.id,
        action="DELETE", old_obj=old_obj
    )

    db.delete(order)
    db.commit()
    return None


@router.get("/export")
async def export_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export orders to CSV format for Excel."""
    query = db.query(Order).filter(Order.company_id == current_user.company_id)
    orders = query.order_by(Order.order_date.desc()).all()
    populate_product_summary(orders, db)
    
    # Headers: Номер | Клієнт | Виріб | Сума | Передоплата | Статус | Менеджер | Дедлайн
    headers = ["Номер", "Клієнт", "Виріб", "Сума", "Передоплата", "Статус", "Менеджер", "Дедлайн"]
    
    output = StringIO()
    # Use semicolon as delimiter and utf-8-sig for Excel compatibility in Ukraine/Europe
    writer = csv.writer(output, delimiter=';')
    writer.writerow(headers)
    
    for o in orders:
        client_name = o.counterparty.name if o.counterparty else "—"
        manager_name = o.manager.name if o.manager else "—"
        deadline = o.deadline_date.strftime("%d.%m.%Y") if o.deadline_date else "—"
        
        writer.writerow([
            o.order_number,
            client_name,
            o.product_summary,
            str(o.total_amount),
            str(o.paid_amount or 0),
            o.crm_stage,
            manager_name,
            deadline
        ])
    
    filename = f"orders_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Return as streaming response with BOM for Excel
    content = output.getvalue().encode("utf-8-sig")
    
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
