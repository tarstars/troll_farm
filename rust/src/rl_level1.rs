//! Batched curriculum environment for the first PPO capability gate.
//!
//! Level 1 fixes the requested second-troll specification and automatically
//! submits that TRAIN request every turn.  The learned policy controls the
//! starting troll and must collect/bank the missing resources and vacate the
//! shack.  The C ABI keeps Python/PyTorch out of the referee hot loop.

use crate::game::fast::{
    cid, step_fast, training_cost_fast, FAct, FCmds, FastState, NavTable, CD_BASE,
};
use crate::game::mapgen::generate_bronze;

pub const OBS_CHANNELS: usize = 104;
pub const OBS_HEIGHT: usize = 11;
pub const OBS_WIDTH: usize = 22;
pub const OBS_CELLS: usize = OBS_HEIGHT * OBS_WIDTH;
pub const OBS_SIZE: usize = OBS_CHANNELS * OBS_CELLS;
pub const ACTION_PLANES: usize = 13;
pub const ACTION_SIZE: usize = ACTION_PLANES * OBS_CELLS;
pub type WorkerSpec = (i8, i8, i8, i8);
pub const LEVEL1_TARGET: WorkerSpec = (1, 3, 0, 1);
pub const LEVEL2_TARGETS: [WorkerSpec; 8] = [
    (1, 1, 1, 1), // cheap planter
    (1, 2, 1, 1), // compact farmer
    (2, 2, 1, 1), // balanced producer
    (2, 2, 2, 1), // harvest producer
    (1, 3, 0, 1), // Level-1 anchor
    (1, 2, 0, 2), // lean chopper
    (2, 2, 0, 2), // standard chopper
    (2, 3, 1, 2), // hybrid chopper
];
const RELEVANT_ITEMS: [usize; 4] = [0, 1, 2, 4];

#[inline]
fn splitmix64_finalizer(mut value: u64) -> u64 {
    value = (value ^ (value >> 30)).wrapping_mul(0xbf58_476d_1ce4_e5b9);
    value = (value ^ (value >> 27)).wrapping_mul(0x94d0_49bb_1331_11eb);
    value ^ (value >> 31)
}

pub fn level2_recipe(seed: u64) -> (u8, WorkerSpec) {
    let recipe_id =
        (splitmix64_finalizer(seed ^ 0x4c32_7265_6369_7065) % LEVEL2_TARGETS.len() as u64) as u8;
    (recipe_id, LEVEL2_TARGETS[recipe_id as usize])
}

#[inline]
fn spatial(x: i8, y: i8) -> usize {
    y as usize * OBS_WIDTH + x as usize
}

#[inline]
fn action(plane: usize, x: i8, y: i8) -> usize {
    plane * OBS_CELLS + spatial(x, y)
}

#[inline]
fn quant(value: f32, scale: f32) -> u8 {
    if scale <= 0.0 {
        return 0;
    }
    (255.0 * value / scale).round().clamp(0.0, 255.0) as u8
}

pub struct Level1Env {
    pub state: FastState,
    nav: Box<NavTable>,
    iron: [bool; OBS_CELLS],
    seed: u64,
    target: WorkerSpec,
    recipe_id: u8,
    initial_deficit: u8,
    initial_total_deficit: u8,
    max_turns: u16,
    steps: u16,
    episode_return: f32,
    potential: f32,
    previous_action_plane: u8,
}

impl Level1Env {
    pub fn new(seed: u64, max_turns: u16) -> Self {
        Self::new_with_target(seed, max_turns, 0, LEVEL1_TARGET)
    }

    pub fn new_level2(seed: u64, max_turns: u16) -> Self {
        let (recipe_id, target) = level2_recipe(seed);
        Self::new_with_target(seed, max_turns, recipe_id, target)
    }

    fn new_with_target(seed: u64, max_turns: u16, recipe_id: u8, target: WorkerSpec) -> Self {
        let game = generate_bronze(seed);
        let mut iron = [false; OBS_CELLS];
        for &(x, y) in &game.iron {
            iron[spatial(x as i8, y as i8)] = true;
        }
        let nav = NavTable::build(&game);
        let state = FastState::from_game(&game);
        let initial_cost = training_cost_fast(1, target);
        let initial_deficit = (initial_cost[1] - state.inv[0][1]).max(0) as u8;
        let initial_total_deficit = RELEVANT_ITEMS
            .iter()
            .map(|&item| (initial_cost[item] - state.inv[0][item]).max(0) as u16)
            .sum::<u16>()
            .min(u8::MAX as u16) as u8;
        let mut env = Self {
            state,
            nav,
            iron,
            seed,
            target,
            recipe_id,
            initial_deficit,
            initial_total_deficit,
            max_turns,
            steps: 0,
            episode_return: 0.0,
            potential: 0.0,
            previous_action_plane: 0,
        };
        env.potential = env.estimated_turns_remaining();
        env
    }

