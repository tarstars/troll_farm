#!/usr/bin/env python3
"""Tests for the frozen oscillation situation libraries (manifest item M3a).

Run:  python3 -m unittest test_oscillation_library -v
      (python3.12 stdlib only; no pytest)

**Two trees are under test, and telling them apart is the point.**

  `oscillation-library-98628e98/library/` -- the M3a SUBJECT,
      `readable__no_orchard` (`98628e98...`) judged against itself.  This is
      the deliverable.  `TestSubject*` covers it.

  `oscillation-library/` -- the PARENT lineage (`a8eb3b2b...`), a different
      program, published as M3a in error and retained only for comparison.
      The original `Test*` classes still cover it unchanged, and
      `TestParentLineageIsLabelled` asserts its index says what it is so it
      can never be cited as M3a again.

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

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import oscillation_library as ol

HERE = Path(__file__).resolve().parent


class SourceMaterialisationError(RuntimeError):
    """A pinned bot source could not be produced from Git, or did not verify."""


def materialise_pinned_sources(cfg, workdir: Path) -> dict:
    """Rewrite `cfg` so every bot source is a real file inside `workdir`.

    The panel configs used to name their bot sources by absolute path, under a
    session scratchpad and a developer home directory.  Both are absent on a
    clean runner -- and on this host too, once the session scratchpad is reaped
    -- so the replay suites could only ever pass on the machine that produced
    them.  `chatgpt_1` found this by running them somewhere else
    (`20260811T230000Z`, REVISION_REQUIRED -- SOURCE REPLAY NOT PORTABLE).

    Each entry now declares `source_git = {commit, path}`.  The blob is read
    from that **commit** -- immutable, never a branch, because a moving ref is
    the trust-root defect `chatgpt_1` raised against I-30 -- and verified
    against the entry's own `sha256` pin before it is used.  Provenance comes
    from the commit; content comes from the digest; neither comes from the
    filesystem this happens to run on.

    Returns the mutated cfg.  Raises `SourceMaterialisationError` loudly rather
    than falling back to any host path: a replay that silently used a different
    file would be worth less than one that did not run.
    """
    repo = Path(__file__).resolve()
    for parent in repo.parents:
        if (parent / ".git").exists():
            repo = parent
            break
    else:  # pragma: no cover - the tree is always inside a checkout
        raise SourceMaterialisationError("not inside a Git checkout")

    for key in ("candidate", "parent"):
        entry = cfg.get(key)
        if not entry:
            continue
        pin = entry.get("source_git")
        if not pin:
            raise SourceMaterialisationError(
                "%s has no source_git pin; this config predates the portability "
                "repair and cannot be replayed off its original host" % key)
        commit, path = pin["commit"], pin["path"]
        proc = subprocess.run(["git", "-C", str(repo), "show", "%s:%s" % (commit, path)],
                              capture_output=True)
        if proc.returncode != 0:
            raise SourceMaterialisationError(
                "cannot read %s:%s from %s -- %s"
                % (commit, path, repo, proc.stderr.decode("utf-8", "replace").strip()))
        blob = proc.stdout
        digest = hashlib.sha256(blob).hexdigest()
        declared = entry.get("sha256", "")
        if declared and not digest.startswith(declared.rstrip(".")):
            raise SourceMaterialisationError(
                "%s sha256 mismatch: config pins %s, %s:%s is %s"
                % (key, declared, commit, path, digest))
        out = workdir / ("source-%s-%s" % (key, digest[:16]))
        out.write_bytes(blob)
        entry["source"] = str(out)

    # The cache and games directories were absolute session paths too.  Replay
    # needs neither: build into the throwaway workdir so a run leaves nothing
    # behind and depends on nothing outside it.
    cfg.pop("bin_cache_dir", None)
    cfg["games_dir"] = str(workdir / "games")
    return cfg

# The parent lineage (a8eb3b2b) -- NOT the M3a subject.
LIB = HERE / "oscillation-library"
PARENT_PANEL_CONFIG = HERE / "oscillation-library-panel-config.json"

# The M3a subject (98628e98), judged against itself.
SUBJECT_TREE = HERE / "oscillation-library-98628e98"
SUBJECT_LIB = SUBJECT_TREE / "library"
SUBJECT_PANEL_CONFIG = SUBJECT_TREE / "panel-config.json"


class LibraryTestBase(unittest.TestCase):
    #: which tree this class tests.  Subclasses override to retarget the whole
    #: inherited suite at the other library.
    LIB = LIB

    @classmethod
    def setUpClass(cls):
        cls.situations = ol.load_library(cls.LIB)
        cls.index = ol.load_index(cls.LIB)

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

    #: which tree the mutation demonstrations run against.
    LIB = LIB

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="osclib-"))
        self.dir = self.tmp / "oscillation-library"
        shutil.copytree(self.LIB, self.dir)
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
        files = sorted(p.name for p in self.LIB.glob("*.json")
                       if p.name != "index.json")
        self.assertEqual(self.index["situation_count"], len(files))
        self.assertEqual(len(self.index["situations"]), len(files))
        self.assertEqual(len(self.situations), len(files))

    def test_index_ids_are_unique_and_match_file_names(self):
        ids = [e["id"] for e in self.index["situations"]]
        self.assertEqual(len(ids), len(set(ids)))
        for e in self.index["situations"]:
            self.assertEqual(e["file"], "%s.json" % e["id"])
            self.assertTrue((self.LIB / e["file"]).exists())

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

    #: the panel config whose `candidate` is the bot that produced this tree.
    PANEL_CONFIG = PARENT_PANEL_CONFIG

    @unittest.skipUnless(os.environ.get("OSC_LIB_REPLAY"),
                         "set OSC_LIB_REPLAY=1 (needs rustc + a bot build)")
    def test_every_full_situation_reproduces_its_command_window(self):
        import sys
        sys.path.insert(0, str(HERE.parent / "pipeline"))
        import fuzz_panel as fp
        import regression_tests as rt

        # Corpus eligibility is decided BEFORE anything is compiled.  A frozen
        # situation replays byte-for-byte only under the referee that produced
        # it -- `make_referee` is always the CURRENT panel -- so a situation
        # frozen under an earlier corpus is not expected to reproduce and is
        # not silently counted as if it had.  Evaluating that first means a
        # tree that is entirely pre-bump skips without invoking rustc at all,
        # instead of spending a bot build to discover it has nothing to check
        # (required by chatgpt_1's review, 20260811T230000Z).
        replayable, skipped = [], 0
        for s in self.situations:
            if s["completeness"] != "FULL":
                continue
            if s["provenance"]["corpus_version"] != fp.CORPUS_VERSION:
                skipped += 1
                continue
            replayable.append(s)
        if not replayable:
            self.skipTest(
                "every FULL situation in %s was frozen under a corpus other "
                "than the running panel's %s (%d skipped); replay is not "
                "meaningful across a corpus bump, and no bot was built"
                % (self.LIB.name, fp.CORPUS_VERSION, skipped))

        workdir = Path(tempfile.mkdtemp(prefix="osclib-bot-"))
        self.addCleanup(shutil.rmtree, workdir, ignore_errors=True)
        cfg = json.loads(self.PANEL_CONFIG.read_text())
        cfg["config_dir"] = self.PANEL_CONFIG.parent
        # Materialise the pinned sources from Git into `workdir` and verify
        # them against the config's own digests, so this runs on a clean
        # checkout with no scratch directory and no developer home.
        cfg = materialise_pinned_sources(cfg, workdir)
        binary = fp.compile_bot(cfg, "candidate", workdir)

        checked = 0
        for s in replayable:
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
        print("\n  replay: %s -- %d/%d FULL situations reproduce their frozen "
              "command window byte-for-byte (%d skipped: older corpus)"
              % (self.LIB.name, checked, checked + skipped, skipped))


# ===========================================================================
# The M3a SUBJECT library -- `readable__no_orchard` (98628e98) vs itself.
#
# The whole inherited suite is re-run against it by overriding `LIB`, so the
# subject tree gets the same round-trip, fail-closed-mutation, index and
# no-best-action guarantees the parent tree got -- not a weaker copy of them.
# ===========================================================================

class TestSubjectRoundTrip(TestRoundTrip):
    LIB = SUBJECT_LIB


class TestSubjectIndex(TestIndex):
    LIB = SUBJECT_LIB


class TestSubjectNoBestActionRecorded(TestNoBestActionRecorded):
    LIB = SUBJECT_LIB


class TestSubjectIntegrityFailsClosed(TestIntegrityFailsClosed):
    LIB = SUBJECT_LIB


class TestSubjectReplay(TestFrozenStatesReplay):
    LIB = SUBJECT_LIB
    PANEL_CONFIG = SUBJECT_PANEL_CONFIG


class TestSubjectIdentity(LibraryTestBase):
    """The defect this tree exists to correct was an IDENTITY defect: the
    published library named `readable__no_orchard` as its subject and
    contained not one situation from it.  These tests make that class of
    error a test failure rather than a reading error."""

    LIB = SUBJECT_LIB

    def test_every_situation_was_produced_by_the_subject_bot(self):
        for s in self.situations:
            self.assertEqual(s["provenance"]["bot_source_sha256"],
                             ol.SUBJECT_SHA256,
                             "%s was not produced by the M3a subject" % s["id"])

    def test_no_situation_came_from_the_parent_or_any_other_bot(self):
        """The parent digest, and the third bot that produced the parent
        tree's REAL_CORPUS record, must appear nowhere in this library."""
        others = (ol.PARENT_LINEAGE_SHA256,
                  "f26e3781e972006cb2698420bba3474f1a038708225beeb562f3ab"
                  "2242593e4a")
        for s in self.situations:
            blob = json.dumps(s)
            for digest in others:
                self.assertNotIn(digest, blob,
                                 "%s references foreign bot %s"
                                 % (s["id"], digest[:16]))

    def test_the_index_declares_the_subject_and_the_floor_identity(self):
        subject = self.index["subject"]
        self.assertEqual(subject["sha256"], ol.SUBJECT_SHA256)
        self.assertEqual(subject["name"], "readable__no_orchard")
        self.assertEqual(subject["run_identity"], "floor")
        self.assertIn("submitted-agent6593838-readable-no-orchard.rs",
                      subject["path"])
        note = self.index["subject_note"]
        self.assertIn(ol.SUBJECT_SHA256, note)
        self.assertIn(ol.PARENT_LINEAGE_SHA256, note)

    def test_the_panel_config_is_a_floor_run_of_the_subject_against_itself(self):
        cfg = json.loads(SUBJECT_PANEL_CONFIG.read_text())
        self.assertEqual(cfg["run_identity"], "floor")
        self.assertEqual(cfg["candidate"]["sha256"], ol.SUBJECT_SHA256)
        self.assertEqual(cfg["parent"]["sha256"], ol.SUBJECT_SHA256)
        self.assertEqual(cfg["candidate"]["source"], cfg["parent"]["source"])
        self.assertNotEqual(cfg["candidate"]["crate"], cfg["parent"]["crate"])

    def test_no_real_corpus_record_is_present(self):
        """The parent tree's one REAL_CORPUS situation came from a third bot.
        A subject-declared library may not contain it."""
        self.assertEqual(ol.find(self.situations, kind="REAL_CORPUS"), [])
        for s in self.situations:
            self.assertEqual(s["completeness"], "FULL")


