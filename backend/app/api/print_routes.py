from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from datetime import datetime

from app.db.session import get_db, engine
from app.models import PrintTemplate, Order, SalesInvoice, Company, Counterparty, BankAccount
from app.schemas.print_template import PrintTemplateCreate, PrintTemplateUpdate, PrintTemplateResponse
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/print", tags=["Print Templates"])

# Ensure table exists on first access in case Alembic was not executed
try:
    from app.models import Base
    Base.metadata.create_all(bind=engine)
except Exception:
    pass

DEFAULT_INVOICE_HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@page {
  size: A4;
  margin: 12mm;
}
.print-page {
  width: 210mm;
  min-height: 297mm;
  background: #fff;
  color: #000;
  font-family: Arial, sans-serif;
  font-size: 12px;
  line-height: 1.35;
  padding: 10px;
}
.header { font-weight: bold; font-size: 18px; border-bottom: 2px solid #000; padding-bottom: 5px; margin-bottom: 15px; }
.table { width: 100%; border-collapse: collapse; margin-top: 15px; }
.table th, .table td { border: 1px solid #000; padding: 6px; text-align: left; }
.table th { background-color: #f2f2f2; }
.totals { text-align: right; margin-top: 15px; font-weight: bold; }
.in-words { margin-top: 20px; font-style: italic; border-top: 1px solid #ccc; padding-top: 10px; }
@media print {
  body { background: #fff; }
  .no-print { display: none !important; }
  .print-page { box-shadow: none; margin: 0; }
}
</style>
</head>
<body>
<div class="print-page">
  <div class="header">Рахунок на оплату № {{document.number}} від {{document.date}}</div>
  <p><strong>Постачальник:</strong> {{seller.name}}, ЄДРПОУ {{seller.edrpou}}, IBAN {{seller.iban}}, Банк {{seller.bank_name}}, МФО {{seller.mfo}}</p>
  <p><strong>Покупець:</strong> {{buyer.name}}</p>
  
  <table class="table">
    <thead>
      <tr>
        <th>№</th>
        <th>Артикул</th>
        <th>Товари / послуги</th>
        <th>Кількість</th>
        <th>Од.</th>
        <th>Ціна</th>
        <th>Сума</th>
      </tr>
    </thead>
    <tbody>
      {{items_table}}
    </tbody>
  </table>
  
  <div class="totals">
    <p>Разом: {{totals.total_without_vat}} грн</p>
    <p>ПДВ: {{totals.vat}} грн</p>
    <p>Усього до сплати: {{totals.total_with_vat}} грн</p>
  </div>
  
  <div class="in-words">
    Всього найменувань {{totals.items_count}}, на суму {{totals.total_with_vat}} грн.<br>
    {{totals.total_in_words}}
  </div>
</div>
</body>
</html>"""

@router.get("/templates", response_model=List[PrintTemplateResponse])
def get_templates(
    document_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get active print templates, optionally filtered by document type."""
    query = db.query(PrintTemplate).filter(PrintTemplate.is_active == True)
    if document_type:
        query = query.filter(PrintTemplate.document_type == document_type)
    
    templates = query.all()
    
    # If empty and requesting 'invoice', inject default placeholder template
    if not templates and document_type == "invoice":
        # Return a fake or generated default instance safely
        default_t = PrintTemplate(
            id=uuid4(),
            name="Системний рахунок (Default)",
            document_type="invoice",
            description="Автоматичний дефолтний шаблон системи",
            html_template=DEFAULT_INVOICE_HTML,
            css_template="",
            is_default=True,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        return [default_t]
        
    return templates

@router.get("/templates/{template_id}", response_model=PrintTemplateResponse)
def get_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    template = db.query(PrintTemplate).filter(PrintTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Шаблон не знайдено")
    return template

@router.post("/templates", response_model=PrintTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(
    template_in: PrintTemplateCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # If setting this as default, unset previous defaults for this doc type
    if template_in.is_default:
        db.query(PrintTemplate).filter(
            PrintTemplate.document_type == template_in.document_type,
            PrintTemplate.is_default == True
        ).update({"is_default": False})

    template = PrintTemplate(**template_in.model_dump())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template

@router.put("/templates/{template_id}", response_model=PrintTemplateResponse)
def update_template(
    template_id: UUID,
    template_in: PrintTemplateUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    template = db.query(PrintTemplate).filter(PrintTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Шаблон не знайдено")
        
    update_data = template_in.model_dump(exclude_unset=True)
    
    if update_data.get("is_default"):
        db.query(PrintTemplate).filter(
            PrintTemplate.document_type == template.document_type,
            PrintTemplate.is_default == True
        ).update({"is_default": False})

    for key, val in update_data.items():
        setattr(template, key, val)
        
    db.commit()
    db.refresh(template)
    return template

@router.delete("/templates/{template_id}")
def delete_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    template = db.query(PrintTemplate).filter(PrintTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Шаблон не знайдено")
    
    db.delete(template)
    db.commit()
    return {"status": "deleted"}

@router.get("/data/{document_type}/{document_id}")
def get_print_data(
    document_type: str,
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Collect data context for the document and format it for the print template engine.
    Supported types: invoice, sales_invoice
    """
    totals = {
        "items_count": 0,
        "total_without_vat": 0.0,
        "vat": 0.0,
        "total_with_vat": 0.0,
        "total_in_words": "",
    }
    
    items = []
    doc_data = {"number": "Б/Н", "date": datetime.now().strftime("%d.%m.%Y")}
    seller = {"name": "Постачальник"}
    buyer = {"name": "Покупець"}

    if document_type == "invoice":
        # Assuming Order model acts as payment invoice source
        order = db.query(Order).filter(Order.id == document_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Документ не знайдено")
        
        doc_data["number"] = order.order_number
        doc_data["date"] = order.order_date.strftime("%d.%m.%Y") if order.order_date else ""
        doc_data["contract"] = order.contract or ""
        doc_data["comment"] = order.comment or ""
        
        # Find company details
        company = db.query(Company).filter(Company.id == order.company_id).first()
        if company:
            seller["name"] = company.name
            seller["edrpou"] = getattr(company, "edrpou", "") or getattr(company, "tax_id", "")
            seller["address"] = getattr(company, "address", "")
            seller["phone"] = getattr(company, "phone", "")
            
            # Find IBAN from related accounts
            bank = db.query(BankAccount).filter(BankAccount.company_id == company.id).first()
            if bank:
                seller["iban"] = bank.iban or ""
                seller["bank_name"] = bank.bank_name or ""
                seller["mfo"] = getattr(bank, "mfo", "")

        # Find buyer details
        cp = db.query(Counterparty).filter(Counterparty.id == order.counterparty_id).first()
        if cp:
            buyer["name"] = cp.name
            buyer["edrpou"] = getattr(cp, "edrpou", "")
            buyer["address"] = getattr(cp, "address", "")

        # Lines
        totals["items_count"] = len(order.lines)
        totals["total_with_vat"] = float(order.total_amount)
        # For simplified mapping, assuming VAT 20% if requested
        totals["total_without_vat"] = round(totals["total_with_vat"] / 1.2, 2)
        totals["vat"] = round(totals["total_with_vat"] - totals["total_without_vat"], 2)

        for idx, line in enumerate(order.lines, 1):
            line_total = float(line.total)
            line_price = float(line.price)
            items.append({
                "index": idx,
                "name": line.product.name if line.product else "Товар",
                "quantity": float(line.quantity),
                "unit": "шт",
                "price_with_vat": line_price,
                "sum_with_vat": line_total
            })

    elif document_type == "sales_invoice":
        invoice = db.query(SalesInvoice).filter(SalesInvoice.id == document_id).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Видаткову накладну не знайдено")

        doc_data["number"] = invoice.invoice_number
        doc_data["date"] = invoice.invoice_date.strftime("%d.%m.%Y") if invoice.invoice_date else ""
        
        # Find company details
        company = db.query(Company).filter(Company.id == invoice.company_id).first()
        if company:
            seller["name"] = company.name
            seller["edrpou"] = getattr(company, "edrpou", "") or getattr(company, "tax_id", "")
            seller["address"] = getattr(company, "address", "")
            
        cp = db.query(Counterparty).filter(Counterparty.id == invoice.counterparty_id).first()
        if cp:
            buyer["name"] = cp.name
            buyer["edrpou"] = getattr(cp, "edrpou", "")
            buyer["address"] = getattr(cp, "address", "")

        totals["items_count"] = len(invoice.lines)
        totals["total_with_vat"] = float(invoice.total_amount)
        totals["total_without_vat"] = round(totals["total_with_vat"] / 1.2, 2)
        totals["vat"] = round(totals["total_with_vat"] - totals["total_without_vat"], 2)

        for idx, line in enumerate(invoice.lines, 1):
            items.append({
                "index": idx,
                "name": line.product.name if line.product else "Товар",
                "quantity": float(line.quantity),
                "unit": "шт",
                "price_with_vat": float(line.price),
                "sum_with_vat": float(line.total)
            })

    return {
        "document": doc_data,
        "seller": seller,
        "buyer": buyer,
        "items": items,
        "totals": totals
    }
