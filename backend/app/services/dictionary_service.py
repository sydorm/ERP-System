from sqlalchemy.orm import Session
from uuid import UUID
from app.models.dictionary import DictionaryItem

DEFAULT_DICTIONARIES = {
    "UOM": [
        {"code": "pcs", "name": "Штука", "sort_order": 1, "is_fixed": True},
        {"code": "kg", "name": "Кілограм", "sort_order": 2},
        {"code": "m", "name": "Метр", "sort_order": 3},
        {"code": "m2", "name": "М.кв", "sort_order": 4},
        {"code": "m3", "name": "М.куб", "sort_order": 5},
        {"code": "l", "name": "Літр", "sort_order": 6},
        {"code": "pack", "name": "Упаковка", "sort_order": 7},
        {"code": "set", "name": "Комплект", "sort_order": 8},
    ],
    "PRODUCT_CATEGORY": [
        {"code": "materials", "name": "Матеріали", "sort_order": 1},
        {"code": "hardware", "name": "Фурнітура", "sort_order": 2},
        {"code": "services", "name": "Послуги", "sort_order": 3},
    ],
    "ORDER_STATUS": [
        {"code": "new", "name": "Новий", "color": "info", "sort_order": 1, "is_fixed": True},
        {"code": "processing", "name": "В роботі", "color": "warning", "sort_order": 2, "is_fixed": True},
        {"code": "shipped", "name": "Відвантажено", "color": "primary", "sort_order": 3, "is_fixed": True},
        {"code": "completed", "name": "Виконано", "color": "success", "sort_order": 4, "is_fixed": True},
        {"code": "cancelled", "name": "Скасовано", "color": "danger", "sort_order": 5, "is_fixed": True},
    ],
    "PAYMENT_METHOD": [
        {"code": "cash", "name": "Готівка", "sort_order": 1},
        {"code": "card", "name": "Картка", "sort_order": 2},
        {"code": "bank_transfer", "name": "Безготівковий (Рахунок)", "sort_order": 3},
    ],
    "CURRENCY": [
        {"code": "UAH", "name": "Гривня", "sort_order": 1, "is_fixed": True},
        {"code": "USD", "name": "Долар США", "sort_order": 2},
        {"code": "EUR", "name": "Євро", "sort_order": 3},
    ]
}

def seed_company_dictionaries(db: Session, company_id: UUID):
    """
    Populate default dictionaries for a new company
    """
    for category, items in DEFAULT_DICTIONARIES.items():
        for item in items:
            db_item = DictionaryItem(
                company_id=company_id,
                category=category,
                code=item["code"],
                name=item["name"],
                color=item.get("color"),
                sort_order=item.get("sort_order", 0),
                is_fixed=item.get("is_fixed", False),
                is_active=True
            )
            db.add(db_item)
    
    db.commit()
