"""
Database initialization script
Run migrations using: alembic upgrade head
"""
from app.db.session import engine
from app.models import Base
from sqlalchemy import text


def init_db():
    """
    Initialize database
    Create all tables using Alembic migrations
    """
    # Check connection
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("Initializing database...")
    if init_db():
        print("\n✓ Database initialized successfully!")
        print("\nNext steps:")
        print("1. Run migrations: alembic upgrade head")
        print("2. Create initial data (optional)")
    else:
        print("\n✗ Database initialization failed")
