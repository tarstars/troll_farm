import time, sys, re
from playwright.sync_api import sync_playwright
PROFILE="/home/tarstars/prj/troll_farm/cgauto/profile"
URL="https://www.codingame.com/ide/puzzle/spring-challenge-2026-troll-farm"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 YaBrowser/25.8.0.0 Safari/537.36"
MAIN=sys.argv[2] if len(sys.argv)>2 else "/home/tarstars/prj/troll_farm/rust/src/main.rs"
N=int(sys.argv[1]) if len(sys.argv)>1 else 10
code=open(MAIN).read()

cks=[]
for line in open("/home/tarstars/prj/troll_farm/cgauto/cg_session.txt"):
    line=line.strip()
    if line and not line.startswith('#') and '=' in line:
        n,v=line.split('=',1); n,v=n.strip(),v.strip()
        if v and 'PASTE' not in v:
            cks.append({"name":n,"value":v,"domain":"www.codingame.com","path":"/","secure":True,"httpOnly":True,"sameSite":"Lax"})

def winner_of(body):
    lines=[l.strip() for l in body.splitlines()]
    for i in range(len(lines)-5):
        if lines[i]=='1' and lines[i+1]=='ST' and lines[i+3]=='2' and lines[i+4]=='ND':
            return lines[i+2]   # the 1st-place name
    return None

with sync_playwright() as pw:
    ctx=pw.chromium.launch_persistent_context(PROFILE, headless=False, no_viewport=True, user_agent=UA,
        args=["--no-proxy-server","--disable-blink-features=AutomationControlled","--window-size=1680,1000"])
    ctx.add_cookies(cks)
    ctx.grant_permissions(["clipboard-read","clipboard-write"], origin="https://www.codingame.com")
    page=ctx.pages[0] if ctx.pages else ctx.new_page()
    for attempt in range(5):
        try:
            page.goto(URL, wait_until="domcontentloaded", timeout=90000)
            page.wait_for_selector(".monaco-editor", timeout=75000)
            break
        except Exception as e:
            print(f"load attempt {attempt} failed ({str(e)[:70]}); cooling down 25s", flush=True)
            if attempt == 4: raise
            time.sleep(25)
    time.sleep(6)
    assert not page.evaluate("/SIGN UP AND START PLAYING/i.test(document.body.innerText)"), "not logged in"
    # set code once
    page.evaluate("(t)=>navigator.clipboard.writeText(t)", code); time.sleep(0.4)
    page.click(".monaco-editor .view-lines"); time.sleep(0.4)
    page.keyboard.press("Control+a"); time.sleep(0.3)
    page.keyboard.press("Control+v"); time.sleep(2.5)
    print(f"code set from {MAIN}; running {N} games vs Boss 4...", flush=True)

    # The "1ST/2ND" panel is a per-FRAME LIVE standing and the replay plays slowly, so reading
    # it mid-replay gives the wrong (early/mid) result. To get the real outcome we read the
    # FINAL frame: click PLAY -> wait for the new replay to load -> SCRUB to the end via the
    # viewer's skip-to-end button (a coordinate click; the viewer is a cross-origin iframe) ->
    # confirm the turn counter reads N/N (game ends ~turn 293, not always 300) -> read standing.
    def has_log(b): return ('Game Summary' in b) or ('Standard Error Stream' in b)
    def at_end(b):
        return any(m.group(1)==m.group(2) and 50<int(m.group(2))<320
                   for m in re.finditer(r'(\d+)\s*/\s*(\d+)', b))
    bb=page.evaluate("""()=>{const e=document.querySelector('.cg-player-sandbox')||document.querySelector('.cg-ide-player');
        if(!e)return null; const r=e.getBoundingClientRect(); return [Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)];}""")
    # Fallback to the known-good viewer rect if the element renders degenerate (height 0),
    # otherwise the skip-to-end click lands at the wrong y and every read is mid-replay.
    if (not bb) or bb[3] < 100 or bb[2] < 100:
        bb=[101,43,752,470]
        print("viewer bbox degenerate -> fallback", bb, flush=True)
    else:
        print("viewer bbox:", bb, flush=True)
    def play_one():
        page.get_by_text("PLAY MY CODE", exact=False).first.click()
        for _ in range(70):                       # wait for the log to CLEAR (computing)
            time.sleep(0.5)
            if not has_log(page.evaluate("document.body.innerText")): break
        for _ in range(80):                       # wait for the NEW replay to load
            time.sleep(0.5)
            b=page.evaluate("document.body.innerText")
            if has_log(b) and winner_of(b): break
        if bb: page.mouse.click(bb[0]+154, bb[1]+bb[3]-18)   # skip-to-end (single click only)
        confirmed=False
        for _ in range(26):                        # let it settle at the final frame
            time.sleep(0.5)
            if at_end(page.evaluate("document.body.innerText")): confirmed=True; break
        return winner_of(page.evaluate("document.body.innerText")), confirmed
    wins=losses=0; res=[]; conf=0
    for g in range(N):
        w, ok = play_one()
        res.append(w); conf += 1 if ok else 0
        if w and 'tass' in w.lower(): wins+=1; tag="WON "
        elif w: losses+=1; tag="lost"
        else: tag="????"
        print(f"  game {g+1}/{N}: {tag}  (1st={w}) {'[final]' if ok else '[UNCONFIRMED]'}", flush=True)
    tot=wins+losses
    print(f"\n=== vs Boss 4: {wins}W / {losses}L = {100*wins//max(1,tot)}% over {tot} games  ({conf}/{N} confirmed at final frame) ===", flush=True)
    page.screenshot(path="/home/tarstars/prj/troll_farm/cgauto/lastgame.png")   # visual check: is the viewer at N/N?
    ctx.close()
