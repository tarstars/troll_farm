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

import ast
import contextlib
import hashlib
import inspect
import io
import json
import sys
import tempfile
import textwrap
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

# Planted bot for the r2 revision: trains as often as the ENGINE allows.
# Every turn it walks each own unit to a private parking cell (so the shack is
# free, engine.rs:545) and appends a TRAIN.  The floor bot never exercises
# this -- its own can_train refuses past two workers -- so this bot is the
# end-to-end evidence that the referee no longer forbids what engine.rs
# permits.
TRAINER_BOT = r"""
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
        if lines.next().is_none() { return; }   // own inventory
        lines.next();                           // opponent inventory
        let np: usize = lines.next().unwrap().trim().parse().unwrap();
        for _ in 0..np { lines.next(); }
        let nu: usize = lines.next().unwrap().trim().parse().unwrap();
        let mut mine: Vec<i64> = Vec::new();
        for _ in 0..nu {
            let line = lines.next().unwrap();
            let v: Vec<i64> = line.split_whitespace()
                .map(|t| t.parse().unwrap()).collect();
            if v[1] == 0 { mine.push(v[0]); }
        }
        mine.sort();
        let mut cmds: Vec<String> = Vec::new();
        for (i, id) in mine.iter().enumerate() {
            cmds.push(format!("MOVE {} {} {}", id,
                              1 + (i % 10) as i64, 1 + (i / 10) as i64));
        }
        cmds.push("TRAIN 1 1 0 1".to_string());
        println!("{}", cmds.join(";"));
        std::io::stdout().flush().unwrap();
    }
}
"""

# Planted defect bot: emits a verb the referee does not implement. The
# exhaustive dispatcher must terminate the run (GATE_UNREADY /
# unsupported_command) rather than silently discard it.
BOGUS_VERB_BOT = r"""
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
        println!("TELEPORT 0 1 1");
        std::io::stdout().flush().unwrap();
    }
}
"""

_BOT_CACHE: dict[str, Path] = {}
_BIN_CACHE: dict[str, Path] = {}
_BOT_DIR: tempfile.TemporaryDirectory | None = None


def _bot_dir() -> Path:
    global _BOT_DIR
    if _BOT_DIR is None:
        _BOT_DIR = tempfile.TemporaryDirectory(prefix="fuzz-selftest-")
    return Path(_BOT_DIR.name)


def compiled_bot(name: str, source: str) -> Path:
    if name not in _BOT_CACHE:
        src = _bot_dir() / (name + ".rs")
        src.write_text(source)
        binary = _bot_dir() / name
        sh.compile_text(source, binary, "selftest_" + name)
        _BOT_CACHE[name] = src
    return _BOT_CACHE[name]


# The floor bot: the submission the committed panel config runs as parent and
# the one the two mandatory m040 regression rows are defined against.
FLOOR_BOT_SOURCE = (HERE.parent.parent / "cgauto" / "submissions"
                    / "candidate-agent6553250-preseed-orchard-coverage-slim"
                      ".min.rs")


def compiled_binary(name: str, source_path: Path, source: str = None) -> Path:
    """Compile a submission (or literal source) once per test process and
    return the BINARY path (compiled_bot returns the source path for CLI
    configs)."""
    if name not in _BIN_CACHE:
        binary = _bot_dir() / ("bin-" + name)
        text = source if source is not None else source_path.read_text()
        sh.compile_text(text, binary, "selftest_" + name)
        _BIN_CACHE[name] = binary
    return _BIN_CACHE[name]


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
            # r3 / review B7: both version keys must be present in the RAW
            # config or load_config fails closed.
            "instrument_version": fp.INSTRUMENT_VERSION,
            "corpus_version": fp.CORPUS_VERSION,
            # review B5: one bot against itself IS the floor, two bots are a
            # candidate run, and load_config refuses a mislabelled config.
            "run_identity": ("floor" if candidate_src == parent_src
                             else "candidate"),
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


# ---------------------------------------------------------------------------
# Referee command dispatch + TRAIN (referee TRAIN repair, 2026-08-09)
#
# Conformance reference: rust/src/bin/yamo_orchard_live.rs (authoritative
# engine, sacred / byte-untouchable).  Every rule asserted below carries its
# source line in the referee-train-repair-2026-08-09.md report.
# ---------------------------------------------------------------------------

TRAIN_ROWS = ("0....1",
              "......",
              "......")
# Room for a dozen workers to park off the shack.
TRAINER_ROWS = ("0..........1",
                "............",
                "............",
                "............",
                "............")
IRON_ROWS = ("0..+.1",          # '+' at (3,0): iron present, not walkable
             "......",
             "......")


def train_referee(rows=TRAIN_ROWS, inventory=(0, 0, 0, 0, 0, 0),
                  units=None, plants=(), profile="idle"):
    """A live FuzzReferee on a tiny map: own unit 0 on the tent's door
    (1,0), opponent unit 5 parked far away (so the spawned worker's id is
    max(existing)+1 = 6, the engine's read_turn next_id rule)."""
    if units is None:
        units = [[0, 0, 1, 0, 1, 2, 1, 1] + [0] * 6,
                 [5, 1, 4, 2, 1, 2, 0, 0] + [0] * 6]
    return fp.make_referee({
        "rows": list(rows), "inventory": list(inventory),
        "plants": [list(p) for p in plants],
        "units": [list(u) for u in units], "profile": profile})


class TestExhaustiveDispatch(unittest.TestCase):
    """Requirement 1: the command dispatcher is exhaustive.  An unknown or
    unimplemented verb terminates the run as GATE_UNREADY /
    unsupported_command -- there is no silent default branch anywhere.  This
    is the defect class (silent default) that produced D-9, D-6, the I-30
    tie-break and this referee."""

    def test_unknown_verb_is_a_retained_structured_error(self):
        # REVISION r3 (review B6/B7): the verb is still fail-closed, but the
        # ROW must survive into the denominator, so the referee RECORDS the
        # error instead of aborting the run before any row is written.
        ref = train_referee()
        ref.apply("TELEPORT 0 1 1")
        err = ref.command_errors[0]
        self.assertEqual(err["kind"], fp.ERROR_UNSUPPORTED_VERB)
        self.assertEqual(err["verb"], "TELEPORT")
        self.assertEqual(err["raw"], "TELEPORT 0 1 1")
        self.assertEqual(err["turn"], 1)
        self.assertIn("GATE_UNREADY", err["reason"])

    def test_an_unsupported_verb_makes_the_aggregate_gate_unready(self):
        self.assertEqual(fp.aggregate_verdict(
            [{"execution_status": fp.ERROR_UNSUPPORTED_VERB, "block": False}]),
            "GATE_UNREADY")

    def test_unknown_verb_anywhere_in_a_multi_command_line(self):
        ref = train_referee()
        ref.apply("MOVE 0 2 0;TELEPORT 0 1 1")
        self.assertEqual([e["verb"] for e in ref.command_errors], ["TELEPORT"])

    def test_dispatch_table_is_total_over_the_engine_verb_set(self):
        # Every verb the engine's command parser recognises must have a
        # handler; nothing may fall through to a default branch.
        self.assertEqual(fp.ENGINE_COMMANDS - fp.SUPPORTED_COMMANDS, set())
        self.assertEqual(set(fp.FuzzReferee.VERB_HANDLERS),
                         set(fp.SUPPORTED_COMMANDS))
        for verb in ("TRAIN", "MINE", "MOVE", "HARVEST", "CHOP", "PLANT",
                     "PICK", "DROP", "WAIT", "MSG"):
            self.assertIn(verb, fp.SUPPORTED_COMMANDS, verb)

    def test_verbs_are_matched_case_insensitively(self):
        ref = train_referee(inventory=[9, 9, 9, 0, 9, 0])
        ref.apply("train 1 1 0 1")
        self.assertEqual(len(ref.own_unit_ids()), 2)

    def test_panel_exits_gate_unready_on_an_unsupported_verb(self):
        # Superseded in r3 by TestUnsupportedVerbRetainsTheRow: the exit code
        # is still 2, but the report/JSON must now be PUBLISHED with every
        # affected row retained (contract §8) rather than the run aborting.
        bogus = compiled_bot("bogusverbbot", BOGUS_VERB_BOT)
        wait = compiled_bot("waitbot", WAIT_BOT)
        with tempfile.TemporaryDirectory() as tmp:
            cfg = {
                "task": "fuzz-selftest-unsupported",
                "instrument_version": fp.INSTRUMENT_VERSION,
                "corpus_version": fp.CORPUS_VERSION,
                "run_identity": "candidate",
                "candidate": {"source": str(bogus)},
                "parent": {"source": str(wait)},
                "seeds": [11], "maps": 1, "turns": 8, "processes": 1,
                "class_mix": {"open_field": 1.0},
                "opponent_mix": {"idle": 1.0},
            }
            cfg_path = Path(tmp) / "cfg.json"
            cfg_path.write_text(json.dumps(cfg))
            report = Path(tmp) / "r.md"
            code = fp.main(["--config", str(cfg_path),
                            "--report", str(report)])
            self.assertEqual(code, fp.EXIT_ERROR,
                             "an unsupported verb must fail the gate closed")
            text = report.read_text()
            self.assertIn("GATE_UNREADY", text)
            self.assertIn("unsupported_verb", text)


class TestTrainingCost(unittest.TestCase):
    """yamo_orchard_live.rs:196-204  rules::training_cost."""

    def test_bill_matches_the_engine_formula(self):
        self.assertEqual(fp.training_cost(1, (1, 1, 0, 1)),
                         [2, 2, 1, 0, 2, 0])
        self.assertEqual(fp.training_cost(1, (2, 2, 0, 3)),
                         [5, 5, 1, 0, 10, 0])
        self.assertEqual(fp.training_cost(2, (3, 3, 3, 3)),
                         [11, 11, 11, 0, 11, 0])

    def test_banana_and_wood_are_never_billed(self):
        for n in (0, 1, 2):
            for t in ((0, 0, 0, 0), (3, 3, 3, 3)):
                cost = fp.training_cost(n, t)
                self.assertEqual(cost[3], 0)
                self.assertEqual(cost[5], 0)


def _body_ast(fn_or_src):
    """AST of a function (or of function source text) with the docstring
    stripped.

    The conformance tests below assert on the CODE, not on the prose: a
    citation of `engine.rs:527` in a docstring must not be able to satisfy
    (or fail) a test about whether the rule is implemented.  Comments are
    gone for free -- the parser drops them."""
    src = (fn_or_src if isinstance(fn_or_src, str)
           else inspect.getsource(fn_or_src))
    tree = ast.parse(textwrap.dedent(src))
    node = tree.body[0]
    if (node.body and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)):
        node.body = node.body[1:]
    return node


def _attrs_in_source_order(node) -> list:
    """Attribute names in SOURCE order.  `ast.walk` is breadth-first, so it
    cannot answer an ordering question."""
    out = []

    def visit(n):
        if isinstance(n, ast.Attribute):
            out.append(n.attr)
        for child in ast.iter_child_nodes(n):
            visit(child)

    for stmt in (node.body if hasattr(node, "body") else []):
        visit(stmt)
    return out


def _reads_the_turn_counter(fn_or_src) -> bool:
    """True iff the body reads `<something>.turn` or any TOTAL_TURNS-like
    global.  (A substring test would fire on the `turn` inside `return`.)"""
    for node in ast.walk(_body_ast(fn_or_src)):
        if isinstance(node, ast.Attribute) and node.attr == "turn":
            return True
        if isinstance(node, ast.Name) and "TURN" in node.id.upper():
            return True
    return False


class TestTrainAuthorityIsTheEngine(unittest.TestCase):
    """REVISION r2.  The authority for TRAIN legality is
    `rust/src/game/engine.rs::apply_train` (lines 525-568), NOT
    `MoisanBot::can_train` in `rust/src/bin/yamo_orchard_live.rs:834-844`.

    `yamo_orchard_live.rs:836`

        if n >= 2 || TOTAL_TURNS - view.turn <= 20 { return false; }

    is ONE BOT'S SELF-RESTRAINT.  `engine.rs::apply_train` enforces neither
    condition: between `let n = ...count()` (527) and the spawn (556-567) the
    only rejections are the affordability check (539-541) and the occupied
    shack check (545-547).  A referee that forbids what the engine permits
    would silently reject a candidate that trains a third worker while the
    real game accepts it -- the same class of defect as the silently
    discarded verb this work was repairing, pointing the other way."""

    def test_no_bot_derived_worker_cap_constant(self):
        self.assertFalse(
            hasattr(fp, "WORKER_CAP"),
            "engine.rs::apply_train has no worker cap; a WORKER_CAP constant "
            "in the referee is bot self-restraint smuggled in as a rule")

    def test_no_bot_derived_final_turn_guard_constant(self):
        self.assertFalse(
            hasattr(fp, "TRAIN_GUARD_TURNS"),
            "engine.rs::apply_train has no final-N-turn guard; a "
            "TRAIN_GUARD_TURNS constant in the referee is bot self-restraint "
            "smuggled in as a rule")

    def test_can_train_does_not_consult_the_turn_counter(self):
        self.assertFalse(
            _reads_the_turn_counter(fp.FuzzReferee.can_train),
            "engine.rs::apply_train (525-568) never reads game.turn; TRAIN "
            "legality must not depend on it")

    def test_train_does_not_consult_the_turn_counter(self):
        self.assertFalse(
            _reads_the_turn_counter(fp.FuzzReferee.train),
            "engine.rs::apply_train (525-568) never reads game.turn")

    def test_a_real_bot_trains_past_two_workers_closed_loop(self):
        """End-to-end, through the same compile + binary + referee loop the
        m040 regression rows use.  MEASURED necessity: on the committed
        240-game floor the floor bot emits TRAIN in exactly 2 of 240 games,
        once each (m040 s0 t=35, m040 s1 t=19) -- its own can_train refuses
        past two workers -- so the floor cannot exercise this at all.  A bot
        that does ask for more must get more."""
        binary = compiled_binary("trainerbot", None, TRAINER_BOT)
        ref = train_referee(rows=TRAINER_ROWS,
                            inventory=[99, 99, 99, 0, 0, 0],
                            units=[[0, 0, 1, 0, 1, 2, 1, 1] + [0] * 6,
                                   [5, 1, 10, 0, 1, 2, 0, 0] + [0] * 6])
        rt.run_binary_custom(binary, ref, 8)
        own = ref.own_unit_ids()
        self.assertGreater(
            len(own), 2,
            "a bot that asks for a third worker, can afford it and leaves "
            "the shack free must get it (engine.rs:525-568 imposes no cap)")
        for uid in own[1:]:
            u = ref.units[uid]
            self.assertEqual((u["speed"], u["cap"], u["harvest"], u["chop"]),
                             (1, 1, 0, 1))
        # The bill is the only limit: it grows with n (engine.rs:517-520), so
        # the run must stop while the inventory is still non-negative.
        self.assertTrue(all(v >= 0 for v in ref.inv), ref.inv)

    def test_the_turn_reader_itself_is_not_vacuous(self):
        """Guard on the guard: `_reads_the_turn_counter` must actually fire
        on the rule it is meant to forbid (the pre-revision `can_train`
        body), and must not fire on a body whose only `turn` is inside
        `return`."""
        bot_restraint = """
            def can_train(self, talents):
                '''yamo_orchard_live.rs:836'''
                if TOTAL_TURNS - self.turn <= 20:
                    return False
                return True
        """
        engine_rule = """
            def can_train(self, talents):
                '''engine.rs:539-541 -- the turn counter is never read.'''
                if self.inv[0] < 1:
                    return False
                return True
        """
        self.assertTrue(_reads_the_turn_counter(bot_restraint))
        self.assertFalse(_reads_the_turn_counter(engine_rule))


