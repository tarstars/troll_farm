#!/usr/bin/env python3
"""Containment for the banana farm on the 34 frozen situations — a READ, not the gate.

Same claim, same method, same code as Candidate 3's `claude_1/cure3/containment.py`: the
**farm-off** arm, with its `MSG` fragment stripped, must be byte-identical in play to the champion,
in both the command stream and the referee state after the last turn. This file does not copy that
script; it imports it and repoints three things — the arm directory (`claude_1/farm`), the decoder
(`narrate8`, because a farm arm speaks v8) and the output name.

**Status: supporting evidence, not the pre-commitment.** The owner retired the 34 frozen fixtures
as gates on 2026-08-26T14:45Z (board row 0-1). The farm's containment gate C1 is stated on the 240
panel games, where the evidence is live. This read is kept because it is nearly free, and because a
disagreement between the two would itself be worth knowing.

    python3 claude_1/farm/containment_farm.py [--arm farmoff|candidate|instrument] [--rule-on]
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "cure3"))
sys.path.insert(0, str(REPO / "claude_1" / "narrate8"))

import containment as C  # noqa: E402
import narrate8 as n8    # noqa: E402

C.HERE = HERE
C.n6 = n8
C.strip_msg = n8.strip_msg

if __name__ == "__main__":
    if "--arm" not in sys.argv:
        sys.argv.extend(["--arm", "farmoff"])
    sys.exit(C.main())
