#!/usr/bin/env node
/**
 * Apply verified vendor list prices to registry BOM lines and honestly label
 * everything that has no public list price.
 *
 * Prices below were read from the vendor product pages (see source URLs) on
 * 2026-09-12. Lines that don't match a verified component are relabelled as
 * "estimate — vendor quote required" rather than left as a vague "list est.".
 *
 * Usage: node initiatives/price-sourcing.mjs
 */
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const regDir = join(here, 'registry');

// Verified from vendor pages (price as listed on 2026-09-12).
const REAL = [
  { match: /esp32/i, unitUsd: 15.0, supplier: 'Adafruit', source: 'https://www.adafruit.com/product/3269 — $15.00 (2026-09-12)' },
  { match: /dht22/i, unitUsd: 9.95, supplier: 'Adafruit', source: 'https://www.adafruit.com/product/385 — $9.95 (discontinued)' },
  { match: /ina219/i, unitUsd: 9.95, supplier: 'Adafruit', source: 'https://www.adafruit.com/product/904 — $9.95 (2026-09-12)' },
  { match: /ds18b20/i, unitUsd: 9.95, supplier: 'Adafruit', source: 'https://www.adafruit.com/product/381 — $9.95 (2026-09-12)' },
  { match: /capacitive soil|stemma soil/i, unitUsd: 7.5, supplier: 'Adafruit', source: 'https://www.adafruit.com/product/4026 — $7.50 (2026-09-12)' },
  { match: /sht31/i, unitUsd: 13.95, supplier: 'Adafruit', source: 'https://www.adafruit.com/product/2857 — $13.95 (2026-09-12)' },
  { match: /^(5v )?relay (module|board)$|^setpoint relay board$/i, unitUsd: 6.95, supplier: 'Adafruit', source: 'https://www.adafruit.com/product/4409 — STEMMA mini relay $6.95 (2026-09-12)' },
  { match: /^flow sensor( \(yf-s201\))?$/i, unitUsd: 9.95, supplier: 'Adafruit', source: 'https://www.adafruit.com/product/828 — liquid flow meter $9.95 (2026-09-12)' },
  { match: /^peristaltic (dosing|feed) pump$/i, unitUsd: 24.95, supplier: 'Adafruit', source: 'https://www.adafruit.com/product/1150 — peristaltic pump $24.95 (2026-09-12)' },
  { match: /^air pump$/i, unitUsd: 7.95, supplier: 'Adafruit', source: 'https://www.adafruit.com/product/4699 — air pump $7.95 (2026-09-12)' },
  { match: /^load cell \(350 ohm\)$/i, unitUsd: 3.95, supplier: 'Adafruit', source: 'https://www.adafruit.com/product/4541 — 5Kg strain gauge load cell $3.95 (2026-09-12)' },
  { match: /^hx711 amplifier$/i, unitUsd: 9.95, supplier: 'Adafruit', source: 'https://www.adafruit.com/product/5974 — HX711 24-bit ADC $9.95 (2026-09-12)' },
  { match: /^max6675 \+ thermocouple$/i, unitUsd: 24.9, supplier: 'Adafruit', source: 'MAX31855 $14.95 (adafruit.com/product/269) + Type-K thermocouple $9.95 (product/270) = $24.90 (2026-09-12)' },
  { match: /sgp30/i, unitUsd: 17.5, supplier: 'Adafruit', source: 'https://www.adafruit.com/product/3709 — SGP30 VOC/eCO2 $17.50 (2026-09-12)' },
  { match: /^4-channel led driver$/i, unitUsd: 9.95, supplier: 'Adafruit', source: 'https://www.adafruit.com/product/5757 — Mosfetti 4-channel MOSFET driver $9.95 (2026-09-12)' },
  { match: /^peltier condenser module$/i, unitUsd: 34.95, supplier: 'Adafruit', source: 'https://www.adafruit.com/product/1335 — 12V 5A Peltier + heatsink $34.95 (2026-09-12)' },
  { match: /^servo\/gate actuator$/i, unitUsd: 12.0, supplier: 'Adafruit', source: 'https://www.adafruit.com/product/155 — TowerPro SG-5010 standard servo $12.00 (2026-09-12)' },
  { match: /^small pv panel$/i, unitUsd: 20.95, supplier: 'Adafruit', source: 'https://www.adafruit.com/product/5366 — 6V 2W solar panel $20.95 (2026-09-12)' },
  { match: /^5v fan$/i, unitUsd: 3.5, supplier: 'Adafruit', source: 'https://www.adafruit.com/product/3368 — miniature 5V fan $3.50 (2026-09-12)' },
  { match: /^fan$/i, unitUsd: 5.5, supplier: 'Adafruit', source: 'https://www.adafruit.com/product/6103 — 5V 6cm fan $5.50 (2026-09-12)' },
  { match: /^photodiode irradiance$/i, unitUsd: 7.5, supplier: 'Adafruit', source: 'https://www.adafruit.com/product/6524 — TSL2585 ambient/UVA light sensor $7.50 (2026-09-12)' },
  { match: /^ph probe \+ board$/i, unitUsd: 29.5, supplier: 'DFRobot', source: 'https://www.dfrobot.com/product-1025.html — SEN0161 pH kit (board + probe) $29.50 (2026-09-12)' },
  { match: /^dissolved-oxygen probe$/i, unitUsd: 313.98, supplier: 'Atlas Scientific', source: 'DO probe $259.99 (atlas-scientific.com/probes/dissolved-oxygen-probe/) + EZO-DO circuit $53.99 (atlas-scientific.com/embedded-solutions/ezo-dissolved-oxygen-circuit/) = $313.98 (2026-09-12)' },
  { match: /^breadboard \+ jumper(s| kit)$/i, unitUsd: 9.95, supplier: 'Adafruit', source: 'https://www.adafruit.com/product/3314 — half-size breadboard + 78-piece jumper bundle $9.95 (2026-09-12)' },
  { match: /^heating pad$/i, unitUsd: 7.95, supplier: 'Adafruit', source: 'https://www.adafruit.com/product/1481 — electric heating pad 10x5cm $7.95 (2026-09-12)' },
  { match: /^ppfd\/spectrum sensor$/i, unitUsd: 410.0, supplier: 'Apogee Instruments', source: 'https://www.apogeeinstruments.com/sq-500-ss-full-spectrum-quantum-sensor/ — SQ-500-SS full-spectrum quantum (PPFD) sensor $410.00 (2026-09-12)' },
  { match: /^moisture probe$/i, unitUsd: 7.5, supplier: 'Adafruit', source: 'https://www.adafruit.com/product/4026 — capacitive moisture sensor $7.50 (2026-09-12)' },
  { match: /^ina226 monitor$/i, unitUsd: 9.95, supplier: 'Adafruit', source: 'INA226 not stocked; INA260 substitute $9.95 — adafruit.com/product/4226 (2026-09-12)' },
];

