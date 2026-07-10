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
use super::*;

/// The most wood-efficient reachable, non-doomed, fellable tree for `u` — the wrong-tree
/// fix: `efficiency = wood_yield / (travel_steps + chops_to_fell)`, `wood_yield ~ size`
/// (fell wood ~ size) and `chops_to_fell = ceil(health / chop_power)`, so a SOFT tree (few
/// chops) beats a nearer TANKY one (many chops) whenever the chop-time saved outweighs the
/// extra travel. Trees an enemy will fell before we arrive (`planner::race` returns `None`)
/// are skipped outright — never donate the travel to a doomed target (same check the band
/// system already relies on for bands 70/72/42/40/31/30). Canonical: candidates sorted by
/// `(-efficiency, cell)`, so ties break on cell coordinate — never HashMap/HashSet
/// iteration order (this codebase's recurring determinism hazard).
pub fn fell_target(state: &State, u: &Troll) -> Option<Cell> {
    let d = bfs_distances(&state.walkable, &[u.pos()]);
    let ms = u.movement_speed.max(1);
    let cp = u.chop_power.max(1);
    let mut cands: Vec<(i64, Cell)> = Vec::new(); // (-efficiency_scaled, cell); smaller sorts first
    for t in &state.trees {
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
