// The champion of record ("door 1"), in the canonical readable format.
//
// Source of this file: cgauto/submissions/candidate-door1-pure-deletion.rs
//   (75,653 bytes, SHA-256 547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0)
// produced by claude_1/readable-source/format_readable.py with the pinned rustfmt 1.9.0.
//
// This file is for READING. Comments and layout are free: the compactor
// (cgauto/compact_rust_source.py) deletes them, so they cannot change the program.
// Changing any *token* produces a new candidate and must pass the usual gates.
//
// How to check it is the same program (the round-trip gate, docs/readable-format.md):
//   python3 cgauto/compact_rust_source.py readable/door1-champion.rs a.rs
//   python3 cgauto/compact_rust_source.py cgauto/submissions/candidate-door1-pure-deletion.rs b.rs
//   sha256sum a.rs b.rs   -> both 0da12c33e07a4524a5411a624d0d0da12b2e2f815b176b75df9d6d97c5c3ca01
// The source file was never fully minified, so compacting this file does NOT reproduce
// 547fa706... byte for byte; the gate is that both compact to identical bytes
// (report: readable/reports/door1-champion.round-trip.json, verdict READABLE_SOURCE_ROUND_TRIP_EXACT).
//
// Lineage: cure C (cgauto/submissions/submitted-sub41153619-cure-c-quiet.rs, ad3bfefe...) minus
// one pure-deletion hunk (the "fictional decay" inference) = this program; owner KEEP 2026-08-21.
// Earlier ancestors carried an "orchard_stripped" expansion header (parent 102caecd...); that
// lineage line does not apply to this file and was removed on 2026-08-26.
//
// Annotated blocks: claude_1/block-index/blocks.json (block names are stable across the lineage).

mod game {

    // === types =============================================================
    // Core game vocabulary: cells, plant kinds, unit stats, and the per-turn GameState
    // snapshot.
    pub mod types {
        use std::collections::BTreeSet;
        pub type Cell = (i32, i32);
        pub const ITEM_COUNT: usize = 6;
        pub const PLUM: usize = 0;
        pub const LEMON: usize = 1;
        pub const APPLE: usize = 2;
        pub const BANANA: usize = 3;
        pub const IRON: usize = 4;
        pub const WOOD: usize = 5;
        pub type Stock = [i32; ITEM_COUNT];
        #[derive(Clone, Copy, Debug, Eq, PartialEq, Ord, PartialOrd, Hash)]
        pub enum PlantKind {
            Plum,
            Lemon,
            Apple,
            Banana,
        }
        impl PlantKind {
            pub fn parse(value: &str) -> Option<PlantKind> {
                match value.to_ascii_uppercase().as_str() {
                    "PLUM" => Some(PlantKind::Plum),
                    "LEMON" => Some(PlantKind::Lemon),
                    "APPLE" => Some(PlantKind::Apple),
                    "BANANA" => Some(PlantKind::Banana),
                    _ => None,
                }
            }
            pub fn as_str(self) -> &'static str {
                match self {
                    PlantKind::Plum => "PLUM",
                    PlantKind::Lemon => "LEMON",
                    PlantKind::Apple => "APPLE",
                    PlantKind::Banana => "BANANA",
                }
            }
            pub fn item_index(self) -> usize {
                match self {
                    PlantKind::Plum => PLUM,
                    PlantKind::Lemon => LEMON,
                    PlantKind::Apple => APPLE,
                    PlantKind::Banana => BANANA,
                }
            }
        }
        #[derive(Clone, Copy, Debug, Eq, PartialEq)]
        pub struct Stats {
            pub movement_speed: i32,
            pub carry_capacity: i32,
            pub harvest_power: i32,
            pub chop_power: i32,
        }
        impl Stats {
            pub fn tuple(self) -> (i32, i32, i32, i32) {
                (
                    self.movement_speed,
                    self.carry_capacity,
                    self.harvest_power,
                    self.chop_power,
                )
            }
        }
        #[derive(Clone, Debug, Eq, PartialEq)]
        pub struct Unit {
            pub id: i32,
            pub player: usize,
            pub cell: Cell,
            pub stats: Stats,
            pub carry: Stock,
        }
        impl Unit {
            pub fn total_carried(&self) -> i32 {
                self.carry.iter().sum()
            }
            pub fn free_capacity(&self) -> i32 {
                self.stats.carry_capacity - self.total_carried()
            }
        }
        #[derive(Clone, Debug, Eq, PartialEq)]
        pub struct Plant {
            pub kind: PlantKind,
            pub cell: Cell,
            pub size: i32,
            pub health: i32,
            pub fruits: i32,
            pub cooldown: i32,
        }
        #[derive(Clone, Debug, Eq, PartialEq)]
        pub struct GameState {
            pub width: i32,
            pub height: i32,
            pub walkable: BTreeSet<Cell>,
            pub shacks: [Cell; 2],
            pub inventories: [Stock; 2],
            pub units: Vec<Unit>,
            pub plants: Vec<Plant>,
            pub scores: [i32; 2],
            pub turn: i32,
            pub next_id: i32,
            pub iron: BTreeSet<Cell>,
            pub water: BTreeSet<Cell>,
        }
        impl GameState {
            pub fn plant_at(&self, cell: Cell) -> Option<usize> {
                self.plants.iter().position(|plant| plant.cell == cell)
            }
            pub fn unit(&self, id: i32) -> Option<&Unit> {
                self.units.iter().find(|unit| unit.id == id)
            }
        }
    }

    // === rules =============================================================
    // Referee arithmetic reproduced exactly: growth cooldowns, tree health, training costs,
    // scoring.
    pub mod rules {
        use super::types::{PlantKind, Stock, APPLE, IRON, LEMON, PLUM, WOOD};
        pub const TOTAL_TURNS: i32 = 300;
        pub const WOOD_POINTS: i32 = 4;
        pub fn plant_cooldown(kind: PlantKind) -> i32 {
            match kind {
                PlantKind::Plum => 8,
                PlantKind::Lemon => 8,
                PlantKind::Apple => 9,
                PlantKind::Banana => 6,
            }
        }
        pub fn water_boost(kind: PlantKind) -> i32 {
            match kind {
                PlantKind::Plum => 5,
                PlantKind::Lemon => 5,
                PlantKind::Apple => 7,
                PlantKind::Banana => 2,
            }
        }
        pub fn tree_health_params(kind: PlantKind) -> (i32, i32) {
            match kind {
                PlantKind::Plum | PlantKind::Lemon => (4, 2),
                PlantKind::Apple => (8, 3),
                PlantKind::Banana => (2, 1),
            }
        }
        pub fn tree_health(kind: PlantKind, size: i32) -> i32 {
            let (base, slope) = tree_health_params(kind);
            base + slope * size
        }
        pub fn effective_cooldown(kind: PlantKind, near_water: bool) -> i32 {
            plant_cooldown(kind) - if near_water { water_boost(kind) } else { 0 }
        }
        pub fn training_cost(n: i32, talents: (i32, i32, i32, i32)) -> Stock {
            let (ms, cc, hp, chop) = talents;
            let mut cost = [0; 6];
            cost[PLUM] = n + ms * ms;
            cost[LEMON] = n + cc * cc;
            cost[APPLE] = n + hp * hp;
            cost[IRON] = n + chop * chop;
            cost
        }
        pub fn score(inventory: &Stock) -> i32 {
            inventory[PLUM]
                + inventory[LEMON]
                + inventory[APPLE]
                + inventory[3]
                + WOOD_POINTS * inventory[WOOD]
        }
        pub fn item_index(name: &str) -> Option<usize> {
            match name.to_ascii_uppercase().as_str() {
                "PLUM" => Some(PLUM),
                "LEMON" => Some(LEMON),
                "APPLE" => Some(APPLE),
                "BANANA" => Some(3),
                "IRON" => Some(IRON),
                "WOOD" => Some(WOOD),
                _ => None,
            }
        }
    }

    // === nav ===============================================================
    // Grid navigation: orthogonal neighbours, Manhattan distance, and breadth-first distance
    // maps.
    pub mod nav {
        use super::types::Cell;
        use std::collections::{BTreeMap, BTreeSet, VecDeque};
        pub const NEIGHBORS: [Cell; 4] = [(0, 1), (1, 0), (0, -1), (-1, 0)];
        pub fn manhattan(a: Cell, b: Cell) -> i32 {
            (a.0 - b.0).abs() + (a.1 - b.1).abs()
        }
        pub fn ortho_neighbors(cell: Cell) -> [Cell; 4] {
            [
                (cell.0, cell.1 + 1),
                (cell.0 + 1, cell.1),
                (cell.0, cell.1 - 1),
                (cell.0 - 1, cell.1),
            ]
        }
        pub fn is_adjacent(a: Cell, b: Cell) -> bool {
            manhattan(a, b) == 1
        }
        pub fn bfs_distances(walkable: &BTreeSet<Cell>, sources: &[Cell]) -> BTreeMap<Cell, i32> {
            let mut dist = BTreeMap::new();
            let mut queue = VecDeque::new();
            for &cell in sources {
                if dist.insert(cell, 0).is_none() {
                    queue.push_back(cell);
                }
            }
            while let Some(cell) = queue.pop_front() {
                let d = dist[&cell];
                for delta in NEIGHBORS {
                    let next = (cell.0 + delta.0, cell.1 + delta.1);
                    if walkable.contains(&next) && !dist.contains_key(&next) {
                        dist.insert(next, d + 1);
                        queue.push_back(next);
                    }
                }
            }
            dist
        }
        pub fn next_cell(
            walkable: &BTreeSet<Cell>,
            current: Cell,
            target: Cell,
            speed: i32
        ) -> Cell {
            let from_current = bfs_distances(walkable, &[current]);
            if let Some(distance) = from_current.get(&target) {
                if *distance <= speed {
                    return target;
                }
            }
            let to_target = if !from_current.contains_key(&target) {
                if from_current.is_empty() {
                    return current;
                }
                let best_manhattan = from_current
                    .keys()
                    .map(|cell| manhattan(target, *cell))
                    .min()
                    .unwrap();
                let goals: Vec<Cell> = from_current
                    .keys()
                    .filter(|cell| manhattan(target, **cell) == best_manhattan)
                    .copied()
                    .collect();
                bfs_distances(walkable, &goals)
            } else {
                bfs_distances(walkable, &[target])
            };
            from_current
                .iter()
                .filter(|(cell, distance)| **distance <= speed && to_target.contains_key(*cell))
                .map(|(cell, _)| *cell)
                .min_by_key(|cell| (to_target[cell], *cell))
                .unwrap_or(current)
        }
    }

    // === protocol ==========================================================
    // Reads the platform's turn protocol from stdin into a GameState.
    pub mod protocol {
        use super::rules::score;
        use super::types::{Cell, GameState, Plant, PlantKind, Stats, Unit};
        use std::collections::BTreeSet;
        use std::io::BufRead;
        #[derive(Clone, Debug)]
        pub struct StaticMap {
            pub width: i32,
            pub height: i32,
            pub walkable: BTreeSet<Cell>,
            pub shacks: [Cell; 2],
            pub iron: BTreeSet<Cell>,
            pub water: BTreeSet<Cell>,
        }
        pub fn read_line(reader: &mut impl BufRead) -> Option<String> {
            let mut line = String::new();
            match reader.read_line(&mut line) {
                Ok(0) => None,
                Ok(_) => Some(
                    line.trim_end_matches('\n')
                        .trim_end_matches('\r')
                        .to_string(),
                ),
                Err(_) => None,
            }
        }
        pub fn read_static_map(reader: &mut impl BufRead) -> Option<StaticMap> {
            let header = read_line(reader)?;
            let mut parts = header.split_whitespace();
            let width = parts.next()?.parse().ok()?;
            let height = parts.next()?.parse().ok()?;
            let mut rows = Vec::new();
            for _ in 0..height {
                rows.push(read_line(reader)?);
            }
            Some(parse_static_map(width, height, &rows))
        }
        pub fn parse_static_map(width: i32, height: i32, rows: &[String]) -> StaticMap {
            let mut walkable = BTreeSet::new();
            let mut shacks = [(0, 0), (0, 0)];
            let mut iron = BTreeSet::new();
            let mut water = BTreeSet::new();
            for (y, row) in rows.iter().enumerate() {
                for (x, ch) in row.chars().enumerate() {
                    let cell = (x as i32, y as i32);
                    match ch {
                        '0' => shacks[0] = cell,
                        '1' => shacks[1] = cell,
                        '.' => {
                            walkable.insert(cell);
                        }
                        '+' => {
                            iron.insert(cell);
                        }
                        '~' => {
                            water.insert(cell);
                        }
                        _ => {}
                    }
                }
            }
            StaticMap {
                width,
                height,
                walkable,
                shacks,
                iron,
                water,
            }
        }
        pub fn read_turn(
            reader: &mut impl BufRead,
            map: &StaticMap,
            turn: i32
        ) -> Option<GameState> {
            let mut inventories = [[0; 6]; 2];
            for inv in &mut inventories {
                let line = read_line(reader)?;
                let values: Vec<i32> = line
                    .split_whitespace()
                    .map(|value| value.parse().ok())
                    .collect::<Option<Vec<i32>>>()?;
                if values.len() != 6 {
                    return None;
                }
                inv.copy_from_slice(&values);
            }
            let tree_count: usize = read_line(reader)?.trim().parse().ok()?;
            let mut plants = Vec::with_capacity(tree_count);
            for _ in 0..tree_count {
                let line = read_line(reader)?;
                let fields: Vec<&str> = line.split_whitespace().collect();
                if fields.len() != 7 {
                    return None;
                }
                plants.push(Plant {
                    kind: PlantKind::parse(fields[0])?,
                    cell: (fields[1].parse().ok()?, fields[2].parse().ok()?),
                    size: fields[3].parse().ok()?,
                    health: fields[4].parse().ok()?,
                    fruits: fields[5].parse().ok()?,
                    cooldown: fields[6].parse().ok()?,
                });
            }
            let unit_count: usize = read_line(reader)?.trim().parse().ok()?;
            let mut units = Vec::with_capacity(unit_count);
            let mut next_id = 0;
            for _ in 0..unit_count {
                let line = read_line(reader)?;
                let values: Vec<i32> = line
                    .split_whitespace()
                    .map(|value| value.parse().ok())
                    .collect::<Option<Vec<i32>>>()?;
                if values.len() != 14 {
                    return None;
                }
                next_id = next_id.max(values[0] + 1);
                units.push(Unit {
                    id: values[0],
                    player: values[1] as usize,
                    cell: (values[2], values[3]),
                    stats: Stats {
                        movement_speed: values[4],
                        carry_capacity: values[5],
                        harvest_power: values[6],
                        chop_power: values[7],
                    },
                    carry: [
                        values[8], values[9], values[10], values[11], values[12], values[13],
                    ],
                });
            }
            Some(GameState {
                width: map.width,
                height: map.height,
                walkable: map.walkable.clone(),
                shacks: map.shacks,
                inventories,
                units,
                plants,
                scores: [score(&inventories[0]), score(&inventories[1])],
                turn,
                next_id,
                iron: map.iron.clone(),
                water: map.water.clone(),
            })
        }
    }
    pub use types::GameState;
}
mod bot {

