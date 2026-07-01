import time, os, shutil
from playwright.sync_api import sync_playwright
PROFILE="/home/tarstars/prj/troll_farm/cgauto/yandex_profile"
YANDEX="/opt/yandex/browser/yandex_browser"
URL="https://www.codingame.com/ide/puzzle/spring-challenge-2026-troll-farm"
shutil.rmtree(os.path.join(PROFILE,"Default","Service Worker"), ignore_errors=True)
with sync_playwright() as pw:
    ctx=pw.chromium.launch_persistent_context(PROFILE, executable_path=YANDEX, headless=False,
        no_viewport=True, args=["--no-first-run","--no-default-browser-check"])
    page=ctx.pages[0] if ctx.pages else ctx.new_page()
    try: page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    except Exception as e: print("goto:", e, flush=True)
    ok=False
    for i in range(30):
        time.sleep(2)
        try:
            m=page.evaluate("typeof monaco!=='undefined'")
            txt=page.evaluate("document.body?document.body.innerText.replace(/\\s+/g,' ').slice(0,110):''")
            print(f"[{i*2}s] monaco={m} body={txt!r}", flush=True)
            if m: ok=True; print(">>> LOGGED IN (IDE loaded) <<<", flush=True); break
        except Exception as e: print(f"[{i*2}s] err {e}", flush=True)
    print("FINAL:", "LOGGED IN" if ok else "NOT loaded/logged-in", flush=True)
    page.screenshot(path="/home/tarstars/prj/troll_farm/cgauto/yandex_test3.png")
    ctx.close()
