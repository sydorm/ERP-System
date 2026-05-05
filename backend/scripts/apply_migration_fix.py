import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import SessionLocal
from sqlalchemy import text

def apply_fix():
    db = SessionLocal()
    try:
        print("Checking for missing columns in 'attributes' and 'product_attributes'...")
        
        columns_to_add_attr = [
            ("show_in_purchase_receipt", "BOOLEAN DEFAULT TRUE"),
            ("show_in_purchase_order", "BOOLEAN DEFAULT TRUE"),
            ("show_in_sales_order", "BOOLEAN DEFAULT TRUE"),
            ("required", "BOOLEAN DEFAULT FALSE"),
            ("track_stock_separately", "BOOLEAN DEFAULT TRUE"),
            ("block_if_empty", "BOOLEAN DEFAULT FALSE")
        ]
        
        columns_to_add_prod_attr = columns_to_add_attr + [
            ("affects_sku", "BOOLEAN DEFAULT TRUE")
        ]
        
        for col, type_def in columns_to_add_attr:
            try:
                db.execute(text(f"ALTER TABLE attributes ADD COLUMN {col} {type_def}"))
                print(f"Added {col} to attributes")
            except Exception as e:
                print(f"Column {col} might already exist in attributes")
        
        for col, type_def in columns_to_add_prod_attr:
            try:
                db.execute(text(f"ALTER TABLE product_attributes ADD COLUMN {col} {type_def}"))
                print(f"Added {col} to product_attributes")
            except Exception as e:
                print(f"Column {col} might already exist in product_attributes")
        
        db.commit()
        print("Done!")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    apply_fix()
