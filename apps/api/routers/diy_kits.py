"""
ECOS DIY Kits Router - Physical hardware kits tied to each of the 13 projects
Catalog, ordering, BOM generation, assembly tracking, community builds
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, computed_field
from typing import List, Optional
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/api/kits", tags=["diy-kits"])


class KitDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FULFILLING = "fulfilling"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    ASSEMBLED = "assembled"


class BOMItem(BaseModel):
    part_name: str
    part_number: Optional[str] = None
    quantity: int
    unit_price_usd: float
    supplier: Optional[str] = None
    notes: Optional[str] = None

    # Web-contract aliases (see apps/web/src/app/diy-kits/page.tsx)
    @computed_field
    @property
    def component(self) -> str:
        return self.part_name

    @computed_field
    @property
    def unit_cost_usd(self) -> float:
        return self.unit_price_usd

    @computed_field
    @property
    def qty(self) -> int:
        return self.quantity


class DIYKit(BaseModel):
    id: str
    project_id: int  # Maps to one of the 13 projects
    project_name: str
    title: str
    description: str
    difficulty: KitDifficulty
    price_usd: float
    founder_price_usd: float  # 25% off for Founder members
    bom: List[BOMItem] = []
    estimated_build_hours: float
    learning_outcomes: List[str] = []
    firmware_url: Optional[str] = None
    video_guide_url: Optional[str] = None
    stock: int = 100
    units_sold: int = 0
    community_builds: int = 0
    created_at: datetime = Field(default_factory=datetime.now)

    # Web-contract alias
    @computed_field
    @property
    def category(self) -> str:
        return self.project_name


class KitOrder(BaseModel):
    id: str
    kit_id: str
    user_id: str
    quantity: int
    unit_price: float
    total_price: float
    member_discount_applied: bool = False
    status: OrderStatus = OrderStatus.PENDING
    shipping_address: Optional[str] = None
    tracking_number: Optional[str] = None
    ordered_at: datetime = Field(default_factory=datetime.now)


class BuildLog(BaseModel):
    id: str
    kit_id: str
    user_id: str
    progress_pct: int = Field(ge=0, le=100)
    notes: str = ""
    photos_count: int = 0
    completed: bool = False
    xp_earned: int = 0
    logged_at: datetime = Field(default_factory=datetime.now)


# ---- Catalog pre-populated with one kit per project ----
KITS_CATALOG: List[DIYKit] = [
    DIYKit(
        id="KIT-P01", project_id=1, project_name="EcoHomes OS",
        title="Foam Home Sensor Hub", difficulty=KitDifficulty.BEGINNER,
        description="Build an ESP32 sensor hub that monitors home temperature and humidity, publishing live MQTT telemetry to EcoHomes OS.",
        price_usd=79.99, founder_price_usd=59.99,
        estimated_build_hours=4, learning_outcomes=["ESP32 setup", "MQTT", "Home automation"],
        bom=[
            BOMItem(part_name="ESP32 DevKit", quantity=1, unit_price_usd=8.99),
            BOMItem(part_name="DHT22 Temp/Humidity", quantity=2, unit_price_usd=5.49),
            BOMItem(part_name="USB-C Power Module", quantity=1, unit_price_usd=3.99),
        ]
    ),
    DIYKit(
        id="KIT-P02", project_id=2, project_name="AgriConnect",
        title="Mycelium Monitoring Kit", difficulty=KitDifficulty.INTERMEDIATE,
        description="Assemble a soil and CO2 monitoring rig with ML inference for precision mycelium and crop growth.",
        price_usd=119.99, founder_price_usd=89.99,
        estimated_build_hours=6, learning_outcomes=["Soil sensing", "pH monitoring", "ML inference"],
        bom=[
            BOMItem(part_name="ESP32 + Soil Sensor", quantity=1, unit_price_usd=14.99),
            BOMItem(part_name="pH Probe Module", quantity=1, unit_price_usd=22.50),
            BOMItem(part_name="CO2 Sensor MH-Z19", quantity=1, unit_price_usd=18.99),
        ]
    ),
    DIYKit(
        id="KIT-P05", project_id=5, project_name="LumiFreq",
        title="Grow Light Controller", difficulty=KitDifficulty.INTERMEDIATE,
        description="Control full-spectrum grow lighting with PWM dimming, spectrum presets, and photoperiod automation.",
        price_usd=149.99, founder_price_usd=112.49,
        estimated_build_hours=8,
        learning_outcomes=["PWM lighting", "Spectrum control", "Photoperiod automation"],
        bom=[
            BOMItem(part_name="ESP32 + BLE", quantity=1, unit_price_usd=9.99),
            BOMItem(part_name="LED Driver Board", quantity=2, unit_price_usd=12.99),
            BOMItem(part_name="Full Spectrum LED Strip 1m", quantity=2, unit_price_usd=14.50),
            BOMItem(part_name="LDR Sensor", quantity=1, unit_price_usd=2.99),
        ]
    ),
    DIYKit(
        id="KIT-P09", project_id=9, project_name="AquaGen",
        title="Atmospheric Water Generator Kit", difficulty=KitDifficulty.ADVANCED,
        description="Harvest drinking water from humid air using Peltier cooling, with TDS water-quality sensing.",
        price_usd=249.99, founder_price_usd=187.49,
        estimated_build_hours=16,
        learning_outcomes=["Peltier cooling", "Humidity harvesting", "Water quality sensing"],
        bom=[
            BOMItem(part_name="Peltier TEC1-12706", quantity=2, unit_price_usd=8.99),
            BOMItem(part_name="Heatsink + Fan", quantity=2, unit_price_usd=7.99),
            BOMItem(part_name="TDS Water Quality Sensor", quantity=1, unit_price_usd=12.99),
            BOMItem(part_name="ESP32 + Display", quantity=1, unit_price_usd=14.99),
        ]
    ),
    DIYKit(
        id="KIT-P12", project_id=12, project_name="SolarShare",
        title="Solar Irradiance Monitor", difficulty=KitDifficulty.BEGINNER,
        description="Measure solar irradiance and log energy data for rooftop forecasting and SolarShare analytics.",
        price_usd=59.99, founder_price_usd=44.99,
        estimated_build_hours=3,
        learning_outcomes=["Solar measurement", "Energy forecasting", "Data logging"],
        bom=[
            BOMItem(part_name="ESP32 DevKit", quantity=1, unit_price_usd=8.99),
            BOMItem(part_name="BH1750 Light Sensor", quantity=1, unit_price_usd=4.99),
            BOMItem(part_name="MicroSD Module", quantity=1, unit_price_usd=3.49),
        ]
    ),
]

KITS_DB = {k.id: k for k in KITS_CATALOG}
ORDERS_DB: dict = {}
BUILD_LOGS_DB: dict = {}


@router.get("", response_model=List[DIYKit])
async def list_kits(
    project_id: Optional[int] = None,
    difficulty: Optional[KitDifficulty] = None,
    max_price: Optional[float] = None
):
    kits = list(KITS_DB.values())
    if project_id:
        kits = [k for k in kits if k.project_id == project_id]
    if difficulty:
        kits = [k for k in kits if k.difficulty == difficulty]
    if max_price:
        kits = [k for k in kits if k.price_usd <= max_price]
    return sorted(kits, key=lambda x: x.units_sold, reverse=True)


@router.get("/{kit_id}", response_model=DIYKit)
async def get_kit(kit_id: str):
    if kit_id not in KITS_DB:
        raise HTTPException(404, f"Kit {kit_id} not found")
    return KITS_DB[kit_id]


@router.get("/{kit_id}/bom")
async def get_bom(kit_id: str):
    if kit_id not in KITS_DB:
        raise HTTPException(404, "Kit not found")
    kit = KITS_DB[kit_id]
    total_parts_cost = sum(item.quantity * item.unit_price_usd for item in kit.bom)
    return {
        "kit_id": kit_id,
        "kit_title": kit.title,
        "bom": kit.bom,
        "total_parts_cost_usd": round(total_parts_cost, 2),
        "kit_price_usd": kit.price_usd,
        "margin_usd": round(kit.price_usd - total_parts_cost, 2),
    }


class KitOrderRequest(BaseModel):
    """JSON body for POST /kits/{id}/order (web-contract shape)."""
    user_id: Optional[str] = None
    quantity: int = 1
    is_founder: bool = False


class BuildLogRequest(BaseModel):
    """JSON body for POST /kits/{id}/build-log (web-contract shape)."""
    user_id: Optional[str] = None
    progress_pct: Optional[int] = None
    notes: str = ""


@router.post("/{kit_id}/order", response_model=KitOrder)
async def order_kit(kit_id: str, body: Optional[KitOrderRequest] = None, user_id: Optional[str] = None, quantity: int = 1, is_founder: bool = False):
    user_id = (body.user_id if body and body.user_id else user_id)
    if body:
        quantity = body.quantity
        is_founder = body.is_founder
    if not user_id:
        raise HTTPException(400, "user_id is required")
    if kit_id not in KITS_DB:
        raise HTTPException(404, "Kit not found")
    if quantity < 1:
        raise HTTPException(400, "quantity must be >= 1")
    kit = KITS_DB[kit_id]
    if kit.stock < quantity:
        raise HTTPException(400, f"Only {kit.stock} in stock")

    unit_price = kit.founder_price_usd if is_founder else kit.price_usd
    total = round(unit_price * quantity, 2)

    order = KitOrder(
        id=f"ORD{len(ORDERS_DB) + 1:05d}",
        kit_id=kit_id,
        user_id=user_id,
        quantity=quantity,
        unit_price=unit_price,
        total_price=total,
        member_discount_applied=is_founder,
        status=OrderStatus.PAID,
    )
    ORDERS_DB[order.id] = order
    kit.stock -= quantity
    kit.units_sold += quantity
    return order


@router.post("/{kit_id}/build-log", response_model=BuildLog)
async def log_build_progress(kit_id: str, body: Optional[BuildLogRequest] = None, user_id: Optional[str] = None, progress_pct: Optional[int] = None, notes: str = ""):
    user_id = (body.user_id if body and body.user_id else user_id)
    if body:
        progress_pct = body.progress_pct if body.progress_pct is not None else progress_pct
        notes = body.notes
    if not user_id:
        raise HTTPException(400, "user_id is required")
    if progress_pct is None:
        raise HTTPException(400, "progress_pct is required")
    if kit_id not in KITS_DB:
        raise HTTPException(404, "Kit not found")
    if not (0 <= progress_pct <= 100):
        raise HTTPException(400, "progress_pct must be 0-100")

    xp_earned = 0
    completed = progress_pct >= 100
    if completed:
        xp_earned = 300  # Award 300 XP for kit assembly
        KITS_DB[kit_id].community_builds += 1

    log = BuildLog(
        id=f"BLD{len(BUILD_LOGS_DB) + 1:05d}",
        kit_id=kit_id,
        user_id=user_id,
        progress_pct=progress_pct,
        notes=notes,
        completed=completed,
        xp_earned=xp_earned
    )
    BUILD_LOGS_DB[log.id] = log
    return log


@router.get("/stats/overview")
async def get_kit_stats():
    total_revenue = sum(o.total_price for o in ORDERS_DB.values())
    by_kit = {}
    for kit in KITS_DB.values():
        by_kit[kit.id] = {"title": kit.title, "units_sold": kit.units_sold,
                          "community_builds": kit.community_builds}
    return {
        "total_kits": len(KITS_DB),
        "total_kits_available": len(KITS_DB),
        "total_orders": len(ORDERS_DB),
        "total_revenue_usd": round(total_revenue, 2),
        "completed_builds": sum(1 for b in BUILD_LOGS_DB.values() if b.completed),
        "community_builds": sum(k.community_builds for k in KITS_DB.values()),
        "by_kit": by_kit,
    }
