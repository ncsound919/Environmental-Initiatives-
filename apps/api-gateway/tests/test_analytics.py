"""
Smoke tests for the ECOS API Gateway analytics pipeline.

Verifies analytics are computed from REAL ingested telemetry (no fabricated
data): empty store reports no_data, ingested readings produce real aggregates,
and carbon credits derive from the real carbon-credit engine.
"""
import sys
import os
import importlib.util
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

_GATEWAY_DIR = os.path.join(os.path.dirname(__file__), "..")


def _load_main() -> None:
    """Load the gateway main.py under a unique module name so it never collides
    with the revenue API's equally-named main when both test suites run in one
    process. The gateway dir is pinned to the front of sys.path and any cached
    `routers` package (from the revenue API) is evicted first."""
    path = os.path.join(_GATEWAY_DIR, "main.py")
    sys.path.insert(0, _GATEWAY_DIR)
    sys.modules.pop("routers", None)
    spec = importlib.util.spec_from_file_location("ecos_gateway_main", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["ecos_gateway_main"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)


_load_main()

from ecos_gateway_main import app  # noqa: E402


@pytest.fixture()
def client():
    from telemetry_store import TELEMETRY
    TELEMETRY.clear()
    return TestClient(app)


def _ingest(client, project_code="P12", measurement_type="energy", value=5.0, unit="kwh"):
    now = datetime.now(timezone.utc)
    return client.post(
        "/api/iot/ingest",
        json={
            "sensor_id": "s1",
            "project_code": project_code,
            "device_id": "d1",
            "measurement_type": measurement_type,
            "measurement_value": value,
            "unit": unit,
            "timestamp": now.isoformat(),
            "quality_flag": "valid",
        },
    )


def test_empty_store_does_not_fabricate(client):
    r = client.get("/api/analytics/ecosystem")
    assert r.status_code == 200
    body = r.json()
    assert body["data_source"] == "REAL_TELEMETRY"
    assert body["summary"]["total_readings"] == 0
    assert body["summary"]["projects_with_data"] == 0
    for project in body["projects"]:
        assert project["has_data"] is False


def test_ingest_persists_and_analytics_reflect_it(client):
    assert _ingest(client).status_code == 200
    assert _ingest(client, measurement_type="irradiance", value=800.0, unit="W/m2").status_code == 200

    r = client.get("/api/analytics/ecosystem").json()
    p12 = next(p for p in r["projects"] if p["project"]["id"] == "P12")
    assert p12["has_data"] is True
    assert p12["reading_count"] == 2
    assert p12["energy_kwh"] == 5.0
    assert r["summary"]["total_readings"] == 2

    project = client.get("/api/analytics/project/P12").json()
    assert project["data_source"] == "REAL_TELEMETRY"
    assert project["has_data"] is True


def test_carbon_credits_from_real_energy(client):
    for i in range(10):
        assert _ingest(client, value=5.0 + (i % 3)).status_code == 200

    body = client.get("/api/analytics/carbon-credits").json()
    assert body["data_source"] == "REAL_TELEMETRY"
    assert body["verification_status"] == "unverified"
    assert body["total_tonnes_co2e"] > 0
    assert body["estimated_market_value_usd"]["verra_vcs"] > 0
    p12 = next(p for p in body["projects"] if p["project_id"] == "P12")
    assert p12["tonnes_co2e"] > 0


def test_anomaly_detect_is_real_computation(client):
    body = client.post(
        "/api/analytics/anomaly-detect",
        json={"project_id": "P12", "readings": [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 100]},
    ).json()
    assert body["data_source"] == "REAL_TELEMETRY"
    assert body["anomaly_count"] == 1
    assert body["anomalies"][0]["value"] == 100


def test_gateway_web_contract_endpoints(client):
    assert client.get("/health").status_code == 200
    assert client.get("/projects").status_code == 200
    assert client.get("/api/checklist/readiness").status_code == 200
    assert client.get("/hardware/manifest").status_code == 200
    assert client.get("/api/analytics/ecosystem").status_code == 200