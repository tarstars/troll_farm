import time, sys
from playwright.sync_api import sync_playwright
PROFILE="/home/tarstars/prj/troll_farm/cgauto/profile"
URL="https://www.codingame.com/ide/puzzle/spring-challenge-2026-troll-farm"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 YaBrowser/25.8.0.0 Safari/537.36"
MAIN=sys.argv[1] if len(sys.argv)>1 else "/home/tarstars/prj/troll_farm/rust/src/main.rs"
code=open(MAIN).read()
# HARD SIZE GATE: CodinGame rejects sources over 100k chars. A stale/oversized
# artifact once burned 8+ submit attempts reading as throttle failures.
CG_LIMIT = 99000
if len(code) > CG_LIMIT:
    print(f"SIZE GATE: {MAIN} is {len(code)} chars > {CG_LIMIT} — REFUSING to submit."
          f" Minify first: rust/tools/minify.py", flush=True)
    sys.exit(2)
print(f"size gate ok: {len(code)} chars ({MAIN})", flush=True)

cks=[]
for line in open("/home/tarstars/prj/troll_farm/cgauto/cg_session.txt"):
    line=line.strip()
    if line and not line.startswith('#') and '=' in line:
        n,v=line.split('=',1); n,v=n.strip(),v.strip()
        if v and 'PASTE' not in v:
            cks.append({"name":n,"value":v,"domain":"www.codingame.com","path":"/","secure":True,"httpOnly":True,"sameSite":"Lax"})

with sync_playwright() as pw:
    ctx=pw.chromium.launch_persistent_context(PROFILE, headless=False, no_viewport=True, user_agent=UA,
        args=["--no-proxy-server","--disable-blink-features=AutomationControlled","--window-size=1680,1000"])
    ctx.add_cookies(cks)
    ctx.grant_permissions(["clipboard-read","clipboard-write"], origin="https://www.codingame.com")
    page=ctx.pages[0] if ctx.pages else ctx.new_page()
    for attempt in range(6):
        try:
            page.goto(URL, wait_until="domcontentloaded", timeout=90000)
            page.wait_for_selector(".monaco-editor", timeout=75000); break
        except Exception as e:
            print(f"load attempt {attempt} failed ({str(e)[:60]}); retry 25s", flush=True)
            if attempt==5: raise
            time.sleep(25)
    time.sleep(6)
    assert not page.evaluate("/SIGN UP AND START PLAYING/i.test(document.body.innerText)"), "not logged in"

    # set the code we want to submit
    page.evaluate("(t)=>navigator.clipboard.writeText(t)", code); time.sleep(0.4)
    page.click(".monaco-editor .view-lines"); time.sleep(0.4)
    page.keyboard.press("Control+a"); time.sleep(0.3)
    page.keyboard.press("Control+v"); time.sleep(2.5)
    page.keyboard.press("Control+Home"); time.sleep(0.5)
    vis=page.evaluate("(document.querySelector('.view-lines')||{}).innerText||''")
    print("code set; version visible:", ("1.0.1-denialrace" in vis), flush=True)

    # TEST IN ARENA -> the modal asks "Do you still want to submit? YES / CANCEL".
    # Must click the YES *button* (NOT the modal's "Submit" title).
    page.get_by_text("TEST IN ARENA", exact=False).first.click()
    print("clicked TEST IN ARENA; waiting for YES confirm…", flush=True)
    clicked=False
    for _ in range(20):
        time.sleep(1)
        for getter in [lambda: page.get_by_role("button", name="YES"),
                       lambda: page.get_by_role("button", name="Yes"),
                       lambda: page.locator("button", has_text="YES"),
                       lambda: page.get_by_text("YES", exact=True)]:
            try:
                el=getter().first
                if el.is_visible():
                    el.click(); clicked=True; print("clicked confirm YES", flush=True); break
            except Exception:
                pass
        if clicked: break
    print("YES confirm clicked:", clicked, flush=True)
    time.sleep(5)
    page.screenshot(path="/home/tarstars/prj/troll_farm/cgauto/submit.png")
    body=page.evaluate("document.body.innerText")
    import re
    hints=re.findall(r'(submitted|arena|in progress|rank|Boss|League|calculating|Battling)[^\n]{0,40}', body, re.I)
    print("post-submit hints:", hints[:12], flush=True)
    print("saved submit.png", flush=True)
    time.sleep(3)
    ctx.close()
