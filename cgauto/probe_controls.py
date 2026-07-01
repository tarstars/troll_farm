import time
from playwright.sync_api import sync_playwright
PROFILE="/home/tarstars/prj/troll_farm/cgauto/profile"
URL="https://www.codingame.com/ide/puzzle/spring-challenge-2026-troll-farm"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 YaBrowser/25.8.0.0 Safari/537.36"
code=open("/home/tarstars/prj/troll_farm/rust/src/main.rs").read()
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
        if L[i]=='1' and L[i+1]=='ST' and L[i+3]=='2' and L[i+4]=='ND': return L[i+2]
    return None
def has_log(b): return ('Game Summary' in b) or ('Standard Error Stream' in b)
with sync_playwright() as pw:
    ctx=pw.chromium.launch_persistent_context(PROFILE, headless=False, no_viewport=True, user_agent=UA,
        args=["--no-proxy-server","--disable-blink-features=AutomationControlled","--window-size=1680,1000"])
    ctx.add_cookies(cks); ctx.grant_permissions(["clipboard-read","clipboard-write"], origin="https://www.codingame.com")
    page=ctx.pages[0] if ctx.pages else ctx.new_page()
    for a in range(3):
        try: page.goto(URL, wait_until="domcontentloaded", timeout=60000); page.wait_for_selector(".monaco-editor", timeout=40000); break
        except Exception as e: print("load retry", e, flush=True); time.sleep(3)
    time.sleep(6)
    page.evaluate("(t)=>navigator.clipboard.writeText(t)", code); time.sleep(0.4)
    page.click(".monaco-editor .view-lines"); time.sleep(0.4)
    page.keyboard.press("Control+a"); time.sleep(0.3); page.keyboard.press("Control+v"); time.sleep(2.5)
    page.get_by_text("PLAY MY CODE", exact=False).first.click()
    for _ in range(70):
        time.sleep(0.5)
        if not has_log(page.evaluate("document.body.innerText")): break
    for _ in range(70):
        time.sleep(0.5); b=page.evaluate("document.body.innerText")
        if has_log(b) and winner_of(b): break
    print("EARLY winner:", winner_of(page.evaluate("document.body.innerText")), flush=True)
    # dump playback controls + turn counter
    ctrls=page.evaluate(r"""() => {
      const out=[];
      document.querySelectorAll('button,[role=button],svg,[class*=control i],[class*=play i],[class*=timeline i],[class*=progress i],[class*=slider i],[aria-label],[title]').forEach(e=>{
        const t=(e.innerText||'').trim().slice(0,16);
        const al=e.getAttribute&&e.getAttribute('aria-label')||'';
        const ti=e.getAttribute&&e.getAttribute('title')||'';
        const cl=(e.className&&e.className.toString?e.className.toString():'').slice(0,45);
        if (al||ti||/play|paus|end|last|skip|forward|next|speed|step|frame|slider|timeline|progress|track/i.test(cl))
          out.push(`<${e.tagName}> t='${t}' al='${al}' ti='${ti}' cl='${cl}'`);
      });
      return [...new Set(out)].slice(0,50).join('\n');
    }""")
    print("CONTROLS:\n"+ctrls, flush=True)
    # any "/300" turn counter text?
    import re
    body=page.evaluate("document.body.innerText")
    print("turn-counter-ish:", re.findall(r'\b\d{1,3}\s*/\s*300\b|\b0\d\d\b', body)[:6], flush=True)
    page.screenshot(path="/home/tarstars/prj/troll_farm/cgauto/controls.png")
    print("screenshot -> controls.png", flush=True)
    ctx.close()
