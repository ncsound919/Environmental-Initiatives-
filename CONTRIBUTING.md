# Contributing to ECOS

**ECOS is a unified ecosystem. Changes to shared packages affect all 13 projects.**

## Table of Contents
- [Development Rules](#development-rules)
- [Getting Started](#getting-started)
- [Branch Strategy](#branch-strategy)
- [Commit Convention](#commit-convention)
- [Testing](#testing)
- [Adding a New Project](#adding-a-new-project)
- [Code Review](#code-review)

## Development Rules

These rules are non-negotiable. PRs violating them will be blocked.

1. **Never duplicate logic** — All optimization, forecasting, and solver code lives in `packages/ecosystem-brains`. Do not re-implement it in individual project routers.
2. **Single database schema** — Extend `packages/core/database-schema/schema.prisma` with additive migrations. Never create parallel schemas.
3. **Strict typing** — No `any` types in TypeScript. No untyped function signatures in Python. Use Zod for runtime validation on all API inputs.
4. **Test before merge** — All logic must have passing unit tests. CI will block merges if tests fail.

## Getting Started

```bash
# 1. Clone
git clone https://github.com/ncsound919/Environmental-Initiatives-.git
cd Environmental-Initiatives-

# 2. Install dependencies
npm install
pip install -r apps/api-gateway/requirements.txt

# 3. Copy environment config
cp .env.example .env
# Fill in your values: DATABASE_URL, AUTH0_DOMAIN, STRIPE_SECRET_KEY, etc.

# 4. Start services
docker compose up -d postgres redis mqtt

# 5. Seed the database
python scripts/seed.py

# 6. Start the API
cd apps/api-gateway && python main.py

# 7. Start the web app
cd apps/web && npm run dev
```

## Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready code only. Protected. |
| `develop` | Integration branch for feature work. |
| `feat/<name>` | New features. Branch from `develop`. |
| `fix/<name>` | Bug fixes. Branch from `develop`. |
| `docs/<name>` | Documentation changes only. |
| `chore/<name>` | Dependency updates, tooling. |

## Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(scope): <short description>

[optional body]
```

**Types:**
- `feat` — new feature
- `fix` — bug fix
- `docs` — documentation only
- `chore` — tooling, CI, dependencies
- `refactor` — code change that neither fixes a bug nor adds a feature
- `test` — adding or updating tests
- `ci` — CI/CD changes

**Scopes:** `P01`–`P13`, `auth`, `billing`, `api`, `db`, `firmware`, `ui`, `infra`

**Examples:**
```
feat(P09): add dew point calculation to AquaGen optimizer
fix(auth): handle expired Auth0 JWKS cache
chore(deps): upgrade Stripe SDK to 15.x
docs(P11): add BioSynth API usage examples
```

## Testing

### Python (FastAPI + ecosystem-brains)
```bash
cd apps/api-gateway
pytest tests/ -v --tb=short

cd packages/ecosystem-brains
pytest tests/ -v
```

### TypeScript
```bash
npx turbo run test
```

### Full CI locally
```bash
npx turbo run build lint type-check
python validate_structure.py
python validate_readiness.py
```

## Adding a New Project

ECOS slots P01–P13 are defined. If you are expanding (P14+), follow these steps:

1. Add project entry to the `PROJECTS` array in `scripts/seed.py`
2. Add a router at `apps/api-gateway/routers/<project_code>.py` following the P11 BioSynth template
3. Register the router in `apps/api-gateway/main.py`
4. Add Prisma models if new data models are needed (extend `schema.prisma`)
5. Add ESP32 firmware template to `firmware/` following the existing `esp32-template`
6. Update the project table in `README.md` and `IMPLEMENTATION_STATUS.md`
7. Run `python validate_structure.py` to confirm compliance

## Code Review

- All PRs require at least 1 approving review before merge
- Copilot review comments are informational — human sign-off is required
- New shared package changes (`ecosystem-brains`, `auth-module`, `billing-engine`) require 2 approvals
- Tag `@ncsound919` for final merge approval on any change that touches `packages/core/database-schema`

## Security

- Never commit secrets to the repo. Use `.env` (gitignored) or GitHub Secrets for CI.
- Run `npm audit` and `pip-audit` before submitting a PR that changes dependencies
- Report security vulnerabilities via GitHub Security Advisories, not public Issues

---

**Built for a sustainable future. Contribute with intention.**
