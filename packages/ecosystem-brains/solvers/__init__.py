"""
Solvers Module - Shared optimization logic for ECOS projects
Supports: OR-Tools, Linear Programming, Graph Theory
"""

from typing import Dict, List, Optional, Any
import numpy as np
from ortools.linear_solver import pywraplp
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus


def optimize_nutrient_cycle(
    waste_inputs: Dict[str, float],
    crop_demands: Dict[str, float]
) -> Dict[str, Any]:
    """
    Nutrient cycle optimization for Closed-Loop Farm (#3)
    Uses OR-Tools linear programming to balance waste inputs with crop demands
    
    Args:
        waste_inputs: Available nutrients from waste {N, P, K} in kg
        crop_demands: Required nutrients for crops {N, P, K} in kg
        
    Returns:
        Optimization solution with allocation plan
    """
    solver = pywraplp.Solver.CreateSolver('GLOP')
    
    if not solver:
        return {'status': 'error', 'message': 'Solver not available'}
    
    # Variables: how much of each nutrient to allocate
    n_alloc = solver.NumVar(0, waste_inputs['N'], 'n_alloc')
    p_alloc = solver.NumVar(0, waste_inputs['P'], 'p_alloc')
    k_alloc = solver.NumVar(0, waste_inputs['K'], 'k_alloc')
    
    # Constraints: meet crop demands
    solver.Add(n_alloc >= crop_demands['N'])
    solver.Add(p_alloc >= crop_demands['P'])
    solver.Add(k_alloc >= crop_demands['K'])
    
    # Objective: minimize waste
    objective = solver.Objective()
    objective.SetCoefficient(n_alloc, 1)
    objective.SetCoefficient(p_alloc, 1)
    objective.SetCoefficient(k_alloc, 1)
    objective.SetMinimization()
    
    status = solver.Solve()
    
    if status == pywraplp.Solver.OPTIMAL:
        return {
            'status': 'optimal',
            'allocation': {
                'N': n_alloc.solution_value(),
                'P': p_alloc.solution_value(),
                'K': k_alloc.solution_value(),
            },
            'waste': {
                'N': waste_inputs['N'] - n_alloc.solution_value(),
                'P': waste_inputs['P'] - p_alloc.solution_value(),
                'K': waste_inputs['K'] - k_alloc.solution_value(),
            },
            'objective_value': solver.Objective().Value(),
        }
    else:
        return {'status': 'infeasible', 'message': 'No solution found'}


def optimize_awg_schedule(
    humidity_forecast: List[float],
    energy_prices: List[float],
    target_liters: float
) -> Dict[str, Any]:
    """
    AWG run schedule optimization (#9)
    Minimize energy cost while meeting water production targets
    
    Args:
        humidity_forecast: Predicted humidity for next N hours
        energy_prices: Energy prices for next N hours ($/kWh)
        target_liters: Required water production (liters)
        
    Returns:
        Optimal run schedule
    """
    hours = len(humidity_forecast)
    
    # Create LP problem
    prob = LpProblem("AWG_Schedule", LpMinimize)
    
    # Decision variables: binary run/no-run for each hour
    run = [LpVariable(f"run_hour_{i}", cat='Binary') for i in range(hours)]
    
    # Water production rate (liters/hour) depends on humidity
    # Simplified model: production = humidity * 0.1
    production_rate = [h * 0.1 for h in humidity_forecast]
    
    # Constraint: meet production target
    prob += lpSum([run[i] * production_rate[i] for i in range(hours)]) >= target_liters
    
    # Objective: minimize energy cost
    # Assume 2 kWh per hour of operation
    energy_per_hour = 2.0
    prob += lpSum([run[i] * energy_prices[i] * energy_per_hour for i in range(hours)])
    
    # Solve
    prob.solve()
    
    if LpStatus[prob.status] == 'Optimal':
        schedule = [int(run[i].varValue) for i in range(hours)]
        total_production = sum([schedule[i] * production_rate[i] for i in range(hours)])
        total_cost = sum([schedule[i] * energy_prices[i] * energy_per_hour for i in range(hours)])
        
        return {
            'status': 'optimal',
            'schedule': schedule,
            'total_production_liters': total_production,
            'total_cost_usd': total_cost,
            'cost_per_liter': total_cost / total_production if total_production > 0 else 0,
        }
    else:
        return {'status': 'infeasible', 'message': 'No solution found'}


def optimize_geothermal_flow(
    building_loads: Dict[str, float],
    ground_temp: float,
    available_capacity: float
) -> Dict[str, Any]:
    """
    Geothermal network flow optimization (#10)
    Balance heat loads between buildings using graph theory
    
    Args:
        building_loads: Required heat for each building {building_id: kW}
        ground_temp: Current ground loop temperature (celsius)
        available_capacity: Total system capacity (kW)
        
    Returns:
        Flow allocation for each building
    """
    solver = pywraplp.Solver.CreateSolver('GLOP')
    
    if not solver:
        return {'status': 'error', 'message': 'Solver not available'}
    
    buildings = list(building_loads.keys())
    
    # Variables: heat allocation to each building
    allocations = {}
    for building in buildings:
        allocations[building] = solver.NumVar(0, building_loads[building], f'alloc_{building}')
    
    # Constraint: total allocation <= available capacity
    solver.Add(solver.Sum([allocations[b] for b in buildings]) <= available_capacity)
    
    # Objective: maximize satisfied demand (prioritize critical buildings equally)
    objective = solver.Objective()
    for building in buildings:
        objective.SetCoefficient(allocations[building], 1)
    objective.SetMaximization()
    
    status = solver.Solve()
    
    if status == pywraplp.Solver.OPTIMAL:
        result = {
            'status': 'optimal',
            'allocations': {b: allocations[b].solution_value() for b in buildings},
            'total_allocated': sum([allocations[b].solution_value() for b in buildings]),
            'capacity_utilization': sum([allocations[b].solution_value() for b in buildings]) / available_capacity,
        }
        
        # Calculate unmet demand
        unmet = {b: max(0, building_loads[b] - allocations[b].solution_value()) for b in buildings}
        result['unmet_demand'] = unmet
        
        return result
    else:
        return {'status': 'infeasible', 'message': 'No solution found'}


def optimize_fungal_match(soil_data: Dict[str, float]) -> Dict[str, Any]:
    """
    Fungal strain recommendation for Symbiosis (#2)
    Simple ML-based matching (placeholder for scikit-learn model)
    
    Args:
        soil_data: Soil characteristics {pH, moisture, NPK, temp}
        
    Returns:
        Recommended fungal strain and expected yield increase
    """
    # Simplified rule-based system (in production, use trained ML model)
    ph = soil_data.get('pH', 7.0)
    moisture = soil_data.get('moisture', 50.0)
    
    if ph < 6.0:
        strain = "Acidophilus_Strain_A"
        yield_increase = 0.25
    elif ph > 7.5:
        strain = "Alkalophilus_Strain_B"
        yield_increase = 0.20
    else:
        strain = "Neutral_Strain_C"
        yield_increase = 0.30
    
    # Adjust for moisture
    if moisture < 40:
        yield_increase *= 0.8
    elif moisture > 70:
        yield_increase *= 0.9
    
    return {
        'recommended_strain': strain,
        'expected_yield_increase': yield_increase,
        'confidence': 0.85,
        'soil_compatibility': 'high' if 6.0 <= ph <= 7.5 else 'medium',
    }


# Export main solver functions
__all__ = [
    'optimize_nutrient_cycle',
    'optimize_awg_schedule',
    'optimize_geothermal_flow',
    'optimize_fungal_match',
]
