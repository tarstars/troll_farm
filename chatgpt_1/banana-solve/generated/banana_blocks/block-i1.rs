// ===========================================================================
// I1 — BananaBot wrapper (banana wood-printer restoration r2).
// Inserted immediately BEFORE the parent anchor `pub struct SecureOrchardBot{`
// (inside `mod bot::moisan`, so same-module field visibility applies).
//
// Contract: invariant-spec-2026-08-04.md I-1..I-29 plus the integrator's
// 2026-08-04 corrections:
//   C1 resident = the starter (min-id own unit at turn 1);
//   C2 turn-1 arbitration decided BEFORE the first delegation via a READ-ONLY
//      replica of SecureOrchardBot::initialize's geometry-eligibility test;
//   C3 single protected mother: at most ONE diagonal-of-tent banana mother;
//      mother floor counts live bananas on diag(tent);
//   C4 ownership/safety ETAs use the resident's ETA, not a min over workers;
//   C5 mother protection through the dedicated YamoBot seam field
//      `banana_protected_cell` (candidate retain-filter, same pattern as
//      `external_protected_tree`) plus post-edit + resolver forbidden set;
//   C6 hysteresis H=3 / eps=1.0 implemented literally per spec section (e);
//   C7 dynamic ownership-loss response (full I-10a; CONVERSION_RACE_ORACLE
//      unification, round 4, 2026-08-05): ownership of the mother (I-7,
//      committed-harvester ETA, ties conceded) is re-evaluated on EVERY
//      active turn — wood-cycle, camping and banking turns included — and
//      at the first turn it flips false the resident responds
//      deterministically, preempting its current activity: harvest now iff
//      a ripe fruit is harvestable immediately; else convert (CHOP the
//      flipped mother) iff CONVERSION_RACE_ORACLE reports feasible — the
//      absolute conversion-completion turn (growth-only predict over the
//      travel eta, then MoisanBot::chop_outcome, growth during travel and
//      chopping included) is STRICTLY earlier than the opponent's absolute
//      earliest EXECUTABLE HARVEST turn (arrival AND ripeness,
//      max(t + eta_opp_h, first_fruit_turn)); the convert decision latches
//      until the mother falls; else
//      the Abandoned transition — cease all investment in the asset (no
//      PLANT, no MOVE toward the mother; rev. 2026-08-06: the resident
//      banks leftovers and is then released to the inner economy, while
//      the persistent protected-cell claim keeps the inner policy from
//      reinvesting in the lost asset). The single
//      sanctioned response deferral is an already-committed banking DROP
//      executing at the flip turn itself (I-10a/I-19: the response then
//      begins wood-free at t + 1). D-8's mother-protection is scoped to
//      NON-flipped mothers: the convert-branch chop is the specified
//      ownership-loss response, not a D-8 violation;
//   C8 single-door banking serializes deterministically (resident priority in
//      the conflict resolver, inherited id order otherwise).
//
// Dormant/disabled turns are a structural identity: both seam fields are None
// and the command vector is returned untouched (acceptance check 4).
// Comments are erased by cgauto/compact_rust_source.py; the compacted form of
// this file is the exact I1 insertion string.
// ===========================================================================

/// Lifecycle phases (B1..B9): Dormant until the deterministic activation
/// predicate fires (I-1/I-16 + ring checkpoint), Active while the plot runs,
/// Abandoned permanently once the feature is impossible or past deadline.
#[derive(Clone, Copy, Eq, PartialEq)]
enum BananaPhase {
    Dormant,
    Active,
    Abandoned,
}

/// Target kinds of the resident's commitment state. The derived order is the
/// second component of the strict total order (score, kind, cell) of I-26.
#[derive(Clone, Copy, Eq, PartialEq, Ord, PartialOrd)]
enum BananaTask {
    Chop,
    Plant,
    Harvest,
    Bank,
    Boot,
    Idle,
}

pub struct BananaBot {
    inner: SecureOrchardBot,
    // None until the turn-1 arbitration decision (I-27/I-28): Some(true) iff
    // the orchard's initialize would NOT find geometry on this map.
    banana_enabled: Option<bool>,
    banana_phase: BananaPhase,
    // The resident: the starter (min own id), fixed at activation (C1).
    banana_worker: Option<i32>,
    // I-2: at most one bank-bootstrap PICK per game.
    banana_bootstrap_used: bool,
    // Commitment state of spec section (e): (target kind, target cell),
    // hold age, consecutive blocked turns, and last-position bookkeeping.
    banana_target: Option<(BananaTask, Cell)>,
    banana_hold_age: i32,
    banana_blocked_turns: i32,
    banana_last_cell: Option<Cell>,
    banana_last_move: bool,
    // I-10a Abandoned-after-ownership-loss (C7, rev. 2026-08-06): while
    // true the banana lifecycle has ceased all investment in the lost
    // asset. The resident stays reserved ONLY while banking leftover
    // cargo; once empty it is released to the inner economy (spec
    // Revision 2026-08-06 — the worker reservation does not survive the
    // Abandoned transition). Reinvestment in the lost asset is blocked by
    // the persistent protected-cell claim instead (F-C2).
    banana_lost: bool,
    // F-D2 (rev. 2026-08-06): consecutive active turns whose chosen
    // candidate was Idle. At 3 the reservation is released until the
    // first turn a non-Idle candidate exists (starvation release).
    banana_idle_streak: i32,
    // F-B3 (rev. 2026-08-06): minimal BFS distance achieved from the
    // worker to the held target while holding it. A post-MOVE turn whose
    // distance did not drop below this minimum counts as blocked, so
    // two-cell resolver bounces (position changes, no progress) feed the
    // clause-1 blocked counter exactly like standing still.
    banana_best_dist: Option<i32>,
    // F-D1 (rev. 2026-08-06): true only from the ownership-loss turn until
    // the leftover cargo the resident held AT the loss is banked. Once it
    // clears, the resident belongs to the inner economy permanently —
    // cargo it later acquires under inner control is the inner's business,
    // never re-captured by the wrapper (re-capturing produced an inner
    // PICK / wrapper DROP churn, D-2).
    banana_lost_banking: bool,
    // Exact identity of the one diagonal mother founded by this wrapper.
    // Never recomputed from arbitrary live bananas: an opponent plant cannot
    // migrate the claim or ownership response.
    banana_mother: Option<Cell>,
}

