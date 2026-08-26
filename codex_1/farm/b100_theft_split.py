#!/usr/bin/env python3
"""Report the attributable processed fields for Track F-1's b100 games."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

AGENT_ID = 6590083
CORPUS_SHA256 = "150a5507e90c2c00a5d22b34abf19b7a0ad933fc3b31e3abf3521d3bc4dc4d24"
CHECKPOINT = Path(
    "data/analysis/live-agent-6553250/"
    "owner-banana-factory-b100-reconvergence-checkpoint-20260802T162907Z.json"
)


def banana_harvested(pp: dict) -> int:
    values = pp.get("harvested") or {}
    return values.get("BANANA", 0) + values.get("BANANAs", 0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, default=Path("data/processed/games.jsonl"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    digest = hashlib.sha256(args.corpus.read_bytes()).hexdigest()
    if digest != CORPUS_SHA256:
        raise SystemExit(f"corpus hash mismatch: {digest}")
    rows = []
    with args.corpus.open() as source:
        for line in source:
            game = json.loads(line)
            seats = [p["index"] for p in game["players"] if p["agentId"] == AGENT_ID]
            if not seats:
                continue
            seat = seats[0]
            opp = 1 - seat
            own_pp = game["per_player"][str(seat)]
            opp_pp = game["per_player"][str(opp)]
            rows.append({
                "game": game["gameId"], "seat": seat,
                "opponent": game["players"][opp]["name"],
                "opponent_agent": game["players"][opp]["agentId"],
                "own_score": game["scores"][seat], "opponent_score": game["scores"][opp],
                "own_banana_plants": (own_pp.get("planted_ok") or {}).get("BANANA", 0),
                "own_banana_harvest_units": banana_harvested(own_pp),
                "opponent_banana_plants": (opp_pp.get("planted_ok") or {}).get("BANANA", 0),
                "opponent_banana_harvest_units": banana_harvested(opp_pp),
            })
    if len(rows) != 4:
        raise SystemExit(f"expected 4 b100 games, found {len(rows)}")
    checkpoint = json.loads(CHECKPOINT.read_text())
    summary = checkpoint["summary"]
    margins = [row["margin"] for row in checkpoint["rows"]]
    if checkpoint["agent_id"] != AGENT_ID or summary["games"] != len(margins):
        raise SystemExit("b100 checkpoint identity or game count mismatch")
    lines = [
        "# Track F read 1 — b100 theft split stops at the attribution gate", "",
        "- Date: 2026-08-26",
        f"- Corpus: `{args.corpus}` — **23,613 games**, SHA-256 `{CORPUS_SHA256}`",
        "- Reproduce: `python3 codex_1/farm/b100_theft_split.py --output "
        "codex_1/farm/b100-theft-split-2026-08-26.md`", "",
        "## Verdict: DEAD CONDITION MET", "",
        "The b100 played 98 recorded ladder games. This corpus holds four of them, all from its "
        "first batch, and the table below covers only those four. The processed rows do not contain tree-generation "
        "identity, per-turn cargo changes, or per-turn commands. They cannot distinguish bananas "
        "harvested from our trees from bananas harvested from starting or opponent-planted trees. "
        "They also cannot reconstruct the five-turn abort sensor. The card says to stop in exactly "
        "this case, report what remains attributable, and not design a farm.", "",
        "| game | seat | opponent | opponent id | final score us–them | our banana plants | our banana harvest units | their banana plants | their banana harvest units |",
        "|---:|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['game']} | {row['seat']} | {row['opponent']} | {row['opponent_agent']} | "
            f"{row['own_score']:.0f}–{row['opponent_score']:.0f} | {row['own_banana_plants']} | "
            f"{row['own_banana_harvest_units']} | {row['opponent_banana_plants']} | "
            f"{row['opponent_banana_harvest_units']} |"
        )
    lines.extend([
        "", "## Full recorded ladder run", "",
        f"The permitted checkpoint `{CHECKPOINT}` records **{summary['games']} games**, a mean "
        f"margin of **{summary['mean_margin']:+.1f}**, **{summary['losses']} losses**, and a worst "
        f"game of **{min(margins):.0f}**. These are outcome counts, not harvest attribution; the "
        "four-game corpus slice cannot represent the shape of the full ladder run.",
    ])
    lines.extend(["", "## What is not attributable", "",
                  "The requested theft-versus-own-crop split and abort time are not identifiable "
                  "from these aggregates. Treating an opponent's total banana harvest as their "
                  "own crop would be wrong because each map begins with banana trees and either "
                  "player can harvest either side's trees. No point-value or farm go/no-go claim "
                  "is made from this file.", ""])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