    fn selected_ui(&self) -> usize {
        (0..self.state.n_units as usize)
            .filter(|&ui| self.state.u_pl[ui] == 0)
            .min_by_key(|&ui| self.state.u_id[ui])
            .expect("Level 1 always has a player-zero starter")
    }

    fn own_count(&self) -> usize {
        (0..self.state.n_units as usize)
            .filter(|&ui| self.state.u_pl[ui] == 0)
            .count()
    }

    fn target_built(&self) -> bool {
        self.own_count() >= 2
            && (0..self.state.n_units as usize).any(|ui| {
                self.state.u_pl[ui] == 0
                    && self.state.u_id[ui] != self.state.u_id[self.selected_ui()]
                    && (
                        self.state.u_ms[ui],
                        self.state.u_cc[ui],
                        self.state.u_hp[ui],
                        self.state.u_chop[ui],
                    ) == self.target
            })
    }

    fn target_cost(&self) -> [i16; 6] {
        training_cost_fast(self.own_count() as i16, self.target)
    }

    fn target_affordable(&self) -> bool {
        let cost = self.target_cost();
        (0..6).all(|i| self.state.inv[0][i] >= cost[i])
    }

    fn local_cell(&self, x: i8, y: i8) -> usize {
        cid(x, y, self.state.w)
    }