impl BananaBot {
    pub fn new(inner: SecureOrchardBot) -> Self {
        Self {
            inner,
            banana_enabled: None,
            banana_phase: BananaPhase::Dormant,
            banana_worker: None,
            banana_bootstrap_used: false,
            banana_target: None,
            banana_hold_age: 0,
            banana_blocked_turns: 0,
            banana_last_cell: None,
            banana_last_move: false,
            banana_lost: false,
            banana_idle_streak: 0,
            banana_best_dist: None,
            banana_lost_banking: false,
            banana_mother: None,
        }
    }

    /// READ-ONLY replica of SecureOrchardBot::initialize's geometry test (C2):
    /// true iff the orchard would set `geometry = Some(..)` at turn 1.
    /// Mirrors the parent gate-for-gate: >= 2 sorted doors, non-empty initial
    /// natural plants, all naturals door-reachable with median return >= 8.0,
    /// and at least one plant-free water-adjacent door with enemy door
    /// distance >= 11. Does not mutate any inner state.
    fn banana_orchard_geometry(view: &GameState) -> bool {
        let banana_natural: Vec<Cell> = view
            .plants
            .iter()
            .filter(|plant| plant.health > 0)
            .map(|plant| plant.cell)
            .collect();
        let mut doors: Vec<Cell> = ortho_neighbors(view.shacks[0])
            .into_iter()
            .filter(|cell| view.walkable.contains(cell))
            .collect();
        doors.sort_unstable();
        if doors.len() < 2 || banana_natural.is_empty() {
            return false;
        }
        let enemy_doors: Vec<Cell> = ortho_neighbors(view.shacks[1])
            .into_iter()
            .filter(|cell| view.walkable.contains(cell))
            .collect();
        let home_distance = bfs_distances(&view.walkable, &doors);
        let enemy_distance = bfs_distances(&view.walkable, &enemy_doors);
        let natural_return: Vec<i32> = banana_natural
            .iter()
            .filter_map(|cell| home_distance.get(cell).copied())
            .collect();
        if natural_return.len() != banana_natural.len()
            || SecureOrchardBot::median(natural_return) < 8.0
        {
            return false;
        }
        doors.iter().any(|door| {
            view.plant_at(*door).is_none()
                && view.water.iter().any(|water| is_adjacent(*water, *door))
                && enemy_distance.get(door).copied().unwrap_or(10_000) >= 11
        })
    }

    /// The Chebyshev-1 tent ring (I-12): walkable cells at Chebyshev distance
    /// exactly 1 from the own tent; |Ring| <= 8.
    fn banana_ring(view: &GameState) -> Vec<Cell> {
        let tent = view.shacks[0];
        view.walkable
            .iter()
            .copied()
            .filter(|cell| (cell.0 - tent.0).abs().max((cell.1 - tent.1).abs()) == 1)
            .collect()
    }

    /// Live banana plant at `cell`, if any.
    fn banana_live(view: &GameState, cell: Cell) -> Option<&Plant> {
        view.plant_at(cell)
            .map(|index| &view.plants[index])
            .filter(|plant| plant.kind == PlantKind::Banana && plant.health > 0)
    }

    /// The single protected mother, latched at our own founding decision.
    /// A natural/opponent banana is never adopted merely because it is the minimum
    /// diagonal cell.  The claim lapses when the exact latched plant is gone.
    fn banana_mother_cell(&self, view: &GameState) -> Option<Cell> {
        self.banana_mother
            .filter(|cell| Self::banana_live(view, *cell).is_some())
    }

    /// Minimal opponent ETA to `cell` over harvesters (chopper=false) or
    /// choppers (chopper=true); unreachable = 10000 (spec section 0).
    fn banana_opponent_eta(view: &GameState, cell: Cell, chopper: bool) -> i32 {
        let dist = bfs_distances(&view.walkable, &[cell]);
        view.units
            .iter()
            .filter(|unit| unit.player == 1)
            .filter(|unit| {
                if chopper {
                    unit.stats.chop_power > 0
                } else {
                    unit.stats.harvest_power > 0
                }
            })
            .filter_map(|unit| {
                dist.get(&unit.cell)
                    .map(|d| MoisanBot::ceil_div(*d, unit.stats.movement_speed))
            })
            .min()
            .unwrap_or(10_000)
    }

    /// Growth-only forward simulation of a live plant over `turns` growth
    /// ticks — the CONVERSION_RACE_ORACLE `predict_tree` mirror (spec
    /// Revision 2026-08-05: "state(t+k) of an unchopped tree =
    /// predict_tree(S_t.plant, k)" under NATURAL growth). Deliberately not
    /// MoisanBot::predict_tree: the inner policy's predictor folds in an
    /// opponent-attrition heuristic (predicted_opp_chop) that the oracle
    /// forbids — the oracle's arrival state is pure growth.
    fn banana_predict_growth(view: &GameState, plant: &Plant, turns: i32) -> PredictedTree {
        let near_water = view.water.iter().any(|water| is_adjacent(*water, plant.cell));
        let mut size = plant.size;
        let mut health = plant.health;
        let mut fruits = plant.fruits;
        let mut cooldown = plant.cooldown;
        for _ in 0..turns {
            if cooldown > 0 {
                cooldown -= 1;
            }
            if cooldown == 0 && health > 0 {
                if size < 4 {
                    size += 1;
                    health += crate::game::rules::tree_health_params(plant.kind).1;
                    cooldown = effective_cooldown(plant.kind, near_water);
                } else if fruits < 3 {
                    fruits += 1;
                    cooldown = effective_cooldown(plant.kind, near_water);
                }
            }
        }
        PredictedTree {
            size,
            health,
            cooldown,
        }
    }

    /// I-5 late cutoff, applied to every ring plant decision (conservative:
    /// the orthogonal wood-slot formula, the stricter of the two clauses):
    /// no PLANT after 300 - (2*CD(c) + ceil(health(2)/chop) + 2).
    fn banana_plant_late(view: &GameState, cell: Cell, chop: i32) -> bool {
        let near_water = view.water.iter().any(|water| is_adjacent(*water, cell));
        let cooldown = effective_cooldown(PlantKind::Banana, near_water);
        let cut = MoisanBot::ceil_div(tree_health(PlantKind::Banana, 2), chop);
        view.turn > TOTAL_TURNS - (2 * cooldown + cut + 2)
    }

