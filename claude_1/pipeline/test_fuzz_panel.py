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
