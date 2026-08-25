"""`ExecutionValidity` must check a run against a reviewed artifact, not itself.

`chatgpt_1`'s I-30 revision 3 review (`20260811T235000Z`), trust-root blocker 1:

    `ExecutionValidity` validates a harness's self-declaration; it does not
    bind the run to a reviewed referee artifact, derive the verb manifest from
    that dispatcher, or derive executed counts from per-command events. A
    self-consistent silent discard can still pass.

Every clause it had was self-consistent by construction:

* `referee_sha256` was checked for **presence**, so any 64 hex characters passed;
* `verb_manifest_sha256` was checked against **the caller's own manifest**, so it
  could not disagree with itself;
* `commands_emitted` / `commands_executed` were **caller-supplied integers**, so a
  harness that silently discarded a command and reported them equal passed.

The headline case is the last one, and it is the `m040` signature: the referee
accepts a line, produces no effect, reports no error. These tests build exactly
that declaration and assert it is refused.

Run:  python3 -m unittest test_i30_execution_trust_root
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import i30_ledger as ledger  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTRY_PATH = os.path.join(HERE, "i30", "reviewed_referees.json")

COMMANDS = "MOVE 0 3 3\nHARVEST 0\n"


def registry() -> dict:
    with open(REGISTRY_PATH, encoding="utf-8") as fh:
        return json.load(fh)["referees"]


def reviewed_digest() -> str:
    return sorted(registry())[0]


def declaration(**overrides) -> dict:
    """A declaration that is complete, honest and reviewed."""
    entry = registry()[reviewed_digest()]
    events = [{"turn": 1, "verb": "MOVE", "executed": True},
              {"turn": 2, "verb": "HARVEST", "executed": True}]
    out = {
        "execution_status": ledger.EXECUTION_OK,
        "commands_emitted": 2,
        "commands_executed": 2,
        "unsupported_command_events": 0,
        "malformed_command_events": 0,
        "verb_manifest": list(entry["verb_manifest"]),
        "verb_manifest_sha256": ledger.verb_manifest_sha256(entry["verb_manifest"]),
        "command_events": events,
        "referee_sha256": reviewed_digest(),
        "engine_sha256": "e" * 64,
        "instrument_version": "fuzz-panel/5-two-player-phase-merged-referee",
        "corpus_version": "c5-two-player-phase-merged-2026-08-11",
    }
    out.update(overrides)
    return out


class ExecutionTrustRoot(unittest.TestCase):
    def ev(self, **overrides):
        return ledger.ExecutionValidity(declaration(**overrides), COMMANDS,
                                        registry=registry())

    # -- control ---------------------------------------------------------
    def test_an_honest_reviewed_run_is_valid(self):
        """Without this the refusals below could be refusing everything."""
        ev = self.ev()
        self.assertEqual(ev.reasons, [])
        self.assertTrue(ev.valid)
        self.assertEqual(ev.trust_root, "reviewed_referee_registry")

    # -- the headline defect ---------------------------------------------
    def test_a_silent_discard_is_refused_even_when_the_harness_agrees_with_itself(self):
        """The m040 signature: one command produced no effect, and the harness
        reports emitted == executed == 2. The integers are self-consistent; the
        events say otherwise, and the events win."""
        events = [{"turn": 1, "verb": "MOVE", "executed": True},
                  {"turn": 2, "verb": "HARVEST", "executed": False}]
        ev = self.ev(command_events=events)
        self.assertFalse(ev.valid)
        self.assertIn("command_counts_not_derived_from_events", ev.reasons)
        self.assertEqual(ev.derived_counts,
                         {"commands_emitted": 2, "commands_executed": 1})

    def test_counts_must_come_from_events_at_all(self):
        ev = self.ev(command_events=None)
        self.assertFalse(ev.valid)
        self.assertIn("command_events_absent", ev.reasons)

    # -- binding to a reviewed artifact ----------------------------------
    def test_an_unreviewed_referee_is_refused_however_well_formed(self):
        ev = self.ev(referee_sha256="a" * 64)
        self.assertFalse(ev.valid)
        self.assertIn("referee_not_in_reviewed_registry", ev.reasons)

    # -- deriving rather than trusting -----------------------------------
    def test_a_manifest_the_referee_does_not_implement_is_refused(self):
        """Self-consistency is not evidence: the caller hashes its own list, so
        the declaration agrees with itself while disagreeing with the referee."""
        bogus = ["MOVE", "HARVEST", "TELEPORT"]
        ev = self.ev(verb_manifest=bogus,
                     verb_manifest_sha256=ledger.verb_manifest_sha256(bogus))
        self.assertFalse(ev.valid)
        self.assertIn("verb_manifest_not_derived_from_referee", ev.reasons)

    def test_dropping_a_verb_the_referee_implements_is_also_refused(self):
        entry = registry()[reviewed_digest()]
        short = [v for v in entry["verb_manifest"] if v != "MINE"]
        ev = self.ev(verb_manifest=short,
                     verb_manifest_sha256=ledger.verb_manifest_sha256(short))
        self.assertFalse(ev.valid)
        self.assertIn("verb_manifest_not_derived_from_referee", ev.reasons)

    # -- the pre-repair behaviour, stated as a test ----------------------
    def test_without_a_registry_the_same_declaration_is_self_declared(self):
        """The old trust model, kept only for fixtures — and it now SAYS so, so
        a fixture verdict can never be read as a production one."""
        events = [{"turn": 1, "verb": "MOVE", "executed": True},
                  {"turn": 2, "verb": "HARVEST", "executed": False}]
        ev = ledger.ExecutionValidity(declaration(command_events=events,
                                                  referee_sha256="a" * 64),
                                      COMMANDS)
        self.assertEqual(ev.trust_root, "self_declared_unverified")
        self.assertTrue(ev.valid,
                        "pre-repair: a silent discard under an unreviewed "
                        "referee passed, which is the defect being closed")


class RegistryIsDerived(unittest.TestCase):
    """The registry must be a projection of the referee, not a hand-list."""

    def test_the_registry_still_derives_from_its_pinned_blobs(self):
        proc = subprocess.run(
            [sys.executable, os.path.join(HERE, "i30", "derive_referee_manifest.py"),
             "--check"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_the_reviewed_referee_is_the_accepted_r4_panel(self):
        """The digest in the registry must be the one the r4 acceptance and the
        B1 closure name, or this binds runs to the wrong artifact."""
        self.assertIn(
            "d8900abf31dd030d07096e9a063365aa0e1f58b85a1613d02b07d3935c523a6a",
            registry())


if __name__ == "__main__":
    unittest.main()
