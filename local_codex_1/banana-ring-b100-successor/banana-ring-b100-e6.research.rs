#![allow(dead_code, unused_imports)]
pub mod game {
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
            pub const ALL: [PlantKind; 4] = [
                PlantKind::Plum,
                PlantKind::Lemon,
                PlantKind::Apple,
                PlantKind::Banana,
            ];
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
            pub const STARTER_GOLD: Stats = Stats {
                movement_speed: 1,
                carry_capacity: 1,
                harvest_power: 1,
                chop_power: 1,
            };
            pub const STARTER_WOOD: Stats = Stats {
                movement_speed: 1,
                carry_capacity: 1,
                harvest_power: 1,
                chop_power: 0,
            };
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
            pub fn empty(width: i32, height: i32) -> GameState {
                GameState {
                    width,
                    height,
                    walkable: BTreeSet::new(),
                    shacks: [(0, 0), (0, 0)],
                    inventories: [[0; ITEM_COUNT]; 2],
                    units: Vec::new(),
                    plants: Vec::new(),
                    scores: [0, 0],
                    turn: 1,
                    next_id: 0,
                    iron: BTreeSet::new(),
                    water: BTreeSet::new(),
                }
            }
            pub fn plant_at(&self, cell: Cell) -> Option<usize> {
                self.plants.iter().position(|plant| plant.cell == cell)
            }
            pub fn unit(&self, id: i32) -> Option<&Unit> {
                self.units.iter().find(|unit| unit.id == id)
            }
            pub fn unit_mut(&mut self, id: i32) -> Option<&mut Unit> {
                self.units.iter_mut().find(|unit| unit.id == id)
            }
            pub fn units_for(&self, player: usize) -> Vec<&Unit> {
                let mut units: Vec<&Unit> = self
                    .units
                    .iter()
                    .filter(|unit| unit.player == player)
                    .collect();
                units.sort_by_key(|unit| unit.id);
                units
            }
        }
    }
    pub mod rules {
        use super::types::{PlantKind, Stock, APPLE, IRON, LEMON, PLUM, WOOD};
        pub const TOTAL_TURNS: i32 = 300;
        pub const MAX_SIZE: i32 = 4;
        pub const MAX_FRUITS: i32 = 3;
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
            speed: i32,
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
        pub fn grid_rows(game: &GameState, seat: usize) -> Vec<String> {
            (0..game.height)
                .map(|y| {
                    (0..game.width)
                        .map(|x| {
                            let cell = (x, y);
                            if cell == game.shacks[seat] {
                                '0'
                            } else if cell == game.shacks[1 - seat] {
                                '1'
                            } else if game.iron.contains(&cell) {
                                '+'
                            } else if game.water.contains(&cell) {
                                '~'
                            } else if game.walkable.contains(&cell) {
                                '.'
                            } else {
                                '#'
                            }
                        })
                        .collect()
                })
                .collect()
        }
        pub fn turn_block(game: &GameState, seat: usize) -> String {
            let mut out = String::new();
            for player in [seat, 1 - seat] {
                let inv = game.inventories[player];
                out.push_str(&format!(
                    "{} {} {} {} {} {}\n",
                    inv[0], inv[1], inv[2], inv[3], inv[4], inv[5]
                ));
            }
            out.push_str(&format!("{}\n", game.plants.len()));
            for plant in &game.plants {
                out.push_str(&format!(
                    "{} {} {} {} {} {} {}\n",
                    plant.kind.as_str(),
                    plant.cell.0,
                    plant.cell.1,
                    plant.size,
                    plant.health,
                    plant.fruits,
                    plant.cooldown
                ));
            }
            out.push_str(&format!("{}\n", game.units.len()));
            for unit in &game.units {
                let rel_player = if unit.player == seat { 0 } else { 1 };
                out.push_str(&format!(
                    "{} {} {} {} {} {} {} {} {} {} {} {} {} {}\n",
                    unit.id,
                    rel_player,
                    unit.cell.0,
                    unit.cell.1,
                    unit.stats.movement_speed,
                    unit.stats.carry_capacity,
                    unit.stats.harvest_power,
                    unit.stats.chop_power,
                    unit.carry[0],
                    unit.carry[1],
                    unit.carry[2],
                    unit.carry[3],
                    unit.carry[4],
                    unit.carry[5]
                ));
            }
            out
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
            turn: i32,
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
    pub use types::{Cell, GameState, Plant, PlantKind, Stats, Unit};
}
pub mod bot {
    pub mod moisan {
        use super::super::game::nav::{
            bfs_distances, is_adjacent, manhattan, next_cell, ortho_neighbors,
        };
        use super::super::game::rules::{
            effective_cooldown, item_index, score, training_cost, tree_health, TOTAL_TURNS,
        };
        use super::super::game::types::{
            Cell, GameState, Plant, PlantKind, Stats, Stock, Unit, APPLE, BANANA, IRON, LEMON,
            PLUM, WOOD,
        };
        use super::Bot;
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
        #[derive(Default)]
        pub struct MoisanBot {
            announced: bool,
            type_to_cut: Option<PlantKind>,
            desired_second: Option<Stats>,
        }
        #[derive(Clone, Copy, Debug, Eq, PartialEq)]
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
        impl Default for YamoOpeningPolicy {
            fn default() -> Self {
                Self {
                    train_horizon: 15,
                    preferred_min_carry: 1,
                    max_carry_capacity: 3,
                    preferred_min_chop: 1,
                    max_chop_power: 3,
                    require_preferred: false,
                    max_extra_eta: 0,
                    hard_train_turn: i32::MAX,
                    prefer_movement_ties: false,
                }
            }
        }
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
            pub const CARRY2_CHOP2: Self = Self {
                train_horizon: 15,
                preferred_min_carry: 2,
                max_carry_capacity: 2,
                preferred_min_chop: 2,
                max_chop_power: 2,
                require_preferred: true,
                max_extra_eta: 0,
                hard_train_turn: 35,
                prefer_movement_ties: false,
            };
            pub const TUNED_CARRY_CHOP2: Self = Self {
                max_chop_power: 2,
                ..Self::TUNED_CARRY
            };
            pub const TUNED_CARRY_MOVEMENT: Self = Self {
                prefer_movement_ties: true,
                ..Self::TUNED_CARRY
            };
        }
        #[derive(Clone, Copy, Debug, Eq, PartialEq)]
        struct OpeningObjective {
            stats: Stats,
            estimated_eta: i32,
        }
        #[derive(Clone, Copy, Debug, Eq, PartialEq)]
        enum ScarceIntent {
            NeedSeed,
            HarvestSeed {
                source: Cell,
                kind: PlantKind,
            },
            PlantMother {
                target: Cell,
                kind: PlantKind,
            },
            TendMother {
                mother: Cell,
                kind: PlantKind,
            },
            PlantCrop {
                mother: Cell,
                target: Cell,
                kind: PlantKind,
            },
        }
        #[derive(Clone, Copy, Debug, Eq, PartialEq)]
        struct ScarcePlan {
            farmer_id: i32,
            intent: ScarceIntent,
            crop: Option<Cell>,
        }
        #[derive(Clone, Copy, Debug, Eq, PartialEq)]
        struct BankCommitment {
            door: Cell,
            cargo: Stock,
            previous: Option<Cell>,
        }
        #[derive(Clone, Copy, Debug, Eq, PartialEq)]
        struct BankConflictProbe {
            door: Cell,
            cargo: Stock,
            from: Cell,
            detour: Cell,
            blocker: Option<(i32, Cell)>,
        }
        #[derive(Clone, Copy, Debug, Eq, PartialEq)]
        struct BankActivation {
            door: Cell,
            previous: Option<Cell>,
        }
        #[derive(Clone, Copy, Debug, Eq, PartialEq)]
        struct PartialTreeConflictProbe {
            tree: Cell,
            cargo: Stock,
            from: Cell,
            detour: Cell,
            blocker: (i32, Cell),
        }
        #[derive(Clone)]
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
            bank_router: bool,
            bank_router_confirmed: bool,
            partial_tree_coordination: bool,
            idle_harvest: bool,
            idle_harvest_clock_only: bool,
            bank_commitments: BTreeMap<i32, BankCommitment>,
            bank_conflict_probes: BTreeMap<i32, BankConflictProbe>,
            regeneration_commitments: BTreeMap<i32, PlantKind>,
            fresh_harvest_regeneration: bool,
            fresh_harvest_commitments: usize,
            fresh_harvest_first_turn: Option<i32>,
            fresh_harvest_units: BTreeSet<i32>,
            fresh_harvest_pending_plants: BTreeMap<i32, (i32, Cell, PlantKind)>,
            fresh_harvest_successful_plants: usize,
            scarce_farming: bool,
            initial_tree_count: Option<usize>,
            scarce_plan: Option<ScarcePlan>,
            opponent_eta_penalty: i32,
            tree_target_bonus: i32,
            tree_commitments: BTreeMap<i32, Cell>,
            partial_tree_conflict_probes: BTreeMap<i32, PartialTreeConflictProbe>,
            external_idle_unit: Option<i32>,
            external_protected_tree: Option<Cell>,
            external_orchard_task: Option<(i32, Cell)>,
            external_orchard_offers: usize,
            external_orchard_selections: usize,
            external_orchard_harvest_selections: usize,
            external_orchard_first_selected_turn: Option<i32>,
            external_orchard_selected_this_turn: bool,
            first_worker_max_bank_hp0: bool,
            first_worker_turn_one_override: Option<Stats>,
            plant_history_initialized: bool,
            previous_plants: BTreeSet<Cell>,
            own_plant_attempts: BTreeSet<Cell>,
            opponent_crops: BTreeSet<Cell>,
            opponent_crops_seen: usize,
            opponent_crop_bonus: i32,
            opponent_crop_dual_value: bool,
            opponent_crop_eta_limit: i32,
            opponent_crop_start_turn: i32,
            opponent_crop_min_seen: usize,
            opponent_crop_selected: usize,
            opponent_crop_first_selected_turn: Option<i32>,
            opponent_crop_harvest_contact: bool,
            opponent_crop_harvested: BTreeSet<Cell>,
            opponent_crop_harvest_rewrites: usize,
        }
        impl Default for YamoBot {
            fn default() -> Self {
                Self::with_opening_policy(YamoOpeningPolicy::default())
            }
        }
        #[derive(Clone, Copy)]
        struct PredictedTree {
            size: i32,
            health: i32,
            cooldown: i32,
        }
        impl MoisanBot {
            fn ensure_focus_type(&mut self, view: &GameState) {
                if self.type_to_cut.is_some() {
                    return;
                }
                self.type_to_cut = Some(Self::focus_type(view));
            }
            fn focus_type(view: &GameState) -> PlantKind {
                let starts: Vec<Cell> = ortho_neighbors(view.shacks[0])
                    .iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .copied()
                    .collect();
                let dist = bfs_distances(&view.walkable, &starts);
                [PlantKind::Lemon, PlantKind::Plum]
                    .into_iter()
                    .min_by_key(|kind| {
                        view.plants
                            .iter()
                            .filter(|plant| plant.kind == *kind)
                            .map(|plant| dist.get(&plant.cell).copied().unwrap_or(10_000))
                            .sum::<i32>()
                    })
                    .unwrap_or(PlantKind::Lemon)
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
            fn ensure_desired_second(&mut self, view: &GameState) {
                if self.desired_second.is_some() {
                    return;
                }
                let n = view.units.iter().filter(|unit| unit.player == 0).count() as i32;
                let level = |item: usize| {
                    if view.inventories[0][item] >= n + 9 {
                        3
                    } else {
                        2
                    }
                };
                self.desired_second = Some(Stats {
                    movement_speed: level(PLUM),
                    carry_capacity: level(LEMON),
                    harvest_power: 0,
                    chop_power: if view.iron.is_empty() { 3 } else { level(IRON) },
                });
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
                let expected = tree_health(plant.kind, plant.size);
                if plant.health < expected {
                    1
                } else {
                    0
                }
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
                            health += super::super::game::rules::tree_health_params(plant.kind).1;
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
                let (_, growth_health) = super::super::game::rules::tree_health_params(plant.kind);
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
                    if Some(plant.kind) == type_to_cut && opponent_trolls <= 2 {
                        let opponent_distance = manhattan(plant.cell, view.shacks[1]);
                        score += 900.0 / (1 + opponent_distance) as f64;
                    }
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
            fn ring_cells(view: &GameState) -> Vec<Cell> {
                let shack = view.shacks[0];
                let mut cells = Vec::new();
                for dx in -1..=1 {
                    for dy in -1..=1 {
                        if dx == 0 && dy == 0 {
                            continue;
                        }
                        let cell = (shack.0 + dx, shack.1 + dy);
                        if view.walkable.contains(&cell) {
                            cells.push(cell);
                        }
                    }
                }
                cells.sort_unstable();
                cells
            }
            fn is_ring_diagonal(view: &GameState, cell: Cell) -> bool {
                (cell.0 - view.shacks[0].0).abs() == 1 && (cell.1 - view.shacks[0].1).abs() == 1
            }
            fn farmer_candidates(view: &GameState, unit: &Unit) -> Vec<Candidate> {
                let mut out = vec![Self::wait()];
                let ring = Self::ring_cells(view);
                let ring_set: BTreeSet<Cell> = ring.iter().copied().collect();
                let dist = bfs_distances(&view.walkable, &[unit.cell]);
                let empty_ring: Vec<Cell> = ring
                    .iter()
                    .filter(|cell| view.plant_at(**cell).is_none())
                    .filter(|cell| dist.contains_key(*cell))
                    .filter(|cell| {
                        !view.units.iter().any(|other| {
                            other.player == 0 && other.id != unit.id && other.cell == **cell
                        })
                    })
                    .copied()
                    .collect();
                if Self::carrying_any(unit) || unit.free_capacity() <= 0 {
                    if unit.carry[BANANA] > 0 {
                        for cell in &empty_ring {
                            let travel = Self::ceil_div(dist[cell], unit.stats.movement_speed);
                            out.push(Candidate {
                                command: if unit.cell == *cell {
                                    format!("PLANT {} BANANA", unit.id)
                                } else {
                                    format!("MOVE {} {} {}", unit.id, cell.0, cell.1)
                                },
                                score: 9_000.0 - travel as f64,
                                target: Target::Cell(*cell),
                            });
                        }
                    }
                    out.extend(Self::bank_candidates(view, unit));
                    return out;
                }
                for plant in view.plants.iter().filter(|plant| {
                    plant.kind == PlantKind::Banana
                        && plant.health > 0
                        && plant.fruits > 0
                        && dist.contains_key(&plant.cell)
                        && (!ring_set.contains(&plant.cell)
                            || Self::is_ring_diagonal(view, plant.cell))
                }) {
                    let travel = Self::ceil_div(dist[&plant.cell], unit.stats.movement_speed);
                    let local_seed = ring_set.contains(&plant.cell);
                    out.push(Candidate {
                        command: if unit.cell == plant.cell {
                            format!("HARVEST {}", unit.id)
                        } else {
                            format!("MOVE {} {} {}", unit.id, plant.cell.0, plant.cell.1)
                        },
                        score: if local_seed { 8_200.0 } else { 7_600.0 } - travel as f64,
                        target: Target::Tree(plant.cell),
                    });
                }
                if !empty_ring.is_empty() && view.inventories[0][BANANA] > 0 {
                    for cell in ortho_neighbors(view.shacks[0]) {
                        let Some(distance) = dist.get(&cell) else {
                            continue;
                        };
                        if !view.walkable.contains(&cell) {
                            continue;
                        }
                        out.push(Candidate {
                            command: if unit.cell == cell {
                                format!("PICK {} BANANA", unit.id)
                            } else {
                                format!("MOVE {} {} {}", unit.id, cell.0, cell.1)
                            },
                            score: 7_800.0
                                - Self::ceil_div(*distance, unit.stats.movement_speed) as f64,
                            target: Target::Cell(cell),
                        });
                    }
                }
                for kind in PlantKind::ALL {
                    let base = if kind == PlantKind::Banana {
                        3_400.0
                    } else {
                        3_000.0
                    };
                    out.extend(Self::fruit_candidates(view, unit, kind, base));
                }
                out
            }
            fn ring_chop_candidates(view: &GameState, unit: &Unit) -> Vec<Candidate> {
                if unit.stats.chop_power <= 0 || unit.free_capacity() <= 0 {
                    return Vec::new();
                }
                let ring: BTreeSet<Cell> = Self::ring_cells(view).into_iter().collect();
                let dist = bfs_distances(&view.walkable, &[unit.cell]);
                let mut out = Vec::new();
                for plant in view.plants.iter().filter(|plant| {
                    plant.kind == PlantKind::Banana
                        && plant.health > 0
                        && ring.contains(&plant.cell)
                        && !Self::is_ring_diagonal(view, plant.cell)
                        && dist.contains_key(&plant.cell)
                }) {
                    let travel = Self::ceil_div(dist[&plant.cell], unit.stats.movement_speed);
                    let Some(predicted) = Self::predict_tree(view, plant, travel) else {
                        continue;
                    };
                    if predicted.size < 2 {
                        continue;
                    }
                    let chop_turns = Self::ceil_div(predicted.health, unit.stats.chop_power);
                    let wood = predicted.size.min(unit.free_capacity());
                    out.push(Candidate {
                        command: if unit.cell == plant.cell {
                            format!("CHOP {}", unit.id)
                        } else {
                            format!("MOVE {} {} {}", unit.id, plant.cell.0, plant.cell.1)
                        },
                        score: 5_000.0 + 100.0 * wood as f64 / (travel + chop_turns).max(1) as f64,
                        target: Target::Tree(plant.cell),
                    });
                }
                out
            }
            fn main_loop_candidates(
                view: &GameState,
                unit: &Unit,
                type_to_cut: Option<PlantKind>,
                is_farmer: bool,
            ) -> Vec<Candidate> {
                if is_farmer {
                    return Self::farmer_candidates(view, unit);
                }
                let mut out = vec![Self::wait()];
                if Self::carrying_any(unit) || unit.free_capacity() <= 0 {
                    out.extend(Self::bank_candidates(view, unit));
                    return out;
                }
                out.extend(Self::ring_chop_candidates(view, unit));
                out.extend(Self::chop_candidates(view, unit, type_to_cut));
                out
            }
            fn endgame_candidates(
                view: &GameState,
                unit: &Unit,
                type_to_cut: Option<PlantKind>,
            ) -> Vec<Candidate> {
                let mut out = vec![Self::wait()];
                if Self::carrying_any(unit) {
                    out.extend(Self::bank_candidates(view, unit));
                    return out;
                }
                if unit.stats.harvest_power > 0 && unit.free_capacity() > 0 {
                    let dist = bfs_distances(&view.walkable, &[unit.cell]);
                    let to_shack = bfs_distances(
                        &view.walkable,
                        &ortho_neighbors(view.shacks[0])
                            .into_iter()
                            .filter(|cell| view.walkable.contains(cell))
                            .collect::<Vec<_>>(),
                    );
                    let turns_left = TOTAL_TURNS - view.turn + 1;
                    for plant in view.plants.iter().filter(|plant| {
                        plant.health > 0
                            && plant.fruits > 0
                            && dist.contains_key(&plant.cell)
                            && to_shack.contains_key(&plant.cell)
                    }) {
                        let travel = Self::ceil_div(dist[&plant.cell], unit.stats.movement_speed);
                        let home = Self::ceil_div(to_shack[&plant.cell], unit.stats.movement_speed);
                        if travel + home + 2 > turns_left {
                            continue;
                        }
                        out.push(Candidate {
                            command: if unit.cell == plant.cell {
                                format!("HARVEST {}", unit.id)
                            } else {
                                format!("MOVE {} {} {}", unit.id, plant.cell.0, plant.cell.1)
                            },
                            score: 6_000.0 - (travel + home) as f64,
                            target: Target::Tree(plant.cell),
                        });
                    }
                }
                out.extend(Self::ring_chop_candidates(view, unit));
                out.extend(Self::chop_candidates(view, unit, type_to_cut));
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
                    .filter_map(|(index, command)| {
                        Self::move_command(command).map(|(id, _)| (id, index))
                    })
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
            fn endgame(view: &GameState) -> bool {
                view.turn > 275
            }
        }
        impl Bot for MoisanBot {
            fn commands(&mut self, view: &GameState) -> Vec<String> {
                self.ensure_focus_type(view);
                self.ensure_desired_second(view);
                let mut out = Vec::new();
                if !self.announced {
                    self.announced = true;
                    out.push("MSG moisan-recipe".to_string());
                }
                let desired = self
                    .desired_second
                    .expect("desired second troll initialized");
                let train_now = Self::can_train(view, desired);
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
                let mut by_id = BTreeMap::new();
                let early = my_units.len() < 2 && !train_now;
                let endgame = Self::endgame(view);
                let farmer_id = my_units.first().map(|unit| unit.id);
                for unit in my_units {
                    let clear_cell = (train_now && unit.cell == view.shacks[0])
                        .then(|| {
                            ortho_neighbors(view.shacks[0])
                                .into_iter()
                                .filter(|cell| view.walkable.contains(cell))
                                .min()
                        })
                        .flatten();
                    let candidates = if let Some(cell) = clear_cell {
                        vec![Candidate {
                            command: format!("MOVE {} {} {}", unit.id, cell.0, cell.1),
                            score: 20_000.0,
                            target: Target::Cell(cell),
                        }]
                    } else if endgame {
                        Self::endgame_candidates(view, unit, self.type_to_cut)
                    } else if early {
                        Self::early_candidates(view, unit, desired)
                    } else {
                        Self::main_loop_candidates(
                            view,
                            unit,
                            self.type_to_cut,
                            farmer_id == Some(unit.id),
                        )
                    };
                    by_id.insert(unit.id, candidates);
                }
                let mut selected = Self::select(by_id, &view.inventories[0]);
                Self::resolve_move_conflicts(view, &mut selected);
                out.extend(selected);
                if out.is_empty() {
                    out.push("WAIT".to_string());
                }
                out
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
                    bank_router: false,
                    bank_router_confirmed: false,
                    partial_tree_coordination: false,
                    idle_harvest: false,
                    idle_harvest_clock_only: false,
                    bank_commitments: BTreeMap::new(),
                    bank_conflict_probes: BTreeMap::new(),
                    regeneration_commitments: BTreeMap::new(),
                    fresh_harvest_regeneration: false,
                    fresh_harvest_commitments: 0,
                    fresh_harvest_first_turn: None,
                    fresh_harvest_units: BTreeSet::new(),
                    fresh_harvest_pending_plants: BTreeMap::new(),
                    fresh_harvest_successful_plants: 0,
                    scarce_farming: false,
                    initial_tree_count: None,
                    scarce_plan: None,
                    opponent_eta_penalty: 0,
                    tree_target_bonus: 0,
                    tree_commitments: BTreeMap::new(),
                    partial_tree_conflict_probes: BTreeMap::new(),
                    external_idle_unit: None,
                    external_protected_tree: None,
                    external_orchard_task: None,
                    external_orchard_offers: 0,
                    external_orchard_selections: 0,
                    external_orchard_harvest_selections: 0,
                    external_orchard_first_selected_turn: None,
                    external_orchard_selected_this_turn: false,
                    first_worker_max_bank_hp0: false,
                    first_worker_turn_one_override: None,
                    plant_history_initialized: false,
                    previous_plants: BTreeSet::new(),
                    own_plant_attempts: BTreeSet::new(),
                    opponent_crops: BTreeSet::new(),
                    opponent_crops_seen: 0,
                    opponent_crop_bonus: 0,
                    opponent_crop_dual_value: false,
                    opponent_crop_eta_limit: 0,
                    opponent_crop_start_turn: i32::MAX,
                    opponent_crop_min_seen: usize::MAX,
                    opponent_crop_selected: 0,
                    opponent_crop_first_selected_turn: None,
                    opponent_crop_harvest_contact: false,
                    opponent_crop_harvested: BTreeSet::new(),
                    opponent_crop_harvest_rewrites: 0,
                }
            }
            pub fn tuned_carry() -> Self {
                let mut bot = Self::with_opening_policy(YamoOpeningPolicy::TUNED_CARRY);
                bot.announcement = "yamo-carry2-rust";
                bot
            }
            pub fn carry2_chop2() -> Self {
                let mut bot = Self::with_opening_policy(YamoOpeningPolicy::CARRY2_CHOP2);
                bot.announcement = "yamo-carry2-chop2-rust";
                bot
            }
            pub fn tuned_carry_regeneration() -> Self {
                let mut bot = Self::with_opening_policy(YamoOpeningPolicy::TUNED_CARRY);
                bot.announcement = "yamo-carry-regen-rust";
                bot.idle_regeneration = true;
                bot
            }
            pub fn tuned_carry_regeneration_unblocked() -> Self {
                let mut bot =
                    Self::regeneration_unblocked_with_policy(YamoOpeningPolicy::TUNED_CARRY);
                bot.announcement = "yamo-carry-regen-unblocked-rust";
                bot
            }
            pub fn tuned_carry_regeneration_transit() -> Self {
                let mut bot = Self::tuned_carry_regeneration_unblocked();
                bot.announcement = "yamo-carry-regen-transit-rust";
                bot.partial_bank_transit = true;
                bot
            }
            pub fn tuned_carry_regeneration_transit_idle_harvest() -> Self {
                let mut bot = Self::tuned_carry_regeneration_transit();
                bot.announcement = "yamo-carry-regen-transit-idle-harvest-rust";
                bot.idle_harvest = true;
                bot
            }
            pub fn tuned_carry_regeneration_transit_idle_harvest_clock_only() -> Self {
                let mut bot = Self::tuned_carry_regeneration_transit_idle_harvest();
                bot.announcement = "yamo-carry-regen-transit-clock-idle-harvest-rust";
                bot.idle_harvest_clock_only = true;
                bot
            }
            pub fn tuned_carry_regeneration_transit_idle_harvest_partial_tree_coordination() -> Self
            {
                let mut bot = Self::tuned_carry_regeneration_transit_idle_harvest();
                bot.announcement = "yamo-carry-regen-transit-idle-harvest-partial-tree-rust";
                bot.partial_tree_coordination = true;
                bot
            }
            pub fn tuned_carry_regeneration_transit_idle_harvest_bank_router() -> Self {
                let mut bot = Self::tuned_carry_regeneration_transit_idle_harvest();
                bot.announcement = "yamo-carry-regen-transit-idle-harvest-bank-router-rust";
                bot.bank_router = true;
                bot
            }
            pub fn tuned_carry_regeneration_transit_idle_harvest_confirmed_bank_router() -> Self {
                let mut bot = Self::tuned_carry_regeneration_transit_idle_harvest_bank_router();
                bot.announcement =
                    "yamo-carry-regen-transit-idle-harvest-confirmed-bank-router-rust";
                bot.bank_router_confirmed = true;
                bot
            }
            pub fn regeneration_unblocked_with_policy(opening_policy: YamoOpeningPolicy) -> Self {
                Self::regeneration_unblocked_with_routing(opening_policy, 0)
            }
            pub fn regeneration_unblocked_with_routing(
                opening_policy: YamoOpeningPolicy,
                opponent_eta_penalty: i32,
            ) -> Self {
                Self::regeneration_unblocked_with_strategy(opening_policy, opponent_eta_penalty, 0)
            }
            pub fn regeneration_unblocked_with_strategy(
                opening_policy: YamoOpeningPolicy,
                opponent_eta_penalty: i32,
                tree_target_bonus: i32,
            ) -> Self {
                let mut bot = Self::with_opening_policy(opening_policy);
                bot.announcement = "yamo-regen-unblocked-custom-rust";
                bot.idle_regeneration = true;
                bot.persistent_regeneration = true;
                bot.door_unblocking = true;
                bot.opponent_eta_penalty = opponent_eta_penalty.max(0);
                bot.tree_target_bonus = tree_target_bonus.max(0);
                bot
            }
            pub fn tuned_carry_regeneration_chop2() -> Self {
                let mut bot =
                    Self::regeneration_unblocked_with_policy(YamoOpeningPolicy::TUNED_CARRY_CHOP2);
                bot.announcement = "yamo-carry-regen-chop2-rust";
                bot
            }
            pub fn tuned_carry_regeneration_scarce() -> Self {
                let mut bot = Self::tuned_carry_regeneration_unblocked();
                bot.announcement = "yamo-carry-regen-scarce-rust";
                bot.scarce_farming = true;
                bot
            }
            pub fn tuned_carry_regeneration_committed() -> Self {
                let mut bot = Self::with_opening_policy(YamoOpeningPolicy::TUNED_CARRY);
                bot.announcement = "yamo-carry-regen-committed-rust";
                bot.idle_regeneration = true;
                bot.persistent_regeneration = true;
                bot
            }
            pub fn planned_second_troll(view: &GameState, policy: YamoOpeningPolicy) -> Stats {
                Self::choose_second_troll(view, policy).stats
            }
            fn ensure_opening(&mut self, view: &GameState) {
                if self.initial_tree_count.is_none() {
                    self.initial_tree_count = Some(view.plants.len());
                    if self.scarce_farming && view.plants.len() <= 14 {
                        self.scarce_plan = view
                            .units
                            .iter()
                            .filter(|unit| unit.player == 0)
                            .min_by_key(|unit| unit.id)
                            .map(|unit| ScarcePlan {
                                farmer_id: unit.id,
                                intent: ScarceIntent::NeedSeed,
                                crop: None,
                            });
                    }
                }
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
                    (cost[PLUM] - view.inventories[0][PLUM]).max(0),
                ) + Self::collection_eta(
                    view,
                    LEMON,
                    (cost[LEMON] - view.inventories[0][LEMON]).max(0),
                );
                if !view.iron.is_empty() {
                    estimated_eta += Self::collection_eta(
                        view,
                        IRON,
                        (cost[IRON] - view.inventories[0][IRON]).max(0),
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
                policy: YamoOpeningPolicy,
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
                        Target::Bank(cell) if cell != unit.cell => {
                            !view.units.iter().any(|other| {
                                other.player == unit.player
                                    && other.id != unit.id
                                    && other.cell == cell
                            })
                        }
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
                let regeneration = self
                    .regeneration_commitments
                    .get(&unit.id)
                    .is_some_and(|kind| unit.carry[kind.item_index()] > 0);
                let scarce = self.scarce_plan.is_some_and(|plan| {
                    if plan.farmer_id != unit.id {
                        return false;
                    }
                    let kind = match plan.intent {
                        ScarceIntent::PlantMother { kind, .. }
                        | ScarceIntent::PlantCrop { kind, .. } => Some(kind),
                        _ => None,
                    };
                    kind.is_some_and(|kind| unit.carry[kind.item_index()] > 0)
                });
                regeneration || scarce
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
                    if let Some((landing, _)) = candidates.get(&blocker.id).and_then(|options| {
                        Self::planned_egress(view, blocker, options, &forbidden)
                    }) {
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
                        .and_then(|options| {
                            Self::planned_egress(view, blocker, options, &forbidden)
                        })
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
            fn scarce_kind_priority(kind: PlantKind) -> i32 {
                match kind {
                    PlantKind::Banana => 0,
                    PlantKind::Plum | PlantKind::Lemon => 4,
                    PlantKind::Apple => 8,
                }
            }
            fn scarce_inventory_kind(view: &GameState) -> Option<PlantKind> {
                [
                    PlantKind::Banana,
                    PlantKind::Plum,
                    PlantKind::Lemon,
                    PlantKind::Apple,
                ]
                .into_iter()
                .find(|kind| view.inventories[0][kind.item_index()] > 0)
            }
            fn scarce_carried_kind(unit: &Unit) -> Option<PlantKind> {
                [
                    PlantKind::Banana,
                    PlantKind::Plum,
                    PlantKind::Lemon,
                    PlantKind::Apple,
                ]
                .into_iter()
                .find(|kind| unit.carry[kind.item_index()] > 0)
            }
            fn scarce_seed_source(view: &GameState, unit: &Unit) -> Option<(Cell, PlantKind)> {
                let distance = bfs_distances(&view.walkable, &[unit.cell]);
                view.plants
                    .iter()
                    .filter(|plant| {
                        plant.health > 0 && plant.fruits > 0 && distance.contains_key(&plant.cell)
                    })
                    .min_by_key(|plant| {
                        let travel =
                            MoisanBot::ceil_div(distance[&plant.cell], unit.stats.movement_speed);
                        let wait = (MoisanBot::ticks_until_fruit(view, plant) - travel).max(0);
                        (
                            travel + wait + Self::scarce_kind_priority(plant.kind),
                            travel,
                            plant.cell,
                        )
                    })
                    .map(|plant| (plant.cell, plant.kind))
            }
            fn scarce_plant_cell(
                view: &GameState,
                unit: &Unit,
                excluded: &BTreeSet<Cell>,
                mother: bool,
            ) -> Option<Cell> {
                let doors: BTreeSet<Cell> = ortho_neighbors(view.shacks[0])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .collect();
                let from_shack =
                    bfs_distances(&view.walkable, &doors.iter().copied().collect::<Vec<_>>());
                let from_unit = bfs_distances(&view.walkable, &[unit.cell]);
                view.walkable
                    .iter()
                    .filter(|cell| !doors.contains(cell) && !excluded.contains(cell))
                    .filter(|cell| view.plant_at(**cell).is_none() && from_unit.contains_key(*cell))
                    .filter(|cell| from_shack.contains_key(*cell))
                    .min_by_key(|cell| {
                        let near_water = view.water.iter().any(|water| is_adjacent(*water, **cell));
                        let exits = ortho_neighbors(**cell)
                            .into_iter()
                            .filter(|neighbor| view.walkable.contains(neighbor))
                            .count() as i32;
                        let shack_distance = from_shack.get(*cell).copied().unwrap_or(10_000);
                        let travel = from_unit.get(*cell).copied().unwrap_or(10_000);
                        if mother {
                            (
                                shack_distance > 2,
                                !near_water,
                                shack_distance,
                                -exits,
                                travel,
                                **cell,
                            )
                        } else {
                            (
                                shack_distance > 2,
                                false,
                                shack_distance,
                                -exits,
                                travel,
                                **cell,
                            )
                        }
                    })
                    .copied()
            }
            fn scarce_tree_exists(view: &GameState, cell: Cell, kind: PlantKind) -> bool {
                view.plant_at(cell)
                    .map(|index| {
                        let plant = &view.plants[index];
                        plant.health > 0 && plant.kind == kind
                    })
                    .unwrap_or(false)
            }
            fn reconcile_scarce_plan(&mut self, view: &GameState) {
                let Some(mut plan) = self.scarce_plan else {
                    return;
                };
                let Some(farmer) = view.unit(plan.farmer_id) else {
                    self.scarce_plan = None;
                    return;
                };
                if plan.crop.is_some_and(|crop| view.plant_at(crop).is_none()) {
                    plan.crop = None;
                }
                plan.intent = match plan.intent {
                    ScarceIntent::NeedSeed => {
                        if let Some(kind) = Self::scarce_carried_kind(farmer) {
                            let target =
                                Self::scarce_plant_cell(view, farmer, &BTreeSet::new(), true);
                            target.map_or(ScarceIntent::NeedSeed, |target| {
                                ScarceIntent::PlantMother { target, kind }
                            })
                        } else if Self::scarce_inventory_kind(view).is_some() {
                            ScarceIntent::NeedSeed
                        } else if let Some((source, kind)) = Self::scarce_seed_source(view, farmer)
                        {
                            ScarceIntent::HarvestSeed { source, kind }
                        } else {
                            ScarceIntent::NeedSeed
                        }
                    }
                    ScarceIntent::HarvestSeed { source, kind } => {
                        if farmer.carry[kind.item_index()] > 0 {
                            Self::scarce_plant_cell(view, farmer, &BTreeSet::from([source]), true)
                                .map_or(ScarceIntent::NeedSeed, |target| {
                                    ScarceIntent::PlantMother { target, kind }
                                })
                        } else if Self::scarce_tree_exists(view, source, kind) {
                            ScarceIntent::HarvestSeed { source, kind }
                        } else {
                            ScarceIntent::NeedSeed
                        }
                    }
                    ScarceIntent::PlantMother { mut target, kind } => {
                        if Self::scarce_tree_exists(view, target, kind)
                            && farmer.carry[kind.item_index()] == 0
                        {
                            ScarceIntent::TendMother {
                                mother: target,
                                kind,
                            }
                        } else if farmer.carry[kind.item_index()] == 0 {
                            ScarceIntent::NeedSeed
                        } else {
                            let occupied = view
                                .plant_at(target)
                                .is_some_and(|index| view.plants[index].kind != kind);
                            if occupied || !view.walkable.contains(&target) {
                                if let Some(replacement) =
                                    Self::scarce_plant_cell(view, farmer, &BTreeSet::new(), true)
                                {
                                    target = replacement;
                                }
                            }
                            ScarceIntent::PlantMother { target, kind }
                        }
                    }
                    ScarceIntent::TendMother { mother, kind } => {
                        if !Self::scarce_tree_exists(view, mother, kind) {
                            if let Some(carried) = Self::scarce_carried_kind(farmer) {
                                Self::scarce_plant_cell(view, farmer, &BTreeSet::new(), true)
                                    .map_or(ScarceIntent::NeedSeed, |target| {
                                        ScarceIntent::PlantMother {
                                            target,
                                            kind: carried,
                                        }
                                    })
                            } else {
                                ScarceIntent::NeedSeed
                            }
                        } else if farmer.carry[kind.item_index()] > 0 {
                            let excluded = BTreeSet::from([mother]);
                            Self::scarce_plant_cell(view, farmer, &excluded, false).map_or(
                                ScarceIntent::TendMother { mother, kind },
                                |target| ScarceIntent::PlantCrop {
                                    mother,
                                    target,
                                    kind,
                                },
                            )
                        } else {
                            ScarceIntent::TendMother { mother, kind }
                        }
                    }
                    ScarceIntent::PlantCrop {
                        mother,
                        mut target,
                        kind,
                    } => {
                        if !Self::scarce_tree_exists(view, mother, kind) {
                            if farmer.carry[kind.item_index()] > 0 {
                                Self::scarce_plant_cell(view, farmer, &BTreeSet::new(), true)
                                    .map_or(ScarceIntent::NeedSeed, |target| {
                                        ScarceIntent::PlantMother { target, kind }
                                    })
                            } else {
                                ScarceIntent::NeedSeed
                            }
                        } else if farmer.carry[kind.item_index()] == 0 {
                            if Self::scarce_tree_exists(view, target, kind) {
                                plan.crop = Some(target);
                            }
                            ScarceIntent::TendMother { mother, kind }
                        } else {
                            let occupied = view.plant_at(target).is_some();
                            if occupied || !view.walkable.contains(&target) {
                                if let Some(replacement) = Self::scarce_plant_cell(
                                    view,
                                    farmer,
                                    &BTreeSet::from([mother]),
                                    false,
                                ) {
                                    target = replacement;
                                }
                            }
                            ScarceIntent::PlantCrop {
                                mother,
                                target,
                                kind,
                            }
                        }
                    }
                };
                self.scarce_plan = Some(plan);
            }
            fn scarce_protected_tree(&self) -> Option<Cell> {
                self.scarce_plan.and_then(|plan| match plan.intent {
                    ScarceIntent::HarvestSeed { source, .. } => Some(source),
                    ScarceIntent::TendMother { mother, .. }
                    | ScarceIntent::PlantCrop { mother, .. } => Some(mother),
                    _ => None,
                })
            }
            fn scarce_crop(&self) -> Option<Cell> {
                self.scarce_plan.and_then(|plan| plan.crop)
            }
            fn scarce_planting_farmer(&self, view: &GameState) -> Option<i32> {
                let plan = self.scarce_plan?;
                let kind = match plan.intent {
                    ScarceIntent::PlantMother { kind, .. }
                    | ScarceIntent::PlantCrop { kind, .. } => kind,
                    _ => return None,
                };
                view.unit(plan.farmer_id)
                    .is_some_and(|unit| unit.carry[kind.item_index()] > 0)
                    .then_some(plan.farmer_id)
            }
            fn reconcile_regeneration_commitments(&mut self, view: &GameState) {
                if self.fresh_harvest_regeneration {
                    let completed: Vec<_> = self
                        .fresh_harvest_pending_plants
                        .iter()
                        .filter(|(_, (turn, _, _))| *turn < view.turn)
                        .map(|(id, (_, cell, kind))| {
                            let success = view.plant_at(*cell).is_some_and(|index| {
                                let plant = &view.plants[index];
                                plant.health > 0 && plant.kind == *kind
                            });
                            (*id, success)
                        })
                        .collect();
                    for (id, success) in completed {
                        self.fresh_harvest_pending_plants.remove(&id);
                        self.fresh_harvest_units.remove(&id);
                        if success {
                            self.fresh_harvest_successful_plants += 1;
                        }
                    }
                }
                if !self.persistent_regeneration {
                    self.regeneration_commitments.clear();
                    self.fresh_harvest_units.clear();
                    self.fresh_harvest_pending_plants.clear();
                    return;
                }
                self.regeneration_commitments.retain(|id, kind| {
                    let Some(unit) = view.unit(*id) else {
                        return false;
                    };
                    unit.carry[kind.item_index()] > 0
                        || unit.carry[super::super::game::types::WOOD] > 0
                        || view
                            .plant_at(unit.cell)
                            .map(|index| {
                                let plant = &view.plants[index];
                                plant.kind == *kind && plant.health > 0
                            })
                            .unwrap_or(false)
                });
                if self.fresh_harvest_regeneration {
                    self.fresh_harvest_units.retain(|id| {
                        self.regeneration_commitments.contains_key(id)
                            || self.fresh_harvest_pending_plants.contains_key(id)
                    });
                }
            }
            fn reconcile_tree_commitments(&mut self, view: &GameState) {
                if self.tree_target_bonus <= 0 {
                    self.tree_commitments.clear();
                    return;
                }
                self.tree_commitments.retain(|id, cell| {
                    let Some(unit) = view.unit(*id) else {
                        return false;
                    };
                    unit.player == 0
                        && unit.stats.chop_power > 0
                        && unit.total_carried() == 0
                        && unit.free_capacity() > 0
                        && view
                            .plant_at(*cell)
                            .is_some_and(|index| view.plants[index].health > 0)
                        && bfs_distances(&view.walkable, &[unit.cell]).contains_key(cell)
                });
            }
            fn reconcile_opponent_crops(&mut self, view: &GameState) {
                let current: BTreeSet<Cell> = view
                    .plants
                    .iter()
                    .filter(|plant| plant.health > 0)
                    .map(|plant| plant.cell)
                    .collect();
                if self.plant_history_initialized {
                    for cell in current.difference(&self.previous_plants) {
                        if !self.own_plant_attempts.contains(cell)
                            && self.opponent_crops.insert(*cell)
                        {
                            self.opponent_crops_seen += 1;
                        }
                    }
                    self.opponent_crops.retain(|cell| current.contains(cell));
                } else {
                    self.plant_history_initialized = true;
                }
                self.opponent_crop_harvested
                    .retain(|cell| self.opponent_crops.contains(cell));
                self.previous_plants = current;
                self.own_plant_attempts.clear();
            }
            fn remember_own_plant_attempts(&mut self, view: &GameState, commands: &[String]) {
                for command in commands {
                    let fields: Vec<_> = command.split_whitespace().collect();
                    if fields.first() != Some(&"PLANT") {
                        continue;
                    }
                    let Some(unit) = fields
                        .get(1)
                        .and_then(|id| id.parse().ok())
                        .and_then(|id| view.unit(id))
                        .filter(|unit| unit.player == 0)
                    else {
                        continue;
                    };
                    self.own_plant_attempts.insert(unit.cell);
                }
            }
            fn crop_priority_active(&self, view: &GameState) -> bool {
                (self.opponent_crop_bonus > 0 || self.opponent_crop_dual_value)
                    && view.turn >= self.opponent_crop_start_turn
                    && self.opponent_crops_seen >= self.opponent_crop_min_seen
            }
            fn apply_opponent_crop_priority(
                &self,
                view: &GameState,
                unit: &Unit,
                candidates: &mut [Candidate],
            ) {
                if !self.crop_priority_active(view) {
                    return;
                }
                let distance = bfs_distances(&view.walkable, &[unit.cell]);
                for candidate in candidates {
                    let Target::Tree(cell) = candidate.target else {
                        continue;
                    };
                    if !self.opponent_crops.contains(&cell) {
                        continue;
                    }
                    let Some(cells) = distance.get(&cell) else {
                        continue;
                    };
                    let eta = MoisanBot::ceil_div(*cells, unit.stats.movement_speed);
                    if eta <= self.opponent_crop_eta_limit {
                        if self.opponent_crop_dual_value {
                            // The ordinary score estimates our wood-conversion value per
                            // action.  Capturing an opponent-created crop also removes the
                            // same conversion opportunity from the opponent, so count that
                            // value once more without a fitted flat bonus.
                            candidate.score += candidate.score;
                        } else {
                            candidate.score += self.opponent_crop_bonus as f64;
                        }
                    }
                }
            }
            fn apply_opponent_crop_harvest_contact(
                &mut self,
                view: &GameState,
                commands: &mut [String],
            ) {
                if !self.opponent_crop_harvest_contact || !self.crop_priority_active(view) {
                    return;
                }
                for command in commands {
                    let unit_id = {
                        let fields: Vec<_> = command.split_whitespace().collect();
                        if fields.first() != Some(&"CHOP") {
                            continue;
                        }
                        let Some(unit_id) = fields.get(1).and_then(|value| value.parse().ok())
                        else {
                            continue;
                        };
                        unit_id
                    };
                    let Some(unit) = view
                        .unit(unit_id)
                        .filter(|unit| unit.player == 0)
                        .filter(|unit| unit.total_carried() == 0)
                        .filter(|unit| unit.stats.harvest_power > 0)
                    else {
                        continue;
                    };
                    let cell = unit.cell;
                    if !self.opponent_crops.contains(&cell)
                        || self.opponent_crop_harvested.contains(&cell)
                    {
                        continue;
                    }
                    let ripe = view.plant_at(cell).is_some_and(|index| {
                        let plant = &view.plants[index];
                        plant.health > 0 && plant.fruits > 0
                    });
                    if !ripe {
                        continue;
                    }
                    *command = format!("HARVEST {}", unit_id);
                    self.opponent_crop_harvested.insert(cell);
                    self.opponent_crop_harvest_rewrites += 1;
                }
            }
            fn tree_targets_by_command(
                candidates: &BTreeMap<i32, Vec<Candidate>>,
            ) -> BTreeMap<String, Cell> {
                candidates
                    .values()
                    .flatten()
                    .filter_map(|candidate| match candidate.target {
                        Target::Tree(cell) => Some((candidate.command.clone(), cell)),
                        _ => None,
                    })
                    .collect()
            }
            fn remember_selected_tree_targets(
                &mut self,
                view: &GameState,
                commands: &[String],
                tree_targets: &BTreeMap<String, Cell>,
            ) {
                if self.tree_target_bonus <= 0
                    || view.units.iter().filter(|unit| unit.player == 0).count() < 2
                {
                    return;
                }
                for command in commands {
                    let Some(&cell) = tree_targets.get(command) else {
                        continue;
                    };
                    let Some(id) = command
                        .split_whitespace()
                        .nth(1)
                        .and_then(|id| id.parse().ok())
                    else {
                        continue;
                    };
                    self.tree_commitments.insert(id, cell);
                }
            }
            fn remember_selected_regeneration(&mut self, view: &GameState, commands: &[String]) {
                if !self.persistent_regeneration {
                    return;
                }
                for command in commands {
                    let fields: Vec<&str> = command.split_whitespace().collect();
                    match fields.as_slice() {
                        [verb, id, kind] if verb.eq_ignore_ascii_case("PICK") => {
                            let (Ok(id), Some(kind)) = (id.parse(), PlantKind::parse(kind)) else {
                                continue;
                            };
                            self.regeneration_commitments.insert(id, kind);
                        }
                        [verb, id, kind]
                            if self.fresh_harvest_regeneration
                                && verb.eq_ignore_ascii_case("PLANT") =>
                        {
                            let (Ok(id), Some(kind)) = (id.parse(), PlantKind::parse(kind)) else {
                                continue;
                            };
                            if self.fresh_harvest_units.contains(&id)
                                && self.regeneration_commitments.get(&id) == Some(&kind)
                            {
                                let Some(unit) = view.unit(id).filter(|unit| unit.player == 0)
                                else {
                                    continue;
                                };
                                self.fresh_harvest_pending_plants
                                    .insert(id, (view.turn, unit.cell, kind));
                            }
                        }
                        [verb, id]
                            if self.fresh_harvest_regeneration
                                && verb.eq_ignore_ascii_case("HARVEST") =>
                        {
                            let Ok(id) = id.parse() else {
                                continue;
                            };
                            let Some(unit) = view
                                .unit(id)
                                .filter(|unit| unit.player == 0)
                                .filter(|unit| unit.stats.harvest_power > 0)
                                .filter(|unit| unit.free_capacity() > 0)
                            else {
                                continue;
                            };
                            if self.external_protected_tree == Some(unit.cell) {
                                continue;
                            }
                            let Some(kind) = view.plant_at(unit.cell).and_then(|index| {
                                let plant = &view.plants[index];
                                (plant.health > 0 && plant.fruits > 0).then_some(plant.kind)
                            }) else {
                                continue;
                            };
                            self.regeneration_commitments.insert(id, kind);
                            if self.fresh_harvest_units.insert(id) {
                                self.fresh_harvest_commitments += 1;
                                self.fresh_harvest_first_turn.get_or_insert(view.turn);
                            }
                        }
                        _ => {}
                    }
                }
            }
            fn yamo_chop_candidates(
                view: &GameState,
                unit: &Unit,
                type_to_cut: Option<PlantKind>,
                protected_tree: Option<Cell>,
                opponent_eta_penalty: i32,
            ) -> Vec<Candidate> {
                let mut candidates = MoisanBot::chop_candidates(view, unit, type_to_cut);
                if let Some(protected) = protected_tree {
                    candidates.retain(|candidate| candidate.target != Target::Tree(protected));
                }
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
            fn scarce_pick_candidates(
                view: &GameState,
                unit: &Unit,
                kind: PlantKind,
            ) -> Vec<Candidate> {
                if is_adjacent(unit.cell, view.shacks[0]) {
                    return vec![Candidate {
                        command: format!("PICK {} {}", unit.id, kind.as_str()),
                        score: 12_000.0,
                        target: Target::Cell(unit.cell),
                    }];
                }
                let distance = bfs_distances(&view.walkable, &[unit.cell]);
                ortho_neighbors(view.shacks[0])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell) && distance.contains_key(cell))
                    .map(|cell| Candidate {
                        command: format!("MOVE {} {} {}", unit.id, cell.0, cell.1),
                        score: 11_000.0 - distance[&cell] as f64,
                        target: Target::Cell(cell),
                    })
                    .collect()
            }
            fn scarce_farmer_candidates(
                &self,
                view: &GameState,
                unit: &Unit,
                type_to_cut: Option<PlantKind>,
            ) -> Vec<Candidate> {
                let Some(plan) = self.scarce_plan.filter(|plan| plan.farmer_id == unit.id) else {
                    return Self::main_candidates(
                        view,
                        unit,
                        type_to_cut,
                        false,
                        self.persistent_regeneration,
                        None,
                        self.opponent_eta_penalty,
                    );
                };
                let protected = self.scarce_protected_tree();
                let expected_kind = match plan.intent {
                    ScarceIntent::PlantMother { kind, .. }
                    | ScarceIntent::PlantCrop { kind, .. } => Some(kind),
                    _ => None,
                };
                if unit.total_carried() > 0
                    && !expected_kind.is_some_and(|kind| unit.carry[kind.item_index()] > 0)
                {
                    let mut out = vec![MoisanBot::wait()];
                    out.extend(Self::bank_candidates(view, unit));
                    return out;
                }
                let action = match plan.intent {
                    ScarceIntent::NeedSeed => Self::scarce_inventory_kind(view)
                        .filter(|_| {
                            Self::scarce_plant_cell(view, unit, &BTreeSet::new(), true).is_some()
                        })
                        .map(|kind| Self::scarce_pick_candidates(view, unit, kind))
                        .unwrap_or_default(),
                    ScarceIntent::HarvestSeed { source, .. } => {
                        let ready = view
                            .plant_at(source)
                            .is_some_and(|index| view.plants[index].fruits > 0);
                        if unit.cell == source && ready {
                            vec![Candidate {
                                command: format!("HARVEST {}", unit.id),
                                score: 12_000.0,
                                target: Target::Tree(source),
                            }]
                        } else if unit.cell != source {
                            vec![Candidate {
                                command: format!("MOVE {} {} {}", unit.id, source.0, source.1),
                                score: 11_500.0,
                                target: Target::Tree(source),
                            }]
                        } else {
                            vec![MoisanBot::wait()]
                        }
                    }
                    ScarceIntent::PlantMother { target, kind } => vec![Candidate {
                        command: if unit.cell == target {
                            format!("PLANT {} {}", unit.id, kind.as_str())
                        } else {
                            format!("MOVE {} {} {}", unit.id, target.0, target.1)
                        },
                        score: 12_000.0,
                        target: Target::Cell(target),
                    }],
                    ScarceIntent::TendMother { mother, .. } => {
                        if plan.crop.is_some() {
                            return Vec::new();
                        }
                        if !Self::yamo_chop_candidates(
                            view,
                            unit,
                            type_to_cut,
                            Some(mother),
                            self.opponent_eta_penalty,
                        )
                        .is_empty()
                        {
                            return Vec::new();
                        }
                        let Some(index) = view.plant_at(mother) else {
                            return vec![MoisanBot::wait()];
                        };
                        let plant = &view.plants[index];
                        let distance = bfs_distances(&view.walkable, &[unit.cell]);
                        let travel = distance
                            .get(&mother)
                            .copied()
                            .map(|distance| {
                                MoisanBot::ceil_div(distance, unit.stats.movement_speed)
                            })
                            .unwrap_or(10_000);
                        if plant.fruits > 0 && unit.cell == mother {
                            vec![Candidate {
                                command: format!("HARVEST {}", unit.id),
                                score: 12_000.0,
                                target: Target::Tree(mother),
                            }]
                        } else if plant.fruits > 0
                            || MoisanBot::ticks_until_fruit(view, plant) <= travel + 1
                        {
                            if unit.cell == mother {
                                vec![MoisanBot::wait()]
                            } else {
                                vec![Candidate {
                                    command: format!("MOVE {} {} {}", unit.id, mother.0, mother.1),
                                    score: 11_000.0,
                                    target: Target::Tree(mother),
                                }]
                            }
                        } else {
                            Vec::new()
                        }
                    }
                    ScarceIntent::PlantCrop { target, kind, .. } => vec![Candidate {
                        command: if unit.cell == target {
                            format!("PLANT {} {}", unit.id, kind.as_str())
                        } else {
                            format!("MOVE {} {} {}", unit.id, target.0, target.1)
                        },
                        score: 12_000.0,
                        target: Target::Cell(target),
                    }],
                };
                if !action.is_empty() {
                    return action;
                }
                let mut out = vec![MoisanBot::wait()];
                let chops = Self::yamo_chop_candidates(
                    view,
                    unit,
                    type_to_cut,
                    protected,
                    self.opponent_eta_penalty,
                );
                if unit.total_carried() > 0 || chops.is_empty() && unit.total_carried() > 0 {
                    out.extend(Self::bank_candidates(view, unit));
                } else {
                    out.extend(chops);
                }
                out
            }
            fn main_candidates(
                view: &GameState,
                unit: &Unit,
                type_to_cut: Option<PlantKind>,
                idle_regeneration: bool,
                safe_regeneration: bool,
                protected_tree: Option<Cell>,
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
                            score: 7_500.0 - priority as f64,
                            target: Target::Cell(unit.cell),
                        });
                    }
                }
                if unit.free_capacity() <= 0 {
                    out.extend(Self::bank_candidates(view, unit));
                    return out;
                }
                let chops = Self::yamo_chop_candidates(
                    view,
                    unit,
                    type_to_cut,
                    protected_tree,
                    opponent_eta_penalty,
                );
                if idle_regeneration && chops.is_empty() {
                    return Self::endgame_candidates(
                        view,
                        unit,
                        type_to_cut,
                        safe_regeneration,
                        protected_tree,
                        opponent_eta_penalty,
                    );
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
                chop: i32,
            ) -> i32 {
                if chop <= 0 {
                    return 10_000;
                }
                let near_water = view.water.iter().any(|water| is_adjacent(*water, cell));
                let cooldown_reset = effective_cooldown(kind, near_water);
                let (_, growth_health) = super::super::game::rules::tree_health_params(kind);
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
                protected_tree: Option<Cell>,
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
                            .map(|distance| {
                                MoisanBot::ceil_div(distance, unit.stats.movement_speed) + 1
                            })
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
                let chops = Self::yamo_chop_candidates(
                    view,
                    unit,
                    type_to_cut,
                    protected_tree,
                    opponent_eta_penalty,
                );
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
                                unit.stats.chop_power,
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
            fn idle_harvest_candidates(
                view: &GameState,
                unit: &Unit,
                protected_tree: Option<Cell>,
            ) -> Vec<Candidate> {
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
                            && Some(plant.cell) != protected_tree
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
            fn external_orchard_candidate(
                view: &GameState,
                unit: &Unit,
                mother: Cell,
            ) -> Option<Candidate> {
                if unit.total_carried() != 0
                    || unit.stats.harvest_power <= 0
                    || unit.free_capacity() <= 0
                    || !is_adjacent(mother, view.shacks[0])
                {
                    return None;
                }
                let plant = view
                    .plant_at(mother)
                    .map(|index| &view.plants[index])
                    .filter(|plant| {
                        plant.kind == PlantKind::Apple && plant.health > 0 && plant.fruits > 0
                    })?;
                let distance = bfs_distances(&view.walkable, &[unit.cell]);
                let travel =
                    MoisanBot::ceil_div(distance.get(&mother).copied()?, unit.stats.movement_speed);
                let bankable = plant
                    .fruits
                    .min(unit.stats.harvest_power)
                    .min(unit.free_capacity());
                let trip = travel + 2;
                if bankable <= 0 || trip > TOTAL_TURNS - view.turn + 1 {
                    return None;
                }
                Some(Candidate {
                    command: if unit.cell == mother {
                        format!("HARVEST {}", unit.id)
                    } else {
                        format!("MOVE {} {} {}", unit.id, mother.0, mother.1)
                    },
                    score: 250.0 * bankable as f64 / trip as f64,
                    target: Target::Tree(mother),
                })
            }
            fn endgame(view: &GameState) -> bool {
                view.turn > 250
                    || (view.plants.len() <= 4
                        && score(&view.inventories[0]) < score(&view.inventories[1]))
            }
        }
        impl Bot for YamoBot {
            fn commands(&mut self, view: &GameState) -> Vec<String> {
                self.external_orchard_selected_this_turn = false;
                self.reconcile_opponent_crops(view);
                self.reconcile_regeneration_commitments(view);
                self.reconcile_tree_commitments(view);
                self.ensure_opening(view);
                self.reconcile_scarce_plan(view);
                self.enforce_training_deadline(view);
                let own_count = view.units.iter().filter(|unit| unit.player == 0).count();
                let max_level = |item: usize| {
                    let available = (view.inventories[0][item] - own_count as i32).max(0);
                    let mut level = 0;
                    while level < 3 && (level + 1) * (level + 1) <= available {
                        level += 1;
                    }
                    level.max(1)
                };
                let turn_one_override = self.first_worker_turn_one_override.filter(|stats| {
                    view.turn == 1 && own_count == 1 && MoisanBot::can_train(view, *stats)
                });
                let desired = if let Some(stats) = turn_one_override {
                    stats
                } else if self.first_worker_max_bank_hp0 && own_count == 1 {
                    Stats {
                        movement_speed: max_level(PLUM),
                        carry_capacity: max_level(LEMON),
                        harvest_power: 0,
                        chop_power: max_level(IRON),
                    }
                } else {
                    self.desired_second
                        .map(|objective| objective.stats)
                        .unwrap_or_else(Self::fallback_second_troll)
                };
                let train_now = !self.opening_abandoned && MoisanBot::can_train(view, desired);
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
                let scarce_farmer_id = (my_units.len() >= 2)
                    .then(|| {
                        if view.turn > 250 {
                            self.scarce_planting_farmer(view)
                        } else {
                            self.scarce_plan.map(|plan| plan.farmer_id)
                        }
                    })
                    .flatten();
                let protected_tree = self.external_protected_tree.or_else(|| {
                    scarce_farmer_id
                        .is_some()
                        .then(|| self.scarce_protected_tree())
                        .flatten()
                });
                let scarce_crop = scarce_farmer_id
                    .is_some()
                    .then(|| self.scarce_crop())
                    .flatten();
                let mut by_id = BTreeMap::new();
                for unit in my_units {
                    let committed_regeneration =
                        self.regeneration_commitments.contains_key(&unit.id);
                    let mut candidates = if scarce_farmer_id == Some(unit.id) {
                        self.scarce_farmer_candidates(view, unit, self.type_to_cut)
                    } else if committed_regeneration {
                        Self::endgame_candidates(
                            view,
                            unit,
                            self.type_to_cut,
                            self.persistent_regeneration,
                            protected_tree,
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
                            None,
                            self.opponent_eta_penalty,
                        )
                    } else if endgame {
                        Self::endgame_candidates(
                            view,
                            unit,
                            self.type_to_cut,
                            self.persistent_regeneration,
                            protected_tree,
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
                            protected_tree,
                            self.opponent_eta_penalty,
                        )
                    };
                    self.apply_opponent_crop_priority(view, unit, &mut candidates);
                    if scarce_farmer_id != Some(unit.id) {
                        for candidate in &mut candidates {
                            if scarce_crop
                                .is_some_and(|crop| candidate.target == Target::Tree(crop))
                            {
                                candidate.score += 15_000.0;
                            }
                        }
                    }
                    if let Some(target) = self.tree_commitments.get(&unit.id) {
                        for candidate in &mut candidates {
                            if candidate.target == Target::Tree(*target) {
                                candidate.score += self.tree_target_bonus as f64;
                            }
                        }
                    }
                    if endgame
                        && self.idle_harvest
                        && (!self.idle_harvest_clock_only || view.turn > 250)
                        && !self.scarce_farming
                        && candidates
                            .iter()
                            .all(|candidate| candidate.target == Target::None)
                    {
                        candidates.extend(Self::idle_harvest_candidates(
                            view,
                            unit,
                            protected_tree,
                        ));
                    }
                    if self.persistent_regeneration && train_now {
                        candidates.retain(|candidate| !candidate.command.starts_with("PICK "));
                    }
                    if let Some(protected) = self.external_protected_tree {
                        candidates.retain(|candidate|{!matches!(candidate.target,Target::Tree(cell)|Target::Bank(cell)|Target::Cell(cell)if cell==protected)});
                    }
                    if let Some((starter_id, mother)) = self.external_orchard_task {
                        if starter_id == unit.id {
                            if let Some(candidate) =
                                Self::external_orchard_candidate(view, unit, mother)
                            {
                                self.external_orchard_offers += 1;
                                candidates.push(candidate);
                            }
                        }
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
                if self.door_unblocking {
                    self.force_unique_door_clear(view, &mut by_id);
                }
                if let Some(id) = self.external_idle_unit {
                    by_id.insert(id, vec![MoisanBot::wait()]);
                }
                let tree_targets = Self::tree_targets_by_command(&by_id);
                let mut selected = MoisanBot::select(by_id, &view.inventories[0]);
                if let Some((starter_id, mother)) = self.external_orchard_task {
                    if let Some(command) = selected.iter().find(|command| {
                        command
                            .split_whitespace()
                            .nth(1)
                            .and_then(|value| value.parse().ok())
                            == Some(starter_id)
                            && tree_targets.get(*command) == Some(&mother)
                    }) {
                        self.external_orchard_selected_this_turn = true;
                        self.external_orchard_selections += 1;
                        self.external_orchard_first_selected_turn
                            .get_or_insert(view.turn);
                        if command.starts_with("HARVEST ") {
                            self.external_orchard_harvest_selections += 1;
                        }
                    }
                }
                if self.crop_priority_active(view) {
                    for command in &selected {
                        if tree_targets
                            .get(command)
                            .is_some_and(|cell| self.opponent_crops.contains(cell))
                        {
                            self.opponent_crop_selected += 1;
                            self.opponent_crop_first_selected_turn
                                .get_or_insert(view.turn);
                        }
                    }
                }
                self.remember_selected_tree_targets(view, &selected, &tree_targets);
                MoisanBot::resolve_move_conflicts(view, &mut selected);
                self.remember_selected_regeneration(view, &selected);
                self.apply_opponent_crop_harvest_contact(view, &mut selected);
                self.remember_own_plant_attempts(view, &selected);
                if let Some(farmer_id) = scarce_farmer_id {
                    self.regeneration_commitments.remove(&farmer_id);
                }
                out.extend(selected);
                if out.is_empty() {
                    out.push("WAIT".to_string());
                }
                out
            }
        }
        #[derive(Clone, Copy, Debug, Eq, PartialEq)]
        enum OrchardPhase {
            Dormant,
            CarryingSeed,
            Active,
            Abandoned,
        }
        #[derive(Clone, Debug)]
        struct OrchardGeometry {
            mother: Cell,
            enemy_door_distance: i32,
            doors: Vec<Cell>,
            alternate_doors: Vec<Cell>,
        }
        #[derive(Clone, Copy, Debug, Eq, PartialEq)]
        struct OrchardCycle {
            first_chop_eta: i32,
            cycle_eta: i32,
        }
        #[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
        pub struct TaskMarketOrchardTelemetry {
            pub activation_turn: Option<i32>,
            pub seed_repaid_turn: Option<i32>,
            pub market_turns: usize,
            pub offers: usize,
            pub selections: usize,
            pub harvest_selections: usize,
            pub first_selection_turn: Option<i32>,
            pub forced_setup_actions: usize,
        }
        #[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
        pub struct FreshHarvestRegenerationTelemetry {
            pub commitments: usize,
            pub first_commitment_turn: Option<i32>,
            pub successful_plants: usize,
        }
        #[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
        pub struct BananaSeedFactoryTelemetry {
            pub active: bool,
            pub activation_turn: Option<i32>,
            pub selector_decided: bool,
            pub selector_selected: bool,
            pub initial_budget: i32,
            pub bootstrap_attempts: usize,
            pub bootstrap_successes: usize,
            pub reserve: Option<Cell>,
            pub reserve_promotions: usize,
            pub reserve_losses: usize,
            pub own_crop_harvest_selections: usize,
            pub own_crop_harvest_successes: usize,
            pub bank_source_harvest_selections: usize,
            pub bank_source_harvest_successes: usize,
            pub conversion_source_harvest_selections: usize,
            pub conversion_source_harvest_successes: usize,
            pub opponent_crops_seen: usize,
            pub opponent_crop_policy_selections: usize,
            pub trained_opponent_crop_selections: usize,
            pub renewable_plant_attempts: usize,
            pub renewable_plant_successes: usize,
            pub trained_role_rewrites: usize,
            pub trained_forbidden_commands: usize,
            pub tracked_live_crops: usize,
            pub worker_three_bridge_funding_turns: usize,
            pub worker_three_bridge_fruit_harvest_selections: [usize; 3],
            pub worker_three_bridge_fruit_harvest_successes: [usize; 3],
            pub worker_three_bridge_iron_mine_selections: usize,
            pub worker_three_bridge_iron_mine_successes: usize,
            pub worker_three_bridge_train_attempts: usize,
            pub worker_three_bridge_train_successes: usize,
            pub worker_three_bridge_trained_turn: Option<i32>,
            pub worker_three_bridge_forbidden_commands: usize,
            pub worker_three_bridge_post_training_commands: usize,
        }
        #[derive(Clone, Copy, Debug, Eq, PartialEq)]
        enum BananaFactoryPlantSource {
            BankBootstrap,
            RenewableHarvest,
        }
        #[derive(Clone)]
        pub struct SecureOrchardBot {
            inner: YamoBot,
            initialized: bool,
            starter_id: Option<i32>,
            geometry: Option<OrchardGeometry>,
            initial_natural: BTreeMap<Cell, PlantKind>,
            phase: OrchardPhase,
            plant_attempted: bool,
            minimum_enemy_eta: i32,
            require_idle_starter: bool,
            minimum_enemy_door_distance: i32,
            minimum_worker_speed: i32,
            task_market_enabled: bool,
            task_market_seed_repaid: bool,
            task_market_activation_turn: Option<i32>,
            task_market_seed_repaid_turn: Option<i32>,
            task_market_turns: usize,
            task_market_forced_setup_actions: usize,
            banana_factory_enabled: bool,
            banana_factory_ring: bool,
            banana_ring_cells_cache: std::cell::OnceCell<Vec<Cell>>,
            banana_ring_home_distances_cache: std::cell::OnceCell<BTreeMap<Cell, i32>>,
            banana_factory_source_separated: bool,
            banana_factory_selector_enabled: bool,
            banana_factory_selector_decided: bool,
            banana_factory_selector_selected: bool,
            banana_factory_trained_dual_value_e6: bool,
            banana_factory_active: bool,
            banana_factory_activation_turn: Option<i32>,
            banana_factory_initial_budget: Option<i32>,
            banana_factory_bootstrap_attempts: usize,
            banana_factory_bootstrap_successes: usize,
            banana_factory_owned_crops: BTreeMap<Cell, bool>,
            banana_factory_reserve: Option<Cell>,
            banana_factory_reserve_promotions: usize,
            banana_factory_reserve_losses: usize,
            banana_factory_plant_target: Option<Cell>,
            banana_factory_pending_plant: Option<(i32, Cell, BananaFactoryPlantSource, i32)>,
            banana_factory_pending_harvest: Option<(i32, i32, bool)>,
            banana_factory_seed_from_harvest: bool,
            banana_factory_harvest_selections: usize,
            banana_factory_harvest_successes: usize,
            banana_factory_bank_harvest_selections: usize,
            banana_factory_bank_harvest_successes: usize,
            banana_factory_conversion_harvest_selections: usize,
            banana_factory_conversion_harvest_successes: usize,
            banana_factory_renewable_plant_attempts: usize,
            banana_factory_renewable_plant_successes: usize,
            banana_factory_trained_role_rewrites: usize,
            banana_factory_trained_forbidden_commands: usize,
            banana_factory_trained_opponent_crop_selections: usize,
            banana_factory_worker_three_bridge: bool,
            banana_factory_worker_three_bridge_funding_turns: usize,
            banana_factory_worker_three_bridge_pending_harvest: Option<(i32, i32, usize, i32)>,
            banana_factory_worker_three_bridge_fruit_harvest_selections: [usize; 3],
            banana_factory_worker_three_bridge_fruit_harvest_successes: [usize; 3],
            banana_factory_worker_three_bridge_pending_mine: Option<(i32, i32, i32)>,
            banana_factory_worker_three_bridge_iron_mine_selections: usize,
            banana_factory_worker_three_bridge_iron_mine_successes: usize,
            banana_factory_worker_three_bridge_pending_train: Option<(i32, usize)>,
            banana_factory_worker_three_bridge_train_attempts: usize,
            banana_factory_worker_three_bridge_train_successes: usize,
            banana_factory_worker_three_bridge_trained_turn: Option<i32>,
            banana_factory_worker_three_bridge_forbidden_commands: usize,
            banana_factory_worker_three_bridge_post_training_commands: usize,
        }
        impl Default for SecureOrchardBot {
            fn default() -> Self {
                Self::new()
            }
        }
        impl SecureOrchardBot {
            pub fn new() -> Self {
                Self::with_policy(
                    YamoBot::tuned_carry_regeneration_transit_idle_harvest(),
                    8,
                    false,
                    11,
                    1,
                )
            }
            pub fn task_market() -> Self {
                let mut bot = Self::new();
                bot.task_market_enabled = true;
                bot
            }
            pub fn fresh_harvest_regeneration() -> Self {
                let mut bot = Self::new();
                bot.inner.fresh_harvest_regeneration = true;
                bot
            }
            pub fn banana_seed_factory() -> Self {
                let mut bot = Self::new();
                bot.banana_factory_enabled = true;
                bot
            }
            pub fn banana_ring_opponent_crop_b100_e6() -> Self {
                let mut bot = Self::banana_seed_factory();
                bot.banana_factory_ring = true;
                bot.inner.opponent_crop_bonus = 100;
                bot.inner.opponent_crop_eta_limit = 6;
                bot.inner.opponent_crop_start_turn = 1;
                bot.inner.opponent_crop_min_seen = 1;
                bot
            }
            pub fn banana_seed_factory_source_separated() -> Self {
                let mut bot = Self::banana_seed_factory();
                bot.banana_factory_source_separated = true;
                bot
            }
            pub fn banana_seed_factory_activation_selector() -> Self {
                let mut bot = Self::banana_seed_factory();
                bot.banana_factory_selector_enabled = true;
                bot
            }
            pub fn banana_seed_factory_dual_value_e6() -> Self {
                let mut bot = Self::banana_seed_factory();
                bot.inner.opponent_crop_dual_value = true;
                bot.inner.opponent_crop_eta_limit = 6;
                bot.inner.opponent_crop_start_turn = 1;
                bot.inner.opponent_crop_min_seen = 1;
                bot
            }
            pub fn banana_seed_factory_trained_dual_value_e6() -> Self {
                let mut bot = Self::banana_seed_factory();
                bot.banana_factory_trained_dual_value_e6 = true;
                bot
            }
            pub fn banana_seed_factory_worker_three_bridge() -> Self {
                let mut bot = Self::banana_seed_factory();
                bot.banana_factory_worker_three_bridge = true;
                bot
            }
            pub fn fresh_harvest_regeneration_telemetry(
                &self,
            ) -> FreshHarvestRegenerationTelemetry {
                FreshHarvestRegenerationTelemetry {
                    commitments: self.inner.fresh_harvest_commitments,
                    first_commitment_turn: self.inner.fresh_harvest_first_turn,
                    successful_plants: self.inner.fresh_harvest_successful_plants,
                }
            }
            pub fn banana_seed_factory_telemetry(&self) -> BananaSeedFactoryTelemetry {
                BananaSeedFactoryTelemetry {
                    active: self.banana_factory_active,
                    activation_turn: self.banana_factory_activation_turn,
                    selector_decided: self.banana_factory_selector_decided,
                    selector_selected: self.banana_factory_selector_selected,
                    initial_budget: self.banana_factory_initial_budget.unwrap_or(0),
                    bootstrap_attempts: self.banana_factory_bootstrap_attempts,
                    bootstrap_successes: self.banana_factory_bootstrap_successes,
                    reserve: self.banana_factory_reserve,
                    reserve_promotions: self.banana_factory_reserve_promotions,
                    reserve_losses: self.banana_factory_reserve_losses,
                    own_crop_harvest_selections: self.banana_factory_harvest_selections,
                    own_crop_harvest_successes: self.banana_factory_harvest_successes,
                    bank_source_harvest_selections: self.banana_factory_bank_harvest_selections,
                    bank_source_harvest_successes: self.banana_factory_bank_harvest_successes,
                    conversion_source_harvest_selections: self
                        .banana_factory_conversion_harvest_selections,
                    conversion_source_harvest_successes: self
                        .banana_factory_conversion_harvest_successes,
                    opponent_crops_seen: self.inner.opponent_crops_seen,
                    opponent_crop_policy_selections: self.inner.opponent_crop_selected,
                    trained_opponent_crop_selections: self
                        .banana_factory_trained_opponent_crop_selections,
                    renewable_plant_attempts: self.banana_factory_renewable_plant_attempts,
                    renewable_plant_successes: self.banana_factory_renewable_plant_successes,
                    trained_role_rewrites: self.banana_factory_trained_role_rewrites,
                    trained_forbidden_commands: self.banana_factory_trained_forbidden_commands,
                    tracked_live_crops: self.banana_factory_owned_crops.len(),
                    worker_three_bridge_funding_turns: self
                        .banana_factory_worker_three_bridge_funding_turns,
                    worker_three_bridge_fruit_harvest_selections: self
                        .banana_factory_worker_three_bridge_fruit_harvest_selections,
                    worker_three_bridge_fruit_harvest_successes: self
                        .banana_factory_worker_three_bridge_fruit_harvest_successes,
                    worker_three_bridge_iron_mine_selections: self
                        .banana_factory_worker_three_bridge_iron_mine_selections,
                    worker_three_bridge_iron_mine_successes: self
                        .banana_factory_worker_three_bridge_iron_mine_successes,
                    worker_three_bridge_train_attempts: self
                        .banana_factory_worker_three_bridge_train_attempts,
                    worker_three_bridge_train_successes: self
                        .banana_factory_worker_three_bridge_train_successes,
                    worker_three_bridge_trained_turn: self
                        .banana_factory_worker_three_bridge_trained_turn,
                    worker_three_bridge_forbidden_commands: self
                        .banana_factory_worker_three_bridge_forbidden_commands,
                    worker_three_bridge_post_training_commands: self
                        .banana_factory_worker_three_bridge_post_training_commands,
                }
            }
            pub fn task_market_telemetry(&self) -> TaskMarketOrchardTelemetry {
                TaskMarketOrchardTelemetry {
                    activation_turn: self.task_market_activation_turn,
                    seed_repaid_turn: self.task_market_seed_repaid_turn,
                    market_turns: self.task_market_turns,
                    offers: self.inner.external_orchard_offers,
                    selections: self.inner.external_orchard_selections,
                    harvest_selections: self.inner.external_orchard_harvest_selections,
                    first_selection_turn: self.inner.external_orchard_first_selected_turn,
                    forced_setup_actions: self.task_market_forced_setup_actions,
                }
            }
            pub fn opponent_crop_priority(
                bonus: i32,
                eta_limit: i32,
                start_turn: i32,
                minimum_seen: usize,
            ) -> Self {
                let mut bot = Self::new();
                bot.inner.opponent_crop_bonus = bonus.max(0);
                bot.inner.opponent_crop_eta_limit = eta_limit.max(0);
                bot.inner.opponent_crop_start_turn = start_turn.max(1);
                bot.inner.opponent_crop_min_seen = minimum_seen;
                bot
            }
            pub fn opponent_crop_dual_value_e6() -> Self {
                let mut bot = Self::new();
                bot.inner.opponent_crop_dual_value = true;
                bot.inner.opponent_crop_eta_limit = 6;
                bot.inner.opponent_crop_start_turn = 1;
                bot.inner.opponent_crop_min_seen = 1;
                bot
            }
            pub fn opponent_crop_harvest_contact() -> Self {
                let mut bot = Self::opponent_crop_priority(100, 6, 1, 1);
                bot.inner.opponent_crop_harvest_contact = true;
                bot
            }
            pub fn opponent_crop_telemetry(&self) -> (usize, usize, Option<i32>, usize) {
                (
                    self.inner.opponent_crops_seen,
                    self.inner.opponent_crop_selected,
                    self.inner.opponent_crop_first_selected_turn,
                    self.inner.opponent_crops.len(),
                )
            }
            pub fn opponent_crop_harvest_rewrites(&self) -> usize {
                self.inner.opponent_crop_harvest_rewrites
            }
            pub fn max_bank_first_hp0() -> Self {
                let mut bot = Self::new();
                bot.inner.first_worker_max_bank_hp0 = true;
                bot
            }
            pub fn forced_first_worker_hp0(
                movement_speed: i32,
                carry_capacity: i32,
                chop_power: i32,
            ) -> Self {
                let mut bot = Self::new();
                bot.inner.first_worker_turn_one_override = Some(Stats {
                    movement_speed,
                    carry_capacity,
                    harvest_power: 0,
                    chop_power,
                });
                bot
            }
            pub fn idle_strict() -> Self {
                Self::with_policy(
                    YamoBot::tuned_carry_regeneration_transit_idle_harvest(),
                    12,
                    true,
                    11,
                    1,
                )
            }
            pub fn clock_only() -> Self {
                Self::with_policy(
                    YamoBot::tuned_carry_regeneration_transit_idle_harvest_clock_only(),
                    12,
                    true,
                    11,
                    1,
                )
            }
            pub fn coverage_only() -> Self {
                Self::with_policy(
                    YamoBot::tuned_carry_regeneration_transit_idle_harvest(),
                    8,
                    false,
                    11,
                    1,
                )
            }
            pub fn work_conserving() -> Self {
                Self::with_policy(
                    YamoBot::tuned_carry_regeneration_transit_idle_harvest(),
                    8,
                    true,
                    11,
                    1,
                )
            }
            pub fn fast_worker() -> Self {
                Self::with_policy(
                    YamoBot::tuned_carry_regeneration_transit_idle_harvest(),
                    8,
                    false,
                    14,
                    2,
                )
            }
            pub fn fast_worker_strict() -> Self {
                Self::new()
            }
            fn with_policy(
                inner: YamoBot,
                minimum_enemy_eta: i32,
                require_idle_starter: bool,
                minimum_enemy_door_distance: i32,
                minimum_worker_speed: i32,
            ) -> Self {
                Self {
                    inner,
                    initialized: false,
                    starter_id: None,
                    geometry: None,
                    initial_natural: BTreeMap::new(),
                    phase: OrchardPhase::Dormant,
                    plant_attempted: false,
                    minimum_enemy_eta,
                    require_idle_starter,
                    minimum_enemy_door_distance,
                    minimum_worker_speed,
                    task_market_enabled: false,
                    task_market_seed_repaid: false,
                    task_market_activation_turn: None,
                    task_market_seed_repaid_turn: None,
                    task_market_turns: 0,
                    task_market_forced_setup_actions: 0,
                    banana_factory_enabled: false,
                    banana_factory_ring: false,
                    banana_ring_cells_cache: std::cell::OnceCell::new(),
                    banana_ring_home_distances_cache: std::cell::OnceCell::new(),
                    banana_factory_source_separated: false,
                    banana_factory_selector_enabled: false,
                    banana_factory_selector_decided: false,
                    banana_factory_selector_selected: false,
                    banana_factory_trained_dual_value_e6: false,
                    banana_factory_active: false,
                    banana_factory_activation_turn: None,
                    banana_factory_initial_budget: None,
                    banana_factory_bootstrap_attempts: 0,
                    banana_factory_bootstrap_successes: 0,
                    banana_factory_owned_crops: BTreeMap::new(),
                    banana_factory_reserve: None,
                    banana_factory_reserve_promotions: 0,
                    banana_factory_reserve_losses: 0,
                    banana_factory_plant_target: None,
                    banana_factory_pending_plant: None,
                    banana_factory_pending_harvest: None,
                    banana_factory_seed_from_harvest: false,
                    banana_factory_harvest_selections: 0,
                    banana_factory_harvest_successes: 0,
                    banana_factory_bank_harvest_selections: 0,
                    banana_factory_bank_harvest_successes: 0,
                    banana_factory_conversion_harvest_selections: 0,
                    banana_factory_conversion_harvest_successes: 0,
                    banana_factory_renewable_plant_attempts: 0,
                    banana_factory_renewable_plant_successes: 0,
                    banana_factory_trained_role_rewrites: 0,
                    banana_factory_trained_forbidden_commands: 0,
                    banana_factory_trained_opponent_crop_selections: 0,
                    banana_factory_worker_three_bridge: false,
                    banana_factory_worker_three_bridge_funding_turns: 0,
                    banana_factory_worker_three_bridge_pending_harvest: None,
                    banana_factory_worker_three_bridge_fruit_harvest_selections: [0; 3],
                    banana_factory_worker_three_bridge_fruit_harvest_successes: [0; 3],
                    banana_factory_worker_three_bridge_pending_mine: None,
                    banana_factory_worker_three_bridge_iron_mine_selections: 0,
                    banana_factory_worker_three_bridge_iron_mine_successes: 0,
                    banana_factory_worker_three_bridge_pending_train: None,
                    banana_factory_worker_three_bridge_train_attempts: 0,
                    banana_factory_worker_three_bridge_train_successes: 0,
                    banana_factory_worker_three_bridge_trained_turn: None,
                    banana_factory_worker_three_bridge_forbidden_commands: 0,
                    banana_factory_worker_three_bridge_post_training_commands: 0,
                }
            }
            fn median(mut values: Vec<i32>) -> f64 {
                values.sort_unstable();
                let middle = values.len() / 2;
                if values.len() % 2 == 0 {
                    (values[middle - 1] + values[middle]) as f64 / 2.0
                } else {
                    values[middle] as f64
                }
            }
            fn initialize(&mut self, view: &GameState) {
                self.initialized = true;
                if self.banana_factory_enabled {
                    self.banana_factory_initial_budget = Some(view.inventories[0][BANANA]);
                }
                self.starter_id = view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 0)
                    .map(|unit| unit.id)
                    .min();
                self.initial_natural = view
                    .plants
                    .iter()
                    .filter(|plant| plant.health > 0)
                    .map(|plant| (plant.cell, plant.kind))
                    .collect();
                let mut doors: Vec<_> = ortho_neighbors(view.shacks[0])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .collect();
                doors.sort_unstable();
                if doors.len() < 2 || self.initial_natural.is_empty() {
                    return;
                }
                let enemy_doors: Vec<_> = ortho_neighbors(view.shacks[1])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .collect();
                let home_distance = bfs_distances(&view.walkable, &doors);
                let enemy_distance = bfs_distances(&view.walkable, &enemy_doors);
                let natural_return: Vec<_> = self
                    .initial_natural
                    .keys()
                    .filter_map(|cell| home_distance.get(cell).copied())
                    .collect();
                if natural_return.len() != self.initial_natural.len()
                    || Self::median(natural_return) < 8.0
                {
                    return;
                }
                let mut mothers: Vec<_> = doors
                    .iter()
                    .copied()
                    .filter(|door| view.plant_at(*door).is_none())
                    .filter(|door| view.water.iter().any(|water| is_adjacent(*water, *door)))
                    .filter(|door| enemy_distance.get(door).copied().unwrap_or(10_000) >= 11)
                    .collect();
                mothers.sort_by(|a, b| {
                    enemy_distance
                        .get(b)
                        .copied()
                        .unwrap_or(10_000)
                        .cmp(&enemy_distance.get(a).copied().unwrap_or(10_000))
                        .then_with(|| a.cmp(b))
                });
                let Some(mother) = mothers.first().copied() else {
                    return;
                };
                let alternate_doors = doors
                    .iter()
                    .copied()
                    .filter(|door| *door != mother)
                    .collect();
                self.geometry = Some(OrchardGeometry {
                    mother,
                    enemy_door_distance: enemy_distance.get(&mother).copied().unwrap_or(10_000),
                    doors,
                    alternate_doors,
                });
            }
            fn reconcile_initial_natural(&mut self, view: &GameState) {
                self.initial_natural.retain(|cell, initial_kind| {
                    view.plant_at(*cell).is_some_and(|index| {
                        let plant = &view.plants[index];
                        plant.health > 0 && plant.kind == *initial_kind
                    })
                });
            }
            fn walkable_without(view: &GameState, cell: Cell) -> BTreeSet<Cell> {
                let mut walkable = view.walkable.clone();
                walkable.remove(&cell);
                walkable
            }
            fn route_cycle(
                view: &GameState,
                unit: &Unit,
                plant: &Plant,
                walkable: &BTreeSet<Cell>,
                doors: &[Cell],
                first_chop_eta: i32,
                available_capacity: i32,
            ) -> Option<OrchardCycle> {
                if available_capacity <= 0 {
                    return None;
                }
                let predicted = MoisanBot::predict_tree(view, plant, first_chop_eta)?;
                if predicted.size <= 0 || predicted.health <= 0 {
                    return None;
                }
                let (chop_turns, final_size) =
                    MoisanBot::chop_outcome(view, plant, predicted, unit.stats.chop_power)?;
                if final_size.min(available_capacity) <= 0 {
                    return None;
                }
                let to_doors = bfs_distances(walkable, doors);
                let return_eta =
                    MoisanBot::ceil_div(*to_doors.get(&plant.cell)?, unit.stats.movement_speed);
                let cycle_eta = first_chop_eta + chop_turns + return_eta + 1;
                (cycle_eta <= TOTAL_TURNS - view.turn + 1).then_some(OrchardCycle {
                    first_chop_eta,
                    cycle_eta,
                })
            }
            fn bankable_cycle(
                view: &GameState,
                unit: &Unit,
                plant: &Plant,
                walkable: &BTreeSet<Cell>,
                doors: &[Cell],
            ) -> Option<OrchardCycle> {
                if unit.stats.chop_power <= 0 || doors.is_empty() {
                    return None;
                }
                let from_unit = bfs_distances(walkable, &[unit.cell]);
                let mut cycles = Vec::new();
                if unit.free_capacity() > 0 {
                    if let Some(distance) = from_unit.get(&plant.cell) {
                        let first_chop_eta =
                            MoisanBot::ceil_div(*distance, unit.stats.movement_speed);
                        if let Some(cycle) = Self::route_cycle(
                            view,
                            unit,
                            plant,
                            walkable,
                            doors,
                            first_chop_eta,
                            unit.free_capacity(),
                        ) {
                            cycles.push(cycle);
                        }
                    }
                }
                if unit.total_carried() > 0 {
                    for door in doors {
                        let (Some(to_door), Some(to_tree)) = (
                            from_unit.get(door),
                            bfs_distances(walkable, &[*door]).get(&plant.cell).copied(),
                        ) else {
                            continue;
                        };
                        let first_chop_eta =
                            MoisanBot::ceil_div(*to_door, unit.stats.movement_speed)
                                + 1
                                + MoisanBot::ceil_div(to_tree, unit.stats.movement_speed);
                        if let Some(cycle) = Self::route_cycle(
                            view,
                            unit,
                            plant,
                            walkable,
                            doors,
                            first_chop_eta,
                            unit.stats.carry_capacity,
                        ) {
                            cycles.push(cycle);
                        }
                    }
                }
                cycles
                    .into_iter()
                    .min_by_key(|cycle| (cycle.first_chop_eta, cycle.cycle_eta))
            }
            fn enemy_eta(view: &GameState, target: Cell) -> i32 {
                let distance = bfs_distances(&view.walkable, &[target]);
                view.units
                    .iter()
                    .filter(|unit| unit.player == 1 && unit.stats.chop_power > 0)
                    .filter_map(|unit| {
                        distance
                            .get(&unit.cell)
                            .map(|cells| MoisanBot::ceil_div(*cells, unit.stats.movement_speed))
                    })
                    .min()
                    .unwrap_or(10_000)
            }
            fn worker_can_use_alternate(
                view: &GameState,
                starter_id: i32,
                geometry: &OrchardGeometry,
                minimum_speed: i32,
            ) -> bool {
                let walkable = Self::walkable_without(view, geometry.mother);
                view.units
                    .iter()
                    .filter(|unit| {
                        unit.player == 0
                            && unit.id != starter_id
                            && unit.stats.chop_power > 0
                            && unit.stats.movement_speed >= minimum_speed
                    })
                    .any(|unit| {
                        let distance = bfs_distances(&walkable, &[unit.cell]);
                        geometry
                            .alternate_doors
                            .iter()
                            .any(|door| distance.contains_key(door))
                    })
            }
            fn loses_contested_tree(
                &self,
                view: &GameState,
                starter: &Unit,
                geometry: &OrchardGeometry,
            ) -> bool {
                let worker_walkable = Self::walkable_without(view, geometry.mother);
                let enemy_doors: Vec<_> = ortho_neighbors(view.shacks[1])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .collect();
                self.initial_natural.keys().any(|cell| {
                    let Some(index) = view.plant_at(*cell) else {
                        return false;
                    };
                    let plant = &view.plants[index];
                    let Some(starter_cycle) =
                        Self::bankable_cycle(view, starter, plant, &view.walkable, &geometry.doors)
                    else {
                        return false;
                    };
                    let enemy_cycle = view
                        .units
                        .iter()
                        .filter(|unit| unit.player == 1)
                        .filter_map(|unit| {
                            Self::bankable_cycle(view, unit, plant, &view.walkable, &enemy_doors)
                        })
                        .min_by_key(|cycle| (cycle.first_chop_eta, cycle.cycle_eta));
                    let Some(enemy_cycle) = enemy_cycle else {
                        return false;
                    };
                    if starter_cycle.first_chop_eta > enemy_cycle.first_chop_eta {
                        return false;
                    }
                    let trained_cycle = view
                        .units
                        .iter()
                        .filter(|unit| unit.player == 0 && unit.id != starter.id)
                        .filter_map(|unit| {
                            Self::bankable_cycle(
                                view,
                                unit,
                                plant,
                                &worker_walkable,
                                &geometry.alternate_doors,
                            )
                        })
                        .min_by_key(|cycle| (cycle.first_chop_eta, cycle.cycle_eta));
                    trained_cycle
                        .map(|cycle| cycle.first_chop_eta > enemy_cycle.first_chop_eta)
                        .unwrap_or(true)
                })
            }
            fn can_activate(
                &self,
                view: &GameState,
                starter: &Unit,
                geometry: &OrchardGeometry,
            ) -> bool {
                view.inventories[0][APPLE] > 0
                    && geometry.enemy_door_distance >= self.minimum_enemy_door_distance
                    && bfs_distances(&view.walkable, &[starter.cell]).contains_key(&geometry.mother)
                    && view.plant_at(geometry.mother).is_none()
                    && !view
                        .units
                        .iter()
                        .any(|unit| unit.id != starter.id && unit.cell == geometry.mother)
                    && Self::enemy_eta(view, geometry.mother) > self.minimum_enemy_eta
                    && Self::worker_can_use_alternate(
                        view,
                        starter.id,
                        geometry,
                        self.minimum_worker_speed,
                    )
                    && !self.loses_contested_tree(view, starter, geometry)
            }
            fn can_continue_seed(
                &self,
                view: &GameState,
                starter: &Unit,
                geometry: &OrchardGeometry,
            ) -> bool {
                let to_mother = bfs_distances(&view.walkable, &[starter.cell])
                    .get(&geometry.mother)
                    .copied()
                    .map(|distance| MoisanBot::ceil_div(distance, starter.stats.movement_speed));
                let turns_to_plant =
                    to_mother.map(|travel| travel + if starter.carry[APPLE] > 0 { 1 } else { 2 });
                (starter.carry[APPLE] > 0 || view.inventories[0][APPLE] > 0)
                    && turns_to_plant.is_some()
                    && view.plant_at(geometry.mother).is_none()
                    && !view
                        .units
                        .iter()
                        .any(|unit| unit.id != starter.id && unit.cell == geometry.mother)
                    && Self::enemy_eta(view, geometry.mother) > turns_to_plant.unwrap_or(10_000)
                    && Self::worker_can_use_alternate(
                        view,
                        starter.id,
                        geometry,
                        self.minimum_worker_speed,
                    )
            }
            fn starter_control_is_idle(
                commands: &[String],
                unit_ids: &[i32],
                starter: &Unit,
            ) -> bool {
                let Some(slot) = Self::unit_action_slot(commands, unit_ids, starter.id) else {
                    return false;
                };
                commands[slot].split_whitespace().next() == Some("WAIT")
            }
            fn unit_action_slot(commands: &[String], unit_ids: &[i32], id: i32) -> Option<usize> {
                let mut slot = 0usize;
                for (index, command) in commands.iter().enumerate() {
                    if command.starts_with("MSG ") || command.starts_with("TRAIN ") {
                        continue;
                    }
                    if unit_ids.get(slot).copied() == Some(id) {
                        return Some(index);
                    }
                    slot += 1;
                }
                None
            }
            fn replace_action(
                commands: &mut Vec<String>,
                unit_ids: &[i32],
                id: i32,
                action: String,
            ) {
                if let Some(slot) = Self::unit_action_slot(commands, unit_ids, id) {
                    commands[slot] = action;
                } else {
                    commands.push(action);
                }
            }
            fn best_alternate_door(
                view: &GameState,
                unit: &Unit,
                geometry: &OrchardGeometry,
            ) -> Option<Cell> {
                let walkable = Self::walkable_without(view, geometry.mother);
                let distance = bfs_distances(&walkable, &[unit.cell]);
                geometry
                    .alternate_doors
                    .iter()
                    .filter(|door| distance.contains_key(*door))
                    .min_by_key(|door| (distance[*door], **door))
                    .copied()
            }
            fn protect_mother(
                view: &GameState,
                commands: &mut Vec<String>,
                unit_ids: &[i32],
                starter_id: i32,
                geometry: &OrchardGeometry,
                reserve_apple: bool,
            ) {
                for unit in view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 0 && unit.id != starter_id)
                {
                    let Some(slot) = Self::unit_action_slot(commands, unit_ids, unit.id) else {
                        continue;
                    };
                    let command = commands[slot].clone();
                    let fields: Vec<_> = command.split_whitespace().collect();
                    let move_target = (fields.first() == Some(&"MOVE"))
                        .then(|| Some((fields.get(2)?.parse().ok()?, fields.get(3)?.parse().ok()?)))
                        .flatten();
                    let move_lands_on_mother = move_target.is_some_and(|target| {
                        next_cell(&view.walkable, unit.cell, target, unit.stats.movement_speed)
                            == geometry.mother
                    });
                    let stays_on_mother = unit.cell == geometry.mother
                        && !(fields.first() == Some(&"MOVE") && !move_lands_on_mother);
                    let steals_seed = reserve_apple
                        && fields.first() == Some(&"PICK")
                        && fields.get(2) == Some(&"APPLE");
                    if !move_lands_on_mother && !stays_on_mother && !steals_seed {
                        continue;
                    }
                    let safe_tree_waypoint = (move_lands_on_mother
                        && unit.cell != geometry.mother
                        && unit.total_carried() == 0)
                        .then(|| {
                            let walkable = Self::walkable_without(view, geometry.mother);
                            let landing = next_cell(
                                &walkable,
                                unit.cell,
                                move_target?,
                                unit.stats.movement_speed,
                            );
                            (landing != unit.cell && landing != geometry.mother).then_some(landing)
                        })
                        .flatten();
                    let replacement = safe_tree_waypoint
                        .or_else(|| {
                            Self::best_alternate_door(view, unit, geometry).filter(|_| {
                                unit.cell == geometry.mother || unit.total_carried() > 0
                            })
                        })
                        .map(|cell| format!("MOVE {} {} {}", unit.id, cell.0, cell.1))
                        .unwrap_or_else(|| "WAIT".to_string());
                    Self::replace_action(commands, unit_ids, unit.id, replacement);
                }
            }
            fn banana_factory_home_doors(view: &GameState, player: usize) -> Vec<Cell> {
                ortho_neighbors(view.shacks[player])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .collect()
            }

            fn banana_ring_frontdoor(view: &GameState) -> Option<Cell> {
                let mut gates = Self::banana_factory_home_doors(view, 0);
                gates.sort_unstable();
                if gates.len() < 2 {
                    return None;
                }
                let gate_distances: Vec<(Cell, BTreeMap<Cell, i32>)> = gates
                    .iter()
                    .map(|gate| (*gate, bfs_distances(&view.walkable, &[*gate])))
                    .collect();
                let mut max_pair = 0;
                for left in 0..gate_distances.len() {
                    for right in (left + 1)..gate_distances.len() {
                        max_pair = max_pair.max(
                            gate_distances[left]
                                .1
                                .get(&gate_distances[right].0)
                                .copied()
                                .unwrap_or(i32::MAX / 2),
                        );
                    }
                }
                if max_pair <= 8 {
                    return None;
                }
                let from_enemy = bfs_distances(&view.walkable, &[view.shacks[1]]);
                let mut viable: Vec<(Cell, i32)> = gate_distances
                    .iter()
                    .filter(|(_, distances)| {
                        view.walkable
                            .iter()
                            .filter(|cell| distances.get(cell).is_some_and(|steps| *steps <= 2))
                            .count()
                            >= 4
                    })
                    .map(|(gate, _)| (*gate, from_enemy.get(gate).copied().unwrap_or(0)))
                    .collect();
                viable.sort_by_key(|(gate, enemy_distance)| (-*enemy_distance, *gate));
                viable.first().map(|(gate, _)| *gate)
            }
            fn banana_ring_cells(&self, view: &GameState) -> &[Cell] {
                self.banana_ring_cells_cache.get_or_init(|| {
                    let home_doors = Self::banana_factory_home_doors(view, 0);
                    let from_home = bfs_distances(&view.walkable, &home_doors);
                    let frontdoor = Self::banana_ring_frontdoor(view);
                    let from_frontdoor = frontdoor
                        .map(|gate| bfs_distances(&view.walkable, &[gate]));
                    let shack = view.shacks[0];
                    let mut cells = Vec::new();
                    for dy in -1..=1 {
                        for dx in -1..=1 {
                            if dx == 0 && dy == 0 {
                                continue;
                            }
                            let cell = (shack.0 + dx, shack.1 + dy);
                            if !view.walkable.contains(&cell) || !from_home.contains_key(&cell) {
                                continue;
                            }
                            if from_frontdoor
                                .as_ref()
                                .is_some_and(|distances| {
                                    !distances.get(&cell).is_some_and(|steps| *steps <= 2)
                                })
                            {
                                continue;
                            }
                            cells.push(cell);
                        }
                    }
                    cells.sort_unstable();
                    cells
                }).as_slice()
            }
            fn banana_ring_is_diagonal(view: &GameState, cell: Cell) -> bool {
                (cell.0 - view.shacks[0].0).abs() == 1
                    && (cell.1 - view.shacks[0].1).abs() == 1
            }
            fn banana_ring_goal(&self, view: &GameState) -> usize {
                (self.banana_factory_initial_budget.unwrap_or(0).max(0) as usize)
                    .min(self.banana_ring_cells(view).len())
            }
            fn banana_ring_release_mothers(&self, view: &GameState) -> bool {
                if TOTAL_TURNS - view.turn <= 34 {
                    return true;
                }
                let from_home = self.banana_ring_home_distances_cache.get_or_init(|| {
                    bfs_distances(&view.walkable, &[view.shacks[0]])
                });
                view.units.iter().any(|unit| {
                    unit.player == 1
                        && from_home
                            .get(&unit.cell)
                            .is_some_and(|distance| *distance <= 4)
                })
            }
            fn banana_ring_plant_cell(&self, view: &GameState, unit: &Unit) -> Option<Cell> {
                let ring = self.banana_ring_cells(view);
                let distance = bfs_distances(&view.walkable, &[unit.cell]);
                let has_live_mother = view.plants.iter().any(|plant| {
                    plant.health > 0
                        && plant.kind == PlantKind::Banana
                        && ring.contains(&plant.cell)
                        && Self::banana_ring_is_diagonal(view, plant.cell)
                });
                ring.iter().copied()
                    .filter(|cell| view.plant_at(*cell).is_none())
                    .filter(|cell| distance.contains_key(cell))
                    .filter(|cell| {
                        !view
                            .units
                            .iter()
                            .any(|other| other.id != unit.id && other.cell == *cell)
                    })
                    .min_by_key(|cell| {
                        (
                            if !has_live_mother && Self::banana_ring_is_diagonal(view, *cell) {
                                0
                            } else {
                                1
                            },
                            distance[cell],
                            *cell,
                        )
                    })
            }
            fn banana_ring_harvest_target(
                &self,
                view: &GameState,
                unit: &Unit,
            ) -> Option<(Cell, bool)> {
                let ring: BTreeSet<Cell> = self.banana_ring_cells(view).iter().copied().collect();
                let distance = bfs_distances(&view.walkable, &[unit.cell]);
                view.plants
                    .iter()
                    .filter(|plant| {
                        plant.health > 0
                            && plant.kind == PlantKind::Banana
                            && plant.fruits > 0
                            && ring.contains(&plant.cell)
                            && Self::banana_ring_is_diagonal(view, plant.cell)
                            && distance.contains_key(&plant.cell)
                    })
                    .min_by_key(|plant| (distance[&plant.cell], plant.cell))
                    .map(|plant| {
                        (
                            plant.cell,
                            self.banana_factory_owned_crops
                                .get(&plant.cell)
                                .copied()
                                .unwrap_or(false),
                        )
                    })
            }
            fn banana_ring_bank_command(view: &GameState, unit: &Unit) -> Option<String> {
                YamoBot::bank_candidates(view, unit)
                    .into_iter()
                    .max_by(|left, right| left.score.total_cmp(&right.score))
                    .map(|candidate| candidate.command)
            }
            fn banana_ring_issue_harvest(
                &mut self,
                view: &GameState,
                starter: &Unit,
                target: Cell,
                bank_source: bool,
            ) -> String {
                if starter.cell != target {
                    return format!("MOVE {} {} {}", starter.id, target.0, target.1);
                }
                self.banana_factory_harvest_selections += 1;
                if bank_source {
                    self.banana_factory_bank_harvest_selections += 1;
                } else {
                    self.banana_factory_conversion_harvest_selections += 1;
                }
                self.banana_factory_pending_harvest =
                    Some((view.turn, starter.carry[BANANA], bank_source));
                format!("HARVEST {}", starter.id)
            }
            fn banana_ring_starter_command(
                &mut self,
                view: &GameState,
                starter: &Unit,
            ) -> Option<String> {
                if starter.total_carried() > starter.carry[BANANA] {
                    return Self::banana_ring_bank_command(view, starter);
                }
                let goal = self.banana_ring_goal(view);
                let target = self
                    .banana_factory_plant_target
                    .filter(|cell| {
                        self.banana_ring_cells(view).contains(cell)
                            && view.plant_at(*cell).is_none()
                            && !view
                                .units
                                .iter()
                                .any(|other| other.id != starter.id && other.cell == *cell)
                    })
                    .or_else(|| self.banana_ring_plant_cell(view, starter));
                if starter.carry[BANANA] > 0 {
                    let Some(target) = target else {
                        self.banana_factory_plant_target = None;
                        return Self::banana_ring_bank_command(view, starter);
                    };
                    self.banana_factory_plant_target = Some(target);
                    let source = if self.banana_factory_seed_from_harvest
                        || self.banana_factory_bootstrap_successes >= goal
                    {
                        BananaFactoryPlantSource::RenewableHarvest
                    } else {
                        BananaFactoryPlantSource::BankBootstrap
                    };
                    if starter.cell != target {
                        return Some(format!("MOVE {} {} {}", starter.id, target.0, target.1));
                    }
                    match source {
                        BananaFactoryPlantSource::BankBootstrap => {
                            self.banana_factory_bootstrap_attempts += 1;
                        }
                        BananaFactoryPlantSource::RenewableHarvest => {
                            self.banana_factory_renewable_plant_attempts += 1;
                        }
                    }
                    self.banana_factory_pending_plant =
                        Some((view.turn, target, source, starter.carry[BANANA]));
                    return Some(format!("PLANT {} BANANA", starter.id));
                }
                if starter.free_capacity() <= 0 {
                    return Self::banana_ring_bank_command(view, starter);
                }
                let harvest = self.banana_ring_harvest_target(view, starter);
                if let Some((cell, bank_source)) = harvest.filter(|(cell, _)| {
                    manhattan(starter.cell, *cell) <= 1
                }) {
                    return Some(self.banana_ring_issue_harvest(
                        view,
                        starter,
                        cell,
                        bank_source,
                    ));
                }
                if self.banana_factory_bootstrap_successes < goal {
                    if let Some(target) = target {
                        let distance = bfs_distances(&view.walkable, &[starter.cell]);
                        let movement_turns = distance
                            .get(&target)
                            .map(|steps| MoisanBot::ceil_div(*steps, starter.stats.movement_speed));
                        if view.inventories[0][BANANA] > 0
                            && movement_turns.is_some_and(|turns| turns <= 2)
                        {
                            return Self::banana_factory_bank_command(view, starter);
                        }
                    }
                }
                harvest.map(|(cell, bank_source)| {
                    self.banana_ring_issue_harvest(view, starter, cell, bank_source)
                })
            }
            fn banana_ring_promote_reserve(&mut self, view: &GameState) {
                let ring: BTreeSet<Cell> = self.banana_ring_cells(view).iter().copied().collect();
                let selected = view
                    .plants
                    .iter()
                    .filter(|plant| {
                        plant.health > 0
                            && plant.kind == PlantKind::Banana
                            && ring.contains(&plant.cell)
                            && Self::banana_ring_is_diagonal(view, plant.cell)
                    })
                    .map(|plant| plant.cell)
                    .min();
                if self.banana_factory_reserve != selected {
                    if self.banana_factory_reserve.is_some() {
                        self.banana_factory_reserve_losses += 1;
                    }
                    if selected.is_some() {
                        self.banana_factory_reserve_promotions += 1;
                    }
                    self.banana_factory_reserve = selected;
                }
            }
            fn banana_ring_wood_command(&mut self, view: &GameState, unit: &Unit) -> String {
                let mut candidates = if unit.total_carried() > 0 {
                    YamoBot::bank_candidates(view, unit)
                } else {
                    YamoBot::yamo_chop_candidates(
                        view,
                        unit,
                        self.inner.type_to_cut,
                        self.banana_factory_reserve,
                        self.inner.opponent_eta_penalty,
                    )
                };
                let ring: BTreeSet<Cell> = self.banana_ring_cells(view).iter().copied().collect();
                if !self.banana_ring_release_mothers(view) {
                    candidates.retain(|candidate| {
                        !matches!(
                            candidate.target,
                            Target::Tree(cell)
                                if ring.contains(&cell)
                                    && Self::banana_ring_is_diagonal(view, cell)
                        )
                    });
                }
                self.inner
                    .apply_opponent_crop_priority(view, unit, &mut candidates);
                let distance = bfs_distances(&view.walkable, &[unit.cell]);
                let urgent = self.inner.crop_priority_active(view).then(|| {
                    candidates
                        .iter()
                        .filter(|candidate| {
                            let Target::Tree(cell) = candidate.target else {
                                return false;
                            };
                            self.inner.opponent_crops.contains(&cell)
                                && distance.get(&cell).is_some_and(|steps| {
                                    MoisanBot::ceil_div(*steps, unit.stats.movement_speed)
                                        <= self.inner.opponent_crop_eta_limit
                                })
                        })
                        .max_by(|left, right| left.score.total_cmp(&right.score))
                        .cloned()
                }).flatten();
                if let Some(selected) = urgent {
                    self.banana_factory_trained_opponent_crop_selections += 1;
                    return selected.command;
                }
                let orthogonal = candidates
                    .iter()
                    .filter(|candidate| {
                        let Target::Tree(cell) = candidate.target else {
                            return false;
                        };
                        ring.contains(&cell)
                            && !Self::banana_ring_is_diagonal(view, cell)
                            && view.plant_at(cell).is_some_and(|index| {
                                let plant = &view.plants[index];
                                plant.health > 0
                                    && plant.kind == PlantKind::Banana
                                    && plant.size >= 2
                            })
                    })
                    .max_by(|left, right| left.score.total_cmp(&right.score))
                    .cloned();
                orthogonal
                    .or_else(|| {
                        candidates
                            .into_iter()
                            .max_by(|left, right| left.score.total_cmp(&right.score))
                    })
                    .map(|candidate| candidate.command)
                    .unwrap_or_else(|| "WAIT".to_string())
            }
            fn banana_ring_commands(&mut self, view: &GameState) -> Vec<String> {
                self.reconcile_banana_factory(view);
                if !self.banana_factory_active {
                    self.banana_factory_active = true;
                    self.banana_factory_activation_turn = Some(view.turn);
                }
                self.inner.external_idle_unit = None;
                self.inner.external_orchard_task = None;
                self.inner.external_protected_tree = self.banana_factory_reserve;
                self.inner.regeneration_commitments.clear();
                let mut commands = self.inner.commands(view);
                let mut unit_ids: Vec<_> = view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 0)
                    .map(|unit| unit.id)
                    .collect();
                unit_ids.sort_unstable();
                let Some(starter_id) = self.starter_id else {
                    return commands;
                };
                if let Some(starter) = view.unit(starter_id) {
                    if let Some(command) = self.banana_ring_starter_command(view, starter) {
                        Self::replace_action(&mut commands, &unit_ids, starter_id, command);
                    }
                }
                if !self.banana_ring_release_mothers(view) {
                    if let Some(starter) = view.unit(starter_id) {
                        let protected_mother = self.banana_ring_cells(view).contains(&starter.cell)
                            && Self::banana_ring_is_diagonal(view, starter.cell)
                            && view.plant_at(starter.cell).is_some_and(|index| {
                                let plant = &view.plants[index];
                                plant.health > 0 && plant.kind == PlantKind::Banana
                            });
                        if protected_mother {
                            if let Some(slot) = Self::unit_action_slot(&commands, &unit_ids, starter_id) {
                                if commands[slot]
                                    .split_whitespace()
                                    .next()
                                    .is_some_and(|verb| verb == "CHOP")
                                {
                                    commands[slot] = "WAIT".to_string();
                                }
                            }
                        }
                    }
                }
                for unit in view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 0 && unit.id != starter_id)
                {
                    if let Some(slot) = Self::unit_action_slot(&commands, &unit_ids, unit.id) {
                        commands[slot] = self.banana_ring_wood_command(view, unit);
                        self.banana_factory_trained_role_rewrites += 1;
                    }
                }
                self.inner.regeneration_commitments.clear();
                self.inner.own_plant_attempts.clear();
                let priority = BTreeSet::from([starter_id]);
                let forbidden: BTreeSet<Cell> = if self.banana_ring_release_mothers(view) {
                    BTreeSet::new()
                } else {
                    self.banana_ring_cells(view)
                        .iter()
                        .copied()
                        .filter(|cell| Self::banana_ring_is_diagonal(view, *cell))
                        .collect()
                };
                MoisanBot::resolve_move_conflicts_with_priority_and_forbidden(
                    view,
                    &mut commands,
                    &priority,
                    &forbidden,
                );
                self.inner.remember_own_plant_attempts(view, &commands);
                commands
            }
            fn banana_factory_plant_cell(
                &self,
                view: &GameState,
                unit: &Unit,
                reserve_preference: bool,
            ) -> Option<Cell> {
                if self.banana_factory_ring { return self.banana_ring_plant_cell(view, unit); }
                let home_doors = Self::banana_factory_home_doors(view, 0);
                let enemy_doors = Self::banana_factory_home_doors(view, 1);
                let from_unit = bfs_distances(&view.walkable, &[unit.cell]);
                let from_home = bfs_distances(&view.walkable, &home_doors);
                let from_enemy = bfs_distances(&view.walkable, &enemy_doors);
                view.walkable
                    .iter()
                    .copied()
                    .filter(|cell| view.plant_at(*cell).is_none())
                    .filter(|cell| {
                        !view
                            .units
                            .iter()
                            .any(|other| other.id != unit.id && other.cell == *cell)
                    })
                    .filter(|cell| from_unit.contains_key(cell) && from_home.contains_key(cell))
                    .filter(|cell| {
                        from_home[cell] <= from_enemy.get(cell).copied().unwrap_or(10_000)
                    })
                    .min_by_key(|cell| {
                        let water = view.water.iter().any(|water| is_adjacent(*water, *cell));
                        let home = from_home[cell];
                        let enemy = from_enemy.get(cell).copied().unwrap_or(10_000);
                        let travel = from_unit[cell];
                        if reserve_preference {
                            (if water { 0 } else { 1 }, home, -enemy, 0, *cell)
                        } else {
                            (0, travel, home, -enemy, *cell)
                        }
                    })
            }
            fn banana_factory_promote_reserve(&mut self, view: &GameState) {
                if self.banana_factory_ring { self.banana_ring_promote_reserve(view); return; }
                if self.banana_factory_reserve.is_some() {
                    return;
                }
                let home_doors = Self::banana_factory_home_doors(view, 0);
                let enemy_doors = Self::banana_factory_home_doors(view, 1);
                let from_home = bfs_distances(&view.walkable, &home_doors);
                let from_enemy = bfs_distances(&view.walkable, &enemy_doors);
                let selected = self
                    .banana_factory_owned_crops
                    .iter()
                    .filter(|(cell, _)| {
                        view.plant_at(**cell).is_some_and(|index| {
                            let plant = &view.plants[index];
                            plant.health > 0 && plant.kind == PlantKind::Banana
                        })
                    })
                    .min_by_key(|(cell, bank_seed)| {
                        let water = view.water.iter().any(|water| is_adjacent(*water, **cell));
                        let home = from_home.get(*cell).copied().unwrap_or(10_000);
                        let enemy = from_enemy.get(*cell).copied().unwrap_or(10_000);
                        (
                            if **bank_seed { 0 } else { 1 },
                            if water { 0 } else { 1 },
                            -enemy,
                            home,
                            **cell,
                        )
                    })
                    .map(|(cell, _)| *cell);
                if let Some(cell) = selected {
                    self.banana_factory_reserve = Some(cell);
                    self.banana_factory_reserve_promotions += 1;
                }
            }
            fn reconcile_banana_factory(&mut self, view: &GameState) {
                if let Some((turn, cell, source, before_carry)) = self.banana_factory_pending_plant
                {
                    if turn < view.turn {
                        let spent = self
                            .starter_id
                            .and_then(|id| view.unit(id))
                            .is_some_and(|starter| starter.carry[BANANA] < before_carry);
                        let success = spent
                            && view.plant_at(cell).is_some_and(|index| {
                                let plant = &view.plants[index];
                                plant.health > 0 && plant.kind == PlantKind::Banana
                            });
                        if success {
                            let bank_seed = source == BananaFactoryPlantSource::BankBootstrap;
                            self.banana_factory_owned_crops.insert(cell, bank_seed);
                            match source {
                                BananaFactoryPlantSource::BankBootstrap => {
                                    self.banana_factory_bootstrap_successes += 1;
                                }
                                BananaFactoryPlantSource::RenewableHarvest => {
                                    self.banana_factory_renewable_plant_successes += 1;
                                    self.banana_factory_seed_from_harvest = false;
                                }
                            }
                        }
                        self.banana_factory_pending_plant = None;
                        self.banana_factory_plant_target = None;
                    }
                }
                if let Some((turn, before_carry, bank_source)) = self.banana_factory_pending_harvest
                {
                    if turn < view.turn {
                        let success = self
                            .starter_id
                            .and_then(|id| view.unit(id))
                            .is_some_and(|starter| starter.carry[BANANA] > before_carry);
                        if success {
                            self.banana_factory_harvest_successes += 1;
                            if bank_source {
                                self.banana_factory_bank_harvest_successes += 1;
                            } else {
                                self.banana_factory_conversion_harvest_successes += 1;
                            }
                            self.banana_factory_seed_from_harvest = true;
                        }
                        self.banana_factory_pending_harvest = None;
                    }
                }
                self.banana_factory_owned_crops.retain(|cell, _| {
                    view.plant_at(*cell).is_some_and(|index| {
                        let plant = &view.plants[index];
                        plant.health > 0 && plant.kind == PlantKind::Banana
                    })
                });
                if self
                    .banana_factory_reserve
                    .is_some_and(|cell| !self.banana_factory_owned_crops.contains_key(&cell))
                {
                    self.banana_factory_reserve = None;
                    self.banana_factory_reserve_losses += 1;
                }
                self.banana_factory_promote_reserve(view);
                if self.banana_factory_plant_target.is_some_and(|cell| {
                    view.plant_at(cell).is_some()
                        || view
                            .units
                            .iter()
                            .any(|other| Some(other.id) != self.starter_id && other.cell == cell)
                }) {
                    self.banana_factory_plant_target = None;
                }
                if self.banana_factory_ring
                    && self.banana_factory_pending_harvest.is_none()
                    && self.banana_factory_pending_plant.is_none()
                    && self
                        .starter_id
                        .and_then(|id| view.unit(id))
                        .is_some_and(|starter| starter.carry[BANANA] == 0)
                {
                    self.banana_factory_seed_from_harvest = false;
                }
}
            fn banana_factory_bank_command(view: &GameState, unit: &Unit) -> Option<String> {
                if is_adjacent(unit.cell, view.shacks[0]) {
                    return Some(format!("PICK {} BANANA", unit.id));
                }
                let distance = bfs_distances(&view.walkable, &[unit.cell]);
                Self::banana_factory_home_doors(view, 0)
                    .into_iter()
                    .filter(|cell| distance.contains_key(cell))
                    .min_by_key(|cell| (distance[cell], *cell))
                    .map(|cell| format!("MOVE {} {} {}", unit.id, cell.0, cell.1))
            }
            fn banana_factory_harvest_target(
                &self,
                view: &GameState,
                unit: &Unit,
            ) -> Option<(Cell, bool)> {
                if self.banana_factory_ring { return self.banana_ring_harvest_target(view, unit); }
                let distance = bfs_distances(&view.walkable, &[unit.cell]);
                self.banana_factory_owned_crops
                    .iter()
                    .filter(|(cell, _)| distance.contains_key(*cell))
                    .filter(|(cell, bank_seed)| {
                        !self.banana_factory_source_separated
                            || **bank_seed
                            || self.banana_factory_reserve == Some(**cell)
                    })
                    .filter(|(cell, _)| {
                        view.plant_at(**cell).is_some_and(|index| {
                            let plant = &view.plants[index];
                            plant.health > 0 && plant.kind == PlantKind::Banana && plant.fruits > 0
                        })
                    })
                    .min_by_key(|(cell, bank_seed)| {
                        (
                            if self.banana_factory_reserve == Some(**cell) {
                                0
                            } else {
                                1
                            },
                            if **bank_seed { 0 } else { 1 },
                            distance[*cell],
                            **cell,
                        )
                    })
                    .map(|(cell, bank_seed)| (*cell, *bank_seed))
            }
            fn banana_factory_starter_command(
                &mut self,
                view: &GameState,
                starter: &Unit,
            ) -> Option<String> {
                if self.banana_factory_ring { return self.banana_ring_starter_command(view, starter); }
                let banana_carry = starter.carry[BANANA];
                if starter.total_carried() > banana_carry {
                    return None;
                }
                let goal = self.banana_factory_initial_budget.unwrap_or(0).max(0) as usize;
                if banana_carry > 0 {
                    let source = if self.banana_factory_seed_from_harvest
                        || self.banana_factory_bootstrap_successes >= goal
                    {
                        BananaFactoryPlantSource::RenewableHarvest
                    } else {
                        BananaFactoryPlantSource::BankBootstrap
                    };
                    let reserve_preference = source == BananaFactoryPlantSource::BankBootstrap
                        && self.banana_factory_reserve.is_none()
                        && self.banana_factory_bootstrap_successes == 0;
                    let target = self
                        .banana_factory_plant_target
                        .filter(|cell| {
                            view.plant_at(*cell).is_none()
                                && !view
                                    .units
                                    .iter()
                                    .any(|other| other.id != starter.id && other.cell == *cell)
                        })
                        .or_else(|| {
                            self.banana_factory_plant_cell(view, starter, reserve_preference)
                        })?;
                    self.banana_factory_plant_target = Some(target);
                    if starter.cell == target {
                        match source {
                            BananaFactoryPlantSource::BankBootstrap => {
                                self.banana_factory_bootstrap_attempts += 1;
                            }
                            BananaFactoryPlantSource::RenewableHarvest => {
                                self.banana_factory_renewable_plant_attempts += 1;
                            }
                        }
                        self.banana_factory_pending_plant =
                            Some((view.turn, target, source, starter.carry[BANANA]));
                        return Some(format!("PLANT {} BANANA", starter.id));
                    }
                    return Some(format!("MOVE {} {} {}", starter.id, target.0, target.1));
                }
                if self.banana_factory_bootstrap_successes < goal {
                    if view.inventories[0][BANANA] > 0 {
                        return Self::banana_factory_bank_command(view, starter);
                    }
                    return None;
                }
                if starter.free_capacity() <= 0 {
                    return None;
                }
                if let Some((target, bank_source)) =
                    self.banana_factory_harvest_target(view, starter)
                {
                    if starter.cell == target {
                        self.banana_factory_harvest_selections += 1;
                        if bank_source {
                            self.banana_factory_bank_harvest_selections += 1;
                        } else {
                            self.banana_factory_conversion_harvest_selections += 1;
                        }
                        self.banana_factory_pending_harvest =
                            Some((view.turn, starter.carry[BANANA], bank_source));
                        return Some(format!("HARVEST {}", starter.id));
                    }
                    return Some(format!("MOVE {} {} {}", starter.id, target.0, target.1));
                }
                if let Some(reserve) = self.banana_factory_reserve {
                    if let Some(index) = view.plant_at(reserve) {
                        let plant = &view.plants[index];
                        let distance = bfs_distances(&view.walkable, &[starter.cell]);
                        if let Some(cells) = distance.get(&reserve) {
                            let travel = MoisanBot::ceil_div(*cells, starter.stats.movement_speed);
                            if MoisanBot::ticks_until_fruit(view, plant) <= travel + 1 {
                                return if starter.cell == reserve {
                                    Some("WAIT".to_string())
                                } else {
                                    Some(format!("MOVE {} {} {}", starter.id, reserve.0, reserve.1))
                                };
                            }
                        }
                    }
                }
                None
            }
            fn banana_factory_worker_three_stats() -> Stats {
                Stats {
                    movement_speed: 2,
                    carry_capacity: 2,
                    harvest_power: 0,
                    chop_power: 2,
                }
            }
            fn banana_factory_worker_three_cost(view: &GameState) -> Stock {
                let mut cost = training_cost(2, Self::banana_factory_worker_three_stats().tuple());
                if view.iron.is_empty() {
                    cost[IRON] = 0;
                }
                cost
            }
            fn banana_factory_worker_three_bootstrap_complete(&self) -> bool {
                let goal = self.banana_factory_initial_budget.unwrap_or(0).max(0) as usize;
                self.banana_factory_bootstrap_successes >= goal
            }
            fn banana_factory_worker_three_funding_active(&self, view: &GameState) -> bool {
                self.banana_factory_worker_three_bridge
                    && self.banana_factory_worker_three_bridge_train_successes == 0
                    && view.units.iter().filter(|unit| unit.player == 0).count() == 2
                    && self.banana_factory_worker_three_bootstrap_complete()
            }
            fn reconcile_banana_factory_worker_three_bridge(&mut self, view: &GameState) {
                if let Some((turn, unit_id, item, before_carry)) =
                    self.banana_factory_worker_three_bridge_pending_harvest
                {
                    if turn < view.turn {
                        if view
                            .unit(unit_id)
                            .is_some_and(|unit| unit.carry[item] > before_carry)
                        {
                            self.banana_factory_worker_three_bridge_fruit_harvest_successes
                                [item] += 1;
                        }
                        self.banana_factory_worker_three_bridge_pending_harvest = None;
                    }
                }
                if let Some((turn, unit_id, before_iron)) =
                    self.banana_factory_worker_three_bridge_pending_mine
                {
                    if turn < view.turn {
                        if view
                            .unit(unit_id)
                            .is_some_and(|unit| unit.carry[IRON] > before_iron)
                        {
                            self.banana_factory_worker_three_bridge_iron_mine_successes += 1;
                        }
                        self.banana_factory_worker_three_bridge_pending_mine = None;
                    }
                }
                if let Some((turn, before_workers)) =
                    self.banana_factory_worker_three_bridge_pending_train
                {
                    if turn < view.turn {
                        let workers = view.units.iter().filter(|unit| unit.player == 0).count();
                        if workers > before_workers {
                            self.banana_factory_worker_three_bridge_train_successes += 1;
                            self.banana_factory_worker_three_bridge_trained_turn = Some(turn);
                        }
                        self.banana_factory_worker_three_bridge_pending_train = None;
                    }
                }
            }
            fn banana_factory_worker_three_bank_command(
                view: &GameState,
                unit: &Unit,
            ) -> Option<String> {
                YamoBot::bank_candidates(view, unit)
                    .into_iter()
                    .max_by(|left, right| left.score.total_cmp(&right.score))
                    .map(|candidate| candidate.command)
            }
            fn banana_factory_worker_three_fruit_target(
                view: &GameState,
                starter: &Unit,
            ) -> Option<(Cell, usize)> {
                if starter.stats.harvest_power <= 0 || starter.free_capacity() <= 0 {
                    return None;
                }
                let cost = Self::banana_factory_worker_three_cost(view);
                let mut items = vec![PLUM, LEMON, APPLE];
                items.sort_by_key(|item| {
                    let deficit = (cost[*item] - view.inventories[0][*item]).max(0);
                    (-deficit, *item)
                });
                let from_starter = bfs_distances(&view.walkable, &[starter.cell]);
                let home_doors = Self::banana_factory_home_doors(view, 0);
                let from_home = bfs_distances(&view.walkable, &home_doors);
                for item in items {
                    let deficit = (cost[item] - view.inventories[0][item]).max(0);
                    if deficit == 0 {
                        continue;
                    }
                    let kind = match item {
                        PLUM => PlantKind::Plum,
                        LEMON => PlantKind::Lemon,
                        APPLE => PlantKind::Apple,
                        _ => unreachable!(),
                    };
                    let target = view
                        .plants
                        .iter()
                        .filter(|plant| {
                            plant.health > 0
                                && plant.kind == kind
                                && plant.fruits > 0
                                && from_starter.contains_key(&plant.cell)
                                && from_home.contains_key(&plant.cell)
                        })
                        .min_by_key(|plant| {
                            let progress = plant
                                .fruits
                                .min(starter.stats.harvest_power)
                                .min(starter.free_capacity())
                                .min(deficit);
                            let travel = MoisanBot::ceil_div(
                                from_starter[&plant.cell],
                                starter.stats.movement_speed,
                            );
                            let home = MoisanBot::ceil_div(
                                from_home[&plant.cell],
                                starter.stats.movement_speed,
                            );
                            (-progress, travel + home, plant.cell)
                        })
                        .map(|plant| plant.cell);
                    if let Some(cell) = target {
                        return Some((cell, item));
                    }
                }
                None
            }
            fn banana_factory_worker_three_starter_command(
                &mut self,
                view: &GameState,
                starter: &Unit,
            ) -> Option<String> {
                if starter.total_carried() > starter.carry[BANANA] {
                    return Self::banana_factory_worker_three_bank_command(view, starter);
                }
                if starter.carry[BANANA] > 0
                    || self.banana_factory_seed_from_harvest
                    || self.banana_factory_plant_target.is_some()
                    || self.banana_factory_pending_plant.is_some()
                    || self.banana_factory_pending_harvest.is_some()
                {
                    return None;
                }
                let (target, item) = Self::banana_factory_worker_three_fruit_target(view, starter)?;
                if starter.cell == target {
                    self.banana_factory_worker_three_bridge_fruit_harvest_selections[item] += 1;
                    self.banana_factory_worker_three_bridge_pending_harvest =
                        Some((view.turn, starter.id, item, starter.carry[item]));
                    Some(format!("HARVEST {}", starter.id))
                } else {
                    Some(format!("MOVE {} {} {}", starter.id, target.0, target.1))
                }
            }
            fn banana_factory_worker_three_mining_command(
                &mut self,
                view: &GameState,
                unit: &Unit,
            ) -> Option<String> {
                if unit.total_carried() > 0 {
                    return Self::banana_factory_worker_three_bank_command(view, unit);
                }
                let cost = Self::banana_factory_worker_three_cost(view);
                if view.inventories[0][IRON] >= cost[IRON] {
                    return None;
                }
                let command = MoisanBot::iron_candidates(view, unit, 0.0)
                    .into_iter()
                    .max_by(|left, right| left.score.total_cmp(&right.score))?
                    .command;
                if command.starts_with("MINE ") {
                    self.banana_factory_worker_three_bridge_iron_mine_selections += 1;
                    self.banana_factory_worker_three_bridge_pending_mine =
                        Some((view.turn, unit.id, unit.carry[IRON]));
                }
                Some(command)
            }
            fn banana_factory_worker_three_can_train(&self, view: &GameState) -> bool {
                if !self.banana_factory_worker_three_funding_active(view)
                    || TOTAL_TURNS - view.turn <= 20
                {
                    return false;
                }
                let cost = Self::banana_factory_worker_three_cost(view);
                if (0..cost.len()).any(|item| view.inventories[0][item] < cost[item]) {
                    return false;
                }
                !view.units.iter().any(|unit| unit.cell == view.shacks[0])
            }
            fn banana_factory_wood_command(&mut self, view: &GameState, unit: &Unit) -> String {
                if self.banana_factory_ring { return self.banana_ring_wood_command(view, unit); }
                let mut candidates = if unit.total_carried() > 0 {
                    YamoBot::bank_candidates(view, unit)
                } else {
                    YamoBot::yamo_chop_candidates(
                        view,
                        unit,
                        self.inner.type_to_cut,
                        self.banana_factory_reserve,
                        self.inner.opponent_eta_penalty,
                    )
                };
                if self.banana_factory_trained_dual_value_e6 && self.inner.opponent_crops_seen >= 1
                {
                    let distance = bfs_distances(&view.walkable, &[unit.cell]);
                    for candidate in &mut candidates {
                        let Target::Tree(cell) = candidate.target else {
                            continue;
                        };
                        if !self.inner.opponent_crops.contains(&cell) {
                            continue;
                        }
                        let Some(cells) = distance.get(&cell) else {
                            continue;
                        };
                        let eta = MoisanBot::ceil_div(*cells, unit.stats.movement_speed);
                        if eta <= 6 {
                            candidate.score += candidate.score;
                        }
                    }
                } else {
                    self.inner
                        .apply_opponent_crop_priority(view, unit, &mut candidates);
                }
                let selected = candidates
                    .into_iter()
                    .max_by(|left, right| left.score.total_cmp(&right.score));
                if selected.as_ref().is_some_and(|candidate| {
                    matches!(candidate.target, Target::Tree(cell) if self.inner.opponent_crops.contains(&cell))
                }) {
                    self.banana_factory_trained_opponent_crop_selections += 1;
                }
                selected
                    .map(|candidate| candidate.command)
                    .unwrap_or_else(|| "WAIT".to_string())
            }
            fn banana_factory_commands(&mut self, view: &GameState) -> Vec<String> {
                if self.banana_factory_ring { return self.banana_ring_commands(view); }
                self.reconcile_banana_factory(view);
                self.reconcile_banana_factory_worker_three_bridge(view);
                if !self.banana_factory_active {
                    self.banana_factory_active = true;
                    self.banana_factory_activation_turn = Some(view.turn);
                }
                self.inner.external_idle_unit = None;
                self.inner.external_orchard_task = None;
                self.inner.external_protected_tree = self.banana_factory_reserve;
                self.inner.regeneration_commitments.clear();
                let mut commands = self.inner.commands(view);
                let mut unit_ids: Vec<_> = view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 0)
                    .map(|unit| unit.id)
                    .collect();
                unit_ids.sort_unstable();
                let Some(starter_id) = self.starter_id else {
                    return commands;
                };
                let bridge_funding = self.banana_factory_worker_three_funding_active(view);
                if bridge_funding {
                    self.banana_factory_worker_three_bridge_funding_turns += 1;
                }
                if let Some(starter) = view.unit(starter_id) {
                    let bridge_command = if bridge_funding {
                        self.banana_factory_worker_three_starter_command(view, starter)
                    } else {
                        None
                    };
                    if bridge_command.as_ref().is_some_and(|command| {
                        matches!(
                            command.split_whitespace().next().unwrap_or("WAIT"),
                            "PICK" | "PLANT"
                        )
                    }) {
                        self.banana_factory_worker_three_bridge_forbidden_commands += 1;
                    }
                    let command = if bridge_command.is_some() {
                        bridge_command
                    } else {
                        self.banana_factory_starter_command(view, starter)
                    };
                    if let Some(command) = command {
                        Self::replace_action(&mut commands, &unit_ids, starter_id, command);
                    }
                }
                for unit in view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 0 && unit.id != starter_id)
                {
                    let Some(slot) = Self::unit_action_slot(&commands, &unit_ids, unit.id) else {
                        continue;
                    };
                    if bridge_funding {
                        if let Some(command) =
                            self.banana_factory_worker_three_mining_command(view, unit)
                        {
                            if !matches!(
                                command.split_whitespace().next().unwrap_or("WAIT"),
                                "MOVE" | "MINE" | "DROP"
                            ) {
                                self.banana_factory_worker_three_bridge_forbidden_commands += 1;
                            }
                            commands[slot] = command;
                            continue;
                        }
                    }
                    let verb = commands[slot].split_whitespace().next().unwrap_or("WAIT");
                    if matches!(verb, "PICK" | "PLANT" | "HARVEST" | "MINE") {
                        commands[slot] = self.banana_factory_wood_command(view, unit);
                        self.banana_factory_trained_role_rewrites += 1;
                    }
                }
                self.inner.regeneration_commitments.clear();
                self.inner.own_plant_attempts.clear();
                let bridge_train_now = self.banana_factory_worker_three_can_train(view);
                let priority = BTreeSet::from([starter_id]);
                let mut forbidden = self
                    .banana_factory_reserve
                    .map(|cell| BTreeSet::from([cell]))
                    .unwrap_or_default();
                if bridge_train_now {
                    forbidden.insert(view.shacks[0]);
                }
                MoisanBot::resolve_move_conflicts_with_priority_and_forbidden(
                    view,
                    &mut commands,
                    &priority,
                    &forbidden,
                );
                for unit in view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 0 && unit.id != starter_id)
                {
                    if let Some(slot) = Self::unit_action_slot(&commands, &unit_ids, unit.id) {
                        let verb = commands[slot].split_whitespace().next().unwrap_or("WAIT");
                        let allowed_bridge_mine = bridge_funding && verb == "MINE";
                        if matches!(verb, "PICK" | "PLANT" | "HARVEST" | "MINE")
                            && !allowed_bridge_mine
                        {
                            self.banana_factory_trained_forbidden_commands += 1;
                        }
                    }
                }
                if bridge_train_now {
                    let stats = Self::banana_factory_worker_three_stats();
                    commands.push(format!(
                        "TRAIN {} {} {} {}",
                        stats.movement_speed,
                        stats.carry_capacity,
                        stats.harvest_power,
                        stats.chop_power
                    ));
                    self.banana_factory_worker_three_bridge_train_attempts += 1;
                    self.banana_factory_worker_three_bridge_pending_train = Some((
                        view.turn,
                        view.units.iter().filter(|unit| unit.player == 0).count(),
                    ));
                }
                self.inner.remember_own_plant_attempts(view, &commands);
                commands
            }
        }

        #[cfg(test)]
        mod banana_ring_tests {
            use super::*;
            fn banana_ring_fixture() -> GameState {
                let mut view = GameState::empty(7, 7);
                view.shacks = [(3, 3), (6, 6)];
                view.walkable = (0..7)
                    .flat_map(|y| (0..7).map(move |x| (x, y)))
                    .filter(|cell| *cell != (3, 3) && *cell != (6, 6))
                    .collect();
                view.units.push(Unit {
                    id: 7,
                    player: 0,
                    cell: (2, 3),
                    stats: Stats {
                        movement_speed: 1,
                        carry_capacity: 1,
                        harvest_power: 1,
                        chop_power: 1,
                    },
                    carry: [0; 6],
                });
                view.units.push(Unit {
                    id: 8,
                    player: 0,
                    cell: (3, 2),
                    stats: Stats {
                        movement_speed: 2,
                        carry_capacity: 2,
                        harvest_power: 0,
                        chop_power: 2,
                    },
                    carry: [0; 6],
                });
                view
            }
            fn banana_ring_tree(cell: Cell, size: i32, fruits: i32) -> Plant {
                Plant {
                    kind: PlantKind::Banana,
                    cell,
                    size,
                    health: 2 + size,
                    fruits,
                    cooldown: 1,
                }
            }
            #[test]
            fn banana_ring_plant_target_never_leaves_ring() {
                let view = banana_ring_fixture();
                let bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                let target = bot.banana_ring_plant_cell(&view, view.unit(7).unwrap()).unwrap();
                assert!(bot.banana_ring_cells(&view).contains(&target));
                assert_eq!((target.0 - 3).abs().max((target.1 - 3).abs()), 1);
            }
            #[test]
            fn banana_ring_goal_caps_large_bank_at_capacity() {
                let mut view = banana_ring_fixture();
                view.inventories[0][BANANA] = 24;
                let mut bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                bot.initialize(&view);
                assert_eq!(bot.banana_ring_goal(&view), 8);
            }
            #[test]
            fn banana_ring_full_banks_surplus_and_never_picks() {
                let mut view = banana_ring_fixture();
                view.inventories[0][BANANA] = 24;
                let bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                for cell in bot.banana_ring_cells(&view).iter().copied() {
                    view.plants.push(banana_ring_tree(cell, 2, 0));
                }
                view.units[0].carry[BANANA] = 1;
                let mut bot = bot;
                bot.initialize(&view);
                let command = bot.banana_ring_starter_command(&view, view.unit(7).unwrap()).unwrap();
                assert!(command.starts_with("DROP ") || command.starts_with("MOVE "));
                assert!(!command.starts_with("PICK "));
                assert!(!command.contains("PLANT"));
            }
            #[test]
            fn banana_ring_pick_requires_target_within_two_move_turns() {
                let mut view = banana_ring_fixture();
                view.inventories[0][BANANA] = 3;
                view.units[0].cell = (0, 0);
                let ring_bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                for cell in ring_bot.banana_ring_cells(&view).iter().copied() {
                    if cell != (4, 4) {
                        view.plants.push(banana_ring_tree(cell, 2, 0));
                    }
                }
                let mut bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                bot.initialize(&view);
                let command = bot.banana_ring_starter_command(&view, view.unit(7).unwrap());
                assert!(!command.is_some_and(|command| command.starts_with("PICK ")));
            }
            #[test]
            fn banana_ring_near_mother_harvest_beats_pick() {
                let mut view = banana_ring_fixture();
                view.inventories[0][BANANA] = 3;
                view.plants.push(banana_ring_tree((2, 2), 4, 1));
                let mut bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                bot.initialize(&view);
                let command = bot.banana_ring_starter_command(&view, view.unit(7).unwrap()).unwrap();
                assert_eq!(command, "MOVE 7 2 2");
            }
            #[test]
            fn banana_ring_harvests_diagonal_not_orthogonal() {
                let mut view = banana_ring_fixture();
                view.plants.push(banana_ring_tree((2, 2), 4, 1));
                view.plants.push(banana_ring_tree((3, 2), 4, 3));
                let bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                assert_eq!(
                    bot.banana_ring_harvest_target(&view, view.unit(7).unwrap()).map(|pair| pair.0),
                    Some((2, 2))
                );
            }
            #[test]
            fn banana_ring_chops_size_two_orthogonal() {
                let mut view = banana_ring_fixture();
                view.plants.push(banana_ring_tree((3, 2), 2, 0));
                let mut bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                let command = bot.banana_ring_wood_command(&view, view.unit(8).unwrap());
                assert_eq!(command, "CHOP 8");
            }
            #[test]
            fn banana_ring_keeps_diagonal_before_release() {
                let mut view = banana_ring_fixture();
                view.units[1].cell = (2, 2);
                view.plants.push(banana_ring_tree((2, 2), 2, 0));
                let mut bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                let command = bot.banana_ring_wood_command(&view, view.unit(8).unwrap());
                assert_eq!(command, "WAIT");
            }
            #[test]
            fn banana_ring_releases_diagonal_in_endgame() {
                let mut view = banana_ring_fixture();
                view.turn = 270;
                view.units[1].cell = (2, 2);
                view.plants.push(banana_ring_tree((2, 2), 2, 0));
                let mut bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                assert_eq!(bot.banana_ring_wood_command(&view, view.unit(8).unwrap()), "CHOP 8");
            }
            #[test]
            fn banana_ring_releases_diagonal_under_local_raid() {
                let mut view = banana_ring_fixture();
                view.units[1].cell = (2, 2);
                view.plants.push(banana_ring_tree((2, 2), 2, 0));
                view.units.push(Unit {
                    id: 9,
                    player: 1,
                    cell: (4, 3),
                    stats: Stats { movement_speed: 1, carry_capacity: 1, harvest_power: 0, chop_power: 1 },
                    carry: [0; 6],
                });
                let mut bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                assert_eq!(bot.banana_ring_wood_command(&view, view.unit(8).unwrap()), "CHOP 8");
            }
            #[test]
            fn banana_ring_frontdoor_excludes_far_side() {
                let mut view = GameState::empty(11, 7);
                view.shacks = [(5, 2), (10, 2)];
                for x in 0..=4 {
                    for y in 0..=6 {
                        view.walkable.insert((x, y));
                    }
                }
                for x in 6..=10 {
                    for y in 0..=6 {
                        view.walkable.insert((x, y));
                    }
                }
                view.walkable.insert((5, 6));
                view.walkable.remove(&(10, 2));
                let bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                let ring = bot.banana_ring_cells(&view);
                assert!(ring.iter().all(|cell| cell.0 < 5));
                assert!(ring.contains(&(4, 2)));
            }
            #[test]
            fn banana_ring_eta6_opponent_crop_beats_orthogonal_cut() {
                let mut view = banana_ring_fixture();
                view.plants.push(banana_ring_tree((3, 2), 2, 0));
                view.plants.push(Plant {
                    kind: PlantKind::Plum,
                    cell: (0, 2),
                    size: 4,
                    health: 12,
                    fruits: 0,
                    cooldown: 1,
                });
                let mut bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                bot.inner.opponent_crops_seen = 1;
                bot.inner.opponent_crops.insert((0, 2));
                let command = bot.banana_ring_wood_command(&view, view.unit(8).unwrap());
                assert_eq!(command, "MOVE 8 0 2");
            }
            #[test]
            fn banana_ring_own_plant_is_not_opponent_provenance() {
                let mut view = banana_ring_fixture();
                let mut bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                bot.inner.reconcile_opponent_crops(&view);
                view.units[0].cell = (2, 3);
                bot.inner
                    .remember_own_plant_attempts(&view, &["PLANT 7 BANANA".to_string()]);
                view.turn += 1;
                view.plants.push(banana_ring_tree((2, 3), 1, 0));
                bot.inner.reconcile_opponent_crops(&view);
                assert!(!bot.inner.opponent_crops.contains(&(2, 3)));
                assert_eq!(bot.inner.opponent_crops_seen, 0);
            }
            #[test]
            fn banana_ring_clears_harvest_seed_after_observed_drop() {
                let view = banana_ring_fixture();
                let mut bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                bot.initialize(&view);
                bot.banana_factory_seed_from_harvest = true;
                bot.reconcile_banana_factory(&view);
                assert!(!bot.banana_factory_seed_from_harvest);
            }
            #[test]
            fn banana_ring_wrapper_regenerates_worker_command() {
                let mut view = banana_ring_fixture();
                view.plants.push(banana_ring_tree((4, 3), 2, 0));
                let mut expected_bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                expected_bot.initialize(&view);
                let expected = expected_bot.banana_ring_wood_command(&view, view.unit(8).unwrap());
                let mut wrapped = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                let commands = wrapped.commands(&view);
                let unit_ids = vec![7, 8];
                let slot = SecureOrchardBot::unit_action_slot(&commands, &unit_ids, 8).unwrap();
                assert_eq!(commands[slot], expected);
            }
            #[test]
            fn banana_ring_starter_never_chops_unripe_mother_before_release() {
                let mut view = banana_ring_fixture();
                view.units[0].cell = (2, 2);
                view.plants.push(banana_ring_tree((2, 2), 2, 0));
                let mut bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                let commands = bot.commands(&view);
                let slot = SecureOrchardBot::unit_action_slot(&commands, &[7, 8], 7).unwrap();
                assert_ne!(commands[slot], "CHOP 7");
            }
        }
        impl Bot for SecureOrchardBot {
            fn commands(&mut self, view: &GameState) -> Vec<String> {
                if !self.initialized {
                    self.initialize(view);
                }
                self.reconcile_initial_natural(view);
                let own_count = view.units.iter().filter(|unit| unit.player == 0).count();
                if self.banana_factory_enabled
                    && self.banana_factory_selector_enabled
                    && !self.banana_factory_selector_decided
                    && own_count >= 2
                {
                    self.banana_factory_selector_decided = true;
                    let live_plants: Vec<_> = view
                        .plants
                        .iter()
                        .filter(|plant| plant.health > 0)
                        .collect();
                    let fruits: i32 = live_plants.iter().map(|plant| plant.fruits).sum();
                    let banana_plants = live_plants
                        .iter()
                        .filter(|plant| plant.kind == PlantKind::Banana)
                        .count();
                    self.banana_factory_selector_selected =
                        live_plants.len() <= 20 && fruits >= 27 && banana_plants >= 6;
                }
                if self.banana_factory_enabled
                    && (!self.banana_factory_selector_enabled
                        || self.banana_factory_selector_selected)
                    && (self.banana_factory_active || own_count >= 2)
                {
                    return self.banana_factory_commands(view);
                }
                if let Some(geometry) = &self.geometry {
                    let mother_alive = view.plant_at(geometry.mother).is_some_and(|index| {
                        let plant = &view.plants[index];
                        plant.kind == PlantKind::Apple && plant.health > 0
                    });
                    if matches!(
                        self.phase,
                        OrchardPhase::CarryingSeed | OrchardPhase::Active
                    ) {
                        if mother_alive {
                            self.phase = OrchardPhase::Active;
                        } else if self.phase == OrchardPhase::Active || self.plant_attempted {
                            self.phase = OrchardPhase::Abandoned;
                        } else if !self
                            .starter_id
                            .and_then(|id| view.unit(id))
                            .is_some_and(|starter| self.can_continue_seed(view, starter, geometry))
                        {
                            self.phase = OrchardPhase::Abandoned;
                        }
                    }
                }
                let reserve_orchard = matches!(
                    self.phase,
                    OrchardPhase::CarryingSeed | OrchardPhase::Active
                );
                let market_active = self.task_market_enabled
                    && self.task_market_seed_repaid
                    && self.phase == OrchardPhase::Active;
                if market_active {
                    self.task_market_turns += 1;
                }
                self.inner.external_idle_unit = (reserve_orchard && !market_active)
                    .then_some(self.starter_id)
                    .flatten();
                self.inner.external_protected_tree = reserve_orchard
                    .then(|| self.geometry.as_ref().map(|geometry| geometry.mother))
                    .flatten();
                self.inner.external_orchard_task = market_active.then(|| {
                    (
                        self.starter_id.expect("active orchard starter"),
                        self.geometry
                            .as_ref()
                            .expect("active orchard geometry")
                            .mother,
                    )
                });
                let mut commands = self.inner.commands(view);
                let (Some(starter_id), Some(geometry)) = (self.starter_id, self.geometry.clone())
                else {
                    return commands;
                };
                let Some(starter) = view.unit(starter_id) else {
                    self.phase = OrchardPhase::Abandoned;
                    return commands;
                };
                let mut unit_ids: Vec<_> = view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 0)
                    .map(|unit| unit.id)
                    .collect();
                unit_ids.sort_unstable();
                let has_second = unit_ids.len() >= 2;
                let empty_on_door = starter.total_carried() == 0
                    && geometry.doors.iter().any(|door| *door == starter.cell);
                let checkpoint = empty_on_door;
                if self.phase == OrchardPhase::Dormant {
                    if view.turn > 100 {
                        self.phase = OrchardPhase::Abandoned;
                        return commands;
                    }
                    let starter_is_busy = self.require_idle_starter
                        && !Self::starter_control_is_idle(&commands, &unit_ids, starter);
                    if checkpoint
                        && has_second
                        && !starter_is_busy
                        && self.can_activate(view, starter, &geometry)
                    {
                        self.phase = OrchardPhase::CarryingSeed;
                    } else {
                        return commands;
                    }
                }
                if self.phase == OrchardPhase::Abandoned {
                    return commands;
                }
                let mother = view
                    .plant_at(geometry.mother)
                    .map(|index| &view.plants[index])
                    .filter(|plant| plant.kind == PlantKind::Apple && plant.health > 0);
                if mother.is_some() {
                    self.phase = OrchardPhase::Active;
                } else if self.phase == OrchardPhase::Active || self.plant_attempted {
                    self.phase = OrchardPhase::Abandoned;
                    return commands;
                }
                if market_active {
                    Self::protect_mother(
                        view,
                        &mut commands,
                        &unit_ids,
                        starter_id,
                        &geometry,
                        false,
                    );
                    let priority = self
                        .inner
                        .external_orchard_selected_this_turn
                        .then(|| BTreeSet::from([starter_id]))
                        .unwrap_or_default();
                    MoisanBot::resolve_move_conflicts_with_priority_and_forbidden(
                        view,
                        &mut commands,
                        &priority,
                        &BTreeSet::from([geometry.mother]),
                    );
                    self.inner.remember_own_plant_attempts(view, &commands);
                    return commands;
                }
                let forced = if let Some(mother) = mother {
                    if starter.cell != geometry.mother {
                        format!(
                            "MOVE {} {} {}",
                            starter.id, geometry.mother.0, geometry.mother.1
                        )
                    } else if starter.total_carried() > 0 {
                        format!("DROP {}", starter.id)
                    } else if mother.fruits > 0 && starter.free_capacity() > 0 {
                        format!("HARVEST {}", starter.id)
                    } else {
                        "WAIT".to_string()
                    }
                } else {
                    if !self.can_continue_seed(view, starter, &geometry) {
                        self.phase = OrchardPhase::Abandoned;
                        return commands;
                    }
                    if starter.carry[APPLE] > 0 {
                        if starter.cell == geometry.mother {
                            self.plant_attempted = true;
                            format!("PLANT {} APPLE", starter.id)
                        } else {
                            format!(
                                "MOVE {} {} {}",
                                starter.id, geometry.mother.0, geometry.mother.1
                            )
                        }
                    } else if starter.cell == geometry.mother {
                        format!("PICK {} APPLE", starter.id)
                    } else {
                        format!(
                            "MOVE {} {} {}",
                            starter.id, geometry.mother.0, geometry.mother.1
                        )
                    }
                };
                let repays_seed = self.task_market_enabled
                    && self.phase == OrchardPhase::Active
                    && starter.cell == geometry.mother
                    && starter.carry[APPLE] > 0
                    && forced.starts_with("DROP ");
                Self::replace_action(&mut commands, &unit_ids, starter_id, forced);
                if self.task_market_enabled {
                    self.task_market_activation_turn.get_or_insert(view.turn);
                    self.task_market_forced_setup_actions += 1;
                    if repays_seed {
                        self.task_market_seed_repaid = true;
                        self.task_market_seed_repaid_turn = Some(view.turn);
                    }
                }
                Self::protect_mother(
                    view,
                    &mut commands,
                    &unit_ids,
                    starter_id,
                    &geometry,
                    self.phase == OrchardPhase::CarryingSeed,
                );
                MoisanBot::resolve_move_conflicts_with_priority_and_forbidden(
                    view,
                    &mut commands,
                    &BTreeSet::from([starter_id]),
                    &BTreeSet::from([geometry.mother]),
                );
                self.inner.remember_own_plant_attempts(view, &commands);
                commands
            }
        }

        #[cfg(test)]
        mod crop_provenance_tests {
            use super::*;

            fn fixture() -> GameState {
                let mut view = GameState::empty(5, 5);
                view.shacks = [(0, 0), (4, 4)];
                view.walkable = (0..5).flat_map(|y| (0..5).map(move |x| (x, y))).collect();
                view.units.push(Unit {
                    id: 7,
                    player: 0,
                    cell: (1, 1),
                    stats: Stats {
                        movement_speed: 1,
                        carry_capacity: 1,
                        harvest_power: 1,
                        chop_power: 1,
                    },
                    carry: [0; 6],
                });
                view.plants.push(Plant {
                    kind: PlantKind::Plum,
                    cell: (2, 2),
                    size: 2,
                    health: 2,
                    fruits: 1,
                    cooldown: 0,
                });
                view
            }

            #[test]
            fn initial_natural_trees_are_not_opponent_crops() {
                let view = fixture();
                let mut bot = YamoBot::tuned_carry_regeneration_transit_idle_harvest();
                bot.reconcile_opponent_crops(&view);
                assert_eq!(bot.opponent_crops_seen, 0);
                assert!(bot.opponent_crops.is_empty());
            }

            #[test]
            fn newly_appeared_unattributed_tree_is_an_opponent_crop() {
                let mut view = fixture();
                let mut bot = YamoBot::tuned_carry_regeneration_transit_idle_harvest();
                bot.reconcile_opponent_crops(&view);
                view.turn += 1;
                view.plants.push(Plant {
                    kind: PlantKind::Apple,
                    cell: (3, 3),
                    size: 1,
                    health: 1,
                    fruits: 0,
                    cooldown: 0,
                });
                bot.reconcile_opponent_crops(&view);
                assert_eq!(bot.opponent_crops_seen, 1);
                assert_eq!(bot.opponent_crops, BTreeSet::from([(3, 3)]));
            }

            #[test]
            fn own_plant_attempt_excludes_the_new_tree_from_opponent_provenance() {
                let mut view = fixture();
                let mut bot = YamoBot::tuned_carry_regeneration_transit_idle_harvest();
                bot.reconcile_opponent_crops(&view);
                bot.remember_own_plant_attempts(&view, &["PLANT 7 APPLE".to_string()]);
                view.turn += 1;
                view.plants.push(Plant {
                    kind: PlantKind::Apple,
                    cell: (1, 1),
                    size: 1,
                    health: 1,
                    fruits: 0,
                    cooldown: 0,
                });
                bot.reconcile_opponent_crops(&view);
                assert_eq!(bot.opponent_crops_seen, 0);
                assert!(bot.opponent_crops.is_empty());
            }

            #[test]
            fn dual_value_counts_opponent_crop_conversion_once_more() {
                let view = fixture();
                let unit = view.unit(7).unwrap();
                let mut bot = YamoBot::tuned_carry_regeneration_transit_idle_harvest();
                bot.opponent_crop_dual_value = true;
                bot.opponent_crop_eta_limit = 6;
                bot.opponent_crop_start_turn = 1;
                bot.opponent_crop_min_seen = 1;
                bot.opponent_crops_seen = 1;
                bot.opponent_crops.insert((2, 2));
                let mut candidates = vec![Candidate {
                    command: "MOVE 7 2 2".to_string(),
                    score: 125.0,
                    target: Target::Tree((2, 2)),
                }];
                bot.apply_opponent_crop_priority(&view, unit, &mut candidates);
                assert_eq!(candidates[0].score, 250.0);
            }

            #[test]
            fn orchard_market_prices_one_door_apple_as_quarter_wood() {
                let mut view = fixture();
                view.units[0].cell = (1, 0);
                view.plants.push(Plant {
                    kind: PlantKind::Apple,
                    cell: (1, 0),
                    size: 4,
                    health: 20,
                    fruits: 1,
                    cooldown: 1,
                });
                let candidate = YamoBot::external_orchard_candidate(&view, &view.units[0], (1, 0))
                    .expect("ripe bankable mother task");
                assert_eq!(candidate.command, "HARVEST 7");
                assert_eq!(candidate.target, Target::Tree((1, 0)));
                assert_eq!(candidate.score, 125.0);

                view.units[0].carry[WOOD] = 1;
                assert!(
                    YamoBot::external_orchard_candidate(&view, &view.units[0], (1, 0)).is_none()
                );
            }

            #[test]
            fn fresh_harvest_commitment_is_disabled_by_default_and_pick_is_unchanged() {
                let mut view = fixture();
                view.plants[0].cell = view.units[0].cell;
                let mut bot = YamoBot::tuned_carry_regeneration_transit_idle_harvest();
                bot.remember_selected_regeneration(&view, &["HARVEST 7".to_string()]);
                assert!(bot.regeneration_commitments.is_empty());
                assert_eq!(bot.fresh_harvest_commitments, 0);

                bot.remember_selected_regeneration(&view, &["PICK 7 PLUM".to_string()]);
                assert_eq!(bot.regeneration_commitments.get(&7), Some(&PlantKind::Plum));
                assert_eq!(bot.fresh_harvest_commitments, 0);
            }

            #[test]
            fn eligible_fresh_harvest_creates_one_species_commitment() {
                let mut view = fixture();
                view.plants[0].cell = view.units[0].cell;
                let mut bot = YamoBot::tuned_carry_regeneration_transit_idle_harvest();
                bot.fresh_harvest_regeneration = true;
                bot.remember_selected_regeneration(&view, &["HARVEST 7".to_string()]);
                assert_eq!(bot.regeneration_commitments.get(&7), Some(&PlantKind::Plum));
                assert_eq!(bot.fresh_harvest_units, BTreeSet::from([7]));
                assert_eq!(bot.fresh_harvest_commitments, 1);
                assert_eq!(bot.fresh_harvest_first_turn, Some(view.turn));

                bot.remember_selected_regeneration(&view, &["HARVEST 7".to_string()]);
                assert_eq!(bot.fresh_harvest_commitments, 1);
            }

            #[test]
            fn protected_or_unripe_harvest_does_not_create_commitment() {
                let mut view = fixture();
                view.plants[0].cell = view.units[0].cell;
                let mut protected = YamoBot::tuned_carry_regeneration_transit_idle_harvest();
                protected.fresh_harvest_regeneration = true;
                protected.external_protected_tree = Some(view.units[0].cell);
                protected.remember_selected_regeneration(&view, &["HARVEST 7".to_string()]);
                assert!(protected.regeneration_commitments.is_empty());

                let mut unripe = YamoBot::tuned_carry_regeneration_transit_idle_harvest();
                unripe.fresh_harvest_regeneration = true;
                view.plants[0].fruits = 0;
                unripe.remember_selected_regeneration(&view, &["HARVEST 7".to_string()]);
                assert!(unripe.regeneration_commitments.is_empty());
            }

            #[test]
            fn harvested_carried_fruit_reuses_existing_regeneration_candidates() {
                let mut view = fixture();
                view.plants[0].cell = view.units[0].cell;
                let mut bot = YamoBot::tuned_carry_regeneration_transit_idle_harvest();
                bot.fresh_harvest_regeneration = true;
                bot.remember_selected_regeneration(&view, &["HARVEST 7".to_string()]);
                view.turn += 1;
                view.units[0].carry[PLUM] = 1;
                bot.reconcile_regeneration_commitments(&view);
                let candidates =
                    YamoBot::endgame_candidates(&view, &view.units[0], None, true, None, 0);
                assert!(candidates.iter().any(|candidate| {
                    candidate.command.starts_with("MOVE 7 ") || candidate.command == "PLANT 7 PLUM"
                }));
            }

            fn add_factory_worker(view: &mut GameState) {
                view.units.push(Unit {
                    id: 8,
                    player: 0,
                    cell: (2, 1),
                    stats: Stats {
                        movement_speed: 2,
                        carry_capacity: 2,
                        harvest_power: 0,
                        chop_power: 2,
                    },
                    carry: [0; 6],
                });
            }

            #[test]
            fn banana_factory_is_disabled_by_default_and_preactivation_is_exact() {
                let mut view = fixture();
                view.inventories[0][BANANA] = 3;
                view.units[0].cell = (1, 0);
                let mut control = SecureOrchardBot::new();
                let mut candidate = SecureOrchardBot::banana_seed_factory();
                assert!(!control.banana_factory_enabled);
                assert_eq!(control.commands(&view), candidate.commands(&view));
                assert!(!candidate.banana_seed_factory_telemetry().active);
            }

            #[test]
            fn banana_factory_activates_on_observed_worker_two_and_picks_bank_seed() {
                let mut view = fixture();
                view.inventories[0][BANANA] = 3;
                view.units[0].cell = (1, 0);
                add_factory_worker(&mut view);
                let mut candidate = SecureOrchardBot::banana_seed_factory();
                let commands = candidate.commands(&view);
                assert!(commands.iter().any(|command| command == "PICK 7 BANANA"));
                let telemetry = candidate.banana_seed_factory_telemetry();
                assert!(telemetry.active);
                assert_eq!(telemetry.activation_turn, Some(1));
                assert_eq!(telemetry.initial_budget, 3);
            }

            #[test]
            fn banana_factory_reconciles_successful_and_failed_bootstrap_plants() {
                let mut view = fixture();
                view.inventories[0][BANANA] = 1;
                let mut success = SecureOrchardBot::banana_seed_factory();
                success.initialize(&view);
                success.banana_factory_pending_plant =
                    Some((1, (1, 1), BananaFactoryPlantSource::BankBootstrap, 1));
                view.turn = 2;
                view.units[0].carry[BANANA] = 0;
                view.plants.push(Plant {
                    kind: PlantKind::Banana,
                    cell: (1, 1),
                    size: 1,
                    health: 3,
                    fruits: 0,
                    cooldown: 6,
                });
                success.reconcile_banana_factory(&view);
                assert_eq!(success.banana_factory_bootstrap_successes, 1);
                assert_eq!(success.banana_factory_reserve, Some((1, 1)));

                let mut failure_view = fixture();
                failure_view.inventories[0][BANANA] = 1;
                let mut failure = SecureOrchardBot::banana_seed_factory();
                failure.initialize(&failure_view);
                failure.banana_factory_pending_plant =
                    Some((1, (1, 1), BananaFactoryPlantSource::BankBootstrap, 1));
                failure_view.turn = 2;
                failure_view.units[0].carry[BANANA] = 1;
                failure_view.plants.push(Plant {
                    kind: PlantKind::Banana,
                    cell: (1, 1),
                    size: 1,
                    health: 3,
                    fruits: 0,
                    cooldown: 6,
                });
                failure.reconcile_banana_factory(&failure_view);
                assert_eq!(failure.banana_factory_bootstrap_successes, 0);
                assert!(failure.banana_factory_owned_crops.is_empty());
            }

            #[test]
            fn banana_factory_promotes_bank_crop_then_live_replacement() {
                let mut view = fixture();
                view.plants.push(Plant {
                    kind: PlantKind::Banana,
                    cell: (1, 1),
                    size: 2,
                    health: 4,
                    fruits: 0,
                    cooldown: 3,
                });
                view.plants.push(Plant {
                    kind: PlantKind::Banana,
                    cell: (3, 3),
                    size: 2,
                    health: 4,
                    fruits: 0,
                    cooldown: 3,
                });
                let mut bot = SecureOrchardBot::banana_seed_factory();
                bot.initialize(&view);
                bot.banana_factory_owned_crops.insert((1, 1), false);
                bot.banana_factory_owned_crops.insert((3, 3), true);
                bot.banana_factory_promote_reserve(&view);
                assert_eq!(bot.banana_factory_reserve, Some((3, 3)));
                view.plants.retain(|plant| plant.cell != (3, 3));
                bot.reconcile_banana_factory(&view);
                assert_eq!(bot.banana_factory_reserve, Some((1, 1)));
                assert_eq!(bot.banana_factory_reserve_losses, 1);
            }

            #[test]
            fn source_separated_factory_excludes_ordinary_conversion_harvests() {
                let mut view = fixture();
                view.plants.clear();
                view.plants.push(Plant {
                    kind: PlantKind::Banana,
                    cell: (4, 3),
                    size: 4,
                    health: 6,
                    fruits: 0,
                    cooldown: 3,
                });
                view.plants.push(Plant {
                    kind: PlantKind::Banana,
                    cell: (1, 2),
                    size: 4,
                    health: 6,
                    fruits: 1,
                    cooldown: 1,
                });
                let starter = view.unit(7).unwrap();

                let mut full = SecureOrchardBot::banana_seed_factory();
                full.banana_factory_owned_crops.insert((4, 3), true);
                full.banana_factory_owned_crops.insert((1, 2), false);
                full.banana_factory_reserve = Some((4, 3));
                assert_eq!(
                    full.banana_factory_harvest_target(&view, starter),
                    Some(((1, 2), false))
                );

                let mut separated = SecureOrchardBot::banana_seed_factory_source_separated();
                separated.banana_factory_owned_crops.insert((4, 3), true);
                separated.banana_factory_owned_crops.insert((1, 2), false);
                separated.banana_factory_reserve = Some((4, 3));
                assert_eq!(
                    separated.banana_factory_harvest_target(&view, starter),
                    None
                );
            }

            #[test]
            fn source_separated_factory_can_harvest_promoted_conversion_reserve() {
                let mut view = fixture();
                view.plants[0] = Plant {
                    kind: PlantKind::Banana,
                    cell: (2, 2),
                    size: 4,
                    health: 6,
                    fruits: 1,
                    cooldown: 1,
                };
                let starter = view.unit(7).unwrap();
                let mut bot = SecureOrchardBot::banana_seed_factory_source_separated();
                bot.banana_factory_owned_crops.insert((2, 2), false);
                bot.banana_factory_reserve = Some((2, 2));
                assert_eq!(
                    bot.banana_factory_harvest_target(&view, starter),
                    Some(((2, 2), false))
                );
            }

            fn selector_fixture() -> GameState {
                let mut view = fixture();
                view.units[0].cell = (1, 0);
                view.inventories[0][BANANA] = 3;
                add_factory_worker(&mut view);
                view.plants.clear();
                for (index, cell) in [(1, 1), (2, 1), (3, 1), (1, 2), (2, 2), (3, 2)]
                    .into_iter()
                    .enumerate()
                {
                    view.plants.push(Plant {
                        kind: PlantKind::Banana,
                        cell,
                        size: 4,
                        health: 6,
                        fruits: if index == 0 { 7 } else { 4 },
                        cooldown: 1,
                    });
                }
                view
            }

            #[test]
            fn activation_selector_selects_exact_frozen_resource_boundary() {
                let view = selector_fixture();
                let mut bot = SecureOrchardBot::banana_seed_factory_activation_selector();
                let commands = bot.commands(&view);
                let telemetry = bot.banana_seed_factory_telemetry();
                assert!(telemetry.selector_decided);
                assert!(telemetry.selector_selected);
                assert!(telemetry.active);
                assert!(commands.iter().any(|command| command == "PICK 7 BANANA"));
            }

            #[test]
            fn activation_selector_abstention_remains_resident_exact() {
                let mut view = selector_fixture();
                view.plants[0].fruits -= 1;
                let mut control = SecureOrchardBot::new();
                let mut candidate = SecureOrchardBot::banana_seed_factory_activation_selector();
                assert_eq!(control.commands(&view), candidate.commands(&view));
                let telemetry = candidate.banana_seed_factory_telemetry();
                assert!(telemetry.selector_decided);
                assert!(!telemetry.selector_selected);
                assert!(!telemetry.active);

                view.turn += 1;
                assert_eq!(control.commands(&view), candidate.commands(&view));
                assert!(!candidate.banana_seed_factory_telemetry().active);
            }

            #[test]
            fn banana_factory_persists_harvest_into_renewable_plant_task() {
                let mut view = fixture();
                view.inventories[0][BANANA] = 0;
                view.units[0].cell = (2, 2);
                view.plants[0] = Plant {
                    kind: PlantKind::Banana,
                    cell: (2, 2),
                    size: 4,
                    health: 6,
                    fruits: 1,
                    cooldown: 1,
                };
                add_factory_worker(&mut view);
                let mut bot = SecureOrchardBot::banana_seed_factory();
                bot.banana_factory_owned_crops.insert((2, 2), true);
                bot.banana_factory_reserve = Some((2, 2));
                let first = bot.commands(&view);
                assert!(first.iter().any(|command| command == "HARVEST 7"));
                view.turn = 2;
                view.units[0].carry[BANANA] = 1;
                view.plants[0].fruits = 0;
                let second = bot.commands(&view);
                assert!(second.iter().any(|command| {
                    command.starts_with("MOVE 7 ") || command == "PLANT 7 BANANA"
                }));
                assert_eq!(
                    bot.banana_seed_factory_telemetry()
                        .own_crop_harvest_successes,
                    1
                );
                assert!(bot.banana_factory_seed_from_harvest);
            }

            #[test]
            fn banana_factory_trained_role_emits_only_wood_or_logistics() {
                let mut view = fixture();
                add_factory_worker(&mut view);
                let mut bot = SecureOrchardBot::banana_seed_factory();
                bot.initialize(&view);
                let worker = view.unit(8).unwrap();
                let command = bot.banana_factory_wood_command(&view, worker);
                let verb = command.split_whitespace().next().unwrap();
                assert!(matches!(verb, "MOVE" | "CHOP" | "DROP" | "WAIT"));
            }

            #[test]
            fn worker_three_bridge_targets_largest_existing_fruit_deficit() {
                let mut view = fixture();
                add_factory_worker(&mut view);
                view.inventories[0][PLUM] = 5;
                view.inventories[0][LEMON] = 0;
                view.inventories[0][APPLE] = 0;
                view.plants.push(Plant {
                    kind: PlantKind::Lemon,
                    cell: (3, 2),
                    size: 4,
                    health: 12,
                    fruits: 2,
                    cooldown: 1,
                });
                view.plants.push(Plant {
                    kind: PlantKind::Apple,
                    cell: (3, 3),
                    size: 4,
                    health: 20,
                    fruits: 2,
                    cooldown: 1,
                });
                assert_eq!(
                    SecureOrchardBot::banana_factory_worker_three_fruit_target(
                        &view,
                        view.unit(7).unwrap(),
                    ),
                    Some(((3, 2), LEMON))
                );
            }

            #[test]
            fn worker_three_bridge_mines_and_trains_only_from_deposited_bill() {
                let mut mining_view = fixture();
                add_factory_worker(&mut mining_view);
                mining_view.iron.insert((2, 2));
                let mut mining = SecureOrchardBot::banana_seed_factory_worker_three_bridge();
                let mine = mining
                    .banana_factory_worker_three_mining_command(
                        &mining_view,
                        mining_view.unit(8).unwrap(),
                    )
                    .expect("reachable iron command");
                assert_eq!(mine, "MINE 8");
                assert_eq!(
                    mining
                        .banana_seed_factory_telemetry()
                        .worker_three_bridge_iron_mine_selections,
                    1
                );

                let mut funded = mining_view;
                funded.turn = 50;
                funded.inventories[0][PLUM] = 6;
                funded.inventories[0][LEMON] = 6;
                funded.inventories[0][APPLE] = 2;
                funded.inventories[0][IRON] = 6;
                let mut bridge = SecureOrchardBot::banana_seed_factory_worker_three_bridge();
                let commands = bridge.commands(&funded);
                assert!(commands.iter().any(|command| command == "TRAIN 2 2 0 2"));
                let telemetry = bridge.banana_seed_factory_telemetry();
                assert_eq!(telemetry.worker_three_bridge_train_attempts, 1);
                assert_eq!(telemetry.worker_three_bridge_forbidden_commands, 0);
            }

            #[test]
            fn dual_value_factory_applies_opponent_provenance_to_trained_wood() {
                let mut view = fixture();
                add_factory_worker(&mut view);
                let mut bot = SecureOrchardBot::banana_seed_factory_dual_value_e6();
                bot.initialize(&view);
                bot.inner.opponent_crops_seen = 1;
                bot.inner.opponent_crops.insert((2, 2));
                let worker = view.unit(8).unwrap();
                let command = bot.banana_factory_wood_command(&view, worker);
                assert!(command == "MOVE 8 2 2" || command == "CHOP 8");
                assert_eq!(
                    bot.banana_seed_factory_telemetry()
                        .trained_opponent_crop_selections,
                    1
                );
            }

            #[test]
            fn trained_only_dual_value_does_not_modify_starter_inner_policy() {
                let mut view = fixture();
                add_factory_worker(&mut view);
                let mut bot = SecureOrchardBot::banana_seed_factory_trained_dual_value_e6();
                bot.initialize(&view);
                assert!(!bot.inner.opponent_crop_dual_value);
                bot.inner.opponent_crops_seen = 1;
                bot.inner.opponent_crops.insert((2, 2));
                let worker = view.unit(8).unwrap();
                let command = bot.banana_factory_wood_command(&view, worker);
                assert!(command == "MOVE 8 2 2" || command == "CHOP 8");
                assert_eq!(
                    bot.banana_seed_factory_telemetry()
                        .trained_opponent_crop_selections,
                    1
                );
                assert_eq!(bot.inner.opponent_crop_selected, 0);
            }
        }
    }
    use super::game::GameState;
    pub trait Bot {
        fn commands(&mut self, view: &GameState) -> Vec<String>;
    }
}
use self::bot::moisan::SecureOrchardBot;
use self::bot::Bot;
use self::game::protocol::{read_static_map, read_turn};
use std::io::{self, Write};
fn main() {
    let stdin = io::stdin();
    let stdout = io::stdout();
    let mut reader = io::BufReader::new(stdin.lock());
    let mut out = io::BufWriter::new(stdout.lock());
    let Some(map) = read_static_map(&mut reader) else {
        return;
    };
    let mut bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
    let mut turn = 1;
    while let Some(view) = read_turn(&mut reader, &map, turn) {
        let commands = bot.commands(&view);
        writeln!(out, "{}", commands.join(";")).expect("write command line");
        out.flush().expect("flush command line");
        turn += 1;
    }
}
