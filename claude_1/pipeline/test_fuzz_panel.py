#!/usr/bin/env python3
"""Self-tests for fuzz_panel (python3 -m unittest test_fuzz_panel).

Covers, in both directions where meaningful:
  * mix scheduling apportionment;
  * map generator determinism (same seed -> byte-identical specs) and
    validity (tents, doors, connectivity, plants/units on walkable cells,
    orchard-class eligibility, both-seat variants);
  * the orchard-eligibility mirror against the known harness geometries;
  * P2 catches the r5 planted-oscillator control and passes the compliant
    control (reusing the regression_tests r5 controls closed-loop);
  * P3 via a synthetic command-stream mismatch (and both non-triggering
    directions);
  * P4 stall-window machinery;
  * CLI exit-code semantics with planted bots: exit 0 (WAIT bot vs itself:
    identical streams, no detector episodes, inherited quiescence), exit 1
    (planted A->B->A oscillator bot caught by P1/D-1), exit 2 (bad config).

Planted-bot runs compile two tiny Rust bots (cached per test run); the real
candidate/parent are deliberately NOT exercised here so the self-tests stay
green independent of the candidate's own defects.
"""

from __future__ import annotations

import inspect
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import fuzz_panel as fp                       # noqa: E402

sys.path.insert(0, str(fp.BR2))
import semantic_harness as sh                 # noqa: E402
import trace_detectors as td                  # noqa: E402
import regression_tests as rt                 # noqa: E402

WAIT_BOT = r"""
use std::io::{BufRead, Write};
fn main() {
    let stdin = std::io::stdin();
    let mut lines = stdin.lock().lines().filter_map(|l| l.ok());
    let first = match lines.next() { Some(l) => l, None => return };
    let mut it = first.split_whitespace();
    let _w: usize = it.next().unwrap().parse().unwrap();
    let h: usize = it.next().unwrap().parse().unwrap();
    for _ in 0..h { lines.next(); }
    loop {
        if lines.next().is_none() { return; }
        lines.next();
        let np: usize = lines.next().unwrap().trim().parse().unwrap();
        for _ in 0..np { lines.next(); }
        let nu: usize = lines.next().unwrap().trim().parse().unwrap();
        for _ in 0..nu { lines.next(); }
        println!("WAIT");
        std::io::stdout().flush().unwrap();
    }
}
"""

# Planted defect bot: locks onto its starter unit's initial cell, picks the
# first walkable orthogonal neighbour, and MOVEs back and forth forever with
# no other verb -- a pure A->B->A zero-progress alternation (the D-1 / host
# round-4 episode shape).
OSCILLATOR_BOT = r"""
use std::io::{BufRead, Write};
fn main() {
    let stdin = std::io::stdin();
    let mut lines = stdin.lock().lines().filter_map(|l| l.ok());
    let first = match lines.next() { Some(l) => l, None => return };
    let mut it = first.split_whitespace();
    let w: i64 = it.next().unwrap().parse().unwrap();
    let h: i64 = it.next().unwrap().parse().unwrap();
    let mut rows: Vec<Vec<u8>> = Vec::new();
    for _ in 0..h { rows.push(lines.next().unwrap().into_bytes()); }
    let mut base: Option<(i64, i64, i64)> = None;
    let mut target: Option<(i64, i64)> = None;
    loop {
        if lines.next().is_none() { return; }
        lines.next();
        let np: usize = lines.next().unwrap().trim().parse().unwrap();
        for _ in 0..np { lines.next(); }
        let nu: usize = lines.next().unwrap().trim().parse().unwrap();
        let mut me: Option<(i64, i64, i64)> = None;
        for _ in 0..nu {
            let line = lines.next().unwrap();
            let v: Vec<i64> = line.split_whitespace()
                .map(|t| t.parse().unwrap()).collect();
            if v[1] == 0 && (me.is_none() || v[0] < me.unwrap().0) {
                me = Some((v[0], v[2], v[3]));
            }
        }
        let Some((id, x, y)) = me else {
            println!("WAIT");
            std::io::stdout().flush().unwrap();
            continue;
        };
        if base.is_none() {
            base = Some((id, x, y));
            for (dx, dy) in [(0i64, 1i64), (1, 0), (0, -1), (-1, 0)] {
                let (nx, ny) = (x + dx, y + dy);
                if nx >= 0 && ny >= 0 && nx < w && ny < h
                    && rows[ny as usize][nx as usize] == b'.' {
                    target = Some((nx, ny));
                    break;
                }
            }
        }
        let (bid, bx, by) = base.unwrap();
        match target {
            Some((tx, ty)) => {
                if x == bx && y == by { println!("MOVE {} {} {}", bid, tx, ty); }
                else { println!("MOVE {} {} {}", bid, bx, by); }
            }
            None => println!("WAIT"),
        }
        std::io::stdout().flush().unwrap();
    }
}
"""

