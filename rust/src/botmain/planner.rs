//! L2 JOINT TASK ASSIGNMENT (R6b) — the activity manager's task stage.
//!
//! The sequential cascade (jobs.rs) let troll-id order decide contested resources: the
//! first troll `reserved` its target, later trolls avoided it. Here every troll's viable
//! tasks are enumerated as (target, value) CANDIDATES — the cascade's branch hierarchy
//! becomes value BANDS (spaced wider than any ETA, so each troll still prefers its higher
//! branch), ETA differentiates within a band — and the assignment is chosen JOINTLY:
//! exhaustive over per-troll top-K, maximizing total value, conflicting target claims
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
const RACE_SHARE_PEN: i64 = 2; // sharepen4 kept-at-parity = INCONCLUSIVE under policy v2; champion (race) semantics = 2
// v1.53.0-pressurefarm (Task 2 Step 3): under Orange/Red observed pressure, a created/farm
// tree the ownership model marks not-safely-ours (plan.pressure.exposed_created_cells) gets
// a small within-band bump — raises it before less-urgent same-band work, never overrides
// the priority hierarchy (« BAND, same discipline as STICKY/DENY_W/RACE_SHARE_PEN above).
// Under Green/Yellow, exposed_created_cells is always empty (Yellow's own_half signal alone
// never implies created_exposed>0 — see ownership::classify_pressure), so this is always +0
// there: a proven no-op, not a static preference.
const PRESSURE_LIQ_BONUS: i64 = 4;

#[derive(Clone, Debug, PartialEq)]
enum Kind {
    Bank, // render via motion::bank_cmd (DROP if adjacent, else camp-cell MOVE)
    Park, // render via motion::park_cmd (target None = idle band-10, ring-2-aware;
    // target Some(shack) = band-49 park-to-pick errand, direct camp approach)
    ChopHere,  // CHOP at current cell
    MoveTo,    // MOVE toward target (fell/fund/seed/mine-adjacent/plant travel)
    PlantHere, // PLANT BANANA at current cell
    Harvest,   // HARVEST at current cell
    Mine,      // MINE (adjacent to iron)
    Pick,      // PICK BANANA (shack-adjacent)
}

#[derive(Clone, Debug)]
struct Cand {
    kind: Kind,
    target: Option<Cell>, // claimed resource (tree/plant/iron-adj cell); None = un-contested
    value: i64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum ClaimClass {
    Cell,
    Fruit,
    Wood,
}

#[derive(Clone, Copy, Debug)]
struct ClaimInfo {
    class: ClaimClass,
    cell: Cell,
    steps: i64,
}

#[derive(Clone, Debug)]
struct Assignments {
    ids: Vec<i32>,
    cands: Vec<Vec<Cand>>,
    picks: Vec<usize>,
}

impl Assignments {
    fn idx(&self, id: i32) -> Option<usize> {
        self.ids.binary_search(&id).ok()
    }

    fn selected(&self, id: i32) -> Option<&Cand> {
        let i = self.idx(id)?;
        self.cands.get(i)?.get(self.picks[i])
    }

    fn selected_value(&self, id: i32) -> Option<i64> {
        self.selected(id).map(|c| c.value)
    }
}

fn eta(d: &HashMap<Cell, i32>, c: Cell, ms: i32) -> i64 {
    let dist = d.get(&c).copied().unwrap_or(1 << 20);
    ((dist + ms - 1) / ms.max(1)) as i64
}

fn value_band(value: i64) -> i64 {
    (value + BAND - 1) / BAND
}

fn claim_info(state: &State, c: &Cand, steps: i64) -> Option<ClaimInfo> {
    let cell = c.target?;
    let class = match c.kind {
        Kind::ChopHere => ClaimClass::Wood,
        Kind::Harvest => ClaimClass::Fruit,
        Kind::MoveTo => {
            let targets_tree = state.trees.iter().any(|p| p.pos() == cell);
            if targets_tree {
                match value_band(c.value) {
                    70 | 40 | 30 => ClaimClass::Wood,
                    63 | 62 | 58 | 52 | 44 | 38 => ClaimClass::Fruit,
                    _ => ClaimClass::Cell,
                }
            } else {
                ClaimClass::Cell
            }
        }
        Kind::Bank | Kind::Park | Kind::PlantHere | Kind::Mine | Kind::Pick => ClaimClass::Cell,
    };
    Some(ClaimInfo { class, cell, steps })
}

fn claims_conflict(a: ClaimInfo, b: ClaimInfo) -> bool {
    if a.cell != b.cell {
        return false;
    }
    match (a.class, b.class) {
        (ClaimClass::Fruit, ClaimClass::Wood) => a.steps >= b.steps,
        (ClaimClass::Wood, ClaimClass::Fruit) => b.steps >= a.steps,
        _ => true,
    }
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
        enemy_d
            .as_ref()
            .map_or(false, |ed| ed.get(&pc).map_or(false, |&dd| dd <= 2))
    };

