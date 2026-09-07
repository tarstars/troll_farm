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
    pub use types::GameState;
