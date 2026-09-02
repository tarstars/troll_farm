#!/usr/bin/env python3
"""The field reading for rung 1: the candidate and the champion against the same local field.

Plain words for the owner
-------------------------
Rung 1 of the port's selector (`coordination/tasks/20260902-norxondor-port.md`, ruling of
2026-09-02 08:4xZ) is not a duel. The candidate and the champion of record are each played by
`h2h.py` against the same opponents on the same panel, and the question is the paired difference
(candidate minus champion) against each opponent on each map and seat. This script reads those
result files, pairs them cell by cell, and prints one line per opponent and one line for the field.

For each opponent you give a pair of `h2h.py` result files: the candidate's run against that
opponent and the champion's run against the same opponent. The two files must have been played
on the same panel (the panel sha must match), against the same opponent file (the bot sha must
match), and over the same cells (map, seat). The script refuses anything else, because a pair
that differs in any of those is not a paired reading.

Per cell (opponent, map, seat), two differences: the win indicator (candidate's strict win minus
the champion's) and the score margin (candidate's own score minus the opponent's, minus the same
for the champion). Per opponent the cells of one map are averaged over the seats, and the
interval is the gates' clustered bootstrap over maps (`gate1.clustered_bootstrap`, 10,000 draws,
seed 1). The **field** line does the same with every opponent's cells pooled: per map the mean
over all (opponent, seat) cells, then the bootstrap over maps, so a map's cells against every
opponent travel together in every draw.

The bar to rung 2 as ruled: the field-mean interval above zero. Both statistics are printed; the
**win indicator** is the one the verdict line reads (ruling 2026-09-02 09:23Z: the ladder's rating is
computed from wins and losses, a margin is a size the ladder never sees), and the margin reading stands
beside it on every line as the finer instrument that explains a straddle.
Execution faults in any file are reported and make the reading `clean: false`; the verdict is then
`INCONCLUSIVE`, as in the gates.

Use
---
    python3 claude_1/h2h-panel/field.py \\
        --opponent champion=results/port-vs-champion.json,results/champion-vs-champion.json \\
        --opponent orchard6=results/port-vs-orchard6.json,results/champion-vs-orchard6.json \\
        --expected-cells 400 --json-out results/port-field.json

Each `--opponent` is `<name>=<candidate-run.json>,<champion-run.json>`.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "local_claude_1" / "nn-bot"))

import gate1  # noqa: E402

BOOTSTRAP_DRAWS = 10000
BOOTSTRAP_SEED = 1

ABOVE = "FIELD_ABOVE_ZERO"
BELOW = "FIELD_BELOW_ZERO"
STRADDLES = "FIELD_STRADDLES_ZERO"
INCONCLUSIVE = "INCONCLUSIVE"

DECISION_RULE = (
    "FIELD_ABOVE_ZERO = the field-mean WIN-INDICATOR difference's 95 % interval wholly above zero "
    "(the bar to rung 2; ruling 2026-09-02 09:23Z); FIELD_BELOW_ZERO = wholly below; "
    "FIELD_STRADDLES_ZERO = contains zero (rung 2 decides); INCONCLUSIVE = a fault in any run, or "
    "an incomplete pairing. The margin difference is printed beside it and does not decide."
)


class Pair:
    """One opponent: the candidate's run and the champion's run against it, paired by cell."""

    def __init__(self, name: str, candidate: Path, champion: Path, expected_cells: int) -> None:
        self.name = name
        self.candidate = gate1.Bench(candidate)
        self.champion = gate1.Bench(champion)
        c, k = self.candidate.payload, self.champion.payload
        problems = []
        if c.get("panel_sha256") != k.get("panel_sha256"):
            problems.append(f"panel differs: {c.get('panel_sha256')} vs {k.get('panel_sha256')}")
        if c.get("bot_sha256") != k.get("bot_sha256"):
            problems.append(f"opponent differs: {c.get('bot_sha256')} vs {k.get('bot_sha256')}")
        if set(self.candidate.cells) != set(self.champion.cells):
            only_c = len(set(self.candidate.cells) - set(self.champion.cells))
            only_k = len(set(self.champion.cells) - set(self.candidate.cells))
            problems.append(f"cells differ: {only_c} only in the candidate's run, {only_k} only in the champion's")
        if expected_cells and len(self.candidate.cells) != expected_cells:
            problems.append(f"expected {expected_cells} cells, the candidate's run has {len(self.candidate.cells)}")
        if problems:
            raise ValueError(f"opponent {name!r}: " + "; ".join(problems))
        # the candidate run's row order, so a reading against a zero champion run reproduces
        # h2h.py's own paired reading draw for draw (the bootstrap resamples in list order)
        self.cells = list(self.candidate.cells)
        self.faults = {
            "candidate": self.candidate.execution_faults(),
            "champion": self.champion.execution_faults(),
        }

    def diff_win(self, key) -> float:
        return float(self.candidate.won(key) - self.champion.won(key))

    def diff_margin(self, key) -> float:
        return self.candidate.margin(key) - self.champion.margin(key)

    @property
    def clean(self) -> bool:
        return not self.faults["candidate"] and not self.faults["champion"]


def per_map(values_by_cell: dict[tuple[str, int], float]) -> dict[str, float]:
    """Average a per-cell quantity over the cells of each map (the cluster the bootstrap draws)."""
    by_map: dict[str, list[float]] = {}
    for (map_hash, _seat), value in values_by_cell.items():
        by_map.setdefault(map_hash, []).append(value)
    return {m: sum(v) / len(v) for m, v in by_map.items()}


def reading(values_by_cell: dict, draws: int, seed: int) -> dict[str, Any]:
    maps = per_map(values_by_cell)
    point, lo, hi = gate1.clustered_bootstrap(maps, draws, seed)
    return {
        "mean": round(point, 4),
        "interval_95": [round(lo, 4), round(hi, 4)],
        "above_zero": bool(lo > 0),
        "below_zero": bool(hi < 0),
        "maps": len(maps),
        "cells": len(values_by_cell),
    }


def compute(pairs: list[Pair], *, draws: int = BOOTSTRAP_DRAWS, seed: int = BOOTSTRAP_SEED) -> dict[str, Any]:
    if not pairs:
        raise ValueError("no opponents given")
    names = [p.name for p in pairs]
    if len(set(names)) != len(names):
        raise ValueError(f"opponent names repeat: {names}")
    field_win: dict[tuple[str, int], float] = {}
    field_margin: dict[tuple[str, int], float] = {}
    opponents = []
    for p in pairs:
        win = {key: p.diff_win(key) for key in p.cells}
        margin = {key: p.diff_margin(key) for key in p.cells}
        for key in p.cells:
            # the field's cell is (map, "opponent/seat"): one map keeps every opponent's seats
            field_win[(key[0], f"{p.name}/{key[1]}")] = win[key]
            field_margin[(key[0], f"{p.name}/{key[1]}")] = margin[key]
        opponents.append({
            "opponent": p.name,
            "opponent_sha256": p.candidate.payload.get("bot_sha256"),
            "candidate_run": str(p.candidate.path),
            "champion_run": str(p.champion.path),
            "candidate_sha256": p.candidate.payload.get("policy_sha256"),
            "champion_sha256": p.champion.payload.get("policy_sha256"),
            "candidate_wins": sum(p.candidate.won(k) for k in p.cells),
            "champion_wins": sum(p.champion.won(k) for k in p.cells),
            "win_diff": reading(win, draws, seed),
            "margin_diff": reading(margin, draws, seed),
            "faults": p.faults,
            "clean": p.clean,
        })
    field = {
        "opponents": names,
        "win_diff": reading(field_win, draws, seed),
        "margin_diff": reading(field_margin, draws, seed),
    }
    clean = all(o["clean"] for o in opponents)
    panel_sha = pairs[0].candidate.payload.get("panel_sha256")
    candidate_shas = {o["candidate_sha256"] for o in opponents}
    champion_shas = {o["champion_sha256"] for o in opponents}
    problems = []
    if not clean:
        problems.append("execution faults in at least one run")
    if any(p.candidate.payload.get("panel_sha256") != panel_sha for p in pairs):
        problems.append("the opponents were not all played on the same panel")
    if len(candidate_shas) != 1:
        problems.append(f"the candidate is not one file across the opponents: {sorted(candidate_shas)}")
    if len(champion_shas) != 1:
        problems.append(f"the champion is not one file across the opponents: {sorted(champion_shas)}")
    if problems:
        verdict = INCONCLUSIVE
    elif field["win_diff"]["above_zero"]:      # the verdict reads the win indicator (ruling 09-02 09:23Z)
        verdict = ABOVE
    elif field["win_diff"]["below_zero"]:
        verdict = BELOW
    else:
        verdict = STRADDLES
    return {
        "instrument": "field.py -- rung 1 of the port's selector: candidate minus champion against the same local field, paired by (opponent, map, seat), clustered bootstrap over maps",
        "unit": "map (every opponent's seats of one map carried together)",
        "panel_sha256": panel_sha,
        "candidate_sha256": sorted(candidate_shas)[0] if len(candidate_shas) == 1 else sorted(candidate_shas),
        "champion_sha256": sorted(champion_shas)[0] if len(champion_shas) == 1 else sorted(champion_shas),
        "per_opponent": opponents,
        "field": field,
        "clean": clean,
        "problems": problems,
        "decision_rule": DECISION_RULE,
        "verdict": verdict,
        "bootstrap": {"draws": draws, "seed": seed},
    }


def fmt_line(name: str, win: dict, margin: dict, extra: str = "") -> str:
    w = win["interval_95"]
    m = margin["interval_95"]
    return (f"{name:<12} maps {win['maps']:>4} cells {win['cells']:>5}  "
            f"Δwin {win['mean']:+.4f} [{w[0]:+.4f}, {w[1]:+.4f}]  "
            f"Δmargin {margin['mean']:+.2f} [{m[0]:+.2f}, {m[1]:+.2f}]{extra}")


def render(report: dict) -> str:
    lines = []
    for o in report["per_opponent"]:
        faults = "" if o["clean"] else f"  FAULTS {o['faults']}"
        lines.append(fmt_line(o["opponent"], o["win_diff"], o["margin_diff"],
                              f"  wins {o['candidate_wins']} vs {o['champion_wins']}{faults}"))
    lines.append(fmt_line("FIELD", report["field"]["win_diff"], report["field"]["margin_diff"]))
    for p in report["problems"]:
        lines.append(f"problem: {p}")
    lines.append(f"VERDICT: {report['verdict']}")
    return "\n".join(lines)


def parse_opponent(item: str, expected_cells: int) -> Pair:
    if "=" not in item or "," not in item.split("=", 1)[1]:
        raise SystemExit(f"expected <name>=<candidate-run.json>,<champion-run.json>, got {item!r}")
    name, files = item.split("=", 1)
    cand, champ = files.split(",", 1)
    return Pair(name.strip(), Path(cand.strip()), Path(champ.strip()), expected_cells)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--opponent", action="append", required=True,
                        help="<name>=<candidate-run.json>,<champion-run.json>, repeatable")
    parser.add_argument("--expected-cells", type=int, default=400,
                        help="cells per opponent run (200 maps x 2 seats); 0 to skip the check")
    parser.add_argument("--bootstrap", type=int, default=BOOTSTRAP_DRAWS)
    parser.add_argument("--seed", type=int, default=BOOTSTRAP_SEED)
    parser.add_argument("--json-out", default=None)
    args = parser.parse_args()
    try:
        pairs = [parse_opponent(item, args.expected_cells) for item in args.opponent]
        report = compute(pairs, draws=args.bootstrap, seed=args.seed)
    except ValueError as e:
        raise SystemExit(f"field.py: {e}")
    print(render(report))
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(report, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
