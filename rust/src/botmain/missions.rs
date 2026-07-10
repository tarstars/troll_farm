//! L2 MISSION LAYER (v1.60.0-fellmission) — increment 1 of the intent-driven mission
//! redesign (docs/superpowers/specs/2026-07-10-intent-missions-design.md). Replaces the
//! chopper's weighted fell bands (planner.rs bands 70/72 primary-fell, 42/40 chop-help,
//! 31/30 anti-starvation) with ONE explicit, COMMITTED FellForWood mission: pick the most
//! wood-EFFICIENT reachable tree (not the nearest tanky one — the "wrong-tree" bug: the
//! chopper sat on a health-20 apple 9 turns for zero wood) and fell it to completion;
//! re-plan only when the target is Done (felled/gone) or Invalidated (unreachable, or now
//! race-doomed) — a mission persists, it does not re-win a weighted argmax every turn.
//!
//! Scope of this increment: ONLY the chopper (chop_power >= 2) runs a mission; every other
//! troll's behavior is untouched (still `planner::assign_resolved`'s bands — the +1.7 ring
//! economy). See `botmain::resolve_commands` for the decide_elite wiring. Later increments
//! (v1.61+) migrate Bank/BuildRing/TrainTroll/HarvestFruit; see the design doc's
//! "Incremental build path".
use super::planner;
use super::tactics::Plan;
use super::*;
use std::cell::RefCell;
use std::collections::HashMap;

thread_local! {
    // committed fell target per troll id — mission commitment, kept across turns until
    // Done (tree gone) or Invalidated (unreachable / race lost). Pattern: planner.rs's
    // LAST_TGT. Reset at turn 1 (see `reset`).
    static COMMITTED: RefCell<HashMap<i32, Cell>> = RefCell::new(HashMap::new());
}

/// Turn-1 reset of mission memory.
pub fn reset() {
    COMMITTED.with(|m| m.borrow_mut().clear());
}

/// The most wood-efficient reachable, non-doomed, fellable tree for `u` — the wrong-tree
/// fix: `efficiency = wood_yield / (travel_steps + chops_to_fell)`, `wood_yield ~ size`
/// (fell wood ~ size) and `chops_to_fell = ceil(health / chop_power)`, so a SOFT tree (few
/// chops) beats a nearer TANKY one (many chops) whenever the chop-time saved outweighs the
/// extra travel. Trees an enemy will fell before we arrive (`planner::race` returns `None`)
/// are skipped outright — never donate the travel to a doomed target (same check the band
/// system already relies on for bands 70/72/42/40/31/30). Canonical: candidates sorted by
/// `(-efficiency, cell)`, so ties break on cell coordinate — never HashMap/HashSet
/// iteration order (this codebase's recurring determinism hazard).
///
/// Code review Fix C1 (2026-07-11): the candidate tree set is restricted to EXACTLY the
/// champion's fell-band eligibility — `planner::fell_ok`/`own_half`/`within_roam`, the same
/// predicate `candidates()` uses to gate bands 70/72/40/42. WITHOUT this, the most
/// "wood-efficient" reachable tree is often our OWN standing ring diagonal (small/soft,
/// close to the shack) — the mission would commit to felling the seed/fruit engine
/// ringfix3's bands would never touch. The mission changes HOW we pick among the eligible
/// trees (max efficiency + commit); it must never change WHICH trees are eligible.
pub fn fell_target(state: &State, plan: &Plan, u: &Troll) -> Option<Cell> {
    let d = bfs_distances(&state.walkable, &[u.pos()]);
    let ms = u.movement_speed.max(1);
    let cp = u.chop_power.max(1);
    let mut cands: Vec<(i64, Cell)> = Vec::new(); // (-efficiency_scaled, cell); smaller sorts first
    for t in &state.trees {
        if !(planner::fell_ok(plan, t) && planner::own_half(plan, t) && planner::within_roam(plan, t))
        {
            continue; // not in the champion's fell-eligible set (ring diagonal / seed_cells /
                      // enemy-half / out-of-roam / undersized) — never a mission candidate
        }
        let pc = t.pos();
        let steps = match d.get(&pc) {
            Some(&s) => s as i64,
            None => continue, // unreachable
        };
        let chops = ((t.health + cp - 1) / cp) as i64;
        if chops <= 0 {
            continue; // no health left to fell (shouldn't occur — felled trees are removed)
        }
        let our_eta = (steps + ms as i64 - 1) / ms as i64;
        if planner::race(state, pc, our_eta).is_none() {
            continue; // doomed: an enemy fells it before we arrive — skip, don't donate the travel
        }
        // efficiency = wood_yield / (travel + chops); wood_yield ~ size. Scaled to integer
        // (x1000) so soft/close trees separate cleanly from tanky/far ones.
        let eff = (t.size as i64 * 1000) / (steps + chops).max(1);
        cands.push((-eff, pc));
    }
    cands.sort(); // canonical: best efficiency first, then cell (deterministic tie-break)
    cands.first().map(|&(_, c)| c)
}

/// The chopper's COMMITTED fell target: kept across turns unless the tree is Done (no
/// longer stands at that cell — the engine removes a plant from the list the instant its
/// health reaches 0, so "still stands" is a simple presence check) or Invalidated
/// (unreachable, or newly race-doomed by an enemy that has since moved onto it). A mission
/// persists; it does NOT abandon/backtrack to a newly-nearer or newly-more-efficient tree
/// (that flap is exactly the STICKY hack this replaces with a first-class concept — see the
/// design doc). `reset()` clears all commitments at turn 1.
pub fn chopper_target(state: &State, plan: &Plan, u: &Troll) -> Option<Cell> {
    let committed = COMMITTED.with(|m| m.borrow().get(&u.id).copied());
    if let Some(c) = committed {
        let still_stands = state.trees.iter().any(|t| t.pos() == c);
        let d = bfs_distances(&state.walkable, &[u.pos()]);
        if still_stands {
            if let Some(&steps) = d.get(&c) {
                let ms = u.movement_speed.max(1);
                let our_eta = (steps as i64 + ms as i64 - 1) / ms as i64;
                if planner::race(state, c, our_eta).is_some() {
                    return Some(c); // Active: keep the commitment, no re-plan
                }
            }
        }
        // Done (tree gone) or Invalidated (unreachable / now race-doomed): fall through
    }
    let fresh = fell_target(state, plan, u);
    COMMITTED.with(|m| {
        let mut m = m.borrow_mut();
        match fresh {
            Some(c) => {
                m.insert(u.id, c);
            }
            None => {
                m.remove(&u.id);
            }
        }
    });
    fresh
}
