#!/usr/bin/env python3
"""I-30 measurement ledger (RED stub).

Public API frozen against
`chatgpt_1/schedule-opponent-production-invariant-spec-2026-08-08.md` sections
5 (event ledger) and 6 (per-pair quantities). Bodies are deliberately
unimplemented so the bite-tests fail with `NotImplementedError` (the ledger is
missing) rather than with an import error.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trace_detectors as td  # noqa: E402  (real transcript/command parser)

ITEM_NAMES = td.ITEM_NAMES
PLUM, LEMON, APPLE, BANANA, IRON, WOOD = td.PLUM, td.LEMON, td.APPLE, \
    td.BANANA, td.IRON, td.WOOD

# spec sec. 5.1 frozen score weights (engine.rs recompute_scores / WOOD_POINTS)
SCORE_WEIGHT = (1, 1, 1, 1, 0, 4)

SOURCE_CLASSES = ("ours", "opponent", "natural", "unknown")
OPPONENT_PLAYER = 1
OWN_PLAYER = 0


def score_of(inventory):
    raise NotImplementedError("I-30 ledger: score_of not implemented")


def training_cost(n, talents, iron_present):
    raise NotImplementedError("I-30 ledger: training_cost not implemented")


def sha256_text(text):
    raise NotImplementedError("I-30 ledger: sha256_text not implemented")


class RunRecord:
    """One side of a pair: transcript + command stream + identity hashes."""

    def __init__(self, run_id, transcript_text, commands_text, identity=None,
                 banana_mechanism_claimed=False):
        raise NotImplementedError("I-30 ledger: RunRecord not implemented")


class RunLedger:
    """Per-run opponent accounting (spec sec. 5 / 6)."""

    def __init__(self, **kwargs):
        raise NotImplementedError("I-30 ledger: RunLedger not implemented")


def build_run_ledger(record):
    raise NotImplementedError("I-30 ledger: build_run_ledger not implemented")