    /// Plant-eligibility of a ring vacancy (I-10 + I-5 + C3/C4): plant-free,
    /// not occupied by any other unit, not past the late cutoff, diagonal
    /// only while no live diagonal mother exists (single-mother cap), and
    /// plant-time safety with the RESIDENT's ETA: eta_opp_h > eta_res
    /// (strict, ties forbidden) and eta_opp_x > 2.
    fn banana_vacant_ok(view: &GameState, worker: &Unit, cell: Cell, diag_taken: bool) -> bool {
        if view.plant_at(cell).is_some() {
            return false;
        }
        if view
            .units
            .iter()
            .any(|other| other.id != worker.id && other.cell == cell)
        {
            return false;
        }
        if Self::banana_plant_late(view, cell, worker.stats.chop_power) {
            return false;
        }
        let tent = view.shacks[0];
        if !is_adjacent(cell, tent) && diag_taken {
            return false;
        }
        let dist = bfs_distances(&view.walkable, &[cell]);
        let resident_eta = dist
            .get(&worker.cell)
            .map(|d| MoisanBot::ceil_div(*d, worker.stats.movement_speed))
            .unwrap_or(10_000);
        if resident_eta >= 10_000 {
            return false;
        }
        let near_water = view.water.iter().any(|water| is_adjacent(*water, cell));
        let cooldown = effective_cooldown(PlantKind::Banana, near_water);
        let eta_h = Self::banana_opponent_eta(view, cell, false);
        let eta_x = Self::banana_opponent_eta(view, cell, true);
        if is_adjacent(cell, tent) {
            // Consumable wood trees are felled at size two, before fruit exists.
            // Still require enough uncontested time to grow and bank the cut;
            // this removes the opponent-chop-at-plant defect without pretending
            // an orthogonal tree is a renewable mother.
            let service = resident_eta + cooldown + 3;
            return eta_x > service;
        }
        // A renewable diagonal mother is founded only when its first fruit is
        // private under the current positions.  Four cooldown periods is the
        // exact conservative fresh-plant-to-first-fruit horizon (creation tick
        // included); ties are unsafe because cross-player co-location and
        // last-fruit duplication are legal.
        let first_fruit = resident_eta + 4 * cooldown + 2;
        eta_h > first_fruit && eta_x > first_fruit
    }


    /// Conservative activation gate.  Banana play starts only on an open,
    /// multi-door ring where one private diagonal mother and one consumable
    /// orthogonal wood slot can be founded without interfering with the newly
    /// trained economy.  Risky maps remain byte-identical to the stable parent.
    fn banana_activation_safe(view: &GameState, worker: &Unit) -> bool {
        let tent = view.shacks[0];
        let doors: Vec<Cell> = ortho_neighbors(tent)
            .into_iter()
            .filter(|cell| view.walkable.contains(cell))
            .collect();
        if doors.len() < 3 {
            return false;
        }
        if view.units.iter().any(|unit| {
            unit.player == 0 && unit.id != worker.id && unit.total_carried() > 0
        }) {
            return false;
        }
        // Start from a clean plot; otherwise provenance and the single-mother
        // invariant are not observable.
        if Self::banana_ring(view)
            .into_iter()
            .any(|cell| Self::banana_live(view, cell).is_some())
        {
            return false;
        }
        let mut safe_diag = false;
        let mut safe_orth = false;
        for cell in Self::banana_ring(view) {
            if !Self::banana_vacant_ok(view, worker, cell, false) {
                continue;
            }
            if is_adjacent(cell, tent) {
                safe_orth = true;
                continue;
            }
            // The resident/claim cell must not be an articulation barrier for
            // any peer's route to every bank door.
            let mut walk = view.walkable.clone();
            walk.remove(&cell);
            let route_safe = view.units.iter().filter(|unit| {
                unit.player == 0 && unit.id != worker.id
            }).all(|unit| {
                let dist = bfs_distances(&walk, &[unit.cell]);
                doors.iter().any(|door| dist.contains_key(door))
            });
            if route_safe {
                safe_diag = true;
            }
        }
        safe_diag && safe_orth
    }

    /// Banking candidates (I-19/I-20/I-21, B7): DROP on the current door or
    /// MOVE toward each reachable door. On single-door maps this serializes
    /// naturally (C8): one door cell, resident priority in the resolver.
    /// F-B2 (rev. 2026-08-06): a door occupied by another unit is skipped
    /// while any free door exists (mirror of the inner policy's own
    /// occupied-door filter and of `banana_vacant_ok`'s occupancy check) —
    /// targeting an occupied door only feeds the resolver's detour
    /// tie-break and produces the period-2 banking bounce (diagnosis-r6
    /// family (b2)); occupied doors stay eligible only when no free door
    /// exists.
    fn banana_bank(
        view: &GameState,
        worker: &Unit,
        from_worker: &BTreeMap<Cell, i32>,
        on_score: i32,
        move_score: i32,
        out: &mut Vec<(i32, BananaTask, Cell, String)>,
    ) {
        let occupied = |cell: Cell| {
            view.units
                .iter()
                .any(|other| other.id != worker.id && other.cell == cell)
        };
        let doors: Vec<Cell> = ortho_neighbors(view.shacks[0])
            .into_iter()
            .filter(|door| view.walkable.contains(door))
            .collect();
        let any_free = doors.iter().any(|door| !occupied(*door));
        for door in doors {
            if any_free && occupied(door) {
                continue;
            }
            if door == worker.cell {
                out.push((on_score, BananaTask::Bank, door, format!("DROP {}", worker.id)));
            } else if let Some(d) = from_worker.get(&door) {
                out.push((
                    move_score - MoisanBot::ceil_div(*d, worker.stats.movement_speed),
                    BananaTask::Bank,
                    door,
                    format!("MOVE {} {} {}", worker.id, door.0, door.1),
                ));
            }
        }
    }

    /// Post-abandonment action (I-10a branch 3, C7): no further investment
    /// in anything — bank leftover cargo at the nearest door (deterministic
    /// (distance, cell) minimum; banking is not asset investment), else
    /// WAIT. Never PLANT, never a mother-directed verb.
    fn banana_lost_action(view: &GameState, worker: &Unit) -> String {
        if worker.total_carried() > 0 {
            let from_worker = bfs_distances(&view.walkable, &[worker.cell]);
            let mut best: Option<(i32, Cell)> = None;
            for door in ortho_neighbors(view.shacks[0]) {
                if !view.walkable.contains(&door) {
                    continue;
                }
                if door == worker.cell {
                    return format!("DROP {}", worker.id);
                }
                if let Some(d) = from_worker.get(&door).copied() {
                    if best.map(|b| (d, door) < b).unwrap_or(true) {
                        best = Some((d, door));
                    }
                }
            }
            if let Some((_d, door)) = best {
                return format!("MOVE {} {} {}", worker.id, door.0, door.1);
            }
        }
        "WAIT".to_string()
    }

