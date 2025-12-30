"""
Forecasting Module - Shared time-series prediction for ECOS projects
Supports: Prophet, LSTM, and general time-series forecasting
"""

from typing import Dict, List, Optional, Union
import numpy as np
import pandas as pd
from prophet import Prophet
import torch
import torch.nn as nn


class LSTMForecaster(nn.Module):
    """
    LSTM model template for time-series forecasting.
    Used by: Solar (#12), Hydro (#13), AWG (#9)
    """
    
    def __init__(self, input_size: int = 1, hidden_size: int = 50, num_layers: int = 2, output_size: int = 1):
        super(LSTMForecaster, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out


class ProphetForecaster:
    """
    Prophet wrapper for time-series forecasting.
    Used by: AWG (#9), Solar (#12), Farm (#3)
    """
    
    def __init__(self, seasonality_mode: str = 'multiplicative'):
        self.model = Prophet(seasonality_mode=seasonality_mode)
        self.fitted = False
    
    def fit(self, df: pd.DataFrame):
        """
        Fit Prophet model on historical data.
        
        Args:
            df: DataFrame with 'ds' (timestamp) and 'y' (value) columns
        """
        self.model.fit(df)
        self.fitted = True
    
    def predict(self, periods: int = 24) -> pd.DataFrame:
        """
        Generate forecast for future periods.
        
        Args:
            periods: Number of time periods to forecast
            
        Returns:
            DataFrame with predictions
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before prediction")
        
        future = self.model.make_future_dataframe(periods=periods, freq='H')
        forecast = self.model.predict(future)
        return forecast


def forecast_stream_flow(historical_data: Dict[str, List[float]], hours_ahead: int = 24) -> Dict[str, float]:
    """
    Forecast stream flow for Micro-Hydro (#13)
    
    Args:
        historical_data: Dict with 'timestamp', 'flow', 'precipitation', 'temperature'
        hours_ahead: Forecast horizon
        
    Returns:
        Forecast predictions
    """
    df = pd.DataFrame(historical_data)
    df['ds'] = pd.to_datetime(df['timestamp'])
    df['y'] = df['flow']
    
    forecaster = ProphetForecaster()
    forecaster.fit(df[['ds', 'y']])
    forecast = forecaster.predict(periods=hours_ahead)
    
    return {
        'predicted_flow': float(forecast['yhat'].iloc[-1]),
        'confidence_lower': float(forecast['yhat_lower'].iloc[-1]),
        'confidence_upper': float(forecast['yhat_upper'].iloc[-1]),
    }


def forecast_solar_irradiance(historical_data: Dict[str, List[float]], hours_ahead: int = 24) -> Dict[str, float]:
    """
    Forecast solar irradiance for Solar Gardens (#12)
    
    Args:
        historical_data: Dict with 'timestamp', 'irradiance', 'cloud_cover', 'temperature'
        hours_ahead: Forecast horizon
        
    Returns:
        Forecast predictions
    """
    df = pd.DataFrame(historical_data)
    df['ds'] = pd.to_datetime(df['timestamp'])
    df['y'] = df['irradiance']
    
    forecaster = ProphetForecaster()
    forecaster.fit(df[['ds', 'y']])
    forecast = forecaster.predict(periods=hours_ahead)
    
    return {
        'predicted_irradiance': float(forecast['yhat'].iloc[-1]),
        'confidence_lower': float(forecast['yhat_lower'].iloc[-1]),
        'confidence_upper': float(forecast['yhat_upper'].iloc[-1]),
    }


def forecast_humidity(historical_data: Dict[str, List[float]], hours_ahead: int = 6) -> Dict[str, float]:
    """
    Forecast humidity windows for AWG (#9) optimization
    
    Args:
        historical_data: Dict with 'timestamp', 'humidity', 'temperature'
        hours_ahead: Forecast horizon
        
    Returns:
        Optimal run windows
    """
    df = pd.DataFrame(historical_data)
    df['ds'] = pd.to_datetime(df['timestamp'])
    df['y'] = df['humidity']
    
    forecaster = ProphetForecaster()
    forecaster.fit(df[['ds', 'y']])
    forecast = forecaster.predict(periods=hours_ahead)
    
    # Identify optimal windows (humidity > 70%)
    optimal_windows = forecast[forecast['yhat'] > 70.0]
    
    return {
        'predicted_humidity': float(forecast['yhat'].iloc[-1]),
        'optimal_windows_count': len(optimal_windows),
        'next_optimal_window': optimal_windows.iloc[0]['ds'].isoformat() if len(optimal_windows) > 0 else None,
    }


def predict_bulb_failure(telemetry_data: Dict[str, float]) -> Dict[str, float]:
    """
    Bayesian reliability prediction for Centennial Bulb (#8)
    
    Args:
        telemetry_data: Dict with 'voltage', 'thermal_cycles', 'uptime'
        
    Returns:
        Failure probability and expected lifetime
    """
    # Simplified Bayesian model - in production, use more sophisticated approach
    voltage_stress = max(0, (telemetry_data['voltage'] - 12.0) / 12.0)  # Normalized
    thermal_stress = telemetry_data['thermal_cycles'] / 10000.0  # Normalized
    age_factor = telemetry_data['uptime'] / 87600.0  # Hours in 10 years
    
    # Combined stress factor
    stress_score = (voltage_stress * 0.3 + thermal_stress * 0.4 + age_factor * 0.3)
    
    # Failure probability (0-1)
    failure_probability = min(1.0, stress_score)
    
    # Expected remaining lifetime (hours)
    base_lifetime = 87600  # 10 years
    expected_remaining = base_lifetime * (1 - failure_probability)
    
    return {
        'failure_probability': float(failure_probability),
        'expected_remaining_hours': float(expected_remaining),
        'expected_remaining_years': float(expected_remaining / 8760),
        'stress_score': float(stress_score),
    }


# Export main forecasting functions
__all__ = [
    'LSTMForecaster',
    'ProphetForecaster',
    'forecast_stream_flow',
    'forecast_solar_irradiance',
    'forecast_humidity',
    'predict_bulb_failure',
]
