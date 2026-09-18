#!/usr/bin/env node
/**
 * Founding-readiness report for Overlay Environmental initiatives.
 *
 * Deterministic over the IDS registry. Optionally cross-checks Twenty CRM for a
 * partner company matching each venture (real REST call when TWENTY_API_URL +
 * TWENTY_API_KEY are present in apps/web/.env.local). Missing config => the
 * partner signal is reported as "unknown", never guessed.
 *
 * Usage: node initiatives/readiness.mjs
 */
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const ecosRoot = join(here, '..');
const regDir = join(here, 'registry');
const envFile = join(ecosRoot, 'apps', 'web', '.env.local');

function readEnv(path) {
  const out = {};
  if (!existsSync(path)) return out;
  for (const line of readFileSync(path, 'utf8').split(/\r?\n/)) {
    const m = /^([^=]+)=(.*)$/.exec(line);
    if (m) out[m[1].trim()] = m[2].trim();
  }
  return out;
}

async function twentyCompanies(env) {
  const base = env.TWENTY_API_URL;
  const key = env.TWENTY_API_KEY;
  if (!base || !key) return { configured: false, names: [] };
  try {
    const res = await fetch(`${base.replace(/\/$/, '')}/rest/companies?limit=200`, {
      headers: { Authorization: `Bearer ${key}` },
      signal: AbortSignal.timeout(8000),
    });
    if (!res.ok) return { configured: true, names: [], error: `HTTP ${res.status}` };
    const data = await res.json();
    const names = (data?.data?.companies ?? []).map((c) => String(c.name ?? '').toLowerCase());
    return { configured: true, names };
  } catch (e) {
    return { configured: true, names: [], error: e instanceof Error ? e.message : String(e) };
  }
}

const files = readdirSync(regDir).filter((f) => f.endsWith('.json'));
const specs = files.map((f) => JSON.parse(readFileSync(join(regDir, f), 'utf8')));
const twenty = await twentyCompanies(readEnv(envFile));

console.log(`# Founding readiness — Overlay Environmental`);
console.log(`# initiatives: ${specs.length} | Twenty: ${twenty.configured ? (twenty.error ? `configured (${twenty.error})` : 'configured') : 'not configured'}\n`);
console.log('code                stage       verified  readiness  gaps  partner');
console.log('------------------  ----------  --------  ---------  ----  -------');
let ready = 0;
for (const s of specs.sort((a, b) => a.id.localeCompare(b.id))) {
  const verified = [s.hardware?.individual?.status, s.hardware?.enterprise?.status].filter((x) => x === 'verified').length;
  const r = s.founding?.readiness ?? {};
  const score = [r.hardwarePilot, r.partnerLoi, r.unitEconomics].filter(Boolean).length;
  if (score === 3) ready += 1;
  const gaps =
    (s.hardware?.individual?.missing?.length ?? 0) + (s.hardware?.enterprise?.missing?.length ?? 0);
  let partner = '—';
  if (twenty.configured && !twenty.error) {
    const name = String(s.founding?.ventureName ?? s.name).toLowerCase();
    partner = twenty.names.some((n) => n.includes(name) || name.includes(n)) ? 'LEAD' : 'none';
  } else {
    partner = 'unknown';
  }
  console.log(
    `${s.code.padEnd(18)}  ${String(s.stage).padEnd(10)}  ${String(verified).padEnd(8)}  ${`${score}/3`.padEnd(9)}  ${String(gaps).padEnd(4)}  ${partner}`,
  );
}
console.log(`\nfully ready for founding: ${ready}/${specs.length}`);
