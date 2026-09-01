#!/usr/bin/env python3
"""The frozen Gate 1: does removing the entropy bonus help?

This computes the verdict defined in `coordination/GOAL.md` step 4 — the reviewer's 10:36Z gate
as corrected by its 11:45Z panel note, which is the definition of record. It is written and
tested **before** the arms finish, so the rule cannot be shaped by the numbers it will judge.

The design under test
---------------------
Two arms from the same clone, same seed, same everything, differing in one field:
**E01** is the control (`entropy_coef = 0.01`, the run-I recipe) and **E00** the treatment
(`entropy_coef = 0`). The treatment effect is read as **E00 − E01 on paired cells**.

A *cell* is one map-seat unit: `(map_hash, policy_seat)`. The locked confirmation panel is 72
maps × 2 seats = 144 cells. The two confirmed ages (updates 1,500 and 2,500) are **repeated
measures of those same 144 units**, which is why the interval below resamples units, never rows:
pooling 288 rows would treat one map seen twice as two independent observations and would report
an interval far narrower than the evidence supports.

What is computed
----------------
1. Per cell `c` and age `a`, the paired difference of win indicators
   `delta[c,a] = won(E00, c, a) - won(E01, c, a)` — each in {-1, 0, +1}.
2. Per cell, the mean over the two ages `d[c] = mean_a delta[c,a]`.
3. The interval: a **clustered / repeated-measure bootstrap over the 144 units** — each draw
   resamples whole cells with replacement, carrying both of that cell's ages together — of the
   mean of `d`.
4. The per-age mean effects `mean_c delta[c,a]`, which must each be positive.
5. Clone non-inferiority for the treatment arm: `net cells lost = (cells the clone wins and E00
   loses) - (cells E00 wins and the clone loses)`, which must be at most 6 of 144.

The four frozen outcomes
------------------------
- `ENTROPY_CONFIRMED` — the interval lies wholly above zero, **and** the mean effect is positive
  at each age separately, **and** clone non-inferiority holds.
- `ENTROPY_PARTIAL` — the interval lies wholly above zero, but one of the two secondary
  conditions fails: the effect is not positive at both ages, or non-inferiority fails.
- `ENTROPY_NOT_CONFIRMED` — the interval contains or lies below zero.
- `INCONCLUSIVE` — the identity, population, execution or evaluation evidence is incomplete.
  Underpowered is a verdict, not a licence: too few cells returns INCONCLUSIVE rather than a
  quiet NOT_CONFIRMED.

Where the frozen text is silent, this file makes the reading explicit rather than hiding it: the
text fixes the interval, the per-age positivity, the non-inferiority budget and the four outcome
names, but does not spell out which combination yields PARTIAL rather than CONFIRMED. The mapping
above is the reading applied, it is printed with every verdict as `decision_rule`, and the
reviewer can overturn it without touching any of the arithmetic.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import random
import statistics
from typing import Any

CONFIRMED = "ENTROPY_CONFIRMED"
PARTIAL = "ENTROPY_PARTIAL"
NOT_CONFIRMED = "ENTROPY_NOT_CONFIRMED"
INCONCLUSIVE = "INCONCLUSIVE"

DECISION_RULE = (
    "CONFIRMED = interval wholly above zero AND positive at each age AND clone non-inferiority; "
    "PARTIAL = interval wholly above zero but one secondary condition fails; "
    "NOT_CONFIRMED = interval contains or lies below zero; "
    "INCONCLUSIVE = incomplete identity, population, execution or evaluation evidence."
)


class Bench:
    """One bench result, indexed by cell."""

    def __init__(self, path: pathlib.Path) -> None:
        self.path = path
        payload = json.loads(path.read_text())
        self.payload = payload
        self.cells: dict[tuple[str, int], dict[str, Any]] = {}
        for row in payload.get("rows", []):
            key = (str(row["map_hash"]), int(row["policy_seat"]))
            if key in self.cells:
                raise ValueError(f"{path}: duplicate cell {key}")
            self.cells[key] = row

    @property
    def checkpoint(self) -> str:
        return str(self.payload.get("checkpoint", ""))

    def won(self, key: tuple[str, int]) -> int:
        return 1 if self.cells[key]["policy_won"] else 0

    def margin(self, key: tuple[str, int]) -> float:
        row = self.cells[key]
        return float(row["policy_score"]) - float(row["bot_score"])

    def execution_faults(self) -> dict[str, int]:
        """Anything that means the games were not cleanly played."""
        faults = {
            "illegal_commands": int(self.payload.get("illegal_commands_total", 0) or 0),
            "timeouts": int(self.payload.get("timeouts_total", 0) or 0),
            "referee_errors": int(self.payload.get("referee_errors_total", 0) or 0),
        }
        return {name: count for name, count in faults.items() if count}


def clustered_bootstrap(
    per_cell: dict[tuple[str, int], float], draws: int, seed: int
) -> tuple[float, float, float]:
    """Resample whole cells with replacement; return the mean and a 95 % percentile interval.

    Each cell carries both of its ages, so the repeated measures stay together in every draw.
    """

    values = list(per_cell.values())
    if not values:
        return float("nan"), float("nan"), float("nan")
    point = statistics.fmean(values)
    rng = random.Random(seed)
    n = len(values)
    means = []
    for _ in range(draws):
        means.append(statistics.fmean([values[rng.randrange(n)] for _ in range(n)]))
    means.sort()
    lo = means[int(0.025 * draws)]
    hi = means[min(int(0.975 * draws), draws - 1)]
    return point, lo, hi


def compute(
    treatment: dict[int, Bench],
    control: dict[int, Bench],
    *,
    clone: Bench | None = None,
    expected_cells: int = 144,
    non_inferiority_budget: int = 6,
    draws: int = 10000,
    seed: int = 1,
) -> dict[str, Any]:
    """The frozen gate. `treatment` and `control` map age (update number) -> Bench."""

    report: dict[str, Any] = {
        "decision_rule": DECISION_RULE,
        "expected_cells": expected_cells,
        "non_inferiority_budget": non_inferiority_budget,
        "ages": sorted(set(treatment) | set(control)),
        "inconclusive_reasons": [],
    }
    reasons: list[str] = report["inconclusive_reasons"]

    # --- identity and population evidence ------------------------------------------------
    if set(treatment) != set(control):
        reasons.append(
            f"the arms were benched at different ages: treatment {sorted(treatment)}, "
            f"control {sorted(control)}"
        )
    ages = sorted(set(treatment) & set(control))
    if len(ages) < 2:
        reasons.append(f"the gate needs two confirmed ages, found {len(ages)}")

    cell_sets = [set(bench.cells) for bench in list(treatment.values()) + list(control.values())]
    common: set[tuple[str, int]] = set.intersection(*cell_sets) if cell_sets else set()
    for label, bench in [("treatment", b) for b in treatment.values()] + [
        ("control", b) for b in control.values()
    ]:
        missing = len(set(bench.cells) - common)
        if missing:
            reasons.append(
                f"{label} bench {bench.path.name} has {missing} cells absent from another arm"
            )
    if clone is not None:
        common &= set(clone.cells)
    report["cells_used"] = len(common)
    if len(common) < expected_cells:
        reasons.append(
            f"the panel is underpowered: {len(common)} cells in common, {expected_cells} required"
        )

    # --- execution evidence ---------------------------------------------------------------
    faults: dict[str, dict[str, int]] = {}
    for bench in list(treatment.values()) + list(control.values()) + (
        [clone] if clone is not None else []
    ):
        found = bench.execution_faults()
        if found:
            faults[bench.path.name] = found
            reasons.append(f"{bench.path.name} did not play cleanly: {found}")
    report["execution_faults"] = faults

    if reasons:
        report["verdict"] = INCONCLUSIVE
        return report

    # --- the statistic --------------------------------------------------------------------
    per_cell: dict[tuple[str, int], float] = {}
    per_age_mean: dict[int, float] = {}
    for age in ages:
        deltas = {key: treatment[age].won(key) - control[age].won(key) for key in common}
        per_age_mean[age] = statistics.fmean(deltas.values())
    for key in common:
        per_cell[key] = statistics.fmean(
            [treatment[age].won(key) - control[age].won(key) for age in ages]
        )

    point, lo, hi = clustered_bootstrap(per_cell, draws, seed)
    report["per_age_mean_effect"] = {str(age): round(value, 6) for age, value in per_age_mean.items()}
    report["mean_effect"] = round(point, 6)
    report["ci95"] = [round(lo, 6), round(hi, 6)]
    report["interval_above_zero"] = bool(lo > 0.0)
    report["positive_at_each_age"] = all(value > 0.0 for value in per_age_mean.values())
    report["bootstrap_draws"] = draws
    report["bootstrap_seed"] = seed

    # secondary, reported but not part of the gate: the same statistic on score margins
    margin_per_cell = {
        key: statistics.fmean([treatment[age].margin(key) - control[age].margin(key) for age in ages])
        for key in common
    }
    m_point, m_lo, m_hi = clustered_bootstrap(margin_per_cell, draws, seed)
    report["margin_effect_not_the_gate"] = {
        "mean": round(m_point, 4),
        "ci95": [round(m_lo, 4), round(m_hi, 4)],
    }

    # --- clone non-inferiority -------------------------------------------------------------
    if clone is None:
        report["clone_non_inferiority"] = None
        report["non_inferiority_holds"] = None
    else:
        lost = 0
        gained = 0
        for key in common:
            clone_won = clone.won(key)
            # a cell counts as lost if the clone wins it at both ages and the treatment at neither
            treat_won = max(treatment[age].won(key) for age in ages)
            if clone_won and not treat_won:
                lost += 1
            elif treat_won and not clone_won:
                gained += 1
        net = lost - gained
        report["clone_non_inferiority"] = {
            "cells_lost": lost,
            "cells_gained": gained,
            "net_cells_lost": net,
            "budget": non_inferiority_budget,
        }
        report["non_inferiority_holds"] = bool(net <= non_inferiority_budget)

    # --- the verdict -----------------------------------------------------------------------
    if not report["interval_above_zero"]:
        report["verdict"] = NOT_CONFIRMED
    else:
        secondary = [report["positive_at_each_age"]]
        if report["non_inferiority_holds"] is not None:
            secondary.append(report["non_inferiority_holds"])
        report["verdict"] = CONFIRMED if all(secondary) else PARTIAL
    return report


def load_ages(pairs: list[str]) -> dict[int, Bench]:
    """`--treatment 1500=path.json` -> {1500: Bench(path)}."""

    out: dict[int, Bench] = {}
    for item in pairs:
        age_text, _, path = item.partition("=")
        if not path:
            raise SystemExit(f"expected <update>=<bench.json>, got {item!r}")
        out[int(age_text)] = Bench(pathlib.Path(path))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--treatment", action="append", required=True,
                        help="E00 (entropy 0) as <update>=<bench.json>, repeatable")
    parser.add_argument("--control", action="append", required=True,
                        help="E01 (entropy 0.01) as <update>=<bench.json>, repeatable")
    parser.add_argument("--clone", default=None, help="the clone's bench on the same panel")
    parser.add_argument("--expected-cells", type=int, default=144)
    parser.add_argument("--non-inferiority-budget", type=int, default=6)
    parser.add_argument("--bootstrap", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--json-out", default=None)
    args = parser.parse_args()

    report = compute(
        load_ages(args.treatment),
        load_ages(args.control),
        clone=Bench(pathlib.Path(args.clone)) if args.clone else None,
        expected_cells=args.expected_cells,
        non_inferiority_budget=args.non_inferiority_budget,
        draws=args.bootstrap,
        seed=args.seed,
    )
    text = json.dumps(report, indent=2)
    print(text)
    if args.json_out:
        pathlib.Path(args.json_out).write_text(text + "\n")
    print(f"\nVERDICT: {report['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
