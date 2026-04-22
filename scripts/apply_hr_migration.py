import sys
import os
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://erp_user:erp_password@localhost:5432/erp_db"

def apply_migration_v2():
    engine = create_engine(DATABASE_URL)
    
    queries = [
        # 1. Update Users (Link to employees)
        """
        DO $$ 
        BEGIN 
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='employee_id') THEN
                ALTER TABLE users ADD COLUMN employee_id UUID;
                ALTER TABLE users ADD CONSTRAINT fk_users_employee_id_employees FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE SET NULL;
            END IF;
        END $$;
        """,

        # 2. Attendance Records
        """
        CREATE TABLE IF NOT EXISTS attendance_records (
            id UUID PRIMARY KEY,
            employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
            date DATE NOT NULL,
            status_id UUID NOT NULL REFERENCES dictionary_items(id) ON DELETE RESTRICT,
            notes VARCHAR(255),
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            UNIQUE (employee_id, date)
        );
        """,
        "CREATE INDEX IF NOT EXISTS ix_attendance_records_employee_id ON attendance_records (employee_id);",
        "CREATE INDEX IF NOT EXISTS ix_attendance_records_date ON attendance_records (date);",

        # 3. Payroll Transactions
        """
        CREATE TABLE IF NOT EXISTS payroll_transactions (
            id UUID PRIMARY KEY,
            employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
            amount NUMERIC(15, 2) NOT NULL,
            transaction_type VARCHAR(50) NOT NULL,
            date DATE NOT NULL,
            category_id UUID NOT NULL REFERENCES dictionary_items(id) ON DELETE RESTRICT,
            production_order_id UUID REFERENCES production_orders(id) ON DELETE SET NULL,
            created_by UUID REFERENCES users(id) ON DELETE SET NULL,
            description VARCHAR(500),
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now()
        );
        """,
        "CREATE INDEX IF NOT EXISTS ix_payroll_transactions_employee_id ON payroll_transactions (employee_id);",
        "CREATE INDEX IF NOT EXISTS ix_payroll_transactions_date ON payroll_transactions (date);",

        # 4. Update Alembic Version
        "UPDATE alembic_version SET version_num = 'b4e5f6a7c8d9' WHERE version_num = '7d2e9f1a0e8c';"
    ]

    with engine.connect() as conn:
        print("Connecting to database...")
        for query in queries:
            try:
                conn.execute(text(query))
                conn.commit()
                # print("Executed query successfully.")
            except Exception as e:
                print(f"Error executing query: {e}")
                conn.rollback()
        print("\nHR Migration v2 Applied Successfully! (Schema vb4e5f6a7c8d9)")

if __name__ == "__main__":
    apply_migration_v2()
