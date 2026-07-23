//! Behavioral port of the Legend-league referee map generator.
//!
//! The implementation follows `engine.Board.createMap` from Troll Farm referee
//! commit `290129129db7a7539d98739ebdb0ed63ee6ceb50`, driven by the SUN SHA1PRNG
//! supplied by game-engine 4.7.8.  It deliberately lives beside the historical
//! synthetic generator: old experiments keep their old maps, while new
//! experiments can opt into the official seed semantics.

use super::engine::{plant_cooldown, tree_health, tree_health_params, water_boost};
use super::state::{Cell, GameState, Plant, Unit};
use std::collections::{HashSet, VecDeque};

const FRUITS: [&str; 4] = ["PLUM", "LEMON", "APPLE", "BANANA"];
const MAX_SIZE: i32 = 4;
const MAX_RESOURCES: i32 = 3;
const MAX_OPPONENT_DISTANCE: i32 = 16;
const NEIGHBORS: [(i32, i32); 4] = [(0, 1), (1, 0), (0, -1), (-1, 0)];

fn sha1(input: &[u8]) -> [u8; 20] {
    let bit_length = (input.len() as u64) * 8;
    let mut padded = input.to_vec();
    padded.push(0x80);
    while padded.len() % 64 != 56 {
        padded.push(0);
    }
    padded.extend(bit_length.to_be_bytes());

    let mut hash = [
        0x6745_2301_u32,
        0xefcd_ab89,
        0x98ba_dcfe,
        0x1032_5476,
        0xc3d2_e1f0,
    ];
    for chunk in padded.chunks_exact(64) {
        let mut words = [0_u32; 80];
        for (index, word) in words.iter_mut().take(16).enumerate() {
            let start = index * 4;
            *word = u32::from_be_bytes(chunk[start..start + 4].try_into().unwrap());
        }
        for index in 16..80 {
            words[index] =
                (words[index - 3] ^ words[index - 8] ^ words[index - 14] ^ words[index - 16])
                    .rotate_left(1);
        }

        let [mut a, mut b, mut c, mut d, mut e] = hash;
        for (index, &word) in words.iter().enumerate() {
            let (function, constant) = match index {
                0..=19 => ((b & c) | ((!b) & d), 0x5a82_7999),
                20..=39 => (b ^ c ^ d, 0x6ed9_eba1),
                40..=59 => ((b & c) | (b & d) | (c & d), 0x8f1b_bcdc),
                _ => (b ^ c ^ d, 0xca62_c1d6),
            };
            let next = a
                .rotate_left(5)
                .wrapping_add(function)
                .wrapping_add(e)
                .wrapping_add(constant)
                .wrapping_add(word);
            e = d;
            d = c;
            c = b.rotate_left(30);
            b = a;
            a = next;
        }
        for (slot, value) in hash.iter_mut().zip([a, b, c, d, e]) {
            *slot = slot.wrapping_add(value);
        }
    }

    let mut output = [0_u8; 20];
    for (index, value) in hash.iter().enumerate() {
        output[index * 4..index * 4 + 4].copy_from_slice(&value.to_be_bytes());
    }
    output
}

/// SUN's Java 17 `SHA1PRNG`, exposed by game-engine 4.7.8 as a `Random`.
#[derive(Clone, Debug)]
pub struct Sha1Prng {
    state: [u8; 20],
    remainder: [u8; 20],
    remainder_count: usize,
}

impl Sha1Prng {
    pub fn new(seed: i64) -> Self {
        assert_ne!(
            seed, 0,
            "OpenJDK ignores setSeed(0) and therefore cannot generate a deterministic official map"
        );
        Self {
            state: sha1(&(seed as u64).to_le_bytes()),
            remainder: [0; 20],
            remainder_count: 0,
        }
    }

