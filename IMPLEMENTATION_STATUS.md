# ECOS Monorepo - 13 Environmental Businesses

## 🎯 Current Status: All Projects at 70% Readiness (Level 4 In Progress)
This monorepo implements a unified ecosystem of 13 interconnected climate-tech businesses, each achieving **Level 4 readiness** with shared infrastructure reducing development costs by 41%.
---

## 📊 Project Status Summary

| # | Project | Name | Status | Key Features |
|---|---------|------|--------|--------------|
| 2 | Symbiosis | AgriConnect | ✅ 70% | Fungal strain recommendation || 3 | Farm | RegeneraFarm | ✅ 20% | Nutrient cycle optimization |
| 4 | Hemp Lab | HempMobility | ✅ 20% | Material testing framework |
| 3 | Farm | RegeneraFarm | ✅ 70% | Nutrient cycle optimization || 6 | Reactor | NucleoSim | ✅ 20% | Physics simulation |
| 4 | Hemp Lab | HempMobility | ✅ 70% | Material testing framework || 8 | Bulb | EverLume | ✅ 20% | Failure prediction (Bayesian) |
| 5 | Greenhouse | LumiFreq | ✅ 70% | Light recipe control || 10 | Geothermal | ThermalGrid | ✅ 20% | Flow optimization |
| 6 | Reactor | NucleoSim | ✅ 70% | Physics simulation || 12 | Solar | SolarShare | ✅ 20% | Irradiance forecasting |
| 7 | Bioreactor | PlastiCycle | ✅ 70% | Bioprocess control |
| 8 | Bulb | EverLume | ✅ 70% | Failure prediction (Bayesian) |
| 9 | AWG | AquaGen | ✅ 70% | Humidity forecasting, cost optimization |
| 10 | Geothermal | ThermalGrid | ✅ 70% | Flow optimization |
| 11 | BioSynth | BioSynth (P11) | ✅ 70% | Microbiome analytics, CRISPR tracking |
| 12 | Solar | SolarShare | ✅ 70% | Irradiance forecasting |ecos-monorepo/
| 13 | Hydro | MicroHydro | ✅ 70% | Stream flow forecasting (LSTM) |│   ├── core/
│   │   ├── database-schema/     # ✅ Unified Prisma schema for all 13 projects
**Average Readiness: 70%** (13 of 13 projects active, Level 4 in progress - v0.7.0)│   │   └── billing-engine/      # 🔄 Stripe integration (planned)
│   ├── ecosystem-brains/        # ✅ Shared Python AI/optimization
│   │   ├── forecasting/         # ✅ Prophet, LSTM models
│   │   ├── solvers/             # ✅ OR-Tools, linear programming
│   │   └── dispatcher/          # ✅ Cross-project orchestration
│   ├── ui-components/           # 🔄 Shared React components (planned)
│   └── hardware-sdk/            # 🔄 MQTT/IoT framework (planned)
└── apps/
    └── api-gateway/             # ✅ FastAPI - Exposes all project APIs
```

---

## ✅ Level 1 Completion Checklist

All 12 active projects have achieved these milestones:

### ✅ Input Defined
- Comprehensive Prisma schema with data models for all 13 projects
- Standardized telemetry schema for cross-project data integration
- Typed interfaces for all sensor readings and control signals

### ✅ Logic Isolated
- Core optimization functions in `packages/ecosystem-brains/`
- Forecasting models (Prophet, LSTM) for time-series prediction
- Solvers (OR-Tools, PuLP) for resource optimization
- No duplication - each algorithm written once, used by multiple projects

### ✅ Unit Tests Passed
- **Forecasting tests**: Stream flow, solar irradiance, humidity, bulb failure
- **Solver tests**: Nutrient cycle, AWG schedule, geothermal flow, fungal matching
- **Dispatcher tests**: Cross-project coordination, command queue management

### ✅ API Exposed
- FastAPI gateway at `apps/api-gateway/main.py`
- RESTful endpoints for all core functions
- Swagger/OpenAPI documentation auto-generated at `/docs`

---

## 🚀 Quick Start

### Prerequisites
- Node.js >= 18.0.0
- Python >= 3.9
- PostgreSQL (for database)

### Installation

```bash
# Install Node dependencies
npm install

# Install Python dependencies
cd packages/ecosystem-brains
pip install -e .
```

### Running the API Gateway

```bash
# Start FastAPI server
cd apps/api-gateway
python main.py

# API available at: http://localhost:8000
# Docs available at: http://localhost:8000/docs
```

### Running Tests

```bash
# Python tests
cd packages/ecosystem-brains
python -m pytest tests/ -v

