import os
import uuid
from sqlalchemy import create_engine, text

import os
import sqlalchemy
from sqlalchemy import create_engine, text

# Get DB URL from environment (standard for Docker setup)
DB_URL = os.getenv("DATABASE_URL", "postgresql://erp_user:erp_password@db:5432/erp_db")

engine = create_engine(DB_URL)

def run_sql(sql, params=None):
    with engine.connect() as conn:
        conn.execute(text(sql), params)
        conn.commit()

def recovery():
    print("Starting emergency recovery...")
    
    # 1. Add employee_id to users if missing
    print("Checking users table...")
    try:
        run_sql("ALTER TABLE users ADD COLUMN IF NOT EXISTS employee_id UUID")
        print("OK: users.employee_id check passed")
    except Exception as e:
        print(f"Error updating users: {e}")

    # 2. Ensure departments table exists (base for HR)
    print("Checking departments table...")
    run_sql("""
    CREATE TABLE IF NOT EXISTS departments (
        id UUID PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        manager_id UUID,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
    )
    """)

    # 3. Ensure employees table exists
    print("Checking employees table...")
    run_sql("""
    CREATE TABLE IF NOT EXISTS employees (
        id UUID PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        department_id UUID REFERENCES departments(id),
        position VARCHAR(255),
        status_id UUID,
        hire_date DATE,
        phone VARCHAR(50),
        email VARCHAR(255),
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
    )
    """)

    # 4. CRITICAL: Check if production_orders exists (to satisfy FKs)
    # If not exists, we create a stub to allow the app to work
    print("Checking production_orders table...")
    run_sql("""
    CREATE TABLE IF NOT EXISTS production_orders (
        id UUID PRIMARY KEY,
        order_number VARCHAR(50),
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
    )
    """)

    # 5. Create Attendance and Payroll tables
    print("Checking HR v2 tables...")
    run_sql("""
    CREATE TABLE IF NOT EXISTS attendance_records (
        id UUID PRIMARY KEY,
        employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
        date DATE NOT NULL,
        status_id UUID NOT NULL,
        hours NUMERIC(5, 2),
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
        UNIQUE(employee_id, date)
    )
    """)

    run_sql("""
    CREATE TABLE IF NOT EXISTS payroll_transactions (
        id UUID PRIMARY KEY,
        employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
        amount NUMERIC(15, 2) NOT NULL,
        transaction_type VARCHAR(50) NOT NULL,
        date DATE NOT NULL,
        category_id UUID NOT NULL,
        production_order_id UUID REFERENCES production_orders(id) ON DELETE SET NULL,
        created_by UUID,
        description VARCHAR(500),
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
    )
    """)

    print("SUCCESS: Recovery script finished. Try to reload the page.")

if __name__ == "__main__":
    recovery()
