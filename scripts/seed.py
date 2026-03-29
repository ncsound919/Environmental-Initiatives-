#!/usr/bin/env python3
"""
ECOS Database Seed Script
Populates PostgreSQL with realistic test data for all 13 projects.
Run: python scripts/seed.py
"""
import os
import random
import datetime
import asyncio
from typing import Any

try:
    import asyncpg
except ImportError:
    print("Install asyncpg: pip install asyncpg")
    raise

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ecos:ecos_dev@localhost:5432/ecos_dev")

PROJECTS = [
    {"id": 1,  "code": "P01", "name": "EcoHomes OS",    "description": "Parametric foam home design & BOM generation", "zone": "A", "status": "active"},
    {"id": 2,  "code": "P02", "name": "AgriConnect",    "description": "Fungal strain & mycorrhizal network recommendation", "zone": "C", "status": "active"},
    {"id": 3,  "code": "P03", "name": "RegeneraFarm",   "description": "Nutrient cycle optimization for regenerative agriculture", "zone": "C", "status": "active"},
    {"id": 4,  "code": "P04", "name": "HempMobility",   "description": "Hemp composite material testing & certification", "zone": "B", "status": "active"},
    {"id": 5,  "code": "P05", "name": "LumiFreq",       "description": "Spectral light recipe control for greenhouse crops", "zone": "C", "status": "active"},
    {"id": 6,  "code": "P06", "name": "NucleoSim",      "description": "Small modular reactor physics simulation", "zone": "D", "status": "active"},
    {"id": 7,  "code": "P07", "name": "PlastiCycle",    "description": "Microbial plastic degradation bioprocess control", "zone": "D", "status": "active"},
    {"id": 8,  "code": "P08", "name": "EverLume",       "description": "Bayesian LED failure prediction & maintenance", "zone": "A", "status": "active"},
    {"id": 9,  "code": "P09", "name": "AquaGen",        "description": "Atmospheric water generation with humidity forecasting", "zone": "B", "status": "active"},
    {"id": 10, "code": "P10", "name": "ThermalGrid",    "description": "Geothermal heat flow optimization for buildings", "zone": "B", "status": "active"},
    {"id": 11, "code": "P11", "name": "BioSynth",       "description": "Microbiome analytics & CRISPR strain tracking platform", "zone": "D", "status": "active"},
    {"id": 12, "code": "P12", "name": "SolarShare",     "description": "Community solar irradiance forecasting & P2P trading", "zone": "B", "status": "active"},
    {"id": 13, "code": "P13", "name": "MicroHydro",     "description": "Run-of-river LSTM stream flow forecasting", "zone": "B", "status": "active"},
]

DEVICES = [
    {"project_id": 9,  "device_id": "AWG-001",    "device_type": "ESP32", "firmware_version": "1.2.0"},
    {"project_id": 9,  "device_id": "AWG-002",    "device_type": "ESP32", "firmware_version": "1.2.0"},
    {"project_id": 12, "device_id": "SOLAR-001",  "device_type": "ESP32", "firmware_version": "1.1.3"},
    {"project_id": 10, "device_id": "GEO-001",    "device_type": "ESP32", "firmware_version": "1.0.8"},
    {"project_id": 8,  "device_id": "BULB-001",   "device_type": "ESP32", "firmware_version": "1.3.1"},
    {"project_id": 5,  "device_id": "LUMI-001",   "device_type": "ESP32", "firmware_version": "1.1.0"},
    {"project_id": 13, "device_id": "HYDRO-001",  "device_type": "ESP32", "firmware_version": "1.0.5"},
]


async def seed_projects(conn: asyncpg.Connection) -> None:
    print("Seeding projects...")
    for proj in PROJECTS:
        await conn.execute(
            """
            INSERT INTO projects (id, code, name, description, zone, status, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, NOW())
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                status = EXCLUDED.status
            """,
            proj["id"], proj["code"], proj["name"],
            proj["description"], proj["zone"], proj["status"],
        )
    print(f"  Seeded {len(PROJECTS)} projects")


