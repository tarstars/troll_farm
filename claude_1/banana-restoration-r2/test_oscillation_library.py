#!/usr/bin/env python3
"""Tests for the frozen oscillation situation library (manifest item M3a).

Run:  python3 -m unittest test_oscillation_library -v
      (python3.12 stdlib only; no pytest)

Four obligations, from the item:

  1. the loader round-trips every situation;
  2. hash verification catches a mutated fixture -- **demonstrated** on a
     scratch copy that is really mutated, not asserted in prose;
  3. the classification of the named cases matches the mechanism analysis;
  4. the index count equals the file count.

Plus one guard the item's purpose demands: **nothing in this library records
what the best action was.**  That judgement is M3b; recording it here, derived
from the same scorer that produced the oscillation, would poison M3b with the
circularity it exists to avoid.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import oscillation_library as ol

HERE = Path(__file__).resolve().parent
LIB = HERE / "oscillation-library"


class LibraryTestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.situations = ol.load_library(LIB)
        cls.index = ol.load_index(LIB)

    def situation(self, **criteria):
        hits = ol.find(self.situations, **criteria)
        self.assertTrue(hits, "no situation matches %r" % (criteria,))
        return hits

    def episode_of(self, map_id, seat, unit, turn_start):
        """The frozen situation whose multiplicity list contains this episode.

        Deduplication keeps one representative per (mechanism, geometry), so a
        named episode may be a member rather than the representative.
        """
        for s in self.situations:
            for m in s["multiplicity"]["members"]:
                if (m.get("map_id") == map_id and m.get("seat") == seat
                        and m.get("unit") == unit
                        and m.get("turn_start") == turn_start):
                    return s, m
        self.fail("no frozen situation contains episode %s s%d u%d @t%d"
                  % (map_id, seat, unit, turn_start))


# ---------------------------------------------------------------------------
# 1. round-trip
# ---------------------------------------------------------------------------

class TestRoundTrip(LibraryTestBase):

    def test_every_situation_loads(self):
        self.assertGreater(len(self.situations), 0)
        for s in self.situations:
            self.assertEqual(s["schema"], ol.SCHEMA_SITUATION)
            self.assertIn(s["kind"], ol.KINDS)

    def test_round_trip_through_json_preserves_the_digest(self):
        """Serialize -> parse -> rehash must be a fixed point.  If it is not,
        the digest is a property of the file's formatting rather than of the
        data, and the freeze is worthless."""
        for s in self.situations:
            again = json.loads(json.dumps(s, sort_keys=True, indent=1))
            self.assertEqual(ol.payload_sha256(again), s["content_sha256"],
                             "%s does not round-trip" % s["id"])

    def test_round_trip_is_stable_under_key_reordering(self):
        for s in self.situations:
            shuffled = dict(reversed(list(s.items())))
            self.assertEqual(ol.payload_sha256(shuffled), s["content_sha256"])

    def test_every_full_situation_carries_a_literal_replayable_state(self):
        """A frozen situation must be re-derivable without the map generator:
        literal rows, literal plants, literal units of BOTH players, literal
        inventories."""
        for s in self.situations:
            if s["completeness"] != "FULL":
                continue
            rows = s["static_map_rows"]
            self.assertTrue(rows and all(isinstance(r, str) for r in rows))
            self.assertEqual(len(rows), s["provenance"]["map_height"])
            for state_key in ("world_state_at_entry", "initial_world_state"):
                st = s[state_key]
                self.assertIn("plants", st)
                self.assertIn("units", st)
                self.assertEqual(len(st["inventories"]["own"]), 6)
                self.assertEqual(len(st["inventories"]["opponent"]), 6)
                self.assertTrue(st["units"], "%s has no units" % s["id"])
                for u in st["units"]:
                    self.assertEqual(len(u), 14, "unit row is not wire-shaped")
                self.assertTrue(any(u[1] == 0 for u in st["units"]))
                self.assertTrue(any(u[1] == 1 for u in st["units"]),
                                "%s: opponent units are missing" % s["id"])
            self.assertEqual(s["world_state_at_entry"]["turn"],
                             s["window"]["turn_start"])
            self.assertEqual(s["initial_world_state"]["turn"], 1)

    def test_every_situation_records_its_provenance(self):
        for s in self.situations:
            p = s["provenance"]
            for field in ol.REQUIRED_PROVENANCE_FIELDS:
                self.assertIn(field, p)
            self.assertRegex(p["bot_source_sha256"], r"^[0-9a-f]{64}$")

    def test_every_situation_carries_its_observed_command_window(self):
        for s in self.situations:
            cmds = s["window"]["commands"]
            self.assertTrue(cmds, "%s froze no command window" % s["id"])
            turns = [c["turn"] for c in cmds]
            self.assertEqual(turns, sorted(turns))
            self.assertTrue(all(isinstance(c["line"], str) for c in cmds))

    def test_every_situation_states_what_is_unresolved(self):
        for s in self.situations:
            self.assertTrue(s["unresolved"],
                            "%s claims nothing is unresolved" % s["id"])


# ---------------------------------------------------------------------------
# 2. hash verification fails closed -- DEMONSTRATED
# ---------------------------------------------------------------------------

class TestIntegrityFailsClosed(unittest.TestCase):
    """Each test really mutates a scratch copy of the library and shows the
    loader refusing it.  Nothing here asserts a property in the abstract."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="osclib-"))
        self.dir = self.tmp / "oscillation-library"
        shutil.copytree(LIB, self.dir)
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.target = sorted(self.dir.glob("OSC-*.json"))[0]

    def write(self, path, doc):
        path.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")

    def test_the_unmutated_copy_loads(self):
        """Control: without this, every test below could pass vacuously."""
        self.assertTrue(ol.load_library(self.dir))

    def test_mutating_a_frozen_world_state_is_caught(self):
        doc = json.loads(self.target.read_text())
        before = doc["world_state_at_entry"]["units"][0][2]
        doc["world_state_at_entry"]["units"][0][2] = before + 1   # move a unit
        self.write(self.target, doc)
        with self.assertRaises(ol.IntegrityError) as ctx:
            ol.load_library(self.dir)
        self.assertIn("content hash mismatch", str(ctx.exception))
        self.assertIn(doc["id"], str(ctx.exception))

    def test_mutating_the_classification_is_caught(self):
        doc = json.loads(self.target.read_text())
        doc["classification"]["mechanism"] = (
            "M3" if doc["classification"]["mechanism"] != "M3" else "M1")
        self.write(self.target, doc)
        with self.assertRaises(ol.IntegrityError):
            ol.load_library(self.dir)

    def test_mutating_a_single_command_line_is_caught(self):
        doc = json.loads(self.target.read_text())
        doc["window"]["commands"][0]["line"] += " "
        self.write(self.target, doc)
        with self.assertRaises(ol.IntegrityError):
            ol.load_library(self.dir)

    def test_a_self_consistent_forgery_is_caught_by_the_index(self):
        """The interesting case: an editor who also recomputes the file's own
        digest.  The index still holds the frozen value."""
        doc = json.loads(self.target.read_text())
        doc["world_state_at_entry"]["inventories"]["own"][0] += 7
        doc.pop("content_sha256")
        doc["content_sha256"] = ol.payload_sha256(doc)
        self.write(self.target, doc)
        with self.assertRaises(ol.IntegrityError) as ctx:
            ol.load_library(self.dir)
        self.assertIn("index records", str(ctx.exception))

    def test_a_forgery_consistent_with_the_index_is_caught_by_library_hash(self):
        """... and an editor who also rewrites the index entry still trips the
        library-wide hash."""
        doc = json.loads(self.target.read_text())
        doc["world_state_at_entry"]["inventories"]["own"][0] += 7
        doc.pop("content_sha256")
        doc["content_sha256"] = ol.payload_sha256(doc)
        self.write(self.target, doc)
        index = json.loads((self.dir / "index.json").read_text())
        for entry in index["situations"]:
            if entry["id"] == doc["id"]:
                entry["content_sha256"] = doc["content_sha256"]
        self.write(self.dir / "index.json", index)
        with self.assertRaises(ol.IntegrityError) as ctx:
            ol.load_library(self.dir)
        self.assertIn("library hash mismatch", str(ctx.exception))

    def test_deleting_a_situation_file_is_caught(self):
        self.target.unlink()
        with self.assertRaises(ol.IntegrityError) as ctx:
            ol.load_library(self.dir)
        self.assertIn("does not match the index", str(ctx.exception))

    def test_adding_an_unindexed_situation_file_is_caught(self):
        shutil.copy(self.target, self.dir / "OSC-999.json")
        with self.assertRaises(ol.IntegrityError) as ctx:
            ol.load_library(self.dir)
        self.assertIn("does not match the index", str(ctx.exception))

    def test_tampering_with_the_declared_count_is_caught(self):
        index = json.loads((self.dir / "index.json").read_text())
        index["situation_count"] += 1
        self.write(self.dir / "index.json", index)
        with self.assertRaises(ol.IntegrityError) as ctx:
            ol.load_library(self.dir)
        self.assertIn("situation_count", str(ctx.exception))

    def test_tampering_with_the_library_hash_is_caught(self):
        index = json.loads((self.dir / "index.json").read_text())
        index["library_sha256"] = "0" * 64
        self.write(self.dir / "index.json", index)
        with self.assertRaises(ol.IntegrityError):
            ol.load_library(self.dir)

    def test_a_situation_that_loses_its_provenance_is_rejected(self):
        doc = json.loads(self.target.read_text())
        doc["provenance"].pop("bot_source_sha256")
        doc.pop("content_sha256")
        doc["content_sha256"] = ol.payload_sha256(doc)
        index = json.loads((self.dir / "index.json").read_text())
        for entry in index["situations"]:
            if entry["id"] == doc["id"]:
                entry["content_sha256"] = doc["content_sha256"]
        index["library_sha256"] = ol.library_sha256(index["situations"])
        self.write(self.target, doc)
        self.write(self.dir / "index.json", index)
        with self.assertRaises(ol.IntegrityError) as ctx:
            ol.load_library(self.dir)
        self.assertIn("provenance", str(ctx.exception))

    def test_a_full_situation_that_loses_its_world_state_is_rejected(self):
        doc = json.loads(self.target.read_text())
        self.assertEqual(doc["completeness"], "FULL")
        doc["world_state_at_entry"] = None
        doc.pop("content_sha256")
        doc["content_sha256"] = ol.payload_sha256(doc)
        index = json.loads((self.dir / "index.json").read_text())
        for entry in index["situations"]:
            if entry["id"] == doc["id"]:
                entry["content_sha256"] = doc["content_sha256"]
        index["library_sha256"] = ol.library_sha256(index["situations"])
        self.write(self.target, doc)
        self.write(self.dir / "index.json", index)
        with self.assertRaises(ol.IntegrityError) as ctx:
            ol.load_library(self.dir)
        self.assertIn("no world state", str(ctx.exception))

    def test_the_cli_reports_failure_with_a_nonzero_status(self):
        doc = json.loads(self.target.read_text())
        doc["window"]["turn_start"] += 1
        self.write(self.target, doc)
        self.assertEqual(ol.main(["--dir", str(self.dir)]), 1)


