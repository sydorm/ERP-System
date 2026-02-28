"""
Standalone Calculator Backend — minimal FastAPI
"""
import os
import json
import base64
import httpx
import logging
from typing import List, Optional
from decimal import Decimal

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Boolean, Integer, Numeric, Text, DateTime, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func

# ── DB Setup ──────────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://calc_user:calc_password@calc_postgres:5432/calc_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
VISION_MODEL = os.getenv("OPENROUTER_VISION_MODEL", "google/gemini-2.0-flash-exp:free")

logger = logging.getLogger(__name__)

# ── Models ────────────────────────────────────────────────────────────────────
class CalcMaterial(Base):
    __tablename__ = "calc_materials"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    thickness_mm = Column(Integer, nullable=True)
    price_per_m2 = Column(Numeric(12, 2), nullable=False, default=0)
    unit = Column(String(20), nullable=False, default="м²")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CalcHardware(Base):
    __tablename__ = "calc_hardware"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    brand = Column(String(100), nullable=True)
    length_mm = Column(Integer, nullable=True)
    category = Column(String(100), nullable=False, default="направляючі")
    price_per_unit = Column(Numeric(12, 2), nullable=False, default=0)
    unit = Column(String(20), nullable=False, default="пара")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CalcService(Base):
    __tablename__ = "calc_services"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    price = Column(Numeric(12, 2), nullable=False, default=0)
    unit = Column(String(50), nullable=False, default="шт")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CalcQuote(Base):
    __tablename__ = "calc_quotes"
    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(255), nullable=True)
    input_json = Column(Text, nullable=False)
    result_json = Column(Text, nullable=False)
    total_price = Column(Numeric(12, 2), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# ── Metal Calculator Models ───────────────────────────────────────────────────
class MetalProfile(Base):
    """Metal profiles: tubes, angles, rounds, sheets — with cross-section perimeter for M² calc"""
    __tablename__ = "metal_profiles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)          # "30×30*1.2", "Круг 10мм"
    profile_type = Column(String(50), nullable=False, default="труба")  # труба/куток/круг/лист
    perimeter_m = Column(Numeric(10, 4), nullable=False, default=0)     # Cross-section perimeter in metres
    price_per_meter = Column(Numeric(12, 2), nullable=False, default=0) # UAH per linear metre
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MetalPaint(Base):
    """Paints and primers for powder coating"""
    __tablename__ = "metal_paints"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)            # "Чорна RAL 9005"
    paint_type = Column(String(20), nullable=False, default="фарба")  # фарба / ґрунтовка
    price_per_kg = Column(Numeric(12, 2), nullable=False, default=0)  # UAH/kg
    consumption_kg_per_m2 = Column(Numeric(8, 4), nullable=False, default=0.28)  # kg/m²
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MetalWorkItem(Base):
    """Per-M² or fixed cost items: painting labor, oven, consumables, prep, assembly, welder"""
    __tablename__ = "metal_work_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    pricing_type = Column(String(20), nullable=False, default="per_m2")  # per_m2 / fixed / per_unit
    price = Column(Numeric(12, 2), nullable=False, default=0)
    unit = Column(String(50), nullable=False, default="м²")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MetalOverhead(Base):
    """Fixed overhead items per quote: marketing, rent, electricity"""
    __tablename__ = "metal_overhead"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    price = Column(Numeric(12, 2), nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MetalQuote(Base):
    __tablename__ = "metal_quotes"
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(255), nullable=True)
    client_name = Column(String(255), nullable=True)
    input_json = Column(Text, nullable=False)
    result_json = Column(Text, nullable=False)
    total_price = Column(Numeric(12, 2), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MetalTemplate(Base):
    """Saved calculator configurations — load to pre-fill the form"""
    __tablename__ = "metal_templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)           # Display name: "Стелаж Лорен"
    description = Column(Text, nullable=True)             # Optional description
    input_json = Column(Text, nullable=False)             # Full MetalCalcInput JSON
    result_json = Column(Text, nullable=True)             # Last computed result JSON
    total_price = Column(Numeric(12, 2), nullable=True)   # Last total for display
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# ── Create tables + seed data ─────────────────────────────────────────────────
def seed_data(db: Session):
    if db.query(CalcMaterial).count() == 0:
        db.add_all([
            CalcMaterial(name="ЛДСП 16мм білий", thickness_mm=16, price_per_m2=280, unit="м²"),
            CalcMaterial(name="ЛДСП 18мм білий", thickness_mm=18, price_per_m2=320, unit="м²"),
            CalcMaterial(name="ДВП 4мм (дно шухляди)", thickness_mm=4, price_per_m2=85, unit="м²"),
            CalcMaterial(name="МДФ 16мм", thickness_mm=16, price_per_m2=360, unit="м²"),
            CalcMaterial(name="ЛДСП 16мм сірий", thickness_mm=16, price_per_m2=290, unit="м²"),
        ])
    if db.query(CalcHardware).count() == 0:
        db.add_all([
            CalcHardware(name="Напрямні Muller 300мм", brand="Muller", length_mm=300, category="направляючі", price_per_unit=85, unit="пара"),
            CalcHardware(name="Напрямні Muller 350мм", brand="Muller", length_mm=350, category="направляючі", price_per_unit=95, unit="пара"),
            CalcHardware(name="Напрямні Muller 400мм", brand="Muller", length_mm=400, category="направляючі", price_per_unit=105, unit="пара"),
            CalcHardware(name="Напрямні Muller 450мм", brand="Muller", length_mm=450, category="направляючі", price_per_unit=115, unit="пара"),
            CalcHardware(name="Напрямні Muller 500мм", brand="Muller", length_mm=500, category="направляючі", price_per_unit=125, unit="пара"),
            CalcHardware(name="Напрямні Muller 550мм", brand="Muller", length_mm=550, category="направляючі", price_per_unit=135, unit="пара"),
            CalcHardware(name="Напрямні кульові GTV 350мм", brand="GTV", length_mm=350, category="направляючі", price_per_unit=145, unit="пара"),
            CalcHardware(name="Напрямні кульові GTV 450мм", brand="GTV", length_mm=450, category="направляючі", price_per_unit=165, unit="пара"),
            CalcHardware(name="Ручка-рейлінг 128мм", brand=None, length_mm=None, category="ручки", price_per_unit=45, unit="шт"),
            CalcHardware(name="Ручка-рейлінг 192мм", brand=None, length_mm=None, category="ручки", price_per_unit=55, unit="шт"),
        ])
    if db.query(CalcService).count() == 0:
        db.add_all([
            CalcService(name="Різання матеріалу", price=3, unit="пог.м"),
            CalcService(name="Крайкування ПВХ 0.4мм", price=12, unit="пог.м"),
            CalcService(name="Крайкування ПВХ 2мм", price=25, unit="пог.м"),
            CalcService(name="Складання шухляди", price=150, unit="шт"),
            CalcService(name="Монтаж напрямних", price=50, unit="шт"),
        ])
    db.commit()

def seed_metal_data(db: Session):
    if db.query(MetalProfile).count() == 0:
        db.add_all([
            MetalProfile(name="Профіль 20×20*1.2", profile_type="труба", perimeter_m=0.08, price_per_meter=28),
            MetalProfile(name="Профіль 25×25*1.5", profile_type="труба", perimeter_m=0.10, price_per_meter=38),
            MetalProfile(name="Профіль 30×30*1.2", profile_type="труба", perimeter_m=0.12, price_per_meter=50),
            MetalProfile(name="Профіль 40×40*2.0", profile_type="труба", perimeter_m=0.16, price_per_meter=85),
            MetalProfile(name="Профіль 60×60*2.0", profile_type="труба", perimeter_m=0.24, price_per_meter=130),
            MetalProfile(name="Куток 25×25*3", profile_type="куток", perimeter_m=0.10, price_per_meter=45),
            MetalProfile(name="Куток 40×40*4", profile_type="куток", perimeter_m=0.16, price_per_meter=78),
            MetalProfile(name="Круг 10мм", profile_type="круг", perimeter_m=0.0314, price_per_meter=24),
            MetalProfile(name="Круг 12мм", profile_type="круг", perimeter_m=0.0377, price_per_meter=34),
            MetalProfile(name="Лист 1мм", profile_type="лист", perimeter_m=1.0, price_per_meter=65),   # price per m²
            MetalProfile(name="Лист 2мм", profile_type="лист", perimeter_m=1.0, price_per_meter=125),
        ])
    if db.query(MetalPaint).count() == 0:
        db.add_all([
            MetalPaint(name="Чорна RAL 9005", paint_type="фарба", price_per_kg=198, consumption_kg_per_m2=0.28),
            MetalPaint(name="Біла RAL 9003", paint_type="фарба", price_per_kg=210, consumption_kg_per_m2=0.28),
            MetalPaint(name="Сіра RAL 7016", paint_type="фарба", price_per_kg=205, consumption_kg_per_m2=0.28),
            MetalPaint(name="Ґрунтовка епоксидна", paint_type="ґрунтовка", price_per_kg=145, consumption_kg_per_m2=0.20),
        ])
    if db.query(MetalWorkItem).count() == 0:
        db.add_all([
            MetalWorkItem(name="Робота покраски", pricing_type="per_m2", price=50, unit="м²"),
            MetalWorkItem(name="Піч (порошкове покриття)", pricing_type="per_m2", price=40, unit="м²"),
            MetalWorkItem(name="Розхідник", pricing_type="per_m2", price=50, unit="м²"),
            MetalWorkItem(name="Підготовка металу", pricing_type="per_m2", price=30, unit="м²"),
            MetalWorkItem(name="Збирання", pricing_type="per_m2", price=25, unit="м²"),
            MetalWorkItem(name="Робота зварювальника", pricing_type="fixed", price=330, unit="виріб"),
            MetalWorkItem(name="Різання металу", pricing_type="per_unit", price=15, unit="різ"),
        ])
    if db.query(MetalOverhead).count() == 0:
        db.add_all([
            MetalOverhead(name="Маркетинг", price=50),
            MetalOverhead(name="Оренда / Світло", price=170),
        ])
    db.commit()

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    seed_data(db)
    seed_metal_data(db)

# ── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(title="Drawer Calculator API")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from fastapi import Depends

# ── Schemas ───────────────────────────────────────────────────────────────────
class MaterialOut(BaseModel):
    id: int; name: str; thickness_mm: Optional[int]; price_per_m2: float; unit: str; is_active: bool
    class Config: from_attributes = True

class MaterialCreate(BaseModel):
    name: str; thickness_mm: Optional[int] = None; price_per_m2: float; unit: str = "м²"

class MaterialUpdate(BaseModel):
    name: Optional[str] = None; thickness_mm: Optional[int] = None
    price_per_m2: Optional[float] = None; unit: Optional[str] = None; is_active: Optional[bool] = None

class HardwareOut(BaseModel):
    id: int; name: str; brand: Optional[str]; length_mm: Optional[int]
    category: str; price_per_unit: float; unit: str; is_active: bool
    class Config: from_attributes = True

class HardwareCreate(BaseModel):
    name: str; brand: Optional[str] = None; length_mm: Optional[int] = None
    category: str = "направляючі"; price_per_unit: float; unit: str = "пара"

class HardwareUpdate(BaseModel):
    name: Optional[str] = None; brand: Optional[str] = None; length_mm: Optional[int] = None
    category: Optional[str] = None; price_per_unit: Optional[float] = None
    unit: Optional[str] = None; is_active: Optional[bool] = None

class ServiceOut(BaseModel):
    id: int; name: str; price: float; unit: str; is_active: bool
    class Config: from_attributes = True

class ServiceCreate(BaseModel):
    name: str; price: float; unit: str = "шт"

class ServiceUpdate(BaseModel):
    name: Optional[str] = None; price: Optional[float] = None
    unit: Optional[str] = None; is_active: Optional[bool] = None

class DetailItem(BaseModel):
    name: str; material: str; width_mm: int; height_mm: int
    quantity: int; area_m2: float; price: float

class DrawerInput(BaseModel):
    drawer_count: int = 1; direction: str = "vertical"; facade_type: str = "overlay"
    box_width: int; box_height: int; box_depth: int; drawer_depth: int = 450
    main_material_id: int; bottom_material_id: Optional[int] = None
    facade_material_id: Optional[int] = None; hardware_id: Optional[int] = None
    service_ids: Optional[List[int]] = []
    client_name: Optional[str] = None; notes: Optional[str] = None

class CalcResult(BaseModel):
    details: List[DetailItem]; materials_total: float
    hardware_total: float; services_total: float; grand_total: float; summary: str

# ── Calculation ───────────────────────────────────────────────────────────────
def do_calculate(inp: DrawerInput, main: CalcMaterial,
                 bottom: Optional[CalcMaterial], facade: Optional[CalcMaterial]) -> list:
    n = inp.drawer_count
    section_h = inp.box_height // n
    inner_w = inp.box_width - 32
    drawer_h = section_h - 3
    items = []

    def add(name, mat, w, h, qty):
        area = round((w/1000)*(h/1000)*qty, 4)
        items.append(DetailItem(name=name, material=mat.name, width_mm=w, height_mm=h,
                                quantity=qty, area_m2=area,
                                price=round(float(mat.price_per_m2)*area, 2)))

    add(f"Бічна стінка ×{2*n}", main, inp.drawer_depth, drawer_h, 2*n)
    add(f"Передня/задня ×{2*n}", main, inner_w, drawer_h, 2*n)
    bm = bottom or main
    add(f"Дно ДВП ×{n}", bm, inner_w+12, inp.drawer_depth-12, n)
    if inp.facade_type != "none":
        fm = facade or main
        fw = inp.box_width - 3 if inp.direction == "vertical" else (inp.box_width//n)-3
        fh = section_h - 3
        add(f"Фасад ×{n}", fm, fw, fh, n)
    return items

# ── Materials ─────────────────────────────────────────────────────────────────
@app.get("/api/calculator/materials", response_model=List[MaterialOut])
def get_materials(active_only: bool = True, db: Session = Depends(get_db)):
    q = db.query(CalcMaterial)
    if active_only: q = q.filter(CalcMaterial.is_active == True)
    return q.order_by(CalcMaterial.name).all()

@app.post("/api/calculator/materials", response_model=MaterialOut)
def add_material(data: MaterialCreate, db: Session = Depends(get_db)):
    m = CalcMaterial(**data.model_dump()); db.add(m); db.commit(); db.refresh(m); return m

@app.patch("/api/calculator/materials/{id}", response_model=MaterialOut)
def update_material(id: int, data: MaterialUpdate, db: Session = Depends(get_db)):
    m = db.get(CalcMaterial, id)
    if not m: raise HTTPException(404, "Not found")
    for k, v in data.model_dump(exclude_unset=True).items(): setattr(m, k, v)
    db.commit(); db.refresh(m); return m

# ── Hardware ──────────────────────────────────────────────────────────────────
@app.get("/api/calculator/hardware", response_model=List[HardwareOut])
def get_hardware(active_only: bool = True, db: Session = Depends(get_db)):
    q = db.query(CalcHardware)
    if active_only: q = q.filter(CalcHardware.is_active == True)
    return q.order_by(CalcHardware.category, CalcHardware.name).all()

@app.post("/api/calculator/hardware", response_model=HardwareOut)
def add_hardware(data: HardwareCreate, db: Session = Depends(get_db)):
    h = CalcHardware(**data.model_dump()); db.add(h); db.commit(); db.refresh(h); return h

@app.patch("/api/calculator/hardware/{id}", response_model=HardwareOut)
def update_hardware(id: int, data: HardwareUpdate, db: Session = Depends(get_db)):
    h = db.get(CalcHardware, id)
    if not h: raise HTTPException(404, "Not found")
    for k, v in data.model_dump(exclude_unset=True).items(): setattr(h, k, v)
    db.commit(); db.refresh(h); return h

# ── Services ──────────────────────────────────────────────────────────────────
@app.get("/api/calculator/services", response_model=List[ServiceOut])
def get_services(active_only: bool = True, db: Session = Depends(get_db)):
    q = db.query(CalcService)
    if active_only: q = q.filter(CalcService.is_active == True)
    return q.order_by(CalcService.name).all()

@app.post("/api/calculator/services", response_model=ServiceOut)
def add_service(data: ServiceCreate, db: Session = Depends(get_db)):
    s = CalcService(**data.model_dump()); db.add(s); db.commit(); db.refresh(s); return s

@app.patch("/api/calculator/services/{id}", response_model=ServiceOut)
def update_service(id: int, data: ServiceUpdate, db: Session = Depends(get_db)):
    s = db.get(CalcService, id)
    if not s: raise HTTPException(404, "Not found")
    for k, v in data.model_dump(exclude_unset=True).items(): setattr(s, k, v)
    db.commit(); db.refresh(s); return s

# ── Calculate ─────────────────────────────────────────────────────────────────
@app.post("/api/calculator/calculate", response_model=CalcResult)
def calculate(inp: DrawerInput, db: Session = Depends(get_db)):
    main = db.get(CalcMaterial, inp.main_material_id)
    if not main: raise HTTPException(400, "Матеріал не знайдено")
    bottom = db.get(CalcMaterial, inp.bottom_material_id) if inp.bottom_material_id else None
    facade = db.get(CalcMaterial, inp.facade_material_id) if inp.facade_material_id else None
    details = do_calculate(inp, main, bottom, facade)
    mat_total = round(sum(d.price for d in details), 2)
    hw_total = 0.0
    if inp.hardware_id:
        hw = db.get(CalcHardware, inp.hardware_id)
        if hw: hw_total = round(float(hw.price_per_unit) * inp.drawer_count, 2)
    svc_total = 0.0
    if inp.service_ids:
        svcs = db.query(CalcService).filter(CalcService.id.in_(inp.service_ids)).all()
        for s in svcs:
            svc_total += float(s.price) * inp.drawer_count * (2 if s.unit == "пог.м" else 1)
    svc_total = round(svc_total, 2)
    grand = round(mat_total + hw_total + svc_total, 2)
    summary = f"Короб {inp.box_width}×{inp.box_height}×{inp.box_depth}мм, {inp.drawer_count} шухл. — {grand:.0f} грн"
    return CalcResult(details=details, materials_total=mat_total, hardware_total=hw_total,
                      services_total=svc_total, grand_total=grand, summary=summary)

# ── AI Image ──────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Ти — меблевий технолог. Проаналізуй фото і поверни ТІЛЬКИ JSON без зайвого тексту:
{"drawer_count":2,"direction":"vertical","facade_type":"overlay","approx_width":600,"approx_height":720,"approx_depth":500,"drawer_depth":450,"confidence":"high","notes":"опис"}"""

@app.post("/api/calculator/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Потрібне зображення")
    data = await file.read()
    if len(data) > 10*1024*1024:
        raise HTTPException(400, "Файл завеликий (макс 10МБ)")
    if not OPENROUTER_API_KEY:
        return {"drawer_count":1,"direction":"vertical","facade_type":"overlay",
                "approx_width":600,"approx_height":720,"approx_depth":500,
                "drawer_depth":450,"confidence":"low","notes":"API ключ не налаштовано"}
    b64 = base64.b64encode(data).decode()
    payload = {
        "model": VISION_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:{file.content_type};base64,{b64}"}},
                {"type": "text", "text": "Проаналізуй шухляди на фото."}
            ]}
        ],
        "max_tokens": 400, "temperature": 0.1
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post("https://openrouter.ai/api/v1/chat/completions",
                              json=payload,
                              headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}",
                                       "Content-Type": "application/json"})
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"].strip()
        if "```" in text:
            text = text.split("```")[1].replace("json","").strip()
        return json.loads(text)

# ── Save quote ────────────────────────────────────────────────────────────────
@app.post("/api/calculator/save-quote")
def save_quote(body: dict, db: Session = Depends(get_db)):
    q = CalcQuote(
        client_name=body.get("client_name"),
        input_json=json.dumps(body.get("inp", {})),
        result_json=json.dumps(body.get("result", {})),
        total_price=body.get("result", {}).get("grand_total"),
        notes=body.get("notes")
    )
    db.add(q); db.commit(); db.refresh(q)
    return {"id": q.id}

@app.get("/api/calculator/quotes")
def list_quotes(db: Session = Depends(get_db)):
    return db.query(CalcQuote).order_by(CalcQuote.created_at.desc()).limit(50).all()

@app.get("/")
def root(): return {"status": "ok", "service": "Calculator API (Drawer + Metal)"}

# ════════════════════════════════════════════════════════════════════
# METAL CALCULATOR API
# ════════════════════════════════════════════════════════════════════

# ── Metal Pydantic Schemas ────────────────────────────────────────────────────
class MetalProfileOut(BaseModel):
    id: int; name: str; profile_type: str; perimeter_m: float
    price_per_meter: float; is_active: bool
    class Config: from_attributes = True

class MetalProfileCreate(BaseModel):
    name: str; profile_type: str = "труба"; perimeter_m: float; price_per_meter: float

class MetalProfileUpdate(BaseModel):
    name: Optional[str]=None; profile_type: Optional[str]=None
    perimeter_m: Optional[float]=None; price_per_meter: Optional[float]=None; is_active: Optional[bool]=None

class MetalPaintOut(BaseModel):
    id: int; name: str; paint_type: str; price_per_kg: float
    consumption_kg_per_m2: float; is_active: bool
    class Config: from_attributes = True

class MetalPaintCreate(BaseModel):
    name: str; paint_type: str = "фарба"; price_per_kg: float; consumption_kg_per_m2: float = 0.28

class MetalPaintUpdate(BaseModel):
    name: Optional[str]=None; paint_type: Optional[str]=None
    price_per_kg: Optional[float]=None; consumption_kg_per_m2: Optional[float]=None; is_active: Optional[bool]=None

class MetalWorkItemOut(BaseModel):
    id: int; name: str; pricing_type: str; price: float; unit: str; is_active: bool
    class Config: from_attributes = True

class MetalWorkItemCreate(BaseModel):
    name: str; pricing_type: str = "per_m2"; price: float; unit: str = "м²"

class MetalWorkItemUpdate(BaseModel):
    name: Optional[str]=None; pricing_type: Optional[str]=None
    price: Optional[float]=None; unit: Optional[str]=None; is_active: Optional[bool]=None

class MetalOverheadOut(BaseModel):
    id: int; name: str; price: float; is_active: bool
    class Config: from_attributes = True

class MetalOverheadCreate(BaseModel):
    name: str; price: float

class MetalOverheadUpdate(BaseModel):
    name: Optional[str]=None; price: Optional[float]=None; is_active: Optional[bool]=None

# Input for metal calculation
class MetalProfileRow(BaseModel):
    profile_id: int
    length_m: float        # linear metres
    quantity: int = 1      # pieces

class MetalCalcInput(BaseModel):
    product_name: Optional[str] = None
    client_name: Optional[str] = None
    rows: List[MetalProfileRow]          # list of profile rows
    paint_id: Optional[int] = None
    with_primer: bool = False
    primer_id: Optional[int] = None
    work_item_ids: Optional[List[int]] = []   # selected work items
    overhead_ids: Optional[List[int]] = []    # selected overhead items
    welder_qty: int = 1                       # number of weld jobs
    cuts_qty: int = 0                         # number of cuts
    notes: Optional[str] = None

class MetalResultLine(BaseModel):
    name: str; qty: float; unit: str; price_unit: float; total: float

class MetalCalcResult(BaseModel):
    product_name: Optional[str]
    total_m2: float
    metal_lines: List[MetalResultLine]
    coating_lines: List[MetalResultLine]
    work_lines: List[MetalResultLine]
    overhead_lines: List[MetalResultLine]
    metal_subtotal: float
    coating_subtotal: float
    work_subtotal: float
    overhead_subtotal: float
    grand_total: float

# ── Metal CRUD ────────────────────────────────────────────────────────────────
@app.get("/api/metal/profiles", response_model=List[MetalProfileOut])
def get_profiles(active_only: bool=True, db: Session=Depends(get_db)):
    q = db.query(MetalProfile)
    if active_only: q = q.filter(MetalProfile.is_active==True)
    return q.order_by(MetalProfile.profile_type, MetalProfile.name).all()

@app.post("/api/metal/profiles", response_model=MetalProfileOut)
def add_profile(data: MetalProfileCreate, db: Session=Depends(get_db)):
    p=MetalProfile(**data.model_dump()); db.add(p); db.commit(); db.refresh(p); return p

@app.patch("/api/metal/profiles/{id}", response_model=MetalProfileOut)
def upd_profile(id: int, data: MetalProfileUpdate, db: Session=Depends(get_db)):
    p=db.get(MetalProfile,id)
    if not p: raise HTTPException(404,"Not found")
    for k,v in data.model_dump(exclude_unset=True).items(): setattr(p,k,v)
    db.commit(); db.refresh(p); return p

@app.get("/api/metal/paints", response_model=List[MetalPaintOut])
def get_paints(active_only: bool=True, db: Session=Depends(get_db)):
    q = db.query(MetalPaint)
    if active_only: q = q.filter(MetalPaint.is_active==True)
    return q.order_by(MetalPaint.paint_type, MetalPaint.name).all()

@app.post("/api/metal/paints", response_model=MetalPaintOut)
def add_paint(data: MetalPaintCreate, db: Session=Depends(get_db)):
    p=MetalPaint(**data.model_dump()); db.add(p); db.commit(); db.refresh(p); return p

@app.patch("/api/metal/paints/{id}", response_model=MetalPaintOut)
def upd_paint(id: int, data: MetalPaintUpdate, db: Session=Depends(get_db)):
    p=db.get(MetalPaint,id)
    if not p: raise HTTPException(404,"Not found")
    for k,v in data.model_dump(exclude_unset=True).items(): setattr(p,k,v)
    db.commit(); db.refresh(p); return p

@app.get("/api/metal/work-items", response_model=List[MetalWorkItemOut])
def get_work_items(active_only: bool=True, db: Session=Depends(get_db)):
    q = db.query(MetalWorkItem)
    if active_only: q = q.filter(MetalWorkItem.is_active==True)
    return q.order_by(MetalWorkItem.name).all()

@app.post("/api/metal/work-items", response_model=MetalWorkItemOut)
def add_work_item(data: MetalWorkItemCreate, db: Session=Depends(get_db)):
    w=MetalWorkItem(**data.model_dump()); db.add(w); db.commit(); db.refresh(w); return w

@app.patch("/api/metal/work-items/{id}", response_model=MetalWorkItemOut)
def upd_work_item(id: int, data: MetalWorkItemUpdate, db: Session=Depends(get_db)):
    w=db.get(MetalWorkItem,id)
    if not w: raise HTTPException(404,"Not found")
    for k,v in data.model_dump(exclude_unset=True).items(): setattr(w,k,v)
    db.commit(); db.refresh(w); return w

@app.get("/api/metal/overhead", response_model=List[MetalOverheadOut])
def get_overhead(active_only: bool=True, db: Session=Depends(get_db)):
    q = db.query(MetalOverhead)
    if active_only: q = q.filter(MetalOverhead.is_active==True)
    return q.all()

@app.post("/api/metal/overhead", response_model=MetalOverheadOut)
def add_overhead(data: MetalOverheadCreate, db: Session=Depends(get_db)):
    o=MetalOverhead(**data.model_dump()); db.add(o); db.commit(); db.refresh(o); return o

@app.patch("/api/metal/overhead/{id}", response_model=MetalOverheadOut)
def upd_overhead(id: int, data: MetalOverheadUpdate, db: Session=Depends(get_db)):
    o=db.get(MetalOverhead,id)
    if not o: raise HTTPException(404,"Not found")
    for k,v in data.model_dump(exclude_unset=True).items(): setattr(o,k,v)
    db.commit(); db.refresh(o); return o

# ── Metal Calculate ───────────────────────────────────────────────────────────
@app.post("/api/metal/calculate", response_model=MetalCalcResult)
def metal_calculate(inp: MetalCalcInput, db: Session=Depends(get_db)):
    metal_lines = []
    total_m2 = 0.0

    for row in inp.rows:
        prof = db.get(MetalProfile, row.profile_id)
        if not prof: continue
        # M² = perimeter × length × quantity
        m2 = round(float(prof.perimeter_m) * row.length_m * row.quantity, 4)
        total_m2 += m2
        mat_cost = round(row.length_m * row.quantity * float(prof.price_per_meter), 2)
        metal_lines.append(MetalResultLine(
            name=prof.name,
            qty=round(row.length_m * row.quantity, 3),
            unit="м",
            price_unit=float(prof.price_per_meter),
            total=mat_cost
        ))

    total_m2 = round(total_m2, 4)
    metal_subtotal = round(sum(l.total for l in metal_lines), 2)

    # ── Coating (paint + oven) ──────────────────────────────────────────────
    coating_lines = []
    coating_subtotal = 0.0

    if inp.paint_id:
        paint = db.get(MetalPaint, inp.paint_id)
        if paint:
            paint_kg = round(total_m2 * float(paint.consumption_kg_per_m2), 4)
            paint_cost = round(paint_kg * float(paint.price_per_kg), 2)
            coating_lines.append(MetalResultLine(
                name=paint.name, qty=paint_kg, unit="кг",
                price_unit=float(paint.price_per_kg), total=paint_cost
            ))
            coating_subtotal += paint_cost

    if inp.with_primer and inp.primer_id:
        primer = db.get(MetalPaint, inp.primer_id)
        if primer:
            primer_kg = round(total_m2 * float(primer.consumption_kg_per_m2), 4)
            primer_cost = round(primer_kg * float(primer.price_per_kg), 2)
            coating_lines.append(MetalResultLine(
                name=f"Ґрунтовка: {primer.name}", qty=primer_kg, unit="кг",
                price_unit=float(primer.price_per_kg), total=primer_cost
            ))
            coating_subtotal += primer_cost

    coating_subtotal = round(coating_subtotal, 2)

    # ── Work items ────────────────────────────────────────────────────────────
    work_lines = []
    work_subtotal = 0.0

    if inp.work_item_ids:
        items = db.query(MetalWorkItem).filter(MetalWorkItem.id.in_(inp.work_item_ids)).all()
        for wi in items:
            if wi.pricing_type == "per_m2":
                cost = round(total_m2 * float(wi.price), 2)
                qty = total_m2
                unit = "м²"
            elif wi.pricing_type == "per_unit":
                # welder = welder_qty, cuts = cuts_qty
                unit_count = inp.cuts_qty if "різ" in wi.name.lower() else inp.welder_qty
                cost = round(unit_count * float(wi.price), 2)
                qty = float(unit_count)
                unit = wi.unit
            else:  # fixed
                cost = float(wi.price)
                qty = 1
                unit = wi.unit
            work_lines.append(MetalResultLine(
                name=wi.name, qty=qty, unit=unit,
                price_unit=float(wi.price), total=cost
            ))
            work_subtotal += cost
    work_subtotal = round(work_subtotal, 2)

    # ── Overhead ───────────────────────────────────────────────────────────────
    overhead_lines = []
    overhead_subtotal = 0.0
    if inp.overhead_ids:
        ovs = db.query(MetalOverhead).filter(MetalOverhead.id.in_(inp.overhead_ids)).all()
        for o in ovs:
            overhead_lines.append(MetalResultLine(
                name=o.name, qty=1, unit="разово",
                price_unit=float(o.price), total=float(o.price)
            ))
            overhead_subtotal += float(o.price)
    overhead_subtotal = round(overhead_subtotal, 2)

    grand = round(metal_subtotal + coating_subtotal + work_subtotal + overhead_subtotal, 2)

    return MetalCalcResult(
        product_name=inp.product_name,
        total_m2=total_m2,
        metal_lines=metal_lines,
        coating_lines=coating_lines,
        work_lines=work_lines,
        overhead_lines=overhead_lines,
        metal_subtotal=metal_subtotal,
        coating_subtotal=coating_subtotal,
        work_subtotal=work_subtotal,
        overhead_subtotal=overhead_subtotal,
        grand_total=grand
    )

@app.post("/api/metal/save-quote")
def metal_save_quote(body: dict, db: Session=Depends(get_db)):
    q = MetalQuote(
        product_name=body.get("product_name"),
        client_name=body.get("client_name"),
        input_json=json.dumps(body.get("inp", {})),
        result_json=json.dumps(body.get("result", {})),
        total_price=body.get("result", {}).get("grand_total"),
        notes=body.get("notes")
    )
    db.add(q); db.commit(); db.refresh(q)
    return {"id": q.id}

@app.get("/api/metal/quotes")
def metal_list_quotes(db: Session=Depends(get_db)):
    return db.query(MetalQuote).order_by(MetalQuote.created_at.desc()).limit(50).all()

# ── Metal Templates ────────────────────────────────────────────────────────────
@app.get("/api/metal/templates")
def list_templates(db: Session=Depends(get_db)):
    rows = db.query(MetalTemplate).order_by(MetalTemplate.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "total_price": float(r.total_price) if r.total_price else None,
            "input_json": r.input_json,
            "result_json": r.result_json,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]

@app.post("/api/metal/templates")
def save_template(body: dict, db: Session=Depends(get_db)):
    t = MetalTemplate(
        name=body.get("name", "Без назви"),
        description=body.get("description"),
        input_json=json.dumps(body.get("inp", {})),
        result_json=json.dumps(body.get("result", {})) if body.get("result") else None,
        total_price=body.get("result", {}).get("grand_total") if body.get("result") else None,
    )
    db.add(t); db.commit(); db.refresh(t)
    return {"id": t.id, "name": t.name}

@app.patch("/api/metal/templates/{tid}")
def update_template(tid: int, body: dict, db: Session=Depends(get_db)):
    t = db.query(MetalTemplate).filter(MetalTemplate.id == tid).first()
    if not t: raise HTTPException(status_code=404, detail="Not found")
    if "name" in body: t.name = body["name"]
    if "description" in body: t.description = body["description"]
    db.commit(); db.refresh(t)
    return {"id": t.id}

@app.delete("/api/metal/templates/{tid}")
def delete_template(tid: int, db: Session=Depends(get_db)):
    t = db.query(MetalTemplate).filter(MetalTemplate.id == tid).first()
    if not t: raise HTTPException(status_code=404, detail="Not found")
    db.delete(t); db.commit()
    return {"ok": True}
