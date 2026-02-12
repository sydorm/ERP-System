"""
Create sample data for development/testing
"""
from app.db.session import SessionLocal
from app.models import Company, User, Warehouse, Product, Counterparty
from passlib.context import CryptContext
from datetime import datetime
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_sample_data():
    """Create sample data for development"""
    db = SessionLocal()
    
    try:
        # 1. Create Company
        company = Company(
            id=uuid.uuid4(),
            name="Демо ФОП",
            legal_name="ФОП Іваненко Іван Іванович",
            tax_id="1234567890",
            company_type="FOP",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(company)
        db.flush()
        
        # 2. Create Admin User
        admin_user = User(
            id=uuid.uuid4(),
            email="admin@demo.com",
            hashed_password=pwd_context.hash("admin123"),
            first_name="Іван",
            last_name="Іваненко",
            is_active=True,
            is_superuser=True,
            company_id=company.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(admin_user)
        
        # 3. Create Warehouse
        warehouse = Warehouse(
            id=uuid.uuid4(),
            name="Головний склад",
            address="м. Київ, вул. Хрещатик, 1",
            is_default=True,
            is_active=True,
            company_id=company.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(warehouse)
        
        # 4. Create Sample Products
        products = [
            Product(
                id=uuid.uuid4(),
                code="PROD-001",
                name="Ноутбук Dell XPS 15",
                description="Потужний ноутбук для професіоналів",
                category="Електроніка",
                unit_of_measure="шт",
                price=45000.00,
                cost=38000.00,
                is_active=True,
                company_id=company.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            Product(
                id=uuid.uuid4(),
                code="PROD-002",
                name="iPhone 15 Pro",
                description="Смартфон Apple iPhone 15 Pro 256GB",
                category="Електроніка",
                unit_of_measure="шт",
                price=38000.00,
                cost=32000.00,
                is_active=True,
                company_id=company.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            Product(
                id=uuid.uuid4(),
                code="PROD-003",
                name="Миша Logitech MX Master 3",
                description="Бездротова миша для продуктивності",
                category="Аксесуари",
                unit_of_measure="шт",
                price=3200.00,
                cost=2500.00,
                is_active=True,
                company_id=company.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        for product in products:
            db.add(product)
        
        # 5. Create Sample Counterparties
        counterparties = [
            Counterparty(
                id=uuid.uuid4(),
                name="ТОВ Електроніка Плюс",
                legal_name="Товариство з обмеженою відповідальністю 'Електроніка Плюс'",
                tax_id="12345678",
                is_customer=True,
                is_supplier=False,
                phone="+380501234567",
                email="info@electronica.ua",
                address="м. Київ, вул. Промислова, 10",
                is_active=True,
                company_id=company.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            Counterparty(
                id=uuid.uuid4(),
                name="ФОП Петренко П.П.",
                legal_name="Фізична особа підприємець Петренко Петро Петрович",
                tax_id="9876543210",
                is_customer=False,
                is_supplier=True,
                phone="+380679876543",
                email="petrenko@supplier.ua",
                address="м. Львів, вул. Торгова, 5",
                is_active=True,
                company_id=company.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        for counterparty in counterparties:
            db.add(counterparty)
        
        db.commit()
        print("✓ Sample data created successfully!")
        print(f"\nLogin credentials:")
        print(f"  Email: admin@demo.com")
        print(f"  Password: admin123")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error creating sample data: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("Creating sample data...")
    create_sample_data()
