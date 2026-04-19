import sqlalchemy as sa
from app.core.config import settings

def test_conn():
    print(f"Testing connection to: {settings.DATABASE_URL}")
    try:
        engine = sa.create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            res = conn.execute(sa.text("SELECT 1")).scalar()
            print(f"Success! Result: {res}")
    except Exception as e:
        print(f"Connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_conn()
