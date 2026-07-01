import time, hashlib
from playwright.sync_api import sync_playwright
PROFILE="/home/tarstars/prj/troll_farm/cgauto/profile"
URL="https://www.codingame.com/ide/puzzle/spring-challenge-2026-troll-farm"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 YaBrowser/25.8.0.0 Safari/537.36"
MAIN="/home/tarstars/prj/troll_farm/rust/src/main.rs"
code=open(MAIN).read()
cks=[]
for line in open("/home/tarstars/prj/troll_farm/cgauto/cg_session.txt"):
    line=line.strip()
    if line and not line.startswith('#') and '=' in line:
        n,v=line.split('=',1); n,v=n.strip(),v.strip()
        if v and 'PASTE' not in v:
            cks.append({"name":n,"value":v,"domain":"www.codingame.com","path":"/","secure":True,"httpOnly":True,"sameSite":"Lax"})

def winner_of(body):
    L=[l.strip() for l in body.splitlines()]
    for i in range(len(L)-5):
        if L[i]=='1' and L[i+1]=='ST' and L[i+3]=='2' and L[i+4]=='ND':
            return L[i+2]
    return None

def gamelog_sig(body):
    # hash the game-log region (the per-turn moves differ per map -> per-game fingerprint)
    i = body.find('Game Summary')
    if i < 0: i = body.find('Standard Error Stream')
    seg = body[i:i+400] if i >= 0 else ''
    return hashlib.md5(seg.encode()).hexdigest()[:8], seg.replace('\n',' ')[:70]

with sync_playwright() as pw:
    ctx=pw.chromium.launch_persistent_context(PROFILE, headless=False, no_viewport=True, user_agent=UA,
        args=["--no-proxy-server","--disable-blink-features=AutomationControlled","--window-size=1680,1000"])
    ctx.add_cookies(cks); ctx.grant_permissions(["clipboard-read","clipboard-write"], origin="https://www.codingame.com")
    page=ctx.pages[0] if ctx.pages else ctx.new_page()
    for a in range(3):
        try:
            page.goto(URL, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector(".monaco-editor", timeout=40000); break
        except Exception as e:
            print("load retry", e, flush=True); time.sleep(3)
    time.sleep(6)
    page.evaluate("(t)=>navigator.clipboard.writeText(t)", code); time.sleep(0.4)
    page.click(".monaco-editor .view-lines"); time.sleep(0.4)
    page.keyboard.press("Control+a"); time.sleep(0.3); page.keyboard.press("Control+v"); time.sleep(2.5)
    print("code set; probing 3 PLAY cycles\n", flush=True)
    for g in range(3):
        print(f"=== click PLAY  (game {g}) ===", flush=True)
        page.get_by_text("PLAY MY CODE", exact=False).first.click()
        for i in range(26):
            time.sleep(1.5)
            body=page.evaluate("document.body.innerText")
            w=winner_of(body)
            sig,seg=gamelog_sig(body)
            spin=page.evaluate("document.querySelectorAll('[class*=loading i],[class*=spinner i],[class*=computing i],[class*=running i],[class*=progress i]').length")
            print(f"  {i*1.5:4.0f}s len={len(body):5} spin={spin} w={str(w):7} sig={sig} | {seg}", flush=True)
        open(f"/home/tarstars/prj/troll_farm/cgauto/probe_g{g}.txt","w").write(body)
    ctx.close()
