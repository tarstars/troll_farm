"""Tests for the frozen Gate 1.

Written before the arms finished, so the rule is pinned independently of the numbers it will
judge. What is pinned:

1. all four outcomes are reachable, each for its stated reason;
2. the interval is a **clustered** bootstrap over cells — a cell's two ages move together, and
   pooling the ages as independent rows (the mistake the reviewer's panel note forbids) would
   give a visibly narrower interval, so the test asserts the clustering actually happens;
3. INCONCLUSIVE wins over any statistical verdict: too few cells, mismatched populations,
   mismatched ages, or games that did not play cleanly, even when the effect is large;
4. the arithmetic itself: paired win deltas, per-age means, and the net-cells-lost count.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NN_BOT = ROOT / "local_claude_1" / "nn-bot"

spec = importlib.util.spec_from_file_location("gate1", NN_BOT / "gate1.py")
gate1 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = gate1
spec.loader.exec_module(gate1)


def write_bench(path: Path, wins: dict[tuple[str, int], bool], *, faults: dict | None = None,
                margin: int = 10) -> Path:
    rows = []
    for (map_hash, seat), won in wins.items():
        rows.append({
            "map_hash": map_hash,
            "policy_seat": seat,
            "policy_won": won,
            "policy_score": 100 + (margin if won else 0),
            "bot_score": 100,
        })
    payload = {
        "rows": rows,
        "illegal_commands_total": 0,
        "timeouts_total": 0,
        "referee_errors_total": 0,
        "checkpoint": str(path),
    }
    payload.update(faults or {})
    path.write_text(json.dumps(payload))
    return path


def cells(n: int) -> list[tuple[str, int]]:
    return [(f"map{i:04d}", seat) for i in range(n // 2) for seat in (0, 1)]


def bench_pair(tmp_path, name, wins_by_age):
    return {age: gate1.Bench(write_bench(tmp_path / f"{name}-u{age}.json", wins))
            for age, wins in wins_by_age.items()}


def test_confirmed_when_treatment_wins_everywhere(tmp_path):
    keys = cells(144)
    treatment = bench_pair(tmp_path, "t", {
        1500: {k: True for k in keys},
        2500: {k: True for k in keys},
    })
    control = bench_pair(tmp_path, "c", {
        1500: {k: False for k in keys},
        2500: {k: False for k in keys},
    })
    clone = gate1.Bench(write_bench(tmp_path / "clone.json", {k: False for k in keys}))

    report = gate1.compute(treatment, control, clone=clone, draws=500)
    assert report["verdict"] == gate1.CONFIRMED
    assert report["mean_effect"] == 1.0
    assert report["interval_above_zero"] is True
    assert report["positive_at_each_age"] is True
    assert report["clone_non_inferiority"]["net_cells_lost"] == -144  # all gained


def test_not_confirmed_when_the_arms_are_the_same(tmp_path):
    keys = cells(144)
    same = {k: (i % 2 == 0) for i, k in enumerate(keys)}
    treatment = bench_pair(tmp_path, "t", {1500: dict(same), 2500: dict(same)})
    control = bench_pair(tmp_path, "c", {1500: dict(same), 2500: dict(same)})

    report = gate1.compute(treatment, control, draws=500)
    assert report["verdict"] == gate1.NOT_CONFIRMED
    assert report["mean_effect"] == 0.0


def test_partial_when_the_effect_is_not_positive_at_both_ages(tmp_path):
    keys = cells(144)
    # treatment sweeps the late age, loses a little at the early one: the pooled effect is
    # positive and its interval clears zero, but the early age is negative
    treatment = bench_pair(tmp_path, "t", {
        1500: {k: False for k in keys},
        2500: {k: True for k in keys},
    })
    control = bench_pair(tmp_path, "c", {
        1500: {k: i < 10 for i, k in enumerate(keys)},
        2500: {k: False for k in keys},
    })
    report = gate1.compute(treatment, control, draws=2000)
    assert report["interval_above_zero"] is True
    assert report["positive_at_each_age"] is False
    assert report["verdict"] == gate1.PARTIAL


def test_partial_when_clone_non_inferiority_fails(tmp_path):
    keys = cells(144)
    # the treatment beats the control everywhere, but drops many cells the clone held
    treatment = bench_pair(tmp_path, "t", {
        1500: {k: i >= 40 for i, k in enumerate(keys)},
        2500: {k: i >= 40 for i, k in enumerate(keys)},
    })
    control = bench_pair(tmp_path, "c", {
        1500: {k: False for k in keys},
        2500: {k: False for k in keys},
    })
    clone = gate1.Bench(write_bench(tmp_path / "clone.json", {k: True for k in keys}))

    report = gate1.compute(treatment, control, clone=clone, draws=500)
    assert report["interval_above_zero"] is True
    assert report["clone_non_inferiority"]["net_cells_lost"] == 40
    assert report["non_inferiority_holds"] is False
    assert report["verdict"] == gate1.PARTIAL


def test_inconclusive_when_underpowered_even_with_a_huge_effect(tmp_path):
    keys = cells(20)
    treatment = bench_pair(tmp_path, "t", {
        1500: {k: True for k in keys}, 2500: {k: True for k in keys}})
    control = bench_pair(tmp_path, "c", {
        1500: {k: False for k in keys}, 2500: {k: False for k in keys}})

    report = gate1.compute(treatment, control, draws=200)
    assert report["verdict"] == gate1.INCONCLUSIVE
    assert any("underpowered" in reason for reason in report["inconclusive_reasons"])
    assert "mean_effect" not in report  # the statistic is not reported on incomplete evidence


def test_inconclusive_when_a_bench_did_not_play_cleanly(tmp_path):
    keys = cells(144)
    treatment = {
        1500: gate1.Bench(write_bench(tmp_path / "t-1500.json", {k: True for k in keys},
                                      faults={"illegal_commands_total": 3})),
        2500: gate1.Bench(write_bench(tmp_path / "t-2500.json", {k: True for k in keys})),
    }
    control = bench_pair(tmp_path, "c", {
        1500: {k: False for k in keys}, 2500: {k: False for k in keys}})

    report = gate1.compute(treatment, control, draws=200)
    assert report["verdict"] == gate1.INCONCLUSIVE
    assert "t-1500.json" in report["execution_faults"]


def test_inconclusive_when_the_arms_were_benched_at_different_ages(tmp_path):
    keys = cells(144)
    treatment = bench_pair(tmp_path, "t", {
        1500: {k: True for k in keys}, 2500: {k: True for k in keys}})
    control = bench_pair(tmp_path, "c", {
        1000: {k: False for k in keys}, 2500: {k: False for k in keys}})

    report = gate1.compute(treatment, control, draws=200)
    assert report["verdict"] == gate1.INCONCLUSIVE
    assert any("different ages" in reason for reason in report["inconclusive_reasons"])


def test_the_bootstrap_clusters_cells_rather_than_pooling_rows(tmp_path):
    """A cell's two ages must move together.

    Build data where every cell is either +1 at both ages or -1 at both ages. Clustered
    resampling keeps that perfect within-cell correlation, so the spread of the mean is that of
    a 144-unit sample of ±1. Pooling the 288 rows as independent would halve the variance, and
    the interval would be visibly narrower. The test asserts the interval is at least as wide as
    the correctly-clustered standard error implies.
    """

    keys = cells(144)
    half = len(keys) // 2
    treatment_wins = {k: (i < half) for i, k in enumerate(keys)}
    control_wins = {k: (i >= half) for i, k in enumerate(keys)}
    treatment = bench_pair(tmp_path, "t", {1500: dict(treatment_wins), 2500: dict(treatment_wins)})
    control = bench_pair(tmp_path, "c", {1500: dict(control_wins), 2500: dict(control_wins)})

    report = gate1.compute(treatment, control, draws=4000, seed=7)
    lo, hi = report["ci95"]
    width = hi - lo
    # per-cell values are exactly ±1 in equal numbers: sd = 1, se = 1/sqrt(144) = 0.0833,
    # so a correct 95 % interval is about 4 * 0.0833 = 0.33 wide. Row-pooling would give ~0.23.
    assert width > 0.28, f"interval {width:.3f} is too narrow — are the ages being pooled as rows?"
    assert report["verdict"] == gate1.NOT_CONFIRMED  # centred on zero


def test_net_cells_lost_counts_both_directions(tmp_path):
    keys = cells(144)
    # clone wins the first 20; treatment wins the last 8 that the clone loses
    clone_wins = {k: i < 20 for i, k in enumerate(keys)}
    treat_wins = {k: i >= len(keys) - 8 for i, k in enumerate(keys)}
    treatment = bench_pair(tmp_path, "t", {1500: dict(treat_wins), 2500: dict(treat_wins)})
    control = bench_pair(tmp_path, "c", {
        1500: {k: False for k in keys}, 2500: {k: False for k in keys}})
    clone = gate1.Bench(write_bench(tmp_path / "clone.json", clone_wins))

    report = gate1.compute(treatment, control, clone=clone, draws=200)
    non_inf = report["clone_non_inferiority"]
    assert non_inf["cells_lost"] == 20
    assert non_inf["cells_gained"] == 8
    assert non_inf["net_cells_lost"] == 12
