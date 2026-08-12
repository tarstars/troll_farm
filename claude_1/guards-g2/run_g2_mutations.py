#!/usr/bin/env python3
"""G2 — negative controls for the transport suite (task `20260810-guards-that-cannot-fail`).

The question the sub-item asks: **of the 96 tests guarding `inbox_sweep.py` and
`lint_outbox.py`, which actually fail when their subject is broken?** Those tests were written
by the same agent that wrote the tooling, so "they pass" carries no independent information
until something has tried to make them fail.

Measured against **trunk** (`origin/main`) in a detached worktree, not against my branch: the
transport tooling everyone actually runs is trunk's, and the publish gate is trunk's exit
status. The subject files are restored from an in-memory copy after every mutant, and the drive
refuses to report if restoration did not happen.

## Sampling rule, stated because the task requires it

This is a **targeted** pass, not exhaustive mutation. Mutants are chosen so that every
functional area of each subject carries at least one, and within an area they prefer the edit
whose failure would be **silent** — a wrong count, a skipped check, a swallowed error — over
one that would crash loudly and be noticed anyway. Concretely, for `inbox_sweep.py`: authority
selection (which refs count), addressee matching, ack discharge, quarantine handling, the
legacy-baseline path, and exit status. For `lint_outbox.py`: schema validation, artifact
verification, sender/namespace checks, and exit status. A mutant that no test catches is
reported as a **gap in the suite**, not as a defect in the tooling — the tooling may well be
correct; the point is that nothing would tell us if it stopped being so.

Usage: python3 claude_1/guards-g2/run_g2_mutations.py --worktree <path-to-main> --out-dir <dir>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "collector-v2"))

from mutation_runner import run_drive  # noqa: E402

TESTS = ["tests/test_inbox_sweep.py", "tests/test_lint_outbox.py"]

# (id, area, description, old, new) — anchors read from trunk's source, each verified unique.
SWEEP_MUTANTS = [
    ("S1-authority-includes-local-refs", "authority selection",
     "treats local branches as authoritative, so unpushed messages count as delivered",
     'REMOTE_PREFIX = "refs/remotes/origin/"', 'REMOTE_PREFIX = "refs/heads/"'),
    ("S2-roster-from-wrong-ref", "quarantine/roster authority",
     "reads the roster from a branch instead of trunk — the exact defect the comment above it "
     "describes, where a ref with no quarantine suppressed nothing and reported zero errors",
     'ROSTER_REF = REMOTE_PREFIX + "main"',
     'ROSTER_REF = REMOTE_PREFIX + "agent/local_claude_1"'),
    ("S3-ack-required-ignores-yaml", "ack discharge",
     "ignores the v2 requires_ack field, honouring only the legacy line and the kind default",
     'return yaml_required is True or legacy_required or kind in ACK_REQUIRED_KINDS',
     'return legacy_required or kind in ACK_REQUIRED_KINDS'),
    ("S4-ack-required-ignores-legacy", "ack discharge",
     "ignores the legacy `Requires acknowledgement: yes` line, so pre-v2 obligations vanish",
     'return yaml_required is True or legacy_required or kind in ACK_REQUIRED_KINDS',
     'return yaml_required is True or kind in ACK_REQUIRED_KINDS'),
    ("S5-exit-zero-when-unacknowledged", "exit status",
     "exits 0 with outstanding acknowledgements, so the inbox gate can never fail",
     '    return 1 if unacked else 0', '    return 0'),
    ("S6-transport-break-not-signalled", "exit status",
     "drops the exit-2 transport-broken signal, hiding delivery errors behind a clean exit",
     '    if transport_broken:\n        return 2', '    if False:\n        return 2'),
    ("S7-schema-version-parse-lenient", "schema validation",
     "reports a non-integer schema_version as legacy instead of an error",
     '        return 2, f"schema_version is not an integer: {raw!r}"', '        return 0, None'),
]

LINT_MUTANTS = [
    ("L1-exit-zero-with-errors", "exit status",
     "exits 0 even with lint errors — the publish gate is the exit status, so this removes it",
     '    return 2 if errors else 0', '    return 0'),
    ("L2-wrong-branch-not-flagged", "publish-branch check",
     "stops warning that publishing from a non-canonical branch is undelivered (finding F9b, "
     "the cause of three real quarantine entries)",
     '    if unpublished and branch and branch != canonical_branch:',
     '    if False and unpublished and branch and branch != canonical_branch:'),
    ("L3-immutable-collision-ignored", "immutability",
     "accepts a path whose bytes differ across authoritative refs (finding TQ-6)",
     '            if len(per_path[path]) != 1:', '            if False:'),
    ("L4-republish-with-new-bytes-allowed", "immutability",
     "lets an already-published message be edited in place instead of demanding a correction",
     '            if text not in published_bodies(per_path, path):', '            if False:'),
    ("L5-deletion-not-detected", "immutability",
     "stops noticing that the proposed tree deletes a published message (finding TQ-4)",
     '        if path not in tree:', '        if False:'),
    ("L6-foreign-file-accepted", "namespace validation",
     "accepts any filename in the outbox namespace, not just canonical message names",
     '        if kind == "foreign":', '        if False:'),
]

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="G2 transport-suite negative controls")
    ap.add_argument("--worktree", required=True, help="detached checkout of origin/main")
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args(argv)

    repo = Path(args.worktree)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    codes = []
    for name, subject, mutants in (
            ("g2-inbox-sweep", repo / "scripts/inbox_sweep.py", SWEEP_MUTANTS),
            ("g2-lint-outbox", repo / "scripts/lint_outbox.py", LINT_MUTANTS)):
        code = run_drive(drive=name, target=subject,
                         tests=[repo / t for t in TESTS],
                         mutants=[(m[0], f"[{m[1]}] {m[2]}", m[3], m[4]) for m in mutants],
                         out=out / f"{name}-results.json", repo=repo)
        codes.append(code)
        print(f"{name}: exit {code}")

    print(json.dumps({"drives": codes}, indent=2))
    return max(codes)


if __name__ == "__main__":
    sys.exit(main())
