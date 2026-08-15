#!/usr/bin/env python3
"""D2 Phase 1 — troll-moves viewer generator.

Authorized by `local_claude_1` policy `20260815T070500Z` (owner ruling: form approved,
display-only, live sessions). Claimed at `c5f1add3`. Phase 2 (packet overlay, blind mode) is
gated on P-1 and a separate go and is NOT built here.

**What this is.** One self-contained HTML page per frozen situation, plus an index. No server,
no external asset, keyboard step-through. The owner drives it in a live session while
`local_claude_1` records rulings separately; the page captures nothing.

**Generated through the verifying loader.** Pages are built from `load_library(verify=True)`,
which fails closed on any digest, file-set, count, schema or enumeration mismatch. If the
library is not intact, no page is produced at all.

## The three honesty rules (blocking, from `codex_1` finding V1/V2)

A command is an ORDER, not a landing. `engine.rs::next_cell` returns the target only when
`d <= speed`, so a distant MOVE lands somewhere in between, and simultaneous resolution against
an opponent whose commands are NOT in this library can move it again. Therefore:

1. **verbatim command line and its parsed target are GROUND TRUTH** — rendered solid;
2. **any position we infer is INFERENCE** — rendered hollow/dashed, and never called realized;
3. **every side panel is stamped `at entry`** and never advanced — inventories, plants and the
   opponent are frozen snapshots, and own commands cannot honestly advance them.

**This generator does not re-implement the referee.** It computes no predicted landing: doing so
would mean a BFS/speed mirror of `engine.rs`, and a mirror that disagrees with the authority is
worse than no mirror. The single inference it draws is *"the unit is at the target of the most
recent MOVE"*, which is stated on every page as an assumption that the referee does not
guarantee.

## Guards

`--self-test` demonstrates every check REJECTING before any of them is trusted:
unknown map character, situation-count drift, rendered-turn-count disagreement, and a derived
position emitted without its inference marking. A check never seen failing is not a check.

Run:
    python3 claude_1/viewer/build_viewer.py --self-test
    python3 claude_1/viewer/build_viewer.py --out claude_1/viewer/out
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
LIB_PARENT = os.path.join(REPO, "claude_1", "banana-restoration-r2")
LIB_DIR = os.path.join(LIB_PARENT, "oscillation-library-98628e98", "library")

sys.path.insert(0, LIB_PARENT)

#: The library's full alphabet, measured across all 34 situations 2026-08-15 — not assumed.
#: An unknown character must break the page loudly rather than default to wall, because a
#: plausible-but-wrong board is worse in a live session than no board.
MAP_LEGEND = {
    "#": ("wall", "impassable"),
    ".": ("floor", "walkable"),
    "0": ("shack-own", "our shack"),
    "1": ("shack-opp", "opponent shack"),
    "+": ("iron", "iron"),
    "~": ("water", "water"),
}

CARRY_SLOTS = ["PLUM", "APPLE", "LEMON", "BANANA", "ORANGE", "WOOD"]

MOVE_RE = re.compile(r"\AMOVE\s+(\d+)\s+(\d+)\s+(\d+)\Z")


class BuildError(Exception):
    """Any check failing aborts the whole build. There is no partial generation."""


# --------------------------------------------------------------------------------------
# checks — each one is demonstrated failing in --self-test


def check_map_alphabet(rows, sid):
    unknown = sorted({c for r in rows for c in r} - set(MAP_LEGEND))
    if unknown:
        raise BuildError(
            f"{sid}: map uses character(s) {unknown!r} absent from the legend. Refusing to "
            f"render: an unrecognised cell drawn as a guess is a wrong board.")


def check_situation_count(situations, expected=34):
    if len(situations) != expected:
        raise BuildError(
            f"library holds {len(situations)} situations, expected {expected}. The subject-correct "
            f"library is frozen; a change in count means the wrong tree or a mutated one.")


def check_turn_coverage(sit):
    w = sit["window"]
    turns = [c["turn"] for c in w["commands"]]
    if len(turns) != w["length_turns"]:
        raise BuildError(
            f"{sit['id']}: {len(turns)} command rows against length_turns={w['length_turns']}. "
            f"The page would silently show fewer turns than the episode has.")
    expected = list(range(w["turn_start"], w["turn_end"] + 1))
    if turns != expected:
        raise BuildError(
            f"{sit['id']}: command turns are not the contiguous range "
            f"{w['turn_start']}..{w['turn_end']}; stepping would skip a hole.")


#: Every inferred position must carry BOTH the data-role and the visual class. The check is
#: structural rather than visual: it cannot see a stylesheet, and it says so.
DERIVED_ROLE = 'data-role="derived-position"'
DERIVED_CLASS = "derived"


CLASS_ATTR_RE = re.compile(r'class="([^"]*)"')


def check_inference_marked(page_html, sid):
    # The class is read out of the `class` attribute, NOT matched against the whole tag.
    # Matching the tag passed for the wrong reason: `data-role="derived-position"` itself
    # contains the substring "derived", so an unmarked element satisfied it. The negative
    # control caught that; without the control the check would have shipped inert.
    for m in re.finditer(r"<[^>]*" + re.escape(DERIVED_ROLE) + r"[^>]*>", page_html):
        tag = m.group(0)
        cm = CLASS_ATTR_RE.search(tag)
        classes = cm.group(1).split() if cm else []
        if DERIVED_CLASS not in classes:
            raise BuildError(
                f"{sid}: an inferred position is emitted without its `{DERIVED_CLASS}` marking: "
                f"{tag[:120]}. Inference rendered as fact is the V1 defect.")
    if DERIVED_ROLE in page_html and "legend-derived" not in page_html:
        raise BuildError(
            f"{sid}: page draws inferred positions but carries no legend explaining them.")


def _rule(css, selector):
    m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", css)
    return m.group(1) if m else ""


def check_visual_distinction(css):
    """Ground-truth marks and inferred marks must not be styled alike.

    This is the closest a generator can get to the pixel rule without a browser. It proves the
    two classes differ in fill and that only the inferred one is dashed. **It does not prove the
    page LOOKS right** — see the note printed by `--self-test`.
    """
    own, opp = _rule(css, ".own"), _rule(css, ".opp")
    if not own or not opp:
        raise BuildError("stylesheet is missing a rule for .own or .opp")
    if "stroke-dasharray" not in own:
        raise BuildError(
            "inferred own positions are not dashed: `.own` has no stroke-dasharray, so "
            "inference would render as solid — indistinguishable from recorded fact.")
    if "stroke-dasharray" in opp:
        raise BuildError(
            "the opponent snapshot is dashed; dashing is reserved for inference, and the "
            "opponent's entry position is recorded fact.")
    own_fill = re.search(r"fill:\s*([^;]+)", own)
    opp_fill = re.search(r"fill:\s*([^;]+)", opp)
    if not own_fill or own_fill.group(1).strip() != "none":
        raise BuildError("inferred own positions must be hollow (`fill:none`)")
    if not opp_fill or opp_fill.group(1).strip() == "none":
        raise BuildError(
            "the opponent mark is hollow, the same treatment as inference. Ground truth and "
            "assumption would look alike — the exact confusion the honesty rules forbid.")


# --------------------------------------------------------------------------------------
# rendering


def parse_commands(line):
    """Split a wire line into per-unit commands. Verbatim text is preserved untouched."""
    return [seg.strip() for seg in line.split(";") if seg.strip()]


def move_target(seg):
    m = MOVE_RE.match(seg)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None


def derived_positions(sit):
    """The ONE inference this viewer draws, per turn: 'at the target of the most recent MOVE'.

    Seeded from the entry position, which IS ground truth. Every later value assumes the order
    completed — an assumption `engine.rs` does not guarantee, stated on the page.
    """
    w = sit["window"]
    pos = {}
    for u in sit["world_state_at_entry"]["units"]:
        pos[u[0]] = (u[2], u[3])
    own_ids = {u[0] for u in sit["world_state_at_entry"]["units"] if u[1] == 0}
    out = []
    for cmd in w["commands"]:
        for seg in parse_commands(cmd["line"]):
            t = move_target(seg)
            if t and t[0] in own_ids:
                pos[t[0]] = (t[1], t[2])
        out.append({"turn": cmd["turn"], "line": cmd["line"],
                    "segments": parse_commands(cmd["line"]),
                    "own": {str(k): v for k, v in pos.items() if k in own_ids}})
    return out


def board_svg(sit, turn_index, frames):
    rows = sit["static_map_rows"]
    h, w = len(rows), len(rows[0])
    cell = 34
    parts = [f'<svg viewBox="0 0 {w*cell} {h*cell}" class="board" '
             f'role="img" aria-label="situation board">']
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            klass, _ = MAP_LEGEND[ch]
            parts.append(f'<rect class="c {klass}" x="{x*cell}" y="{y*cell}" '
                         f'width="{cell}" height="{cell}"/>')
    # the paced cells of the episode, drawn as the standing highlight
    for (cx, cy) in sit["window"]["cells"]:
        parts.append(f'<rect class="cycle" x="{cx*cell}" y="{cy*cell}" '
                     f'width="{cell}" height="{cell}"/>')
    # plants and opponent: FROZEN AT ENTRY, drawn with the entry marker
    for p in sit["world_state_at_entry"]["plants"]:
        kind, px, py = p[0], p[1], p[2]
        parts.append(f'<text class="plant entry" x="{px*cell+cell/2}" y="{py*cell+cell*0.68}" '
                     f'text-anchor="middle">{html.escape(kind[0])}</text>')
    for u in sit["world_state_at_entry"]["units"]:
        if u[1] != 0:
            parts.append(f'<circle class="opp entry" cx="{u[2]*cell+cell/2}" '
                         f'cy="{u[3]*cell+cell/2}" r="{cell*0.30}"/>')
    # own units: INFERRED position — hollow + dashed, marked structurally
    for f_i, frame in enumerate(frames):
        for uid, (ux, uy) in frame["own"].items():
            parts.append(
                f'<circle {DERIVED_ROLE} class="own {DERIVED_CLASS} f{f_i}" '
                f'cx="{ux*cell+cell/2}" cy="{uy*cell+cell/2}" r="{cell*0.32}"/>')
            parts.append(
                f'<text {DERIVED_ROLE} class="ownid {DERIVED_CLASS} f{f_i}" '
                f'x="{ux*cell+cell/2}" y="{uy*cell+cell*0.62}" '
                f'text-anchor="middle">{html.escape(uid)}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


CSS = """
:root{--bg:#fbfaf7;--fg:#1d1b17;--line:#c9c3b6;--wall:#3a352d;--floor:#f2eee5;
--own:#1a5fb4;--opp:#b4401a;--cycle:#ffd98a;--iron:#8d8577;--water:#8fb8cf;--muted:#6c665c}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#16150f;--fg:#efe9dc;
--line:#4a453b;--wall:#0c0b08;--floor:#26241d;--cycle:#6b5320;--muted:#a09a8e}}
*{box-sizing:border-box}
body{margin:0;padding:1.2rem;background:var(--bg);color:var(--fg);
font:15px/1.5 ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
h1{font-size:1.25rem;margin:0 0 .2rem}
.sub{color:var(--muted);margin:0 0 1rem;font-size:.9rem}
.wrap{display:flex;gap:1.4rem;flex-wrap:wrap;align-items:flex-start}
.board{width:min(560px,94vw);height:auto;border:1px solid var(--line);background:var(--floor)}
.c{stroke:var(--line);stroke-width:.5}
.wall{fill:var(--wall)}.floor{fill:var(--floor)}
.shack-own{fill:#cfe0f5}.shack-opp{fill:#f5d8cf}.iron{fill:var(--iron)}.water{fill:var(--water)}
.cycle{fill:var(--cycle);opacity:.55}
.plant{font:600 13px ui-monospace,monospace;fill:#2f6b34}
/* Ground truth is SOLID. Inference is HOLLOW + DASHED. The two must not look alike:
   the opponent snapshot is recorded fact, the own position is our assumption. An earlier
   draft drew both hollow, which is precisely the confusion these rules exist to prevent. */
.opp{fill:var(--opp);stroke:none}
.own{fill:none;stroke:var(--own);stroke-width:2.5;stroke-dasharray:4 3}
.ownid{font:600 12px ui-monospace,monospace;fill:var(--own)}
.own,.ownid,.opp,.plant{pointer-events:none}
[data-role="derived-position"]{display:none}
[data-role="derived-position"].show{display:inline}
.panel{min-width:280px;max-width:460px;flex:1}
.panel h2{font-size:.82rem;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);
margin:1rem 0 .3rem;border-bottom:1px solid var(--line);padding-bottom:.2rem}
.cmd{font:13px/1.5 ui-monospace,monospace;background:#00000010;padding:.5rem .6rem;
border-left:3px solid var(--own);overflow-x:auto;white-space:pre}
table{border-collapse:collapse;width:100%;font-size:.86rem}
td,th{border-bottom:1px solid var(--line);padding:.22rem .35rem;text-align:left}
th{color:var(--muted);font-weight:600}
.entrytag{display:inline-block;background:#00000012;color:var(--muted);border-radius:3px;
padding:.05rem .38rem;font-size:.72rem;letter-spacing:.04em;margin-left:.35rem}
.warn{border:1px solid var(--line);border-left:3px solid #c07a18;padding:.6rem .7rem;
background:#c07a1810;font-size:.88rem;margin:.9rem 0}
.legend{font-size:.82rem;color:var(--muted);margin-top:.7rem}
.legend b{color:var(--fg)}
.ctrl{display:flex;gap:.5rem;align-items:center;margin:.7rem 0}
button{font:inherit;padding:.3rem .8rem;border:1px solid var(--line);border-radius:4px;
background:var(--bg);color:var(--fg);cursor:pointer}
button:hover{background:#00000010}
.turnno{font:600 15px ui-monospace,monospace;min-width:8ch}
a{color:var(--own)}
"""


def page(sit):
    w = sit["window"]
    frames = derived_positions(sit)
    check_turn_coverage(sit)
    check_map_alphabet(sit["static_map_rows"], sit["id"])

    inv = sit["world_state_at_entry"]["inventories"]
    inv_rows = "".join(
        f"<tr><td>{html.escape(k)}</td>"
        + "".join(f"<td>{v}</td>" for v in inv[k]) + "</tr>"
        for k in sorted(inv))
    plant_rows = "".join(
        f"<tr><td>{html.escape(p[0])}</td><td>({p[1]},{p[2]})</td><td>{p[3]}</td>"
        f"<td>{p[4]}</td><td>{p[5]}</td><td>{p[6]}</td></tr>"
        for p in sit["world_state_at_entry"]["plants"])
    unit_rows = "".join(
        f"<tr><td>{u[0]}</td><td>{'ours' if u[1]==0 else 'opponent'}</td>"
        f"<td>({u[2]},{u[3]})</td><td>{u[4]}</td><td>{u[5]}</td><td>{u[6]}</td>"
        f"<td>{u[7]}</td><td>{','.join(str(x) for x in u[8:])}</td></tr>"
        for u in sit["world_state_at_entry"]["units"])

    single = len(w["cells"]) == 1
    shape = ("a one-cell STALL — the unit does not move at all"
             if single else
             f"a {len(w['cells'])}-cell cycle between "
             + " and ".join(f"({c[0]},{c[1]})" for c in w["cells"]))

    frames_json = json.dumps([{"turn": f["turn"], "line": f["line"],
                               "segments": f["segments"]} for f in frames])

    body = f"""<h1>{html.escape(sit['id'])} — {html.escape(sit['kind'])}</h1>
<p class="sub">unit {w['unit']} · turns {w['turn_start']}–{w['turn_end']}
({w['length_turns']} turns) · k={w['k']} · {html.escape(shape)} ·
completeness {html.escape(sit['completeness'])}</p>

<div class="wrap">
<div>
{board_svg(sit, 0, frames)}
<div class="ctrl">
  <button id="prev">◀ prev</button>
  <span class="turnno" id="turnno"></span>
  <button id="next">next ▶</button>
  <span class="sub" style="margin:0">← → step · Home/End jump</span>
</div>
<div class="legend">
  <span class="legend-derived"><b>Dashed hollow circle</b> = <b>inferred</b> own position —
  where the troll would be <em>if</em> its order completed. Not a recorded position.</span><br>
  <b>Solid red circle</b> = opponent <span class="entrytag">at entry</span> ·
  <b>Letter</b> = plant <span class="entrytag">at entry</span> ·
  <b>Amber cells</b> = the squares this episode repeats.
</div>
</div>

<div class="panel">
<h2>Command this turn — ground truth</h2>
<div class="cmd" id="cmdline"></div>
<div id="targets" class="legend"></div>

<div class="warn">
<b>What is recorded and what is inferred.</b> The command line above is copied verbatim from the
referee transcript — it is what our bot ordered. The dashed circle is <b>our inference</b> that
the order completed. It may not have: a <code>MOVE</code> to a square further than the unit's
speed lands part-way, and a simultaneous move by the opponent can change the result. The
opponent's own commands are <b>not in this library</b>, so no realized position can be
reconstructed from it.
</div>

<h2>Inventories <span class="entrytag">at entry</span></h2>
<table><tr><th>side</th>{''.join(f'<th>{s[:2]}</th>' for s in CARRY_SLOTS)}</tr>
{inv_rows}</table>

<h2>Units <span class="entrytag">at entry</span></h2>
<table><tr><th>id</th><th>side</th><th>cell</th><th>speed</th><th>cap</th><th>harv</th>
<th>chop</th><th>carry</th></tr>{unit_rows}</table>

<h2>Plants <span class="entrytag">at entry</span></h2>
<table><tr><th>kind</th><th>cell</th><th>size</th><th>health</th><th>fruits</th>
<th>cooldown</th></tr>{plant_rows}</table>

<p class="sub">Every panel above is frozen at turn {sit['world_state_at_entry']['turn']}, the
episode's entry. They are <b>not advanced</b> as you step: plant growth, harvests, cargo and
inventories cannot be derived honestly from our own commands alone.</p>

<p class="sub"><a href="index.html">← all situations</a></p>
</div>
</div>

<script>
const FRAMES = {frames_json};
let i = 0;
function render() {{
  document.querySelectorAll('[data-role="derived-position"]').forEach(function (el) {{
    el.classList.toggle('show', el.classList.contains('f' + i));
  }});
  document.getElementById('turnno').textContent = 'turn ' + FRAMES[i].turn;
  document.getElementById('cmdline').textContent = FRAMES[i].line;
  var t = FRAMES[i].segments.map(function (s) {{
    var m = /^MOVE\\s+(\\d+)\\s+(\\d+)\\s+(\\d+)$/.exec(s);
    return m ? ('unit ' + m[1] + ' ordered to (' + m[2] + ',' + m[3] + ')')
             : ('unit order: ' + s);
  }}).join(' · ');
  document.getElementById('targets').textContent = t + '  — order target, ground truth';
}}
function step(d) {{ i = Math.max(0, Math.min(FRAMES.length - 1, i + d)); render(); }}
document.getElementById('prev').onclick = function () {{ step(-1); }};
document.getElementById('next').onclick = function () {{ step(1); }};
document.addEventListener('keydown', function (e) {{
  if (e.key === 'ArrowLeft') {{ step(-1); e.preventDefault(); }}
  if (e.key === 'ArrowRight') {{ step(1); e.preventDefault(); }}
  if (e.key === 'Home') {{ i = 0; render(); e.preventDefault(); }}
  if (e.key === 'End') {{ i = FRAMES.length - 1; render(); e.preventDefault(); }}
}});
render();
</script>"""

    out = (f"<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
           f"<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
           f"<title>{html.escape(sit['id'])} — {html.escape(sit['kind'])}</title>"
           f"<style>{CSS}</style></head><body>{body}</body></html>")
    check_inference_marked(out, sit["id"])
    return out


def index_page(situations):
    rows = []
    for s in sorted(situations, key=lambda x: x["id"]):
        w = s["window"]
        shape = "stall (1 cell)" if len(w["cells"]) == 1 else f"{len(w['cells'])}-cell cycle"
        terrain = sorted({c for r in s["static_map_rows"] for c in r} & {"+", "~"})
        rows.append(
            f'<tr><td><a href="{s["id"]}.html">{s["id"]}</a></td>'
            f'<td>{html.escape(s["kind"])}</td><td>{shape}</td>'
            f'<td>{w["length_turns"]}</td><td>{w["turn_start"]}–{w["turn_end"]}</td>'
            f'<td>{w["unit"]}</td><td>{"".join(terrain) or "—"}</td></tr>')
    kinds = {}
    for s in situations:
        kinds[s["kind"]] = kinds.get(s["kind"], 0) + 1
    body = f"""<h1>Oscillation situations — {len(situations)} frozen</h1>
<p class="sub">Subject <code>readable__no_orchard</code>
<code>98628e98…</code> · {' · '.join(f'{v} {k}' for k, v in sorted(kinds.items()))} ·
display-only, nothing here is a ruling</p>
<div class="warn"><b>How to read these pages.</b> Solid marks are recorded facts — the command
line and the opponent/plant snapshot at the moment the episode begins. The dashed hollow circle
is the one thing we infer: where a troll would be if its order completed. Side panels are frozen
at entry and never advance.</div>
<table><tr><th>id</th><th>kind</th><th>shape</th><th>turns</th><th>range</th><th>unit</th>
<th>terrain</th></tr>{''.join(rows)}</table>"""
    return (f"<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            f"<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>Oscillation situations</title><style>{CSS}</style></head>"
            f"<body>{body}</body></html>")


# --------------------------------------------------------------------------------------


def load(directory=LIB_DIR):
    import oscillation_library as ol
    return ol.load_library(directory)


def build(outdir, situations=None):
    situations = load() if situations is None else situations
    check_situation_count(situations)
    check_visual_distinction(CSS)
    os.makedirs(outdir, exist_ok=True)
    written = []
    for s in situations:
        p = os.path.join(outdir, f"{s['id']}.html")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(page(s))
        written.append(p)
    p = os.path.join(outdir, "index.html")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(index_page(situations))
    written.append(p)
    return written


def _self_test():
    """Every check must be observed REJECTING before the build is trusted."""
    situations = load()
    cases = []

    def rejects(label, fn, expect_fragment):
        try:
            fn()
        except BuildError as e:
            ok = expect_fragment.lower() in str(e).lower()
            cases.append((label, ok, str(e)[:90]))
            return
        cases.append((label, False, "NO ERROR RAISED — the check cannot fail"))

    def accepts(label, fn):
        try:
            fn()
            cases.append((label, True, "accepted"))
        except BuildError as e:
            cases.append((label, False, f"unexpected rejection: {e}"))

    accepts("baseline: all 34 situations render", lambda: [page(s) for s in situations])
    accepts("baseline: count check passes", lambda: check_situation_count(situations))

    bad_map = json.loads(json.dumps(situations[0]))
    bad_map["static_map_rows"][2] = bad_map["static_map_rows"][2][:-1] + "Z"
    rejects("unknown map character", lambda: page(bad_map), "absent from the legend")

    rejects("situation count drift (33)",
            lambda: check_situation_count(situations[:-1]), "expected 34")

    short = json.loads(json.dumps(situations[0]))
    short["window"]["commands"] = short["window"]["commands"][:-1]
    rejects("fewer command rows than length_turns", lambda: page(short), "command rows against")

    holed = json.loads(json.dumps(situations[0]))
    if len(holed["window"]["commands"]) > 2:
        holed["window"]["commands"][1]["turn"] += 100
        rejects("a hole in the turn sequence", lambda: page(holed), "contiguous range")

    # The inference-marking check, exercised against a deliberately unmarked emitter.
    unmarked = f'<svg><circle {DERIVED_ROLE} class="own f0"/></svg><span class="legend-derived">x'
    rejects("derived position emitted without its marking",
            lambda: check_inference_marked(unmarked, "SYNTH"), "without its")

    nolegend = f'<svg><circle {DERIVED_ROLE} class="own derived f0"/></svg>'
    rejects("inferred positions drawn with no legend explaining them",
            lambda: check_inference_marked(nolegend, "SYNTH"), "no legend")

    accepts("baseline: ground truth and inference styled differently",
            lambda: check_visual_distinction(CSS))
    rejects("inference not dashed (looks like recorded fact)",
            lambda: check_visual_distinction(CSS.replace("stroke-dasharray:4 3", "")),
            "not dashed")
    rejects("opponent drawn hollow, same treatment as inference",
            lambda: check_visual_distinction(
                CSS.replace(".opp{fill:var(--opp);stroke:none}", ".opp{fill:none;stroke:red}")),
            "look alike")

    allok = True
    for label, ok, detail in cases:
        print(f"  {'OK  ' if ok else 'BAD '} {label:52} {detail}")
        allok = allok and ok

    print(f"\nself-test: {len(cases)} cases —",
          "PASS — every check observed rejecting" if allok
          else "FAIL — a check that cannot fail is not a check")
    print("\nWhat this self-test CANNOT see. It proves inferred marks carry their role and class,"
          "\nand that `.own` and `.opp` are styled differently (hollow+dashed vs solid). It does"
          "\nNOT prove the page LOOKS right: no browser renders here, nothing is screenshotted,"
          "\nand a stylesheet that is well-formed but visually confusing would pass every case"
          "\nabove. **The visual layer is unverified by execution and needs one human look before"
          "\nthe first live session.** Stated rather than papered over.")
    return 0 if allok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=os.path.join("claude_1", "viewer", "out"))
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    written = build(os.path.join(REPO, args.out) if not os.path.isabs(args.out) else args.out)
    print(f"wrote {len(written)} files to {args.out}")
    print(f"open {os.path.join(args.out, 'index.html')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
