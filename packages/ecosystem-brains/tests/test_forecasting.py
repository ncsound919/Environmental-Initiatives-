"""
Unit tests for ecosystem-brains forecasting module
Validates Level 1 completion criteria
"""

from datetime import datetime, timedelta
import pandas as pd
from forecasting import (
    forecast_stream_flow,
    forecast_solar_irradiance,
    forecast_humidity,
    predict_bulb_failure,
    ProphetForecaster,
)


def test_forecast_stream_flow():
    """Test Micro-Hydro (#13) stream flow forecasting"""
    # Mock historical data
    timestamps = [datetime.now() - timedelta(hours=i) for i in range(48, 0, -1)]
    historical_data = {
        'timestamp': [t.isoformat() for t in timestamps],
        'flow': [5.0 + i * 0.1 for i in range(48)],
        'precipitation': [10.0 for _ in range(48)],
        'temperature': [15.0 for _ in range(48)],
    }
    
    result = forecast_stream_flow(historical_data, hours_ahead=24)
    
    assert 'predicted_flow' in result
    assert 'confidence_lower' in result
    assert 'confidence_upper' in result
    assert isinstance(result['predicted_flow'], float)
    assert result['predicted_flow'] > 0
    print(f"✓ Micro-Hydro (#13) forecast: {result['predicted_flow']:.2f} m³/s")


def test_forecast_solar_irradiance():
    """Test Solar Gardens (#12) irradiance forecasting"""
    timestamps = [datetime.now() - timedelta(hours=i) for i in range(48, 0, -1)]
    historical_data = {
        'timestamp': [t.isoformat() for t in timestamps],
        'irradiance': [500.0 + i * 5.0 for i in range(48)],
        'cloud_cover': [20.0 for _ in range(48)],
        'temperature': [25.0 for _ in range(48)],
    }
    
    result = forecast_solar_irradiance(historical_data, hours_ahead=24)
    
    assert 'predicted_irradiance' in result
    assert isinstance(result['predicted_irradiance'], float)
    assert result['predicted_irradiance'] >= 0
    print(f"✓ Solar Gardens (#12) forecast: {result['predicted_irradiance']:.2f} W/m²")


def test_forecast_humidity():
    """Test AWG (#9) humidity forecasting"""
    timestamps = [datetime.now() - timedelta(hours=i) for i in range(48, 0, -1)]
    historical_data = {
        'timestamp': [t.isoformat() for t in timestamps],
        'humidity': [60.0 + i * 0.5 for i in range(48)],
        'temperature': [20.0 for _ in range(48)],
    }
    
    result = forecast_humidity(historical_data, hours_ahead=6)
    
    assert 'predicted_humidity' in result
    assert 'optimal_windows_count' in result
    assert isinstance(result['predicted_humidity'], float)
    print(f"✓ AWG (#9) forecast: {result['predicted_humidity']:.2f}% humidity")


def test_predict_bulb_failure():
    """Test Centennial Bulb (#8) failure prediction"""
    telemetry = {
        'voltage': 12.5,
        'thermal_cycles': 5000,
        'uptime': 43800,  # 5 years
    }
    
    result = predict_bulb_failure(telemetry)
    
    assert 'failure_probability' in result
    assert 'expected_remaining_hours' in result
    assert 'expected_remaining_years' in result
    assert 0 <= result['failure_probability'] <= 1
    assert result['expected_remaining_hours'] >= 0
    print(f"✓ Bulb (#8) prediction: {result['failure_probability']:.2%} failure probability")


def test_prophet_forecaster():
    """Test Prophet wrapper functionality"""
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    df = pd.DataFrame({
        'ds': dates,
        'y': [10 + i * 0.1 for i in range(100)]
    })
    
    forecaster = ProphetForecaster()
    forecaster.fit(df)
    forecast = forecaster.predict(periods=7)
    
    assert len(forecast) > 0
    assert 'yhat' in forecast.columns
    print(f"✓ Prophet forecaster: {len(forecast)} predictions generated")


if __name__ == '__main__':
    print("\n=== ECOS Forecasting Module Tests ===\n")
    test_forecast_stream_flow()
    test_forecast_solar_irradiance()
    test_forecast_humidity()
    test_predict_bulb_failure()
    test_prophet_forecaster()
    print("\n✓ All forecasting tests passed!\n")
