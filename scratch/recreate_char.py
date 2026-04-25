
import sys
import os
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Set up DB connection
DATABASE_URL = "postgresql://erp_user:erp_password@localhost:5432/erp_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # 1. Find the characteristic
    char_name = "Розмір ДСП"
    res = db.execute(text("SELECT id FROM attributes WHERE name = :name"), {"name": char_name}).first()
    
    if res:
        char_id = res[0]
        print(f"Found existing characteristic: {char_id}")
        
        # Delete related records
        db.execute(text("DELETE FROM product_attribute_values WHERE attribute_id = :id"), {"id": char_id})
        db.execute(text("DELETE FROM attribute_options WHERE attribute_id = :id"), {"id": char_id})
        db.execute(text("DELETE FROM attributes WHERE id = :id"), {"id": char_id})
        db.commit()
        print("Deleted existing characteristic and related records.")
    else:
        print("Characteristic not found, skipping delete.")

    # 2. Find Category "ДСП Матеріали"
    cat_res = db.execute(text("SELECT id FROM product_categories WHERE name = 'ДСП Матеріали'")).first()
    if not cat_res:
        # Try finding by partial name or use first category
        cat_res = db.execute(text("SELECT id FROM product_categories LIMIT 1")).first()
        print(f"Category 'ДСП Матеріали' not found, using category ID: {cat_res[0] if cat_res else 'None'}")
    
    cat_id = cat_res[0] if cat_res else None

    # 3. Create new characteristic
    new_id = str(uuid.uuid4())
    db.execute(text("""
        INSERT INTO attributes (id, name, type, category_id, generates_sku, allow_custom_value, affects_bom_dimensions, dimension_format, is_active)
        VALUES (:id, :name, 'DIMENSIONS', :cat_id, false, false, false, '{width}×{height}', true)
    """), {
        "id": new_id,
        "name": char_name,
        "cat_id": cat_id
    })
    db.commit()
    print(f"Created new characteristic: {new_id}")

    # 4. Find Product "ДСП Сонома 18мм"
    prod_name = "ДСП Сонома 18мм"
    prod_res = db.execute(text("SELECT id FROM products WHERE name = :name"), {"name": prod_name}).first()
    
    if prod_res:
        prod_id = prod_res[0]
        print(f"Found product: {prod_id}")
        
        # Assign characteristic to product (if not already via category)
        # Check if product_attributes entry exists
        db.execute(text("""
            INSERT INTO product_attributes (product_id, attribute_id)
            VALUES (:pid, :aid)
            ON CONFLICT DO NOTHING
        """), {"pid": prod_id, "aid": new_id})
        
        # Add value 600x320
        # Create attribute option first
        opt_id = str(uuid.uuid4())
        db.execute(text("""
            INSERT INTO attribute_options (id, attribute_id, value, width, height)
            VALUES (:id, :aid, '600×320', 600, 320)
        """), {"id": opt_id, "aid": new_id})
        
        # Link value to product
        db.execute(text("""
            INSERT INTO product_attribute_values (id, product_id, attribute_id, option_id, text_value)
            VALUES (:vid, :pid, :aid, :oid, '600×320')
        """), {
            "vid": str(uuid.uuid4()),
            "pid": prod_id,
            "aid": new_id,
            "oid": opt_id
        })
        db.commit()
        print("Assigned 600x320 to product.")
    else:
        print(f"Product '{prod_name}' not found.")

except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
