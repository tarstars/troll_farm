#!/usr/bin/env python3
"""Deliverable 2 — the mechanism carry-over table.

Which of the owner-ruled mechanisms have an exhibit on the CHAMPION, and which old rulings
have none any more. The second half is the part that has to be said carefully: a mechanism
with no case in this library has **NO EXHIBIT** on the champion. That is not "fixed", and
this file never writes that word about a mechanism. Two different things can produce it —
the champion genuinely no longer does it, or the champion's 240-game floor simply did not
land in a game that shows it — and nothing here distinguishes them.

What is measured here, and what is cited:

* **Measured** (from the two libraries' own frozen records and a replay of the champion):
  each champion case's classifier label, its blocker state, the game it comes from, which
  old case shares that game, and its benched unit-turns under the accepted eligible-action
  oracle (`claude_1/hstarve1/oracle.py`).
* **Cited** (the old side of every row): which old cases the record attaches to each ruled
  mechanism, with the artifact that says so. No attribution is invented here; where the
  record does not pin a case list, the row says so instead of guessing.

The classifier's own vocabulary is the join, and it is a published definition, not a
reading of mine (`build_oscillation_library.classify`):

    M1  a stationary peer occupies the route             -> the "pass" shapes
    M2  the stationary peer is IDLE and stands on a live plant, invisible to `compatible`
                                                        -> "idle troll parked on a plant"
    M3  no peer is alive in the window, so the goal itself alternates
                                                        -> "single-troll goal flip"
    UNCLASSIFIED  none of the discriminators applies

M1 does NOT separate "corridor pass" from "open-map pass", and nothing in the library
separates "same tree wanted" at all: the discriminator is the resolver's GOAL, which the
library records as explicitly UNRESOLVED (`GOAL_UNRESOLVED`). Those rows say so.

    python3 carry_over.py [--json out.json] [--md out.md]
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
R2 = HERE.parent
REPO = R2.parent.parent
for p in ("claude_1/t1", "claude_1/pipeline", "claude_1/hstarve1"):
    sys.path.insert(0, str(REPO / p))
sys.path.insert(0, str(R2))
sys.path.insert(0, str(HERE))

import fixture_harness as fh          # noqa: E402
import oscillation_library as ol      # noqa: E402
import oracle                          # noqa: E402
import build_subject_library as bsl    # noqa: E402

CHAMP = HERE / "library"
OLD = R2 / "oscillation-library-98628e98" / "library"

# The old side of the table. Every entry names the artifact that attaches those cases to
# that mechanism; nothing here is my own attribution.
RULED = [
    {
        "mechanism": "corridor pass -> swap",
        "rule": "R-1 (owner-approved 2026-08-16)",
        "old_cases": ["OSC-001"],
        "old_class_note": "expected to bear on the 11 M1 corridor episodes",
        "cited": "docs/RULES-LEDGER.md R-1; local_claude_1/adjudications/OSC-001-ruling-2026-08-16.md",
        "library_label": "M1",
    },
    {
        "mechanism": "open-map pass -> teammate-aware routing",
        "rule": "cure beta, designed, not built",
        "old_cases": ["OSC-010"],
        "old_class_note": "named as a beta target; OSC-010 is M1/WORKING in the old tree",
        "cited": "claude_1/swap1/g0-design-swap-r1-2026-08-21.md section 6",
        "library_label": "M1",
    },
    {
        "mechanism": "same tree wanted -> reservation",
        "rule": "cure beta, designed, not built",
        "old_cases": ["OSC-030"],
        "old_class_note": "named as a beta target; OSC-030 is UNCLASSIFIED in the old tree",
        "cited": "claude_1/swap1/g0-design-swap-r1-2026-08-21.md section 6",
        "library_label": None,
    },
    {
        "mechanism": "single-troll goal flip",
        "rule": "cure gamma, designed, not built; OSC-026 stamp candidate at 4b",
        "old_cases": ["OSC-026"],
        "old_class_note": "the only M3 case in the old tree (no peer alive in the window)",
        "cited": ("claude_1/swap1/g0-design-swap-r1-2026-08-21.md section 6; "
                  "local_claude_1/session-inputs/4b-sitting-package-2026-08-21.md bucket D"),
        "library_label": "M3",
    },
    {
        "mechanism": "idle troll parked on a plant",
        "rule": "cure alpha target shape (amended G-2, 20260821T105914Z)",
        "old_cases": ["OSC-012", "OSC-013", "OSC-017"],
        "old_class_note": "the M2 discriminator IS this shape, by the classifier's definition",
        "cited": ("coordination/messages/local_claude_1/20260821T105914Z-20260821-"
                  "swap-r1-cure-gate-amendment-policy.md; build_oscillation_library.classify"),
        "library_label": "M2",
    },
    {
        "mechanism": "benching: a troll with available work is not employed",
        "rule": "R-2 (owner-approved 2026-08-20), class-wide",
        "old_cases": ["OSC-017", "OSC-013", "OSC-034", "OSC-004"],
        "old_class_note": ("class = all 24 GOAL_SPLIT cases of the pool-3 table; decided by the "
                           "eligible-action oracle, NOT by the library's classifier"),
        "cited": ("docs/RULES-LEDGER.md R-2; "
                  "local_claude_1/session-inputs/4a-sitting-package-2026-08-19.md"),
        "library_label": "ORACLE",
    },
]


def benched_unit_turns(tr, sit):
    """R-2's shape, per case: own unit-turns inside the window that emit WAIT while the
    oracle says the unit had at least one legal action available.

    This is a COUNT of a shape, not a verdict on the bot: the rule the owner approved is
    that such a turn is a defect, and the rule is theirs, not this file's."""
    w = sit["window"]
    lo, hi = int(w["turn_start"]), min(int(w["turn_end"]), tr.T)
    per_unit, total = {}, 0
    for t in range(lo, hi + 1):
        st = tr.state(t)
        for u in st.units:
            if u.player != 0:
                continue
            cmd = tr.cmd_of(u.id, t)
            waiting = cmd is None or str(cmd).strip().upper().startswith("WAIT")
            if waiting and oracle.has_eligible_action(tr, u.id, t):
                per_unit[u.id] = per_unit.get(u.id, 0) + 1
                total += 1
    return {"benched_unit_turns": total, "per_unit": per_unit,
            "window_turns": hi - lo + 1}


