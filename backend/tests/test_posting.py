import pytest
from uuid import uuid4
from app.services.posting_service import PostingService, PostingEntry
from app.models import AccumulationRegister, RegisterType

def test_posting_stock_movement(db, test_company, test_warehouse, test_product):
    # 1. Define document
    doc_type = "TEST_DOC"
    doc_id = uuid4()
    
    # 2. Define entries (e.g., +10 to stock)
    entries = [
        PostingEntry(
            register_type=RegisterType.STOCK,
            product_id=test_product.id,
            warehouse_id=test_warehouse.id,
            quantity=10,
            notes="Initial stock"
        )
    ]
    
    # 3. Post document
    PostingService.post_document(
        db, test_company.id, doc_type, doc_id, entries
    )
    
    # 4. Verify register
    records = db.query(AccumulationRegister).filter(
        AccumulationRegister.document_id == doc_id
    ).all()
    
    assert len(records) == 1
    assert records[0].quantity == 10
    assert records[0].product_id == test_product.id
    assert records[0].register_type == RegisterType.STOCK

def test_unposting_clears_records(db, test_company, test_warehouse, test_product):
    doc_id = uuid4()
    entries = [
        PostingEntry(RegisterType.STOCK, quantity=5, product_id=test_product.id)
    ]
    
    PostingService.post_document(db, test_company.id, "TEST", doc_id, entries)
    assert db.query(AccumulationRegister).filter(AccumulationRegister.document_id == doc_id).count() == 1
    
    PostingService.unpost_document(db, test_company.id, "TEST", doc_id)
    assert db.query(AccumulationRegister).filter(AccumulationRegister.document_id == doc_id).count() == 0

def test_reposting_updates_records(db, test_company, test_product):
    doc_id = uuid4()
    
    # First post
    PostingService.post_document(db, test_company.id, "TEST", doc_id, [
        PostingEntry(RegisterType.STOCK, quantity=10, product_id=test_product.id)
    ])
    
    # Second post (idempotency check)
    PostingService.post_document(db, test_company.id, "TEST", doc_id, [
        PostingEntry(RegisterType.STOCK, quantity=25, product_id=test_product.id)
    ])
    
    records = db.query(AccumulationRegister).filter(AccumulationRegister.document_id == doc_id).all()
    assert len(records) == 1
    assert records[0].quantity == 25
