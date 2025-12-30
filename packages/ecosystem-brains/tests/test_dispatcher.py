"""
Unit tests for ecosystem-brains dispatcher module
Validates Level 1 completion criteria
"""

import pytest
from dispatcher import EcosDispatcher, dispatch


def test_dispatcher_solar_awg():
    """Test Solar-AWG coordination"""
    solar_forecast = {'predicted_irradiance': 800.0}  # W/m²
    humidity_forecast = {'predicted_humidity': 75.0}  # %
    water_demand = 50.0  # liters
    
    result = dispatch(
        'coordinate_solar_awg',
        solar_forecast=solar_forecast,
        humidity_forecast=humidity_forecast,
        water_demand=water_demand
    )
    
    assert result['status'] == 'dispatched'
    assert result['action']['project'] == 'P09_AWG'
    assert result['action']['command'] == 'START_PRODUCTION'
    print(f"✓ Solar-AWG coordination: {result['status']}")


def test_dispatcher_geothermal_solar():
    """Test Geothermal-Solar heat storage coordination"""
    solar_excess = 50.0  # kW
    geothermal_capacity = 100.0  # kW
    
    result = dispatch(
        'coordinate_geothermal_solar',
        solar_excess=solar_excess,
        geothermal_capacity=geothermal_capacity
    )
    
    assert result['status'] == 'dispatched'
    assert result['action']['project'] == 'P10_GEOTHERMAL'
    assert result['action']['command'] == 'STORE_HEAT'
    print(f"✓ Geothermal-Solar coordination: {result['action']['heat_kw']:.1f}kW stored")


def test_dispatcher_queue():
    """Test command queue management"""
    # Clear queue first
    dispatch('clear_queue')
    
    # Add commands
    dispatch('coordinate_solar_awg',
             solar_forecast={'predicted_irradiance': 800.0},
             humidity_forecast={'predicted_humidity': 75.0},
             water_demand=50.0)
    
    # Get queue
    result = dispatch('get_queue')
    assert 'queue' in result
    assert len(result['queue']) > 0
    print(f"✓ Command queue: {len(result['queue'])} commands pending")
    
    # Clear queue
    dispatch('clear_queue')
    result = dispatch('get_queue')
    assert len(result['queue']) == 0
    print("✓ Command queue cleared")


def test_dispatcher_status():
    """Test system status retrieval"""
    result = dispatch('status')
    
    assert 'timestamp' in result
    assert 'system_health' in result
    assert result['system_health'] == 'operational'
    print(f"✓ System status: {result['system_health']}")


if __name__ == '__main__':
    print("\n=== ECOS Dispatcher Module Tests ===\n")
    test_dispatcher_solar_awg()
    test_dispatcher_geothermal_solar()
    test_dispatcher_queue()
    test_dispatcher_status()
    print("\n✓ All dispatcher tests passed!\n")
