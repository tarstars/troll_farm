# Paired Self-Play A/B Gate (`playmatch` + `abgate.py`) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A cheap, high-n, paired REJECT filter (candidate vs champion self-play on the real engine) that kills arena-loser candidates locally before they cost an arena slot.

**Architecture:** Extract equality.rs's game driver into `src/game/driver.rs` (lib); add a thin Rust `playmatch` bin (one scored match → one machine-readable line); add `cgauto/abgate.py` (seed loop, seat-swap pairing, stats, verdict, CSV, self-tests); validate the whole instrument against 5 known arena verdicts (calibration study).

**Tech Stack:** Rust (existing crate `troll_farm`, edition 2021), Python 3 via `uv run --no-sync python` (stdlib only: argparse/subprocess/csv/math/concurrent.futures).

**Spec:** `docs/superpowers/specs/2026-07-11-selfplay-gate-design.md` (approved 2026-07-11).

## Global Constraints

- cwd: run `cargo` from `/home/tarstars/prj/troll_farm/rust`, run `cgauto/*.py` and the calibration script from `/home/tarstars/prj/troll_farm` (repo root).
- Python invocation is always `uv run --no-sync python`.
- Do NOT touch `rust/src/game/engine.rs` (validated referee model) or any frozen artifact in `cgauto/submissions/` (read-only inputs).
- Reimplementing referee logic in Python is FORBIDDEN (spec); Python only orchestrates.
- rustc gotcha for frozen artifacts: needs `--edition 2021` and a dot-free source filename (copy `X.min.rs` to `$W/cc.rs` first).
- Every commit message ends with the trailer line: `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- equality.rs's observable behavior must be preserved exactly (it is the project's reference instrument).

---

### Task 1: Extract the game driver into `src/game/driver.rs` (behavior-preserving)

**Files:**
- Create: `rust/src/game/driver.rs`
- Modify: `rust/src/game/mod.rs` (add one line: `pub mod driver;`)
- Modify: `rust/src/bin/equality.rs` (delete moved code, import from the lib; `main()` unchanged)

**Interfaces:**
- Consumes: `crate::game::engine::step`, `crate::game::mapgen::generate_bronze`, `crate::game::state::GameState` (all existing).
- Produces (used by Task 2/3 and by equality.rs): `pub struct Bot { pub child: Child }` with `pub fn spawn(path: &str) -> Bot`, `pub fn send(&mut self, s: &str) -> std::io::Result<()>`; `pub fn grid_rows(g: &GameState, seat: usize) -> Vec<String>`; `pub fn turn_block(g: &GameState, seat: usize) -> String`; `pub fn read_cmds(reader: &mut BufReader<ChildStdout>) -> Option<String>`; `pub fn play(bot_path: &str, opp_path: &str, seed: u64, seat: usize, max_turns: i32) -> Vec<String>`.

The move is verbatim except ONE deliberate change: `Bot::send` returns `io::Result<()>` instead of unwrapping internally (Task 2 needs fallible sends for crash flagging). All existing call sites append `.unwrap()`, preserving the old panic-on-error behavior exactly.

- [ ] **Step 1: Create `rust/src/game/driver.rs`** with this exact content (bodies of `grid_rows`, `turn_block`, `read_cmds`, `play` are the current `equality.rs` code moved verbatim; only the `use` paths change to `crate::` and `send` gains the `Result` return):

```rust
//! Shared black-box game driver: spawns bot BINARIES and speaks the CG stdin/stdout
//! protocol over simulated games (real `engine::step`, real `generate_bronze` maps).
//! Consumers: bin/equality.rs (exactness assertions), bin/playmatch.rs (scored matches).
//! Extracted verbatim from bin/equality.rs on 2026-07-11 (see that file's doc comment
//! for the protocol description). One deliberate change: `Bot::send` is fallible so a
//! crashed bot can be FLAGGED instead of panicking (equality call sites `.unwrap()`).

use std::io::{BufRead, BufReader, Write};
use std::process::{Child, ChildStdout, Command, Stdio};

use crate::game::engine::step;
use crate::game::mapgen::generate_bronze;
use crate::game::state::GameState;

pub struct Bot {
    pub child: Child,
}

impl Bot {
    pub fn spawn(path: &str) -> Bot {
        let child = Command::new(path)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::null())
            .spawn()
            .unwrap_or_else(|e| panic!("cannot spawn bot {path}: {e}"));
        Bot { child }
    }
    pub fn send(&mut self, s: &str) -> std::io::Result<()> {
        let stdin = self.child.stdin.as_mut().unwrap();
        stdin.write_all(s.as_bytes())?;
        stdin.flush()
    }
}

