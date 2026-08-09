#!/usr/bin/env python3
"""Verify the complete M3a golden bundle, including its generating scripts.

The golden *data* is the frozen D-1 situation JSON.  The extractor, verifier,
tests, source panel, subject candidate, and detector contract are the pinned
trusted toolchain that makes that data reproducible.  A change to any member
invalidates the bundle until the manifest and reviews are deliberately renewed.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

REPO = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO / "chatgpt_1/m3a-golden-set-manifest-v2-2026-08-09.json"


class GoldenSetError(RuntimeError):
    """The committed bundle no longer matches its golden manifest."""


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def load_python_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise GoldenSetError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_artifact(repo: Path, artifact: dict[str, Any]) -> dict[str, str]:
    path = repo / artifact["path"]
    if not path.is_file():
        raise GoldenSetError(f"missing {artifact['role']}: {artifact['path']}")

    actual_blob = git_blob_sha1(path)
    expected_blob = artifact.get("git_blob_sha1")
    if expected_blob and actual_blob != expected_blob:
        raise GoldenSetError(
            f"{artifact['role']} Git blob mismatch: "
            f"expected {expected_blob}, got {actual_blob} ({artifact['path']})"
        )

    actual_sha256 = sha256_file(path)
    expected_sha256 = artifact.get("sha256")
    if expected_sha256 and actual_sha256 != expected_sha256:
        raise GoldenSetError(
            f"{artifact['role']} SHA-256 mismatch: "
            f"expected {expected_sha256}, got {actual_sha256} ({artifact['path']})"
        )

    return {"git_blob_sha1": actual_blob, "sha256": actual_sha256}


def verify_bundle(manifest_path: Path = DEFAULT_MANIFEST, repo: Path = REPO) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "troll-farm-m3a-golden-bundle/v2":
        raise GoldenSetError(f"unsupported manifest schema: {manifest.get('schema')!r}")

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise GoldenSetError("manifest.artifacts must be a non-empty list")

    by_role: dict[str, dict[str, Any]] = {}
    verified: dict[str, dict[str, str]] = {}
    for artifact in artifacts:
        role = artifact.get("role")
        if not isinstance(role, str) or not role:
            raise GoldenSetError("every artifact needs a non-empty role")
        if role in by_role:
            raise GoldenSetError(f"duplicate artifact role: {role}")
        by_role[role] = artifact
        verified[role] = verify_artifact(repo, artifact)

    required_roles = {
        "source_panel",
        "subject_candidate",
        "detector_contract",
        "extractor",
        "golden_output",
        "bundle_verifier",
        "golden_tests",
    }
    missing_roles = sorted(required_roles - by_role.keys())
    if missing_roles:
        raise GoldenSetError(f"manifest missing roles: {missing_roles}")

    extractor_path = repo / by_role["extractor"]["path"]
    extractor = load_python_module(extractor_path, "m3a_extract_from_panel_golden")
    panel_path = repo / by_role["source_panel"]["path"]
    panel = json.loads(panel_path.read_text(encoding="utf-8"))
    library = extractor.build_library(panel)
    extractor.validate(library, panel)

    regenerated = canonical_json(library)
    golden_path = repo / by_role["golden_output"]["path"]
    golden = golden_path.read_text(encoding="utf-8")
    if regenerated != golden:
        raise GoldenSetError(
            "extractor output is not byte-identical to the golden JSON; "
            "renewal requires a reviewed manifest update"
        )

    expected_summary = manifest.get("expected_summary")
    if library.get("summary") != expected_summary:
        raise GoldenSetError(
            "semantic summary mismatch:\n"
            f"expected={json.dumps(expected_summary, sort_keys=True)}\n"
            f"actual={json.dumps(library.get('summary'), sort_keys=True)}"
        )

    source = library.get("source", {})
    expected_source = manifest.get("expected_source")
    if source != expected_source:
        raise GoldenSetError(
            "source provenance mismatch:\n"
            f"expected={json.dumps(expected_source, sort_keys=True)}\n"
            f"actual={json.dumps(source, sort_keys=True)}"
        )

    review_gate = manifest.get("review_gate", {})
    reviewers = review_gate.get("required_reviewers", [])
    if not reviewers or any("reviewer" not in row or "lens" not in row for row in reviewers):
        raise GoldenSetError("manifest must name the required reviewers and review lenses")
    if not review_gate.get("second_machine_execution_required"):
        raise GoldenSetError("golden renewal must require second-machine execution")

    return {
        "schema": manifest["schema"],
        "bundle_status": "VERIFIED",
        "data_members": manifest.get("data_members", []),
        "toolchain_members": manifest.get("toolchain_members", []),
        "summary": library["summary"],
        "verified_artifacts": verified,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--repo", type=Path, default=REPO)
    args = parser.parse_args()
    result = verify_bundle(args.manifest.resolve(), args.repo.resolve())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
