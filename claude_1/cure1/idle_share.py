#!/usr/bin/env python3
"""R-C / disposition (4b) — the **per-troll idle-with-work share**, this family's G-1 safety net.

The ruling of 2026-08-25T09:42:00Z declares `P4` BLIND for this candidate family and replaces it:
`fuzz_panel.progress_turns` credits a turn when the own inventory **or any own unit's cargo**
changes, which is a GAME-level predicate, so one troll parked beside a working teammate is
invisible to it. The charter's poison arm proved that empirically -- 2,689 hold turns with a
194-turn maximum and P4 unmoved at the base's 16.

The replacement clause, fixed by the coordinator BEFORE this arm's numbers existed:

    idle-with-work share = (`H` + `W` turns) / own troll-turns   must be <= 1.5 %

measured on the 240-game panel from the instrument arm's own v4 telemetry, which is per unit and
per turn. `H` is a hold; `W` is a forced or self-targeting WAIT. `N` (no MOVE command at all) is
NOT idle-with-work: a unit harvesting, chopping, planting or banking is working. The base's own
share is measured the same way from the rule-off arm and reproduces the 0.72 % baseline the G-2
kill rule cites.

Three numbers are reported, not one, because the clause has a control attached:

  * the panel aggregate share (the graded number);
  * the per-troll distribution -- worst troll, and how many trolls sit above the line -- because
    the whole reason P4 failed is that an aggregate can hide one parked unit;
  * the longest consecutive hold run, which is what "parked" means.

    python3 claude_1/cure1/idle_share.py [--arms candidate=<games.jsonl.gz> ...]
"""
from __future__ import annotations

import argparse
import collections
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "narrate4"))
import narrate4 as n4               # noqa: E402

LINE = 1.5
DEFAULT_ARMS = {
    "base (rule-off)": "/tmp/claude-1000/cure1/cure1-ruleoff/games/games.jsonl.gz",
    "candidate (rule-on)": "/tmp/claude-1000/cure1/cure1-instrument/games/games.jsonl.gz",
}
OUT = HERE / "results" / "idle-share.json"


def census(path: Path) -> dict:
    branches = collections.Counter()
    per_troll = collections.Counter()          # (map, seat, uid) -> H+W
    per_troll_turns = collections.Counter()    # (map, seat, uid) -> own turns
    longest = 0
    longest_where = None
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for line in fh:
            game = json.loads(line)
            key0 = (game["map_id"], game["seat"])
            for cmdline in game["artifacts"]["candidate_commands"].rstrip("\n").split("\n"):
                frags = n4.msg_fragments(cmdline)
                if not frags:
                    continue
                _, units, _, _, _ = n4.decode(frags[0].strip())
                for uid, (_, _, branch, blocked) in units.items():
                    key = key0 + (uid,)
                    branches[branch] += 1
                    per_troll_turns[key] += 1
                    if branch in ("H", "W"):
                        per_troll[key] += 1
                    if branch == "H" and blocked > longest:
                        longest, longest_where = blocked, key
    turns = sum(branches.values())
    if not turns:
        raise SystemExit(f"{path}: no v4 telemetry on the wire -- this arm cannot be measured")
    shares = {k: 100.0 * per_troll[k] / per_troll_turns[k] for k in per_troll_turns}
    worst = max(shares, key=lambda k: (shares[k], k))
    above = sorted(k for k in shares if shares[k] > LINE)
    return {
        "games_archive": str(path),
        "branches": dict(branches),
        "own_troll_turns": turns,
        "idle_with_work_turns": branches["H"] + branches["W"],
        "idle_with_work_share_pct": round(100.0 * (branches["H"] + branches["W"]) / turns, 4),
        "hold_share_pct": round(100.0 * branches["H"] / turns, 4),
        "wait_share_pct": round(100.0 * branches["W"] / turns, 4),
        "trolls": len(per_troll_turns),
        "worst_troll": {"map_id": worst[0], "seat": worst[1], "unit": worst[2],
                        "share_pct": round(shares[worst], 4),
                        "idle_turns": per_troll[worst], "turns": per_troll_turns[worst]},
        "trolls_above_the_line": [{"map_id": k[0], "seat": k[1], "unit": k[2],
                                   "share_pct": round(shares[k], 4)} for k in above],
        "trolls_above_the_line_count": len(above),
        "longest_consecutive_hold_run": longest,
        "longest_consecutive_hold_run_where": (
            {"map_id": longest_where[0], "seat": longest_where[1], "unit": longest_where[2]}
            if longest_where else None),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--arm", action="append", default=[],
                    help="LABEL=<games.jsonl.gz>; repeatable. Defaults to base + candidate.")
    ap.add_argument("--json", default=str(OUT))
    args = ap.parse_args(argv)
    arms = dict(a.split("=", 1) for a in args.arm) if args.arm else DEFAULT_ARMS

    report = {
        "clause": "R-C / disposition 4b -- per-troll idle-with-work share (H + W over own "
                  "troll-turns) <= 1.5 %, the G-1 safety net that replaces the blind P4 clause",
        "ruling": ("coordination/messages/local_claude_1/"
                   "20260825T094200Z-20260825-dance-cure-candidate-1-hold-policy.md"),
        "line_pct": LINE,
        "arms": {},
    }
    for label, path in arms.items():
        report["arms"][label] = census(Path(path))
        row = report["arms"][label]
        print(f"  {label:<28} H+W {row['idle_with_work_share_pct']:>7.4f} %   "
              f"(H {row['hold_share_pct']:.4f} %, W {row['wait_share_pct']:.4f} %)   "
              f"worst troll {row['worst_troll']['share_pct']:.2f} %   "
              f"above the line {row['trolls_above_the_line_count']}/{row['trolls']}   "
              f"longest hold run {row['longest_consecutive_hold_run']}")
    graded = [k for k in report["arms"] if "candidate" in k]
    if graded:
        share = report["arms"][graded[0]]["idle_with_work_share_pct"]
        report["graded_arm"] = graded[0]
        report["graded_share_pct"] = share
        report["verdict"] = "PASS" if share <= LINE else "FAIL"
        print(f"\n  clause: {share} % against the {LINE} % line -> {report['verdict']}")
    Path(args.json).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"  -> {args.json}")
    return 0 if report.get("verdict", "PASS") == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