_BOT_CACHE: dict[str, Path] = {}
_BOT_DIR: tempfile.TemporaryDirectory | None = None


def compiled_bot(name: str, source: str) -> Path:
    global _BOT_DIR
    if name not in _BOT_CACHE:
        if _BOT_DIR is None:
            _BOT_DIR = tempfile.TemporaryDirectory(prefix="fuzz-selftest-")
        src = Path(_BOT_DIR.name) / (name + ".rs")
        src.write_text(source)
        binary = Path(_BOT_DIR.name) / name
        sh.compile_text(source, binary, "selftest_" + name)
        _BOT_CACHE[name] = src
    return _BOT_CACHE[name]


def mini_cfg(**overrides) -> dict:
    cfg = {
        "seeds": [11], "maps": 2, "turns": 30, "processes": 1,
        "class_mix": {"open_field": 1.0}, "opponent_mix": {"idle": 1.0},
        "max_generation_attempts": 64, "liveness_window": 60,
        "margin_collapse_threshold": 100, "config_dir": Path("."),
    }
    cfg.update(overrides)
    return cfg


class TestScheduling(unittest.TestCase):
    def test_apportionment_is_exact_and_deterministic(self):
        out = fp.schedule({"a": 0.5, "b": 0.25, "c": 0.25}, 8)
        self.assertEqual(out.count("a"), 4)
        self.assertEqual(out.count("b"), 2)
        self.assertEqual(out.count("c"), 2)
        self.assertEqual(out, fp.schedule({"a": 0.5, "b": 0.25, "c": 0.25}, 8))

    def test_choke_share_of_committed_config(self):
        cfg = json.loads((HERE / "fuzz-panel-config.json").read_text())
        out = fp.schedule(cfg["class_mix"], int(cfg["maps"]))
        self.assertGreaterEqual(out.count("choke_corridor") / len(out), 0.20)


class TestGenerator(unittest.TestCase):
    def test_same_seed_byte_identical_specs(self):
        cfg = mini_cfg(seeds=[982451653])
        for cls in fp.MAP_CLASSES:
            a = fp.build_skeleton(3, cls, "harvester", cfg)
            b = fp.build_skeleton(3, cls, "harvester", cfg)
            self.assertEqual(json.dumps(a, sort_keys=True),
                             json.dumps(b, sort_keys=True), cls)

    def test_different_index_different_map(self):
        cfg = mini_cfg(seeds=[982451653])
        a = fp.build_skeleton(0, "open_field", "idle", cfg)
        b = fp.build_skeleton(1, "open_field", "idle", cfg)
        self.assertNotEqual(json.dumps(a, sort_keys=True),
                            json.dumps(b, sort_keys=True))

    def test_generated_specs_are_valid(self):
        cfg = mini_cfg(seeds=[982451653, 15485863])
        for i, cls in enumerate(fp.MAP_CLASSES):
            _, specs = fp.build_skeleton(i, cls, "harvester", cfg)
            self.assertEqual([s["seat"] for s in specs], [0, 1], cls)
            for spec in specs:
                rows = spec["rows"]
                self.assertLessEqual(len(rows[0]), 14)
                self.assertLessEqual(len(rows), 8)
                geo = sh.parse_rows(tuple(rows))
                self.assertIn(0, geo["shacks"], cls)   # tent placed
                self.assertIn(1, geo["shacks"], cls)
                walk = geo["walkable"]
                own_doors = sorted(
                    c for c in fp._orth_neighbors(geo["shacks"][0])
                    if c in walk)
                self.assertTrue(own_doors, cls)        # at least one door
                reach = sh.bfs(walk, own_doors)
                opp_doors = sorted(
                    c for c in fp._orth_neighbors(geo["shacks"][1])
                    if c in walk)
                self.assertTrue(opp_doors, cls)
                self.assertIn(opp_doors[0], reach, cls)   # connectivity
                for p in spec["plants"]:
                    self.assertIn((p[1], p[2]), reach, cls)
                for u in spec["units"]:
                    self.assertIn((u[2], u[3]), walk, cls)
            self.assertTrue(
                cls != "orchard_eligible" or specs[0]["orchard_eligible"])

    def test_seat_variants_swap_tents(self):
        cfg = mini_cfg(seeds=[982451653])
        skel, specs = fp.build_skeleton(0, "open_field", "idle", cfg)
        g0 = sh.parse_rows(tuple(specs[0]["rows"]))
        g1 = sh.parse_rows(tuple(specs[1]["rows"]))
        self.assertEqual(g0["shacks"][0], g1["shacks"][1])
        self.assertEqual(g0["shacks"][1], g1["shacks"][0])


