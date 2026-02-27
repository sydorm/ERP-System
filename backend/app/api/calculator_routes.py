"""
Calculator API Routes - Drawer Price Calculator
Isolated from main ERP, uses separate calc_* tables
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from decimal import Decimal
import json

from app.db.session import get_db
from app.models.calculator import CalcMaterial, CalcHardware, CalcService, CalcQuote
from app.services.openrouter_service import analyze_drawer_image

router = APIRouter(prefix="/api/calculator", tags=["Calculator"])


# ─── Pydantic schemas ─────────────────────────────────────────────────────────

class MaterialOut(BaseModel):
    id: int
    name: str
    thickness_mm: Optional[int]
    price_per_m2: float
    unit: str
    is_active: bool
    class Config: from_attributes = True

class MaterialCreate(BaseModel):
    name: str
    thickness_mm: Optional[int] = None
    price_per_m2: float
    unit: str = "м²"

class MaterialUpdate(BaseModel):
    name: Optional[str] = None
    thickness_mm: Optional[int] = None
    price_per_m2: Optional[float] = None
    unit: Optional[str] = None
    is_active: Optional[bool] = None


class HardwareOut(BaseModel):
    id: int
    name: str
    brand: Optional[str]
    length_mm: Optional[int]
    category: str
    price_per_unit: float
    unit: str
    is_active: bool
    class Config: from_attributes = True

class HardwareCreate(BaseModel):
    name: str
    brand: Optional[str] = None
    length_mm: Optional[int] = None
    category: str = "направляючі"
    price_per_unit: float
    unit: str = "пара"

class HardwareUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    length_mm: Optional[int] = None
    category: Optional[str] = None
    price_per_unit: Optional[float] = None
    unit: Optional[str] = None
    is_active: Optional[bool] = None


class ServiceOut(BaseModel):
    id: int
    name: str
    price: float
    unit: str
    is_active: bool
    class Config: from_attributes = True

class ServiceCreate(BaseModel):
    name: str
    price: float
    unit: str = "шт"

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    unit: Optional[str] = None
    is_active: Optional[bool] = None


class DrawerInput(BaseModel):
    # Конфігурація
    drawer_count: int = 1
    direction: str = "vertical"   # "vertical" або "horizontal"
    facade_type: str = "overlay"  # "overlay", "inset", "none"
    # Розміри короба (мм)
    box_width: int
    box_height: int
    box_depth: int
    # Głębokість шухляди (мм)
    drawer_depth: int = 450
    # Матеріали
    main_material_id: int
    bottom_material_id: Optional[int] = None   # ДВП для дна
    facade_material_id: Optional[int] = None
    # Фурнітура
    hardware_id: Optional[int] = None
    # Послуги (список id)
    service_ids: Optional[List[int]] = []
    # Клієнт
    client_name: Optional[str] = None
    notes: Optional[str] = None


class DetailItem(BaseModel):
    name: str
    material: str
    width_mm: int
    height_mm: int
    quantity: int
    area_m2: float
    price: float


class CalculationResult(BaseModel):
    details: List[DetailItem]
    materials_total: float
    hardware_total: float
    services_total: float
    grand_total: float
    summary: str


class QuoteOut(BaseModel):
    id: int
    client_name: Optional[str]
    total_price: Optional[float]
    notes: Optional[str]
    created_at: str
    class Config: from_attributes = True


# ─── Calculation Logic ────────────────────────────────────────────────────────

def calculate_drawer_details(inp: DrawerInput, main_mat: CalcMaterial,
                              bottom_mat: Optional[CalcMaterial],
                              facade_mat: Optional[CalcMaterial]) -> List[DetailItem]:
    """
    Core drawer cutting calculation.
    Standard furniture formulas (16mm board, roller slides).
    """
    details = []
    n = inp.drawer_count

    # Height per drawer section
    section_height = inp.box_height // n

    # Drawer inner width (box width minus 2x board thickness and clearance)
    drawer_inner_width = inp.box_width - 32   # 2 × 16mm boards
    drawer_height = section_height - 3         # 3mm clearance per drawer

    # ── КОЖНА ШУХЛЯДА ──────────────────────────────────────────────────────
    # Бічні стінки ×2 (ЛДСП основний)
    side_w = inp.drawer_depth
    side_h = drawer_height
    side_area = round((side_w / 1000) * (side_h / 1000), 4)
    details.append(DetailItem(
        name=f"Бічна стінка шухляди ×{2 * n}",
        material=main_mat.name,
        width_mm=side_w,
        height_mm=side_h,
        quantity=2 * n,
        area_m2=round(side_area * 2 * n, 4),
        price=round(float(main_mat.price_per_m2) * side_area * 2 * n, 2)
    ))

    # Передня/задня стінка ×2 (ЛДСП)
    front_w = drawer_inner_width
    front_h = drawer_height
    front_area = round((front_w / 1000) * (front_h / 1000), 4)
    details.append(DetailItem(
        name=f"Передня/задня стінка ×{2 * n}",
        material=main_mat.name,
        width_mm=front_w,
        height_mm=front_h,
        quantity=2 * n,
        area_m2=round(front_area * 2 * n, 4),
        price=round(float(main_mat.price_per_m2) * front_area * 2 * n, 2)
    ))

    # Дно шухляди (ДВП)
    bottom_mat_used = bottom_mat or main_mat
    bottom_w = drawer_inner_width + 12  # вставляється в пази
    bottom_h = inp.drawer_depth - 12
    bottom_area = round((bottom_w / 1000) * (bottom_h / 1000), 4)
    details.append(DetailItem(
        name=f"Дно шухляди (ДВП) ×{n}",
        material=bottom_mat_used.name,
        width_mm=bottom_w,
        height_mm=bottom_h,
        quantity=n,
        area_m2=round(bottom_area * n, 4),
        price=round(float(bottom_mat_used.price_per_m2) * bottom_area * n, 2)
    ))

    # Фасад (якщо є)
    if inp.facade_type != "none":
        facade_mat_used = facade_mat or main_mat
        if inp.direction == "vertical":
            facade_w = inp.box_width - 3
            facade_h = section_height - 3
        else:
            facade_w = (inp.box_width // n) - 3
            facade_h = inp.box_height - 3
        facade_area = round((facade_w / 1000) * (facade_h / 1000), 4)
        details.append(DetailItem(
            name=f"Фасад шухляди ×{n}",
            material=facade_mat_used.name,
            width_mm=facade_w,
            height_mm=facade_h,
            quantity=n,
            area_m2=round(facade_area * n, 4),
            price=round(float(facade_mat_used.price_per_m2) * facade_area * n, 2)
        ))

    return details


# ─── Materials CRUD ───────────────────────────────────────────────────────────

@router.get("/materials", response_model=List[MaterialOut])
def get_materials(active_only: bool = True, db: Session = Depends(get_db)):
    q = db.query(CalcMaterial)
    if active_only:
        q = q.filter(CalcMaterial.is_active == True)
    return q.order_by(CalcMaterial.name).all()

@router.post("/materials", response_model=MaterialOut)
def create_material(data: MaterialCreate, db: Session = Depends(get_db)):
    item = CalcMaterial(**data.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.patch("/materials/{item_id}", response_model=MaterialOut)
def update_material(item_id: int, data: MaterialUpdate, db: Session = Depends(get_db)):
    item = db.query(CalcMaterial).get(item_id)
    if not item: raise HTTPException(404, "Матеріал не знайдено")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit(); db.refresh(item)
    return item


# ─── Hardware CRUD ────────────────────────────────────────────────────────────

@router.get("/hardware", response_model=List[HardwareOut])
def get_hardware(active_only: bool = True, db: Session = Depends(get_db)):
    q = db.query(CalcHardware)
    if active_only:
        q = q.filter(CalcHardware.is_active == True)
    return q.order_by(CalcHardware.category, CalcHardware.name).all()

@router.post("/hardware", response_model=HardwareOut)
def create_hardware(data: HardwareCreate, db: Session = Depends(get_db)):
    item = CalcHardware(**data.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.patch("/hardware/{item_id}", response_model=HardwareOut)
def update_hardware(item_id: int, data: HardwareUpdate, db: Session = Depends(get_db)):
    item = db.query(CalcHardware).get(item_id)
    if not item: raise HTTPException(404, "Фурнітуру не знайдено")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit(); db.refresh(item)
    return item


# ─── Services CRUD ────────────────────────────────────────────────────────────

@router.get("/services", response_model=List[ServiceOut])
def get_services(active_only: bool = True, db: Session = Depends(get_db)):
    q = db.query(CalcService)
    if active_only:
        q = q.filter(CalcService.is_active == True)
    return q.order_by(CalcService.name).all()

@router.post("/services", response_model=ServiceOut)
def create_service(data: ServiceCreate, db: Session = Depends(get_db)):
    item = CalcService(**data.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.patch("/services/{item_id}", response_model=ServiceOut)
def update_service(item_id: int, data: ServiceUpdate, db: Session = Depends(get_db)):
    item = db.query(CalcService).get(item_id)
    if not item: raise HTTPException(404, "Послугу не знайдено")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit(); db.refresh(item)
    return item


# ─── Calculation ──────────────────────────────────────────────────────────────

@router.post("/calculate", response_model=CalculationResult)
def calculate(inp: DrawerInput, db: Session = Depends(get_db)):
    main_mat = db.query(CalcMaterial).get(inp.main_material_id)
    if not main_mat:
        raise HTTPException(400, "Основний матеріал не знайдено")

    bottom_mat = db.query(CalcMaterial).get(inp.bottom_material_id) if inp.bottom_material_id else None
    facade_mat = db.query(CalcMaterial).get(inp.facade_material_id) if inp.facade_material_id else None

    details = calculate_drawer_details(inp, main_mat, bottom_mat, facade_mat)
    materials_total = round(sum(d.price for d in details), 2)

    # Hardware
    hardware_total = 0.0
    if inp.hardware_id:
        hw = db.query(CalcHardware).get(inp.hardware_id)
        if hw:
            hardware_total = round(float(hw.price_per_unit) * inp.drawer_count, 2)

    # Services
    services_total = 0.0
    if inp.service_ids:
        services = db.query(CalcService).filter(CalcService.id.in_(inp.service_ids)).all()
        for svc in services:
            # Services like cutting/edging multiply by drawer count
            if svc.unit in ("пог.м",):
                services_total += float(svc.price) * inp.drawer_count * 2
            else:
                services_total += float(svc.price) * inp.drawer_count
        services_total = round(services_total, 2)

    grand_total = round(materials_total + hardware_total + services_total, 2)

    summary = (
        f"Короб {inp.box_width}×{inp.box_height}×{inp.box_depth}мм, "
        f"{inp.drawer_count} шухл., матеріал: {main_mat.name}, "
        f"разом: {grand_total:.0f} грн"
    )

    return CalculationResult(
        details=details,
        materials_total=materials_total,
        hardware_total=hardware_total,
        services_total=services_total,
        grand_total=grand_total,
        summary=summary
    )


# ─── AI Image Analysis ────────────────────────────────────────────────────────

@router.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    """Upload a drawer/furniture photo and get AI-suggested configuration"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Потрібно завантажити зображення (jpg, png і ін.)")

    image_bytes = await file.read()
    if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(400, "Файл завеликий (макс. 10МБ)")

    result = await analyze_drawer_image(image_bytes, file.content_type)
    return result


# ─── Quotes (save/list) ───────────────────────────────────────────────────────

@router.post("/save-quote")
def save_quote(inp: DrawerInput, result: CalculationResult, db: Session = Depends(get_db)):
    quote = CalcQuote(
        client_name=inp.client_name,
        input_json=inp.model_dump_json(),
        result_json=result.model_dump_json(),
        total_price=result.grand_total,
        notes=inp.notes
    )
    db.add(quote); db.commit(); db.refresh(quote)
    return {"id": quote.id, "total_price": float(quote.total_price)}

@router.get("/quotes", response_model=List[QuoteOut])
def get_quotes(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(CalcQuote).order_by(CalcQuote.created_at.desc()).limit(limit).all()