class TestSubjectNamedCases(LibraryTestBase):
    """The four cases named by `oscillation-attack-claude_1-2026-08-09.md`
    -- which was itself written about `98628e98` -- must land on the subject.
    Windows may differ from the parent tree's by a few turns: that tree ran
    corpus c3 and this one runs c5."""

    LIB = SUBJECT_LIB

    def episode_of(self, map_id, seat, unit, turn_start):
        for s in self.situations:
            for m in s["multiplicity"]["members"]:
                if (m.get("map_id") == map_id and m.get("seat") == seat
                        and m.get("unit") == unit
                        and m.get("turn_start") == turn_start):
                    return s, m
        self.fail("no frozen situation contains episode %s s%d u%d @t%d"
                  % (map_id, seat, unit, turn_start))

    def test_m110_seat1_is_M1_with_an_idle_blocker(self):
        s, m = self.episode_of("m110", 1, 0, 6)
        self.assertEqual(s["classification"]["mechanism"], "M1")
        self.assertEqual(s["classification"]["blocker_state"], "IDLE")
        self.assertEqual([m["turn_start"], m["turn_end"]], [6, 200])
        self.assertEqual(m["length_turns"], 195)
        b = s["classification"]["blocker"]
        self.assertEqual(b["unit"], 2)
        self.assertEqual(b["cell_at_entry"], [4, 2])
        self.assertEqual(b["distinct_cells_in_window"], 1)
        self.assertIsNone(b["plant_on_cell_at_entry"])

    def test_m040_seat1_is_M1_with_a_working_blocker(self):
        s, m = self.episode_of("m040", 1, 0, 80)
        self.assertEqual(s["classification"]["mechanism"], "M1")
        self.assertEqual(s["classification"]["blocker_state"], "WORKING")
        self.assertEqual([m["turn_start"], m["turn_end"]], [80, 86])
        b = s["classification"]["blocker"]
        self.assertIn("CHOP", b["non_wait_verbs_in_window"])
        self.assertFalse(b["idle_by_analysis_criterion"])

    def test_m014_seat1_is_M2_an_idle_peer_on_the_target_plant(self):
        s, m = self.episode_of("m014", 1, 2, 7)
        self.assertEqual(s["classification"]["mechanism"], "M2")
        self.assertEqual(s["classification"]["blocker_state"], "IDLE")
        b = s["classification"]["blocker"]
        self.assertIsNotNone(b["plant_on_cell_at_entry"])
        self.assertTrue(b["idle_by_analysis_criterion"])

    def test_m085_seat0_is_M3_a_scorer_cycle_with_one_own_unit(self):
        s, m = self.episode_of("m085", 0, 0, 17)
        self.assertEqual(s["classification"]["mechanism"], "M3")
        self.assertEqual(s["classification"]["blocker_state"], "NONE")
        self.assertIsNone(s["classification"]["blocker"])
        self.assertEqual(s["classification"]["all_own_peers_at_entry"], [])

    def test_the_two_named_cases_differ_exactly_in_the_blocker(self):
        long_s, long_m = self.episode_of("m110", 1, 0, 6)
        short_s, short_m = self.episode_of("m040", 1, 0, 80)
        self.assertEqual(long_s["classification"]["mechanism"],
                         short_s["classification"]["mechanism"])
        self.assertNotEqual(long_s["classification"]["blocker_state"],
                            short_s["classification"]["blocker_state"])
        self.assertGreater(long_m["length_turns"],
                           25 * short_m["length_turns"])


