//! L2 JOINT TASK ASSIGNMENT (R6b) — the activity manager's task stage.
//!
//! The sequential cascade (jobs.rs) let troll-id order decide contested resources: the
//! first troll `reserved` its target, later trolls avoided it. Here every troll's viable
//! tasks are enumerated as (target, value) CANDIDATES — the cascade's branch hierarchy
//! becomes value BANDS (spaced wider than any ETA, so each troll still prefers its higher
//! branch), ETA differentiates within a band — and the assignment is chosen JOINTLY:
//! exhaustive over per-troll top-K, maximizing total value, same-target conflicts
//! forbidden, canonical tie-break. SHUFFLE INVARIANCE: the plan depends on the objective,
//! never on troll/candidate iteration order.
use super::tactics::{Phase, Plan};
use super::*;
use std::cell::RefCell;
use std::collections::{HashMap, HashSet};

thread_local! {
    // last MoveTo target per troll (diagnostics: assignment-flap counter) + flap count
    static LAST_TGT: RefCell<HashMap<i32, Cell>> = RefCell::new(HashMap::new());
    static FLAPS: RefCell<u32> = RefCell::new(0);
}

/// Turn-1 reset of diagnostics.
pub fn reset() {
    LAST_TGT.with(|m| m.borrow_mut().clear());
    FLAPS.with(|f| *f.borrow_mut() = 0);
}

pub fn flaps() -> u32 {
    FLAPS.with(|f| *f.borrow())
}

const K: usize = 8; // per-troll candidate cap (bands make more irrelevant)
const BAND: i64 = 100_000; // > any ETA by orders of magnitude
// v1.28.1 STICKINESS: bonus for keeping last turn's target — the joint matcher re-plans
// globally every turn and small ETA shifts flipped assignments mid-travel (measured 16-36
// flaps/game = leaked steps, the v1.27 arena fade). Within-band (« BAND): stability never
// overrides the priority hierarchy, only breaks near-ties toward the current plan.
const STICKY: i64 = 6; // v1.28.3 sweep: residual flaps 2-21 at 3; absorb bigger ETA jitter
// v1.38.0-deny1 (A2 probe): bias the PRIMARY fell choice (bands 70/72 ONLY — not the
// anti-starvation fallback, not the starter's chop-help band) toward trees nearer the
// opponent's shack. Silver-era denial weighting toward the foe was the single biggest lever
// measured pre-planner (MB_DENIAL_W in botmain.rs); the R6b joint planner has carried weight
// 0 since it replaced that cascade. At DENY_W=0 every fell value is byte-identical to the
// pre-probe code (the subtracted term is `0 * x == 0`); DENY_W=1 only breaks near-ties and
// nudges marginal calls, « BAND — never overrides the priority hierarchy.
// v1.39.0-sharepen4: REVERTED — analyst b62c977 measured this candidate at ~17.0 (down from
// the 19.9-20.1 race-check band) and diagnosed a collision with the race check's own
// tie-breaking. Parked at 0 (byte-identical to pre-probe) pending a retest that doesn't fight
// RACE_SHARE_PEN; see tests/deny_probe.rs (its one test now requires DENY_W=1 and is ignored).
const DENY_W: i64 = 0; // A2 reverted — collided with the race check per analyst b62c977; knob kept at 0
// v1.36.0-race: mild discount for a JOINABLE contested tree (an enemy is already chopping it,
// but we can arrive before they finish) — the wood splits round-robin among cell-sharers
// (engine apply_chop), so a shared tree is worth slightly less than an uncontested one, but
// never enough to lose to a materially worse alternative. « BAND, like STICKY.
// v1.39.0-sharepen4: sweep 2 -> 4 per analyst (queue #1, b62c977) — the race check is the one
// mechanism that just gained +1.3 in the arena; the analyst's decoded losses show excessive
// trekking to contested trees when a free tree is only marginally farther away, so discount
// joinable contests harder.
const RACE_SHARE_PEN: i64 = 4; // sweep 2->4 per analyst; harder discount on joinable contests

