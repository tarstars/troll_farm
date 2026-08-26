#!/usr/bin/env python3
"""Control C-1, panel half — the rule-off arm against the champion on all 240 panel games.

Parity is codex_1's definition 4: exact ordered gameplay-token equality after stripping the single
`MSG` fragment. The panel records BOTH streams for every game (`candidate_commands` and
`parent_commands` come from the same map, seat, seeds and opponent), so the comparison needs no
re-run and no second referee.

    python3 claude_1/cure2/panel_parity.py <arm> [games.jsonl.gz]

With `--expect-divergence` (the instrument/candidate arms) the divergent games are NAMED with
their first divergence rather than failing the gate — that is control C-15's input.
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


def main() -> int:
    arm = sys.argv[1] if len(sys.argv) > 1 else "ruleoff"
    expect = "--expect-divergence" in sys.argv
    games_path = Path(f"/tmp/claude-1000/cure2/cure2-{arm}/games/games.jsonl.gz")
    rows, diverging = [], []
    for line in gzip.open(games_path, "rt"):
        game = json.loads(line)
        key = f"{game['map_id']}:{game.get('seat', '?')}"
        arm_lines = [n5.strip_msg(l) for l in
                     game["artifacts"]["candidate_commands"].rstrip("\n").split("\n")]
        base_lines = [n5.strip_msg(l) for l in
                      game["artifacts"]["parent_commands"].rstrip("\n").split("\n")]
        identical = arm_lines == base_lines
        first = None
        if not identical:
            for i, (a, b) in enumerate(zip(base_lines, arm_lines), 1):
                if a != b:
                    first = {"turn": i, "base": a, "arm": b}
                    break
            if first is None:
                first = {"turn": None, "base_turns": len(base_lines), "arm_turns": len(arm_lines)}
            diverging.append({"game": key, "class": game["class"],
                              "score_delta": game["candidate"]["score"] - game["parent"]["score"],
                              "first_divergence": first})
        rows.append({"game": key, "identical": identical})
    ok = len(diverging) == 0
    report = {
        "control": "C-1 panel half — rule-off vs champion, MSG stripped",
        "arm": arm, "games": len(rows),
        "byte_identical_without_msg": sum(1 for r in rows if r["identical"]),
        "diverging_games": len(diverging),
        "verdict": ("PASS" if ok else ("NAMED" if expect else "FAIL")),
        "divergences": diverging[:60],
    }
    out = HERE / "results" / f"panel-parity-{arm}.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"  {arm}: {report['byte_identical_without_msg']}/{len(rows)} byte-identical without "
          f"MSG, {len(diverging)} diverging -> {report['verdict']}")
    for row in diverging[:10]:
        print(f"    {row['game']:<12} first divergence turn "
              f"{row['first_divergence'].get('turn')}  delta {row['score_delta']:+}")
    print(f"  -> {out.relative_to(REPO)}")
    return 0 if (ok or expect) else 1


if __name__ == "__main__":
    sys.exit(main())
