import sqlalchemy as sa
from app.core.config import settings
from app.models.order import Order
from app.schemas.order import OrderResponse
from sqlalchemy.orm import Session
import traceback
from uuid import UUID

def debug_order(order_uuid_str):
    print(f"Connecting to: {settings.DATABASE_URL}")
    engine = sa.create_engine(settings.DATABASE_URL)
    
    # 1. Check table columns
    try:
        inspector = sa.inspect(engine)
        columns = [c['name'] for c in inspector.get_columns('orders')]
        print(f"Columns in 'orders' table: {columns}")
    except Exception as e:
        print(f"Failed to inspect columns: {e}")

    # 2. Try to fetch and serialize order
    try:
        with Session(engine) as session:
            oid = UUID(order_uuid_str)
            order = session.query(Order).filter(Order.id == oid).first()
            if not order:
                print(f"Order {order_uuid_str} not found in DB")
                return
            
            print(f"Order found: {order.order_number}")
            
            # Try to serialize
            try:
                resp = OrderResponse.model_validate(order)
                print("Serialization successful!")
            except Exception as e:
                print(f"Serialization failed: {e}")
                traceback.print_exc()
                
    except Exception as e:
        print(f"Database query failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    # From screenshot: http://.../crm/orders/8f89b4bc-0856-475f-a4a4-35c1634ea030
    debug_order("8f89b4bc-0856-475f-a4a4-35c1634ea030")