    fn home_cells(&self) -> impl Iterator<Item = (i8, i8)> + '_ {
        let shack = self.state.shack[0];
        [(0i8, 1i8), (1, 0), (0, -1), (-1, 0)]
            .into_iter()
            .map(move |(dx, dy)| (shack.0 + dx, shack.1 + dy))
            .filter(|&(x, y)| {
                x >= 0
                    && y >= 0
                    && x < self.state.w
                    && y < self.state.h
                    && self.nav.walk[self.local_cell(x, y)]
            })
    }

    fn distance(&self, from: (i8, i8), to: (i8, i8)) -> Option<u8> {
        let d = self
            .nav
            .d(self.local_cell(from.0, from.1), self.local_cell(to.0, to.1));
        (d != 255).then_some(d)
    }

    fn home_distance_from(&self, from: (i8, i8)) -> u8 {
        self.home_cells()
            .filter_map(|home| self.distance(from, home))
            .min()
            .unwrap_or(180)
    }

    fn source_options(&self, item: usize) -> Vec<((i8, i8), u16)> {
        if item == 4 {
            let mut out = Vec::new();
            for y in 0..self.state.h {
                for x in 0..self.state.w {
                    let lc = self.local_cell(x, y);
                    if self.nav.walk[lc] && self.state.iron_adj[lc] {
                        out.push(((x, y), 0));
                    }
                }
            }
            return out;
        }

        (0..self.state.n_plants as usize)
            .filter(|&pi| self.state.p_type[pi] as usize == item)
            .map(|pi| {
                let wait = if self.state.p_fruits[pi] > 0 {
                    0
                } else {
                    let ty = self.state.p_type[pi] as usize;
                    let cd = if self.state.p_wet[pi] {
                        (CD_BASE[ty] - crate::game::fast::CD_BOOST[ty]).max(1)
                    } else {
                        CD_BASE[ty]
                    } as u16;
                    self.state.p_cd[pi].max(0) as u16
                        + (4 - self.state.p_size[pi]).max(0) as u16 * cd
                        + cd
                };
                ((self.state.p_x[pi], self.state.p_y[pi]), wait)
            })
            .collect()
    }

    fn best_source(&self, item: usize, from: (i8, i8)) -> Option<((i8, i8), u16)> {
        self.source_options(item)
            .into_iter()
            .filter_map(|(pos, wait)| {
                self.distance(from, pos)
                    .map(|d| (pos, wait, d as u16 + wait))
            })
            .min_by_key(|&(pos, wait, total)| (total, wait, pos.1, pos.0))
            .map(|(pos, wait, _)| (pos, wait))
    }

    fn estimated_turns_remaining(&self) -> f32 {
        if self.target_built() {
            return 0.0;
        }
        let ui = self.selected_ui();
        let here = (self.state.u_x[ui], self.state.u_y[ui]);
        let cost = self.target_cost();
        let mut estimate = 0.0f32;

        for item in RELEVANT_ITEMS {
            let bank_need = (cost[item] - self.state.inv[0][item]).max(0) as i32;
            if bank_need == 0 {
                continue;
            }
            let carried = self.state.u_carry[ui][item].max(0) as i32;
            let useful_carry = carried.min(bank_need);
            let remaining = bank_need - useful_carry;
            let home_d = self.home_distance_from(here) as f32;
            if useful_carry > 0 {
                estimate += home_d + 1.0;
            }
            if remaining <= 0 {
                continue;
            }

            let start = if useful_carry > 0 {
                self.home_cells().next().unwrap_or(here)
            } else {
                here
            };
            let Some((source, wait)) = self.best_source(item, start) else {
                estimate += 180.0;
                continue;
            };
            let outward = self.distance(start, source).unwrap_or(180) as f32;
            let return_d = self.home_distance_from(source) as f32;
            let per_trip = outward + wait as f32 + 1.0 + return_d + 1.0;
            let repeat = return_d + outward + 2.0;
            estimate += per_trip + (remaining - 1).max(0) as f32 * repeat;
        }
        estimate
    }

    fn nearest_needed_distance(&self) -> u8 {
        let ui = self.selected_ui();
        let here = (self.state.u_x[ui], self.state.u_y[ui]);
        let cost = self.target_cost();
        if RELEVANT_ITEMS
            .iter()
            .any(|&item| self.state.inv[0][item] < cost[item] && self.state.u_carry[ui][item] > 0)
        {
            return self.home_distance_from(here);
        }
        RELEVANT_ITEMS
            .iter()
            .filter(|&&item| self.state.inv[0][item] < cost[item])
            .filter_map(|&item| {
                self.best_source(item, here)
                    .and_then(|(pos, _)| self.distance(here, pos))
            })
            .min()
            .unwrap_or(0)
    }

    fn fill_broadcast(&self, obs: &mut [u8], channel: usize, value: u8) {
        let base = channel * OBS_CELLS;
        for y in 0..self.state.h {
            for x in 0..self.state.w {
                obs[base + spatial(x, y)] = value;
            }
        }
    }

    pub fn observe(&self, obs: &mut [u8], mask: &mut [u8]) {
        assert_eq!(obs.len(), OBS_SIZE);
        assert_eq!(mask.len(), ACTION_SIZE);
        obs.fill(0);
        mask.fill(0);
        let ui = self.selected_ui();
        let sx = self.state.u_x[ui];
        let sy = self.state.u_y[ui];

        for y in 0..self.state.h {
            for x in 0..self.state.w {
                let sc = spatial(x, y);
                let lc = self.local_cell(x, y);
                let target = if self.nav.walk[lc] {
                    lc
                } else {
                    self.nav.park[lc] as usize
                };
                let selected = self.local_cell(sx, sy);
                let selected_distance = self.nav.d(selected, target);
                let target_pos = (
                    (target % self.state.w as usize) as i8,
                    (target / self.state.w as usize) as i8,
                );
                let home_distance = self.home_distance_from(target_pos);
                obs[sc] = 255; // 0: in bounds
                obs[OBS_CELLS + sc] = if self.nav.walk[lc] { 255 } else { 0 }; // 1
                                                                               // 2: selected-to-cell BFS proximity (high means near).
                obs[2 * OBS_CELLS + sc] =
                    255u8.saturating_sub(quant(selected_distance as f32, 40.0));
                obs[3 * OBS_CELLS + sc] = if self.state.iron_adj[lc] { 255 } else { 0 };
                obs[4 * OBS_CELLS + sc] = if self.state.water_adj[lc] { 255 } else { 0 };
                // 103: cell-to-own-home BFS proximity (high means near).
                obs[103 * OBS_CELLS + sc] = 255u8.saturating_sub(quant(home_distance as f32, 40.0));
            }
        }
        for player in 0..2usize {
            let (x, y) = self.state.shack[player];
            obs[(5 + player) * OBS_CELLS + spatial(x, y)] = 255;
        }
        obs[7 * OBS_CELLS + spatial(sx, sy)] = 255;

        for unit in 0..self.state.n_units as usize {
            let sc = spatial(self.state.u_x[unit], self.state.u_y[unit]);
            let own = self.state.u_pl[unit] == 0;
            obs[(if own { 8 } else { 9 }) * OBS_CELLS + sc] = 255;
            let base = if own { 10 } else { 15 };
            obs[base * OBS_CELLS + sc] = quant(self.state.u_ms[unit] as f32, 3.0);
            obs[(base + 1) * OBS_CELLS + sc] = quant(self.state.u_cc[unit] as f32, 4.0);
            obs[(base + 2) * OBS_CELLS + sc] = quant(self.state.u_hp[unit] as f32, 3.0);
            obs[(base + 3) * OBS_CELLS + sc] = quant(self.state.u_chop[unit] as f32, 4.0);
            obs[(base + 4) * OBS_CELLS + sc] = quant(self.state.free(unit) as f32, 4.0);
            let carry_base = if own { 20 } else { 26 };
            for item in 0..6 {
                obs[(carry_base + item) * OBS_CELLS + sc] =
                    quant(self.state.u_carry[unit][item] as f32, 4.0);
            }
        }

        for pi in 0..self.state.n_plants as usize {
            let sc = spatial(self.state.p_x[pi], self.state.p_y[pi]);
            let base = 32 + self.state.p_type[pi] as usize * 6;
            obs[base * OBS_CELLS + sc] = 255;
            obs[(base + 1) * OBS_CELLS + sc] = quant(self.state.p_size[pi] as f32, 4.0);
            obs[(base + 2) * OBS_CELLS + sc] = quant(self.state.p_health[pi] as f32, 20.0);
            obs[(base + 3) * OBS_CELLS + sc] = quant(self.state.p_fruits[pi] as f32, 3.0);
            obs[(base + 4) * OBS_CELLS + sc] = quant(self.state.p_cd[pi] as f32, 9.0);
            obs[(base + 5) * OBS_CELLS + sc] = if self.state.p_wet[pi] { 255 } else { 0 };
        }

        for item in 0..6 {
            self.fill_broadcast(obs, 56 + item, quant(self.state.inv[0][item] as f32, 30.0));
            self.fill_broadcast(obs, 62 + item, quant(self.state.inv[1][item] as f32, 30.0));
            self.fill_broadcast(
                obs,
                68 + item,
                quant(self.state.u_carry[ui][item] as f32, 4.0),
            );
        }
        self.fill_broadcast(obs, 74, quant(self.state.u_ms[ui] as f32, 3.0));
        self.fill_broadcast(obs, 75, quant(self.state.u_cc[ui] as f32, 4.0));
        self.fill_broadcast(obs, 76, quant(self.state.u_hp[ui] as f32, 3.0));
        self.fill_broadcast(obs, 77, quant(self.state.u_chop[ui] as f32, 4.0));
        self.fill_broadcast(obs, 78, quant(self.state.free(ui) as f32, 4.0));
        self.fill_broadcast(
            obs,
            79,
            quant(self.home_distance_from((sx, sy)) as f32, 40.0),
        );
        self.fill_broadcast(obs, 80, quant(self.steps as f32, self.max_turns as f32));
        self.fill_broadcast(
            obs,
            81,
            quant((self.max_turns - self.steps) as f32, self.max_turns as f32),
        );
        self.fill_broadcast(obs, 82, quant(self.state.score(0) as f32, 400.0));
        self.fill_broadcast(obs, 83, quant(self.state.score(1) as f32, 400.0));
        self.fill_broadcast(obs, 84, quant(self.own_count() as f32, 6.0));
        let opp_count = (0..self.state.n_units as usize)
            .filter(|&u| self.state.u_pl[u] == 1)
            .count();
        self.fill_broadcast(obs, 85, quant(opp_count as f32, 6.0));

        for (offset, value) in [self.target.0, self.target.1, self.target.2, self.target.3]
            .into_iter()
            .enumerate()
        {
            self.fill_broadcast(obs, 86 + offset, quant(value as f32, 4.0));
        }
        let cost = self.target_cost();
        for (offset, item) in RELEVANT_ITEMS.into_iter().enumerate() {
            self.fill_broadcast(obs, 90 + offset, quant(cost[item] as f32, 20.0));
            let deficit = (cost[item] - self.state.inv[0][item]).max(0);
            self.fill_broadcast(obs, 94 + offset, quant(deficit as f32, 20.0));
        }
        self.fill_broadcast(obs, 98, if self.target_affordable() { 255 } else { 0 });
        let shack = self.state.shack[0];
        let shack_occupied = (0..self.state.n_units as usize)
            .any(|u| self.state.u_x[u] == shack.0 && self.state.u_y[u] == shack.1);
        self.fill_broadcast(obs, 99, if shack_occupied { 255 } else { 0 });
        let carrying_needed = RELEVANT_ITEMS
            .iter()
            .any(|&item| self.state.inv[0][item] < cost[item] && self.state.u_carry[ui][item] > 0);
        self.fill_broadcast(obs, 100, if carrying_needed { 255 } else { 0 });
        self.fill_broadcast(obs, 101, quant(self.nearest_needed_distance() as f32, 40.0));
        self.fill_broadcast(obs, 102, quant(self.previous_action_plane as f32, 12.0));

        // MOVE/current is the canonical WAIT and guarantees a nonempty mask.
        mask[action(0, sx, sy)] = 1;
        for pi in 0..self.state.n_plants as usize {
            mask[action(0, self.state.p_x[pi], self.state.p_y[pi])] = 1;
        }
        let home = self.state.shack[0];
        mask[action(0, home.0, home.1)] = 1;
        for y in 0..self.state.h {
            for x in 0..self.state.w {
                let lc = self.local_cell(x, y);
                if self.iron[spatial(x, y)] || (self.nav.walk[lc] && self.state.iron_adj[lc]) {
                    mask[action(0, x, y)] = 1;
                }
            }
        }

        let current = spatial(sx, sy);
        if let Some(pi) = self.state.plant_at(sx, sy) {
            if self.state.u_hp[ui] > 0 && self.state.free(ui) > 0 && self.state.p_fruits[pi] > 0 {
                mask[OBS_CELLS + current] = 1;
            }
            if self.state.u_chop[ui] > 0 {
                mask[2 * OBS_CELLS + current] = 1;
            }
        }
        let near_home = (sx - home.0).abs() + (sy - home.1).abs() <= 1;
        if near_home && self.state.u_carry[ui].iter().sum::<i8>() > 0 {
            mask[3 * OBS_CELLS + current] = 1;
        }
        if self.state.u_chop[ui] > 0
            && self.state.free(ui) > 0
            && self.state.iron_adj[self.local_cell(sx, sy)]
        {
            mask[4 * OBS_CELLS + current] = 1;
        }
        if self.nav.walk[self.local_cell(sx, sy)] && self.state.plant_at(sx, sy).is_none() {
            for item in 0..4 {
                if self.state.u_carry[ui][item] > 0 {
                    mask[(5 + item) * OBS_CELLS + current] = 1;
                }
            }
        }
        if near_home && self.state.free(ui) > 0 {
            for item in 0..4 {
                if self.state.inv[0][item] > 0 {
                    mask[(9 + item) * OBS_CELLS + current] = 1;
                }
            }
        }
    }

    fn decode(&self, selected_action: usize) -> FAct {
        if selected_action >= ACTION_SIZE {
            return FAct::Idle;
        }
        let plane = selected_action / OBS_CELLS;
        let sc = selected_action % OBS_CELLS;
        let x = (sc % OBS_WIDTH) as i8;
        let y = (sc / OBS_WIDTH) as i8;
        match plane {
            0 if x < self.state.w && y < self.state.h => FAct::Move(self.local_cell(x, y) as u8),
            1 => FAct::Harvest,
            2 => FAct::Chop,
            3 => FAct::Drop,
            4 => FAct::Mine,
            5..=8 => FAct::Plant((plane - 5) as u8),
            9..=12 => FAct::Pick((plane - 9) as u8),
            _ => FAct::Idle,
        }
    }

    pub fn teacher_action(&self) -> usize {
        let ui = self.selected_ui();
        let here = (self.state.u_x[ui], self.state.u_y[ui]);
        let home = self.state.shack[0];
        let cost = self.target_cost();

        if self.target_affordable() {
            if here == home {
                if let Some(pi) = (0..self.state.n_plants as usize).min_by_key(|&pi| {
                    self.distance(here, (self.state.p_x[pi], self.state.p_y[pi]))
                        .unwrap_or(255)
                }) {
                    return action(0, self.state.p_x[pi], self.state.p_y[pi]);
                }
            }
            return action(0, here.0, here.1);
        }

        let carried_needed = RELEVANT_ITEMS
            .iter()
            .any(|&item| self.state.inv[0][item] < cost[item] && self.state.u_carry[ui][item] > 0);
        if carried_needed || self.state.free(ui) == 0 {
            if (here.0 - home.0).abs() + (here.1 - home.1).abs() <= 1 {
                return action(3, here.0, here.1);
            }
            return action(0, home.0, home.1);
        }

        let needed = RELEVANT_ITEMS
            .into_iter()
            .filter(|&item| self.state.inv[0][item] < cost[item])
            .min_by_key(|&item| {
                self.best_source(item, here)
                    .and_then(|(pos, _)| self.distance(here, pos))
                    .unwrap_or(255)
            });
        let Some(item) = needed else {
            return action(0, here.0, here.1);
        };

        if item == 4 {
            if self.state.iron_adj[self.local_cell(here.0, here.1)] {
                return action(4, here.0, here.1);
            }
        } else if let Some(pi) = self.state.plant_at(here.0, here.1) {
            if self.state.p_type[pi] as usize == item && self.state.p_fruits[pi] > 0 {
                return action(1, here.0, here.1);
            }
        }

        if let Some((source, _)) = self.best_source(item, here) {
            return action(0, source.0, source.1);
        }
        action(0, here.0, here.1)
    }

    pub fn step(
        &mut self,
        selected_action: usize,
    ) -> (f32, bool, bool, u16, f32, u64, u8, u8, u8, u8, WorkerSpec) {
        let ui = self.selected_ui();
        let mut commands = [FCmds::default(), FCmds::default()];
        commands[0].acts[ui] = self.decode(selected_action);
        commands[0].train = Some(self.target);
        self.previous_action_plane = (selected_action / OBS_CELLS).min(12) as u8;
        step_fast(&mut self.state, &self.nav, &commands);
        self.steps += 1;

        let success = self.target_built();
        let next_potential = if success {
            0.0
        } else {
            self.estimated_turns_remaining()
        };
        let mut reward = self.potential - next_potential - 0.01;
        if success {
            reward += 20.0;
        }
        let timeout = self.steps >= self.max_turns && !success;
        if timeout {
            reward -= 20.0;
        }
        self.potential = next_potential;
        self.episode_return += reward;
        let done = success || timeout;
        (
            reward,
            done,
            success,
            self.steps,
            self.episode_return,
            self.seed,
            self.state.h as u8,
            self.initial_deficit,
            self.recipe_id,
            self.initial_total_deficit,
            self.target,
        )
    }
}