class TestSubjectIdleBlockerCrossTab(LibraryTestBase):
    """The headline of the parent-lineage report -- *every* terminal
    (>= 62 turn) D-1 episode has an idle blocker, and no episode with a
    working blocker or no blocker reaches 62 -- re-tested on the SUBJECT.

    It is asserted as a test, not narrated, so a re-harvest that changes the
    answer fails here rather than silently contradicting the report.
    `blocker_state` is part of the dedupe key, so every member of a group was
    independently measured to the same state and the episode-level tabulation
    is sound."""

    LIB = SUBJECT_LIB
    TERMINAL_TURNS = 62

    def cross_tab(self):
        tab = {}
        for s in self.situations:
            if s["kind"] != "D1_EPISODE":
                continue
            state = s["classification"]["blocker_state"]
            for m in s["multiplicity"]["members"]:
                key = (state, m["length_turns"] >= self.TERMINAL_TURNS)
                tab[key] = tab.get(key, 0) + 1
        return tab

    def test_all_terminal_episodes_have_an_idle_blocker(self):
        tab = self.cross_tab()
        self.assertEqual(tab.get(("WORKING", True), 0), 0)
        self.assertEqual(tab.get(("NONE", True), 0), 0)
        self.assertGreater(tab.get(("IDLE", True), 0), 0)

    def test_the_measured_cross_tab_is_exactly_as_reported(self):
        self.assertEqual(self.cross_tab(), {
            ("IDLE", True): 20, ("IDLE", False): 2,
            ("WORKING", False): 8, ("NONE", False): 8,
        })

    def test_the_evidence_for_idleness_is_carried_per_situation(self):
        """Names the fields that settle the claim.  chatgpt_1's base panel
        carries none of them; this library carries all of them."""
        for s in self.situations:
            if s["kind"] != "D1_EPISODE":
                continue
            b = s["classification"]["blocker"]
            if b is None:
                self.assertEqual(s["classification"]["blocker_state"], "NONE")
                continue
            for field in ("unit", "cell_at_entry", "wait_fraction_in_window",
                          "distinct_cells_in_window",
                          "non_wait_verbs_in_window",
                          "idle_by_analysis_criterion"):
                self.assertIn(field, b, "%s blocker lacks %s" % (s["id"], field))
            self.assertEqual(
                b["idle_by_analysis_criterion"],
                bool(b["wait_fraction_in_window"] >= 0.95
                     and b["distinct_cells_in_window"] == 1))
            self.assertEqual(
                s["classification"]["blocker_state"],
                "IDLE" if b["idle_by_analysis_criterion"] else "WORKING")

    def test_the_blocker_wait_fraction_is_rederivable_from_the_frozen_window(self):
        """Not a stored opinion: recompute it from the verbatim command lines
        the situation itself carries, and require agreement."""
        checked = 0
        for s in self.situations:
            if s["kind"] != "D1_EPISODE":
                continue
            b = s["classification"]["blocker"]
            if b is None:
                continue
            lines = s["window"]["commands"]
            self.assertTrue(lines, "%s carries no command window" % s["id"])
            acting = 0
            for entry in lines:
                for frag in entry["line"].split(";"):
                    parts = frag.strip().split()
                    if (len(parts) > 1 and parts[0] != "WAIT"
                            and parts[1] == str(b["unit"])):
                        acting += 1
                        break
            self.assertAlmostEqual(1.0 - acting / len(lines),
                                   b["wait_fraction_in_window"], delta=0.02,
                                   msg="%s: stored wait fraction does not "
                                       "match its own command window" % s["id"])
            checked += 1
        self.assertGreater(checked, 0)


