
from app.db.session import SessionLocal
from app.models import DictionaryItem, Company, User

db = SessionLocal()
try:
    # Get first user to find their company_id
    user = db.query(User).first()
    if not user:
        print("No user found")
    else:
        print(f"Checking for User: {user.email}, Company ID: {user.company_id}")
        
        # Get all dictionary items for this company
        items = db.query(DictionaryItem).filter(DictionaryItem.company_id == user.company_id).all()
        print(f"Total dictionary items for company: {len(items)}")
        
        categories = set(item.category for item in items)
        print(f"Categories found: {categories}")
        
        for cat in categories:
            cat_items = [i for i in items if i.category == cat]
            print(f"\nCategory: {cat} ({len(cat_items)} items)")
            for item in cat_items:
                print(f"  - Code: {item.code}, Name: {item.name}, Active: {item.is_active}")
finally:
    db.close()