class TestTrainApplication(unittest.TestCase):
    """TRAIN is implemented and conformance-tested against
    `rust/src/game/engine.rs::apply_train` -- legality, bill, spawn stats,
    spawn cell, occupied-shack handling, turn timing.  Mirror EXACTLY what
    apply_train enforces and NOTHING it does not."""

    def test_legal_train_spawns_a_second_worker_and_charges_the_bill(self):
        ref = train_referee(inventory=[3, 3, 2, 7, 0, 4])
        self.assertTrue(ref.apply("TRAIN 1 1 0 1") is None)
        own = ref.own_unit_ids()
        self.assertEqual(len(own), 2, "a legal TRAIN spawns a second worker")
        nid = own[-1]
        self.assertEqual(nid, 6, "spawn id = max(existing id) + 1")
        new = ref.units[nid]
        self.assertEqual(new["cell"], ref.tent, "spawn cell is the own shack")
        self.assertEqual((new["speed"], new["cap"], new["harvest"],
                          new["chop"]), (1, 1, 0, 1),
                         "spawn stats are the TRAIN talents")
        self.assertEqual(new["carry"], [0] * 6)
        self.assertEqual(new["player"], 0)
        # bill: n=1, talents (1,1,0,1) -> PLUM 2, LEMON 2, APPLE 1; no iron
        # on the map so IRON is not charged.
        self.assertEqual(ref.inv, [1, 1, 1, 7, 0, 4])

    def test_a_third_worker_trains_because_the_engine_has_no_worker_cap(self):
        """THE BLOCKER.  `engine.rs::apply_train` counts own units only to
        price the bill --

            engine.rs:527  let n = game.units.iter()
                               .filter(|u| u.player == player).count() as i32;
            engine.rs:528  let cost = training_cost(n, talents);

        -- and never compares `n` to anything.  An `n >= 2` TRAIN that is
        affordable with an available shack MUST succeed."""
        ref = train_referee(inventory=[99, 99, 99, 0, 99, 0])
        ref.apply("TRAIN 1 1 0 1")
        own = ref.own_unit_ids()
        self.assertEqual(len(own), 2)
        # Vacate the shack, so the occupied-shack guard (engine.rs:545-547) is
        # not what decides the third worker.
        nid = own[-1]
        # (1,0) is held by unit 0 and engine.rs::apply_moves (289) refuses an
        # occupied cell, so the fresh worker leaves via the other door.
        ref.apply("MOVE %d 0 1" % nid)
        self.assertNotEqual(ref.units[nid]["cell"], ref.tent)
        self.assertFalse(any(u["cell"] == ref.tent
                             for u in ref.units.values()))
        before = list(ref.inv)
        self.assertIsNone(ref.can_train((1, 1, 0, 1)),
                        "n == 2 with an affordable bill and a free shack is "
                        "legal under engine.rs::apply_train")
        ref.apply("TRAIN 1 1 0 1")
        self.assertEqual(len(ref.own_unit_ids()), 3,
                         "engine.rs::apply_train imposes NO worker cap: the "
                         "third worker must spawn (yamo_orchard_live.rs:836 "
                         "`n >= 2` is the BOT's self-restraint, not a rule)")
        # bill at n == 2, talents (1,1,0,1): PLUM 3, LEMON 3, APPLE 2; no
        # iron terrain on TRAIN_ROWS so the IRON leg is not charged
        # (engine.rs:532-536).
        self.assertEqual(ref.inv, [before[0] - 3, before[1] - 3,
                                   before[2] - 2, before[3], before[4],
                                   before[5]],
                         "the third worker's bill is priced at n == 2")
        newest = ref.own_unit_ids()[-1]
        self.assertEqual(ref.units[newest]["cell"], ref.tent)

    def test_the_worker_count_only_prices_the_bill(self):
        """`n` grows without bound; the bill grows with it (engine.rs:517-520
        `cost[PLUM] = n + ms * ms`), which is the only thing that ever stops
        a bot from training."""
        # The talents must include ms >= 1: the r2 mirror let a speed-0
        # worker step off the non-walkable shack, which engine.rs::next_cell
        # (126-134) cannot do, so `TRAIN 0 0 0 0` would wedge the shack
        # forever.  ms = 1 costs one extra PLUM (engine.rs:517).
        ref = train_referee(rows=TRAINER_ROWS,
                            inventory=[99, 99, 99, 0, 99, 0],
                            units=[[0, 0, 5, 4, 1, 2, 1, 1] + [0] * 6,
                                   [5, 1, 10, 0, 1, 2, 0, 0] + [0] * 6])
        for expected_n in (1, 2, 3, 4):
            before = list(ref.inv)
            nid_before = set(ref.own_unit_ids())
            ref.apply("TRAIN 1 0 0 0")
            new = set(ref.own_unit_ids()) - nid_before
            self.assertEqual(len(new), 1,
                             "TRAIN #%d must spawn" % expected_n)
            nid = new.pop()
            # cost[PLUM] = n + 1, cost[LEMON] = cost[APPLE] = n
            self.assertEqual(ref.inv[:3],
                             [before[0] - expected_n - 1,
                              before[1] - expected_n,
                              before[2] - expected_n])
            # walk the fresh worker off the shack and out of the way
            for _ in range(6):
                ref.apply("MOVE %d %d 4" % (nid, expected_n))
            self.assertNotEqual(ref.units[nid]["cell"], ref.tent)
        self.assertEqual(len(ref.own_unit_ids()), 5)

    def test_unaffordable_train_is_rejected_and_charges_nothing(self):
        ref = train_referee(inventory=[2, 2, 0, 0, 0, 0])   # APPLE short by 1
        ref.apply("TRAIN 1 1 0 1")
        self.assertEqual(len(ref.own_unit_ids()), 1)
        self.assertEqual(ref.inv, [2, 2, 0, 0, 0, 0])
        ref.inv[2] = 1
        ref.apply("TRAIN 1 1 0 1")
        self.assertEqual(len(ref.own_unit_ids()), 2,
                         "exactly-affordable is affordable (>=, not >)")

    def test_iron_is_billed_only_when_the_map_has_iron(self):
        # No iron on the map: the IRON leg of the bill is not required and
        # not charged (yamo:840 pay_iron).
        ref = train_referee(inventory=[9, 9, 9, 0, 0, 0])
        ref.apply("TRAIN 1 1 0 3")           # IRON leg would be 1 + 9 = 10
        self.assertEqual(len(ref.own_unit_ids()), 2)
        self.assertEqual(ref.inv[4], 0)
        # Iron on the map: the IRON leg is required and charged.
        ref = train_referee(rows=IRON_ROWS, inventory=[9, 9, 9, 0, 9, 0])
        ref.apply("TRAIN 1 1 0 3")
        self.assertEqual(len(ref.own_unit_ids()), 1,
                         "iron present -> the IRON leg must be paid")
        ref = train_referee(rows=IRON_ROWS, inventory=[9, 9, 9, 0, 10, 0])
        ref.apply("TRAIN 1 1 0 3")
        self.assertEqual(len(ref.own_unit_ids()), 2)
        self.assertEqual(ref.inv[4], 0)

    def test_no_final_turn_guard_the_engine_imposes_none(self):
        """`engine.rs::apply_train` (525-568) never reads `game.turn`; the
        turn counter is touched only by `step` itself (engine.rs:805
        `game.turn += 1`).  A TRAIN inside the final 20 turns -- and on the
        very last turn -- must succeed if it is affordable with a free
        shack.  `yamo_orchard_live.rs:836` `TOTAL_TURNS - view.turn <= 20` is
        the BOT's self-restraint."""
        for turn in (279, 280, 290, 299, 300, 400):
            ref = train_referee(inventory=[9, 9, 9, 0, 9, 0])
            ref.turn = turn
            ref.apply("TRAIN 1 1 0 1")
            self.assertEqual(
                len(ref.own_unit_ids()), 2,
                "turn %d: engine.rs::apply_train has no turn condition"
                % turn)

    def test_referee_turn_counter_advances_one_per_applied_command_line(self):
        ref = train_referee()
        self.assertEqual(ref.turn, 1)
        ref.apply("WAIT")
        ref.apply("WAIT")
        self.assertEqual(ref.turn, 3)

    def test_occupied_shack_blocks_the_spawn(self):
        # engine.rs:544-547
        #   let shack = game.shacks[p];
        #   if game.units.iter().any(|u| u.pos() == shack) { return; }
        units = [[0, 0, 0, 0, 1, 2, 1, 1] + [0] * 6,     # standing ON the tent
                 [5, 1, 4, 2, 1, 2, 0, 0] + [0] * 6]
        ref = train_referee(inventory=[9, 9, 9, 0, 9, 0], units=units)
        ref.apply("TRAIN 1 1 0 1")
        self.assertEqual(len(ref.own_unit_ids()), 1,
                         "the spawn cell must be free")
        self.assertEqual(ref.inv, [9, 9, 9, 0, 9, 0])

    def test_an_opponent_unit_on_the_own_shack_blocks_the_spawn(self):
        """engine.rs:545 iterates `game.units` -- ALL units, both players --
        not just the training player's.  An opponent standing on my shack
        blocks my spawn."""
        units = [[0, 0, 1, 0, 1, 2, 1, 1] + [0] * 6,
                 [5, 1, 0, 0, 1, 2, 0, 0] + [0] * 6]   # opponent ON own tent
        ref = train_referee(inventory=[9, 9, 9, 0, 9, 0], units=units)
        self.assertEqual(ref.units[5]["cell"], ref.tent)
        ref.apply("TRAIN 1 1 0 1")
        self.assertEqual(len(ref.own_unit_ids()), 1,
                         "any unit on the shack blocks the spawn "
                         "(engine.rs:545)")
        self.assertEqual(ref.inv, [9, 9, 9, 0, 9, 0],
                         "a rejected TRAIN charges nothing (engine.rs:546 "
                         "returns before the deduction at 550-552)")

    def test_two_trains_on_one_line_the_second_hits_the_fresh_spawn(self):
        """engine.rs:786-788 applies EVERY parsed TRAIN of a player in turn
        (`for talents in &a.train { apply_train(game, 0, *talents) }`), and
        the parser pushes them all (engine.rs:697-706 `continue`s before the
        per-unit `used` bookkeeping).  The second call then finds the shack
        occupied by the unit the first call just spawned."""
        ref = train_referee(inventory=[99, 99, 99, 0, 99, 0])
        before = list(ref.inv)
        ref.apply("TRAIN 1 1 0 1;TRAIN 1 1 0 1")
        self.assertEqual(len(ref.own_unit_ids()), 2,
                         "exactly one spawn: the second TRAIN finds the "
                         "shack occupied by the first spawn")
        self.assertEqual(ref.inv, [before[0] - 2, before[1] - 2,
                                   before[2] - 1, before[3], before[4],
                                   before[5]],
                         "only one bill is charged")

    def test_spawn_id_follows_the_engine_next_id_counter(self):
        """engine.rs:555/567  `let nid = game.next_id; ... game.next_id += 1;`
        -- a monotone counter, never reused (engine.rs contains no unit
        removal at all)."""
        ref = train_referee(inventory=[99, 99, 99, 0, 99, 0])
        ref.apply("TRAIN 1 1 0 1")
        first = ref.own_unit_ids()[-1]
        self.assertEqual(first, 6, "max(existing id 0, 5) + 1")
        ref.apply("MOVE %d 0 1" % first)
        ref.apply("TRAIN 1 1 0 1")
        self.assertEqual(ref.own_unit_ids()[-1], 7,
                         "the counter advances; ids are never reused")

    def test_banana_and_wood_are_on_the_pay_slice_but_cost_nothing(self):
        """engine.rs:532-536 pays over `[0,1,2,3,4,5]` (iron present) or
        `[0,1,2,3,5]` (no iron) -- BANANA (3) and WOOD (5) are always on the
        slice, but `training_cost` never writes them (engine.rs:517-520), so
        the check `inv[i] < cost[i]` is `inv[i] < 0` and the deduction is
        `-= 0`.  A zero BANANA/WOOD inventory must not block a TRAIN and must
        not be reduced by one."""
        ref = train_referee(inventory=[9, 9, 9, 0, 0, 0])
        ref.apply("TRAIN 1 1 0 1")
        self.assertEqual(len(ref.own_unit_ids()), 2)
        self.assertEqual((ref.inv[3], ref.inv[5]), (0, 0))

    def test_turn_timing_train_resolves_after_moves_before_drops(self):
        # engine step order ... MOVE, HARVEST, PLANT, CHOP, PICK, TRAIN,
        # DROP, MINE: the same-turn MOVE that vacates the shack (the
        # yamo clear_cell manoeuvre) must be seen by TRAIN.
        units = [[0, 0, 0, 0, 1, 2, 1, 1] + [0] * 6,
                 [5, 1, 4, 2, 1, 2, 0, 0] + [0] * 6]
        ref = train_referee(inventory=[9, 9, 9, 0, 9, 0], units=units)
        ref.apply("TRAIN 1 1 0 1;MOVE 0 1 0")
        self.assertEqual(ref.units[0]["cell"], (1, 0))
        self.assertEqual(len(ref.own_unit_ids()), 2,
                         "TRAIN is applied after the same-turn MOVE")
        # ... and before DROP: the DROP banks only the mover's cargo, and
        # the spawned worker (empty, on the shack) is unaffected.
        # engine.rs:717-720 gives a unit ONE non-TRAIN command per turn, so
        # the banking unit must not be the mover.
        ref = train_referee(inventory=[9, 9, 9, 0, 9, 0],
                            units=[[0, 0, 0, 0, 1, 2, 1, 1,
                                    0, 0, 0, 0, 0, 1],
                                   [1, 0, 0, 1, 1, 2, 1, 1,
                                    0, 0, 0, 0, 0, 1],
                                   [5, 1, 4, 2, 1, 2, 0, 0] + [0] * 6])
        ref.apply("TRAIN 1 1 0 1;MOVE 0 1 0;DROP 1")
        self.assertEqual(ref.units[1]["carry"], [0] * 6,
                         "DROP runs after TRAIN, but it still runs")
        self.assertEqual(ref.units[0]["carry"][5], 1,
                         "unit 0 spent its single command on MOVE")
        self.assertEqual(len(ref.own_unit_ids()), 3)

    def test_a_spawned_worker_can_leave_the_shack(self):
        # The shack is not a walkable cell, so the mover must mirror the
        # engine's next_cell, which seeds its BFS at the unit's own cell
        # regardless of walkability.  Without this a TRAINed worker is
        # frozen on the shack for the rest of the game.
        ref = train_referee(inventory=[9, 9, 9, 0, 9, 0])
        ref.apply("TRAIN 1 1 0 1")
        nid = ref.own_unit_ids()[-1]
        self.assertEqual(ref.units[nid]["cell"], ref.tent)
        ref.apply("MOVE %d 0 1" % nid)
        self.assertNotEqual(ref.units[nid]["cell"], ref.tent,
                            "a spawned worker must be able to walk off the "
                            "shack")

    def test_malformed_train_is_a_retained_error_not_a_silent_no_op(self):
        # SUPERSEDED IN r3.  The r2 version of this test ratified the exact
        # behaviour contract clause C3 forbids ("silently ignored"); see
        # TestMalformedCommandsAreRetainedErrors for the full matrix.
        ref = train_referee(inventory=[9, 9, 9, 0, 9, 0])
        ref.apply("TRAIN 1 1")
        self.assertEqual(len(ref.own_unit_ids()), 1)
        self.assertEqual(ref.inv, [9, 9, 9, 0, 9, 0])
        self.assertEqual(ref.execution_status, fp.ERROR_MALFORMED)
        self.assertEqual(ref.command_errors[0]["raw"], "TRAIN 1 1")

    def test_train_is_visible_in_the_serialized_state(self):
        ref = train_referee(inventory=[9, 9, 9, 0, 9, 0])
        ref.apply("TRAIN 2 2 0 1")     # bill 5/5/1, affordable from 9/9/9
        state = fp.post_ct_state(ref)
        own = state.own_units()
        self.assertEqual(len(own), 2)
        spawned = [u for u in own if u.cell == ref.tent]
        self.assertEqual(len(spawned), 1)