class TestParentLineageIsLabelled(unittest.TestCase):
    """The old tree stays, but it must say what it is.  Without this, the
    identity defect is one careless citation away from recurring."""

    def test_the_parent_index_records_that_it_is_not_the_m3a_subject(self):
        index = ol.load_index(LIB)
        note = index["subject_note"]
        self.assertIn(ol.PARENT_LINEAGE_SHA256, note)
        self.assertIn(ol.SUBJECT_SHA256, note)
        self.assertIn("MUST NOT BE CITED AS M3a", note)
        self.assertFalse(index["subject"]["is_m3a_subject"])
        self.assertEqual(index["subject"]["sha256"], ol.PARENT_LINEAGE_SHA256)
        self.assertEqual(index["subject"]["m3a_subject_is"]["sha256"],
                         ol.SUBJECT_SHA256)

    def test_labelling_the_parent_tree_did_not_alter_any_situation(self):
        """The marker is an index field only.  `library_sha256` is computed
        over the (id, content_sha256) pairs, so this proves no situation file
        was touched."""
        index = ol.load_index(LIB)
        self.assertEqual(index["library_sha256"],
                         ol.library_sha256(index["situations"]))
        self.assertEqual(
            index["library_sha256"],
            "5858d35122973f017374ed2136aa2855e8e2ace68114b1e8e6f52759e0136c61")
        self.assertEqual(len(ol.load_library(LIB)), 33)

    def test_the_stale_readme_still_describes_the_tree_it_sits_in(self):
        """The loud README is the whole guard against reading this tree by
        path, and it is the one part of that guard nothing tested.  It also
        survives an overwrite: `build_oscillation_library.write_library`
        unlinks `*.json` only, so a run of the builder that omits `--out`
        (whose default is this directory) would replace the cases and leave
        the README behind describing 33 cases that are no longer here.  Tying
        the README's ID map to the tree's actual IDs makes that state fail
        loudly instead of standing as a false document."""
        readme = LIB / "README.md"
        self.assertTrue(readme.exists(), "the stale tree lost its marker README")
        text = readme.read_text()
        self.assertIn("STALE", text.splitlines()[0])
        self.assertIn("Do not read a case out of this directory", text)
        self.assertIn("oscillation-library-98628e98/library", text,
                      "the README must name the authoritative sibling tree")
        tabled = re.findall(r"^\| `(OSC-\d{3})` \|", text, re.M)
        self.assertEqual(len(tabled), len(set(tabled)),
                         "the README's ID map repeats an ID")
        present = sorted(p.stem for p in LIB.glob("OSC-*.json"))
        self.assertEqual(sorted(tabled), present,
                         "the README's ID map and this tree have diverged")

    def test_the_two_libraries_are_distinct_trees(self):
        self.assertNotEqual(ol.load_index(LIB)["library_sha256"],
                            ol.load_index(SUBJECT_LIB)["library_sha256"])
        self.assertEqual(ol.DEFAULT_DIR, SUBJECT_LIB,
                         "an unqualified load must return the M3a subject")