    let fell_ok = |p: &Tree| -> bool {
        // v1.53.0-pressurefarm (Task 2 Step 2): a protected seed tree stays protected UNLESS
        // the pressure governor has specifically released it (Orange/Red AND this exact
        // tree is definitively not ours — see ownership::Pressure::released_seed_cells's doc
        // comment for why the release check is per-tree, not the broader "exposed" set).
        // Under Green/Yellow/Orange-without-a-definite-loser, released_seed_cells is always
        // empty, so this is byte-identical to the pre-pressure check.
        if plan.seed_cells.contains(&p.pos()) && !plan.pressure.released_seed_cells.contains(&p.pos())
        {
            return false;
        }
        if plan.liquidation {
            return p.size >= 1;
        }
        let farm_banana = p.tree_type == "BANANA"
            && plan
                .farm_d
                .get(&p.pos())
                .map_or(false, |&fd| fd <= plan.farm_r);
        p.size
            >= if farm_banana {
                plan.farm_fell
            } else {
                plan.fell_size
            }
    };
    let own_half =
        |p: &Tree| plan.liquidation || manhattan(p.pos(), shack) <= manhattan(p.pos(), plan.opp);
    let within_roam = |p: &Tree| {
        plan.liquidation
            || plan
                .farm_d
                .get(&p.pos())
                .map_or(false, |&fd| fd <= plan.chop_r)
    };
    // v1.36.0-race (user replay finding): a tree an enemy is already chopping is a RACE.
    // If they fell it before we arrive, walking there donates the travel (skip). If we can
    // arrive in time, the wood SPLITS round-robin among cell-sharers (engine apply_chop) —
    // join, but discount the value by the shared payoff. Pure function of `state` (no
    // per-troll mutable state), so shuffle invariance holds; called once per candidate,
    // covers every fell-type push (bands 72/70, 42/40, 31/30) via this one helper.
    let race = |pc: Cell, our_eta: i64| -> Option<i64> {
        // returns None = doomed (skip candidate); Some(penalty) = value adjustment
        let occupant = state
            .opp_trolls
            .iter()
            .find(|e| e.pos() == pc && e.chop_power > 0);
        match occupant {
            None => Some(0),
            Some(e) => {
                let h = state
                    .trees
                    .iter()
                    .find(|p| p.pos() == pc)
                    .map(|p| p.health)
                    .unwrap_or(0) as i64;
                let their_turns = (h + e.chop_power as i64 - 1) / e.chop_power.max(1) as i64;
                if their_turns <= our_eta {
                    None // they finish first: doomed
                } else {
                    Some(RACE_SHARE_PEN) // joinable: shared wood, mild discount
                }
            }
        }
    };
    // v1.53.0-pressurefarm (Task 2 Step 3): see PRESSURE_LIQ_BONUS's doc comment above.
    //
    // Code review I1 (2026-07-09): `race_pen` must gate this too. PRESSURE_LIQ_BONUS (4) >
    // RACE_SHARE_PEN (2), so applying the bonus unconditionally on a joinable-contested tree
    // (race_pen == RACE_SHARE_PEN) would more than cancel that discount (net +2), REVERSING
    // the race check's tuned "don't over-trek to a shared/discounted tree" behavior into a
    // preference for it — the exact opposite of what v1.36.0-race earned its +1.3. A doomed
    // tree (race() returned None) never reaches here at all (every call site `continue`s on
    // None before computing race_pen or calling this), so the only two live values of
    // race_pen are 0 (no opponent occupant — genuinely non-contested) and RACE_SHARE_PEN (a
    // joinable race). Withholding the bonus whenever race_pen != 0 therefore fully preserves
    // it on every non-contested exposed tree (this behavior's primary job — raise exposed
    // farm trees so we fell them before the opponent arrives) while making a contested tree's
    // net adjustment exactly `-race_pen` either way, never a reversal.
    let pressure_bonus = |pc: Cell, race_pen: i64| -> i64 {
        if race_pen != 0 {
            return 0;
        }
        if plan.pressure.state >= ownership::PressureState::Orange
            && plan.pressure.exposed_created_cells.contains(&pc)
        {
            PRESSURE_LIQ_BONUS
        } else {
            0
        }
    };

