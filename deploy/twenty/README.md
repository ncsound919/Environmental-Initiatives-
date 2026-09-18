# Twenty CRM — ECOS partner pipeline

Self-hosted [Twenty](https://github.com/twentyhq/twenty) instance that captures
ECOS partnership/funding inquiries and holds the partner pipeline.

- **URL (local):** http://localhost:3300 (workspace: **Overlay 365**)
- **Bound to loopback only** (`127.0.0.1`) on purpose — see Security.
- Data lives in Docker volumes `twenty_db-data` and `twenty_server-local-data`.

## Start / stop

```bash
cd deploy/twenty
docker compose up -d      # first boot runs DB migrations (~1–2 min)
docker compose ps         # server should be "healthy"
docker compose logs -f server
docker compose down       # stop (keeps volumes/data)
```

## Integration (implemented)

ECOS intake is wired to Twenty through the **REST API** using an API key. The
Next.js route `apps/web/src/app/api/partnership/route.ts` validates the inquiry
and then creates three records in Twenty:

| ECOS field | Twenty record |
|---|---|
| `organization` | **Company** |
| `contact_name` + `email` | **Person** (linked to the Company via `companyId`) |
| message + tracks/sectors/commitment | **Note** titled `Partnership inquiry — <org>` |

The token stays server-side in `apps/web/.env.local` (gitignored):

```
TWENTY_API_URL=http://localhost:3300
TWENTY_API_KEY=<jwt>
```

### Provisioning / refreshing the key

Twenty's plaintext API-key token is only returned by the `generateApiKeyToken`
mutation, so provisioning is scripted:

```bash
cd deploy/twenty
# one-time: create .login.local (EMAIL= / PASSWORD=), then:
python scripts/twenty_login.py       # logs in, saves session to .auth.json
python scripts/twenty_provision.py   # finds/creates the key, mints token, writes apps/web/.env.local
```

Restart the web app after provisioning so it picks up the env.

### Verify end-to-end

```bash
curl -X POST http://localhost:3000/api/partnership \
  -H "Content-Type: application/json" \
  -d '{"organization":"Acme Utilities","email":"jane@acme.example","message":"We can offer a pilot site and offtake for the solar sector.","consent":true}'
```

Expected: `{"ok":true,"delivered":true,"sink":"twenty","companyId":"…","personId":"…","noteId":"…"}`
and a new Company/Person/Note in Twenty. If Twenty is unreachable the route
returns `502`; if nothing is configured it returns `503` — it never fakes success.

### Alternative: Twenty workflow webhook (not used)

Twenty also supports a Workflow **Webhook** trigger (`Settings → Workflows`),
and the route keeps `PARTNERSHIP_INTAKE_WEBHOOK` support for it (or n8n/CRM).
It is not the chosen path because the workflow editor is a graph canvas (hard to
automate/verify) and, as of Twenty v2.37, the inbound webhook has **no auth**.

## Security

- **Loopback only.** Twenty's workflow inbound webhook has no authentication
  (Twenty docs: "coming soon") and the admin UI is privileged, so the port is
  not published to the LAN. The ECOS route is the validating/authenticating
  layer in front of it.
- **API key token** is a JWT minted by Twenty and stored only in
  `apps/web/.env.local` (gitignored). Rotate by revoking the key in
  `Settings → MCP & APIs → API` and re-running `twenty_provision.py`.
- **Local secrets** `deploy/twenty/.env` (DB password + `ENCRYPTION_KEY`),
  `.login.local`, and `.auth.json` are all gitignored. Delete `.login.local`
  and `.auth.json` when done automating.

## Backup / upgrade

```bash
docker compose exec db pg_dump -U twenty twenty > twenty-backup.sql   # backup
# set TAG in .env to a pinned release, then:
docker compose pull && docker compose up -d
```

## Files

| File | Purpose |
|---|---|
| `docker-compose.yml` | Server + worker + Postgres 16 + Redis |
| `.env.example` | Template (copy to `.env`) |
| `.env` | Generated secrets — **gitignored, never commit** |
| `scripts/twenty_login.py` | Playwright login → `.auth.json` |
| `scripts/twenty_provision.py` | Create/mint API key → `apps/web/.env.local` |
| `README.md` | This file |

Adapted from Twenty's official `packages/twenty-docker/docker-compose.yml`.