// Commodity/multi-vendor items: list-priced but volatile and not stocked by the
// catalog vendors used here. Honest state is "procure at build time", not a
// guessed number.
const COMMODITY = /^(mini-pc \(8-core\)|32 gb ram|1 tb nvme|ups|network switch|frame hardware|tubing kit|voltage divider|rgbw \+ far-red led module|logic-level mosfet driver module|12v led cob \+ 12v 1a psu|uv led|circulation pump|pressure\/head sensor|turbine runner \(small\))$/i;

const ESTIMATE = 'estimate — no public list price (vendor quote required)';

let real = 0;
let estimate = 0;
let commodity = 0;

for (const f of readdirSync(regDir).filter((x) => x.endsWith('.json'))) {
  const file = join(regDir, f);
  const d = JSON.parse(readFileSync(file, 'utf8'));
  let changed = false;
  for (const tierName of ['individual', 'enterprise']) {
    const t = d.hardware?.[tierName];
    if (!t?.bom) continue;
    for (const line of t.bom) {
      const hit = REAL.find((r) => r.match.test(line.part));
      if (hit) {
        line.unitUsd = hit.unitUsd;
        line.supplier = hit.supplier;
        line.source = hit.source;
        line.sourcing = 'vendor-list';
        real += 1;
      } else if (/^https?:|^MAX31855|^DO probe/.test(line.source || '')) {
        // already sourced by hand
        line.sourcing = line.sourcing || 'vendor-list';
        real += 1;
      } else if (COMMODITY.test(line.part)) {
        line.source = 'commodity — procure at build time (multi-vendor, volatile price)';
        line.sourcing = 'commodity';
        commodity += 1;
      } else if (tierName === 'enterprise') {
        // capital equipment with no public list price — needs a vendor quote
        line.source = 'quote-required — no public list price (RFQ)';
        line.sourcing = 'quote-required';
        estimate += 1;
      } else {
        line.source = ESTIMATE;
        line.sourcing = 'estimate';
        estimate += 1;
      }
      changed = true;
    }
  }
  if (changed) writeFileSync(file, JSON.stringify(d, null, 2) + '\n', 'utf8');
}

console.log(`BOM lines: ${real} vendor-list, ${commodity} commodity, ${estimate} estimate/quote-required`);