class TestSourcesArePortable(unittest.TestCase):
    """The replay suites are opt-in and need `rustc`, so for weeks nothing
    executed the code path that resolved a bot source.  The configs pointed at
    a session scratchpad and a developer home; on the machine that produced
    them those paths existed, so the defect was invisible here and immediate
    for `chatgpt_1` on a clean runner.

    These tests need neither `rustc` nor `OSC_LIB_REPLAY`: they run in the
    default suite, so a source that is not reachable from Git is a **failure
    now**, on any machine, rather than a surprise for whoever next tries to
    reproduce the library somewhere else.
    """

    CONFIGS = (PARENT_PANEL_CONFIG, SUBJECT_PANEL_CONFIG)

    def _configs(self):
        for path in self.CONFIGS:
            yield path, json.loads(path.read_text())

    def test_no_config_names_an_absolute_host_path(self):
        """`notes` is prose and may quote the old paths; data fields may not."""
        def walk(node, trail=""):
            if isinstance(node, dict):
                for key, value in node.items():
                    if key == "notes":
                        continue
                    yield from walk(value, "%s/%s" % (trail, key))
            elif isinstance(node, list):
                for i, value in enumerate(node):
                    yield from walk(value, "%s[%d]" % (trail, i))
            elif isinstance(node, str) and (node.startswith("/home/")
                                            or node.startswith("/tmp/")):
                yield trail, node

        for path, cfg in self._configs():
            offenders = list(walk(cfg))
            self.assertEqual(
                offenders, [],
                "%s still names absolute host paths, which exist on no clean "
                "runner: %s" % (path.name, offenders))

    def test_every_bot_source_is_pinned_to_an_immutable_commit(self):
        for path, cfg in self._configs():
            for key in ("candidate", "parent"):
                pin = cfg[key].get("source_git")
                self.assertIsNotNone(
                    pin, "%s: %s has no source_git pin" % (path.name, key))
                commit = pin["commit"]
                self.assertRegex(
                    commit, r"^[0-9a-f]{40}$",
                    "%s: %s source_git.commit must be a full 40-hex object id, "
                    "not a branch -- a moving ref is not a pin" % (path.name, key))

    def test_every_pinned_source_resolves_from_git_and_matches_its_digest(self):
        """The pin is only worth something if it produces the declared bytes."""
        workdir = Path(tempfile.mkdtemp(prefix="osclib-src-"))
        self.addCleanup(shutil.rmtree, workdir, ignore_errors=True)
        for path, cfg in self._configs():
            cfg = materialise_pinned_sources(dict(cfg), workdir)
            for key in ("candidate", "parent"):
                source = Path(cfg[key]["source"])
                self.assertTrue(
                    source.is_file(),
                    "%s: %s did not materialise" % (path.name, key))
                digest = hashlib.sha256(source.read_bytes()).hexdigest()
                self.assertTrue(
                    digest.startswith(cfg[key]["sha256"].rstrip(".")),
                    "%s: %s materialised to %s, config pins %s"
                    % (path.name, key, digest, cfg[key]["sha256"]))

    def test_a_floor_config_materialises_both_seats_to_the_same_bytes(self):
        """`run_identity: floor` means the bot is judged against itself.  If
        materialisation ever produced two different files for the two seats the
        run would silently stop being a floor, which is the exact confusion
        `run_identity` was added to make impossible."""
        workdir = Path(tempfile.mkdtemp(prefix="osclib-floor-"))
        self.addCleanup(shutil.rmtree, workdir, ignore_errors=True)
        for path, cfg in self._configs():
            if cfg.get("run_identity") != "floor":
                continue
            cfg = materialise_pinned_sources(dict(cfg), workdir)
            a = Path(cfg["candidate"]["source"]).read_bytes()
            b = Path(cfg["parent"]["source"]).read_bytes()
            self.assertEqual(hashlib.sha256(a).hexdigest(),
                             hashlib.sha256(b).hexdigest(),
                             "%s declares run_identity 'floor' but its two "
                             "seats materialised to different bytes" % path.name)

    def test_materialisation_refuses_a_wrong_digest_rather_than_compiling_it(self):
        """Fail closed, demonstrated on a really-corrupted pin rather than
        asserted in prose -- the same standard the fixture-mutation test
        already holds this suite to."""
        workdir = Path(tempfile.mkdtemp(prefix="osclib-bad-"))
        self.addCleanup(shutil.rmtree, workdir, ignore_errors=True)
        cfg = json.loads(SUBJECT_PANEL_CONFIG.read_text())
        cfg["candidate"]["sha256"] = "0" * 64
        with self.assertRaises(SourceMaterialisationError) as caught:
            materialise_pinned_sources(cfg, workdir)
        self.assertIn("sha256 mismatch", str(caught.exception))

    def test_materialisation_refuses_an_unreachable_commit(self):
        workdir = Path(tempfile.mkdtemp(prefix="osclib-gone-"))
        self.addCleanup(shutil.rmtree, workdir, ignore_errors=True)
        cfg = json.loads(SUBJECT_PANEL_CONFIG.read_text())
        cfg["candidate"]["source_git"]["commit"] = "0" * 40
        with self.assertRaises(SourceMaterialisationError):
            materialise_pinned_sources(cfg, workdir)


if __name__ == "__main__":
    unittest.main()
