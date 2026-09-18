#!/usr/bin/env node
/**
 * Export the IDS registry to the web app as a static module the site imports at
 * build time. Runs after every successful gate apply so the site always shows
 * verified state. Read-only over registry/; writes ONE generated file.
 *
 * Usage: node initiatives/export-web.mjs
 */
import { readFileSync, writeFileSync, readdirSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const ecosRoot = join(here, '..');
const regDir = join(here, 'registry');
const outFile = join(ecosRoot, 'apps', 'web', 'src', 'lib', 'initiatives.generated.json');

if (!existsSync(regDir)) {
  console.error('no registry/ to export');
  process.exit(1);
}

const out = {};
for (const f of readdirSync(regDir).filter((x) => x.endsWith('.json'))) {
  const d = JSON.parse(readFileSync(join(regDir, f), 'utf8'));
  const ind = d.hardware?.individual ?? {};
  const ent = d.hardware?.enterprise ?? {};
  const r = d.founding?.readiness ?? {};
  out[d.code] = {
    code: d.code,
    id: d.id,
    name: d.name,
    type: d.type,
    stage: d.stage,
    phase: d.phase,
    tracks: d.tracks,
    software: d.software,
    hardware: d.hardware,
    founding: d.founding,
    derived: {
      readinessScore: [r.hardwarePilot, r.partnerLoi, r.unitEconomics].filter(Boolean).length,
      gapCount:
        (Array.isArray(ind.missing) ? ind.missing.length : 0) +
        (Array.isArray(ent.missing) ? ent.missing.length : 0),
    },
  };
}

const next = JSON.stringify(out, null, 2) + '\n';
const check = process.argv.includes('--check');
if (check) {
  const current = existsSync(outFile) ? readFileSync(outFile, 'utf8') : '';
  if (current !== next) {
    console.error('STALE: apps/web/src/lib/initiatives.generated.json is out of sync with registry/. Run: node initiatives/export-web.mjs');
    process.exit(1);
  }
  console.log(`in sync: ${Object.keys(out).length} IDS`);
  process.exit(0);
}
writeFileSync(outFile, next, 'utf8');
console.log(`exported ${Object.keys(out).length} IDS -> ${outFile}`);
