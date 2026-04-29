"""
Business Process Engine
Evaluates automation rules and executes actions (create documents, etc.)
"""
from datetime import date
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.business_process import BusinessProcessRule, DocumentRelation, AutomationLog


# ─── Validation ──────────────────────────────────────────────────────────────

def _validate_crm_to_processing(db: Session, order_id: UUID) -> Optional[str]:
    """Return an error string if the CRM order cannot move to 'processing'."""
    from app.models import Order
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return "Замовлення не знайдено"
    if not order.counterparty_id:
        return "Клієнт не заповнений"
    if not order.deadline_date:
        return "Вкажіть дату готовності перед передачею заявки в роботу"
    if not order.total_amount or float(order.total_amount) <= 0:
        return "Сума замовлення має бути більше 0"
    return None


def _validate_production_to_completed(db: Session, production_id: UUID) -> Optional[str]:
    """Return an error string if the production order cannot move to 'completed'."""
    from app.models import ProductionOrder
    prod = db.query(ProductionOrder).filter(ProductionOrder.id == production_id).first()
    if not prod:
        return "Виробниче завдання не знайдено"
    if not prod.client_id:
        return "Клієнт не заповнений у виробничому завданні"
    if not prod.lines:
        return "Виробниче завдання не має рядків продукції"
    total_qty = sum(float(l.quantity or 0) for l in prod.lines)
    if total_qty <= 0:
        return "Кількість продукції має бути більше 0"
    return None


# ─── Duplicate check ─────────────────────────────────────────────────────────

def _find_existing_relation(
    db: Session, source_type: str, source_id: UUID, target_type: str
) -> Optional[DocumentRelation]:
    return db.query(DocumentRelation).filter(
        DocumentRelation.source_type == source_type,
        DocumentRelation.source_id == source_id,
        DocumentRelation.target_type == target_type,
    ).first()


# ─── Execution helpers ───────────────────────────────────────────────────────

def _execute_create_customer_order(
    db: Session, company_id: UUID, order_id: UUID, rule: BusinessProcessRule
) -> dict:
    """Record that the CRM lead has become a confirmed customer order."""
    from app.models import Order

    if rule.prevent_duplicates:
        existing = _find_existing_relation(db, "crm_lead", order_id, "customer_order")
        if existing:
            order = db.query(Order).filter(Order.id == existing.target_id).first()
            return {
                "status": "skipped",
                "message": f"Замовлення покупця вже існує: {order.order_number if order else existing.target_id}",
                "document_type": "customer_order",
                "document_id": str(existing.target_id),
                "document_number": order.order_number if order else None,
            }

    order = db.query(Order).filter(Order.id == order_id).first()

    rel = DocumentRelation(
        source_type="crm_lead",
        source_id=order_id,
        target_type="customer_order",
        target_id=order_id,
        relation_type="crm_to_order",
        company_id=company_id,
    )
    db.add(rel)

    if rule.log_execution:
        db.add(AutomationLog(
            rule_id=rule.id,
            event_type="status_changed",
            source_type="crm_lead",
            source_id=order_id,
            action_type="create_customer_order",
            status="success",
            message=f"Замовлення покупця {order.order_number} підтверджено",
            created_document_type="customer_order",
            created_document_id=order_id,
            company_id=company_id,
        ))
    db.flush()

    return {
        "status": "success",
        "message": f"Замовлення покупця {order.order_number} підтверджено в роботі",
        "document_type": "customer_order",
        "document_id": str(order_id),
        "document_number": order.order_number,
    }


