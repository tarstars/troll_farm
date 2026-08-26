#!/usr/bin/env python3
r"""PEEK follow-on card — build the PICKER PROBE on the CHAMPION (diagnostics only).

Card: `coordination/messages/local_claude_1/20260823T055832Z-20260822-peek-planner-target-map-policy.md`

> **CARD to claude_1:** re-run this classification on the **champion**, over the **989 peek
> encounters** rather than the benching set: for each encounter, the partner's own best candidate
> at that tick and its destination, classified against the contested square. Read-only, probe
> only, no candidate edit.

The coordinator's ruling was measured on cure-C (`ad3bfefe…`, retired) over the 24-situation
BENCHING case set. This builds the same instrument on the champion of record
`candidate-door1-pure-deletion.rs` (`547fa706…`).

## Why this is the SAME instrument and not a re-implementation

The four patch anchors and their replacements are IMPORTED VERBATIM from
`claude_1/picker1/make_picker_probe.py`. Nothing is retyped, so the two probes cannot drift and
the champion rows are comparable to the cure-C rows field for field. All four anchors match
exactly once in the champion source, which is checked here and is the licence for the import:
`select()` is byte-identical between the two subjects in the patched regions.

**Probe only.** The output is `claude_1/peek/probe-champion-picker.rs`, which is never a delivery
candidate and is never submitted. The champion source is not touched.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "picker1"))
import make_picker_probe as P   # noqa: E402  -- the anchors come from here, verbatim

SUBJECT = REPO / "cgauto/submissions/candidate-door1-pure-deletion.rs"
SUBJECT_SHA = "547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0"
OUT = HERE / "probe-champion-picker.rs"

PATCHES = [
    (P.OLD_TURN, P.NEW_TURN, "turn tap"),
    (P.OLD_HEAD, P.NEW_HEAD, "select head"),
    (P.OLD_PAIR, P.NEW_PAIR, "pair loop"),
    (P.OLD_GREEDY, P.NEW_GREEDY, "greedy arm"),
]


def main() -> int:
    src = SUBJECT.read_text()
    got = hashlib.sha256(src.encode()).hexdigest()
    if got != SUBJECT_SHA:
        raise SystemExit(f"REFUSING: champion digest differs\n  want {SUBJECT_SHA}\n  got  {got}")
    out = src
    for old, new, what in PATCHES:
        n = out.count(old)
        if n != 1:
            raise SystemExit(f"REFUSING: {what} anchor matched {n} times in the champion, want 1")
        out = out.replace(old, new)
    OUT.write_text(out)
    print(f"wrote {OUT.relative_to(REPO)}  sha256={hashlib.sha256(out.encode()).hexdigest()}")
    print(f"  patched from {SUBJECT.relative_to(REPO)} sha256={got}")
    print(f"  anchors imported verbatim from claude_1/picker1/make_picker_probe.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