    fn update_state(&mut self, output: &[u8; 20]) {
        let mut carry = 1_i32;
        let mut changed = false;
        for (state, &generated) in self.state.iter_mut().zip(output) {
            let value = i32::from(*state as i8) + i32::from(generated as i8) + carry;
            let next = value as i8 as u8;
            changed |= *state != next;
            *state = next;
            carry = value >> 8;
        }
        if !changed {
            self.state[0] = self.state[0].wrapping_add(1);
        }
    }

    fn next_bytes(&mut self, result: &mut [u8]) {
        let mut index = 0;
        if self.remainder_count > 0 {
            let available = 20 - self.remainder_count;
            let count = result.len().min(available);
            for output in result.iter_mut().take(count) {
                *output = self.remainder[self.remainder_count];
                self.remainder[self.remainder_count] = 0;
                self.remainder_count += 1;
            }
            index += count;
        }
        while index < result.len() {
            let mut output = sha1(&self.state);
            self.update_state(&output);
            let count = (result.len() - index).min(20);
            result[index..index + count].copy_from_slice(&output[..count]);
            output[..count].fill(0);
            self.remainder = output;
            self.remainder_count += count;
            index += count;
        }
        self.remainder_count %= 20;
    }

    fn next(&mut self, bits: u32) -> u32 {
        assert!(bits <= 32);
        let byte_count = bits.div_ceil(8) as usize;
        let mut bytes = [0_u8; 4];
        self.next_bytes(&mut bytes[..byte_count]);
        let mut value = 0_u32;
        for &byte in &bytes[..byte_count] {
            value = (value << 8) | u32::from(byte);
        }
        value >> (byte_count as u32 * 8 - bits)
    }

    /// Java's `Random.nextInt(bound)` for a positive bound.
    pub fn next_int(&mut self, bound: i32) -> i32 {
        assert!(bound > 0, "Java Random bound must be positive");
        if bound & -bound == bound {
            return ((i64::from(bound) * i64::from(self.next(31))) >> 31) as i32;
        }
        loop {
            let bits = self.next(31) as i32;
            let value = bits % bound;
            // The Java loop retries exactly when this signed-i32 expression
            // overflows negative.
            if bits.wrapping_sub(value).wrapping_add(bound - 1) >= 0 {
                return value;
            }
        }
    }

