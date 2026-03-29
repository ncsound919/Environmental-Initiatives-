"""
ECOS Revenue Engine - Marketplace Router
Listing, purchasing, royalties for algorithms, datasets, templates, services
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/api/marketplace", tags=["marketplace"])


class ProductType(str, Enum):
    ALGORITHM = "algorithm"     # ML models, optimization solvers
    DATASET = "dataset"         # Training data, sensor readings
    TEMPLATE = "template"       # Project blueprints, configs
    FIRMWARE = "firmware"       # ESP32 firmware packages
    REPORT = "report"           # Analysis reports, whitepapers
    SERVICE = "service"         # Consulting, integration help


class ProductStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class MarketplaceProduct(BaseModel):
    id: str
    seller_id: str
    project_id: Optional[int] = None  # Which of the 13 projects this serves
    title: str
    description: str
    product_type: ProductType
    price_usd: float = Field(ge=0)
    royalty_rate: float = Field(default=0.15, ge=0, le=0.5)  # 15% to ECOS
    status: ProductStatus = ProductStatus.ACTIVE
    downloads: int = 0
    revenue_generated: float = 0.0
    tags: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    preview_url: Optional[str] = None
    demo_url: Optional[str] = None


class Purchase(BaseModel):
    id: str
    product_id: str
    buyer_id: str
    seller_id: str
    price_paid: float
    platform_fee: float
    seller_payout: float
    purchased_at: datetime = Field(default_factory=datetime.now)
    license_key: Optional[str] = None


class ProductCreate(BaseModel):
    seller_id: str
    project_id: Optional[int] = Field(None, ge=1, le=13)
    title: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=20)
    product_type: ProductType
    price_usd: float = Field(ge=0, le=50000)
    tags: List[str] = []
    preview_url: Optional[str] = None


PRODUCTS_DB: dict = {}
PURCHASES_DB: dict = {}

PLATFORM_FEE = 0.15  # 15% platform cut


@router.get("/", response_model=List[MarketplaceProduct])
async def list_products(
    project_id: Optional[int] = None,
    product_type: Optional[ProductType] = None,
    max_price: Optional[float] = None,
    free_only: bool = False
):
    products = [p for p in PRODUCTS_DB.values() if p.status == ProductStatus.ACTIVE]
    if project_id:
        products = [p for p in products if p.project_id == project_id]
    if product_type:
        products = [p for p in products if p.product_type == product_type]
    if max_price is not None:
        products = [p for p in products if p.price_usd <= max_price]
    if free_only:
        products = [p for p in products if p.price_usd == 0]
    return sorted(products, key=lambda x: x.downloads, reverse=True)


@router.post("/list", response_model=MarketplaceProduct)
async def list_product(product: ProductCreate):
    product_id = f"MP{len(PRODUCTS_DB) + 1:05d}"
    new_product = MarketplaceProduct(
        id=product_id,
        seller_id=product.seller_id,
        project_id=product.project_id,
        title=product.title,
        description=product.description,
        product_type=product.product_type,
        price_usd=product.price_usd,
        tags=product.tags,
        preview_url=product.preview_url
    )
    PRODUCTS_DB[product_id] = new_product
    return new_product


@router.post("/{product_id}/purchase", response_model=Purchase)
async def purchase_product(product_id: str, buyer_id: str):
    if product_id not in PRODUCTS_DB:
        raise HTTPException(404, "Product not found")
    product = PRODUCTS_DB[product_id]
    if product.status != ProductStatus.ACTIVE:
        raise HTTPException(400, f"Product is {product.status}")

    platform_fee = round(product.price_usd * PLATFORM_FEE, 2)
    seller_payout = round(product.price_usd - platform_fee, 2)
    import secrets
    license_key = secrets.token_urlsafe(16) if product.price_usd > 0 else None

    purchase = Purchase(
        id=f"PUR{len(PURCHASES_DB) + 1:05d}",
        product_id=product_id,
        buyer_id=buyer_id,
        seller_id=product.seller_id,
        price_paid=product.price_usd,
        platform_fee=platform_fee,
        seller_payout=seller_payout,
        license_key=license_key
    )
    PURCHASES_DB[purchase.id] = purchase
    product.downloads += 1
    product.revenue_generated += product.price_usd
    return purchase


@router.get("/seller/{seller_id}/earnings")
async def get_seller_earnings(seller_id: str):
    purchases = [p for p in PURCHASES_DB.values() if p.seller_id == seller_id]
    total_revenue = sum(p.price_paid for p in purchases)
    total_payout = sum(p.seller_payout for p in purchases)
    platform_fees = sum(p.platform_fee for p in purchases)
    return {
        "seller_id": seller_id,
        "total_sales": len(purchases),
        "gross_revenue_usd": total_revenue,
        "net_payout_usd": total_payout,
        "platform_fees_usd": platform_fees,
    }


@router.get("/stats/overview")
async def get_marketplace_stats():
    total_gmv = sum(p.price_paid for p in PURCHASES_DB.values())
    platform_revenue = sum(p.platform_fee for p in PURCHASES_DB.values())
    by_type = {}
    for p in PRODUCTS_DB.values():
        by_type[p.product_type] = by_type.get(p.product_type, 0) + 1
    return {
        "total_products": len(PRODUCTS_DB),
        "total_transactions": len(PURCHASES_DB),
        "gross_merchandise_value_usd": total_gmv,
        "platform_revenue_usd": platform_revenue,
        "products_by_type": by_type,
        "top_products": sorted(
            [{"id": p.id, "title": p.title, "downloads": p.downloads}
             for p in PRODUCTS_DB.values()],
            key=lambda x: x["downloads"], reverse=True
        )[:10]
    }
