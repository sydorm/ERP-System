import sys
import os
from sqlalchemy import text

# Add the parent directory to sys.path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal

def fix():
    db = SessionLocal()
    try:
        print("Оновлюю базу даних (додаю поля для характеристик)...")
        # Add option_id column
        db.execute(text("ALTER TABLE product_attributes ADD COLUMN IF NOT EXISTS option_id UUID;"))
        # Add text_value column
        db.execute(text("ALTER TABLE product_attributes ADD COLUMN IF NOT EXISTS text_value VARCHAR(500);"))
        db.commit()
        print("✅ База даних успішно оновлена! Поля option_id та text_value додані.")
    except Exception as e:
        print(f"❌ Помилка при оновленні: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix()