    /// Resident candidate set. Every entry is (score, kind, cell, command);
    /// the list always contains WAIT, so every active mode returns a definite
    /// command (I-25, no None fallthrough). Carried wood short-circuits to
    /// bank-only candidates (I-19/I-21: while wood-committed the only verbs
    /// are MOVE-to-door and DROP; D-4).
    fn banana_candidates(&self, view: &GameState, worker: &Unit) -> Vec<(i32, BananaTask, Cell, String)> {
        let tent = view.shacks[0];
        let mut out = vec![(0, BananaTask::Idle, worker.cell, "WAIT".to_string())];
        let from_worker = bfs_distances(&view.walkable, &[worker.cell]);
        if worker.carry[crate::game::types::WOOD] > 0 {
            Self::banana_bank(view, worker, &from_worker, 9_500, 9_000, &mut out);
            return out;
        }
        let banana_eta = |cell: Cell| {
            from_worker
                .get(&cell)
                .map(|d| MoisanBot::ceil_div(*d, worker.stats.movement_speed))
                .unwrap_or(10_000)
        };
        let diag_taken = self.banana_mother_cell(view).is_some();
        let carried = worker.carry[BANANA] > 0;
        // I-9 one-seed reservation (GREEN 2026-08-05): replant demand has
        // priority for AT MOST ONE carried seed; every additional carried
        // banana is surplus and must be on a bank path (door approach, then
        // DROP) BEFORE any further planting. While surplus is carried, no
        // Plant candidate is offered at all — planting resumes only once the
        // resident carries exactly the reserved seed again (a DROP at a door
        // banks the whole cargo, so the surplus window closes at the bank).
        let surplus = worker.carry[BANANA] > 1;
        let mut demand = false;
        for cell in Self::banana_ring(view) {
            let orth = is_adjacent(cell, tent);
            if let Some(plant) = Self::banana_live(view, cell) {
                let occupied = view
                    .units
                    .iter()
                    .any(|other| other.id != worker.id && other.cell == cell);
                // Orthogonal wood slots: cut at size >= 2 (I-4/I-14); the
                // diagonal mother is never a chop target of ours (D-8).
                if orth && plant.size >= 2 && worker.stats.chop_power > 0 && worker.free_capacity() > 0 {
                    if cell == worker.cell {
                        out.push((9_000, BananaTask::Chop, cell, format!("CHOP {}", worker.id)));
                    } else if !occupied {
                        out.push((
                            6_500 - banana_eta(cell),
                            BananaTask::Chop,
                            cell,
                            format!("MOVE {} {} {}", worker.id, cell.0, cell.1),
                        ));
                    }
                }
                // Diagonal mother service: harvest-only (B3).
                if !orth && plant.fruits > 0 && worker.stats.harvest_power > 0 && worker.free_capacity() > 0 {
                    if cell == worker.cell {
                        out.push((8_600, BananaTask::Harvest, cell, format!("HARVEST {}", worker.id)));
                    } else if !occupied {
                        out.push((
                            6_000 - banana_eta(cell),
                            BananaTask::Harvest,
                            cell,
                            format!("MOVE {} {} {}", worker.id, cell.0, cell.1),
                        ));
                    }
                }
            } else if Self::banana_vacant_ok(view, worker, cell, diag_taken) {
                demand = true;
                if carried && !surplus {
                    // Mother-founding priority (I-3 mother floor, B1): while
                    // no diagonal mother is alive, establishing one outranks
                    // any orthogonal wood-slot plant — otherwise the single
                    // bootstrap seed (I-2) can die as a wood tree and strand
                    // the lifecycle without a renewable fruit source.
                    let founding = !orth && !diag_taken;
                    let base = if founding {
                        8_900
                    } else if cell == worker.cell {
                        8_800
                    } else {
                        7_500
                    };
                    let command = if cell == worker.cell {
                        format!("PLANT {} BANANA", worker.id)
                    } else {
                        format!("MOVE {} {} {}", worker.id, cell.0, cell.1)
                    };
                    out.push((base - banana_eta(cell), BananaTask::Plant, cell, command));
                }
            }
        }
        // Bootstrap (I-2): at most one bank PICK per game, only while a
        // replant demand exists and nothing is carried.
        if !self.banana_bootstrap_used
            && worker.total_carried() == 0
            && view.inventories[0][BANANA] > 0
            && demand
            && worker.free_capacity() > 0
        {
            if is_adjacent(worker.cell, tent) && view.walkable.contains(&worker.cell) {
                out.push((6_800, BananaTask::Boot, worker.cell, format!("PICK {} BANANA", worker.id)));
            } else {
                for door in ortho_neighbors(tent) {
                    if view.walkable.contains(&door) {
                        if let Some(d) = from_worker.get(&door) {
                            out.push((
                                5_500 - MoisanBot::ceil_div(*d, worker.stats.movement_speed),
                                BananaTask::Boot,
                                door,
                                format!("MOVE {} {} {}", worker.id, door.0, door.1),
                            ));
                        }
                    }
                }
            }
        }
        // Banking (I-8/I-9): carried cargo with no replant demand (or
        // non-banana cargo) goes to the bank, and — one-seed reservation —
        // so does every carried banana beyond the single reserved seed,
        // BEFORE any further planting (surplus, I-9).
        if worker.total_carried() > 0 && (!carried || !demand || surplus) {
            Self::banana_bank(view, worker, &from_worker, 8_000, 7_000, &mut out);
        }
        out
    }

