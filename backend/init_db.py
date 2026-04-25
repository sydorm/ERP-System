import sys
import os
import logging
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import engine, SessionLocal
from app.models import Base

def init_db():
    try:
        logger.info("🚀 Starting database initialization...")
        # 1. Create tables
        Base.metadata.create_all(bind=engine)
        
        # 2. Force add columns that might be missing due to schema updates
        db = SessionLocal()
        try:
            logger.info("🛠 Running hot-fixes for missing columns...")
            # Fix Company table
            db.execute(text("ALTER TABLE companies ADD COLUMN IF NOT EXISTS tax_id VARCHAR(20);"))
            # Fix ProductAttribute table
            db.execute(text("ALTER TABLE product_attributes ADD COLUMN IF NOT EXISTS option_id UUID;"))
            db.execute(text("ALTER TABLE product_attributes ADD COLUMN IF NOT EXISTS text_value VARCHAR(500);"))
            db.commit()
            logger.info("✅ Hot-fixes applied!")
        finally:
            db.close()
            
        logger.info("✅ Database initialization complete!")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    init_db()
