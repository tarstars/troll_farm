        const R1FA_CROP_DENIAL_BONUS: i32 = 20000;
        // Scarce-fruit denial premium. The archived 900/(1+distance) was quoted at a
        // 1000*wood/trip scale; this controller rates 100000*(4*wood)/trip, so the same
        // premium is 360000/(1+distance).
        const R1FA_SCARCE_DENIAL_SCALE: i32 = 360_000;

        #[derive(Clone, Copy, Debug, Eq, PartialEq)]
        enum R1faJob {
            Seed(PlantKind),
            Plant(PlantKind),
            Harvest(PlantKind),
            Chop,
            Drop,
            Mine,
        }

        #[derive(Clone, Copy, Debug, Eq, PartialEq)]
        struct R1faGoal {
            job: R1faJob,
            cell: Cell,
        }

        pub struct R1faBot {
            goals: BTreeMap<i32, R1faGoal>,
            planted: BTreeSet<Cell>,
            previous_plants: BTreeSet<Cell>,
            opponent_plants: BTreeSet<Cell>,
            focus: Option<PlantKind>,
        }

        impl R1faBot {
            pub fn new() -> Self {
                Self {
                    goals: BTreeMap::new(),
                    planted: BTreeSet::new(),
                    previous_plants: BTreeSet::new(),
                    opponent_plants: BTreeSet::new(),
                    focus: None,
                }
            }

            fn index(kind: PlantKind) -> usize {
                kind.item_index()
            }

            fn kind(index: usize) -> PlantKind {
                match index {
                    PLUM => PlantKind::Plum,
                    LEMON => PlantKind::Lemon,
                    APPLE => PlantKind::Apple,
                    _ => PlantKind::Banana,
                }
            }

            // Scarce-kind selector copied unchanged from the archived V439 controller.
            fn focus_type(view: &GameState) -> PlantKind {
                let starts: Vec<Cell> = ortho_neighbors(view.shacks[0])
                    .iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .copied()
                    .collect();
                let dist = bfs_distances(&view.walkable, &starts);
                let sum = |kind: PlantKind| {
                    view.plants
                        .iter()
                        .filter(|plant| plant.kind == kind)
                        .map(|plant| dist.get(&plant.cell).copied().unwrap_or(10_000))
                        .sum::<i32>()
                };
                let lemon = sum(PlantKind::Lemon);
                let plum = sum(PlantKind::Plum);
                if lemon <= plum && plum - lemon <= 8 {
                    PlantKind::Plum
                } else if lemon <= plum {
                    PlantKind::Lemon
                } else {
                    PlantKind::Plum
                }
            }

            fn next_spec(workers: usize) -> Option<(i32, i32, i32, i32)> {
                match workers {
                    1 => Some((2, 2, 1, 1)),
                    2 => Some((2, 3, 1, 2)),
                    3 => Some((2, 4, 0, 3)),
                    _ => None,
                }
            }

            fn affordable_first_spec(view: &GameState) -> Option<(i32, i32, i32, i32)> {
                let mut best = None;
                for movement in 1..=3 {
                    for carry in 1..=3 {
                        for chop in 1..=3 {
                            let spec = (movement, carry, 1, chop);
                            let cost = training_cost(1, spec);
                            if !Self::affordable(view, &cost) {
                                continue;
                            }
                            let key = (movement + carry + chop, chop, carry, movement);
                            if best.is_none_or(|(best_key, _)| key > best_key) {
                                best = Some((key, spec));
                            }
                        }
                    }
                }
                best.map(|(_, spec)| spec)
            }

            fn affordable(view: &GameState, cost: &[i32; 6]) -> bool {
                (PLUM..=IRON).all(|index| view.inventories[0][index] >= cost[index])
            }

            fn planned_spec(view: &GameState, workers: usize) -> Option<(i32, i32, i32, i32)> {
                // Funding stops at the ceiling. Carried transactions and the first
                // hire are untouched; only new purchases are refused here.
                if workers >= WORKER_LIMIT {
                    return None;
                }
                let spec = if workers == 1 {
                    Self::affordable_first_spec(view)?
                } else {
                    Self::next_spec(workers)?
                };
                let bill = training_cost(workers as i32, spec);
                let bank = Self::bank_distances(view);
                let mut acquisition = 0;
                let mut longest_resource = 0;
                // A bill is a finite transaction, not a permanent target. Credit carried
                // stock, but require a reachable source for every still-missing item.
                for item in PLUM..=IRON {
                    let before = acquisition;
                    let carried: i32 = view.units.iter().filter(|u| u.player == 0)
                        .map(|u| u.carry[item]).sum();
                    let missing = (bill[item] - view.inventories[0][item] - carried).max(0);
                    if missing == 0 { continue; }
                    if item == IRON {
                        let distance = view.iron.iter().flat_map(|cell| ortho_neighbors(*cell))
                            .filter_map(|cell| bank.get(&cell).copied()).min()?;
                        let throughput = view.units.iter().filter(|u| u.player == 0)
                            .map(|u| u.stats.chop_power.min(u.stats.carry_capacity)).max().unwrap_or(0);
                        if throughput == 0 { return None; }
                        acquisition += (missing + throughput - 1) / throughput * (2 * distance + 2);
                    } else if item <= APPLE {
                        let source = view.plants.iter()
                            .filter(|p| Self::index(p.kind) == item && p.health > 0)
                            .filter_map(|p| bank.get(&p.cell).map(|d| (*d, p)))
                            .min_by_key(|(d, p)| (*d, p.cooldown));
                        if let Some((distance, plant)) = source {
                            acquisition += missing * (2 * distance + 2)
                                + if plant.fruits > 0 { 0 } else { plant.cooldown };
                        } else if view.inventories[0][item] + carried > 0 {
                            // Retained seed can restore a source, including maturation.
                            acquisition += 4 * effective_cooldown(Self::kind(item), false)
                                + missing * 4 + 4;
                        } else {
                            return None;
                        }
                    }
                    longest_resource = longest_resource.max(acquisition - before);
                }
                let funders = view.units.iter().filter(|u| u.player == 0 && u.stats.harvest_power > 0).count().min(2) as i32;
                if PARALLEL_CAPITAL {
                    acquisition = longest_resource.max((acquisition + funders.max(1) - 1) / funders.max(1));
                }
                // Charge fruit spent on the worker and on renewing its wood source.
                // This is an explicit near-bank cycle estimate, not an early-score gate.
                let plot_distance = view.walkable.iter()
                    .filter(|cell| Self::on_own_half(view, **cell))
                    .filter_map(|cell| bank.get(cell).copied()).min()?;
                let wood = spec.1.min(4).max(1);
                let cycle = (tree_health(PlantKind::Banana, wood) + spec.3 - 1) / spec.3.max(1)
                    + 2 * (plot_distance + spec.0 - 1) / spec.0.max(1) + 3;
                let fruit_cost: i32 = bill[..4].iter().sum();
                let net = 4 * wood - 1;
                let repayment = (fruit_cost * cycle + net - 1) / net;
                let warmup = (wood - 1) * effective_cooldown(PlantKind::Banana, false);
                if acquisition + repayment + warmup >= TOTAL_TURNS - view.turn + 1 {
                    return None;
                }
                Some(spec)
            }

            fn capital_producer(view: &GameState, unit: &Unit) -> bool {
                let mut candidates: Vec<_> = view.units.iter()
                    .filter(|u| u.player == 0 && u.stats.harvest_power > 0).collect();
                candidates.sort_by_key(|u| (
                        100 * u.stats.chop_power / (u.stats.harvest_power * u.stats.carry_capacity).max(1),
                        u.id,
                    ));
                candidates.into_iter().take(if PARALLEL_CAPITAL { 2 } else { 1 }).any(|u| u.id == unit.id)
            }

            fn production_goal(&self, view: &GameState, unit: &Unit,
                               deficits: &[i32; 6], reserved: &BTreeSet<Cell>) -> Option<R1faGoal> {
                let distance = Self::distances(view, unit.cell);
                let bank = Self::bank_distances(view);
                let speed = unit.stats.movement_speed.max(1);
                let remaining = TOTAL_TURNS - view.turn + 1;
                let banana_stock = view.inventories[0][BANANA] + view.units.iter()
                    .filter(|u| u.player == 0).map(|u| u.carry[BANANA]).sum::<i32>();
                let seed_source = if banana_stock < 2 && remaining > 30 {
                    view.plants.iter().filter(|p| p.kind == PlantKind::Banana && p.health > 0)
                        .filter(|p| self.planted.contains(&p.cell))
                        .min_by_key(|p| (bank.get(&p.cell).copied().unwrap_or(99), p.cell))
                        .map(|p| p.cell)
                } else { None };
                let mut best: Option<(i32, R1faGoal)> = None;
                let enemy_workers = view.units.iter().filter(|u| u.player == 1).count();
                // The denial premium is added after the rate division, so it ranks a
                // scarce-fruit trip against ordinary wood instead of banking fake points.
                let mut offer = |points: i32, turns: i32, bonus: i32, goal: R1faGoal| {
                    if turns > remaining || points <= 0 { return; }
                    let value = 100_000 * points / turns.max(1) + bonus;
                    if best.as_ref().is_none_or(|(old, _)| value > *old) {
                        best = Some((value, goal));
                    }
                };
                for plant in &view.plants {
                    if reserved.contains(&plant.cell) || plant.health <= 0
                        || view.units.iter().any(|u| u.player == 0 && u.id != unit.id && u.cell == plant.cell) {
                        continue;
                    }
                    let (Some(outward), Some(home)) = (distance.get(&plant.cell), bank.get(&plant.cell)) else { continue; };
                    let travel = (*outward + speed - 1) / speed;
                    let transit = travel + (*home + speed - 1) / speed + 1;
                    if unit.stats.chop_power > 0 {
                        let wood = plant.size.min(unit.free_capacity());
                        let chops = (plant.health + unit.stats.chop_power - 1) / unit.stats.chop_power;
                        // Do not squander a growing owned crop while useful carry remains.
                        let growing = self.planted.contains(&plant.cell)
                            && plant.size < unit.stats.carry_capacity.min(4)
                            && remaining > transit + chops + 2 * plant.cooldown.max(1);
                        let threatened = view.units.iter().any(|enemy| enemy.player == 1
                            && enemy.stats.chop_power > 0 && manhattan(enemy.cell, plant.cell) <= 2);
                        let capital_source = deficits[Self::index(plant.kind)] > 0
                            && Self::on_own_half(view, plant.cell);
                        if (!growing && !capital_source && seed_source != Some(plant.cell)) || threatened {
                            // Deny the latched scarce kind on a source we do not own,
                            // while the opponent is small or the worker already stands there.
                            let denial = if RESOURCE_DENIAL
                                && self.focus == Some(plant.kind)
                                && !self.planted.contains(&plant.cell)
                                && (enemy_workers <= 2 || travel == 0)
                            {
                                R1FA_SCARCE_DENIAL_SCALE / (1 + manhattan(plant.cell, view.shacks[1]))
                            } else {
                                0
                            };
                            offer(4 * wood, transit + chops, denial,
                                  R1faGoal { job: R1faJob::Chop, cell: plant.cell });
                        }
                    }
                    if unit.stats.harvest_power > 0 && plant.fruits > 0 {
                        let fruit = plant.fruits.min(unit.free_capacity());
                        let harvests = (fruit + unit.stats.harvest_power - 1) / unit.stats.harvest_power;
                        offer(fruit, transit + harvests, 0,
                              R1faGoal { job: R1faJob::Harvest(plant.kind), cell: plant.cell });
                    }
                }
                // A renewable crop competes with the remaining wild trips. Charge
                // the entire cold cycle, including growth: no free parallelism is
                // assumed here. BANANA is not part of a worker's training bill.
                if view.turn < 275 && unit.total_carried() == 0 && unit.stats.chop_power > 0
                    && self.planted_count(view, None) < 10
                    && view.inventories[0][BANANA] > 0
                    && (view.inventories[0][BANANA] >= 2 || view.plants.iter().any(|p|
                        p.kind == PlantKind::Banana && p.health > 0 && distance.contains_key(&p.cell)))
                {
                    if let (Some(plot), Some(pickup)) = (
                        Self::plant_cell(view, unit, PlantKind::Banana, reserved),
                        Self::bank_cell(view, unit),
                    ) {
                        let from_pickup = Self::distances(view, pickup);
                        if let (Some(to_seed), Some(to_plot), Some(home)) = (
                            distance.get(&pickup), from_pickup.get(&plot), bank.get(&plot),
                        ) {
                            let wood = unit.stats.carry_capacity.min(4).max(1);
                            let watered = view.water.iter().any(|water| is_adjacent(*water, plot));
                            let growth = (wood - 1) * effective_cooldown(PlantKind::Banana, watered);
                            let chops = (tree_health(PlantKind::Banana, wood) + unit.stats.chop_power - 1)
                                / unit.stats.chop_power;
                            let cycle = (*to_seed + speed - 1) / speed + 1
                                + (*to_plot + speed - 1) / speed + 1 + growth + chops
                                + (*home + speed - 1) / speed + 1;
                            offer(4 * wood - 1, cycle, 0,
                                  R1faGoal { job: R1faJob::Seed(PlantKind::Banana), cell: view.shacks[0] });
                        }
                    }
                }
                best.map(|(_, goal)| goal)
            }

            fn own_units<'a>(view: &'a GameState) -> Vec<&'a Unit> {
                let mut units: Vec<_> = view.units.iter().filter(|unit| unit.player == 0).collect();
                units.sort_by_key(|unit| unit.id);
                units
            }

            fn distances(view: &GameState, source: Cell) -> BTreeMap<Cell, i32> {
                bfs_distances(&view.walkable, &[source])
            }

            fn bank_distances(view: &GameState) -> BTreeMap<Cell, i32> {
                let sources: Vec<_> = ortho_neighbors(view.shacks[0])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .collect();
                bfs_distances(&view.walkable, &sources)
            }

            fn opponent_bank_distances(view: &GameState) -> BTreeMap<Cell, i32> {
                let sources: Vec<_> = ortho_neighbors(view.shacks[1])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .collect();
                bfs_distances(&view.walkable, &sources)
            }

            fn home_distance(view: &GameState, cell: Cell) -> i32 {
                Self::bank_distances(view).get(&cell).copied().unwrap_or(99)
            }

            fn on_own_half(view: &GameState, cell: Cell) -> bool {
                manhattan(cell, view.shacks[0]) <= manhattan(cell, view.shacks[1])
            }

            fn bank_cell(view: &GameState, unit: &Unit) -> Option<Cell> {
                let distance = Self::distances(view, unit.cell);
                ortho_neighbors(view.shacks[0])
                    .into_iter()
                    .filter(|cell| {
                        view.walkable.contains(cell)
                            && distance.contains_key(cell)
                            && !view.units.iter().any(|other| {
                                other.player == 0
                                    && other.id != unit.id
                                    && other.cell == *cell
                            })
                    })
                    .min_by_key(|cell| (distance[cell], *cell))
            }

            fn move_command(view: &GameState, unit: &Unit, target: Cell) -> String {
                let next = next_cell(
                    &view.walkable,
                    unit.cell,
                    target,
                    unit.stats.movement_speed.max(1),
                );
                format!("MOVE {} {} {}", unit.id, next.0, next.1)
            }

            fn drop_command(view: &GameState, unit: &Unit) -> Option<String> {
                if is_adjacent(unit.cell, view.shacks[0]) {
                    Some(format!("DROP {}", unit.id))
                } else {
                    Self::bank_cell(view, unit)
                        .map(|cell| Self::move_command(view, unit, cell))
                }
            }

            fn carried_fruit(unit: &Unit) -> Option<PlantKind> {
                (PLUM..=BANANA)
                    .filter(|index| unit.carry[*index] > 0)
                    .max_by_key(|index| (unit.carry[*index], -(*index as i32)))
                    .map(Self::kind)
            }

            fn planted_count(&self, view: &GameState, kind: Option<PlantKind>) -> usize {
                self.planted
                    .iter()
                    .filter(|cell| {
                        view.plants.iter().any(|plant| {
                            plant.cell == **cell && kind.map_or(true, |value| plant.kind == value)
                        })
                    })
                    .count()
            }

            fn source_capacity(&self, view: &GameState, kind: PlantKind) -> i32 {
                let index = Self::index(kind);
                let carried: i32 = view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 0)
                    .map(|unit| unit.carry[index])
                    .sum();
                let trees = view
                    .plants
                    .iter()
                    .filter(|plant| {
                        plant.kind == kind && self.planted.contains(&plant.cell)
                    })
                    .count() as i32;
                view.inventories[0][index] + carried + 3 * trees
            }

            fn deficits(view: &GameState, cost: Option<&[i32; 6]>) -> [i32; 6] {
                let mut result = [0; 6];
                if let Some(cost) = cost {
                    for index in PLUM..=IRON {
                        result[index] = (cost[index] - view.inventories[0][index]).max(0);
                    }
                }
                result
            }

            fn source_shortages(&self, view: &GameState, cost: Option<&[i32; 6]>) -> [i32; 4] {
                let mut result = [0; 4];
                if let Some(cost) = cost {
                    for index in PLUM..=APPLE {
                        result[index] =
                            (cost[index] - self.source_capacity(view, Self::kind(index))).max(0);
                    }
                }
                result
            }

            fn useful_for_bill(unit: &Unit, deficits: &[i32; 6]) -> bool {
                (PLUM..=IRON).any(|index| deficits[index] > 0 && unit.carry[index] > 0)
            }

            fn plant_cell(
                view: &GameState,
                unit: &Unit,
                kind: PlantKind,
                reserved: &BTreeSet<Cell>,
            ) -> Option<Cell> {
                let from_unit = Self::distances(view, unit.cell);
                let from_bank = Self::bank_distances(view);
                let opponent_starts: Vec<Cell> = view
                    .units
                    .iter()
                    .filter(|other| other.player == 1)
                    .map(|other| other.cell)
                    .collect();
                let from_opponent = bfs_distances(&view.walkable, &opponent_starts);
                let occupied: BTreeSet<_> = view.units.iter().filter(|other| other.id != unit.id)
                    .map(|other| other.cell).collect();
                view.walkable
                    .iter()
                    .copied()
                    .filter(|cell| {
                        from_unit.contains_key(cell)
                            && from_bank.get(cell).is_some_and(|distance| *distance <= 4)
                            && Self::on_own_half(view, *cell)
                            && !reserved.contains(cell)
                            && !view.plants.iter().any(|plant| plant.cell == *cell)
                            && !occupied.contains(cell)
                            && !view.shacks.contains(cell)
                            && !view.iron.contains(cell)
                            && !view.water.contains(cell)
                    })
                    .min_by_key(|cell| {
                        let near_water = view
                            .water
                            .iter()
                            .any(|water| is_adjacent(*water, *cell));
                        let apple_penalty = i32::from(kind == PlantKind::Apple && !near_water);
                        let enemy_distance = from_opponent.get(cell).copied().unwrap_or(99);
                        (
                            apple_penalty,
                            from_bank[cell],
                            std::cmp::Reverse(enemy_distance),
                            from_unit[cell],
                            *cell,
                        )
                    })
            }

            fn harvest_cell(
                view: &GameState,
                unit: &Unit,
                kind: Option<PlantKind>,
                reserved: &BTreeSet<Cell>,
                allow_unripe: bool,
            ) -> Option<Cell> {
                let from_unit = Self::distances(view, unit.cell);
                let from_bank = Self::bank_distances(view);
                view.plants
                    .iter()
                    .filter(|plant| {
                        kind.map_or(true, |value| plant.kind == value)
                            && !reserved.contains(&plant.cell)
                            && from_unit.contains_key(&plant.cell)
                            && !view.units.iter().any(|other| {
                                other.player == 0
                                    && other.id != unit.id
                                    && other.cell == plant.cell
                            })
                            && (plant.fruits > 0
                                || (allow_unripe
                                    && plant.cooldown
                                        <= (from_unit[&plant.cell]
                                            + unit.stats.movement_speed.max(1)
                                            - 1)
                                            / unit.stats.movement_speed.max(1)
                                            + 1))
                    })
                    .min_by_key(|plant| {
                        let travel = (from_unit[&plant.cell]
                            + unit.stats.movement_speed.max(1)
                            - 1)
                            / unit.stats.movement_speed.max(1);
                        let wait = if plant.fruits > 0 {
                            0
                        } else {
                            (plant.cooldown - travel).max(0)
                        };
                        (
                            wait,
                            travel + from_bank.get(&plant.cell).copied().unwrap_or(99),
                            i32::from(!Self::on_own_half(view, plant.cell)),
                            -plant.fruits,
                            plant.cell,
                        )
                    })
                    .map(|plant| plant.cell)
            }

            fn mine_cell(
                view: &GameState,
                unit: &Unit,
                reserved: &BTreeSet<Cell>,
            ) -> Option<Cell> {
                let distance = Self::distances(view, unit.cell);
                view.iron
                    .iter()
                    .flat_map(|iron| ortho_neighbors(*iron))
                    .filter(|cell| {
                        view.walkable.contains(cell)
                            && distance.contains_key(cell)
                            && !reserved.contains(cell)
                    })
                    .min_by_key(|cell| (distance[cell], Self::home_distance(view, *cell), *cell))
            }

            fn chop_cell(
                &self,
                view: &GameState,
                unit: &Unit,
                deficits: &[i32; 6],
                reserved: &BTreeSet<Cell>,
            ) -> Option<Cell> {
                if unit.stats.chop_power <= 0 || unit.free_capacity() <= 0 {
                    return None;
                }
                let distance = Self::distances(view, unit.cell);
                let bank = Self::bank_distances(view);
                let turns_left = TOTAL_TURNS - view.turn + 1;
                view.plants
                    .iter()
                    .filter(|plant| {
                        !reserved.contains(&plant.cell)
                            && distance.contains_key(&plant.cell)
                            && !view.units.iter().any(|other| {
                                other.player == 0
                                    && other.id != unit.id
                                    && other.cell == plant.cell
                            })
                            && !(deficits[Self::index(plant.kind)] > 0
                                && Self::on_own_half(view, plant.cell))
                    })
                    .filter_map(|plant| {
                        let travel = (distance[&plant.cell]
                            + unit.stats.movement_speed.max(1)
                            - 1)
                            / unit.stats.movement_speed.max(1);
                        let chops = (plant.health + unit.stats.chop_power - 1)
                            / unit.stats.chop_power;
                        let home = (bank.get(&plant.cell).copied().unwrap_or(99)
                            + unit.stats.movement_speed.max(1)
                            - 1)
                            / unit.stats.movement_speed.max(1);
                        let cycle = travel + chops + home + 1;
                        if cycle + 1 >= turns_left {
                            return None;
                        }
                        let wood = plant.size.min(unit.free_capacity()).max(1);
                        let denial = if self.opponent_plants.contains(&plant.cell)
                            && travel <= 6
                        {
                            R1FA_CROP_DENIAL_BONUS
                        } else {
                            0
                        };
                        let value = 100_000 * wood / cycle.max(1) + denial;
                        Some((
                            (
                                value,
                                i32::from(plant.size == 4),
                                i32::from(Self::on_own_half(view, plant.cell)),
                                -travel,
                                -home,
                            ),
                            plant.cell,
                        ))
                    })
                    .max_by_key(|(score, cell)| (*score, std::cmp::Reverse(*cell)))
                    .map(|(_, cell)| cell)
            }

            fn goal_valid(
                &self,
                view: &GameState,
                unit: &Unit,
                goal: R1faGoal,
                shortages: &[i32; 4],
            ) -> bool {
                match goal.job {
                    R1faJob::Seed(kind) => {
                        (view.inventories[0][Self::index(kind)] > 0
                            || unit.carry[Self::index(kind)] > 0)
                            && (shortages[Self::index(kind)] > 0
                                || self.planted_count(view, None) < 10)
                    }
                    R1faJob::Plant(kind) => {
                        unit.carry[Self::index(kind)] > 0
                            && !view.plants.iter().any(|plant| plant.cell == goal.cell)
                    }
                    R1faJob::Harvest(kind) => {
                        unit.stats.harvest_power > 0
                            && unit.free_capacity() > 0
                            && view
                                .plants
                                .iter()
                                .any(|plant| plant.cell == goal.cell && plant.kind == kind)
                    }
                    R1faJob::Chop => {
                        unit.stats.chop_power > 0
                            && unit.free_capacity() > 0
                            && view.plants.iter().any(|plant| plant.cell == goal.cell)
                    }
                    R1faJob::Drop => unit.total_carried() > 0,
                    R1faJob::Mine => {
                        unit.stats.chop_power > 0 && unit.free_capacity() > 0
                    }
                }
            }

            fn command_for_goal(
                view: &GameState,
                unit: &Unit,
                goal: R1faGoal,
            ) -> Option<String> {
                match goal.job {
                    R1faJob::Seed(kind) => {
                        if is_adjacent(unit.cell, view.shacks[0]) {
                            Some(format!("PICK {} {}", unit.id, kind.as_str()))
                        } else {
                            Self::bank_cell(view, unit)
                                .map(|cell| Self::move_command(view, unit, cell))
                        }
                    }
                    R1faJob::Plant(kind) => {
                        if unit.cell == goal.cell {
                            Some(format!("PLANT {} {}", unit.id, kind.as_str()))
                        } else {
                            Some(Self::move_command(view, unit, goal.cell))
                        }
                    }
                    R1faJob::Harvest(_) => {
                        if unit.cell == goal.cell {
                            view.plants
                                .iter()
                                .find(|plant| plant.cell == goal.cell)
                                .filter(|plant| plant.fruits > 0)
                                .map(|_| format!("HARVEST {}", unit.id))
                        } else {
                            Some(Self::move_command(view, unit, goal.cell))
                        }
                    }
                    R1faJob::Chop => {
                        if unit.cell == goal.cell {
                            Some(format!("CHOP {}", unit.id))
                        } else {
                            Some(Self::move_command(view, unit, goal.cell))
                        }
                    }
                    R1faJob::Drop => Self::drop_command(view, unit),
                    R1faJob::Mine => {
                        if view.iron.iter().any(|iron| is_adjacent(*iron, unit.cell)) {
                            Some(format!("MINE {}", unit.id))
                        } else {
                            Some(Self::move_command(view, unit, goal.cell))
                        }
                    }
                }
            }

            fn resolve_move_conflicts(
                &self,
                view: &GameState,
                mut commands: Vec<String>,
                egress: Option<i32>,
            ) -> Vec<String> {
                let mut priority_ids: BTreeSet<i32> = self
                    .goals
                    .iter()
                    .filter(|(_, goal)| {
                        matches!(goal.job, R1faJob::Drop | R1faJob::Plant(_))
                    })
                    .map(|(id, _)| *id)
                    .collect();
                priority_ids.extend(egress);
                MoisanBot::resolve_move_conflicts_with_egress(
                    view,
                    &mut commands,
                    &priority_ids,
                    &BTreeSet::new(),
                    egress,
                );
                commands
            }

            // Where our own units stand once the resolved MOVE commands are applied.
            // Only an own unit's explicit destination within its movement speed is
            // predictable; an unknown id or an unreachable endpoint fails closed, and
            // an opponent on the shack is never predicted away.
            fn shack_clear_after_moves(view: &GameState, commands: &[String]) -> bool {
                if view
                    .units
                    .iter()
                    .any(|unit| unit.player == 1 && unit.cell == view.shacks[0])
                {
                    return false;
                }
                let mut predicted: BTreeMap<i32, Cell> = view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 0)
                    .map(|unit| (unit.id, unit.cell))
                    .collect();
                let mut moved = BTreeSet::new();
                for command in commands {
                    if !command.split_whitespace().next()
                        .is_some_and(|verb| verb.eq_ignore_ascii_case("MOVE"))
                    {
                        continue;
                    }
                    let Some((id, target)) = MoisanBot::move_command(command) else {
                        return false;
                    };
                    if !moved.insert(id) { return false; }
                    let Some(unit) = view.unit(id).filter(|unit| unit.player == 0) else {
                        return false;
                    };
                    let speed = unit.stats.movement_speed;
                    if speed < 1 || !bfs_distances(&view.walkable, &[unit.cell])
                        .get(&target)
                        .is_some_and(|distance| *distance <= speed)
                    {
                        return false;
                    }
                    predicted.insert(id, target);
                }
                // Unique endpoints suffice for own-unit chains/cycles under the
                // referee. A duplicate may leave an upstream shack occupant blocked.
                let endpoints: BTreeSet<Cell> = predicted.values().copied().collect();
                endpoints.len() == predicted.len() && !endpoints.contains(&view.shacks[0])
            }

            fn post_kind(&self, view: &GameState) -> Option<PlantKind> {
                [PlantKind::Banana, PlantKind::Apple, PlantKind::Plum, PlantKind::Lemon]
                    .iter()
                    .copied()
                    .find(|kind| view.inventories[0][Self::index(*kind)] > 0)
            }

            fn choose_goal(
                &self,
                view: &GameState,
                unit: &Unit,
                ordinal: usize,
                workers: usize,
                train_intent: bool,
                cost: Option<&[i32; 6]>,
                deficits: &[i32; 6],
                shortages: &[i32; 4],
                reserved: &BTreeSet<Cell>,
                assigned_resources: &BTreeSet<usize>,
            ) -> Option<R1faGoal> {
                if unit.total_carried() > 0 {
                    if view.turn < 276 {
                        if let Some(kind) = Self::carried_fruit(unit) {
                            let source_needed = shortages[Self::index(kind)] > 0;
                            let maintain = cost.is_none() && self.planted_count(view, None) < 10;
                            if source_needed || maintain {
                                if let Some(cell) = Self::plant_cell(view, unit, kind, reserved) {
                                    return Some(R1faGoal {
                                        job: R1faJob::Plant(kind),
                                        cell,
                                    });
                                }
                            }
                        }
                    }
                    let completes_bill = cost.is_some_and(|bill| (PLUM..=IRON)
                        .all(|item| view.inventories[0][item] + unit.carry[item] >= bill[item]));
                    let deposit_for_capital = if PARALLEL_CAPITAL { completes_bill } else { Self::useful_for_bill(unit, deficits) };
                    if deposit_for_capital || unit.free_capacity() == 0 {
                        return Some(R1faGoal {
                            job: R1faJob::Drop,
                            cell: view.shacks[0],
                        });
                    }
                    if let Some(goal) = self.goals.get(&unit.id) {
                        if let R1faJob::Harvest(kind) = goal.job {
                            if unit.cell == goal.cell && unit.stats.harvest_power > 0
                                && unit.free_capacity() > 0
                                && view.plants.iter().any(|p| p.cell == goal.cell && p.fruits > 0)
                            {
                                return Some(R1faGoal { job: R1faJob::Harvest(kind), cell: goal.cell });
                            }
                        }
                    }
                    return Some(R1faGoal {
                        job: R1faJob::Drop,
                        cell: view.shacks[0],
                    });
                }

                if train_intent {
                    return None;
                }

                let producer = Self::capital_producer(view, unit);
                let hybrid = false;
                if cost.is_some() && (producer || hybrid) {
                    let source_resource = (PLUM..=APPLE)
                        .filter(|index| {
                            shortages[*index] > 0 && !assigned_resources.contains(index)
                        })
                        .max_by_key(|index| (shortages[*index], -(*index as i32)));
                    if let Some(index) = source_resource {
                        let kind = Self::kind(index);
                        if view.inventories[0][index] > 0 {
                            return Some(R1faGoal {
                                job: R1faJob::Seed(kind),
                                cell: view.shacks[0],
                            });
                        }
                        if unit.stats.harvest_power > 0 {
                            if let Some(cell) =
                                Self::harvest_cell(view, unit, Some(kind), reserved, true)
                            {
                                return Some(R1faGoal {
                                    job: R1faJob::Harvest(kind),
                                    cell,
                                });
                            }
                        }
                    }

                    let fruit_resource = (PLUM..=APPLE)
                        .filter(|index| {
                            deficits[*index] > 0 && !assigned_resources.contains(index)
                        })
                        .max_by_key(|index| (deficits[*index], -(*index as i32)));
                    if producer {
                        if let Some(index) = fruit_resource {
                            let kind = Self::kind(index);
                            if let Some(cell) =
                                Self::harvest_cell(view, unit, Some(kind), reserved, true)
                            {
                                return Some(R1faGoal {
                                    job: R1faJob::Harvest(kind),
                                    cell,
                                });
                            }
                        }
                    }
                    if deficits[IRON] > 0 && (hybrid || fruit_resource.is_none()) {
                        if let Some(cell) = Self::mine_cell(view, unit, reserved) {
                            return Some(R1faGoal {
                                job: R1faJob::Mine,
                                cell,
                            });
                        }
                    }
                }

                if let Some(goal) = self.production_goal(view, unit, deficits, reserved) {
                    return Some(goal);
                }

                if cost.is_none() || producer {
                    if view.turn < 276 && self.planted_count(view, None) < 10 {
                        if let Some(kind) = self.post_kind(view) {
                            return Some(R1faGoal {
                                job: R1faJob::Seed(kind),
                                cell: view.shacks[0],
                            });
                        }
                    }
                }

                if unit.stats.harvest_power > 0 {
                    if let Some(cell) = Self::harvest_cell(view, unit, None, reserved, true) {
                        let kind = view
                            .plants
                            .iter()
                            .find(|plant| plant.cell == cell)
                            .map(|plant| plant.kind)
                            .unwrap_or(PlantKind::Plum);
                        return Some(R1faGoal {
                            job: R1faJob::Harvest(kind),
                            cell,
                        });
                    }
                }
                None
            }
        }

        impl Bot for R1faBot {
            fn commands(&mut self, view: &GameState) -> Vec<String> {
                if view.turn == 1 {
                    self.goals.clear();
                    self.planted.clear();
                    self.previous_plants = view
                        .plants
                        .iter()
                        .filter(|plant| plant.health > 0)
                        .map(|plant| plant.cell)
                        .collect();
                    self.opponent_plants.clear();
                    self.focus = None;
                }
                // One selection per game: latched on the first view we are given.
                if self.focus.is_none() {
                    self.focus = Some(Self::focus_type(view));
                }
                let current_plants: BTreeSet<Cell> = view
                    .plants
                    .iter()
                    .filter(|plant| plant.health > 0)
                    .map(|plant| plant.cell)
                    .collect();
                for cell in current_plants.difference(&self.previous_plants) {
                    if !self.planted.contains(cell) {
                        self.opponent_plants.insert(*cell);
                    }
                }
                self.opponent_plants.retain(|cell| current_plants.contains(cell));
                self.previous_plants = current_plants;
                self.planted
                    .retain(|cell| view.plants.iter().any(|plant| plant.cell == *cell));

                let units = Self::own_units(view);
                let workers = units.len();
                let spec = Self::planned_spec(view, workers);
                let cost = spec.map(|value| training_cost(workers as i32, value));
                let affordable_now = cost
                    .as_ref()
                    .is_some_and(|bill| Self::affordable(view, bill));
                // Any unit, ours or the opponent's, denies an exit cell.
                let occupied: BTreeSet<Cell> =
                    view.units.iter().map(|unit| unit.cell).collect();
                let training_egress = units
                    .iter()
                    .find(|unit| unit.cell == view.shacks[0])
                    .and_then(|unit| {
                        ortho_neighbors(view.shacks[0])
                            .into_iter()
                            .filter(|cell| {
                                view.walkable.contains(cell) && !occupied.contains(cell)
                            })
                            .min()
                            .map(|cell| (unit.id, cell))
                    });
                let shack_is_clear = !units.iter().any(|unit| unit.cell == view.shacks[0]);
                let enemy_on_shack = view
                    .units
                    .iter()
                    .any(|unit| unit.player == 1 && unit.cell == view.shacks[0]);
                // The referee resolves MOVE before TRAIN (TRAIN-EGRESS-FINDING), so an
                // own occupant that can leave this turn does not deny the purchase; an
                // enemy standing on the shack does, and we cannot move it. This is only
                // an intent: the bill is emitted after movement resolution confirms it.
                let train_intent = affordable_now
                    && !enemy_on_shack
                    && (shack_is_clear || training_egress.is_some());
                let deficits = Self::deficits(view, cost.as_ref());
                let shortages = self.source_shortages(view, cost.as_ref());
                let alive: BTreeSet<_> = units.iter().map(|unit| unit.id).collect();
                self.goals.retain(|id, _| alive.contains(id));

                let mut reserved = BTreeSet::new();
                let mut assigned_resources = BTreeSet::new();
                let mut commands = Vec::new();
                let mut seed_stock = view.inventories[0];
                if train_intent {
                    if let Some(bill) = cost {
                        for item in PLUM..=IRON { seed_stock[item] -= bill[item]; }
                    }
                }
                for (ordinal, unit) in units.into_iter().enumerate() {
                    if train_intent && training_egress.is_some_and(|(id, _)| id == unit.id) {
                        let (_, cell) = training_egress.expect("training egress checked above");
                        commands.push(Self::move_command(view, unit, cell));
                        self.goals.remove(&unit.id);
                        continue;
                    }
                    let mut goal = self.goals.get(&unit.id).copied().filter(|goal| {
                        !reserved.contains(&goal.cell)
                            && self.goal_valid(view, unit, *goal, &shortages)
                            && match goal.job {
                                R1faJob::Harvest(kind) => cost.is_some()
                                    && Self::capital_producer(view, unit)
                                    && deficits[Self::index(kind)] > 0,
                                R1faJob::Mine => cost.is_some() && deficits[IRON] > 0,
                                R1faJob::Seed(_) => cost.is_some(),
                                _ => true,
                            }
                    });
                    if unit.total_carried() > 0 {
                        if let Some(R1faGoal {
                            job: R1faJob::Seed(kind),
                            ..
                        }) = goal
                        {
                            if unit.carry[Self::index(kind)] > 0 {
                                goal = Self::plant_cell(view, unit, kind, &reserved).map(|cell| {
                                    R1faGoal {
                                        job: R1faJob::Plant(kind),
                                        cell,
                                    }
                                });
                            }
                        }
                    }
                    if unit.total_carried() > 0
                        && !goal.is_some_and(|value| {
                            matches!(value.job, R1faJob::Plant(_) | R1faJob::Drop)
                        })
                    {
                        goal = None;
                    }
                    if goal.is_none() {
                        goal = self.choose_goal(
                            view,
                            unit,
                            ordinal,
                            workers,
                            train_intent,
                            cost.as_ref(),
                            &deficits,
                            &shortages,
                            &reserved,
                            &assigned_resources,
                        );
                    }
                    if let Some(goal) = goal {
                        if let R1faJob::Seed(kind) | R1faJob::Harvest(kind) | R1faJob::Plant(kind) =
                            goal.job
                        {
                            assigned_resources.insert(Self::index(kind));
                        }
                        if !matches!(goal.job, R1faJob::Drop) {
                            reserved.insert(goal.cell);
                        }
                        if matches!(goal.job, R1faJob::Plant(_)) && unit.cell == goal.cell {
                            self.planted.insert(goal.cell);
                        }
                        if let Some(command) = Self::command_for_goal(view, unit, goal) {
                            if command.starts_with("PICK ") {
                                if let R1faJob::Seed(kind) = goal.job {
                                    let item = Self::index(kind);
                                    if seed_stock[item] <= 0 {
                                        commands.push("WAIT".to_string());
                                        self.goals.remove(&unit.id);
                                        continue;
                                    }
                                    seed_stock[item] -= 1;
                                }
                            }
                            commands.push(command);
                            self.goals.insert(unit.id, goal);
                        } else {
                            self.goals.remove(&unit.id);
                        }
                    } else {
                        self.goals.remove(&unit.id);
                    }
                }
                // Movement resolves first, so the commands are final before the shack
                // is checked. A withheld purchase spends nothing and invents no worker.
                let mut commands = self.resolve_move_conflicts(
                    view,
                    commands,
                    training_egress.filter(|_| train_intent).map(|(id, _)| id),
                );
                if train_intent && Self::shack_clear_after_moves(view, &commands) {
                    if let Some(spec) = spec {
                        commands.push(format!(
                            "TRAIN {} {} {} {}",
                            spec.0, spec.1, spec.2, spec.3
                        ));
                    }
                }
                if commands.is_empty() { commands.push("WAIT".to_string()); }
                commands
            }
        }
