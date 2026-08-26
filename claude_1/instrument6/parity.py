#!/usr/bin/env python3
"""0-3a probe parity on the 240-game panel: the arm with `MSG` stripped IS the champion.

Task `20260826-champion-instrument-v6`. The gate the card names is *parity in play*: strip the
`MSG` fragment from the arm's command stream and what is left must be byte-for-byte the
champion's own stream on the same game.

The panel already ran this arm's exact bytes -- `claude_1/cure3/arm-ruleoff.rs`, sha256
`0f75e7d6…`, which `make_champion_v6.py` regenerates and re-checks -- against the ladder
champion `547fa706…` in the parent seat, 240 games, and kept BOTH command streams per game.
This reads that archive at **command-stream level**. `panel_read.py` compared the two seats'
SCORES; equal scores are not parity, because two different streams can score the same. Nothing
here is taken from that earlier read.

Three things are checked per game and any one of them failing fails the gate:

  * the arm's stream with `MSG` removed == the parent's stream, byte for byte;
  * the opponent's stream is the same in both runs (a divergence there means the two runs did
    not face the same world, and the first check would then be comparing nothing);
  * the arm's `MSG` payloads decode under `narrate6` with zero errors, rule-off census.

    python3 claude_1/instrument6/parity.py [--games <games.jsonl.gz>]
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "narrate6"))
import narrate6 as n6  # noqa: E402

DEFAULT_GAMES = Path("/tmp/claude-1000/cure3/ruleoff/games/games.jsonl.gz")
ARM_SHA = "0f75e7d61c71d4881502aac2204faf6fb5035331857a9f400ea2647bccd94141"
ANNOUNCEMENT = "yamo-carry-regen-transit-idle-harvest-rust"
CHAMPION_MIN_SHA = "547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0"


def lines_of(blob: str) -> list[str]:
    return blob.rstrip("\n").split("\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--games", type=Path, default=DEFAULT_GAMES)
    ap.add_argument("--out", type=Path, default=HERE / "results" / "parity-panel.json")
    args = ap.parse_args()
    if not args.games.exists():
        print(f"REFUSED: no panel archive at {args.games}", file=sys.stderr)
        return 2

    rows, census = [], n6.new_census()
    errors, msg_lines_total = [], 0
    with gzip.open(args.games, "rt") as fh:
        for raw in fh:
            row = json.loads(raw)
            key = f"{row['map_id']}:{row['seat']}"
            arm = lines_of(row["artifacts"]["candidate_commands"])
            parent = lines_of(row["artifacts"]["parent_commands"])
            stripped = [n6.strip_msg(l) for l in arm]
            # The champion is itself an `MSG` speaker: it announces its name on turn 1
            # (`door1-champion.rs:1136`). So BOTH sides are stripped -- `MSG` is not play on
            # either seat -- and the arm's preservation of that announcement is checked
            # separately below rather than smuggled into the parity number.
            champion = [n6.strip_msg(l) for l in parent]
            identical = stripped == champion
            first = None
            if not identical:
                for i, (a, b) in enumerate(zip(champion, stripped), 1):
                    if a != b:
                        first = {"turn": i, "champion": a, "arm_stripped": b}
                        break
                if first is None:
                    first = {"turn": None, "champion_turns": len(champion),
                             "arm_turns": len(stripped)}
            same_world = (row["artifacts"]["candidate_opponent_commands"]
                          == row["artifacts"]["parent_opponent_commands"])
            errs = n6.check_telemetry(key, None, arm, census, rule_off=True)
            errors.extend(f"{key}: {e}" for e in errs[:3])
            msg = sum(1 for l in arm if n6.msg_fragments(l))
            msg_lines_total += msg
            # The champion's own announcement must survive: the arena and the collector know
            # this bot by that string, and an instrument that silently renames the bot would
            # break attribution of the very games it exists to record.
            announced = [l for l in arm if ANNOUNCEMENT in l]
            widest = max(len(l) for l in arm)
            widest_champion = max(len(l) for l in parent)
            rows.append({
                "game": key, "turns": len(arm), "msg_lines": msg,
                "byte_identical_without_msg": identical,
                "same_opponent_stream": same_world,
                "telemetry_errors": len(errs),
                "arm_score": row["candidate"]["score"],
                "champion_score": row["parent"]["score"],
                "announcement_lines": len(announced),
                "widest_command_line": widest,
                "widest_champion_command_line": widest_champion,
                "first_divergence": first,
            })

    parity = sum(1 for r in rows if r["byte_identical_without_msg"])
    worlds = sum(1 for r in rows if r["same_opponent_stream"])
    score_diff = [r["game"] for r in rows if r["arm_score"] != r["champion_score"]]
    announced_ok = all(r["announcement_lines"] == 1 for r in rows)
    ok = (parity == worlds == len(rows) and not errors and not score_diff and announced_ok)
    report = {
        "gate": "0-3a probe parity, 240-game panel, command-stream level",
        "task": "20260826-champion-instrument-v6",
        "archive": str(args.games),
        "arm_sha256": ARM_SHA,
        "champion_sha256": CHAMPION_MIN_SHA,
        "games": len(rows),
        "byte_identical_without_msg": parity,
        "same_opponent_stream": worlds,
        "games_score_differ": len(score_diff),
        "games_announcing_champion_name_once": sum(1 for r in rows
                                                   if r["announcement_lines"] == 1),
        "widest_command_line": max(r["widest_command_line"] for r in rows),
        "widest_champion_command_line": max(r["widest_champion_command_line"]
                                            for r in rows),
        "games_score_differ_named": score_diff[:20],
        "arm_score_total": sum(r["arm_score"] for r in rows),
        "champion_score_total": sum(r["champion_score"] for r in rows),
        "msg_lines_decoded": msg_lines_total,
        "telemetry_error_count": len(errors),
        "telemetry_errors": errors[:100],
        "census": census,
        "status": "PASS" if ok else "FAIL",
        "rows": sorted(rows, key=lambda r: r["game"]),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"  {report['status']}  {parity}/{len(rows)} byte-identical without MSG, "
          f"{worlds}/{len(rows)} same opponent stream, "
          f"{msg_lines_total} MSG lines decoded, {len(errors)} decode errors")
    print(f"  arm total {report['arm_score_total']}  champion total "
          f"{report['champion_score_total']}  -> {args.out}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