def corridor_width_proxy(sit):
    """A DECLARED PROXY, not a ruling: how much free room the cycle cells have.

    The two "pass" mechanisms differ by geometry — a dead-end corridor, where a swap is the
    only resolution, versus open ground, where routing around is available. The classifier
    does not record that distinction, and inventing a corridor/open verdict here would be
    exactly the kind of quiet re-ruling this card forbids. So this counts something plain and
    checkable instead: the mean number of walkable orthogonal neighbours of the window's
    cycle cells. A value near 2 is corridor-shaped; near 4 is open. It is offered so the
    owner can sort the pages, and it decides nothing.
    """
    rows = sit["static_map_rows"]
    walk = {(x, y) for y, r in enumerate(rows) for x, c in enumerate(r) if c not in "#~"}
    cells = [tuple(c) for c in sit["window"]["cells"]]
    if not cells:
        return None
    tot = 0
    for (x, y) in cells:
        tot += sum(1 for d in ((1, 0), (-1, 0), (0, 1), (0, -1))
                   if (x + d[0], y + d[1]) in walk)
    return round(tot / len(cells), 2)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", dest="json_out", default=str(HERE / "carry-over-2026-08-21.json"))
    ap.add_argument("--md", dest="md_out", default=str(HERE / "carry-over-2026-08-21.md"))
    ap.add_argument("--panel-config", default=str(HERE / "panel-config.json"))
    args = ap.parse_args(argv)

    champ = ol.load_library(str(CHAMP))
    old = ol.load_library(str(OLD))
    old_idx = json.loads((OLD / "index.json").read_text())
    champ_idx = json.loads((CHAMP / "index.json").read_text())
    by_game = {}
    for e in old_idx["situations"]:
        by_game.setdefault((e["origin"]["map_id"], e["origin"]["seat"]), []).append(e)

    cfg = json.loads(Path(args.panel_config).read_text())
    rows = []
    with tempfile.TemporaryDirectory(prefix="champlib-carry-") as wd:
        binary = fh.compile_candidate(REPO / bsl.SUBJECT_PATH, Path(wd))
        for s, e in zip(sorted(champ, key=lambda x: x["id"]),
                        sorted(champ_idx["situations"], key=lambda x: x["id"])):
            tr, eps, p4, spec, lines = fh.run_situation_ex(s, binary, cfg)
            ident = fh.episode_identity(s["id"], s, tr, lines)
            if not ident["reproduces_the_recorded_episode"]:
                raise SystemExit("%s: the champion does not reproduce its OWN recorded episode "
                                 "(%s); the table would be about a different game"
                                 % (s["id"], ident["reasons"]))
            bench = benched_unit_turns(tr, s)
            game = (e["origin"]["map_id"], e["origin"]["seat"])
            rows.append({
                "id": s["id"],
                "mechanism_label": e["mechanism"],
                "blocker_state": e["blocker_state"],
                "kind": e["kind"],
                "window": e["window_turns"],
                "unit": e["origin"]["unit"],
                "map_id": game[0],
                "seat": game[1],
                "episodes": e["multiplicity"],
                "free_neighbours_proxy": corridor_width_proxy(s),
                "old_cases_same_game": [
                    {"id": o["id"], "mechanism": o["mechanism"], "window": o["window_turns"],
                     "same_window": o["window_turns"] == e["window_turns"]}
                    for o in by_game.get(game, [])],
                **bench,
            })

    champ_ids = {r["id"] for r in rows}
    labels = {}
    for r in rows:
        labels.setdefault(r["mechanism_label"], []).append(r["id"])
    benched_cases = [r["id"] for r in rows if r["benched_unit_turns"] > 0]

    old_games = {(e["origin"]["map_id"], e["origin"]["seat"]): e["id"]
                 for e in old_idx["situations"]}
    champ_games = {(r["map_id"], r["seat"]) for r in rows}
    old_without_exhibit = sorted(oid for g, oid in old_games.items() if g not in champ_games)

    table = []
    for m in RULED:
        lab = m["library_label"]
        if lab == "ORACLE":
            champ_cases, basis = benched_cases, (
                "cases with at least one benched unit-turn under the eligible-action oracle")
        elif lab is None:
            champ_cases, basis = [], (
                "NOT SEPARABLE by this library's vocabulary: the discriminator is the "
                "resolver's goal, which every situation records as UNRESOLVED")
        else:
            champ_cases, basis = labels.get(lab, []), "classifier label %s" % lab
        shared = [o["mechanism"] for o in RULED
                  if o is not m and o["library_label"] == lab and lab not in (None, "ORACLE")]
        table.append({**m, "champion_cases": champ_cases, "basis": basis,
                      "shares_its_label_with": shared,
                      "exhibit_on_champion": bool(champ_cases),
                      "status": ("exhibit present" if champ_cases
                                 else "NO EXHIBIT -- not a claim that it is fixed")})

    out = {
        "subject": bsl.SUBJECT_GIT_REF,
        "champion_library_sha256": champ_idx["library_sha256"],
        "old_library_sha256": old_idx["library_sha256"],
        "champion_situations": len(rows),
        "old_situations": len(old),
        "label_histogram_champion": champ_idx["mechanism_histogram"],
        "label_histogram_old": old_idx["mechanism_histogram"],
        "carry_over": table,
        "old_cases_whose_GAME_has_no_champion_case": old_without_exhibit,
        "per_case": rows,
        "what_no_exhibit_means": (
            "A mechanism with no case here has NO EXHIBIT on the champion. It is NOT a claim "
            "that the champion has stopped doing it: the champion's floor is 240 games and a "
            "shape can be absent because it did not occur in those games. The owner's rulings "
            "on the old cases are rulings about MECHANISMS and stand unchanged."),
    }
    Path(args.json_out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")

    md = ["# Mechanism carry-over — the champion's exhibits vs the owner's rulings", "",
          "Subject `%s`. Champion library `%s…` (%d cases); old subject library `%s…` (%d cases)."
          % (bsl.SUBJECT_SHA256[:12], champ_idx["library_sha256"][:12], len(rows),
             old_idx["library_sha256"][:12], len(old)), "",
          "**\"No exhibit\" is not \"fixed\".** " + out["what_no_exhibit_means"], "",
          "## The ruled mechanisms", "",
          "| mechanism | rule | old exhibits | champion exhibits | status |",
          "|---|---|---|---|---|"]
    for t in table:
        md.append("| %s | %s | %s | %s | %s |"
                  % (t["mechanism"], t["rule"], ", ".join(t["old_cases"]),
                     ", ".join(t["champion_cases"]) or "—", t["status"]))
    shared_rows = [t for t in table if t.get("shares_its_label_with")]
    if shared_rows:
        md += ["", "**Two rows above share one label and therefore one case list.** " +
               "; ".join("`%s` and %s are both %s in this vocabulary"
                         % (t["mechanism"], " and ".join("`%s`" % x for x in t["shares_its_label_with"]),
                            t["library_label"]) for t in shared_rows[:1]) +
               ". The classifier records that a stationary peer held the route; it does not "
               "record whether the route was a dead-end corridor (where a swap is the only "
               "resolution) or open ground (where routing around exists). Splitting them needs "
               "the resolver's goal, which the library marks UNRESOLVED. The "
               "`free neighbours` column below is a declared geometric PROXY offered for "
               "sorting the viewer pages, and it rules nothing."]
    md += ["", "Join basis, per row: " + "; ".join(
        "**%s** — %s" % (t["mechanism"], t["basis"]) for t in table), "",
        "## Every champion case", "",
        "| case | label | blocker | kind | turns | unit | game | free neighbours (proxy) | benched unit-turns | old case on the same game |",
        "|---|---|---|---|---|---|---|---:|---:|---|"]
    for r in rows:
        old_s = ", ".join("%s (%s%s)" % (o["id"], o["mechanism"],
                                         ", same window" if o["same_window"] else "")
                          for o in r["old_cases_same_game"]) or "— (new game)"
        md.append("| %s | %s | %s | %s | %d–%d | %d | %s s%d | %s | %d | %s |"
                  % (r["id"], r["mechanism_label"], r["blocker_state"], r["kind"],
                     r["window"][0], r["window"][1], r["unit"], r["map_id"], r["seat"],
                     r["free_neighbours_proxy"], r["benched_unit_turns"], old_s))
    md += ["", "## Old cases whose GAME has no champion case (%d)" % len(old_without_exhibit), "",
           ", ".join(old_without_exhibit) or "none", "",
           "A game is matched on `(map_id, seat)`, which is the same panel skeleton in both "
           "libraries. An old case with no champion case on its game means the champion's own "
           "floor recorded no oscillation or stall episode there — again, a statement about "
           "what was recorded, not a verdict about the bot.", ""]
    Path(args.md_out).write_text("\n".join(md))
    print("champion cases: %d; label histogram %s" % (len(rows), champ_idx["mechanism_histogram"]))
    for t in table:
        print("  %-46s %s" % (t["mechanism"], ", ".join(t["champion_cases"]) or "NO EXHIBIT"))
    print("old cases whose game has no champion case: %d" % len(old_without_exhibit))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
