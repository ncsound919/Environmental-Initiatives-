# ECOS Initiatives — Initiative Development Specs (IDS)

One JSON file per initiative in `registry/`. Each IDS is the **continuous
development unit**: software capabilities, an **individual** and an
**enterprise** hardware setup, and a **founding** track — all machine-checked.

## Verify

```bash
node initiatives/verify.mjs
```

Exit 0 = every IDS passes the gate. Exit 1 = list of violations. The verifier is
dependency-free and deterministic; it is the gate a driver (e.g. Recourse) must
pass before an IDS update is promoted.

## What the verifier enforces

- Required fields + filename matches `code` (`<CODE>.json`).
- `stage`, `tracks`, capability `status`, tier `status`, `founding.status` enums.
- `id` exists in `config/hardware-manifests.json`.
- Tier `interfaces.sensors/actuators/deviceTypes` are declared for that `id`.
- Telemetry/control topics match `ecos/<id>/<deviceId>/{telemetry|control}`.
- BOM items: non-empty `part`, integer `qty >= 1`, valid `unitUsd`.
- **Honesty rules:** a `draft` tier must list `missing[]`; a `verified` tier must
  have `verification[]` and may not carry unpriced (`null`) BOM lines.
- `founding.entity`/`jurisdiction` required once `status != not_started`.

## Apply gate (`gate.mjs`)

The writable half of the loop. A driver proposes a candidate; the gate snapshots
the current file, writes it, runs `verify.mjs`, and keeps it **only on pass** —
otherwise it restores the previous file and reports the verifier's reasons.

```bash
# propose (candidate via --source file or stdin)
node initiatives/gate.mjs --driver recourse --file initiatives/registry/P08_BULB.json --source candidate.json

# inspect / undo
node initiatives/gate.mjs --list
node initiatives/gate.mjs --revert <token>
```

- Refuses any path outside `initiatives/registry/P##_*.json` (cannot touch ECOS
  source, env, CI, lockfiles).
- Journals every applied change with a rollback token under `.recourse/`
  (gitignored).
- Exit 0 = applied/reverted, 1 = rejected.

## The loop

```
Recourse dream/forge ──proposes IDS──▶ gate.mjs ──▶ verify.mjs
        ▲                                  │ pass            │ fail
        │ grounding signals                ▼                 ▼
ECOS corpus (read)          registry/<CODE>.json       restore previous
        ▲                    (+ journal/rollback)      + reason
        │                                  │
        │                                  ▼
ECOS site ◀── verified state ──   Founding track (Overlay 365 / Overlay Environmental)
```

Recourse side: `src/lib/ecosDevelopment.ts` (`applyEcosIdsPatch`,
`revertEcosPatch`, `listEcosPatches`) shells to this gate; it returns
`applied:true` only on a real gate pass. Verified by
`scripts/ecos-gate-selftest.ts`.

See `plans/2026-09-12-ecos-continuous-development.md` for the full blueprint.

## Development pipeline (order matters)

```
specify.mjs          author/refresh hardware tiers      (guarded: skips price-sourced specs; --force to regenerate)
price-sourcing.mjs   attach real vendor prices           (idempotent; sets `sourcing`)
gate.mjs             promote a candidate (verify+journal)  └─ runs export-web.mjs on success
rfq.mjs              generate RFQ / apply returned quotes
export-web.mjs       regenerate apps/web/src/lib/initiatives.generated.json (--check in CI)
verify.mjs           the gate
nightly.mjs          verify → export → readiness → driver → reports/ecos-loop-<date>.md
```

**Do not run `specify.mjs` after `price-sourcing.mjs`** unless you pass `--force` and intend to re-source — it regenerates BOMs from scratch and would drop prices. The guard makes this a no-op by default.

## Sourcing classes

Each BOM line carries `sourcing`: `vendor-list` (real dated price + URL), `quote-required` (capital → RFQ), `commodity` (procure at build), `quoted` (recorded quote), `estimate` (unresolved debt — warned).

## Adding an initiative

1. Copy an existing `registry/*.json`, set `code`/`id`/`name`/`type`/`phase`.
2. Fill `hardware.individual` and `hardware.enterprise`. If you don't yet have a
   real BOM/power/price, keep `status: "draft"` and list what's missing — never
   invent numbers.
3. `node initiatives/verify.mjs` must pass.
