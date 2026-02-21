from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title="ERP System API",
    description="Modern ERP system for small and medium businesses",
    version="1.0.0",
)

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

from app.api.specification_routes import router as specification_router
app.include_router(specification_router, prefix="/api/v1")
# from app.api.v1.api import api_router
# app.include_router(api_router, prefix="/api/v1")
