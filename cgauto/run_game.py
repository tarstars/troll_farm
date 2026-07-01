import time, re, sys
from playwright.sync_api import sync_playwright
PROFILE="/home/tarstars/prj/troll_farm/cgauto/profile"
URL="https://www.codingame.com/ide/puzzle/spring-challenge-2026-troll-farm"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 YaBrowser/25.8.0.0 Safari/537.36"
MAIN="/home/tarstars/prj/troll_farm/rust/src/main.rs"

code=open(MAIN).read().replace("const DEBUG: bool = false;","const DEBUG: bool = true;")
assert "const DEBUG: bool = true;" in code, "DEBUG flip failed"

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
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_selector(".monaco-editor", timeout=40000); time.sleep(6)
    print("logged in:", not page.evaluate("/SIGN UP AND START PLAYING/i.test(document.body.innerText)"), flush=True)

    # ---- set_code: clipboard paste (Monaco handles one paste fast) ----
    page.evaluate("(t)=>navigator.clipboard.writeText(t)", code); time.sleep(0.5)
    page.click(".monaco-editor .view-lines"); time.sleep(0.4)
    page.keyboard.press("Control+a"); time.sleep(0.3)
    page.keyboard.press("Control+v"); time.sleep(2.5)
    page.keyboard.press("Control+Home"); time.sleep(0.5)
    vis=page.evaluate("(document.querySelector('.view-lines')||{}).innerText||''")
    print("code set ('0.8.3' visible):", "0.8.3" in vis, "| head:", repr(vis[:70]), flush=True)

    # ---- PLAY MY CODE ----
    page.get_by_text("PLAY MY CODE", exact=False).first.click()
    print("clicked PLAY MY CODE — computing...", flush=True)
    # wait for game to finish: poll for growth to stop
    prev=-1
    for i in range(20):
        time.sleep(3)
        body=page.evaluate("document.body.innerText")
        tf=sum(1 for l in body.splitlines() if l.startswith("@TF"))
        if i%2==0: print(f"  [{i*3}s] @TF lines={tf}", flush=True)
        if tf and tf==prev: break
        prev=tf

    # scrub the replay to the END so the console shows the FINAL turns' @TFSUM
    bb=page.evaluate("""()=>{const e=document.querySelector('.cg-player-sandbox')||document.querySelector('.cg-ide-player');
        if(!e)return null; const r=e.getBoundingClientRect(); return [Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)];}""")
    if bb: page.mouse.click(bb[0]+154, bb[1]+bb[3]-18)
    time.sleep(14)

    body=page.evaluate("document.body.innerText")
    tf=[l for l in body.splitlines() if l.startswith("@TF")]
    res=re.findall(r'(1ST|2ND|VICTORY|DEFEAT|Won|Lost|Score|Rank)[^\n]{0,45}', body, re.I)
    print("\n=== RESULT ===", flush=True)
    print("@TF lines:", len(tf), flush=True)
    print("result hints:", res[:10], flush=True)
    open("/home/tarstars/prj/troll_farm/cgauto/last_console.txt","w").write(body)
    page.screenshot(path="/home/tarstars/prj/troll_farm/cgauto/game.png")
    print("saved last_console.txt + game.png", flush=True)
    ctx.close()