class TestMineApplication(unittest.TestCase):
    """MINE was silently discarded by exactly the same defect (the referee
    implemented no handler and the dispatcher had no default branch to
    complain).  The exhaustive dispatcher forces it to be implemented."""

    def test_mine_yields_iron_when_orthogonally_adjacent(self):
        # unit at (2,0) is orthogonally adjacent to the iron cell (3,0)
        units = [[0, 0, 2, 0, 1, 2, 1, 1] + [0] * 6,
                 [5, 1, 4, 2, 1, 2, 0, 0] + [0] * 6]
        ref = train_referee(rows=IRON_ROWS, units=units)
        ref.apply("MINE 0")
        self.assertEqual(ref.units[0]["carry"][4], 1,
                         "min(chop=1, free=2) iron mined")

    def test_mine_is_a_no_op_without_adjacency_chop_or_capacity(self):
        far = [[0, 0, 1, 2, 1, 2, 1, 1] + [0] * 6,
               [5, 1, 4, 2, 1, 2, 0, 0] + [0] * 6]
        ref = train_referee(rows=IRON_ROWS, units=far)
        ref.apply("MINE 0")
        self.assertEqual(ref.units[0]["carry"][4], 0)
        nochop = [[0, 0, 2, 0, 1, 2, 1, 0] + [0] * 6,
                  [5, 1, 4, 2, 1, 2, 0, 0] + [0] * 6]
        ref = train_referee(rows=IRON_ROWS, units=nochop)
        ref.apply("MINE 0")
        self.assertEqual(ref.units[0]["carry"][4], 0)
        full = [[0, 0, 2, 0, 1, 2, 1, 1, 0, 0, 0, 0, 0, 2],
                [5, 1, 4, 2, 1, 2, 0, 0] + [0] * 6]
        ref = train_referee(rows=IRON_ROWS, units=full)
        ref.apply("MINE 0")
        self.assertEqual(ref.units[0]["carry"][4], 0)

    def test_mine_is_capped_by_free_capacity(self):
        units = [[0, 0, 2, 0, 1, 2, 1, 3, 0, 0, 0, 0, 0, 1],
                 [5, 1, 4, 2, 1, 2, 0, 0] + [0] * 6]
        ref = train_referee(rows=IRON_ROWS, units=units)
        ref.apply("MINE 0")
        self.assertEqual(ref.units[0]["carry"][4], 1,
                         "min(chop=3, free=1)")


class TestCorpusVersion(unittest.TestCase):
    """Requirement 5: implementing TRAIN changes the referee and therefore
    the floor, so the corpus/instrument version is bumped in the config and
    echoed in every report."""

    def test_committed_config_declares_the_bumped_version(self):
        cfg = json.loads((HERE / "fuzz-panel-config.json").read_text())
        self.assertIn("corpus_version", cfg)
        self.assertIn("instrument_version", cfg)
        self.assertEqual(cfg["corpus_version"], fp.CORPUS_VERSION)
        self.assertEqual(cfg["instrument_version"], fp.INSTRUMENT_VERSION)
        self.assertGreaterEqual(int(str(cfg["corpus_version"]).lstrip("c")
                                    .split("-")[0]), 2)

    def test_every_report_echoes_the_versions_and_the_referee_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "r.md"
            cfg = dict(fp.DEFAULTS)
            cfg.update({"task": "t", "seeds": [1],
                        "instrument_version": fp.INSTRUMENT_VERSION,
                        "corpus_version": fp.CORPUS_VERSION,
                        "candidate": {"source": "c.rs"},
                        "parent": {"source": "p.rs"}})
            fp.write_report(out, cfg, [], fp.summarize(cfg, [], 0.0), "CLEAR")
            text = out.read_text()
            self.assertIn(fp.CORPUS_VERSION, text)
            self.assertIn(fp.INSTRUMENT_VERSION, text)
            self.assertIn(fp.referee_sha256(), text)


# ---------------------------------------------------------------------------
# Requirement 4: the two m040 identities are MANDATORY REGRESSION ROWS.
#
# Measured on the pre-repair floor (corpus c1, instrument fuzz-panel/1):
# m040 seat 0 and seat 1 (class forest_dense, opponent harvester, one own
# worker) emitted TRAIN on 166 and 182 of 200 turns respectively -- every
# turn from t=35 and t=19 to the sim horizon -- because the referee silently
# discarded TRAIN, so the own worker count never rose and can_train stayed
# true forever.  Both games nevertheless scored CLEAN (D-1..D-9 all zero,
# block=False), so the panel's two most pathological games were among its
# best.  These rows must never be removed.
# ---------------------------------------------------------------------------

class TestM040RegressionRows(unittest.TestCase):
    MAP_INDEX = 40

    @classmethod
    def specs(cls):
        cfg = fp.load_config(HERE / "fuzz-panel-config.json")
        classes = fp.schedule(cfg["class_mix"], int(cfg["maps"]))
        profiles = fp.schedule(cfg["opponent_mix"], int(cfg["maps"]))
        skel, specs = fp.build_skeleton(
            cls.MAP_INDEX, classes[cls.MAP_INDEX], profiles[cls.MAP_INDEX],
            cfg)
        return cfg, skel, specs

    def test_m040_identity_is_pinned(self):
        cfg, skel, specs = self.specs()
        self.assertEqual(skel["id"], "m040")
        self.assertEqual(skel["class"], "forest_dense")
        self.assertEqual(skel["profile"], "harvester")
        self.assertIsNone(skel["roster"]["second"],
                          "both m040 seats are one-worker games")
        for spec in specs:
            self.assertEqual(
                len([u for u in spec["units"] if u[1] == 0]), 1)

    def _run_seat(self, seat):
        cfg, _, specs = self.specs()
        binary = compiled_binary("floorbot", FLOOR_BOT_SOURCE)
        ref = fp.make_referee(specs[seat])
        _, commands = rt.run_binary_custom(binary, ref, int(cfg["turns"]))
        trains = [i + 1 for i, line in enumerate(commands.splitlines())
                  if any(c.strip().upper().startswith("TRAIN")
                         for c in line.split(";"))]
        return ref, commands, trains

    def _assert_row_repaired(self, seat):
        ref, commands, trains = self._run_seat(seat)
        n_turns = len(commands.splitlines())
        self.assertGreaterEqual(n_turns, 200)
        self.assertTrue(trains, "m040 seat %d must still attempt TRAIN "
                                "(the row would be vacuous otherwise)" % seat)
        self.assertEqual(
            len(trains), 1,
            "m040 seat %d: TRAIN must be emitted once and then stop -- it "
            "was re-emitted on %d of %d turns before the repair"
            % (seat, len(trains), n_turns))
        own = [u for u in ref.units.values() if u["player"] == 0]
        self.assertEqual(len(own), 2,
                         "m040 seat %d: the TRAIN must actually spawn the "
                         "second worker" % seat)

    def test_m040_seat_0_no_longer_re_emits_train_every_turn(self):
        self._assert_row_repaired(0)

    def test_m040_seat_1_no_longer_re_emits_train_every_turn(self):
        self._assert_row_repaired(1)


# ===========================================================================
# REVISION r3 (2026-08-10) -- the frozen acceptance contract
# `chatgpt_1/referee-train-acceptance-contract-2026-08-09.md`, as reviewed by
# `chatgpt_1/referee-train-repair-r2-review-2026-08-10.md`.
#
# Every rule asserted below cites the `rust/src/game/engine.rs` line it
# mirrors.  Where the contract deliberately DIVERGES from engine.rs (the
# trust boundary, contract C3) the divergence is named in the test docstring
# so it can never be mistaken for conformance.
# ===========================================================================

REPO_ROOT = HERE.parent.parent
ENGINE_RS = REPO_ROOT / "rust" / "src" / "game" / "engine.rs"
STATE_RS = REPO_ROOT / "rust" / "src" / "game" / "state.rs"


# --- blocker 5: independent full-state differential oracles ----------------
#
# CIRCULARITY IS THE THING TO AVOID.  r1 copied one bot's `can_train` guard
# into referee law and every hand-written test agreed with it, because the
# tests and the implementation shared an author and a mental model.  An
# oracle built from `fuzz_panel` helpers would reproduce that failure exactly.
#
# Leg A (primary) is therefore not a mirror of the authority at all: it IS the
# authority.  `rust/src/game/engine.rs` and `rust/src/game/state.rs` are
# pulled BYTE-FOR-BYTE into a throwaway crate with `#[path]` (no copy, no
# edit, no transcription) and `engine::step` is executed on the same state and
# the same command line.  Nothing of `fuzz_panel` is on that side of the
# comparison.
#
# Leg B is `sim/engine.py` -- a pre-existing, independently authored Python
# mirror of the same authority, imported read-only.  It is a second opinion,
# not the primary; two mirrors can agree on the same accidental error, which
# is why the contract (§1) also requires hand-written expected values.  Those
# are the `TestTrainApplication` / `TestPhaseOrder` / `TestParser` cases.

RUST_ORACLE_SRC = r'''
#[path = "__STATE_RS__"]
mod state;
#[path = "__ENGINE_RS__"]
mod engine;

use std::io::Read;

fn nums(rest: &str) -> Vec<i32> {
    rest.split_whitespace().map(|s| s.parse().unwrap()).collect()
}

fn main() {
    let mut buf = String::new();
    std::io::stdin().read_to_string(&mut buf).unwrap();
    let mut rows: Vec<String> = Vec::new();
    let mut inv = [[0i32; 6]; 2];
    let mut units: Vec<state::Unit> = Vec::new();
    let mut plants: Vec<state::Plant> = Vec::new();
    let mut next_id = 0i32;
    let mut turn = 1i32;
    let mut c0: Vec<String> = Vec::new();
    let mut c1: Vec<String> = Vec::new();
    for line in buf.lines() {
        if line.is_empty() { continue; }
        let mut it = line.splitn(2, ' ');
        let tag = it.next().unwrap();
        let rest = it.next().unwrap_or("");
        match tag {
            "ROW" => rows.push(rest.to_string()),
            "INV0" => { let v = nums(rest); inv[0].copy_from_slice(&v[..6]); }
            "INV1" => { let v = nums(rest); inv[1].copy_from_slice(&v[..6]); }
            "NEXTID" => next_id = rest.trim().parse().unwrap(),
            "TURN" => turn = rest.trim().parse().unwrap(),
            "UNIT" => {
                let v = nums(rest);
                units.push(state::Unit {
                    id: v[0], player: v[1], x: v[2], y: v[3],
                    ms: v[4], cc: v[5], hp: v[6], chop: v[7],
                    carry: [v[8], v[9], v[10], v[11], v[12], v[13]],
                });
            }
            "PLANT" => {
                let f: Vec<&str> = rest.split_whitespace().collect();
                plants.push(state::Plant {
                    plant_type: f[0].to_string(),
                    x: f[1].parse().unwrap(), y: f[2].parse().unwrap(),
                    size: f[3].parse().unwrap(), health: f[4].parse().unwrap(),
                    fruits: f[5].parse().unwrap(),
                    cooldown: f[6].parse().unwrap(),
                });
            }
            "CMD0" => c0.push(rest.to_string()),
            "CMD1" => c1.push(rest.to_string()),
            other => panic!("unknown spec tag {:?}", other),
        }
    }
    let refs: Vec<&str> = rows.iter().map(|s| s.as_str()).collect();
    let mut g = state::from_ascii(&refs);
    g.inventories = inv;
    g.units = units;
    g.plants = plants;
    g.next_id = next_id;
    g.turn = turn;
    engine::step(&mut g, &c0, &c1);
    let j = |v: &[i32]| v.iter().map(|x| x.to_string())
        .collect::<Vec<_>>().join(" ");
    println!("INV0 {}", j(&g.inventories[0]));
    println!("INV1 {}", j(&g.inventories[1]));
    println!("SCORE {} {}", g.scores[0], g.scores[1]);
    println!("TURN {}", g.turn);
    println!("NEXTID {}", g.next_id);
    let mut us = g.units.clone();
    us.sort_by_key(|u| u.id);
    for u in &us {
        println!("UNIT {} {} {} {} {} {} {} {} {}", u.id, u.player, u.x, u.y,
                 u.ms, u.cc, u.hp, u.chop, j(&u.carry));
    }
    let mut ps = g.plants.clone();
    ps.sort_by_key(|p| (p.x, p.y));
    for p in &ps {
        println!("PLANT {} {} {} {} {} {} {}", p.plant_type, p.x, p.y,
                 p.size, p.health, p.fruits, p.cooldown);
    }
}
'''

_RUST_ORACLE_BIN = []


