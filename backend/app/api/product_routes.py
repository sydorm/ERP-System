from typing import List, Optional
from uuid import UUID
from decimal import Decimal, InvalidOperation
from io import BytesIO, StringIO
import csv
import re
import uuid
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form, Body
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.session import get_db
from app.models import Product, User, ProductSpecification, SpecificationItem, RegisterType
from app.models.counterparty import Counterparty
from app.models.variant import ProductVariant, VariantValue
from app.models.attribute import Attribute, CategoryAttribute
from app.schemas import ProductCreate, ProductUpdate, ProductResponse, ProductAttributeLight
from app.api.dependencies import get_current_active_user
from app.services.posting_service import PostingService

router = APIRouter()

IMPORT_MAX_FILE_SIZE = 10 * 1024 * 1024
IMPORT_MAX_ROWS = 5000
IMPORT_PREVIEW_ROWS = 20
IMPORT_SESSIONS: dict = {}
IMPORT_REPORTS: dict = {}

IMPORT_FIELDS = [
    {"key": "name", "label": "Назва товару", "required": True},
    {"key": "sku", "label": "Артикул / SKU", "recommended": True},
    {"key": "internal_code", "label": "Внутрішній код"},
    {"key": "barcode", "label": "Штрихкод"},
    {"key": "category", "label": "Категорія", "recommended": True},
    {"key": "product_type", "label": "Тип товару", "recommended": True},
    {"key": "unit_of_measure", "label": "Одиниця виміру", "required": True},
    {"key": "description", "label": "Опис"},
    {"key": "status", "label": "Статус"},
    {"key": "track_inventory", "label": "Облік запасів"},
    {"key": "length_mm", "label": "Довжина (мм)"},
    {"key": "width_mm", "label": "Ширина (мм)"},
    {"key": "height_mm", "label": "Висота (мм)"},
    {"key": "weight_kg", "label": "Вага (кг)"},
    {"key": "price", "label": "Ціна продажу"},
    {"key": "cost", "label": "Собівартість"},
    {"key": "currency", "label": "Валюта"},
    {"key": "supplier_name", "label": "Постачальник"},
    {"key": "supplier_sku", "label": "Артикул постачальника"},
    {"key": "supplier_url", "label": "Посилання постачальника"},
    {"key": "supplier_url_type", "label": "Тип посилання"},
    {"key": "extra_attributes", "label": "Додаткові характеристики"},
]

FIELD_ALIASES = {
    "name": ["назва", "назва товару", "товар", "name", "product name", "найменування"],
    "sku": ["артикул", "sku", "код товару", "артикул sku"],
    "internal_code": ["внутрішній код", "internal code", "код"],
    "barcode": ["штрихкод", "barcode", "ean"],
    "category": ["категорія", "category", "група"],
    "product_type": ["тип товару", "тип", "type"],
    "unit_of_measure": ["одиниця", "одиниця виміру", "од. вим.", "uom", "unit"],
    "description": ["опис", "description", "коментар"],
    "status": ["статус", "status", "активний"],
    "track_inventory": ["облік запасів", "облік", "track inventory", "stock tracking"],
    "length_mm": ["довжина", "довжина мм", "length", "length mm"],
    "width_mm": ["ширина", "ширина мм", "width", "width mm"],
    "height_mm": ["висота", "висота мм", "height", "height mm"],
    "weight_kg": ["вага", "вага кг", "weight", "weight kg"],
    "price": ["ціна", "ціна продажу", "price", "sale price"],
    "cost": ["собівартість", "cost", "закупівельна ціна"],
    "currency": ["валюта", "currency"],
    "supplier_name": ["постачальник", "supplier", "supplier name"],
    "supplier_sku": ["артикул постачальника", "supplier sku"],
    "supplier_url": ["посилання постачальника", "supplier link", "url", "order url"],
    "supplier_url_type": ["тип посилання", "url type"],
    "extra_attributes": ["додаткові характеристики", "характеристики", "attributes"],
}


def _norm(value) -> str:
    return re.sub(r"[\s_\-./]+", " ", str(value or "").strip().lower())