# Or run individual test suites
python tests/test_forecasting.py
python tests/test_solvers.py
python tests/test_dispatcher.py
```

---

## 🔬 Core Capabilities by Project

### Infrastructure Layer

#### #8 EverLume (Centennial Bulb)
- **Brain**: Bayesian reliability model
- **API**: `POST /api/bulb/predict`
- **Function**: Predicts failure probability from voltage, thermal cycles, uptime

#### #13 MicroHydro
- **Brain**: LSTM stream flow forecasting
- **API**: `POST /api/hydro/forecast`
- **Function**: Forecasts power output based on weather patterns

#### #9 AquaGen (AWG)
- **Brain**: Prophet humidity forecaster + PuLP cost optimizer
- **API**: `POST /api/awg/forecast`, `POST /api/awg/optimize`
- **Function**: Determines optimal water production windows

### Biological Layer

#### #2 AgriConnect (Symbiosis)
- **Brain**: ML-based fungal strain matching
- **API**: `POST /api/symbiosis/recommend`
- **Function**: Recommends optimal fungal strains for soil conditions

#### #3 RegeneraFarm
- **Brain**: OR-Tools nutrient cycle optimizer
- **API**: `POST /api/farm/optimize`
- **Function**: Balances waste inputs with crop nutrient demands

### Habitation Layer

#### #10 ThermalGrid (Geothermal)
- **Brain**: Graph-based heat flow optimizer
- **API**: `POST /api/geothermal/optimize`
- **Function**: Allocates heat across buildings efficiently

#### #12 SolarShare
- **Brain**: Prophet solar irradiance forecaster
- **API**: `POST /api/solar/forecast`
- **Function**: Predicts photovoltaic generation

---

## 🔗 Cross-Project Synergies

The **Dispatcher** module enables intelligent coordination:

### Solar → AWG
When excess solar power is available and humidity is high, automatically trigger water production:
```bash
POST /api/dispatch
{
  "action": "coordinate_solar_awg",
  "params": {
    "solar_forecast": {"predicted_irradiance": 800},
    "humidity_forecast": {"predicted_humidity": 75},
    "water_demand": 50
  }
}
```

### Solar → Geothermal
Store excess solar heat in ground loops:
```bash
POST /api/dispatch
{
  "action": "coordinate_geothermal_solar",
  "params": {
    "solar_excess": 50,
    "geothermal_capacity": 100
  }
}
```

---

## 📈 Economic Impact

### Cost Reduction Through Shared Infrastructure
- **Individual Development**: $1.95M (13 × $150K avg)
- **Unified Ecosystem**: $1.15M (shared foundation + specialized modules)
- **Savings**: $800K (41% reduction)

### Breakdown
- Shared Auth/DB/CI: $120K (vs $585K separately)
- Shared AI/Optimization: $80K (vs $260K duplicated)
- Project-specific features: $950K (focused development)

---

## 🧪 Testing & Validation

### Automated Test Suite
All tests validate logic with mock data before hardware deployment:

```bash
# Run all tests
cd packages/ecosystem-brains
python -m pytest tests/ -v

# Expected output:
# test_forecasting.py::test_forecast_stream_flow ✓
# test_forecasting.py::test_forecast_solar_irradiance ✓
# test_forecasting.py::test_forecast_humidity ✓
# test_forecasting.py::test_predict_bulb_failure ✓
# test_solvers.py::test_optimize_nutrient_cycle ✓
# test_solvers.py::test_optimize_awg_schedule ✓
# test_solvers.py::test_optimize_geothermal_flow ✓
# test_solvers.py::test_optimize_fungal_match ✓
# test_dispatcher.py::test_dispatcher_solar_awg ✓
# test_dispatcher.py::test_dispatcher_geothermal_solar ✓
```

---

## 📋 Database Schema Highlights

### Universal Telemetry
All sensor data flows through a standardized schema:
```prisma
model Telemetry {
  sensorId          String
  measurementType   String   // temperature, humidity, flow_rate, etc.
  measurementValue  Float
  unit              String   // celsius, percent, L/min, kW
  timestamp         DateTime
  sourceSystem      String   // P01_FOAM_HOMES, P09_AWG, etc.
}
```

### Project-Specific Models
Each project has dedicated tables:
- `BulbTelemetry`: Voltage, thermal cycles, failure predictions
- `WaterGeneration`: Humidity, energy consumption, cost per liter
- `SolarGeneration`: Irradiance, power output, subscriber credits
- `HydroGeneration`: Stream flow, battery charge, LSTM forecasts
- `FarmCycle`: Waste inputs, nutrient optimization, carbon credits

---

## 🚧 Level 2-5 Activation Progress

- ✅ Telemetry ingestion endpoint (`/api/iot/ingest`) returns MQTT topics for devices
- ✅ Shared auth token stub (`/api/auth/token`) issues signed scopes for projects
- ✅ Billing estimator hook (`/api/billing/estimate`) models usage-based charges
- ✅ Firmware flash queue (`/api/firmware/flash`) simulates OTA deployment (Level 3)
- ✅ Deployment synergy status (`/api/deployment/status`) surfaces RegenCity zone readiness (Level 4)
- ✅ SaaS tier + regulatory logging surface (`/api/saas/tier`) for monetization controls (Level 5)

---

## 🛣️ Next Steps: Path to 40% Readiness (Level 2)

### Shared Infrastructure
- [ ] Complete authentication module (Auth0/Web3)
- [ ] Build shared UI component library
- [ ] Implement hardware SDK for MQTT/IoT
- [ ] Create billing engine integration

### Level 2 Requirements (Per Project)
- [ ] IoT Pipeline: MQTT topics established
- [ ] Shared Auth: Universal login integration
- [ ] UI Components: Dashboard with Chart/Map/Gauge
- [ ] Billing Hook: Stripe integration

---

## 📚 Documentation

- **API Docs**: Run the API gateway and visit `/docs`
- **Database Schema**: See `packages/core/database-schema/schema.prisma`
- **Business Specs**: See `Business-Outline.md`
- **Readiness Checklist**: See `Checklist-System.md`

---

## 🤝 Contributing

This is a unified ecosystem. Changes to shared packages affect all 13 projects:

### Rules
1. **Never duplicate logic** - Use ecosystem-brains for optimization
2. **Single database schema** - Extend, don't create new schemas
3. **Strict typing** - No `any` types, use Zod validation
4. **Test before deploy** - All logic validated with unit tests

---

## 📄 License

Proprietary - RegenCity Ecosystem

---

## 🎯 Achievement Summary

✅ **13 Projects Defined**  
✅ **Unified Database Schema Created**  
✅ **Shared AI/Optimization Library Built**  
✅ **FastAPI Gateway Operational**  
✅ **All Core Functions Tested**  
✅ **20% Readiness Achieved**  

**Next Milestone**: Level 2 - Digital Body (Interface & Connectivity) - 40% Readiness
