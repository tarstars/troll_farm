#!/usr/bin/env python3
"""Submit a Troll Farm solution to the CG arena via the REST API directly,
bypassing the throttled browser IDE. Uses the session cookies in cg_session.txt.
Usage: api_submit.py <path-to-.rs>
"""
import sys, json, urllib.request, urllib.error

PUZZLE = "spring-challenge-2026-troll-farm"
USERID = 1302251
LANG = "Rust"
CODE = open(sys.argv[1] if len(sys.argv) > 1 else
            "/home/tarstars/prj/troll_farm/cgauto/submissions/v1.26.0-jointmove.min.rs").read()

if len(CODE) > 100000:
    print(f"SIZE GATE: {len(CODE)} > 100000 — abort"); sys.exit(2)

cookies = []
for line in open("/home/tarstars/prj/troll_farm/cgauto/cg_session.txt"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        n, v = line.split("=", 1)
        n, v = n.strip(), v.strip()
        if v and "PASTE" not in v:
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
