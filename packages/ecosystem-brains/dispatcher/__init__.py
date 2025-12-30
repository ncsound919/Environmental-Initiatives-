"""
Dispatcher Module - Orchestration layer for ECOS projects
Coordinates forecasts, optimization, and hardware control
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


class EcosDispatcher:
    """
    Central orchestration system for cross-project coordination.
    Receives forecasts, triggers optimizations, and dispatches commands.
    """
    
    def __init__(self):
        self.active_projects = []
        self.command_queue = []
    
    def coordinate_solar_awg(
        self,
        solar_forecast: Dict[str, float],
        humidity_forecast: Dict[str, float],
        water_demand: float
    ) -> Dict[str, Any]:
        """
        Coordinate Solar Gardens (#12) with AWG (#9)
        Trigger water production when excess solar power is available
        
        Args:
            solar_forecast: Predicted solar output
            humidity_forecast: Predicted humidity levels
            water_demand: Required water production (liters)
            
        Returns:
            Coordinated action plan
        """
        # Check if excess solar power is available
        excess_power = max(0, solar_forecast.get('predicted_irradiance', 0) - 500)  # W/m²
        
        # Check if humidity is favorable
        humidity = humidity_forecast.get('predicted_humidity', 0)
        
        if excess_power > 200 and humidity > 70:
            # Optimal conditions for AWG operation
            action = {
                'project': 'P09_AWG',
                'command': 'START_PRODUCTION',
                'duration_hours': 2,
                'expected_output': water_demand,
                'energy_source': 'solar_excess',
                'timestamp': datetime.now().isoformat(),
            }
            self.command_queue.append(action)
            
            return {
                'status': 'dispatched',
                'action': action,
                'reasoning': 'Excess solar power and high humidity detected',
            }
        else:
            return {
                'status': 'hold',
                'reasoning': f'Conditions not optimal (power={excess_power}, humidity={humidity})',
            }
    
    def coordinate_geothermal_solar(
        self,
        solar_excess: float,
        geothermal_capacity: float
    ) -> Dict[str, Any]:
        """
        Coordinate Solar (#12) waste heat with Geothermal (#10) storage
        
        Args:
            solar_excess: Excess solar power (kW)
            geothermal_capacity: Available ground loop capacity (kW)
            
        Returns:
            Heat storage command
        """
        # Calculate how much heat can be stored
        storable_heat = min(solar_excess * 0.3, geothermal_capacity)  # 30% efficiency
        
        if storable_heat > 5.0:  # Minimum threshold
            action = {
                'project': 'P10_GEOTHERMAL',
                'command': 'STORE_HEAT',
                'heat_kw': storable_heat,
                'source': 'solar_excess',
                'timestamp': datetime.now().isoformat(),
            }
            self.command_queue.append(action)
            
            return {
                'status': 'dispatched',
                'action': action,
                'reasoning': 'Solar excess heat available for ground loop storage',
            }
        else:
            return {
                'status': 'hold',
                'reasoning': 'Insufficient heat for storage',
            }
    
    def get_command_queue(self) -> List[Dict[str, Any]]:
        """
        Retrieve pending commands for hardware execution
        """
        return self.command_queue
    
    def clear_command_queue(self):
        """
        Clear executed commands
        """
        self.command_queue = []
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get overall system status across all projects
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'active_projects': len(self.active_projects),
            'pending_commands': len(self.command_queue),
            'system_health': 'operational',
        }


# Create singleton dispatcher instance
dispatcher = EcosDispatcher()


def dispatch(action: str, **kwargs) -> Dict[str, Any]:
    """
    Main dispatch function for external API calls
    
    Args:
        action: Action type (e.g., 'coordinate_solar_awg')
        **kwargs: Action-specific parameters
        
    Returns:
        Dispatch result
    """
    if action == 'coordinate_solar_awg':
        return dispatcher.coordinate_solar_awg(
            kwargs.get('solar_forecast', {}),
            kwargs.get('humidity_forecast', {}),
            kwargs.get('water_demand', 0)
        )
    elif action == 'coordinate_geothermal_solar':
        return dispatcher.coordinate_geothermal_solar(
            kwargs.get('solar_excess', 0),
            kwargs.get('geothermal_capacity', 0)
        )
    elif action == 'get_queue':
        return {'queue': dispatcher.get_command_queue()}
    elif action == 'clear_queue':
        dispatcher.clear_command_queue()
        return {'status': 'cleared'}
    elif action == 'status':
        return dispatcher.get_system_status()
    else:
        return {'status': 'error', 'message': f'Unknown action: {action}'}


__all__ = ['EcosDispatcher', 'dispatcher', 'dispatch']
