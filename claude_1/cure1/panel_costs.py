#!/usr/bin/env python3
"""G-1 item 2 — the rule-on 240-game panel with **every changed game named**.

Subject: `claude_1/cure1/arm-candidate.rs` (hold rule ON, no `MSG`). Floor: the champion base
`547fa706` judged against ITSELF over the identical corpus. Both panels are proved matched by
`g2_grade.gate_m` — the floor's candidate arm must BE this panel's parent arm, byte for byte,
game for game — before a single count is read.

The comparator is `claude_1/gd1/gd_named_costs.py`'s `grade`/`controls`, imported rather than
reimplemented. That file's README marks its 2026-08-23 RESULT as inert scratch; what is reused
here is its comparator CODE, and its three controls (null fork, poison fork, non-vacuity) are
re-run on THIS task's panels, so nothing inherits a green from that run.

## The charter's bar, and the number in it that does not belong to this base

The charter asks for "blocking games **not above the base's 35** (r2 went 35 → 115)". That 35 is
the blocking count of `claude_1/picker2/candidate-door1-p1p2.rs` (`5e1f4df4`) — the r2 build's own
base, a different lineage. The champion base of THIS task, `547fa706`, blocks **43** on this
corpus (`claude_1/picker2/panel-door1-floor.json`, 2026-08-20, reproduced here). Both numbers are
reported and each is labelled with the bot it belongs to; the honest comparator for this candidate
is its own base's 43, and the charter's 35 is carried alongside rather than quietly swapped.

## What this does NOT do

It does not grade progress — that is the fixture gate's `progress_restored` clause and, on real
games, G-2. A detector going quiet here is not a healed dance. It measures nothing about score.

    python3 claude_1/cure1/panel_costs.py [--controls]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1/swap1"))
sys.path.insert(0, str(REPO / "claude_1/picker2"))
sys.path.insert(0, str(REPO / "claude_1/gd1"))
import g2_grade as G              # noqa: E402
import gd_named_costs as ND       # noqa: E402

CAND_GAMES = Path("/tmp/claude-1000/cure1/cure1-candidate/games/games.jsonl.gz")
FLOOR_GAMES = Path("/tmp/claude-1000/cure1/cure1-floor/games/games.jsonl.gz")
OUT = HERE / "results" / "panel-named-costs.json"

CHARTER_BAR_35 = ("claude_1/picker2/candidate-door1-p1p2.rs @ 5e1f4df4 — the r2 lineage's base, "
                  "NOT this task's champion base")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--candidate-games", default=str(CAND_GAMES))
    ap.add_argument("--floor-games", default=str(FLOOR_GAMES))
    ap.add_argument("--json", default=str(OUT))
    ap.add_argument("--controls", action="store_true")
    args = ap.parse_args(argv)

    cand_rows = G.load(Path(args.candidate_games))
    floor_rows = G.load(Path(args.floor_games))
    matched, problems = G.gate_m(cand_rows, floor_rows)
    if not matched:
        print("GATE M FAILED — the panels are not matched; refusing to report counts")
        for p in problems[:20]:
            print("   ", p)
        return 1
    print(f"GATE M PASS — {len(cand_rows)} (map, seat) games matched byte-for-byte on the base arm")

    table = ND.grade(cand_rows, floor_rows)
    table["task"] = "20260825-dance-cure-candidate-1-hold"
    table["gate"] = "G-1 item 2 — rule-on 240-game panel, every changed game named"
    table["subject"] = "claude_1/cure1/arm-candidate.rs (hold rule ON, no MSG)"
    table["base"] = ("cgauto/submissions/candidate-door1-pure-deletion.rs @ 547fa706 — the "
                     "champion base, judged against itself as the matched floor")
    table["authorization"] = ("coordination/messages/local_claude_1/"
                              "20260825T075500Z-20260825-dance-cure-candidate-1-hold-policy.md; "
                              "construction ruling 20260825T085500Z")
    table["comparator"] = ("claude_1/gd1/gd_named_costs.py grade/controls, imported; "
                           "g2_grade.gate_m for the matched-panel proof")
    table["gate_m_matched_panel"] = True
    table["charter_bar_note"] = {
        "charter_text": "blocking games not above the base's 35 (r2 went 35 -> 115)",
        "the_35_belongs_to": CHARTER_BAR_35,
        "this_base_blocking_on_this_corpus": table["blocking"]["base"],
        "cross_check": ("claude_1/picker2/panel-door1-floor.json (2026-08-20) reported 43 for "
                        "547fa706 against itself on this corpus"),
    }
    table["not_measured_here"] = ("progress restoration (the fixture gate's clause, and G-2 on "
                                  "real games); score (G-3); anything about the instrument arm, "
                                  "whose MSG token changes eval_p3 by construction")
    if args.controls:
        table["controls"] = ND.controls(cand_rows, floor_rows)

    Path(args.json).write_text(json.dumps(table, indent=2, sort_keys=True) + "\n")

    b = table["blocking"]
    print(f"\n  blocking games   base {b['base']:>3}   candidate {b['candidate']:>3}   "
          f"-> {b['delta']:+d}   (charter's 35 belongs to {CHARTER_BAR_35.split(' — ')[0]})")
    print(f"  D-1 episodes     base {table['d1_episodes']['base']:>3}   candidate "
          f"{table['d1_episodes']['candidate']:>3}")
    print(f"  P4 violations    base {table['p4_violations']['base']:>3}   candidate "
          f"{table['p4_violations']['candidate']:>3}")
    print(f"  command stream identical to the base: "
          f"{table['games_with_a_command_stream_identical_to_the_base']}/{table['games']}")
    print(f"  changed games named: {table['changed_games']}   {table['by_kind']}")
    print("\n  detector totals that GREW:", table["detector_totals"]["grew"] or "-")
    print("  detector totals that SHRANK:", table["detector_totals"]["shrank"] or "-")
    print("  property games that GREW:", table["property_games"]["grew"] or "-")
    print("  flag games that GREW:", table["flag_games"]["grew"] or "-")
    fal = table["falsifiers"]
    print(f"\n  de-novo blocks: {len(fal['s7_3_de_novo_blocks'])}")
    print(f"  P4 worse: {len(fal['s7_5_p4_worse_games'])}   "
          f"r5-horizon new: {len(fal['s7_5_r5_horizon_new_games'])}   "
          f"P3 new: {len(fal['s7_5_p3_new_games'])}")
    if args.controls:
        print("\n  controls:", json.dumps({k: v.get("pass") for k, v in table["controls"].items()
                                           if isinstance(v, dict)}))
    print(f"\n  -> {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
