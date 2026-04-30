from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy.orm import Session
from sqlalchemy import func


def _get_current_stock(db: Session, company_id, product_id, variant_id=None) -> Decimal:
    """Sum all STOCK register entries for this product (before the current receipt is posted)."""
    from app.models.register import AccumulationRegister, RegisterType
    q = db.query(func.sum(AccumulationRegister.quantity)).filter(
        AccumulationRegister.company_id == company_id,
        AccumulationRegister.product_id == product_id,
        AccumulationRegister.register_type == RegisterType.STOCK,
    )
    if variant_id:
        q = q.filter(AccumulationRegister.variant_id == variant_id)
    else:
        q = q.filter(AccumulationRegister.variant_id.is_(None))
    result = q.scalar()
    return Decimal(str(result or 0))


def update_product_cost_from_receipt(
    db: Session,
    company_id,
    receipt_id,
    receipt_number: str,
    receipt_date,
    supplier_id,
    lines,
    created_by_id,
):
    """
    Update product.cost for every line in a purchase receipt.
    Called BEFORE PostingService.post_document so that stock totals
    do not yet include the current receipt's entries.
    """
    from app.models.product import Product
    from app.models.company import Company
    from app.models.product_cost_history import ProductCostHistory

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        return

    method = getattr(company, 'cost_method', None) or 'last_price'
    if method == 'none':
        return

    if hasattr(receipt_date, 'strftime'):
        date_str = receipt_date.strftime('%d.%m.%Y')
    else:
        date_str = str(receipt_date)[:10]

    for line in lines:
        product = db.query(Product).filter(Product.id == line.product_id).first()
        if not product:
            continue

        qty = Decimal(str(line.quantity or 0))
        if qty <= 0:
            continue

        # Prefer explicit price; fall back to total / qty
        if line.price and Decimal(str(line.price)) > 0:
            unit_cost = Decimal(str(line.price))
        elif line.total and qty > 0:
            unit_cost = Decimal(str(line.total)) / qty
        else:
            continue

        # Duplicate guard — skip if this document+product was already processed
        existing = db.query(ProductCostHistory).filter(
            ProductCostHistory.document_id == receipt_id,
            ProductCostHistory.product_id == line.product_id,
        ).first()
        if existing:
            continue

        old_cost = product.cost if product.cost is not None else Decimal('0')
        variant_id = getattr(line, 'variant_id', None)

        if method == 'last_price':
            new_cost = unit_cost
            old_stock = Decimal('0')
        else:  # weighted_average
            old_stock = _get_current_stock(db, company_id, line.product_id, variant_id)
            if old_stock <= 0:
                new_cost = unit_cost
            else:
                new_cost = (old_stock * old_cost + qty * unit_cost) / (old_stock + qty)

        new_cost = new_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        product.cost = new_cost
        product.cost_source = f"Оновлено з {receipt_number} від {date_str}"

        hist = ProductCostHistory(
            product_id=line.product_id,
            variant_id=variant_id,
            document_type="PurchaseReceipt",
            document_id=receipt_id,
            document_number=receipt_number,
            supplier_id=supplier_id,
            old_stock=old_stock,
            old_cost=old_cost,
            incoming_qty=qty,
            incoming_price=unit_cost,
            new_cost=new_cost,
            method=method,
            changed_by=created_by_id,
            company_id=company_id,
        )
        db.add(hist)
