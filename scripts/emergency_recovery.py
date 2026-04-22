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
        company_id UUID NOT NULL,
        name VARCHAR(255) NOT NULL,
        head_id UUID,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
    )
    """)
    # Add company_id if it's missed in an existing table
    try:
        run_sql("ALTER TABLE departments ADD COLUMN IF NOT EXISTS company_id UUID")
        run_sql("ALTER TABLE departments ALTER COLUMN company_id SET NOT NULL")
    except: pass

    # 3. Ensure employees table exists
    print("Checking employees table...")
    run_sql("""
    CREATE TABLE IF NOT EXISTS employees (
        id UUID PRIMARY KEY,
        company_id UUID NOT NULL,
        full_name VARCHAR(255) NOT NULL,
        department_id UUID REFERENCES departments(id),
        position VARCHAR(255),
        status_id UUID,
        hire_date DATE,
        birth_date DATE,
        phone VARCHAR(50),
        email VARCHAR(255),
        notes TEXT,
        photo_url VARCHAR(500),
        is_deleted BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
    )
    """)
    try:
        run_sql("ALTER TABLE employees ADD COLUMN IF NOT EXISTS company_id UUID")
        run_sql("ALTER TABLE employees ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE")
        run_sql("UPDATE employees SET is_deleted = FALSE WHERE is_deleted IS NULL")
    except: pass

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

    # 5. Ensure employee_roles table exists
    print("Checking employee_roles table...")
    run_sql("""
    CREATE TABLE IF NOT EXISTS employee_roles (
        id UUID PRIMARY KEY,
        employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
        role_id UUID NOT NULL,
        role_type_id UUID NOT NULL,
        accrual_type_id UUID NOT NULL,
        rate NUMERIC(15, 2) DEFAULT 0.0 NOT NULL,
        is_active BOOLEAN DEFAULT TRUE NOT NULL,
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
    )
    """)

    # 6. Create Attendance and Payroll tables
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
    try:
        run_sql("ALTER TABLE attendance_records ADD COLUMN IF NOT EXISTS notes VARCHAR(255)")
        run_sql("ALTER TABLE attendance_records ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()")
    except: pass

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
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
    )
    """)
    try:
        run_sql("ALTER TABLE payroll_transactions ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()")
    except: pass

    run_sql("""
    CREATE TABLE IF NOT EXISTS production_order_assignments (
        id UUID PRIMARY KEY,
        production_order_id UUID NOT NULL REFERENCES production_orders(id) ON DELETE CASCADE,
        employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
        stage_id UUID NOT NULL,
        quantity NUMERIC(15, 3),
        status_id UUID,
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
    )
    """)
    try:
        run_sql("ALTER TABLE production_order_assignments ADD COLUMN IF NOT EXISTS status_id UUID")
    except: pass

    # 7. Seed Holidays for 2026
    print("Seeding Ukrainian Holidays for 2026...")
    # Get first company id
    with engine.connect() as conn:
        res = conn.execute(text("SELECT id FROM companies LIMIT 1")).fetchone()
        if res:
            comp_id = res[0]
            holidays = [
                ('2026-01-01', 'Новий рік'),
                ('2026-04-12', 'Великдень'),
                ('2026-04-13', 'Великодній понеділок (перенесення)'),
                ('2026-05-01', 'День праці'),
                ('2026-06-28', 'День Конституції України'),
                ('2026-06-29', 'День Конституції (перенесення)'),
                ('2026-08-24', 'День Незалежності України'),
                ('2026-10-01', 'День захисників і захисниць України'),
                ('2026-12-25', 'Різдво Христове')
            ]
            for h_date, h_name in holidays:
                run_sql("""
                INSERT INTO dictionary_items (id, company_id, category, type, code, name, is_fixed, is_active)
                VALUES (:id, :cid, 'HOLIDAY', 'HOLIDAY', :code, :name, true, true)
                ON CONFLICT (id) DO NOTHING
                """, {
                    "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"holiday-2026-{h_date}")),
                    "cid": comp_id,
                    "code": h_date,
                    "name": h_name
                })
            print(f"OK: Holidays for 2026 seeded for company {comp_id}")

    print("SUCCESS: Recovery script finished. Try to reload the page.")

if __name__ == "__main__":
    recovery()
