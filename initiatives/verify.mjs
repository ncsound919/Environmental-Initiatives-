#!/usr/bin/env node
/**
 * IDS verifier — the gate for continuously developing Overlay Environmental
 * initiatives. Deterministic, dependency-free.
 *
 * Validates every initiatives/registry/*.json against the IDS contract,
 * cross-checks hardware interfaces against config/hardware-manifests.json, and
 * enforces the portfolio identity from initiatives/portfolio.json (parent
 * Overlay 365, division Overlay Environmental). A driver (e.g. Recourse) may
 * only promote an IDS that passes here.
 *
 * Exit 0 = pass, 1 = fail (with reasons), 2 = setup error.
 * Usage: node initiatives/verify.mjs
 */
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const ecosRoot = join(here, '..');

const STAGES = new Set(['research', 'concept', 'prototype', 'pilot', 'verified', 'revenue']);
const TRACKS = new Set(['Grant', 'Strategic Partner', 'Revenue', 'Affiliate']);
const TIER_STATUS = new Set(['draft', 'verified']);
const CAP_STATUS = new Set(['planned', 'scaffold', 'heuristic', 'trained', 'validated']);
const FOUNDING = new Set(['not_started', 'readiness_assessed', 'venture_launched']);
const STRUCTURE = new Set(['division', 'subsidiary', 'spinoff']);
const INDIVIDUAL_MODE = 'community'; // operator decision: individual tier = community builds
const ENTERPRISE_MODES = new Set(['commercial', 'internal']);

const errors = [];
const warnings = [];
const sourcing = { 'vendor-list': 0, estimate: 0, 'quote-required': 0, quoted: 0, commodity: 0 };

function err(file, msg) {
  errors.push(`${file}: ${msg}`);
}

function warn(file, msg) {
  warnings.push(`${file}: ${msg}`);
}

/** Recursively find a firmware file under firmware/ whose PROJECT_CODE matches id. */
function findFirmwareFor(id) {
  const root = join(ecosRoot, 'firmware');
  const stack = [root];
  while (stack.length) {
    const dir = stack.pop();
    let entries;
    try {
      entries = readdirSync(dir, { withFileTypes: true });
    } catch {
      continue;
    }
    for (const e of entries) {
      const p = join(dir, e.name);
      if (e.isDirectory()) {
        stack.push(p);
      } else if (e.name.endsWith('.ino')) {
        const m = /#define\s+PROJECT_CODE\s+"([^"]+)"/.exec(readFileSync(p, 'utf8'));
        if (m && m[1] === id) return p;
      }
    }
  }
  return null;
}

// portfolio identity is the source of truth for parent/division
const portfolioPath = join(here, 'portfolio.json');
if (!existsSync(portfolioPath)) {
  console.error(`setup error: ${portfolioPath} not found`);
  process.exit(2);
}
const portfolio = JSON.parse(readFileSync(portfolioPath, 'utf8'));

const manifestPath = join(ecosRoot, 'config', 'hardware-manifests.json');
if (!existsSync(manifestPath)) {
  console.error(`setup error: ${manifestPath} not found`);
  process.exit(2);
}
const manifests = JSON.parse(readFileSync(manifestPath, 'utf8'));
const byId = new Map((manifests.initiatives ?? []).map((i) => [i.code, i]));

const regDir = join(here, 'registry');
if (!existsSync(regDir)) {
  console.error(`setup error: ${regDir} not found`);
  process.exit(2);
}
const files = readdirSync(regDir).filter((f) => f.endsWith('.json'));
if (files.length === 0) {
  console.error('setup error: no IDS files in registry/');
  process.exit(2);
}

