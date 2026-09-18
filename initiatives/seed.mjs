#!/usr/bin/env node
/**
 * IDS seed generator — creates draft IDS files for initiatives that do not yet
 * have one in registry/. Grounded in config/hardware-manifests.json (real
 * sensor/actuator/deviceTypes) and the Overlay Environmental portfolio.
 *
 * Honesty contract: everything it cannot source is left empty and named in
 * missing[]; it never invents BOM prices or power numbers. It never overwrites
 * an existing registry/<CODE>.json (so the hand-authored P08 seed is preserved).
 *
 * Usage: node initiatives/seed.mjs
 */
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const ecosRoot = join(here, '..');
const regDir = join(here, 'registry');
const portfolio = JSON.parse(readFileSync(join(here, 'portfolio.json'), 'utf8'));
const manifests = JSON.parse(readFileSync(join(ecosRoot, 'config', 'hardware-manifests.json'), 'utf8'));

// Real per-initiative metadata (types/phases/tracks from Business-Outline +
// data.ts; capability endpoints from apps/api-gateway routers).
const META = {
  P01: { code: 'P01_FOAM_HOMES', name: 'EcoHomes OS', type: 'Foam Homes', phase: 3, stage: 'prototype', tracks: ['Strategic Partner', 'Revenue'], cap: { id: 'parametric-bom', name: 'Parametric design + BOM engine', api: '/api/foam-homes/status', status: 'scaffold' } },
  P02: { code: 'P02_SYMBIOSIS', name: 'AgriConnect', type: 'Plant-Fungi Symbiosis', phase: 2, stage: 'prototype', tracks: ['Strategic Partner', 'Revenue', 'Affiliate'], cap: { id: 'fungal-matching', name: 'Fungal strain matching', api: '/api/symbiosis/recommend', status: 'heuristic' } },
  P03: { code: 'P03_FARM', name: 'RegeneraFarm', type: 'Closed-Loop Farm', phase: 2, stage: 'prototype', tracks: ['Strategic Partner', 'Revenue'], cap: { id: 'nutrient-optimizer', name: 'Nutrient cycle optimizer', api: '/api/farm/optimize', status: 'scaffold' } },
  P04: { code: 'P04_HEMP_LAB', name: 'HempMobility', type: 'Hemp Car Lab', phase: 4, stage: 'concept', tracks: ['Grant', 'Strategic Partner'], cap: { id: 'materials-sim', name: 'FEA / LCA materials simulation', api: '/api/hemp-lab/status', status: 'scaffold' } },
  P05: { code: 'P05_GREENHOUSE', name: 'LumiFreq', type: 'Resonant Illumination', phase: 4, stage: 'concept', tracks: ['Strategic Partner', 'Revenue'], cap: { id: 'light-recipes', name: 'Adaptive light recipe control', api: '/api/greenhouse/status', status: 'scaffold' } },
  P06: { code: 'P06_REACTOR', name: 'NucleoSim', type: 'Fast Reactor Twin', phase: 4, stage: 'concept', tracks: ['Grant', 'Strategic Partner'], cap: { id: 'neutronics-sim', name: 'Neutronics + thermal-hydraulics', api: '/api/reactor/status', status: 'scaffold' } },
  P07: { code: 'P07_BIOREACTOR', name: 'PlastiCycle', type: 'Plastic-Eating Bacteria', phase: 2, stage: 'concept', tracks: ['Grant', 'Strategic Partner'], cap: { id: 'bioprocess-control', name: 'Bioprocess control OS', api: '/api/bioreactor/status', status: 'scaffold' } },
  P09: { code: 'P09_AWG', name: 'AquaGen', type: 'Atmospheric Water Generator', phase: 1, stage: 'prototype', tracks: ['Grant', 'Strategic Partner', 'Revenue'], cap: { id: 'awg-forecast', name: 'Humidity forecast + cost optimizer', api: '/api/awg/forecast', status: 'scaffold' } },
  P10: { code: 'P10_GEOTHERMAL', name: 'ThermalGrid', type: 'Geothermal Network', phase: 3, stage: 'concept', tracks: ['Strategic Partner', 'Revenue'], cap: { id: 'heat-flow-optimizer', name: 'Heat flow optimizer', api: '/api/geothermal/optimize', status: 'scaffold' } },
  P11: { code: 'P11_RESERVED', name: 'ThoriumOS', type: 'Reserved - Thorium Reactor', phase: 4, stage: 'research', tracks: ['Grant'], cap: { id: 'molten-salt-sim', name: 'Molten-salt chemistry simulation', api: null, status: 'planned' } },
  P12: { code: 'P12_SOLAR', name: 'SolarShare', type: 'Community Solar', phase: 3, stage: 'prototype', tracks: ['Revenue', 'Affiliate', 'Strategic Partner'], cap: { id: 'irradiance-forecast', name: 'Irradiance forecast + credit allocator', api: '/api/solar/forecast', status: 'scaffold' } },
  P13: { code: 'P13_HYDRO', name: 'MicroHydro', type: 'Micro-Hydro Power', phase: 1, stage: 'concept', tracks: ['Grant', 'Strategic Partner', 'Revenue'], cap: { id: 'streamflow-forecast', name: 'Stream flow forecast (LSTM)', api: '/api/hydro/forecast', status: 'scaffold' } },
};

