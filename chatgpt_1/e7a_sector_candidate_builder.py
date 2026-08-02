#!/usr/bin/env python3
"""Materialize the frozen E7a initial-sector rule on the strongest resident.

This builder changes exactly one complete source anchor: `MoisanBot::focus_type`.
It does not fit a selector, run a value panel, or touch any existing source artifact.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs"
PARENT_SHA256 = "a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55"
SECTOR_ROWS = ROOT / "chatgpt_1/e7a-initial-sector-sign-preflight-2026-08-02.csv"
DEFAULT_CANDIDATE = ROOT / "cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs"
DEFAULT_MANIFEST = ROOT / "chatgpt_1/e7a-sector-candidate-manifest-2026-08-02.json"

OLD_FOCUS = (
    "fn focus_type(view:&GameState)->PlantKind{"
    "let starts:Vec<Cell> =ortho_neighbors(view.shacks[0]).iter()"
    ".filter(|cell|view.walkable.contains(cell)).copied().collect();"
    "let dist=bfs_distances(&view.walkable,&starts);"
    "[PlantKind::Lemon,PlantKind::Plum].into_iter().min_by_key(|kind|{"
    "view.plants.iter().filter(|plant|plant.kind==*kind)"
    ".map(|plant|dist.get(&plant.cell).copied().unwrap_or(10_000))"
    ".sum::<i32>()}).unwrap_or(PlantKind::Lemon)}"
)

NEW_FOCUS = (
    "fn focus_type(view:&GameState)->PlantKind{"
    "let starts:Vec<Cell> =ortho_neighbors(view.shacks[0]).iter()"
    ".filter(|cell|view.walkable.contains(cell)).copied().collect();"
    "let dist=bfs_distances(&view.walkable,&starts);"
    "let sum=|kind:PlantKind|view.plants.iter().filter(|plant|plant.kind==kind)"
    ".map(|plant|dist.get(&plant.cell).copied().unwrap_or(10_000)).sum::<i32>();"
    "let lemon=sum(PlantKind::Lemon);let plum=sum(PlantKind::Plum);"
    "if lemon<=plum&&plum-lemon<=8{PlantKind::Plum}"
    "else if lemon<=plum{PlantKind::Lemon}else{PlantKind::Plum}}"
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def transform(parent: bytes) -> bytes:
    observed = sha256_bytes(parent)
    if observed != PARENT_SHA256:
        raise ValueError(f"parent SHA-256 mismatch: {observed} != {PARENT_SHA256}")
    old = OLD_FOCUS.encode()
    new = NEW_FOCUS.encode()
    old_count = parent.count(old)
    new_count = parent.count(new)
    if old_count != 1 or new_count != 0:
        raise ValueError(
            f"focus anchor multiplicity invalid: old={old_count}, new={new_count}"
        )
    candidate = parent.replace(old, new, 1)
    if candidate.count(old) != 0 or candidate.count(new) != 1:
        raise ValueError("candidate focus anchor multiplicity invalid")
    if candidate.replace(new, old, 1) != parent:
        raise ValueError("inverse transform does not restore the parent bytes")
    return candidate


def load_sector_rows(path: Path = SECTOR_ROWS) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 60:
        raise ValueError(f"expected 60 sector roots, found {len(rows)}")
    seeds = [int(row["seed"]) for row in rows]
    if sorted(seeds) != list(range(60)) or len(set(seeds)) != 60:
        raise ValueError("sector CSV must contain each seed 0..59 exactly once")
    return rows


def row_is_sector(row: dict[str, Any]) -> bool:
    return (
        row["default_species"].upper() == "LEMON"
        and int(float(row["delta_dist_sum"])) <= 8
    )


def sector_census(rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [row for row in rows if row_is_sector(row)]
    positives = [row for row in selected if int(row["preferred_flip_label"]) == 1]
    nonpositives = [row for row in selected if int(row["preferred_flip_label"]) != 1]
    result = {
        "root_count": len(rows),
        "selected_count": len(selected),
        "selected_positive_count": len(positives),
        "selected_nonpositive_count": len(nonpositives),
        "selected_seeds": [int(row["seed"]) for row in selected],
        "selected_positive_seeds": [int(row["seed"]) for row in positives],
        "selected_nonpositive_seeds": [int(row["seed"]) for row in nonpositives],
        "descriptive_precision": len(positives) / len(selected) if selected else 0.0,
    }
    expected = (60, 13, 10, 3)
    observed = (
        result["root_count"],
        result["selected_count"],
        result["selected_positive_count"],
        result["selected_nonpositive_count"],
    )
    if observed != expected:
        raise ValueError(f"frozen sector census mismatch: {observed} != {expected}")
    return result


def compile_candidate(path: Path) -> dict[str, Any]:
    rustc = shutil.which("rustc")
    if rustc is None:
        raise RuntimeError("rustc is required for candidate materialization")
    with tempfile.TemporaryDirectory(prefix="e7a-sector-compile-") as directory:
        output = Path(directory) / "candidate"
        completed = subprocess.run(
            [rustc, "--edition=2021", "-O", str(path), "-o", str(output)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=180,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                "candidate compilation failed\n"
                + completed.stdout
                + "\n"
                + completed.stderr
            )
        return {
            "rustc": subprocess.run(
                [rustc, "--version"], text=True, capture_output=True, check=True
            ).stdout.strip(),
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "binary_bytes": output.stat().st_size,
        }


def build(candidate_path: Path, manifest_path: Path, *, compile_source: bool) -> dict[str, Any]:
    parent = PARENT.read_bytes()
    candidate = transform(parent)
    rows = load_sector_rows()
    census = sector_census(rows)

    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_path.write_bytes(candidate)

    compilation = compile_candidate(candidate_path) if compile_source else None
    manifest = {
        "schema": "troll-farm-e7a-sector-candidate/1",
        "task": "20260802-e7a-sector-candidate",
        "verdict": "MATERIALIZED_EXACT_SOURCE_TRANSFORM",
        "parent": {
            "path": str(PARENT.relative_to(ROOT)),
            "sha256": PARENT_SHA256,
            "bytes": len(parent),
        },
        "candidate": {
            "path": str(candidate_path.relative_to(ROOT))
            if candidate_path.is_relative_to(ROOT)
            else str(candidate_path),
            "sha256": sha256_bytes(candidate),
            "bytes": len(candidate),
            "delta_bytes": len(candidate) - len(parent),
        },
        "transform": {
            "old_anchor_sha256": sha256_bytes(OLD_FOCUS.encode()),
            "new_anchor_sha256": sha256_bytes(NEW_FOCUS.encode()),
            "old_anchor_count_parent": parent.count(OLD_FOCUS.encode()),
            "new_anchor_count_candidate": candidate.count(NEW_FOCUS.encode()),
            "inverse_exact": candidate.replace(
                NEW_FOCUS.encode(), OLD_FOCUS.encode(), 1
            )
            == parent,
            "changed_function": "MoisanBot::focus_type",
            "other_behavior_changes": False,
        },
        "sector": {
            "rule": "default LEMON and plum_distance_sum - lemon_distance_sum <= 8",
            "distance_source": "BFS from resident shack walkable orthogonal doors",
            "unreachable_penalty": 10_000,
            **census,
        },
        "compilation": compilation,
        "value_qualification": False,
        "arena_authorized": False,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def self_test() -> None:
    parent = PARENT.read_bytes()
    candidate = transform(parent)
    assert candidate != parent
    assert candidate.replace(NEW_FOCUS.encode(), OLD_FOCUS.encode(), 1) == parent
    census = sector_census(load_sector_rows())
    assert census["selected_count"] == 13
    assert census["selected_positive_count"] == 10
    print("self-test: ok")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--skip-compile", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    manifest = build(
        args.candidate,
        args.manifest,
        compile_source=not args.skip_compile,
    )
    print(
        json.dumps(
            {
                "verdict": manifest["verdict"],
                "candidate_sha256": manifest["candidate"]["sha256"],
                "candidate_bytes": manifest["candidate"]["bytes"],
                "selected_roots": manifest["sector"]["selected_count"],
                "selected_positive": manifest["sector"]["selected_positive_count"],
                "compiled": manifest["compilation"] is not None,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
