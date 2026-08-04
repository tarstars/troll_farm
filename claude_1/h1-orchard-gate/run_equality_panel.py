#!/usr/bin/env python3
"""Command-stream equality panel for the orchard-code-cost audit.

Replays the frozen open 25-game / 7,234-line packet through two compiled bots
and compares their outputs line by line. Used twice:
  1. reference vs live-baseline expected outputs (expect: identical except the
     single orchard-activation game, proving the reference changes exactly the
     activation and nothing else);
  2. stripped vs reference outputs (expect: identical on every game — the
     physical deletion introduces no behavior beyond the disabled activation).
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import subprocess
from pathlib import Path

PACKET_SHA256 = "fb8e968ff65fc55c6f6f9d2f2b678434ab2dfda8eba84fdb6d0384d41856c7e2"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--left-bin", type=Path, required=True)
    parser.add_argument("--right-bin", type=Path,
                        help="second binary; omit to compare left against the packet's stored baseline outputs")
    parser.add_argument("--label", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("refusing to overwrite equality evidence")

    packet_bytes = args.packet.read_bytes()
    if hashlib.sha256(packet_bytes).hexdigest() != PACKET_SHA256:
        raise RuntimeError("packet SHA-256 mismatch")
    packet = json.loads(gzip.decompress(packet_bytes))

    def run(binary: Path, transcript: str) -> list[str]:
        proc = subprocess.run(
            [str(binary)], input=transcript, capture_output=True, text=True, timeout=120
        )
        if proc.returncode != 0 or proc.stderr:
            raise RuntimeError(f"{binary}: exit {proc.returncode}, stderr {proc.stderr[:200]!r}")
        return proc.stdout.strip().splitlines()

    rows, identical, total_lines = [], 0, 0
    for row in packet["rows"]:
        left = run(args.left_bin, row["transcript"])
        right = (
            run(args.right_bin, row["transcript"])
            if args.right_bin
            else row["baseline_output"].strip().splitlines()
        )
        first_diff = next(
            (i + 1 for i, (a, b) in enumerate(zip(left, right)) if a != b), None
        )
        if first_diff is None and len(left) != len(right):
            first_diff = min(len(left), len(right)) + 1
        total_lines += len(right)
        same = first_diff is None
        identical += same
        rows.append(
            {
                "game_id": row["game_id"],
                "opponent": row["opponent"],
                "turns": row["turns"],
                "identical": same,
                "first_divergent_turn": first_diff,
            }
        )

    result = {
        "schema": "troll-farm-orchard-code-cost-equality-v1",
        "label": args.label,
        "packet_sha256": PACKET_SHA256,
        "games": len(rows),
        "identical_games": identical,
        "compared_lines": total_lines,
        "rows": rows,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"label": args.label, "identical": identical, "games": len(rows), "lines": total_lines}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