class TestOrchardMirror(unittest.TestCase):
    def test_known_orchard_map_is_eligible(self):
        rows = list(sh.MAP_ORCHARD)
        plants = [["LEMON", 12, 2, 4, 12, 1, 0]]
        self.assertTrue(fp.orchard_eligible_view(rows, plants))

    def test_ring_map_is_not_eligible(self):
        rows = ["..............",
                ".0...........1",
                "..............",
                "..............",
                ".............."]
        plants = [["LEMON", 12, 2, 4, 12, 1, 0]]
        self.assertFalse(fp.orchard_eligible_view(rows, plants))

    def test_no_naturals_is_not_eligible(self):
        self.assertFalse(fp.orchard_eligible_view(list(sh.MAP_ORCHARD), []))


class TestProperties(unittest.TestCase):
    def test_p2_catches_planted_r5_oscillator(self):
        transcript, commands = rt.control_r5_oscillator()
        tr = td.build_trace(transcript, commands)
        _, alternations, _ = fp.eval_p2(tr)
        self.assertTrue(alternations)
        self.assertIn("alternation", alternations[0]["why"])

    def test_p2_passes_compliant_r5_control(self):
        transcript, commands = rt.control_r5_compliant()
        tr = td.build_trace(transcript, commands)
        _, alternations, horizon = fp.eval_p2(tr)
        self.assertEqual(alternations, [])
        self.assertEqual(horizon, [])

    def test_p3_synthetic_mismatch(self):
        viol = fp.eval_p3(True, "WAIT\nMOVE 0 1 1\n", "WAIT\nWAIT\n")
        self.assertEqual(len(viol), 1)
        self.assertEqual(viol[0]["first_divergence_turn"], 2)

    def test_p3_equal_streams_and_ineligible_maps_pass(self):
        self.assertEqual(fp.eval_p3(True, "WAIT\n", "WAIT\n"), [])
        self.assertEqual(fp.eval_p3(False, "A\n", "B\n"), [])

    def test_p4_stall_windows(self):
        self.assertEqual(fp.stall_windows(set(), 200, 60), [(1, 199)])
        self.assertEqual(fp.stall_windows({100}, 200, 60),
                         [(1, 99), (101, 199)])
        self.assertEqual(fp.stall_windows(set(range(1, 200, 30)), 200, 60),
                         [])


# ---------------------------------------------------------------------------
# Synthetic trace builder (real StaticMap/GameState objects via the parser,
# so world-state predicates see exactly what a live game would expose)
# ---------------------------------------------------------------------------

OPEN_ROWS = ("0.....",
             "......",
             "......")
# column x=3 is a solid wall: (5,2) is unreachable from the unit at (1,0).
WALLED_ROWS = ("0..#..",
               "...#..",
               "...#..")
RIPE_LEMON = ("LEMON", 5, 2, 4, 12, 1, 3)      # kind x y size health fruits cd


def synth_trace(rows, frames, commands=None):
    """Build a real td.Trace from per-turn frames.

    frames: [{"inv": [6 ints], "plants": [(kind,x,y,size,health,fruits,cd)],
              "units": [[id,player,x,y,speed,cap,harvest,chop,*carry6]]}]
    """
    parts = ["%d %d" % (len(rows[0]), len(rows))] + list(rows)
    for f in frames:
        parts.append(" ".join(str(v) for v in f["inv"]))
        parts.append(" ".join(str(v) for v in f.get("opp_inv", [0] * 6)))
        parts.append(str(len(f["plants"])))
        for p in f["plants"]:
            parts.append(" ".join(str(v) for v in p))
        parts.append(str(len(f["units"])))
        for u in f["units"]:
            parts.append(" ".join(str(v) for v in u))
    transcript = "\n".join(parts) + "\n"
    cmds = commands if commands is not None else ["WAIT"] * len(frames)
    return td.build_trace(transcript, "\n".join(cmds) + "\n")


def post_state(rows=OPEN_ROWS, banked=0, carry=0, plants=(), cell=(1, 0),
               opp_inv=None, opp_units=()):
    """A single referee frame standing for the post-C_T world state (the
    state after the final turn's commands resolve), in the same shape
    `stall_trace` produces its per-turn frames."""
    units = [[7, 0, cell[0], cell[1], 1, 2, 1, 1, 0, 0, 0, 0, 0, carry]]
    units.extend(list(u) for u in opp_units)
    frames = [{"inv": [0, 0, 0, 0, 0, banked],
               "opp_inv": list(opp_inv or [0] * 6),
               "plants": list(plants), "units": units}]
    return synth_trace(rows, frames).state(1)


