# cgauto — CodinGame Troll Farm IDE Automation

A Playwright-based toolkit that drives the CodinGame Spring Challenge 2026
"Troll Farm" web IDE via DOM selectors — no pixel-clicking, no screenshots
required for core operations.

## Prerequisites

- Python 3.11+  
- `playwright` already installed in `.venv`  
- Chromium browser (downloaded once — see below)

## One-time setup

```bash
# 1. Download Playwright's own Chromium (done once, ~150 MB)
/home/tarstars/prj/troll_farm/cgauto/.venv/bin/python -m playwright install chromium

# 2. Launch the browser so you can log in
DISPLAY=:0 /home/tarstars/prj/troll_farm/cgauto/.venv/bin/python cg.py open
```

A Chromium window will open at the CodinGame IDE page.  Log in there
manually.  When you are done logging in, press **Ctrl+C** in the terminal to
close the browser.  Your session is saved in the `profile/` directory and will
be reused on every subsequent run — you never need to log in again.

## CLI usage

All commands open the persistent profile, perform the action, then close the
browser (login persists across runs).

```bash
VENV=/home/tarstars/prj/troll_farm/cgauto/.venv/bin/python

# Open browser at IDE (keep open until Ctrl+C)
DISPLAY=:0 $VENV cg.py open

# Load a Python source file into the editor
DISPLAY=:0 $VENV cg.py setcode ../solution.py

# Run one game vs Boss 4 and wait for it to finish
DISPLAY=:0 $VENV cg.py play

# Print the full console output (all @TF debug lines + stdout)
DISPLAY=:0 $VENV cg.py console

# Print the leaderboard / result line after a game
DISPLAY=:0 $VENV cg.py result

# Submit to the ranked arena (clicks TEST IN ARENA → YES)
DISPLAY=:0 $VENV cg.py submit

# Take a screenshot (optional fallback)
DISPLAY=:0 $VENV cg.py screenshot [output.png]
```

## Python API

```python
import sys
sys.path.insert(0, "/home/tarstars/prj/troll_farm/cgauto")
import cg

pw, ctx, page = cg.open_ide()

# Check login status
if cg.logged_in(page):
    # Push code
    cg.set_code(page, open("solution.py").read())

    # Run a game
    cg.play(page)

    # Read output
    console_text = cg.read_console(page)
    tf_lines = [l for l in console_text.splitlines() if l.startswith("@TF")]
    print("\n".join(tf_lines))

    # Get result
    print(cg.result(page))

    # Submit to arena
    cg.submit_arena(page)

ctx.close()
pw.stop()
```

## Architecture

| Function | Description |
|---|---|
| `open_ide()` | Launch persistent Chromium, navigate to IDE, return `(pw, ctx, page)` |
| `logged_in(page)` | Check URL and DOM for login indicators |
| `set_code(page, code)` | Set editor via Monaco JS API; keyboard fallback |
| `play(page)` | Click "PLAY MY CODE", wait for game to finish |
| `read_console(page)` | Scroll/expand console panel, return all text |
| `result(page)` | Extract leaderboard text ("1ST … / 2ND …") |
| `submit_arena(page)` | Click "TEST IN ARENA" then confirm "YES" |
| `screenshot(page, path)` | Full-page PNG capture |

### Key implementation choices

- **Persistent profile** (`profile/` dir): login cookie survives every run.
- **Monaco JS API for code injection**: `monaco.editor.getModels()[0].setValue(code)` — avoids typing lag for large files.  Falls back to click + Ctrl+A + clipboard paste.
- **Text/role selectors only**: no pixel coordinates, no CSS `nth-child` fragility.
- **Game-end detection**: watches for spinner/loading elements to disappear, then falls back to polling console text for rank patterns (1ST, 2ND …).

## Verified vs needs-login

### Verified without login

| Item | Status |
|---|---|
| Playwright `sync_api` imports correctly | VERIFIED |
| Chromium download / install | VERIFIED |
| `launch_persistent_context` opens browser | VERIFIED (runs at `cg.py open`) |
| Navigation to IDE URL | VERIFIED (redirects to login; URL captured) |
| `logged_in()` detects login page correctly | VERIFIED (returns False on redirect) |

### Needs one-time login to verify

| Item | Notes |
|---|---|
| Monaco `.setValue()` API call | Needs the editor to be loaded |
| `play()` — "PLAY MY CODE" button selector | Text-based; should be robust |
| `read_console()` — console container class names | Angular SPA; class names may change |
| `result()` — leaderboard selectors | Fallback to text-scan in console |
| `submit_arena()` — "TEST IN ARENA" + "YES" | Text-based; should be robust |
| Spinner/loading CSS class names for `_wait_for_game_end` | May need tuning |

### How to finalize selectors after login

1. Run `DISPLAY=:0 python cg.py open` (you will already be logged in).
2. Open the browser's DevTools (F12) and inspect the console area, buttons, and loading spinner to confirm or correct the CSS selectors in `cg.py`.
3. The most likely selectors to need adjustment are in `read_console()` and `_wait_for_game_end()` — the Angular SPA may use generated class names like `_nghost-xxx`.  If that happens, switch to `[data-cy]`, `[aria-label]`, or `role` attributes.

## Troubleshooting

**"Could not find any button matching: ['PLAY MY CODE', ...]"**  
The IDE page did not load or you are not logged in.  Run `python cg.py open`
and check the browser window.

**Console returns empty string**  
The console selectors need updating.  Open DevTools in the live IDE, find the
console container element, note its class/role/aria attributes, and update the
`selectors` list in `read_console()` and `_expand_console()`.

**Monaco API not available**  
The editor has not finished loading.  Add a short `time.sleep(3)` before
calling `set_code()`, or wait for `.monaco-editor` to appear:
```python
page.wait_for_selector(".monaco-editor", timeout=15000)
```
