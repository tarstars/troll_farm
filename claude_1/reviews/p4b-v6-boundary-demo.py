#!/usr/bin/env python3
"""F1 repro for the P4b G-1 review: does evaluate() survive a v6 unit tuple?

Feeds p4b_gate.evaluate() a stub narrator returning exactly the 5-field unit tuple that
codex_1's own test_v6_fixture_decoder_contract returns, then the same thing with 4 fields
as a control. Run with --gate pointing at a checkout of codex_1/p4b/p4b_gate.py.

    python3 claude_1/reviews/p4b-v6-boundary-demo.py --gate /path/to/codex_1/p4b
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
import tempfile
import types
from pathlib import Path


class Narrator:
    """Stub decoder; `fields` is the per-unit tuple width under test."""

    def __init__(self, unit):
        self.unit = unit

    def msg_fragments(self, line):
        return [f for f in line.split(";") if f.lstrip().upper().startswith("MSG ")]

    def decode(self, payload):
        return 1, {0: self.unit}, [0], False, {}


class Unit:
    id = 0
    carry = 0
    cell = (0, 0)


class State:
    inventories = [0]

    def own_units(self):
        return [Unit()]

    def plant_at(self, cell):
        return None


class Trace:
    T = 2

    def unit(self, uid, turn):
        return Unit()

    def cmd_of(self, uid, turn):
        return None

    def state(self, turn):
        return State()


def archive(tmpdir: Path) -> Path:
    path = tmpdir / "one-row.jsonl.gz"
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        fh.write(json.dumps({"map_id": "m000", "seat": 0, "artifacts": {
            "candidate_commands": "MSG NARRATE v6 t=1 u0=TREE(3,4)/TREE(3,4)/r=P/b=0/k=2;WAIT\n",
            "candidate_transcript": ""}}) + "\n")
    return path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", type=Path, required=True, help="dir containing p4b_gate.py")
    args = ap.parse_args()
    sys.path.insert(0, str(args.gate.resolve()))
    import p4b_gate as p

    td = types.SimpleNamespace(build_trace=lambda transcript, commands: Trace())
    cases = {
        "v6 (5 fields, the fixture's own tuple)": ("TREE(3,4)", "TREE(3,4)", "P", 0, 2),
        "control (4 fields)": ("TREE(3,4)", "TREE(3,4)", "P", 0),
    }
    with tempfile.TemporaryDirectory() as tmp:
        path = archive(Path(tmp))
        for label, unit in cases.items():
            try:
                result = p.evaluate(path, td, Narrator(unit), "v6")
                print(f"{label}: RETURNED status={result['status']} errors={result['errors']}")
            except Exception as exc:
                print(f"{label}: UNCAUGHT {type(exc).__name__}: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
