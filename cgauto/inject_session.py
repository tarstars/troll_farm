import time, sys
from playwright.sync_api import sync_playwright
PROFILE="/home/tarstars/prj/troll_farm/cgauto/profile"
URL="https://www.codingame.com/ide/puzzle/spring-challenge-2026-troll-farm"

cks=[]
for line in open("/home/tarstars/prj/troll_farm/cgauto/cg_session.txt"):
    line=line.strip()
    if not line or line.startswith('#') or '=' not in line: continue
    name,val=line.split('=',1); name=name.strip(); val=val.strip()
    if not val or 'PASTE' in val: continue
    cks.append({"name":name,"value":val,"domain":"www.codingame.com","path":"/",
                "secure":True,"httpOnly":True,"sameSite":"Lax"})
if not cks:
    print("No cookie values found in cg_session.txt (still has PASTE placeholders?)"); sys.exit(1)
print("injecting:", [c['name'] for c in cks])

headful = "--headful" in sys.argv
with sync_playwright() as pw:
    ctx=pw.chromium.launch_persistent_context(PROFILE, headless=not headful,
        no_viewport=True, args=["--no-proxy-server","--disable-blink-features=AutomationControlled"])
    ctx.add_cookies(cks)
    page=ctx.pages[0] if ctx.pages else ctx.new_page()
    try: page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    except Exception as e: print("goto:", e)
    ok=False
    for i in range(20):
        try:
            if page.evaluate("typeof monaco!=='undefined'"): ok=True; break
        except Exception: pass
        time.sleep(2)
    print(">>> LOGGED IN — automation browser now has your CG session <<<" if ok
          else ">>> still not logged in (cookie maybe wrong/expired) <<<")
    ctx.close()
