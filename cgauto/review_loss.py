import time, sys, re
from playwright.sync_api import sync_playwright
PROFILE="/home/tarstars/prj/troll_farm/cgauto/profile"
URL="https://www.codingame.com/ide/puzzle/spring-challenge-2026-troll-farm"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 YaBrowser/25.8.0.0 Safari/537.36"
MAIN=sys.argv[1] if len(sys.argv)>1 else "/home/tarstars/prj/troll_farm/rust/src/main.rs"
MAXGAMES=int(sys.argv[2]) if len(sys.argv)>2 else 8
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
            return lines[i+2]
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
            page.wait_for_selector(".monaco-editor", timeout=75000); break
        except Exception as e:
            print(f"load attempt {attempt} failed ({str(e)[:60]}); retry 25s", flush=True)
            if attempt==4: raise
            time.sleep(25)
    time.sleep(6)
    assert not page.evaluate("/SIGN UP AND START PLAYING/i.test(document.body.innerText)"), "not logged in"

    page.evaluate("(t)=>navigator.clipboard.writeText(t)", code); time.sleep(0.4)
    page.click(".monaco-editor .view-lines"); time.sleep(0.4)
    page.keyboard.press("Control+a"); time.sleep(0.3)
    page.keyboard.press("Control+v"); time.sleep(2.5)
    print("code set; hunting for a LOSS (up to %d games)..." % MAXGAMES, flush=True)

    bb=page.evaluate("""()=>{const e=document.querySelector('.cg-player-sandbox')||document.querySelector('.cg-ide-player');
        if(!e)return null; const r=e.getBoundingClientRect(); return [Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)];}""")
    def has_log(b): return ('Game Summary' in b) or ('Standard Error Stream' in b)

    def play_one():
        page.get_by_text("PLAY MY CODE", exact=False).first.click()
        for _ in range(70):
            time.sleep(0.5)
            if not has_log(page.evaluate("document.body.innerText")): break
        for _ in range(80):
            time.sleep(0.5)
            b=page.evaluate("document.body.innerText")
            if has_log(b) and winner_of(b): break
        if bb: page.mouse.click(bb[0]+154, bb[1]+bb[3]-18)  # scrub to end
        time.sleep(13)
        return winner_of(page.evaluate("document.body.innerText"))

    parked=None
    for g in range(MAXGAMES):
        w=play_one()
        won = bool(w and 'tass' in w.lower())
        print(f"  game {g+1}: 1st={w}  -> {'WON' if won else 'LOSS/other'}", flush=True)
        page.screenshot(path=f"/home/tarstars/prj/troll_farm/cgauto/hunt_{g+1}.png")
        if not won:
            parked=g+1
            break

    # rewind to the start of whatever game is loaded so it's ready to watch
    if bb: page.mouse.click(bb[0]+27, bb[1]+bb[3]-18)
    time.sleep(1)
    page.screenshot(path="/home/tarstars/prj/troll_farm/cgauto/review.png")
    if parked:
        print(f"PARKED on a LOSS (game {parked}); browser left open. See hunt_{parked}.png for its final score.", flush=True)
    else:
        print("No loss in the sampled games (we won them all!); parked on the last game.", flush=True)
    time.sleep(3600)
    ctx.close()
