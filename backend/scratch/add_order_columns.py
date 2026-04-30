import sys
import os
from sqlalchemy import text

# Add the backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app.db.session import SessionLocal
    print(f"SessionLocal imported successfully from {backend_dir}")
except ImportError as e:
    print(f"ImportError: {e}. Current sys.path: {sys.path}")
    sys.exit(1)

def add_columns():
    db = SessionLocal()
    try:
        print("Додаю нові поля для контактів у таблицю orders...")
        # Add next_contact_channel column
        db.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS next_contact_channel VARCHAR(50);"))
        # Add next_contact_comment column
        db.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS next_contact_comment TEXT;"))
        db.commit()
        print("✅ Колонки next_contact_channel та next_contact_comment успішно додані!")
    except Exception as e:
        print(f"❌ Помилка при оновленні: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_columns()
