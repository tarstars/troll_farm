#!/usr/bin/env python3
"""R3c+R4 one-shot: split decide_elite into tactics (L1: Plan) + jobs (L2: assign_all).

Anchor-based, verbatim block moves:
  - L1 `src/botmain/tactics.rs`: pub struct Plan + pub fn plan(state, my) — the pre-loop
    tactical block (spec ladder, train gating, farm config, seed reserve) moved verbatim;
    Plan is the explicit L1→L2 interface.
  - L2 `src/botmain/jobs.rs`: pub fn assign_all(state, plan, my) -> HashMap<i32,String> —
    the fell_ok/own_half/within_roam closures + the whole per-troll cascade moved verbatim
    (plan fields re-bound as same-named locals so the body needs zero renames).
  - decide_elite shrinks to: resets → plan → assign_all → motion::watchdog → assemble.
Gated afterwards by: cargo build+test, equality vs reference_bin, bundle gates.
"""
import re

SRC = "src/botmain.rs"
lines = open(SRC).read().split("\n")


def idx(pred, start=0):
    for i in range(start, len(lines)):
        if pred(lines[i]):
            return i
    raise SystemExit("anchor not found")


fn_start = idx(lambda l: l.startswith("fn decide_elite"))
t_start = idx(lambda l: l.strip() == "let shack = state.my_shack;", fn_start)
my_start = idx(lambda l: l.strip().startswith("let mut my: Vec<Troll>"), t_start)
my_end = idx(lambda l: l.strip() == "let n = my.len() as i32;", my_start)
fellok_c = idx(lambda l: l.strip().startswith("// is a tree currently fellable"), my_end)
roam_end = idx(lambda l: l.strip().startswith("let within_roam"), fellok_c)
j2_start = idx(lambda l: l.strip().startswith("let mut reserved"), roam_end)
wd_line = idx(lambda l: "anti-stall watchdog (R3b" in l, j2_start)
fn_end = idx(lambda l: l == "}", wd_line)

# blocks (verbatim)
tact_body = lines[t_start:my_start] + ["    let n = my.len() as i32;"] + lines[my_end + 1 : fellok_c]
closures = lines[fellok_c : roam_end + 1]
loop_blk = lines[j2_start:wd_line]
tail = lines[wd_line : fn_end + 1]

# jobs uses these plan fields as bare names — re-bind only the ones the moved text mentions
COPY_FIELDS = [
    "shack", "opp", "have_iron", "turns_rem", "n", "farm_now", "nchop", "spec",
    "want_chopper", "want_feeder", "train_spec", "cost", "train_now", "need_iron",
    "need_fund", "farm_r", "farm_cap", "fell_size", "farm_fell", "chop_r",
    "starter_chop", "liquidation", "base_trees",
]
jobs_text = "\n".join(closures + loop_blk)
binds = [f"    let {f} = plan.{f};" for f in COPY_FIELDS if re.search(rf"\b{f}\b", jobs_text)]

# ── tactics.rs ──
tactics = """//! Tactics layer (L1, R4): everything decided BEFORE any troll is looked at — the
//! turn-1 adaptive chopper spec, train gating, farm geometry/phase, and the seed
//! reserve. `Plan` is the explicit L1→L2 interface consumed by jobs::assign_all.
//! Bodies moved VERBATIM from decide_elite; equality enforced by the harness.
use super::*;
use std::cell::RefCell;
use std::collections::HashSet;

thread_local! {
    // v1.7.0: the chopper spec chosen ONCE at turn 1 from the starting draw.
    static GE_CHOSEN_SPEC: RefCell<Option<(i32, i32, i32, i32)>> = RefCell::new(None);
}

/// Turn-1 reset of the committed spec.
pub fn reset() {
    GE_CHOSEN_SPEC.with(|c| *c.borrow_mut() = None);
}

pub struct Plan {
    pub shack: Cell,
    pub opp: Cell,
    pub have_iron: bool,
    pub turns_rem: i32,
    pub n: i32,
    pub farm_now: usize,
    pub nchop: i32,
    pub spec: (i32, i32, i32, i32),
    pub want_chopper: bool,
    pub want_feeder: bool,
    pub train_spec: (i32, i32, i32, i32),
    pub cost: [i32; 6],
    pub train_now: bool,
    pub need_iron: bool,
    pub need_fund: [bool; 3],
    pub farm_r: i32,
    pub farm_cap: usize,
    pub fell_size: i32,
    pub farm_fell: i32,
    pub chop_r: i32,
    pub starter_chop: bool,
    pub liquidation: bool,
    pub base_trees: usize,
    pub seed_cells: HashSet<Cell>,
}

pub fn plan(state: &State, my: &[Troll]) -> Plan {
__BODY__
    Plan {
        shack, opp, have_iron, turns_rem, n, farm_now, nchop, spec, want_chopper,
        want_feeder, train_spec, cost, train_now, need_iron, need_fund, farm_r, farm_cap,
        fell_size, farm_fell, chop_r, starter_chop, liquidation, base_trees, seed_cells,
    }
}
""".replace("__BODY__", "\n".join(tact_body))

