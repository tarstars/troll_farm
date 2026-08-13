#!/usr/bin/env python3
"""Read-only audit: how strongly does the resident's denial bonus steer chopping?

Answers an owner question of 2026-08-07 — "we choose one of lemon or plum and
concentrate on chopping it out, is that correct?" — by pricing the two terms of
the resident's chop score against each other.

`MoisanBot::chop_candidates` (`rust/src/bin/yamo_orchard_live.rs:1101-1105`)
scores every reachable tree as

    score = 1000 * wood / turns
    if kind == type_to_cut and opponent_trolls <= 2:
        score += 900 / (1 + manhattan(tree, opponent_shack))

where `wood = min(size_at_death, free_capacity)` and
`turns = travel + chop + return + 1`. `type_to_cut` is one species, picked once
by `focus_type` as whichever of LEMON/PLUM has the smaller summed BFS distance
from OUR shack, and then frozen for the game.

Because `wood` is capped by carry capacity and `chop` scales with chop power,
the base term differs by roughly 8x between the starter (1/1/1) and a trained
worker (3/3/3) — while the denial bonus is identical for both. The audit
reports the resulting crossover distance per worker class.

This module computes only; it never edits the byte-sacred source, touches the
corpus, or proposes a bot change. Constants are re-read from the Rust on every
run (`source_constants`) so the model cannot silently drift from what it claims
to describe.

Usage:
    python3 cgauto/analyze_resident_denial_scoring.py            # table
    python3 cgauto/analyze_resident_denial_scoring.py --json     # machine form
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT / "rust" / "src" / "bin" / "yamo_orchard_live.rs"

DENIAL_BONUS_NUMERATOR = 900.0
BASE_SCORE_NUMERATOR = 1000.0
DENIAL_GATE_MAX_OPPONENT_TROLLS = 2
PLUM_LEMON_HEALTH_BASE = 4
PLUM_LEMON_HEALTH_SLOPE = 2

# (movement_speed, carry_capacity, chop_power); harvest_power is irrelevant here.
STARTER = (1, 1, 1)
TRAINED = (3, 3, 3)
WORKER_CLASSES = {"starter": STARTER, "trained": TRAINED}


def source_constants(source: pathlib.Path = DEFAULT_SOURCE) -> dict:
    """Re-read the scoring constants out of the Rust source (drift guard)."""
    text = source.read_text(encoding="utf-8")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()

    def require(pattern: str, label: str) -> str:
        match = re.search(pattern, text)
        if not match:
            raise ValueError(f"{label} not found in {source}; the model has drifted")
        return match.group(1)

    return {
        "source_sha256": digest,
        "denial_bonus_numerator": float(
            require(r"score \+= ([0-9.]+) / \(1 \+ opponent_distance\)", "denial bonus")
        ),
        "base_score_numerator": float(
            require(r"let mut score = ([0-9.]+) \* wood as f64 / turns as f64", "base score")
        ),
        "denial_gate_max_opponent_trolls": int(
            require(r"opponent_trolls <= (\d+)", "denial gate")
        ),
        "plum_lemon_health_base": int(
            require(r"PlantKind::Plum \| PlantKind::Lemon => \((\d+), \d+\)", "health base")
        ),
        "plum_lemon_health_slope": int(
            require(r"PlantKind::Plum \| PlantKind::Lemon => \(\d+, (\d+)\)", "health slope")
        ),
    }


def ceil_div(a: int, b: int) -> int:
    """Mirrors `MoisanBot::ceil_div`, including its non-positive-divisor guard."""
    return 10_000 if b <= 0 else -(-a // b)


def tree_health(size: int) -> int:
    """PLUM/LEMON only: `health = base + slope * size` (4, 2)."""
    return PLUM_LEMON_HEALTH_BASE + PLUM_LEMON_HEALTH_SLOPE * size


def denial_bonus(distance: int, opponent_trolls: int = 0) -> float:
    """`900 / (1 + manhattan)`, and exactly zero once they hold three trolls."""
    if opponent_trolls > DENIAL_GATE_MAX_OPPONENT_TROLLS:
        return 0.0
    return DENIAL_BONUS_NUMERATOR / (1 + distance)


def evaluate(worker: tuple[int, int, int], size: int, dist_unit: int,
             dist_shack: int) -> dict:
    """Base-score terms for one tree, ignoring regrowth during the approach."""
    movement_speed, carry_capacity, chop_power = worker
    chop = ceil_div(tree_health(size), chop_power)
    travel = ceil_div(dist_unit, movement_speed)
    home = ceil_div(dist_shack, movement_speed)
    turns = max(1, travel + chop + home + 1)
    wood = min(size, carry_capacity)
    return {
        "chop_turns": chop,
        "travel_turns": travel,
        "return_turns": home,
        "turns": turns,
        "wood": wood,
        "base_score": BASE_SCORE_NUMERATOR * wood / turns,
    }


def crossover_distance(worker: tuple[int, int, int], size: int, dist_unit: int = 6,
                       dist_shack: int = 6, max_distance: int = 60) -> int:
    """Largest distance at which the denial bonus still outweighs the base score.

    Zero means the bonus never dominates for this worker class.
    """
    base = evaluate(worker, size, dist_unit, dist_shack)["base_score"]
    dominating = [d for d in range(max_distance + 1) if denial_bonus(d) > base]
    return max(dominating) if dominating else 0


def build_report(dist_unit: int = 6, dist_shack: int = 6,
                 source: pathlib.Path = DEFAULT_SOURCE) -> dict:
    constants = source_constants(source)
    sample_distances = [1, 5, 10, 20, 30]
    rows = []
    for name, worker in WORKER_CLASSES.items():
        for size in (1, 2, 3, 4):
            row = evaluate(worker, size, dist_unit, dist_shack)
            row.update(
                worker=name,
                stats=list(worker),
                size=size,
                crossover_distance=crossover_distance(worker, size, dist_unit, dist_shack),
                bonus_ratio={
                    str(d): denial_bonus(d) / row["base_score"] for d in sample_distances
                },
            )
            rows.append(row)
    return {
        "task": "resident denial-scoring audit (owner question 2026-08-07)",
        "geometry": {"dist_unit": dist_unit, "dist_shack": dist_shack},
        "sample_distances": sample_distances,
        "rows": rows,
        **constants,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="emit the report as JSON")
    ap.add_argument("--dist-unit", type=int, default=6, help="worker-to-tree distance")
    ap.add_argument("--dist-shack", type=int, default=6, help="tree-to-our-shack distance")
    args = ap.parse_args()

    report = build_report(args.dist_unit, args.dist_shack)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0

    print(f"resident denial-scoring audit — source {report['source_sha256'][:8]}")
    print(
        f"geometry: tree {args.dist_unit} from worker, {args.dist_shack} from our shack\n"
    )
    header = f"{'worker':<9}{'size':>5}{'turns':>7}{'wood':>6}{'base':>9}   "
    header += "  ".join(f"d={d:<3}" for d in report["sample_distances"])
    print(header)
    for row in report["rows"]:
        line = (
            f"{row['worker']:<9}{row['size']:>5}{row['turns']:>7}{row['wood']:>6}"
            f"{row['base_score']:>9.1f}   "
        )
        line += "  ".join(
            f"{row['bonus_ratio'][str(d)]:>4.1f}x" for d in report["sample_distances"]
        )
        print(line)
    print()
    for name in WORKER_CLASSES:
        crossovers = [r["crossover_distance"] for r in report["rows"] if r["worker"] == name]
        print(
            f"{name}: denial bonus outweighs wood efficiency out to distance "
            f"{min(crossovers)}–{max(crossovers)}"
        )
    print(
        f"\nbonus is exactly 0 once opponent_trolls > "
        f"{report['denial_gate_max_opponent_trolls']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
