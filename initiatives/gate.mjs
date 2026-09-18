#!/usr/bin/env node
/**
 * IDS apply gate — the writable half of the continuous-development loop.
 *
 * A driver (Recourse, a human, CI) proposes a new initiative spec. This gate:
 *   1. refuses anything outside initiatives/registry/P##_*.json
 *   2. snapshots the current file (journal + backup)
 *   3. writes the candidate and runs the verifier as the gate
 *   4. on pass  -> keeps it and records a rollback token
 *      on fail  -> restores the previous file and reports the verifier's reasons
 *
 * Usage:
 *   node initiatives/gate.mjs --driver recourse --file initiatives/registry/P08_BULB.json --source candidate.json
 *   node initiatives/gate.mjs --driver recourse --file initiatives/registry/P08_BULB.json < candidate.json
 *   node initiatives/gate.mjs --revert <token>
 *   node initiatives/gate.mjs --list
 *
 * Exit: 0 applied/reverted, 1 rejected/error, 2 usage/setup.
 */
import { readFileSync, writeFileSync, existsSync, mkdirSync, rmSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { createHash, randomBytes } from 'node:crypto';
import { join, dirname, resolve, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const ecosRoot = join(here, '..');
const registryDir = join(here, 'registry');
const verifier = join(here, 'verify.mjs');
const journalDir = join(ecosRoot, '.recourse', 'ecos-fleet');
const journalFile = join(journalDir, 'journal.json');

function readJournal() {
  try {
    const j = JSON.parse(readFileSync(journalFile, 'utf8'));
    if (j && Array.isArray(j.entries)) return j;
  } catch {
    /* no journal yet */
  }
  return { entries: [] };
}

function writeJournal(journal) {
  mkdirSync(journalDir, { recursive: true });
  const tmp = journalFile + '.tmp';
  writeFileSync(tmp, JSON.stringify(journal, null, 2), 'utf8');
  writeFileSync(journalFile, readFileSync(tmp));
  rmSync(tmp, { force: true });
}

function args() {
  const a = process.argv.slice(2);
  const out = { _: [] };
  for (let i = 0; i < a.length; i++) {
    if (a[i].startsWith('--')) {
      const key = a[i].slice(2);
      const next = a[i + 1];
      if (next && !next.startsWith('--')) {
        out[key] = next;
        i++;
      } else {
        out[key] = true;
      }
    } else out._.push(a[i]);
  }
  return out;
}

function runVerifier() {
  try {
    const out = execFileSync('node', [verifier], { encoding: 'utf8', cwd: ecosRoot });
    return { ok: true, output: out.trim() };
  } catch (e) {
    const text = `${e.stdout ?? ''}${e.stderr ?? ''}`.trim() || e.message;
    return { ok: false, output: text };
  }
}

const a = args();

// --list
if (a.list) {
  const j = readJournal();
  console.log(JSON.stringify(j.entries.map(({ token, driver, file, ts, reverted }) => ({ token, driver, file, ts, reverted })), null, 2));
  process.exit(0);
}

// --revert <token>
if (a.revert) {
  const journal = readJournal();
  const entry = journal.entries.find((e) => e.token === a.revert);
  if (!entry) {
    console.error(`no applied patch with token ${a.revert}`);
    process.exit(1);
  }
  if (entry.reverted) {
    console.error(`token ${a.revert} already reverted`);
    process.exit(1);
  }
  const abs = resolve(ecosRoot, entry.file);
  if (!abs.startsWith(resolve(registryDir))) {
    console.error('refusing revert outside registry/');
    process.exit(1);
  }
  if (entry.prevExisted && entry.prevSource != null) writeFileSync(abs, entry.prevSource, 'utf8');
  else rmSync(abs, { force: true });
  entry.reverted = true;
  entry.revertedAt = Date.now();
  writeJournal(journal);
  console.log(`reverted ${entry.file}`);
  process.exit(0);
}

// apply
if (!a.driver || !a.file) {
  console.error('usage: node initiatives/gate.mjs --driver <id> --file initiatives/registry/<CODE>.json [--source <file>]');
  process.exit(2);
}

const absTarget = resolve(ecosRoot, a.file);
const rel = relative(registryDir, absTarget).replace(/\\/g, '/');
if (rel.startsWith('..') || resolve(absTarget) === resolve(registryDir)) {
  console.error('refusing: file must be inside initiatives/registry/');
  process.exit(1);
}
if (!/^P\d{2}_[A-Z_]+\.json$/.test(rel)) {
  console.error(`refusing: filename must match P##_CODE.json (got ${rel})`);
  process.exit(1);
}

let candidate;
if (a.source) {
  candidate = readFileSync(resolve(a.source), 'utf8');
} else {
  candidate = readFileSync(0, 'utf8'); // stdin
}
try {
  JSON.parse(candidate);
} catch (e) {
  console.error(`refusing: candidate is not valid JSON (${e.message})`);
  process.exit(1);
}

mkdirSync(journalDir, { recursive: true });
const prevExisted = existsSync(absTarget);
const prevSource = prevExisted ? readFileSync(absTarget, 'utf8') : null;
writeFileSync(absTarget, candidate, 'utf8');

const verdict = runVerifier();
if (!verdict.ok) {
  // restore
  if (prevExisted && prevSource != null) writeFileSync(absTarget, prevSource, 'utf8');
  else rmSync(absTarget, { force: true });
  console.error('REJECTED by verifier — candidate not applied.');
  console.error(verdict.output);
  process.exit(1);
}

const journal = readJournal();
const token = randomBytes(6).toString('hex');
journal.entries.unshift({
  token,
  driver: a.driver,
  file: a.file.replace(/\\/g, '/'),
  hash: createHash('sha256').update(candidate).digest('hex').slice(0, 16),
  prevExisted,
  prevSource,
  ts: Date.now(),
  reverted: false,
});
if (journal.entries.length > 200) journal.entries.length = 200;
writeJournal(journal);

console.log(`APPLIED ${a.file} by ${a.driver}`);
console.log(verdict.output);
console.log(`rollback token: ${token}`);

// Keep the site in sync: regenerate the web IDS export after a successful apply.
try {
  execFileSync('node', [join(here, 'export-web.mjs')], { cwd: ecosRoot, stdio: 'inherit' });
} catch {
  console.error('warning: web export failed — the site may be stale until export-web.mjs runs');
}
process.exit(0);