def stall_trace(T, plants_at, banked_at, carry_at=lambda t: 0,
                rows=OPEN_ROWS, cell=(1, 0), commands=None):
    """One own unit (harvest 1 / chop 1) at `cell`; own banked wood and own
    cargo follow the supplied per-turn functions (the two quantities P4
    reads), the world its plant function."""
    frames = []
    for t in range(1, T + 1):
        frames.append({
            "inv": [0, 0, 0, 0, 0, banked_at(t)],
            "plants": list(plants_at(t)),
            "units": [[7, 0, cell[0], cell[1], 1, 2, 1, 1,
                       0, 0, 0, 0, 0, carry_at(t)]],
        })
    return synth_trace(rows, frames, commands)


class TestRawGate(unittest.TestCase):
    """Owner ruling 2026-08-06: the gate is RAW/ABSOLUTE. Every detector
    D-1..D-9 episode blocks, inherited-from-parent or not; P4 liveness has no
    parent exemption. These tests pin the raw semantics (they FAIL against
    the pre-repair parent-differential / inherited-report-only code)."""

    _PASS = {"verdict": "PASS", "count": 0, "episodes": []}

    def _passes(self, *names):
        return [dict(self._PASS, detector=n) for n in names]

    def test_p1_d9_blocks_even_when_parent_reproduces_it(self):
        # A D-9 episode the PARENT reproduces byte-for-byte on the identical
        # map. Old code: gate_d9_parent_differential drops it (report-only).
        # Raw: it blocks.
        ep = {"unit": 0, "turn": 5, "kind": "BANANA", "command": "HARVEST"}
        d9_fail = {"detector": "D-9", "verdict": "FAIL", "count": 1,
                   "episodes": [ep]}
        results = self._passes("D-1", "D-2", "D-3", "D-4", "D-5", "D-6",
                               "D-7", "D-8") + [d9_fail]
        orig_run_all, orig_d9 = fp.td.run_all, fp.td.detect_d9
        fp.td.run_all = lambda tr, pc=None: [dict(r) for r in results]
        fp.td.detect_d9 = lambda tr, pc=None: {
            "detector": "D-9", "verdict": "FAIL", "count": 1,
            "episodes": [ep]}       # parent reproduces the identical episode
        try:
            _, viol, inherited, dropped = fp.eval_p1(None, None, None, False)
        finally:
            fp.td.run_all, fp.td.detect_d9 = orig_run_all, orig_d9
        self.assertTrue(
            any(v["detector"] == "D-9" for v in viol),
            "D-9 must block under raw even when the parent reproduces the "
            "identical episode (no parent-differential exemption)")
        self.assertEqual(dropped, 0, "no D-9 episode may be dropped under raw")

    def test_p1_d1_blocks_when_parent_also_oscillates(self):
        # A candidate D-1 episode on a map where the parent ALSO fails D-1.
        # Old code: downgraded to a report-tier inherited-parent-D1 flag.
        # Raw: it blocks.
        ep = {"unit": 0, "turn_start": 2, "turn_end": 10, "k": 4,
              "cells": [[1, 1], [2, 1]]}
        d1_fail = {"detector": "D-1", "verdict": "FAIL", "count": 1,
                   "episodes": [ep]}
        results = [d1_fail] + self._passes("D-2", "D-3", "D-4", "D-5", "D-6",
                                           "D-7", "D-8", "D-9")
        orig_run_all = fp.td.run_all
        fp.td.run_all = lambda tr, pc=None: [dict(r) for r in results]
        try:
            _, viol, inherited, _ = fp.eval_p1(None, None, None, True)
        finally:
            fp.td.run_all = orig_run_all
        self.assertTrue(
            any(v["detector"] == "D-1" for v in viol),
            "D-1 must block under raw even when the parent also fails D-1 "
            "(no inherited-report-only downgrade)")
        self.assertEqual(inherited, [],
                         "no inherited-report-only downgrade exists under raw")

    def test_p4_blocks_when_parent_also_stalls(self):
        # A full-game candidate stall that the parent reproduces (parent also
        # makes no progress in the window). Old code: exempted as an
        # inherited WAIT-equilibrium. Raw: it blocks. Work REMAINS all game
        # (a reachable ripe plant), so the terminal-state calibration must
        # not excuse it either.
        tr = stall_trace(10, lambda t: [RIPE_LEMON], lambda t: 0)
        viol = fp.eval_p4(tr, tr, window=6)
        self.assertTrue(
            viol, "P4 must block a stall window even when the parent stalls "
                  "identically in the same window (raw liveness, no parent "
                  "exemption)")
        self.assertEqual(viol[0]["window_start"], 1)