pub struct Level1Batch {
    envs: Vec<Level1Env>,
    next_seed: u64,
    max_turns: u16,
    randomized_targets: bool,
}

impl Level1Batch {
    pub fn new(num_envs: usize, seed_base: u64, max_turns: u16) -> Self {
        Self::new_with_mode(num_envs, seed_base, max_turns, false)
    }

    pub fn new_level2(num_envs: usize, seed_base: u64, max_turns: u16) -> Self {
        Self::new_with_mode(num_envs, seed_base, max_turns, true)
    }

    fn new_with_mode(
        num_envs: usize,
        seed_base: u64,
        max_turns: u16,
        randomized_targets: bool,
    ) -> Self {
        assert!(num_envs > 0);
        let envs = (0..num_envs)
            .map(|i| {
                let seed = seed_base + i as u64;
                if randomized_targets {
                    Level1Env::new_level2(seed, max_turns)
                } else {
                    Level1Env::new(seed, max_turns)
                }
            })
            .collect();
        Self {
            envs,
            next_seed: seed_base + num_envs as u64,
            max_turns,
            randomized_targets,
        }
    }

    pub fn len(&self) -> usize {
        self.envs.len()
    }

    fn reset_slot(&mut self, index: usize) {
        let seed = self.next_seed;
        self.next_seed += 1;
        self.envs[index] = if self.randomized_targets {
            Level1Env::new_level2(seed, self.max_turns)
        } else {
            Level1Env::new(seed, self.max_turns)
        };
    }

