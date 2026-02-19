"""
Unit tests for checklist phase execution module.
Validates Level 2 and Level 3 readiness execution.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from checklist import (
    execute_level_2,
    execute_level_3,
    execute_checklist_phases,
    execute_all_initiatives,
)


def test_execute_level_2():
    result = execute_level_2("P09", "awg-01")
    assert result["passed"] is True
    assert result["mqtt_topic"] == "ecos/P09/awg-01/telemetry"
    print(f"✓ Level 2 executed: {result['mqtt_topic']}")


def test_execute_level_3():
    result = execute_level_3("P09")
    assert result["passed"] is True
    assert result["control_loop_latency_ms"] <= 200
    print(f"✓ Level 3 executed: {result['control_loop_latency_ms']}ms")


def test_project_readiness_hits_target_band():
    result = execute_checklist_phases("P05")
    assert result["readiness"] == 60
    assert result["target_60_to_70"] is True
    print(f"✓ Project readiness in target band: {result['readiness']}%")


def test_all_initiatives_have_target_readiness():
    results = execute_all_initiatives()
    assert len(results) == 13
    assert all(result["readiness"] >= 60 for result in results.values())
    print(f"✓ Initiatives validated: {len(results)} at >=60% readiness")


if __name__ == "__main__":
    print("\n=== ECOS Checklist Phase Tests ===\n")
    test_execute_level_2()
    test_execute_level_3()
    test_project_readiness_hits_target_band()
    test_all_initiatives_have_target_readiness()
    print("\n✓ All checklist phase tests passed!\n")