impl Drop for Bot {
    fn drop(&mut self) {
        let _ = self.child.kill();
        let _ = self.child.wait();
    }
}

pub fn grid_rows(g: &GameState, seat: usize) -> Vec<String> {
    // ... EXACT body of the current equality.rs grid_rows (lines 54-76) ...
}

pub fn turn_block(g: &GameState, seat: usize) -> String {
    // ... EXACT body of the current equality.rs turn_block (lines 78-119) ...
}

/// Read one command line from a bot; None = crash/EOF.
pub fn read_cmds(reader: &mut BufReader<ChildStdout>) -> Option<String> {
    // ... EXACT body of the current equality.rs read_cmds (lines 122-129) ...
}

/// Play one game: `bot_path` in `seat`; opponent = another binary or the scripted "WAIT"
/// bot. Returns the bot's per-turn command lines (empty line marks a read failure).
/// (Equality semantics — verbatim from equality.rs `play`, lines 136-183, with the four
/// internal `send` calls suffixed `.unwrap()`.)
pub fn play(bot_path: &str, opp_path: &str, seed: u64, seat: usize, max_turns: i32) -> Vec<String> {
    // ... EXACT body, with `bot.send(...)` -> `bot.send(...).unwrap();`
    //     and `o.send(...)` -> `o.send(...).unwrap();` (4 sites total) ...
}
```

(The implementer copies the four function bodies from `rust/src/bin/equality.rs` as-is; do not re-type them.)

- [ ] **Step 2: Register the module.** In `rust/src/game/mod.rs` add the line `pub mod driver;` next to the existing `pub mod engine;` etc.

- [ ] **Step 3: Shrink `rust/src/bin/equality.rs`.** Delete the moved items (`Bot`, `grid_rows`, `turn_block`, `read_cmds`, `play`, and the now-unused `use` lines for `step`/`generate_bronze`/`GameState`/process/io imports). Keep the file's doc comment and `main()` untouched, and add:

```rust
use troll_farm::game::driver::play;
```

- [ ] **Step 4: Build + full suite**

Run (from `rust/`): `cargo build --release && cargo test --release`
Expected: `Finished release`, all suites green (same count as before the change).

- [ ] **Step 5: Equality smoke on a real binary (proves the harness end-to-end post-refactor)**

```bash
W=$(mktemp -d); cp /home/tarstars/prj/troll_farm/cgauto/submissions/v1.59.0-ringfix3.min.rs $W/cc.rs
rustc --edition 2021 -O $W/cc.rs -o $W/champ && echo BUILT
cd /home/tarstars/prj/troll_farm/rust
cargo run --release --bin equality -- $W/champ $W/champ 25
```
Expected: last line `EQUAL: 50 games (25 seeds x 2 seats), all command streams identical`.

- [ ] **Step 6: Commit**

```bash
git add rust/src/game/driver.rs rust/src/game/mod.rs rust/src/bin/equality.rs
git commit -m "refactor(driver): extract equality's game driver into game::driver (verbatim; send now fallible, call sites unwrap)"
```

---

### Task 2: `driver::play_match` — one scored two-binary match

**Files:**
- Modify: `rust/src/game/driver.rs` (append)
- Test: `rust/tests/driver_match.rs` (new)

**Interfaces:**
- Consumes: Task 1's `Bot`, `grid_rows`, `turn_block`, `read_cmds`; `crate::game::engine::{recompute_scores, WOOD}`.
- Produces (used by Task 3): `pub struct MatchResult { pub turns: i32, pub scores: [i32; 2], pub fruit: [i32; 2], pub wood: [i32; 2], pub crashed: [bool; 2] }` and `pub fn play_match(bot0_path: &str, bot1_path: &str, seed: u64, max_turns: i32) -> MatchResult` (`"WAIT"` as either path = scripted do-nothing side, no process).

- [ ] **Step 1: Write the failing test** — `rust/tests/driver_match.rs`:

```rust
use troll_farm::game::driver::play_match;

#[test]
fn wait_vs_wait_full_run_scores_starting_inventory() {
    // Nobody acts: game runs all turns (plants never chopped away); score = starting
    // inventory = 4+2+2+8 fruit + 0 wood = 16 for both sides; no crashes.
    let r = play_match("WAIT", "WAIT", 1, 40);
    assert_eq!(r.turns, 40);
    assert_eq!(r.scores, [16, 16]);
    assert_eq!(r.fruit, [16, 16]);
    assert_eq!(r.wood, [0, 0]);
    assert_eq!(r.crashed, [false, false]);
    // deterministic: same seed twice, identical result
    let r2 = play_match("WAIT", "WAIT", 1, 40);
    assert_eq!((r.scores, r.turns), (r2.scores, r2.turns));
}