    // plant-cell search (shared across bands 80/88/50/49): the best free base cell within
    // the farm radius, reachable from this troll. Computed ONCE, whenever there's farm room
    // (base_trees < farm_cap), for EVERY troll — chopper included; band 80 just below needs
    // the answer even though only a non-chopper carrying a banana can ever act on it — so
    // band 80 (full -> bank), band 88 (plant the carried banana) and the PICK/park-to-pick
    // bands (50/49, both in the STARTER branch further down) all agree on whether a banana
    // would even be usable.
    // v1.41.0-nopickloop (user-observed corridor livelock): on maps where water + the map
    // edge leave no reachable, tree-free, un-occupied cell within the farm radius (a
    // dead-end pocket, or a shack whose few walkable neighbors are all tree/troll-occupied),
    // the OLD code still issued PICK whenever the tent held a banana. The picked banana then
    // had nowhere to plant; band 80 (full->bank) was suppressed for a banana-carrying
    // starter expecting to plant it (gated on the tree-COUNT `base_trees < farm_cap`, not a
    // free-CELL check — the bug's heart), so the fallback band 10 banked it right back next
    // turn, and PICK fired again the turn after — an infinite PICK<->DROP loop that also
    // parked the starter on a scarce shack-adjacent cell the chopper needs for banking.
    // Gating bands 88/50/49 on `plant_cell.is_some()` fixed the PICK half; band 80 below,
    // gated the same way (reviewer MINOR fix), closes the other half — a carried banana with
    // nowhere reachable to plant is banked, not hoarded waiting for a spot that never opens.
    let plant_cell: Option<Cell> = if plan.base_trees < plan.farm_cap {
        state
            .walkable
            .iter()
            .filter(|c| {
                plan.farm_d.get(*c).map_or(false, |&fd| fd <= plan.farm_r) && d.contains_key(*c)
            })
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
            out.push(Cand {
                kind: Kind::Bank,
                target: None,
                value: 95 * BAND - e,
            });
        }
    }
    // full -> bank (band 80) — reviewer MINOR fix: was `plan.base_trees < plan.farm_cap` (a
    // tree COUNT), now `plant_cell.is_some()` (an actual reachable free CELL), matching the
    // gate bands 88/50/49 already use. A carried banana with no plantable cell should be
    // banked, not held waiting for room that will never materialize.
    if u.free_capacity() == 0 && !(!is_chopper && u.carry[BANANA] > 0 && plant_cell.is_some()) {
        out.push(Cand {
            kind: Kind::Bank,
            target: None,
            value: 80 * BAND,
        });
    }

    if is_chopper {
        // fell targets (band 70): standing (CHOP now) or travel; value differentiates by
        // steps + chop-time exactly like the cascade's nearest_fell metric.
        for p in state
            .trees
            .iter()
            .filter(|p| fell_ok(p) && own_half(p) && within_roam(p))
        {
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
            let pbonus = pressure_bonus(pc, race_pen);
            if pc == u.pos() {
                // standing on a fellable tree: FINISH IT (cascade branch order) — band 72
                // outranks every travel-fell so invested chops are never abandoned.
                out.push(Cand {
                    kind: Kind::ChopHere,
                    target: Some(pc),
                    value: 72 * BAND - chop_t - race_pen - deny_pen + pbonus,
                });
            } else {
                out.push(Cand {
                    kind: Kind::MoveTo,
                    target: Some(pc),
                    value: 70 * BAND - (steps + chop_t) - race_pen - deny_pen + pbonus,
                });
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
                out.push(Cand {
                    kind: Kind::ChopHere,
                    target: Some(pc),
                    value: 31 * BAND - chop_t - race_pen,
                });
            } else {
                out.push(Cand {
                    kind: Kind::MoveTo,
                    target: Some(pc),
                    value: 30 * BAND - (steps + chop_t) - race_pen,
                });
            }
        }
        // partial bank / park (band 10)
        out.push(Cand {
            kind: if u.total_carried() > 0 {
                Kind::Bank
            } else {
                Kind::Park
            },
            target: None,
            value: 10 * BAND,
        });
    } else {
        // `plant_cell` is hoisted above (before band 95/80) so band 80 can share it too —
        // see its doc comment there. Bands 88 (below) and 50/49 (further down) just consume
        // it.
        // 1) plant carried banana (band 88) at the best free base cell
        if u.carry[BANANA] > 0 {
            if let Some(tc) = plant_cell {
                let kind = if u.pos() == tc {
                    Kind::PlantHere
                } else {
                    Kind::MoveTo
                };
                out.push(Cand {
                    kind,
                    target: Some(tc),
                    value: 88 * BAND - eta(&d, tc, ms),
                });
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
                                && state
                                    .water_cells
                                    .iter()
                                    .any(|w| manhattan(*w, p.pos()) == 1))))
                    || plan.phase == Phase::Hoard; // Hoard wants EVERYTHING ripe standing under foot too
                if want {
                    out.push(Cand {
                        kind: Kind::Harvest,
                        target: Some(u.pos()),
                        value: 75 * BAND,
                    });
                }
            }
        }
        // B2 (Hoard): wallet-building — travel to ANY ripe fruit tree. Fruit is points AND
        // wallet fuel during Hoard, so there is no per-type targeting like the funding/printer
        // bands below (those stay as-is; the matcher just takes the max of every band pushed).
        if plan.phase == Phase::Hoard {
            for p in state
                .trees
                .iter()
                .filter(|p| p.fruits > 0 && d.contains_key(&p.pos()))
            {
                let pc = p.pos();
                out.push(Cand {
                    kind: Kind::MoveTo,
                    target: Some(pc),
                    value: 62 * BAND - eta(&d, pc, ms),
                });
            }
        }
        // 4) FUNDING (bands 60/58) — for the chopper OR a pending 3rd hand (R6b.2: the old
        // feeder never trained because post-funding nobody harvested plum/lemon/apple)
        if plan.want_chopper || plan.want_feeder {
            // v1.28.1: the chopper is EXISTENTIAL (60/58) but a 3rd hand is a LUXURY — its
            // funding (45/44) must never displace printer/seed work (50/48). The v1.28.0
            // regression: perpetual feeder-funding starved the farm on lemon-poor maps.
            let (fund_hi, fund_lo) = if plan.want_chopper {
                (60, 58)
            } else {
                (45, 44)
            };
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
                if state
                    .iron_cells
                    .iter()
                    .any(|ic| manhattan(u.pos(), *ic) == 1)
                {
                    let v = if ladder_funding { 65 } else { fund_hi };
                    out.push(Cand {
                        kind: Kind::Mine,
                        target: Some(u.pos()),
                        value: v * BAND,
                    });
                } else if let Some(c) = state
                    .iron_cells
                    .iter()
                    .flat_map(|ic| ortho_neighbors(*ic))
                    .filter(|c| d.contains_key(c))
                    .min_by_key(|c| (d[c], tie_mix(*c, salt)))
                {
                    let v = if ladder_funding { 64 } else { fund_hi };
                    out.push(Cand {
                        kind: Kind::MoveTo,
                        target: Some(c),
                        value: v * BAND - eta(&d, c, ms),
                    });
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
                out.push(Cand {
                    kind: Kind::MoveTo,
                    target: Some(pc),
                    value: fruit_band * BAND - eta(&d, pc, ms),
                });
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
                            && state
                                .water_cells
                                .iter()
                                .any(|w| manhattan(*w, p.pos()) == 1)))
            }) {
                let pc = p.pos();
                out.push(Cand {
                    kind: Kind::MoveTo,
                    target: Some(pc),
                    value: 52 * BAND - eta(&d, pc, ms),
                });
            }
            // v1.41.0-nopickloop: only PICK (or travel to pick) if a plantable cell
            // actually exists (plant_cell.is_some()) — picking a banana with nowhere to
            // plant it is pure waste that just re-parks the starter on a scarce cell.
            if inv[BANANA] > 0 && u.free_capacity() > 0 && plant_cell.is_some() {
                // target = shack: dedupes the pick errand across multiple hands (R6b.2)
                if manhattan(u.pos(), shack) == 1 {
                    out.push(Cand {
                        kind: Kind::Pick,
                        target: Some(shack),
                        value: 50 * BAND,
                    });
                } else {
                    out.push(Cand {
                        kind: Kind::Park,
                        target: Some(shack),
                        value: 50 * BAND - 1,
                    });
                }
            }
        }
        // 6) chop help (band 40) + anti-starvation (band 30)
        if plan.starter_chop && u.chop_power > 0 {
            for p in state
                .trees
                .iter()
                .filter(|p| fell_ok(p) && own_half(p) && within_roam(p))
            {
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
                let pbonus = pressure_bonus(pc, race_pen);
                if pc == u.pos() {
                    out.push(Cand {
                        kind: Kind::ChopHere,
                        target: Some(pc),
                        value: 42 * BAND - chop_t - race_pen + pbonus,
                    });
                } else {
                    out.push(Cand {
                        kind: Kind::MoveTo,
                        target: Some(pc),
                        value: 40 * BAND - (steps + chop_t) - race_pen + pbonus,
                    });
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
                    let chop_t =
                        ((p.health + u.chop_power.max(1) - 1) / u.chop_power.max(1)) as i64;
                    let race_pen = match race(pc, steps) {
                        None => continue, // doomed: they fell it before we arrive — skip, don't donate the travel
                        Some(pen) => pen,
                    };
                    if pc == u.pos() {
                        out.push(Cand {
                            kind: Kind::ChopHere,
                            target: Some(pc),
                            value: 31 * BAND - chop_t - race_pen,
                        });
                    } else {
                        out.push(Cand {
                            kind: Kind::MoveTo,
                            target: Some(pc),
                            value: 30 * BAND - (steps + chop_t) - race_pen,
                        });
                    }
                }
            }
        }
        // 6.5) IDLE-FRUIT (band 38, design D1 — champion loss taxonomy 2026-07-08 morning,
        // docs/silver-experiment-log.md: 45% of all losses are opponents out-fruiting us,
        // HARVEST+DROP 91-307 vs our flat 20-90). Strictly ABOVE anti-starvation (31/30) —
        // never competes with keeping the wood supply alive — and strictly BELOW chop-help
        // (42/40) and every printer/funding band above it (52/50/49/48/45/44/63/64/65/60/58) —
        // this is the fix for the v1.24.0-fruitbank trap (arena -1.0), which ranked
        // fruit-chasing ABOVE chop-help and lost. Because every one of those higher bands
        // already claims its own trees first, band 38 only ever wins the joint assignment on
        // a turn where nothing more valuable was available — it converts an otherwise-idle
        // turn into fruit points and never displaces wood work, seed work, or funding. No
        // per-type/own-half/roam gating on purpose ("harvest ANY ripe fruit"); mirrors the
        // ChopHere/MoveTo split used by every other band in this function.
        if u.harvest_power > 0 && u.free_capacity() > 0 {
            for p in state
                .trees
                .iter()
                .filter(|p| p.fruits > 0 && d.contains_key(&p.pos()))
            {
                let pc = p.pos();
                let steps = eta(&d, pc, ms);
                // reviewer IMPORTANT follow-up: same race check every other tree-targeting band
                // uses (70/72, 40/42, 30/31) — an enemy chopper already standing on this tree
                // fells it before we arrive, so chasing it donates the travel just like the
                // wood-fell case (doomed-target chasing). Unlike those bands, a joinable race
                // (Some(pen)) does NOT subtract the share-penalty: sharing a cell with an enemy
                // CHOPPER while WE harvest fruit isn't a wood-split situation (apply_chop's
                // round-robin split is a wood-only mechanic) — Some(_) here only means "not
                // doomed"; a same-cell Harvest (steps=0) is never doomed in practice (their_turns
                // is 0 only if the tree's health is already 0, which cannot coexist with the
                // `p.fruits > 0` filter above), so this uniform pre-branch check costs it nothing.
                if race(pc, steps).is_none() {
                    continue; // doomed: they fell it before we arrive — skip, don't donate the travel
                }
                if pc == u.pos() {
                    out.push(Cand {
                        kind: Kind::Harvest,
                        target: Some(pc),
                        value: 38 * BAND,
                    });
                } else {
                    out.push(Cand {
                        kind: Kind::MoveTo,
                        target: Some(pc),
                        value: 38 * BAND - steps,
                    });
                }
            }
        }
        // fallback (band 10)
        out.push(Cand {
            kind: if u.total_carried() > 0 {
                Kind::Bank
            } else {
                Kind::Park
            },
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

fn select_assignments(state: &State, plan: &Plan, my: &[Troll]) -> Assignments {
    let salt = tie_salt(state);
    let mut ids: Vec<i32> = my.iter().map(|t| t.id).collect();
    ids.sort();
    let trolls: Vec<&Troll> = ids
        .iter()
        .map(|id| my.iter().find(|t| t.id == *id).unwrap())
        .collect();
    let cands: Vec<Vec<Cand>> = trolls
        .iter()
        .map(|t| candidates(state, plan, my, t, salt))
        .collect();
    let claim_infos: Vec<Vec<Option<ClaimInfo>>> = trolls
        .iter()
        .zip(cands.iter())
        .map(|(t, cs)| {
            let d = bfs_distances(&state.walkable, &[t.pos()]);
            cs.iter()
                .map(|c| {
                    let steps = c.target.map_or(0, |tc| eta(&d, tc, t.movement_speed));
                    claim_info(state, c, steps)
                })
                .collect()
        })
        .collect();

    let n = ids.len();
    let mut best: Option<(i64, Vec<usize>)> = None;
    let mut pick = vec![0usize; n];
    if n > 0 {
        loop {
            let mut ok = true;
            for i in 0..n {
                for j in 0..i {
                    if let (Some(a), Some(b)) = (claim_infos[i][pick[i]], claim_infos[j][pick[j]]) {
                        if claims_conflict(a, b) {
                            ok = false;
                            break;
                        }
                    }
                }
                if !ok {
                    break;
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

    Assignments {
        ids,
        cands,
        picks: best.map(|(_, picks)| picks).unwrap_or_default(),
    }
}

fn render_assignments(
    state: &State,
    plan: &Plan,
    my: &[Troll],
    assignments: &Assignments,
    update_last_target: bool,
) -> HashMap<i32, String> {
    // render (troll-id order; camp-cell claiming stays deterministic via claimed_drop)
    let mut cmd_by_id: HashMap<i32, String> = HashMap::new();
    let mut claimed_drop: HashSet<Cell> = HashSet::new();
    if !assignments.picks.is_empty() {
        for (i, id) in assignments.ids.iter().enumerate() {
            let u = my.iter().find(|t| t.id == *id).unwrap();
            let d = bfs_distances(&state.walkable, &[u.pos()]);
            let c = &assignments.cands[i][assignments.picks[i]];
            if update_last_target {
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
            }
            let cmd = match (&c.kind, c.target) {
                (Kind::Bank, _) => motion::bank_cmd(state, plan.shack, u, &d, &mut claimed_drop),
                // idle band-10 (target None) gets the ring-2-aware scarce-camp step-back;
                // the band-49 park-to-pick ERRAND (target Some(shack)) never does — it is
                // goal-directed (must reach manhattan==1 to unlock PICK) and the ring-2
                // redirect has no such convergence guarantee (reviewer CRITICAL fix, see
                // motion::park_cmd's doc comment).
                (Kind::Park, park_target) => motion::park_cmd(
                    state,
                    plan.shack,
                    u,
                    &d,
                    &mut claimed_drop,
                    park_target.is_none(),
                ),
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

fn move_intents(cmd_by_id: &HashMap<i32, String>) -> Vec<(i32, Cell)> {
    let mut intents: Vec<(i32, Cell)> = cmd_by_id
        .iter()
        .filter_map(|(id, c)| {
            let p: Vec<&str> = c.split_whitespace().collect();
            if p.len() == 4 && p[0] == "MOVE" {
                Some((*id, (p[2].parse().ok()?, p[3].parse().ok()?)))
            } else {
                None
            }
        })
        .collect();
    intents.sort();
    intents
}

fn pin_landing(my: &[Troll], cmd_by_id: &mut HashMap<i32, String>, landing: HashMap<i32, Cell>) {
    for (id, cell) in landing {
        let cur = my.iter().find(|t| t.id == id).map(|t| t.pos());
        if cur != Some(cell) {
            cmd_by_id.insert(id, format!("MOVE {} {} {}", id, cell.0, cell.1));
        }
    }
}

fn best_progress_without_stationary(
    state: &State,
    mover: &Troll,
    goal: Cell,
    stationary: &HashSet<Cell>,
) -> Option<i32> {
    let dg = bfs_distances(&state.walkable, &[goal]);
    let dp = bfs_distances(&state.walkable, &[mover.pos()]);
    let here = *dg.get(&mover.pos())?;
    let mut best = 0;
    for c in &state.walkable {
        if stationary.contains(c) {
            continue;
        }
        let Some(&from_here) = dp.get(c) else {
            continue;
        };
        if from_here == 0 || from_here > mover.movement_speed {
            continue;
        }
        let Some(&to_goal) = dg.get(c) else {
            continue;
        };
        let progress = here - to_goal;
        if progress >= 0 {
            best = best.max(progress);
        }
    }
    Some(best)
}

fn blocker_landing_progress(
    state: &State,
    mover: &Troll,
    goal: Cell,
    blocker_cell: Cell,
) -> Option<i32> {
    if !state.walkable.contains(&blocker_cell) {
        return None;
    }
    let dg = bfs_distances(&state.walkable, &[goal]);
    let dp = bfs_distances(&state.walkable, &[mover.pos()]);
    let here = *dg.get(&mover.pos())?;
    let from_here = *dp.get(&blocker_cell)?;
    if from_here == 0 || from_here > mover.movement_speed {
        return None;
    }
    let progress = here - *dg.get(&blocker_cell)?;
    (progress > 0).then_some(progress)
}

fn candidate_conflicts(
    assignments: &Assignments,
    blocker_idx: usize,
    target: Option<Cell>,
) -> bool {
    let Some(target) = target else {
        return false;
    };
    assignments.ids.iter().enumerate().any(|(i, _)| {
        i != blocker_idx && assignments.cands[i][assignments.picks[i]].target == Some(target)
    })
}

fn candidate_can_move_for_yield(plan: &Plan, u: &Troll, cand: &Cand) -> bool {
    match cand.kind {
        Kind::MoveTo | Kind::Park => true,
        Kind::Bank => manhattan(u.pos(), plan.shack) != 1,
        Kind::ChopHere | Kind::PlantHere | Kind::Harvest | Kind::Mine | Kind::Pick => false,
    }
}

fn reselect_blocker_for_yield(
    plan: &Plan,
    my: &[Troll],
    assignments: &mut Assignments,
    blocker_id: i32,
) -> bool {
    let Some(blocker_idx) = assignments.idx(blocker_id) else {
        return false;
    };
    let Some(u) = my.iter().find(|t| t.id == blocker_id) else {
        return false;
    };
    let old_pick = assignments.picks[blocker_idx];
    let old_target = assignments.cands[blocker_idx][old_pick].target;
    for new_pick in 0..assignments.cands[blocker_idx].len() {
        if new_pick == old_pick {
            continue;
        }
        let cand = &assignments.cands[blocker_idx][new_pick];
        if old_target.is_some() && cand.target == old_target {
            continue;
        }
        if candidate_conflicts(assignments, blocker_idx, cand.target) {
            continue;
        }
        if !candidate_can_move_for_yield(plan, u, cand) {
            continue;
        }
        assignments.picks[blocker_idx] = new_pick;
        return true;
    }
    false
}

fn yield_pass(
    state: &State,
    plan: &Plan,
    my: &[Troll],
    assignments: &mut Assignments,
    intents: &[(i32, Cell)],
    landing: &HashMap<i32, Cell>,
) -> bool {
    #[derive(Clone)]
    struct YieldCandidate {
        mover_id: i32,
        blocker_id: i32,
        mover_value: i64,
        blocker_value: i64,
    }

    let moving: HashSet<i32> = intents.iter().map(|(id, _)| *id).collect();
    let stationary_cells: HashSet<Cell> = my
        .iter()
        .filter(|t| !moving.contains(&t.id))
        .map(|t| t.pos())
        .collect();
    let stationary: Vec<&Troll> = my.iter().filter(|t| !moving.contains(&t.id)).collect();
    let mut pairs: Vec<YieldCandidate> = Vec::new();

    for (mover_id, goal) in intents {
        let Some(mover) = my.iter().find(|t| t.id == *mover_id) else {
            continue;
        };
        if landing.get(mover_id) != Some(&mover.pos()) {
            continue;
        }
        let Some(mover_value) = assignments.selected_value(*mover_id) else {
            continue;
        };
        let Some(normal_best) =
            best_progress_without_stationary(state, mover, *goal, &stationary_cells)
        else {
            continue;
        };
        if normal_best > 0 {
            continue;
        }
        for blocker in &stationary {
            let Some(blocker_value) = assignments.selected_value(blocker.id) else {
                continue;
            };
            if mover_value <= blocker_value {
                continue;
            }
            let Some(blocked_progress) =
                blocker_landing_progress(state, mover, *goal, blocker.pos())
            else {
                continue;
            };
            if blocked_progress > normal_best {
                pairs.push(YieldCandidate {
                    mover_id: *mover_id,
                    blocker_id: blocker.id,
                    mover_value,
                    blocker_value,
                });
            }
        }
    }

    pairs.sort_by_key(|p| (-p.mover_value, p.blocker_value, p.mover_id, p.blocker_id));
    for p in pairs {
        let mut trial = assignments.clone();
        if reselect_blocker_for_yield(plan, my, &mut trial, p.blocker_id) {
            *assignments = trial;
            if DEBUG {
                eprintln!(
                    "@TFYIELD t={} blocker={} mover={}",
                    state.turn, p.blocker_id, p.mover_id
                );
            }
            return true;
        }
    }
    false
}

/// Joint assignment: exhaustive over per-troll top-K candidates, maximize total value,
/// conflicting target claims forbidden, ties broken by the lexicographic pick vector.
pub fn assign(state: &State, plan: &Plan, my: &[Troll]) -> HashMap<i32, String> {
    let assignments = select_assignments(state, plan, my);
    render_assignments(state, plan, my, &assignments, true)
}

/// Assignment plus the live L3 motion pass. This keeps all task economics in the
/// joint matcher, then lets one lower-value stationary teammate yield to an urgent
/// blocked mover before final MOVE landing cells are pinned.
pub fn assign_resolved(state: &State, plan: &Plan, my: &[Troll]) -> HashMap<i32, String> {
    let mut assignments = select_assignments(state, plan, my);
    let initial_cmds = render_assignments(state, plan, my, &assignments, false);
    let initial_intents = move_intents(&initial_cmds);
    let initial_landing = motion::solve_moves(state, my, &initial_intents);

    let yielded = yield_pass(
        state,
        plan,
        my,
        &mut assignments,
        &initial_intents,
        &initial_landing,
    );
    let mut cmd_by_id = render_assignments(state, plan, my, &assignments, true);
    let landing = if yielded {
        let intents = move_intents(&cmd_by_id);
        motion::solve_moves(state, my, &intents)
    } else {
        initial_landing
    };
    pin_landing(my, &mut cmd_by_id, landing);
    cmd_by_id
}
