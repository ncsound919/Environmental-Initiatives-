#!/usr/bin/env node
/**
 * Nightly ECOS development loop (deterministic passes).
 *
 *   1. verify every IDS (the gate)
 *   2. export verified state to the web app
 *   3. compute the gap/readiness report
 *   4. optionally invoke an external driver to propose IDS improvements
 *
 * The driver step is honest: if ECOS_DRIVER_CMD is unset, it reports
 * "no driver configured" and produces the report only. When set, the command
 * runs with the gap report path in ECOS_REPORT; any proposals it makes must go
 * through initiatives/gate.mjs (that gate is the only writer).
 *
 * Writes reports/ecos-loop-YYYY-MM-DD.md in the Uplift repo.
 *
 * Usage: node initiatives/nightly.mjs
 */
import { readFileSync, readdirSync, writeFileSync, existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const ecosRoot = join(here, '..');
const regDir = join(here, 'registry');
const reportsDir = join(ecosRoot, '..', '..', 'reports');

function run(script) {
  try {
    const out = execFileSync('node', [join(here, script)], { cwd: ecosRoot, encoding: 'utf8' });
    return { ok: true, out: out.trim() };
  } catch (e) {
    return { ok: false, out: `${e.stdout ?? ''}${e.stderr ?? ''}`.trim() || e.message };
  }
}

const verify = run('verify.mjs');
const exp = run('export-web.mjs');
const readiness = run('readiness.mjs');

const specs = readdirSync(regDir)
  .filter((f) => f.endsWith('.json'))
  .map((f) => JSON.parse(readFileSync(join(regDir, f), 'utf8')));

const gaps = specs
  .map((s) => ({
    code: s.code,
    name: s.name,
    gaps:
      (s.hardware?.individual?.missing?.length ?? 0) + (s.hardware?.enterprise?.missing?.length ?? 0),
    missing: [
      ...(s.hardware?.individual?.missing ?? []).map((m) => `community: ${m}`),
      ...(s.hardware?.enterprise?.missing ?? []).map((m) => `enterprise: ${m}`),
    ],
  }))
  .sort((a, b) => b.gaps - a.gaps);

let driverCmd = process.env.ECOS_DRIVER_CMD;
let driverEnabled = true;
if (!driverCmd) {
  const cfgPath = join(here, 'driver.json');
  if (existsSync(cfgPath)) {
    try {
      const cfg = JSON.parse(readFileSync(cfgPath, 'utf8'));
      driverEnabled = cfg.enabled !== false;
      driverCmd =
        cfg.cmd ||
        (cfg.dir && cfg.script ? `npm --prefix "${resolve(ecosRoot, cfg.dir)}" run ${cfg.script}` : undefined);
    } catch {
      /* ignore malformed driver.json */
    }
  }
}
let driverNote;
if (!driverCmd || !driverEnabled) {
  driverNote = 'no driver configured/enabled (set ECOS_DRIVER_CMD or initiatives/driver.json); report-only run.';
} else {
  const reportPath = join(reportsDir, `ecos-loop-${new Date().toISOString().slice(0, 10)}.md`);
  try {
    const out = execFileSync(driverCmd, { shell: true, cwd: ecosRoot, encoding: 'utf8', env: { ...process.env, ECOS_REPORT: reportPath } });
    driverNote = `driver ran: ${driverCmd}\n${out.trim().slice(0, 1000)}`;
  } catch (e) {
    driverNote = `driver failed: ${e.message}`;
  }
}

const date = new Date().toISOString().slice(0, 10);
const md = [];
md.push(`# ECOS Development Loop — ${date}`);
md.push('');
md.push('## Gate');
md.push('```');
md.push(verify.out);
md.push('```');
md.push('');
md.push('## Gap report (draft items still to build)');
md.push('');
md.push('| Initiative | Gaps | Missing (community / enterprise) |');
md.push('|---|---:|---|');
for (const g of gaps) {
  md.push(`| ${g.name} (\`${g.code}\`) | ${g.gaps} | ${g.missing.join('; ') || '—'} |`);
}
md.push('');
md.push('## Readiness');
md.push('```');
md.push(readiness.out);
md.push('```');
md.push('');
md.push('## Driver');
md.push(driverNote);
md.push('');
md.push('## Notes');
md.push('- Every write goes through `initiatives/gate.mjs`; a rejected candidate leaves ECOS untouched.');
md.push('- `export-web.mjs` keeps the site in sync with verified IDS state.');

if (!existsSync(reportsDir)) {
  console.error(`reports dir not found: ${reportsDir}`);
  process.exit(2);
}
const outPath = join(reportsDir, `ecos-loop-${date}.md`);
writeFileSync(outPath, md.join('\n') + '\n', 'utf8');

console.log(`verify: ${verify.ok ? 'PASS' : 'FAIL'}`);
console.log(`export: ${exp.ok ? 'ok' : 'FAIL'}`);
console.log(`driver: ${driverNote.split('\n')[0]}`);
console.log(`report: ${outPath}`);
process.exit(verify.ok ? 0 : 1);