    /// Java 17's `Random.nextInt(origin, bound)` for this generator's small ranges.
    pub fn next_int_range(&mut self, origin: i32, bound: i32) -> i32 {
        assert!(origin < bound, "Java Random range must be non-empty");
        origin + self.next_int(bound - origin)
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum Terrain {
    Grass,
    Water,
    Rock,
    Iron,
    Shack,
}

struct Draft {
    width: i32,
    height: i32,
    terrain: Vec<Terrain>,
    plants: Vec<Plant>,
}

impl Draft {
    fn new(width: i32, height: i32) -> Self {
        Self {
            width,
            height,
            terrain: vec![Terrain::Grass; (width * height) as usize],
            plants: Vec::new(),
        }
    }

    fn index(&self, cell: Cell) -> usize {
        (cell.1 * self.width + cell.0) as usize
    }

    fn terrain(&self, cell: Cell) -> Terrain {
        self.terrain[self.index(cell)]
    }

    fn set_single(&mut self, cell: Cell, terrain: Terrain) {
        let index = self.index(cell);
        self.terrain[index] = terrain;
    }

    fn mirror(&self, cell: Cell) -> Cell {
        (self.width - 1 - cell.0, self.height - 1 - cell.1)
    }

    fn set_symmetric(&mut self, cell: Cell, terrain: Terrain) {
        let mirror = self.mirror(cell);
        self.set_single(cell, terrain);
        self.set_single(mirror, terrain);
    }

    fn neighbor(&self, cell: Cell, direction: usize) -> Option<Cell> {
        let delta = NEIGHBORS[direction];
        let next = (cell.0 + delta.0, cell.1 + delta.1);
        (next.0 >= 0 && next.0 < self.width && next.1 >= 0 && next.1 < self.height).then_some(next)
    }

    fn neighbors(&self, cell: Cell) -> impl Iterator<Item = Cell> + '_ {
        (0..4).filter_map(move |direction| self.neighbor(cell, direction))
    }

    fn near_edge(&self, cell: Cell) -> bool {
        cell.0 == 0 || cell.1 == 0 || cell.0 == self.width - 1 || cell.1 == self.height - 1
    }

    fn has_plant(&self, cell: Cell) -> bool {
        self.plants.iter().any(|plant| plant.pos() == cell)
    }

    fn random_grass(&self, random: &mut Sha1Prng) -> Cell {
        loop {
            let cell = (random.next_int(self.width), random.next_int(self.height));
            if self.terrain(cell) == Terrain::Grass && !self.has_plant(cell) {
                return cell;
            }
        }
    }

    fn near_type(&self, cell: Cell, terrain: Terrain) -> bool {
        self.neighbors(cell)
            .any(|neighbor| self.terrain(neighbor) == terrain)
    }

    fn growth_cooldown(&self, cell: Cell, plant_type: &str) -> i32 {
        let mut cooldown = plant_cooldown(plant_type);
        if self.near_type(cell, Terrain::Water) {
            cooldown -= water_boost(plant_type);
        }
        cooldown
    }

    fn age_plant(&self, plant: &mut Plant, ticks: i32) {
        let growth_cooldown = self.growth_cooldown(plant.pos(), &plant.plant_type);
        let health_delta = tree_health_params(&plant.plant_type).1;
        for _ in 0..ticks {
            if plant.cooldown > 0 {
                plant.cooldown -= 1;
            }
            if plant.cooldown == 0 && plant.health > 0 {
                if plant.size < MAX_SIZE {
                    plant.size += 1;
                    plant.health += health_delta;
                    plant.cooldown = growth_cooldown;
                } else if plant.fruits < MAX_RESOURCES {
                    plant.fruits += 1;
                    plant.cooldown = growth_cooldown;
                }
            }
        }
    }

    fn place_terrain(
        &mut self,
        random: &mut Sha1Prng,
        terrain: Terrain,
        minimum: i32,
        maximum: i32,
    ) {
        let count = random.next_int(maximum - minimum + 1) + minimum;
        for _ in 0..count {
            let cell = self.random_grass(random);
            self.set_symmetric(cell, terrain);
        }
    }

    fn place_trees(
        &mut self,
        random: &mut Sha1Prng,
        plant_type: &'static str,
        minimum: i32,
        maximum: i32,
    ) {
        let count = random.next_int(maximum - minimum + 1) + minimum;
        for _ in 0..count {
            let cell = self.random_grass(random);
            let cooldown = self.growth_cooldown(cell, plant_type);
            let ticks = random.next_int_range(1, cooldown * (MAX_SIZE + MAX_RESOURCES));

            let mut plant = Plant {
                plant_type: plant_type.to_owned(),
                x: cell.0,
                y: cell.1,
                size: 0,
                health: tree_health(plant_type, 0),
                fruits: 0,
                cooldown: 0,
            };
            self.age_plant(&mut plant, ticks);
            self.plants.push(plant);

            let mirror = self.mirror(cell);
            if mirror == cell {
                return;
            }
            let mut plant = Plant {
                plant_type: plant_type.to_owned(),
                x: mirror.0,
                y: mirror.1,
                size: 0,
                health: tree_health(plant_type, 0),
                fruits: 0,
                cooldown: 0,
            };
            self.age_plant(&mut plant, ticks);
            self.plants.push(plant);
        }
    }

    fn distances(&self, start: Cell) -> Vec<i32> {
        let mut distance = vec![-1; self.terrain.len()];
        let mut queue = VecDeque::new();
        distance[self.index(start)] = 0;
        queue.push_back(start);
        while let Some(cell) = queue.pop_front() {
            let next_distance = distance[self.index(cell)] + 1;
            for neighbor in self.neighbors(cell) {
                let index = self.index(neighbor);
                if self.terrain(neighbor) == Terrain::Grass && distance[index] == -1 {
                    distance[index] = next_distance;
                    queue.push_back(neighbor);
                }
            }
        }
        distance
    }

    fn valid(&self, shacks: [Cell; 2]) -> bool {
        if self.near_type(shacks[0], Terrain::Iron) {
            return false;
        }
        if !self
            .neighbors(shacks[0])
            .any(|cell| self.terrain(cell) == Terrain::Grass)
        {
            return false;
        }

        let mut walkable = Vec::new();
        let mut iron = Vec::new();
        // Java iterates x first, then y.
        for x in 0..self.width {
            for y in 0..self.height {
                let cell = (x, y);
                match self.terrain(cell) {
                    Terrain::Grass => walkable.push(cell),
                    Terrain::Iron => iron.push(cell),
                    _ => {}
                }
            }
        }
        let can_reach_iron = iron.iter().any(|&cell| {
            self.neighbors(cell)
                .any(|neighbor| self.terrain(neighbor) == Terrain::Grass)
        });
        if !can_reach_iron || walkable.is_empty() {
            return false;
        }

        let connected = self.distances(walkable[0]);
        if walkable
            .iter()
            .any(|&cell| connected[self.index(cell)] == -1)
        {
            return false;
        }

        let shack_distance = self.distances(shacks[0]);
        let opponent_distance = self
            .neighbors(shacks[1])
            .filter(|&cell| self.terrain(cell) == Terrain::Grass)
            .map(|cell| shack_distance[self.index(cell)] + 1)
            .min()
            .unwrap_or(i32::MAX);
        opponent_distance <= MAX_OPPONENT_DISTANCE
    }

    fn finish(self, shacks: [Cell; 2], inventory: [i32; 6]) -> GameState {
        let mut walkable = HashSet::new();
        let mut iron = HashSet::new();
        let mut water = HashSet::new();
        for x in 0..self.width {
            for y in 0..self.height {
                let cell = (x, y);
                match self.terrain(cell) {
                    Terrain::Grass => {
                        walkable.insert(cell);
                    }
                    Terrain::Iron => {
                        iron.insert(cell);
                    }
                    Terrain::Water => {
                        water.insert(cell);
                    }
                    Terrain::Rock | Terrain::Shack => {}
                }
            }
        }
        let units = vec![
            Unit {
                id: 0,
                player: 0,
                x: shacks[0].0,
                y: shacks[0].1,
                ms: 1,
                cc: 1,
                hp: 1,
                chop: 1,
                carry: [0; 6],
            },
            Unit {
                id: 1,
                player: 1,
                x: shacks[1].0,
                y: shacks[1].1,
                ms: 1,
                cc: 1,
                hp: 1,
                chop: 1,
                carry: [0; 6],
            },
        ];
        let score = inventory[..4].iter().sum();
        GameState {
            width: self.width,
            height: self.height,
            walkable,
            shacks,
            inventories: [inventory, inventory],
            units,
            plants: self.plants,
            scores: [score, score],
            turn: 1,
            next_id: 2,
            iron,
            water,
        }
    }
}

/// Generate the exact initial Legend-league state for a CodinGame referee seed.
pub fn generate_official(seed: i64) -> GameState {
    let mut random = Sha1Prng::new(seed);
    loop {
        let height = random.next_int(4) + 8;
        let width = 2 * height;
        let mut draft = Draft::new(width, height);

        let mut river_budget = width * height - 46;
        let river_count = random.next_int(2) + 2;
        for _ in 0..river_count {
            let mut river = draft.random_grass(&mut random);
            for _ in 0..10 {
                if !draft.near_edge(river) {
                    break;
                }
                river = draft.random_grass(&mut random);
            }
            let mut current = Some(river);
            while let Some(cell) = current {
                if river_budget <= 0 {
                    break;
                }
                draft.set_symmetric(cell, Terrain::Water);
                current = draft.neighbor(cell, random.next_int(4) as usize);
                river_budget -= 2;
            }
        }

        let mut inventory = [0; 6];
        for item in inventory.iter_mut().take(5) {
            *item = random.next_int(9) + 2;
        }

        let mut shack = (random.next_int(width / 2), random.next_int(height));
        while draft.terrain(shack) == Terrain::Water {
            shack = (random.next_int(width / 2), random.next_int(height));
        }
        draft.set_symmetric(shack, Terrain::Shack);
        let shacks = [shack, draft.mirror(shack)];

        draft.place_terrain(&mut random, Terrain::Iron, 1, 2);
        draft.place_terrain(&mut random, Terrain::Rock, 1, 10);
        for plant_type in FRUITS {
            draft.place_trees(&mut random, plant_type, 1, 3);
        }

        if draft.valid(shacks) {
            return draft.finish(shacks, inventory);
        }
    }
}

/// Render the exact initial protocol stream sent to one player.
pub fn render_turn_one(game: &GameState, seat: usize) -> String {
    assert!(seat < 2, "Troll Farm has exactly two seats");
    let mut lines = Vec::new();
    lines.push(format!("{} {}", game.width, game.height));
    for y in 0..game.height {
        let mut row = String::new();
        for x in 0..game.width {
            let cell = (x, y);
            let symbol = if cell == game.shacks[seat] {
                '0'
            } else if cell == game.shacks[1 - seat] {
                '1'
            } else if game.water.contains(&cell) {
                '~'
            } else if game.iron.contains(&cell) {
                '+'
            } else if game.walkable.contains(&cell) {
                '.'
            } else {
                '#'
            };
            row.push(symbol);
        }
        lines.push(row);
    }
    for player in [seat, 1 - seat] {
        lines.push(
            game.inventories[player]
                .iter()
                .map(i32::to_string)
                .collect::<Vec<_>>()
                .join(" "),
        );
    }
    lines.push(game.plants.len().to_string());
    for plant in &game.plants {
        lines.push(format!(
            "{} {} {} {} {} {} {}",
            plant.plant_type,
            plant.x,
            plant.y,
            plant.size,
            plant.health,
            plant.fruits,
            plant.cooldown
        ));
    }
    lines.push(game.units.len().to_string());
    for unit in &game.units {
        let relative_player = usize::from(unit.player as usize != seat);
        let mut values = vec![
            unit.id,
            relative_player as i32,
            unit.x,
            unit.y,
            unit.ms,
            unit.cc,
            unit.hp,
            unit.chop,
        ];
        values.extend(unit.carry);
        lines.push(
            values
                .iter()
                .map(i32::to_string)
                .collect::<Vec<_>>()
                .join(" "),
        );
    }
    lines.join("\n") + "\n"
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sha1_matches_standard_vector() {
        assert_eq!(
            sha1(b"abc"),
            [
                0xa9, 0x99, 0x3e, 0x36, 0x47, 0x06, 0x81, 0x6a, 0xba, 0x3e, 0x25, 0x71, 0x78, 0x50,
                0xc2, 0x6c, 0x9c, 0xd0, 0xd8, 0x9d,
            ]
        );
    }

    #[test]
    fn generated_maps_have_official_structural_invariants() {
        for seed in [-9_i64, 1, 17, i64::MIN, i64::MAX] {
            let game = generate_official(seed);
            assert!((8..=11).contains(&game.height));
            assert_eq!(game.width, 2 * game.height);
            assert_eq!(game.units.len(), 2);
            assert!((8..=24).contains(&game.plants.len()));
            for x in 0..game.width {
                for y in 0..game.height {
                    let cell = (x, y);
                    let mirror = (game.width - 1 - x, game.height - 1 - y);
                    assert_eq!(game.water.contains(&cell), game.water.contains(&mirror));
                    assert_eq!(game.iron.contains(&cell), game.iron.contains(&mirror));
                    assert_eq!(
                        game.walkable.contains(&cell),
                        game.walkable.contains(&mirror)
                    );
                }
            }
            assert_eq!(render_turn_one(&game, 0), render_turn_one(&game, 0));
        }
    }
}