# ---------------------------------------------------------------------------
# 3. classification of the named cases
# ---------------------------------------------------------------------------

class TestNamedCases(LibraryTestBase):
    """The mechanism analysis
    `oscillation-attack-claude_1-2026-08-09.md` names four cases.  The frozen
    classification must agree with it, or one of the two is wrong."""

    def test_m110_seat1_is_M1_with_an_idle_blocker(self):
        """1.2: a width-1 corridor, an idle partner standing in it, and a
        mover whose action space excludes standing still."""
        s, m = self.episode_of("m110", 1, 0, 6)
        self.assertEqual(s["classification"]["mechanism"], "M1")
        self.assertEqual(s["classification"]["blocker_state"], "IDLE")
        self.assertEqual(m["turn_end"], 200)
        self.assertEqual(m["length_turns"], 195)
        blocker = s["classification"]["blocker"]
        self.assertEqual(blocker["unit"], 2)
        self.assertEqual(blocker["cell_at_entry"], [4, 2])
        self.assertIsNone(blocker["plant_on_cell_at_entry"])
        self.assertEqual(blocker["distinct_cells_in_window"], 1)
        self.assertEqual(blocker["wait_fraction_in_window"], 1.0)

    def test_m110_geometry_is_the_published_R6a_fixture(self):
        """The literal state must equal the fixture published in section 6 of
        the mechanism analysis.  This is the anti-drift assertion: if the map
        generator changes, this test still holds, because nothing here is
        generated."""
        s, _ = self.episode_of("m110", 1, 0, 6)
        self.assertEqual(s["static_map_rows"], [
            "#############",
            "#1.##########",
            "#...........0",
            "#############",
            "#############"])
        self.assertEqual(s["initial_world_state"]["units"], [
            [0, 0, 11, 2, 1, 2, 1, 1, 0, 0, 0, 0, 0, 0],
            [2, 0, 4, 2, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0],
            [5, 1, 1, 2, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0]])
        self.assertEqual(s["initial_world_state"]["plants"],
                         [["BANANA", 2, 2, 4, 6, 1, 48]])
        self.assertEqual(s["initial_world_state"]["inventories"]["own"],
                         [0, 0, 0, 2, 0, 0])
        self.assertEqual(s["provenance"]["map_class"], "choke_corridor")
        self.assertEqual(s["provenance"]["opponent_profile"], "harvester")

    def test_m040_seat1_is_M1_with_a_working_blocker(self):
        """1.5: the clean short case -- unit 0 bounces for exactly the turns
        the TRAIN-spawned peer needs to finish its chop."""
        s, m = self.episode_of("m040", 1, 0, 80)
        self.assertEqual(s["classification"]["mechanism"], "M1")
        self.assertEqual(s["classification"]["blocker_state"], "WORKING")
        self.assertEqual([m["turn_start"], m["turn_end"]], [80, 86])
        self.assertEqual(s["window"]["cells"], [[4, 0], [3, 0]])
        blocker = s["classification"]["blocker"]
        self.assertEqual(blocker["unit"], 6)
        self.assertIn("CHOP", blocker["non_wait_verbs_in_window"])
        self.assertFalse(blocker["idle_by_analysis_criterion"])

    def test_the_two_named_cases_differ_exactly_in_the_blocker(self):
        """The idle/working split is the distinction the item asks the library
        to carry: same mechanism, opposite blocker, 195 turns vs 7."""
        long_s, long_m = self.episode_of("m110", 1, 0, 6)
        short_s, short_m = self.episode_of("m040", 1, 0, 80)
        self.assertEqual(long_s["classification"]["mechanism"],
                         short_s["classification"]["mechanism"])
        self.assertNotEqual(long_s["classification"]["blocker_state"],
                            short_s["classification"]["blocker_state"])
        self.assertGreater(long_m["length_turns"],
                           25 * short_m["length_turns"])

    def test_m014_seat1_is_M2_an_idle_peer_on_the_target_plant(self):
        """1.4(b): the peer stands on the goal cell emitting WAIT, and
        `compatible` never sees it because `Target::None` is universally
        compatible."""
        s, m = self.episode_of("m014", 1, 2, 7)
        self.assertEqual(s["classification"]["mechanism"], "M2")
        self.assertEqual(s["classification"]["blocker_state"], "IDLE")
        blocker = s["classification"]["blocker"]
        self.assertEqual(blocker["unit"], 0)
        self.assertEqual(blocker["cell_at_entry"], [10, 0])
        self.assertIsNotNone(blocker["plant_on_cell_at_entry"])
        self.assertEqual(blocker["plant_on_cell_at_entry"][0], "BANANA")
        self.assertEqual(blocker["wait_fraction_in_window"], 1.0)
        self.assertEqual(m["turn_end"], 200)

    def test_m085_seat0_is_M3_a_scorer_cycle_with_one_own_unit(self):
        """1.3 / Theorem 2: a single own unit, so the mover's detour branch
        cannot fire and the goal itself must be alternating.  The supporting
        observable for the door-pricing reading is that one of the two cells
        is an own shack door."""
        s, m = self.episode_of("m085", 0, 0, 17)
        self.assertEqual(s["classification"]["mechanism"], "M3")
        self.assertEqual(s["classification"]["blocker_state"], "NONE")
        self.assertIsNone(s["classification"]["blocker"])
        self.assertEqual(s["classification"]["all_own_peers_at_entry"], [])
        own = [u for u in s["world_state_at_entry"]["units"] if u[1] == 0]
        self.assertEqual(len(own), 1, "M3 requires a single own unit")
        self.assertEqual(
            s["classification"]["shack_door_evidence"][
                "cells_that_are_own_shack_doors"], [[1, 4]])
        self.assertEqual([m["turn_start"], m["turn_end"]], [17, 23])

    def test_the_real_corpus_episode_is_frozen_as_partial_not_invented(self):
        """B3.4's arena evidence cites raw games under the git-ignored
        data/external.  The situation must say so rather than manufacture a
        world state."""
        hits = ol.find(self.situations, kind="REAL_CORPUS")
        self.assertTrue(hits)
        for s in hits:
            self.assertEqual(s["completeness"], "PARTIAL")
            self.assertIsNone(s["world_state_at_entry"])
            self.assertIn("data/external", s["world_state_absent_reason"])
            self.assertIsNone(s["static_map_rows"])
            self.assertRegex(s["provenance"]["evidence_sha256"],
                             r"^[0-9a-f]{64}$")

    def test_mechanism_labels_are_internally_consistent(self):
        for s in self.situations:
            mech = s["classification"]["mechanism"]
            blocker = s["classification"]["blocker"]
            if mech == "M3":
                self.assertIsNone(blocker)
                self.assertEqual(s["classification"]["blocker_state"], "NONE")
            if mech == "M2" and s["completeness"] == "FULL":
                self.assertIsNotNone(blocker)
                self.assertIsNotNone(blocker["plant_on_cell_at_entry"])
                self.assertTrue(blocker["idle_by_analysis_criterion"])
            if mech == "M1":
                self.assertIsNotNone(blocker)
                self.assertTrue(
                    blocker["plant_on_cell_at_entry"] is None
                    or not blocker["idle_by_analysis_criterion"],
                    "%s: M1 requires the blocker to be off-plant or working"
                    % s["id"])

    def test_idle_blockers_really_hold_one_cell(self):
        for s in self.situations:
            if s["classification"]["blocker_state"] != "IDLE":
                continue
            if s["completeness"] != "FULL":
                continue
            b = s["classification"]["blocker"]
            self.assertEqual(b["distinct_cells_in_window"], 1)
            self.assertGreaterEqual(b["wait_fraction_in_window"], 0.95)


