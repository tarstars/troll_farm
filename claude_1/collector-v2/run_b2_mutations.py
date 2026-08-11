#!/usr/bin/env python3
"""Mutation drive for the B2 S3 client (task `20260811-s3-collector-v2`).

Why this exists: the first version of `tests/test_s3client.py` passed 18/18 while the
implementation was mutated to drop '~' from the RFC 3986 unreserved set. The differential
could not see path encoding, because botocore's S3 signer takes the URL path already
encoded. A suite nobody has tried to break is a suite of unknown strength, so each mutant
below is a signing bug that would produce `SignatureDoesNotMatch` against the real endpoint,
and the drive records which ones the tests catch.

Exit status describes the EXPERIMENT, not just the outcome (the B4 lesson from the bite-test
audit): 0 = drive complete and every mutant caught, 1 = control suite not green before
mutating, 2 = drive completed with survivors, 3 = drive could not be completed (a mutation
pattern no longer matches the source, so its result would be a silent false pass).

Usage: python3 claude_1/collector-v2/run_b2_mutations.py --out <results.json>
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "s3client.py"
TESTS = HERE / "tests"

# (id, description, exact source text, replacement) — each is a real signer defect.
MUTANTS = [
    # M1 was originally "drop '~' from the safe set". It survived, and the cause was not a
    # weak test: CPython's `urllib.parse.quote` never encodes ALPHA/DIGIT/'_.-~' whatever
    # `safe` says, so the edit changed no behaviour at all. An inert mutant is not a check —
    # it is replaced here by a mutation that really does mis-encode a reserved character.
    ("M1-plus-treated-as-safe",
     "adds '+' to the unreserved set, so '+' in a key is sent literally instead of %2B",
     'return urllib.parse.quote(value, safe=safe + "-_.~")',
     'return urllib.parse.quote(value, safe=safe + "-_.~+")'),
    ("M2-space-as-plus",
     "encodes space as '+' instead of %20",
     'return urllib.parse.quote(value, safe=safe + "-_.~")',
     'return urllib.parse.quote_plus(value, safe=safe + "-_.~")'),
    ("M3-query-unsorted",
     "does not sort query parameters before canonicalising",
     'f"{_quote(k, safe=\'\')}={_quote(str(v), safe=\'\')}" for k, v in sorted(query.items()))',
     'f"{_quote(k, safe=\'\')}={_quote(str(v), safe=\'\')}" for k, v in query.items())'),
    ("M4-headers-not-lowercased",
     "keeps header names as given instead of lowercasing them",
     'lowered = {k.lower(): " ".join(str(v).split()) for k, v in headers.items()}',
     'lowered = {k: " ".join(str(v).split()) for k, v in headers.items()}'),
    ("M5-header-values-not-trimmed",
     "keeps interior whitespace in header values instead of collapsing it",
     'lowered = {k.lower(): " ".join(str(v).split()) for k, v in headers.items()}',
     'lowered = {k.lower(): str(v) for k, v in headers.items()}'),
    ("M6-empty-payload-hash",
     "signs the empty-body hash regardless of the actual body",
     'payload_sha256 = hashlib.sha256(body).hexdigest() if body else EMPTY_SHA256',
     'payload_sha256 = EMPTY_SHA256'),
    ("M7-wrong-scope-order",
     "swaps region and service in the credential scope",
     'scope = f"{datestamp}/{self.region}/{SERVICE}/aws4_request"',
     'scope = f"{datestamp}/{SERVICE}/{self.region}/aws4_request"'),
    ("M8-signing-key-skips-service",
     "omits the service step from the signing-key derivation chain",
     '        key = _sign(key, SERVICE)\n        return _sign(key, "aws4_request")',
     '        return _sign(key, "aws4_request")'),
    ("M9-single-page-list",
     "stops after the first page instead of following continuation tokens",
     '            if truncated.lower() != "true":\n                return out',
     '            return out'),
    ("M10-credentials-mode-unchecked",
     "accepts a world-readable key file",
     '        if mode & 0o077:',
     '        if False and mode & 0o077:'),
]


def run_tests() -> tuple[bool, str]:
    proc = subprocess.run(
        ["uvx", "--with", "boto3", "pytest", str(TESTS), "-q", "--no-header", "-x"],
        capture_output=True, text=True, cwd=HERE.parents[1])
    return proc.returncode == 0, (proc.stdout + proc.stderr)[-600:]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="B2 mutation drive")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    original = TARGET.read_text()
    control_green, control_output = run_tests()
    results = []
    incomplete = []

    if control_green:
        for mutant_id, description, old, new in MUTANTS:
            if original.count(old) != 1:
                incomplete.append(mutant_id)
                results.append({"id": mutant_id, "description": description,
                                "status": "NOT_APPLIED",
                                "reason": f"pattern occurs {original.count(old)} times, expected 1"})
                continue
            TARGET.write_text(original.replace(old, new, 1))
            try:
                green, tail = run_tests()
            finally:
                TARGET.write_text(original)
            results.append({"id": mutant_id, "description": description,
                            "status": "APPLIED",
                            "caught": not green,
                            "test_output_tail": None if not green else tail})

    assert TARGET.read_text() == original, "implementation not restored — refusing to continue"

    applied = [r for r in results if r["status"] == "APPLIED"]
    survivors = [r["id"] for r in applied if not r["caught"]]
    report = {
        "drive": "b2-s3client-mutations",
        "task_id": "20260811-s3-collector-v2",
        "target": str(TARGET.relative_to(HERE.parents[1])),
        "tests": str(TESTS.relative_to(HERE.parents[1])),
        "control_green": control_green,
        "control_output_tail": None if control_green else control_output,
        "mutants_defined": len(MUTANTS),
        "mutants_applied": len(applied),
        "caught": sum(1 for r in applied if r["caught"]),
        "survivors": survivors,
        "not_applied": incomplete,
        "results": results,
    }
    Path(args.out).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("control_green", "mutants_defined", "mutants_applied", "caught",
                       "survivors", "not_applied")}, indent=2))

    if not control_green:
        return 1
    if incomplete:
        return 3
    return 2 if survivors else 0


if __name__ == "__main__":
    sys.exit(main())
