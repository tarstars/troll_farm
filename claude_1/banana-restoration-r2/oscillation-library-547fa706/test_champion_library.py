#!/usr/bin/env python3
"""The accepted M3a library suite, retargeted at the CHAMPION library.

The suite in `../test_oscillation_library.py` was written for the parent-lineage tree and
retargeted once already, at the `98628e98` subject tree, by overriding one class attribute.
This module does the same for the champion tree: the round-trip, index, fail-closed-mutation,
no-best-action and frozen-replay guarantees are the ACCEPTED ones, inherited, not a weaker
copy written here. What is added is the identity block at the bottom -- the champion tree's
own version of the check whose absence caused the defect this card exists to repair: a
library that names a subject and contains situations from a different bot.

    python3 -m unittest test_champion_library
    OSC_LIB_REPLAY=1 PATH=~/.cargo/bin:$PATH python3 -m unittest test_champion_library
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
R2 = HERE.parent
sys.path.insert(0, str(R2))
sys.path.insert(0, str(HERE))

import test_oscillation_library as base      # noqa: E402
import build_subject_library as bsl          # noqa: E402

CHAMP_LIB = HERE / "library"
CHAMP_PANEL_CONFIG = HERE / "panel-config.json"


class TestChampionRoundTrip(base.TestRoundTrip):
    LIB = CHAMP_LIB


class TestChampionIndex(base.TestIndex):
    LIB = CHAMP_LIB


class TestChampionNoBestActionRecorded(base.TestNoBestActionRecorded):
    LIB = CHAMP_LIB


class TestChampionReplay(base.TestFrozenStatesReplay):
    LIB = CHAMP_LIB
    PANEL_CONFIG = CHAMP_PANEL_CONFIG


class TestChampionIdentity(base.LibraryTestBase):
    """A library that names a subject must contain that subject's episodes and no other's."""

    LIB = CHAMP_LIB

    def test_every_situation_was_produced_by_the_champion(self):
        for s in self.situations:
            self.assertEqual(s["provenance"]["bot_source_sha256"], bsl.SUBJECT_SHA256,
                             "%s was not produced by the champion" % s["id"])

    def test_no_situation_came_from_the_old_subject(self):
        for s in self.situations:
            self.assertNotEqual(s["provenance"]["bot_source_sha256"], bsl.OLD_SUBJECT_SHA256,
                                "%s is a `readable__no_orchard` episode" % s["id"])

    def test_index_declares_the_champion_and_the_builder(self):
        self.assertEqual(self.index["subject"]["sha256"], bsl.SUBJECT_SHA256)
        self.assertEqual(self.index["subject"]["run_identity"], "floor")
        self.assertEqual(self.index["builder_sha256"], bsl.BUILDER_SHA256)

    def test_identity_file_covers_every_case_and_matches_the_frozen_payloads(self):
        ident = json.loads((HERE / "identity.json").read_text())
        self.assertEqual(ident["library_sha256"], self.index["library_sha256"])
        by_id = {c["id"]: c for c in ident["cases"]}
        self.assertEqual(sorted(by_id), sorted(s["id"] for s in self.situations))
        for s in self.situations:
            rec = by_id[s["id"]]
            self.assertEqual(rec["content_sha256"], s["content_sha256"])
            self.assertEqual(rec["window_commands_sha256"],
                             bsl._sha(bsl._canonical_commands(s["window"])))
            self.assertEqual(rec["entry_state_sha256"],
                             bsl._sha(bsl._canonical_entry(s["world_state_at_entry"])))

    def test_identity_digests_reject_a_bent_payload(self):
        """A digest that cannot fail is not a digest."""
        s = json.loads(json.dumps(self.situations[0]))
        rec = {c["id"]: c for c in
               json.loads((HERE / "identity.json").read_text())["cases"]}[s["id"]]
        s["window"]["commands"][0]["line"] = "WAIT"
        self.assertNotEqual(bsl._sha(bsl._canonical_commands(s["window"])),
                            rec["window_commands_sha256"])
        s2 = json.loads(json.dumps(self.situations[0]))
        s2["world_state_at_entry"]["units"][0][2] += 1
        self.assertNotEqual(bsl._sha(bsl._canonical_entry(s2["world_state_at_entry"])),
                            rec["entry_state_sha256"])

    def test_every_case_is_gate_ready(self):
        """`fixture_harness.episode_identity` needs frozen commands AND an entry board whose
        turn is the window's first turn. A case missing either cannot be checked at all."""
        ident = json.loads((HERE / "identity.json").read_text())
        self.assertEqual(ident["gate_ready_count"], ident["case_count"])


if __name__ == "__main__":
    unittest.main()