    /// One resident decision per turn, through the commitment rule of spec
    /// section (e) implemented literally (C6):
    ///   1. invalidation (candidate for the held target vanished, or 2
    ///      consecutive blocked turns) => recompute freely, hold_age = 0;
    ///   2. hold_age < H = 3 => keep the target unconditionally;
    ///   3. else switch only if score(best) >= score(held) + eps (eps = 1,
    ///      one travel turn in this scale); total order (score, kind, cell).
    /// The C7 ownership-loss response (full I-10a) acts BEFORE the
    /// candidate set on every active turn: an I-7 ownership flip of the
    /// mother forces the deterministic harvest-now / convert / abandon
    /// decision below, preempting whatever the resident was doing (sole
    /// deferral: the committed banking DROP at the flip turn, I-19). On
    /// flip-free turns the I-19 wood rule acts through the candidate set:
    /// wood commitment short-circuits to banking.
    /// Returns Some(command) when the wrapper controls the resident this
    /// turn, or None when the resident is released to the inner economy
    /// (F-D1 post-loss with nothing carried; F-D2 starvation release).
    fn banana_action(&mut self, view: &GameState, worker: &Unit) -> Option<String> {
        if view.units.iter().any(|unit| {
            unit.player == 0
                && unit.id != worker.id
                && unit.carry[crate::game::types::WOOD] > 0
        }) {
            self.banana_last_move = false;
            self.banana_last_cell = Some(worker.cell);
            return None;
        }
        // F-B3 (rev. 2026-08-06): a post-MOVE turn is blocked when the BFS
        // distance to the held target did not drop below the best distance
        // achieved while holding it — a two-cell resolver bounce changes
        // position every turn but never improves the distance, so it now
        // feeds the clause-1 counter exactly like standing still.
        let stalled = self.banana_last_move
            && match (self.banana_target, self.banana_best_dist) {
                (Some((_task, cell)), Some(best)) => {
                    bfs_distances(&view.walkable, &[cell])
                        .get(&worker.cell)
                        .map(|d| *d >= best)
                        .unwrap_or(true)
                }
                _ => self.banana_last_cell == Some(worker.cell),
            };
        self.banana_blocked_turns = if stalled { self.banana_blocked_turns + 1 } else { 0 };
        // C7 / I-10a: dynamic ownership-loss response, a pure function of
        // S_t, re-evaluated on EVERY active turn — wood-cycle, camping and
        // banking turns included (round 4, R-4 flip-response reachability:
        // the round-3 code ran this check on wood-free turns only, so a
        // flip landing while wood was carried was never answered from that
        // state). Ownership (I-7) uses the committed harvester's (the
        // resident's) ETA against the minimal opponent-harvester ETA, ties
        // conceded: the mother is LOST at the first turn with
        // eta_res >= eta_opp_h. Then, deterministically:
        //   1. ripe fruit harvestable immediately (resident standing on the
        //      mother, fruit ready, capacity free) -> HARVEST now;
        //   2. else convert iff CONVERSION_RACE_ORACLE (spec Revision
        //      2026-08-05) reports feasible -> CHOP the mother, latched to
        //      completion. This deliberate convert chop is the specified
        //      ownership-loss response; amended D-8 exempts exactly the
        //      post-flip oracle-feasible conversion;
        //   3. else Abandoned: cease all investment in the asset — release
        //      target and reservations, bank leftovers, idle (banana_lost).
        // The response PREEMPTS whatever the resident was doing (I-10a:
        // "the response begins at t itself"); the single sanctioned
        // deferral is an already-committed banking DROP executing at the
        // flip turn (I-19): standing on a door with wood, the DROP banks
        // the cargo this turn and the response begins wood-free at t + 1.
        if let Some(mother) = self.banana_mother_cell(view) {
            // I-10a committed-conversion latch (GREEN round 3,
            // 2026-08-05): the ownership-loss response is decided ONCE,
            // at the first flip turn ("the resident responds
            // deterministically at the first such t"). A committed
            // conversion — banana_target == (Chop, mother) is set
            // nowhere else: ring Chop candidates are orthogonal-only —
            // runs to completion without re-arbitration, so the exact
            // race won at commitment time is not spuriously re-opened
            // when the opponent arrives mid-sequence; the mother's
            // death invalidates the latch through
            // banana_mother_cell = None.
            if self.banana_target == Some((BananaTask::Chop, mother)) {
                self.banana_hold_age = 0;
                self.banana_blocked_turns = 0;
                self.banana_last_cell = Some(worker.cell);
                self.banana_last_move = worker.cell != mother;
                self.banana_best_dist = None;
                self.banana_idle_streak = 0;
                return Some(if worker.cell == mother {
                    format!("CHOP {}", worker.id)
                } else {
                    format!("MOVE {} {} {}", worker.id, mother.0, mother.1)
                });
            }
            let dist = bfs_distances(&view.walkable, &[mother]);
            let resident_eta = dist
                .get(&worker.cell)
                .map(|d| MoisanBot::ceil_div(*d, worker.stats.movement_speed))
                .unwrap_or(10_000);
            let eta_opp = Self::banana_opponent_eta(view, mother, false);
            let banking_drop_now = worker.carry[crate::game::types::WOOD] > 0
                && is_adjacent(worker.cell, view.shacks[0]);
            if resident_eta >= eta_opp && !banking_drop_now {
                let plant = Self::banana_live(view, mother);
                let fruits_ready = plant.map(|p| p.fruits > 0).unwrap_or(false);
                if fruits_ready
                    && worker.cell == mother
                    && worker.stats.harvest_power > 0
                    && worker.free_capacity() > 0
                {
                    // I-10a branch 1: harvest now.
                    self.banana_target = Some((BananaTask::Harvest, mother));
                    self.banana_hold_age = 0;
                    self.banana_blocked_turns = 0;
                    self.banana_last_cell = Some(worker.cell);
                    self.banana_last_move = false;
                    self.banana_best_dist = None;
                    self.banana_idle_streak = 0;
                    return Some(format!("HARVEST {}", worker.id));
                }
                // I-10a branch 2 feasibility = CONVERSION_RACE_ORACLE
                // (spec Revision 2026-08-05; round-4 unification, host
                // review terminal gap 2). The voided round-3 deadline
                // max(eta_opp_h, predicted-cooldown ripen proxy) — and
                // its arrival-only "race still open" guard — are
                // replaced by the oracle's exact absolute arithmetic,
                // anchored at this decision turn t:
                //   - arrival state = growth-only predict over eta_res
                //     (banana_predict_growth, the oracle's predict_tree
                //     mirror);
                //   - exact_chops from the arrival state =
                //     MoisanBot::chop_outcome (growth during the chop
                //     sequence included — the review boundary: size 2,
                //     health 4, cooldown 1, chop 1 needs 5 chops);
                //   - completion_turn = t + eta_res + exact_chops - 1,
                //     the absolute turn the FINAL chop lands;
                //   - opponent_harvest_turn = max(t + eta_opp_h,
                //     first_fruit_turn): HARVEST is executable only
                //     standing on the mother WITH fruits > 0, so arrival
                //     alone is NOT loss and ripeness alone is NOT loss
                //     (first-fruit wait = MoisanBot::ticks_until_fruit,
                //     the oracle's first-fruit-delay mirror for live
                //     bananas: 0 if ripe now, else ticks of natural
                //     growth until the first fruit);
                //   - feasible iff completion_turn <
                //     opponent_harvest_turn, STRICT (the equal-turn race
                //     is conceded, consistent with I-7 tie handling).
                // Both sides share the anchor t, so the relative
                // comparison below IS the oracle's absolute one:
                // eta_res + chops - 1 < max(eta_opp, ripe).
                // Infeasible => the Abandoned transition below (branch
                // 3). Feasible => convert, latched above until the
                // mother falls.
                let feasible = worker.stats.chop_power > 0
                    && resident_eta < 10_000
                    && plant
                        .and_then(|p| {
                            let arrival =
                                Self::banana_predict_growth(view, p, resident_eta);
                            let (chop_turns, _wood) = MoisanBot::chop_outcome(
                                view,
                                p,
                                arrival,
                                worker.stats.chop_power,
                            )?;
                            let ripe = MoisanBot::ticks_until_fruit(view, p);
                            Some(resident_eta + chop_turns - 1 < eta_opp.max(ripe))
                        })
                        .unwrap_or(false);
                if feasible {
                    // I-10a branch 2: convert (deliberate mother chop).
                    self.banana_target = Some((BananaTask::Chop, mother));
                    self.banana_hold_age = 0;
                    self.banana_blocked_turns = 0;
                    self.banana_last_cell = Some(worker.cell);
                    self.banana_last_move = worker.cell != mother;
                    self.banana_best_dist = None;
                    self.banana_idle_streak = 0;
                    return Some(if worker.cell == mother {
                        format!("CHOP {}", worker.id)
                    } else {
                        format!("MOVE {} {} {}", worker.id, mother.0, mother.1)
                    });
                }
                // I-10a branch 3: Abandoned transition. F-D1
                // (rev. 2026-08-06): the resident is held only to bank
                // leftover cargo; with nothing carried it is released to
                // the inner economy at the flip turn itself (the worker
                // reservation does not survive the Abandoned transition —
                // spec Revision 2026-08-06; the asset stays protected via
                // the persistent F-C2 cell claim, not via an idled
                // worker).
                self.banana_phase = BananaPhase::Abandoned;
                self.banana_lost = true;
                self.banana_lost_banking = worker.total_carried() > 0;
                self.banana_target = None;
                self.banana_hold_age = 0;
                self.banana_blocked_turns = 0;
                self.banana_last_cell = Some(worker.cell);
                self.banana_last_move = false;
                self.banana_best_dist = None;
                self.banana_idle_streak = 0;
                return if self.banana_lost_banking {
                    Some(Self::banana_lost_action(view, worker))
                } else {
                    None
                };
            }
        }
        let candidates = self.banana_candidates(view, worker);
        let held = self.banana_target.and_then(|(task, cell)| {
            candidates
                .iter()
                .find(|candidate| candidate.1 == task && candidate.2 == cell)
                .cloned()
        });
        let chosen = match held {
            Some(current) if self.banana_blocked_turns < 2 => {
                if self.banana_hold_age < 3 {
                    // clause 2: hold unconditionally.
                    self.banana_hold_age += 1;
                    current
                } else {
                    let best = candidates
                        .iter()
                        .max_by_key(|candidate| (candidate.0, candidate.1, candidate.2))
                        .cloned();
                    match best {
                        Some(best)
                            if (best.1, best.2) != (current.1, current.2)
                                && best.0 >= current.0 + 1 =>
                        {
                            // clause 3: eps-dominant upgrade.
                            self.banana_hold_age = 0;
                            self.banana_blocked_turns = 0;
                            best
                        }
                        _ => {
                            self.banana_hold_age += 1;
                            current
                        }
                    }
                }
            }
            _ => {
                // clause 1: invalidation (or 2-turn block) => free recompute.
                let block_triggered = self.banana_blocked_turns >= 2
                    && self
                        .banana_target
                        .map(|(task, cell)| {
                            candidates
                                .iter()
                                .any(|candidate| candidate.1 == task && candidate.2 == cell)
                        })
                        .unwrap_or(false);
                self.banana_hold_age = 0;
                self.banana_blocked_turns = 0;
                let best = candidates
                    .iter()
                    .max_by_key(|candidate| (candidate.0, candidate.1, candidate.2))
                    .cloned()
                    .unwrap_or((0, BananaTask::Idle, worker.cell, "WAIT".to_string()));
                // Blocked-hold (rev. 2026-08-06): the recompute was forced
                // by two blocked turns, yet the same target still
                // dominates — the route is sealed by a stationary unit and
                // re-emitting the MOVE only feeds the resolver's detour
                // parity (the period-2 D-1 signature, m097-class). Hold
                // position one turn and re-probe: the inserted repeat cell
                // breaks any A-B-A alternation while the probe resumes as
                // soon as the blocker moves. Guarded to wood-free turns
                // only: a wood-committed WAIT would trip D-4's no-progress
                // clause (I-19/I-20 bind WOOD cargo alone; a fruit carrier
                // may hold — m084-class single-door camp).
                if block_triggered
                    && best.1 != BananaTask::Idle
                    && Some((best.1, best.2)) == self.banana_target
                    && worker.carry[crate::game::types::WOOD] == 0
                {
                    self.banana_idle_streak = 0;
                    self.banana_last_move = false;
                    self.banana_last_cell = Some(worker.cell);
                    return Some("WAIT".to_string());
                }
                best
            }
        };
        let target_changed = self.banana_target != Some((chosen.1, chosen.2));
        self.banana_target = Some((chosen.1, chosen.2));
        self.banana_last_move = chosen.3.starts_with("MOVE ");
        self.banana_last_cell = Some(worker.cell);
        // F-B3 bookkeeping: best distance achieved toward the held target.
        let now_dist = bfs_distances(&view.walkable, &[chosen.2])
            .get(&worker.cell)
            .copied()
            .unwrap_or(10_000);
        self.banana_best_dist = Some(if target_changed {
            now_dist
        } else {
            self.banana_best_dist.map_or(now_dist, |best| best.min(now_dist))
        });
        if chosen.3.starts_with("PICK ") {
            self.banana_bootstrap_used = true;
        }
        if chosen.3.starts_with("PLANT ")
            && !is_adjacent(chosen.2, view.shacks[0])
        {
            self.banana_mother = Some(chosen.2);
        }
        if chosen.1 == BananaTask::Idle {
            self.banana_idle_streak += 1;
            // F-B1 idle-yield (rev. 2026-08-06): an Idle resident camping
            // the mother is a permanent `reserved` obstacle in the C8
            // re-resolution — with a loaded teammate within Chebyshev
            // distance 2 it converts the teammate's one-step bank landing
            // into the period-2 accept/detour livelock (diagnosis-r6
            // family (b1)). Step aside ONCE, off the mother, to the
            // minimal free walkable ortho neighbor whose occupation still
            // leaves every nearby loaded teammate a reachable bank door
            // (the I-15 alternate-door test with the aside cell removed —
            // stepping into the teammate's only corridor would trade one
            // blockade for another); off the mother the resident HOLDS
            // (WAIT) instead of stepping back, so the aside is stable
            // while the teammate passes. The mother needs no occupancy:
            // every protection layer is cell-based, and the resident
            // re-approaches at ETA 1 when fruits ripen.
            let on_mother = self.banana_mother_cell(view) == Some(worker.cell);
            if on_mother {
                let loaded: Vec<&Unit> = view
                    .units
                    .iter()
                    .filter(|other| {
                        other.player == 0
                            && other.id != worker.id
                            && other.total_carried() > 0
                            && (other.cell.0 - worker.cell.0)
                                .abs()
                                .max((other.cell.1 - worker.cell.1).abs())
                                <= 2
                    })
                    .collect();
                if !loaded.is_empty() {
                    let doors: Vec<Cell> = ortho_neighbors(view.shacks[0])
                        .into_iter()
                        .filter(|door| view.walkable.contains(door))
                        .collect();
                    let mut aside: Option<Cell> = None;
                    for cell in ortho_neighbors(worker.cell) {
                        if !view.walkable.contains(&cell) {
                            continue;
                        }
                        if view.units.iter().any(|other| other.cell == cell) {
                            continue;
                        }
                        let mut walk = view.walkable.clone();
                        walk.remove(&cell);
                        let keeps_bank_open = loaded.iter().all(|teammate| {
                            let dist = bfs_distances(&walk, &[teammate.cell]);
                            doors.iter().any(|door| dist.contains_key(door))
                        });
                        if keeps_bank_open && aside.map(|best| cell < best).unwrap_or(true) {
                            aside = Some(cell);
                        }
                    }
                    if let Some(cell) = aside {
                        self.banana_last_move = true;
                        return Some(format!("MOVE {} {} {}", worker.id, cell.0, cell.1));
                    }
                }
            }
            // F-D2 starvation release (rev. 2026-08-06): after 3
            // consecutive Idle choices the candidate generator has nothing
            // to offer (fruitless mother, no seed, nothing to chop); stop
            // reserving the resident so the inner economy can employ it,
            // and re-assert the reservation on the first turn a
            // lifecycle-productive candidate exists.
            if self.banana_idle_streak >= 3 {
                return None;
            }
        } else if self.banana_idle_streak >= 3 && chosen.1 == BananaTask::Bank {
            // F-D2 refinement (rev. 2026-08-06): a released resident's
            // cargo was acquired under INNER control; re-capturing the
            // worker just to bank it produced an inner-PICK / wrapper-DROP
            // churn (D-2) and wrapper takeovers of inner banking runs into
            // blocked corridors (D-1/P2, m056-class). The release ends
            // only at a lifecycle-productive candidate (ring
            // Chop/Harvest/Plant/Boot); the inner banks its own cargo.
            self.banana_idle_streak += 1;
            return None;
        } else {
            self.banana_idle_streak = 0;
        }
        Some(chosen.3)
    }

