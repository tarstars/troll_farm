//! The forced-win oracle: `forced_verdict` decides whether a side can GUARANTEE a strictly
//! better score-diff at the horizon, regardless of the opponent's play, via a sound
//! informed-minimax search over the real (deterministic) game engine.
//!
//! ## Soundness argument
//! Troll Farm is simultaneous-move: both sides commit a joint action each turn without seeing
//! the other's choice. Solving THAT exactly (a game value that may require mixed strategies) is
//! out of scope — we only want a checkable, sound certificate for FORCED wins.
//!
//! The trick: solve an auxiliary SEQUENTIAL game where, at every ply, X commits its joint action
//! first and Y — INFORMED, seeing X's realized move — best-responds to minimize X's score-diff.
//! Call X's guaranteed value under this handicap `informed_minimax(X)`. For any fixed X
//! strategy, an informed Y can always at least replicate whatever a blind (real) Y could do
//! (ignore the extra information) and, being strictly more capable, can only do at least as
//! well *against* X — so `min_{Y informed} <= min_{Y blind}` pointwise in X's strategy. Taking
//! the max over X strategies preserves the inequality:
//! `informed_minimax(X) = max_X min_{Y informed} payoff  <=  max_X min_{Y blind} payoff = X's
//! true simultaneous security level`. Hence `informed_minimax(X) > 0` implies X *genuinely*
//! forces a win in the real blind-simultaneous game — the certificate is conservative (some true
//! forced wins that require X to hide information via mixed play won't be found; that's fine,
//! we want soundness, not completeness) but never a false positive.
//!
//! `forced_verdict` runs this once per side (or only `prove_side` if pinned) and reports
//! `ForcedWin` for the first side whose informed-minimax value is a strictly positive score-diff.

use std::collections::HashMap;

use crate::game::engine;
use crate::game::state::GameState;

use super::actions::joint_actions;
use super::situation::Situation;

/// Safety cap on the number of (X-action, Y-action) transitions explored by a single
/// `informed_minimax` call. Exceeding it aborts the search and reports `TooLarge` rather than
/// hanging — the position is then outside the exact-oracle envelope (see the design doc's
/// tractability envelope: ~1 troll/side, small maps, horizon ~5-20).
///
/// The design doc's illustrative figure was 5e6; empirically that's ~150us/edge here (each edge
/// clones a `GameState` and calls `engine::step`, which resolves MOVE via `next_cell` — 1-2 BFS
/// passes with fresh HashMap/VecDeque allocations per call; that cost lives in game::engine,
/// which this module must not modify), so 5e6 would take ~13 minutes to report TooLarge — too
/// slow for a tool meant to fail fast on an intractable position. 100_000 (~15s worst case,
/// measured) is still comfortably generous for the STATED envelope: a genuine 1-troll-per-side
/// contest at H=16 (near the top of "horizon ~5-20") resolves in ~0.1s here, orders of magnitude
/// under budget. Tune this constant if a legitimate small etude ever reports a false TooLarge.
const NODE_BUDGET: u64 = 100_000;

#[derive(Debug, Clone, PartialEq)]
pub enum Verdict {
    ForcedWin { side: usize, proof: Proof },
    Unresolved,
    TooLarge,
}

/// A checkable certificate for a `ForcedWin`: the forcing side's committed joint command at each
/// ply of the principal variation (the argmax-X / argmin-informed-Y line the search actually
/// found), paired with the resulting `informed_minimax` value from that point on. `line.len() ==
/// horizon`. Independently checkable via `replay_proof`, which does NOT trust this line's values
/// — it only trusts the recorded X commands and re-derives everything else via brute force.
#[derive(Debug, Clone, PartialEq)]
pub struct Proof {
    pub line: Vec<(String, i32)>,
}