# ---------------------------------------------------------------------------
# 4. the index agrees with the directory
# ---------------------------------------------------------------------------

class TestIndex(LibraryTestBase):

    def test_index_count_equals_file_count(self):
        files = sorted(p.name for p in LIB.glob("*.json")
                       if p.name != "index.json")
        self.assertEqual(self.index["situation_count"], len(files))
        self.assertEqual(len(self.index["situations"]), len(files))
        self.assertEqual(len(self.situations), len(files))

    def test_index_ids_are_unique_and_match_file_names(self):
        ids = [e["id"] for e in self.index["situations"]]
        self.assertEqual(len(ids), len(set(ids)))
        for e in self.index["situations"]:
            self.assertEqual(e["file"], "%s.json" % e["id"])
            self.assertTrue((LIB / e["file"]).exists())

    def test_index_histograms_agree_with_the_situations(self):
        self.assertEqual(self.index["mechanism_histogram"],
                         ol.histogram(self.situations, "mechanism"))
        self.assertEqual(self.index["blocker_state_histogram"],
                         ol.histogram(self.situations, "blocker_state"))
        self.assertEqual(self.index["kind_histogram"],
                         ol.histogram(self.situations, "kind"))

    def test_episode_count_equals_the_sum_of_multiplicities(self):
        self.assertEqual(self.index["episode_count"],
                         ol.episode_count(self.situations))
        self.assertGreaterEqual(self.index["episode_count"],
                                self.index["situation_count"])

    def test_dedupe_is_by_mechanism_and_geometry_not_by_game(self):
        """No two situations may share a dedupe key, and any situation with
        multiplicity > 1 must genuinely list that many distinct episodes."""
        keys = [s["multiplicity"]["dedupe_key_sha256"]
                for s in self.situations]
        self.assertEqual(len(keys), len(set(keys)))
        for s in self.situations:
            members = s["multiplicity"]["members"]
            self.assertEqual(len(members), s["multiplicity"]["episodes"])
            stamps = {(m.get("map_id"), m.get("game_id"), m.get("seat"),
                       m.get("unit"), m.get("turn_start")) for m in members}
            self.assertEqual(len(stamps), len(members))

    def test_the_representative_is_the_longest_member(self):
        for s in self.situations:
            longest = max(m["length_turns"]
                          for m in s["multiplicity"]["members"])
            self.assertEqual(s["window"]["length_turns"], longest)

    def test_geometry_stencils_are_distinct_within_a_mechanism(self):
        seen = {}
        for s in self.situations:
            key = (s["kind"], s["classification"]["mechanism"],
                   s["classification"]["blocker_state"],
                   s["classification"]["geometry_stencil"])
            self.assertNotIn(key, seen,
                             "%s duplicates %s" % (s["id"], seen.get(key)))
            seen[key] = s["id"]