#[test]
fn crashed_side_is_flagged_and_plays_wait() {
    // /bin/false exits immediately -> EOF/broken pipe on first exchange -> crash flag,
    // game still completes with that side WAITing.
    let r = play_match("/bin/false", "WAIT", 2, 10);
    assert!(r.crashed[0]);
    assert!(!r.crashed[1]);
    assert_eq!(r.turns, 10);
    assert_eq!(r.scores, [16, 16]); // nobody acted
}
```

- [ ] **Step 2: Run to verify failure**

Run (from `rust/`): `cargo test --release --test driver_match`
Expected: COMPILE ERROR — `play_match` / `MatchResult` not found.

- [ ] **Step 3: Implement** — append to `rust/src/game/driver.rs`:

```rust
use crate::game::engine::{recompute_scores, WOOD};

pub struct MatchResult {
    pub turns: i32,
    pub scores: [i32; 2],
    pub fruit: [i32; 2],
    pub wood: [i32; 2],
    pub crashed: [bool; 2],
}

struct Side {
    bot: Option<Bot>,
    reader: Option<BufReader<ChildStdout>>,
    crashed: bool,
}

/// One scored match on `generate_bronze(seed)`: bot0 = player 0, bot1 = player 1.
/// "WAIT" = scripted do-nothing side. A side that crashes (send/read failure) plays
/// WAIT for the remainder and is FLAGGED. Early end when no plants remain (mirrors the
/// referee, same rule as `play`).
pub fn play_match(bot0_path: &str, bot1_path: &str, seed: u64, max_turns: i32) -> MatchResult {
    let mut g = generate_bronze(seed);
    let mut sides: Vec<Side> = Vec::new();
    for (i, path) in [bot0_path, bot1_path].iter().enumerate() {
        if *path == "WAIT" {
            sides.push(Side { bot: None, reader: None, crashed: false });
        } else {
            let mut b = Bot::spawn(path);
            let rows = grid_rows(&g, i);
            let header_ok = b
                .send(&format!("{} {}\n{}\n", g.width, g.height, rows.join("\n")))
                .is_ok();
            let reader = BufReader::new(b.child.stdout.take().unwrap());
            sides.push(Side { bot: Some(b), reader: Some(reader), crashed: !header_ok });
        }
    }
    let mut turns = 0;
    for _ in 0..max_turns {
        let mut cmds: [Vec<String>; 2] = [vec!["WAIT".to_string()], vec!["WAIT".to_string()]];
        for i in 0..2 {
            let blk = turn_block(&g, i);
            let side = &mut sides[i];
            if side.crashed || side.bot.is_none() {
                continue;
            }
            if side.bot.as_mut().unwrap().send(&blk).is_err() {
                side.crashed = true;
                continue;
            }
            match read_cmds(side.reader.as_mut().unwrap()) {
                Some(l) => cmds[i] = l.split(';').map(|s| s.to_string()).collect(),
                None => side.crashed = true,
            }
        }
        step(&mut g, &cmds[0], &cmds[1]);
        turns += 1;
        if g.plants.is_empty() {
            break;
        }
    }
    recompute_scores(&mut g);
    let fruit = |p: usize| {
        let inv = &g.inventories[p];
        inv[0] + inv[1] + inv[2] + inv[3]
    };
    MatchResult {
        turns,
        scores: [g.scores[0], g.scores[1]],
        fruit: [fruit(0), fruit(1)],
        wood: [g.inventories[0][WOOD], g.inventories[1][WOOD]],
        crashed: [sides[0].crashed, sides[1].crashed],
    }
}
```

- [ ] **Step 4: Run tests**

Run: `cargo test --release --test driver_match`
Expected: `2 passed`. Then full suite: `cargo test --release` — all green.

- [ ] **Step 5: Commit**

```bash
git add rust/src/game/driver.rs rust/tests/driver_match.rs
git commit -m "feat(driver): play_match — one scored two-binary match with crash flagging (WAIT pseudo-bot supported)"
```

---

### Task 3: `playmatch` bin — machine-readable one-line result

**Files:**
- Create: `rust/src/bin/playmatch.rs`

**Interfaces:**
- Consumes: `troll_farm::game::driver::play_match` (Task 2).
- Produces (consumed by Task 4/5's Python): stdout line, space-separated, exactly:
  `seed turns score0 score1 fruit0 wood0 fruit1 wood1 crash0 crash1` (crash as 0/1). Exit 0 on a played match; exit 2 on usage error.

- [ ] **Step 1: Create `rust/src/bin/playmatch.rs`:**

```rust
//! One scored A/B match between two bot binaries on a seeded generated map.
//! usage: playmatch <bot0|WAIT> <bot1|WAIT> <seed> [max_turns=300]
//! stdout (ONE line, versioned interface consumed by cgauto/abgate.py):
//!   seed turns score0 score1 fruit0 wood0 fruit1 wood1 crash0 crash1