    pub fn observe(&self, obs: &mut [u8], masks: &mut [u8]) {
        assert_eq!(obs.len(), self.len() * OBS_SIZE);
        assert_eq!(masks.len(), self.len() * ACTION_SIZE);
        for (index, env) in self.envs.iter().enumerate() {
            env.observe(
                &mut obs[index * OBS_SIZE..(index + 1) * OBS_SIZE],
                &mut masks[index * ACTION_SIZE..(index + 1) * ACTION_SIZE],
            );
        }
    }

    pub fn teacher_actions(&self, actions: &mut [i32]) {
        assert_eq!(actions.len(), self.len());
        for (out, env) in actions.iter_mut().zip(&self.envs) {
            *out = env.teacher_action() as i32;
        }
    }
}

#[no_mangle]
pub extern "C" fn tf_level1_obs_size() -> usize {
    OBS_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level1_action_size() -> usize {
    ACTION_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level1_create(
    num_envs: usize,
    seed_base: u64,
    max_turns: u16,
) -> *mut Level1Batch {
    if num_envs == 0 || max_turns == 0 {
        return std::ptr::null_mut();
    }
    Box::into_raw(Box::new(Level1Batch::new(num_envs, seed_base, max_turns)))
}

#[no_mangle]
pub unsafe extern "C" fn tf_level1_destroy(handle: *mut Level1Batch) {
    if !handle.is_null() {
        drop(Box::from_raw(handle));
    }
}

#[no_mangle]
pub unsafe extern "C" fn tf_level1_observe(
    handle: *mut Level1Batch,
    obs: *mut u8,
    masks: *mut u8,
) -> i32 {
    if handle.is_null() || obs.is_null() || masks.is_null() {
        return -1;
    }
    let batch = &*handle;
    let observations = std::slice::from_raw_parts_mut(obs, batch.len() * OBS_SIZE);
    let action_masks = std::slice::from_raw_parts_mut(masks, batch.len() * ACTION_SIZE);
    batch.observe(observations, action_masks);
    0
}

#[no_mangle]
pub unsafe extern "C" fn tf_level1_teacher_actions(
    handle: *mut Level1Batch,
    actions: *mut i32,
) -> i32 {
    if handle.is_null() || actions.is_null() {
        return -1;
    }
    let batch = &*handle;
    let out = std::slice::from_raw_parts_mut(actions, batch.len());
    batch.teacher_actions(out);
    0
}

#[allow(clippy::too_many_arguments)]
#[no_mangle]
pub unsafe extern "C" fn tf_level1_step(
    handle: *mut Level1Batch,
    actions: *const i32,
    obs: *mut u8,
    masks: *mut u8,
    rewards: *mut f32,
    dones: *mut u8,
    successes: *mut u8,
    episode_turns: *mut u16,
    episode_returns: *mut f32,
    episode_seeds: *mut u64,
    episode_heights: *mut u8,
    initial_deficits: *mut u8,
) -> i32 {
    if handle.is_null()
        || actions.is_null()
        || obs.is_null()
        || masks.is_null()
        || rewards.is_null()
        || dones.is_null()
        || successes.is_null()
        || episode_turns.is_null()
        || episode_returns.is_null()
        || episode_seeds.is_null()
        || episode_heights.is_null()
        || initial_deficits.is_null()
    {
        return -1;
    }
    let batch = &mut *handle;
    let n = batch.len();
    let input_actions = std::slice::from_raw_parts(actions, n);
    let out_rewards = std::slice::from_raw_parts_mut(rewards, n);
    let out_dones = std::slice::from_raw_parts_mut(dones, n);
    let out_successes = std::slice::from_raw_parts_mut(successes, n);
    let out_turns = std::slice::from_raw_parts_mut(episode_turns, n);
    let out_returns = std::slice::from_raw_parts_mut(episode_returns, n);
    let out_seeds = std::slice::from_raw_parts_mut(episode_seeds, n);
    let out_heights = std::slice::from_raw_parts_mut(episode_heights, n);
    let out_deficits = std::slice::from_raw_parts_mut(initial_deficits, n);

    for index in 0..n {
        let chosen = input_actions[index].max(0) as usize;
        let (reward, done, success, turns, total_return, seed, height, initial_deficit, ..) =
            batch.envs[index].step(chosen);
        out_rewards[index] = reward;
        out_dones[index] = done as u8;
        out_successes[index] = success as u8;
        out_turns[index] = if done { turns } else { 0 };
        out_returns[index] = if done { total_return } else { 0.0 };
        out_seeds[index] = if done { seed } else { 0 };
        out_heights[index] = if done { height } else { 0 };
        out_deficits[index] = if done { initial_deficit } else { 0 };
        if done {
            batch.reset_slot(index);
        }
    }

    let observations = std::slice::from_raw_parts_mut(obs, n * OBS_SIZE);
    let action_masks = std::slice::from_raw_parts_mut(masks, n * ACTION_SIZE);
    batch.observe(observations, action_masks);
    0
}

#[no_mangle]
pub extern "C" fn tf_level2_obs_size() -> usize {
    OBS_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level2_action_size() -> usize {
    ACTION_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level2_recipe_count() -> usize {
    LEVEL2_TARGETS.len()
}

#[no_mangle]
pub extern "C" fn tf_level2_create(
    num_envs: usize,
    seed_base: u64,
    max_turns: u16,
) -> *mut Level1Batch {
    if num_envs == 0 || max_turns == 0 {
        return std::ptr::null_mut();
    }
    Box::into_raw(Box::new(Level1Batch::new_level2(
        num_envs, seed_base, max_turns,
    )))
}

#[no_mangle]
pub unsafe extern "C" fn tf_level2_destroy(handle: *mut Level1Batch) {
    if !handle.is_null() {
        drop(Box::from_raw(handle));
    }
}

#[no_mangle]
pub unsafe extern "C" fn tf_level2_observe(
    handle: *mut Level1Batch,
    obs: *mut u8,
    masks: *mut u8,
) -> i32 {
    if handle.is_null() || obs.is_null() || masks.is_null() {
        return -1;
    }
    let batch = &*handle;
    let observations = std::slice::from_raw_parts_mut(obs, batch.len() * OBS_SIZE);
    let action_masks = std::slice::from_raw_parts_mut(masks, batch.len() * ACTION_SIZE);
    batch.observe(observations, action_masks);
    0
}

#[no_mangle]
pub unsafe extern "C" fn tf_level2_teacher_actions(
    handle: *mut Level1Batch,
    actions: *mut i32,
) -> i32 {
    if handle.is_null() || actions.is_null() {
        return -1;
    }
    let batch = &*handle;
    let out = std::slice::from_raw_parts_mut(actions, batch.len());
    batch.teacher_actions(out);
    0
}

#[allow(clippy::too_many_arguments)]
#[no_mangle]
pub unsafe extern "C" fn tf_level2_step(
    handle: *mut Level1Batch,
    actions: *const i32,
    obs: *mut u8,
    masks: *mut u8,
    rewards: *mut f32,
    dones: *mut u8,
    successes: *mut u8,
    episode_turns: *mut u16,
    episode_returns: *mut f32,
    episode_seeds: *mut u64,
    episode_heights: *mut u8,
    recipe_ids: *mut u8,
    initial_total_deficits: *mut u8,
    target_specs: *mut i8,
) -> i32 {
    if handle.is_null()
        || actions.is_null()
        || obs.is_null()
        || masks.is_null()
        || rewards.is_null()
        || dones.is_null()
        || successes.is_null()
        || episode_turns.is_null()
        || episode_returns.is_null()
        || episode_seeds.is_null()
        || episode_heights.is_null()
        || recipe_ids.is_null()
        || initial_total_deficits.is_null()
        || target_specs.is_null()
    {
        return -1;
    }
    let batch = &mut *handle;
    let n = batch.len();
    let input_actions = std::slice::from_raw_parts(actions, n);
    let out_rewards = std::slice::from_raw_parts_mut(rewards, n);
    let out_dones = std::slice::from_raw_parts_mut(dones, n);
    let out_successes = std::slice::from_raw_parts_mut(successes, n);
    let out_turns = std::slice::from_raw_parts_mut(episode_turns, n);
    let out_returns = std::slice::from_raw_parts_mut(episode_returns, n);
    let out_seeds = std::slice::from_raw_parts_mut(episode_seeds, n);
    let out_heights = std::slice::from_raw_parts_mut(episode_heights, n);
    let out_recipe_ids = std::slice::from_raw_parts_mut(recipe_ids, n);
    let out_total_deficits = std::slice::from_raw_parts_mut(initial_total_deficits, n);
    let out_targets = std::slice::from_raw_parts_mut(target_specs, n * 4);

    for index in 0..n {
        let chosen = input_actions[index].max(0) as usize;
        let (
            reward,
            done,
            success,
            turns,
            total_return,
            seed,
            height,
            _,
            recipe_id,
            initial_total_deficit,
            target,
        ) = batch.envs[index].step(chosen);
        out_rewards[index] = reward;
        out_dones[index] = done as u8;
        out_successes[index] = success as u8;
        out_turns[index] = if done { turns } else { 0 };
        out_returns[index] = if done { total_return } else { 0.0 };
        out_seeds[index] = if done { seed } else { 0 };
        out_heights[index] = if done { height } else { 0 };
        out_recipe_ids[index] = if done { recipe_id } else { 0 };
        out_total_deficits[index] = if done { initial_total_deficit } else { 0 };
        let encoded = [target.0, target.1, target.2, target.3];
        for offset in 0..4 {
            out_targets[index * 4 + offset] = if done { encoded[offset] } else { 0 };
        }
        if done {
            batch.reset_slot(index);
        }
    }

    let observations = std::slice::from_raw_parts_mut(obs, n * OBS_SIZE);
    let action_masks = std::slice::from_raw_parts_mut(masks, n * ACTION_SIZE);
    batch.observe(observations, action_masks);
    0
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn mask_is_nonempty_and_teacher_is_legal() {
        for seed in 0..20 {
            let env = Level1Env::new(seed, 180);
            let mut obs = vec![0; OBS_SIZE];
            let mut mask = vec![0; ACTION_SIZE];
            env.observe(&mut obs, &mut mask);
            assert!(mask.iter().any(|&v| v != 0));
            assert_eq!(mask[env.teacher_action()], 1, "seed {seed}");
        }
    }

    #[test]
    fn level2_recipe_and_observation_match_and_teacher_is_legal() {
        let mut seen = [false; LEVEL2_TARGETS.len()];
        for seed in 0..200 {
            let env = Level1Env::new_level2(seed, 240);
            let (recipe_id, target) = level2_recipe(seed);
            assert_eq!(env.recipe_id, recipe_id);
            assert_eq!(env.target, target);
            seen[recipe_id as usize] = true;
            let mut obs = vec![0; OBS_SIZE];
            let mut mask = vec![0; ACTION_SIZE];
            env.observe(&mut obs, &mut mask);
            let teacher = env.teacher_action();
            assert_eq!(
                mask[teacher],
                1,
                "seed {seed}, recipe {recipe_id}, target {target:?}, teacher plane {}, cell {}",
                teacher / OBS_CELLS,
                teacher % OBS_CELLS
            );
            for (offset, value) in [target.0, target.1, target.2, target.3]
                .into_iter()
                .enumerate()
            {
                assert_eq!(obs[(86 + offset) * OBS_CELLS], quant(value as f32, 4.0));
            }
        }
        assert!(seen.into_iter().all(|value| value));
    }

    #[test]
    fn teacher_solves_debug_bank() {
        let mut solved = 0;
        for seed in 0..50 {
            let mut env = Level1Env::new(seed, 180);
            for _ in 0..180 {
                let selected = env.teacher_action();
                let (_, done, success, ..) = env.step(selected);
                if done {
                    solved += success as usize;
                    break;
                }
            }
        }
        assert!(solved >= 45, "teacher solved only {solved}/50");
    }

    #[test]
    fn deterministic_batches_match() {
        let mut a = Level1Batch::new(4, 77, 180);
        let mut b = Level1Batch::new(4, 77, 180);
        for _ in 0..30 {
            let mut aa = vec![0; 4];
            let mut bb = vec![0; 4];
            a.teacher_actions(&mut aa);
            b.teacher_actions(&mut bb);
            assert_eq!(aa, bb);
            for i in 0..4 {
                assert_eq!(
                    a.envs[i].step(aa[i] as usize),
                    b.envs[i].step(bb[i] as usize)
                );
            }
            let mut ao = vec![0; 4 * OBS_SIZE];
            let mut bo = vec![0; 4 * OBS_SIZE];
            let mut am = vec![0; 4 * ACTION_SIZE];
            let mut bm = vec![0; 4 * ACTION_SIZE];
            a.observe(&mut ao, &mut am);
            b.observe(&mut bo, &mut bm);
            assert_eq!(ao, bo);
            assert_eq!(am, bm);
        }
    }

    #[test]
    fn level2_batches_match() {
        let mut a = Level1Batch::new_level2(4, 77, 240);
        let mut b = Level1Batch::new_level2(4, 77, 240);
        for _ in 0..30 {
            let mut aa = vec![0; 4];
            let mut bb = vec![0; 4];
            a.teacher_actions(&mut aa);
            b.teacher_actions(&mut bb);
            assert_eq!(aa, bb);
            for i in 0..4 {
                assert_eq!(
                    a.envs[i].step(aa[i] as usize),
                    b.envs[i].step(bb[i] as usize)
                );
            }
        }
    }
}