    /// Phase machine. Runs on every enabled turn BEFORE delegation, on view
    /// data only, so the reservation seam fields are set for the same turn.
    fn banana_update_phase(&mut self, view: &GameState) {
        match self.banana_phase {
            BananaPhase::Abandoned => {}
            BananaPhase::Dormant => {
                // I-1: past the activation deadline the feature stays dormant
                // for the whole game.
                if view.turn > 100 {
                    self.banana_phase = BananaPhase::Abandoned;
                    return;
                }
                // I-16: activation requires the trained second worker.
                let mut own: Vec<&Unit> = view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 0)
                    .collect();
                if own.len() < 2 {
                    return;
                }
                own.sort_by_key(|unit| unit.id);
                // C1: the resident is the starter (min own id).
                let starter = own[0];
                let tent = view.shacks[0];
                let on_ring = view.walkable.contains(&starter.cell)
                    && (starter.cell.0 - tent.0).abs().max((starter.cell.1 - tent.1).abs()) == 1;
                // Checkpoint: the starter is on the ring, a seed exists,
                // and the complete bounded plot passes the conservative safety gate.
                let seedable = starter.carry[BANANA] > 0
                    || view.inventories[0][BANANA] > 0;
                if on_ring && seedable && Self::banana_activation_safe(view, starter) {
                    self.banana_phase = BananaPhase::Active;
                    self.banana_worker = Some(starter.id);
                    self.banana_target = None;
                    self.banana_hold_age = 0;
                    self.banana_blocked_turns = 0;
                    self.banana_last_move = false;
                    self.banana_best_dist = None;
                    self.banana_idle_streak = 0;
                }
            }
            BananaPhase::Active => {
                let Some(worker) = self.banana_worker.and_then(|id| view.unit(id)) else {
                    // Resident death abandons the feature (R5: no post-edit
                    // for a dead unit, so replace_action can never push).
                    self.banana_phase = BananaPhase::Abandoned;
                    return;
                };
                let ring_alive = Self::banana_ring(view)
                    .into_iter()
                    .any(|cell| Self::banana_live(view, cell).is_some());
                let stock = view.inventories[0][BANANA] > 0 && !self.banana_bootstrap_used;
                // Feature completed/impossible: nothing carried, no live ring
                // banana, no usable banked seed => release the worker forever.
                if worker.total_carried() == 0 && !ring_alive && !stock {
                    self.banana_phase = BananaPhase::Abandoned;
                }
            }
        }
    }
}

