# EcoSphere Full-Stack Readiness & Hardware Integration

**Source:** [`/EcoSphere`](../../EcoSphere) architecture baseline (event-driven microservices + CQRS, Kafka/RabbitMQ, unified PostgreSQL + TimescaleDB + Neo4j + Redis, Keycloak SSO).

This playbook turns the EcoSphere specification into a deployable full-stack posture for all 13 environmental initiatives, with concrete layouts and hardware mappings that align software, data, and field devices.

## Layered Layout (EcoSphere ➜ Implementation)

```
Users (Ops + Field) 
   ↓ SSO (Keycloak/OIDC) → Roles (system/enterprise/consumer/iot)
Web UI (apps/web + ui-components) ————┐
   ↓                                   │
API Gateway (apps/api-gateway, FastAPI)│
   ↓                                   │
Domain Services (per project microservices / dispatcher)
   ↓                                   │
Event Bus (Kafka + RabbitMQ DLQ) ——┬——┘
   ↓ CloudEvents 1.0 envelopes     │
Unified Data Layer (PostgreSQL/TimescaleDB/Neo4j/Redis)
   ↓                               │
Observability (metrics/logs/traces)│
   ↓                               │
Hardware SDK (packages/hardware-sdk) ← MQTT brokers (telemetry/command)
   ↓
Edge Devices (ESP32/PLC/Jetson) in RegenCity zones
```

## Full-Stack Readiness Actions (minimal, per EcoSphere component)

- **Identity & Access:** Bring up Keycloak with the EcoSphere role hierarchy (`system`, `enterprise`, `consumer`, `iot`). Wire OIDC tokens through `apps/api-gateway` and preserve MQTT credentials for device classes.
- **Data & Events:** Route all device payloads through CloudEvents envelopes into Kafka domain topics (e.g., `energy.production.solar`, `iot.sensor.telemetry`) with RabbitMQ as DLQ. TimescaleDB handles time-series metrics; Neo4j stores asset/zone graphs; Redis backs sessions and device heartbeats.
- **Services:** Keep FastAPI as the consolidation point; microservice calls fan out via dispatcher to forecasting/solver modules (`packages/ecosystem-brains/*`) before issuing MQTT commands through `packages/hardware-sdk`.
- **UI Layouts:** 
  - **Operations Console:** fleet status by project/zone, live alarms, and last-ingestion timestamps.
  - **MDM Golden Records:** editable asset/location cards that map device IDs to RegenCity zones and EcoSphere entity IDs.
  - **Energy/Water/Materials Dashboards:** reuse shared charts from `packages/ui-components` with topic-derived metrics (solar → AWG → geothermal loops).
- **Deployment:** Favor `docker-compose up` for end-to-end bring-up (Keycloak, Kafka, API, web). Ensure `.env` includes broker URLs, PostgreSQL/Neo4j/Redis endpoints, and Keycloak realm settings that mirror the `/EcoSphere` `ssoIdentityProvider` defaults (role hierarchy defined there; see **Config Defaults (EcoSphere SSO)** below for token lifetimes).

### Config Defaults (EcoSphere SSO)
- `access_token_lifetime: 15m`
- `refresh_token_lifetime: 7d`

## Hardware Integration Mappings (topics, storage, control)

| Device Class | MQTT Topic Pattern (hardware-sdk) | EcoSphere Domain Topic Route | Storage Target | Control/Feedback Path |
|--------------|-----------------------------------|------------------------------|----------------|-----------------------|
| Sensor/Edge Node (ESP32/STM32) | `ecos/{project}/{deviceId}/telemetry` with `TelemetrySchema` payload (see fields below) | `iot.sensor.telemetry` → project-specific domain topic (e.g., `agriculture.yield.greenhouse`, `water.generation.atmospheric`) | TimescaleDB (metrics) + PostgreSQL (device registry) | Commands on `ecos/{project}/{deviceId}/command` (e.g., setpoint updates) |
| Industrial Controller (PLC) | `ecos/{project}/{deviceId}/telemetry` (flow/temp/pressure) | `energy.consumption.thermal` / `manufacturing.batch.hemp` | TimescaleDB for continuous signals; Neo4j links assets to loops/nodes | `.../command` for valve/pump actions; dispatcher ensures safety envelopes |
| Edge Compute (Raspberry Pi/Jetson) | `ecos/{project}/{deviceId}/telemetry` (camera/ML summaries) | `ml.prediction.generated` / `compliance.audit.required` | PostgreSQL (events) + object storage pointer if needed | `.../command` for model version/pipeline toggles |
| Power & Metering (CT clamps/smart meters) | `ecos/{project}/{deviceId}/telemetry` (kW/kWh, voltage) | `energy.production.solar`, `energy.consumption.thermal`, `commerce.transaction.completed` | TimescaleDB for curves; PostgreSQL for billing snapshots | `.../command` for demand-response throttling |

**Schema Alignment:** Telemetry must validate against `packages/hardware-sdk` `TelemetrySchema` before publish; the API gateway accepts only CloudEvents-wrapped payloads and stamps `source=project_code` + `traceparent`.

**TelemetrySchema Fields (fields with `?` are optional):**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| sensorId | UUID | Yes | Device or sensor identifier |
| locationId? | String | No | RegenCity zone/project locator code (matches `TelemetrySchema.locationId`) |
| measurementType | String (enum) | Yes | temperature, humidity, lux, flow_rate, etc. |
| measurementValue | Float | Yes | Numeric reading |
| unit | String | Yes | SI units (celsius, percent, lux, L/min, kW, etc.) |
| timestamp | ISO8601 string | Yes | Event time (UTC) |
| qualityFlag | Enum | No | valid, suspect, error (closed set; default valid) |
| schemaVersion | String (semver) | Yes | Payload schema version |
| sourceSystem | String | Yes | project_code or originating service |
| ingestionTime? | ISO8601 string | No | When broker ingested the event |

## Minimal Acceptance Checks

- Telemetry from at least one device per project flows MQTT → Kafka → TimescaleDB/PostgreSQL and is visible on the Operations Console.
- SSO tokens propagate through API to MQTT command authorization (role-based topic access).
- Event DLQs are drained (RabbitMQ) and observability traces reach the chosen APM target for dispatcher actions.
