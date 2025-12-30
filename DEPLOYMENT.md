# ECOS Deployment Guide

This guide explains how to deploy and run the ECOS ecosystem in different environments.

---

## 🏁 Quick Start (Development)

### 1. Prerequisites

```bash
# Check versions
node --version    # >= 18.0.0
python --version  # >= 3.9
psql --version    # >= 12.0 (optional for database)
```

### 2. Install Dependencies

```bash
# Install Node dependencies (optional - for TypeScript packages)
npm install

# Install Python dependencies for ecosystem-brains
cd packages/ecosystem-brains
pip install -e .
```

### 3. Run Validation

```bash
# Validate structure (no dependencies required)
python validate_structure.py

# Expected output: 100% validation (53/53 checks)
```

### 4. Start API Gateway

```bash
# Start FastAPI development server
cd apps/api-gateway
python main.py

# Server starts at http://localhost:8000
# API docs at http://localhost:8000/docs
```

---

## 📦 Installation Options

### Option 1: Minimal (Structure Only)

Just clone and validate the structure - no dependencies needed:

```bash
git clone https://github.com/ncsound919/Environmental-Initiatives-.git
cd Environmental-Initiatives-
python validate_structure.py
```

### Option 2: API Gateway Only

Run the FastAPI gateway with Python dependencies:

```bash
# Install Python packages
pip install fastapi uvicorn pydantic numpy pandas prophet ortools pulp scikit-learn torch xgboost

# Start API
cd apps/api-gateway
python main.py
```

### Option 3: Full Development Environment

Install all dependencies for TypeScript and Python development:

```bash
# Node dependencies
npm install

# Python dependencies
cd packages/ecosystem-brains
pip install -e ".[dev]"

# Database (optional)
# Set DATABASE_URL environment variable
export DATABASE_URL="postgresql://user:password@localhost:5432/ecos"
cd packages/core/database-schema
npx prisma generate
npx prisma migrate dev
```

---

## 🌐 API Gateway Usage

### Starting the Server

```bash
cd apps/api-gateway
python main.py
```

The server starts at `http://localhost:8000` with:
- **API endpoints**: http://localhost:8000/api/*
- **Interactive docs**: http://localhost:8000/docs
- **OpenAPI spec**: http://localhost:8000/openapi.json

### Example API Calls

#### Health Check
```bash
curl http://localhost:8000/health
```

#### List All Projects
```bash
curl http://localhost:8000/projects
```

#### Forecast Micro-Hydro Stream Flow (Project #13)
```bash
curl -X POST http://localhost:8000/api/hydro/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "historical_data": {
      "timestamp": ["2024-01-01T00:00:00Z", "2024-01-01T01:00:00Z"],
      "flow": [5.0, 5.2],
      "precipitation": [10.0, 12.0],
      "temperature": [15.0, 14.5]
    },
    "hours_ahead": 24
  }'
```

#### Optimize AWG Water Production (Project #9)
```bash
curl -X POST http://localhost:8000/api/awg/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "humidity_forecast": [60, 65, 75, 80, 85, 70],
    "energy_prices": [0.10, 0.12, 0.08, 0.09, 0.15, 0.11],
    "target_liters": 100.0
  }'
```

#### Predict Bulb Failure (Project #8)
```bash
curl -X POST http://localhost:8000/api/bulb/predict \
  -H "Content-Type: application/json" \
  -d '{
    "voltage": 12.5,
    "thermal_cycles": 5000,
    "uptime": 43800
  }'
```

#### Cross-Project Coordination (Dispatcher)
```bash
curl -X POST http://localhost:8000/api/dispatch \
  -H "Content-Type: application/json" \
  -d '{
    "action": "coordinate_solar_awg",
    "params": {
      "solar_forecast": {"predicted_irradiance": 800.0},
      "humidity_forecast": {"predicted_humidity": 75.0},
      "water_demand": 50.0
    }
  }'
```

---

## 🗄️ Database Setup (Optional)

The system can run without a database for testing APIs. For production:

### 1. Install PostgreSQL

