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
        // The v6 per-turn census. Every field here is a REQUIRED field on the wire; the
        // decoder `claude_1/narrate6/narrate6.py` asserts at import that no field of the grammar
        // is without a consumer and no consumed field is off the grammar (r6 C3).
        #[derive(Clone, Debug, Default)]
        struct KeepMeta {
            kp: u32,
            kq: u32,
            kl: u32,
            kr: u32,
            rd: u32,
            rg: u32,
            ri: u32,
            rx: u32,
            rf: u32,
            rt: u32,
            ro: u32,
            nl: u32,
            nl_producer: u32,
            nl_door: u32,
            nl_admissibility: u32,
            nl_other: u32,
            ka: u32,
            kc: u32,
            xc: u32,
            xw: u32,
            xn: u32,
            xp: u32,
            xg: u32,
            xd: u32,
            xj: u32,
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
            opponent_eta_penalty: i32,
            // Candidate 3. One remembered goal per own troll, its birth turn, and the kind of
            // the plant that stood at a Tree goal when it was recorded (the `rt` release, F7).
            // The one-turn snapshot is the emitted command line and the cell the unit stood on
            // when it emitted it -- `CHOP`/`HARVEST` carry no cell of their own (`:893`, `:707`).
            kept_goals: BTreeMap<i32, Target>,
            kept_since: BTreeMap<i32, i32>,
            kept_kinds: BTreeMap<i32, PlantKind>,
            last_command: BTreeMap<i32, String>,
            last_cell: BTreeMap<i32, Cell>,
        }
        #[derive(Clone, Copy)]
        struct PredictedTree {
            size: i32,
            health: i32,
            cooldown: i32,
        }
        impl MoisanBot {
            // ---------------------------------------------------------------- Candidate 3
            // Task 20260826-candidate-3-keep-your-goal. Packet of record:
            // claude_1/cure3/g0-candidate-3-2026-08-26-r6.md (r5 as amended by r6 C1-C5),
            // ACCEPT-WITH-EDIT by codex_1 20260826T122017Z; the owner's bound forbids an r7.
            //
            // R5, in four steps run inside `commands()` and nowhere else:
            //   (a) release  -- four world predicates, order dead / gone / impossible / done
            //   (b) restrict -- L|g, order preserved; never adds a candidate, never scores
            //   (c) decide   -- the champion's `select` over the restricted lists; a turn the
            //                   restriction makes undecidable releases the YOUNGER goal
            //   (d) record   -- goalless units only, exact string match against the pre-
            //                   restriction list L
            //
            // No margin and no constant of any kind appears in the rule.
            //
            // `build_arms3.py` rewrites exactly the line below to make the three arms, and
            // nothing else differs between them.
            const KEEP_RULE_ENABLED: bool = false; const NARRATE_V6_ENABLED: bool = true;
            // Ruled at G-0 and NOT a knob: a Tree goal is done on CHOP *or* HARVEST at the cell
            // with the carry full (r5 F1, ruled `true` by codex_1 20260826T122017Z).
            const DONE_ON_HARVEST: bool = true;
            // `ERASE_WHEN_NOT_LIVE` is ruled FALSE (coordinator Ruling 2) and is therefore not a
            // constant here: a valid goal that no candidate carries this turn is preserved and
            // unrestricting, and the `true` arm is code nothing would ever execute.

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
                if ids.len() == 2 {
                    let mut best_score = f64::NEG_INFINITY;
                    let mut best_pair = None;
                    for a in &candidates_by_id[&ids[0]] {
                        for b in &candidates_by_id[&ids[1]] {
                            if !Self::compatible(a.target, b.target)
                                || !Self::stock_compatible(a, b, inventory)
                            {
                                continue;
                            }
                            let score = a.score + b.score;
                            if score > best_score {
                                best_score = score;
                                best_pair = Some((a.command.clone(), b.command.clone()));
                            }
                        }
                    }
                    if let Some((a, b)) = best_pair {
                        return vec![a, b];
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
            fn resolve_move_conflicts(
                view: &GameState,
                commands: &mut [String],
                branch: &mut BTreeMap<i32, char>,
                w_collisions: &mut u32,
            ) {
                Self::resolve_move_conflicts_with_priority(
                    view,
                    commands,
                    &BTreeSet::new(),
                    branch,
                    w_collisions,
                );
            }
            fn resolve_move_conflicts_with_priority(
                view: &GameState,
                commands: &mut [String],
                priority_ids: &BTreeSet<i32>,
                branch: &mut BTreeMap<i32, char>,
                w_collisions: &mut u32,
            ) {
                Self::resolve_move_conflicts_with_priority_and_forbidden(
                    view,
                    commands,
                    priority_ids,
                    &BTreeSet::new(),
                    branch,
                    w_collisions,
                );
            }
            fn resolve_move_conflicts_with_priority_and_forbidden(
                view: &GameState,
                commands: &mut [String],
                priority_ids: &BTreeSet<i32>,
                forbidden_for_non_priority: &BTreeSet<Cell>,
                branch: &mut BTreeMap<i32, char>,
                w_collisions: &mut u32,
            ) {
                let mut granted: BTreeSet<Cell> = BTreeSet::new();
                let mut waiting_cells: BTreeSet<Cell> = BTreeSet::new();
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
                for (id, index, current, _, landing) in &projections {
                    if landing == current {
                        commands[*index] = "WAIT".to_string();
                        // A self-targeting MOVE resolved to WAIT is W. Its cell is reserved
                        // already: the unit is not in `moving_ids`.
                        branch.insert(*id, 'W');
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
                        granted.insert(landing);
                        commands[index] = format!("MOVE {} {} {}", id, landing.0, landing.1);
                        branch.insert(id, 'P');
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
                    // `d_cur` uses the detour key's OWN fallback, or L and R would be decided
                    // by comparing two different metrics.
                    let d_cur = toward_goal
                        .get(&unit.cell)
                        .copied()
                        .unwrap_or_else(|| manhattan(unit.cell, target));
                    commands[index] = if let Some(cell) = detour {
                        let d_detour = toward_goal
                            .get(&cell)
                            .copied()
                            .unwrap_or_else(|| manhattan(cell, target));
                        reserved.insert(cell);
                        granted.insert(cell);
                        branch.insert(id, if d_detour <= d_cur { 'L' } else { 'R' });
                        format!("MOVE {} {} {}", id, cell.0, cell.1)
                    } else {
                        waiting_cells.insert(unit.cell);
                        branch.insert(id, 'W');
                        "WAIT".to_string()
                    };
                }
                *w_collisions = waiting_cells
                    .iter()
                    .filter(|cell| granted.contains(cell))
                    .count() as u32;
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
                    kept_goals: BTreeMap::new(),
                    kept_since: BTreeMap::new(),
                    kept_kinds: BTreeMap::new(),
                    last_command: BTreeMap::new(),
                    last_cell: BTreeMap::new(),
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
                let max_carry_capacity = max_carry_capacity.clamp(2, 3);
                let max_chop_power = max_chop_power.clamp(2, 3);
                for movement_speed in 2..=3 {
                    for carry_capacity in 2..=max_carry_capacity {
                        for chop_power in 2..=max_chop_power {
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
                        Self::opening_objective(view, Self::fallback_second_troll())
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
            // If the second worker has not been trained by a deadline turn, trains the strongest
            // currently affordable floored build instead, or waits for the basic 2/2/0/2 -- the
            // second troll is never weaker than speed 2, carry 2, chop 2 (the floor, 2026-08-27).
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
                self.desired_second = Some(
                    Self::strongest_affordable(view, self.opening_policy).unwrap_or_else(|| {
                        Self::opening_objective(view, Self::fallback_second_troll())
                    }),
                );
            }
            fn fallback_second_troll() -> Stats {
                Stats {
                    movement_speed: 2,
                    carry_capacity: 2,
                    harvest_power: 0,
                    chop_power: 2,
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
        // ------------------------------------------------------------ Candidate 3 helpers
        impl MoisanBot {
            // The champion's two-unit joint maximisation (`select`, `:952-972`) lifted verbatim,
            // so the restricted decision and the unrestricted reference `xj` compares it against
            // are literally the same code. The only addition is that the winning sum comes back.
            fn best_pair(
                a_list: &[Candidate],
                b_list: &[Candidate],
                inventory: &[i32; 6],
            ) -> Option<(String, String, f64)> {
                let mut best_score = f64::NEG_INFINITY;
                let mut best = None;
                for a in a_list {
                    for b in b_list {
                        if !Self::compatible(a.target, b.target)
                            || !Self::stock_compatible(a, b, inventory)
                        {
                            continue;
                        }
                        let score = a.score + b.score;
                        if score > best_score {
                            best_score = score;
                            best = Some((a.command.clone(), b.command.clone(), score));
                        }
                    }
                }
                best
            }
            fn best_score(list: &[Candidate]) -> Option<f64> {
                list.iter().map(|candidate| candidate.score).max_by(f64::total_cmp)
            }
            // Basis points given up, floored toward zero and saturating at 999_999: a saturated
            // value is decode-visible and reads as "at least 100x", never as a measurement.
            fn give_up_bps(free: f64, kept: f64) -> u32 {
                if !(kept > 0.0) || !(free > kept) {
                    return 0;
                }
                let raw = (10_000.0 * (free - kept) / kept).floor();
                if !raw.is_finite() || raw >= 999_999.0 {
                    return 999_999;
                }
                if raw <= 0.0 {
                    0
                } else {
                    raw as u32
                }
            }
            // Ids are parsed exactly as `remember_selected_regeneration` (`:1702-1715`) parses
            // them, so the two recording steps cannot disagree about whose command is whose.
            fn command_for_unit(commands: &[String], id: i32) -> Option<String> {
                commands
                    .iter()
                    .find(|command| {
                        let fields: Vec<&str> = command.split_whitespace().collect();
                        fields.len() >= 2 && fields[1].parse::<i32>().map_or(false, |v| v == id)
                    })
                    .cloned()
            }
            // The exact-match rule of R5(d)/§6, used for BOTH the recording and the narrator's
            // `chosen` column so the two cannot disagree: exactly one match, or several agreeing
            // on the target, gives that target; differing targets or no match give `None`.
            fn matched_target(list: &[Candidate], command: &str) -> Option<Target> {
                let targets: Vec<Target> = list
                    .iter()
                    .filter(|candidate| candidate.command == command)
                    .map(|candidate| candidate.target)
                    .collect();
                let first = targets.first().copied()?;
                if targets.iter().any(|target| *target != first) {
                    return None;
                }
                Some(first)
            }
        }
        // ------------------------------------------------------------------- Candidate 3, R5
        impl YamoBot {
            // ---- R5(a) release ---------------------------------------------------------------
            // Runs immediately after `reconcile_regeneration_commitments` and BEFORE any candidate
            // is built, so a kept goal restricts ZERO turns after its invalidating event becomes
            // observable. Order is fixed -- dead, gone, impossible, done -- and the first to fire
            // wins, so the census sums exactly and no turn is double-counted.
            fn release_kept_goals(&mut self, view: &GameState, meta: &mut KeepMeta) {
                let held: Vec<i32> = self.kept_goals.keys().copied().collect();
                for id in held {
                    let Some(goal) = self.kept_goals.get(&id).copied() else {
                        continue;
                    };
                    let alive = view
                        .units
                        .iter()
                        .find(|unit| unit.player == 0 && unit.id == id);
                    let Some(unit) = alive else {
                        self.forget_goal(id);
                        meta.rx += 1;
                        meta.kr += 1;
                        continue;
                    };
                    if let Some(cause) = self.gone_cause(view, unit, goal) {
                        match cause {
                            'f' => meta.rf += 1,
                            't' => meta.rt += 1,
                            'o' => meta.ro += 1,
                            // r6 C1: the Bank cause has NO sub-count. It is asserted structurally
                            // unreachable and `rf + rt + ro == rg` is the falsifier for that
                            // assertion -- strictly better than an always-zero `rw=`, which would
                            // read as a passing check.
                            _ => {}
                        }
                        self.forget_goal(id);
                        meta.rg += 1;
                        meta.kr += 1;
                        continue;
                    }
                    if Self::goal_impossible(view, unit, goal) {
                        self.forget_goal(id);
                        meta.ri += 1;
                        meta.kr += 1;
                        continue;
                    }
                    if self.goal_done(view, unit, goal) {
                        self.forget_goal(id);
                        meta.rd += 1;
                        meta.kr += 1;
                    }
                }
            }
            fn forget_goal(&mut self, id: i32) {
                self.kept_goals.remove(&id);
                self.kept_since.remove(&id);
                self.kept_kinds.remove(&id);
            }
            fn gone_cause(&self, view: &GameState, unit: &Unit, goal: Target) -> Option<char> {
                match goal {
                    Target::Tree(cell) => match view.plant_at(cell) {
                        None => Some('f'),
                        Some(index) => {
                            let plant = &view.plants[index];
                            if plant.health <= 0 {
                                Some('f')
                            } else if self
                                .kept_kinds
                                .get(&unit.id)
                                .map_or(false, |kind| *kind != plant.kind)
                            {
                                // F7: §3.3's `rt` row is worded against "the unit's producer this
                                // turn", but no producer has run yet at release time. The row's own
                                // predicate (`plant.kind != kind`, `:714`) is evaluated against the
                                // goal's OWN kind instead -- the kind that stood at `c` when the
                                // goal was recorded.
                                Some('t')
                            } else {
                                None
                            }
                        }
                    },
                    // F3/C1: no accepts or fullness predicate exists anywhere on the DROP path
                    // (`:596-611`), so the walkable test is the whole cause -- and it is
                    // structurally unreachable, bank cells being
                    // `ortho_neighbors(shacks[0]) INTERSECT walkable` by construction (`:592-594`).
                    Target::Bank(cell) => {
                        if view.walkable.contains(&cell) {
                            None
                        } else {
                            Some('b')
                        }
                    }
                    Target::Cell(cell) => {
                        let taken = view.plant_at(cell).is_some()
                            && !self
                                .last_command
                                .get(&unit.id)
                                .map_or(false, |command| command.starts_with("PLANT "));
                        let no_fruit = Self::carried_fruit(unit).is_none()
                            && !self.regeneration_commitments.contains_key(&unit.id);
                        if !view.walkable.contains(&cell) || taken || no_fruit {
                            Some('o')
                        } else {
                            None
                        }
                    }
                    Target::Shack | Target::None => None,
                }
            }
            fn goal_impossible(view: &GameState, unit: &Unit, goal: Target) -> bool {
                // F4: `Shack` gets NO impossible test. §3.4 names `shacks[0]` as its goal cell,
                // but that cell is never in `view.walkable` (`parse_static_map`, `:328-355`, adds
                // only `.` cells and the shack is `0`), so the literal test would release every
                // `Shack` goal one turn after it is recorded; and the neighbour form fires exactly
                // when the goal is live, since the `Shack` candidate is emitted ONLY when no bank
                // cell is reachable (`:590-623`). `Shack` ends on `done` or `dead`, both reachable.
                let cell = match goal {
                    Target::Tree(cell) | Target::Bank(cell) | Target::Cell(cell) => cell,
                    Target::Shack | Target::None => return false,
                };
                // The champion's own BFS walks `view.walkable`, a static map-derived set that
                // never removes an occupied cell, so a standing teammate is never an
                // impossibility -- it is the exchange rule's business, exactly as the charter says.
                !bfs_distances(&view.walkable, &[unit.cell]).contains_key(&cell)
            }
            fn goal_done(&self, view: &GameState, unit: &Unit, goal: Target) -> bool {
                let last = match self.last_command.get(&unit.id) {
                    Some(command) => command.as_str(),
                    None => "",
                };
                let at = self.last_cell.get(&unit.id).copied();
                match goal {
                    // The capacity middle. NOT the first chop: a single swing is progress toward
                    // the goal, and releasing on it is the champion's re-pick, which is the loop's
                    // mechanism. Done is "the goal has yielded everything this troll can take".
                    Target::Tree(cell) => {
                        let worked = last == format!("CHOP {}", unit.id)
                            || (MoisanBot::DONE_ON_HARVEST
                                && last == format!("HARVEST {}", unit.id));
                        worked && at == Some(cell) && unit.free_capacity() <= 0
                    }
                    Target::Bank(cell) => last == format!("DROP {}", unit.id) && at == Some(cell),
                    Target::Cell(cell) => {
                        view.plant_at(cell).is_some()
                            && last.starts_with(&format!("PLANT {} ", unit.id))
                    }
                    Target::Shack => unit.total_carried() == 0,
                    Target::None => true,
                }
            }
            // ---- R5(b) restrict and R5(c) decide ---------------------------------------------
            // Returns the commands and the ids that were live-restricted on the FIRST pass -- the
            // set `k=2` is read against. `L|g` is a subset of `L`, so the rule can never cause a
            // command the champion did not offer this turn.
            fn select_keeping(
                &mut self,
                view: &GameState,
                by_id: &BTreeMap<i32, Vec<Candidate>>,
                inventory: &[i32; 6],
                door_cleared: &BTreeSet<i32>,
                meta: &mut KeepMeta,
            ) -> (Vec<String>, BTreeSet<i32>) {
                let mut first_pass = true;
                let mut restricted: BTreeSet<i32> = BTreeSet::new();
                loop {
                    let mut live: BTreeSet<i32> = BTreeSet::new();
                    let mut effective: BTreeMap<i32, Vec<Candidate>> = BTreeMap::new();
                    for (id, list) in by_id {
                        let kept: Vec<Candidate> = match self.kept_goals.get(id) {
                            // Order preserved: `L|g` is a filter of `L`, never a re-sort.
                            Some(goal) => list
                                .iter()
                                .filter(|candidate| candidate.target == *goal)
                                .cloned()
                                .collect(),
                            None => Vec::new(),
                        };
                        if kept.is_empty() {
                            // Not live. The goal is NOT erased: `ERASE_WHEN_NOT_LIVE` is false.
                            effective.insert(*id, list.clone());
                        } else {
                            live.insert(*id);
                            effective.insert(*id, kept);
                        }
                    }
                    if first_pass {
                        self.census_entry(view, by_id, &effective, &live, door_cleared, meta);
                        restricted = live.clone();
                        first_pass = false;
                    }
                    // R5(c) first sentence, and the containment theorem: with nothing
                    // live-restricted the champion's `select` runs UNMODIFIED and no step below
                    // executes.
                    if live.is_empty() {
                        return (MoisanBot::select(by_id.clone(), inventory), restricted);
                    }
                    let ids: Vec<i32> = effective.keys().copied().collect();
                    if ids.len() == 1 {
                        // §4.1. `max_by` returns the LAST maximal element, so ties are decided by
                        // list order exactly as in the champion. No contest is possible here.
                        let best = effective[&ids[0]]
                            .iter()
                            .max_by(|a, b| a.score.total_cmp(&b.score))
                            .expect("a live-restricted list is non-empty by construction");
                        return (vec![best.command.clone()], restricted);
                    }
                    if ids.len() == 2 {
                        let (a, b) = (ids[0], ids[1]);
                        let both = live.contains(&a) && live.contains(&b);
                        if let Some((first, second, sum)) =
                            MoisanBot::best_pair(&effective[&a], &effective[&b], inventory)
                        {
                            if both {
                                // §5.3. `xj` is r3's `rho` turned from a threshold into a price
                                // tag: what the joint decision gave up against the unrestricted
                                // maximisation of the SAME turn. F5: the `None` arm is unreachable
                                // -- `L|g` is a subset of `L`, so a restricted pair existing
                                // implies an unrestricted pair exists. It is not a measurement.
                                meta.xj = match MoisanBot::best_pair(&by_id[&a], &by_id[&b], inventory)
                                {
                                    Some((_, _, free)) => MoisanBot::give_up_bps(free, sum),
                                    None => 0,
                                };
                            }
                            return (vec![first, second], restricted);
                        }
                        if both {
                            // §4.3, the contest. The YOUNGER goal is released -- never both, never
                            // to a score, and the elder is untouched. At most one release per
                            // troll per turn, so this terminates.
                            let younger = self.younger_of(a, b);
                            self.forget_goal(younger);
                            meta.xc += 1;
                            meta.kr += 1;
                            continue;
                        }
                        // §4.2(b). One restricted, no joint pair, and no second goal to release,
                        // so the decision is phased -- and THE KEPT TROLL IS NEVER THE ONE THAT
                        // WAITS. The partner's forced `wait()` is the rule's real cost, counted
                        // `xw` and bounded by one turn: the partner holds no goal to carry.
                        let keeper = if live.contains(&a) { a } else { b };
                        let partner = if keeper == a { b } else { a };
                        let chosen = effective[&keeper]
                            .iter()
                            .max_by(|x, y| x.score.total_cmp(&y.score))
                            .expect("a live-restricted list is non-empty by construction")
                            .clone();
                        let mut partner_list = effective[&partner].clone();
                        partner_list.sort_by(|x, y| y.score.total_cmp(&x.score));
                        let taken = partner_list.into_iter().find(|candidate| {
                            MoisanBot::compatible(candidate.target, chosen.target)
                                && MoisanBot::stock_compatible(&chosen, candidate, inventory)
                        });
                        let partner_command = match taken {
                            Some(candidate) => candidate.command,
                            None => {
                                // Counted only when the partner's FULL list held something other
                                // than a `WAIT`, so champion-native waits and the door-clearance
                                // `wait()` are never charged to the rule.
                                if by_id[&partner]
                                    .iter()
                                    .any(|candidate| candidate.command != "WAIT")
                                {
                                    meta.xw += 1;
                                }
                                MoisanBot::wait().command
                            }
                        };
                        meta.xp += 1;
                        let commands = if keeper == a {
                            vec![chosen.command, partner_command]
                        } else {
                            vec![partner_command, chosen.command]
                        };
                        return (commands, restricted);
                    }
                    // §4.4, the `>= 3` path, two phases. Phase 2 cannot un-assign phase 1.
                    let mut used_targets: Vec<Target> = Vec::new();
                    let mut used_stock = [0; 6];
                    let mut assigned: BTreeMap<i32, String> = BTreeMap::new();
                    let mut phase1: Vec<i32> = live.iter().copied().collect();
                    phase1.sort_by_key(|id| {
                        (self.kept_since.get(id).copied().unwrap_or(i32::MAX), *id)
                    });
                    let mut collided: Vec<i32> = Vec::new();
                    for id in phase1 {
                        let mut list = effective[&id].clone();
                        list.sort_by(|x, y| y.score.total_cmp(&x.score));
                        let pick = list.into_iter().find(|candidate| {
                            used_targets
                                .iter()
                                .all(|target| MoisanBot::compatible(candidate.target, *target))
                                && MoisanBot::picked_item(&candidate.command)
                                    .map(|item| used_stock[item] < inventory[item])
                                    .unwrap_or(true)
                        });
                        match pick {
                            Some(candidate) => {
                                used_targets.push(candidate.target);
                                if let Some(item) = MoisanBot::picked_item(&candidate.command) {
                                    used_stock[item] += 1;
                                }
                                assigned.insert(id, candidate.command);
                            }
                            None => {
                                collided.push(id);
                                meta.xc += 1;
                                meta.xg += 1;
                                meta.kr += 1;
                            }
                        }
                    }
                    for id in &collided {
                        self.forget_goal(*id);
                    }
                    // Phase 2 IS the champion's greedy loop -- ascending id, full lists, the same
                    // accumulated sets -- run against what phase 1 already took.
                    let mut commands: Vec<String> = Vec::new();
                    for id in &ids {
                        if let Some(command) = assigned.get(id) {
                            commands.push(command.clone());
                            continue;
                        }
                        let mut list = by_id[id].clone();
                        list.sort_by(|x, y| y.score.total_cmp(&x.score));
                        let pick = list.into_iter().find(|candidate| {
                            used_targets
                                .iter()
                                .all(|target| MoisanBot::compatible(candidate.target, *target))
                                && MoisanBot::picked_item(&candidate.command)
                                    .map(|item| used_stock[item] < inventory[item])
                                    .unwrap_or(true)
                        });
                        let chosen = match pick {
                            Some(candidate) => candidate,
                            None => {
                                if by_id[id]
                                    .iter()
                                    .any(|candidate| candidate.command != "WAIT")
                                {
                                    meta.xw += 1;
                                }
                                MoisanBot::wait()
                            }
                        };
                        used_targets.push(chosen.target);
                        if let Some(item) = MoisanBot::picked_item(&chosen.command) {
                            used_stock[item] += 1;
                        }
                        commands.push(chosen.command);
                    }
                    return (commands, restricted);
                }
            }
            fn younger_of(&self, a: i32, b: i32) -> i32 {
                let key = |id: i32| (self.kept_since.get(&id).copied().unwrap_or(i32::MIN), id);
                if key(a) > key(b) {
                    a
                } else {
                    b
                }
            }
            // ---- the census, taken on the FIRST pass -----------------------------------------
            // A unit whose goal is released as contested was live-restricted when it entered, so
            // it stays in `kq`; `kp == kq + kl` is exact.
            fn census_entry(
                &self,
                view: &GameState,
                by_id: &BTreeMap<i32, Vec<Candidate>>,
                effective: &BTreeMap<i32, Vec<Candidate>>,
                live: &BTreeSet<i32>,
                door_cleared: &BTreeSet<i32>,
                meta: &mut KeepMeta,
            ) {
                for (id, goal) in &self.kept_goals {
                    if !by_id.contains_key(id) {
                        continue;
                    }
                    meta.kp += 1;
                    let age = view.turn - self.kept_since.get(id).copied().unwrap_or(view.turn);
                    if age > 0 {
                        meta.ka = meta.ka.max(age as u32);
                    }
                    if live.contains(id) {
                        meta.kq += 1;
                        // §5.3 `xd`: the per-troll price tag. Units whose kept score is not
                        // positive are excluded and counted in `kq` only.
                        meta.xd = meta.xd.max(MoisanBot::give_up_bps(
                            MoisanBot::best_score(&by_id[id]).unwrap_or(0.0),
                            MoisanBot::best_score(&effective[id]).unwrap_or(0.0),
                        ));
                    } else {
                        meta.kl += 1;
                        meta.nl += 1;
                        match self.not_live_cause(view, *id, *goal, &by_id[id], door_cleared) {
                            'p' => meta.nl_producer += 1,
                            'd' => meta.nl_door += 1,
                            'a' => meta.nl_admissibility += 1,
                            _ => meta.nl_other += 1,
                        }
                    }
                }
            }
            // The four not-live causes of §2, in a fixed priority order, each read off what the
            // turn actually produced rather than re-derived from which branch ran. A non-zero
            // `nl_other` is a FINDING for the packet under §9.10, not a decode error: the causes
            // are a claim about the base and `nl_other` is how that claim is falsified.
            fn not_live_cause(
                &self,
                view: &GameState,
                id: i32,
                goal: Target,
                list: &[Candidate],
                door_cleared: &BTreeSet<i32>,
            ) -> char {
                // Case 3. `force_unique_door_clear` REPLACES a unit's whole list, and R5(b) runs
                // after it, so door clearance is never outvoted by a kept goal.
                if door_cleared.contains(&id) {
                    return 'd';
                }
                // Case 1, the residual walk-back's own counter. The producer chosen this turn
                // routes a carrying unit to bank candidates only (`:1936-1939`, `:1779-1782`), so
                // no Tree or Cell goal can be offered at all.
                if !list.is_empty()
                    && list
                        .iter()
                        .all(|candidate| matches!(candidate.target, Target::Bank(_) | Target::Shack))
                {
                    return 'p';
                }
                // Case 4. The goal's tree is alive AND reachable -- `gone` and `impossible` both
                // ran first and did not fire -- yet no candidate carries it. `chop_candidates`
                // filters on health, reachability and endgame admissibility only (`:859-882`), and
                // the first two are excluded here, so admissibility is the only cause left.
                if let Target::Tree(cell) = goal {
                    if let Some(index) = view.plant_at(cell) {
                        if view.plants[index].health > 0 {
                            return 'a';
                        }
                    }
                }
                'o'
            }
            // `kc`: turns the rule holds a troll on a tree it is already chopping -- where it is
            // inert, since the champion scores that same CHOP at the top of its own list.
            fn chop_holds(&self, commands: &[String]) -> u32 {
                self.kept_goals
                    .iter()
                    .filter(|(id, goal)| {
                        matches!(goal, Target::Tree(_))
                            && MoisanBot::command_for_unit(commands, **id)
                                .map_or(false, |command| command == format!("CHOP {}", id))
                    })
                    .count() as u32
            }
            // ---- R5(d) record, and the one-turn snapshot the release tests read next turn -----
            // Only units that entered the selector WITHOUT a valid kept goal -- including a unit
            // whose goal was released as contested this turn -- take one. Erasure on ambiguity is
            // the safe direction: a missing kept goal costs one turn of preference, a wrong one is
            // a preference for something the troll is not doing.
            fn record_kept_goals(
                &mut self,
                view: &GameState,
                by_id: &BTreeMap<i32, Vec<Candidate>>,
                commands: &[String],
            ) {
                for (id, list) in by_id {
                    let Some(unit) = view
                        .units
                        .iter()
                        .find(|unit| unit.player == 0 && unit.id == *id)
                    else {
                        continue;
                    };
                    // The snapshot and the recording read the SAME final emitted line, so `done`
                    // and the record can never disagree about what the unit did.
                    let emitted = MoisanBot::command_for_unit(commands, *id);
                    match &emitted {
                        Some(command) => {
                            self.last_command.insert(*id, command.clone());
                            self.last_cell.insert(*id, unit.cell);
                        }
                        None => {
                            self.last_command.remove(id);
                            self.last_cell.remove(id);
                        }
                    }
                    if self.kept_goals.contains_key(id) {
                        continue;
                    }
                    let Some(command) = emitted else {
                        continue;
                    };
                    let Some(target) = MoisanBot::matched_target(list, &command) else {
                        continue;
                    };
                    if target == Target::None {
                        continue;
                    }
                    self.kept_goals.insert(*id, target);
                    self.kept_since.insert(*id, view.turn);
                    if let Target::Tree(cell) = target {
                        if let Some(index) = view.plant_at(cell) {
                            self.kept_kinds.insert(*id, view.plants[index].kind);
                        }
                    }
                }
                let alive: BTreeSet<i32> = view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 0)
                    .map(|unit| unit.id)
                    .collect();
                self.last_command.retain(|id, _| alive.contains(id));
                self.last_cell.retain(|id, _| alive.contains(id));
            }
            // ---- the v6 wire -----------------------------------------------------------------
            // Reads only. Nothing here decides anything. v6 is v5's payload with `m=` deleted --
            // there is no margin constant to disambiguate a wire with, which is itself the
            // version's signature -- plus the three-valued `k=` and the keep census.
            fn narrate_target(target: Target) -> String {
                match target {
                    Target::None => "NONE".to_string(),
                    Target::Shack => "SHACK".to_string(),
                    Target::Bank(cell) => format!("BANK({},{})", cell.0, cell.1),
                    Target::Cell(cell) => format!("CELL({},{})", cell.0, cell.1),
                    Target::Tree(cell) => format!("TREE({},{})", cell.0, cell.1),
                }
            }
            // `k=2` restricted AND the emitted command carried the kept goal; `k=1` the unit holds
            // a valid kept goal whose emitted command does not carry it -- the not-live case, and
            // (F6) the case where `resolve_move_conflicts` rewrote a restricted command into
            // something no candidate proposed; `k=0` no valid kept goal, including a goal released
            // as contested this turn, which is why `xc` and `k` are read together and never apart.
            fn keep_code(
                &self,
                id: i32,
                goal_lists: &BTreeMap<i32, Vec<Candidate>>,
                restricted: &BTreeSet<i32>,
                commands: &[String],
            ) -> char {
                let Some(goal) = self.kept_goals.get(&id) else {
                    return '0';
                };
                if restricted.contains(&id) {
                    if let Some(command) = MoisanBot::command_for_unit(commands, id) {
                        let carried = goal_lists
                            .get(&id)
                            .map_or(false, |list| {
                                list.iter().any(|candidate| {
                                    candidate.command == command && candidate.target == *goal
                                })
                            });
                        if carried {
                            return '2';
                        }
                    }
                }
                '1'
            }
            fn narrate_message(
                &self,
                view: &GameState,
                by_id: &BTreeMap<i32, Vec<Candidate>>,
                restricted: &BTreeSet<i32>,
                commands: &[String],
                branch: &BTreeMap<i32, char>,
                meta: &KeepMeta,
                w_collisions: u32,
                banner: Option<&str>,
            ) -> String {
                // Every live own unit exactly once, ids ascending, roster taken from the VIEW.
                let mut ids: Vec<i32> = view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 0)
                    .map(|unit| unit.id)
                    .collect();
                ids.sort();
                let mut tokens: Vec<String> = vec![format!("NARRATE v6 t={}", view.turn)];
                for id in ids {
                    let chosen = MoisanBot::command_for_unit(commands, id)
                        .and_then(|command| {
                            by_id
                                .get(&id)
                                .and_then(|list| MoisanBot::matched_target(list, &command))
                        })
                        .unwrap_or(Target::None);
                    let want = match by_id.get(&id) {
                        Some(list) => match list
                            .iter()
                            .max_by(|a, b| a.score.total_cmp(&b.score))
                        {
                            Some(candidate) => Self::narrate_target(candidate.target),
                            None => "ABSENT".to_string(),
                        },
                        None => "ABSENT".to_string(),
                    };
                    let code = branch.get(&id).copied().unwrap_or('N');
                    // `b=` is v4's `blocked_turns`, kept in the shape for the decoder's benefit
                    // and identically 0: Candidate 1's hold was its only writer and it is retired.
                    tokens.push(format!(
                        "u{}={}/{}/r={}/b=0/k={}",
                        id,
                        Self::narrate_target(chosen),
                        want,
                        code,
                        self.keep_code(id, by_id, restricted, commands)
                    ));
                }
                // `pz=1`, `sp=0` and the four exchange counters have no writer in a Candidate 3
                // arm: R5 adds no holder and there is no exchange rule here. They are carried with
                // v5's meanings unchanged (r6 C4) and a violation is a defect in R5.
                tokens.push("pz=1".to_string());
                tokens.push("sp=0".to_string());
                tokens.push(format!("wc={}", w_collisions));
                tokens.push("sw=0".to_string());
                tokens.push("so=0".to_string());
                tokens.push("sn=0".to_string());
                tokens.push("sf=0".to_string());
                tokens.push(format!("kp={}", meta.kp));
                tokens.push(format!("kq={}", meta.kq));
                tokens.push(format!("kl={}", meta.kl));
                tokens.push(format!("kr={}", meta.kr));
                tokens.push(format!("rd={}", meta.rd));
                tokens.push(format!("rg={}", meta.rg));
                tokens.push(format!("ri={}", meta.ri));
                tokens.push(format!("rx={}", meta.rx));
                tokens.push(format!("rf={}", meta.rf));
                tokens.push(format!("rt={}", meta.rt));
                tokens.push(format!("ro={}", meta.ro));
                tokens.push(format!("nl={}", meta.nl));
                tokens.push(format!("nl_producer={}", meta.nl_producer));
                tokens.push(format!("nl_door={}", meta.nl_door));
                tokens.push(format!("nl_admissibility={}", meta.nl_admissibility));
                tokens.push(format!("nl_other={}", meta.nl_other));
                tokens.push(format!("ka={}", meta.ka));
                tokens.push(format!("kc={}", meta.kc));
                tokens.push(format!("xc={}", meta.xc));
                tokens.push(format!("xw={}", meta.xw));
                tokens.push(format!("xn={}", meta.xn));
                tokens.push(format!("xp={}", meta.xp));
                tokens.push(format!("xg={}", meta.xg));
                tokens.push(format!("xd={}", meta.xd));
                tokens.push(format!("xj={}", meta.xj));
                let body = tokens.join(" ");
                match banner {
                    Some(text) => format!("MSG {} {}", text, body),
                    None => format!("MSG {}", body),
                }
            }
        }
        impl Bot for YamoBot {
            fn commands(&mut self, view: &GameState) -> Vec<String> {
                self.reconcile_regeneration_commitments(view);
                let mut keep_meta = KeepMeta::default();
                // R5(a). Before any candidate is built, so a kept goal restricts zero turns after
                // its invalidating event becomes observable.
                if MoisanBot::KEEP_RULE_ENABLED {
                    self.release_kept_goals(view, &mut keep_meta);
                }
                self.ensure_opening(view);
                self.enforce_training_deadline(view);
                let desired = self
                    .desired_second
                    .map(|objective| objective.stats)
                    .unwrap_or_else(Self::fallback_second_troll);
                let train_now = !self.opening_abandoned && MoisanBot::can_train(view, desired);
                let mut out = Vec::new();
                let narrate_banner = if !self.announced {
                    self.announced = true;
                    if !MoisanBot::NARRATE_V6_ENABLED {
                        out.push(format!("MSG {}", self.announcement));
                    }
                    Some(self.announcement)
                } else {
                    None
                };
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
                    by_id.insert(unit.id, candidates);
                }
                // Which units the door clearance REPLACED the list of, read off the bytes rather
                // than re-derived: `nl_door` is a claim about this call and nothing else.
                let mut door_cleared: BTreeSet<i32> = BTreeSet::new();
                if self.door_unblocking {
                    let before: BTreeMap<i32, Vec<String>> = by_id
                        .iter()
                        .map(|(id, list)| {
                            (*id, list.iter().map(|c| c.command.clone()).collect())
                        })
                        .collect();
                    self.force_unique_door_clear(view, &mut by_id);
                    for (id, list) in &by_id {
                        let after: Vec<String> =
                            list.iter().map(|c| c.command.clone()).collect();
                        if before.get(id) != Some(&after) {
                            door_cleared.insert(*id);
                        }
                    }
                }
                // R5(b) and (c) run AFTER `force_unique_door_clear` -- so door clearance cannot be
                // outvoted by a kept goal -- and BEFORE `select`, because the preference is only
                // correct inside the maximisation.
                let mut restricted: BTreeSet<i32> = BTreeSet::new();
                let mut selected = if MoisanBot::KEEP_RULE_ENABLED {
                    let (commands, live) = self.select_keeping(
                        view,
                        &by_id,
                        &view.inventories[0],
                        &door_cleared,
                        &mut keep_meta,
                    );
                    restricted = live;
                    commands
                } else {
                    MoisanBot::select(by_id.clone(), &view.inventories[0])
                };
                let mut narrate_branch: BTreeMap<i32, char> = BTreeMap::new();
                let mut w_collisions = 0;
                MoisanBot::resolve_move_conflicts(
                    view,
                    &mut selected,
                    &mut narrate_branch,
                    &mut w_collisions,
                );
                if keep_meta.xc > 0 {
                    keep_meta.xn = 1;
                }
                if MoisanBot::KEEP_RULE_ENABLED {
                    keep_meta.kc = self.chop_holds(&selected);
                }
                let narration = if MoisanBot::NARRATE_V6_ENABLED {
                    Some(self.narrate_message(
                        view,
                        &by_id,
                        &restricted,
                        &selected,
                        &narrate_branch,
                        &keep_meta,
                        w_collisions,
                        narrate_banner,
                    ))
                } else {
                    None
                };
                // R5(d) LAST, and against the final emitted line -- never against `select`'s
                // output, which `resolve_move_conflicts` may have rewritten.
                if MoisanBot::KEEP_RULE_ENABLED {
                    self.record_kept_goals(view, &by_id, &selected);
                }
                self.remember_selected_regeneration(&selected);
                out.extend(selected);
                // The empty-check runs on the GAMEPLAY tokens alone, so the payload can never
                // suppress the base's WAIT.
                if out.is_empty() {
                    out.push("WAIT".to_string());
                }
                if let Some(payload) = narration {
                    // Exactly one MSG per turn, FIRST in the list.
                    out.insert(0, payload);
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
