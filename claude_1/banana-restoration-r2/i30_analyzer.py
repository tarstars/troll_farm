#!/usr/bin/env python3
"""I-30 paired analyzer (RED stub).

Public API frozen against
`chatgpt_1/schedule-opponent-production-invariant-spec-2026-08-08.md` sections
3 (pair identity), 6 (per-pair quantities), 8 (status model), 9 (aggregate
report) and 11 (bound freeze). Bodies are deliberately unimplemented so the
bite-tests fail with `NotImplementedError` (the analyzer is missing) rather
than with an import error.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import i30_ledger as ledger  # noqa: E402,F401

# spec sec. 8 status model
NOT_APPLICABLE = "NOT_APPLICABLE"
UNPROVEN = "UNPROVEN"
GATE_UNREADY = "GATE_UNREADY"
PASS = "PASS"
FAIL = "FAIL"
MEASURED_UNTHRESHOLDED = "MEASURED_UNTHRESHOLDED"

# spec sec. 3: every field a pair must share exactly
SHARED_IDENTITY_FIELDS = (
    "map_sha256", "seat", "opponent_source_sha256", "opponent_binary_sha256",
    "opponent_config_sha256", "engine_sha256", "initial_state_sha256",
    "rng_seed", "turn_cap", "termination_rule", "toolchain_sha256",
    "harness_sha256", "analyzer_config_sha256", "detector_config_sha256",
)
# spec sec. 3: the only allowed difference (and, in a declared self-pair,
# these must be equal too)
PAIR_VARIABLE_FIELDS = (
    "bot_source_sha256", "bot_binary_sha256", "command_stream_sha256",
)


class Bound:
    """Hash-pinned owner-frozen bound object (spec sec. 11)."""

    def __init__(self, spec, pinned_sha256=None):
        raise NotImplementedError("I-30 analyzer: Bound not implemented")


def compute_schedule_windfall(d_schedule, d_train):
    """SCHEDULE_WINDFALL = D_SCHEDULE - D_TRAIN (spec sec. 6).

    Resolved through the module namespace by `analyze_pair` so bite-test 15
    can delete the indirect-production calculation and observe the blind-spot
    fixture stop biting.
    """
    raise NotImplementedError(
        "I-30 analyzer: compute_schedule_windfall not implemented")


def check_pair_identity(candidate, parent, self_pair=False):
    raise NotImplementedError(
        "I-30 analyzer: check_pair_identity not implemented")


def detect_activation(candidate, parent):
    raise NotImplementedError(
        "I-30 analyzer: detect_activation not implemented")


def analyze_pair(candidate, parent, bound=None, self_pair=False,
                 banana_mechanism_claimed=None, pair_id=None):
    raise NotImplementedError("I-30 analyzer: analyze_pair not implemented")


def aggregate_report(pair_results, bound=None, manifest=None):
    raise NotImplementedError("I-30 analyzer: aggregate_report not implemented")
