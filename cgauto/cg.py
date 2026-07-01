#!/usr/bin/env python3
"""
cg.py — CodinGame Troll Farm IDE automation toolkit.

Uses Playwright persistent context so login is preserved across runs.

CLI:
    python cg.py open
    python cg.py setcode <file>
    python cg.py play
    python cg.py console
    python cg.py result
    python cg.py submit
    python cg.py screenshot [path]
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, BrowserContext, TimeoutError as PlaywrightTimeoutError

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROFILE_DIR = str(Path(__file__).parent / "profile")
IDE_URL = "https://www.codingame.com/ide/puzzle/spring-challenge-2026-troll-farm"
LOGIN_URL = "https://www.codingame.com/start"

# Timeouts (ms)
NAV_TIMEOUT = 30_000
ACTION_TIMEOUT = 15_000
GAME_TIMEOUT = 120_000   # 2 min for a full game to finish
LONG_WAIT = 5_000


# ---------------------------------------------------------------------------
# Browser context helpers
# ---------------------------------------------------------------------------

def _get_playwright_and_context(headless: bool = False):
    """Return (playwright, context) using a persistent profile so login persists."""
    pw = sync_playwright().start()
    context = pw.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=headless,
        viewport={"width": 1600, "height": 900},
        args=["--disable-blink-features=AutomationControlled"],
    )
    return pw, context


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def open_ide(headless: bool = False):
    """
    Launch the persistent Chromium profile and navigate to the IDE.

    Returns (playwright, context, page).  Caller is responsible for cleanup.
    If the page looks like a login page, a message is printed telling the user
    to log in and the browser is left open.
    """
    pw, context = _get_playwright_and_context(headless=headless)

    # Re-use an existing page if one exists, otherwise open a new one.
    pages = context.pages
    page = pages[0] if pages else context.new_page()

    page.goto(IDE_URL, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)

    # Give the Angular SPA a moment to bootstrap.
    time.sleep(2)

    if not logged_in(page):
        print(
            "\n*** NOT LOGGED IN ***\n"
            "A Chromium window has opened.  Please log in to CodinGame in that window.\n"
            "After you log in the session will be saved in the 'profile' directory and\n"
            "you will not need to log in again.\n"
            "Press Ctrl+C here when you are done to close the browser.\n"
        )

    return pw, context, page


def logged_in(page: Page) -> bool:
    """
    Return True if the current page is the authenticated IDE (editor loaded).

    Key insight from live DOM inspection:
      - CodinGame shows the IDE shell (Monaco DOM element, "PLAY MY CODE" span)
        even when NOT logged in — the Angular SPA pre-renders the layout.
      - The ONLY reliable indicator of a live authenticated session is the
        global `monaco` JS object, which is only defined once the editor
        finishes initialising (which requires auth).
      - Secondary check: the page HTML contains "login" in its content even on
        the IDE URL when not authenticated (CodinGame embeds a login modal).

    Strategy (in order):
      1. URL-based redirect check.
      2. monaco JS global defined — most reliable.
      3. Page HTML does NOT contain login-related content.
    """
    url = page.url
    # If we were redirected to a login / start page we're not logged in.
    if "login" in url or "start" in url or url.rstrip("/") == "https://www.codingame.com":
        return False

    # Primary check: monaco global only exists after the editor loads (auth required).
    try:
        has_monaco = page.evaluate("typeof monaco !== 'undefined' && monaco !== null")
        if has_monaco:
            return True
    except Exception:
        pass

    # If we reach here, monaco isn't loaded yet — not authenticated.
    return False


def set_code(page: Page, code: str) -> None:
    """
    Replace the contents of the Monaco editor with *code*.

    Primary method: Monaco JS API (most reliable).
    Fallback: click the editor, Ctrl+A, paste via clipboard.
    """
    # --- Primary: Monaco API ---
    try:
        result = page.evaluate("""
            (code) => {
                const models = monaco.editor.getModels();
                if (!models || models.length === 0) {
                    return {ok: false, reason: 'no models'};
                }
                // Prefer the first model that isn't a diff-editor secondary.
                let target = models[0];
                if (models.length > 1) {
                    // Pick the largest model, which is usually the user's code.
                    target = models.reduce((a, b) =>
                        a.getValue().length >= b.getValue().length ? a : b
                    );
                }
                target.setValue(code);
                return {ok: true, modelCount: models.length};
            }
        """, code)
        if result and result.get("ok"):
            print(f"[set_code] Monaco API: set {len(code)} bytes "
                  f"(model count: {result.get('modelCount')})")
            return
        print(f"[set_code] Monaco API returned: {result} — falling back to keyboard")
    except Exception as exc:
        print(f"[set_code] Monaco API failed ({exc}) — falling back to keyboard")

    # --- Fallback: click editor, select-all, type ---
    editor = page.locator(".monaco-editor").first
    editor.click()
    page.keyboard.press("Control+a")
    time.sleep(0.1)
    # Paste via clipboard for speed (avoids key-by-key typing of large files).
    page.evaluate("(text) => navigator.clipboard.writeText(text)", code)
    page.keyboard.press("Control+v")
    time.sleep(0.3)
    print(f"[set_code] Keyboard fallback: pasted {len(code)} bytes")


def play(page: Page) -> None:
    """
    Click "PLAY MY CODE" and wait until the game finishes.

    Completion is detected by:
      1. The loading/spinner element disappearing, OR
      2. The result/leaderboard text appearing in the console.
    """
    btn = _find_button(page, ["PLAY MY CODE", "Play my code", "play my code"])
    btn.click()
    print("[play] Clicked 'PLAY MY CODE' — waiting for game to finish …")

    # Wait for game completion.  Try a few heuristics in order.
    _wait_for_game_end(page)
    print("[play] Game finished.")


def read_console(page: Page) -> str:
    """
    Return the full text of the console output area.

    Looks for the Standard Error Stream (debug lines starting with @TF) and
    the Standard Output Stream.  Tries to scroll/expand the panel first.
    """
    _expand_console(page)

    texts = []

    # Try the known console container selectors (inspect these in the live IDE
    # and update if the class names change).
    selectors = [
        ".console-container",
        ".ide-console",
        "[class*='console']",
        ".stderr",
        ".stdout",
        "[class*='output']",
        ".game-log",
    ]
    for sel in selectors:
        try:
            elements = page.locator(sel).all()
            for el in elements:
                t = el.inner_text(timeout=2_000)
                if t.strip():
                    texts.append(t.strip())
        except Exception:
            pass

    if texts:
        combined = "\n".join(texts)
        print(f"[read_console] Captured {len(combined)} chars from console")
        return combined

    # Last-resort fallback: grab visible text from the bottom panel.
    print("[read_console] WARNING: no console selectors matched — "
          "selectors need verification against the live IDE DOM.")
    return ""


def result(page: Page) -> str:
    """
    Return a string like "1ST Boss 4 / 2ND tass" from the post-game leaderboard.
    """
    _expand_console(page)

    # Known result area selectors.
    selectors = [
        ".leaderboard",
        "[class*='leaderboard']",
        "[class*='result']",
        "[class*='rank']",
        ".game-result",
    ]
    for sel in selectors:
        try:
            el = page.locator(sel).first
            t = el.inner_text(timeout=2_000)
            if t.strip():
                print(f"[result] Found via '{sel}'")
                return t.strip()
        except Exception:
            pass

    # Fallback: search console text for the leaderboard pattern.
    console_text = read_console(page)
    for line in console_text.splitlines():
        if "ST " in line or "ND " in line or "RD " in line or "TH " in line:
            return line.strip()

    print("[result] WARNING: could not find result leaderboard — "
          "selectors need verification against the live IDE DOM.")
    return ""


def submit_arena(page: Page) -> None:
    """
    Click "TEST IN ARENA", then confirm by clicking "YES" in the modal.
    """
    btn = _find_button(page, ["TEST IN ARENA", "Test in arena", "test in arena"])
    btn.click()
    print("[submit_arena] Clicked 'TEST IN ARENA' — waiting for confirm modal …")

    # Wait for the Submit modal.
    try:
        page.get_by_role("heading", name="Submit").wait_for(timeout=ACTION_TIMEOUT)
    except PlaywrightTimeoutError:
        # Try alternate modal title.
        try:
            page.get_by_text("Submit", exact=True).wait_for(timeout=3_000)
        except PlaywrightTimeoutError:
            print("[submit_arena] WARNING: could not find 'Submit' modal — "
                  "looking for YES button anyway")

    # Click YES.
    yes_btn = _find_button(page, ["YES", "Yes"])
    yes_btn.click()
    print("[submit_arena] Clicked 'YES' — submission started.")

    # Brief pause to let the arena submission register.
    time.sleep(2)


def screenshot(page: Page, path: str = "screenshot.png") -> str:
    """Take a full-page screenshot and save to *path*. Returns the path."""
    page.screenshot(path=path, full_page=True)
    print(f"[screenshot] Saved to {path}")
    return path


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _find_button(page: Page, candidates: list[str]):
    """
    Find a button / clickable element by trying multiple text candidates.

    Returns the first match.  Raises RuntimeError if none found.
    """
    for text in candidates:
        # 1. get_by_role button
        try:
            el = page.get_by_role("button", name=text, exact=False).first
            el.wait_for(state="visible", timeout=ACTION_TIMEOUT)
            return el
        except PlaywrightTimeoutError:
            pass

        # 2. get_by_text (covers non-<button> clickable elements)
        try:
            el = page.get_by_text(text, exact=False).first
            el.wait_for(state="visible", timeout=ACTION_TIMEOUT)
            return el
        except PlaywrightTimeoutError:
            pass

    raise RuntimeError(
        f"[_find_button] Could not find any button matching: {candidates}\n"
        "This usually means the IDE page is not loaded or the selector needs updating."
    )


def _wait_for_game_end(page: Page) -> None:
    """
    Block until the running game appears to have finished.

    Uses several heuristics with increasing timeout.
    """
    deadline = time.time() + GAME_TIMEOUT / 1000

    # Heuristic 1: wait for a loading/spinner to appear then disappear.
    spinner_selectors = [
        "[class*='loading']",
        "[class*='spinner']",
        "[class*='running']",
        ".cg-loader",
    ]
    for sel in spinner_selectors:
        try:
            # Check if such an element even exists.
            el = page.locator(sel).first
            el.wait_for(state="visible", timeout=5_000)
            # It appeared — now wait for it to go away.
            remaining_ms = int((deadline - time.time()) * 1000)
            el.wait_for(state="hidden", timeout=max(remaining_ms, 5_000))
            print(f"[_wait_for_game_end] Spinner '{sel}' gone — game done")
            return
        except PlaywrightTimeoutError:
            continue

    # Heuristic 2: poll for leaderboard / result text in console.
    result_patterns = ["ST ", "ND ", "RD ", "TH ", "1ST", "2ND", "Win", "Lose"]
    while time.time() < deadline:
        try:
            console_text = read_console(page)
            for pat in result_patterns:
                if pat in console_text:
                    print(f"[_wait_for_game_end] Result pattern '{pat}' found in console")
                    return
        except Exception:
            pass
        time.sleep(1)

    print("[_wait_for_game_end] WARNING: timed out waiting for game end — "
          "proceeding anyway.")


def _expand_console(page: Page) -> None:
    """
    Try to expand / scroll the console panel so all output is visible.
    """
    expand_candidates = [
        "[class*='console-expand']",
        "[class*='expand-console']",
        "[aria-label*='expand']",
        "[class*='panel-toggle']",
    ]
    for sel in expand_candidates:
        try:
            btn = page.locator(sel).first
            btn.wait_for(state="visible", timeout=1_500)
            btn.click()
            time.sleep(0.3)
            return
        except PlaywrightTimeoutError:
            continue

    # Scroll any scrollable console container to the bottom.
    scroll_selectors = [
        ".console-container",
        ".ide-console",
        "[class*='console']",
        "[class*='output']",
    ]
    for sel in scroll_selectors:
        try:
            el = page.locator(sel).first
            el.evaluate("el => el.scrollTop = el.scrollHeight")
        except Exception:
            pass


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _cli():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0].lower()

    if cmd == "open":
        pw, ctx, page = open_ide()
        print(f"[cli] Browser open at: {page.url}")
        print("[cli] Press Ctrl+C to close …")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        ctx.close()
        pw.stop()

    elif cmd == "setcode":
        if len(args) < 2:
            print("Usage: python cg.py setcode <file>")
            sys.exit(1)
        code = Path(args[1]).read_text()
        pw, ctx, page = open_ide()
        try:
            set_code(page, code)
            print("[cli] Code set. Press Ctrl+C to close …")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        finally:
            ctx.close()
            pw.stop()

    elif cmd == "play":
        pw, ctx, page = open_ide()
        try:
            play(page)
        finally:
            ctx.close()
            pw.stop()

    elif cmd == "console":
        pw, ctx, page = open_ide()
        try:
            text = read_console(page)
            print(text)
        finally:
            ctx.close()
            pw.stop()

    elif cmd == "result":
        pw, ctx, page = open_ide()
        try:
            print(result(page))
        finally:
            ctx.close()
            pw.stop()

    elif cmd == "submit":
        pw, ctx, page = open_ide()
        try:
            submit_arena(page)
        finally:
            ctx.close()
            pw.stop()

    elif cmd == "screenshot":
        path = args[1] if len(args) > 1 else "screenshot.png"
        pw, ctx, page = open_ide()
        try:
            screenshot(page, path)
        finally:
            ctx.close()
            pw.stop()

    else:
        print(f"Unknown command: {cmd}")
        print("Commands: open | setcode <file> | play | console | result | submit | screenshot [path]")
        sys.exit(1)


if __name__ == "__main__":
    _cli()
