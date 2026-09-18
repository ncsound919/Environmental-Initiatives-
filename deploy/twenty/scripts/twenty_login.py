"""Log into the local Twenty instance with Playwright and save the session.

Credentials are read from a gitignored file so they are never typed into chat
or committed. Create `deploy/twenty/.login.local` with two lines:

    EMAIL=you@example.com
    PASSWORD=your-password

Usage:
    python scripts/twenty_login.py
    python scripts/twenty_login.py --headed   # watch the browser

On success it writes the Playwright storage state to `deploy/twenty/.auth.json`
(also gitignored), which later automation scripts reuse.
"""

import argparse
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = os.environ.get("TWENTY_BASE_URL", "http://localhost:3300")
HERE = Path(__file__).resolve().parent.parent
LOGIN_FILE = HERE / ".login.local"
STATE_FILE = HERE / ".auth.json"
SHOT_DIR = HERE / "screenshots"


def read_credentials(path: Path) -> dict:
    if not path.exists():
        print(f"ERROR: credentials file not found: {path}")
        print("Create it with two lines: EMAIL=... and PASSWORD=... (it is gitignored).")
        sys.exit(2)
    creds = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        creds[key.strip().upper()] = value.strip()
    if not creds.get("EMAIL") or not creds.get("PASSWORD"):
        print(f"ERROR: {path} must define both EMAIL and PASSWORD.")
        sys.exit(2)
    return creds


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--headed", action="store_true", help="run a visible browser")
    args = ap.parse_args()

    creds = read_credentials(LOGIN_FILE)
    SHOT_DIR.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright

    def shot(page, name):
        path = SHOT_DIR / f"login_{name}.png"
        page.screenshot(path=str(path), full_page=True)
        print(f"  screenshot: {path}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        print("1. open", BASE_URL)
        page.goto(BASE_URL, wait_until="load", timeout=60000)
        page.wait_for_selector("input", timeout=20000)
        page.wait_for_timeout(1500)
        print("   url:", page.url)
        shot(page, "01_landing")

        all_inputs = page.eval_on_selector_all(
            "input",
            "els => els.map(e => ({type:e.type, name:e.name, placeholder:e.placeholder}))",
        )
        print("   inputs:", all_inputs)

        # Step 1: email
        email_input = page.get_by_placeholder("Email", exact=False)
        if email_input.count() == 0:
            email_input = page.locator("input").first
        email_input.fill(creds["EMAIL"])
        page.wait_for_timeout(500)

        def click_continue():
            for name in ["Continue", "Sign in", "Next", "Submit"]:
                loc = page.get_by_role("button", name=name)
                if loc.count() > 0:
                    loc.first.click()
                    return name
            return None

        clicked = click_continue()
        print("2. submitted email (button:", clicked, ")")
        page.wait_for_timeout(5000)
        print("   url:", page.url)
        shot(page, "02_after_email")

        body = page.inner_text("body") if page.locator("body").count() else ""

        # Step 2: password (if the flow asks for it)
        pwd = page.locator("input[type=password]").first
        if pwd.count() > 0:
            pwd.fill(creds["PASSWORD"])
            page.wait_for_timeout(500)
            clicked = click_continue()
            print("3. submitted password (button:", clicked, ")")
            page.wait_for_timeout(7000)
            print("   url:", page.url)
            shot(page, "03_after_password")
            body = page.inner_text("body") if page.locator("body").count() else ""
        else:
            print("3. no password field yet; current body:")
            print("   ", repr(body[:600]))

        # Save session regardless; caller inspects success
        context.storage_state(path=str(STATE_FILE))
        print("session state ->", STATE_FILE)

        logged_in = "/welcome" not in page.url and "sign in" not in page.title().lower()
        print("LOGGED_IN:", logged_in, "| final url:", page.url, "| title:", page.title())
        if not logged_in:
            print("   body tail:", repr(body[-400:]))

        browser.close()
        return 0 if logged_in else 1


if __name__ == "__main__":
    raise SystemExit(main())