def _to_decimal(value, default=None):
    if value in (None, ""):
        return default
    try:
        return Decimal(str(value).replace(",", ".").replace(" ", ""))
    except (InvalidOperation, ValueError):
        return default


def _to_bool(value, default=True):
    if value in (None, ""):
        return default
    text = _norm(value)
    if text in {"так", "true", "1", "yes", "y", "активний", "active"}:
        return True
    if text in {"ні", "false", "0", "no", "n", "неактивний", "inactive"}:
        return False
    return default


def _normalize_uom(value):
    text = _norm(value)
    aliases = {
        "шт": "шт", "штука": "шт", "штук": "шт", "pcs": "шт", "pc": "шт",
        "м": "м", "метр": "м", "m": "м",
        "кг": "кг", "kg": "кг",
        "л": "л", "l": "л",
        "м2": "м2", "м 2": "м2", "m2": "м2",
    }
    return aliases.get(text, str(value or "").strip() or "шт")


def _suggest_mapping(headers):
    mapping = {}
    normalized_headers = {_norm(h): h for h in headers}
    for field, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            if _norm(alias) in normalized_headers:
                mapping[field] = normalized_headers[_norm(alias)]
                break
    return mapping


def _decode_csv(content: bytes):
    for enc in ("utf-8-sig", "utf-8", "cp1251"):
        try:
            text = content.decode(enc)
            break
        except UnicodeDecodeError:
            text = None
    if text is None:
        raise HTTPException(status_code=400, detail="Не вдалося прочитати CSV файл")
    sample = text[:2048]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=";,|\t,")
    except csv.Error:
        dialect = csv.excel
    return [list(row) for row in csv.reader(StringIO(text), dialect)]


def _xlsx_col_index(ref: str) -> int:
    letters = re.sub(r"[^A-Z]", "", ref.upper())
    index = 0
    for char in letters:
        index = index * 26 + (ord(char) - 64)
    return max(index - 1, 0)


def _read_xlsx(content: bytes):
    ns = {
        "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    }
    sheets_data = {}
    with zipfile.ZipFile(BytesIO(content)) as zf:
        shared = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in root.findall("m:si", ns):
                shared.append("".join(t.text or "" for t in si.findall(".//m:t", ns)))

        workbook = ET.fromstring(zf.read("xl/workbook.xml"))
        rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels.findall("rel:Relationship", ns)}
        for sheet in workbook.findall("m:sheets/m:sheet", ns):
            name = sheet.attrib.get("name", "Лист")
            rid = sheet.attrib.get(f"{{{ns['r']}}}id")
            target = rel_map.get(rid, "")
            sheet_path = "xl/" + target.lstrip("/") if not target.startswith("xl/") else target
            if sheet_path not in zf.namelist():
                continue
            root = ET.fromstring(zf.read(sheet_path))
            rows = []
            for row in root.findall(".//m:sheetData/m:row", ns):
                values = []
                for cell in row.findall("m:c", ns):
                    idx = _xlsx_col_index(cell.attrib.get("r", "A1"))
                    while len(values) <= idx:
                        values.append("")
                    cell_type = cell.attrib.get("t")
                    value_node = cell.find("m:v", ns)
                    inline_node = cell.find("m:is/m:t", ns)
                    value = ""
                    if inline_node is not None:
                        value = inline_node.text or ""
                    elif value_node is not None:
                        raw = value_node.text or ""
                        value = shared[int(raw)] if cell_type == "s" and raw.isdigit() and int(raw) < len(shared) else raw
                    values[idx] = value
                rows.append(values)
            sheets_data[name] = rows
    return sheets_data


def _rows_to_records(rows):
    rows = [[str(cell or "").strip() for cell in row] for row in rows if any(str(cell or "").strip() for cell in row)]
    if not rows:
        return [], []
    if len(rows) - 1 > IMPORT_MAX_ROWS:
        raise HTTPException(status_code=400, detail=f"Забагато рядків у файлі. Ліміт: {IMPORT_MAX_ROWS}.")
    headers = rows[0]
    records = []
    for idx, row in enumerate(rows[1:IMPORT_MAX_ROWS + 1], start=2):
        record = {"_row_number": idx}
        for col_idx, header in enumerate(headers):
            if header:
                record[header] = row[col_idx] if col_idx < len(row) else ""
        records.append(record)
    return headers, records