# ---------------------------------------------------------------------------
# 5. M3a must not pre-empt M3b
# ---------------------------------------------------------------------------

class TestNoBestActionRecorded(LibraryTestBase):
    """M3a enumerates and freezes.  Deciding what the right action was is
    M3b, must be done independently of the scorer, and is blocked on the
    Decision Packet.  If a "correct action" ever leaks into a frozen file,
    M3b's independence is gone -- so the library asserts its own silence."""

    FORBIDDEN_KEYS = (
        "best_action", "correct_action", "optimal_action", "right_action",
        "recommended_action", "recommendation", "should_have", "verdict",
        "adjudication", "expected_action", "ideal_action", "fix", "remedy",
    )
    FORBIDDEN_PHRASES = (
        "best action", "correct action", "optimal action", "right action",
        "recommended action", "should have moved", "should have waited",
        "the bot should", "the unit should", "ought to have",
    )

    def walk(self, node, path=""):
        if isinstance(node, dict):
            for k, v in node.items():
                yield path + "/" + str(k), k, v
                yield from self.walk(v, path + "/" + str(k))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                yield from self.walk(v, path + "/%d" % i)

    def test_no_situation_names_a_best_action(self):
        for s in self.situations:
            for path, key, _ in self.walk(s):
                low = str(key).lower()
                for bad in self.FORBIDDEN_KEYS:
                    self.assertNotEqual(low, bad,
                                        "%s records %s at %s"
                                        % (s["id"], bad, path))

    def test_no_situation_text_asserts_what_should_have_happened(self):
        for s in self.situations:
            blob = json.dumps(s).lower()
            for phrase in self.FORBIDDEN_PHRASES:
                self.assertNotIn(phrase, blob,
                                 "%s contains %r" % (s["id"], phrase))

    def test_the_index_declares_the_m3a_scope_limit(self):
        note = self.index["scope_note"].lower()
        self.assertIn("m3b", note)
        self.assertIn("no judgement of the best action", note)


