# Documenso — ECOS e-signature (LOIs & pilot agreements)

Self-hosted [Documenso](https://github.com/documenso/documenso) for signing
Letters of Intent, pilot agreements, and offtake documents with partners.

- **URL (local):** http://localhost:3400
- **Health:** http://localhost:3400/api/health
- Data in Docker volumes `documenso_database` and `documenso_documenso_cert`.

## Start / stop

```bash
cd deploy/documenso
docker compose up -d         # first boot pulls the image + runs migrations
docker compose logs -f documenso
docker compose down
```

Secrets live in `.env` (generated, gitignored). Copy `.env.example` → `.env` and
fill the values if provisioning by hand (`openssl rand -base64 32` for each key).

## First run

Open http://localhost:3400 and create the owner account (first user is admin).

## Signing

Status: **enabled with a self-signed development certificate.**

```json
{"status":"ok","checks":{"database":{"status":"ok"},"certificate":{"status":"ok"}}}
```

A self-signed PKCS#12 was generated into the `documenso_documenso_cert` volume at
`/opt/documenso/cert.p12`, and `.env` holds:

```
NEXT_PRIVATE_SIGNING_LOCAL_FILE_PATH=/opt/documenso/cert.p12
NEXT_PRIVATE_SIGNING_PASSPHRASE=<generated>
```

Check status: `http://localhost:3400/api/certificate-status` →
`{"isAvailable":true}`.

**Honest caveat:** a self-signed certificate is fine for exercising the signing
flow locally, but external partners' PDF readers will not trust it and it is
**not** legally meaningful for enforceable LOIs. Replace it with a CA-issued
certificate before using e-signature with real counterparties: drop the new
`cert.p12` into the same volume path, update the passphrase in `.env`, then
`docker compose up -d`.

To regenerate the dev cert (dev only):

```bash
docker run --rm -v documenso_documenso_cert:/opt/documenso alpine sh -c \
  "apk add --no-cache openssl >/dev/null && cd /opt/documenso && \
   openssl req -x509 -newkey rsa:2048 -keyout k.pem -out c.pem -days 3650 -nodes -subj '/CN=Overlay ECOS Dev Signing' && \
   openssl pkcs12 -export -out cert.p12 -inkey k.pem -in c.pem -passout pass:<passphrase> && \
   chmod 644 cert.p12 && rm -f k.pem c.pem"
```

## Email (SMTP)

`NEXT_PRIVATE_SMTP_*` is required config but no mail server is connected, so
invitation/notification emails will not send. Signing links can still be copied
manually. Point it at a real SMTP provider when you start inviting signers.

## Production note

For production, serve Documenso on its own hostname (e.g.
`sign.ecos.example.com`) rather than a path prefix — Next.js apps don't handle
`basePath` cleanly. Add a site block in `deploy/caddy/Caddyfile` pointing at the
Documenso host/port.

## Files

| File | Purpose |
|---|---|
| `docker-compose.yml` | Documenso + Postgres 15 |
| `.env.example` | Template |
| `.env` | Generated secrets — **gitignored, never commit** |
| `README.md` | This file |

Adapted from Documenso's `docker/production/compose.yml`.