def _parse_import_file(content: bytes, filename: str):
    lower = filename.lower()
    if lower.endswith(".csv"):
        return {"CSV": _decode_csv(content)}
    if lower.endswith(".xlsx"):
        return _read_xlsx(content)
    raise HTTPException(status_code=400, detail="Підтримуються тільки .xlsx та .csv файли")


def _mapped_value(row: dict, mapping: dict, field: str):
    column = mapping.get(field)
    return row.get(column, "") if column else ""


def _build_payload(row: dict, mapping: dict, options: dict):
    normalize_units = options.get("normalize_units", True)
    uom = _mapped_value(row, mapping, "unit_of_measure")
    supplier_name = _mapped_value(row, mapping, "supplier_name")
    supplier_sku = _mapped_value(row, mapping, "supplier_sku")
    supplier_url = _mapped_value(row, mapping, "supplier_url")
    supplier_url_type = _mapped_value(row, mapping, "supplier_url_type") or "Сторінка товару"
    import_meta = {
        "internal_code": _mapped_value(row, mapping, "internal_code"),
        "barcode": _mapped_value(row, mapping, "barcode"),
        "product_type": _mapped_value(row, mapping, "product_type"),
        "track_inventory": _to_bool(_mapped_value(row, mapping, "track_inventory"), True),
        "extra_attributes": _mapped_value(row, mapping, "extra_attributes"),
    }
    supplier_links = []
    if supplier_name or supplier_sku or supplier_url:
        supplier_links.append({
            "supplier_name": supplier_name,
            "supplier_sku": supplier_sku,
            "order_url": supplier_url,
            "url_type": supplier_url_type,
            "is_active": True,
            "is_default_supplier": True,
            "note": "Створено імпортом номенклатури",
        })
    return {
        "name": _mapped_value(row, mapping, "name").strip(),
        "sku": _mapped_value(row, mapping, "sku").strip() or None,
        "description": _mapped_value(row, mapping, "description") or None,
        "category": _mapped_value(row, mapping, "category") or None,
        "unit_of_measure": _normalize_uom(uom) if normalize_units else (uom or "шт"),
        "price": _to_decimal(_mapped_value(row, mapping, "price"), Decimal("0.00")),
        "cost": _to_decimal(_mapped_value(row, mapping, "cost")),
        "currency": (_mapped_value(row, mapping, "currency") or "UAH").upper()[:3],
        "is_active": _to_bool(_mapped_value(row, mapping, "status"), True),
        "length_mm": _to_decimal(_mapped_value(row, mapping, "length_mm")),
        "width_mm": _to_decimal(_mapped_value(row, mapping, "width_mm")),
        "height_mm": _to_decimal(_mapped_value(row, mapping, "height_mm")),
        "weight_kg": _to_decimal(_mapped_value(row, mapping, "weight_kg")),
        "variant_config": {"import_meta": import_meta},
        "supplier_links": supplier_links or None,
    }


def _find_existing_product(db: Session, company_id, payload: dict, duplicate_keys: List[str]):
    products = db.query(Product).filter(Product.company_id == company_id, Product.is_deleted == False).all()
    for product in products:
        meta = (product.variant_config or {}).get("import_meta", {}) if isinstance(product.variant_config, dict) else {}
        checks = {
            "sku": payload.get("sku") and product.sku == payload.get("sku"),
            "name": payload.get("name") and _norm(product.name) == _norm(payload.get("name")),
            "internal_code": meta.get("internal_code") and meta.get("internal_code") == payload["variant_config"]["import_meta"].get("internal_code"),
            "barcode": meta.get("barcode") and meta.get("barcode") == payload["variant_config"]["import_meta"].get("barcode"),
        }
        if any(checks.get(key) for key in duplicate_keys):
            return product
    return None


