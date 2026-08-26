#!/usr/bin/env python3
"""Generate Candidate 3b's ONE source — Candidate 3 plus the stuck-holder release (rule iii).

Task `20260826-candidate-3b-stuck-holder-release` (board row D-4), chartered by the owner at
2026-08-26T15:45Z. Pre-commitments are in the card and were written before this file existed.

Candidate 3b is Candidate 3 **plus one release cause** and nothing else. This generator therefore
does not copy Candidate 3's source: it imports `claude_1/cure3/make_cure3_source.py`, builds that
exact text through `build_text`, verifies it against the recorded sha, and then applies five more
anchored replacements. If Candidate 3's source ever moves, this script stops instead of producing
a plausible file — the same fail-closed stance as its parent.

**The rule, from D-3's read §4(d)** (`claude_1/cure3/m061-stale-goal-read-2026-08-26.md`): a kept
goal is released when its holder has occupied at most **2 distinct cells over the last 20
consecutive turns** and emitted **no work command** in any of them, where work is
`CHOP`/`HARVEST`/`DROP`/`PLANT`/`PICK`. Release reason `rs=`, counted on the wire like every other
cause. No margin, no turn cap, no other change.

**Why five verbs and not the four the charter's summary line lists.** `HARVEST` is a real verb of
this game and is in the work set of the probe that produced every number the charter quotes
(`claude_1/cure3/m061/fixprobe.py:32`). Measured on the same archive before this file was written
(`claude_1/cure3/m061/workset-split.json`): the five-verb rule cuts 6 runs in 6 games and removes
58 work commands, reproducing the charter exactly; the four-verb reading cuts 9 runs in 9 games
and removes 96 — 38 more productive commands, from trolls that were harvesting. The four-verb
reading is a summary slip, not a different rule.

**The wire is v7, not v6.** A fifth release cause breaks v6's census equation
`rd + rg + ri + rx + xc == kr`, so the payload gets its own version and its own decoder
(`claude_1/narrate7/narrate7.py`). `claude_1/narrate6/narrate6.py` is left untouched, which is
what keeps the arm already on the ladder (0-3a, submission `41198581`) decodable by the decoder it
shipped with, and keeps the two version-refusal controls symmetric.

Three arms come from this one file and ONE flag line (`build_arms3b.py`):

  instrument  KEEP=true  NARRATE=true  STUCK=true   the panel read
  candidate   KEEP=true  NARRATE=false STUCK=true   the score block, and the ladder on a pass
  ruleoff     KEEP=false NARRATE=true  STUCK=false  the containment reference

    python3 claude_1/cure3b/make_cure3b_source.py
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "cure3"))

import make_cure3_source as P  # noqa: E402

# Candidate 3's source as this generator was written against. Not a guess: regenerate with
# `python3 claude_1/cure3/make_cure3_source.py` and compare.
PARENT_SHA = "01b61444a109c1d190fba5b0a103c861c6f9e772596e97cf9042b9b2c516b3b3"
OUT = HERE / "cure3b-keep-v7.rs"

GenError = P.GenError
replace_once = P.replace_once

# ------------------------------------------------------------------------- 1. the flag line
# One line, now three flags. `build_arms3b.py` rewrites exactly this line and checks that the arm
# differs from the source by exactly one line, so "one source and a compile-time flag" stays a
# property of the bytes.
FLAG_OLD = ("            const KEEP_RULE_ENABLED: bool = true;"
            " const NARRATE_V6_ENABLED: bool = true;\n")
FLAG_NEW = ('''            // ------------------------------------------------------------- Candidate 3b
            // Task 20260826-candidate-3b-stuck-holder-release, owner-chartered 15:45Z.
            // `STUCK_RELEASE_ENABLED` adds ONE release cause to R5(a) -- rule iii of D-3's read
            // §4(d) -- and changes nothing else. The two window constants below are the rule as
            // measured; they are not knobs and no other value was tried.
            const KEEP_RULE_ENABLED: bool = true; const NARRATE_V6_ENABLED: bool = true; const STUCK_RELEASE_ENABLED: bool = true;
            // 20 turns, at most 2 distinct cells, no work command in the window.
            const STUCK_WINDOW: i32 = 20;
            const STUCK_CELLS: usize = 2;
            // The work set of D-3's probe (`fixprobe.py:32`), verbatim. A holder that swung an
            // axe or moved fruit inside the window is working, not stuck, however little it moved.
            const STUCK_WORK: [&'static str; 5] = ["CHOP", "HARVEST", "DROP", "PLANT", "PICK"];
''')

# ------------------------------------------------------------------------ 2. the `rs` counter
META_OLD = "        struct KeepMeta {\n            kp: u32,\n"
META_NEW = '''        struct KeepMeta {
            // Candidate 3b: releases by rule iii (stuck holder). Counted into `kr` like every
            // other cause, which is why v7's census equation carries an `rs` term and v6's
            // cannot. Identically 0 in an arm with `STUCK_RELEASE_ENABLED = false`.
            rs: u32,
            kp: u32,
'''

# --------------------------------------------------------- 3. the per-unit movement/work trace
# Stored with the turn number on every entry. A "last 20 turns" test that reads the last 20
# *entries* silently widens its own window whenever a unit emitted nothing on some turn; this one
# checks that the entries are turns `t-20 .. t-1` with no gap, and declines to fire otherwise.
STATE_OLD = "            last_cell: BTreeMap<i32, Cell>,\n        }\n"
STATE_NEW = '''            last_cell: BTreeMap<i32, Cell>,
            // Candidate 3b: (turn, cell, worked) per own troll, most recent last, at most
            // STUCK_WINDOW entries. Written once per turn in `record_kept_goals`, read only by
            // `stuck_holder`.
            move_trace: BTreeMap<i32, Vec<(i32, Cell, bool)>>,
        }
'''

INIT_OLD = "                    last_cell: BTreeMap::new(),\n                }\n"
INIT_NEW = '''                    last_cell: BTreeMap::new(),
                    move_trace: BTreeMap::new(),
                }
'''

# --------------------------------------------------------------------- 4. the release itself
# LAST in R5(a)'s order, after dead / gone / impossible / done. The four world predicates say the
# goal is no longer there to pursue; rule iii says the goal is still there and the troll is not
# pursuing it. A world cause therefore always wins, the census still sums exactly, and no turn is
# double-counted.
RELEASE_OLD = '''                    if self.goal_done(view, unit, goal) {
                        self.forget_goal(id);
                        meta.rd += 1;
                        meta.kr += 1;
                    }
                }
            }
'''
RELEASE_NEW = '''                    if self.goal_done(view, unit, goal) {
                        self.forget_goal(id);
                        meta.rd += 1;
                        meta.kr += 1;
                        continue;
                    }
                    // ---- rule iii, Candidate 3b -------------------------------------------
                    if MoisanBot::STUCK_RELEASE_ENABLED && self.stuck_holder(view, unit.id) {
                        self.forget_goal(id);
                        meta.rs += 1;
                        meta.kr += 1;
                    }
                }
            }
            // A holder is stuck when the last STUCK_WINDOW turns it actually played sit on at
            // most STUCK_CELLS distinct cells and contain no work command. Three ways to decline,
            // all of them silent and all of them deliberate:
            //   * the goal is younger than the window -- the window would reach back before the
            //     goal existed, which is a different unit's history, not this goal's;
            //   * the trace holds fewer than STUCK_WINDOW entries, or its entries are not the
            //     consecutive turns `t-STUCK_WINDOW .. t-1` -- a gap means the unit emitted
            //     nothing on some turn and the window is not what it claims to be;
            //   * any entry in the window carries a work command.
            fn stuck_holder(&self, view: &GameState, id: i32) -> bool {
                let window = MoisanBot::STUCK_WINDOW;
                let since = match self.kept_since.get(&id) {
                    Some(turn) => *turn,
                    None => return false,
                };
                if view.turn - since < window {
                    return false;
                }
                let trace = match self.move_trace.get(&id) {
                    Some(trace) => trace,
                    None => return false,
                };
                if trace.len() < window as usize {
                    return false;
                }
                let span = &trace[trace.len() - window as usize..];
                for (offset, entry) in span.iter().enumerate() {
                    if entry.0 != view.turn - window + offset as i32 {
                        return false;
                    }
                    if entry.2 {
                        return false;
                    }
                }
                let mut cells: Vec<Cell> = span.iter().map(|entry| entry.1).collect();
                cells.sort();
                cells.dedup();
                cells.len() <= MoisanBot::STUCK_CELLS
            }
'''

# ------------------------------------------------------------- 5. writing the trace, once a turn
# In `record_kept_goals`, beside the one-turn snapshot the release tests already read, so the
# trace and `last_command`/`last_cell` can never disagree about what the unit did. A turn on which
# the unit emitted no line writes NO entry, which `stuck_holder`'s gap check then sees.
TRACE_OLD = '''                        Some(command) => {
                            self.last_command.insert(*id, command.clone());
                            self.last_cell.insert(*id, unit.cell);
                        }
'''
TRACE_NEW = '''                        Some(command) => {
                            self.last_command.insert(*id, command.clone());
                            self.last_cell.insert(*id, unit.cell);
                            let verb = command.split_whitespace().next().unwrap_or("");
                            let worked = MoisanBot::STUCK_WORK.contains(&verb);
                            let trace = self.move_trace.entry(*id).or_insert_with(Vec::new);
                            trace.push((view.turn, unit.cell, worked));
                            let window = MoisanBot::STUCK_WINDOW as usize;
                            if trace.len() > window {
                                let excess = trace.len() - window;
                                trace.drain(0..excess);
                            }
                        }
'''

RETAIN_OLD = '''                self.last_command.retain(|id, _| alive.contains(id));
                self.last_cell.retain(|id, _| alive.contains(id));
'''
RETAIN_NEW = '''                self.last_command.retain(|id, _| alive.contains(id));
                self.last_cell.retain(|id, _| alive.contains(id));
                self.move_trace.retain(|id, _| alive.contains(id));
'''

# ------------------------------------------------------------------------------ 6. the v7 wire
VERSION_OLD = 'vec![format!("NARRATE v6 t={}", view.turn)]'
VERSION_NEW = 'vec![format!("NARRATE v7 t={}", view.turn)]'

# `rs` is emitted next to the other release causes, in the census order the decoder reads.
WIRE_OLD = '''                tokens.push(format!("rx={}", meta.rx));
'''
WIRE_NEW = '''                tokens.push(format!("rx={}", meta.rx));
                tokens.push(format!("rs={}", meta.rs));
'''


def build_text() -> str:
    base = P.load_base()
    parent = P.build_text(base)
    sha = hashlib.sha256(parent.encode()).hexdigest()
    if sha != PARENT_SHA:
        raise GenError(
            f"Candidate 3's source is {sha}, expected {PARENT_SHA} — refuse to guess. "
            "Candidate 3b is defined as Candidate 3 plus one release cause; if the parent moved, "
            "the definition moved with it.")
    text = parent
    text = replace_once(text, FLAG_OLD, FLAG_NEW, "flag line")
    text = replace_once(text, META_OLD, META_NEW, "rs counter")
    text = replace_once(text, STATE_OLD, STATE_NEW, "move trace state")
    text = replace_once(text, INIT_OLD, INIT_NEW, "move trace init")
    text = replace_once(text, RELEASE_OLD, RELEASE_NEW, "rule iii release")
    text = replace_once(text, TRACE_OLD, TRACE_NEW, "trace write")
    text = replace_once(text, RETAIN_OLD, RETAIN_NEW, "trace retain")
    text = replace_once(text, VERSION_OLD, VERSION_NEW, "wire version")
    text = replace_once(text, WIRE_OLD, WIRE_NEW, "rs on the wire")
    return text


def main() -> int:
    text = build_text()
    OUT.write_text(text)
    out_sha = hashlib.sha256(text.encode()).hexdigest()
    print(f"  parent claude_1/cure3/cure3-keep-v6.rs  sha256 {PARENT_SHA[:16]}")
    print(f"  source {OUT.relative_to(REPO)}  sha256 {out_sha[:16]}  {len(text.splitlines())} lines")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except GenError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)
