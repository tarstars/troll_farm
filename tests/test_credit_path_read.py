"""Tests for the credit-path reader.

The claim this instrument is used to make is a strong one, so the reader must not manufacture it.
The headline is **the share of the advantage's magnitude that came from observed reward** rather
than from the critic's own values — not "did a row hold a reward in its own slot", which for PLAN
rows is always no for a structural reason that carries no meaning (the within-turn trace delivers
the reward anyway). An earlier version of this file reported that structural zero as the headline
and the coordinator misread it as "the plan head never sees a reward"; the tests below now pin the
share, and pin that a row-slot zero does not imply an absent reward.
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
    assert plan["rows_holding_reward_in_their_own_slot"] == 0
    assert plan["bootstrap_share"]["mean"] == 0.97

    troll = report["row_classes"]["troll"]
    assert troll["rows"] == 4000
    assert troll["terminal_event_rows"] == 10
    assert troll["observed_nonzero_reward_rows"] == 10
    assert troll["observed_reward_row_percent"] == 0.25
    assert troll["updates_with_observed_reward"] == 2


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


def test_the_headline_is_the_reward_share_not_the_row_slot(tmp_path):
    """A row slot of zero must not be reported as an absent reward.

    Both classes here hold reward in no row's own slot, yet a quarter of the advantage's
    magnitude came from observed reward through the trace. The instrument must say 25 %.
    """

    def block_with_components(rows, reward_abs, critic_abs):
        return {
            "rows": rows,
            "terminal_event_rows": 0,
            "observed_nonzero_reward_rows": 0,
            "reward_component_abs_sum": reward_abs,
            "critic_component_abs_sum": critic_abs,
            "bootstrap_share": 0.75,
        }

    log = write_log(
        tmp_path / "train.log",
        [
            {
                "update": 1,
                "rollout_credit": {
                    "plan": block_with_components(100, 25.0, 75.0),
                    "troll": block_with_components(100, 25.0, 75.0),
                },
            }
        ],
    )
    plan = credit_path_read.read_log(log)["row_classes"]["plan"]
    assert plan["rows_holding_reward_in_their_own_slot"] == 0
    assert plan["reward_share_of_signal_percent"] == 25.0
    assert plan["updates_with_reward_in_advantage"] == 1


def test_no_reward_anywhere_reports_a_zero_share(tmp_path):
    log = write_log(
        tmp_path / "train.log",
        [
            {
                "update": 1,
                "rollout_credit": {
                    "plan": {"rows": 10, "reward_component_abs_sum": 0.0,
                             "critic_component_abs_sum": 40.0},
                    "troll": {"rows": 10, "reward_component_abs_sum": 0.0,
                              "critic_component_abs_sum": 40.0},
                },
            }
        ],
    )
    plan = credit_path_read.read_log(log)["row_classes"]["plan"]
    assert plan["reward_share_of_signal_percent"] == 0.0
    assert plan["updates_with_reward_in_advantage"] == 0
