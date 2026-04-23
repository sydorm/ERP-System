import sys
import os
from sqlalchemy import create_engine, inspect

# Add backend to path
sys.path.append(os.getcwd())

# Simple DB check
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
engine = create_engine(DATABASE_URL)

def check_structure():
    inspector = inspect(engine)
    if 'production_orders' not in inspector.get_table_names():
        print("ERROR: Table 'production_orders' not found!")
        return
    
    columns = [c['name'] for c in inspector.get_columns('production_orders')]
    print(f"Columns in 'production_orders': {', '.join(columns)}")
    
    # Check specifically for troublesome columns
    needed = ['order_date', 'order_number', 'client_id', 'priority', 'source_type']
    missing = [c for c in needed if c not in columns]
    if missing:
        print(f"MISSING COLUMNS: {missing}")
    else:
        print("SUCCESS: All required columns are present.")

if __name__ == "__main__":
    try:
        check_structure()
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
