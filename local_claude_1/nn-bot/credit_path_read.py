#!/usr/bin/env python3
"""What the learning signal is actually made of, read from a run's `rollout_credit` telemetry.

The trainer records, per update and separately for PLAN rows and TROLL rows, how each advantage
was composed: how many rows carried a terminal event, how many saw a non-zero reward, what share
of the return target came from the critic's bootstrap rather than from observed reward, and what
fraction of rows had a credit trace reaching a real terminal before the 32-mini-step buffer cut.

This matters because of how the card pays reward. With `--reward-credit executing` (the default)
the turn's reward is kept only on the mini-step that executed the turn and zeroed elsewhere. A
PLAN mini-step is never the executing one, so **PLAN rows structurally receive reward zero** and
the plan head can only learn through the critic's value bootstrap. Under
`--train-scope plan-critic` the plan head is the only actor being trained — so the question "how
much of its signal is grounded in outcomes?" has a definite, measurable answer, and this script
is what answers it.

Usage:
    credit_path_read.py --log <train.log> [--log <train.log> ...] [--json-out out.json]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import statistics
from typing import Any

ROW_CLASSES = ("plan", "troll")


def read_log(path: pathlib.Path) -> dict[str, Any]:
    """Aggregate one run's credit telemetry over every update that carries it."""

    totals: dict[str, dict[str, Any]] = {
        name: {
            "rows": 0,
            "terminal_event_rows": 0,
            "observed_nonzero_reward_rows": 0,
            "updates": 0,
            "updates_with_observed_reward": 0,
            "bootstrap_share": [],
            "terminal_traced_fraction": [],
            "critic_component_fraction": [],
            "raw_advantage_std": [],
        }
        for name in ROW_CLASSES
    }
    updates = 0
    first_update = None
    last_update = None

    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            credit = record.get("rollout_credit")
            if not credit:
                continue
            updates += 1
            if first_update is None:
                first_update = record.get("update")
            last_update = record.get("update")
            for name in ROW_CLASSES:
                block = credit.get(name)
                if not block:
                    continue
                bucket = totals[name]
                bucket["updates"] += 1
                bucket["rows"] += int(block.get("rows") or 0)
                bucket["terminal_event_rows"] += int(block.get("terminal_event_rows") or 0)
                observed = int(block.get("observed_nonzero_reward_rows") or 0)
                bucket["observed_nonzero_reward_rows"] += observed
                if observed > 0:
                    bucket["updates_with_observed_reward"] += 1
                for field in (
                    "bootstrap_share",
                    "terminal_traced_fraction",
                    "critic_component_fraction",
                    "raw_advantage_std",
                ):
                    value = block.get(field)
                    if value is not None:
                        bucket[field].append(float(value))

    report: dict[str, Any] = {
        "log": str(path),
        "updates_with_credit_telemetry": updates,
        "first_update": first_update,
        "last_update": last_update,
        "row_classes": {},
    }
    for name in ROW_CLASSES:
        bucket = totals[name]
        rows = max(bucket["rows"], 1)
        entry: dict[str, Any] = {
            "rows": bucket["rows"],
            "terminal_event_rows": bucket["terminal_event_rows"],
            "terminal_event_row_percent": round(100.0 * bucket["terminal_event_rows"] / rows, 6),
            "observed_nonzero_reward_rows": bucket["observed_nonzero_reward_rows"],
            "observed_reward_row_percent": round(
                100.0 * bucket["observed_nonzero_reward_rows"] / rows, 6
            ),
            "updates": bucket["updates"],
            "updates_with_observed_reward": bucket["updates_with_observed_reward"],
        }
        for field in (
            "bootstrap_share",
            "terminal_traced_fraction",
            "critic_component_fraction",
            "raw_advantage_std",
        ):
            values = bucket[field]
            if values:
                entry[field] = {
                    "mean": round(statistics.fmean(values), 6),
                    "min": round(min(values), 6),
                    "max": round(max(values), 6),
                }
        # the headline: is this row class's signal grounded in outcomes at all?
        entry["signal_is_purely_bootstrap"] = bucket["observed_nonzero_reward_rows"] == 0
        report["row_classes"][name] = entry
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", action="append", required=True, help="a trainer train.log")
    parser.add_argument("--json-out", default=None)
    args = parser.parse_args()

    reports = [read_log(pathlib.Path(one)) for one in args.log]
    for report in reports:
        print(f"=== {report['log']}")
        print(
            f"  {report['updates_with_credit_telemetry']:,} updates with credit telemetry "
            f"(updates {report['first_update']}..{report['last_update']})"
        )
        for name, entry in report["row_classes"].items():
            print(f"  --- {name} rows")
            print(f"      rows                            {entry['rows']:,}")
            print(
                f"      carrying a terminal event       {entry['terminal_event_rows']:,} "
                f"({entry['terminal_event_row_percent']} %)"
            )
            print(
                f"      with a non-zero reward          "
                f"{entry['observed_nonzero_reward_rows']:,} "
                f"({entry['observed_reward_row_percent']} %)"
            )
            print(
                f"      updates with any reward         "
                f"{entry['updates_with_observed_reward']:,} of {entry['updates']:,}"
            )
            if "bootstrap_share" in entry:
                share = entry["bootstrap_share"]
                print(
                    f"      bootstrap share of the target   mean {share['mean']} "
                    f"(min {share['min']})"
                )
            if "terminal_traced_fraction" in entry:
                traced = entry["terminal_traced_fraction"]
                print(
                    f"      trace reaches a terminal        mean {traced['mean']} "
                    f"(max {traced['max']})"
                )
            if entry["signal_is_purely_bootstrap"]:
                print("      *** no observed reward ever reached these rows ***")

    if args.json_out:
        pathlib.Path(args.json_out).write_text(json.dumps(reports, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
