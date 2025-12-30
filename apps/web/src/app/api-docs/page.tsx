'use client';

import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { apiEndpoints } from '@/lib/data';

const endpointDocs = [
  {
    method: 'GET',
    path: '/health',
    description: 'System health check',
    response: `{
  "status": "operational",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}`
  },
  {
    method: 'GET',
    path: '/projects',
    description: 'List all 13 projects and their status',
    response: `{
  "projects": [...],
  "total": 13,
  "average_readiness": "18.5%"
}`
  },
  {
    method: 'POST',
    path: '/api/hydro/forecast',
    description: 'Forecast stream flow for Micro-Hydro power generation (#13)',
    request: `{
  "historical_data": {
    "timestamp": ["2024-01-01T00:00:00Z", ...],
    "flow": [45.2, 47.8, ...],
    "precipitation": [0.0, 0.5, ...],
    "temperature": [15.0, 16.2, ...]
  },
  "hours_ahead": 24
}`,
    response: `{
  "project": "P13_HYDRO",
  "result": {
    "predicted_flow": 48.5,
    "confidence_lower": 42.0,
    "confidence_upper": 55.0
  }
}`
  },
  {
    method: 'POST',
    path: '/api/solar/forecast',
    description: 'Forecast solar irradiance for photovoltaic generation (#12)',
    request: `{
  "historical_data": {
    "timestamp": ["2024-01-01T06:00:00Z", ...],
    "irradiance": [100, 250, 450, ...]
  },
  "hours_ahead": 24
}`,
    response: `{
  "project": "P12_SOLAR",
  "result": {
    "predicted_irradiance": 520.0,
    "confidence_lower": 450.0,
    "confidence_upper": 600.0
  }
}`
  },
  {
    method: 'POST',
    path: '/api/awg/forecast',
    description: 'Forecast optimal humidity windows for water generation (#9)',
    request: `{
  "historical_data": {
    "timestamp": ["2024-01-01T00:00:00Z", ...],
    "humidity": [65, 72, 78, ...]
  },
  "hours_ahead": 6
}`,
    response: `{
  "project": "P09_AWG",
  "result": {
    "predicted_humidity": 75.0,
    "optimal_windows_count": 3,
    "next_optimal_window": "2024-01-01T04:00:00Z"
  }
}`
  },
  {
    method: 'POST',
    path: '/api/awg/optimize',
    description: 'Optimize AWG run schedule to minimize energy costs (#9)',
    request: `{
  "humidity_forecast": [65, 72, 78, 80, 75, 68],
  "energy_prices": [0.12, 0.15, 0.20, 0.25, 0.18, 0.10],
  "target_liters": 100
}`,
    response: `{
  "project": "P09_AWG",
  "result": {
    "status": "optimal",
    "schedule": [0, 1, 1, 1, 0, 1],
    "total_production_liters": 105.5,
    "total_cost_usd": 1.56,
    "cost_per_liter": 0.0148
  }
}`
  },
  {
    method: 'POST',
    path: '/api/bulb/predict',
    description: 'Predict bulb failure probability using Bayesian model (#8)',
    request: `{
  "voltage": 12.5,
  "thermal_cycles": 1500,
  "uptime": 25000
}`,
    response: `{
  "project": "P08_BULB",
  "result": {
    "failure_probability": 0.15,
    "expected_remaining_hours": 74460,
    "expected_remaining_years": 8.5,
    "stress_score": 0.15
  }
}`
  },
  {
    method: 'POST',
    path: '/api/farm/optimize',
    description: 'Optimize nutrient cycle allocation (#3)',
    request: `{
  "waste_inputs": {"N": 100, "P": 50, "K": 75},
  "crop_demands": {"N": 80, "P": 40, "K": 60}
}`,
    response: `{
  "project": "P03_FARM",
  "result": {
    "status": "optimal",
    "allocation": {"N": 80, "P": 40, "K": 60},
    "waste": {"N": 20, "P": 10, "K": 15},
    "objective_value": 180
  }
}`
  },
  {
    method: 'POST',
    path: '/api/geothermal/optimize',
    description: 'Optimize geothermal heat flow distribution (#10)',
    request: `{
  "building_loads": {
    "building_a": 50,
    "building_b": 30,
    "building_c": 45
  },
  "ground_temp": 15.0,
  "available_capacity": 100
}`,
    response: `{
  "project": "P10_GEOTHERMAL",
  "result": {
    "status": "optimal",
    "allocations": {...},
    "total_allocated": 100,
    "capacity_utilization": 0.80,
    "unmet_demand": {...}
  }
}`
  },
  {
    method: 'POST',
    path: '/api/symbiosis/recommend',
    description: 'Recommend fungal strain based on soil data (#2)',
    request: `{
  "soil_data": {
    "pH": 6.5,
    "moisture": 55,
    "N": 20,
    "P": 15,
    "K": 25
  }
}`,
    response: `{
  "project": "P02_SYMBIOSIS",
  "result": {
    "recommended_strain": "Neutral_Strain_C",
    "expected_yield_increase": 0.30,
    "confidence": 0.85,
    "soil_compatibility": "high"
  }
}`
  },
  {
    method: 'POST',
    path: '/api/dispatch',
    description: 'Execute cross-project coordination actions',
    request: `{
  "action": "coordinate_solar_awg",
  "params": {
    "solar_forecast": {"predicted_irradiance": 800},
    "humidity_forecast": {"predicted_humidity": 75},
    "water_demand": 50
  }
}`,
    response: `{
  "dispatcher": "ECOS",
  "result": {
    "status": "dispatched",
    "action": {...},
    "reasoning": "Excess solar power and high humidity detected"
  }
}`
  },
  {
    method: 'GET',
    path: '/api/dispatch/status',
    description: 'Get dispatcher system status',
    response: `{
  "timestamp": "2024-01-01T12:00:00Z",
  "active_projects": 12,
  "pending_commands": 3,
  "system_health": "operational"
}`
  }
];