/// X's guaranteed score-diff (`scores[x] - scores[1-x]`) at the horizon when Y is INFORMED
/// (sees X's joint move this turn and best-responds to minimize it). Returns `None` if the node
/// budget is exhausted before the search completes (caller must treat that as `TooLarge`, never
/// as a value).
fn informed_minimax(
    st: &GameState,
    x: usize,
    depth: u32,
    memo: &mut HashMap<(u64, u32, usize), i32>,
    budget: &mut u64,
) -> Option<i32> {
    if depth == 0 {
        let mut s = st.clone();
        engine::recompute_scores(&mut s);
        return Some(s.scores[x] - s.scores[1 - x]);
    }

    let key = (canonical_hash(st), depth, x);
    if let Some(&v) = memo.get(&key) {
        return Some(v);
    }

    let y = 1 - x;
    let xm = joint_actions(st, x);
    let ym = joint_actions(st, y);

    let mut best_x = i32::MIN; // X's best guaranteed value so far (alpha)
    for xc in &xm {
        let mut worst = i32::MAX; // Y (informed) minimizes X's value for this xc
        for yc in &ym {
            if *budget == 0 {
                return None;
            }
            *budget -= 1;

            let mut s = st.clone();
            let (c0, c1) = if x == 0 {
                (xc.clone(), yc.clone())
            } else {
                (yc.clone(), xc.clone())
            };
            engine::step(&mut s, &c0, &c1);
            let v = informed_minimax(&s, x, depth - 1, memo, budget)?;

            if v < worst {
                worst = v;
            }
            if worst <= best_x {
                break; // alpha-beta prune: this xc can't beat what X already has elsewhere
            }
        }
        if worst > best_x {
            best_x = worst;
        }
    }

    memo.insert(key, best_x);
    Some(best_x)
}

/// Canonical, order-independent hash of the DYNAMIC part of a state (units/plants/inventories/
/// turn). Terrain (width/height/walkable/shacks/iron/water) is fixed for the lifetime of a
/// single etude search (no engine rule ever mutates it), so it's deliberately excluded. Unit
/// tuples include the talent fields (ms/cc/hp/chop) alongside id/player/x/y/carry: those never
/// change under the current action set (no TRAIN command is in `actions::troll_actions`, so no
/// unit is ever spawned or re-talented mid-search) but hashing them too costs nothing and keeps
/// this function correct even if a future action set adds TRAIN. Sorting both vectors before
/// hashing makes this independent of `Vec`/`HashSet` iteration order — no nondeterminism leaks
/// into the transposition table.
fn canonical_hash(st: &GameState) -> u64 {
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};

    let mut u: Vec<_> = st
        .units
        .iter()
        .map(|z| (z.id, z.player, z.x, z.y, z.ms, z.cc, z.hp, z.chop, z.carry))
        .collect();
    u.sort();
    let mut p: Vec<_> = st
        .plants
        .iter()
        .map(|z| (z.x, z.y, z.size, z.health, z.fruits, z.cooldown))
        .collect();
    p.sort();

    let mut h = DefaultHasher::new();
    (u, p, st.inventories, st.turn).hash(&mut h);
    h.finish()
}

/// The value `informed_minimax` would report for `(st, x, depth)`, either read straight off the
/// leaf formula (depth 0) or looked up in an ALREADY-COMPLETE memo table (depth > 0). Used by
/// `extract_line`, which only ever asks for values at states a completed (non-`TooLarge`) search
/// actually visited — see the "winning line's Y-loop always runs to completion" note below.
fn lookup_value(st: &GameState, x: usize, depth: u32, memo: &HashMap<(u64, u32, usize), i32>) -> i32 {
    if depth == 0 {
        let mut s = st.clone();
        engine::recompute_scores(&mut s);
        return s.scores[x] - s.scores[1 - x];
    }
    let key = (canonical_hash(st), depth, x);
    *memo.get(&key).expect(
        "extract_line: memo entry missing for a state the completed search must have visited",
    )
}

