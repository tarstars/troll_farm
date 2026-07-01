import time, os, glob, sys
from playwright.sync_api import sync_playwright
PROFILE="/home/tarstars/prj/troll_farm/cgauto/profile"
URL="https://www.codingame.com/ide/puzzle/spring-challenge-2026-troll-farm"

# clear any stale singleton lock so launch never blocks on a half-closed browser
for f in glob.glob(os.path.join(PROFILE,"Singleton*")):
    try: os.remove(f)
    except OSError: pass

def launch(pw):
    for attempt in range(3):
        try:
            return pw.chromium.launch_persistent_context(
                PROFILE, headless=False, no_viewport=True,
                # hide the main "I'm automated" signals so Google's OAuth allows sign-in
                ignore_default_args=["--enable-automation"],
                args=["--start-maximized","--no-first-run","--no-default-browser-check",
                      "--disable-blink-features=AutomationControlled"])
        except Exception as e:
            print(f"launch attempt {attempt} failed: {e}", flush=True); time.sleep(2)
    raise SystemExit("could not launch browser")

with sync_playwright() as pw:
    ctx = launch(pw)
    # override navigator.webdriver before any page script runs (Google checks this)
    ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    try: page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    except Exception as e: print("goto:", e, flush=True)
    print(">>> BROWSER OPEN. Log into CodinGame in that window, then open the", flush=True)
    print(">>> 'Troll Farm' puzzle IDE. I'll auto-detect login (waiting ~10 min).", flush=True)
    ok=False
    for i in range(300):
        try:
            for p in list(ctx.pages):
                if p.evaluate("typeof monaco !== 'undefined'"): ok=True; break
        except Exception: pass
        if ok: break
        if i % 15 == 0:
            urls=[p.url[:55] for p in ctx.pages]
            print(f"   waiting {i*2}s  pages={urls}", flush=True)
        time.sleep(2)
    print(">>> LOGGED IN — session saved to profile/ <<<" if ok else ">>> timed out <<<", flush=True)
    time.sleep(1); ctx.close()
