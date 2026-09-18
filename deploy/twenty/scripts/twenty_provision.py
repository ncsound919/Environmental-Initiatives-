"""Provision ECOS intake against the local Twenty instance (idempotent).

Steps:
  1. Log in via a saved Playwright session (.auth.json) or fresh credentials
     from .login.local.
  2. Find (or create) the "ECOS partnership intake" API key.
  3. Mint the key's plaintext token via the generateApiKeyToken mutation.
  4. Write TWENTY_API_URL / TWENTY_API_KEY into apps/web/.env.local (gitignored).

Prerequisites: deploy/twenty/.login.local with EMAIL=/PASSWORD= (first run only),
and `python scripts/twenty_login.py` to create .auth.json.

Usage:  python scripts/twenty_provision.py
"""

import datetime
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent.parent                 # deploy/twenty
WEB_ENV = HERE.parent.parent / "apps" / "web" / ".env.local"
STATE = HERE / ".auth.json"
BASE = "http://localhost:3300"
KEY_NAME = "ECOS partnership intake"

from playwright.sync_api import sync_playwright

if not STATE.exists():
    print("ERROR: no session state. Run: python scripts/twenty_login.py")
    sys.exit(2)

expires = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)).strftime(
    "%Y-%m-%dT%H:%M:%S.000Z"
)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(storage_state=str(STATE))
    page = ctx.new_page()
    page.goto(BASE + "/objects/companies", wait_until="load", timeout=60000)
    page.wait_for_timeout(4000)
    out = page.evaluate(
        """
        async ({ keyName, expiresAt }) => {
          const meta = async (query, variables) => {
            const r = await fetch('/metadata', { method:'POST', headers:{'Content-Type':'application/json'},
              body: JSON.stringify({ query, variables }) });
            return { status: r.status, body: await r.json() };
          };
          const rest = async (method, url, body) => {
            const o = { method, headers: { 'Content-Type': 'application/json' } };
            if (body !== undefined) o.body = JSON.stringify(body);
            const r = await fetch(url, o);
            return { status: r.status, body: await r.json() };
          };

          const roles = await meta('{ getRoles { id label } }');
          const admin = (roles.body.data.getRoles || []).find(r => r.label === 'Admin');
          if (!admin) return { error: 'no Admin role' };

          const list = await rest('GET', '/rest/apiKeys');
          // Reuse any active ECOS key (name may be "ECOS intake REST" etc.).
          let key = (list.body || []).find(k => (k.name === keyName || k.name.startsWith('ECOS')) && !k.revokedAt);
          if (!key) {
            const created = await rest('POST', '/rest/apiKeys', { name: keyName, expiresAt, roleId: admin.id });
            if (created.status >= 300) return { error: 'create failed', created };
            key = created.body;
          }

          const token = await meta(
            'mutation($apiKeyId: UUID!, $expiresAt: String!){ generateApiKeyToken(apiKeyId:$apiKeyId, expiresAt:$expiresAt){ token } }',
            { apiKeyId: key.id, expiresAt: key.expiresAt },
          );
          return { key: { id: key.id, name: key.name, expiresAt: key.expiresAt }, tokenStatus: token.status, token: token.body };
        }
        """,
        {"keyName": KEY_NAME, "expiresAt": expires},
    )
    browser.close()

if out.get("error"):
    print("ERROR:", json.dumps(out)[:500])
    sys.exit(1)

token = ((out.get("token") or {}).get("data") or {}).get("generateApiKeyToken", {}).get("token")
if not token:
    print("ERROR: token not returned:", json.dumps(out.get("token"))[:500])
    sys.exit(1)

print("API key:", out["key"]["name"], "| id:", out["key"]["id"])
print(f"token len={len(token)} prefix={token[:6]}...")

lines = []
if WEB_ENV.exists():
    lines = [l for l in WEB_ENV.read_text(encoding="utf-8").splitlines() if not l.startswith(("TWENTY_API_URL=", "TWENTY_API_KEY="))]
lines += ["", "# Twenty CRM (run deploy/twenty/scripts/twenty_provision.py to refresh)", "TWENTY_API_URL=http://localhost:3300", f"TWENTY_API_KEY={token}"]
WEB_ENV.parent.mkdir(parents=True, exist_ok=True)
WEB_ENV.write_text("\n".join(lines).lstrip("\n") + "\n", encoding="utf-8")
print("wrote", WEB_ENV)
