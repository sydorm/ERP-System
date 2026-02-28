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

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    seed_data(db)

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
def root(): return {"status": "ok", "service": "Drawer Calculator API"}