class TestFrozenStatesReplay(LibraryTestBase):
    """The freeze is only worth something if the literal data reproduces the
    recorded behaviour WITHOUT a call into the map generator.

    This needs rustc and a compiled bot, so it is opt-in:
        OSC_LIB_REPLAY=1 python3 -m unittest test_oscillation_library
    The result of running it is recorded in the report.
    """

    @unittest.skipUnless(os.environ.get("OSC_LIB_REPLAY"),
                         "set OSC_LIB_REPLAY=1 (needs rustc + a bot build)")
    def test_every_full_situation_reproduces_its_command_window(self):
        import sys
        sys.path.insert(0, str(HERE.parent / "pipeline"))
        import fuzz_panel as fp
        import regression_tests as rt

        workdir = Path(tempfile.mkdtemp(prefix="osclib-bot-"))
        self.addCleanup(shutil.rmtree, workdir, ignore_errors=True)
        cfg = json.loads(
            (HERE / "oscillation-library-panel-config.json").read_text())
        cfg["config_dir"] = HERE
        binary = fp.compile_bot(cfg, "candidate", workdir)

        checked = 0
        for s in self.situations:
            if s["completeness"] != "FULL":
                continue
            init = s["initial_world_state"]
            spec = {
                "rows": s["static_map_rows"],
                "plants": [list(p) for p in init["plants"]],
                "inventory": list(init["inventories"]["own"]),
                "units": [list(u) for u in init["units"]],
                "profile": s["provenance"]["opponent_profile"],
            }
            ref = fp.make_referee(spec)
            _, commands = rt.run_binary_custom(
                binary, ref, s["provenance"]["panel_turns"])
            lines = commands.split("\n")
            while lines and lines[-1] == "":
                lines.pop()
            for entry in s["window"]["commands"]:
                self.assertEqual(lines[entry["turn"] - 1], entry["line"],
                                 "%s: turn %d diverges from the freeze"
                                 % (s["id"], entry["turn"]))
            checked += 1
        self.assertGreater(checked, 0)


if __name__ == "__main__":
    unittest.main()
