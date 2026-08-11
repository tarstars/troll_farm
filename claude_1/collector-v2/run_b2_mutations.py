#!/usr/bin/env python3
"""Mutation drive for the B2 S3 client (task `20260811-s3-collector-v2`).

Why this exists: the first version of `tests/test_s3client.py` passed 18/18 while the
implementation was mutated to drop '~' from the RFC 3986 unreserved set. The differential
could not see path encoding, because botocore's S3 signer takes the URL path already
encoded. A suite nobody has tried to break is a suite of unknown strength, so each mutant
below is a signing bug that would produce `SignatureDoesNotMatch` against the real endpoint,
and the drive records which ones the tests catch.

Mechanics live in `mutation_runner.py`, shared with the B3 drive; this file declares only the
mutants. Exit status describes the EXPERIMENT, not just the outcome (the lesson from the
bite-test audit): 0 complete and all caught, 1 control not green, 2 survivors, 3 incomplete.

Usage: python3 claude_1/collector-v2/run_b2_mutations.py --out <results.json>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mutation_runner import run_drive  # noqa: E402

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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="B2 mutation drive")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    return run_drive(drive="b2-s3client-mutations", target=TARGET, tests=TESTS,
                     mutants=MUTANTS, out=Path(args.out))


if __name__ == "__main__":
    sys.exit(main())