# ── jobs.rs ──
jobs = """//! Jobs layer (L2, R3c): per-troll decision cascade — who funds, mines, harvests,
//! plants, fells, banks, parks. Consumes the tactical Plan; produces one command per
//! troll (id → command). Bodies moved VERBATIM from decide_elite (plan fields re-bound
//! as same-named locals); equality enforced by the harness. This is the layer where the
//! future policy experiments (farm-supply invariant, dynamic starter role) live.
use super::tactics::Plan;
use super::*;
use std::collections::{HashMap, HashSet};

thread_local! {
    // GoldElite::mem — last sticky target cell per troll. Write-only (never read);
    // kept for a faithful 1:1 port. Reset at turn 1.
    static GE_MEM: RefCell<HashMap<i32, Cell>> = RefCell::new(HashMap::new());
}

/// Turn-1 reset of the sticky-target memory.
pub fn reset() {
    GE_MEM.with(|m| m.borrow_mut().clear());
}

pub fn assign_all(state: &State, plan: &Plan, my: &[Troll]) -> HashMap<i32, String> {
__BINDS__
    let seed_cells = &plan.seed_cells;
    let inv = &state.my_inventory;
__CLOSURES__
__LOOP__
    cmd_by_id
}
""".replace("__BINDS__", "\n".join(binds)).replace(
    "__CLOSURES__", "\n".join(closures)
).replace("__LOOP__", "\n".join(loop_blk).replace("for u in &my {", "for u in my {"))

open("src/botmain/tactics.rs", "w").write(tactics)
open("src/botmain/jobs.rs", "w").write(jobs)

# ── rewrite botmain.rs ──
new_fn = [
    "fn decide_elite(state: &State) -> Vec<String> {",
    "    if state.turn == 1 {",
    "        jobs::reset();",
    "        motion::reset();",
    "        tactics::reset();",
    "    }",
    "    let mut my: Vec<Troll> = state.my_trolls.clone();",
    "    my.sort_by_key(|t| t.id);",
    "",
    "    // L1: tactical plan → L2: per-troll job assignment → L3: motion post-pass",
    "    let plan = tactics::plan(state, &my);",
    "    let mut cmd_by_id = jobs::assign_all(state, &plan, &my);",
]
# tail: watchdog + assembly + TRAIN, with plan.-qualified fields
tail_txt = "\n".join(tail)
tail_txt = tail_txt.replace("if train_now", "if plan.train_now")
tail_txt = tail_txt.replace("train_spec.0, train_spec.1, train_spec.2, train_spec.3",
                            "plan.train_spec.0, plan.train_spec.1, plan.train_spec.2, plan.train_spec.3")
tail_txt = tail_txt.replace("u.pos() == shack", "u.pos() == plan.shack")

out = lines[:fn_start] + new_fn + tail_txt.split("\n") + lines[fn_end + 1 :]
txt = "\n".join(out)
txt = txt.replace("mod motion;", "mod motion;\nmod tactics;\nmod jobs;", 1)
# the old root GE_MEM/GE_CHOSEN_SPEC thread_local block is now unused; leave removal to a
# follow-up edit (kept lines would shadow nothing — but remove the decide_elite-era statics
# to avoid confusion): handled below by dropping their thread_local block if it only holds them.
open(SRC, "w").write(txt)
print(f"tactics: {len(tact_body)} body lines; jobs: {len(closures)+len(loop_blk)} lines; binds: {len(binds)}")
print("NOTE: old root GE_MEM/GE_CHOSEN_SPEC thread_local block left in place — remove manually.")