async def seed_devices(conn: asyncpg.Connection) -> None:
    print("Seeding IoT devices...")
    for dev in DEVICES:
        await conn.execute(
            """
            INSERT INTO devices (device_id, project_id, device_type, firmware_version, online, last_seen, created_at)
            VALUES ($1, $2, $3, $4, TRUE, NOW(), NOW())
            ON CONFLICT (device_id) DO UPDATE SET
                firmware_version = EXCLUDED.firmware_version,
                last_seen = NOW()
            """,
            dev["device_id"], dev["project_id"],
            dev["device_type"], dev["firmware_version"],
        )
    print(f"  Seeded {len(DEVICES)} devices")


async def seed_telemetry(conn: asyncpg.Connection, records_per_device: int = 100) -> None:
    """Generate realistic telemetry time-series for the past 24 hours."""
    print(f"Seeding telemetry ({records_per_device} records per device)...")
    now = datetime.datetime.utcnow()
    total = 0
    for dev in DEVICES:
        for i in range(records_per_device):
            ts = now - datetime.timedelta(minutes=i * 15)
            # Realistic sensor values per project
            pid = dev["project_id"]
            if pid == 9:   # AquaGen
                payload = {"humidity": round(random.uniform(55, 85), 1), "water_ml": round(random.uniform(50, 200), 1), "power_w": round(random.uniform(80, 150), 1)}
            elif pid == 12: # SolarShare
                hour_factor = max(0.0, 1.0 - abs((ts.hour - 12) / 6.0))
                payload = {"irradiance_w_m2": round(1000 * hour_factor * random.uniform(0.8, 1.0), 1), "power_kw": round(5.0 * hour_factor, 2)}
            elif pid == 10: # ThermalGrid
                payload = {"inlet_temp_c": round(random.uniform(8, 15), 1), "outlet_temp_c": round(random.uniform(18, 25), 1), "flow_lpm": round(random.uniform(20, 60), 1)}
            elif pid == 8:  # EverLume
                payload = {"voltage_v": round(random.uniform(11.8, 12.5), 2), "current_a": round(random.uniform(0.5, 1.2), 2), "temp_c": round(random.uniform(35, 55), 1)}
            elif pid == 5:  # LumiFreq
                payload = {"ppfd_umol": round(random.uniform(200, 800), 1), "red_pct": 65, "blue_pct": 20, "far_red_pct": 15}
            elif pid == 13: # MicroHydro
                payload = {"flow_m3s": round(random.uniform(0.5, 3.0), 3), "head_m": round(random.uniform(4, 12), 1), "power_kw": round(random.uniform(1.5, 8.0), 2)}
            else:
                payload = {"value": round(random.uniform(0, 100), 2), "unit": "generic"}

            await conn.execute(
                """
                INSERT INTO telemetry (device_id, project_id, timestamp, payload, created_at)
                VALUES ($1, $2, $3, $4::jsonb, NOW())
                ON CONFLICT DO NOTHING
                """,
                dev["device_id"], dev["project_id"], ts,
                str(payload).replace("'", '"'),
            )
            total += 1
    print(f"  Seeded {total} telemetry records")


async def seed_users(conn: asyncpg.Connection) -> None:
    """Create demo users for all roles."""
    print("Seeding demo users...")
    users = [
        {"auth0_id": "auth0|demo_admin",    "email": "admin@ecos.app",    "name": "ECOS Admin",    "plan": "enterprise"},
        {"auth0_id": "auth0|demo_operator", "email": "ops@ecos.app",      "name": "Site Operator", "plan": "pro"},
        {"auth0_id": "auth0|demo_viewer",   "email": "viewer@ecos.app",   "name": "Data Viewer",   "plan": "free"},
    ]
    for user in users:
        await conn.execute(
            """
            INSERT INTO users (auth0_id, email, name, plan, created_at)
            VALUES ($1, $2, $3, $4, NOW())
            ON CONFLICT (auth0_id) DO UPDATE SET
                email = EXCLUDED.email,
                plan = EXCLUDED.plan
            """,
            user["auth0_id"], user["email"], user["name"], user["plan"],
        )
    print(f"  Seeded {len(users)} users")


async def main() -> None:
    print(f"Connecting to {DATABASE_URL[:40]}...")
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await seed_projects(conn)
        await seed_devices(conn)
        await seed_telemetry(conn)
        await seed_users(conn)
        print("\nSeed complete! Run 'curl http://localhost:8000/projects' to verify.")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
