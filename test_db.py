import sys
import os

sys.path.insert(0, os.path.abspath('backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.order import OrderStatus, Order
from app.models.company import Company
from app.db.session import engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Let's try to see what SQLAlchemy compiles.
    from sqlalchemy.schema import CreateTable
    print(CreateTable(Order.__table__).compile(engine))
    
    # Try inserting a dummy order or see the enum type
    c = db.query(Company).first()
    if c:
        print("Company found:", c.id)
    
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()