def _execute_create_sales_invoice(
    db: Session, company_id: UUID, production_id: UUID, rule: BusinessProcessRule, created_by: UUID
) -> dict:
    """Create a SalesInvoice from a completed ProductionOrder."""
    from app.models import ProductionOrder, SalesInvoice, SalesInvoiceLine, Order, OrderLine
    from app.services.sequence_service import SequenceService

    prod = db.query(ProductionOrder).filter(ProductionOrder.id == production_id).first()
    if not prod:
        return {"status": "failed", "message": "Виробниче завдання не знайдено"}

    if rule.prevent_duplicates:
        existing = _find_existing_relation(db, "production_task", production_id, "sales_invoice")
        if existing:
            inv = db.query(SalesInvoice).filter(SalesInvoice.id == existing.target_id).first()
            return {
                "status": "skipped",
                "message": f"Видаткова накладна вже існує: {inv.invoice_number if inv else existing.target_id}",
                "document_type": "sales_invoice",
                "document_id": str(existing.target_id),
                "document_number": inv.invoice_number if inv else None,
            }

    # Build price map from base order lines (if available)
    price_map: dict = {}
    if prod.base_order_id:
        base_lines = db.query(OrderLine).filter(OrderLine.order_id == prod.base_order_id).all()
        for bl in base_lines:
            price_map[str(bl.product_id)] = float(bl.unit_price or 0)

    invoice_number = SequenceService.get_next_number(db, "sales_invoice", "ВН-")

    inv_lines = []
    total = 0.0
    for line in prod.lines:
        price = price_map.get(str(line.product_id), 0.0)
        line_total = float(line.quantity or 0) * price
        total += line_total
        inv_line = SalesInvoiceLine(
            product_id=line.product_id,
            variant_id=line.variant_id,
            quantity=line.quantity,
            price=price,
            total=line_total,
            warehouse_id=prod.warehouse_id,
        )
        inv_lines.append(inv_line)

    invoice = SalesInvoice(
        company_id=company_id,
        invoice_number=invoice_number,
        invoice_date=date.today(),
        counterparty_id=prod.client_id,
        warehouse_id=prod.warehouse_id,
        order_id=prod.base_order_id,
        total_amount=total,
        currency="UAH",
        status="POSTED",
        created_by=created_by,
        notes=prod.comment,
    )
    db.add(invoice)
    db.flush()

    for il in inv_lines:
        il.invoice_id = invoice.id
        db.add(il)

    rel = DocumentRelation(
        source_type="production_task",
        source_id=production_id,
        target_type="sales_invoice",
        target_id=invoice.id,
        relation_type="production_to_invoice",
        company_id=company_id,
    )
    db.add(rel)

    if rule.log_execution:
        db.add(AutomationLog(
            rule_id=rule.id,
            event_type="status_changed",
            source_type="production_task",
            source_id=production_id,
            action_type="create_sales_invoice",
            status="success",
            message=f"Видаткова накладна {invoice_number} створена",
            created_document_type="sales_invoice",
            created_document_id=invoice.id,
            company_id=company_id,
        ))
    db.flush()

    return {
        "status": "success",
        "message": f"Видаткова накладна {invoice_number} створена",
        "document_type": "sales_invoice",
        "document_id": str(invoice.id),
        "document_number": invoice_number,
    }


# ─── Public API ───────────────────────────────────────────────────────────────

ACTION_VALIDATORS = {
    ("crm_lead", "status_changed", "processing"): _validate_crm_to_processing,
    ("production_task", "status_changed", "completed"): _validate_production_to_completed,
}

ACTION_EXECUTORS = {
    "create_customer_order": _execute_create_customer_order,
    "create_sales_invoice": _execute_create_sales_invoice,
}


def evaluate_event(
    db: Session,
    company_id: UUID,
    source_type: str,
    source_id: UUID,
    event_type: str,
    to_status: str,
) -> dict:
    """
    Evaluate matching rules for an event.
    Returns:
      can_proceed   – False if validation blocks the transition
      validation_error – human-readable error when can_proceed=False
      rules         – list of matching rule descriptors (mode, action_type, rule_id, rule_name)
    """
    # 1. Validation check
    validator = ACTION_VALIDATORS.get((source_type, event_type, to_status))
    if validator:
        err = validator(db, source_id)
        if err:
            return {"can_proceed": False, "validation_error": err, "rules": []}

    # 2. Find active matching rules
    matching = db.query(BusinessProcessRule).filter(
        BusinessProcessRule.company_id == company_id,
        BusinessProcessRule.source_type == source_type,
        BusinessProcessRule.event_type == event_type,
        BusinessProcessRule.to_status == to_status,
        BusinessProcessRule.is_active == True,
    ).all()

    rules_out = [
        {
            "rule_id": str(r.id),
            "rule_name": r.name,
            "mode": r.mode,
            "action_type": r.action_type,
        }
        for r in matching
    ]
    return {"can_proceed": True, "validation_error": None, "rules": rules_out}