```bash
# macOS
brew install postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL
# macOS: brew services start postgresql
# Ubuntu: sudo systemctl start postgresql
```

### 2. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE ecos;

# Create user (optional)
CREATE USER ecos_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ecos TO ecos_user;
```

### 3. Configure Environment

```bash
# Create .env file in packages/core/database-schema
echo "DATABASE_URL=postgresql://ecos_user:your_password@localhost:5432/ecos" > packages/core/database-schema/.env
```

### 4. Run Migrations

```bash
cd packages/core/database-schema
npx prisma generate
npx prisma migrate dev --name init
```

### 5. Explore Database (Optional)

```bash
npx prisma studio
# Opens web UI at http://localhost:5555
```

---

## 🧪 Testing

### Structure Validation

```bash
# Validate all files are in place
python validate_structure.py

# Expected: 100% (53/53 checks)
```

### Python Module Tests

```bash
cd packages/ecosystem-brains

# Run specific test files directly
python tests/test_forecasting.py
python tests/test_solvers.py
python tests/test_dispatcher.py

# Or with pytest (if installed)
pytest tests/ -v
```

### API Integration Tests

```bash
# Start the API gateway
cd apps/api-gateway
python main.py &

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/projects
curl http://localhost:8000/api/dispatch/status

# Stop server
kill %1
```

---

## 🐳 Docker Deployment (Planned)

Future deployment will support Docker:

```yaml
# docker-compose.yml (example)
version: '3.8'
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: ecos
      POSTGRES_PASSWORD: ecos_password
    ports:
      - "5432:5432"
  
  api-gateway:
    build: ./apps/api-gateway
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://postgres:ecos_password@postgres:5432/ecos
```

---

## 🔧 Development Workflow

### 1. Make Changes

```bash
# Edit files in packages/ecosystem-brains or apps/api-gateway
# Follow the coding rules:
# - Never duplicate logic
# - Use strict typing
# - Test with mock data first
```

### 2. Validate

```bash
# Check structure
python validate_structure.py

# Test Python modules
cd packages/ecosystem-brains
python tests/test_[module].py
```

### 3. Run API

```bash
# Start server to test endpoints
cd apps/api-gateway
python main.py

# Visit http://localhost:8000/docs to test interactively
```

### 4. Commit

```bash
git add .
git commit -m "Description of changes"
git push
```

---

## 🚨 Troubleshooting

### "Module not found" errors

```bash
# Install missing Python dependencies
pip install [package_name]

# Or install all at once
cd packages/ecosystem-brains
pip install -e ".[dev]"
```

### API server won't start

```bash
# Check port 8000 is available
lsof -i :8000

# Kill existing process if needed
kill -9 [PID]

# Or use different port
uvicorn main:app --port 8001
```

### Database connection errors

```bash
# Verify PostgreSQL is running
pg_isready

# Check connection string
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL
```

### TypeScript compilation errors

```bash
# Install dependencies
npm install

# Build specific package
cd packages/core/auth-module
npm run build
```

---

## 📈 Performance Optimization

### For Development
- Use `--reload` flag for auto-reload during development:
  ```bash
  cd apps/api-gateway
  uvicorn main:app --reload
  ```

### For Production
- Use production WSGI server:
  ```bash
  gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
  ```
- Enable caching for forecasting results
- Use connection pooling for database
- Deploy behind nginx reverse proxy

---

## 🔐 Security

### Development
- JWT secret defaults to 'dev-secret'
- Database can be skipped for testing

### Production
- Set secure JWT_SECRET environment variable
- Use SSL/TLS for database connections
- Enable CORS restrictions in FastAPI
- Use Auth0 for production authentication
- Enable rate limiting on API endpoints

---

## 📞 Support

For deployment issues:
1. Check this guide first
2. Review `IMPLEMENTATION_STATUS.md`
3. Open GitHub issue with:
   - Your environment (OS, Python version, etc.)
   - Error messages
   - Steps to reproduce

---

**Last Updated**: December 2024  
**Version**: 1.0.0 (Level 1 - 20% Readiness)
