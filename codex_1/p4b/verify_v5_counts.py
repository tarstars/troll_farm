#!/usr/bin/env python3
"""Verify a regenerated v5 P4b packet against Candidate 2's accepted count row."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def counts(row: dict) -> dict:
    return {"status": row["status"], "games": row["games"], "map_ids": row["map_ids"],
            "both_seats_per_map": row["both_seats_per_map"], "totals": row["totals"],
            "failed_units": len(row["failed_units"]),
            "blind_population": {k: v["count"] for k, v in row["blind_population"].items()},
            "longest_run_distribution": row["longest_run_distribution"],
            "tripwire_45": len(row["tripwire_45"])}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--accepted-c12", type=Path, required=True)
    ap.add_argument("--reproduced", type=Path, required=True)
    args = ap.parse_args()
    accepted = json.loads(args.accepted_c12.read_text())["accepted_computation_v5_decoded"]["arms"]
    reproduced = json.loads(args.reproduced.read_text())["arms"]
    pairs = (("instrument", "candidate"), ("ruleoff", "champion"))
    result = {old: {"matches": counts(accepted[old]) == counts(reproduced[new]),
                    "accepted": counts(accepted[old]), "reproduced": counts(reproduced[new])}
              for old, new in pairs}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if all(row["matches"] for row in result.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