def _validate_session(import_id: str, mapping: dict, options: dict, duplicate_keys: List[str], db: Session, current_user: User):
    session = IMPORT_SESSIONS.get(import_id)
    if not session:
        raise HTTPException(status_code=404, detail="Сесію імпорту не знайдено. Завантажте файл ще раз.")
    rows = session["records"]
    result_rows = []
    summary = {"create": 0, "update": 0, "skip": 0, "warnings": 0, "errors": 0}
    for row in rows:
        payload = _build_payload(row, mapping, options)
        errors = []
        warnings = []
        if not payload["name"]:
            errors.append("Не вказано назву товару")
        if not payload["unit_of_measure"]:
            errors.append("Не вказано одиницю виміру")
        if not payload.get("sku"):
            warnings.append("Бажано вказати артикул")
        if not payload.get("category"):
            warnings.append("Бажано вказати категорію")
        if payload.get("category") and not options.get("create_missing_categories", False):
            warnings.append("Категорії автоматично не створюються: буде використано значення з файлу")
        supplier_name = payload["supplier_links"][0]["supplier_name"] if payload.get("supplier_links") else ""
        if supplier_name and not options.get("create_missing_suppliers", False):
            existing_supplier = db.query(Counterparty).filter(
                Counterparty.company_id == current_user.company_id,
                Counterparty.is_supplier == True,
                Counterparty.name.ilike(supplier_name)
            ).first()
            if not existing_supplier:
                warnings.append("Постачальника не знайдено. Посилання збережеться текстом без створення постачальника.")

        existing = None if errors else _find_existing_product(db, current_user.company_id, payload, duplicate_keys)
        action = "error" if errors else ("update" if existing else "create")
        if action == "create":
            summary["create"] += 1
        elif action == "update":
            summary["update"] += 1
        else:
            summary["skip"] += 1
            summary["errors"] += len(errors)
        summary["warnings"] += len(warnings)
        result_rows.append({
            "row_number": row["_row_number"],
            "name": payload.get("name"),
            "sku": payload.get("sku"),
            "action": action,
            "existing_product_id": str(existing.id) if existing else None,
            "errors": errors,
            "warnings": warnings,
            "payload": payload,
        })
    session["validation"] = {"summary": summary, "rows": result_rows, "mapping": mapping, "options": options, "duplicate_keys": duplicate_keys}
    return session["validation"]