    // === moisan ============================================================
    // The policy itself: candidate generation, scoring, conflict resolution and the orchard
    // wrapper.
    pub mod moisan {
        use super::Bot;
        use crate::game::nav::{bfs_distances, is_adjacent, manhattan, next_cell, ortho_neighbors};
        use crate::game::rules::{
            effective_cooldown, item_index, score, training_cost, tree_health, TOTAL_TURNS,
        };
        use crate::game::types::{
            Cell, GameState, Plant, PlantKind, Stats, Unit, APPLE, BANANA, IRON, LEMON, PLUM,
        };
        use std::collections::{BTreeMap, BTreeSet};
        #[derive(Clone, Copy, Debug, Eq, PartialEq, Ord, PartialOrd)]
        enum Target {
            None,
            Shack,
            Bank(Cell),
            Cell(Cell),
            Tree(Cell),
        }
        #[derive(Clone, Debug)]
        struct Candidate {
            command: String,
            score: f64,
            target: Target,
        }
        struct MoisanBot;
        #[derive(Clone, Copy, Debug, Eq, PartialEq)]

        // --------------------------------------------------------------------------
        // Opening policy configuration record — indexed block `opening-policy-record`
        // [configuration]
        //
        // Seven-field tuning record (train horizon, carry/chop preferences and caps, extra-ETA
        // allowance, hard train turn) selecting the second worker's stats.
        //
        // Costs 580 bytes of source.
        // --------------------------------------------------------------------------
        pub struct YamoOpeningPolicy {
            pub train_horizon: i32,
            pub preferred_min_carry: i32,
            pub max_carry_capacity: i32,
            pub preferred_min_chop: i32,
            pub max_chop_power: i32,
            pub require_preferred: bool,
            pub max_extra_eta: i32,
            pub hard_train_turn: i32,
            pub prefer_movement_ties: bool,
        }

        // --------------------------------------------------------------------------
        // Opening policy configuration record — indexed block `opening-policy-record`
        // [configuration]
        //
        // Seven-field tuning record (train horizon, carry/chop preferences and caps, extra-ETA
        // allowance, hard train turn) selecting the second worker's stats.
        //
        // Costs 580 bytes of source.
        // --------------------------------------------------------------------------
        impl YamoOpeningPolicy {
            pub const TUNED_CARRY: Self = Self {
                train_horizon: 15,
                preferred_min_carry: 2,
                max_carry_capacity: 3,
                preferred_min_chop: 1,
                max_chop_power: 3,
                require_preferred: false,
                max_extra_eta: 15,
                hard_train_turn: 35,
                prefer_movement_ties: false,
            };
        }
        #[derive(Clone, Copy, Debug, Eq, PartialEq)]
        struct OpeningObjective {
            stats: Stats,
            estimated_eta: i32,
        }
        pub struct YamoBot {
            announced: bool,
            announcement: &'static str,
            type_to_cut: Option<PlantKind>,
            desired_second: Option<OpeningObjective>,
            opening_initialized: bool,
            opening_abandoned: bool,
            opening_policy: YamoOpeningPolicy,
            idle_regeneration: bool,
            persistent_regeneration: bool,
            door_unblocking: bool,
            partial_bank_transit: bool,
            idle_harvest: bool,
            idle_harvest_clock_only: bool,
            regeneration_commitments: BTreeMap<i32, PlantKind>,
            // The opening dispatcher's memory (stage 2A): over once three trolls stand;
            // the seed each troll carries and the cell it is for; seeds picked so far;
            // each troll's target last turn (a small hold against flip-flops).
            opening_done: bool,
            opening_seeds: BTreeMap<i32, (PlantKind, Cell)>,
            opening_seed_count: usize,
            opening_targets: BTreeMap<i32, Cell>,
            // Contested, wood-aware third-troll plan. None means not admitted yet.
            opening_third: Option<Stats>,
            opening_third_deadline: i32,
            opening_third_shadow: [f64; 6],
            opening_third_net: f64,
            opening_third_recheck: i32,
            opponent_eta_penalty: i32,
        }
        #[derive(Clone, Copy)]
        struct PredictedTree {
            size: i32,
            health: i32,
            cooldown: i32,
        }
        impl MoisanBot {

