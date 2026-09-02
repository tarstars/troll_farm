#!/usr/bin/env python3
"""Training-side read of the entropy arms (E00 = entropy off, E01 = entropy on).

This reads the two runs' salvaged training logs and compares them over the update
range they SHARE.  It is deliberately *not* the gate: `win_rate` here is measured on
the training distribution with sampled actions against the training opponent, while
the gate is argmax decoding on the locked panel.  Every earlier attempt to read a
verdict off training win-rate has been optimistic (run I logged 18-21 % while it
benched 4/48).  So this script reports the training-side signal, labelled as such,
with an honest interval that accounts for the fact that consecutive updates share
a rolling window of episodes.

Interval method: non-overlapping blocks of `--block` updates are the resampling
unit (a block is wider than the rolling episode window, so blocks are close to
independent even though neighbouring updates are not).  We bootstrap the paired
per-block difference E01 - E00 over the common range.
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import random
import statistics
from typing import Any

FIELDS = [
    "win_rate",
    "mean_referee_margin",
    "mean_episode_return",
    "entropy",
    "anchor_agreement",
    "explained_variance",
    "approx_kl",
    "clip_fraction",
    "value_loss",
    "mean_episode_turns",
]


def load(path: pathlib.Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Return (config, per-update records sorted by update)."""
    config: dict[str, Any] = {}
    rows: list[dict[str, Any]] = []
    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "update" in record and "win_rate" in record:
                rows.append(record)
            elif not config:
                config = record
    rows.sort(key=lambda r: r["update"])
    return config, rows


def blocks(rows: list[dict[str, Any]], field: str, size: int) -> dict[int, float]:
    """Mean of `field` per non-overlapping block of `size` updates, keyed by block index."""
    acc: dict[int, list[float]] = {}
    for record in rows:
        value = record.get(field)
        if value is None or (isinstance(value, float) and math.isnan(value)):
            continue
        acc.setdefault(int(record["update"]) // size, []).append(float(value))
    return {k: statistics.fmean(v) for k, v in acc.items() if v}


def paired_bootstrap(deltas: list[float], draws: int, seed: int) -> tuple[float, float, float]:
    """Mean delta and a percentile interval, resampling whole blocks."""
    if not deltas:
        return float("nan"), float("nan"), float("nan")
    rng = random.Random(seed)
    point = statistics.fmean(deltas)
    means = []
    n = len(deltas)
    for _ in range(draws):
        means.append(statistics.fmean([deltas[rng.randrange(n)] for _ in range(n)]))
    means.sort()
    lo = means[int(0.025 * draws)]
    hi = means[min(int(0.975 * draws), draws - 1)]
    return point, lo, hi


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--off-log", required=True, help="training log of the entropy-off arm")
    parser.add_argument("--on-log", required=True, help="training log of the entropy-on arm")
    parser.add_argument("--block", type=int, default=250, help="updates per resampling block")
    parser.add_argument("--bootstrap", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--json-out", default=None)
    args = parser.parse_args()

    off_config, off_rows = load(pathlib.Path(args.off_log))
    on_config, on_rows = load(pathlib.Path(args.on_log))

    report: dict[str, Any] = {
        "off": {
            "entropy_coef": off_config.get("entropy_coef"),
            "seed": off_config.get("seed"),
            "updates": off_rows[-1]["update"] if off_rows else 0,
            "wall_hours": round((off_rows[-1].get("wall_seconds") or 0) / 3600, 2) if off_rows else 0,
        },
        "on": {
            "entropy_coef": on_config.get("entropy_coef"),
            "seed": on_config.get("seed"),
            "updates": on_rows[-1]["update"] if on_rows else 0,
            "wall_hours": round((on_rows[-1].get("wall_seconds") or 0) / 3600, 2) if on_rows else 0,
        },
        "block": args.block,
    }

    common_last = min(report["off"]["updates"], report["on"]["updates"])
    report["common_updates"] = common_last
    report["fields"] = {}

    for field in FIELDS:
        off_blocks = blocks([r for r in off_rows if r["update"] <= common_last], field, args.block)
        on_blocks = blocks([r for r in on_rows if r["update"] <= common_last], field, args.block)
        shared = sorted(set(off_blocks) & set(on_blocks))
        deltas = [on_blocks[b] - off_blocks[b] for b in shared]
        point, lo, hi = paired_bootstrap(deltas, args.bootstrap, args.seed)
        report["fields"][field] = {
            "off_mean": round(statistics.fmean([off_blocks[b] for b in shared]), 6) if shared else None,
            "on_mean": round(statistics.fmean([on_blocks[b] for b in shared]), 6) if shared else None,
            "delta_on_minus_off": round(point, 6),
            "ci95": [round(lo, 6), round(hi, 6)],
            "blocks": len(shared),
            "crosses_zero": bool(lo <= 0.0 <= hi),
        }

    # the trajectory, so a trend that reverses is visible rather than averaged away
    report["trajectory"] = []
    for edge in (500, 1000, 1500, 2000, 2500, 3000, 5000, 8000, 12000):
        if edge > max(report["off"]["updates"], report["on"]["updates"]):
            continue
        entry: dict[str, Any] = {"update": edge}
        for label, rows in (("off", off_rows), ("on", on_rows)):
            window = [r for r in rows if edge - args.block < r["update"] <= edge]
            if window:

                def mean_of(name: str, digits: int = 4) -> float | None:
                    values = [
                        float(r[name])
                        for r in window
                        if r.get(name) is not None and not math.isnan(float(r[name]))
                    ]
                    return round(statistics.fmean(values), digits) if values else None

                entry[label] = {
                    "win_rate": mean_of("win_rate"),
                    "margin": mean_of("mean_referee_margin", 3),
                    "entropy": mean_of("entropy"),
                    "anchor_agreement": mean_of("anchor_agreement"),
                    "explained_variance": mean_of("explained_variance"),
                }
        report["trajectory"].append(entry)

    text = json.dumps(report, indent=2)
    print(text)
    if args.json_out:
        pathlib.Path(args.json_out).write_text(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
