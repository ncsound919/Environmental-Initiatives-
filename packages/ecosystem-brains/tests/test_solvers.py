"""
Unit tests for ecosystem-brains solvers module
Validates Level 1 completion criteria
"""

from solvers import (
    optimize_nutrient_cycle,
    optimize_awg_schedule,
    optimize_geothermal_flow,
    optimize_fungal_match,
)


def test_optimize_nutrient_cycle():
    """Test Closed-Loop Farm (#3) nutrient optimization"""
    waste_inputs = {'N': 100.0, 'P': 50.0, 'K': 75.0}  # kg
    crop_demands = {'N': 80.0, 'P': 40.0, 'K': 60.0}  # kg
    
    result = optimize_nutrient_cycle(waste_inputs, crop_demands)
    
    assert result['status'] == 'optimal'
    assert 'allocation' in result
    assert result['allocation']['N'] >= crop_demands['N']
    assert result['allocation']['P'] >= crop_demands['P']
    assert result['allocation']['K'] >= crop_demands['K']
    print(f"✓ Farm (#3) optimization: N={result['allocation']['N']:.1f}kg allocated")


def test_optimize_awg_schedule():
    """Test AWG (#9) schedule optimization"""
    humidity_forecast = [60, 65, 75, 80, 85, 70]  # %
    energy_prices = [0.10, 0.12, 0.08, 0.09, 0.15, 0.11]  # $/kWh
    target_liters = 100.0
    
    result = optimize_awg_schedule(humidity_forecast, energy_prices, target_liters)
    
    assert result['status'] == 'optimal'
    assert 'schedule' in result
    assert len(result['schedule']) == len(humidity_forecast)
    assert result['total_production_liters'] >= target_liters
    print(f"✓ AWG (#9) optimization: ${result['cost_per_liter']:.3f}/liter")


def test_optimize_geothermal_flow():
    """Test Geothermal (#10) flow optimization"""
    building_loads = {
        'building_A': 50.0,  # kW
        'building_B': 30.0,
        'building_C': 40.0,
    }
    ground_temp = 15.0  # celsius
    available_capacity = 100.0  # kW
    
    result = optimize_geothermal_flow(building_loads, ground_temp, available_capacity)
    
    assert result['status'] == 'optimal'
    assert 'allocations' in result
    assert result['total_allocated'] <= available_capacity
    assert result['capacity_utilization'] <= 1.0
    print(f"✓ Geothermal (#10) optimization: {result['capacity_utilization']:.1%} capacity used")


def test_optimize_fungal_match():
    """Test Symbiosis (#2) fungal strain recommendation"""
    soil_data = {
        'pH': 6.5,
        'moisture': 55.0,  # %
        'N': 20.0,
        'P': 15.0,
        'K': 25.0,
        'temp': 22.0,  # celsius
    }
    
    result = optimize_fungal_match(soil_data)
    
    assert 'recommended_strain' in result
    assert 'expected_yield_increase' in result
    assert 0 <= result['expected_yield_increase'] <= 1.0
    assert result['confidence'] > 0
    print(f"✓ Symbiosis (#2) optimization: {result['expected_yield_increase']:.1%} yield increase")


if __name__ == '__main__':
    print("\n=== ECOS Solvers Module Tests ===\n")
    test_optimize_nutrient_cycle()
    test_optimize_awg_schedule()
    test_optimize_geothermal_flow()
    test_optimize_fungal_match()
    print("\n✓ All solver tests passed!\n")
