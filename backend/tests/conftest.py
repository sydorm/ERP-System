import pytest
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models import Company, User, Warehouse, Product

# Use SQLite in-memory for fast unit testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    return engine

@pytest.fixture(scope="function")
def db(engine):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def test_company(db):
    company = Company(name="Test Company", edrpou="12345678")
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

@pytest.fixture
def test_warehouse(db, test_company):
    warehouse = Warehouse(name="Main Warehouse", company_id=test_company.id)
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return warehouse

@pytest.fixture
def test_product(db, test_company):
    product = Product(sku="TEST-001", name="Test Product", company_id=test_company.id)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