def rust_oracle_binary() -> Path:
    """Compile the throwaway crate that `#[path]`-includes the authoritative
    engine.rs / state.rs verbatim.  Deliberately NOT skipped when rustc is
    missing: a silently-absent oracle is the exact failure mode this
    programme keeps rediscovering."""
    if _RUST_ORACLE_BIN:
        return _RUST_ORACLE_BIN[0]
    import os
    import shutil
    import subprocess
    for p in (ENGINE_RS, STATE_RS):
        if not p.exists():
            raise AssertionError("differential oracle needs %s" % p)
    env = dict(os.environ)
    env["PATH"] = str(Path.home() / ".cargo" / "bin") + os.pathsep + env.get(
        "PATH", "")
    rustc = shutil.which("rustc", path=env["PATH"])
    if rustc is None:
        raise AssertionError(
            "the differential oracle requires rustc (the authority is "
            "rust/src/game/engine.rs); refusing to skip the only "
            "non-circular check in the suite")
    out_dir = Path(tempfile.mkdtemp(prefix="fuzz-oracle-"))
    src = out_dir / "oracle.rs"
    src.write_text(RUST_ORACLE_SRC
                   .replace("__STATE_RS__", str(STATE_RS))
                   .replace("__ENGINE_RS__", str(ENGINE_RS)))
    binary = out_dir / "oracle"
    proc = subprocess.run(
        [rustc, "--edition", "2021", "-A", "warnings", "-O",
         str(src), "-o", str(binary)],
        capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        raise AssertionError("oracle build failed:\n%s" % proc.stderr[-4000:])
    _RUST_ORACLE_BIN.append(binary)
    return binary


class Case:
    """One (state, command line) pair, in the panel's own spec vocabulary."""

    def __init__(self, name, rows, inventory, units, plants=(), line="",
                 next_id=None, opp_inventory=(0, 0, 0, 0, 0, 0), line1=""):
        self.name = name
        self.rows = list(rows)
        self.inventory = list(inventory)
        self.opp_inventory = list(opp_inventory)
        self.units = [list(u) for u in units]
        self.plants = [list(p) for p in plants]
        self.line = line
        # r4 / review B2: the OPPONENT's command line for the same turn.
        # `engine.rs::step` takes two streams and merges them phase by phase;
        # a panel that drives player 1 with a direct post-phase simulator is
        # producing a world transition `step` cannot produce.
        self.line1 = line1
        self.next_id = (max(u[0] for u in units) + 1 if next_id is None
                        else next_id)

    def spec(self, profile="idle"):
        return {"rows": self.rows, "inventory": list(self.inventory),
                "opp_inventory": list(self.opp_inventory),
                "plants": [list(p) for p in self.plants],
                "units": [list(u) for u in self.units], "profile": profile}

    def fragments(self):
        return [f.strip() for f in self.line.split(";") if f.strip()]

    def fragments1(self):
        return [f.strip() for f in self.line1.split(";") if f.strip()]


def snapshot_from_referee(ref) -> dict:
    return {
        "inv0": list(ref.inv),
        "inv1": list(ref.opp_inv),
        "score": [fp.score(ref.inv), fp.score(ref.opp_inv)],
        "turn": ref.turn,
        "next_id": ref.next_id,
        "units": sorted(
            [uid, u["player"], u["cell"][0], u["cell"][1], u["speed"],
             u["cap"], u["harvest"], u["chop"]] + list(u["carry"])
            for uid, u in ref.units.items()),
        "plants": sorted(
            ([p["kind"], c[0], c[1], p["size"], p["health"], p["fruits"],
              p["cd"]] for c, p in ref.plants.items()),
            key=lambda r: (r[1], r[2])),
    }


def snapshot_from_rust(case: Case) -> dict:
    """Leg A: run the AUTHORITY's own bytes."""
    import subprocess
    lines = ["ROW " + r for r in case.rows]
    lines.append("INV0 " + " ".join(str(v) for v in case.inventory))
    lines.append("INV1 " + " ".join(str(v) for v in case.opp_inventory))
    lines.append("NEXTID %d" % case.next_id)
    lines.append("TURN 1")
    for u in case.units:
        lines.append("UNIT " + " ".join(str(v) for v in u))
    for p in case.plants:
        lines.append("PLANT " + " ".join(str(v) for v in p))
    for frag in case.fragments():
        lines.append("CMD0 " + frag)
    for frag in case.fragments1():
        lines.append("CMD1 " + frag)
    proc = subprocess.run([str(rust_oracle_binary())], input="\n".join(lines),
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise AssertionError("rust oracle failed on %s: %s"
                             % (case.name, proc.stderr[-2000:]))
    out = {"units": [], "plants": []}
    for line in proc.stdout.splitlines():
        tag, _, rest = line.partition(" ")
        if tag == "INV0":
            out["inv0"] = [int(v) for v in rest.split()]
        elif tag == "INV1":
            out["inv1"] = [int(v) for v in rest.split()]
        elif tag == "SCORE":
            out["score"] = [int(v) for v in rest.split()]
        elif tag == "TURN":
            out["turn"] = int(rest)
        elif tag == "NEXTID":
            out["next_id"] = int(rest)
        elif tag == "UNIT":
            out["units"].append([int(v) for v in rest.split()])
        elif tag == "PLANT":
            f = rest.split()
            out["plants"].append([f[0]] + [int(v) for v in f[1:]])
    out["units"].sort()
    out["plants"].sort(key=lambda r: (r[1], r[2]))
    return out


def snapshot_from_sim(case: Case) -> dict:
    """Leg B: the pre-existing, independently authored `sim/engine.py`."""
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from sim import engine as sim_engine
    from sim.state import GameState, SimPlant, SimUnit
    geo = sh.parse_rows(tuple(case.rows))
    game = GameState(
        width=len(case.rows[0]), height=len(case.rows),
        walkable=set(geo["walkable"]),
        shacks=[geo["shacks"][0], geo["shacks"][1]],
        inventories=[list(case.inventory), list(case.opp_inventory)],
        units=[SimUnit(u[0], u[1], u[2], u[3], u[4], u[5], u[6], u[7],
                       list(u[8:14])) for u in case.units],
        plants=[SimPlant(p[0], p[1], p[2], p[3], p[4], p[5], p[6])
                for p in case.plants],
        scores=[0, 0], turn=1, next_id=case.next_id,
        iron=set(geo["iron"]), water=set(geo["water"]))
    sim_engine.step(game, case.fragments(), case.fragments1())
    return {
        "inv0": list(game.inventories[0]), "inv1": list(game.inventories[1]),
        "score": list(game.scores), "turn": game.turn,
        "next_id": game.next_id,
        "units": sorted([u.id, u.player, u.x, u.y, u.ms, u.cc, u.hp, u.chop]
                        + list(u.carry) for u in game.units),
        "plants": sorted(([p.type, p.x, p.y, p.size, p.health, p.fruits,
                           p.cooldown] for p in game.plants),
                         key=lambda r: (r[1], r[2])),
    }


# Geometry used by the differential matrix.  '0'/'1' are the two shacks (NOT
# walkable, engine.rs state.rs from_ascii), '+' is iron terrain, '#' wall.
D_ROWS = ("#########",
          "#0.....1#",
          "#.......#",
          "#########")
D_IRON = ("#########",
          "#0..+..1#",
          "#.......#",
          "#########")
RICH = [40, 40, 40, 40, 40, 40]


def _u(uid, player, x, y, speed=1, cap=4, harvest=1, chop=1, carry=()):
    return [uid, player, x, y, speed, cap, harvest, chop] + (
        list(carry) + [0] * 6)[:6]


DIFFERENTIAL_CASES = [
    # --- TRAIN, contract §3 ------------------------------------------------
    Case("train_success_iron", D_IRON, RICH,
         [_u(0, 0, 2, 1), _u(9, 1, 7, 1)], line="TRAIN 2 3 1 4"),
    Case("train_success_no_iron", D_ROWS, RICH,
         [_u(0, 0, 2, 1), _u(9, 1, 7, 1)], line="TRAIN 2 3 1 4"),
    Case("train_unaffordable", D_IRON, [1, 1, 1, 1, 1, 1],
         [_u(0, 0, 2, 1), _u(9, 1, 7, 1)], line="TRAIN 2 3 1 4"),
    Case("train_shack_occupied_by_own", D_IRON, RICH,
         [_u(0, 0, 1, 1), _u(9, 1, 7, 1)], line="TRAIN 1 1 1 1"),
    Case("train_shack_occupied_by_opponent", D_IRON, RICH,
         [_u(0, 0, 2, 1), _u(9, 1, 1, 1)], line="TRAIN 1 1 1 1"),
    # --- N3: MOVE resolves first and changes TRAIN legality ---------------
    Case("move_off_shack_enables_train", D_IRON, RICH,
         [_u(0, 0, 1, 1), _u(9, 1, 7, 1)], line="MOVE 0 3 1;TRAIN 1 1 1 1"),
    Case("move_off_shack_enables_train_permuted", D_IRON, RICH,
         [_u(0, 0, 1, 1), _u(9, 1, 7, 1)], line="TRAIN 1 1 1 1;MOVE 0 3 1"),
    Case("move_onto_shack_blocks_train", D_IRON, RICH,
         [_u(0, 0, 2, 1), _u(9, 1, 7, 1)], line="MOVE 0 1 1;TRAIN 1 1 1 1"),
    Case("move_onto_shack_blocks_train_permuted", D_IRON, RICH,
         [_u(0, 0, 2, 1), _u(9, 1, 7, 1)], line="TRAIN 1 1 1 1;MOVE 0 1 1"),
    # --- O1: PICK is visible to TRAIN, DROP is not ------------------------
    Case("pick_before_train_starves_the_bill", D_ROWS, [2, 2, 2, 0, 0, 0],
         [_u(0, 0, 2, 1), _u(9, 1, 7, 1)], line="PICK 0 PLUM;TRAIN 1 1 1 1"),
    Case("no_pick_control_train_succeeds", D_ROWS, [2, 2, 2, 0, 0, 0],
         [_u(0, 0, 2, 1), _u(9, 1, 7, 1)], line="TRAIN 1 1 1 1"),
    Case("drop_written_first_cannot_fund_train", D_ROWS, [1, 1, 1, 0, 0, 0],
         [_u(0, 0, 2, 1, carry=[1, 1, 1, 0, 0, 0]), _u(9, 1, 7, 1)],
         line="DROP 0;TRAIN 1 1 1 1"),
    Case("drop_written_last_cannot_fund_train", D_ROWS, [1, 1, 1, 0, 0, 0],
         [_u(0, 0, 2, 1, carry=[1, 1, 1, 0, 0, 0]), _u(9, 1, 7, 1)],
         line="TRAIN 1 1 1 1;DROP 0"),
    # --- O2: repeated TRAIN is sequential ---------------------------------
    Case("two_trains_second_blocked_by_the_fresh_spawn", D_ROWS, RICH,
         [_u(0, 0, 2, 1), _u(9, 1, 7, 1)],
         line="TRAIN 1 1 1 1;TRAIN 1 1 1 1"),
    Case("first_train_fails_second_succeeds", D_ROWS, [9, 9, 9, 0, 0, 0],
         [_u(0, 0, 2, 1), _u(9, 1, 7, 1)],
         line="TRAIN 9 9 9 9;TRAIN 1 1 1 1"),
    Case("three_trains_costs_use_the_growing_roster", D_ROWS, RICH,
         [_u(0, 0, 2, 1), _u(9, 1, 7, 1)],
         line="TRAIN 1 1 1 1;MOVE 0 3 1;TRAIN 1 1 1 1"),
    # --- O3: future-id visibility ----------------------------------------
    Case("future_id_drop_after_spawn", D_ROWS, RICH,
         [_u(0, 0, 2, 1), _u(9, 1, 7, 1)], line="TRAIN 1 1 1 1;DROP 10"),
    Case("future_id_mine_after_spawn", D_IRON, RICH,
         [_u(0, 0, 2, 1), _u(9, 1, 7, 1)], line="TRAIN 1 1 1 1;MINE 10"),
    # --- C5: first non-TRAIN command per unit -----------------------------
    Case("second_command_for_a_unit_is_discarded", D_ROWS, [5, 0, 0, 0, 0, 0],
         [_u(0, 0, 2, 1), _u(9, 1, 7, 1)], line="MOVE 0 4 1;PICK 0 PLUM"),
    Case("second_command_for_a_unit_is_discarded_reversed", D_ROWS,
         [5, 0, 0, 0, 0, 0], [_u(0, 0, 2, 1), _u(9, 1, 7, 1)],
         line="PICK 0 PLUM;MOVE 0 4 1"),
    Case("duplicate_mine_is_discarded", D_IRON, RICH,
         [_u(0, 0, 3, 1, cap=6), _u(9, 1, 7, 1)], line="MINE 0;MINE 0"),
    # --- C4: phase order for the non-TRAIN verbs --------------------------
    Case("mine_resolves_after_drop", D_IRON, [0] * 6,
         [_u(0, 0, 3, 1, cap=6, carry=[0, 0, 0, 0, 2, 0]), _u(9, 1, 7, 1)],
         line="MINE 0;DROP 0"),
    Case("harvest_then_plant_then_chop", D_ROWS, [0] * 6,
         [_u(0, 0, 3, 1, cap=6, harvest=2, chop=3, carry=[1, 0, 0, 0, 0, 0]),
          _u(9, 1, 7, 1)],
         plants=[["BANANA", 4, 1, 4, 6, 3, 4]],
         line="CHOP 0;MOVE 0 4 1"),
    Case("harvest_multi_round_by_harvest_power", D_ROWS, [0] * 6,
         [_u(0, 0, 4, 1, cap=6, harvest=3), _u(9, 1, 7, 1)],
         plants=[["BANANA", 4, 1, 4, 6, 3, 4]], line="HARVEST 0"),
    Case("plant_creates_a_tree_that_is_not_choppable_this_turn", D_ROWS,
         [0] * 6,
         [_u(0, 0, 4, 1, cap=6, chop=9, carry=[0, 0, 0, 1, 0, 0]),
          _u(9, 1, 7, 1)], line="PLANT 0 BANANA"),
    Case("two_units_plant_the_same_cell", D_ROWS, [0] * 6,
         [_u(0, 0, 4, 1, carry=[0, 0, 0, 1, 0, 0]),
          _u(1, 0, 4, 1, carry=[0, 0, 0, 1, 0, 0]), _u(9, 1, 7, 1)],
         line="PLANT 0 BANANA;PLANT 1 BANANA"),
    # --- movement conformance --------------------------------------------
    Case("move_contention_highest_id_wins", D_ROWS, [0] * 6,
         [_u(0, 0, 2, 1), _u(1, 0, 4, 1), _u(9, 1, 7, 1)],
         line="MOVE 0 3 1;MOVE 1 3 1"),
    Case("zero_speed_unit_on_the_shack_cannot_move", D_ROWS, [0] * 6,
         [_u(0, 0, 1, 1, speed=0), _u(9, 1, 7, 1)], line="MOVE 0 4 1"),
    Case("zero_speed_unit_on_a_walkable_cell_cannot_move", D_ROWS, [0] * 6,
         [_u(0, 0, 3, 1, speed=0), _u(9, 1, 7, 1)], line="MOVE 0 6 1"),
    Case("pick_and_drop_work_from_the_shack_cell_itself", D_ROWS,
         [3, 0, 0, 0, 0, 0],
         [_u(0, 0, 1, 1, carry=[0, 1, 0, 0, 0, 0]), _u(9, 1, 7, 1)],
         line="PICK 0 PLUM"),
    Case("wait_and_msg_are_world_no_ops", D_ROWS, [1] * 6,
         [_u(0, 0, 2, 1), _u(9, 1, 7, 1)], line="MSG hello there;WAIT"),
]

# Leg B (`sim/engine.py`) is DEFECTIVE relative to the authority on these
# cases and is excluded from them.  Found by this differential, reported, not
# fixed here (sim/ is outside this task's boundary):
#
#   sim/engine.py:115  `best = min(target_dist[c] for c in in_range)`
#   has no counterpart to engine.rs:132-134
#       if in_range.is_empty() { return current; }
#   so a speed-0 unit standing on a non-walkable cell (a shack -- exactly
#   where TRAIN puts a fresh worker) raises `ValueError: min() iterable
#   argument is empty` instead of standing still.
SIM_LEG_DEFECTS = ("zero_speed_unit_on_the_shack_cannot_move",)

PERMUTATION_GROUPS = [
    # identical command multisets, different textual order (contract C4)
    ("move_and_train", D_IRON, RICH, [_u(0, 0, 1, 1), _u(9, 1, 7, 1)],
     ["MOVE 0 3 1;TRAIN 2 3 1 4", "TRAIN 2 3 1 4;MOVE 0 3 1"]),
    ("drop_and_train", D_ROWS, [1, 1, 1, 0, 0, 0],
     [_u(0, 0, 2, 1, carry=[1, 1, 1, 0, 0, 0]), _u(9, 1, 7, 1)],
     ["DROP 0;TRAIN 1 1 1 1", "TRAIN 1 1 1 1;DROP 0"]),
    # NOTE: permutation invariance (C4) is bounded by C5 -- engine.rs:717-720
    # makes textual order decide WHICH of two commands for the SAME unit
    # survives, so the multiset must not repeat a unit.
    ("mine_and_drop", D_IRON, [0] * 6,
     [_u(0, 0, 3, 1, cap=6, carry=[0, 0, 0, 0, 1, 0]),
      _u(1, 0, 2, 1, cap=6, carry=[0, 0, 0, 0, 1, 0]), _u(9, 1, 7, 1)],
     ["MINE 0;DROP 1", "DROP 1;MINE 0"]),
    ("pick_and_train", D_ROWS, [2, 2, 2, 0, 0, 0],
     [_u(0, 0, 2, 1), _u(9, 1, 7, 1)],
     ["PICK 0 PLUM;TRAIN 1 1 1 1", "TRAIN 1 1 1 1;PICK 0 PLUM"]),
]


class TestDifferentialFullState(unittest.TestCase):
    """Contract §6 / review B5.  Full post-turn state equality against the
    AUTHORITY ITSELF (engine.rs compiled verbatim) and against the
    independent `sim/engine.py` mirror, over the whole load-bearing
    parser/phase/TRAIN matrix."""

    def _run_referee(self, case):
        ref = fp.make_referee(case.spec())
        ref.apply(case.line)
        ref.grow()
        return ref

    def test_rust_authority_agrees_on_every_case(self):
        for case in DIFFERENTIAL_CASES:
            with self.subTest(case=case.name):
                ref = self._run_referee(case)
                self.assertEqual(snapshot_from_referee(ref),
                                 snapshot_from_rust(case))

    def test_sim_engine_mirror_agrees_on_every_case(self):
        for case in DIFFERENTIAL_CASES:
            if case.name in SIM_LEG_DEFECTS:
                continue
            with self.subTest(case=case.name):
                ref = self._run_referee(case)
                self.assertEqual(snapshot_from_referee(ref),
                                 snapshot_from_sim(case))

    def test_the_two_oracles_agree_with_each_other(self):
        # If leg A and leg B ever disagree, neither may be used as an oracle.
        for case in DIFFERENTIAL_CASES:
            if case.name in SIM_LEG_DEFECTS:
                continue
            with self.subTest(case=case.name):
                self.assertEqual(snapshot_from_rust(case),
                                 snapshot_from_sim(case))

    def test_the_sim_leg_defects_are_real_and_named(self):
        """Leg B is excluded from exactly the cases named in
        `SIM_LEG_DEFECTS`, and the exclusion is not a convenience: each one
        must still FAIL against leg B, for the documented reason.  A silent
        exclusion list is how an oracle stops being an oracle."""
        self.assertTrue(SIM_LEG_DEFECTS)
        by_name = {c.name: c for c in DIFFERENTIAL_CASES}
        for name in SIM_LEG_DEFECTS:
            with self.subTest(case=name):
                self.assertIn(name, by_name)
                with self.assertRaises(ValueError):
                    snapshot_from_sim(by_name[name])
                # leg A -- the authority itself -- handles it correctly.
                ref = self._run_referee(by_name[name])
                self.assertEqual(snapshot_from_referee(ref),
                                 snapshot_from_rust(by_name[name]))

    def test_the_oracle_is_not_vacuous(self):
        # A deliberately wrong post-state must be REJECTED by the oracle, so
        # a green differential run cannot be an artefact of a no-op compare.
        case = DIFFERENTIAL_CASES[0]
        ref = self._run_referee(case)
        broken = snapshot_from_referee(ref)
        broken["inv0"][0] += 1
        self.assertNotEqual(broken, snapshot_from_rust(case))

    def test_permutation_invariance_over_identical_multisets(self):
        for name, rows, inv, units, lines in PERMUTATION_GROUPS:
            snaps = []
            for line in lines:
                case = Case(name, rows, inv, units, line=line)
                snaps.append(snapshot_from_referee(self._run_referee(case)))
            with self.subTest(case=name):
                self.assertEqual(snaps[0], snaps[1],
                                 "textual order changed the post-state: %s"
                                 % name)


# --- blocker 2 / contract C4: the complete engine phase order --------------

class TestPhaseOrder(unittest.TestCase):
    """engine.rs:753-754 (`step` doc) and engine.rs:762-801 (the calls):

        MOVE -> HARVEST -> PLANT -> CHOP -> PICK -> TRAIN -> DROP -> MINE
    """

    def test_phase_order_constant_is_the_engine_order(self):
        self.assertEqual(
            tuple(fp.PHASE_ORDER),
            ("MOVE", "HARVEST", "PLANT", "CHOP", "PICK", "TRAIN", "DROP",
             "MINE"))

    def test_execute_calls_the_phases_in_that_order(self):
        # AST-level: the phase appliers must appear in `_execute` in engine
        # order.  Prose in a docstring cannot satisfy this.
        calls = [a for a in _attrs_in_source_order(
            _body_ast(fp.FuzzReferee._execute))
            if a.startswith(("_apply_", "_train_"))]
        # `_train_one` appears twice: engine.rs:786-791 runs the candidate's
        # TRAIN entries as player 0 and the opponent's as player 1, sharing
        # one `next_id`.  Every other phase takes the MERGED bucket.
        self.assertEqual(
            calls,
            ["_apply_moves", "_apply_harvest", "_apply_plant", "_apply_chop",
             "_apply_pick", "_train_one", "_train_one", "_apply_drop",
             "_apply_mine"])

    def test_drop_never_funds_a_same_turn_train(self):
        ref = train_referee(inventory=[1, 1, 1, 0, 1, 0],
                            units=[[0, 0, 1, 0, 1, 4, 1, 1, 1, 1, 1, 0, 1, 0],
                                   [5, 1, 4, 2, 1, 2, 0, 0] + [0] * 6])
        ref.apply("DROP 0;TRAIN 1 1 1 1")
        self.assertEqual(len(ref.own_unit_ids()), 1,
                         "DROP resolves AFTER TRAIN (engine.rs:786-796)")
        self.assertEqual(ref.inv, [2, 2, 2, 0, 2, 0], "DROP still executed")

    def test_pick_is_visible_to_the_same_turn_train(self):
        # CONTRACT NOTE (O1): the frozen contract says "PICK can fund TRAIN".
        # engine.rs:451-456 makes PICK strictly DECREASE the inventory, so a
        # PICK can only ever starve a bill, never supply it.  What is real,
        # and what this pins, is the PHASE VISIBILITY the clause is about:
        # PICK's inventory write happens before TRAIN reads it.
        base = dict(inventory=[2, 2, 2, 0, 2, 0])
        ok = train_referee(**base)
        ok.apply("TRAIN 1 1 1 1")
        self.assertEqual(len(ok.own_unit_ids()), 2)
        starved = train_referee(**base)
        starved.apply("PICK 0 PLUM;TRAIN 1 1 1 1")
        self.assertEqual(len(starved.own_unit_ids()), 1)

    def test_mine_resolves_after_drop(self):
        # (1,0) is adjacent to BOTH the shack (0,0) and the iron cell (2,0),
        # so one unit can bank and mine in the same turn.  engine.rs:717-720
        # allows a unit only ONE non-TRAIN command per turn, so the DROP and
        # the MINE must come from different units -- both stand on cells
        # adjacent to the shack and the iron.
        rows = ("0.+..1", "......", "......")
        ref = train_referee(
            rows=rows, inventory=[0] * 6,
            units=[[0, 0, 1, 0, 1, 6, 1, 2] + [0, 0, 0, 0, 3, 0],
                   [1, 0, 0, 1, 1, 6, 1, 2] + [0, 0, 0, 0, 4, 0],
                   [5, 1, 4, 2, 1, 2, 0, 0] + [0] * 6])
        ref.apply("MINE 0;DROP 1")
        self.assertEqual(ref.inv[fp.IRON], 4,
                         "DROP banked unit 1's pre-MINE iron")
        self.assertEqual(ref.units[0]["carry"][fp.IRON], 5,
                         "MINE ran and added min(chop=2, free=3) = 2")
        self.assertEqual(ref.units[1]["carry"][fp.IRON], 0,
                         "unit 1 dropped; MINE ran AFTER DROP so a unit that "
                         "only dropped stays empty")


# --- blocker 3 / contract C5: first non-TRAIN command per unit -------------

class TestParserUnitDedup(unittest.TestCase):
    """engine.rs:717-720

        if used.contains(&uid) { continue; }
        used.insert(uid);

    -- the first non-TRAIN command for a unit wins; every later one for the
    same unit is discarded.  TRAIN (engine.rs:697-706) `continue`s before the
    uid is even parsed, so it is not unit-scoped."""

    def test_second_non_train_command_for_a_unit_is_discarded(self):
        parsed = fp.FuzzReferee.parse_commands("MOVE 0 4 1;PICK 0 PLUM")
        self.assertEqual(parsed.moves, {0: (4, 1)})
        self.assertEqual(parsed.pick, [])

    def test_the_first_command_wins_whichever_it_is(self):
        parsed = fp.FuzzReferee.parse_commands("PICK 0 PLUM;MOVE 0 4 1")
        self.assertEqual(parsed.pick, [(0, "PLUM")])
        self.assertEqual(parsed.moves, {})

    def test_dedup_is_per_unit_not_global(self):
        parsed = fp.FuzzReferee.parse_commands("MINE 0;MINE 1")
        self.assertEqual(parsed.mine, [0, 1])

    def test_train_is_not_unit_scoped_and_keeps_parse_order(self):
        parsed = fp.FuzzReferee.parse_commands(
            "TRAIN 1 2 3 4;MOVE 0 4 1;TRAIN 5 6 7 8;DROP 0")
        self.assertEqual(parsed.train, [(1, 2, 3, 4), (5, 6, 7, 8)])
        self.assertEqual(parsed.drop, [], "unit 0 was already used by MOVE")

    def test_parsing_happens_before_any_mutation(self):
        # The parser is a pure classmethod: it cannot touch referee state.
        self.assertIsInstance(
            fp.FuzzReferee.__dict__["parse_commands"], classmethod)


# --- blocker 1 / contract C3: strict trust-boundary parsing ----------------

class TestMalformedCommandsAreRetainedErrors(unittest.TestCase):
    """Contract C3.  This is a DELIBERATE DIVERGENCE FROM engine.rs, not
    conformance: `engine.rs::parse_cmds` is permissive (697-706 accepts
    `parts.len() >= 5` and coerces every unparsable talent with
    `parse().unwrap_or(0)`).  At the panel's trust boundary a malformed
    emitted command is an instrument/protocol error and must be RETAINED
    with its raw bytes, never converted into a fabricated legal command."""

    def test_four_field_train_is_a_malformed_command(self):
        parsed = fp.FuzzReferee.parse_commands("TRAIN 1 1 1", turn=7)
        self.assertEqual(parsed.train, [])
        self.assertEqual(len(parsed.errors), 1)
        err = parsed.errors[0]
        self.assertEqual(err["kind"], fp.ERROR_MALFORMED)
        self.assertEqual(err["verb"], "TRAIN")
        self.assertEqual(err["raw"], "TRAIN 1 1 1")
        self.assertEqual(err["turn"], 7)

    def test_six_field_train_is_a_malformed_command(self):
        parsed = fp.FuzzReferee.parse_commands("TRAIN 1 1 1 1 1")
        self.assertEqual(parsed.train, [])
        self.assertEqual([e["kind"] for e in parsed.errors],
                         [fp.ERROR_MALFORMED])

    def test_non_integer_talent_is_a_malformed_command_not_a_zero(self):
        parsed = fp.FuzzReferee.parse_commands("TRAIN x 1 1 1")
        self.assertEqual(parsed.train, [])
        self.assertEqual([e["kind"] for e in parsed.errors],
                         [fp.ERROR_MALFORMED])

    def test_malformed_train_cannot_fabricate_a_zero_speed_worker(self):
        """The concrete state divergence behind C3 (review B1).  Coercing a
        non-integer movement field to 0 spawns a speed-0 worker on the
        non-walkable shack; engine.rs::next_cell (99-144) with speed 0 can
        only ever select the source cell, so such a worker must never
        appear at all."""
        ref = train_referee(inventory=[9, 9, 9, 0, 9, 0])
        ref.apply("TRAIN x 1 1 1")
        self.assertEqual(len(ref.own_unit_ids()), 1)
        self.assertEqual(ref.inv, [9, 9, 9, 0, 9, 0])
        self.assertEqual(ref.execution_status, fp.ERROR_MALFORMED)

    def test_a_speed_zero_unit_on_the_shack_cannot_step_out(self):
        ref = train_referee(units=[[0, 0, 0, 0, 0, 2, 1, 1] + [0] * 6,
                                   [5, 1, 4, 2, 1, 2, 0, 0] + [0] * 6])
        ref.apply("MOVE 0 3 1")
        self.assertEqual(ref.units[0]["cell"], (0, 0))

    def test_malformed_arity_is_rejected_for_every_verb(self):
        for line in ("MOVE 0 4", "HARVEST", "PICK 0", "PLANT 0",
                     "DROP 0 extra", "MINE", "CHOP 0 0"):
            with self.subTest(line=line):
                parsed = fp.FuzzReferee.parse_commands(line)
                self.assertEqual([e["kind"] for e in parsed.errors],
                                 [fp.ERROR_MALFORMED], line)

    def test_non_integer_unit_id_is_malformed(self):
        parsed = fp.FuzzReferee.parse_commands("MOVE zero 4 1")
        self.assertEqual([e["kind"] for e in parsed.errors],
                         [fp.ERROR_MALFORMED])

    def test_unknown_item_is_malformed(self):
        for line in ("PICK 0 GOLD", "PLANT 0 IRON"):
            with self.subTest(line=line):
                parsed = fp.FuzzReferee.parse_commands(line)
                self.assertEqual([e["kind"] for e in parsed.errors],
                                 [fp.ERROR_MALFORMED], line)

    def test_the_error_record_is_json_serialisable(self):
        parsed = fp.FuzzReferee.parse_commands("TRAIN 1 1 1")
        json.dumps(parsed.errors)


# --- blocker 7 / contract §8: unsupported verbs retain the row -------------

class TestUnsupportedVerbRetainsTheRow(unittest.TestCase):
    """Review B6/B7 + contract §8: 'A row with incomplete command execution
    is counted in the denominator and makes the aggregate gate unready. It is
    never silently dropped and never reported as a clean game.'"""

    def test_unsupported_verb_is_a_retained_error_not_an_abort(self):
        ref = train_referee()
        ref.apply("TELEPORT 0 1 1")          # must NOT raise
        self.assertEqual(ref.execution_status, fp.ERROR_UNSUPPORTED_VERB)
        self.assertEqual(len(ref.command_errors), 1)
        self.assertEqual(ref.command_errors[0]["verb"], "TELEPORT")
        self.assertEqual(ref.command_errors[0]["raw"], "TELEPORT 0 1 1")

    def test_the_rest_of_the_line_is_still_recorded_as_invalid(self):
        ref = train_referee()
        ref.apply("MOVE 0 2 0;TELEPORT 0 1 1")
        self.assertNotEqual(ref.execution_status, "ok")

    def test_panel_retains_the_row_and_publishes_gate_unready(self):
        bogus = compiled_bot("bogusverbbot", BOGUS_VERB_BOT)
        wait = compiled_bot("waitbot", WAIT_BOT)
        with tempfile.TemporaryDirectory() as tmp:
            cfg = {
                "task": "fuzz-selftest-unsupported",
                "instrument_version": fp.INSTRUMENT_VERSION,
                "corpus_version": fp.CORPUS_VERSION,
                "run_identity": "candidate",
                "candidate": {"source": str(bogus)},
                "parent": {"source": str(wait)},
                "seeds": [11], "maps": 1, "turns": 8, "processes": 1,
                "class_mix": {"open_field": 1.0},
                "opponent_mix": {"idle": 1.0},
            }
            cfg_path = Path(tmp) / "cfg.json"
            cfg_path.write_text(json.dumps(cfg))
            report = Path(tmp) / "r.md"
            out = Path(tmp) / "r.json"
            code = fp.main(["--config", str(cfg_path), "--report",
                            str(report), "--json", str(out)])
            self.assertEqual(code, fp.EXIT_ERROR)
            payload = json.loads(out.read_text())
            self.assertEqual(payload["verdict"], "GATE_UNREADY")
            self.assertEqual(len(payload["games"]), 2,
                             "both seats stay in the denominator")
            for row in payload["games"]:
                self.assertEqual(row["execution_status"],
                                 fp.ERROR_UNSUPPORTED_VERB)
                self.assertTrue(row["command_errors"])
                self.assertIn("raw", row["command_errors"][0])
            self.assertIn("GATE_UNREADY", report.read_text())


# --- blocker 6 / contract §8: per-row provenance ---------------------------

class TestRowProvenance(unittest.TestCase):

    def test_every_row_carries_execution_status_events_and_hashes(self):
        wait = compiled_bot("waitbot", WAIT_BOT)
        with tempfile.TemporaryDirectory() as tmp:
            cfg = {
                "task": "fuzz-selftest-provenance",
                "instrument_version": fp.INSTRUMENT_VERSION,
                "corpus_version": fp.CORPUS_VERSION,
                # one bot against itself IS a floor run (review B5).
                "run_identity": "floor",
                "candidate": {"source": str(wait)},
                "parent": {"source": str(wait)},
                "seeds": [11], "maps": 1, "turns": 8, "processes": 1,
                "class_mix": {"open_field": 1.0},
                "opponent_mix": {"idle": 1.0},
            }
            cfg_path = Path(tmp) / "cfg.json"
            cfg_path.write_text(json.dumps(cfg))
            out = Path(tmp) / "r.json"
            fp.main(["--config", str(cfg_path), "--report",
                     str(Path(tmp) / "r.md"), "--json", str(out)])
            payload = json.loads(out.read_text())
            self.assertEqual(payload["referee_sha256"], fp.referee_sha256())
            for row in payload["games"]:
                for key in ("execution_status", "command_errors",
                            "command_error_total", "error_lines",
                            "train_events", "spawns", "run_identity",
                            "parent_execution_status",
                            "parent_command_errors", "provenance"):
                    self.assertIn(key, row)
                prov = row["provenance"]
                self.assertEqual(prov["referee_sha256"], fp.referee_sha256())
                self.assertEqual(prov["corpus_version"], fp.CORPUS_VERSION)
                self.assertEqual(prov["instrument_version"],
                                 fp.INSTRUMENT_VERSION)
                self.assertIn("engine_sha256", prov)

    def test_train_events_record_turn_bill_and_spawn(self):
        ref = train_referee(inventory=[9, 9, 9, 0, 9, 0])
        ref.apply("TRAIN 2 1 1 1")
        self.assertEqual(len(ref.train_events), 1)
        ev = ref.train_events[0]
        self.assertEqual(ev["turn"], 1)
        self.assertEqual(ev["talents"], [2, 1, 1, 1])
        self.assertTrue(ev["spawned"])
        self.assertEqual(ev["cost"], fp.training_cost(1, (2, 1, 1, 1)))
        self.assertEqual(ev["unit_id"], 6)
        self.assertEqual(ev["cell"], [0, 0])   # the own shack
        self.assertEqual(ev["carry"], [0] * 6)
        json.dumps(ref.train_events)

    def test_a_rejected_train_is_also_recorded(self):
        ref = train_referee(inventory=[0] * 6)
        ref.apply("TRAIN 1 1 1 1")
        self.assertEqual(len(ref.train_events), 1)
        self.assertFalse(ref.train_events[0]["spawned"])
        self.assertEqual(ref.train_events[0]["reason"], "unaffordable")

    def test_referee_hash_tracks_the_actual_source(self):
        self.assertEqual(
            fp.referee_sha256(),
            fp.sha256_path(Path(fp.__file__)))


# --- blocker 8 / review B7: version declaration fails closed ---------------

class TestVersionDeclarationFailsClosed(unittest.TestCase):

    def _cfg(self, **overrides):
        cfg = {
            "task": "t",
            "instrument_version": fp.INSTRUMENT_VERSION,
            "corpus_version": fp.CORPUS_VERSION,
            "run_identity": "candidate",
            "candidate": {"source": "c.rs"}, "parent": {"source": "p.rs"},
            "seeds": [1], "maps": 1, "turns": 4,
        }
        cfg.update(overrides)
        return cfg

    def _load(self, cfg):
        with tempfile.TemporaryDirectory() as tmp:
            # review B5: the identity check reads the two sources' bytes, so
            # they have to exist and differ for a `candidate` declaration.
            (Path(tmp) / "c.rs").write_text("// candidate\n")
            (Path(tmp) / "p.rs").write_text("// parent\n")
            p = Path(tmp) / "cfg.json"
            p.write_text(json.dumps(cfg))
            return fp.load_config(p)

    def test_missing_corpus_version_is_rejected(self):
        cfg = self._cfg()
        cfg.pop("corpus_version")
        with self.assertRaises(fp.PanelError) as ctx:
            self._load(cfg)
        self.assertIn("corpus_version", str(ctx.exception))

    def test_missing_instrument_version_is_rejected(self):
        cfg = self._cfg()
        cfg.pop("instrument_version")
        with self.assertRaises(fp.PanelError):
            self._load(cfg)

    def test_the_versions_are_not_in_defaults(self):
        # If they stay in DEFAULTS, `cfg.update(raw)` re-supplies them and
        # the equality check below can never fail (review B7).
        self.assertNotIn("corpus_version", fp.DEFAULTS)
        self.assertNotIn("instrument_version", fp.DEFAULTS)

    def test_a_correct_declaration_still_loads(self):
        self.assertEqual(self._load(self._cfg())["corpus_version"],
                         fp.CORPUS_VERSION)

    def test_the_committed_configs_declare_the_r4_bump(self):
        for name in ("fuzz-panel-config.json",
                     "fuzz-panel-floor-config.json"):
            with self.subTest(config=name):
                cfg = json.loads((HERE / name).read_text())
                self.assertEqual(cfg["corpus_version"], fp.CORPUS_VERSION)
                self.assertEqual(cfg["instrument_version"],
                                 fp.INSTRUMENT_VERSION)
                self.assertIn("c5", cfg["corpus_version"])


# --- blocker 12-F: no silent upstream dispatcher ---------------------------

class TestNoSecondCommandLanguage(unittest.TestCase):
    """Review B11 / contract §1: 'the repaired panel must not contain a
    second, informal command language.'  The inherited
    `make_banana_traces.Referee.apply` is a sequential if/elif fragment
    executor with a silent fall-through bottom -- the original defect.  No
    code path may reach it any more."""

    def test_the_referee_never_delegates_to_the_inherited_dispatcher(self):
        src = inspect.getsource(fp.FuzzReferee)
        self.assertNotIn("mbt.Referee.apply", src)

    def test_no_handler_delegates_to_the_inherited_module(self):
        for name in dir(fp.FuzzReferee):
            if not name.startswith("_apply_") and not name.startswith(
                    "_cmd_"):
                continue
            fn = getattr(fp.FuzzReferee, name)
            if not callable(fn):
                continue
            self.assertNotIn("mbt.Referee", inspect.getsource(fn), name)

    def test_the_inherited_apply_would_be_caught_if_it_were_reachable(self):
        # Control: prove the assertion above is not vacuous.
        self.assertIn("mbt.Referee", inspect.getsource(fp))


# --- blocker 9 / contract §7: the m040 six-part regression packet ----------

M040_FLOOR_BOT_SHA256 = (
    "a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55")

# MEASURED under corpus c4 (see referee-train-repair-r3-2026-08-10.md §7) and
# pinned byte-for-byte.  These are the two mandatory rows of contract §7.
# r4 RE-MEASUREMENT (corpus bump c4 -> c5).  m040 runs the `harvester`
# opponent profile, and B2 changes what that opponent can do in a turn: it
# can no longer step onto a plant AND harvest it in the same turn, because
# its intent is now a command line subject to engine.rs:717-720.  It
# therefore strips the shared map more slowly, the floor bot banks its bill
# sooner, and seat 0's single TRAIN moves from turn 35 (c4) to turn 33 (c5).
# Every other clause of the six-part packet is byte-identical in both
# corpora, and seat 1 is unchanged at turn 19.  Nothing here was chosen; it
# was measured after the repair and is recorded with its c4 predecessor.
M040_EXPECTED = {
    0: {"train_turn": 33, "unit_id": 6, "talents": [1, 1, 0, 1],
        "cell": [1, 2], "cost": [2, 2, 1, 0, 2, 0],
        "inventory_after": [0, 0, 0, 2, 0, 0],
        "serialized_unit_row": "6 0 1 2 1 1 0 1 0 0 0 0 0 0",
        "train_emissions": [33]},
    1: {"train_turn": 19, "unit_id": 6, "talents": [1, 1, 0, 1],
        "cell": [9, 1], "cost": [2, 2, 1, 0, 2, 0],
        "inventory_after": [0, 0, 0, 2, 0, 0],
        "serialized_unit_row": "6 0 9 1 1 1 0 1 0 0 0 0 0 0",
        "train_emissions": [19]},
}

# --- committed mutation definitions (review B9) ----------------------------
# Each entry is an exact byte edit of the committed `fuzz_panel.py`, the
# blocker it probes and the test that must catch it.  `mutation_drive.py`
# equivalents no longer live in scratch: the definitions are here and the
# caught/survived results are in the r3 report.
MUTATIONS = [
    {"id": "M1-malformed-train-coerced",
     "blocker": "1 (C3 strict TRAIN parsing)",
     "pinned_by": "TestMalformedCommandsAreRetainedErrors",
     "old": "            if len(tok) != 5:\n                raise "
            "_Malformed(",
     "new": "            if False:\n                raise _Malformed("},
    {"id": "M2-textual-order-executor",
     "blocker": "2 (C4 full phase order)",
     "pinned_by": "TestPhaseOrder / TestDifferentialFullState",
     "old": "        self._apply_pick(list(parsed.pick) + list(opp.pick))",
     "new": "        pass  # mutated: PICK dropped from the phase order"},
    {"id": "M3-no-per-unit-dedup",
     "blocker": "3 (C5 first non-TRAIN per unit)",
     "pinned_by": "TestParserUnitDedup",
     "old": "            if uid in used:\n                continue\n"
            "            used.add(uid)",
     "new": "            pass"},
    {"id": "M4-drop-funds-train",
     "blocker": "4 (O1 same-turn matrix)",
     "pinned_by": "TestPhaseOrder.test_drop_never_funds_a_same_turn_train",
     "old": "        self._apply_drop(list(parsed.drop) + list(opp.drop))\n"
            "        self._apply_mine(list(parsed.mine) + list(opp.mine))",
     "new": "        self._apply_mine(list(parsed.mine) + list(opp.mine))\n"
            "        self._apply_drop(list(parsed.drop) + list(opp.drop))"},
    {"id": "M5-next-cell-ignores-speed",
     "blocker": "5 (differential oracle) + the zero-speed shack divergence",
     "pinned_by": "TestDifferentialFullState / "
                  "test_a_speed_zero_unit_on_the_shack_cannot_step_out",
     "old": "        in_range = [c for c, dd in src.items()\n"
            "                    if dd <= speed and c in tdist]",
     "new": "        in_range = [c for c, dd in src.items()\n"
            "                    if dd <= max(speed, 1) and c in tdist]"},
    {"id": "M6-drop-the-provenance",
     "blocker": "6 (per-row provenance)",
     "pinned_by": "TestRowProvenance",
     "old": "        \"run_identity\": job.get(\"run_identity\"),\n"
            "        \"provenance\": provenance(job.get(\"run_identity\")),",
     "new": "        \"run_identity\": job.get(\"run_identity\"),\n"
            "        \"provenance\": {},"},
    {"id": "M7-unsupported-verb-aborts",
     "blocker": "7 (row retention)",
     "pinned_by": "TestUnsupportedVerbRetainsTheRow",
     "old": "                p.errors.append(command_error(\n"
            "                    ERROR_UNSUPPORTED_VERB, verb, raw, turn,",
     "new": "                raise unsupported_command(verb, raw, turn)\n"
            "                p.errors.append(command_error(\n"
            "                    ERROR_UNSUPPORTED_VERB, verb, raw, turn,"},
    {"id": "M8-version-defaults-restored",
     "blocker": "8 (version declaration fails closed)",
     "pinned_by": "TestVersionDeclarationFailsClosed",
     "old": "    for key, current in ((\"instrument_version\", "
            "INSTRUMENT_VERSION),\n                         (\"corpus_version\""
            ", CORPUS_VERSION)):\n        if key not in raw:",
     "new": "    for key, current in ((\"instrument_version\", "
            "INSTRUMENT_VERSION),\n                         (\"corpus_version\""
            ", CORPUS_VERSION)):\n        if False:"},
    {"id": "M9-train-events-dropped",
     "blocker": "9 (m040 six-part packet)",
     "pinned_by": "TestM040SixPartPacket / TestRowProvenance",
     "old": "        self.train_events.append(event)",
     "new": "        pass  # mutated: TRAIN events no longer recorded"},
    {"id": "M10-reinstate-the-bot-worker-cap",
     "blocker": "12 / r2 regression guard (no invented worker cap)",
     "pinned_by": "TestTrainAuthorityIsTheEngine",
     "old": "        n = len(self.own_unit_ids(player))\n"
            "        cost = training_cost(n, talents)\n"
            "        inv = self._inv_of(player)\n"
            "        for item in self.train_billed_items():\n"
            "            if inv[item] < cost[item]:",
     "new": "        n = len(self.own_unit_ids(player))\n"
            "        if n >= 2:\n            return \"worker_cap\"\n"
            "        cost = training_cost(n, talents)\n"
            "        inv = self._inv_of(player)\n"
            "        for item in self.train_billed_items():\n"
            "            if inv[item] < cost[item]:"},
    # --- r4 blockers -----------------------------------------------------
    {"id": "M11-opponent-stream-ignored",
     "blocker": "B2 (one phase-merged two-player transition)",
     "pinned_by": "TestDifferentialTwoPlayer / "
                  "TestOpponentIsAPhaseMergedCommandStream",
     "old": "        moves = dict(parsed.moves)\n"
            "        moves.update(opp.moves)",
     "new": "        moves = dict(parsed.moves)"},
    {"id": "M12-train-ignores-the-player",
     "blocker": "B2 (apply_train is per player, engine.rs:786-791)",
     "pinned_by": "TestDifferentialTwoPlayer",
     "old": "        self.units[nid] = {\n"
            "            \"player\": player, \"cell\": self.shacks[player],"
            " \"speed\": ms,",
     "new": "        self.units[nid] = {\n"
            "            \"player\": 0, \"cell\": self.shacks[0],"
            " \"speed\": ms,"},
    {"id": "M13-parent-failure-fails-open",
     "blocker": "B3 (parent execution dominates the aggregate)",
     "pinned_by": "TestParentExecutionFailsClosed",
     "old": "    return (row.get(\"execution_status\", EXECUTION_OK) "
            "!= EXECUTION_OK\n"
            "            or row.get(\"parent_execution_status\",\n"
            "                       EXECUTION_OK) != EXECUTION_OK)",
     "new": "    return row.get(\"execution_status\", EXECUTION_OK) "
            "!= EXECUTION_OK"},
    {"id": "M14-raw-fragment-stripped-again",
     "blocker": "B4 (verbatim bytes + exact span)",
     "pinned_by": "TestDurableRawCommandEvidence",
     "old": "        for start, end, raw in cls.split_fragments(command_line):"
            "\n            norm = \" \".join(raw.split())",
     "new": "        for start, end, raw in cls.split_fragments(command_line):"
            "\n            raw = raw.strip()"
            "\n            norm = \" \".join(raw.split())"},
    {"id": "M15-error-stream-recapped",
     "blocker": "B4 (the retained stream is uncapped)",
     "pinned_by": "TestDurableRawCommandEvidence",
     "old": "            self.command_errors.append(err)",
     "new": "            if len(self.command_errors) < 50:\n"
            "                self.command_errors.append(err)"},
    {"id": "M16-floor-claim-unchecked",
     "blocker": "B5 (run identity is machine-checked)",
     "pinned_by": "TestRunIdentityIsMachineChecked",
     "old": "    if identity == RUN_IDENTITY_FLOOR and not same:",
     "new": "    if False:"},
]


class TestM040SixPartPacket(unittest.TestCase):
    """Contract §7.  Six clauses, all machine-checked, both seats."""

    def _run(self, seat):
        cfg = fp.load_config(HERE / "fuzz-panel-config.json")
        classes = fp.schedule(cfg["class_mix"], int(cfg["maps"]))
        profiles = fp.schedule(cfg["opponent_mix"], int(cfg["maps"]))
        _, specs = fp.build_skeleton(40, classes[40], profiles[40], cfg)
        binary = compiled_binary("floorbot", FLOOR_BOT_SOURCE)
        ref = fp.make_referee(specs[seat])
        transcript, commands = rt.run_binary_custom(
            binary, ref, int(cfg["turns"]))
        return cfg, ref, transcript, commands

    def test_floor_bot_source_sha_is_pinned(self):
        # Contract §7 clause 6: the compiled floor bot's source SHA is part
        # of the regression packet.
        self.assertEqual(fp.sha256_path(FLOOR_BOT_SOURCE),
                         M040_FLOOR_BOT_SHA256)

    def _packet(self, seat):
        exp = M040_EXPECTED[seat]
        cfg, ref, transcript, commands = self._run(seat)
        # (1) the first affordable TRAIN is executed exactly once
        spawned = [e for e in ref.train_events if e["spawned"]]
        self.assertEqual(len(spawned), 1)
        self.assertEqual(spawned[0]["turn"], exp["train_turn"])
        # (2) the trained unit appears with exact id/stats/cell/carry
        self.assertEqual(spawned[0]["unit_id"], exp["unit_id"])
        self.assertEqual(spawned[0]["talents"], exp["talents"])
        self.assertEqual(spawned[0]["cell"], exp["cell"])
        self.assertEqual(spawned[0]["carry"], [0] * 6)
        self.assertEqual(spawned[0]["cost"], exp["cost"])
        self.assertEqual(spawned[0]["inventory_after"], exp["inventory_after"])
        # ... and in the NEXT serialized state block
        blocks = transcript.split("\n")
        self.assertIn(exp["serialized_unit_row"], blocks,
                      "the spawn must be visible in the next state block")
        # (3) the repeated-TRAIN no-op loop is gone
        trains = [i + 1 for i, line in enumerate(commands.splitlines())
                  if any(c.strip().upper().startswith("TRAIN")
                         for c in line.split(";"))]
        self.assertEqual(trains, exp["train_emissions"])
        # (4) no unsupported or malformed command occurred
        self.assertEqual(ref.command_errors, [])
        self.assertEqual(ref.execution_status, "ok")
        # (5)+(6) provenance
        self.assertEqual(fp.referee_sha256(), fp.sha256_path(
            Path(fp.__file__)))
        self.assertEqual(cfg["corpus_version"], fp.CORPUS_VERSION)

    def test_m040_seat_0_packet(self):
        self._packet(0)

    def test_m040_seat_1_packet(self):
        self._packet(1)

    def test_old_rows_are_retained_as_machine_readable_invalid_evidence(self):
        cfg = json.loads((HERE / "fuzz-panel-config.json").read_text())
        rows = cfg["instrument_invalid_rows"]
        keys = {(r["map_id"], r["seat"], r["corpus_version"]) for r in rows}
        self.assertIn(("m040", 0, "c1-silent-train-2026-08-09"), keys)
        self.assertIn(("m040", 1, "c1-silent-train-2026-08-09"), keys)
        for r in rows:
            self.assertEqual(r["status"], "instrument_invalid")
            self.assertTrue(r["reason"])
            self.assertFalse(r["eligible_for_calibration"])


# --- blocker 10: committed mutation definitions ----------------------------

class TestMutationDefinitionsAreCommitted(unittest.TestCase):
    """Review B9: the mutation evidence must be reproducible from the
    committed packet, not from a scratch driver.  Each definition below is
    an exact byte edit of `fuzz_panel.py`; the report records caught/survived
    per blocker."""

    def test_every_mutant_is_valid_python(self):
        # A mutant that does not compile proves nothing -- it "fails" for the
        # wrong reason and, if the driver only greps for FAIL:/ERROR: lines,
        # can even look like a SURVIVOR.  (Measured: the first draft of M1
        # had the wrong indentation and did exactly that.)
        src = (HERE / "fuzz_panel.py").read_text()
        for mut in MUTATIONS:
            with self.subTest(mutation=mut["id"]):
                mutant = src.replace(mut["old"], mut["new"])
                self.assertNotEqual(mutant, src)
                compile(mutant, "mutant-%s.py" % mut["id"], "exec")

    def test_every_mutation_anchor_still_exists_exactly_once(self):
        src = (HERE / "fuzz_panel.py").read_text()
        for mut in MUTATIONS:
            with self.subTest(mutation=mut["id"]):
                self.assertEqual(src.count(mut["old"]), 1,
                                 "anchor rotted: %s" % mut["id"])
                self.assertNotEqual(mut["old"], mut["new"])
                self.assertTrue(mut["blocker"])
                self.assertTrue(mut["pinned_by"])


# ===========================================================================
# r4 revision -- against chatgpt_1/referee-train-repair-r3-review-2026-08-09.md
#
#   B2  active opponents still use a second informal simulator
#   B3  parent protocol failure fails open at aggregate level
#   B4  the durable error packet does not retain exact raw output
#   B5  the corrected floor is still not a committed reproducible packet
#   B6  the corpus version cannot be adopted while B2-B5 remain
#   C-O1 / C-C4-C5  the two authoritative contract corrections
# ===========================================================================

# A bot whose stdout line carries leading blanks, empty fragments, an
# unsupported verb and a malformed TRAIN -- i.e. exactly the bytes review B4
# says the durable packet must be able to reconstruct.
RAW_EVIDENCE_BOT = r"""
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
        println!("  MOVE 0 1 1 ;; FLY 0 ; TRAIN 1 1 1 ;");
        std::io::stdout().flush().unwrap();
    }
}
"""

OPP_ROWS = ("0....1",
            "......",
            "......")


def opp_referee(profile, opp_unit, plants=(), inventory=(0,) * 6,
                own_unit=(0, 0, 1, 0, 1, 2, 1, 1, 0, 0, 0, 0, 0, 0)):
    return fp.make_referee({
        "rows": list(OPP_ROWS), "inventory": list(inventory),
        "plants": [list(p) for p in plants],
        "units": [list(own_unit), list(opp_unit)], "profile": profile})


class TestOpponentIsAPhaseMergedCommandStream(unittest.TestCase):
    """Review B2.

    `engine.rs::step` (755-806) takes TWO command streams and merges them
    phase by phase.  Until r4 the panel applied the candidate's eight phases
    and then called `OPP_POLICIES[self.profile](self)`, a direct
    mini-simulator that moved, harvested, chopped and banked opponent units
    itself.  That produces a world transition `step` cannot produce, so every
    opponent-sensitive property (detectors, margins, P4) was measured against
    a fiction."""

    def test_the_opponent_policies_emit_command_lines(self):
        for profile in fp.OPP_PROFILES:
            with self.subTest(profile=profile):
                ref = opp_referee(
                    profile, [5, 1, 4, 2, 1, 2, 1, 1] + [0] * 6,
                    plants=[("PLUM", 4, 1, 2, 4, 3, 5)])
                line = fp.opponent_command_line(ref)
                self.assertIsInstance(
                    line, str,
                    "an opponent policy must PRODUCE COMMANDS, not mutate "
                    "the world")

    def test_the_generated_opponent_line_is_well_formed(self):
        for profile in fp.OPP_PROFILES:
            with self.subTest(profile=profile):
                ref = opp_referee(
                    profile, [5, 1, 4, 2, 1, 2, 1, 1] + [0] * 6,
                    plants=[("PLUM", 4, 1, 2, 4, 3, 5)])
                parsed = fp.FuzzReferee.parse_commands(
                    fp.opponent_command_line(ref), ref.turn)
                self.assertEqual(parsed.errors, [],
                                 "the panel's own opponent line must pass "
                                 "its own trust boundary")

    def test_no_direct_opponent_simulator_remains(self):
        src = (HERE / "fuzz_panel.py").read_text()
        self.assertNotIn("OPP_POLICIES[self.profile](self)", src)
        for gone in ("def _act_harvest(", "def _act_chop("):
            self.assertNotIn(gone, src,
                             "%s is a second, informal applier" % gone)

    def test_execute_merges_two_parsed_streams(self):
        sig = inspect.signature(fp.FuzzReferee._execute)
        self.assertIn("opp", sig.parameters,
                      "_execute must take BOTH players' parsed streams and "
                      "merge them phase by phase (engine.rs:760-801)")

    def test_opponent_cannot_move_and_act_in_the_same_turn(self):
        """engine.rs:717-720 -- one non-TRAIN command per unit per turn.  The
        direct simulator stepped the unit AND harvested on arrival."""
        ref = opp_referee("harvester", [5, 1, 4, 2, 1, 4, 1, 1] + [0] * 6,
                          plants=[("PLUM", 4, 1, 2, 4, 3, 5)])
        ref.apply("WAIT")
        self.assertEqual(ref.units[5]["cell"], (4, 1), "it moved")
        self.assertEqual(ref.plants[(4, 1)]["fruits"], 3,
                         "and could NOT also harvest in the same turn")
        ref.apply("WAIT")
        self.assertEqual(ref.plants[(4, 1)]["fruits"], 2)

    def test_opponent_harvest_goes_through_the_engine_applier(self):
        """engine.rs::apply_harvest is multi-round (`for i in 1..=3`): a
        troll with hp 2 takes TWO fruits.  The retired `_act_harvest` took
        exactly one, whatever the harvest power."""
        ref = opp_referee("harvester", [5, 1, 4, 1, 1, 4, 2, 1] + [0] * 6,
                          plants=[("PLUM", 4, 1, 2, 4, 3, 5)])
        ref.apply("WAIT")
        self.assertEqual(ref.plants[(4, 1)]["fruits"], 1)
        self.assertEqual(ref.units[5]["carry"][fp.PLUM], 2)

    def test_the_opponent_stream_is_retained_on_the_referee(self):
        ref = opp_referee("harvester", [5, 1, 4, 2, 1, 4, 1, 1] + [0] * 6,
                          plants=[("PLUM", 4, 1, 2, 4, 3, 5)])
        ref.apply("WAIT")
        self.assertEqual(ref.opponent_commands, ["MOVE 5 4 1"])


# --- B2, strongest leg: two-player differential against engine.rs ----------

TWO_PLAYER_CASES = [
    Case("tp_move_contention_same_cell", D_ROWS, RICH,
         [_u(0, 0, 3, 2), _u(1, 1, 5, 2)],
         line="MOVE 0 4 2", line1="MOVE 1 4 2"),
    Case("tp_both_players_train", D_ROWS, RICH,
         [_u(0, 0, 3, 2), _u(1, 1, 5, 2)],
         line="TRAIN 1 1 1 1", line1="TRAIN 2 1 1 1",
         opp_inventory=RICH),
    Case("tp_opponent_shack_occupied_blocks_only_that_player", D_ROWS, RICH,
         [_u(0, 0, 3, 2), _u(1, 1, 7, 1)],
         line="TRAIN 1 1 1 1", line1="TRAIN 1 1 1 1",
         opp_inventory=RICH),
    Case("tp_both_command_the_same_unit", D_ROWS, RICH,
         [_u(0, 0, 2, 2), _u(1, 1, 5, 2)],
         line="MOVE 1 2 2", line1="MOVE 1 6 2"),
    Case("tp_both_chop_one_tree", D_ROWS, RICH,
         [_u(0, 0, 4, 2, chop=2, cap=6), _u(1, 1, 4, 2, chop=3, cap=6)],
         plants=[["PLUM", 4, 2, 3, 4, 0, 5]],
         line="CHOP 0", line1="CHOP 1"),
    Case("tp_both_harvest_one_plant", D_ROWS, RICH,
         [_u(0, 0, 4, 2, harvest=1, cap=4),
          _u(1, 1, 4, 2, harvest=2, cap=4)],
         plants=[["PLUM", 4, 2, 3, 4, 3, 5]],
         line="HARVEST 0", line1="HARVEST 1"),
    Case("tp_pick_and_drop_in_one_turn", D_ROWS, RICH,
         [_u(0, 0, 2, 1, cap=4), _u(1, 1, 6, 1, cap=4, carry=(0, 0, 2, 0,
                                                             0, 0))],
         line="PICK 0 PLUM", line1="DROP 1", opp_inventory=[0] * 6),
    Case("tp_mixed_plant_on_one_cell_cancels", D_ROWS, [0] * 6,
         [_u(0, 0, 4, 2, carry=(1, 0, 0, 0, 0, 0)),
          _u(1, 1, 4, 2, carry=(0, 1, 0, 0, 0, 0))],
         line="PLANT 0 PLUM", line1="PLANT 1 LEMON"),
    Case("tp_same_plant_on_one_cell_merges", D_ROWS, [0] * 6,
         [_u(0, 0, 4, 2, carry=(1, 0, 0, 0, 0, 0)),
          _u(1, 1, 4, 2, carry=(1, 0, 0, 0, 0, 0))],
         line="PLANT 0 PLUM", line1="PLANT 1 PLUM"),
    Case("tp_both_mine_the_same_iron", D_IRON, RICH,
         [_u(0, 0, 3, 2, chop=2, cap=6), _u(1, 1, 5, 1, chop=3, cap=6)],
         line="MINE 0", line1="MINE 1"),
]


class TestDifferentialTwoPlayer(unittest.TestCase):
    """Review B2, the non-circular leg: a merged two-player turn must match
    `engine::step(&mut g, &c0, &c1)` compiled from the authority's own
    bytes."""

    def _run_referee(self, case):
        ref = fp.make_referee(case.spec())
        ref.apply_two(case.line, case.line1)
        ref.grow()
        return ref

    def test_rust_authority_agrees_on_every_two_player_case(self):
        for case in TWO_PLAYER_CASES:
            with self.subTest(case=case.name):
                self.assertEqual(snapshot_from_referee(self._run_referee(case)),
                                 snapshot_from_rust(case))

    def test_sim_mirror_agrees_on_every_two_player_case(self):
        for case in TWO_PLAYER_CASES:
            if case.name in SIM_LEG_DEFECTS:
                continue
            with self.subTest(case=case.name):
                self.assertEqual(snapshot_from_referee(self._run_referee(case)),
                                 snapshot_from_sim(case))

    def test_the_two_player_oracle_is_not_vacuous(self):
        case = TWO_PLAYER_CASES[0]
        broken = snapshot_from_referee(self._run_referee(case))
        broken["units"][0][2] += 1
        self.assertNotEqual(broken, snapshot_from_rust(case))

    def test_every_two_player_case_actually_commands_player_one(self):
        for case in TWO_PLAYER_CASES:
            with self.subTest(case=case.name):
                self.assertTrue(case.fragments1())

    def test_a_generated_opponent_line_is_engine_conformant(self):
        """End to end: the line the panel's own policy generates, executed
        as player 1's stream through the authority."""
        ref = opp_referee("harvester", [5, 1, 4, 2, 1, 4, 1, 1] + [0] * 6,
                          plants=[("PLUM", 4, 1, 2, 4, 3, 5)])
        line1 = fp.opponent_command_line(ref)
        case = Case("generated_opponent_line", OPP_ROWS, [0] * 6,
                    [_u(0, 0, 1, 0, cap=2), _u(5, 1, 4, 2, cap=4)],
                    plants=[["PLUM", 4, 1, 2, 4, 3, 5]],
                    line="WAIT", line1=line1)
        ref2 = fp.make_referee(case.spec(profile="idle"))
        ref2.apply_two(case.line, case.line1)
        ref2.grow()
        self.assertEqual(snapshot_from_referee(ref2), snapshot_from_rust(case))


# --- B3: parent protocol failure must fail closed --------------------------

class TestParentExecutionFailsClosed(unittest.TestCase):
    """Review B3.  `aggregate_verdict` consumed only the CANDIDATE's
    `execution_status`, so a malformed or unsupported PARENT command left the
    aggregate at CLEAR/BLOCK while P3 and every diagnostic comparison
    consumed an invalid parent trace."""

    def test_aggregate_is_unready_when_only_the_parent_failed(self):
        self.assertEqual(
            fp.aggregate_verdict([{"execution_status": fp.EXECUTION_OK,
                                   "parent_execution_status":
                                       fp.ERROR_UNSUPPORTED_VERB,
                                   "block": False}]),
            "GATE_UNREADY")

    def test_aggregate_is_unready_for_a_malformed_parent_command(self):
        self.assertEqual(
            fp.aggregate_verdict([{"execution_status": fp.EXECUTION_OK,
                                   "parent_execution_status":
                                       fp.ERROR_MALFORMED,
                                   "block": True}]),
            "GATE_UNREADY")

    def _run(self, candidate, parent, tmp):
        cfg = {
            "task": "fuzz-selftest-parent-fail-closed",
            "instrument_version": fp.INSTRUMENT_VERSION,
            "corpus_version": fp.CORPUS_VERSION,
            "run_identity": "candidate",
            "candidate": {"source": str(candidate)},
            "parent": {"source": str(parent)},
            "seeds": [11], "maps": 1, "turns": 8, "processes": 1,
            "class_mix": {"open_field": 1.0},
            "opponent_mix": {"idle": 1.0},
        }
        cfg_path = Path(tmp) / "cfg.json"
        cfg_path.write_text(json.dumps(cfg))
        out = Path(tmp) / "r.json"
        code = fp.main(["--config", str(cfg_path), "--report",
                        str(Path(tmp) / "r.md"), "--json", str(out)])
        return code, json.loads(out.read_text())

    def test_unsupported_parent_command_makes_the_run_gate_unready(self):
        wait = compiled_bot("waitbot", WAIT_BOT)
        bogus = compiled_bot("bogusverbbot", BOGUS_VERB_BOT)
        with tempfile.TemporaryDirectory() as tmp:
            code, payload = self._run(wait, bogus, tmp)
        self.assertEqual(code, fp.EXIT_ERROR)
        self.assertEqual(payload["verdict"], "GATE_UNREADY")
        self.assertEqual(len(payload["games"]), 2, "both seats retained")
        for row in payload["games"]:
            self.assertEqual(row["execution_status"], fp.EXECUTION_OK)
            self.assertEqual(row["parent_execution_status"],
                             fp.ERROR_UNSUPPORTED_VERB)
            self.assertTrue(row["parent_command_errors"],
                            "the parent's error ledger must be RETAINED on "
                            "the durable row")
            self.assertEqual(row["parent_command_errors"][0]["verb"],
                             "TELEPORT")

    def test_malformed_parent_command_makes_the_run_gate_unready(self):
        wait = compiled_bot("waitbot", WAIT_BOT)
        raw = compiled_bot("rawevidencebot", RAW_EVIDENCE_BOT)
        with tempfile.TemporaryDirectory() as tmp:
            code, payload = self._run(wait, raw, tmp)
        self.assertEqual(code, fp.EXIT_ERROR)
        self.assertEqual(payload["verdict"], "GATE_UNREADY")
        for row in payload["games"]:
            self.assertNotEqual(row["parent_execution_status"],
                                fp.EXECUTION_OK)
            kinds = {e["kind"] for e in row["parent_command_errors"]}
            self.assertIn(fp.ERROR_MALFORMED, kinds)

    def test_the_parent_ledger_is_complete_on_the_row(self):
        wait = compiled_bot("waitbot", WAIT_BOT)
        bogus = compiled_bot("bogusverbbot", BOGUS_VERB_BOT)
        with tempfile.TemporaryDirectory() as tmp:
            _, payload = self._run(wait, bogus, tmp)
        for row in payload["games"]:
            for key in ("parent_execution_status", "parent_command_errors",
                        "parent_command_error_counts", "parent_train_events",
                        "parent_command_error_total"):
                self.assertIn(key, row)
            self.assertEqual(
                row["parent_command_error_total"],
                sum(row["parent_command_error_counts"].values()))

    def test_the_summary_counts_parent_invalid_rows(self):
        wait = compiled_bot("waitbot", WAIT_BOT)
        bogus = compiled_bot("bogusverbbot", BOGUS_VERB_BOT)
        with tempfile.TemporaryDirectory() as tmp:
            _, payload = self._run(wait, bogus, tmp)
        self.assertEqual(payload["stats"]["parent_instrument_invalid_games"],
                         2)
        self.assertEqual(payload["stats"]["gate_unready_games"], 2)


# --- B4: the durable packet must retain the exact raw output ---------------

class TestDurableRawCommandEvidence(unittest.TestCase):
    """Review B4.  `parse_commands` stripped every fragment before recording
    `raw`, so leading/trailing bytes, empty-fragment placement and fragment
    offsets were lost, and the retained list was capped at 50 while the full
    stream lived only in `artifacts`, which the JSON packet drops."""

    LINE = "  MOVE 0 1 1 ;; FLY 0 ; TRAIN 1 1 1 ;"

    def test_every_error_carries_an_exact_span_into_the_original_line(self):
        parsed = fp.FuzzReferee.parse_commands(self.LINE, turn=3)
        self.assertEqual(len(parsed.errors), 2)
        for err in parsed.errors:
            start, end = err["span"]
            self.assertEqual(self.LINE[start:end], err["raw"],
                             "the span must reproduce the raw fragment "
                             "byte for byte")

    def test_the_raw_fragment_is_verbatim_and_the_normalization_separate(self):
        parsed = fp.FuzzReferee.parse_commands(self.LINE, turn=3)
        by_verb = {e["verb"]: e for e in parsed.errors}
        self.assertEqual(by_verb["FLY"]["raw"], " FLY 0 ")
        self.assertEqual(by_verb["FLY"]["normalized"], "FLY 0")

    def test_every_error_names_the_line_it_came_from(self):
        ref = train_referee()
        ref.apply(self.LINE)
        digest = hashlib.sha256(self.LINE.encode("utf-8")).hexdigest()
        for err in ref.command_errors:
            self.assertEqual(err["line_sha256"], digest)
            self.assertEqual(err["line_length"], len(self.LINE))

    def test_the_verbatim_line_is_retained_for_every_offending_turn(self):
        ref = train_referee()
        ref.apply(self.LINE)
        ref.apply("WAIT")
        ref.apply(self.LINE)
        self.assertEqual([e["turn"] for e in ref.error_lines], [1, 3])
        for entry in ref.error_lines:
            self.assertEqual(entry["line"], self.LINE)
            self.assertEqual(entry["length"], len(self.LINE))

    def test_the_error_stream_is_not_capped(self):
        n = 3 * 50
        line = ";".join("FLY %d" % i for i in range(n))
        ref = train_referee()
        ref.apply(line)
        self.assertEqual(ref.command_error_total, n)
        self.assertEqual(len(ref.command_errors), n,
                         "a capped ledger cannot reconstruct every "
                         "offending command from the durable packet")

    def test_the_durable_row_can_reconstruct_every_offending_command(self):
        raw = compiled_bot("rawevidencebot", RAW_EVIDENCE_BOT)
        wait = compiled_bot("waitbot", WAIT_BOT)
        with tempfile.TemporaryDirectory() as tmp:
            cfg = {
                "task": "fuzz-selftest-raw-evidence",
                "instrument_version": fp.INSTRUMENT_VERSION,
                "corpus_version": fp.CORPUS_VERSION,
                "run_identity": "candidate",
                "candidate": {"source": str(raw)},
                "parent": {"source": str(wait)},
                "seeds": [11], "maps": 1, "turns": 4, "processes": 1,
                "class_mix": {"open_field": 1.0},
                "opponent_mix": {"idle": 1.0},
            }
            cfg_path = Path(tmp) / "cfg.json"
            cfg_path.write_text(json.dumps(cfg))
            out = Path(tmp) / "r.json"
            fp.main(["--config", str(cfg_path), "--report",
                     str(Path(tmp) / "r.md"), "--json", str(out)])
            payload = json.loads(out.read_text())
        for row in payload["games"]:
            lines = {e["turn"]: e["line"] for e in row["error_lines"]}
            self.assertTrue(lines)
            self.assertEqual(row["command_error_total"],
                             len(row["command_errors"]))
            for err in row["command_errors"]:
                line = lines[err["turn"]]
                start, end = err["span"]
                self.assertEqual(line[start:end], err["raw"])
                self.assertEqual(
                    hashlib.sha256(line.encode("utf-8")).hexdigest(),
                    err["line_sha256"])


# --- B5: the run identity is declared and machine-checked ------------------

FLOOR_CONFIG = HERE / "fuzz-panel-floor-config.json"
CANDIDATE_CONFIG = HERE / "fuzz-panel-config.json"


class TestRunIdentityIsMachineChecked(unittest.TestCase):
    """Review B5 + owner instruction: a floor claim made from a candidate
    config must be IMPOSSIBLE, not merely discouraged.  Every config declares
    `run_identity`; `floor` requires candidate.source and parent.source to be
    the same bytes, `candidate` requires them to differ, and the identity is
    carried into the report, the JSON packet and every row."""

    def test_the_committed_candidate_config_declares_a_candidate_run(self):
        cfg = json.loads(CANDIDATE_CONFIG.read_text())
        self.assertEqual(cfg["run_identity"], "candidate")
        self.assertNotEqual(cfg["candidate"]["sha256"],
                            cfg["parent"]["sha256"])

    def test_a_committed_floor_config_exists_and_is_parent_versus_itself(self):
        self.assertTrue(FLOOR_CONFIG.exists(),
                        "the floor needs its OWN committed config: reusing "
                        "the candidate config under the label 'floor' is the "
                        "defect review B5 blocks on")
        cfg = json.loads(FLOOR_CONFIG.read_text())
        self.assertEqual(cfg["run_identity"], "floor")
        self.assertEqual(cfg["candidate"]["sha256"], cfg["parent"]["sha256"])
        self.assertEqual(
            fp.sha256_path(fp.resolve(fp.load_config(FLOOR_CONFIG),
                                      cfg["candidate"]["source"])),
            fp.sha256_path(fp.resolve(fp.load_config(FLOOR_CONFIG),
                                      cfg["parent"]["source"])))

    def test_both_committed_configs_load(self):
        for path, identity in ((CANDIDATE_CONFIG, "candidate"),
                               (FLOOR_CONFIG, "floor")):
            with self.subTest(config=path.name):
                self.assertEqual(fp.load_config(path)["run_identity"],
                                 identity)

    def _write(self, tmp, **over):
        wait = compiled_bot("waitbot", WAIT_BOT)
        osc = compiled_bot("oscbot", OSCILLATOR_BOT)
        cfg = {
            "task": "run-identity",
            "instrument_version": fp.INSTRUMENT_VERSION,
            "corpus_version": fp.CORPUS_VERSION,
            "run_identity": "candidate",
            "candidate": {"source": str(osc)},
            "parent": {"source": str(wait)},
            "seeds": [11], "maps": 1, "turns": 4, "processes": 1,
            "class_mix": {"open_field": 1.0}, "opponent_mix": {"idle": 1.0},
        }
        cfg.update(over)
        p = Path(tmp) / "cfg.json"
        p.write_text(json.dumps(cfg))
        return p

    def test_a_missing_run_identity_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self._write(tmp)
            cfg = json.loads(p.read_text())
            cfg.pop("run_identity")
            p.write_text(json.dumps(cfg))
            with self.assertRaises(fp.PanelError) as ctx:
                fp.load_config(p)
        self.assertIn("run_identity", str(ctx.exception))

    def test_a_floor_claim_over_two_different_bots_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self._write(tmp, run_identity="floor")
            with self.assertRaises(fp.PanelError) as ctx:
                fp.load_config(p)
        self.assertIn("floor", str(ctx.exception))

    def test_a_candidate_claim_over_one_bot_against_itself_is_rejected(self):
        wait = compiled_bot("waitbot", WAIT_BOT)
        with tempfile.TemporaryDirectory() as tmp:
            p = self._write(tmp, run_identity="candidate",
                            candidate={"source": str(wait)},
                            parent={"source": str(wait)})
            with self.assertRaises(fp.PanelError) as ctx:
                fp.load_config(p)
        self.assertIn("floor", str(ctx.exception))

    def test_an_unknown_run_identity_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self._write(tmp, run_identity="baseline")
            with self.assertRaises(fp.PanelError):
                fp.load_config(p)

    def test_the_identity_reaches_the_report_the_packet_and_every_row(self):
        wait = compiled_bot("waitbot", WAIT_BOT)
        with tempfile.TemporaryDirectory() as tmp:
            p = self._write(tmp, run_identity="floor",
                            candidate={"source": str(wait)},
                            parent={"source": str(wait)})
            report = Path(tmp) / "r.md"
            out = Path(tmp) / "r.json"
            fp.main(["--config", str(p), "--report", str(report),
                     "--json", str(out)])
            payload = json.loads(out.read_text())
            text = report.read_text()
        self.assertEqual(payload["run_identity"], "floor")
        self.assertIn("floor", text.lower())
        for row in payload["games"]:
            self.assertEqual(row["run_identity"], "floor")
            self.assertEqual(row["provenance"]["run_identity"], "floor")


# --- the two authoritative contract corrections ---------------------------

class TestCorrectedContractClauses(unittest.TestCase):
    """chatgpt_1's r3 review withdraws two clauses of its own frozen
    contract; the corrected rules are authoritative and pinned here.

    C-O1: PICK cannot fund TRAIN -- `engine.rs::apply_pick` (438-458) moves
    stock OUT of the bank, so it can only STARVE the bill; DROP (796) is
    after TRAIN (786) and cannot fund it either.

    C-C4/C5: textual-order invariance holds only when no unit has two
    non-TRAIN commands; when it does, `engine.rs:717-720` makes textual order
    choose the survivor."""

    def test_pick_can_only_starve_a_train_never_fund_it(self):
        base = dict(inventory=[2, 2, 2, 0, 2, 0])
        for line in ("PICK 0 PLUM;TRAIN 1 1 1 1", "TRAIN 1 1 1 1;PICK 0 PLUM"):
            with self.subTest(line=line):
                ref = train_referee(**base)
                ref.apply(line)
                self.assertEqual(
                    len(ref.own_unit_ids()), 1,
                    "PICK resolves BEFORE TRAIN in both textual orders and "
                    "removes the last PLUM from the bank")

    def test_no_pick_makes_the_same_bill_affordable(self):
        ref = train_referee(inventory=[2, 2, 2, 0, 2, 0])
        ref.apply("TRAIN 1 1 1 1")
        self.assertEqual(len(ref.own_unit_ids()), 2)

    def test_drop_cannot_fund_a_same_turn_train_either(self):
        ref = train_referee(inventory=[1, 1, 1, 0, 1, 0],
                            units=[[0, 0, 1, 0, 1, 4, 1, 1, 1, 1, 1, 0, 1, 0],
                                   [5, 1, 4, 2, 1, 2, 0, 0] + [0] * 6])
        ref.apply("DROP 0;TRAIN 1 1 1 1")
        self.assertEqual(len(ref.own_unit_ids()), 1)
        self.assertEqual(ref.inv, [2, 2, 2, 0, 2, 0])

    def test_textual_order_is_invariant_without_duplicate_unit_commands(self):
        units = [_u(0, 0, 2, 2, cap=6, carry=(1, 0, 0, 0, 0, 0)),
                 _u(2, 0, 5, 2, cap=6), _u(1, 1, 6, 1)]
        a = Case("inv_a", D_ROWS, RICH, units,
                 line="PLANT 0 PLUM;MOVE 2 3 2;TRAIN 1 1 1 1")
        b = Case("inv_b", D_ROWS, RICH, units,
                 line="TRAIN 1 1 1 1;MOVE 2 3 2;PLANT 0 PLUM")
        snaps = []
        for case in (a, b):
            ref = fp.make_referee(case.spec())
            ref.apply(case.line)
            ref.grow()
            snaps.append(snapshot_from_referee(ref))
        self.assertEqual(snaps[0], snaps[1])

    def test_with_a_duplicate_unit_command_textual_order_decides(self):
        units = [_u(0, 0, 2, 2, cap=6, carry=(1, 0, 0, 0, 0, 0)),
                 _u(1, 1, 6, 1)]
        snaps = []
        for line in ("PLANT 0 PLUM;MOVE 0 5 2", "MOVE 0 5 2;PLANT 0 PLUM"):
            case = Case("dup", D_ROWS, RICH, units, line=line)
            ref = fp.make_referee(case.spec())
            ref.apply(case.line)
            ref.grow()
            snaps.append(snapshot_from_referee(ref))
        self.assertNotEqual(
            snaps[0], snaps[1],
            "engine.rs:717-720 makes the FIRST command win, so with a "
            "duplicate the textual order is load-bearing -- invariance must "
            "NOT be asserted here")
        for case, snap in zip(
                (Case("dup_a", D_ROWS, RICH, units,
                      line="PLANT 0 PLUM;MOVE 0 5 2"),
                 Case("dup_b", D_ROWS, RICH, units,
                      line="MOVE 0 5 2;PLANT 0 PLUM")), snaps):
            with self.subTest(case=case.name):
                self.assertEqual(snap, snapshot_from_rust(case))


# --- B6: the corpus/instrument version must be bumped for r4 ---------------

class TestR4CorpusBump(unittest.TestCase):

    def test_the_instrument_and_corpus_are_the_r4_identity(self):
        self.assertIn("5", fp.INSTRUMENT_VERSION.split("/")[1][:2])
        self.assertTrue(fp.CORPUS_VERSION.startswith("c5"),
                        "B2-B5 change the trust envelope: c4 results cannot "
                        "enter calibration")

    def test_the_c4_corpus_is_retired_as_machine_readable_evidence(self):
        cfg = json.loads(CANDIDATE_CONFIG.read_text())
        retired = {r["corpus_version"] for r in cfg["instrument_invalid_rows"]}
        self.assertTrue(any(v.startswith("c4") for v in retired))
        for row in cfg["instrument_invalid_rows"]:
            self.assertFalse(row["eligible_for_calibration"])


if __name__ == "__main__":
    unittest.main()
