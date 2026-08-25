#!/usr/bin/env python3
"""G-1 item 1, second half — the **alpha parity gate on the 240-game panel**.

The panel already runs both bots on the identical spec and archives both command streams. This
reads that archive and asks the parity question directly, game by game:

  the rule-off arm's stream, with its single `MSG` fragment per turn stripped, must be the
  parent's stream token for token, in order, on all 240 games

plus the same v4 wire controls the fixture gate runs (one pass, no `H`, no nonzero `b`, `sp=0`),
now over ~48,000 turns of real panel play rather than 6,800 fixture turns.

## Why the rule-off panel's BLOCKING COUNT is not read here, and must not be

A telemetry arm emits a `MSG` token on every turn. `eval_p3` compares the candidate's command
stream to the parent's BYTE-WISE, so on an orchard-eligible map the extra token is a P3 violation
by construction, and the detector layer sees a differently-shaped command line. The rule-off arm's
52 blocking games against the floor's 43 are therefore an artifact of the instrument, not a
property result, and this module says so rather than quietly reporting the number. The blocking
comparison that means something is the CANDIDATE arm's (no `MSG`), in `panel_costs.py`.

    python3 claude_1/cure1/panel_parity.py [--games <games.jsonl.gz>] [--rule-on]
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "narrate4"))
import narrate4 as n4               # noqa: E402

DEFAULT_GAMES = Path("/tmp/claude-1000/cure1/cure1-ruleoff/games/games.jsonl.gz")


def lines(blob: str) -> list[str]:
    return blob.rstrip("\n").split("\n") if blob.strip() else []


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--games", default=str(DEFAULT_GAMES))
    ap.add_argument("--no-telemetry", action="store_true",
                    help="the arm emits no MSG (the candidate arm): compare streams only")
    ap.add_argument("--rule-on", action="store_true",
                    help="the arm has the hold rule ON: report divergence, do not require parity")
    ap.add_argument("--out", default=str(HERE / "results" / "panel-parity-ruleoff.json"))
    args = ap.parse_args()

    rows, telemetry_errors, changed = [], [], []
    census = n4.new_census()
    with gzip.open(args.games, "rt", encoding="utf-8") as fh:
        games = [json.loads(line) for line in fh]
    for game in games:
        art = game.get("artifacts") or {}
        cand, parent = lines(art.get("candidate_commands", "")), \
            lines(art.get("parent_commands", ""))
        stripped = [n4.strip_msg(l) for l in cand]
        base = [n4.strip_msg(l) for l in parent]
        identical = stripped == base
        first = None
        if not identical:
            for i, (a, b) in enumerate(zip(base, stripped), 1):
                if a != b:
                    first = {"turn": i, "base": a, "arm": b}
                    break
            if first is None:
                first = {"turn": None, "base_turns": len(base), "arm_turns": len(stripped)}
            changed.append({"map_id": game["map_id"], "seat": game["seat"],
                            "first_divergence": first})
        errs = [] if args.no_telemetry else n4.check_telemetry(
            f"{game['map_id']}s{game['seat']}", None, cand, census, rule_off=not args.rule_on)
        telemetry_errors.extend(f"{game['map_id']} s{game['seat']}: {e}" for e in errs)
        rows.append({"map_id": game["map_id"], "seat": game["seat"], "turns": len(cand),
                     "byte_identical_without_msg": identical, "telemetry_errors": len(errs),
                     "first_divergence": first})

    parity = sum(1 for r in rows if r["byte_identical_without_msg"])
    ok = (not telemetry_errors) and (args.rule_on or parity == len(rows))
    report = {
        "gate": "alpha parity on the 240-game panel",
        "task": "20260825-dance-cure-candidate-1-hold",
        "games_archive": args.games,
        "rule_on": args.rule_on,
        "games": len(rows),
        "byte_identical_without_msg": parity,
        "changed_games": changed if args.rule_on else changed[:40],
        "changed_game_count": len(changed),
        "telemetry_error_count": len(telemetry_errors),
        "telemetry_errors": telemetry_errors[:40],
        "verdict": "PASS" if ok else "FAIL",
        "census": None if args.no_telemetry else census,
        "blocking_count_not_read_here":
            "a telemetry arm emits one MSG token per turn; eval_p3 compares command streams "
            "byte-wise, so the rule-off arm's blocking count is an instrument artifact. The "
            "blocking comparison that means something is the candidate arm's, which emits no MSG.",
        "rows": rows,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"  panel parity: {parity}/{len(rows)} games byte-identical without MSG, "
          f"{len(telemetry_errors)} telemetry errors over {census['turns']} turns "
          f"-> {report['verdict']}")
    if args.no_telemetry:
        print("  (no telemetry on this arm: stream comparison only)")
        print(f"  changed games {len(changed)}")
        return 0 if ok else 1
    print(f"  branches: {census['branches']}  max passes {census['max_passes']}  "
          f"stale protections {census['stale_protections']}  "
          f"W-collisions {census['w_collision_events']} on {census['w_collision_turns']} turns")
    print(f"  longest payload {census['payload_max_chars']} chars; changed games "
          f"{len(changed)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
