#!/usr/bin/env node
/**
 * RFQ tracker for quote-required BOM lines (capital equipment with no public
 * list price).
 *
 *   node initiatives/rfq.mjs            generate initiatives/rfq/RFQ.md
 *   node initiatives/rfq.mjs --apply    apply initiatives/rfq/quotes.json
 *
 * quotes.json entries: { "code": "P10_GEOTHERMAL", "part": "Ground loop + drilling",
 *                        "unitUsd": 245000, "supplier": "Acme Geothermal",
 *                        "ref": "Q-2026-114" }
 * Applying a quote sets the line's price, supplier, source (quote ref) and
 * sourcing:"quoted", then re-verifies. Nothing is written for unmatched lines.
 */
import { readFileSync, writeFileSync, readdirSync, existsSync, mkdirSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const regDir = join(here, 'registry');
const rfqDir = join(here, 'rfq');
const rfqFile = join(rfqDir, 'RFQ.md');
const quotesFile = join(rfqDir, 'quotes.json');

function loadRegistry() {
  return readdirSync(regDir)
    .filter((f) => f.endsWith('.json'))
    .map((f) => ({ file: join(regDir, f), data: JSON.parse(readFileSync(join(regDir, f), 'utf8')) }));
}

if (process.argv.includes('--apply')) {
  if (!existsSync(quotesFile)) {
    console.error(`no ${quotesFile}`);
    process.exit(2);
  }
  const quotes = JSON.parse(readFileSync(quotesFile, 'utf8'));
  let applied = 0;
  let missed = 0;
  for (const q of quotes) {
    const entry = loadRegistry().find((e) => e.data.code === q.code);
    if (!entry) {
      missed += 1;
      continue;
    }
    let found = false;
    for (const tier of ['individual', 'enterprise']) {
      for (const b of entry.data.hardware?.[tier]?.bom ?? []) {
        if (b.part === q.part) {
          b.unitUsd = q.unitUsd;
          b.supplier = q.supplier;
          b.source = `quote ${q.ref ?? 'provided'} (${new Date().toISOString().slice(0, 10)})`;
          b.sourcing = 'quoted';
          found = true;
        }
      }
    }
    if (found) {
      writeFileSync(entry.file, JSON.stringify(entry.data, null, 2) + '\n', 'utf8');
      applied += 1;
    } else {
      missed += 1;
    }
  }
  try {
    execFileSync('node', [join(here, 'verify.mjs')], { cwd: join(here, '..'), stdio: 'inherit' });
  } catch {
    console.error('verify failed after applying quotes');
    process.exit(1);
  }
  console.log(`quotes applied: ${applied}, unmatched: ${missed}`);
  process.exit(0);
}

// generate RFQ.md
const entries = loadRegistry().sort((a, b) => a.data.id.localeCompare(b.data.id));
const L = ['# RFQ — Quote-Required BOM Lines', '', 'Capital equipment with no public list price. Fill a quote per line into `initiatives/rfq/quotes.json`, then run `node initiatives/rfq.mjs --apply`.', ''];
let count = 0;
for (const { data } of entries) {
  const t = data.hardware?.enterprise;
  const lines = (t?.bom ?? []).filter((b) => b.sourcing === 'quote-required');
  if (lines.length === 0) continue;
  L.push(`## ${data.name} (${data.code}) — enterprise, ${t.unit ?? 'per site'}`);
  L.push('');
  L.push('| Part | Qty | Est. price (USD) | Quote (USD) | Supplier | MOQ / lead |');
  L.push('|---|---:|---:|---:|---|---|');
  for (const b of lines) {
    count += 1;
    L.push(`| ${b.part} | ${b.qty} | ${b.unitUsd ?? '—'} |  | ${b.supplier ?? ''} |  |`);
  }
  L.push('');
}
L.push(`_${count} lines awaiting quotes._`);
mkdirSync(rfqDir, { recursive: true });
writeFileSync(rfqFile, L.join('\n') + '\n', 'utf8');
if (!existsSync(quotesFile)) writeFileSync(quotesFile, '[]\n', 'utf8');
console.log(`RFQ written: ${rfqFile} (${count} lines)`);
