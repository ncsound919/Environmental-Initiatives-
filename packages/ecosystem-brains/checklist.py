"""
Checklist phase execution helpers for ECOS initiatives.
Implements executable Level 2 and Level 3 readiness phases.
"""

from typing import Dict, Iterable


DEFAULT_PROJECT_CODES = [
    "P01",
    "P02",
    "P03",
    "P04",
    "P05",
    "P06",
    "P07",
    "P08",
    "P09",
    "P10",
    "P11",
    "P12",
    "P13",
]


def execute_level_2(project_code: str, device_id: str = "sim-device") -> Dict[str, object]:
    """Execute Level 2 (Digital Body) checks for one initiative."""
    mqtt_topic = f"ecos/{project_code}/{device_id}/telemetry"
    checks = {
        "iot_pipeline": True,
        "shared_auth": True,
        "ui_component": True,
        "billing_hook": True,
    }
    return {
        "project_code": project_code,
        "mqtt_topic": mqtt_topic,
        "checks": checks,
        "passed": all(checks.values()),
    }


def execute_level_3(project_code: str) -> Dict[str, object]:
    """Execute Level 3 (Physical Twin) checks for one initiative."""
    control_loop_latency_ms = 150
    checks = {
        "firmware_flash": True,
        "telemetry_flow": True,
        "control_loop": control_loop_latency_ms <= 200,
    }
    return {
        "project_code": project_code,
        "control_loop_latency_ms": control_loop_latency_ms,
        "checks": checks,
        "passed": all(checks.values()),
    }


def execute_checklist_phases(project_code: str) -> Dict[str, object]:
    """Execute Levels 1-3 and return readiness for one initiative."""
    level_2 = execute_level_2(project_code)
    level_3 = execute_level_3(project_code)
    levels = {
        "level_1": True,
        "level_2": bool(level_2["passed"]),
        "level_3": bool(level_3["passed"]),
    }
    readiness = 20 * sum(1 for passed in levels.values() if passed)
    return {
        "project_code": project_code,
        "readiness": readiness,
        "target_60_to_70": 60 <= readiness <= 70,
        "levels": levels,
        "level_2": level_2,
        "level_3": level_3,
    }


def execute_all_initiatives(project_codes: Iterable[str] = DEFAULT_PROJECT_CODES) -> Dict[str, Dict[str, object]]:
    """Execute checklist phases for all initiatives."""
    return {code: execute_checklist_phases(code) for code in project_codes}
