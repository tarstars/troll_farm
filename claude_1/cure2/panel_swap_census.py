#!/usr/bin/env python3
"""C-4/C-5/C-6/C-9/C-14/C-15 over the 240-game panel, read off the instrument arm's own wire.

This is the population number the C-5 stop needs: how often the same pair re-exchanges within six
turns, on how many games, and what those games cost. Every figure here is decoded by
`claude_1/narrate5/narrate5.py` from the candidate command stream the panel itself recorded — no
adapter, no re-run, no second referee.

    python3 claude_1/cure2/panel_swap_census.py [/tmp/.../games.jsonl.gz]

What it produces, each a pre-committed control:

  C-4   `pz == 1` on every turn of every game                      (the single-pass invariant)
  C-9   0 telemetry errors; no `H`; `b == 0` everywhere; the longest v5 payload
  C-5   same unordered pair exchanging twice within 6 turns        (0 required; positive = STOP)
  C-6   same unordered pair exchanging on consecutive turns        (0 required; positive falsifies
                                                                    Theorem 1)
  C-14  the refusal counters `so=` / `sn=` / `sf=` per game        (`sf` expected 0)
  C-15  every game whose score changed, named with its delta       (published, never netted away)
  bar   swap ticks <= 1 per 50 turns per game                      (G-0 §8)
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "narrate5"))

import narrate5 as n5                 # noqa: E402

WINDOW = 6
TICK_BUDGET_TURNS = 50


def main() -> int:
    games_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "/tmp/claude-1000/cure2/cure2-instrument/games/games.jsonl.gz")
    errors, rows = [], []
    c5_rows, c6_rows, ambiguous = [], [], []
    totals = {"turns": 0, "swaps": 0, "swap_turns": 0, "so": 0, "sn": 0, "sf": 0,
              "wc": 0, "payload_max_chars": 0, "branches": {c: 0 for c in n5.BRANCH_CODES}}
    for line in gzip.open(games_path, "rt"):
        game = json.loads(line)
        key = f"{game['map_id']}:{game.get('seat', '?')}"
        commands = game["artifacts"]["candidate_commands"].rstrip("\n").split("\n")
        swaps, per_game = [], {"so": 0, "sn": 0, "sf": 0, "wc": 0, "turns": len(commands)}
        for index, text in enumerate(commands, 1):
            frags = n5.msg_fragments(text)
            if len(frags) != 1:
                errors.append(f"{key} turn {index}: {len(frags)} MSG fragments")
                continue
            payload = frags[0].strip()
            try:
                turn, units, order, banner, meta = n5.decode(payload)
            except n5.GateError as exc:
                errors.append(f"{key} turn {index}: {exc}")
                continue
            totals["payload_max_chars"] = max(totals["payload_max_chars"], len(payload))
            if meta["pz"] != 1:
                errors.append(f"{key} turn {index}: pz={meta['pz']}, expected 1 (C-4)")
            if meta["sp"]:
                errors.append(f"{key} turn {index}: sp={meta['sp']}, expected 0")
            for uid, unit in units.items():
                totals["branches"][unit[2]] += 1
                if unit[3]:
                    errors.append(f"{key} turn {index}: u{uid} b={unit[3]}, expected 0 (C-9)")
            s_ids = sorted(uid for uid, u in units.items() if u[2] == "S")
            x_ids = sorted(uid for uid, u in units.items() if u[2] == "X")
            if len(s_ids) != meta["sw"] or len(x_ids) != meta["sw"]:
                errors.append(f"{key} turn {index}: sw={meta['sw']} against {len(s_ids)} S / "
                              f"{len(x_ids)} X codes")
            for field in ("so", "sn", "sf", "wc"):
                per_game[field] += meta[field]
                totals[field] += meta[field]
            totals["turns"] += 1
            if meta["sw"]:
                totals["swaps"] += meta["sw"]
                totals["swap_turns"] += 1
                if len(s_ids) == 1 and len(x_ids) == 1:
                    swaps.append({"turn": index, "mover": s_ids[0], "displaced": x_ids[0],
                                  "targets": {str(uid): units[uid][0] for uid in (s_ids[0],
                                                                                 x_ids[0])}})
                else:
                    ambiguous.append({"game": key, "turn": index,
                                      "movers": s_ids, "displaced": x_ids})
        by_pair = {}
        for event in swaps:
            by_pair.setdefault(tuple(sorted((event["mover"], event["displaced"]))),
                               []).append(event)
        game_c5, game_c6 = 0, 0
        for pair, events in sorted(by_pair.items()):
            for previous, current in zip(events, events[1:]):
                gap = current["turn"] - previous["turn"]
                record = {"game": key, "pair": list(pair), "first_turn": previous["turn"],
                          "second_turn": current["turn"], "gap": gap,
                          "reversed": current["mover"] == previous["displaced"],
                          "targets_first": previous["targets"],
                          "targets_second": current["targets"]}
                if gap <= WINDOW:
                    c5_rows.append(record)
                    game_c5 += 1
                if gap == 1:
                    c6_rows.append(record)
                    game_c6 += 1
        delta = game["candidate"]["score"] - game["parent"]["score"]
        budget = per_game["turns"] / TICK_BUDGET_TURNS
        rows.append({"game": key, "class": game["class"],
                     "orchard_eligible": game["orchard_eligible"],
                     "turns": per_game["turns"], "swaps": len(swaps),
                     "swap_budget": round(budget, 2),
                     "over_tick_budget": len(swaps) > budget,
                     "c5": game_c5, "c6": game_c6,
                     "so": per_game["so"], "sn": per_game["sn"], "sf": per_game["sf"],
                     "candidate_score": game["candidate"]["score"],
                     "parent_score": game["parent"]["score"], "delta": delta,
                     "candidate_d3": game["detector_counts"]["D-3"],
                     "parent_d3": None})
    changed = [r for r in rows if r["delta"]]
    c5_games = sorted({r["game"] for r in c5_rows})
    report = {
        "control": "panel swap census (C-4, C-5, C-6, C-9, C-14, C-15)",
        "task": "20260825-dance-cure-candidate-2-swap",
        "source": str(games_path),
        "games": len(rows), "turns": totals["turns"],
        "telemetry_errors": len(errors), "telemetry_error_sample": errors[:40],
        "c9_verdict": "PASS" if not errors else "FAIL",
        "payload_max_chars": totals["payload_max_chars"],
        "branches": totals["branches"],
        "exchanges": totals["swaps"], "swap_turns": totals["swap_turns"],
        "games_with_an_exchange": sum(1 for r in rows if r["swaps"]),
        "ambiguous_turns": len(ambiguous),
        "c6_rows": c6_rows, "c6_count": len(c6_rows),
        "c6_verdict": "PASS" if not c6_rows and not ambiguous else "FAIL",
        "c5_rows": c5_rows, "c5_count": len(c5_rows), "c5_games": c5_games,
        "c5_verdict": "PASS" if not c5_rows and not ambiguous else "STOP_AND_ASK",
        "refusals": {"so": totals["so"], "sn": totals["sn"], "sf": totals["sf"]},
        "c14_verdict": "PASS" if totals["sf"] == 0 else "FAIL",
        "w_collisions": totals["wc"],
        "tick_budget_breaches": [r for r in rows if r["over_tick_budget"]],
        "changed_games": len(changed),
        "better": sum(1 for r in changed if r["delta"] > 0),
        "worse": sum(1 for r in changed if r["delta"] < 0),
        "net_delta": sum(r["delta"] for r in rows),
        "rows": rows,
    }
    out = HERE / "results" / "panel-swap-census.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"  games {len(rows)}  turns {totals['turns']}  telemetry errors {len(errors)} "
          f"-> C-9 {report['c9_verdict']}")
    print(f"  branches {totals['branches']}  longest payload {totals['payload_max_chars']} chars")
    print(f"  exchanges {totals['swaps']} on {report['games_with_an_exchange']} games; "
          f"refusals so={totals['so']} sn={totals['sn']} sf={totals['sf']} -> C-14 "
          f"{report['c14_verdict']}")
    print(f"  C-6 consecutive repeats {len(c6_rows)} -> {report['c6_verdict']}")
    print(f"  C-5 repeats within {WINDOW} turns {len(c5_rows)} on {len(c5_games)} games -> "
          f"{report['c5_verdict']}")
    print(f"  tick-budget breaches {len(report['tick_budget_breaches'])} games")
    print(f"  score: {report['better']} better, {report['worse']} worse, "
          f"net {report['net_delta']:+} over {len(rows)} games")
    print(f"  -> {out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
