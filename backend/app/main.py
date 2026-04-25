from fastapi import FastAPI
# Force reload: 2026-04-26 00:25:00
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title="ERP System API",
    description="Modern ERP system for small and medium businesses",
    version="1.0.0",
)

@app.on_event("startup")
def on_startup():
    """Ensure database schema is up to date for recent changes"""
    from app.db.session import SessionLocal
    from sqlalchemy import text
    db = SessionLocal()
    try:
        # Manually ensure columns exist to prevent 500 errors if alembic is lagging
        db.execute(text("ALTER TABLE attribute_options ADD COLUMN IF NOT EXISTS width INTEGER"))
        db.execute(text("ALTER TABLE attribute_options ADD COLUMN IF NOT EXISTS height INTEGER"))
        
        # Add columns to document lines
        db.execute(text("ALTER TABLE order_lines ADD COLUMN IF NOT EXISTS characteristic_width NUMERIC(15,2)"))
        db.execute(text("ALTER TABLE order_lines ADD COLUMN IF NOT EXISTS characteristic_height NUMERIC(15,2)"))
        db.execute(text("ALTER TABLE purchase_receipt_lines ADD COLUMN IF NOT EXISTS characteristic_width NUMERIC(15,2)"))
        db.execute(text("ALTER TABLE purchase_receipt_lines ADD COLUMN IF NOT EXISTS characteristic_height NUMERIC(15,2)"))
        
        # --- TASK: Recreate 'Розмір ДСП' ---
        char_name = "Розмір ДСП"
        # 1. Delete existing
        char_res = db.execute(text("SELECT id FROM attributes WHERE name = :name"), {"name": char_name}).first()
        if char_res:
            cid = char_res[0]
            db.execute(text("DELETE FROM product_attribute_values WHERE attribute_id = :id"), {"id": cid})
            db.execute(text("DELETE FROM attribute_options WHERE attribute_id = :id"), {"id": cid})
            db.execute(text("DELETE FROM product_attributes WHERE attribute_id = :id"), {"id": cid})
            db.execute(text("DELETE FROM attributes WHERE id = :id"), {"id": cid})
            print(f"🗑️ Deleted existing attribute {char_name}")

        # 2. Find Category "ДСП Матеріали"
        cat_res = db.execute(text("SELECT id FROM product_categories WHERE name = 'ДСП Матеріали'")).first()
        cat_id = cat_res[0] if cat_res else None

        # 3. Create new
        new_attr_id = "00000000-0000-0000-0000-000000000001" # Fixed ID for easier debugging
        db.execute(text("""
            INSERT INTO attributes (id, name, type, category_id, generates_sku, allow_custom_value, affects_bom_dimensions, dimension_format, is_active)
            VALUES (:id, :name, 'DIMENSIONS', :cat_id, false, false, false, '{width}×{height}', true)
            ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, type = EXCLUDED.type
        """), {"id": new_attr_id, "name": char_name, "cat_id": cat_id})

        # 4. Find Product and assign
        prod_res = db.execute(text("SELECT id FROM products WHERE name = 'ДСП Сонома 18мм'")).first()
        if prod_res:
            pid = prod_res[0]
            db.execute(text("INSERT INTO product_attributes (product_id, attribute_id) VALUES (:pid, :aid) ON CONFLICT DO NOTHING"), 
                       {"pid": pid, "aid": new_attr_id})
            
            # Create option 600x320
            oid = "00000000-0000-0000-0000-000000000002"
            db.execute(text("""
                INSERT INTO attribute_options (id, attribute_id, value, width, height)
                VALUES (:id, :aid, '600×320', 600, 320)
                ON CONFLICT (id) DO NOTHING
            """), {"id": oid, "aid": new_attr_id})
            
            # Create value for product
            db.execute(text("""
                INSERT INTO product_attribute_values (id, product_id, attribute_id, option_id, text_value)
                VALUES (:vid, :pid, :aid, :oid, '600×320')
                ON CONFLICT DO NOTHING
            """), {"vid": "00000000-0000-0000-0000-000000000003", "pid": pid, "aid": new_attr_id, "oid": oid})
            
        # -----------------------------------

        db.commit()
        print("✅ Database schema check: OK")
    except Exception as e:
        print(f"⚠️ Database schema check failed: {e}")
    finally:
        db.close()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_cors_header_on_error(request, call_next):
    """
    Ensure CORS headers are present even on internal server errors.
    This helps in debugging remote servers.
    """
    response = await call_next(request)
    if "Access-Control-Allow-Origin" not in response.headers:
        response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler to ensure JSON response and CORS headers.
    Includes traceback for debugging.
    """
    import traceback
    from fastapi.responses import JSONResponse
    from fastapi import Request
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "traceback": traceback.format_exc()
        },
        headers={"Access-Control-Allow-Origin": "*"}
    )


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "ERP System API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check for monitoring"""
    from app.db.session import SessionLocal
    from sqlalchemy import text
    db_status = "ok"
    alembic_version = "unknown"
    try:
        db = SessionLocal()
        res = db.execute(text("SELECT version_num FROM alembic_version")).first()
        if res:
            alembic_version = res[0]
        db.close()
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "ok" else "unhealthy",
        "database": db_status,
        "alembic_version": alembic_version
    }