class TestP4TerminalCalibration(unittest.TestCase):
    """P4 terminal-state calibration (ABSOLUTE, no parent reference).

    A stall window is only a liveness failure over the turns in which the
    referee world still offers the candidate a resource action: a plant
    reachable by an own unit (to harvest or chop) or cargo still held (to
    bank/plant). Turns after the world is exhausted for the rest of the game
    are excused; a stall while work REMAINS still blocks, trailing or not.
    """

    T = 200
    WINDOW = 60

    def test_finished_work_then_idle_to_horizon_passes(self):
        # Bot works until turn 120 (banking every turn), clears the last
        # plant, and idles to the horizon with empty cargo. The trailing
        # 120-199 stall is explained by an exhausted world, not by the bot
        # being stuck -> must PASS. (RED before the calibration.)
        tr = stall_trace(
            self.T,
            lambda t: [] if t > 120 else [RIPE_LEMON],
            lambda t: min(t, 120))
        self.assertEqual(fp.stall_windows(fp.progress_turns(tr), tr.T,
                                          self.WINDOW), [(120, 199)])
        self.assertEqual(
            fp.eval_p4(tr, None, self.WINDOW), [],
            "a trailing stall after the world is exhausted (no reachable "
            "plant, empty cargo) is not a liveness failure")

    def test_midgame_stall_with_work_remaining_blocks(self):
        # Stalls turns 40-109 with a reachable ripe plant on the board, then
        # resumes: a genuine mid-game liveness bug -> must BLOCK.
        tr = stall_trace(
            self.T,
            lambda t: [RIPE_LEMON],
            lambda t: t if t <= 40 else (40 if t <= 110 else 40 + (t - 110)))
        viol = fp.eval_p4(tr, None, self.WINDOW)
        self.assertEqual([(v["window_start"], v["window_end"]) for v in viol],
                         [(40, 109)],
                         "a mid-game stall with work remaining must block")

    def test_trailing_stall_with_work_remaining_blocks(self):
        # Stalls from turn 40 to the horizon while a reachable ripe plant is
        # still on the board: trailing, but NOT explained by a terminal
        # world -> must BLOCK (the over-exemption guard).
        tr = stall_trace(
            self.T, lambda t: [RIPE_LEMON], lambda t: min(t, 40))
        viol = fp.eval_p4(tr, None, self.WINDOW)
        self.assertEqual([(v["window_start"], v["window_end"]) for v in viol],
                         [(40, 199)],
                         "a stall running to the horizon still blocks while "
                         "reachable work remains")

    def test_trailing_stall_with_unbanked_cargo_blocks(self):
        # Board cleared, but the unit still holds cargo it never banks: work
        # remains (banking is progress) -> must BLOCK.
        tr = stall_trace(
            self.T, lambda t: [], lambda t: min(t, 40), carry_at=lambda t: 1)
        viol = fp.eval_p4(tr, None, self.WINDOW)
        self.assertEqual([(v["window_start"], v["window_end"]) for v in viol],
                         [(40, 199)],
                         "held cargo is unfinished work even with an empty "
                         "board")

    def test_only_plant_unreachable_is_terminal(self):
        # The one remaining plant is walled off from the own unit: the world
        # offers nothing, so the stall is terminal -> PASS.
        tr = stall_trace(
            self.T, lambda t: [RIPE_LEMON], lambda t: min(t, 40),
            rows=WALLED_ROWS)
        self.assertEqual(fp.eval_p4(tr, None, self.WINDOW), [],
                         "a plant no own unit can reach is not work")

    def test_no_parent_reference_in_eval_p4_body(self):
        # The raw ruling stands: the calibration must be absolute. Only the
        # (documentary) signature and docstring may name tr_p at all.
        src = inspect.getsource(fp.eval_p4)
        self.assertGreaterEqual(src.count('"""'), 2)
        body = src.split('"""')[2]
        for token in ("parent", "inherit", "aligned", "tr_p"):
            self.assertNotIn(
                token, body,
                "eval_p4 body must not reference %r (absolute gate)" % token)

    def test_work_remaining_is_a_pure_world_state_predicate(self):
        ripe = stall_trace(3, lambda t: [RIPE_LEMON], lambda t: 0)
        empty = stall_trace(3, lambda t: [], lambda t: 0)
        walled = stall_trace(3, lambda t: [RIPE_LEMON], lambda t: 0,
                             rows=WALLED_ROWS)
        carrying = stall_trace(3, lambda t: [], lambda t: 0,
                               carry_at=lambda t: 1)
        self.assertTrue(fp.work_remaining(ripe, 1))
        self.assertFalse(fp.work_remaining(empty, 1))
        self.assertFalse(fp.work_remaining(walled, 1))
        self.assertTrue(fp.work_remaining(carrying, 1))
        self.assertEqual(fp.live_horizon(ripe), 4)      # never terminal
        self.assertEqual(fp.live_horizon(empty), 1)     # terminal all game