impl Bot for BananaBot {
    fn commands(&mut self, view: &GameState) -> Vec<String> {
        // I-28 (C2): decided once, before the first delegation, from the
        // static map and initial plants only.
        if self.banana_enabled.is_none() {
            self.banana_enabled = Some(!Self::banana_orchard_geometry(view));
        }
        if self.banana_enabled == Some(true) {
            self.banana_update_phase(view);
        }
        let active = self.banana_enabled == Some(true) && self.banana_phase == BananaPhase::Active;
        // Resident decision BEFORE delegation (rev. 2026-08-06): the
        // reservation seam field must reflect the F-D1/F-D2 release states
        // on the very turn they begin, so the inner policy plans real work
        // for a released resident in the same turn. banana_action reads
        // only `view` and wrapper state, so hoisting it above the
        // delegated call is behavior-preserving for the computed action.
        // Some(cmd) = the wrapper controls the resident this turn;
        // None = released (dormant, F-D2 starvation, or post-loss with
        // nothing left to bank — F-D1).
        let wrapper_action: Option<String> = match self
            .banana_worker
            .and_then(|id| view.unit(id))
        {
            Some(worker) if active => self.banana_action(view, worker),
            // I-10a Abandoned (C7 rev. 2026-08-06): while lost, the
            // resident is held ONLY until the leftover cargo it carried AT
            // the loss is banked (`banana_lost_banking` latch); then the
            // reservation is dropped permanently and the inner economy
            // re-employs the worker (spec Revision 2026-08-06). Cargo the
            // worker later acquires under inner control is never
            // re-captured. Reinvestment in the lost asset is blocked by
            // the persistent cell claim below, not by idling the worker.
            Some(worker)
                if self.banana_enabled == Some(true)
                    && self.banana_lost
                    && self.banana_lost_banking =>
            {
                if worker.total_carried() > 0 {
                    Some(Self::banana_lost_action(view, worker))
                } else {
                    self.banana_lost_banking = false;
                    None
                }
            }
            _ => None,
        };
        // F-C2 persistent claim (rev. 2026-08-06): the protected-cell
        // claim survives ownership loss while the lost plant lives — the
        // I6 retain filter keeps every inner candidate off the
        // opponent-owned asset (the round-6 D-8 episodes were inner-policy
        // chops enabled by the old post-loss claim release). The claim
        // lapses when the plant dies. banana_action may have set
        // banana_lost this very turn; the claim is computed after it.
        // Dormant/disabled games: banana_lost is unreachable and active is
        // false, so both seam fields stay None (check 4).
        let claim = if active || (self.banana_enabled == Some(true) && self.banana_lost) {
            self.banana_mother_cell(view)
        } else {
            None
        };
        // R1: both seam fields are (re)written on every turn BEFORE the
        // delegated call; None on every dormant/disabled turn (check 4).
        self.inner.inner.banana_idle_unit =
            if wrapper_action.is_some() { self.banana_worker } else { None };
        self.inner.inner.banana_protected_cell = claim;
        let mut commands = self.inner.commands(view);
        let lost = self.banana_enabled == Some(true) && self.banana_lost;
        if wrapper_action.is_none() && claim.is_none() && !active && !lost {
            // Structural identity: no post-edit outside banana activation
            // (dormant/disabled/never-lost-abandoned turns).
            return commands;
        }
        let mut unit_ids: Vec<i32> = view
            .units
            .iter()
            .filter(|unit| unit.player == 0)
            .map(|unit| unit.id)
            .collect();
        unit_ids.sort_unstable();
        // wrapper_worker = the unit whose command the wrapper set this
        // turn (None on released turns: the inner's command stands).
        let mut wrapper_worker: Option<i32> = None;
        if let (Some(worker_id), Some(action)) = (self.banana_worker, wrapper_action.clone()) {
            if view.unit(worker_id).is_some() {
                SecureOrchardBot::replace_action(&mut commands, &unit_ids, worker_id, action);
                wrapper_worker = Some(worker_id);
            }
        }
        // C5 second layer: post-edit protection of the claimed mother
        // against on-cell verbs by any unit the wrapper does not control
        // this turn (rev. 2026-08-06: a released resident is
        // inner-controlled and is protected against exactly like a peer),
        // and I-2/I-15 banana-PICK exclusivity — held while Active AND
        // after ownership loss: banana stock stays out of the inner
        // economy's hands for the rest of the game (an inner bank-PICKed
        // banana can only become an unmanaged replant, the D-5/D-6 tail
        // the round-5 lost-hold also prevented; every other economy verb
        // of a released resident is sanctioned by spec Revision
        // 2026-08-06).
        for unit in view
            .units
            .iter()
            .filter(|unit| unit.player == 0 && Some(unit.id) != wrapper_worker)
        {
            let Some(slot) = SecureOrchardBot::unit_action_slot(&commands, &unit_ids, unit.id)
            else {
                continue;
            };
            let on_mother = claim == Some(unit.cell);
            let harms_mother = on_mother
                && (commands[slot].starts_with("CHOP ") || commands[slot].starts_with("HARVEST "));
            let steals_seed = active
                && !self.banana_bootstrap_used
                && commands[slot].starts_with("PICK ")
                && commands[slot].ends_with(" BANANA");
            if harms_mother || steals_seed {
                commands[slot] = "WAIT".to_string();
            }
        }
        // C8 (rev. round 5, R-5): resident priority in move resolution;
        // the mother is NOT movement-forbidden. I-29's protection intent
        // covers harming verbs (CHOP/HARVEST, second layer above; D-8),
        // PLANT-over (illegal on an occupied plant cell; candidate-side
        // Target::Cell exclusion via the I6 retain filter; I-13) and
        // camping-as-a-goal (the I6 filter removes every Tree/Bank/Cell
        // candidate equal to the protected cell, so no non-resident ever
        // SELECTS the mother as a destination) -- standing on a plant's
        // cell is a legal game action, so TRANSIT across the mother must
        // stay possible. The former landing-forbidden set made the mother
        // "transit-impossible" and livelocked full carriers whose every
        // door route crosses it (R-5 accept/detour parity oscillation);
        // by this stage moves are already rewritten to their one-step
        // landing, so a movement-level veto cannot distinguish transit
        // from destination at all and belongs at the candidate layer.
        // Re-resolution is needed only when the wrapper actually rewrote
        // the resident's command (a replaced move can conflict with the
        // inner's accepted landings); the second-layer vetoes above only
        // turn stationary verbs into WAIT, which cannot create a movement
        // conflict. Released turns keep the inner's own resolution.
        if let Some(worker_id) = wrapper_worker {
            MoisanBot::resolve_move_conflicts_with_priority(
                view,
                &mut commands,
                &BTreeSet::from([worker_id]),
            );
        }
        commands
    }
}
