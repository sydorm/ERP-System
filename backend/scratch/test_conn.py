import psycopg2
from app.core.config import settings

try:
    print(f"Connecting to: {settings.DATABASE_URL}")
    conn = psycopg2.connect(settings.DATABASE_URL)
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
    import traceback
    traceback.print_exc()