use troll_farm::game::driver::play_match;

fn main() {
    let a: Vec<String> = std::env::args().collect();
    if a.len() < 4 {
        eprintln!("usage: playmatch <bot0|WAIT> <bot1|WAIT> <seed> [max_turns=300]");
        std::process::exit(2);
    }
    let seed: u64 = a[3].parse().expect("seed must be a u64");
    let max_turns: i32 = a.get(4).map(|s| s.parse().expect("max_turns")).unwrap_or(300);
    let r = play_match(&a[1], &a[2], seed, max_turns);
    println!(
        "{} {} {} {} {} {} {} {} {} {}",
        seed,
        r.turns,
        r.scores[0],
        r.scores[1],
        r.fruit[0],
        r.wood[0],
        r.fruit[1],
        r.wood[1],
        r.crashed[0] as u8,
        r.crashed[1] as u8
    );
}
```

- [ ] **Step 2: Verify exact output**

Run (from `rust/`): `cargo run --release --bin playmatch -- WAIT WAIT 1 40`
Expected stdout: `1 40 16 16 16 0 16 0 0 0`

- [ ] **Step 3: Commit**

```bash
git add rust/src/bin/playmatch.rs
git commit -m "feat(playmatch): thin bin — one scored match, one machine-readable line"
```

---

### Task 4: `cgauto/abgate.py` — paired stats core with `--check-stats`

**Files:**
- Create: `cgauto/abgate.py`

**Interfaces:**
- Produces (used within this file by Task 5): `pair_rows(g_a: dict, g_b: dict) -> dict` (candidate-centric per-pair numbers), `paired_stats(pairs: list[dict]) -> dict`, `verdict(st: dict) -> str` returning one of `"REJECT" | "PASS-TO-ARENA" | "INVALID"`.
- Convention: in game A the candidate is bot0; in game B (seats swapped) the candidate is bot1. `run_playmatch` row keys: `seed turns score0 score1 fruit0 wood0 fruit1 wood1 crash0 crash1` (all int).

- [ ] **Step 1: Create `cgauto/abgate.py`** with the stats core and a self-checking fixture mode (`--check-stats` is the test — written to fail until the functions exist; run it before filling the bodies if you want the RED step literally, then implement):

```python
#!/usr/bin/env python3
"""Paired self-play A/B gate — REJECT filter before the arena (never an accepter).
Spec: docs/superpowers/specs/2026-07-11-selfplay-gate-design.md

usage (from repo root):
  uv run --no-sync python cgauto/abgate.py CAND_BIN CHAMP_BIN [--seeds 200]
      [--max-turns 300] [--jobs 1] [--playmatch rust/target/release/playmatch]
      [--csv PATH]
  uv run --no-sync python cgauto/abgate.py --selftest BOT_BIN   # 5 seeds, pair delta == 0
  uv run --no-sync python cgauto/abgate.py --check-stats        # pure stats self-test

Verdict: REJECT if CI95 entirely < 0 OR the candidate crashed in any game;
PASS-TO-ARENA otherwise. Champion crash => INVALID (harness problem, exit 2).
Exit codes: 0 PASS, 1 REJECT, 2 INVALID/usage.
"""
import argparse
import csv
import math
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIELDS = ["seed", "turns", "score0", "score1", "fruit0", "wood0", "fruit1", "wood1", "crash0", "crash1"]


