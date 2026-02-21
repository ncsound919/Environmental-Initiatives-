#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Starting EcoSphere stack (PostgreSQL, MQTT, Redis, Keycloak, Kafka, API, Web)..."
docker-compose -f "${ROOT_DIR}/docker-compose.yml" up -d

echo "Waiting for containers (this may take longer on first run)..."
sleep 20
docker-compose -f "${ROOT_DIR}/docker-compose.yml" ps

echo "If API is running, visit http://localhost:8000/docs"
echo "If Keycloak is running, visit http://localhost:8080"
