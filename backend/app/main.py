from fastapi import FastAPI
# Force reload: 2026-04-27 12:30:00
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title="ERP System API",
    description="Modern ERP system for small and medium businesses",
    version="1.0.0",
)

@app.on_event("startup")
def on_startup():
    """Ensure database schema is up to date and all tables exist"""
    from app.db.session import engine, SessionLocal
    from app.models import Base
    from sqlalchemy import text
    
    # 1. Automatically create all missing tables (like 'users', 'products', etc)
    try:
        print("🛠 Initializing database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

    # 2. Seed default business process rules for every company that has none
    try:
        from app.services.business_process_engine import seed_default_rules
        from app.models import Company
        db_seed = SessionLocal()
        companies = db_seed.query(Company).filter(Company.is_active == True).all()
        for company in companies:
            seed_default_rules(db_seed, company.id)
        db_seed.close()
        print("✅ Business process rules seeded")
    except Exception as e:
        print(f"⚠️ Business process rules seed failed: {e}")

    # 3. Manually ensure specific columns exist (for hot-fixes)
    db = SessionLocal()
    try:
        db.execute(text("ALTER TABLE attribute_options ADD COLUMN IF NOT EXISTS width INTEGER"))
        db.execute(text("ALTER TABLE attribute_options ADD COLUMN IF NOT EXISTS height INTEGER"))

        # Add columns to document lines
        db.execute(text("ALTER TABLE order_lines ADD COLUMN IF NOT EXISTS characteristic_width NUMERIC(15,2)"))
        db.execute(text("ALTER TABLE order_lines ADD COLUMN IF NOT EXISTS characteristic_height NUMERIC(15,2)"))
        db.execute(text("ALTER TABLE purchase_receipt_lines ADD COLUMN IF NOT EXISTS characteristic_width NUMERIC(15,2)"))
        db.execute(text("ALTER TABLE purchase_receipt_lines ADD COLUMN IF NOT EXISTS characteristic_height NUMERIC(15,2)"))

        # Data Migration for CRM Stages
        db.execute(text("UPDATE orders SET crm_stage = 'processing' WHERE crm_stage = 'confirmed'"))

        # Cost tracking columns (migration 038)
        db.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS cost_source VARCHAR(200)"))
        db.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS supplier_links JSONB"))
        db.execute(text("ALTER TABLE companies ADD COLUMN IF NOT EXISTS cost_method VARCHAR(30) NOT NULL DEFAULT 'last_price'"))

        # Business process tables (migration 037) — columns guard
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS product_cost_history (
                id UUID PRIMARY KEY,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
                product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
                variant_id UUID REFERENCES product_variants(id) ON DELETE SET NULL,
                document_type VARCHAR(50) NOT NULL,
                document_id UUID NOT NULL,
                document_number VARCHAR(100) NOT NULL,
                supplier_id UUID REFERENCES counterparties(id) ON DELETE SET NULL,
                old_stock NUMERIC(15,4) NOT NULL DEFAULT 0,
                old_cost NUMERIC(15,2),
                incoming_qty NUMERIC(15,4) NOT NULL,
                incoming_price NUMERIC(15,2) NOT NULL,
                new_cost NUMERIC(15,2) NOT NULL,
                method VARCHAR(30) NOT NULL,
                changed_by UUID REFERENCES users(id) ON DELETE SET NULL,
                company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE
            )
        """))

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
app.include_router(user_router, prefix="/api/v1", tags=["Users"])

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

from app.api.dashboard_routes import router as dashboard_router
app.include_router(dashboard_router, prefix="/api/v1", tags=["Dashboard"])


from app.api.tax_settings_routes import router as tax_settings_router
app.include_router(tax_settings_router, prefix="/api/v1", tags=["Organization"])

from app.api.finance_routes import router as finance_router
app.include_router(finance_router, prefix="/api/v1", tags=["Finance"])

from app.api.notification_routes import router as notification_router
app.include_router(notification_router, prefix="/api/v1", tags=["Notifications"])

from app.api.business_process_routes import router as bp_router
app.include_router(bp_router, prefix="/api/v1", tags=["Business Process"])

# ─── APScheduler: SLA cron job ────────────────────────────────────────────────
from apscheduler.schedulers.background import BackgroundScheduler

_scheduler = BackgroundScheduler()

@app.on_event("startup")
def start_sla_scheduler():
    from app.services.sla_service import run_sla_check
    from app.services.business_process_engine import seed_default_rules
    from app.db.session import SessionLocal
    from app.models.company import Company

    def _sla_job():
        db = SessionLocal()
        try:
            run_sla_check(db)
        except Exception as exc:
            print(f"[SLA] cron error: {exc}")
        finally:
            db.close()

    _scheduler.add_job(_sla_job, "interval", minutes=30, id="sla_check", replace_existing=True)
    _scheduler.start()
    print("✅ SLA scheduler started (every 30 min)")

    db_seed = SessionLocal()
    try:
        companies = db_seed.query(Company).filter(Company.is_active == True).all()
        for company in companies:
            seed_default_rules(db_seed, company.id)
        print(f"✅ Business process rules seeded for {len(companies)} companies")
    except Exception as exc:
        print(f"[BP] seed error: {exc}")
    finally:
        db_seed.close()

@app.on_event("shutdown")
def stop_sla_scheduler():
    if _scheduler.running:
        _scheduler.shutdown(wait=False)

from app.api.hr_routes import router as hr_router
app.include_router(hr_router, prefix="/api/v1", tags=["Personnel"])

from app.api.payroll_routes import router as payroll_router
app.include_router(payroll_router, prefix="/api/v1", tags=["Payroll"])

from app.api.brigade_routes import router as brigade_router
app.include_router(brigade_router, prefix="/api/v1", tags=["Production"])

from app.api.print_routes import router as print_router
app.include_router(print_router, prefix="/api/v1")

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
