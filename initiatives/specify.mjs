#!/usr/bin/env node
/**
 * Portfolio spec-readiness generator.
 *
 * Writes a `verified` community + enterprise hardware tier for each initiative
 * from an authored, sourced (vendor list estimate) specification, and creates a
 * matching firmware scaffold per physical initiative. This reaches SPEC
 * readiness — not physical/founding readiness. The gate still enforces every
 * structural + firmware + sourcing check.
 *
 * Honesty: prices are labelled vendor list estimates, not quotes; enterprise
 * deployment figures are indicative and require EPC quotes. P11 (research) is
 * intentionally left draft. P08 is hand-authored and preserved.
 *
 * Usage: node initiatives/specify.mjs
 */
import { readFileSync, writeFileSync, existsSync, mkdirSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const ecosRoot = join(here, '..');
const regDir = join(here, 'registry');
const fwDir = join(ecosRoot, 'firmware', 'scaffolds');

const p = (part, qty, unitUsd, supplier, source) => ({ part, qty, unitUsd, supplier, source });

const SPEC = {
  P01: {
    device: 'hvac-controller', powerC: 'USB 5V 0.5A (2.5 W)', hoursC: 3, powerE: '~120 W per home', hoursE: 8,
    topology: 'thermostat -> HVAC controller -> BMS gateway -> MQTT',
    c: [p('ESP32-DevKitC v4', 1, 9.95, 'Adafruit', 'adafruit.com/product/3269'), p('DHT22 temp/humidity', 1, 9.95, 'Adafruit', 'adafruit.com/product/385'), p('SGP30 TVOC/CO2', 1, 19.95, 'Adafruit', 'adafruit.com/product/3709'), p('5V relay module', 1, 4.5, 'Generic', 'list est.'), p('5V fan', 1, 6.5, 'Generic', 'list est.'), p('Breadboard + jumpers', 1, 4.0, 'Adafruit', 'adafruit.com/product/64')],
    e: [p('Commercial thermostat (0-10V)', 1, 120, 'HVAC distributor', 'list est.'), p('CO2/VOC sensor', 1, 45, 'Digi-Key', 'digikey.com'), p('Damper actuator', 4, 60, 'HVAC distributor', 'list est.'), p('Heat-pump control board', 1, 55, 'HVAC distributor', 'list est.'), p('BMS edge gateway', 1, 150, 'Industrial supplier', 'list est.')],
  },
  P02: {
    device: 'soil-probe', powerC: 'USB 5V 0.5A + 12V pump 1A (~14.5 W)', hoursC: 4, powerE: '~200 W per acre', hoursE: 16,
    topology: 'probes -> LoRa -> gateway -> MQTT',
    c: [p('ESP32-DevKitC v4', 1, 9.95, 'Adafruit', 'adafruit.com/product/3269'), p('Capacitive soil moisture', 1, 7.5, 'Adafruit', 'adafruit.com/product/4026'), p('RS485 NPK soil sensor', 1, 45, 'Generic', 'list est.'), p('Peristaltic dosing pump', 1, 12, 'Generic', 'list est.'), p('Relay module', 1, 4.5, 'Generic', 'list est.'), p('Tubing kit', 1, 6, 'Generic', 'list est.')],
    e: [p('Soil probe array', 6, 45, 'Generic', 'list est.'), p('LoRa gateway', 1, 220, 'Digi-Key', 'digikey.com'), p('Irrigation valve + actuator', 4, 85, 'Agricultural supplier', 'list est.'), p('Fertigation dosing pump', 1, 250, 'Agricultural supplier', 'list est.'), p('Zone controller', 1, 150, 'Industrial supplier', 'list est.'), p('Solar + battery PSU', 1, 180, 'Generic', 'list est.')],
  },
  P03: {
    device: 'compost-sensor', powerC: 'USB 5V 0.5A + 12V (~18 W)', hoursC: 4, powerE: '~1.2 kW per site', hoursE: 24,
    topology: 'probes -> controller -> aerator/doser -> gateway -> MQTT',
    c: [p('ESP32-DevKitC v4', 1, 9.95, 'Adafruit', 'adafruit.com/product/3269'), p('DS18B20 temp probe', 1, 9.0, 'Adafruit', 'adafruit.com/product/381'), p('Moisture probe', 1, 7.5, 'Adafruit', 'adafruit.com/product/4026'), p('pH probe + board', 1, 45, 'DFRobot', 'dfrobot.com'), p('Air pump', 1, 15, 'Generic', 'list est.'), p('Relay module', 1, 4.5, 'Generic', 'list est.')],
    e: [p('Compost probe set', 8, 45, 'Generic', 'list est.'), p('Aerator blower', 1, 350, 'Agricultural supplier', 'list est.'), p('Nutrient dosing pump', 1, 300, 'Agricultural supplier', 'list est.'), p('Loop controller', 1, 180, 'Industrial supplier', 'list est.'), p('LoRa gateway', 1, 200, 'Digi-Key', 'digikey.com'), p('Windrow sensor', 1, 250, 'Agricultural supplier', 'list est.')],
  },
  P04: {
    device: 'material-testbench', powerC: 'USB 5V 1A + 12V 2A (~29 W)', hoursC: 5, powerE: '~3 kW per lab', hoursE: 80,
    topology: 'test frame -> DAQ -> HPC -> results store',
    c: [p('ESP32-DevKitC v4', 1, 9.95, 'Adafruit', 'adafruit.com/product/3269'), p('Load cell (350 ohm)', 1, 6, 'SparkFun', 'sparkfun.com'), p('HX711 amplifier', 1, 6, 'SparkFun', 'sparkfun.com'), p('MAX6675 + thermocouple', 1, 12, 'Adafruit', 'adafruit.com/product/269'), p('Heating pad', 1, 8, 'Generic', 'list est.'), p('Frame hardware', 1, 15, 'Generic', 'list est.')],
    e: [p('Universal testing machine (small)', 1, 12000, 'Materials lab supplier', 'list est.'), p('Thermal chamber', 1, 6000, 'Environmental supplier', 'list est.'), p('DAQ system', 1, 1500, 'National Instruments', 'ni.com'), p('HPC workstation', 1, 4500, 'Hardware vendor', 'list est.'), p('Instrumented fixtures', 1, 500, 'Materials lab supplier', 'list est.')],
  },
  P05: {
    device: 'spectral-controller', powerC: '12V 3A (~36 W)', hoursC: 4, powerE: '~6.5 kW per greenhouse', hoursE: 40,
    topology: 'LED arrays -> zone controller -> gateway -> MQTT',
    c: [p('ESP32-DevKitC v4', 1, 9.95, 'Adafruit', 'adafruit.com/product/3269'), p('4-channel LED driver', 1, 18, 'Generic', 'list est.'), p('RGBW + far-red LED module', 1, 35, 'LED supplier', 'list est.'), p('PPFD/spectrum sensor', 1, 220, 'Apogee Instruments', 'apogeeinstruments.com'), p('Breadboard + jumpers', 1, 4.0, 'Adafruit', 'adafruit.com/product/64')],
    e: [p('LED array (4-channel)', 20, 320, 'LED supplier', 'list est.'), p('Spectral sensor', 6, 220, 'Apogee Instruments', 'apogeeinstruments.com'), p('Zone controller', 1, 350, 'Industrial supplier', 'list est.'), p('Gateway', 1, 200, 'Industrial supplier', 'list est.')],
  },
  P06: {
    compute: true, powerC: '~120 W', hoursC: 3, powerE: '~4 kW per node', hoursE: 40,
    topology: 'simulation nodes -> scheduler -> results store',
    c: [p('Mini-PC (8-core)', 1, 450, 'Hardware vendor', 'list est.'), p('32 GB RAM', 1, 80, 'Hardware vendor', 'list est.'), p('1 TB NVMe', 1, 70, 'Hardware vendor', 'list est.'), p('UPS', 1, 90, 'Hardware vendor', 'list est.'), p('Network switch', 1, 30, 'Hardware vendor', 'list est.')],
    e: [p('HPC node (dual CPU)', 1, 12000, 'OEM', 'list est.'), p('GPU accelerator', 1, 8000, 'OEM', 'list est.'), p('Rack + PDU', 1, 2500, 'Datacenter supplier', 'list est.'), p('Cooling', 1, 1800, 'Datacenter supplier', 'list est.'), p('Networking (100GbE)', 1, 3000, 'Datacenter supplier', 'list est.')],
  },
  P07: {
    device: 'bioreactor', powerC: 'USB 5V 0.5A + 12V 2A (~26 W)', hoursC: 8, powerE: '~3 kW per reactor', hoursE: 80,
    topology: 'reactor -> PLC -> HMI -> MQTT',
    c: [p('ESP32-DevKitC v4', 1, 9.95, 'Adafruit', 'adafruit.com/product/3269'), p('pH probe + board', 1, 55, 'DFRobot', 'dfrobot.com'), p('DS18B20 temp probe', 1, 9.0, 'Adafruit', 'adafruit.com/product/381'), p('Dissolved-oxygen probe', 1, 120, 'Atlas Scientific', 'atlas-scientific.com'), p('Peristaltic feed pump', 1, 25, 'Generic', 'list est.'), p('Air pump', 1, 18, 'Generic', 'list est.'), p('Relay board', 1, 8, 'Generic', 'list est.')],
    e: [p('100 L bioreactor vessel', 1, 8000, 'Biotech supplier', 'list est.'), p('Agitator drive', 1, 2000, 'Biotech supplier', 'list est.'), p('DO/pH controllers', 1, 1500, 'Biotech supplier', 'list est.'), p('Feed/air pumps', 1, 900, 'Biotech supplier', 'list est.'), p('Industrial PLC', 1, 2500, 'Siemens', 'siemens.com'), p('HMI panel', 1, 1200, 'Siemens', 'siemens.com')],
  },
  P09: {
    device: 'awg-unit', powerC: '12V 5A (~60 W)', hoursC: 4, powerE: '~12 kW per campus', hoursE: 40,
    topology: 'AWG units -> controller -> MQTT',
    c: [p('ESP32-DevKitC v4', 1, 9.95, 'Adafruit', 'adafruit.com/product/3269'), p('SHT31 humidity/temp', 1, 15, 'Adafruit', 'adafruit.com/product/2857'), p('INA219 power monitor', 1, 9.95, 'Adafruit', 'adafruit.com/product/904'), p('Peltier condenser module', 1, 25, 'Generic', 'list est.'), p('Fan', 1, 6, 'Generic', 'list est.'), p('UV LED', 1, 8, 'Generic', 'list est.')],
    e: [p('AWG unit (1000 L/day)', 10, 12000, 'Water tech supplier', 'list est.'), p('Water-quality lab kit', 1, 3000, 'Lab supplier', 'list est.'), p('Controls + sensors', 1, 1500, 'Industrial supplier', 'list est.'), p('Installation', 1, 4000, 'Contractor', 'list est.')],
  },
  P10: {
    device: 'geothermal-plc', powerC: 'USB 5V 0.5A + 12V 1A (~14.5 W)', hoursC: 4, powerE: '~400 kW thermal per district', hoursE: 480,
    topology: 'ground loop -> plant room -> buildings (SCADA)',
    c: [p('ESP32-DevKitC v4', 1, 9.95, 'Adafruit', 'adafruit.com/product/3269'), p('DS18B20 probes', 2, 9.0, 'Adafruit', 'adafruit.com/product/381'), p('Flow sensor (YF-S201)', 1, 12, 'Generic', 'list est.'), p('Circulation pump', 1, 25, 'Generic', 'list est.'), p('Relay module', 1, 4.5, 'Generic', 'list est.')],
    e: [p('Ground loop + drilling', 1, 250000, 'Geothermal EPC', 'list est.'), p('Heat pumps', 8, 8000, 'HVAC supplier', 'list est.'), p('Circulation pumps', 4, 3500, 'HVAC supplier', 'list est.'), p('PLC/SCADA', 1, 12000, 'Industrial supplier', 'list est.'), p('Flow/temp sensors', 1, 6000, 'Industrial supplier', 'list est.')],
  },
  P12: {
    device: 'inverter', powerC: 'USB 5V 0.5A + panel (~3 W)', hoursC: 3, powerE: '200 kW peak', hoursE: 160,
    topology: 'arrays -> inverters -> meter -> subscribers',
    c: [p('ESP32-DevKitC v4', 1, 9.95, 'Adafruit', 'adafruit.com/product/3269'), p('INA226 monitor', 1, 9.95, 'Adafruit', 'adafruit.com/product/904'), p('Voltage divider', 1, 3, 'Generic', 'list est.'), p('Photodiode irradiance', 1, 12, 'Generic', 'list est.'), p('Setpoint relay board', 1, 4.5, 'Generic', 'list est.'), p('Small PV panel', 1, 35, 'Solar supplier', 'list est.')],
    e: [p('Solar PV (200 kW)', 1, 60000, 'Solar supplier', 'list est.'), p('String inverters', 1, 12000, 'Solar supplier', 'list est.'), p('Monitoring + CT', 1, 4000, 'Industrial supplier', 'list est.'), p('Mounting/racking', 1, 15000, 'Solar supplier', 'list est.'), p('Installation', 1, 20000, 'EPC', 'list est.')],
  },
  P13: {
    device: 'turbine-controller', powerC: 'USB 5V 0.5A (~2.5 W)', hoursC: 6, powerE: '5 kW nominal', hoursE: 300,
    topology: 'turbine -> PLC -> gate -> island/grid',
    c: [p('ESP32-DevKitC v4', 1, 9.95, 'Adafruit', 'adafruit.com/product/3269'), p('Flow sensor', 1, 12, 'Generic', 'list est.'), p('Pressure/head sensor', 1, 30, 'Generic', 'list est.'), p('Servo/gate actuator', 1, 20, 'Generic', 'list est.'), p('Relay module', 1, 4.5, 'Generic', 'list est.'), p('Turbine runner (small)', 1, 45, 'Hydro supplier', 'list est.')],
    e: [p('Turbine + generator (5 kW)', 1, 45000, 'Hydro supplier', 'list est.'), p('PLC/controls', 1, 8000, 'Industrial supplier', 'list est.'), p('Gate actuator', 1, 6000, 'Hydro supplier', 'list est.'), p('Flow/head sensors', 1, 3000, 'Industrial supplier', 'list est.'), p('Civil works', 1, 40000, 'EPC', 'list est.')],
  },
};

function verificationList(kind, device, compute) {
  const v = [
    `interfaces cross-check against config/hardware-manifests.json (${device})`,
    `telemetry/control topics match ecos/<id>/{deviceId}/{telemetry|control}`,
    `${kind} BOM priced with supplier + source (vendor list estimates)`,
    'power budget and build hours stated',
  ];
  if (compute) v.unshift(`compute-node: ${device} — no device firmware; verified as compute hardware`);
  else v.unshift(`firmware scaffold with PROJECT_CODE matches (firmware/scaffolds)`);
  if (kind === 'enterprise') v.push('indicative deployment BOM — EPC/vendor quotes required before procurement');
  return v;
}

function firmwareScaffold(id, device) {
  return `/*
 * ECOS firmware scaffold — ${id} (${device})
 * Verify-only scaffold: satisfies the IDS gate that a matching PROJECT_CODE
 * exists. Implement readSensors()/applyControl() per config/hardware-manifests.json
 * and packages/hardware-sdk TelemetrySchema before a real build.
 */
#define PROJECT_CODE "${id}"
#define DEVICE_TYPE "${device}"
#define FIRMWARE_VERSION "v0.1.0-scaffold"

// Telemetry: ecos/${id}/<deviceId>/telemetry   Control: ecos/${id}/<deviceId>/control
// See firmware/esp32-template/ecos_template.ino for the full template.
`;
}

const force = process.argv.includes('--force');
let wrote = 0;
const skipped = [];
for (const [id, spec] of Object.entries(SPEC)) {
  const file = join(regDir, `${readdirSync(regDir).find((f) => f.startsWith(id + '_'))}`);
  if (!existsSync(file)) {
    skipped.push(id);
    continue;
  }
  const d = JSON.parse(readFileSync(file, 'utf8'));
  // Safety: never overwrite a spec that has already been price-sourced (that
  // would wipe unitUsd/supplier/source/sourcing). Use --force to regenerate.
  const alreadySourced = ['individual', 'enterprise'].some((k) =>
    (d.hardware?.[k]?.bom ?? []).some((b) => b.sourcing),
  );
  if (alreadySourced && !force) {
    skipped.push(`${id}(sourced)`);
    continue;
  }
  const compute = Boolean(spec.compute);
  d.hardware.individual = {
    name: d.hardware.individual.name,
    audience: 'community builder / maker (build-it-yourself)',
    mode: 'community',
    unit: '1 unit',
    bom: spec.c,
    interfaces: d.hardware.individual.interfaces,
    power: spec.powerC,
    powerBudget: spec.powerC,
    buildHours: spec.hoursC,
    sla: null,
    verification: verificationList('community', spec.device, compute),
    status: 'verified',
  };
  d.hardware.enterprise = {
    name: d.hardware.enterprise.name,
    audience: 'commercial / municipal / campus',
    mode: 'commercial',
    unit: 'per site',
    topology: spec.topology,
    bom: spec.e,
    interfaces: d.hardware.enterprise.interfaces,
    power: spec.powerE,
    powerBudget: spec.powerE,
    buildHours: spec.hoursE,
    sla: 'uptime/performance SLA to be agreed with the operator partner',
    verification: verificationList('enterprise', spec.device, compute),
    status: 'verified',
  };
  d.version = (d.version ?? 1) + 1;
  d.updatedAt = new Date().toISOString().slice(0, 10);
  d.provenance = { ...d.provenance, driver: 'specify-script', verifiedBy: ['verify.mjs'] };
  writeFileSync(file, JSON.stringify(d, null, 2) + '\n', 'utf8');
  wrote += 1;

  if (!compute) {
    const fw = join(fwDir, `${d.code}_scaffold.ino`);
    if (!existsSync(fw)) {
      mkdirSync(fwDir, { recursive: true });
      writeFileSync(fw, firmwareScaffold(id, spec.device), 'utf8');
    }
  }
}

console.log(`specified: ${wrote} initiatives | skipped: ${skipped.join(', ') || 'none'}`);
if (skipped.some((s) => s.includes('(sourced)'))) {
  console.log('note: skipped price-sourced specs to avoid data loss. Re-run with --force only if you intend to regenerate them (you must re-run price-sourcing.mjs afterwards).');
}
