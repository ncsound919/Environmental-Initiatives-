-- ECOS Database Initialization Script
-- Adds TimescaleDB extension for time-series telemetry optimization

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Create hypertables for time-series data (after Prisma migration)
-- These will be created by the migration script after Prisma generates tables

-- Note: Run this after `npx prisma migrate dev`
-- SELECT create_hypertable('telemetry', 'timestamp');
-- SELECT create_hypertable('bulb_telemetry', 'timestamp');
-- SELECT create_hypertable('water_generation', 'timestamp');
-- SELECT create_hypertable('solar_generation', 'timestamp');
-- SELECT create_hypertable('hydro_generation', 'timestamp');
-- SELECT create_hypertable('geothermal_flow', 'timestamp');
-- SELECT create_hypertable('bioreactor_readings', 'timestamp');
-- SELECT create_hypertable('prediction_logs', 'timestamp');
-- SELECT create_hypertable('audit_logs', 'timestamp');

-- Create indexes for common query patterns
-- CREATE INDEX IF NOT EXISTS idx_telemetry_project_time ON telemetry (sourceSystem, timestamp DESC);
-- CREATE INDEX IF NOT EXISTS idx_telemetry_device_time ON telemetry (sensorId, timestamp DESC);

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE ecos_db TO ecos;
