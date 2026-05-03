import sys
import os
from uuid import UUID

# Add backend to path
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.models import Product, ProductVariant, VariantValue, AccumulationRegister, Attribute, AttributeOption

def debug_product_stock(product_id_str):
    db = SessionLocal()
    pid = UUID(product_id_str)
    
    print(f"--- Debugging Product: {product_id_str} ---")
    
    product = db.query(Product).filter(Product.id == pid).first()
    if not product:
        print("Product not found!")
        return
        
    print(f"Product Name: {product.name}, SKU: {product.sku}")
    
    print("\n--- Variants ---")
    variants = db.query(ProductVariant).filter(ProductVariant.product_id == pid).all()
    for v in variants:
        print(f"Variant ID: {v.id}, SKU: {v.sku}, Active: {v.is_active}")
        vals = db.query(VariantValue).filter(VariantValue.variant_id == v.id).all()
        for vv in vals:
            attr = db.query(Attribute).filter(Attribute.id == vv.attribute_id).first()
            attr_name = attr.name if attr else "Unknown"
            val_text = vv.text_value or ""
            if vv.option_id:
                opt = db.query(AttributeOption).filter(AttributeOption.id == vv.option_id).first()
                val_text = opt.value if opt else f"Option({vv.option_id})"
            print(f"  - {attr_name}: {val_text}")
            
    print("\n--- Stock (AccumulationRegister) ---")
    stocks = db.query(AccumulationRegister).filter(
        AccumulationRegister.product_id == pid,
        AccumulationRegister.register_type == 'stock'
    ).all()
    for s in stocks:
        print(f"Warehouse ID: {s.warehouse_id}, Variant ID: {s.variant_id}, Qty: {s.quantity}")

if __name__ == "__main__":
    debug_product_stock("29c5611f-c8fc-4e2b-aa3b-61ca454ddaff")