def execute_rule(
    db: Session,
    company_id: UUID,
    rule_id: UUID,
    source_type: str,
    source_id: UUID,
    created_by: UUID,
) -> dict:
    """Execute a specific rule's action. Called after user confirmation or automatically."""
    rule = db.query(BusinessProcessRule).filter(
        BusinessProcessRule.id == rule_id,
        BusinessProcessRule.company_id == company_id,
    ).first()
    if not rule:
        return {"status": "failed", "message": "Правило не знайдено"}
    if rule.mode == "disabled":
        return {"status": "skipped", "message": "Правило вимкнено"}

    executor = ACTION_EXECUTORS.get(rule.action_type)
    if not executor:
        return {"status": "failed", "message": f"Невідомий тип дії: {rule.action_type}"}

    if rule.action_type == "create_customer_order":
        result = executor(db, company_id, source_id, rule)
    else:
        result = executor(db, company_id, source_id, rule, created_by)

    db.commit()
    return result


def skip_rule(
    db: Session,
    company_id: UUID,
    rule_id: UUID,
    source_type: str,
    source_id: UUID,
) -> None:
    """Log that the user chose not to execute the rule."""
    rule = db.query(BusinessProcessRule).filter(
        BusinessProcessRule.id == rule_id
    ).first()
    if rule and rule.log_execution:
        db.add(AutomationLog(
            rule_id=rule_id,
            event_type="status_changed",
            source_type=source_type,
            source_id=source_id,
            action_type=rule.action_type if rule else None,
            status="skipped",
            message="Користувач відмовився від створення документа",
            company_id=company_id,
        ))
        db.commit()


def get_related_documents(db: Session, source_type: str, source_id: UUID) -> list:
    """Return all document relations for a given source document."""
    from app.models import Order, SalesInvoice
    from app.models import ProductionOrder

    relations = db.query(DocumentRelation).filter(
        DocumentRelation.source_id == source_id,
    ).all()

    also_as_target = db.query(DocumentRelation).filter(
        DocumentRelation.target_id == source_id,
    ).all()

    result = []

    def _doc_label(doc_type: str, doc_id: UUID) -> dict:
        label = str(doc_id)
        number = None
        url = None
        if doc_type == "customer_order":
            o = db.query(Order).filter(Order.id == doc_id).first()
            if o:
                number = o.order_number
                label = f"ЗП: {o.order_number}"
                url = f"/crm/orders/{o.id}"
        elif doc_type == "crm_lead":
            o = db.query(Order).filter(Order.id == doc_id).first()
            if o:
                number = o.order_number
                label = f"CRM: {o.order_number}"
                url = f"/crm/orders/{o.id}"
        elif doc_type == "sales_invoice":
            inv = db.query(SalesInvoice).filter(SalesInvoice.id == doc_id).first()
            if inv:
                number = inv.invoice_number
                label = f"ВН: {inv.invoice_number}"
                url = f"/sales/invoices/{inv.id}"
        elif doc_type == "production_task":
            po = db.query(ProductionOrder).filter(ProductionOrder.id == doc_id).first()
            if po:
                number = po.order_number
                label = f"Вир: {po.order_number}"
                url = f"/production/orders/{po.id}"
        return {"doc_type": doc_type, "doc_id": str(doc_id), "number": number, "label": label, "url": url}

    for rel in relations:
        result.append({
            "relation_type": rel.relation_type,
            "direction": "outgoing",
            **_doc_label(rel.target_type, rel.target_id),
        })
    for rel in also_as_target:
        result.append({
            "relation_type": rel.relation_type,
            "direction": "incoming",
            **_doc_label(rel.source_type, rel.source_id),
        })

    return result


def seed_default_rules(db: Session, company_id: UUID) -> None:
    """Create the two default automation rules for a company if they don't exist yet."""
    existing = db.query(BusinessProcessRule).filter(
        BusinessProcessRule.company_id == company_id
    ).count()
    if existing > 0:
        return

    db.add(BusinessProcessRule(
        company_id=company_id,
        name="CRM-заявка → Замовлення покупця",
        description="При переході CRM-заявки у статус «В роботі» підтвердити створення Замовлення покупця",
        is_active=True,
        source_type="crm_lead",
        event_type="status_changed",
        from_status="new",
        to_status="processing",
        action_type="create_customer_order",
        mode="ask_confirmation",
        prevent_duplicates=True,
        log_execution=True,
    ))

    db.add(BusinessProcessRule(
        company_id=company_id,
        name="Виробництво → Видаткова накладна",
        description="При завершенні виробничого завдання запропонувати створення Видаткової накладної",
        is_active=True,
        source_type="production_task",
        event_type="status_changed",
        from_status="in_progress",
        to_status="completed",
        action_type="create_sales_invoice",
        mode="ask_confirmation",
        prevent_duplicates=True,
        log_execution=True,
    ))

    db.commit()
