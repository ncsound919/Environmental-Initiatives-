"""
ECOS Telemetry Store - real in-memory telemetry persistence.

Readings arrive via POST /api/iot/ingest (and MQTT bridge) and are consumed by
the /api/analytics endpoints. This module only stores what actually arrives;
analytics never fabricate readings.

In production, back this store with TimescaleDB (see the `postgres` service in
docker-compose.yml). The store interface is intentionally small so the swap is
contained to this module.
"""
from __future__ import annotations

import threading
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

_lock = threading.Lock()
# project_code -> measurement_type -> list of readings
TELEMETRY: Dict[str, Dict[str, List[Dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))


def ingest_reading(
    sensor_id: str,
    project_code: str,
    device_id: str,
    measurement_type: str,
    measurement_value: float,
    unit: str,
    timestamp: datetime,
    quality_flag: str,
) -> None:
    """Store a telemetry reading for later analytics consumption."""
    with _lock:
        TELEMETRY[project_code][measurement_type].append(
            {
                "sensor_id": sensor_id,
                "device_id": device_id,
                "measurement_value": measurement_value,
                "unit": unit,
                "timestamp": timestamp.isoformat(),
                "quality_flag": quality_flag,
            }
        )


def readings_for(project_code: str, measurement_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return stored readings for a project, optionally filtered by measurement type."""
    with _lock:
        if measurement_type:
            return list(TELEMETRY.get(project_code, {}).get(measurement_type, []))
        return [
            reading
            for series in TELEMETRY.get(project_code, {}).values()
            for reading in series
        ]


def measurement_types(project_code: str) -> List[str]:
    """List measurement types that actually have stored data for a project."""
    with _lock:
        return list(TELEMETRY.get(project_code, {}).keys())


def all_measurement_types() -> List[str]:
    with _lock:
        seen: set[str] = set()
        for series in TELEMETRY.values():
            seen.update(series.keys())
        return sorted(seen)


def project_energy_kwh(project_code: str) -> float:
    """Sum real energy readings (unit == 'kwh') for a project."""
    return sum(
        r["measurement_value"]
        for r in readings_for(project_code, "energy")
        if str(r.get("unit", "")).lower() == "kwh"
    )


def project_count(project_code: str) -> int:
    return len(readings_for(project_code))


def totals() -> Dict[str, Any]:
    """Aggregate real telemetry across all projects."""
    total_readings = sum(len(series) for series in TELEMETRY.values())
    total_energy_kwh = 0.0
    projects_with_data = 0
    for project_code in TELEMETRY:
        if project_count(project_code) > 0:
            projects_with_data += 1
        total_energy_kwh += project_energy_kwh(project_code)
    return {
        "total_readings": total_readings,
        "total_energy_kwh": round(total_energy_kwh, 2),
        "projects_with_data": projects_with_data,
        "measurement_types": all_measurement_types(),
    }
