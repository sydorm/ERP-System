import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

query = text("""
    SELECT 
        v.id as variant_id, 
        v.sku, 
        p.name as product_name,
        vv.text_value,
        a.name as attr_name,
        a.type as attr_type
    FROM product_variants v
    JOIN products p ON v.product_id = p.id
    LEFT JOIN variant_values vv ON vv.variant_id = v.id
    LEFT JOIN attributes a ON vv.attribute_id = a.id
    WHERE p.name LIKE :pname
""")

with engine.connect() as conn:
    result = conn.execute(query, {"pname": "%Сонома%"})
    rows = result.fetchall()
    
    if not rows:
        print("Варіантів для 'Сонома' не знайдено.")
    else:
        print(f"{'SKU':<15} | {'Product':<25} | {'Attr':<15} | {'Value':<15} | {'Type'}")
        print("-" * 85)
        for row in rows:
            print(f"{str(row.sku):<15} | {str(row.product_name):<25} | {str(row.attr_name):<15} | {str(row.text_value):<15} | {str(row.attr_type)}")
