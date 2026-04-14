import os
import sys

# Add backend to sys.path
sys.path.append(os.path.abspath("g:\\Моделювання\\R1\\backend"))

from sqlalchemy.orm import Session, joinedload
from app.db.session import SessionLocal
from app.models.specification import ProductSpecification, SpecificationItem
from app.models.product import Product
from uuid import UUID

def test_get_specifications():
    db = SessionLocal()
    try:
        # Get first product ID
        product = db.query(Product).first()
        if not product:
            print("No products found in database")
            return
        
        product_id = product.id
        print(f"Testing for product_id: {product_id}")
        
        specs = db.query(ProductSpecification).options(
            joinedload(ProductSpecification.items).options(
                joinedload(SpecificationItem.component)
            )
        ).filter(
            ProductSpecification.product_id == product_id
        ).order_by(ProductSpecification.created_at.desc()).all()
        
        print(f"Success! Found {len(specs)} specifications")
        for spec in specs:
            print(f"Spec: {spec.name}, Items: {len(spec.items)}")
            
    except Exception as e:
        print(f"Error caught: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_get_specifications()
