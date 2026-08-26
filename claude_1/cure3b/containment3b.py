#!/usr/bin/env python3
"""Containment for Candidate 3b on the 34 frozen situations — a READ, no longer a gate.

Same claim, same method, same code as Candidate 3's `claude_1/cure3/containment.py`: the rule-off
arm, with its `MSG` fragment stripped, must be byte-identical in play to the champion, in both the
command stream and the referee state after the last turn. This file does not copy that script; it
imports it and repoints three things — the arm directory (`claude_1/cure3b`), the decoder
(`narrate7`, because a 3b arm speaks v7) and the task name.

**Status: supporting evidence, not a pre-commitment.** The owner retired the 34 frozen fixtures as
gates at 2026-08-26T15:45Z (board row 0-1); Candidate 3b's containment pre-commitment is stated on
the 240 panel games instead, where the evidence is live. This read is kept because it is nearly
free and because a disagreement between the two would itself be worth knowing.

    python3 claude_1/cure3b/containment3b.py [--arm ruleoff|candidate|instrument] [--rule-on]
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "cure3"))
sys.path.insert(0, str(REPO / "claude_1" / "narrate7"))

import containment as C  # noqa: E402
import narrate7 as n7    # noqa: E402

C.HERE = HERE
C.n6 = n7
C.strip_msg = n7.strip_msg

if __name__ == "__main__":
    sys.exit(C.main())
