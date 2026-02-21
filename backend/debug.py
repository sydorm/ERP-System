import asyncio
from app.db.session import SessionLocal
from app.models.document_sequence import DocumentSequence
from app.schemas.document_sequence import DocumentSequenceResponse

def test():
    db = SessionLocal()
    try:
        seq = DocumentSequence(id=1, document_type="order", prefix="ORD-", next_number=1, padding=5)
        res = DocumentSequenceResponse.model_validate(seq)
        print("DocumentSequenceResponse works:", res.model_dump())
    except Exception as e:
        print("DocumentSequenceResponse ERROR:", e)

    from app.models.specification import ProductSpecification, SpecificationItem
    from app.models.product import Product
    from app.schemas.specification import ProductSpecificationResponse
    try:
        prod = Product(id="123e4567-e89b-12d3-a456-426614174000", sku="TEST", name="TEST", company_id="123e4567-e89b-12d3-a456-426614174000")
        spec = ProductSpecification(id="123e4567-e89b-12d3-a456-426614174001", product_id=prod.id, name="Test spec", notes="test")
        item = SpecificationItem(id="123e4567-e89b-12d3-a456-426614174002", specification_id=spec.id, component_id=prod.id, quantity=1.0)
        item.component = prod
        spec.items = [item]
        res = ProductSpecificationResponse.from_orm(spec)
        print("ProductSpecificationResponse works:", res.dict())
    except Exception as e:
        print("ProductSpecificationResponse ERROR:", e)

if __name__ == "__main__":
    test()