# Include AI router
from app.api.ai_routes import router as ai_router
from app.api.auth_routes import router as auth_router

# Include routers
app.include_router(ai_router)
app.include_router(auth_router, tags=["Authentication"])

from app.api.purchase_receipt_routes import router as purchase_receipt_router
app.include_router(purchase_receipt_router, prefix="/api/v1", tags=["Purchases"])

from app.api.purchase_order_routes import router as purchase_order_router
app.include_router(purchase_order_router, prefix="/api/v1", tags=["Purchases"])

from app.api.user_routes import router as user_router
app.include_router(user_router, tags=["Users"])

from app.api.product_routes import router as product_router
app.include_router(product_router, prefix="/api/v1", tags=["Products"])

from app.api.dictionary_routes import router as dictionary_router
app.include_router(dictionary_router, prefix="/api/v1", tags=["Dictionaries"])

from app.api.attribute_routes import router as attribute_router
app.include_router(attribute_router, prefix="/api/v1")

from app.api.company_routes import router as company_router
app.include_router(company_router, prefix="/api/v1")

from app.api.counterparty_routes import router as counterparty_router
app.include_router(counterparty_router, prefix="/api/v1", tags=["Sales"])

from app.api.order_routes import router as order_router
app.include_router(order_router, prefix="/api/v1", tags=["Sales"])

from app.api.sales_invoice_routes import router as sales_invoice_router
app.include_router(sales_invoice_router, prefix="/api/v1", tags=["Sales"])

from app.api.warehouse_routes import router as warehouse_router
app.include_router(warehouse_router, prefix="/api/v1", tags=["Inventory"])

from app.api.document_sequence_routes import router as document_sequence_router
app.include_router(document_sequence_router, prefix="/api/v1", tags=["Administration"])

from app.api.trash_routes import router as trash_router
app.include_router(trash_router, prefix="/api/v1", tags=["Administration"])

from app.api.specification_routes import router as specification_router
app.include_router(specification_router, prefix="/api/v1")

from app.api.calculator_routes import router as calculator_router
app.include_router(calculator_router)

from app.api.audit_log_routes import router as audit_log_router
app.include_router(audit_log_router, prefix="/api/v1")

from app.api.upload_routes import router as upload_router
app.include_router(upload_router, prefix="/api/v1/upload", tags=["Uploads"])

from app.api.production_routes import router as production_router
app.include_router(production_router, prefix="/api/v1/production", tags=["Production"])

from app.api.crm_routes import router as crm_router
app.include_router(crm_router, prefix="/api/v1", tags=["CRM"])

from app.api.tax_settings_routes import router as tax_settings_router
app.include_router(tax_settings_router, prefix="/api/v1", tags=["Organization"])

from app.api.finance_routes import router as finance_router
app.include_router(finance_router, prefix="/api/v1", tags=["Finance"])

from app.api.notification_routes import router as notification_router
app.include_router(notification_router, prefix="/api/v1", tags=["Notifications"])

from app.api.hr_routes import router as hr_router
app.include_router(hr_router, prefix="/api/v1", tags=["Personnel"])

from app.api.payroll_routes import router as payroll_router
app.include_router(payroll_router, prefix="/api/v1", tags=["Payroll"])

from app.api.brigade_routes import router as brigade_router
app.include_router(brigade_router, prefix="/api/v1", tags=["Production"])

# Debug/Dev helper for migrations
@app.post("/api/v1/debug/migrate")
async def run_migrations():
    """Manually trigger alembic migrations"""
    from alembic.config import Config
    from alembic import command
    import os
    
    # Use alembic.ini from the backend root
    # Note: we might need to adjust paths depending on where uvicorn is running
    ini_path = "alembic.ini"
    if not os.path.exists(ini_path):
        ini_path = "backend/alembic.ini"
        
    try:
        alembic_cfg = Config(ini_path)
        # Ensure we point to the correct versions directory
        command.upgrade(alembic_cfg, "head")
        return {"status": "success", "message": "Migrations applied successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/v1/debug/fix-db")
async def fix_db():
    """Manually add missing columns if migrations are stuck"""
    from app.db.session import SessionLocal
    from sqlalchemy import text
    db = SessionLocal()
    try:
        db.execute(text("ALTER TABLE attribute_options ADD COLUMN IF NOT EXISTS width INTEGER"))
        db.execute(text("ALTER TABLE attribute_options ADD COLUMN IF NOT EXISTS height INTEGER"))
        db.commit()
        return {"status": "success", "message": "Columns added successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

# Ensure uploads directory exists and mount it for static file serving
import os
from fastapi.staticfiles import StaticFiles
os.makedirs("uploads", exist_ok=True)
app.mount("/api/v1/uploads", StaticFiles(directory="uploads"), name="uploads")
