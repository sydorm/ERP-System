import psycopg2
dsn = "host=localhost port=5432 user=erp_user password=erp_password dbname=erp_db"
try:
    print(f"Connecting with DSN: {dsn}")
    conn = psycopg2.connect(dsn)
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
    import traceback
    traceback.print_exc()
