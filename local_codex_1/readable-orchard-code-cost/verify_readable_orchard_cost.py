#!/usr/bin/env python3
"""Verify readable orchard artifacts and finalize their manifest."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
SACRED = REPO / "rust/src/bin/yamo_orchard_live.rs"
SACRED_SHA256 = "fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f"
# Landmarks that bound the orchard-exclusive groups inside the with-orchard readable file.
TYPES_START = "enum OrchardPhase {"
HELPERS_START = "impl SecureOrchardBot {"
DRIVER_START = "impl Bot for SecureOrchardBot {"
HEADER_LINES = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def landmark(lines: list[str], needle: str) -> int:
    for number, line in enumerate(lines, 1):
        if line.strip() == needle:
            return number
    raise RuntimeError(f"landmark not found: {needle}")


def line_inventory(baseline: Path, stripped: Path) -> dict[str, object]:
    """Group the with-orchard lines the stripped variant does not have."""

    with_orchard = baseline.read_text(encoding="utf-8").splitlines()
    without = stripped.read_text(encoding="utf-8").splitlines()
    types = landmark(with_orchard, TYPES_START) - 1  # the derive attribute above the enum
    helpers = landmark(with_orchard, HELPERS_START)
    driver = landmark(with_orchard, DRIVER_START)

    removed: list[int] = []
    replacements = 0
    opcodes = difflib.SequenceMatcher(None, with_orchard, without, autojunk=False).get_opcodes()
    for tag, i1, i2, j1, j2 in opcodes:
        if tag not in {"delete", "replace"}:
            continue
        span = [number for number in range(i1 + 1, i2 + 1) if number > HEADER_LINES]
        removed.extend(span)
        if span and tag == "replace":
            replacements += j2 - j1  # lines the stripped variant kept in their place

    groups = {
        "orchard_data_types_and_wrapper_state": 0,
        "orchard_selection_and_maintenance_helpers": 0,
        "orchard_per_turn_driver": 0,
        "reservation_channel_import_and_main_wiring": 0,
    }
    for number in removed:
        if types <= number < helpers:
            groups["orchard_data_types_and_wrapper_state"] += 1
        elif helpers <= number < driver:
            groups["orchard_selection_and_maintenance_helpers"] += 1
        elif driver <= number <= max(n for n in removed if n >= driver and n < len(with_orchard) - 40):
            groups["orchard_per_turn_driver"] += 1
        else:
            groups["reservation_channel_import_and_main_wiring"] += 1
    # Replaced lines are rewrites of the reservation channel and main wiring, not deletions.
    groups["reservation_channel_import_and_main_wiring"] -= replacements
    total = sum(groups.values())
    if total != len(with_orchard) - len(without):
        raise RuntimeError(f"line inventory {total} does not match physical delta")
    return {
        **groups,
        "total": total,
        "basis": "canonical generated with-orchard line spans; grouped against exact stripped token stream",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    manifest = load(manifest_path)
    base = manifest_path.parent

    if sha256(SACRED) != SACRED_SHA256:
        raise RuntimeError("sacred readable resident changed")
    for record in manifest["sources"].values():
        readable = REPO / record["readable_path"]
        compact = REPO / record["compact_path"]
        if sha256(readable) != record["readable_sha256"]:
            raise RuntimeError(f"readable hash mismatch: {readable}")
        if sha256(compact) != record["compact_sha256"]:
            raise RuntimeError(f"compact hash mismatch: {compact}")

    fixture_files = {
        "with_orchard": base / "baseline-semantic-fixtures.json",
        "activation_disabled": base / "activation-disabled-semantic-fixtures.json",
        "orchard_stripped": base / "stripped-semantic-fixtures.json",
    }
    for label, path in fixture_files.items():
        evidence = load(path)
        if evidence.get("verdict") != "SEMANTIC_FIXTURES_EXACT_PASS" or evidence.get("fixture_count") != 10:
            raise RuntimeError(f"{label}: semantic fixture evidence failed")

    panels = {
        "readable_baseline_vs_packet": load(base / "readable-baseline-vs-packet.json"),
        "readable_disabled_vs_baseline": load(base / "readable-disabled-vs-baseline.json"),
        "readable_stripped_vs_disabled": load(base / "readable-stripped-vs-disabled.json"),
    }
    expected = {
        "readable_baseline_vs_packet": 25,
        "readable_disabled_vs_baseline": 24,
        "readable_stripped_vs_disabled": 25,
    }
    for label, evidence in panels.items():
        if evidence.get("games") != 25 or evidence.get("compared_lines") != 7234:
            raise RuntimeError(f"{label}: panel support changed")
        if evidence.get("identical_games") != expected[label]:
            raise RuntimeError(f"{label}: equality result changed")
    divergent = [
        (row["game_id"], row["first_divergent_turn"])
        for row in panels["readable_disabled_vs_baseline"]["rows"]
        if not row["identical"]
    ]
    if divergent != [(897833045, 79)]:
        raise RuntimeError(f"unexpected activation divergence: {divergent}")

    with tempfile.TemporaryDirectory(prefix="readable-orchard-cost-") as directory:
        temporary = Path(directory)
        compile_results = {}
        for label, record in manifest["sources"].items():
            source = REPO / record["readable_path"]
            binary = temporary / label
            subprocess.run(
                ["rustc", "--edition=2021", "-O", "-Awarnings", "-o", str(binary), str(source)],
                cwd=REPO,
                check=True,
                capture_output=True,
            )
            empty = subprocess.run([str(binary)], input=b"", capture_output=True, timeout=10)
            if empty.returncode != 0 or empty.stdout or empty.stderr:
                raise RuntimeError(f"{label}: empty-input gate failed")
            compile_results[label] = "PASS: optimized compile; empty input exit 0 with zero output"

    manifest["line_inventory"] = line_inventory(
        REPO / manifest["sources"]["with_orchard"]["readable_path"],
        REPO / manifest["sources"]["orchard_stripped"]["readable_path"],
    )
    manifest["verification"] = {
        "sacred_sha256": SACRED_SHA256,
        "readable_compile_empty_input": compile_results,
        "semantic_fixtures": "PASS: all three exact compact parents, 10/10 each",
        "baseline_vs_packet": "PASS: 25/25 games, 7234/7234 commands",
        "disabled_vs_baseline": "PASS: 24/25; only game 897833045 diverges at turn 79",
        "stripped_vs_disabled": "PASS: 25/25 games, 7234/7234 commands",
        "arena_mutation": False,
    }
    manifest["commands"] = {
        "build": "python3 local_codex_1/readable-orchard-code-cost/build_readable_orchard_cost.py --output-dir local_codex_1/readable-orchard-code-cost --manifest local_codex_1/readable-orchard-code-cost/manifest.json --force",
        "verify": "python3 local_codex_1/readable-orchard-code-cost/verify_readable_orchard_cost.py --manifest local_codex_1/readable-orchard-code-cost/manifest.json",
        "panels": "compile the three readable sources, then run claude_1/orchard-code-cost/run_equality_panel.py for baseline/disabled/stripped as recorded in the report",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "verdict": "READABLE_ORCHARD_LOC_VERIFIED",
                "lines_removed": manifest["line_inventory"]["total"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