def run_playmatch(playmatch, bot0, bot1, seed, max_turns):
    out = subprocess.run(
        [playmatch, bot0, bot1, str(seed), str(max_turns)],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        raise RuntimeError(f"playmatch failed (seed={seed}): {out.stderr.strip()}")
    parts = out.stdout.split()
    if len(parts) != len(FIELDS):
        raise RuntimeError(f"bad playmatch line (seed={seed}): {out.stdout!r}")
    return dict(zip(FIELDS, map(int, parts)))


def pair_rows(g_a, g_b):
    """Candidate-centric per-pair numbers. Game A: candidate=bot0; game B: candidate=bot1."""
    d_a = g_a["score0"] - g_a["score1"]
    d_b = g_b["score1"] - g_b["score0"]
    return {
        "delta": (d_a + d_b) / 2.0,
        "wood_delta": ((g_a["wood0"] - g_a["wood1"]) + (g_b["wood1"] - g_b["wood0"])) / 2.0,
        "fruit_delta": ((g_a["fruit0"] - g_a["fruit1"]) + (g_b["fruit1"] - g_b["fruit0"])) / 2.0,
        "wins": int(d_a > 0) + int(d_b > 0),
        "draws": int(d_a == 0) + int(d_b == 0),
        "losses": int(d_a < 0) + int(d_b < 0),
        "cand_crash": bool(g_a["crash0"] or g_b["crash1"]),
        "champ_crash": bool(g_a["crash1"] or g_b["crash0"]),
    }


def paired_stats(pairs):
    n = len(pairs)
    deltas = [p["delta"] for p in pairs]
    mean = sum(deltas) / n
    var = sum((d - mean) ** 2 for d in deltas) / (n - 1) if n > 1 else 0.0
    sd = math.sqrt(var)
    ci = 1.96 * sd / math.sqrt(n)
    return {
        "n": n, "mean": mean, "sd": sd, "ci_lo": mean - ci, "ci_hi": mean + ci,
        "wins": sum(p["wins"] for p in pairs),
        "draws": sum(p["draws"] for p in pairs),
        "losses": sum(p["losses"] for p in pairs),
        "wood": sum(p["wood_delta"] for p in pairs) / n,
        "fruit": sum(p["fruit_delta"] for p in pairs) / n,
        "cand_crashes": sum(p["cand_crash"] for p in pairs),
        "champ_crashes": sum(p["champ_crash"] for p in pairs),
    }


def verdict(st):
    if st["champ_crashes"]:
        return "INVALID"
    if st["cand_crashes"]:
        return "REJECT"
    if st["ci_hi"] < 0:
        return "REJECT"
    return "PASS-TO-ARENA"


def check_stats():
    """Pure self-test on synthetic rows; hand-computed expectations. Exits non-zero on failure."""
    mk = lambda s0, s1, w0, w1, f0, f1, c0=0, c1=0: {
        "seed": 0, "turns": 300, "score0": s0, "score1": s1,
        "fruit0": f0, "wood0": w0, "fruit1": f1, "wood1": w1, "crash0": c0, "crash1": c1,
    }
    # pair 1: candidate wins both seatings by 8 -> delta 8
    p1 = pair_rows(mk(20, 12, 4, 2, 4, 4), mk(12, 20, 2, 4, 4, 4))
    assert p1["delta"] == 8.0 and p1["wins"] == 2 and p1["losses"] == 0, p1
    assert p1["wood_delta"] == 2.0 and p1["fruit_delta"] == 0.0, p1
    # pair 2: candidate loses both by 4 -> delta -4
    p2 = pair_rows(mk(10, 14, 1, 2, 6, 6), mk(14, 10, 2, 1, 6, 6))
    assert p2["delta"] == -4.0 and p2["losses"] == 2, p2
    # pair 3: split 6 / -6 -> delta 0, one win one loss
    p3 = pair_rows(mk(22, 16, 3, 3, 10, 4), mk(22, 16, 3, 3, 10, 4))
    assert p3["delta"] == 0.0 and p3["wins"] == 1 and p3["losses"] == 1, p3
    st = paired_stats([p1, p2, p3])
    assert st["n"] == 3 and abs(st["mean"] - (8 - 4 + 0) / 3.0) < 1e-9, st
    assert st["wins"] == 3 and st["losses"] == 3 and st["draws"] == 0, st
    assert verdict(st) == "PASS-TO-ARENA", st
    # crash semantics
    pc = pair_rows(mk(20, 12, 4, 2, 4, 4, c0=1), mk(12, 20, 2, 4, 4, 4))
    stc = paired_stats([pc])
    assert stc["cand_crashes"] == 1 and verdict(stc) == "REJECT", stc
    pch = pair_rows(mk(20, 12, 4, 2, 4, 4, c1=1), mk(12, 20, 2, 4, 4, 4))
    assert verdict(paired_stats([pch])) == "INVALID"
    # clearly-negative CI
    neg = [dict(p2, delta=p2["delta"] + i * 0.01) for i in range(30)]
    assert verdict(paired_stats(neg)) == "REJECT"
    print("check-stats: ALL OK")
```

- [ ] **Step 2: Run the stats self-test**

Run (from repo root): `uv run --no-sync python cgauto/abgate.py --check-stats`
(Temporarily wire a minimal `if __name__ == "__main__":` that calls `check_stats()` when `--check-stats` is the only arg — Task 5 replaces it with the full CLI.)
Expected: `check-stats: ALL OK`

- [ ] **Step 3: Commit**

```bash
git add cgauto/abgate.py
git commit -m "feat(abgate): paired stats core (pair_rows/paired_stats/verdict) + --check-stats self-test"
```

---

### Task 5: `abgate.py` orchestration — pairs, CSV, `--selftest`, `--jobs`, full CLI

**Files:**
- Modify: `cgauto/abgate.py` (append orchestration + replace the temporary main)

**Interfaces:**
- Consumes: Task 3's `playmatch` binary (default path `rust/target/release/playmatch` relative to repo root) and Task 4's functions.
- Produces: the gate CLI (spec §What-it-is), CSV rows (one per GAME): `seed,cand_seat,turns,cand_score,champ_score,cand_fruit,cand_wood,champ_fruit,champ_wood,cand_crash,champ_crash` under `data/abgate/` by default.

- [ ] **Step 1: Append orchestration + full main:**

```python
def play_pair(job):
    """Top-level for ProcessPoolExecutor picklability."""
    playmatch, cand, champ, seed, max_turns = job
    g_a = run_playmatch(playmatch, cand, champ, seed, max_turns)  # candidate = bot0
    g_b = run_playmatch(playmatch, champ, cand, seed, max_turns)  # candidate = bot1
    return seed, g_a, g_b


def csv_rows_for(seed, g_a, g_b):
    return [
        {"seed": seed, "cand_seat": 0, "turns": g_a["turns"],
         "cand_score": g_a["score0"], "champ_score": g_a["score1"],
         "cand_fruit": g_a["fruit0"], "cand_wood": g_a["wood0"],
         "champ_fruit": g_a["fruit1"], "champ_wood": g_a["wood1"],
         "cand_crash": g_a["crash0"], "champ_crash": g_a["crash1"]},
        {"seed": seed, "cand_seat": 1, "turns": g_b["turns"],
         "cand_score": g_b["score1"], "champ_score": g_b["score0"],
         "cand_fruit": g_b["fruit1"], "cand_wood": g_b["wood1"],
         "champ_fruit": g_b["fruit0"], "champ_wood": g_b["wood0"],
         "cand_crash": g_b["crash1"], "champ_crash": g_b["crash0"]},
    ]


def run_gate(cand, champ, seeds, max_turns, jobs, playmatch, csv_path):
    jobs_list = [(playmatch, cand, champ, s, max_turns) for s in range(seeds)]
    t0 = time.time()
    if jobs > 1:
        with ProcessPoolExecutor(max_workers=jobs) as ex:
            results = list(ex.map(play_pair, jobs_list))
    else:
        results = [play_pair(j) for j in jobs_list]
    results.sort(key=lambda r: r[0])  # deterministic order regardless of jobs
    pairs, rows = [], []
    for seed, g_a, g_b in results:
        pairs.append(pair_rows(g_a, g_b))
        rows.extend(csv_rows_for(seed, g_a, g_b))
    st = paired_stats(pairs)
    v = verdict(st)
    if csv_path:
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        with open(csv_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    dt = time.time() - t0
    print(f"abgate: {st['n']} pairs ({st['n']*2} games) in {dt:.0f}s "
          f"| cand={os.path.basename(cand)} champ={os.path.basename(champ)}")
    print(f"  pair delta mean {st['mean']:+.2f}  sd {st['sd']:.2f}  "
          f"CI95 [{st['ci_lo']:+.2f}, {st['ci_hi']:+.2f}]")
    print(f"  W/D/L {st['wins']}/{st['draws']}/{st['losses']}  "
          f"wood {st['wood']:+.2f}  fruit {st['fruit']:+.2f}  "
          f"crashes cand={st['cand_crashes']} champ={st['champ_crashes']}")
    if csv_path:
        print(f"  csv: {csv_path}")
    print(f"GATE: {v}")
    return v


def selftest(bot, max_turns, playmatch):
    """Same binary both roles: the swapped game is the identical matchup with labels
    exchanged, so pair delta must be EXACTLY 0 for every seed."""
    for seed in range(5):
        g_a = run_playmatch(playmatch, bot, bot, seed, max_turns)
        g_b = run_playmatch(playmatch, bot, bot, seed, max_turns)
        p = pair_rows(g_a, g_b)
        assert p["delta"] == 0.0, (seed, p, g_a, g_b)
        print(f"  seed {seed}: pair delta 0.0 OK (scores {g_a['score0']}-{g_a['score1']})")
    print("selftest: ALL OK (pair delta exactly 0 on 5 seeds)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bots", nargs="*", help="CAND_BIN CHAMP_BIN (or BOT_BIN with --selftest)")
    ap.add_argument("--seeds", type=int, default=200)
    ap.add_argument("--max-turns", type=int, default=300)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--playmatch", default=os.path.join(REPO, "rust/target/release/playmatch"))
    ap.add_argument("--csv", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check-stats", action="store_true")
    a = ap.parse_args()
    if a.check_stats:
        check_stats()
        return 0
    if not os.path.exists(a.playmatch):
        sys.exit(f"playmatch not found at {a.playmatch} — build it: "
                 f"cd rust && cargo build --release --bin playmatch")
    if a.selftest:
        if len(a.bots) != 1:
            sys.exit("--selftest needs exactly one BOT_BIN (or WAIT)")
        selftest(a.bots[0], a.max_turns, a.playmatch)
        return 0
    if len(a.bots) != 2:
        ap.print_help()
        return 2
    cand, champ = a.bots
    csv_path = a.csv
    if csv_path is None:
        ts = time.strftime("%Y%m%d-%H%M%S")
        csv_path = os.path.join(REPO, "data/abgate",
                                f"{ts}_{os.path.basename(cand)}_vs_{os.path.basename(champ)}.csv")
    v = run_gate(cand, champ, a.seeds, a.max_turns, a.jobs, a.playmatch, csv_path)
    return {"PASS-TO-ARENA": 0, "REJECT": 1, "INVALID": 2}[v]


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: WAIT selftest (no bot binaries needed)**

Run: `uv run --no-sync python cgauto/abgate.py --selftest WAIT --max-turns 40`
Expected: 5 × `pair delta 0.0 OK (scores 16-16)` then `selftest: ALL OK`.

- [ ] **Step 3: Real-binary selftest (champion vs itself — proves determinism end to end)**

```bash
W=$(mktemp -d); cp cgauto/submissions/v1.59.0-ringfix3.min.rs $W/cc.rs
rustc --edition 2021 -O $W/cc.rs -o $W/champ
uv run --no-sync python cgauto/abgate.py --selftest $W/champ
```
Expected: 5 × `pair delta 0.0 OK` (non-trivial scores), `selftest: ALL OK`. If a nonzero
delta appears, the bot is nondeterministic — STOP and report (this is itself a finding).

- [ ] **Step 4: Jobs equivalence check**

Run a tiny real gate twice: `uv run --no-sync python cgauto/abgate.py $W/champ $W/champ --seeds 6 --jobs 1 --csv /tmp/j1.csv` and again with `--jobs 4 --csv /tmp/j4.csv`.
Expected: both print `GATE: PASS-TO-ARENA` with `pair delta mean +0.00`; `diff /tmp/j1.csv /tmp/j4.csv` → no differences.

- [ ] **Step 5: Commit**

```bash
git add cgauto/abgate.py
git commit -m "feat(abgate): full gate CLI — seat-swap pairs, CSV, --selftest (exact-zero invariant), --jobs"
```

---

### Task 6: Calibration study — the gate's own acceptance test

**Files:**
- Create: `cgauto/abgate_calibrate.sh`
- Modify: `docs/superpowers/specs/2026-07-11-selfplay-gate-design.md` (append results table)
- Modify: `docs/silver-experiment-log.md` (append calibration entry)
- Modify: `docs/arena-queue.md` (process note: abgate = standard pre-arena REJECT filter, if accepted)

**Interfaces:**
- Consumes: Task 5's CLI; frozen artifacts in `cgauto/submissions/` (read-only).
- Produces: recorded calibration verdict; adoption decision.

- [ ] **Step 1: Verify all six frozen artifacts exist**

Run: `ls cgauto/submissions/v1.56.0-ringfarm.min.rs cgauto/submissions/v1.59.0-ringfix3.min.rs cgauto/submissions/v1.57.0-ringtune.min.rs cgauto/submissions/v1.58.0-trainfruit.min.rs cgauto/submissions/v1.60.0-fellmission.min.rs cgauto/submissions/v1.61.0-chopharvest.min.rs`
Expected: all six listed. If `v1.60.0-fellmission.min.rs` is missing, copy it from `data/candidates/v1.60.0-fellmission/`; if any other is missing, STOP and report.

- [ ] **Step 2: Create `cgauto/abgate_calibrate.sh`:**

```bash
#!/bin/bash
# Calibration study for the abgate self-play gate (spec acceptance test):
# 5 candidate-vs-base pairs with KNOWN arena verdicts. usage: abgate_calibrate.sh [seeds] [jobs]
set -u
cd "$(dirname "$0")/.."
N=${1:-200}; J=${2:-4}
B=rust/target/abgate-bins; mkdir -p "$B" data/abgate

build() { # build <name> <min.rs>
  local W; W=$(mktemp -d); cp "$2" "$W/cc.rs"
  rustc --edition 2021 -O "$W/cc.rs" -o "$B/$1" || { echo "BUILD FAILED: $1"; exit 3; }
  echo "built $1"
}
build ringfarm    cgauto/submissions/v1.56.0-ringfarm.min.rs
build ringfix3    cgauto/submissions/v1.59.0-ringfix3.min.rs
build ringtune    cgauto/submissions/v1.57.0-ringtune.min.rs
build trainfruit  cgauto/submissions/v1.58.0-trainfruit.min.rs
build fellmission cgauto/submissions/v1.60.0-fellmission.min.rs
build chopharvest cgauto/submissions/v1.61.0-chopharvest.min.rs

G="uv run --no-sync python cgauto/abgate.py"
run() { # run <cand> <base> <arena_known>
  echo "=== $1 vs $2 (arena: $3) ==="
  $G "$B/$1" "$B/$2" --seeds "$N" --jobs "$J" --csv "data/abgate/cal_$1.csv" \
    | tee "data/abgate/cal_$1.txt"
}
run ringfix3    ringfarm  "+1.1 KEEP"
run ringtune    ringfarm  "-2.4 REVERT"
run trainfruit  ringfarm  "-3.2 REVERT"
run fellmission ringfix3  "-1.0 REVERT"
run chopharvest ringfix3  "-5.0 REVERT"
echo "calibration done — record the table in the spec + silver log"
```

Then: `chmod +x cgauto/abgate_calibrate.sh`

- [ ] **Step 3: Timing probe before the full run**

Run: `bash cgauto/abgate_calibrate.sh 10 4` and note the per-pair `in N s` lines.
Expected: builds succeed, 5 mini-runs complete. Project the full time: `(seconds for 10 seeds) × 20 × 5 pairs`. If the projection exceeds ~60 min, use `--jobs 8` (rerun step 4 with `200 8`).

- [ ] **Step 4: Full calibration run**

Run: `bash cgauto/abgate_calibrate.sh 200 4` (or `200 8` per step 3).
Expected: five result blocks, each ending `GATE: ...`.

- [ ] **Step 5: Record + decide.** Append to the spec doc a results table:

```markdown
## Calibration results (2026-07-11, n=200 pairs each)
| pair | arena (known) | gate delta [CI95] | gate verdict | sign agrees? |
|---|---|---|---|---|
| ringfix3 vs ringfarm | +1.1 | <mean> [<lo>,<hi>] | <verdict> | yes/no |
| ringtune vs ringfarm | −2.4 | ... | ... | ... |
| trainfruit vs ringfarm | −3.2 | ... | ... | ... |
| fellmission vs ringfix3 | −1.0 | ... | ... | ... |
| chopharvest vs ringfix3 | −5.0 | ... | ... | ... |
```
filled with the real numbers (no placeholders left). Acceptance per spec: ≥4/5 sign
agreement AND ringtune+trainfruit+chopharvest all REJECTed. Append the same summary +
verdict to `docs/silver-experiment-log.md`. If ACCEPTED: add the process note to
`docs/arena-queue.md` ("every candidate runs abgate before submission; REJECT = do not
submit; PASS = proceed to boss/field/arena as before") and set the numeric REJECT
threshold in the spec from the observed spread. If NOT accepted: record which pair
slipped through, do NOT wire into the process, and STOP — the escalation (frozen-pool
variant) is a user decision.

- [ ] **Step 6: Commit**

```bash
git add cgauto/abgate_calibrate.sh data/abgate/cal_*.txt docs/superpowers/specs/2026-07-11-selfplay-gate-design.md docs/silver-experiment-log.md docs/arena-queue.md
git commit -m "feat(abgate): calibration study vs 5 known arena verdicts — results + adoption decision"
```

---

## Self-review notes (done at write time)

- Spec coverage: driver extraction (T1), playmatch line format (T3 = spec's field list), seat-swap pairing + candidate-centric deltas (T4/T5), exact-zero selftest (T5), crash semantics REJECT/INVALID (T4 `verdict`), CSV corpus (T5), calibration + acceptance + process wiring (T6), equality re-validation (T1 step 5). `--jobs` is an addition justified by the 2000-game calibration volume; default remains 1.
- Type consistency: `MatchResult` fields ↔ playmatch print order ↔ Python `FIELDS` ↔ `pair_rows` keys all match the same 10-field line.
- No placeholders except the calibration results table, which Task 6 step 5 explicitly requires filling with real numbers before commit.