#[derive(Clone, Debug, PartialEq)]
enum Kind {
    Bank,       // render via motion::bank_cmd (DROP if adjacent, else camp-cell MOVE)
    Park,       // render via motion::park_cmd
    ChopHere,   // CHOP at current cell
    MoveTo,     // MOVE toward target (fell/fund/seed/mine-adjacent/plant travel)
    PlantHere,  // PLANT BANANA at current cell
    Harvest,    // HARVEST at current cell
    Mine,       // MINE (adjacent to iron)
    Pick,       // PICK BANANA (shack-adjacent)
}

#[derive(Clone, Debug)]
struct Cand {
    kind: Kind,
    target: Option<Cell>, // claimed resource (tree/plant/iron-adj cell); None = un-contested
    value: i64,
}

fn eta(d: &HashMap<Cell, i32>, c: Cell, ms: i32) -> i64 {
    let dist = d.get(&c).copied().unwrap_or(1 << 20);
    ((dist + ms - 1) / ms.max(1)) as i64
}

/// candidates for one troll — a faithful transcription of the jobs.rs cascade into bands.
#[allow(clippy::too_many_lines)]
fn candidates(state: &State, plan: &Plan, my: &[Troll], u: &Troll, salt: u64) -> Vec<Cand> {
    let shack = plan.shack;
    let inv = &state.my_inventory;
    let d = bfs_distances(&state.walkable, &[u.pos()]);
    let ms = u.movement_speed;
    let is_chopper = u.chop_power >= 2;
    let mut out: Vec<Cand> = Vec::new();

    // B2 (Hoard): suppress felling except the denial emergency (an enemy troll within
    // map-distance 2 of the tree). Computed ONCE per candidates() call — a single multi-source
    // BFS from every opp troll, not a BFS per (enemy, tree) pair — and ONLY during Hoard, so
    // the Tempo path (the live meta) pays zero extra cost.
    let hoard = plan.phase == Phase::Hoard;
    let enemy_d: Option<HashMap<Cell, i32>> = if hoard {
        Some(bfs_distances(
            &state.walkable,
            &state.opp_trolls.iter().map(|e| e.pos()).collect::<Vec<_>>(),
        ))
    } else {
        None
    };
    let threatened = |pc: Cell| -> bool {
        enemy_d.as_ref().map_or(false, |ed| ed.get(&pc).map_or(false, |&dd| dd <= 2))
    };

    let fell_ok = |p: &Tree| -> bool {
        if plan.seed_cells.contains(&p.pos()) {
            return false;
        }
        if plan.liquidation {
            return p.size >= 1;
        }
        let farm_banana = p.tree_type == "BANANA" && plan.farm_d.get(&p.pos()).map_or(false, |&fd| fd <= plan.farm_r);
        p.size >= if farm_banana { plan.farm_fell } else { plan.fell_size }
    };
    let own_half =
        |p: &Tree| plan.liquidation || manhattan(p.pos(), shack) <= manhattan(p.pos(), plan.opp);
    let within_roam = |p: &Tree| plan.liquidation || plan.farm_d.get(&p.pos()).map_or(false, |&fd| fd <= plan.chop_r);

    // v1.36.0-race (user replay finding): a tree an enemy is already chopping is a RACE.
    // If they fell it before we arrive, walking there donates the travel (skip). If we can
    // arrive in time, the wood SPLITS round-robin among cell-sharers (engine apply_chop) —
    // join, but discount the value by the shared payoff. Pure function of `state` (no
    // per-troll mutable state), so shuffle invariance holds; called once per candidate,
    // covers every fell-type push (bands 72/70, 42/40, 31/30) via this one helper.
    let race = |pc: Cell, our_eta: i64| -> Option<i64> {
        // returns None = doomed (skip candidate); Some(penalty) = value adjustment
        let occupant = state.opp_trolls.iter().find(|e| e.pos() == pc && e.chop_power > 0);
        match occupant {
            None => Some(0),
            Some(e) => {
                let h = state.trees.iter().find(|p| p.pos() == pc).map(|p| p.health).unwrap_or(0) as i64;
                let their_turns = (h + e.chop_power as i64 - 1) / e.chop_power.max(1) as i64;
                if their_turns <= our_eta {
                    None // they finish first: doomed
                } else {
                    Some(RACE_SHARE_PEN) // joinable: shared wood, mild discount
                }
            }
        }
    };

    // endgame banking (band 95): bank a carried load in time to score it
    if u.total_carried() > 0 {
        let d_home = ortho_neighbors(shack)
            .iter()
            .filter(|c| state.walkable.contains(*c))
            .filter_map(|c| d.get(c))
            .min()
            .copied()
            .unwrap_or(i32::MAX / 2);
        let e = ((d_home + ms - 1) / ms.max(1) + 1) as i64;
        if (plan.turns_rem as i64) <= e + 1 {
            out.push(Cand { kind: Kind::Bank, target: None, value: 95 * BAND - e });
        }
    }
    // full -> bank (band 80)
    if u.free_capacity() == 0 && !(!is_chopper && u.carry[BANANA] > 0 && plan.base_trees < plan.farm_cap)
    {
        out.push(Cand { kind: Kind::Bank, target: None, value: 80 * BAND });
    }

    if is_chopper {
        // fell targets (band 70): standing (CHOP now) or travel; value differentiates by
        // steps + chop-time exactly like the cascade's nearest_fell metric.
        for p in state.trees.iter().filter(|p| fell_ok(p) && own_half(p) && within_roam(p)) {
            let pc = p.pos();
            if !d.contains_key(&pc) {
                continue;
            }
            if hoard && !threatened(pc) {
                continue; // Hoard: no fells unless the tree is under denial threat
            }
            let steps = eta(&d, pc, ms);
            let chop_t = ((p.health + u.chop_power.max(1) - 1) / u.chop_power.max(1)) as i64;
            let race_pen = match race(pc, steps) {
                None => continue, // doomed: they fell it before we arrive — skip, don't donate the travel
                Some(pen) => pen,
            };
            // A2 probe (DENY_W): trees closer to the opponent lose less -> rank higher.
            let deny_pen = DENY_W * (manhattan(pc, plan.opp) as i64 / 2);
            if pc == u.pos() {
                // standing on a fellable tree: FINISH IT (cascade branch order) — band 72
                // outranks every travel-fell so invested chops are never abandoned.
                out.push(Cand { kind: Kind::ChopHere, target: Some(pc), value: 72 * BAND - chop_t - race_pen - deny_pen });
            } else {
                out.push(Cand { kind: Kind::MoveTo, target: Some(pc), value: 70 * BAND - (steps + chop_t) - race_pen - deny_pen });
            }
        }
        // anti-starvation fell anything (band 30)
        for p in state.trees.iter().filter(|p| p.size >= 1) {
            let pc = p.pos();
            if !d.contains_key(&pc) {
                continue;
            }
            if hoard && !threatened(pc) {
                continue; // Hoard: no fells unless the tree is under denial threat
            }
            let steps = eta(&d, pc, ms);
            let chop_t = ((p.health + u.chop_power.max(1) - 1) / u.chop_power.max(1)) as i64;
            let race_pen = match race(pc, steps) {
                None => continue, // doomed: they fell it before we arrive — skip, don't donate the travel
                Some(pen) => pen,
            };
            if pc == u.pos() {
                out.push(Cand { kind: Kind::ChopHere, target: Some(pc), value: 31 * BAND - chop_t - race_pen });
            } else {
                out.push(Cand { kind: Kind::MoveTo, target: Some(pc), value: 30 * BAND - (steps + chop_t) - race_pen });
            }
        }
        // partial bank / park (band 10)
        out.push(Cand {
            kind: if u.total_carried() > 0 { Kind::Bank } else { Kind::Park },
            target: None,
            value: 10 * BAND,
        });
    } else {
        // STARTER — plant-cell search (shared): the best free base cell within the farm
        // radius, reachable from this troll. Computed ONCE whenever there's farm room
        // (base_trees < farm_cap), regardless of whether a banana is currently carried —
        // both band 88 (plant the carried banana, right below) AND the PICK/park-to-pick
        // bands (50/49, further down) need to know whether picking one up would even be
        // usable.
        // v1.41.0-nopickloop (user-observed corridor livelock): on maps where water + the
        // map edge leave no reachable, tree-free, un-occupied cell within the farm radius
        // (a dead-end pocket, or a shack whose few walkable neighbors are all tree/troll-
        // occupied), the OLD code still issued PICK whenever the tent held a banana. The
        // picked banana then had nowhere to plant; band 80 (full->bank) is suppressed for
        // a banana-carrying starter expecting to plant it, so the fallback band 10 banked
        // it right back next turn, and PICK fired again the turn after — an infinite
        // PICK<->DROP loop that also parks the starter on a scarce shack-adjacent cell the
        // chopper needs for banking. Gating both bands on `plant_cell.is_some()` fixes it:
        // no reachable destination, no PICK.
        let plant_cell: Option<Cell> = if plan.base_trees < plan.farm_cap {
            state
                .walkable
                .iter()
                .filter(|c| plan.farm_d.get(*c).map_or(false, |&fd| fd <= plan.farm_r) && d.contains_key(*c))
                .filter(|c| !state.trees.iter().any(|p| p.pos() == **c))
                .filter(|c| !my.iter().any(|o| o.id != u.id && o.pos() == **c))
                .min_by_key(|c| {
                    let wet = state.water_cells.iter().any(|w| manhattan(*w, **c) == 1);
                    // v1.37.0-nanaflow (user replay finding #3): DIAGONAL PLANT PLACEMENT. The
                    // four cells orthogonally adjacent to the shack (farm_d==1) are the only
                    // bank/DROP cells every hand's carry trip needs — planting there congests
                    // banking, so penalize them (+3). The four diagonal-to-shack cells sit at
                    // the same map-distance (2) but off that traffic path, so reward them (-1).
                    let bank_adj = plan.farm_d.get(*c).copied() == Some(1);
                    let (cx, cy) = **c;
                    let diag = (cx - plan.shack.0).abs() == 1 && (cy - plan.shack.1).abs() == 1;
                    let geo = (if bank_adj { 3 } else { 0 }) + (if diag { -1 } else { 0 });
                    (d[*c] + if wet { 0 } else { 2 } + geo, tie_mix(**c, salt))
                })
                .copied()
        } else {
            None
        };
        // 1) plant carried banana (band 88) at the best free base cell
        if u.carry[BANANA] > 0 {
            if let Some(tc) = plant_cell {
                let kind = if u.pos() == tc { Kind::PlantHere } else { Kind::MoveTo };
                out.push(Cand { kind, target: Some(tc), value: 88 * BAND - eta(&d, tc, ms) });
            }
        }
        // 3) standing on a ripe wanted fruit (band 75)
        if let Some(p) = state.trees.iter().find(|p| p.pos() == u.pos()) {
            if p.fruits > 0 && u.harvest_power > 0 && u.free_capacity() > 0 {
                let ty = ge_fruit_ty(&p.tree_type);
                let funding = plan.want_chopper || plan.want_feeder;
                let want = (funding && ty.map_or(false, |t| t < 3 && plan.need_fund[t]))
                    || (!plan.want_chopper
                        && (p.tree_type == "BANANA"
                            || (p.tree_type == "APPLE"
                                && state.water_cells.iter().any(|w| manhattan(*w, p.pos()) == 1))))
                    || plan.phase == Phase::Hoard; // Hoard wants EVERYTHING ripe standing under foot too
                if want {
                    out.push(Cand { kind: Kind::Harvest, target: Some(u.pos()), value: 75 * BAND });
                }
            }
        }
        // B2 (Hoard): wallet-building — travel to ANY ripe fruit tree. Fruit is points AND
        // wallet fuel during Hoard, so there is no per-type targeting like the funding/printer
        // bands below (those stay as-is; the matcher just takes the max of every band pushed).
        if plan.phase == Phase::Hoard {
            for p in state.trees.iter().filter(|p| p.fruits > 0 && d.contains_key(&p.pos())) {
                let pc = p.pos();
                out.push(Cand { kind: Kind::MoveTo, target: Some(pc), value: 62 * BAND - eta(&d, pc, ms) });
            }
        }
        // 4) FUNDING (bands 60/58) — for the chopper OR a pending 3rd hand (R6b.2: the old
        // feeder never trained because post-funding nobody harvested plum/lemon/apple)
        if plan.want_chopper || plan.want_feeder {
            // v1.28.1: the chopper is EXISTENTIAL (60/58) but a 3rd hand is a LUXURY — its
            // funding (45/44) must never displace printer/seed work (50/48). The v1.28.0
            // regression: perpetual feeder-funding starved the farm on lemon-poor maps.
            let (fund_hi, fund_lo) = if plan.want_chopper { (60, 58) } else { (45, 44) };
            // Gatekeeper verdict #3 (post-b14ebc7) fixed two compounding defects in one change:
            // (a) BAND COLLISION — e09ac48 (iron, 64/63) and b14ebc7 (fruit, 63) independently
            // landed on the SAME band, 63, so a troll needing both at once (routine: the
            // ladder's last hand needs all four resources together) picked whichever was
            // physically closer instead of the scarcer one. Iron has no fruit-harvest
            // alternative (B2.1: "iron is scarce and un-substitutable") so it must win
            // unconditionally — bumped to 65/64, strictly above the fruit band (63).
            // (b) T_SWITCH CLIFF — all these bands were gated `phase == Phase::Hoard` only, so
            // at t=140 a nearly-complete wallet was abandoned instantly (funding fell to
            // fund_lo=44, below Printer's 48/50) and the ladder's last hand never trained
            // (chopper 1/14 games). The elevated bands extend through a grace window scoped to
            // `want_feeder` (the ladder is still incomplete) instead of Hoard alone — it covers
            // Hoard (want_feeder is true throughout the ladder) AND the Factory grace (want_feeder
            // stays true until the ladder finishes), self-extinguishing once the ladder completes
            // (n reaches GE_MAX_TROLLS).
            // v1.35.0 (T-hand): renamed `scale_funding` -> `ladder_funding` and DROPPED the
            // `plan.phase != Phase::Tempo` gate — the elevated funding stack now serves ANY
            // pending ladder hand, including Tempo's revived 3rd hand (GE_MAX_TROLLS 2->3), not
            // just Scale's Hoard/Factory ladder. Graceful: a MoveTo/Mine candidate only exists
            // where ripe deficit fruit / adjacent iron actually exists on the map, and
            // `want_feeder` self-extinguishes the instant the pending hand trains — so Tempo
            // degrades to today's champion behavior on any map where the wallet never fills.
            // The generic wallet band (62, ~line 207 above) is UNTOUCHED: it stays gated on
            // `plan.phase == Phase::Hoard` directly, never on this variable.
            let ladder_funding = plan.want_feeder;
            if plan.need_iron && u.chop_power > 0 {
                if state.iron_cells.iter().any(|ic| manhattan(u.pos(), *ic) == 1) {
                    let v = if ladder_funding { 65 } else { fund_hi };
                    out.push(Cand { kind: Kind::Mine, target: Some(u.pos()), value: v * BAND });
                } else if let Some(c) = state
                    .iron_cells
                    .iter()
                    .flat_map(|ic| ortho_neighbors(*ic))
                    .filter(|c| d.contains_key(c))
                    .min_by_key(|c| (d[c], tie_mix(*c, salt)))
                {
                    let v = if ladder_funding { 64 } else { fund_hi };
                    out.push(Cand { kind: Kind::MoveTo, target: Some(c), value: v * BAND - eta(&d, c, ms) });
                }
            }
            // Deficit-fruit funding (PLUM/LEMON/APPLE): same grace window, one band below iron.
            let fruit_band = if ladder_funding { 63 } else { fund_lo };
            for p in state.trees.iter().filter(|p| {
                p.fruits > 0
                    && d.contains_key(&p.pos())
                    && ge_fruit_ty(&p.tree_type).map_or(false, |t| t < 3 && plan.need_fund[t])
            }) {
                let pc = p.pos();
                out.push(Cand { kind: Kind::MoveTo, target: Some(pc), value: fruit_band * BAND - eta(&d, pc, ms) });
            }
        }
        // 5) PRINTER (bands 52/50/49) — v1.37.0-nanaflow (user replay finding #2): TREE-FIRST.
        // Harvesting a ripe seed tree directly converts its fruit straight into a farm seed;
        // banked tent stock is just as harvestable a turn later. So a ripe seed tree now
        // outranks the tent unconditionally (band 52, the old `inv[BANANA] == 0` gate is
        // REMOVED — harvested even with tent stock on hand). PICK/park (50/49, unchanged) is
        // the fallback once no ripe seed tree is reachable; excess bananas accumulate in the
        // tent via the existing full->bank flow (1pt banked each, or 8pt later via plant->fell).
        if plan.base_trees < plan.farm_cap {
            for p in state.trees.iter().filter(|p| {
                p.fruits > 0
                    && d.contains_key(&p.pos())
                    && (p.tree_type == "BANANA"
                        || (p.tree_type == "APPLE"
                            && state.water_cells.iter().any(|w| manhattan(*w, p.pos()) == 1)))
            }) {
                let pc = p.pos();
                out.push(Cand { kind: Kind::MoveTo, target: Some(pc), value: 52 * BAND - eta(&d, pc, ms) });
            }
            // v1.41.0-nopickloop: only PICK (or travel to pick) if a plantable cell
            // actually exists (plant_cell.is_some()) — picking a banana with nowhere to
            // plant it is pure waste that just re-parks the starter on a scarce cell.
            if inv[BANANA] > 0 && u.free_capacity() > 0 && plant_cell.is_some() {
                // target = shack: dedupes the pick errand across multiple hands (R6b.2)
                if manhattan(u.pos(), shack) == 1 {
                    out.push(Cand { kind: Kind::Pick, target: Some(shack), value: 50 * BAND });
                } else {
                    out.push(Cand { kind: Kind::Park, target: Some(shack), value: 50 * BAND - 1 });
                }
            }
        }
        // 6) chop help (band 40) + anti-starvation (band 30)
        if plan.starter_chop && u.chop_power > 0 {
            for p in state.trees.iter().filter(|p| fell_ok(p) && own_half(p) && within_roam(p)) {
                if u.free_capacity() == 0 {
                    break;
                }
                let pc = p.pos();
                if !d.contains_key(&pc) {
                    continue;
                }
                if hoard && !threatened(pc) {
                    continue; // Hoard: no fells unless the tree is under denial threat
                }
                let steps = eta(&d, pc, ms);
                let chop_t = ((p.health + u.chop_power.max(1) - 1) / u.chop_power.max(1)) as i64;
                let race_pen = match race(pc, steps) {
                    None => continue, // doomed: they fell it before we arrive — skip, don't donate the travel
                    Some(pen) => pen,
                };
                if pc == u.pos() {
                    out.push(Cand { kind: Kind::ChopHere, target: Some(pc), value: 42 * BAND - chop_t - race_pen });
                } else {
                    out.push(Cand { kind: Kind::MoveTo, target: Some(pc), value: 40 * BAND - (steps + chop_t) - race_pen });
                }
            }
            if u.free_capacity() > 0 {
                for p in state.trees.iter().filter(|p| p.size >= 1) {
                    let pc = p.pos();
                    if !d.contains_key(&pc) {
                        continue;
                    }
                    if hoard && !threatened(pc) {
                        continue; // Hoard: no fells unless the tree is under denial threat
                    }
                    let steps = eta(&d, pc, ms);
                    let chop_t = ((p.health + u.chop_power.max(1) - 1) / u.chop_power.max(1)) as i64;
                    let race_pen = match race(pc, steps) {
                        None => continue, // doomed: they fell it before we arrive — skip, don't donate the travel
                        Some(pen) => pen,
                    };
                    if pc == u.pos() {
                        out.push(Cand { kind: Kind::ChopHere, target: Some(pc), value: 31 * BAND - chop_t - race_pen });
                    } else {
                        out.push(Cand { kind: Kind::MoveTo, target: Some(pc), value: 30 * BAND - (steps + chop_t) - race_pen });
                    }
                }
            }
        }
        // fallback (band 10)
        out.push(Cand {
            kind: if u.total_carried() > 0 { Kind::Bank } else { Kind::Park },
            target: None,
            value: 10 * BAND,
        });
    }

    // stickiness: prefer last turn's target on near-ties (see STICKY)
    let last = LAST_TGT.with(|m| m.borrow().get(&u.id).copied());
    if let Some(lt) = last {
        for c in out.iter_mut() {
            if c.target == Some(lt) {
                c.value += STICKY;
            }
        }
    }
    // canonical order + cap: by (-value, target) — never by discovery order
    out.sort_by_key(|c| (-c.value, c.target));
    out.truncate(K);
    out
}

