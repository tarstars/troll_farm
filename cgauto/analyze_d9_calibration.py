#!/usr/bin/env python3
"""D-9 calibration: does `banana_before_train` measure TRAIN displacement?

Phase 1 item 1 of `docs/HARDENING-PLAN-CONSOLIDATED-2026-08-07.md`. Read-only
analysis over the committed parent-vs-parent floor self-test; it runs no games,
edits no detector, and proposes no gate change.

D-9 ("second-worker TRAIN displacement",
`claude_1/banana-restoration-r2/trace_detectors.py:1172`) has two kinds of
clause:

* **paired** — `train_late`, `train_missing`, `train_stats_differ`. These compare
  the candidate's first TRAIN turn and stats tuple against the parent's, so they
  observe displacement directly. They require `parent_commands`, which
  `fuzz_panel.eval_p1` forwards through `td.run_all`.
* **unpaired proxy** — `banana_before_train` (spec A10, read literally): any
  `PLANT`/`PICK … BANANA` command issued before the candidate's own TRAIN while
  it holds one unit. It never looks at the parent. It assumes banana work before
  TRAIN must have delayed TRAIN.

The floor self-test judged the parent against *itself*, so displacement is zero
by construction: the candidate trains on the same turn, with the same stats, as
the reference it is compared to. Any D-9 episode in that run is therefore a
false positive by construction. This module reports how many there are, split by
clause, which is the calibration answer.

It also lists detectors with zero episodes over the whole panel. Those are
`UNPROVEN`, not passing: nothing in the run demonstrates they can fire at all.

Usage:
    python3 cgauto/analyze_d9_calibration.py [--json] [<floor-result.json>]
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_FLOOR = (REPO_ROOT / "local_claude_1" / "verification"
                 / "local_claude_1-floor-selftest-result-2026-08-07.json")
PAIRED_CLAUSES = ("train_late", "train_missing", "train_stats_differ")
PROXY_CLAUSE = "banana_before_train"
ALL_DETECTORS = tuple(f"D-{i}" for i in range(1, 10))


def sha256_of(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_report(floor_path: pathlib.Path = DEFAULT_FLOOR) -> dict:
    data = json.loads(floor_path.read_text(encoding="utf-8"))
    games = data["games"]

    # Parent-vs-parent is what makes the run interpretable: if the candidate is
    # the parent, no displacement can exist, so every D-9 episode is spurious.
    is_parent_vs_parent = all(
        g.get("candidate") == g.get("parent") for g in games
    ) and bool(games)

    by_clause: collections.Counter = collections.Counter()
    verbs: collections.Counter = collections.Counter()
    d9_games: set[int] = set()
    detector_episodes: collections.Counter = collections.Counter()
    detector_games: collections.Counter = collections.Counter()

    for index, game in enumerate(games):
        for detector, count in (game.get("detector_counts") or {}).items():
            if count:
                detector_episodes[detector] += count
                detector_games[detector] += 1
        for violation in game.get("violations") or []:
            if violation.get("detector") != "D-9":
                continue
            d9_games.add(index)
            for episode in violation.get("episodes", []):
                by_clause[episode.get("kind")] += 1
                if episode.get("verb"):
                    verbs[episode["verb"]] += 1

    blocking = [i for i, g in enumerate(games) if g.get("block")]
    # What the floor would be if D-9 were retired: a game still blocks when any
    # other detector fired in it.
    without_d9 = [
        i for i in blocking
        if any(c for d, c in (games[i].get("detector_counts") or {}).items()
               if d != "D-9")
    ]

    proxy = by_clause.get(PROXY_CLAUSE, 0)
    measured = sum(by_clause.get(c, 0) for c in PAIRED_CLAUSES)
    if is_parent_vs_parent and proxy and not measured:
        verdict = "MISCALIBRATED_RETIRE_OR_REPAIR"
    elif not proxy:
        verdict = "PROXY_SILENT_ON_THIS_PANEL"
    else:
        verdict = "INCONCLUSIVE"

    return {
        "task": "D-9 calibration (Phase 1 item 1)",
        "source": str(floor_path.relative_to(REPO_ROOT)),
        "source_sha256": sha256_of(floor_path),
        "games": len(games),
        "is_parent_vs_parent": is_parent_vs_parent,
        "episodes_by_clause": dict(by_clause),
        "verbs": dict(verbs),
        "affected_games": len(d9_games),
        "proxy_episodes": proxy,
        "measured_displacement_episodes": measured,
        "verdict": verdict,
        "blocking_games": len(blocking),
        "blocking_games_without_d9": len(without_d9),
        "detector_totals": {
            d: {"episodes": detector_episodes.get(d, 0),
                "games": detector_games.get(d, 0)}
            for d in ALL_DETECTORS
        },
        "unproven_detectors": [
            d for d in ALL_DETECTORS if not detector_episodes.get(d, 0)
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("floor", nargs="?", type=pathlib.Path, default=DEFAULT_FLOOR)
    ap.add_argument("--json", action="store_true", help="emit the report as JSON")
    args = ap.parse_args()

    report = build_report(args.floor)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0

    print(f"D-9 calibration — {report['source']} ({report['source_sha256'][:12]})")
    print(
        f"{report['games']} games, parent-vs-parent="
        f"{report['is_parent_vs_parent']} (displacement is zero by construction)\n"
    )
    print("D-9 episodes by clause:")
    for clause in (PROXY_CLAUSE, *PAIRED_CLAUSES):
        count = report["episodes_by_clause"].get(clause, 0)
        tag = "proxy  " if clause == PROXY_CLAUSE else "paired "
        print(f"  {tag}{clause:<22}{count:>6}")
    print(f"\n  affected games: {report['affected_games']}")
    print(f"  verbs: {report['verbs']}")
    print(f"\nverdict: {report['verdict']}")
    print(
        f"floor: {report['blocking_games']} blocking games; "
        f"{report['blocking_games_without_d9']} would still block without D-9"
    )
    print("\ndetector totals (episodes / games):")
    for detector, totals in report["detector_totals"].items():
        mark = "  UNPROVEN — never fired" if not totals["episodes"] else ""
        print(f"  {detector}: {totals['episodes']:>4} / {totals['games']:>3}{mark}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