@router.post("/nomenclature/import/preview")
async def preview_nomenclature_import(
    file: UploadFile = File(...),
    sheet: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    content = await file.read()
    if len(content) > IMPORT_MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Файл завеликий. Максимальний розмір: 10 MB.")
    if not file.filename.lower().endswith((".xlsx", ".csv")):
        raise HTTPException(status_code=400, detail="Підтримуються тільки Excel .xlsx або CSV файли.")

    sheets = _parse_import_file(content, file.filename)
    sheet_names = list(sheets.keys())
    selected_sheet = sheet if sheet in sheets else sheet_names[0]
    headers, records = _rows_to_records(sheets[selected_sheet])
    if len(records) > IMPORT_MAX_ROWS:
        raise HTTPException(status_code=400, detail=f"Забагато рядків. Ліміт: {IMPORT_MAX_ROWS}.")

    import_id = str(uuid.uuid4())
    IMPORT_SESSIONS[import_id] = {
        "company_id": str(current_user.company_id),
        "filename": file.filename,
        "sheets": sheets,
        "selected_sheet": selected_sheet,
        "headers": headers,
        "records": records,
        "created_at": datetime.utcnow().isoformat(),
        "validation": None,
    }

    return {
        "import_id": import_id,
        "filename": file.filename,
        "sheets": sheet_names,
        "selected_sheet": selected_sheet,
        "headers": headers,
        "rows": records[:IMPORT_PREVIEW_ROWS],
        "row_count": len(records),
        "fields": IMPORT_FIELDS,
        "suggested_mapping": _suggest_mapping(headers),
        "limits": {"max_rows": IMPORT_MAX_ROWS, "max_file_size_mb": 10},
    }


@router.post("/nomenclature/import/validate")
async def validate_nomenclature_import(
    body: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    import_id = body.get("import_id")
    mapping = body.get("mapping") or {}
    options = body.get("options") or {}
    duplicate_keys = body.get("duplicate_keys") or ["sku", "name", "internal_code", "barcode"]
    if not import_id:
        raise HTTPException(status_code=400, detail="Не передано import_id")
    if not mapping.get("name") or not mapping.get("unit_of_measure"):
        raise HTTPException(status_code=400, detail="Зіставте обов'язкові поля: Назва товару та Одиниця виміру.")
    validation = _validate_session(import_id, mapping, options, duplicate_keys, db, current_user)
    return validation


@router.post("/nomenclature/import/execute")
async def execute_nomenclature_import(
    body: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    import_id = body.get("import_id")
    mode = body.get("mode") or "create_update"
    session = IMPORT_SESSIONS.get(import_id)
    if not session or not session.get("validation"):
        raise HTTPException(status_code=400, detail="Перед імпортом потрібно виконати preview та validation.")

    validation = session["validation"]
    result = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}
    report_rows = []
    create_missing_suppliers = validation["options"].get("create_missing_suppliers", False)

    for item in validation["rows"]:
      try:
        if item["errors"]:
            result["skipped"] += 1
            result["errors"] += len(item["errors"])
            report_rows.append({**item, "result": "skipped"})
            continue
        payload = item["payload"]
        existing = _find_existing_product(db, current_user.company_id, payload, validation["duplicate_keys"])
        if existing and mode == "create_only":
            result["skipped"] += 1
            report_rows.append({**item, "result": "skipped_existing"})
            continue
        if not existing and mode == "update_only":
            result["skipped"] += 1
            report_rows.append({**item, "result": "skipped_new"})
            continue

        supplier_link = payload.get("supplier_links", [None])[0] if payload.get("supplier_links") else None
        if supplier_link and supplier_link.get("supplier_name"):
            supplier = db.query(Counterparty).filter(
                Counterparty.company_id == current_user.company_id,
                Counterparty.is_supplier == True,
                Counterparty.name.ilike(supplier_link["supplier_name"])
            ).first()
            if not supplier and create_missing_suppliers:
                supplier = Counterparty(
                    company_id=current_user.company_id,
                    name=supplier_link["supplier_name"],
                    is_customer=False,
                    is_supplier=True,
                    is_active=True,
                )
                db.add(supplier)
                db.flush()
            if supplier:
                supplier_link["supplier_id"] = str(supplier.id)

        if existing:
            for field, value in payload.items():
                if field == "supplier_links" and value:
                    current_links = existing.supplier_links or []
                    existing.supplier_links = current_links + [link for link in value if link.get("order_url") or link.get("supplier_sku") or link.get("supplier_name")]
                elif field == "variant_config" and value:
                    current_config = existing.variant_config if isinstance(existing.variant_config, dict) else {}
                    current_config["import_meta"] = value.get("import_meta", {})
                    existing.variant_config = current_config
                elif value is not None:
                    setattr(existing, field, value)
            result["updated"] += 1
            report_rows.append({**item, "result": "updated"})
        else:
            product = Product(**payload, company_id=current_user.company_id)
            db.add(product)
            result["created"] += 1
            report_rows.append({**item, "result": "created"})
      except Exception as exc:
        result["skipped"] += 1
        result["errors"] += 1
        report_rows.append({**item, "result": "error", "errors": item.get("errors", []) + [str(exc)]})

    db.commit()
    report_id = str(uuid.uuid4())
    IMPORT_REPORTS[report_id] = {"created_at": datetime.utcnow().isoformat(), "result": result, "rows": report_rows}
    return {"report_id": report_id, **result}


def _build_template_xlsx():
    headers = [field["label"] for field in IMPORT_FIELDS]
    example = [
        "Профіль 20x20x1,2", "PRF-20-12", "INT-001", "4820000000001", "MATERIAL", "Матеріал", "м",
        "Металевий профіль для виробництва", "Активний", "Так", "3000", "20", "20", "1.2", "120", "95",
        "UAH", "Альтабез", "ALT-20", "https://supplier.example/product/20", "Сторінка товару", "Колір=чорний; Товщина=1.2",
    ]

    def sheet_xml():
        rows = []
        for r_idx, row in enumerate([headers, example], start=1):
            cells = []
            for c_idx, value in enumerate(row, start=1):
                col = ""
                n = c_idx
                while n:
                    n, rem = divmod(n - 1, 26)
                    col = chr(65 + rem) + col
                cells.append(f'<c r="{col}{r_idx}" t="inlineStr"><is><t>{str(value)}</t></is></c>')
            rows.append(f'<row r="{r_idx}">{"".join(cells)}</row>')
        return f'<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>{"".join(rows)}</sheetData></worksheet>'

    bio = BytesIO()
    with zipfile.ZipFile(bio, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
        zf.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        zf.writestr("xl/workbook.xml", '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Номенклатура" sheetId="1" r:id="rId1"/></sheets></workbook>')
        zf.writestr("xl/_rels/workbook.xml.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>')
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml())
    bio.seek(0)
    return bio


@router.get("/nomenclature/import/template")
async def download_nomenclature_import_template(
    current_user: User = Depends(get_current_active_user),
):
    bio = _build_template_xlsx()
    return StreamingResponse(
        bio,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="nomenclature_import_template.xlsx"'},
    )


@router.get("/nomenclature/import/report/{report_id}")
async def download_nomenclature_import_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user),
):
    report = IMPORT_REPORTS.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Звіт імпорту не знайдено")
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Рядок", "Назва", "Артикул", "Результат", "Помилки", "Попередження"])
    for row in report["rows"]:
        writer.writerow([
            row.get("row_number"),
            row.get("name"),
            row.get("sku"),
            row.get("result"),
            "; ".join(row.get("errors") or []),
            "; ".join(row.get("warnings") or []),
        ])
    return Response(
        content=output.getvalue().encode("utf-8-sig"),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="nomenclature_import_report_{report_id}.csv"'},
    )

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

@router.post("/products/bulk-update")
@router.post("/products/bulk_update")
async def bulk_update_products(
    body: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    ids = body.get("ids", [])
    updates = body.get("updates", {})
    if not ids or not updates:
        return {"updated": 0}
    
    # Allowed fields for bulk update
    allowed_fields = {"category", "unit_of_measure", "is_active"}
    clean_updates = {k: v for k, v in updates.items() if k in allowed_fields}
    
    # Map status to is_active if present
    if "status" in updates:
        clean_updates["is_active"] = updates["status"] == "active"

    if not clean_updates:
        return {"updated": 0}

    query = db.query(Product).filter(
        Product.id.in_(ids),
        Product.company_id == current_user.company_id
    )
    
    count = query.update(clean_updates, synchronize_session=False)
    db.commit()
    return {"updated": count}

@router.post("/products/bulk-delete")
@router.post("/products/bulk_delete")
async def bulk_delete_products(
    body: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    ids = body.get("ids", [])
    if not ids:
        return {"deleted": 0}
    
    query = db.query(Product).filter(
        Product.id.in_(ids),
        Product.company_id == current_user.company_id
    )
    
    count = query.update({"is_deleted": True}, synchronize_session=False)
    db.commit()
    return {"deleted": count}

@router.post("/products/bulk-update-prices")
@router.post("/products/bulk_update_prices")
async def bulk_update_prices(
    body: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    ids = body.get("ids", [])
    adj_type = body.get("type") # 'percentage' or 'fixed'
    operation = body.get("operation") # 'increase' or 'decrease'
    value = body.get("value", 0)
    
    if not ids or value <= 0:
        return {"updated": 0}
    
    products = db.query(Product).filter(
        Product.id.in_(ids),
        Product.company_id == current_user.company_id
    ).all()
    
    count = 0
    for p in products:
        current_price = p.price or Decimal("0.00")
        adjustment = Decimal(str(value))
        
        if adj_type == 'percentage':
            change = (current_price * adjustment) / Decimal("100")
        else:
            change = adjustment
            
        if operation == 'increase':
            p.price = current_price + change
        else:
            p.price = max(Decimal("0.00"), current_price - change)
        count += 1
        
    db.commit()
    return {"updated": count}

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
