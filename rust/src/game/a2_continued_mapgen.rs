//! D33 map generation with the post-generation SHA1PRNG state retained.
//!
//! This is an isolated copy of the source-locked D33 implementation through
//! `Draft::finish`. A2-0b tests every generated field against the unchanged public
//! `official_mapgen::generate_official` for 1,024 seeds before this path is accepted.

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
pub(crate) struct Sha1Prng {
    state: [u8; 20],
    remainder: [u8; 20],
    remainder_count: usize,
}

impl Sha1Prng {
    fn new(seed: i64) -> Self {
        assert_ne!(
            seed, 0,
            "OpenJDK ignores setSeed(0) and cannot generate a deterministic official map"
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

    pub(crate) fn next_int(&mut self, bound: i32) -> i32 {
        assert!(bound > 0, "Java Random bound must be positive");
        if bound & -bound == bound {
            return ((i64::from(bound) * i64::from(self.next(31))) >> 31) as i32;
        }
        loop {
            let bits = self.next(31) as i32;
            let value = bits % bound;
            if bits.wrapping_sub(value).wrapping_add(bound - 1) >= 0 {
                return value;
            }
        }
    }

    fn next_int_range(&mut self, origin: i32, bound: i32) -> i32 {
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
        (next.0 >= 0 && next.0 < self.width && next.1 >= 0 && next.1 < self.height)
            .then_some(next)
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

pub(crate) fn generate_official_with_rng(seed: i64) -> (GameState, Sha1Prng) {
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
            return (draft.finish(shacks, inventory), random);
        }
    }
}
