# P08 EverLume — Unit Economics (DRAFT)

> **Status: draft estimates, not verified.** Derived from the verified BOM in
> `initiatives/registry/P08_BULB.json`. Prices are list estimates; volumes,
> assembly labor, and offtake rates are assumptions to be replaced with real
> quotes. This sheet does **not** satisfy `founding.readiness.unitEconomics`
> until the numbers are sourced and the operator confirms them.

## Community tier (1 bench fixture)

| Line | Value | Basis |
|---|---:|---|
| BOM (verified) | $42.85 | sum of verified BOM lines |
| Packaging + handling (est.) | $6.00 | assumption |
| **Community kit cost** | **$48.85** | |
| Suggested community price | $55.00 | at-cost + handling; community mode = learning, not margin |

Community tier is a participation/learning product; margin is not the goal.

## Enterprise tier (per 100-fixture building)

| Line | Value | Basis |
|---|---:|---|
| Fixtures + drivers + mesh (100 × $88) | $8,800 | verified BOM |
| Meters (8 × $20) | $160 | verified BOM |
| Gateway + switch | $270 | verified BOM |
| **Hardware subtotal** | **$9,230** | |
| Installation (24 h × $95/h crew, est.) | $2,280 | assumption |
| **Deployed cost (est.)** | **$11,510** | |

Revenue model (LaaS, assumption): $50/fixture/month × 100 = **$5,000/mo**
($60,000/yr). Simple payback ≈ **2.3 months** on deployed cost — attractive, but
this depends on the underwriting partner and the achieved uptime/SLA.

## What is missing to call this "verified"

- Real vendor quotes (not list estimates) at order quantity.
- Real installation hours from a pilot building.
- A signed offtake/LaaS rate (partner LOI → definitive agreement).
- Warranty/underwriting cost, which the uptime guarantee requires.

Until then `readiness.unitEconomics` stays `false`.
