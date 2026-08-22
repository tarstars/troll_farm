#!/usr/bin/env python3
"""Compare the single-deletion candidate with exact live E7a on ten fixtures."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile


REPO = Path(__file__).resolve().parents[2]
BASELINE = REPO / "cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs"
BASELINE_SHA256 = "97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595"
SACRED = REPO / "rust/src/bin/yamo_orchard_live.rs"
SACRED_SHA256 = "fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f"
SHARED_PATH = REPO / "local_codex_1/e7a-half-size-logical-simplification/validate_semantics.py"
FOCUS_ANCHOR = (
    "if self.type_to_cut.is_none(){self.type_to_cut="
    "Some(MoisanBot::focus_type(view));}"
)
FOCUS_PROBE = (
    "if self.type_to_cut.is_none(){let focus=MoisanBot::focus_type(view);"
    'eprintln!("@FOCUS {}",focus.as_str());self.type_to_cut=Some(focus);}'
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_shared():
    specification = importlib.util.spec_from_file_location(
        "e7a_single_delete_semantic_shared", SHARED_PATH
    )
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load shared semantic fixtures")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    candidate = args.candidate.resolve()
    output = args.output.resolve()

    if output.exists():
        parser.error("refusing to overwrite semantic evidence")
    if sha256(BASELINE) != BASELINE_SHA256:
        raise RuntimeError("exact live baseline hash mismatch")
    if sha256(SACRED) != SACRED_SHA256:
        raise RuntimeError("sacred source hash mismatch")
    if sha256(candidate) != args.expected_sha256:
        raise RuntimeError("candidate hash mismatch")

    baseline_source = BASELINE.read_text()
    candidate_source = candidate.read_text()
    if baseline_source.count(FOCUS_ANCHOR) != 1:
        raise RuntimeError("baseline focus probe anchor mismatch")
    if candidate_source.count(FOCUS_ANCHOR) != 1:
        raise RuntimeError("candidate focus probe anchor mismatch")

    shared = load_shared()
    with tempfile.TemporaryDirectory(prefix="e7a-single-delete-semantics-") as directory:
        temp = Path(directory)
        baseline_binary = temp / "baseline"
        candidate_binary = temp / "candidate"
        baseline_probe = temp / "baseline-probe"
        candidate_probe = temp / "candidate-probe"
        shared.compile_text(baseline_source, baseline_binary, "e7a_single_delete_baseline")
        shared.compile_text(candidate_source, candidate_binary, "e7a_single_delete_candidate")
        shared.compile_text(
            baseline_source.replace(FOCUS_ANCHOR, FOCUS_PROBE, 1),
            baseline_probe,
            "e7a_single_delete_baseline_probe",
        )
        shared.compile_text(
            candidate_source.replace(FOCUS_ANCHOR, FOCUS_PROBE, 1),
            candidate_probe,
            "e7a_single_delete_candidate_probe",
        )

        baseline = {
            "focus": shared.focus_fixtures(baseline_probe),
            "training_bill": shared.training_bill_fixture(baseline_binary),
            "training_fallback": shared.training_fallback_fixture(baseline_binary),
            "banking_commitment": shared.banking_commitment_fixture(baseline_binary),
            "same_target": shared.same_target_fixture(baseline_binary),
            "landing_conflict": shared.landing_conflict_fixture(baseline_binary),
            "endgame_deadline": shared.endgame_deadline_fixture(baseline_binary),
        }
        observed = {
            "focus": shared.focus_fixtures(candidate_probe),
            "training_bill": shared.training_bill_fixture(candidate_binary),
            "training_fallback": shared.training_fallback_fixture(candidate_binary),
            "banking_commitment": shared.banking_commitment_fixture(candidate_binary),
            "same_target": shared.same_target_fixture(candidate_binary),
            "landing_conflict": shared.landing_conflict_fixture(candidate_binary),
            "endgame_deadline": shared.endgame_deadline_fixture(candidate_binary),
        }

    if observed != baseline:
        raise AssertionError("candidate semantic fixtures differ from exact live E7a")
    fixture_count = len(baseline["focus"]) + len(baseline) - 1
    if fixture_count != 10:
        raise AssertionError(f"expected ten fixtures, got {fixture_count}")

    result = {
        "schema": "troll-farm-e7a-single-logical-deletion-semantics-v1",
        "baseline": {
            "path": str(BASELINE.relative_to(REPO)),
            "bytes": BASELINE.stat().st_size,
            "sha256": BASELINE_SHA256,
        },
        "candidate": {
            "path": str(candidate.relative_to(REPO)),
            "bytes": candidate.stat().st_size,
            "sha256": args.expected_sha256,
        },
        "sacred_sha256": SACRED_SHA256,
        "fixture_count": fixture_count,
        "exact_fixture_parity": True,
        "fixtures": observed,
        "verdict": "SEMANTIC_FIXTURES_EXACT_PASS",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"verdict": result["verdict"], "fixtures": fixture_count}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