class TestP4PostCT(unittest.TestCase):
    """P4 post-C_T referee-state rule (ABSOLUTE, no parent reference).

    The transcript records S_1..S_T, every state being the world BEFORE that
    turn's commands resolve, so the outcome of the final command set C_T is
    invisible: the last turn carries no liveness obligation at all today --
    a do-nothing C_T is never counted as a stalled turn, and a C_T that banks
    or plants is never counted as progress.  The rule closes both halves with
    the post-C_T referee state (the world after C_T resolves):

      turn T is a stalled turn  <=>  work remains in S_T (pre-state
      obligation, unchanged) AND resolving C_T changes neither the own
      inventory nor any own unit's cargo (post-state outcome).

    Both directions are pinned below: a final turn that completes work must
    not be counted as a stall, and a final turn that does nothing must be.
    """

    T = 10
    WINDOW = 6

    def base(self):
        """Progress on turns 1-4, then a stall to the horizon: turns 5-9 are
        five OBSERVABLE stalled turns -- one short of the window -- so the
        verdict turns entirely on how turn T=10 is counted."""
        tr = stall_trace(self.T, lambda t: [RIPE_LEMON],
                         lambda t: min(t, 5))
        self.assertEqual(fp.progress_turns(tr), {1, 2, 3, 4})
        self.assertEqual(fp.stall_windows(fp.progress_turns(tr), tr.T,
                                          self.WINDOW), [])
        return tr

    def test_idle_final_turn_completes_the_stall_window(self):
        # C_T resolves to nothing (post state == S_T): turns 5-10 are six
        # stalled turns over a live world -> BLOCK.
        tr = self.base()
        idle = post_state(banked=5, carry=0, plants=[RIPE_LEMON])
        viol = fp.eval_p4(tr, None, self.WINDOW, idle)
        self.assertEqual(
            [(v["window_start"], v["window_end"]) for v in viol],
            [(5, self.T)],
            "a final turn whose commands change nothing is a stalled turn "
            "and must complete the window")

    def test_final_turn_that_banks_is_progress_and_passes(self):
        # Same game, but C_T banks (own inventory rises): turn T is progress,
        # so only five stalled turns remain -> PASS.
        tr = self.base()
        banked = post_state(banked=6, carry=0, plants=[RIPE_LEMON])
        self.assertEqual(
            fp.eval_p4(tr, None, self.WINDOW, banked), [],
            "work completed by C_T is progress, not a stall")

    def test_final_turn_cargo_change_is_progress_and_passes(self):
        # Cargo side of the same predicate: C_T harvests/picks up.
        tr = self.base()
        picked = post_state(banked=5, carry=1, plants=[RIPE_LEMON])
        self.assertEqual(fp.eval_p4(tr, None, self.WINDOW, picked), [],
                         "an own-cargo change at C_T is progress")

    def test_opponent_only_change_at_C_T_is_not_own_progress(self):
        # Anti-vacuity: the post state moves only for the OPPONENT.  P4 is an
        # own-progress property, so the window must still close -> BLOCK.
        tr = self.base()
        opp = post_state(banked=5, carry=0, plants=[RIPE_LEMON],
                         opp_inv=[9, 9, 9, 9, 9, 9],
                         opp_units=[[8, 1, 3, 1, 1, 2, 1, 1,
                                     1, 1, 1, 1, 1, 1]])
        viol = fp.eval_p4(tr, None, self.WINDOW, opp)
        self.assertEqual(
            [(v["window_start"], v["window_end"]) for v in viol],
            [(5, self.T)],
            "opponent inventory/cargo movement at C_T is not own progress")

    def test_terminal_world_at_T_carries_no_final_turn_obligation(self):
        # The obligation half stays PRE-state: with the world exhausted (no
        # plant, no cargo) the final turn is not live, so an idle C_T cannot
        # complete a window -> PASS.
        tr = stall_trace(self.T, lambda t: [], lambda t: min(t, 5))
        idle = post_state(banked=5, carry=0, plants=[])
        self.assertEqual(fp.eval_p4(tr, None, self.WINDOW, idle), [],
                         "an exhausted world imposes no obligation on the "
                         "final turn either")

    def test_completing_work_at_C_T_does_not_excuse_a_longer_stall(self):
        # Over-exemption guard: a 160-turn stall that ends with a final-turn
        # bank is still a 160-turn stall -> BLOCK.
        tr = stall_trace(200, lambda t: [RIPE_LEMON], lambda t: min(t, 40))
        banked = post_state(banked=41, carry=0, plants=[RIPE_LEMON])
        viol = fp.eval_p4(tr, None, 60, banked)
        self.assertEqual([(v["window_start"], v["window_end"]) for v in viol],
                         [(40, 199)],
                         "post-C_T progress ends the window at T-1; it does "
                         "not retroactively excuse the stalled turns")

    def test_without_a_post_state_the_final_turn_is_not_counted(self):
        # Back-compatible call shape: with no post-C_T state the outcome of
        # C_T is unknown, so turn T carries no obligation (the pre-rule
        # behaviour, kept for callers that cannot supply the referee state).
        tr = self.base()
        self.assertEqual(fp.eval_p4(tr, None, self.WINDOW), [])
        self.assertEqual(fp.eval_p4(tr, None, self.WINDOW, None), [])

    def test_post_ct_progress_predicate(self):
        tr = self.base()
        self.assertFalse(fp.post_ct_progress(
            tr, post_state(banked=5, carry=0, plants=[RIPE_LEMON])))
        self.assertTrue(fp.post_ct_progress(
            tr, post_state(banked=6, carry=0, plants=[RIPE_LEMON])))
        self.assertTrue(fp.post_ct_progress(
            tr, post_state(banked=5, carry=2, plants=[RIPE_LEMON])))
        # plant growth between S_T and the post state is world motion, not
        # own progress
        grown = post_state(banked=5, carry=0,
                           plants=[("LEMON", 5, 2, 4, 12, 2, 3)])
        self.assertFalse(fp.post_ct_progress(tr, grown))

    def test_stall_windows_last_known_turn(self):
        # The default (T-1) reproduces the historical behaviour exactly; the
        # post-C_T caller passes T to make the final turn countable.
        self.assertEqual(fp.stall_windows({1, 2, 3, 4}, 10, 6), [])
        self.assertEqual(fp.stall_windows({1, 2, 3, 4}, 10, 6, 10),
                         [(5, 10)])
        self.assertEqual(fp.stall_windows({1, 2, 3, 4}, 10, 6, 9),
                         fp.stall_windows({1, 2, 3, 4}, 10, 6))
        self.assertEqual(fp.stall_windows(set(), 200, 60, 200), [(1, 200)])

    def test_post_ct_state_reads_the_live_referee(self):
        # Plumbing: the panel's own referee, after the final command has been
        # applied, is the authority for the post-C_T world state.
        # a live FuzzReferee needs both tents on the map
        rows = ["0....1", "......", "......"]
        spec = {"rows": rows, "inventory": [0] * 6, "plants": [],
                "units": [[7, 0, 1, 0, 1, 2, 1, 1, 0, 1, 0, 0, 0, 0]],
                "profile": "idle"}
        ref = fp.make_referee(spec)
        before = fp.post_ct_state(ref)
        self.assertEqual(list(before.inventories[0]), [0] * 6)
        self.assertEqual(list(before.own_units()[0].carry),
                         [0, 1, 0, 0, 0, 0])
        ref.apply("DROP 7")          # banks the carried LEMON at the door
        after = fp.post_ct_state(ref)
        self.assertEqual(list(after.inventories[0]), [0, 1, 0, 0, 0, 0])
        self.assertEqual(sum(after.own_units()[0].carry), 0)