const INDIVIDUAL_MISSING = ['Sourced BOM prices', 'Power budget', 'Build guide', 'Verification test'];
const ENTERPRISE_MISSING = ['Deployment topology', 'Site engineering', 'Unit economics', 'Named pilot partner'];

function interfaces(id, man) {
  return {
    telemetryTopic: `ecos/${id}/{deviceId}/telemetry`,
    controlTopic: `ecos/${id}/{deviceId}/control`,
    deviceTypes: man.deviceTypes,
    sensors: man.sensors,
    actuators: man.actuators,
  };
}

function tier(name, audience, mode, unit, id, man, missing) {
  return {
    name,
    audience,
    mode,
    unit,
    bom: [],
    interfaces: interfaces(id, man),
    power: null,
    powerBudget: null,
    buildHours: null,
    sla: null,
    verification: [],
    status: 'draft',
    missing,
  };
}

let created = 0;
let skipped = 0;

for (const man of manifests.initiatives) {
  const meta = META[man.code];
  if (!meta) continue;
  const file = join(regDir, `${meta.code}.json`);
  if (existsSync(file)) {
    skipped += 1;
    continue;
  }
  const ids = {
    code: meta.code,
    id: man.code,
    name: meta.name,
    type: meta.type,
    phase: meta.phase,
    stage: meta.stage,
    tracks: meta.tracks,
    version: 1,
    updatedAt: new Date().toISOString().slice(0, 10),
    software: { capabilities: [{ ...meta.cap, evidence: 'Scaffold endpoint (see apps/api-gateway); status per fundability audit' }] },
    hardware: {
      individual: tier(`${meta.name} Community Build`, 'community builder / maker (build-it-yourself)', 'community', '1 unit', man.code, man, INDIVIDUAL_MISSING),
      enterprise: tier(`${meta.name} Enterprise Deployment`, 'commercial / municipal / campus', 'commercial', 'per site', man.code, man, ENTERPRISE_MISSING),
    },
    founding: {
      status: 'not_started',
      parent: portfolio.parent,
      division: portfolio.division,
      ventureName: meta.name,
      structure: 'division',
      licenses: [],
      capitalAsk: 'to_verify',
      offtake: null,
      compliance: [],
      readiness: { hardwarePilot: false, partnerLoi: false, unitEconomics: false },
    },
    provenance: { verifiedBy: [], driver: null, rollbackToken: null, source: 'seed.mjs (draft from hardware-manifests.json)' },
  };
  writeFileSync(file, JSON.stringify(ids, null, 2) + '\n', 'utf8');
  created += 1;
  console.log(`created registry/${meta.code}.json`);
}

console.log(`\nseed complete: ${created} created, ${skipped} preserved`);
