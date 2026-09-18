# Caddy — ECOS single entrypoint

Reverse proxy that puts the Next.js web app and the two FastAPI backends behind
one address, with TLS.

- `http://localhost:8088` — HTTP entrypoint
- `https://localhost:8443` — TLS via Caddy's internal CA (`curl -k` locally)

## Start / stop

```bash
cd deploy/caddy
docker compose up -d
docker compose logs -f caddy
docker compose down
```

## Routing

Both FastAPI apps use `/api/*` prefixes, which would shadow the Next.js
`/api/partnership` route. Caddy therefore dispatches by explicit, ordered
matchers (see `Caddyfile`):

| Path | Upstream | Service |
|---|---|---|
| `/api/partnership*` | `WEB_UPSTREAM` | Next.js web (its own API route) |
| `/api/challenges*`, `/api/membership*`, `/api/marketplace*`, `/api/gamification*`, `/api/kits*` | `API_UPSTREAM` | `apps/api` (revenue) |
| `/api/hydro*`, `/api/solar*`, `/api/awg*`, `/api/bulb*`, `/api/farm*`, `/api/geothermal*`, `/api/symbiosis*`, `/api/dispatch*`, `/api/bioreactor*`, `/api/foam-homes*`, `/api/hemp-lab*`, `/api/reactor*`, `/api/greenhouse*`, `/projects` | `GATEWAY_UPSTREAM` | `apps/api-gateway` (13 brains) |
| everything else | `WEB_UPSTREAM` | Next.js web |

Verified:

```
web  /                    -> WEB_APP:/
web  /api/partnership     -> WEB_APP:/api/partnership
rev  /api/challenges      -> REVENUE_API:/api/challenges
gw   /api/hydro/forecast  -> GATEWAY_API:/api/hydro/forecast
tls  https://localhost:8443/api/challenges -> REVENUE_API:/api/challenges
```

## TLS

- **Local:** the `:8443` site uses `tls internal` (Caddy's own CA). Trust it with
  `docker compose exec caddy caddy trust` or just `curl -k`.
- **Production:** set `SITE_ADDRESS=ecos.example.com` and publish ports `80` and
  `443`; Caddy obtains and renews public certificates automatically.

## Upstreams

Defaults target apps on the host (`host.docker.internal`). If the ECOS stack runs
in Docker on `ecos-network`, set `WEB_UPSTREAM=web:3000`, `API_UPSTREAM=api:8000`,
`GATEWAY_UPSTREAM=api-gateway:8000` and attach this service to that network.

## Honest note

Explicit path matchers are a stopgap. The real fix for the "two competing
backends" issue (see `reports/2026-09-12-ecos-site-audit.md`) is to merge
`apps/api-gateway` into `apps/api` or give each a distinct, non-overlapping
prefix. Until then, new endpoints must be added to the matcher list.