export default function ApiDocsPage() {
  return (
    <>
      <Header />
      <main className="section">
        <div className="container">
          <h1 className="section-title">API Documentation</h1>
          <p className="section-subtitle">
            REST API for the ECOS ecosystem. Base URL: <code style={{ background: '#f3f4f6', padding: '0.25rem 0.5rem', borderRadius: '0.25rem' }}>http://localhost:8000</code>
          </p>

          <div className="dashboard-card" style={{ marginBottom: '2rem' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '1rem' }}>
              Getting Started
            </h2>
            <p style={{ marginBottom: '1rem' }}>
              The ECOS API Gateway provides unified access to all 13 project APIs. 
              Start the server with:
            </p>
            <pre style={{ 
              background: '#1f2937', 
              color: '#f9fafb', 
              padding: '1rem', 
              borderRadius: '0.5rem',
              overflow: 'auto',
              fontSize: '0.875rem'
            }}>
{`cd apps/api-gateway
python main.py

# Server running at http://localhost:8000
# Interactive docs at http://localhost:8000/docs`}
            </pre>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {endpointDocs.map((endpoint, index) => (
              <div key={index} className="dashboard-card">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                  <span style={{ 
                    background: endpoint.method === 'GET' ? '#10b98120' : '#3b82f620',
                    color: endpoint.method === 'GET' ? '#10b981' : '#3b82f6',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '0.25rem',
                    fontWeight: 'bold',
                    fontSize: '0.875rem'
                  }}>
                    {endpoint.method}
                  </span>
                  <code style={{ 
                    background: '#f3f4f6', 
                    padding: '0.25rem 0.5rem', 
                    borderRadius: '0.25rem',
                    fontSize: '0.875rem'
                  }}>
                    {endpoint.path}
                  </code>
                </div>
                <p style={{ marginBottom: '1rem', color: '#374151' }}>{endpoint.description}</p>
                
                {endpoint.request && (
                  <div style={{ marginBottom: '1rem' }}>
                    <h4 style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: '0.5rem', color: '#6b7280' }}>
                      Request Body
                    </h4>
                    <pre style={{ 
                      background: '#1f2937', 
                      color: '#f9fafb', 
                      padding: '1rem', 
                      borderRadius: '0.5rem',
                      overflow: 'auto',
                      fontSize: '0.75rem'
                    }}>
                      {endpoint.request}
                    </pre>
                  </div>
                )}
                
                <div>
                  <h4 style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: '0.5rem', color: '#6b7280' }}>
                    Response
                  </h4>
                  <pre style={{ 
                    background: '#1f2937', 
                    color: '#f9fafb', 
                    padding: '1rem', 
                    borderRadius: '0.5rem',
                    overflow: 'auto',
                    fontSize: '0.75rem'
                  }}>
                    {endpoint.response}
                  </pre>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