for (const f of files) {
  let d;
  try {
    d = JSON.parse(readFileSync(join(regDir, f), 'utf8'));
  } catch (e) {
    err(f, `invalid JSON: ${e.message}`);
    continue;
  }

  for (const k of ['code', 'id', 'name', 'type', 'phase', 'stage', 'tracks', 'version', 'software', 'hardware', 'founding', 'provenance']) {
    if (!(k in d)) err(f, `missing required field "${k}"`);
  }
  if (f !== `${d.code}.json`) err(f, `filename must match code (${d.code}.json)`);
  if (!STAGES.has(d.stage)) err(f, `stage "${d.stage}" invalid`);
  if (!Array.isArray(d.tracks) || d.tracks.length === 0) err(f, 'tracks must be a non-empty array');
  else for (const t of d.tracks) if (!TRACKS.has(t)) err(f, `track "${t}" invalid`);
  if (!Number.isInteger(d.phase) || d.phase < 1 || d.phase > 4) err(f, 'phase must be 1..4');

  const man = byId.get(d.id);
  if (!man) err(f, `id "${d.id}" not found in hardware-manifests.json`);

  // software capabilities
  const caps = d.software?.capabilities;
  if (!Array.isArray(caps) || caps.length === 0) err(f, 'software.capabilities must be a non-empty array');
  else for (const c of caps) {
    if (!c.id || !c.name) err(f, 'capability requires id and name');
    if (!CAP_STATUS.has(c.status)) err(f, `capability "${c.id}" status "${c.status}" invalid`);
  }

  // hardware tiers
  const topicRe = new RegExp(`^ecos/${d.id}/[^/]+/(telemetry|control)$`);
  for (const tierName of ['individual', 'enterprise']) {
    const t = d.hardware?.[tierName];
    if (!t) {
      err(f, `hardware.${tierName} missing`);
      continue;
    }
    if (!TIER_STATUS.has(t.status)) err(f, `hardware.${tierName}.status "${t.status}" invalid`);

    // Operator decision: individual = community, enterprise = commercial/internal.
    if (tierName === 'individual' && t.mode !== INDIVIDUAL_MODE) err(f, `hardware.individual.mode must be "${INDIVIDUAL_MODE}"`);
    if (tierName === 'enterprise' && !ENTERPRISE_MODES.has(t.mode)) err(f, `hardware.enterprise.mode must be one of ${[...ENTERPRISE_MODES].join('/')}`);

    if (t.status === 'draft' && !(Array.isArray(t.missing) && t.missing.length > 0)) {
      err(f, `hardware.${tierName} is draft but lists no missing[] (no silent blanks)`);
    }
    if (t.status === 'verified' && !(Array.isArray(t.verification) && t.verification.length > 0)) {
      err(f, `hardware.${tierName} is verified but has no verification steps`);
    }
    if (t.status === 'verified') {
      for (const b of t.bom ?? []) {
        if (b.unitUsd == null) err(f, `hardware.${tierName} is verified but BOM "${b.part}" has no price`);
        if (!b.supplier) err(f, `hardware.${tierName} is verified but BOM "${b.part}" has no supplier`);
        if (!b.source) err(f, `hardware.${tierName} is verified but BOM "${b.part}" has no source`);
      }
      if (!t.power && !t.powerBudget) err(f, `hardware.${tierName} is verified but states no power/powerBudget`);
      if (typeof t.buildHours !== 'number') err(f, `hardware.${tierName} is verified but has no buildHours`);
      // Sourcing accounting: 'quote-required' is an acknowledged, expected state
      // for capital equipment; 'estimate' is unresolved debt and is warned.
      for (const b of t.bom ?? []) {
        const hasUrl = /(https?:\/\/|[\w.-]+\.[a-z]{2,}\/)/i.test(b.source || '');
        const kind = b.sourcing || (hasUrl ? 'vendor-list' : 'estimate');
        if (kind in sourcing) sourcing[kind] += 1;
        if (kind === 'estimate') {
          warn(f, `hardware.${tierName} BOM "${b.part}" is an unresolved estimate (no vendor price/quote)`);
        }
      }
    }

    for (const b of t.bom ?? []) {
      if (!b.part) err(f, `hardware.${tierName} BOM item missing "part"`);
      if (!Number.isInteger(b.qty) || b.qty < 1) err(f, `hardware.${tierName} BOM "${b.part}" qty must be integer >= 1`);
      if (b.unitUsd != null && (typeof b.unitUsd !== 'number' || b.unitUsd < 0)) {
        err(f, `hardware.${tierName} BOM "${b.part}" unitUsd invalid`);
      }
    }

    const it = t.interfaces ?? {};
    if (it.telemetryTopic && !topicRe.test(it.telemetryTopic)) {
      err(f, `hardware.${tierName}.telemetryTopic "${it.telemetryTopic}" must match ecos/${d.id}/<deviceId>/telemetry`);
    }
    if (it.controlTopic && !topicRe.test(it.controlTopic)) {
      err(f, `hardware.${tierName}.controlTopic "${it.controlTopic}" must match ecos/${d.id}/<deviceId>/control`);
    }
    if (man) {
      for (const s of it.sensors ?? []) {
        if (!man.sensors.includes(s)) err(f, `hardware.${tierName} sensor "${s}" not declared in manifest for ${d.id}`);
      }
      for (const a of it.actuators ?? []) {
        if (!man.actuators.includes(a)) err(f, `hardware.${tierName} actuator "${a}" not declared in manifest for ${d.id}`);
      }
      for (const dt of it.deviceTypes ?? []) {
        if (!man.deviceTypes.includes(dt)) err(f, `hardware.${tierName} deviceType "${dt}" not declared in manifest for ${d.id}`);
      }
    }
  }

  // A verified tier must be backed by real firmware configured for this project
  // (any .ino under firmware/ whose PROJECT_CODE matches), OR explicitly be a
  // compute node (marked with a "compute-node:" verification entry), since a
  // simulation/GPU node has no device firmware.
  const anyVerified = ['individual', 'enterprise'].some((k) => d.hardware?.[k]?.status === 'verified');
  if (anyVerified) {
    const hasFirmware = findFirmwareFor(d.id) !== null;
    const computeMarker = ['individual', 'enterprise']
      .flatMap((k) => d.hardware?.[k]?.verification ?? [])
      .some((v) => typeof v === 'string' && v.startsWith('compute-node:'));
    if (!hasFirmware && !computeMarker) {
      err(f, `verified tier requires firmware with PROJECT_CODE "${d.id}" under firmware/ (or a "compute-node:" verification entry)`);
    }
  }

  // founding — must sit under Overlay 365 / Overlay Environmental
  const fo = d.founding;
  if (!fo) err(f, 'founding missing');
  else {
    if (!FOUNDING.has(fo.status)) err(f, `founding.status "${fo.status}" invalid`);
    if (fo.parent !== portfolio.parent) err(f, `founding.parent must be "${portfolio.parent}"`);
    if (fo.division !== portfolio.division) err(f, `founding.division must be "${portfolio.division}"`);
    if (!fo.ventureName) err(f, 'founding.ventureName required');
    if (!STRUCTURE.has(fo.structure)) err(f, `founding.structure "${fo.structure}" invalid`);
    const r = fo.readiness;
    if (!r || typeof r.hardwarePilot !== 'boolean' || typeof r.partnerLoi !== 'boolean' || typeof r.unitEconomics !== 'boolean') {
      err(f, 'founding.readiness must have boolean hardwarePilot/partnerLoi/unitEconomics');
    } else if (r.hardwarePilot === true) {
      // Honesty: a hardware pilot cannot be claimed without a verified tier.
      const anyVerified = ['individual', 'enterprise'].some((k) => d.hardware?.[k]?.status === 'verified');
      if (!anyVerified) err(f, 'founding.readiness.hardwarePilot is true but no hardware tier is verified');
    }
  }

  if (!d.provenance || !Array.isArray(d.provenance.verifiedBy)) {
    err(f, 'provenance.verifiedBy must be an array');
  }
}

console.log(`IDS files checked: ${files.length}`);
console.log(
  `BOM sourcing: vendor-list ${sourcing['vendor-list']}, quote-required ${sourcing['quote-required']}, quoted ${sourcing.quoted}, commodity ${sourcing.commodity}, estimate ${sourcing.estimate}`,
);
if (warnings.length) {
  console.warn(`\nWARNINGS (${warnings.length}) — non-fatal, but these are sourcing debt:`);
  console.warn('  - ' + warnings.slice(0, 8).join('\n  - '));
  if (warnings.length > 8) console.warn(`  …and ${warnings.length - 8} more`);
}
if (errors.length) {
  console.error(`\nFAIL (${errors.length}):`);
  for (const e of errors) console.error('  - ' + e);
  process.exit(1);
}
console.log(`PASS — ${portfolio.parent} / ${portfolio.division}`);
