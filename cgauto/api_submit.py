#!/usr/bin/env python3
"""Submit a Troll Farm solution to the CG arena via the REST API directly,
bypassing the throttled browser IDE. Uses the session cookies in cg_session.txt.
Usage: api_submit.py <path-to-.rs>
"""
import sys, json, urllib.request, urllib.error
from pathlib import Path

PUZZLE = "spring-challenge-2026-troll-farm"
USERID = 1302251

# There is deliberately NO default source. Until 2026-08-12 an argument-less run
# silently submitted candidate-agent6553250-preseed-orchard-coverage-slim.min.rs
# (a8eb3b2b…, written 2026-07-17) — by then three residents stale. A mistyped or
# argument-less invocation would have replaced the live bot with a July source and
# forfeited a matured score, which is not recoverable by editing anything here.
# Submission is irreversible and outward-facing: it must be stated, never assumed.
if len(sys.argv) < 2:
    print(
        "USAGE GATE: api_submit.py <path-to-.rs>\n"
        "  No default source. Name the source you mean to submit.\n"
        "  Current resident (docs/STATE.md §1): 98628e98…\n"
        "    cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs\n"
        "  Programmatic callers should use api_submit_once.py, which requires an\n"
        "  explicit path AND its expected SHA-256."
    )
    sys.exit(2)

SOURCE = Path(sys.argv[1])
LANG = {".go": "Go", ".rs": "Rust"}.get(SOURCE.suffix)
if LANG is None:
    print(f"LANGUAGE GATE: unsupported extension {SOURCE.suffix!r}"); sys.exit(2)
CODE = SOURCE.read_text()

if len(CODE) > 100000:
    print(f"SIZE GATE: {len(CODE)} > 100000 — abort"); sys.exit(2)

cookies = []
for line in open("/home/tarstars/prj/troll_farm/cgauto/cg_session.txt"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        n, v = line.split("=", 1)
        n, v = n.strip(), v.strip()
        if n == "rememberMe" and v and "PASTE" not in v:
            cookies.append(f"{n}={v}")
COOKIE = "; ".join(cookies)

def call(service, method, payload):
    url = f"https://www.codingame.com/services/{service}/{method}"
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Cookie": COOKIE,
                 "User-Agent": "Mozilla/5.0"})
    try:
        r = urllib.request.urlopen(req, timeout=30)
        return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:400]
    except Exception as e:
        return None, str(e)[:200]

# 1) fresh IDE session handle
st, body = call("Puzzle", "generateSessionFromPuzzlePrettyId", [USERID, PUZZLE, False])
print("session:", st, body[:200])
handle = json.loads(body)["handle"] if st == 200 else None
if not handle:
    sys.exit(1)

# 2) try known submit endpoints/shapes until one is accepted
attempts = [
    ("TestSession", "submit", [handle, {"code": CODE, "programmingLanguageId": LANG}, None]),
    ("TestSession", "submit", [handle, {"code": CODE, "programmingLanguageId": LANG}]),
    ("Solution", "submit", [USERID, {"testSessionHandle": handle, "code": CODE, "programmingLanguageId": LANG}]),
    ("Solution", "submit", [{"userId": USERID, "testSessionHandle": handle, "code": CODE, "programmingLanguageId": LANG}]),
]
for svc, m, payload in attempts:
    st, body = call(svc, m, payload)
    print(f"{svc}/{m}: {st} {body[:220]}")
    if st == 200:
        print("SUBMIT-OK via", svc, m)
        sys.exit(0)
print("no submit endpoint accepted")
sys.exit(3)
