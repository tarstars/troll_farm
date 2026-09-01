"""Tests for the credit-path reader.

The claim this instrument is used to make is a strong one — that under `--train-scope plan-critic`
the only actor being trained receives no observed reward at all, and learns purely from the
critic's bootstrap. A reader that silently mis-sums, or that reports "no reward ever arrived"
because a field was missing rather than because it was zero, would manufacture that claim. So the
tests pin: the sums, the percentages, the distinction between *absent* and *zero*, and the
headline flag.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NN_BOT = ROOT / "local_claude_1" / "nn-bot"

spec = importlib.util.spec_from_file_location("credit_path_read", NN_BOT / "credit_path_read.py")
credit_path_read = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = credit_path_read
spec.loader.exec_module(credit_path_read)


def write_log(path: Path, updates: list[dict]) -> Path:
    with path.open("w") as handle:
        handle.write(json.dumps({"event": "start", "entropy_coef": 0.0}) + "\n")
        for record in updates:
            handle.write(json.dumps(record) + "\n")
    return path


def block(rows, terminal=0, observed=0, bootstrap=1.0, traced=0.0):
    return {
        "rows": rows,
        "terminal_event_rows": terminal,
        "observed_nonzero_reward_rows": observed,
        "bootstrap_share": bootstrap,
        "terminal_traced_fraction": traced,
        "critic_component_fraction": 1.0,
        "raw_advantage_std": 0.08,
    }


def test_sums_percentages_and_the_purely_bootstrap_flag(tmp_path):
    log = write_log(
        tmp_path / "train.log",
        [
            {
                "update": 1,
                "rollout_credit": {
                    "plan": block(1000, terminal=0, observed=0, bootstrap=0.98, traced=0.01),
                    "troll": block(2000, terminal=4, observed=4, bootstrap=0.97, traced=0.02),
                },
            },
            {
                "update": 2,
                "rollout_credit": {
                    "plan": block(1000, terminal=0, observed=0, bootstrap=0.96, traced=0.03),
                    "troll": block(2000, terminal=6, observed=6, bootstrap=0.95, traced=0.04),
                },
            },
        ],
    )
    report = credit_path_read.read_log(log)

    assert report["updates_with_credit_telemetry"] == 2
    assert report["first_update"] == 1 and report["last_update"] == 2

    plan = report["row_classes"]["plan"]
    assert plan["rows"] == 2000
    assert plan["observed_nonzero_reward_rows"] == 0
    assert plan["updates_with_observed_reward"] == 0
    assert plan["signal_is_purely_bootstrap"] is True
    assert plan["bootstrap_share"]["mean"] == 0.97

    troll = report["row_classes"]["troll"]
    assert troll["rows"] == 4000
    assert troll["terminal_event_rows"] == 10
    assert troll["observed_nonzero_reward_rows"] == 10
    assert troll["observed_reward_row_percent"] == 0.25
    assert troll["updates_with_observed_reward"] == 2
    assert troll["signal_is_purely_bootstrap"] is False


def test_one_rewarded_update_clears_the_flag(tmp_path):
    log = write_log(
        tmp_path / "train.log",
        [
            {"update": 1, "rollout_credit": {"plan": block(100), "troll": block(100)}},
            {
                "update": 2,
                "rollout_credit": {
                    "plan": block(100, terminal=1, observed=1),
                    "troll": block(100),
                },
            },
        ],
    )
    plan = credit_path_read.read_log(log)["row_classes"]["plan"]
    assert plan["signal_is_purely_bootstrap"] is False
    assert plan["updates_with_observed_reward"] == 1


def test_absent_fields_are_not_counted_as_zero(tmp_path):
    """A missing `bootstrap_share` must be left out of the mean, not read as 0.0."""

    log = write_log(
        tmp_path / "train.log",
        [
            {"update": 1, "rollout_credit": {"plan": {"rows": 10, "bootstrap_share": 0.5}}},
            {"update": 2, "rollout_credit": {"plan": {"rows": 10}}},
        ],
    )
    plan = credit_path_read.read_log(log)["row_classes"]["plan"]
    assert plan["rows"] == 20
    assert plan["bootstrap_share"]["mean"] == 0.5  # not 0.25
    assert plan["updates"] == 2


def test_lines_without_credit_telemetry_are_skipped(tmp_path):
    log = write_log(
        tmp_path / "train.log",
        [
            {"update": 1, "win_rate": 0.2},  # a plain update line, no credit block
            {"update": 2, "rollout_credit": {"plan": block(10), "troll": block(10)}},
        ],
    )
    report = credit_path_read.read_log(log)
    assert report["updates_with_credit_telemetry"] == 1
    assert report["first_update"] == 2
