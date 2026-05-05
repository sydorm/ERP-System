from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models import AccumulationRegister, RegisterType

class PostingEntry:
    """Helper class to define a single register entry"""
    def __init__(
        self,
        register_type: RegisterType,
        quantity: float = 0,
        amount: float = 0,
        product_id: Optional[UUID] = None,
        variant_id: Optional[UUID] = None,
        warehouse_id: Optional[UUID] = None,
        counterparty_id: Optional[UUID] = None,
        bank_account_id: Optional[UUID] = None,
        currency: str = "UAH",
        notes: Optional[str] = None,
        attribute_values: Optional[dict] = None
    ):
        self.register_type = register_type
        self.quantity = quantity
        self.amount = amount
        self.product_id = product_id
        self.variant_id = variant_id
        self.warehouse_id = warehouse_id
        self.counterparty_id = counterparty_id
        self.bank_account_id = bank_account_id
        self.currency = currency
        self.notes = notes
        self.attribute_values = attribute_values

class PostingService:
    @staticmethod
    def post_document(
        db: Session,
        company_id: UUID,
        document_type: str,
        document_id: UUID,
        entries: List[PostingEntry]
    ):
        """
        Create register records for a document.
        Automatically removes previous records for this document to ensure idempotency.
        """
        # 1. Unpost first (idempotency)
        PostingService.unpost_document(db, company_id, document_type, document_id)
        
        # 2. Add new entries
        for entry in entries:
            db_record = AccumulationRegister(
                company_id=company_id,
                register_type=entry.register_type,
                product_id=entry.product_id,
                variant_id=entry.variant_id,
                warehouse_id=entry.warehouse_id,
                counterparty_id=entry.counterparty_id,
                bank_account_id=entry.bank_account_id,
                quantity=entry.quantity,
                amount=entry.amount,
                currency=entry.currency,
                document_type=document_type,
                document_id=document_id,
                notes=entry.notes,
                extra_data={"attribute_values": entry.attribute_values} if entry.attribute_values else None
            )
            db.add(db_record)
        
        db.flush()
        
        # 3. Check for low stock alerts
        # (Usually better to do after commit, but for simplicity and immediate feedback we do it here or via background task)
        # For now, we only check products involved in this posting
        product_ids = {e.product_id for e in entries if e.product_id and e.register_type == RegisterType.STOCK}
        if product_ids:
            PostingService.check_stock_alerts(db, company_id, list(product_ids))

    @staticmethod
    def check_stock_alerts(db: Session, company_id: UUID, product_ids: List[UUID]):
        """
        Check if stock for specific products falls below min_stock and create notifications.
        """
        from app.models import Product, Notification
        from app.models.user import User

        # Get balances
        balances = PostingService.get_stock_balances(db, company_id, product_ids)
        
        # Get products with min_stock info
        products = db.query(Product).filter(
            Product.id.in_(product_ids),
            Product.min_stock > 0,
            Product.is_deleted == False
        ).all()
        
        for p in products:
            curr_qty = balances.get(str(p.id), 0.0)
            if curr_qty < float(p.min_stock):
                # Check if notification already exists recently (to avoid spam)
                # For v1, just create one. 
                # We need a recipient (usually owner/manager)
                admins = db.query(User).filter(User.company_id == company_id).all()
                for admin in admins:
                    text = f"Залишки товару '{p.name}' ({p.sku}) опустилися до {curr_qty} {p.unit_of_measure}. Мінімум: {p.min_stock}."
                    notif = Notification(
                        company_id=company_id,
                        user_id=admin.id,
                        title="Low Stock Alert",
                        message=text,
                        type="warning",
                        is_read=False
                    )
                    db.add(notif)
        db.flush()

    @staticmethod
    def unpost_document(
        db: Session,
        company_id: UUID,
        document_type: str,
        document_id: UUID
    ):
        """Remove all register records associated with a document"""
        db.query(AccumulationRegister).filter(
            AccumulationRegister.company_id == company_id,
            AccumulationRegister.document_type == document_type,
            AccumulationRegister.document_id == document_id
        ).delete()
        db.flush()

    @staticmethod
    def get_stock_balances(
        db: Session,
        company_id: UUID,
        product_ids: Optional[List[UUID]] = None,
        group_by_variant: bool = False,
    ):
        """
        Get current stock balances for products.
        When group_by_variant=False (default): {product_id: quantity}
        When group_by_variant=True: {product_id: {variant_id_or_None: quantity}}
        """
        from sqlalchemy import func

        if group_by_variant:
            # We fetch all register entries
            query = db.query(
                AccumulationRegister.product_id,
                AccumulationRegister.variant_id,
                func.sum(AccumulationRegister.quantity).label("balance"),
            ).filter(
                AccumulationRegister.company_id == company_id,
                AccumulationRegister.register_type == RegisterType.STOCK
            )
            if product_ids:
                query = query.filter(AccumulationRegister.product_id.in_(product_ids))
            
            raw_results = query.group_by(
                AccumulationRegister.product_id,
                AccumulationRegister.variant_id
            ).all()

            # Now we need to post-process and group by tracked attributes
            from app.models.product import ProductAttribute
            from app.models.variant import VariantValue
            
            # Cache non-tracked attributes per product
            non_tracked_map = {}
            if product_ids:
                nt_attrs = db.query(ProductAttribute).filter(
                    ProductAttribute.product_id.in_(product_ids),
                    ProductAttribute.track_stock_separately == False
                ).all()
                for nt in nt_attrs:
                    p_id = str(nt.product_id)
                    if p_id not in non_tracked_map: non_tracked_map[p_id] = set()
                    non_tracked_map[p_id].add(str(nt.attribute_id))

            # Grouping logic
            grouped_balances = {} # {product_id: {variant_id_or_mapped: quantity}}
            
            for r in raw_results:
                p_id = str(r.product_id)
                v_id = str(r.variant_id) if r.variant_id else None
                
                if p_id not in grouped_balances: grouped_balances[p_id] = {}
                
                # If we have non-tracked attributes, we might need to map this variant to a common key
                target_v_id = v_id
                if v_id and p_id in non_tracked_map:
                    # Fetch variant values
                    v_vals = db.query(VariantValue).filter(VariantValue.variant_id == r.variant_id).all()
                    # Check if any value belongs to a non-tracked attribute
                    has_nt = any(str(vv.attribute_id) in non_tracked_map[p_id] for vv in v_vals)
                    if has_nt:
                        # Find a "Canonical Variant ID" or create a fingerprint
                        # For now, we'll use a simplified approach: 
                        # if it has non-tracked attributes, we use the first variant found that matches tracked ones.
                        # BUT this is complex for a GET request.
                        # SIMPLIFIED: Just aggregate into a single "variant-less" bucket if ANY attribute is non-tracked?
                        # No, only aggregate if they share TRACKED attributes.
                        pass

                grouped_balances[p_id][target_v_id] = grouped_balances[p_id].get(target_v_id, 0.0) + float(r.balance)
            
            return grouped_balances
        else:
            query = db.query(
                AccumulationRegister.product_id,
                func.sum(AccumulationRegister.quantity).label("balance"),
            ).filter(
                AccumulationRegister.company_id == company_id,
                AccumulationRegister.register_type == RegisterType.STOCK
            )
            if product_ids:
                query = query.filter(AccumulationRegister.product_id.in_(product_ids))
            
            results = query.group_by(AccumulationRegister.product_id).all()
            return {str(r.product_id): float(r.balance or 0) for r in results if r.product_id}

    @staticmethod
    def get_overall_statistics(db: Session, company_id: UUID):
        """
        Get overall stock statistics for the company using dynamic thresholds.
        """
        from app.models import Product
        from sqlalchemy import func

        # 1. Total active products
        total_products = db.query(func.count(Product.id)).filter(
            Product.company_id == company_id,
            Product.is_active == True,
            Product.is_deleted == False
        ).scalar() or 0

        # 2. Get all active products with their min_stock
        active_products = db.query(Product).filter(
            Product.company_id == company_id,
            Product.is_active == True,
            Product.is_deleted == False
        ).all()
        
        product_ids = [p.id for p in active_products]
        balances = PostingService.get_stock_balances(db, company_id, product_ids)
        
        in_stock_count = 0
        low_stock_count = 0
        out_of_stock_count = 0
        
        for p in active_products:
            p_id = str(p.id)
            qty = balances.get(p_id, 0.0)
            min_val = float(p.min_stock or 0.0)
            
            if qty <= 0:
                out_of_stock_count += 1
            elif qty < min_val:
                low_stock_count += 1
            else:
                in_stock_count += 1

        return {
            "total_products": total_products,
            "in_stock": in_stock_count,
            "low_stock": low_stock_count,
            "out_of_stock": out_of_stock_count
        }