/// Walk the principal variation of an already-completed (`memo` fully populated, budget never
/// exhausted) `informed_minimax(st0, x, horizon)` search: at each ply, re-derive X's argmax
/// action and Y's argmin (informed) response via a plain O(|xm|*|ym|) scan using `lookup_value`
/// (cheap — no re-exploration, just memo reads), matching exactly what the original search found
/// (it's deterministic given the same canonical action ordering). This is safe — i.e. every
/// `lookup_value` call here hits an already-known value — because alpha-beta only ever discards
/// an X-action whose partial worst-so-far already can't beat the running best (see
/// `informed_minimax`'s `break`), so the X-action that DOES end up winning at each node had its
/// Y-loop run to completion without early-exit, and completed without hitting the node budget
/// (otherwise `forced_verdict` would have returned `TooLarge`, not called this).
fn extract_line(st0: &GameState, x: usize, horizon: u32, memo: &HashMap<(u64, u32, usize), i32>) -> Vec<(String, i32)> {
    let y = 1 - x;
    let mut line = Vec::with_capacity(horizon as usize);
    let mut st = st0.clone();

    for depth in (1..=horizon).rev() {
        let xm = joint_actions(&st, x);
        let ym = joint_actions(&st, y);

        let mut best_val = i32::MIN;
        let mut best_xc: &Vec<String> = &xm[0];
        let mut best_yc: &Vec<String> = &ym[0];
        for xc in &xm {
            let mut worst = i32::MAX;
            let mut worst_yc: &Vec<String> = &ym[0];
            for yc in &ym {
                let mut s = st.clone();
                let (c0, c1) = if x == 0 {
                    (xc.clone(), yc.clone())
                } else {
                    (yc.clone(), xc.clone())
                };
                engine::step(&mut s, &c0, &c1);
                let v = lookup_value(&s, x, depth - 1, memo);
                if v < worst {
                    worst = v;
                    worst_yc = yc;
                }
            }
            if worst > best_val {
                best_val = worst;
                best_xc = xc;
                best_yc = worst_yc;
            }
        }

        line.push((best_xc.join(" | "), best_val));

        let mut s = st.clone();
        let (c0, c1) = if x == 0 {
            (best_xc.clone(), best_yc.clone())
        } else {
            (best_yc.clone(), best_xc.clone())
        };
        engine::step(&mut s, &c0, &c1);
        st = s;
    }

    line
}

/// Decide the forced-outcome verdict for a Situation: `ForcedWin{side, proof}` if that side's
/// informed-minimax value is a strictly positive score-diff (checked for `prove_side` only, or
/// both sides in id order if unpinned), else `Unresolved`, else `TooLarge` if the node budget
/// was exhausted along the way.
pub fn forced_verdict(sit: &Situation) -> Verdict {
    let sides: Vec<usize> = match sit.prove_side {
        Some(p) => vec![p],
        None => vec![0, 1],
    };
    for x in sides {
        let mut memo = HashMap::new();
        let mut budget = NODE_BUDGET;
        match informed_minimax(&sit.state, x, sit.horizon, &mut memo, &mut budget) {
            None => return Verdict::TooLarge,
            Some(v) if v > 0 => {
                let line = extract_line(&sit.state, x, sit.horizon, &memo);
                return Verdict::ForcedWin {
                    side: x,
                    proof: Proof { line },
                };
            }
            _ => {}
        }
    }
    Verdict::Unresolved
}

/// Independently validate a `ForcedWin` proof: replay the forcing side's committed joint command
/// at each ply against a BRUTE-FORCE opponent that tries EVERY `joint_actions` response (not just
/// the search's own pruned/memoized path), recursing over every branch, and assert the horizon
/// score-diff is strictly positive on every single leaf. This does not trust `informed_minimax`,
/// `canonical_hash`, or the memo table at all — it only trusts the proof's recorded X commands
/// plus `joint_actions`/`engine::step`/`engine::recompute_scores`, so it independently re-proves
/// the guarantee and would catch a bug in the search machinery. Returns `false` for a non-
/// `ForcedWin` verdict (nothing to replay) or if any branch fails to hold.
pub fn replay_proof(sit: &Situation, verdict: &Verdict) -> bool {
    let (side, proof) = match verdict {
        Verdict::ForcedWin { side, proof } => (*side, proof),
        _ => return false,
    };
    replay_from(&sit.state, side, &proof.line)
}

fn replay_from(st: &GameState, x: usize, remaining: &[(String, i32)]) -> bool {
    if remaining.is_empty() {
        let mut s = st.clone();
        engine::recompute_scores(&mut s);
        return s.scores[x] - s.scores[1 - x] > 0;
    }
    let y = 1 - x;
    let xc: Vec<String> = remaining[0].0.split(" | ").map(|c| c.to_string()).collect();
    let ym = joint_actions(st, y);
    for yc in &ym {
        let mut s = st.clone();
        let (c0, c1) = if x == 0 {
            (xc.clone(), yc.clone())
        } else {
            (yc.clone(), xc.clone())
        };
        engine::step(&mut s, &c0, &c1);
        if !replay_from(&s, x, &remaining[1..]) {
            return false;
        }
    }
    true
}