            // --------------------------------------------------------------------------
            // Focus species selection — indexed block `focus-species-selection`
            // [shared-infrastructure]
            //
            // Chooses which fruit species to cut based on aggregate walking distance from the shack to
            // each species' trees.
            // --------------------------------------------------------------------------
            fn focus_type(view: &GameState) -> PlantKind {
                let starts: Vec<Cell> = ortho_neighbors(view.shacks[0])
                    .iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .copied()
                    .collect();
                let dist = bfs_distances(&view.walkable, &starts);
                let sum = |kind: PlantKind| 
                    view.plants
                        .iter()
                        .filter(|plant| plant.kind == kind)
                        .map(|plant| dist.get(&plant.cell).copied().unwrap_or(10_000))
                        .sum::<i32>()
                ;
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
            fn ceil_div(a: i32, b: i32) -> i32 {
                if b <= 0 {
                    10_000
                } else {
                    (a + b - 1) / b
                }
            }
            fn carry_total(unit: &Unit) -> i32 {
                unit.carry.iter().sum()
            }
            fn carrying_any(unit: &Unit) -> bool {
                Self::carry_total(unit) > 0
            }
            fn bank_candidates(view: &GameState, unit: &Unit) -> Vec<Candidate> {
                let dist = bfs_distances(&view.walkable, &[unit.cell]);
                let mut out: Vec<Candidate> = ortho_neighbors(view.shacks[0])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell) && dist.contains_key(cell))
                    .map(|cell| {
                        let at_drop = unit.cell == cell;
                        Candidate {
                            command: if at_drop {
                                format!("DROP {}", unit.id)
                            } else {
                                format!("MOVE {} {} {}", unit.id, cell.0, cell.1)
                            },
                            score: if at_drop {
                                8_000.0
                            } else {
                                7_000.0
                                    - Self::ceil_div(dist[&cell], unit.stats.movement_speed) as f64
                            },
                            target: Target::Bank(cell),
                        }
                    })
                    .collect();
                if out.is_empty() {
                    out.push(Candidate {
                        command: format!(
                            "MOVE {} {} {}",
                            unit.id, view.shacks[0].0, view.shacks[0].1
                        ),
                        score: 7_000.0,
                        target: Target::Shack,
                    });
                }
                out
            }
            fn can_train(view: &GameState, stats: Stats) -> bool {
                let n = view.units.iter().filter(|unit| unit.player == 0).count() as i32;
                if n >= 2 || TOTAL_TURNS - view.turn <= 20 {
                    return false;
                }
                let cost = training_cost(n, stats.tuple());
                let pay_iron = !view.iron.is_empty();
                view.inventories[0][PLUM] >= cost[PLUM]
                    && view.inventories[0][LEMON] >= cost[LEMON]
                    && view.inventories[0][APPLE] >= cost[APPLE]
                    && (!pay_iron || view.inventories[0][IRON] >= cost[IRON])
            }
            fn ticks_until_fruit(view: &GameState, plant: &Plant) -> i32 {
                if plant.fruits > 0 {
                    return 0;
                }
                let near_water = view
                    .water
                    .iter()
                    .any(|water| is_adjacent(*water, plant.cell));
                let mut size = plant.size;
                let mut cooldown = plant.cooldown.max(0);
                for turns in 1..=100 {
                    if cooldown > 0 {
                        cooldown -= 1;
                    }
                    if cooldown == 0 {
                        if size < 4 {
                            size += 1;
                            cooldown = effective_cooldown(plant.kind, near_water);
                        } else {
                            return turns;
                        }
                    }
                }
                100
            }
            fn early_candidates(view: &GameState, unit: &Unit, desired: Stats) -> Vec<Candidate> {
                let mut out = vec![Self::wait()];
                if Self::carrying_any(unit) || unit.free_capacity() <= 0 {
                    out.extend(Self::bank_candidates(view, unit));
                    return out;
                }
                let n = view.units.iter().filter(|unit| unit.player == 0).count() as i32;
                let cost = training_cost(n, desired.tuple());
                for item in [PLUM, LEMON, APPLE, IRON] {
                    if item == APPLE && cost[item] <= view.inventories[0][item] {
                        continue;
                    }
                    if item != APPLE && cost[item] <= view.inventories[0][item] {
                        continue;
                    }
                    if item == IRON {
                        out.extend(Self::iron_candidates(view, unit, 6_100.0));
                    } else {
                        let kind = match item {
                            PLUM => PlantKind::Plum,
                            LEMON => PlantKind::Lemon,
                            APPLE => PlantKind::Apple,
                            _ => unreachable!(),
                        };
                        out.extend(Self::fruit_candidates(view, unit, kind, 6_000.0));
                    }
                }
                if out.len() == 1 {
                    out.extend(Self::chop_candidates(view, unit, None));
                }
                out
            }
            fn fruit_candidates(
                view: &GameState,
                unit: &Unit,
                kind: PlantKind,
                base_score: f64,
            ) -> Vec<Candidate> {
                let mut out = Vec::new();
                if view
                    .plants
                    .iter()
                    .any(|plant| plant.cell == unit.cell && plant.kind == kind && plant.fruits > 0)
                {
                    out.push(Candidate {
                        command: format!("HARVEST {}", unit.id),
                        score: base_score + 900.0,
                        target: Target::Tree(unit.cell),
                    });
                }
                let dist = bfs_distances(&view.walkable, &[unit.cell]);
                for plant in &view.plants {
                    if plant.kind != kind || plant.health <= 0 || !dist.contains_key(&plant.cell) {
                        continue;
                    }
                    let travel = Self::ceil_div(dist[&plant.cell], unit.stats.movement_speed);
                    let wait = (Self::ticks_until_fruit(view, plant) - travel).max(0);
                    out.push(Candidate {
                        command: format!("MOVE {} {} {}", unit.id, plant.cell.0, plant.cell.1),
                        score: base_score - (travel + wait) as f64,
                        target: Target::Tree(plant.cell),
                    });
                }
                out
            }
            fn iron_candidates(view: &GameState, unit: &Unit, base_score: f64) -> Vec<Candidate> {
                let mut out = Vec::new();
                if view.iron.iter().any(|iron| is_adjacent(*iron, unit.cell)) {
                    out.push(Candidate {
                        command: format!("MINE {}", unit.id),
                        score: base_score + 900.0,
                        target: Target::Cell(unit.cell),
                    });
                }
                let dist = bfs_distances(&view.walkable, &[unit.cell]);
                for iron in &view.iron {
                    for cell in ortho_neighbors(*iron) {
                        if !view.walkable.contains(&cell) {
                            continue;
                        }
                        if let Some(d) = dist.get(&cell) {
                            out.push(Candidate {
                                command: format!("MOVE {} {} {}", unit.id, cell.0, cell.1),
                                score: base_score - *d as f64,
                                target: Target::Cell(cell),
                            });
                        }
                    }
                }
                out
            }
            fn predicted_opp_chop(view: &GameState, plant: &Plant) -> i32 {
                let on_tree: i32 = view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 1 && unit.cell == plant.cell)
                    .map(|unit| unit.stats.chop_power)
                    .sum();
                if on_tree > 0 {
                    return on_tree;
                }
                0
            }
            fn predict_tree(view: &GameState, plant: &Plant, turns: i32) -> Option<PredictedTree> {
                let mut size = plant.size;
                let mut health = plant.health;
                let mut fruits = plant.fruits;
                let mut cooldown = plant.cooldown;
                let opp_chop = Self::predicted_opp_chop(view, plant);
                let near_water = view
                    .water
                    .iter()
                    .any(|water| is_adjacent(*water, plant.cell));
                for _ in 0..turns {
                    if opp_chop > 0 {
                        health -= opp_chop;
                        if health <= 0 {
                            return None;
                        }
                    }
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
                Some(PredictedTree {
                    size,
                    health,
                    cooldown,
                })
            }
            fn chop_outcome(
                view: &GameState,
                plant: &Plant,
                predicted: PredictedTree,
                chop_power: i32,
            ) -> Option<(i32, i32)> {
                if chop_power <= 0 {
                    return None;
                }
                let near_water = view
                    .water
                    .iter()
                    .any(|water| is_adjacent(*water, plant.cell));
                let cooldown_reset = effective_cooldown(plant.kind, near_water);
                let (_, growth_health) = crate::game::rules::tree_health_params(plant.kind);
                let mut size = predicted.size;
                let mut health = predicted.health;
                let mut cooldown = predicted.cooldown;
                for turns in 1..=100 {
                    health -= chop_power;
                    if health <= 0 {
                        return Some((turns, size));
                    }
                    if cooldown > 0 {
                        cooldown -= 1;
                    }
                    if cooldown == 0 && size < 4 {
                        size += 1;
                        health += growth_health;
                        cooldown = cooldown_reset;
                    }
                }
                None
            }
            fn chop_candidates(
                view: &GameState,
                unit: &Unit,
                type_to_cut: Option<PlantKind>,
            ) -> Vec<Candidate> {
                let mut out = Vec::new();
                if unit.stats.chop_power <= 0 || unit.free_capacity() <= 0 {
                    return out;
                }
                let from_unit = bfs_distances(&view.walkable, &[unit.cell]);
                let shack_starts: Vec<Cell> = ortho_neighbors(view.shacks[0])
                    .iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .copied()
                    .collect();
                let to_shack = bfs_distances(&view.walkable, &shack_starts);
                let opponent_trolls = view.units.iter().filter(|unit| unit.player == 1).count();
                for plant in &view.plants {
                    if plant.health <= 0 || !from_unit.contains_key(&plant.cell) {
                        continue;
                    }
                    let travel_turns =
                        Self::ceil_div(from_unit[&plant.cell], unit.stats.movement_speed);
                    let Some(predicted) = Self::predict_tree(view, plant, travel_turns) else {
                        continue;
                    };
                    if predicted.size <= 0 || predicted.health <= 0 {
                        continue;
                    }
                    let return_turns = to_shack
                        .get(&plant.cell)
                        .map(|d| Self::ceil_div(*d, unit.stats.movement_speed))
                        .unwrap_or_else(|| {
                            Self::ceil_div(
                                manhattan(plant.cell, view.shacks[0]),
                                unit.stats.movement_speed,
                            )
                        });
                    let Some((chop_turns, final_size)) =
                        Self::chop_outcome(view, plant, predicted, unit.stats.chop_power)
                    else {
                        continue;
                    };
                    let turns = (travel_turns + chop_turns + return_turns + 1).max(1);
                    if turns > TOTAL_TURNS - view.turn + 1 {
                        continue;
                    }
                    let wood = final_size.min(unit.free_capacity());
                    if wood <= 0 {
                        continue;
                    }
                    let mut score = 1000.0 * wood as f64 / turns as f64;
                    let command = if plant.cell == unit.cell {
                        format!("CHOP {}", unit.id)
                    } else {
                        format!("MOVE {} {} {}", unit.id, plant.cell.0, plant.cell.1)
                    };
                    out.push(Candidate {
                        command,
                        score,
                        target: Target::Tree(plant.cell),
                    });
                }
                out
            }
            fn wait() -> Candidate {
                Candidate {
                    command: "WAIT".to_string(),
                    score: 0.0,
                    target: Target::None,
                }
            }
            fn compatible(a: Target, b: Target) -> bool {
                if a == Target::None || b == Target::None {
                    return true;
                }
                let cell = |target| match target {
                    Target::Bank(cell) | Target::Cell(cell) | Target::Tree(cell) => Some(cell),
                    _ => None,
                };
                match (cell(a), cell(b)) {
                    (Some(a), Some(b)) => a != b,
                    _ => a != b,
                }
            }
            fn picked_item(command: &str) -> Option<usize> {
                let fields: Vec<_> = command.split_whitespace().collect();
                (fields.len() == 3 && fields[0].eq_ignore_ascii_case("PICK"))
                    .then(|| item_index(fields[2]))
                    .flatten()
            }
            fn stock_compatible(a: &Candidate, b: &Candidate, inventory: &[i32; 6]) -> bool {
                match (Self::picked_item(&a.command), Self::picked_item(&b.command)) {
                    (Some(a), Some(b)) if a == b => inventory[a] >= 2,
                    _ => true,
                }
            }
            fn select(
                candidates_by_id: BTreeMap<i32, Vec<Candidate>>,
                inventory: &[i32; 6],
            ) -> Vec<String> {
                let ids: Vec<i32> = candidates_by_id.keys().copied().collect();
                if ids.is_empty() {
                    return Vec::new();
                }
                if ids.len() == 1 {
                    let best = candidates_by_id[&ids[0]]
                        .iter()
                        .max_by(|a, b| a.score.total_cmp(&b.score))
                        .unwrap();
                    return vec![best.command.clone()];
                }
                // The joint choice for every own troll at once (the third troll, 2026-08-28):
                // a depth-first walk over the trolls in id order through every combination of
                // one candidate per troll whose targets do not collide and whose PICKs do not
                // overdraw the shack; the best sum of scores wins, the first found on a tie.
                // With two trolls this is the pair search it replaces, choice for choice.
                let lists: Vec<&Vec<Candidate>> =
                    ids.iter().map(|id| &candidates_by_id[id]).collect();
                let combinations = lists
                    .iter()
                    .fold(1usize, |n, list| n.saturating_mul(list.len()));
                if combinations <= Self::JOINT_SELECT_LIMIT {
                    let mut best_score = f64::NEG_INFINITY;
                    let mut best_set = None;
                    let mut chosen = Vec::new();
                    Self::select_joint(
                        &lists,
                        inventory,
                        &mut chosen,
                        0.0,
                        &mut best_score,
                        &mut best_set,
                    );
                    if let Some(commands) = best_set {
                        return commands;
                    }
                }
                let mut used_targets = Vec::new();
                let mut used_stock = [0; 6];
                let mut commands = Vec::new();
                for id in ids {
                    let mut candidates = candidates_by_id[&id].clone();
                    candidates.sort_by(|a, b| b.score.total_cmp(&a.score));
                    let best = candidates
                        .into_iter()
                        .find(|candidate| {
                            used_targets
                                .iter()
                                .all(|target| Self::compatible(candidate.target, *target))
                                && Self::picked_item(&candidate.command)
                                    .map(|item| used_stock[item] < inventory[item])
                                    .unwrap_or(true)
                        })
                        .unwrap_or_else(Self::wait);
                    used_targets.push(best.target);
                    if let Some(item) = Self::picked_item(&best.command) {
                        used_stock[item] += 1;
                    }
                    commands.push(best.command);
                }
                commands
            }
            // Above this many combinations the greedy id-order pass below `select_joint`'s
            // call is used instead (never reached with the champion's list sizes; a bound on
            // the turn's time, not a behaviour).
            const JOINT_SELECT_LIMIT: usize = 400_000;
            fn select_joint<'a>(
                lists: &[&'a Vec<Candidate>],
                inventory: &[i32; 6],
                chosen: &mut Vec<&'a Candidate>,
                sum: f64,
                best_score: &mut f64,
                best_set: &mut Option<Vec<String>>,
            ) {
                let depth = chosen.len();
                if depth == lists.len() {
                    if sum > *best_score {
                        *best_score = sum;
                        *best_set = Some(chosen.iter().map(|c| c.command.clone()).collect());
                    }
                    return;
                }
                for candidate in lists[depth] {
                    let targets_fit = chosen
                        .iter()
                        .all(|earlier| Self::compatible(earlier.target, candidate.target));
                    let stock_fits = match Self::picked_item(&candidate.command) {
                        Some(item) => {
                            let taken = chosen
                                .iter()
                                .filter(|earlier| Self::picked_item(&earlier.command) == Some(item))
                                .count() as i32;
                            taken == 0 || inventory[item] >= taken + 1
                        }
                        None => true,
                    };
                    if !targets_fit || !stock_fits {
                        continue;
                    }
                    chosen.push(candidate);
                    Self::select_joint(
                        lists,
                        inventory,
                        chosen,
                        sum + candidate.score,
                        best_score,
                        best_set,
                    );
                    chosen.pop();
                }
            }
            fn move_command(command: &str) -> Option<(i32, Cell)> {
                let fields: Vec<&str> = command.split_whitespace().collect();
                if fields.len() != 4 || !fields[0].eq_ignore_ascii_case("MOVE") {
                    return None;
                }
                Some((
                    fields[1].parse().ok()?,
                    (fields[2].parse().ok()?, fields[3].parse().ok()?),
                ))
            }
            fn resolve_move_conflicts(view: &GameState, commands: &mut [String]) {
                Self::resolve_move_conflicts_with_priority(view, commands, &BTreeSet::new());
            }
            fn resolve_move_conflicts_with_priority(
                view: &GameState,
                commands: &mut [String],
                priority_ids: &BTreeSet<i32>,
            ) {
                Self::resolve_move_conflicts_with_priority_and_forbidden(
                    view,
                    commands,
                    priority_ids,
                    &BTreeSet::new(),
                );
            }
            fn resolve_move_conflicts_with_priority_and_forbidden(
                view: &GameState,
                commands: &mut [String],
                priority_ids: &BTreeSet<i32>,
                forbidden_for_non_priority: &BTreeSet<Cell>,
            ) {
                let command_by_id: BTreeMap<i32, usize> = commands
                    .iter()
                    .enumerate()
                    .filter_map(|(index, command)| 
                        Self::move_command(command).map(|(id, _)| (id, index))
                    )
                    .collect();
                let projections: Vec<(i32, usize, Cell, Cell, Cell)> = command_by_id
                    .iter()
                    .filter_map(|(id, index)| {
                        let unit = view.unit(*id)?;
                        let (_, target) = Self::move_command(&commands[*index])?;
                        let landing =
                            next_cell(&view.walkable, unit.cell, target, unit.stats.movement_speed);
                        Some((*id, *index, unit.cell, target, landing))
                    })
                    .collect();
                let moving_ids: BTreeSet<i32> = projections
                    .iter()
                    .filter(|(_, _, current, _, landing)| landing != current)
                    .map(|(id, _, _, _, _)| *id)
                    .collect();
                let occupied_now: BTreeSet<Cell> = view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 0)
                    .map(|unit| unit.cell)
                    .collect();
                let mut reserved: BTreeSet<Cell> = view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 0 && !moving_ids.contains(&unit.id))
                    .map(|unit| unit.cell)
                    .collect();
                for (_, index, current, _, landing) in &projections {
                    if landing == current {
                        commands[*index] = "WAIT".to_string();
                    }
                }
                let mut movers: Vec<(i32, usize, Cell, Cell)> = projections
                    .into_iter()
                    .filter(|(_, _, current, _, landing)| landing != current)
                    .map(|(id, index, _, target, landing)| (id, index, target, landing))
                    .collect();
                movers.sort_by(|a, b| {
                    let a_priority = priority_ids.contains(&a.0);
                    let b_priority = priority_ids.contains(&b.0);
                    b_priority.cmp(&a_priority).then_with(|| b.0.cmp(&a.0))
                });
                for (id, index, target, landing) in movers {
                    let Some(unit) = view.unit(id) else { continue };
                    let landing_forbidden = !priority_ids.contains(&id)
                        && forbidden_for_non_priority.contains(&landing);
                    if !landing_forbidden && !reserved.contains(&landing) {
                        reserved.insert(landing);
                        commands[index] = format!("MOVE {} {} {}", id, landing.0, landing.1);
                        continue;
                    }
                    let toward_goal = bfs_distances(&view.walkable, &[target]);
                    let detour = ortho_neighbors(unit.cell)
                        .into_iter()
                        .filter(|cell| view.walkable.contains(cell))
                        .filter(|cell| !reserved.contains(cell))
                        .filter(|cell| !occupied_now.contains(cell))
                        .filter(|cell| {
                            priority_ids.contains(&id) || !forbidden_for_non_priority.contains(cell)
                        })
                        .min_by_key(|cell| {
                            (
                                toward_goal
                                    .get(cell)
                                    .copied()
                                    .unwrap_or_else(|| manhattan(*cell, target)),
                                *cell,
                            )
                        });
                    commands[index] = if let Some(cell) = detour {
                        reserved.insert(cell);
                        format!("MOVE {} {} {}", id, cell.0, cell.1)
                    } else {
                        "WAIT".to_string()
                    };
                }
            }
        }
        impl YamoBot {
            pub fn with_opening_policy(opening_policy: YamoOpeningPolicy) -> Self {
                Self {
                    announced: false,
                    announcement: "yamo-waypoint-rust",
                    type_to_cut: None,
                    desired_second: None,
                    opening_initialized: false,
                    opening_abandoned: false,
                    opening_policy,
                    idle_regeneration: false,
                    persistent_regeneration: false,
                    door_unblocking: false,
                    partial_bank_transit: false,
                    idle_harvest: false,
                    idle_harvest_clock_only: false,
                    regeneration_commitments: BTreeMap::new(),
                    opponent_eta_penalty: 0,
                    opening_done: false,
                    opening_seeds: BTreeMap::new(),
                    opening_seed_count: 0,
                    opening_targets: BTreeMap::new(),
                    opening_third: None,
                    opening_third_deadline: 0,
                    opening_third_shadow: [1.0; 6],
                    opening_third_net: f64::NEG_INFINITY,
                    opening_third_recheck: 0,
                }
            }
            pub fn tuned_carry_regeneration_transit_idle_harvest() -> Self {
                let mut bot = Self::with_opening_policy(YamoOpeningPolicy::TUNED_CARRY);
                bot.announcement = "yamo-carry-regen-transit-idle-harvest-rust";
                bot.idle_regeneration = true;
                bot.persistent_regeneration = true;
                bot.door_unblocking = true;
                bot.partial_bank_transit = true;
                bot.idle_harvest = true;
                bot
            }
            fn ensure_opening(&mut self, view: &GameState) {
                if self.type_to_cut.is_none() {
                    self.type_to_cut = Some(MoisanBot::focus_type(view));
                }
                if !self.opening_initialized {
                    self.desired_second =
                        Some(Self::choose_second_troll(view, self.opening_policy));
                    self.opening_initialized = true;
                }
            }
            fn collection_eta(view: &GameState, item: usize, missing: i32) -> i32 {
                if missing <= 0 {
                    return 0;
                }
                let starts: Vec<Cell> = ortho_neighbors(view.shacks[0])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .collect();
                let distance = bfs_distances(&view.walkable, &starts);
                if item == IRON {
                    let best = view
                        .iron
                        .iter()
                        .flat_map(|iron| ortho_neighbors(*iron))
                        .filter_map(|cell| distance.get(&cell).copied())
                        .min();
                    return best.map_or(10_000, |d| missing * (2 * d + 2));
                }
                let kind = match item {
                    PLUM => PlantKind::Plum,
                    LEMON => PlantKind::Lemon,
                    APPLE => PlantKind::Apple,
                    BANANA => PlantKind::Banana,
                    _ => return 10_000,
                };
                view.plants
                    .iter()
                    .filter(|plant| plant.kind == kind && plant.health > 0)
                    .filter_map(|plant| {
                        let d = distance.get(&plant.cell).copied()?;
                        let ready = MoisanBot::ticks_until_fruit(view, plant);
                        let wait = (ready - d).max(0);
                        Some(missing * (2 * d + 2) + wait)
                    })
                    .min()
                    .unwrap_or(10_000)
            }
            fn opening_objective(view: &GameState, stats: Stats) -> OpeningObjective {
                let n = view.units.iter().filter(|unit| unit.player == 0).count() as i32;
                let cost = training_cost(n, stats.tuple());
                let mut estimated_eta = Self::collection_eta(
                    view,
                    PLUM,
                    (cost[PLUM] - view.inventories[0][PLUM]).max(0)
                ) + Self::collection_eta(
                    view,
                    LEMON,
                    (cost[LEMON] - view.inventories[0][LEMON]).max(0),
                );
                if !view.iron.is_empty() {
                    estimated_eta += Self::collection_eta(
                        view,
                        IRON,
                        (cost[IRON] - view.inventories[0][IRON]).max(0)
                    );
                }
                OpeningObjective {
                    stats,
                    estimated_eta,
                }
            }
            fn opening_key(
                objective: &OpeningObjective,
                policy: YamoOpeningPolicy,
            ) -> (i32, i32, i32, i32, i32) {
                let stats = objective.stats;
                let total = stats.movement_speed + stats.carry_capacity + stats.chop_power;
                if policy.prefer_movement_ties {
                    (
                        total,
                        -objective.estimated_eta,
                        stats.movement_speed,
                        stats.carry_capacity,
                        stats.chop_power,
                    )
                } else {
                    (
                        total,
                        -objective.estimated_eta,
                        stats.chop_power,
                        stats.carry_capacity,
                        stats.movement_speed,
                    )
                }
            }
            fn opening_options(
                view: &GameState,
                max_carry_capacity: i32,
                max_chop_power: i32,
            ) -> Vec<OpeningObjective> {
                let mut options = Vec::new();
                let max_carry_capacity = max_carry_capacity.clamp(1, 3);
                let max_chop_power = max_chop_power.clamp(1, 3);
                for movement_speed in 1..=3 {
                    for carry_capacity in 1..=max_carry_capacity {
                        for chop_power in 1..=max_chop_power {
                            let stats = Stats {
                                movement_speed,
                                carry_capacity,
                                harvest_power: 0,
                                chop_power,
                            };
                            options.push(Self::opening_objective(view, stats));
                        }
                    }
                }
                options
            }
            fn choose_second_troll(
                view: &GameState,
                policy: YamoOpeningPolicy
            ) -> OpeningObjective {
                let options =
                    Self::opening_options(view, policy.max_carry_capacity, policy.max_chop_power);
                let baseline = options
                    .iter()
                    .filter(|objective| objective.estimated_eta <= policy.train_horizon)
                    .max_by_key(|objective| Self::opening_key(objective, policy))
                    .copied()
                    .unwrap_or_else(|| {
                        Self::opening_objective(
                            view,
                            Stats {
                                movement_speed: 1,
                                carry_capacity: 1,
                                harvest_power: 0,
                                chop_power: 1,
                            },
                        )
                    });
                let preferred_min_carry = policy
                    .preferred_min_carry
                    .clamp(1, policy.max_carry_capacity.clamp(1, 3));
                let preferred_min_chop = policy
                    .preferred_min_chop
                    .clamp(1, policy.max_chop_power.clamp(1, 3));
                if policy.require_preferred {
                    let preferred = options.iter().filter(|objective| {
                        objective.stats.carry_capacity >= preferred_min_carry
                            && objective.stats.chop_power >= preferred_min_chop
                            && objective.estimated_eta < 10_000
                    });
                    return preferred
                        .clone()
                        .filter(|objective| objective.estimated_eta <= policy.train_horizon)
                        .max_by_key(|objective| Self::opening_key(objective, policy))
                        .or_else(|| {
                            preferred.max_by_key(|objective| {
                                (-objective.estimated_eta, objective.stats.movement_speed)
                            })
                        })
                        .copied()
                        .unwrap_or(baseline);
                }
                if policy.max_extra_eta <= 0
                    || (baseline.stats.carry_capacity >= preferred_min_carry
                        && baseline.stats.chop_power >= preferred_min_chop)
                {
                    return baseline;
                }
                let deadline_eta = policy.hard_train_turn.saturating_sub(view.turn).max(0);
                let allowed_eta = baseline
                    .estimated_eta
                    .saturating_add(policy.max_extra_eta)
                    .min(deadline_eta);
                options
                    .iter()
                    .filter(|objective| {
                        objective.stats.carry_capacity >= preferred_min_carry
                            && objective.stats.chop_power >= preferred_min_chop
                            && objective.estimated_eta <= allowed_eta
                    })
                    .max_by_key(|objective| Self::opening_key(objective, policy))
                    .copied()
                    .unwrap_or(baseline)
            }
            fn training_affordable(view: &GameState, stats: Stats) -> bool {
                let n = view.units.iter().filter(|unit| unit.player == 0).count() as i32;
                if n >= 2 {
                    return false;
                }
                let cost = training_cost(n, stats.tuple());
                view.inventories[0][PLUM] >= cost[PLUM]
                    && view.inventories[0][LEMON] >= cost[LEMON]
                    && view.inventories[0][APPLE] >= cost[APPLE]
                    && (view.iron.is_empty() || view.inventories[0][IRON] >= cost[IRON])
            }
            fn strongest_affordable(
                view: &GameState,
                policy: YamoOpeningPolicy,
            ) -> Option<OpeningObjective> {
                Self::opening_options(view, policy.max_carry_capacity, policy.max_chop_power)
                    .into_iter()
                    .filter(|objective| Self::training_affordable(view, objective.stats))
                    .map(|mut objective| {
                        objective.estimated_eta = 0;
                        objective
                    })
                    .max_by_key(|objective| Self::opening_key(objective, policy))
            }

            // --------------------------------------------------------------------------
            // Training deadline fallback — indexed block `training-deadline-fallback` [feature]
            //
            // If the second worker has not been trained by a deadline turn, abandons the preferred
            // build and trains the strongest currently affordable one instead.
            //
            // Coverage: guard runs 35,529 times; strongest_affordable / training_affordable /
            // fallback_second_troll all 0% covered
            // --------------------------------------------------------------------------
            fn enforce_training_deadline(&mut self, view: &GameState) {
                if self.opening_abandoned
                    || view.turn < self.opening_policy.hard_train_turn
                    || view.units.iter().filter(|unit| unit.player == 0).count() >= 2
                {
                    return;
                }
                let Some(objective) = self.desired_second else {
                    self.opening_abandoned = true;
                    return;
                };
                if Self::training_affordable(view, objective.stats) {
                    return;
                }
                if self.opening_policy.require_preferred {
                    let preferred_min_carry = self
                        .opening_policy
                        .preferred_min_carry
                        .clamp(1, self.opening_policy.max_carry_capacity.clamp(1, 3));
                    let preferred_min_chop = self
                        .opening_policy
                        .preferred_min_chop
                        .clamp(1, self.opening_policy.max_chop_power.clamp(1, 3));
                    if let Some(affordable) = Self::opening_options(
                        view,
                        self.opening_policy.max_carry_capacity,
                        self.opening_policy.max_chop_power,
                    )
                    .into_iter()
                    .filter(|candidate| {
                        candidate.stats.carry_capacity >= preferred_min_carry
                            && candidate.stats.chop_power >= preferred_min_chop
                            && Self::training_affordable(view, candidate.stats)
                    })
                    .max_by_key(|objective| Self::opening_key(objective, self.opening_policy))
                    {
                        self.desired_second = Some(affordable);
                    }
                    return;
                }
                self.desired_second = Self::strongest_affordable(view, self.opening_policy);
                if self.desired_second.is_none() {
                    self.opening_abandoned = true;
                }
            }
            // --------------------------------------------------------------------------
            // The opening dispatcher (stage 2A of `20260903-opening-solver`, 2026-09-03).
            //
            // From turn 1 until the third troll is trained the opening is played by the
            // offline solver's dispatcher in its deterministic form, recomputed every turn
            // from the live board (a taken tree or a planted cell repairs itself by
            // recomputation), in the order of weight the design round ruled:
            //   R1  turn 1 the starting troll steps off the shack and the shack trains the
            //       second troll from the draw when the draw affords a useful one (each
            //       talent the most its fruit affords, capped 2/2/2/1, and at least carry 2
            //       with harvest 1 -- the floor that reproduces the solver's buy-or-wait call
            //       on 332 of its 400 verified schedules); else the second troll (2/2/1/1,
            //       harvest 2 when the apples afford it) is funded from the first harvests,
            //       the strongest affordable carry-2 troll from turn 35, any harvester from 60;
            //   R2  a trip home carries a useful load: the task values trade the load's
            //       worth against the turns it costs, and a full troll banks;
            //   R3  the invariant: the bill is checked on the pre-turn stock, no PICK is
            //       issued on a turn the TRAIN fires, a seed never delays the second troll;
            //   R4  a seed goes next to water when the detour is short, else next door,
            //       and the picking troll plants it on its way;
            //   R5  everybody gathers, iron only against the bill's deficit, nobody idles.
            // The third troll's shape follows the iron (the orchard bots' rule: chop 3 with
            // iron within 5 steps of a door, 2 within 10, 1 within 16). Once three trolls
            // stand the champion's own play takes over, unchanged.
            // --------------------------------------------------------------------------
            const OPENING_HORIZON_LAST_TURN: i32 = 200;
            const OPENING_SECOND_DEADLINE: i32 = 35;
            const OPENING_SECOND_LAST_CALL: i32 = 60;
            const OPENING_SEED_TURN_LIMIT: i32 = 14;
            const OPENING_SEEDS: [PlantKind; 2] = [PlantKind::Lemon, PlantKind::Plum];
            const OPENING_WATER_DETOUR: i32 = 6;
            const OPENING_SURPLUS_WEIGHT: f64 = 0.25;
            const OPENING_WAIT_CD: i32 = 4;
            const OPENING_BOTTLENECK: f64 = 1.0;
            const OPENING_HOLD: f64 = 1.05;
            const OPENING_CAPS: (i32, i32, i32, i32) = (2, 2, 2, 1);
            const OPENING_SCORE: f64 = 100_000.0;
            const IRON_STEPS_FOR_CHOP: [(i32, i32); 3] = [(5, 3), (10, 2), (16, 1)];
            fn opening_doors(view: &GameState) -> Vec<Cell> {
                ortho_neighbors(view.shacks[0])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .collect()
            }
            fn opening_pay(view: &GameState) -> Vec<usize> {
                if view.iron.is_empty() {
                    vec![PLUM, LEMON, APPLE]
                } else {
                    vec![PLUM, LEMON, APPLE, IRON]
                }
            }
            fn opening_affordable(view: &GameState, n: i32, stats: Stats, inv: &[i32; 6]) -> bool {
                let cost = training_cost(n, stats.tuple());
                Self::opening_pay(view).into_iter().all(|item| inv[item] >= cost[item])
            }
            fn iron_steps(view: &GameState) -> Option<i32> {
                let from_doors = bfs_distances(&view.walkable, &Self::opening_doors(view));
                view.iron
                    .iter()
                    .flat_map(|iron| ortho_neighbors(*iron))
                    .filter_map(|cell| from_doors.get(&cell).copied())
                    .min()
            }
            fn third_troll_for(view: &GameState) -> Option<Stats> {
                let shape = |chop: i32| Stats {
                    movement_speed: 2,
                    carry_capacity: 3,
                    harvest_power: 0,
                    chop_power: chop,
                };
                if view.iron.is_empty() {
                    return Some(shape(3));
                }
                let steps = Self::iron_steps(view);
                let stock = view.inventories[0][IRON];
                for (limit, chop) in Self::IRON_STEPS_FOR_CHOP {
                    let needed = 2 + chop * chop - stock;
                    if needed <= 0 || steps.is_some_and(|s| s <= limit) {
                        return Some(shape(chop));
                    }
                }
                None
            }
            // The most of each talent the stock affords for a second troll, capped; None when
            // no troll at all is affordable (a talent below its floor).
            fn opening_second_permax(view: &GameState) -> Option<Stats> {
                let inv = &view.inventories[0];
                let best = |item: usize, cap: i32, floor: i32| -> i32 {
                    let mut v = floor - 1;
                    for t in floor..=cap {
                        if inv[item] >= 1 + t * t {
                            v = t;
                        }
                    }
                    v
                };
                let (ms_cap, cc_cap, hp_cap, chop_cap) = Self::OPENING_CAPS;
                let movement_speed = best(PLUM, ms_cap, 1);
                let carry_capacity = best(LEMON, cc_cap, 1);
                let harvest_power = best(APPLE, hp_cap, 0);
                let chop_power = if view.iron.is_empty() { chop_cap } else { best(IRON, chop_cap, 0) };
                if movement_speed < 1 || carry_capacity < 1 || harvest_power < 0 || chop_power < 0 {
                    return None;
                }
                // Harvest above carry is wasted: a troll takes at most what it can hold.
                let harvest_power = harvest_power.min(carry_capacity);
                Some(Stats {
                    movement_speed,
                    carry_capacity,
                    harvest_power,
                    chop_power,
                })
            }
            fn opening_second_target(view: &GameState) -> Stats {
                let permax = Self::opening_second_permax(view);
                if view.turn <= 1 {
                    if let Some(p) = permax {
                        if p.carry_capacity >= 2 && p.harvest_power >= 1 {
                            return p;
                        }
                    }
                }
                // Past the deadline the strongest affordable troll that still carries two;
                // past the last call, any troll that harvests (the champion never stays alone).
                if view.turn >= Self::OPENING_SECOND_DEADLINE {
                    if let Some(p) = permax {
                        if p.harvest_power >= 1
                            && (p.carry_capacity >= 2 || view.turn >= Self::OPENING_SECOND_LAST_CALL)
                        {
                            return p;
                        }
                    }
                }
                Stats {
                    movement_speed: 2,
                    carry_capacity: 2,
                    harvest_power: 1,
                    chop_power: 1,
                }
            }
            fn opening_fruits_at(plant: &Plant, cd_eff: i32, dt: i32) -> (i32, i32, i32) {
                let (mut size, mut fruits, mut cd) = (plant.size, plant.fruits, plant.cooldown.max(0));
                for _ in 0..dt {
                    if cd > 0 {
                        cd -= 1;
                    }
                    if cd == 0 {
                        if size < 4 {
                            size += 1;
                            cd = cd_eff;
                        } else if fruits < 3 {
                            fruits += 1;
                            cd = cd_eff;
                        }
                    }
                }
                (fruits, size, cd)
            }
            fn opening_near_water(view: &GameState, cell: Cell) -> bool {
                view.water.iter().any(|water| is_adjacent(*water, cell))
            }
            fn opening_ceil(a: i32, b: i32) -> i32 {
                (a + b.max(1) - 1) / b.max(1)
            }
            // The free reachable cell minimising distance-to-a-door plus distance-to-the-troll
            // (the top bots' rule), among cells next to water when asked; never a door.
            fn opening_plant_cell(
                view: &GameState,
                home: &BTreeMap<Cell, i32>,
                from_unit: &BTreeMap<Cell, i32>,
                doors: &[Cell],
                water: bool,
            ) -> Option<(i32, Cell)> {
                let mut best: Option<(i32, Cell)> = None;
                for (cell, d_home) in home {
                    if *d_home == 0 || doors.contains(cell) || view.plant_at(*cell).is_some() {
                        continue;
                    }
                    if water && !Self::opening_near_water(view, *cell) {
                        continue;
                    }
                    let Some(d_unit) = from_unit.get(cell) else {
                        continue;
                    };
                    let v = (*d_home + 1 + *d_unit, *cell);
                    if best.map_or(true, |b| v < b) {
                        best = Some(v);
                    }
                }
                best
            }
            // Turns per unit of `item` for the troll from the cheapest source now (walking
            // there and back from the nearest door, the taking, per unit carried); None: no
            // source. Measured from the doors, not from the troll, so the weights do not
            // change as it walks (a weight that moved with the troll made it dance).
            fn opening_fetch_cost(
                view: &GameState,
                unit: &Unit,
                item: usize,
                from_door: &BTreeMap<Cell, i32>,
                mine_cells: &[Cell],
            ) -> Option<f64> {
                let free = unit.free_capacity();
                if item == IRON {
                    let chop = unit.stats.chop_power;
                    if chop == 0 {
                        return None;
                    }
                    let d = mine_cells
                        .iter()
                        .filter_map(|c| from_door.get(c).copied())
                        .min()?;
                    let take = if free > 0 { free.min(chop) } else { 1 };
                    return Some((2 * d + Self::opening_ceil(take, chop) + 1) as f64 / take.max(1) as f64);
                }
                let mut best: Option<f64> = None;
                for plant in &view.plants {
                    if plant.kind.item_index() != item || plant.health <= 0 {
                        continue;
                    }
                    let Some(d) = from_door.get(&plant.cell) else {
                        continue;
                    };
                    let fr = if plant.fruits > 0 { plant.fruits } else if plant.size >= 4 { 1 } else { 0 };
                    if fr <= 0 {
                        continue;
                    }
                    let take = unit.stats.carry_capacity.max(1).min(fr);
                    let cost = (2 * d + Self::opening_ceil(take, unit.stats.harvest_power) + 1) as f64
                        / take as f64;
                    if best.map_or(true, |b| cost < b) {
                        best = Some(cost);
                    }
                }
                best
            }
            // --------------------------------------------------------------------------
            // Three-troll optimized start (owner, 2026-09-03).
            //
            // Unlike stage 2A, this does not optimise "third troll as early as possible".
            // It searches the small complete roster frontier, estimates the two workers'
            // contested resource assignments, charges those worker-turns against the wood
            // they could bank instead, and admits a third-troll plan only when the robust
            // estimate still pays. The estimate is re-rooted from the live board; a plan
            // that stops paying is abandoned and the champion resumes immediately.
            // --------------------------------------------------------------------------
            const OPENING_ENABLE_THIRD: bool = false;
            const OPENING_THIRD_LATEST: i32 = 110;
            const OPENING_THIRD_MIN_NET: f64 = 8.0;
            const OPENING_THIRD_RECHECK: i32 = 5;
            const OPENING_RESOURCE_INF: i32 = 20_000;

            fn opening_bank_eta(view: &GameState, unit: &Unit) -> i32 {
                if unit.total_carried() == 0 {
                    return 0;
                }
                let from = bfs_distances(&view.walkable, &[unit.cell]);
                Self::opening_doors(view)
                    .iter()
                    .filter_map(|door| from.get(door).copied())
                    .map(|distance| Self::opening_ceil(distance, unit.stats.movement_speed) + 1)
                    .min()
                    .unwrap_or(Self::OPENING_RESOURCE_INF)
            }

            // Cost in turns to bank `amount` units of one resource. The curve uses the
            // current board, includes full-load trips and regrowth, and treats fruit that
            // an opponent can reach no later than us as unavailable on the first visit.
            fn opening_resource_curve(
                view: &GameState,
                unit: &Unit,
                item: usize,
                contested: bool,
            ) -> [i32; 13] {
                let mut out = [Self::OPENING_RESOURCE_INF; 13];
                out[0] = 0;
                let capacity = unit.stats.carry_capacity.max(1);
                let movement = unit.stats.movement_speed.max(1);
                let doors = Self::opening_doors(view);
                if doors.is_empty() {
                    return out;
                }
                let from_unit = bfs_distances(&view.walkable, &[unit.cell]);
                let to_home = bfs_distances(&view.walkable, &doors);
                let starts_home = unit.total_carried() > 0;

                if item == IRON {
                    if view.iron.is_empty() || unit.stats.chop_power <= 0 {
                        return out;
                    }
                    let mut best: Option<(i32, i32)> = None;
                    for iron in &view.iron {
                        for cell in ortho_neighbors(*iron) {
                            if !view.walkable.contains(&cell) {
                                continue;
                            }
                            let Some(home_distance) = to_home.get(&cell).copied() else {
                                continue;
                            };
                            let first_distance = if starts_home {
                                home_distance
                            } else {
                                from_unit.get(&cell).copied().unwrap_or(Self::OPENING_RESOURCE_INF)
                            };
                            let first = Self::opening_ceil(first_distance, movement);
                            let home = Self::opening_ceil(home_distance, movement);
                            let key = (first + home, home);
                            if best.map_or(true, |old| key < old) {
                                best = Some(key);
                            }
                        }
                    }
                    let Some((first_plus_home, home)) = best else {
                        return out;
                    };
                    for amount in 1..=12i32 {
                        let trips = Self::opening_ceil(amount, capacity);
                        let mining = Self::opening_ceil(amount, unit.stats.chop_power);
                        out[amount as usize] = first_plus_home
                            + mining
                            + trips
                            + (trips - 1) * 2 * home;
                    }
                    return out;
                }

                let kind = match item {
                    PLUM => PlantKind::Plum,
                    LEMON => PlantKind::Lemon,
                    APPLE => PlantKind::Apple,
                    BANANA => PlantKind::Banana,
                    _ => return out,
                };
                if unit.stats.harvest_power <= 0 {
                    return out;
                }

                let mut any_source = false;
                for plant in &view.plants {
                    if plant.kind != kind || plant.health <= 0 {
                        continue;
                    }
                    let Some(from_distance) = from_unit.get(&plant.cell).copied() else {
                        continue;
                    };
                    let Some(home_distance) = to_home.get(&plant.cell).copied() else {
                        continue;
                    };
                    let arrive = Self::opening_ceil(from_distance, movement);
                    if MoisanBot::predict_tree(view, plant, arrive).is_none() {
                        continue;
                    }
                    any_source = true;
                    let home = Self::opening_ceil(home_distance, movement);
                    let first = if starts_home { home } else { arrive };
                    let mut cooldown = effective_cooldown(
                        plant.kind,
                        Self::opening_near_water(view, plant.cell),
                    )
                    .max(1);
                    let (mut safe_fruits, _, _) =
                        Self::opening_fruits_at(plant, cooldown, arrive);
                    let mut wait = (MoisanBot::ticks_until_fruit(view, plant) - arrive).max(0);

                    if contested {
                        // Manhattan distance is a lower bound on the opponent's real route. It
                        // therefore errs on the safe side: ambiguous first fruit is removed, and
                        // the following fruit is charged two cooldowns instead of one.
                        let opponent_eta = view
                            .units
                            .iter()
                            .filter(|opponent| {
                                opponent.player == 1 && opponent.stats.harvest_power > 0
                            })
                            .map(|opponent| {
                                Self::opening_ceil(
                                    manhattan(opponent.cell, plant.cell),
                                    opponent.stats.movement_speed,
                                )
                            })
                            .min();
                        if opponent_eta.is_some_and(|eta| eta <= arrive + 1) {
                            safe_fruits = 0;
                            wait = wait.max(cooldown);
                            cooldown = cooldown.saturating_mul(2);
                        }
                    }

                    let take_per_trip = capacity.min(3).max(1);
                    for amount in 1..=12i32 {
                        let trips = Self::opening_ceil(amount, take_per_trip);
                        let harvesting = Self::opening_ceil(amount, unit.stats.harvest_power);
                        let regrowth = (amount - safe_fruits.clamp(0, 3)).max(0) * cooldown;
                        let cost = first
                            + home
                            + wait
                            + harvesting
                            + trips
                            + (trips - 1) * 2 * home
                            + regrowth;
                        out[amount as usize] = out[amount as usize].min(cost);
                    }
                }

                if !any_source {
                    return out;
                }
                out
            }

            fn opening_cost_tables(
                view: &GameState,
                own: &[&Unit],
                contested: bool,
            ) -> [[[i32; 13]; 4]; 2] {
                let mut tables = [[[Self::OPENING_RESOURCE_INF; 13]; 4]; 2];
                let items = [PLUM, LEMON, APPLE, IRON];
                for worker in 0..2 {
                    for resource in 0..4 {
                        tables[worker][resource] = Self::opening_resource_curve(
                            view,
                            own[worker],
                            items[resource],
                            contested,
                        );
                    }
                }
                tables
            }

            // Exact enumeration of all splits of the four small training deficits between
            // two workers. This is the dynamic-programming core: equal deficit vectors keep
            // only the earliest pair of worker completion times.
            fn opening_assignment(
                deficits: [i32; 4],
                tables: &[[[i32; 13]; 4]; 2],
                base: [i32; 2],
            ) -> Option<([i32; 2], i32)> {
                if deficits.iter().any(|value| *value < 0 || *value > 12) {
                    return None;
                }
                let mut best: Option<((i32, i32, i32, i32), [i32; 2])> = None;
                for plum0 in 0..=deficits[0] {
                    for lemon0 in 0..=deficits[1] {
                        for apple0 in 0..=deficits[2] {
                            for iron0 in 0..=deficits[3] {
                                let assigned0 = [plum0, lemon0, apple0, iron0];
                                let mut turns = base;
                                let mut feasible = true;
                                for resource in 0..4 {
                                    let amount0 = assigned0[resource] as usize;
                                    let amount1 = (deficits[resource] - assigned0[resource]) as usize;
                                    let cost0 = tables[0][resource][amount0];
                                    let cost1 = tables[1][resource][amount1];
                                    if cost0 >= Self::OPENING_RESOURCE_INF
                                        || cost1 >= Self::OPENING_RESOURCE_INF
                                    {
                                        feasible = false;
                                        break;
                                    }
                                    turns[0] += cost0;
                                    turns[1] += cost1;
                                }
                                if !feasible {
                                    continue;
                                }
                                let key = (
                                    turns[0].max(turns[1]),
                                    turns[0] + turns[1],
                                    turns[0],
                                    turns[1],
                                );
                                if best.as_ref().map_or(true, |(old, _)| key < *old) {
                                    best = Some((key, turns));
                                }
                            }
                        }
                    }
                }
                best.map(|(key, turns)| (turns, key.0))
            }

            fn opening_wood_rate(view: &GameState, unit: &Unit) -> f64 {
                if unit.stats.chop_power <= 0 {
                    return 0.0;
                }
                let mut probe = unit.clone();
                probe.carry = [0; 6];
                MoisanBot::chop_candidates(view, &probe, None)
                    .iter()
                    .map(|candidate| candidate.score * 0.004)
                    .fold(0.0f64, f64::max)
                    .max(0.12 * unit.stats.chop_power as f64)
            }

            fn opening_third_wood_rate(view: &GameState, stats: Stats) -> f64 {
                let mut best = 0.0f64;
                for cell in Self::opening_doors(view) {
                    let probe = Unit {
                        id: -1,
                        player: 0,
                        cell,
                        stats,
                        carry: [0; 6],
                    };
                    best = best.max(
                        MoisanBot::chop_candidates(view, &probe, None)
                            .iter()
                            .map(|candidate| candidate.score * 0.004)
                            .fold(0.0f64, f64::max),
                    );
                }
                best
            }

            fn opening_standing_wood_points(view: &GameState) -> f64 {
                4.0 * view
                    .plants
                    .iter()
                    .filter(|plant| plant.health > 0)
                    .map(|plant| plant.size.clamp(0, 4) as f64)
                    .sum::<f64>()
            }

            fn opening_evaluate_third(
                view: &GameState,
                own: &[&Unit],
                target: Stats,
                idle: &[[[i32; 13]; 4]; 2],
                contested: &[[[i32; 13]; 4]; 2],
                wood_rates: [f64; 2],
            ) -> Option<(i32, [f64; 6], f64)> {
                let bill = training_cost(2, target.tuple());
                let mut have = view.inventories[0];
                for unit in own {
                    for item in 0..6 {
                        have[item] += unit.carry[item];
                    }
                }
                let mut deficits = [0i32; 4];
                let items = [PLUM, LEMON, APPLE, IRON];
                for resource in 0..4 {
                    let item = items[resource];
                    deficits[resource] = if item == IRON && view.iron.is_empty() {
                        0
                    } else {
                        (bill[item] - have[item]).max(0)
                    };
                }
                let base = [
                    Self::opening_bank_eta(view, own[0]),
                    Self::opening_bank_eta(view, own[1]),
                ];
                let (_, idle_makespan) = Self::opening_assignment(deficits, idle, base)?;
                let (worker_turns, contested_makespan) =
                    Self::opening_assignment(deficits, contested, base)?;
                let finish = view.turn + contested_makespan + 1;
                if finish > Self::OPENING_THIRD_LATEST {
                    return None;
                }

                let third_rate = Self::opening_third_wood_rate(view, target);
                if third_rate <= 0.0 {
                    return None;
                }
                // The old opening extrapolated an idle-board production rate for the rest
                // of the game. Cap the estimate by the wood visible now and by the measured
                // scale on which a third lumberjack has previously paid back. This is a
                // deliberate anti-fantasy bound, not a proof of game value.
                let time_value = (TOTAL_TURNS - finish).max(0) as f64 * third_rate * 0.45;
                let supply_value =
                    (Self::opening_standing_wood_points(view) * 0.30 + 12.0).min(44.0);
                let future = time_value.min(supply_value);
                let funding_cost = worker_turns[0] as f64 * wood_rates[0]
                    + worker_turns[1] as f64 * wood_rates[1];
                let fruit_face = (deficits[0] + deficits[1] + deficits[2]) as f64;
                let contest_delay = (contested_makespan - idle_makespan).max(0) as f64;
                let net = future
                    - funding_cost
                    - fruit_face
                    - contest_delay * third_rate * 0.50;
                if net < Self::OPENING_THIRD_MIN_NET {
                    return None;
                }

                let total = deficits.iter().sum::<i32>().max(1) as f64;
                let shared_value = (future / total).clamp(1.0, 28.0);
                let mut shadows = [1.0f64; 6];
                shadows[5] = 4.0;
                for resource in 0..4 {
                    if deficits[resource] == 0 {
                        continue;
                    }
                    let item = items[resource];
                    let amount = deficits[resource] as usize;
                    let mut opportunity = f64::INFINITY;
                    for worker in 0..2 {
                        let curve = contested[worker][resource][amount];
                        if curve < Self::OPENING_RESOURCE_INF {
                            opportunity = opportunity.min(
                                curve as f64 / deficits[resource] as f64
                                    * wood_rates[worker],
                            );
                        }
                    }
                    if !opportunity.is_finite() {
                        return None;
                    }
                    shadows[item] = shared_value.max(opportunity * 1.08 + 0.5).clamp(1.0, 40.0);
                }
                Some((finish, shadows, net))
            }

            fn opening_score_third(
                view: &GameState,
                own: &[&Unit],
                target: Stats,
            ) -> Option<(i32, [f64; 6], f64)> {
                if own.len() != 2 {
                    return None;
                }
                let idle = Self::opening_cost_tables(view, own, false);
                let contested = Self::opening_cost_tables(view, own, true);
                let wood_rates = [
                    Self::opening_wood_rate(view, own[0]),
                    Self::opening_wood_rate(view, own[1]),
                ];
                Self::opening_evaluate_third(
                    view,
                    own,
                    target,
                    &idle,
                    &contested,
                    wood_rates,
                )
            }

            fn opening_optimize_third(
                view: &GameState,
                own: &[&Unit],
            ) -> Option<(Stats, i32, [f64; 6], f64)> {
                if !Self::OPENING_ENABLE_THIRD || own.len() != 2 {
                    return None;
                }
                let idle = Self::opening_cost_tables(view, own, false);
                let contested = Self::opening_cost_tables(view, own, true);
                let wood_rates = [
                    Self::opening_wood_rate(view, own[0]),
                    Self::opening_wood_rate(view, own[1]),
                ];
                let specs = [
                    Stats {
                        movement_speed: 1,
                        carry_capacity: 1,
                        harvest_power: 0,
                        chop_power: 1,
                    },
                    Stats {
                        movement_speed: 1,
                        carry_capacity: 2,
                        harvest_power: 0,
                        chop_power: 1,
                    },
                    Stats {
                        movement_speed: 2,
                        carry_capacity: 2,
                        harvest_power: 0,
                        chop_power: 1,
                    },
                    Stats {
                        movement_speed: 2,
                        carry_capacity: 2,
                        harvest_power: 0,
                        chop_power: 2,
                    },
                    Stats {
                        movement_speed: 2,
                        carry_capacity: 3,
                        harvest_power: 0,
                        chop_power: 1,
                    },
                    Stats {
                        movement_speed: 2,
                        carry_capacity: 3,
                        harvest_power: 0,
                        chop_power: 2,
                    },
                    Stats {
                        movement_speed: 2,
                        carry_capacity: 3,
                        harvest_power: 0,
                        chop_power: 3,
                    },
                ];
                let mut best: Option<(Stats, i32, [f64; 6], f64)> = None;
                for target in specs {
                    let Some((finish, shadows, net)) = Self::opening_evaluate_third(
                        view,
                        own,
                        target,
                        &idle,
                        &contested,
                        wood_rates,
                    ) else {
                        continue;
                    };
                    let replace = best.as_ref().map_or(true, |(old, old_finish, _, old_net)| {
                        net > *old_net + 1e-9
                            || ((net - *old_net).abs() <= 1e-9
                                && (finish < *old_finish
                                    || (finish == *old_finish
                                        && target.chop_power > old.chop_power)))
                    });
                    if replace {
                        best = Some((target, finish, shadows, net));
                    }
                }
                best.map(|(target, finish, shadows, net)| {
                    (
                        target,
                        (finish + 8).min(Self::OPENING_THIRD_LATEST),
                        shadows,
                        net,
                    )
                })
            }

            // One turn of the opening: the TRAIN (if the pre-turn stock clears the bill) and
            // one command per own troll; None once the opening is over (the champion plays).
            fn opening_dispatch(&mut self, view: &GameState) -> Option<(Option<Stats>, BTreeMap<i32, Candidate>)> {
                struct Task {
                    value: f64,
                    command: String,
                    target: Cell,
                    claim: Option<(usize, i32)>,
                    claim_cell: Option<(Cell, i32)>,
                    seed: Option<(PlantKind, Cell)>,
                    // A task that fetches something the bill still needs (or banks, or plants).
                    needed: bool,
                }
                if self.opening_done {
                    return None;
                }
                let mut own: Vec<&Unit> = view.units.iter().filter(|unit| unit.player == 0).collect();
                own.sort_by_key(|unit| unit.id);
                let n = own.len() as i32;
                let shack = view.shacks[0];
                let doors = Self::opening_doors(view);
                if n == 0 || n >= 3 || doors.is_empty() || (n == 2 && view.turn > Self::OPENING_HORIZON_LAST_TURN) {
                    self.opening_done = true;
                    return None;
                }
                let target = if n == 1 {
                    Some(Self::opening_second_target(view))
                } else {
                    if !Self::OPENING_ENABLE_THIRD {
                        self.opening_done = true;
                        return None;
                    }
                    if self.opening_third.is_none() {
                        let Some((stats, deadline, shadows, net)) =
                            Self::opening_optimize_third(view, &own)
                        else {
                            self.opening_done = true;
                            return None;
                        };
                        self.opening_third = Some(stats);
                        self.opening_third_deadline = deadline;
                        self.opening_third_shadow = shadows;
                        self.opening_third_net = net;
                        self.opening_third_recheck = view.turn + Self::OPENING_THIRD_RECHECK;
                    } else if view.turn >= self.opening_third_recheck {
                        let stats = self.opening_third.unwrap();
                        let Some((finish, shadows, net)) =
                            Self::opening_score_third(view, &own, stats)
                        else {
                            self.opening_done = true;
                            return None;
                        };
                        self.opening_third_deadline =
                            (finish + 8).min(Self::OPENING_THIRD_LATEST);
                        self.opening_third_shadow = shadows;
                        self.opening_third_net = net;
                        self.opening_third_recheck = view.turn + Self::OPENING_THIRD_RECHECK;
                    }
                    if view.turn > self.opening_third_deadline {
                        self.opening_done = true;
                        return None;
                    }
                    self.opening_third
                };
                let Some(target) = target else {
                    self.opening_done = true;
                    return None;
                };
                let bill = training_cost(n, target.tuple());
                let pay = Self::opening_pay(view);
                let inv = view.inventories[0];
                // R3: the TRAIN on the pre-turn stock; a delayed second troll takes harvest 2
                // when the apples afford it.
                let mut train: Option<Stats> = None;
                if Self::opening_affordable(view, n, target, &inv) {
                    let mut chosen = target;
                    if n == 1 && view.turn > 1 && chosen.harvest_power == 1 {
                        let up = Stats {
                            harvest_power: 2,
                            ..chosen
                        };
                        if Self::opening_affordable(view, n, up, &inv) {
                            chosen = up;
                        }
                    }
                    train = Some(chosen);
                }
                let home = bfs_distances(&view.walkable, &doors);
                let from_doors: Vec<(Cell, BTreeMap<Cell, i32>)> = doors
                    .iter()
                    .map(|door| (*door, bfs_distances(&view.walkable, &[*door])))
                    .collect();
                let mut mine_cells: Vec<Cell> = view
                    .iron
                    .iter()
                    .flat_map(|iron| ortho_neighbors(*iron))
                    .filter(|cell| home.contains_key(cell))
                    .collect();
                mine_cells.sort();
                mine_cells.dedup();
                let sw = if n == 2 { 1.0 } else { Self::OPENING_SURPLUS_WEIGHT };
                // The stock, every troll's load and this turn's claims count toward the bill.
                let mut have = inv;
                for unit in &own {
                    for item in 0..6 {
                        have[item] += unit.carry[item];
                    }
                }
                let mut claims_by_cell: BTreeMap<Cell, i32> = BTreeMap::new();
                let mut commands: BTreeMap<i32, Candidate> = BTreeMap::new();
                let mut targets_now: BTreeMap<i32, Cell> = BTreeMap::new();
                let mut seeds_now = self.opening_seed_count;
                for unit in &own {
                    let from_unit = bfs_distances(&view.walkable, &[unit.cell]);
                    let on_shack = unit.cell == shack;
                    let at_door = !on_shack && is_adjacent(unit.cell, shack);
                    let free = unit.free_capacity();
                    let carrying = unit.total_carried();
                    let ms = unit.stats.movement_speed.max(1);
                    let hp = unit.stats.harvest_power;
                    let mut need = [0i32; 6];
                    for item in pay.iter().copied() {
                        need[item] = (bill[item] - have[item]).max(0);
                    }
                    let needed_any = need.iter().any(|d| *d > 0);
                    // A seed in hand is planted where it was meant to go, or where a free cell
                    // now is; a seed no longer carried is forgotten.
                    let mut task: Option<Task> = None;
                    if let Some((kind, cell)) = self.opening_seeds.get(&unit.id).copied() {
                        if unit.carry[kind.item_index()] > 0 {
                            let cell = if view.plant_at(cell).is_none() && home.contains_key(&cell) {
                                Some(cell)
                            } else {
                                let wet = Self::opening_plant_cell(view, &home, &from_unit, &doors, true);
                                let dry = Self::opening_plant_cell(view, &home, &from_unit, &doors, false);
                                match (wet, dry) {
                                    (Some(w), Some(d)) if w.0 <= d.0 + Self::OPENING_WATER_DETOUR => Some(w.1),
                                    (_, Some(d)) => Some(d.1),
                                    (Some(w), None) => Some(w.1),
                                    (None, None) => None,
                                }
                            };
                            if let Some(cell) = cell {
                                self.opening_seeds.insert(unit.id, (kind, cell));
                                let command = if unit.cell == cell {
                                    format!("PLANT {} {}", unit.id, kind.as_str())
                                } else {
                                    format!("MOVE {} {} {}", unit.id, cell.0, cell.1)
                                };
                                task = Some(Task {
                                    value: 0.0,
                                    command,
                                    target: cell,
                                    claim: None,
                                    claim_cell: None,
                                    seed: None,
                                    needed: true,
                                });
                            } else {
                                self.opening_seeds.remove(&unit.id);
                            }
                        } else {
                            self.opening_seeds.remove(&unit.id);
                        }
                    }
                    if task.is_none() {
                        // The door to bank at: the walk to it plus the walk from it to the next
                        // job (the closest tree with fruit the bill needs, or the mine).
                        let mut job_cells: Vec<Cell> = view
                            .plants
                            .iter()
                            .filter(|plant| {
                                plant.health > 0
                                    && home.contains_key(&plant.cell)
                                    && (plant.fruits > 0 || plant.size >= 4)
                                    && need[plant.kind.item_index()] > 0
                            })
                            .map(|plant| plant.cell)
                            .collect();
                        if need[IRON] > 0 {
                            job_cells.extend(mine_cells.iter().take(2).copied());
                        }
                        let door = from_doors
                            .iter()
                            .map(|(door, map)| {
                                let d0 = if on_shack { 1 } else { from_unit.get(door).copied().unwrap_or(9_999) };
                                let d1 = job_cells
                                    .iter()
                                    .map(|cell| map.get(cell).copied().unwrap_or(9_999))
                                    .min()
                                    .unwrap_or(0);
                                ((d0 + d1, d0, *door), *door)
                            })
                            .min_by_key(|(key, _)| *key)
                            .map(|(_, door)| door)
                            .unwrap();
                        let d_home = if on_shack { 1 } else { from_unit.get(&door).copied().unwrap_or(9_999) };
                        // The bottleneck first: a needed unit's weight is its fetch cost
                        // relative to the mean over the items still needed.
                        let mut w = [1.0f64; 6];
                        if needed_any && Self::OPENING_BOTTLENECK > 0.0 {
                            let mut costs: Vec<(usize, f64)> = Vec::new();
                            for item in 0..6 {
                                if need[item] > 0 {
                                    let c = Self::opening_fetch_cost(view, unit, item, &home, &mine_cells)
                                        .unwrap_or(40.0);
                                    costs.push((item, c));
                                }
                            }
                            if !costs.is_empty() {
                                let mean = costs.iter().map(|(_, c)| *c).sum::<f64>() / costs.len() as f64;
                                for (item, c) in costs {
                                    w[item] = (1.0 + Self::OPENING_BOTTLENECK * (c / mean - 1.0)).clamp(0.3, 4.0);
                                }
                            }
                        }
                        if n == 2 {
                            for item in pay.iter().copied() {
                                if need[item] > 0 {
                                    w[item] = self.opening_third_shadow[item].max(1.0);
                                }
                            }
                        }
                        let mut tasks: Vec<Task> = Vec::new();
                        if carrying > 0 {
                            let mut carried_value = 0.0;
                            for item in 0..6 {
                                let needed = if needed_any {
                                    unit.carry[item].min(need[item])
                                } else {
                                    0
                                };
                                carried_value += needed as f64 * w[item];
                                let surplus = unit.carry[item] - needed;
                                carried_value += surplus as f64
                                    * if n == 2 {
                                        if item == 5 { 4.0 } else { 1.0 }
                                    } else {
                                        sw
                                    };
                            }
                            let value = carried_value / (d_home + 1) as f64
                                + if free == 0 { 2.0 } else { 0.0 };
                            let command = if at_door {
                                format!("DROP {}", unit.id)
                            } else {
                                format!("MOVE {} {} {}", unit.id, door.0, door.1)
                            };
                            tasks.push(Task {
                                value,
                                command,
                                target: door,
                                claim: None,
                                claim_cell: None,
                                seed: None,
                                needed: true,
                            });
                        }
                        if free > 0 {
                            for plant in &view.plants {
                                if plant.health <= 0 || hp <= 0 {
                                    continue;
                                }
                                let Some(d) = from_unit.get(&plant.cell).copied() else {
                                    continue;
                                };
                                let arrive = Self::opening_ceil(d, ms);
                                let cd_eff = effective_cooldown(plant.kind, Self::opening_near_water(view, plant.cell));
                                let (fr, size, cd) = Self::opening_fruits_at(plant, cd_eff, arrive);
                                let claimed = claims_by_cell.get(&plant.cell).copied().unwrap_or(0);
                                let k = plant.kind.item_index();
                                let worth_each = if need[k] > 0 { w[k] } else { sw };
                                let back = home.get(&plant.cell).copied().unwrap_or(9_999) as f64 / ms as f64 + 1.0;
                                let worth_of = |take: i32| -> f64 {
                                    if needed_any {
                                        take.min(need[k]) as f64 * w[k] + (take - need[k]).max(0) as f64 * sw
                                    } else {
                                        take as f64
                                    }
                                };
                                let harvest = |take: i32| -> String {
                                    if unit.cell == plant.cell {
                                        let _ = take;
                                        format!("HARVEST {}", unit.id)
                                    } else {
                                        format!("MOVE {} {} {}", unit.id, plant.cell.0, plant.cell.1)
                                    }
                                };
                                let avail = (fr - claimed).max(0);
                                if avail > 0 {
                                    let take = free.min(avail + if fr >= 3 && cd == 0 { 1 } else { 0 });
                                    let turns = (arrive + Self::opening_ceil(take, hp)) as f64 + back;
                                    tasks.push(Task {
                                        value: worth_of(take) / turns,
                                        command: harvest(take),
                                        target: plant.cell,
                                        claim: Some((k, take)),
                                        claim_cell: Some((plant.cell, take)),
                                        seed: None,
                                        needed: need[k] > 0,
                                    });
                                }
                                if size >= 4 && cd_eff <= Self::OPENING_WAIT_CD && free > avail && claimed == 0 {
                                    let take = free;
                                    let extra = take - avail;
                                    let turns = (arrive + Self::opening_ceil(avail, hp).max(1) + extra * cd_eff) as f64 + back;
                                    let command = if unit.cell == plant.cell && plant.fruits == 0 {
                                        "WAIT".to_string()
                                    } else {
                                        harvest(take)
                                    };
                                    tasks.push(Task {
                                        value: worth_of(take) / turns * 0.98,
                                        command,
                                        target: plant.cell,
                                        claim: Some((k, take)),
                                        claim_cell: Some((plant.cell, take)),
                                        seed: None,
                                        needed: need[k] > 0,
                                    });
                                }
                                if arrive < 20 && fr == 0 && size >= 4 && cd > 0 && cd + arrive <= 12 && need[k] > 0 && claimed == 0 {
                                    let take = free.min(1);
                                    let turns = (arrive + (cd - arrive).max(0) + 1) as f64 + back;
                                    let command = if unit.cell == plant.cell {
                                        "WAIT".to_string()
                                    } else {
                                        harvest(take)
                                    };
                                    tasks.push(Task {
                                        value: worth_each / turns * 0.9,
                                        command,
                                        target: plant.cell,
                                        claim: Some((k, take)),
                                        claim_cell: Some((plant.cell, take)),
                                        seed: None,
                                        needed: true,
                                    });
                                }
                            }
                            if !view.iron.is_empty() && unit.stats.chop_power > 0 && need[IRON] > 0 {
                                if let Some(cell) = mine_cells
                                    .iter()
                                    .min_by_key(|c| (from_unit.get(c).copied().unwrap_or(9_999), **c))
                                    .copied()
                                {
                                    let d = from_unit.get(&cell).copied().unwrap_or(9_999);
                                    let arrive = Self::opening_ceil(d, ms);
                                    let take = free.min(need[IRON].max(1));
                                    let turns = (arrive + Self::opening_ceil(take, unit.stats.chop_power)) as f64
                                        + home.get(&cell).copied().unwrap_or(9_999) as f64 / ms as f64
                                        + 1.0;
                                    let command = if unit.cell == cell {
                                        format!("MINE {}", unit.id)
                                    } else {
                                        format!("MOVE {} {} {}", unit.id, cell.0, cell.1)
                                    };
                                    tasks.push(Task {
                                        value: take.min(need[IRON]) as f64 * w[IRON] / turns,
                                        command,
                                        target: cell,
                                        claim: Some((IRON, take)),
                                        claim_cell: None,
                                        seed: None,
                                        needed: true,
                                    });
                                }
                            }
                            // Stage 2A suppressed the wood race until the third troll. Here
                            // ordinary 4-point wood trips compete directly with the dynamic
                            // program's shadow-priced training resources. A needed fruit tree
                            // is discounted, not made immortal: if its wood is still the better
                            // use, the live recheck may abandon the third-troll plan.
                            if n == 2 {
                                for candidate in MoisanBot::chop_candidates(view, unit, None) {
                                    let target = match candidate.target {
                                        Target::Tree(cell) | Target::Cell(cell) | Target::Bank(cell) => cell,
                                        _ => continue,
                                    };
                                    let protected = view
                                        .plant_at(target)
                                        .map(|index| need[view.plants[index].kind.item_index()] > 0)
                                        .unwrap_or(false);
                                    tasks.push(Task {
                                        value: candidate.score * 0.004
                                            * if protected { 0.35 } else { 1.0 },
                                        command: candidate.command,
                                        target,
                                        claim: None,
                                        claim_cell: None,
                                        seed: None,
                                        needed: false,
                                    });
                                }
                            }
                            // A seed: only from stock the second troll's bill does not need,
                            // never on a turn the TRAIN fires (R3), early in the game, with
                            // empty hands; next to water when the detour is short (R4).
                            if seeds_now < Self::OPENING_SEEDS.len()
                                && n <= 1
                                && view.turn <= Self::OPENING_SEED_TURN_LIMIT
                                && carrying == 0
                                && train.is_none()
                            {
                                let kind = Self::OPENING_SEEDS[seeds_now];
                                let k = kind.item_index();
                                let reserve = if n <= 1 { bill[k] } else { 0 };
                                if inv[k] - reserve > 0 {
                                    let wet = Self::opening_plant_cell(view, &home, &from_unit, &doors, true);
                                    let dry = Self::opening_plant_cell(view, &home, &from_unit, &doors, false);
                                    let cell = match (wet, dry) {
                                        (Some(w), Some(d)) if w.0 <= d.0 + Self::OPENING_WATER_DETOUR => Some(w.1),
                                        (_, Some(d)) => Some(d.1),
                                        (Some(w), None) => Some(w.1),
                                        (None, None) => None,
                                    };
                                    if let Some(cell) = cell {
                                        let turns = d_home + 1 + home.get(&cell).copied().unwrap_or(9_999) + 1;
                                        let command = if at_door {
                                            format!("PICK {} {}", unit.id, kind.as_str())
                                        } else {
                                            format!("MOVE {} {} {}", unit.id, door.0, door.1)
                                        };
                                        tasks.push(Task {
                                            value: 3.0 / turns as f64,
                                            command,
                                            target: cell,
                                            claim: None,
                                            claim_cell: None,
                                            seed: Some((kind, cell)),
                                            needed: true,
                                        });
                                    }
                                }
                            }
                        }
                        // The bill first (R5): while anything the bill needs can be fetched, a
                        // harvest for points alone is not an option (a near tree's quarter-points
                        // every other turn once outscored the only plum tree on the map, 16 steps
                        // away, and the third troll never came). Then the best value wins, the
                        // first on a tie; last turn's target holds a little, so a close call
                        // does not flip a troll every turn.
                        if n <= 1 && tasks.iter().any(|t| t.needed && t.claim.is_some()) {
                            tasks.retain(|t| t.needed);
                        }
                        let last = self.opening_targets.get(&unit.id).copied();
                        let mut best: Option<Task> = None;
                        for t in tasks {
                            let value = if last == Some(t.target) { t.value * Self::OPENING_HOLD } else { t.value };
                            if best.as_ref().map_or(true, |b| value > b.value) {
                                best = Some(Task { value, ..t });
                            }
                        }
                        task = best;
                    }
                    let (command, target) = match task {
                        Some(t) => {
                            if let Some((item, amount)) = t.claim {
                                have[item] += amount;
                            }
                            if let Some((cell, amount)) = t.claim_cell {
                                *claims_by_cell.entry(cell).or_insert(0) += amount;
                            }
                            if let Some(seed) = t.seed {
                                if t.command.starts_with("PICK ") {
                                    self.opening_seeds.insert(unit.id, seed);
                                    self.opening_seed_count += 1;
                                }
                                seeds_now += 1;
                            }
                            (t.command, Some(t.target))
                        }
                        None => ("WAIT".to_string(), None),
                    };
                    // A troll on the shack always steps off it (it can do nothing there and it
                    // blocks the TRAIN).
                    let command = if on_shack && !command.starts_with("MOVE ") {
                        format!("MOVE {} {} {}", unit.id, doors[0].0, doors[0].1)
                    } else {
                        command
                    };
                    if let Some(cell) = target {
                        targets_now.insert(unit.id, cell);
                    }
                    commands.insert(
                        unit.id,
                        Candidate {
                            command,
                            score: Self::OPENING_SCORE,
                            target: Target::None,
                        },
                    );
                }
                self.opening_targets = targets_now;
                Some((train, commands))
            }
            fn fallback_second_troll() -> Stats {
                Stats {
                    movement_speed: 1,
                    carry_capacity: 1,
                    harvest_power: 0,
                    chop_power: 1,
                }
            }
            fn bank_candidates(view: &GameState, unit: &Unit) -> Vec<Candidate> {
                MoisanBot::bank_candidates(view, unit)
                    .into_iter()
                    .filter(|candidate| match candidate.target {
                        Target::Bank(cell) if cell != unit.cell => 
                            !view.units.iter().any(|other| {
                                other.player == unit.player
                                    && other.id != unit.id
                                    && other.cell == cell
                            })
                        ,
                        _ => true,
                    })
                    .collect()
            }
            fn unique_shack_door(view: &GameState) -> Option<Cell> {
                let doors: Vec<Cell> = ortho_neighbors(view.shacks[0])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .collect();
                (doors.len() == 1).then_some(doors[0])
            }
            fn forced_move(unit: &Unit, cell: Cell) -> Candidate {
                Candidate {
                    command: format!("MOVE {} {} {}", unit.id, cell.0, cell.1),
                    score: 20_000.0,
                    target: Target::Cell(cell),
                }
            }
            fn carries_committed_fruit(&self, unit: &Unit) -> bool {
                self.regeneration_commitments
                    .get(&unit.id)
                    .is_some_and(|kind| unit.carry[kind.item_index()] > 0)
            }
            fn planned_egress(
                view: &GameState,
                unit: &Unit,
                options: &[Candidate],
                forbidden: &BTreeSet<Cell>,
            ) -> Option<(Cell, Target)> {
                let candidate = options.iter().max_by(|a, b| a.score.total_cmp(&b.score))?;
                let (_, target) = MoisanBot::move_command(&candidate.command)?;
                let landing =
                    next_cell(&view.walkable, unit.cell, target, unit.stats.movement_speed);
                let occupied = view.units.iter().any(|other| {
                    other.player == unit.player && other.id != unit.id && other.cell == landing
                });
                (landing != unit.cell && !forbidden.contains(&landing) && !occupied)
                    .then_some((landing, candidate.target))
            }

            // --------------------------------------------------------------------------
            // Shack door unblocking — indexed block `door-unblocking` [feature]
            //
            // When the home shack has exactly one walkable doorway, detects a worker blocking it and
            // issues forced moves to clear the way for a carrier heading to the bank.
            //
            // Costs 5,991 bytes of source (9.537% of the live program).
            // Coverage: entered 7,234 times (every turn); 1.17% of regions; action paths
            // planned_egress/forced_move/carries_committed_fruit have ZERO entries
            // Measured live value: unmeasured; disabling changed 0 of 7,234 commands on the frozen
            // packet
            // --------------------------------------------------------------------------
            fn force_unique_door_clear(
                &self,
                view: &GameState,
                candidates: &mut BTreeMap<i32, Vec<Candidate>>,
            ) {
                let Some(door) = Self::unique_shack_door(view) else {
                    return;
                };
                let blocker_at_door = view
                    .units
                    .iter()
                    .find(|unit| unit.player == 0 && unit.cell == door);
                if let (Some(blocker), Some(transit)) = (
                    blocker_at_door,
                    view.units
                        .iter()
                        .filter(|unit| unit.player == 0 && unit.cell == view.shacks[0])
                        .min_by_key(|unit| unit.id),
                ) {
                    if blocker.total_carried() > 0 && !self.carries_committed_fruit(blocker) {
                        candidates.insert(
                            blocker.id,
                            vec![Candidate {
                                command: format!("DROP {}", blocker.id),
                                score: 20_000.0,
                                target: Target::Cell(door),
                            }],
                        );
                        candidates.insert(transit.id, vec![MoisanBot::wait()]);
                        return;
                    }
                    let forbidden = BTreeSet::from([door, view.shacks[0]]);
                    if let Some((landing, _)) = candidates.get(&blocker.id).and_then(|options| 
                        Self::planned_egress(view, blocker, options, &forbidden)
                    ) {
                        candidates.insert(blocker.id, vec![Self::forced_move(blocker, landing)]);
                        candidates.insert(transit.id, vec![Self::forced_move(transit, door)]);
                        return;
                    }
                    let occupied: BTreeSet<Cell> = view
                        .units
                        .iter()
                        .filter(|unit| unit.player == 0 && unit.id != blocker.id)
                        .map(|unit| unit.cell)
                        .collect();
                    if let Some(egress) = ortho_neighbors(door)
                        .into_iter()
                        .filter(|cell| view.walkable.contains(cell) && !occupied.contains(cell))
                        .min()
                    {
                        candidates.insert(blocker.id, vec![Self::forced_move(blocker, egress)]);
                        candidates.insert(transit.id, vec![Self::forced_move(transit, door)]);
                    }
                    return;
                }
                let from_door = bfs_distances(&view.walkable, &[door]);
                let Some(carrier) = view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 0 && unit.cell != door)
                    .filter(|unit| unit.total_carried() > 0)
                    .filter(|unit| {
                        if unit.free_capacity() <= 0 {
                            return true;
                        }
                        self.partial_bank_transit
                            && candidates.get(&unit.id).is_some_and(|options| {
                                let has_bank_route = options.iter().any(|candidate| {
                                    candidate.target == Target::Bank(door)
                                        || candidate.target == Target::Cell(door)
                                        || candidate.target == Target::Shack
                                });
                                let is_idle = !options.is_empty()
                                    && options
                                        .iter()
                                        .all(|candidate| candidate.target == Target::None);
                                has_bank_route || is_idle
                            })
                    })
                    .filter(|unit| !self.carries_committed_fruit(unit))
                    .filter(|unit| from_door.contains_key(&unit.cell))
                    .min_by_key(|unit| {
                        (
                            unit.free_capacity() > 0,
                            from_door[&unit.cell],
                            -unit.total_carried(),
                            unit.id,
                        )
                    })
                else {
                    return;
                };
                let carrier_landing = next_cell(
                    &view.walkable,
                    carrier.cell,
                    door,
                    carrier.stats.movement_speed,
                );
                let Some(blocker) = blocker_at_door else {
                    let Some(blocker) = view.units.iter().find(|unit| {
                        unit.player == 0
                            && unit.id != carrier.id
                            && unit.cell == carrier_landing
                            && unit.total_carried() == 0
                    }) else {
                        return;
                    };
                    let mut forbidden = BTreeSet::new();
                    forbidden.insert(blocker.cell);
                    forbidden.insert(door);
                    if candidates
                        .get(&blocker.id)
                        .and_then(|options| 
                            Self::planned_egress(view, blocker, options, &forbidden)
                        )
                        .filter(|(_, target)| MoisanBot::compatible(*target, Target::Cell(door)))
                        .is_some()
                    {
                        return;
                    }
                    let blocker_to_carrier = next_cell(
                        &view.walkable,
                        blocker.cell,
                        carrier.cell,
                        blocker.stats.movement_speed,
                    );
                    if blocker_to_carrier == carrier.cell {
                        candidates
                            .insert(carrier.id, vec![Self::forced_move(carrier, blocker.cell)]);
                        candidates
                            .insert(blocker.id, vec![Self::forced_move(blocker, carrier.cell)]);
                        return;
                    }
                    let clear = next_cell(&view.walkable, blocker.cell, carrier.cell, 1);
                    if clear != blocker.cell && clear != carrier.cell {
                        candidates.insert(blocker.id, vec![Self::forced_move(blocker, clear)]);
                        candidates.insert(carrier.id, vec![MoisanBot::wait()]);
                    }
                    return;
                };
                if blocker.total_carried() > 0 && !self.carries_committed_fruit(blocker) {
                    candidates.insert(
                        blocker.id,
                        vec![Candidate {
                            command: format!("DROP {}", blocker.id),
                            score: 20_000.0,
                            target: Target::Cell(door),
                        }],
                    );
                    if carrier_landing == door {
                        candidates.insert(carrier.id, vec![MoisanBot::wait()]);
                    }
                    return;
                }
                let occupied: BTreeSet<Cell> = view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 0 && unit.id != blocker.id)
                    .map(|unit| unit.cell)
                    .collect();
                let forbidden = BTreeSet::from([door, carrier_landing]);
                let planned_egress = candidates
                    .get(&blocker.id)
                    .and_then(|options| Self::planned_egress(view, blocker, options, &forbidden));
                if planned_egress.is_some() {
                    return;
                }
                let blocker_to_carrier = next_cell(
                    &view.walkable,
                    blocker.cell,
                    carrier.cell,
                    blocker.stats.movement_speed,
                );
                if carrier_landing == door && blocker_to_carrier == carrier.cell {
                    candidates.insert(carrier.id, vec![Self::forced_move(carrier, door)]);
                    candidates.insert(blocker.id, vec![Self::forced_move(blocker, carrier.cell)]);
                    return;
                }
                let from_carrier = bfs_distances(&view.walkable, &[carrier.cell]);
                let egress = ortho_neighbors(door)
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .filter(|cell| !occupied.contains(cell))
                    .min_by_key(|cell| {
                        (
                            *cell == carrier_landing,
                            -from_carrier.get(cell).copied().unwrap_or(10_000),
                            *cell,
                        )
                    });
                if let Some(cell) = egress {
                    candidates.insert(blocker.id, vec![Self::forced_move(blocker, cell)]);
                    if carrier_landing == cell {
                        candidates.insert(carrier.id, vec![MoisanBot::wait()]);
                    } else if carrier_landing != carrier.cell {
                        candidates.insert(
                            carrier.id,
                            vec![Self::forced_move(carrier, carrier_landing)],
                        );
                    }
                }
            }
            fn reconcile_regeneration_commitments(&mut self, view: &GameState) {
                if !self.persistent_regeneration {
                    self.regeneration_commitments.clear();
                    return;
                }
                self.regeneration_commitments.retain(|id, kind| {
                    let Some(unit) = view.unit(*id) else {
                        return false;
                    };
                    unit.carry[kind.item_index()] > 0
                        || unit.carry[crate::game::types::WOOD] > 0
                        || view
                            .plant_at(unit.cell)
                            .map(|index| {
                                let plant = &view.plants[index];
                                plant.kind == *kind && plant.health > 0
                            })
                            .unwrap_or(false)
                });
            }
            fn remember_selected_regeneration(&mut self, commands: &[String]) {
                if !self.persistent_regeneration {
                    return;
                }
                for command in commands {
                    let fields: Vec<&str> = command.split_whitespace().collect();
                    if fields.len() != 3 || !fields[0].eq_ignore_ascii_case("PICK") {
                        continue;
                    }
                    let (Ok(id), Some(kind)) = (fields[1].parse(), PlantKind::parse(fields[2]))
                    else {
                        continue;
                    };
                    self.regeneration_commitments.insert(id, kind);
                }
            }
            fn yamo_chop_candidates(
                view: &GameState,
                unit: &Unit,
                type_to_cut: Option<PlantKind>,
                opponent_eta_penalty: i32,
            ) -> Vec<Candidate> {
                let mut candidates = MoisanBot::chop_candidates(view, unit, type_to_cut);
                if opponent_eta_penalty <= 0 {
                    return candidates;
                }
                let from_unit = bfs_distances(&view.walkable, &[unit.cell]);
                let opponents: Vec<_> = view
                    .units
                    .iter()
                    .filter(|opponent| {
                        opponent.player == 1
                            && opponent.stats.chop_power > 0
                            && opponent.free_capacity() > 0
                    })
                    .map(|opponent| (opponent, bfs_distances(&view.walkable, &[opponent.cell])))
                    .collect();
                for candidate in &mut candidates {
                    let Target::Tree(cell) = candidate.target else {
                        continue;
                    };
                    let Some(plant_index) = view.plant_at(cell) else {
                        continue;
                    };
                    let Some(distance) = from_unit.get(&cell) else {
                        continue;
                    };
                    let our_eta = MoisanBot::ceil_div(*distance, unit.stats.movement_speed);
                    let risk = opponents
                        .iter()
                        .filter_map(|(opponent, distances)| {
                            let distance = distances.get(&cell)?;
                            let opponent_eta =
                                MoisanBot::ceil_div(*distance, opponent.stats.movement_speed);
                            if opponent_eta > our_eta {
                                return None;
                            }
                            let uncontested_turns = our_eta - opponent_eta + 1;
                            let damage = uncontested_turns * opponent.stats.chop_power;
                            Some(damage as f64 / view.plants[plant_index].health.max(1) as f64)
                        })
                        .fold(0.0_f64, f64::max)
                        .min(2.0);
                    candidate.score -= opponent_eta_penalty as f64 * risk;
                }
                candidates
            }
            fn main_candidates(
                view: &GameState,
                unit: &Unit,
                type_to_cut: Option<PlantKind>,
                idle_regeneration: bool,
                safe_regeneration: bool,
                opponent_eta_penalty: i32,
            ) -> Vec<Candidate> {
                let mut out = vec![MoisanBot::wait()];
                let carried = unit.total_carried();
                if safe_regeneration && Self::carried_fruit(unit).is_some() {
                    out.extend(Self::bank_candidates(view, unit));
                    return out;
                }
                if carried > 0 && is_adjacent(unit.cell, view.shacks[0]) {
                    out.extend(Self::bank_candidates(view, unit));
                }
                if safe_regeneration
                    && carried == 0
                    && view.turn >= 100
                    && view.plants.len() <= 2
                    && view.units.iter().filter(|unit| unit.player == 0).count() >= 2
                    && is_adjacent(unit.cell, view.shacks[0])
                    && view.plant_at(unit.cell).is_none()
                {
                    for (priority, kind) in Self::inventory_fruits(view).into_iter().enumerate() {
                        out.push(Candidate {
                            command: format!("PICK {} {}", unit.id, kind.as_str()),
                            score: 7500.0 - priority as f64,
                            target: Target::Cell(unit.cell),
                        });
                    }
                }
                if unit.free_capacity() <= 0 {
                    out.extend(Self::bank_candidates(view, unit));
                    return out;
                }
                let chops =
                    Self::yamo_chop_candidates(view, unit, type_to_cut, opponent_eta_penalty,);
                if idle_regeneration && chops.is_empty() {
                    let mut fallback = vec![MoisanBot::wait()];
                    fallback.extend(Self::idle_harvest_candidates(view, unit));
                    if unit.total_carried() > 0 {
                        fallback.extend(Self::bank_candidates(view, unit));
                    }
                    return fallback;
                }
                if chops.is_empty() && carried > 0 {
                    out.extend(Self::bank_candidates(view, unit));
                } else {
                    out.extend(chops);
                }
                out
            }
            fn carried_fruit(unit: &Unit) -> Option<PlantKind> {
                [
                    (PLUM, PlantKind::Plum),
                    (LEMON, PlantKind::Lemon),
                    (APPLE, PlantKind::Apple),
                    (BANANA, PlantKind::Banana),
                ]
                .into_iter()
                .find(|(item, _)| unit.carry[*item] > 0)
                .map(|(_, kind)| kind)
            }
            fn inventory_fruits(view: &GameState) -> Vec<PlantKind> {
                [
                    (view.inventories[0][BANANA], PlantKind::Banana),
                    (view.inventories[0][PLUM], PlantKind::Plum),
                    (view.inventories[0][LEMON], PlantKind::Lemon),
                    (view.inventories[0][APPLE], PlantKind::Apple),
                ]
                .into_iter()
                .filter(|(amount, _)| *amount > 0)
                .map(|(_, kind)| kind)
                .collect()
            }
            fn conversion_chop_turns(
                view: &GameState,
                cell: Cell,
                kind: PlantKind,
                chop: i32
            ) -> i32 {
                if chop <= 0 {
                    return 10_000;
                }
                let near_water = view.water.iter().any(|water| is_adjacent(*water, cell));
                let cooldown_reset = effective_cooldown(kind, near_water);
                let (_, growth_health) = crate::game::rules::tree_health_params(kind);
                let mut size = 1;
                let mut health = tree_health(kind, size);
                let mut cooldown = cooldown_reset;
                for turns in 1..=100 {
                    health -= chop;
                    if health <= 0 {
                        return turns;
                    }
                    if cooldown > 0 {
                        cooldown -= 1;
                    }
                    if cooldown == 0 && size < 4 {
                        size += 1;
                        health += growth_health;
                        cooldown = cooldown_reset;
                    }
                }
                10_000
            }
            fn endgame_candidates(
                view: &GameState,
                unit: &Unit,
                type_to_cut: Option<PlantKind>,
                safe_regeneration: bool,
                opponent_eta_penalty: i32,
            ) -> Vec<Candidate> {
                let mut out = vec![MoisanBot::wait()];
                let dist = bfs_distances(&view.walkable, &[unit.cell]);
                let shack_starts: Vec<Cell> = ortho_neighbors(view.shacks[0])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .collect();
                let to_shack = bfs_distances(&view.walkable, &shack_starts);
                let turns_left = TOTAL_TURNS - view.turn + 1;
                if let Some(kind) = Self::carried_fruit(unit) {
                    for cell in view.walkable.iter().filter(|cell| {
                        view.plant_at(**cell).is_none()
                            && dist.contains_key(*cell)
                            && !view.units.iter().any(|other| {
                                other.player == unit.player
                                    && other.id != unit.id
                                    && other.cell == **cell
                            })
                    }) {
                        let travel = MoisanBot::ceil_div(dist[cell], unit.stats.movement_speed);
                        let chop_turns =
                            Self::conversion_chop_turns(view, *cell, kind, unit.stats.chop_power);
                        let return_turns = to_shack
                            .get(cell)
                            .copied()
                            .map(|distance| 
                                MoisanBot::ceil_div(distance, unit.stats.movement_speed) + 1
                            )
                            .unwrap_or(10_000);
                        if travel + 1 + chop_turns + return_turns > turns_left {
                            continue;
                        }
                        let at_target = unit.cell == *cell;
                        out.push(Candidate {
                            command: if at_target {
                                format!("PLANT {} {}", unit.id, kind.as_str())
                            } else {
                                format!("MOVE {} {} {}", unit.id, cell.0, cell.1)
                            },
                            score: if at_target {
                                9_000.0
                            } else {
                                8_000.0 - dist[cell] as f64
                            },
                            target: Target::Cell(*cell),
                        });
                    }
                    if out.len() > 1 {
                        return out;
                    }
                    out.extend(Self::bank_candidates(view, unit));
                    return out;
                }
                if unit.total_carried() > 0 {
                    out.extend(Self::bank_candidates(view, unit));
                    return out;
                }
                let chops =
                    Self::yamo_chop_candidates(view, unit, type_to_cut, opponent_eta_penalty,);
                if let Some(mut current) = chops
                    .iter()
                    .find(|candidate| candidate.command == format!("CHOP {}", unit.id))
                    .cloned()
                {
                    current.score = 10_000.0;
                    out.push(current);
                    return out;
                }
                for (priority, kind) in Self::inventory_fruits(view).into_iter().enumerate() {
                    let conversion_turns =
                        Self::conversion_chop_turns(view, unit.cell, kind, unit.stats.chop_power);
                    let can_plant_here = !safe_regeneration || view.plant_at(unit.cell).is_none();
                    if is_adjacent(unit.cell, view.shacks[0])
                        && can_plant_here
                        && conversion_turns + 3 <= turns_left
                    {
                        let conversion_score = if view.turn > 250 {
                            7_000.0 - priority as f64
                        } else {
                            750.0 / (conversion_turns + 3) as f64 - priority as f64 / 100.0
                        };
                        out.push(Candidate {
                            command: format!("PICK {} {}", unit.id, kind.as_str()),
                            score: conversion_score,
                            target: Target::Cell(unit.cell),
                        });
                    } else {
                        for cell in &shack_starts {
                            let Some(distance) = dist.get(cell) else {
                                continue;
                            };
                            if safe_regeneration && view.plant_at(*cell).is_some() {
                                continue;
                            }
                            if view.units.iter().any(|other| {
                                other.player == unit.player
                                    && other.id != unit.id
                                    && other.cell == *cell
                            }) {
                                continue;
                            }
                            let travel = MoisanBot::ceil_div(*distance, unit.stats.movement_speed);
                            let conversion_turns = Self::conversion_chop_turns(
                                view,
                                *cell,
                                kind,
                                unit.stats.chop_power
                            );
                            if travel + conversion_turns + 3 > turns_left {
                                continue;
                            }
                            let conversion_score = if view.turn > 250 {
                                6_000.0 - priority as f64 - travel as f64
                            } else {
                                750.0 / (travel + conversion_turns + 3) as f64
                                    - priority as f64 / 100.0
                            };
                            out.push(Candidate {
                                command: format!("MOVE {} {} {}", unit.id, cell.0, cell.1),
                                score: conversion_score,
                                target: Target::Cell(*cell),
                            });
                        }
                    }
                }
                out.extend(chops);
                out
            }

            // --------------------------------------------------------------------------
            // Endgame idle harvest — indexed block `idle-harvest` [feature]
            //
            // In the endgame, when every candidate action is a WAIT, harvests ripe fruit instead of
            // idling.
            // --------------------------------------------------------------------------
            fn idle_harvest_candidates(view: &GameState, unit: &Unit,) -> Vec<Candidate> {
                if unit.total_carried() != 0 || unit.stats.harvest_power <= 0 {
                    return Vec::new();
                }
                let from_unit = bfs_distances(&view.walkable, &[unit.cell]);
                let shack_starts: Vec<Cell> = ortho_neighbors(view.shacks[0])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .collect();
                let to_shack = bfs_distances(&view.walkable, &shack_starts);
                let turns_left = TOTAL_TURNS - view.turn + 1;
                view.plants
                    .iter()
                    .filter(|plant| {
                        plant.health > 0
                            && plant.fruits > 0
                            && (unit.cell == plant.cell
                                || !view.units.iter().any(|other| {
                                    other.player == 1
                                        && other.cell == plant.cell
                                        && other.total_carried() == 0
                                }))
                            && from_unit.contains_key(&plant.cell)
                            && to_shack.contains_key(&plant.cell)
                    })
                    .filter_map(|plant| {
                        let travel =
                            MoisanBot::ceil_div(from_unit[&plant.cell], unit.stats.movement_speed);
                        let home =
                            MoisanBot::ceil_div(to_shack[&plant.cell], unit.stats.movement_speed);
                        let trip = travel + 1 + home + 1;
                        (trip <= turns_left).then(|| Candidate {
                            command: if unit.cell == plant.cell {
                                format!("HARVEST {}", unit.id)
                            } else {
                                format!("MOVE {} {} {}", unit.id, plant.cell.0, plant.cell.1)
                            },
                            score: 1.0 / trip.max(1) as f64,
                            target: Target::Tree(plant.cell),
                        })
                    })
                    .collect()
            }
            fn endgame(view: &GameState) -> bool {
                view.turn > 250
                    || (view.plants.len() <= 4
                        && score(&view.inventories[0]) < score(&view.inventories[1]))
            }
        }
        impl Bot for YamoBot {
            fn commands(&mut self, view: &GameState) -> Vec<String> {
                self.reconcile_regeneration_commitments(view);
                self.ensure_opening(view);
                self.enforce_training_deadline(view);
                // The opening dispatcher (stage 2A) owns the TRAIN and every troll's command
                // from turn 1 to the third troll; None once the champion's own play resumes.
                let opening = self.opening_dispatch(view);
                let desired = match opening.as_ref().and_then(|plan| plan.0) {
                    Some(stats) => stats,
                    None => self
                        .desired_second
                        .map(|objective| objective.stats)
                        .unwrap_or_else(Self::fallback_second_troll),
                };
                let train_now = match opening.as_ref() {
                    Some(plan) => plan.0.is_some(),
                    None => !self.opening_abandoned && MoisanBot::can_train(view, desired),
                };
                let mut out = Vec::new();
                if !self.announced {
                    self.announced = true;
                    out.push(format!("MSG {}", self.announcement));
                }
                if train_now {
                    out.push(format!(
                        "TRAIN {} {} {} {}",
                        desired.movement_speed,
                        desired.carry_capacity,
                        desired.harvest_power,
                        desired.chop_power
                    ));
                }
                let mut my_units: Vec<&Unit> =
                    view.units.iter().filter(|unit| unit.player == 0).collect();
                my_units.sort_by_key(|unit| unit.id);
                let early = !self.opening_abandoned && my_units.len() < 2 && !train_now;
                let endgame = Self::endgame(view);
                let mut by_id = BTreeMap::new();
                for unit in my_units {
                    let committed_regeneration =
                        self.regeneration_commitments.contains_key(&unit.id);
                    let mut candidates = if committed_regeneration {
                        Self::endgame_candidates(
                            view,
                            unit,
                            self.type_to_cut,
                            self.persistent_regeneration,
                            self.opponent_eta_penalty,
                        )
                    } else if endgame
                        && self.persistent_regeneration
                        && Self::carried_fruit(unit).is_some()
                    {
                        Self::main_candidates(
                            view,
                            unit,
                            self.type_to_cut,
                            false,
                            true,
                            self.opponent_eta_penalty,
                        )
                    } else if endgame {
                        Self::endgame_candidates(
                            view,
                            unit,
                            self.type_to_cut,
                            self.persistent_regeneration,
                            self.opponent_eta_penalty,
                        )
                    } else if early {
                        MoisanBot::early_candidates(view, unit, desired)
                    } else {
                        Self::main_candidates(
                            view,
                            unit,
                            self.type_to_cut,
                            self.idle_regeneration,
                            self.persistent_regeneration,
                            self.opponent_eta_penalty,
                        )
                    };
                    if endgame
                        && self.idle_harvest
                        && (!self.idle_harvest_clock_only || view.turn > 250)
                        && candidates
                            .iter()
                            .all(|candidate| candidate.target == Target::None)
                    {
                        candidates.extend(Self::idle_harvest_candidates(view, unit));
                    }
                    if self.persistent_regeneration && train_now {
                        candidates.retain(|candidate| !candidate.command.starts_with("PICK "));
                    }
                    if train_now
                        && unit.cell == view.shacks[0]
                        && !candidates
                            .iter()
                            .any(|candidate| candidate.command.starts_with("MOVE "))
                    {
                        if let Some(cell) = ortho_neighbors(view.shacks[0])
                            .into_iter()
                            .find(|cell| view.walkable.contains(cell))
                        {
                            candidates.push(Candidate {
                                command: format!("MOVE {} {} {}", unit.id, cell.0, cell.1),
                                score: 6_500.0,
                                target: Target::Cell(cell),
                            });
                        }
                    }
                    if let Some(forced) = opening.as_ref().and_then(|plan| plan.1.get(&unit.id)) {
                        candidates = vec![forced.clone()];
                    }
                    by_id.insert(unit.id, candidates);
                }
                if self.door_unblocking {
                    self.force_unique_door_clear(view, &mut by_id);
                }
                let mut selected = MoisanBot::select(by_id, &view.inventories[0]);
                MoisanBot::resolve_move_conflicts(view, &mut selected);
                self.remember_selected_regeneration(&selected);
                out.extend(selected);
                if out.is_empty() {
                    out.push("WAIT".to_string());
                }
                out
            }
        }
    }
    use crate::game::GameState;
    pub trait Bot {
        fn commands(&mut self, view: &GameState) -> Vec<String>;
    }
}
use std::io::{self, Write};
use crate::bot::moisan::YamoBot;
use crate::bot::Bot;
use crate::game::protocol::{read_static_map, read_turn};
fn main() {
    let stdin = io::stdin();
    let stdout = io::stdout();
    let mut reader = io::BufReader::new(stdin.lock());
    let mut out = io::BufWriter::new(stdout.lock());
    let Some(map) = read_static_map(&mut reader) else {
        return;
    };
    let mut bot = YamoBot::tuned_carry_regeneration_transit_idle_harvest();
    let mut turn = 1;
    while let Some(view) = read_turn(&mut reader, &map, turn) {
        let commands = bot.commands(&view);
        writeln!(out, "{}", commands.join(";")).expect("write command line");
        out.flush().expect("flush command line");
        turn += 1;
    }
}