/// Joint assignment: exhaustive over per-troll top-K candidates, maximize total value,
/// same-target conflicts forbidden, ties broken by the lexicographic pick vector.
pub fn assign(state: &State, plan: &Plan, my: &[Troll]) -> HashMap<i32, String> {
    let salt = tie_salt(state);
    let mut ids: Vec<i32> = my.iter().map(|t| t.id).collect();
    ids.sort();
    let trolls: Vec<&Troll> = ids.iter().map(|id| my.iter().find(|t| t.id == *id).unwrap()).collect();
    let cands: Vec<Vec<Cand>> = trolls.iter().map(|t| candidates(state, plan, my, t, salt)).collect();

    let n = ids.len();
    let mut best: Option<(i64, Vec<usize>)> = None;
    let mut pick = vec![0usize; n];
    if n > 0 {
        loop {
            let mut targets: Vec<Cell> = Vec::new();
            let mut ok = true;
            for i in 0..n {
                if let Some(t) = cands[i][pick[i]].target {
                    if targets.contains(&t) {
                        ok = false;
                        break;
                    }
                    targets.push(t);
                }
            }
            if ok {
                let total: i64 = (0..n).map(|i| cands[i][pick[i]].value).sum();
                let better = match &best {
                    None => true,
                    Some((bt, bp)) => total > *bt || (total == *bt && pick < *bp),
                };
                if better {
                    best = Some((total, pick.clone()));
                }
            }
            let mut i = 0;
            loop {
                if i == n {
                    break;
                }
                pick[i] += 1;
                if pick[i] < cands[i].len() {
                    break;
                }
                pick[i] = 0;
                i += 1;
            }
            if i == n {
                break;
            }
        }
    }

    // render (troll-id order; camp-cell claiming stays deterministic via claimed_drop)
    let mut cmd_by_id: HashMap<i32, String> = HashMap::new();
    let mut claimed_drop: HashSet<Cell> = HashSet::new();
    if let Some((_, picks)) = best {
        for (i, id) in ids.iter().enumerate() {
            let u = trolls[i];
            let d = bfs_distances(&state.walkable, &[u.pos()]);
            let c = &cands[i][picks[i]];
            if let (Kind::MoveTo, Some(tc)) = (&c.kind, c.target) {
                LAST_TGT.with(|m| {
                    let mut m = m.borrow_mut();
                    if let Some(prev) = m.get(id) {
                        if *prev != tc && u.pos() != *prev {
                            FLAPS.with(|f| *f.borrow_mut() += 1);
                        }
                    }
                    m.insert(*id, tc);
                });
            } else {
                LAST_TGT.with(|m| m.borrow_mut().remove(id));
            }
            let cmd = match (&c.kind, c.target) {
                (Kind::Bank, _) => motion::bank_cmd(state, plan.shack, u, &d, &mut claimed_drop),
                (Kind::Park, _) => motion::park_cmd(state, plan.shack, u, &d, &mut claimed_drop),
                (Kind::ChopHere, _) => format!("CHOP {}", u.id),
                (Kind::PlantHere, _) => format!("PLANT {} BANANA", u.id),
                (Kind::Harvest, _) => format!("HARVEST {}", u.id),
                (Kind::Mine, _) => format!("MINE {}", u.id),
                (Kind::Pick, _) => format!("PICK {} BANANA", u.id),
                (Kind::MoveTo, Some(tc)) => format!("MOVE {} {} {}", u.id, tc.0, tc.1),
                (Kind::MoveTo, None) => format!("MOVE {} {} {}", u.id, plan.shack.0, plan.shack.1),
            };
            cmd_by_id.insert(*id, cmd);
        }
    }
    cmd_by_id
}