class TestExitCodes(unittest.TestCase):
    def run_panel(self, candidate_src: Path, parent_src: Path, tmp: Path,
                  **cfg_overrides) -> tuple[int, dict | None]:
        cfg = {
            "task": "fuzz-selftest",
            "candidate": {"source": str(candidate_src)},
            "parent": {"source": str(parent_src)},
            "seeds": [11], "maps": 2, "turns": 30, "processes": 1,
            "class_mix": {"open_field": 1.0}, "opponent_mix": {"idle": 1.0},
        }
        cfg.update(cfg_overrides)
        cfg_path = tmp / "cfg.json"
        cfg_path.write_text(json.dumps(cfg))
        code = fp.main(["--config", str(cfg_path),
                        "--report", str(tmp / "report.md"),
                        "--json", str(tmp / "report.json"),
                        "--save-failures", str(tmp / "failures")])
        payload = None
        if (tmp / "report.json").exists():
            payload = json.loads((tmp / "report.json").read_text())
        return code, payload

    def test_exit_0_clear_wait_bot_vs_itself(self):
        wait = compiled_bot("waitbot", WAIT_BOT)
        with tempfile.TemporaryDirectory() as tmp:
            code, payload = self.run_panel(wait, wait, Path(tmp))
            self.assertEqual(code, fp.EXIT_CLEAR)
            self.assertEqual(payload["verdict"], "CLEAR")
            self.assertEqual(payload["stats"]["games"], 4)
            self.assertEqual(payload["stats"]["blocking_games"], 0)
            self.assertTrue((Path(tmp) / "report.md").exists())

    def test_exit_1_block_planted_oscillator_caught_by_d1(self):
        wait = compiled_bot("waitbot", WAIT_BOT)
        osc = compiled_bot("oscbot", OSCILLATOR_BOT)
        with tempfile.TemporaryDirectory() as tmp:
            code, payload = self.run_panel(osc, wait, Path(tmp))
            self.assertEqual(code, fp.EXIT_BLOCK)
            self.assertEqual(payload["verdict"], "BLOCK")
            blocked = [g for g in payload["games"] if g["block"]]
            self.assertTrue(blocked)
            d1 = [v for g in blocked for v in g["violations"]
                  if v.get("detector") == "D-1"]
            self.assertTrue(d1, "planted oscillator must be caught by P1/D-1")
            # failure artifacts saved for every blocking game
            for g in blocked:
                d = Path(tmp) / "failures" / (
                    "%s-s%d" % (g["map_id"], g["seat"]))
                self.assertTrue((d / "candidate-commands.txt").exists())
                self.assertTrue((d / "properties.json").exists())

    def test_exit_1_raw_gate_blocks_oscillator_vs_itself(self):
        # RAW gate acceptance proof: the planted oscillator run against
        # ITSELF as parent. Under the old mixed rules D-1 was downgraded to
        # an inherited-parent-D1 flag and the all-stall window was exempted
        # as an inherited WAIT-equilibrium -> CLEAR. Under raw both block.
        osc = compiled_bot("oscbot", OSCILLATOR_BOT)
        with tempfile.TemporaryDirectory() as tmp:
            # 30-turn games -> use a 10-turn liveness window so a full-game
            # stall window forms (the default 60 exceeds the game length).
            code, payload = self.run_panel(osc, osc, Path(tmp),
                                           liveness_window=10)
            self.assertEqual(
                code, fp.EXIT_BLOCK,
                "raw gate must block a candidate D-1/P4 even when the parent "
                "oscillates identically")
            blocked = [g for g in payload["games"] if g["block"]]
            self.assertTrue(blocked)
            dets = {v.get("detector") for g in blocked for v in g["violations"]}
            props = {v["property"] for g in blocked for v in g["violations"]}
            self.assertIn("D-1", dets, "D-1 must block raw")
            self.assertIn("P4", props, "P4 stall must block raw")
            flags = {f["flag"] for g in payload["games"] for f in g["flags"]}
            self.assertNotIn("inherited-parent-D1", flags,
                             "the inherited-report-only downgrade is removed")
            self.assertNotIn("inherited-parent-D9", flags,
                             "the parent-differential D-9 downgrade is removed")

    def test_panel_supplies_the_post_ct_referee_state_to_p4(self):
        # Plumbing, end to end: every game's P4 evaluation must receive the
        # post-C_T referee state (a real GameState), never None -- otherwise
        # the final turn silently keeps its old free pass.
        wait = compiled_bot("waitbot", WAIT_BOT)
        seen = []
        orig = fp.eval_p4

        def spy(tr_c, tr_p, window, post_state=None):
            seen.append(post_state)
            return orig(tr_c, tr_p, window, post_state)

        fp.eval_p4 = spy
        try:
            with tempfile.TemporaryDirectory() as tmp:
                self.run_panel(wait, wait, Path(tmp), maps=1, turns=8)
        finally:
            fp.eval_p4 = orig
        self.assertEqual(len(seen), 2, "one P4 evaluation per game")
        for post in seen:
            self.assertIsInstance(
                post, td.GameState,
                "run_pair must hand P4 the post-C_T referee state")
            self.assertTrue(post.own_units())

    def test_exit_2_on_missing_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            code = fp.main(["--config", str(Path(tmp) / "absent.json"),
                            "--report", str(Path(tmp) / "r.md")])
            self.assertEqual(code, fp.EXIT_ERROR)

    def test_exit_2_on_sha_mismatch(self):
        wait = compiled_bot("waitbot", WAIT_BOT)
        with tempfile.TemporaryDirectory() as tmp:
            code, _ = self.run_panel(
                wait, wait, Path(tmp),
                candidate={"source": str(wait), "sha256": "0" * 64})
            self.assertEqual(code, fp.EXIT_ERROR)


if __name__ == "__main__":
    unittest.main()
