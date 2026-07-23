#!/usr/bin/env python3
"""Validate packaging, research parity, and latency for the dual-value crop candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import statistics
import sys
import tempfile


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.idle_harvest_study import compile_source  # noqa: E402
from cgauto.make_opponent_crop_dual_value_candidate import (  # noqa: E402
    make_candidate,
    OUTPUT as CANDIDATE,
    PARENT,
)
from cgauto.validate_opponent_crop_candidate import (  # noqa: E402
    capture_reference_stream,
    DYNAMIC_CELLS,
    first_turn_gate,
    OPPONENTS,
    percentile,
    replay_interactive,
    RESEARCH,
    RESIDENT,
)


DEFAULT_OUTPUT = (
    REPO
    / "data/analysis/live-agent-6553250/"
    "opponent-crop-dual-value-local-gate-2026-07-19.json"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def activate_research_source(source: str) -> str:
    before = "    let mut bot = SecureOrchardBot::new();"
    after = "    let mut bot = SecureOrchardBot::opponent_crop_dual_value_e6();"
    count = source.count(before)
    if count != 1:
        raise ValueError(f"expected one research main anchor, found {count}")
    return source.replace(before, after, 1)


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    if CANDIDATE.read_text() != make_candidate(PARENT.read_text()):
        raise RuntimeError("candidate artifact does not match the fail-closed generator")
    expected_sidecar = f"{digest(CANDIDATE)}  {CANDIDATE.name}"
    if CANDIDATE.with_name(CANDIDATE.name + ".sha256").read_text().strip() != expected_sidecar:
        raise RuntimeError("candidate SHA-256 sidecar mismatch")
    if CANDIDATE.stat().st_size >= 100_000:
        raise RuntimeError("candidate exceeds the 100,000-byte source limit")

    with tempfile.TemporaryDirectory(prefix="crop-dual-value-gate-") as directory:
        temp = Path(directory)
        activated = temp / "activated_research.rs"
        activated.write_text(activate_research_source(RESEARCH.read_text()))
        binaries = {
            "candidate": temp / "candidate",
            "resident": temp / "resident",
            "reference": temp / "reference",
        }
        compile_source(CANDIDATE, binaries["candidate"], "crop_dual_candidate")
        compile_source(RESIDENT, binaries["resident"], "crop_dual_resident")
        compile_source(activated, binaries["reference"], "crop_dual_reference")
        for name, source in OPPONENTS.items():
            binaries[name] = temp / name
            compile_source(source, binaries[name], f"crop_dual_{name}")

        first_turn = first_turn_gate(binaries["resident"], binaries["candidate"])
        rows = []
        latencies = []
        for seed, seat, opponent in DYNAMIC_CELLS:
            stream = capture_reference_stream(
                binaries["reference"], binaries[opponent], seed, seat
            )
            candidate = replay_interactive(
                binaries["candidate"], stream["grid"], stream["turn_blocks"]
            )
            resident = replay_interactive(
                binaries["resident"], stream["grid"], stream["turn_blocks"]
            )
            exact = candidate["lines"] == stream["reference_lines"]
            if not exact:
                first = next(
                    index
                    for index, (actual, expected) in enumerate(
                        zip(candidate["lines"], stream["reference_lines"]), 1
                    )
                    if actual != expected
                )
                raise RuntimeError(
                    f"slim/reference mismatch seed={seed} seat={seat} turn={first}"
                )
            if candidate["stderr"]:
                raise RuntimeError("candidate unexpectedly wrote to stderr")
            divergence = next(
                (
                    turn
                    for turn, (left, right) in enumerate(
                        zip(candidate["lines"], resident["lines"]), 1
                    )
                    if left.split(" MSG ", 1)[0] != right.split(" MSG ", 1)[0]
                ),
                None,
            )
            latencies.extend(candidate["elapsed_ms"])
            rows.append(
                {
                    "seed": seed,
                    "seat": seat,
                    "opponent": opponent,
                    "turns": len(candidate["lines"]),
                    "terminal_turn": stream["terminal_turn"],
                    "exact_reference_stream": exact,
                    "first_resident_divergence_turn": divergence,
                }
            )

    latency = {
        "commands": len(latencies),
        "mean_ms": statistics.mean(latencies),
        "p50_ms": percentile(latencies, 0.50),
        "p95_ms": percentile(latencies, 0.95),
        "maximum_ms": max(latencies),
        "p95_limit_ms": 20,
        "maximum_limit_ms": 100,
    }
    latency["passed"] = latency["p95_ms"] <= 20 and latency["maximum_ms"] <= 100
    dynamic_passed = all(row["exact_reference_stream"] for row in rows)
    passed = first_turn["passed"] and dynamic_passed and latency["passed"]
    payload = {
        "schema": 1,
        "scope": "consumed-seed packaging, parity, and latency gate; no outcome inference",
        "sources": {
            "parent": {"path": str(PARENT.relative_to(REPO)), "sha256": digest(PARENT)},
            "resident": {"path": str(RESIDENT.relative_to(REPO)), "sha256": digest(RESIDENT)},
            "candidate": {
                "path": str(CANDIDATE.relative_to(REPO)),
                "bytes": CANDIDATE.stat().st_size,
                "sha256": digest(CANDIDATE),
            },
            "research": str(RESEARCH.relative_to(REPO)),
        },
        "fixed_treatment": {"valuation": "existing_score_x2", "eta_limit": 6},
        "first_turn_resident_parity": first_turn,
        "dynamic_reference_parity": {
            "streams": len(rows),
            "exact_streams": sum(row["exact_reference_stream"] for row in rows),
            "activated_streams": sum(
                row["first_resident_divergence_turn"] is not None for row in rows
            ),
            "rows": rows,
            "passed": dynamic_passed,
        },
        "interactive_latency": latency,
        "verdict": "PASS" if passed else "FAIL",
    }
    save(args.output, payload)
    print(
        f"{payload['verdict']}: {CANDIDATE.stat().st_size} bytes, "
        f"turn1={120-len(first_turn['mismatches'])}/120, "
        f"dynamic={payload['dynamic_reference_parity']['exact_streams']}/{len(rows)}, "
        f"activated={payload['dynamic_reference_parity']['activated_streams']}, "
        f"p95={latency['p95_ms']:.3f} ms, max={latency['maximum_ms']:.3f} ms"
    )
    print(f"saved {args.output}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
