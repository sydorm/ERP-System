from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://erp_user:erp_password@localhost:5432/erp_db"
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    try:
        # Check if columns exist
        res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'attribute_options'"))
        cols = [r[0] for r in res]
        print(f"Columns in attribute_options: {cols}")
        
        if 'width' not in cols:
            print("Missing width column. Adding manually...")
            conn.execute(text("ALTER TABLE attribute_options ADD COLUMN width INTEGER"))
            conn.execute(text("ALTER TABLE attribute_options ADD COLUMN height INTEGER"))
            conn.execute(text("COMMIT"))
            print("Columns added successfully.")
        else:
            print("Columns already exist.")
            
    except Exception as e:
        print(f"Error: {e}")
