//! Curriculum Level 3: fund a fixed chopper, then operate both resident trolls
//! through one complete renewable production loop.
//!
//! After the second troll is trained, one referee turn is represented by two
//! sequential policy decisions. The first action is stored without advancing
//! the game; the second action completes the joint command and steps the exact
//! fast referee. This preserves the Level-1/2 spatial action vocabulary while
//! making the shared actor control both roles.

use crate::game::fast::{
    cid, step_fast, training_cost_fast, FAct, FCmds, FastState, NavTable, CD_BASE, MAXU,
};
use crate::game::mapgen::generate_bronze;
use crate::rl_level1::{level2_recipe, WorkerSpec, ACTION_SIZE, OBS_CELLS, OBS_SIZE, OBS_WIDTH};
use crate::strategies::rhea_bot::baseline_commands;

pub const LEVEL3_TARGET: WorkerSpec = (2, 2, 0, 2);
pub const LEVEL3_SCORE_GAIN: i16 = 12;
const RELEVANT_ITEMS: [usize; 4] = [0, 1, 2, 4];
const BANANA: usize = 3;
const WOOD: usize = 5;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum OpponentMode {
    Waiting,
    CompleteBaseline,
    CompleteBaselineRecovery,
    NaturalForager,
    NaturalPlanter,
    OneShotReaper,
    FundedPair,
    FundedTrio,
    FundedTrioSustained,
    FundedTrioSustained180,
    CropFirstFundedTrioSustained180,
    CropFirstFundedTrioRepeatedPressure180,
    CropFirstFundedTrioRepeatedPressureReacquire180,
}

const LEVEL6_OPPONENTS: [OpponentMode; 6] = [
    OpponentMode::CompleteBaseline,
    OpponentMode::NaturalPlanter,
    OpponentMode::OneShotReaper,
    OpponentMode::FundedPair,
    OpponentMode::FundedTrioSustained180,
    OpponentMode::CropFirstFundedTrioRepeatedPressureReacquire180,
];

#[inline]
fn level6_opponent(seed: u64) -> OpponentMode {
    let mut value = seed ^ 0x4c36_6f70_706f_6e65;
    value = (value ^ (value >> 30)).wrapping_mul(0xbf58_476d_1ce4_e5b9);
    value = (value ^ (value >> 27)).wrapping_mul(0x94d0_49bb_1331_11eb);
    value ^= value >> 31;
    LEVEL6_OPPONENTS[value as usize % LEVEL6_OPPONENTS.len()]
}

const OPPONENT_D5_TARGET: WorkerSpec = (2, 2, 0, 2);
const OPPONENT_D6_TARGET: WorkerSpec = (1, 1, 1, 0);

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

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Level3Terminal {
    pub reward: f32,
    pub done: bool,
    pub success: bool,
    pub turns: u16,
    pub episode_return: f32,
    pub seed: u64,
    pub height: u8,
    pub initial_total_deficit: u8,
    pub training_turn: u16,
    pub score_gain: i16,
    pub renewable_harvests: u8,
    pub created_crop: bool,
    pub recipe_id: u8,
    pub target: WorkerSpec,
    pub opponent_score: i16,
    pub opponent_workers: u8,
    pub opponent_created_crops: u8,
    pub opponent_renewable_harvests: u8,
    pub opponent_crop_destructions: u8,
    pub opponent_training_turn: u16,
    pub opponent_funding_deposits: u8,
    pub opponent_funded_training_events: u8,
    pub opponent_second_worker_productive_actions: u16,
    pub opponent_third_worker_training_turn: u16,
    pub opponent_third_worker_productive_actions: u16,
}

pub struct Level3Env {
    pub state: FastState,
    nav: Box<NavTable>,
    iron: [bool; OBS_CELLS],
    seed: u64,
    target: WorkerSpec,
    recipe_id: u8,
    max_turns: u16,
    min_success_turn: u16,
    turns: u16,
    decision_phase: u8,
    pending: [FAct; MAXU],
    episode_return: f32,
    progress: f32,
    previous_action_plane: u8,
    initial_total_deficit: u8,
    training_turn: u16,
    score_at_training: Option<i32>,
    planned_crop: (i8, i8),
    created_crop: Option<(i8, i8)>,
    renewable_harvests: u8,
    initial_plant_cells: [bool; OBS_CELLS],
    opponent_mode: OpponentMode,
    opponent_planned_crop: (i8, i8),
    opponent_created_crop: Option<((i8, i8), u8)>,
    opponent_created_crops: u8,
    opponent_renewable_harvests: u8,
    opponent_crop_destructions: u8,
    opponent_starter_id: i16,
    opponent_training_turn: u16,
    opponent_funding_deposits: u8,
    opponent_funded_since_last_training: bool,
    opponent_funded_training_events: u8,
    opponent_second_worker_productive_actions: u16,
    opponent_third_worker_training_turn: u16,
    opponent_third_worker_productive_actions: u16,
    competitive: bool,
    previous_margin: i32,
}

impl Level3Env {
    pub fn new(seed: u64, max_turns: u16) -> Self {
        Self::new_with_target(seed, max_turns, 6, LEVEL3_TARGET, OpponentMode::Waiting)
    }

    pub fn new_level4(seed: u64, max_turns: u16) -> Self {
        let (recipe_id, target) = level2_recipe(seed);
        Self::new_with_target(seed, max_turns, recipe_id, target, OpponentMode::Waiting)
    }

    pub fn new_level5(seed: u64, max_turns: u16) -> Self {
        let (recipe_id, target) = level2_recipe(seed);
        Self::new_with_target(
            seed,
            max_turns,
            recipe_id,
            target,
            OpponentMode::CompleteBaseline,
        )
    }

    pub fn new_level5_recovery(seed: u64, max_turns: u16) -> Self {
        let (recipe_id, target) = level2_recipe(seed);
        Self::new_with_target(
            seed,
            max_turns,
            recipe_id,
            target,
            OpponentMode::CompleteBaselineRecovery,
        )
    }

    pub fn new_level5_forager(seed: u64, max_turns: u16) -> Self {
        let (recipe_id, target) = level2_recipe(seed);
        Self::new_with_target(
            seed,
            max_turns,
            recipe_id,
            target,
            OpponentMode::NaturalForager,
        )
    }

    pub fn new_level5_planter(seed: u64, max_turns: u16) -> Self {
        let (recipe_id, target) = level2_recipe(seed);
        Self::new_with_target(
            seed,
            max_turns,
            recipe_id,
            target,
            OpponentMode::NaturalPlanter,
        )
    }

    pub fn new_level5_reaper(seed: u64, max_turns: u16) -> Self {
        let (recipe_id, target) = level2_recipe(seed);
        Self::new_with_target(
            seed,
            max_turns,
            recipe_id,
            target,
            OpponentMode::OneShotReaper,
        )
    }

    pub fn new_level5_funded_pair(seed: u64, max_turns: u16) -> Self {
        let (recipe_id, target) = level2_recipe(seed);
        Self::new_with_target(seed, max_turns, recipe_id, target, OpponentMode::FundedPair)
    }

    pub fn new_level5_funded_trio(seed: u64, max_turns: u16) -> Self {
        let (recipe_id, target) = level2_recipe(seed);
        Self::new_with_target(seed, max_turns, recipe_id, target, OpponentMode::FundedTrio)
    }

    pub fn new_level5_funded_trio_sustained(seed: u64, max_turns: u16) -> Self {
        let (recipe_id, target) = level2_recipe(seed);
        Self::new_with_target(
            seed,
            max_turns,
            recipe_id,
            target,
            OpponentMode::FundedTrioSustained,
        )
    }

    pub fn new_level5_funded_trio_sustained_180(seed: u64, max_turns: u16) -> Self {
        let (recipe_id, target) = level2_recipe(seed);
        Self::new_with_target(
            seed,
            max_turns,
            recipe_id,
            target,
            OpponentMode::FundedTrioSustained180,
        )
    }

    pub fn new_level5_crop_first_funded_trio_sustained_180(seed: u64, max_turns: u16) -> Self {
        let (recipe_id, target) = level2_recipe(seed);
        Self::new_with_target(
            seed,
            max_turns,
            recipe_id,
            target,
            OpponentMode::CropFirstFundedTrioSustained180,
        )
    }

    pub fn new_level5_crop_first_funded_trio_repeated_pressure_180(
        seed: u64,
        max_turns: u16,
    ) -> Self {
        let (recipe_id, target) = level2_recipe(seed);
        Self::new_with_target(
            seed,
            max_turns,
            recipe_id,
            target,
            OpponentMode::CropFirstFundedTrioRepeatedPressure180,
        )
    }

    pub fn new_level5_crop_first_funded_trio_repeated_pressure_reacquire_180(
        seed: u64,
        max_turns: u16,
    ) -> Self {
        let (recipe_id, target) = level2_recipe(seed);
        Self::new_with_target(
            seed,
            max_turns,
            recipe_id,
            target,
            OpponentMode::CropFirstFundedTrioRepeatedPressureReacquire180,
        )
    }

    pub fn new_level6(seed: u64, max_turns: u16) -> Self {
        let (recipe_id, target) = level2_recipe(seed);
        let mut env =
            Self::new_with_target(seed, max_turns, recipe_id, target, level6_opponent(seed));
        env.competitive = true;
        env.previous_margin = env.state.score(0) - env.state.score(1);
        env.episode_return = 0.0;
        env
    }

    fn new_with_target(
        seed: u64,
        max_turns: u16,
        recipe_id: u8,
        target: WorkerSpec,
        opponent_mode: OpponentMode,
    ) -> Self {
        let game = generate_bronze(seed);
        let mut iron = [false; OBS_CELLS];
        for &(x, y) in &game.iron {
            iron[spatial(x as i8, y as i8)] = true;
        }
        let nav = NavTable::build(&game);
        let state = FastState::from_game(&game);
        let mut initial_plant_cells = [false; OBS_CELLS];
        for plant in 0..state.n_plants as usize {
            initial_plant_cells[spatial(state.p_x[plant], state.p_y[plant])] = true;
        }
        let cost = training_cost_fast(1, target);
        let initial_total_deficit = RELEVANT_ITEMS
            .iter()
            .map(|&item| (cost[item] - state.inv[0][item]).max(0) as u16)
            .sum::<u16>()
            .min(u8::MAX as u16) as u8;
        let planned_crop = Self::choose_crop_cell(&state, &nav)
            .expect("generated map always has a free home-area crop cell");
        let opponent_planned_crop = Self::choose_crop_cell_for_player(&state, &nav, 1)
            .expect("generated map always has a free opponent-home crop cell");
        let opponent_starter_id = (0..state.n_units as usize)
            .filter(|&unit| state.u_pl[unit] == 1)
            .map(|unit| state.u_id[unit])
            .min()
            .expect("generated map always has one opponent starter");
        let mut env = Self {
            state,
            nav,
            iron,
            seed,
            target,
            recipe_id,
            max_turns,
            min_success_turn: match opponent_mode {
                OpponentMode::FundedTrioSustained => 120,
                OpponentMode::FundedTrioSustained180
                | OpponentMode::CropFirstFundedTrioSustained180
                | OpponentMode::CropFirstFundedTrioRepeatedPressure180
                | OpponentMode::CropFirstFundedTrioRepeatedPressureReacquire180 => 180,
                _ => 0,
            },
            turns: 0,
            decision_phase: 0,
            pending: [FAct::Idle; MAXU],
            episode_return: 0.0,
            progress: 0.0,
            previous_action_plane: 0,
            initial_total_deficit,
            training_turn: 0,
            score_at_training: None,
            planned_crop,
            created_crop: None,
            renewable_harvests: 0,
            initial_plant_cells,
            opponent_mode,
            opponent_planned_crop,
            opponent_created_crop: None,
            opponent_created_crops: 0,
            opponent_renewable_harvests: 0,
            opponent_crop_destructions: 0,
            opponent_starter_id,
            opponent_training_turn: 0,
            opponent_funding_deposits: 0,
            opponent_funded_since_last_training: false,
            opponent_funded_training_events: 0,
            opponent_second_worker_productive_actions: 0,
            opponent_third_worker_training_turn: 0,
            opponent_third_worker_productive_actions: 0,
            competitive: false,
            previous_margin: 0,
        };
        env.progress = env.objective_progress();
        env
    }

    fn choose_crop_cell(state: &FastState, nav: &NavTable) -> Option<(i8, i8)> {
        Self::choose_crop_cell_for_player(state, nav, 0)
    }

    fn choose_crop_cell_for_player(
        state: &FastState,
        nav: &NavTable,
        player: usize,
    ) -> Option<(i8, i8)> {
        let home = state.shack[player];
        let mut candidates = Vec::new();
        for y in 0..state.h {
            for x in 0..state.w {
                let cell = cid(x, y, state.w);
                let radius = (x - home.0).abs() + (y - home.1).abs();
                if radius == 0 || radius > 3 || !nav.walk[cell] || state.plant_at(x, y).is_some() {
                    continue;
                }
                candidates.push((!state.water_adj[cell], radius, y, x));
            }
        }
        candidates.sort_unstable();
        candidates.first().map(|&(_, _, y, x)| (x, y))
    }

    fn own_units(&self) -> Vec<usize> {
        let mut units: Vec<_> = (0..self.state.n_units as usize)
            .filter(|&ui| self.state.u_pl[ui] == 0)
            .collect();
        units.sort_by_key(|&ui| self.state.u_id[ui]);
        units
    }

    fn starter_ui(&self) -> usize {
        self.own_units()[0]
    }

    fn active_ui(&self) -> usize {
        let units = self.own_units();
        if units.len() < 2 || self.decision_phase == 0 {
            units[0]
        } else {
            units[1]
        }
    }

    fn target_built(&self) -> bool {
        let starter = self.starter_ui();
        self.own_units().into_iter().any(|ui| {
            ui != starter
                && (
                    self.state.u_ms[ui],
                    self.state.u_cc[ui],
                    self.state.u_hp[ui],
                    self.state.u_chop[ui],
                ) == self.target
        })
    }

    fn target_cost(&self) -> [i16; 6] {
        training_cost_fast(1, self.target)
    }

    fn target_affordable(&self) -> bool {
        let cost = self.target_cost();
        (0..6).all(|item| self.state.inv[0][item] >= cost[item])
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
            .unwrap_or(240)
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
                    .map(|distance| (pos, wait, distance as u16 + wait))
            })
            .min_by_key(|&(pos, wait, total)| (total, wait, pos.1, pos.0))
            .map(|(pos, wait, _)| (pos, wait))
    }

    fn score_gain(&self) -> i16 {
        self.score_at_training
            .map(|baseline| {
                (self.state.score(0) - baseline).clamp(i16::MIN as i32, i16::MAX as i32) as i16
            })
            .unwrap_or(0)
    }

    fn reported_score_gain(&self) -> i16 {
        if self.competitive {
            self.state.score(0).clamp(i16::MIN as i32, i16::MAX as i32) as i16
        } else {
            self.score_gain()
        }
    }

    fn crop_exists(&self) -> bool {
        self.created_crop.is_some_and(|(x, y)| {
            self.state
                .plant_at(x, y)
                .is_some_and(|pi| self.state.p_type[pi] as usize == BANANA)
        })
    }

    fn success(&self) -> bool {
        self.turns >= self.min_success_turn
            && self.target_built()
            && self.crop_exists()
            && self.renewable_harvests > 0
            && self.score_gain() >= LEVEL3_SCORE_GAIN
    }

    fn objective_progress(&self) -> f32 {
        if !self.target_built() {
            let cost = self.target_cost();
            let ui = self.starter_ui();
            let funded: f32 = RELEVANT_ITEMS
                .iter()
                .map(|&item| {
                    let available = self.state.inv[0][item] + self.state.u_carry[ui][item] as i16;
                    available.min(cost[item]).max(0) as f32 / cost[item].max(1) as f32
                })
                .sum();
            return 2.0 * funded;
        }
        8.0 + self.score_gain().clamp(0, LEVEL3_SCORE_GAIN) as f32
            + if self.crop_exists() { 4.0 } else { 0.0 }
            + if self.renewable_harvests > 0 {
                4.0
            } else {
                0.0
            }
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
        let ui = self.active_ui();
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
                obs[sc] = 255;
                obs[OBS_CELLS + sc] = if self.nav.walk[lc] { 255 } else { 0 };
                obs[2 * OBS_CELLS + sc] =
                    255u8.saturating_sub(quant(selected_distance as f32, 40.0));
                obs[3 * OBS_CELLS + sc] = if self.state.iron_adj[lc] { 255 } else { 0 };
                obs[4 * OBS_CELLS + sc] = if self.state.water_adj[lc] { 255 } else { 0 };
                obs[103 * OBS_CELLS + sc] =
                    255u8.saturating_sub(quant(self.home_distance_from(target_pos) as f32, 40.0));
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
        self.fill_broadcast(obs, 80, quant(self.turns as f32, self.max_turns as f32));
        self.fill_broadcast(
            obs,
            81,
            quant((self.max_turns - self.turns) as f32, self.max_turns as f32),
        );
        self.fill_broadcast(obs, 82, quant(self.state.score(0) as f32, 400.0));
        self.fill_broadcast(obs, 83, quant(self.state.score(1) as f32, 400.0));
        self.fill_broadcast(obs, 84, quant(self.own_units().len() as f32, 6.0));
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

        if !self.target_built() {
            let cost = self.target_cost();
            for (offset, item) in RELEVANT_ITEMS.into_iter().enumerate() {
                self.fill_broadcast(obs, 90 + offset, quant(cost[item] as f32, 20.0));
                self.fill_broadcast(
                    obs,
                    94 + offset,
                    quant((cost[item] - self.state.inv[0][item]).max(0) as f32, 20.0),
                );
            }
        } else {
            self.fill_broadcast(obs, 90, quant(self.score_gain().max(0) as f32, 40.0));
            self.fill_broadcast(
                obs,
                91,
                quant(
                    (LEVEL3_SCORE_GAIN - self.score_gain()).max(0) as f32,
                    LEVEL3_SCORE_GAIN as f32,
                ),
            );
            self.fill_broadcast(obs, 92, if self.crop_exists() { 255 } else { 0 });
            self.fill_broadcast(obs, 93, quant(self.renewable_harvests as f32, 4.0));
            self.fill_broadcast(obs, 94, 255);
            self.fill_broadcast(obs, 95, if ui == self.starter_ui() { 255 } else { 0 });
            self.fill_broadcast(obs, 96, if ui != self.starter_ui() { 255 } else { 0 });
            self.fill_broadcast(obs, 97, if self.decision_phase == 1 { 255 } else { 0 });
        }
        self.fill_broadcast(obs, 98, if self.target_affordable() { 255 } else { 0 });
        let shack = self.state.shack[0];
        let shack_occupied = (0..self.state.n_units as usize)
            .any(|u| self.state.u_x[u] == shack.0 && self.state.u_y[u] == shack.1);
        self.fill_broadcast(obs, 99, if shack_occupied { 255 } else { 0 });
        let carrying_score =
            (0..4).any(|item| self.state.u_carry[ui][item] > 0) || self.state.u_carry[ui][WOOD] > 0;
        self.fill_broadcast(obs, 100, if carrying_score { 255 } else { 0 });
        let objective_cell = self.created_crop.unwrap_or(self.planned_crop);
        self.fill_broadcast(
            obs,
            101,
            quant(
                self.distance((sx, sy), objective_cell).unwrap_or(40) as f32,
                40.0,
            ),
        );
        self.fill_broadcast(obs, 102, quant(self.previous_action_plane as f32, 12.0));

        mask[action(0, sx, sy)] = 1;
        for pi in 0..self.state.n_plants as usize {
            mask[action(0, self.state.p_x[pi], self.state.p_y[pi])] = 1;
        }
        let home = self.state.shack[0];
        mask[action(0, home.0, home.1)] = 1;
        mask[action(0, self.planned_crop.0, self.planned_crop.1)] = 1;
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

    fn teacher_funding_action(&self) -> usize {
        let ui = self.starter_ui();
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
        let Some(item) = RELEVANT_ITEMS
            .into_iter()
            .filter(|&item| self.state.inv[0][item] < cost[item])
            .min_by_key(|&item| {
                self.best_source(item, here)
                    .and_then(|(pos, _)| self.distance(here, pos))
                    .unwrap_or(255)
            })
        else {
            return action(0, here.0, here.1);
        };
        if item == 4 && self.state.iron_adj[self.local_cell(here.0, here.1)] {
            return action(4, here.0, here.1);
        }
        if item < 4 {
            if let Some(pi) = self.state.plant_at(here.0, here.1) {
                if self.state.p_type[pi] as usize == item && self.state.p_fruits[pi] > 0 {
                    return action(1, here.0, here.1);
                }
            }
        }
        self.best_source(item, here)
            .map(|(source, _)| action(0, source.0, source.1))
            .unwrap_or_else(|| action(0, here.0, here.1))
    }

    fn bank_action(&self, ui: usize) -> usize {
        let here = (self.state.u_x[ui], self.state.u_y[ui]);
        let home = self.state.shack[0];
        if (here.0 - home.0).abs() + (here.1 - home.1).abs() <= 1 {
            action(3, here.0, here.1)
        } else {
            action(0, home.0, home.1)
        }
    }

    fn teacher_farmer_action(&self, ui: usize) -> usize {
        let here = (self.state.u_x[ui], self.state.u_y[ui]);
        let home = self.state.shack[0];
        let carried: i8 = self.state.u_carry[ui].iter().sum();
        if !self.crop_exists() {
            if self.state.u_carry[ui][BANANA] > 0 {
                return if here == self.planned_crop {
                    action(5 + BANANA, here.0, here.1)
                } else {
                    action(0, self.planned_crop.0, self.planned_crop.1)
                };
            }
            if carried > 0 {
                return self.bank_action(ui);
            }
            if (here.0 - home.0).abs() + (here.1 - home.1).abs() <= 1
                && self.state.free(ui) > 0
                && self.state.inv[0][BANANA] > 0
            {
                return action(9 + BANANA, here.0, here.1);
            }
            return action(0, home.0, home.1);
        }
        let crop = self
            .created_crop
            .expect("crop_exists implies a tracked crop");
        if self.renewable_harvests == 0 {
            if carried > 0 {
                return self.bank_action(ui);
            }
            if here == crop {
                let pi = self.state.plant_at(crop.0, crop.1).unwrap();
                if self.state.p_fruits[pi] > 0 && self.state.free(ui) > 0 {
                    return action(1, here.0, here.1);
                }
            }
            return action(0, crop.0, crop.1);
        }
        if carried > 0 {
            return self.bank_action(ui);
        }
        let nearest = (0..self.state.n_plants as usize)
            .filter(|&pi| self.state.p_fruits[pi] > 0)
            .filter_map(|pi| {
                let pos = (self.state.p_x[pi], self.state.p_y[pi]);
                self.distance(here, pos)
                    .map(|distance| (distance, pos.1, pos.0, pos))
            })
            .min();
        if let Some((_, _, _, target)) = nearest {
            if target == here {
                action(1, here.0, here.1)
            } else {
                action(0, target.0, target.1)
            }
        } else {
            action(0, crop.0, crop.1)
        }
    }

    fn teacher_reacquiring_farmer_action(&self, ui: usize) -> usize {
        let here = (self.state.u_x[ui], self.state.u_y[ui]);
        let carried: i8 = self.state.u_carry[ui].iter().sum();
        if !self.crop_exists() && carried == 0 && self.state.inv[0][BANANA] == 0 {
            if self.state.free(ui) > 0
                && self.state.plant_at(here.0, here.1).is_some_and(|plant| {
                    self.state.p_type[plant] as usize == BANANA && self.state.p_fruits[plant] > 0
                })
            {
                return action(1, here.0, here.1);
            }
            if let Some((source, _)) = self.best_source(BANANA, here) {
                return action(0, source.0, source.1);
            }
        }
        self.teacher_farmer_action(ui)
    }

    fn teacher_chopper_action(&self, ui: usize) -> usize {
        let here = (self.state.u_x[ui], self.state.u_y[ui]);
        let carried_value: i16 = (0..4)
            .map(|item| self.state.u_carry[ui][item] as i16)
            .sum::<i16>()
            + 4 * self.state.u_carry[ui][WOOD] as i16;
        if carried_value > 0
            && (self.state.free(ui) == 0 || self.score_gain() + carried_value >= LEVEL3_SCORE_GAIN)
        {
            return self.bank_action(ui);
        }
        if self.state.plant_at(here.0, here.1).is_some() {
            if Some(here) != self.created_crop && self.state.u_chop[ui] > 0 {
                return action(2, here.0, here.1);
            }
        }
        let target = (0..self.state.n_plants as usize)
            .filter(|&pi| Some((self.state.p_x[pi], self.state.p_y[pi])) != self.created_crop)
            .filter_map(|pi| {
                let pos = (self.state.p_x[pi], self.state.p_y[pi]);
                self.distance(here, pos)
                    .map(|distance| (distance, -self.state.p_size[pi], pos.1, pos.0, pos))
            })
            .min();
        if let Some((_, _, _, _, pos)) = target {
            action(0, pos.0, pos.1)
        } else if carried_value > 0 {
            self.bank_action(ui)
        } else {
            action(0, here.0, here.1)
        }
    }

    pub fn teacher_action(&self) -> usize {
        if !self.target_built() {
            return self.teacher_funding_action();
        }
        let ui = self.active_ui();
        if ui == self.starter_ui() {
            if self.opponent_mode == OpponentMode::CropFirstFundedTrioRepeatedPressureReacquire180 {
                self.teacher_reacquiring_farmer_action(ui)
            } else {
                self.teacher_farmer_action(ui)
            }
        } else {
            self.teacher_chopper_action(ui)
        }
    }

    fn natural_forager_commands(&self) -> FCmds {
        let mut commands = FCmds::default();
        let player = 1usize;
        let shack = self.state.shack[player];
        for ui in 0..self.state.n_units as usize {
            if self.state.u_pl[ui] as usize != player {
                continue;
            }
            let here = (self.state.u_x[ui], self.state.u_y[ui]);
            let carried: i16 = (0..4).map(|item| self.state.u_carry[ui][item] as i16).sum();
            let target = (0..self.state.n_plants as usize)
                .filter(|&plant| {
                    self.initial_plant_cells[spatial(self.state.p_x[plant], self.state.p_y[plant])]
                        && self.state.p_fruits[plant] > 0
                })
                .map(|plant| {
                    let pos = (self.state.p_x[plant], self.state.p_y[plant]);
                    (
                        self.nav.d(
                            self.local_cell(here.0, here.1),
                            self.local_cell(pos.0, pos.1),
                        ),
                        pos.1,
                        pos.0,
                        pos,
                    )
                })
                .min();

            let bank = || {
                if (here.0 - shack.0).abs() + (here.1 - shack.1).abs() <= 1 {
                    return FAct::Drop;
                }
                let drop = [(0i8, 1i8), (1, 0), (0, -1), (-1, 0)]
                    .into_iter()
                    .filter_map(|(dx, dy)| {
                        let pos = (shack.0 + dx, shack.1 + dy);
                        if pos.0 < 0 || pos.1 < 0 || pos.0 >= self.state.w || pos.1 >= self.state.h
                        {
                            return None;
                        }
                        let cell = self.local_cell(pos.0, pos.1);
                        self.nav.walk[cell].then_some((
                            self.nav.d(self.local_cell(here.0, here.1), cell),
                            pos.1,
                            pos.0,
                            cell,
                        ))
                    })
                    .min();
                drop.map(|(_, _, _, cell)| FAct::Move(cell as u8))
                    .unwrap_or_else(|| FAct::Move(self.local_cell(here.0, here.1) as u8))
            };

            commands.acts[ui] = if carried > 0 && (self.state.free(ui) == 0 || target.is_none()) {
                bank()
            } else if self.state.free(ui) > 0
                && self.state.plant_at(here.0, here.1).is_some_and(|plant| {
                    self.initial_plant_cells[spatial(here.0, here.1)]
                        && self.state.p_fruits[plant] > 0
                })
            {
                FAct::Harvest
            } else if let Some((_, _, _, pos)) = target {
                FAct::Move(self.local_cell(pos.0, pos.1) as u8)
            } else if carried > 0 {
                bank()
            } else {
                FAct::Move(self.local_cell(here.0, here.1) as u8)
            };
        }
        commands
    }

    fn opponent_bank_action(&self, ui: usize) -> FAct {
        let player = 1usize;
        let here = (self.state.u_x[ui], self.state.u_y[ui]);
        let shack = self.state.shack[player];
        if (here.0 - shack.0).abs() + (here.1 - shack.1).abs() <= 1 {
            return FAct::Drop;
        }
        [(0i8, 1i8), (1, 0), (0, -1), (-1, 0)]
            .into_iter()
            .filter_map(|(dx, dy)| {
                let pos = (shack.0 + dx, shack.1 + dy);
                if pos.0 < 0 || pos.1 < 0 || pos.0 >= self.state.w || pos.1 >= self.state.h {
                    return None;
                }
                let cell = self.local_cell(pos.0, pos.1);
                self.nav.walk[cell].then_some((
                    self.nav.d(self.local_cell(here.0, here.1), cell),
                    pos.1,
                    pos.0,
                    cell,
                ))
            })
            .min()
            .map(|(_, _, _, cell)| FAct::Move(cell as u8))
            .unwrap_or_else(|| FAct::Move(self.local_cell(here.0, here.1) as u8))
    }

    fn natural_planter_commands(&mut self) -> FCmds {
        if self.opponent_created_crop.is_some_and(|(pos, species)| {
            !self
                .state
                .plant_at(pos.0, pos.1)
                .is_some_and(|plant| self.state.p_type[plant] == species)
        }) {
            self.opponent_created_crop = None;
        }
        if self.opponent_created_crop.is_none()
            && self
                .state
                .plant_at(self.opponent_planned_crop.0, self.opponent_planned_crop.1)
                .is_some()
        {
            if let Some(next_crop) = Self::choose_crop_cell_for_player(&self.state, &self.nav, 1) {
                self.opponent_planned_crop = next_crop;
            }
        }

        let mut commands = FCmds::default();
        let Some(ui) = (0..self.state.n_units as usize).find(|&unit| self.state.u_pl[unit] == 1)
        else {
            return commands;
        };
        let here = (self.state.u_x[ui], self.state.u_y[ui]);
        let free = self.state.free(ui);
        let carried_fruit: i16 = (0..4).map(|item| self.state.u_carry[ui][item] as i16).sum();

        let natural_target = || {
            (0..self.state.n_plants as usize)
                .filter(|&plant| {
                    self.initial_plant_cells[spatial(self.state.p_x[plant], self.state.p_y[plant])]
                        && self.state.p_fruits[plant] > 0
                })
                .map(|plant| {
                    let pos = (self.state.p_x[plant], self.state.p_y[plant]);
                    (
                        self.nav.d(
                            self.local_cell(here.0, here.1),
                            self.local_cell(pos.0, pos.1),
                        ),
                        pos.1,
                        pos.0,
                        pos,
                    )
                })
                .min()
                .map(|(_, _, _, pos)| pos)
        };
        let harvest_or_move = |target: (i8, i8)| {
            if here == target && free > 0 {
                FAct::Harvest
            } else {
                FAct::Move(self.local_cell(target.0, target.1) as u8)
            }
        };

        commands.acts[ui] = if self.opponent_created_crop.is_none() {
            if let Some(species) = (0..4).find(|&item| self.state.u_carry[ui][item] > 0) {
                if here == self.opponent_planned_crop
                    && self.state.plant_at(here.0, here.1).is_none()
                {
                    FAct::Plant(species as u8)
                } else {
                    FAct::Move(
                        self.local_cell(self.opponent_planned_crop.0, self.opponent_planned_crop.1)
                            as u8,
                    )
                }
            } else if let Some(target) = natural_target() {
                harvest_or_move(target)
            } else {
                FAct::Move(self.local_cell(here.0, here.1) as u8)
            }
        } else if carried_fruit > 0 {
            self.opponent_bank_action(ui)
        } else {
            let (crop, _) = self.opponent_created_crop.expect("checked above");
            if self
                .state
                .plant_at(crop.0, crop.1)
                .is_some_and(|plant| self.state.p_fruits[plant] > 0 && free > 0)
            {
                harvest_or_move(crop)
            } else if let Some(target) = natural_target() {
                harvest_or_move(target)
            } else {
                FAct::Move(self.local_cell(crop.0, crop.1) as u8)
            }
        };
        commands
    }

    fn one_shot_reaper_commands(&mut self) -> FCmds {
        if self.opponent_crop_destructions == 0 && self.crop_exists() {
            let mut commands = FCmds::default();
            let crop = self.created_crop.expect("crop_exists implies tracked crop");
            if let Some(ui) = (0..self.state.n_units as usize)
                .find(|&unit| self.state.u_pl[unit] == 1 && self.state.u_chop[unit] > 0)
            {
                let here = (self.state.u_x[ui], self.state.u_y[ui]);
                commands.acts[ui] = if here == crop {
                    FAct::Chop
                } else {
                    FAct::Move(self.local_cell(crop.0, crop.1) as u8)
                };
                return commands;
            }
        }
        self.natural_planter_commands()
    }

    fn opponent_funding_action(&self, ui: usize, worker_count: i16, target: WorkerSpec) -> FAct {
        let here = (self.state.u_x[ui], self.state.u_y[ui]);
        let carried_cost_item: i16 = [0usize, 1, 2, 4]
            .into_iter()
            .map(|item| self.state.u_carry[ui][item] as i16)
            .sum();
        if carried_cost_item > 0 {
            return self.opponent_bank_action(ui);
        }

        let cost = training_cost_fast(worker_count, target);
        let deficit: [bool; 6] = std::array::from_fn(|item| self.state.inv[1][item] < cost[item]);
        let has_deficit = [0usize, 1, 2, 4].into_iter().any(|item| deficit[item]);
        let mut best: Option<((bool, u8, usize, i8, i8), FAct)> = None;
        let from = self.local_cell(here.0, here.1);

        for plant in 0..self.state.n_plants as usize {
            let item = self.state.p_type[plant] as usize;
            if item >= 3 || (has_deficit && !deficit[item]) {
                continue;
            }
            let pos = (self.state.p_x[plant], self.state.p_y[plant]);
            let distance = self.nav.d(from, self.local_cell(pos.0, pos.1));
            if distance == u8::MAX {
                continue;
            }
            let ready = self.state.p_fruits[plant] > 0;
            let act = if here == pos && ready && self.state.free(ui) > 0 {
                FAct::Harvest
            } else {
                FAct::Move(self.local_cell(pos.0, pos.1) as u8)
            };
            let key = (!ready, distance, item, pos.1, pos.0);
            if best.as_ref().map_or(true, |(old, _)| key < *old) {
                best = Some((key, act));
            }
        }

        if self.state.has_iron && (!has_deficit || deficit[4]) {
            for cell in 0..(self.state.w as usize * self.state.h as usize) {
                if !self.state.iron_adj[cell] || !self.nav.walk[cell] {
                    continue;
                }
                let distance = self.nav.d(from, cell);
                if distance == u8::MAX {
                    continue;
                }
                let x = (cell % self.state.w as usize) as i8;
                let y = (cell / self.state.w as usize) as i8;
                let act = if cell == from && self.state.free(ui) > 0 {
                    FAct::Mine
                } else {
                    FAct::Move(cell as u8)
                };
                let key = (false, distance, 4usize, y, x);
                if best.as_ref().map_or(true, |(old, _)| key < *old) {
                    best = Some((key, act));
                }
            }
        }

        best.map(|(_, act)| act)
            .unwrap_or_else(|| FAct::Move(from as u8))
    }

    fn opponent_crop_destruction_limit(&self) -> u8 {
        match self.opponent_mode {
            OpponentMode::OneShotReaper
            | OpponentMode::FundedPair
            | OpponentMode::FundedTrio
            | OpponentMode::FundedTrioSustained
            | OpponentMode::FundedTrioSustained180
            | OpponentMode::CropFirstFundedTrioSustained180 => 1,
            OpponentMode::CropFirstFundedTrioRepeatedPressure180
            | OpponentMode::CropFirstFundedTrioRepeatedPressureReacquire180 => 3,
            _ => 0,
        }
    }

    fn funded_pair_chopper_action(&self, ui: usize) -> FAct {
        let here = (self.state.u_x[ui], self.state.u_y[ui]);
        let carried_wood = self.state.u_carry[ui][WOOD];
        if carried_wood > 0 && self.state.free(ui) == 0 {
            return self.opponent_bank_action(ui);
        }
        if self.opponent_crop_destructions < self.opponent_crop_destruction_limit()
            && self.crop_exists()
        {
            let crop = self.created_crop.expect("crop_exists implies tracked crop");
            return if here == crop {
                FAct::Chop
            } else {
                FAct::Move(self.local_cell(crop.0, crop.1) as u8)
            };
        }

        let opponent_crop = self.opponent_created_crop.map(|(pos, _)| pos);
        let target = (0..self.state.n_plants as usize)
            .filter(|&plant| {
                let pos = (self.state.p_x[plant], self.state.p_y[plant]);
                self.initial_plant_cells[spatial(pos.0, pos.1)]
                    && Some(pos) != self.created_crop
                    && Some(pos) != opponent_crop
            })
            .map(|plant| {
                let pos = (self.state.p_x[plant], self.state.p_y[plant]);
                (
                    self.nav.d(
                        self.local_cell(here.0, here.1),
                        self.local_cell(pos.0, pos.1),
                    ),
                    -self.state.p_size[plant],
                    pos.1,
                    pos.0,
                    pos,
                )
            })
            .filter(|(distance, _, _, _, _)| *distance != u8::MAX)
            .min();
        if let Some((_, _, _, _, pos)) = target {
            if here == pos {
                FAct::Chop
            } else {
                FAct::Move(self.local_cell(pos.0, pos.1) as u8)
            }
        } else if carried_wood > 0 {
            self.opponent_bank_action(ui)
        } else {
            FAct::Move(self.local_cell(here.0, here.1) as u8)
        }
    }

    fn funded_pair_commands(&mut self) -> FCmds {
        let opponent_units: Vec<usize> = (0..self.state.n_units as usize)
            .filter(|&unit| self.state.u_pl[unit] == 1)
            .collect();
        if opponent_units.len() == 1 {
            let ui = opponent_units[0];
            let cost = training_cost_fast(1, OPPONENT_D5_TARGET);
            let affordable = (0..6).all(|item| {
                (item == 4 && !self.state.has_iron) || self.state.inv[1][item] >= cost[item]
            });
            if affordable && self.opponent_funded_since_last_training {
                let mut commands = self.natural_planter_commands();
                commands.train = Some(OPPONENT_D5_TARGET);
                return commands;
            }
            let mut commands = FCmds::default();
            commands.acts[ui] = self.opponent_funding_action(ui, 1, OPPONENT_D5_TARGET);
            return commands;
        }

        let mut commands = self.natural_planter_commands();
        if let Some(ui) = opponent_units
            .into_iter()
            .find(|&unit| self.state.u_id[unit] != self.opponent_starter_id)
        {
            commands.acts[ui] = self.funded_pair_chopper_action(ui);
        }
        commands
    }

    fn funded_trio_forager_action(&self, ui: usize) -> FAct {
        let here = (self.state.u_x[ui], self.state.u_y[ui]);
        let carried: i16 = (0..4).map(|item| self.state.u_carry[ui][item] as i16).sum();
        let target = (0..self.state.n_plants as usize)
            .filter(|&plant| {
                self.initial_plant_cells[spatial(self.state.p_x[plant], self.state.p_y[plant])]
                    && self.state.p_fruits[plant] > 0
            })
            .map(|plant| {
                let pos = (self.state.p_x[plant], self.state.p_y[plant]);
                (
                    self.nav.d(
                        self.local_cell(here.0, here.1),
                        self.local_cell(pos.0, pos.1),
                    ),
                    pos.1,
                    pos.0,
                    pos,
                )
            })
            .filter(|(distance, _, _, _)| *distance != u8::MAX)
            .min();
        if carried > 0 && (self.state.free(ui) == 0 || target.is_none()) {
            return self.opponent_bank_action(ui);
        }
        if let Some((_, _, _, pos)) = target {
            if here == pos && self.state.free(ui) > 0 {
                FAct::Harvest
            } else {
                FAct::Move(self.local_cell(pos.0, pos.1) as u8)
            }
        } else if carried > 0 {
            self.opponent_bank_action(ui)
        } else {
            FAct::Move(self.local_cell(here.0, here.1) as u8)
        }
    }

    fn funded_trio_commands(&mut self) -> FCmds {
        let mut opponent_units: Vec<usize> = (0..self.state.n_units as usize)
            .filter(|&unit| self.state.u_pl[unit] == 1)
            .collect();
        opponent_units.sort_by_key(|&unit| self.state.u_id[unit]);
        if opponent_units.len() == 1 {
            let ui = opponent_units[0];
            let cost = training_cost_fast(1, OPPONENT_D5_TARGET);
            let affordable = (0..6).all(|item| {
                (item == 4 && !self.state.has_iron) || self.state.inv[1][item] >= cost[item]
            });
            if affordable && self.opponent_funded_since_last_training {
                let mut commands = self.natural_planter_commands();
                commands.train = Some(OPPONENT_D5_TARGET);
                return commands;
            }
            let mut commands = FCmds::default();
            commands.acts[ui] = self.opponent_funding_action(ui, 1, OPPONENT_D5_TARGET);
            return commands;
        }
        if opponent_units.len() == 2 {
            let starter = opponent_units[0];
            let chopper = opponent_units[1];
            let cost = training_cost_fast(2, OPPONENT_D6_TARGET);
            let affordable = (0..6).all(|item| {
                (item == 4 && !self.state.has_iron) || self.state.inv[1][item] >= cost[item]
            });
            let mut commands = FCmds::default();
            commands.acts[starter] = self.opponent_funding_action(starter, 2, OPPONENT_D6_TARGET);
            commands.acts[chopper] = self.funded_pair_chopper_action(chopper);
            if affordable && self.opponent_funded_since_last_training {
                commands.train = Some(OPPONENT_D6_TARGET);
            }
            return commands;
        }

        let mut commands = self.natural_planter_commands();
        commands.acts[opponent_units[1]] = self.funded_pair_chopper_action(opponent_units[1]);
        commands.acts[opponent_units[2]] = self.funded_trio_forager_action(opponent_units[2]);
        commands
    }

    fn crop_first_funded_trio_commands(&mut self) -> FCmds {
        let mut opponent_units: Vec<usize> = (0..self.state.n_units as usize)
            .filter(|&unit| self.state.u_pl[unit] == 1)
            .collect();
        opponent_units.sort_by_key(|&unit| self.state.u_id[unit]);
        if opponent_units.len() == 2 && self.opponent_created_crop.is_none() {
            let mut commands = self.natural_planter_commands();
            commands.acts[opponent_units[1]] = self.funded_pair_chopper_action(opponent_units[1]);
            debug_assert!(commands.train.is_none());
            return commands;
        }
        self.funded_trio_commands()
    }

    fn refresh_planned_crop(&mut self) {
        let supports_replanning = self.competitive
            || matches!(
                self.opponent_mode,
                OpponentMode::CompleteBaselineRecovery
                    | OpponentMode::NaturalPlanter
                    | OpponentMode::OneShotReaper
                    | OpponentMode::FundedPair
                    | OpponentMode::FundedTrio
                    | OpponentMode::FundedTrioSustained
                    | OpponentMode::FundedTrioSustained180
                    | OpponentMode::CropFirstFundedTrioSustained180
                    | OpponentMode::CropFirstFundedTrioRepeatedPressure180
                    | OpponentMode::CropFirstFundedTrioRepeatedPressureReacquire180
            );
        if supports_replanning && self.created_crop.is_some() && !self.crop_exists() {
            self.created_crop = None;
        }
        if !supports_replanning
            || self.created_crop.is_some()
            || self
                .state
                .plant_at(self.planned_crop.0, self.planned_crop.1)
                .is_none()
        {
            return;
        }
        if let Some(next_crop) = Self::choose_crop_cell(&self.state, &self.nav) {
            self.planned_crop = next_crop;
        }
    }

    fn execute_turn(&mut self, train: bool) {
        let player_crop_before = self.created_crop.filter(|&(x, y)| {
            self.state
                .plant_at(x, y)
                .is_some_and(|plant| self.state.p_type[plant] as usize == BANANA)
        });
        let before_positions: [(i8, i8); MAXU] =
            std::array::from_fn(|ui| (self.state.u_x[ui], self.state.u_y[ui]));
        let before_banana: [i8; MAXU] = std::array::from_fn(|ui| self.state.u_carry[ui][BANANA]);
        let before_carry = self.state.u_carry;
        let before_inv = self.state.inv;
        let before_ids = self.state.u_id;
        let before_players = self.state.u_pl;
        let before_n_units = self.state.n_units as usize;
        let before_plants: [bool; MAXU] = std::array::from_fn(|ui| {
            let (x, y) = before_positions[ui];
            self.state.plant_at(x, y).is_some()
        });
        let mut commands = [FCmds::default(), FCmds::default()];
        commands[0].acts = self.pending;
        if train {
            commands[0].train = Some(self.target);
        }
        commands[1] = match self.opponent_mode {
            OpponentMode::Waiting => FCmds::default(),
            OpponentMode::CompleteBaseline | OpponentMode::CompleteBaselineRecovery => {
                baseline_commands(&self.state, &self.nav, 1)
            }
            OpponentMode::NaturalForager => self.natural_forager_commands(),
            OpponentMode::NaturalPlanter => self.natural_planter_commands(),
            OpponentMode::OneShotReaper => self.one_shot_reaper_commands(),
            OpponentMode::FundedPair => self.funded_pair_commands(),
            OpponentMode::FundedTrio
            | OpponentMode::FundedTrioSustained
            | OpponentMode::FundedTrioSustained180 => self.funded_trio_commands(),
            OpponentMode::CropFirstFundedTrioSustained180
            | OpponentMode::CropFirstFundedTrioRepeatedPressure180
            | OpponentMode::CropFirstFundedTrioRepeatedPressureReacquire180 => {
                self.crop_first_funded_trio_commands()
            }
        };
        step_fast(&mut self.state, &self.nav, &commands);
        self.turns += 1;

        if matches!(
            self.opponent_mode,
            OpponentMode::FundedPair
                | OpponentMode::FundedTrio
                | OpponentMode::FundedTrioSustained
                | OpponentMode::FundedTrioSustained180
                | OpponentMode::CropFirstFundedTrioSustained180
                | OpponentMode::CropFirstFundedTrioRepeatedPressure180
                | OpponentMode::CropFirstFundedTrioRepeatedPressureReacquire180
        ) {
            let opponent_workers_before = (0..before_n_units)
                .filter(|&unit| before_players[unit] == 1)
                .count();
            let opponent_workers_after = (0..self.state.n_units as usize)
                .filter(|&unit| self.state.u_pl[unit] == 1)
                .count();
            if opponent_workers_before == 1 && opponent_workers_after == 2 {
                if self.opponent_training_turn == 0 {
                    self.opponent_training_turn = self.turns;
                }
                debug_assert!(self.opponent_funded_since_last_training);
                if self.opponent_funded_since_last_training {
                    self.opponent_funded_training_events =
                        self.opponent_funded_training_events.saturating_add(1);
                }
                self.opponent_funded_since_last_training = false;
            } else if opponent_workers_before == 2 && opponent_workers_after == 3 {
                if self.opponent_third_worker_training_turn == 0 {
                    self.opponent_third_worker_training_turn = self.turns;
                }
                debug_assert!(self.opponent_funded_since_last_training);
                if self.opponent_funded_since_last_training {
                    self.opponent_funded_training_events =
                        self.opponent_funded_training_events.saturating_add(1);
                }
                self.opponent_funded_since_last_training = false;
            }
            let funding_drop = (0..before_n_units).any(|ui| {
                before_players[ui] == 1
                    && before_ids[ui] == self.opponent_starter_id
                    && matches!(commands[1].acts[ui], FAct::Drop)
                    && [0usize, 1, 2, 4].into_iter().any(|item| {
                        before_carry[ui][item] > 0 && self.state.inv[1][item] > before_inv[1][item]
                    })
            });
            if funding_drop {
                self.opponent_funding_deposits = self.opponent_funding_deposits.saturating_add(1);
                self.opponent_funded_since_last_training = true;
            }
            let mut trained_ids: Vec<i16> = (0..before_n_units)
                .filter(|&ui| before_players[ui] == 1 && before_ids[ui] != self.opponent_starter_id)
                .map(|ui| before_ids[ui])
                .collect();
            trained_ids.sort_unstable();
            let productive = |ui: usize| {
                if before_players[ui] != 1 {
                    return false;
                }
                let pos = before_positions[ui];
                match commands[1].acts[ui] {
                    FAct::Chop => {
                        self.state.u_chop[ui] > 0
                            && before_plants[ui]
                            && self.state.u_x[ui] == pos.0
                            && self.state.u_y[ui] == pos.1
                    }
                    FAct::Drop => {
                        before_carry[ui].iter().any(|&amount| amount > 0)
                            && (pos.0 - self.state.shack[1].0).abs()
                                + (pos.1 - self.state.shack[1].1).abs()
                                <= 1
                    }
                    FAct::Harvest => {
                        before_plants[ui]
                            && self.state.u_hp[ui] > 0
                            && (0..4)
                                .any(|item| self.state.u_carry[ui][item] > before_carry[ui][item])
                    }
                    _ => false,
                }
            };
            let second_productive = trained_ids.first().is_some_and(|&worker_id| {
                (0..before_n_units)
                    .find(|&ui| before_ids[ui] == worker_id)
                    .is_some_and(productive)
            });
            if second_productive {
                self.opponent_second_worker_productive_actions = self
                    .opponent_second_worker_productive_actions
                    .saturating_add(1);
            }
            let third_productive = trained_ids.get(1).is_some_and(|&worker_id| {
                (0..before_n_units)
                    .find(|&ui| before_ids[ui] == worker_id)
                    .is_some_and(productive)
            });
            if third_productive {
                self.opponent_third_worker_productive_actions = self
                    .opponent_third_worker_productive_actions
                    .saturating_add(1);
            }
        }

        if matches!(
            self.opponent_mode,
            OpponentMode::NaturalPlanter
                | OpponentMode::OneShotReaper
                | OpponentMode::FundedPair
                | OpponentMode::FundedTrio
                | OpponentMode::FundedTrioSustained
                | OpponentMode::FundedTrioSustained180
                | OpponentMode::CropFirstFundedTrioSustained180
                | OpponentMode::CropFirstFundedTrioRepeatedPressure180
                | OpponentMode::CropFirstFundedTrioRepeatedPressureReacquire180
        ) {
            for ui in 0..before_n_units {
                if before_players[ui] != 1 {
                    continue;
                }
                let pos = before_positions[ui];
                match commands[1].acts[ui] {
                    FAct::Plant(species)
                        if before_carry[ui][species as usize]
                            > self.state.u_carry[ui][species as usize] =>
                    {
                        self.opponent_created_crops = self.opponent_created_crops.saturating_add(1);
                        if self
                            .state
                            .plant_at(pos.0, pos.1)
                            .is_some_and(|plant| self.state.p_type[plant] == species)
                        {
                            self.opponent_created_crop = Some((pos, species));
                        }
                    }
                    FAct::Harvest
                        if self.opponent_created_crop.is_some_and(|(crop, species)| {
                            crop == pos
                                && self.state.u_carry[ui][species as usize]
                                    > before_carry[ui][species as usize]
                        }) =>
                    {
                        self.opponent_renewable_harvests =
                            self.opponent_renewable_harvests.saturating_add(1);
                    }
                    _ => {}
                }
            }
        }
        let destruction_limit = self.opponent_crop_destruction_limit();
        if self.opponent_crop_destructions < destruction_limit {
            if let Some(crop) = player_crop_before {
                let chopped_by_opponent = (0..before_n_units).any(|ui| {
                    before_players[ui] == 1
                        && before_positions[ui] == crop
                        && matches!(commands[1].acts[ui], FAct::Chop)
                });
                let crop_survived = self
                    .state
                    .plant_at(crop.0, crop.1)
                    .is_some_and(|plant| self.state.p_type[plant] as usize == BANANA);
                if chopped_by_opponent && !crop_survived {
                    self.opponent_crop_destructions =
                        self.opponent_crop_destructions.saturating_add(1);
                    self.created_crop = None;
                }
            }
        }

        let own_after = self.own_units();
        for &ui in &own_after {
            if matches!(self.pending[ui], FAct::Plant(3)) && !before_plants[ui] {
                let (x, y) = before_positions[ui];
                if self
                    .state
                    .plant_at(x, y)
                    .is_some_and(|pi| self.state.p_type[pi] as usize == BANANA)
                {
                    self.created_crop = Some((x, y));
                }
            }
            if matches!(self.pending[ui], FAct::Harvest)
                && Some(before_positions[ui]) == self.created_crop
                && self.state.u_carry[ui][BANANA] > before_banana[ui]
            {
                self.renewable_harvests = self.renewable_harvests.saturating_add(1);
            }
        }
        self.refresh_planned_crop();
        if self.score_at_training.is_none() && self.target_built() {
            self.training_turn = self.turns;
            self.score_at_training = Some(self.state.score(0));
        }
        self.pending = [FAct::Idle; MAXU];
    }

    pub fn step(&mut self, selected_action: usize) -> Level3Terminal {
        let ui = self.active_ui();
        self.pending[ui] = self.decode(selected_action);
        self.previous_action_plane = (selected_action / OBS_CELLS).min(12) as u8;

        if self.target_built() && self.decision_phase == 0 {
            self.decision_phase = 1;
            return Level3Terminal {
                reward: 0.0,
                done: false,
                success: false,
                turns: self.turns,
                episode_return: self.episode_return,
                seed: self.seed,
                height: self.state.h as u8,
                initial_total_deficit: self.initial_total_deficit,
                training_turn: self.training_turn,
                score_gain: self.reported_score_gain(),
                renewable_harvests: self.renewable_harvests,
                created_crop: self.crop_exists(),
                recipe_id: self.recipe_id,
                target: self.target,
                opponent_score: self.state.score(1).clamp(i16::MIN as i32, i16::MAX as i32) as i16,
                opponent_workers: (0..self.state.n_units as usize)
                    .filter(|&unit| self.state.u_pl[unit] == 1)
                    .count()
                    .min(u8::MAX as usize) as u8,
                opponent_created_crops: self.opponent_created_crops,
                opponent_renewable_harvests: self.opponent_renewable_harvests,
                opponent_crop_destructions: self.opponent_crop_destructions,
                opponent_training_turn: self.opponent_training_turn,
                opponent_funding_deposits: self.opponent_funding_deposits,
                opponent_funded_training_events: self.opponent_funded_training_events,
                opponent_second_worker_productive_actions: self
                    .opponent_second_worker_productive_actions,
                opponent_third_worker_training_turn: self.opponent_third_worker_training_turn,
                opponent_third_worker_productive_actions: self
                    .opponent_third_worker_productive_actions,
            };
        }

        let should_train = !self.target_built();
        self.execute_turn(should_train);
        self.decision_phase = 0;
        if self.competitive {
            let margin = self.state.score(0) - self.state.score(1);
            let reward = (margin - self.previous_margin) as f32 / 100.0;
            self.previous_margin = margin;
            self.episode_return += reward;
            let done = self.turns >= self.max_turns;
            if done {
                self.episode_return = margin as f32 / 100.0;
            }
            return Level3Terminal {
                reward,
                done,
                success: done && margin > 0,
                turns: self.turns,
                episode_return: self.episode_return,
                seed: self.seed,
                height: self.state.h as u8,
                initial_total_deficit: self.initial_total_deficit,
                training_turn: self.training_turn,
                score_gain: self.reported_score_gain(),
                renewable_harvests: self.renewable_harvests,
                created_crop: self.crop_exists(),
                recipe_id: self.recipe_id,
                target: self.target,
                opponent_score: self.state.score(1).clamp(i16::MIN as i32, i16::MAX as i32) as i16,
                opponent_workers: (0..self.state.n_units as usize)
                    .filter(|&unit| self.state.u_pl[unit] == 1)
                    .count()
                    .min(u8::MAX as usize) as u8,
                opponent_created_crops: self.opponent_created_crops,
                opponent_renewable_harvests: self.opponent_renewable_harvests,
                opponent_crop_destructions: self.opponent_crop_destructions,
                opponent_training_turn: self.opponent_training_turn,
                opponent_funding_deposits: self.opponent_funding_deposits,
                opponent_funded_training_events: self.opponent_funded_training_events,
                opponent_second_worker_productive_actions: self
                    .opponent_second_worker_productive_actions,
                opponent_third_worker_training_turn: self.opponent_third_worker_training_turn,
                opponent_third_worker_productive_actions: self
                    .opponent_third_worker_productive_actions,
            };
        }
        let success = self.success();
        let next_progress = self.objective_progress();
        let mut reward = next_progress - self.progress - 0.01;
        if success {
            reward += 20.0;
        }
        let timeout = self.turns >= self.max_turns && !success;
        if timeout {
            reward -= 20.0;
        }
        self.progress = next_progress;
        self.episode_return += reward;
        Level3Terminal {
            reward,
            done: success || timeout,
            success,
            turns: self.turns,
            episode_return: self.episode_return,
            seed: self.seed,
            height: self.state.h as u8,
            initial_total_deficit: self.initial_total_deficit,
            training_turn: self.training_turn,
            score_gain: self.reported_score_gain(),
            renewable_harvests: self.renewable_harvests,
            created_crop: self.crop_exists(),
            recipe_id: self.recipe_id,
            target: self.target,
            opponent_score: self.state.score(1).clamp(i16::MIN as i32, i16::MAX as i32) as i16,
            opponent_workers: (0..self.state.n_units as usize)
                .filter(|&unit| self.state.u_pl[unit] == 1)
                .count()
                .min(u8::MAX as usize) as u8,
            opponent_created_crops: self.opponent_created_crops,
            opponent_renewable_harvests: self.opponent_renewable_harvests,
            opponent_crop_destructions: self.opponent_crop_destructions,
            opponent_training_turn: self.opponent_training_turn,
            opponent_funding_deposits: self.opponent_funding_deposits,
            opponent_funded_training_events: self.opponent_funded_training_events,
            opponent_second_worker_productive_actions: self
                .opponent_second_worker_productive_actions,
            opponent_third_worker_training_turn: self.opponent_third_worker_training_turn,
            opponent_third_worker_productive_actions: self.opponent_third_worker_productive_actions,
        }
    }
}

pub struct Level3Batch {
    envs: Vec<Level3Env>,
    next_seed: u64,
    max_turns: u16,
    randomized_targets: bool,
    opponent_mode: OpponentMode,
    competitive: bool,
}

impl Level3Batch {
    pub fn new(num_envs: usize, seed_base: u64, max_turns: u16) -> Self {
        assert!(num_envs > 0);
        Self {
            envs: (0..num_envs)
                .map(|offset| Level3Env::new(seed_base + offset as u64, max_turns))
                .collect(),
            next_seed: seed_base + num_envs as u64,
            max_turns,
            randomized_targets: false,
            opponent_mode: OpponentMode::Waiting,
            competitive: false,
        }
    }

    pub fn new_level4(num_envs: usize, seed_base: u64, max_turns: u16) -> Self {
        assert!(num_envs > 0);
        Self {
            envs: (0..num_envs)
                .map(|offset| Level3Env::new_level4(seed_base + offset as u64, max_turns))
                .collect(),
            next_seed: seed_base + num_envs as u64,
            max_turns,
            randomized_targets: true,
            opponent_mode: OpponentMode::Waiting,
            competitive: false,
        }
    }

    pub fn new_level5(num_envs: usize, seed_base: u64, max_turns: u16) -> Self {
        assert!(num_envs > 0);
        Self {
            envs: (0..num_envs)
                .map(|offset| Level3Env::new_level5(seed_base + offset as u64, max_turns))
                .collect(),
            next_seed: seed_base + num_envs as u64,
            max_turns,
            randomized_targets: true,
            opponent_mode: OpponentMode::CompleteBaseline,
            competitive: false,
        }
    }

    pub fn new_level5_recovery(num_envs: usize, seed_base: u64, max_turns: u16) -> Self {
        assert!(num_envs > 0);
        Self {
            envs: (0..num_envs)
                .map(|offset| Level3Env::new_level5_recovery(seed_base + offset as u64, max_turns))
                .collect(),
            next_seed: seed_base + num_envs as u64,
            max_turns,
            randomized_targets: true,
            opponent_mode: OpponentMode::CompleteBaselineRecovery,
            competitive: false,
        }
    }

    pub fn new_level5_forager(num_envs: usize, seed_base: u64, max_turns: u16) -> Self {
        assert!(num_envs > 0);
        Self {
            envs: (0..num_envs)
                .map(|offset| Level3Env::new_level5_forager(seed_base + offset as u64, max_turns))
                .collect(),
            next_seed: seed_base + num_envs as u64,
            max_turns,
            randomized_targets: true,
            opponent_mode: OpponentMode::NaturalForager,
            competitive: false,
        }
    }

    pub fn new_level5_planter(num_envs: usize, seed_base: u64, max_turns: u16) -> Self {
        assert!(num_envs > 0);
        Self {
            envs: (0..num_envs)
                .map(|offset| Level3Env::new_level5_planter(seed_base + offset as u64, max_turns))
                .collect(),
            next_seed: seed_base + num_envs as u64,
            max_turns,
            randomized_targets: true,
            opponent_mode: OpponentMode::NaturalPlanter,
            competitive: false,
        }
    }

    pub fn new_level5_reaper(num_envs: usize, seed_base: u64, max_turns: u16) -> Self {
        assert!(num_envs > 0);
        Self {
            envs: (0..num_envs)
                .map(|offset| Level3Env::new_level5_reaper(seed_base + offset as u64, max_turns))
                .collect(),
            next_seed: seed_base + num_envs as u64,
            max_turns,
            randomized_targets: true,
            opponent_mode: OpponentMode::OneShotReaper,
            competitive: false,
        }
    }

    pub fn new_level5_funded_pair(num_envs: usize, seed_base: u64, max_turns: u16) -> Self {
        assert!(num_envs > 0);
        Self {
            envs: (0..num_envs)
                .map(|offset| {
                    Level3Env::new_level5_funded_pair(seed_base + offset as u64, max_turns)
                })
                .collect(),
            next_seed: seed_base + num_envs as u64,
            max_turns,
            randomized_targets: true,
            opponent_mode: OpponentMode::FundedPair,
            competitive: false,
        }
    }

    pub fn new_level5_funded_trio(num_envs: usize, seed_base: u64, max_turns: u16) -> Self {
        assert!(num_envs > 0);
        Self {
            envs: (0..num_envs)
                .map(|offset| {
                    Level3Env::new_level5_funded_trio(seed_base + offset as u64, max_turns)
                })
                .collect(),
            next_seed: seed_base + num_envs as u64,
            max_turns,
            randomized_targets: true,
            opponent_mode: OpponentMode::FundedTrio,
            competitive: false,
        }
    }

    pub fn new_level5_funded_trio_sustained(
        num_envs: usize,
        seed_base: u64,
        max_turns: u16,
    ) -> Self {
        assert!(num_envs > 0);
        Self {
            envs: (0..num_envs)
                .map(|offset| {
                    Level3Env::new_level5_funded_trio_sustained(
                        seed_base + offset as u64,
                        max_turns,
                    )
                })
                .collect(),
            next_seed: seed_base + num_envs as u64,
            max_turns,
            randomized_targets: true,
            opponent_mode: OpponentMode::FundedTrioSustained,
            competitive: false,
        }
    }

    pub fn new_level5_funded_trio_sustained_180(
        num_envs: usize,
        seed_base: u64,
        max_turns: u16,
    ) -> Self {
        assert!(num_envs > 0);
        Self {
            envs: (0..num_envs)
                .map(|offset| {
                    Level3Env::new_level5_funded_trio_sustained_180(
                        seed_base + offset as u64,
                        max_turns,
                    )
                })
                .collect(),
            next_seed: seed_base + num_envs as u64,
            max_turns,
            randomized_targets: true,
            opponent_mode: OpponentMode::FundedTrioSustained180,
            competitive: false,
        }
    }

    pub fn new_level5_crop_first_funded_trio_sustained_180(
        num_envs: usize,
        seed_base: u64,
        max_turns: u16,
    ) -> Self {
        assert!(num_envs > 0);
        Self {
            envs: (0..num_envs)
                .map(|offset| {
                    Level3Env::new_level5_crop_first_funded_trio_sustained_180(
                        seed_base + offset as u64,
                        max_turns,
                    )
                })
                .collect(),
            next_seed: seed_base + num_envs as u64,
            max_turns,
            randomized_targets: true,
            opponent_mode: OpponentMode::CropFirstFundedTrioSustained180,
            competitive: false,
        }
    }

    pub fn new_level5_crop_first_funded_trio_repeated_pressure_180(
        num_envs: usize,
        seed_base: u64,
        max_turns: u16,
    ) -> Self {
        assert!(num_envs > 0);
        Self {
            envs: (0..num_envs)
                .map(|offset| {
                    Level3Env::new_level5_crop_first_funded_trio_repeated_pressure_180(
                        seed_base + offset as u64,
                        max_turns,
                    )
                })
                .collect(),
            next_seed: seed_base + num_envs as u64,
            max_turns,
            randomized_targets: true,
            opponent_mode: OpponentMode::CropFirstFundedTrioRepeatedPressure180,
            competitive: false,
        }
    }

    pub fn new_level5_crop_first_funded_trio_repeated_pressure_reacquire_180(
        num_envs: usize,
        seed_base: u64,
        max_turns: u16,
    ) -> Self {
        assert!(num_envs > 0);
        Self {
            envs: (0..num_envs)
                .map(|offset| {
                    Level3Env::new_level5_crop_first_funded_trio_repeated_pressure_reacquire_180(
                        seed_base + offset as u64,
                        max_turns,
                    )
                })
                .collect(),
            next_seed: seed_base + num_envs as u64,
            max_turns,
            randomized_targets: true,
            opponent_mode: OpponentMode::CropFirstFundedTrioRepeatedPressureReacquire180,
            competitive: false,
        }
    }

    pub fn new_level6(num_envs: usize, seed_base: u64, max_turns: u16) -> Self {
        assert!(num_envs > 0);
        Self {
            envs: (0..num_envs)
                .map(|offset| Level3Env::new_level6(seed_base + offset as u64, max_turns))
                .collect(),
            next_seed: seed_base + num_envs as u64,
            max_turns,
            randomized_targets: true,
            opponent_mode: OpponentMode::Waiting,
            competitive: true,
        }
    }

    fn len(&self) -> usize {
        self.envs.len()
    }

    fn reset_slot(&mut self, index: usize) {
        let seed = self.next_seed;
        self.next_seed += 1;
        if self.competitive {
            self.envs[index] = Level3Env::new_level6(seed, self.max_turns);
            return;
        }
        self.envs[index] = match (self.randomized_targets, self.opponent_mode) {
            (false, _) => Level3Env::new(seed, self.max_turns),
            (true, OpponentMode::Waiting) => Level3Env::new_level4(seed, self.max_turns),
            (true, OpponentMode::CompleteBaseline) => Level3Env::new_level5(seed, self.max_turns),
            (true, OpponentMode::CompleteBaselineRecovery) => {
                Level3Env::new_level5_recovery(seed, self.max_turns)
            }
            (true, OpponentMode::NaturalForager) => {
                Level3Env::new_level5_forager(seed, self.max_turns)
            }
            (true, OpponentMode::NaturalPlanter) => {
                Level3Env::new_level5_planter(seed, self.max_turns)
            }
            (true, OpponentMode::OneShotReaper) => {
                Level3Env::new_level5_reaper(seed, self.max_turns)
            }
            (true, OpponentMode::FundedPair) => {
                Level3Env::new_level5_funded_pair(seed, self.max_turns)
            }
            (true, OpponentMode::FundedTrio) => {
                Level3Env::new_level5_funded_trio(seed, self.max_turns)
            }
            (true, OpponentMode::FundedTrioSustained) => {
                Level3Env::new_level5_funded_trio_sustained(seed, self.max_turns)
            }
            (true, OpponentMode::FundedTrioSustained180) => {
                Level3Env::new_level5_funded_trio_sustained_180(seed, self.max_turns)
            }
            (true, OpponentMode::CropFirstFundedTrioSustained180) => {
                Level3Env::new_level5_crop_first_funded_trio_sustained_180(seed, self.max_turns)
            }
            (true, OpponentMode::CropFirstFundedTrioRepeatedPressure180) => {
                Level3Env::new_level5_crop_first_funded_trio_repeated_pressure_180(
                    seed,
                    self.max_turns,
                )
            }
            (true, OpponentMode::CropFirstFundedTrioRepeatedPressureReacquire180) => {
                Level3Env::new_level5_crop_first_funded_trio_repeated_pressure_reacquire_180(
                    seed,
                    self.max_turns,
                )
            }
        };
    }

    fn observe(&self, obs: &mut [u8], masks: &mut [u8]) {
        for (index, env) in self.envs.iter().enumerate() {
            env.observe(
                &mut obs[index * OBS_SIZE..(index + 1) * OBS_SIZE],
                &mut masks[index * ACTION_SIZE..(index + 1) * ACTION_SIZE],
            );
        }
    }

    fn teacher_actions(&self, actions: &mut [i32]) {
        for (out, env) in actions.iter_mut().zip(&self.envs) {
            *out = env.teacher_action() as i32;
        }
    }

    fn current_metadata(&self, turns: &mut [u16], phases: &mut [u8], seeds: &mut [u64]) {
        for (index, env) in self.envs.iter().enumerate() {
            turns[index] = env.turns;
            phases[index] = env.decision_phase;
            seeds[index] = env.seed;
        }
    }
}

#[no_mangle]
pub extern "C" fn tf_level3_obs_size() -> usize {
    OBS_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level3_action_size() -> usize {
    ACTION_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level3_create(
    num_envs: usize,
    seed_base: u64,
    max_turns: u16,
) -> *mut Level3Batch {
    if num_envs == 0 || max_turns == 0 {
        return std::ptr::null_mut();
    }
    Box::into_raw(Box::new(Level3Batch::new(num_envs, seed_base, max_turns)))
}

#[no_mangle]
pub unsafe extern "C" fn tf_level3_destroy(handle: *mut Level3Batch) {
    if !handle.is_null() {
        drop(Box::from_raw(handle));
    }
}

#[no_mangle]
pub unsafe extern "C" fn tf_level3_observe(
    handle: *mut Level3Batch,
    obs: *mut u8,
    masks: *mut u8,
) -> i32 {
    if handle.is_null() || obs.is_null() || masks.is_null() {
        return -1;
    }
    let batch = &*handle;
    batch.observe(
        std::slice::from_raw_parts_mut(obs, batch.len() * OBS_SIZE),
        std::slice::from_raw_parts_mut(masks, batch.len() * ACTION_SIZE),
    );
    0
}

#[no_mangle]
pub unsafe extern "C" fn tf_level3_teacher_actions(
    handle: *mut Level3Batch,
    actions: *mut i32,
) -> i32 {
    if handle.is_null() || actions.is_null() {
        return -1;
    }
    let batch = &*handle;
    batch.teacher_actions(std::slice::from_raw_parts_mut(actions, batch.len()));
    0
}

#[allow(clippy::too_many_arguments)]
#[no_mangle]
pub unsafe extern "C" fn tf_level3_step(
    handle: *mut Level3Batch,
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
    initial_total_deficits: *mut u8,
    training_turns: *mut u16,
    score_gains: *mut i16,
    renewable_harvests: *mut u8,
    created_crops: *mut u8,
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
        || initial_total_deficits.is_null()
        || training_turns.is_null()
        || score_gains.is_null()
        || renewable_harvests.is_null()
        || created_crops.is_null()
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
    let out_deficits = std::slice::from_raw_parts_mut(initial_total_deficits, n);
    let out_training_turns = std::slice::from_raw_parts_mut(training_turns, n);
    let out_score_gains = std::slice::from_raw_parts_mut(score_gains, n);
    let out_harvests = std::slice::from_raw_parts_mut(renewable_harvests, n);
    let out_crops = std::slice::from_raw_parts_mut(created_crops, n);

    for index in 0..n {
        let terminal = batch.envs[index].step(input_actions[index].max(0) as usize);
        out_rewards[index] = terminal.reward;
        out_dones[index] = terminal.done as u8;
        out_successes[index] = terminal.success as u8;
        out_turns[index] = if terminal.done { terminal.turns } else { 0 };
        out_returns[index] = if terminal.done {
            terminal.episode_return
        } else {
            0.0
        };
        out_seeds[index] = if terminal.done { terminal.seed } else { 0 };
        out_heights[index] = if terminal.done { terminal.height } else { 0 };
        out_deficits[index] = if terminal.done {
            terminal.initial_total_deficit
        } else {
            0
        };
        out_training_turns[index] = if terminal.done {
            terminal.training_turn
        } else {
            0
        };
        out_score_gains[index] = if terminal.done {
            terminal.score_gain
        } else {
            0
        };
        out_harvests[index] = if terminal.done {
            terminal.renewable_harvests
        } else {
            0
        };
        out_crops[index] = if terminal.done {
            terminal.created_crop as u8
        } else {
            0
        };
        if terminal.done {
            batch.reset_slot(index);
        }
    }
    batch.observe(
        std::slice::from_raw_parts_mut(obs, n * OBS_SIZE),
        std::slice::from_raw_parts_mut(masks, n * ACTION_SIZE),
    );
    0
}

#[no_mangle]
pub extern "C" fn tf_level4_obs_size() -> usize {
    OBS_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level4_action_size() -> usize {
    ACTION_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level4_recipe_count() -> usize {
    crate::rl_level1::LEVEL2_TARGETS.len()
}

#[no_mangle]
pub extern "C" fn tf_level4_create(
    num_envs: usize,
    seed_base: u64,
    max_turns: u16,
) -> *mut Level3Batch {
    if num_envs == 0 || max_turns == 0 {
        return std::ptr::null_mut();
    }
    Box::into_raw(Box::new(Level3Batch::new_level4(
        num_envs, seed_base, max_turns,
    )))
}

#[no_mangle]
pub unsafe extern "C" fn tf_level4_destroy(handle: *mut Level3Batch) {
    if !handle.is_null() {
        drop(Box::from_raw(handle));
    }
}

#[no_mangle]
pub unsafe extern "C" fn tf_level4_observe(
    handle: *mut Level3Batch,
    obs: *mut u8,
    masks: *mut u8,
) -> i32 {
    if handle.is_null() || obs.is_null() || masks.is_null() {
        return -1;
    }
    let batch = &*handle;
    batch.observe(
        std::slice::from_raw_parts_mut(obs, batch.len() * OBS_SIZE),
        std::slice::from_raw_parts_mut(masks, batch.len() * ACTION_SIZE),
    );
    0
}

#[no_mangle]
pub unsafe extern "C" fn tf_level4_teacher_actions(
    handle: *mut Level3Batch,
    actions: *mut i32,
) -> i32 {
    if handle.is_null() || actions.is_null() {
        return -1;
    }
    let batch = &*handle;
    batch.teacher_actions(std::slice::from_raw_parts_mut(actions, batch.len()));
    0
}

#[allow(clippy::too_many_arguments)]
#[no_mangle]
pub unsafe extern "C" fn tf_level4_step(
    handle: *mut Level3Batch,
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
    initial_total_deficits: *mut u8,
    training_turns: *mut u16,
    score_gains: *mut i16,
    renewable_harvests: *mut u8,
    created_crops: *mut u8,
    recipe_ids: *mut u8,
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
        || initial_total_deficits.is_null()
        || training_turns.is_null()
        || score_gains.is_null()
        || renewable_harvests.is_null()
        || created_crops.is_null()
        || recipe_ids.is_null()
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
    let out_deficits = std::slice::from_raw_parts_mut(initial_total_deficits, n);
    let out_training_turns = std::slice::from_raw_parts_mut(training_turns, n);
    let out_score_gains = std::slice::from_raw_parts_mut(score_gains, n);
    let out_harvests = std::slice::from_raw_parts_mut(renewable_harvests, n);
    let out_crops = std::slice::from_raw_parts_mut(created_crops, n);
    let out_recipe_ids = std::slice::from_raw_parts_mut(recipe_ids, n);
    let out_targets = std::slice::from_raw_parts_mut(target_specs, n * 4);

    for index in 0..n {
        let terminal = batch.envs[index].step(input_actions[index].max(0) as usize);
        out_rewards[index] = terminal.reward;
        out_dones[index] = terminal.done as u8;
        out_successes[index] = terminal.success as u8;
        out_turns[index] = if terminal.done { terminal.turns } else { 0 };
        out_returns[index] = if terminal.done {
            terminal.episode_return
        } else {
            0.0
        };
        out_seeds[index] = if terminal.done { terminal.seed } else { 0 };
        out_heights[index] = if terminal.done { terminal.height } else { 0 };
        out_deficits[index] = if terminal.done {
            terminal.initial_total_deficit
        } else {
            0
        };
        out_training_turns[index] = if terminal.done {
            terminal.training_turn
        } else {
            0
        };
        out_score_gains[index] = if terminal.done {
            terminal.score_gain
        } else {
            0
        };
        out_harvests[index] = if terminal.done {
            terminal.renewable_harvests
        } else {
            0
        };
        out_crops[index] = if terminal.done {
            terminal.created_crop as u8
        } else {
            0
        };
        out_recipe_ids[index] = if terminal.done { terminal.recipe_id } else { 0 };
        let encoded = [
            terminal.target.0,
            terminal.target.1,
            terminal.target.2,
            terminal.target.3,
        ];
        for offset in 0..4 {
            out_targets[index * 4 + offset] = if terminal.done { encoded[offset] } else { 0 };
        }
        if terminal.done {
            batch.reset_slot(index);
        }
    }
    batch.observe(
        std::slice::from_raw_parts_mut(obs, n * OBS_SIZE),
        std::slice::from_raw_parts_mut(masks, n * ACTION_SIZE),
    );
    0
}

#[no_mangle]
pub extern "C" fn tf_level5_obs_size() -> usize {
    OBS_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level5_action_size() -> usize {
    ACTION_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level5_recipe_count() -> usize {
    crate::rl_level1::LEVEL2_TARGETS.len()
}

#[no_mangle]
pub extern "C" fn tf_level5_create(
    num_envs: usize,
    seed_base: u64,
    max_turns: u16,
) -> *mut Level3Batch {
    if num_envs == 0 || max_turns == 0 {
        return std::ptr::null_mut();
    }
    Box::into_raw(Box::new(Level3Batch::new_level5(
        num_envs, seed_base, max_turns,
    )))
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_destroy(handle: *mut Level3Batch) {
    if !handle.is_null() {
        drop(Box::from_raw(handle));
    }
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_observe(
    handle: *mut Level3Batch,
    obs: *mut u8,
    masks: *mut u8,
) -> i32 {
    if handle.is_null() || obs.is_null() || masks.is_null() {
        return -1;
    }
    let batch = &*handle;
    batch.observe(
        std::slice::from_raw_parts_mut(obs, batch.len() * OBS_SIZE),
        std::slice::from_raw_parts_mut(masks, batch.len() * ACTION_SIZE),
    );
    0
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_teacher_actions(
    handle: *mut Level3Batch,
    actions: *mut i32,
) -> i32 {
    if handle.is_null() || actions.is_null() {
        return -1;
    }
    let batch = &*handle;
    batch.teacher_actions(std::slice::from_raw_parts_mut(actions, batch.len()));
    0
}

#[allow(clippy::too_many_arguments)]
#[no_mangle]
pub unsafe extern "C" fn tf_level5_step(
    handle: *mut Level3Batch,
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
    initial_total_deficits: *mut u8,
    training_turns: *mut u16,
    score_gains: *mut i16,
    renewable_harvests: *mut u8,
    created_crops: *mut u8,
    recipe_ids: *mut u8,
    target_specs: *mut i8,
    opponent_scores: *mut i16,
    opponent_workers: *mut u8,
    opponent_created_crops: *mut u8,
    opponent_renewable_harvests: *mut u8,
    opponent_crop_destructions: *mut u8,
    opponent_training_turns: *mut u16,
    opponent_funding_deposits: *mut u8,
    opponent_second_worker_productive_actions: *mut u16,
    opponent_funded_training_events: *mut u8,
    opponent_third_worker_training_turns: *mut u16,
    opponent_third_worker_productive_actions: *mut u16,
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
        || initial_total_deficits.is_null()
        || training_turns.is_null()
        || score_gains.is_null()
        || renewable_harvests.is_null()
        || created_crops.is_null()
        || recipe_ids.is_null()
        || target_specs.is_null()
        || opponent_scores.is_null()
        || opponent_workers.is_null()
        || opponent_created_crops.is_null()
        || opponent_renewable_harvests.is_null()
        || opponent_crop_destructions.is_null()
        || opponent_training_turns.is_null()
        || opponent_funding_deposits.is_null()
        || opponent_second_worker_productive_actions.is_null()
        || opponent_funded_training_events.is_null()
        || opponent_third_worker_training_turns.is_null()
        || opponent_third_worker_productive_actions.is_null()
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
    let out_deficits = std::slice::from_raw_parts_mut(initial_total_deficits, n);
    let out_training_turns = std::slice::from_raw_parts_mut(training_turns, n);
    let out_score_gains = std::slice::from_raw_parts_mut(score_gains, n);
    let out_harvests = std::slice::from_raw_parts_mut(renewable_harvests, n);
    let out_crops = std::slice::from_raw_parts_mut(created_crops, n);
    let out_recipe_ids = std::slice::from_raw_parts_mut(recipe_ids, n);
    let out_targets = std::slice::from_raw_parts_mut(target_specs, n * 4);
    let out_opponent_scores = std::slice::from_raw_parts_mut(opponent_scores, n);
    let out_opponent_workers = std::slice::from_raw_parts_mut(opponent_workers, n);
    let out_opponent_crops = std::slice::from_raw_parts_mut(opponent_created_crops, n);
    let out_opponent_harvests = std::slice::from_raw_parts_mut(opponent_renewable_harvests, n);
    let out_opponent_destructions = std::slice::from_raw_parts_mut(opponent_crop_destructions, n);
    let out_opponent_training_turns = std::slice::from_raw_parts_mut(opponent_training_turns, n);
    let out_opponent_funding_deposits =
        std::slice::from_raw_parts_mut(opponent_funding_deposits, n);
    let out_opponent_second_worker_actions =
        std::slice::from_raw_parts_mut(opponent_second_worker_productive_actions, n);
    let out_opponent_funded_training_events =
        std::slice::from_raw_parts_mut(opponent_funded_training_events, n);
    let out_opponent_third_training_turns =
        std::slice::from_raw_parts_mut(opponent_third_worker_training_turns, n);
    let out_opponent_third_worker_actions =
        std::slice::from_raw_parts_mut(opponent_third_worker_productive_actions, n);

    for index in 0..n {
        let terminal = batch.envs[index].step(input_actions[index].max(0) as usize);
        out_rewards[index] = terminal.reward;
        out_dones[index] = terminal.done as u8;
        out_successes[index] = terminal.success as u8;
        out_turns[index] = if terminal.done { terminal.turns } else { 0 };
        out_returns[index] = if terminal.done {
            terminal.episode_return
        } else {
            0.0
        };
        out_seeds[index] = if terminal.done { terminal.seed } else { 0 };
        out_heights[index] = if terminal.done { terminal.height } else { 0 };
        out_deficits[index] = if terminal.done {
            terminal.initial_total_deficit
        } else {
            0
        };
        out_training_turns[index] = if terminal.done {
            terminal.training_turn
        } else {
            0
        };
        out_score_gains[index] = if terminal.done {
            terminal.score_gain
        } else {
            0
        };
        out_harvests[index] = if terminal.done {
            terminal.renewable_harvests
        } else {
            0
        };
        out_crops[index] = if terminal.done {
            terminal.created_crop as u8
        } else {
            0
        };
        out_recipe_ids[index] = if terminal.done { terminal.recipe_id } else { 0 };
        let encoded = [
            terminal.target.0,
            terminal.target.1,
            terminal.target.2,
            terminal.target.3,
        ];
        for offset in 0..4 {
            out_targets[index * 4 + offset] = if terminal.done { encoded[offset] } else { 0 };
        }
        out_opponent_scores[index] = if terminal.done {
            terminal.opponent_score
        } else {
            0
        };
        out_opponent_workers[index] = if terminal.done {
            terminal.opponent_workers
        } else {
            0
        };
        out_opponent_crops[index] = if terminal.done {
            terminal.opponent_created_crops
        } else {
            0
        };
        out_opponent_harvests[index] = if terminal.done {
            terminal.opponent_renewable_harvests
        } else {
            0
        };
        out_opponent_destructions[index] = if terminal.done {
            terminal.opponent_crop_destructions
        } else {
            0
        };
        out_opponent_training_turns[index] = if terminal.done {
            terminal.opponent_training_turn
        } else {
            0
        };
        out_opponent_funding_deposits[index] = if terminal.done {
            terminal.opponent_funding_deposits
        } else {
            0
        };
        out_opponent_second_worker_actions[index] = if terminal.done {
            terminal.opponent_second_worker_productive_actions
        } else {
            0
        };
        out_opponent_funded_training_events[index] = if terminal.done {
            terminal.opponent_funded_training_events
        } else {
            0
        };
        out_opponent_third_training_turns[index] = if terminal.done {
            terminal.opponent_third_worker_training_turn
        } else {
            0
        };
        out_opponent_third_worker_actions[index] = if terminal.done {
            terminal.opponent_third_worker_productive_actions
        } else {
            0
        };
        if terminal.done {
            batch.reset_slot(index);
        }
    }
    batch.observe(
        std::slice::from_raw_parts_mut(obs, n * OBS_SIZE),
        std::slice::from_raw_parts_mut(masks, n * ACTION_SIZE),
    );
    0
}

#[no_mangle]
pub extern "C" fn tf_level6_obs_size() -> usize {
    OBS_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level6_action_size() -> usize {
    ACTION_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level6_recipe_count() -> usize {
    crate::rl_level1::LEVEL2_TARGETS.len()
}

#[no_mangle]
pub extern "C" fn tf_level6_create(
    num_envs: usize,
    seed_base: u64,
    max_turns: u16,
) -> *mut Level3Batch {
    if num_envs == 0 || max_turns == 0 {
        return std::ptr::null_mut();
    }
    Box::into_raw(Box::new(Level3Batch::new_level6(
        num_envs, seed_base, max_turns,
    )))
}

#[no_mangle]
pub unsafe extern "C" fn tf_level6_destroy(handle: *mut Level3Batch) {
    tf_level5_destroy(handle);
}

#[no_mangle]
pub unsafe extern "C" fn tf_level6_observe(
    handle: *mut Level3Batch,
    obs: *mut u8,
    masks: *mut u8,
) -> i32 {
    tf_level5_observe(handle, obs, masks)
}

#[no_mangle]
pub unsafe extern "C" fn tf_level6_teacher_actions(
    handle: *mut Level3Batch,
    actions: *mut i32,
) -> i32 {
    tf_level5_teacher_actions(handle, actions)
}

#[no_mangle]
pub unsafe extern "C" fn tf_level6_current_metadata(
    handle: *mut Level3Batch,
    turns: *mut u16,
    phases: *mut u8,
    seeds: *mut u64,
) -> i32 {
    if handle.is_null() || turns.is_null() || phases.is_null() || seeds.is_null() {
        return -1;
    }
    let batch = &*handle;
    batch.current_metadata(
        std::slice::from_raw_parts_mut(turns, batch.len()),
        std::slice::from_raw_parts_mut(phases, batch.len()),
        std::slice::from_raw_parts_mut(seeds, batch.len()),
    );
    0
}

#[allow(clippy::too_many_arguments)]
#[no_mangle]
pub unsafe extern "C" fn tf_level6_step(
    handle: *mut Level3Batch,
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
    initial_total_deficits: *mut u8,
    training_turns: *mut u16,
    score_gains: *mut i16,
    renewable_harvests: *mut u8,
    created_crops: *mut u8,
    recipe_ids: *mut u8,
    target_specs: *mut i8,
    opponent_scores: *mut i16,
    opponent_workers: *mut u8,
    opponent_created_crops: *mut u8,
    opponent_renewable_harvests: *mut u8,
    opponent_crop_destructions: *mut u8,
    opponent_training_turns: *mut u16,
    opponent_funding_deposits: *mut u8,
    opponent_second_worker_productive_actions: *mut u16,
    opponent_funded_training_events: *mut u8,
    opponent_third_worker_training_turns: *mut u16,
    opponent_third_worker_productive_actions: *mut u16,
) -> i32 {
    tf_level5_step(
        handle,
        actions,
        obs,
        masks,
        rewards,
        dones,
        successes,
        episode_turns,
        episode_returns,
        episode_seeds,
        episode_heights,
        initial_total_deficits,
        training_turns,
        score_gains,
        renewable_harvests,
        created_crops,
        recipe_ids,
        target_specs,
        opponent_scores,
        opponent_workers,
        opponent_created_crops,
        opponent_renewable_harvests,
        opponent_crop_destructions,
        opponent_training_turns,
        opponent_funding_deposits,
        opponent_second_worker_productive_actions,
        opponent_funded_training_events,
        opponent_third_worker_training_turns,
        opponent_third_worker_productive_actions,
    )
}

#[no_mangle]
pub extern "C" fn tf_level5_forager_obs_size() -> usize {
    OBS_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level5_forager_action_size() -> usize {
    ACTION_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level5_forager_recipe_count() -> usize {
    crate::rl_level1::LEVEL2_TARGETS.len()
}

#[no_mangle]
pub extern "C" fn tf_level5_forager_create(
    num_envs: usize,
    seed_base: u64,
    max_turns: u16,
) -> *mut Level3Batch {
    if num_envs == 0 || max_turns == 0 {
        return std::ptr::null_mut();
    }
    Box::into_raw(Box::new(Level3Batch::new_level5_forager(
        num_envs, seed_base, max_turns,
    )))
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_forager_destroy(handle: *mut Level3Batch) {
    tf_level5_destroy(handle);
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_forager_observe(
    handle: *mut Level3Batch,
    obs: *mut u8,
    masks: *mut u8,
) -> i32 {
    tf_level5_observe(handle, obs, masks)
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_forager_teacher_actions(
    handle: *mut Level3Batch,
    actions: *mut i32,
) -> i32 {
    tf_level5_teacher_actions(handle, actions)
}

#[allow(clippy::too_many_arguments)]
#[no_mangle]
pub unsafe extern "C" fn tf_level5_forager_step(
    handle: *mut Level3Batch,
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
    initial_total_deficits: *mut u8,
    training_turns: *mut u16,
    score_gains: *mut i16,
    renewable_harvests: *mut u8,
    created_crops: *mut u8,
    recipe_ids: *mut u8,
    target_specs: *mut i8,
    opponent_scores: *mut i16,
    opponent_workers: *mut u8,
    opponent_created_crops: *mut u8,
    opponent_renewable_harvests: *mut u8,
    opponent_crop_destructions: *mut u8,
    opponent_training_turns: *mut u16,
    opponent_funding_deposits: *mut u8,
    opponent_second_worker_productive_actions: *mut u16,
    opponent_funded_training_events: *mut u8,
    opponent_third_worker_training_turns: *mut u16,
    opponent_third_worker_productive_actions: *mut u16,
) -> i32 {
    tf_level5_step(
        handle,
        actions,
        obs,
        masks,
        rewards,
        dones,
        successes,
        episode_turns,
        episode_returns,
        episode_seeds,
        episode_heights,
        initial_total_deficits,
        training_turns,
        score_gains,
        renewable_harvests,
        created_crops,
        recipe_ids,
        target_specs,
        opponent_scores,
        opponent_workers,
        opponent_created_crops,
        opponent_renewable_harvests,
        opponent_crop_destructions,
        opponent_training_turns,
        opponent_funding_deposits,
        opponent_second_worker_productive_actions,
        opponent_funded_training_events,
        opponent_third_worker_training_turns,
        opponent_third_worker_productive_actions,
    )
}

#[no_mangle]
pub extern "C" fn tf_level5_recovery_obs_size() -> usize {
    OBS_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level5_recovery_action_size() -> usize {
    ACTION_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level5_recovery_recipe_count() -> usize {
    crate::rl_level1::LEVEL2_TARGETS.len()
}

#[no_mangle]
pub extern "C" fn tf_level5_recovery_create(
    num_envs: usize,
    seed_base: u64,
    max_turns: u16,
) -> *mut Level3Batch {
    if num_envs == 0 || max_turns == 0 {
        return std::ptr::null_mut();
    }
    Box::into_raw(Box::new(Level3Batch::new_level5_recovery(
        num_envs, seed_base, max_turns,
    )))
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_recovery_destroy(handle: *mut Level3Batch) {
    tf_level5_destroy(handle);
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_recovery_observe(
    handle: *mut Level3Batch,
    obs: *mut u8,
    masks: *mut u8,
) -> i32 {
    tf_level5_observe(handle, obs, masks)
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_recovery_teacher_actions(
    handle: *mut Level3Batch,
    actions: *mut i32,
) -> i32 {
    tf_level5_teacher_actions(handle, actions)
}

#[allow(clippy::too_many_arguments)]
#[no_mangle]
pub unsafe extern "C" fn tf_level5_recovery_step(
    handle: *mut Level3Batch,
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
    initial_total_deficits: *mut u8,
    training_turns: *mut u16,
    score_gains: *mut i16,
    renewable_harvests: *mut u8,
    created_crops: *mut u8,
    recipe_ids: *mut u8,
    target_specs: *mut i8,
    opponent_scores: *mut i16,
    opponent_workers: *mut u8,
    opponent_created_crops: *mut u8,
    opponent_renewable_harvests: *mut u8,
    opponent_crop_destructions: *mut u8,
    opponent_training_turns: *mut u16,
    opponent_funding_deposits: *mut u8,
    opponent_second_worker_productive_actions: *mut u16,
    opponent_funded_training_events: *mut u8,
    opponent_third_worker_training_turns: *mut u16,
    opponent_third_worker_productive_actions: *mut u16,
) -> i32 {
    tf_level5_step(
        handle,
        actions,
        obs,
        masks,
        rewards,
        dones,
        successes,
        episode_turns,
        episode_returns,
        episode_seeds,
        episode_heights,
        initial_total_deficits,
        training_turns,
        score_gains,
        renewable_harvests,
        created_crops,
        recipe_ids,
        target_specs,
        opponent_scores,
        opponent_workers,
        opponent_created_crops,
        opponent_renewable_harvests,
        opponent_crop_destructions,
        opponent_training_turns,
        opponent_funding_deposits,
        opponent_second_worker_productive_actions,
        opponent_funded_training_events,
        opponent_third_worker_training_turns,
        opponent_third_worker_productive_actions,
    )
}

#[no_mangle]
pub extern "C" fn tf_level5_planter_obs_size() -> usize {
    OBS_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level5_planter_action_size() -> usize {
    ACTION_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level5_planter_recipe_count() -> usize {
    crate::rl_level1::LEVEL2_TARGETS.len()
}

#[no_mangle]
pub extern "C" fn tf_level5_planter_create(
    num_envs: usize,
    seed_base: u64,
    max_turns: u16,
) -> *mut Level3Batch {
    if num_envs == 0 || max_turns == 0 {
        return std::ptr::null_mut();
    }
    Box::into_raw(Box::new(Level3Batch::new_level5_planter(
        num_envs, seed_base, max_turns,
    )))
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_planter_destroy(handle: *mut Level3Batch) {
    tf_level5_destroy(handle);
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_planter_observe(
    handle: *mut Level3Batch,
    obs: *mut u8,
    masks: *mut u8,
) -> i32 {
    tf_level5_observe(handle, obs, masks)
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_planter_teacher_actions(
    handle: *mut Level3Batch,
    actions: *mut i32,
) -> i32 {
    tf_level5_teacher_actions(handle, actions)
}

#[allow(clippy::too_many_arguments)]
#[no_mangle]
pub unsafe extern "C" fn tf_level5_planter_step(
    handle: *mut Level3Batch,
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
    initial_total_deficits: *mut u8,
    training_turns: *mut u16,
    score_gains: *mut i16,
    renewable_harvests: *mut u8,
    created_crops: *mut u8,
    recipe_ids: *mut u8,
    target_specs: *mut i8,
    opponent_scores: *mut i16,
    opponent_workers: *mut u8,
    opponent_created_crops: *mut u8,
    opponent_renewable_harvests: *mut u8,
    opponent_crop_destructions: *mut u8,
    opponent_training_turns: *mut u16,
    opponent_funding_deposits: *mut u8,
    opponent_second_worker_productive_actions: *mut u16,
    opponent_funded_training_events: *mut u8,
    opponent_third_worker_training_turns: *mut u16,
    opponent_third_worker_productive_actions: *mut u16,
) -> i32 {
    tf_level5_step(
        handle,
        actions,
        obs,
        masks,
        rewards,
        dones,
        successes,
        episode_turns,
        episode_returns,
        episode_seeds,
        episode_heights,
        initial_total_deficits,
        training_turns,
        score_gains,
        renewable_harvests,
        created_crops,
        recipe_ids,
        target_specs,
        opponent_scores,
        opponent_workers,
        opponent_created_crops,
        opponent_renewable_harvests,
        opponent_crop_destructions,
        opponent_training_turns,
        opponent_funding_deposits,
        opponent_second_worker_productive_actions,
        opponent_funded_training_events,
        opponent_third_worker_training_turns,
        opponent_third_worker_productive_actions,
    )
}

#[no_mangle]
pub extern "C" fn tf_level5_reaper_obs_size() -> usize {
    OBS_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level5_reaper_action_size() -> usize {
    ACTION_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level5_reaper_recipe_count() -> usize {
    crate::rl_level1::LEVEL2_TARGETS.len()
}

#[no_mangle]
pub extern "C" fn tf_level5_reaper_create(
    num_envs: usize,
    seed_base: u64,
    max_turns: u16,
) -> *mut Level3Batch {
    if num_envs == 0 || max_turns == 0 {
        return std::ptr::null_mut();
    }
    Box::into_raw(Box::new(Level3Batch::new_level5_reaper(
        num_envs, seed_base, max_turns,
    )))
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_reaper_destroy(handle: *mut Level3Batch) {
    tf_level5_destroy(handle);
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_reaper_observe(
    handle: *mut Level3Batch,
    obs: *mut u8,
    masks: *mut u8,
) -> i32 {
    tf_level5_observe(handle, obs, masks)
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_reaper_teacher_actions(
    handle: *mut Level3Batch,
    actions: *mut i32,
) -> i32 {
    tf_level5_teacher_actions(handle, actions)
}

#[allow(clippy::too_many_arguments)]
#[no_mangle]
pub unsafe extern "C" fn tf_level5_reaper_step(
    handle: *mut Level3Batch,
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
    initial_total_deficits: *mut u8,
    training_turns: *mut u16,
    score_gains: *mut i16,
    renewable_harvests: *mut u8,
    created_crops: *mut u8,
    recipe_ids: *mut u8,
    target_specs: *mut i8,
    opponent_scores: *mut i16,
    opponent_workers: *mut u8,
    opponent_created_crops: *mut u8,
    opponent_renewable_harvests: *mut u8,
    opponent_crop_destructions: *mut u8,
    opponent_training_turns: *mut u16,
    opponent_funding_deposits: *mut u8,
    opponent_second_worker_productive_actions: *mut u16,
    opponent_funded_training_events: *mut u8,
    opponent_third_worker_training_turns: *mut u16,
    opponent_third_worker_productive_actions: *mut u16,
) -> i32 {
    tf_level5_step(
        handle,
        actions,
        obs,
        masks,
        rewards,
        dones,
        successes,
        episode_turns,
        episode_returns,
        episode_seeds,
        episode_heights,
        initial_total_deficits,
        training_turns,
        score_gains,
        renewable_harvests,
        created_crops,
        recipe_ids,
        target_specs,
        opponent_scores,
        opponent_workers,
        opponent_created_crops,
        opponent_renewable_harvests,
        opponent_crop_destructions,
        opponent_training_turns,
        opponent_funding_deposits,
        opponent_second_worker_productive_actions,
        opponent_funded_training_events,
        opponent_third_worker_training_turns,
        opponent_third_worker_productive_actions,
    )
}

#[no_mangle]
pub extern "C" fn tf_level5_funded_pair_obs_size() -> usize {
    OBS_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level5_funded_pair_action_size() -> usize {
    ACTION_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level5_funded_pair_recipe_count() -> usize {
    crate::rl_level1::LEVEL2_TARGETS.len()
}

#[no_mangle]
pub extern "C" fn tf_level5_funded_pair_create(
    num_envs: usize,
    seed_base: u64,
    max_turns: u16,
) -> *mut Level3Batch {
    if num_envs == 0 || max_turns == 0 {
        return std::ptr::null_mut();
    }
    Box::into_raw(Box::new(Level3Batch::new_level5_funded_pair(
        num_envs, seed_base, max_turns,
    )))
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_funded_pair_destroy(handle: *mut Level3Batch) {
    tf_level5_destroy(handle);
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_funded_pair_observe(
    handle: *mut Level3Batch,
    obs: *mut u8,
    masks: *mut u8,
) -> i32 {
    tf_level5_observe(handle, obs, masks)
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_funded_pair_teacher_actions(
    handle: *mut Level3Batch,
    actions: *mut i32,
) -> i32 {
    tf_level5_teacher_actions(handle, actions)
}

#[allow(clippy::too_many_arguments)]
#[no_mangle]
pub unsafe extern "C" fn tf_level5_funded_pair_step(
    handle: *mut Level3Batch,
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
    initial_total_deficits: *mut u8,
    training_turns: *mut u16,
    score_gains: *mut i16,
    renewable_harvests: *mut u8,
    created_crops: *mut u8,
    recipe_ids: *mut u8,
    target_specs: *mut i8,
    opponent_scores: *mut i16,
    opponent_workers: *mut u8,
    opponent_created_crops: *mut u8,
    opponent_renewable_harvests: *mut u8,
    opponent_crop_destructions: *mut u8,
    opponent_training_turns: *mut u16,
    opponent_funding_deposits: *mut u8,
    opponent_second_worker_productive_actions: *mut u16,
    opponent_funded_training_events: *mut u8,
    opponent_third_worker_training_turns: *mut u16,
    opponent_third_worker_productive_actions: *mut u16,
) -> i32 {
    tf_level5_step(
        handle,
        actions,
        obs,
        masks,
        rewards,
        dones,
        successes,
        episode_turns,
        episode_returns,
        episode_seeds,
        episode_heights,
        initial_total_deficits,
        training_turns,
        score_gains,
        renewable_harvests,
        created_crops,
        recipe_ids,
        target_specs,
        opponent_scores,
        opponent_workers,
        opponent_created_crops,
        opponent_renewable_harvests,
        opponent_crop_destructions,
        opponent_training_turns,
        opponent_funding_deposits,
        opponent_second_worker_productive_actions,
        opponent_funded_training_events,
        opponent_third_worker_training_turns,
        opponent_third_worker_productive_actions,
    )
}

#[no_mangle]
pub extern "C" fn tf_level5_funded_trio_obs_size() -> usize {
    OBS_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level5_funded_trio_action_size() -> usize {
    ACTION_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level5_funded_trio_recipe_count() -> usize {
    crate::rl_level1::LEVEL2_TARGETS.len()
}

#[no_mangle]
pub extern "C" fn tf_level5_funded_trio_create(
    num_envs: usize,
    seed_base: u64,
    max_turns: u16,
) -> *mut Level3Batch {
    if num_envs == 0 || max_turns == 0 {
        return std::ptr::null_mut();
    }
    Box::into_raw(Box::new(Level3Batch::new_level5_funded_trio(
        num_envs, seed_base, max_turns,
    )))
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_funded_trio_destroy(handle: *mut Level3Batch) {
    tf_level5_destroy(handle);
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_funded_trio_observe(
    handle: *mut Level3Batch,
    obs: *mut u8,
    masks: *mut u8,
) -> i32 {
    tf_level5_observe(handle, obs, masks)
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_funded_trio_teacher_actions(
    handle: *mut Level3Batch,
    actions: *mut i32,
) -> i32 {
    tf_level5_teacher_actions(handle, actions)
}

#[allow(clippy::too_many_arguments)]
#[no_mangle]
pub unsafe extern "C" fn tf_level5_funded_trio_step(
    handle: *mut Level3Batch,
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
    initial_total_deficits: *mut u8,
    training_turns: *mut u16,
    score_gains: *mut i16,
    renewable_harvests: *mut u8,
    created_crops: *mut u8,
    recipe_ids: *mut u8,
    target_specs: *mut i8,
    opponent_scores: *mut i16,
    opponent_workers: *mut u8,
    opponent_created_crops: *mut u8,
    opponent_renewable_harvests: *mut u8,
    opponent_crop_destructions: *mut u8,
    opponent_training_turns: *mut u16,
    opponent_funding_deposits: *mut u8,
    opponent_second_worker_productive_actions: *mut u16,
    opponent_funded_training_events: *mut u8,
    opponent_third_worker_training_turns: *mut u16,
    opponent_third_worker_productive_actions: *mut u16,
) -> i32 {
    tf_level5_step(
        handle,
        actions,
        obs,
        masks,
        rewards,
        dones,
        successes,
        episode_turns,
        episode_returns,
        episode_seeds,
        episode_heights,
        initial_total_deficits,
        training_turns,
        score_gains,
        renewable_harvests,
        created_crops,
        recipe_ids,
        target_specs,
        opponent_scores,
        opponent_workers,
        opponent_created_crops,
        opponent_renewable_harvests,
        opponent_crop_destructions,
        opponent_training_turns,
        opponent_funding_deposits,
        opponent_second_worker_productive_actions,
        opponent_funded_training_events,
        opponent_third_worker_training_turns,
        opponent_third_worker_productive_actions,
    )
}

#[no_mangle]
pub extern "C" fn tf_level5_funded_trio_sustained_obs_size() -> usize {
    OBS_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level5_funded_trio_sustained_action_size() -> usize {
    ACTION_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level5_funded_trio_sustained_recipe_count() -> usize {
    crate::rl_level1::LEVEL2_TARGETS.len()
}

#[no_mangle]
pub extern "C" fn tf_level5_funded_trio_sustained_create(
    num_envs: usize,
    seed_base: u64,
    max_turns: u16,
) -> *mut Level3Batch {
    if num_envs == 0 || max_turns < 120 {
        return std::ptr::null_mut();
    }
    Box::into_raw(Box::new(Level3Batch::new_level5_funded_trio_sustained(
        num_envs, seed_base, max_turns,
    )))
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_funded_trio_sustained_destroy(handle: *mut Level3Batch) {
    tf_level5_destroy(handle);
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_funded_trio_sustained_observe(
    handle: *mut Level3Batch,
    obs: *mut u8,
    masks: *mut u8,
) -> i32 {
    tf_level5_observe(handle, obs, masks)
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_funded_trio_sustained_teacher_actions(
    handle: *mut Level3Batch,
    actions: *mut i32,
) -> i32 {
    tf_level5_teacher_actions(handle, actions)
}

#[allow(clippy::too_many_arguments)]
#[no_mangle]
pub unsafe extern "C" fn tf_level5_funded_trio_sustained_step(
    handle: *mut Level3Batch,
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
    initial_total_deficits: *mut u8,
    training_turns: *mut u16,
    score_gains: *mut i16,
    renewable_harvests: *mut u8,
    created_crops: *mut u8,
    recipe_ids: *mut u8,
    target_specs: *mut i8,
    opponent_scores: *mut i16,
    opponent_workers: *mut u8,
    opponent_created_crops: *mut u8,
    opponent_renewable_harvests: *mut u8,
    opponent_crop_destructions: *mut u8,
    opponent_training_turns: *mut u16,
    opponent_funding_deposits: *mut u8,
    opponent_second_worker_productive_actions: *mut u16,
    opponent_funded_training_events: *mut u8,
    opponent_third_worker_training_turns: *mut u16,
    opponent_third_worker_productive_actions: *mut u16,
) -> i32 {
    tf_level5_step(
        handle,
        actions,
        obs,
        masks,
        rewards,
        dones,
        successes,
        episode_turns,
        episode_returns,
        episode_seeds,
        episode_heights,
        initial_total_deficits,
        training_turns,
        score_gains,
        renewable_harvests,
        created_crops,
        recipe_ids,
        target_specs,
        opponent_scores,
        opponent_workers,
        opponent_created_crops,
        opponent_renewable_harvests,
        opponent_crop_destructions,
        opponent_training_turns,
        opponent_funding_deposits,
        opponent_second_worker_productive_actions,
        opponent_funded_training_events,
        opponent_third_worker_training_turns,
        opponent_third_worker_productive_actions,
    )
}

#[no_mangle]
pub extern "C" fn tf_level5_funded_trio_sustained_180_obs_size() -> usize {
    OBS_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level5_funded_trio_sustained_180_action_size() -> usize {
    ACTION_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level5_funded_trio_sustained_180_recipe_count() -> usize {
    crate::rl_level1::LEVEL2_TARGETS.len()
}

#[no_mangle]
pub extern "C" fn tf_level5_funded_trio_sustained_180_create(
    num_envs: usize,
    seed_base: u64,
    max_turns: u16,
) -> *mut Level3Batch {
    if num_envs == 0 || max_turns < 180 {
        return std::ptr::null_mut();
    }
    Box::into_raw(Box::new(Level3Batch::new_level5_funded_trio_sustained_180(
        num_envs, seed_base, max_turns,
    )))
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_funded_trio_sustained_180_destroy(handle: *mut Level3Batch) {
    tf_level5_destroy(handle);
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_funded_trio_sustained_180_observe(
    handle: *mut Level3Batch,
    obs: *mut u8,
    masks: *mut u8,
) -> i32 {
    tf_level5_observe(handle, obs, masks)
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_funded_trio_sustained_180_teacher_actions(
    handle: *mut Level3Batch,
    actions: *mut i32,
) -> i32 {
    tf_level5_teacher_actions(handle, actions)
}

#[allow(clippy::too_many_arguments)]
#[no_mangle]
pub unsafe extern "C" fn tf_level5_funded_trio_sustained_180_step(
    handle: *mut Level3Batch,
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
    initial_total_deficits: *mut u8,
    training_turns: *mut u16,
    score_gains: *mut i16,
    renewable_harvests: *mut u8,
    created_crops: *mut u8,
    recipe_ids: *mut u8,
    target_specs: *mut i8,
    opponent_scores: *mut i16,
    opponent_workers: *mut u8,
    opponent_created_crops: *mut u8,
    opponent_renewable_harvests: *mut u8,
    opponent_crop_destructions: *mut u8,
    opponent_training_turns: *mut u16,
    opponent_funding_deposits: *mut u8,
    opponent_second_worker_productive_actions: *mut u16,
    opponent_funded_training_events: *mut u8,
    opponent_third_worker_training_turns: *mut u16,
    opponent_third_worker_productive_actions: *mut u16,
) -> i32 {
    tf_level5_step(
        handle,
        actions,
        obs,
        masks,
        rewards,
        dones,
        successes,
        episode_turns,
        episode_returns,
        episode_seeds,
        episode_heights,
        initial_total_deficits,
        training_turns,
        score_gains,
        renewable_harvests,
        created_crops,
        recipe_ids,
        target_specs,
        opponent_scores,
        opponent_workers,
        opponent_created_crops,
        opponent_renewable_harvests,
        opponent_crop_destructions,
        opponent_training_turns,
        opponent_funding_deposits,
        opponent_second_worker_productive_actions,
        opponent_funded_training_events,
        opponent_third_worker_training_turns,
        opponent_third_worker_productive_actions,
    )
}

#[no_mangle]
pub extern "C" fn tf_level5_crop_first_funded_trio_sustained_180_obs_size() -> usize {
    OBS_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level5_crop_first_funded_trio_sustained_180_action_size() -> usize {
    ACTION_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level5_crop_first_funded_trio_sustained_180_recipe_count() -> usize {
    crate::rl_level1::LEVEL2_TARGETS.len()
}

#[no_mangle]
pub extern "C" fn tf_level5_crop_first_funded_trio_sustained_180_create(
    num_envs: usize,
    seed_base: u64,
    max_turns: u16,
) -> *mut Level3Batch {
    if num_envs == 0 || max_turns < 180 {
        return std::ptr::null_mut();
    }
    Box::into_raw(Box::new(
        Level3Batch::new_level5_crop_first_funded_trio_sustained_180(
            num_envs, seed_base, max_turns,
        ),
    ))
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_crop_first_funded_trio_sustained_180_destroy(
    handle: *mut Level3Batch,
) {
    tf_level5_destroy(handle);
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_crop_first_funded_trio_sustained_180_observe(
    handle: *mut Level3Batch,
    obs: *mut u8,
    masks: *mut u8,
) -> i32 {
    tf_level5_observe(handle, obs, masks)
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_crop_first_funded_trio_sustained_180_teacher_actions(
    handle: *mut Level3Batch,
    actions: *mut i32,
) -> i32 {
    tf_level5_teacher_actions(handle, actions)
}

#[allow(clippy::too_many_arguments)]
#[no_mangle]
pub unsafe extern "C" fn tf_level5_crop_first_funded_trio_sustained_180_step(
    handle: *mut Level3Batch,
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
    initial_total_deficits: *mut u8,
    training_turns: *mut u16,
    score_gains: *mut i16,
    renewable_harvests: *mut u8,
    created_crops: *mut u8,
    recipe_ids: *mut u8,
    target_specs: *mut i8,
    opponent_scores: *mut i16,
    opponent_workers: *mut u8,
    opponent_created_crops: *mut u8,
    opponent_renewable_harvests: *mut u8,
    opponent_crop_destructions: *mut u8,
    opponent_training_turns: *mut u16,
    opponent_funding_deposits: *mut u8,
    opponent_second_worker_productive_actions: *mut u16,
    opponent_funded_training_events: *mut u8,
    opponent_third_worker_training_turns: *mut u16,
    opponent_third_worker_productive_actions: *mut u16,
) -> i32 {
    tf_level5_step(
        handle,
        actions,
        obs,
        masks,
        rewards,
        dones,
        successes,
        episode_turns,
        episode_returns,
        episode_seeds,
        episode_heights,
        initial_total_deficits,
        training_turns,
        score_gains,
        renewable_harvests,
        created_crops,
        recipe_ids,
        target_specs,
        opponent_scores,
        opponent_workers,
        opponent_created_crops,
        opponent_renewable_harvests,
        opponent_crop_destructions,
        opponent_training_turns,
        opponent_funding_deposits,
        opponent_second_worker_productive_actions,
        opponent_funded_training_events,
        opponent_third_worker_training_turns,
        opponent_third_worker_productive_actions,
    )
}

#[no_mangle]
pub extern "C" fn tf_level5_crop_first_funded_trio_repeated_pressure_180_obs_size() -> usize {
    OBS_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level5_crop_first_funded_trio_repeated_pressure_180_action_size() -> usize {
    ACTION_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level5_crop_first_funded_trio_repeated_pressure_180_recipe_count() -> usize {
    crate::rl_level1::LEVEL2_TARGETS.len()
}

#[no_mangle]
pub extern "C" fn tf_level5_crop_first_funded_trio_repeated_pressure_180_create(
    num_envs: usize,
    seed_base: u64,
    max_turns: u16,
) -> *mut Level3Batch {
    if num_envs == 0 || max_turns < 180 {
        return std::ptr::null_mut();
    }
    Box::into_raw(Box::new(
        Level3Batch::new_level5_crop_first_funded_trio_repeated_pressure_180(
            num_envs, seed_base, max_turns,
        ),
    ))
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_crop_first_funded_trio_repeated_pressure_180_destroy(
    handle: *mut Level3Batch,
) {
    tf_level5_destroy(handle);
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_crop_first_funded_trio_repeated_pressure_180_observe(
    handle: *mut Level3Batch,
    obs: *mut u8,
    masks: *mut u8,
) -> i32 {
    tf_level5_observe(handle, obs, masks)
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_crop_first_funded_trio_repeated_pressure_180_teacher_actions(
    handle: *mut Level3Batch,
    actions: *mut i32,
) -> i32 {
    tf_level5_teacher_actions(handle, actions)
}

#[allow(clippy::too_many_arguments)]
#[no_mangle]
pub unsafe extern "C" fn tf_level5_crop_first_funded_trio_repeated_pressure_180_step(
    handle: *mut Level3Batch,
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
    initial_total_deficits: *mut u8,
    training_turns: *mut u16,
    score_gains: *mut i16,
    renewable_harvests: *mut u8,
    created_crops: *mut u8,
    recipe_ids: *mut u8,
    target_specs: *mut i8,
    opponent_scores: *mut i16,
    opponent_workers: *mut u8,
    opponent_created_crops: *mut u8,
    opponent_renewable_harvests: *mut u8,
    opponent_crop_destructions: *mut u8,
    opponent_training_turns: *mut u16,
    opponent_funding_deposits: *mut u8,
    opponent_second_worker_productive_actions: *mut u16,
    opponent_funded_training_events: *mut u8,
    opponent_third_worker_training_turns: *mut u16,
    opponent_third_worker_productive_actions: *mut u16,
) -> i32 {
    tf_level5_step(
        handle,
        actions,
        obs,
        masks,
        rewards,
        dones,
        successes,
        episode_turns,
        episode_returns,
        episode_seeds,
        episode_heights,
        initial_total_deficits,
        training_turns,
        score_gains,
        renewable_harvests,
        created_crops,
        recipe_ids,
        target_specs,
        opponent_scores,
        opponent_workers,
        opponent_created_crops,
        opponent_renewable_harvests,
        opponent_crop_destructions,
        opponent_training_turns,
        opponent_funding_deposits,
        opponent_second_worker_productive_actions,
        opponent_funded_training_events,
        opponent_third_worker_training_turns,
        opponent_third_worker_productive_actions,
    )
}

#[no_mangle]
pub extern "C" fn tf_level5_crop_first_funded_trio_repeated_pressure_reacquire_180_obs_size(
) -> usize {
    OBS_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level5_crop_first_funded_trio_repeated_pressure_reacquire_180_action_size(
) -> usize {
    ACTION_SIZE
}

#[no_mangle]
pub extern "C" fn tf_level5_crop_first_funded_trio_repeated_pressure_reacquire_180_recipe_count(
) -> usize {
    crate::rl_level1::LEVEL2_TARGETS.len()
}

#[no_mangle]
pub extern "C" fn tf_level5_crop_first_funded_trio_repeated_pressure_reacquire_180_create(
    num_envs: usize,
    seed_base: u64,
    max_turns: u16,
) -> *mut Level3Batch {
    if num_envs == 0 || max_turns < 180 {
        return std::ptr::null_mut();
    }
    Box::into_raw(Box::new(
        Level3Batch::new_level5_crop_first_funded_trio_repeated_pressure_reacquire_180(
            num_envs, seed_base, max_turns,
        ),
    ))
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_crop_first_funded_trio_repeated_pressure_reacquire_180_destroy(
    handle: *mut Level3Batch,
) {
    tf_level5_destroy(handle);
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_crop_first_funded_trio_repeated_pressure_reacquire_180_observe(
    handle: *mut Level3Batch,
    obs: *mut u8,
    masks: *mut u8,
) -> i32 {
    tf_level5_observe(handle, obs, masks)
}

#[no_mangle]
pub unsafe extern "C" fn tf_level5_crop_first_funded_trio_repeated_pressure_reacquire_180_teacher_actions(
    handle: *mut Level3Batch,
    actions: *mut i32,
) -> i32 {
    tf_level5_teacher_actions(handle, actions)
}

#[allow(clippy::too_many_arguments)]
#[no_mangle]
pub unsafe extern "C" fn tf_level5_crop_first_funded_trio_repeated_pressure_reacquire_180_step(
    handle: *mut Level3Batch,
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
    initial_total_deficits: *mut u8,
    training_turns: *mut u16,
    score_gains: *mut i16,
    renewable_harvests: *mut u8,
    created_crops: *mut u8,
    recipe_ids: *mut u8,
    target_specs: *mut i8,
    opponent_scores: *mut i16,
    opponent_workers: *mut u8,
    opponent_created_crops: *mut u8,
    opponent_renewable_harvests: *mut u8,
    opponent_crop_destructions: *mut u8,
    opponent_training_turns: *mut u16,
    opponent_funding_deposits: *mut u8,
    opponent_second_worker_productive_actions: *mut u16,
    opponent_funded_training_events: *mut u8,
    opponent_third_worker_training_turns: *mut u16,
    opponent_third_worker_productive_actions: *mut u16,
) -> i32 {
    tf_level5_step(
        handle,
        actions,
        obs,
        masks,
        rewards,
        dones,
        successes,
        episode_turns,
        episode_returns,
        episode_seeds,
        episode_heights,
        initial_total_deficits,
        training_turns,
        score_gains,
        renewable_harvests,
        created_crops,
        recipe_ids,
        target_specs,
        opponent_scores,
        opponent_workers,
        opponent_created_crops,
        opponent_renewable_harvests,
        opponent_crop_destructions,
        opponent_training_turns,
        opponent_funding_deposits,
        opponent_second_worker_productive_actions,
        opponent_funded_training_events,
        opponent_third_worker_training_turns,
        opponent_third_worker_productive_actions,
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn teacher_is_legal_through_sequential_two_troll_control() {
        for seed in 0..50 {
            let mut env = Level3Env::new(seed, 240);
            for _ in 0..480 {
                let mut obs = vec![0; OBS_SIZE];
                let mut mask = vec![0; ACTION_SIZE];
                env.observe(&mut obs, &mut mask);
                let selected = env.teacher_action();
                assert_eq!(
                    mask[selected], 1,
                    "seed {seed}, turn {}, phase {}",
                    env.turns, env.decision_phase
                );
                let terminal = env.step(selected);
                if terminal.done {
                    assert!(
                        terminal.success,
                        "teacher timed out on seed {seed}: {terminal:?}"
                    );
                    break;
                }
            }
        }
    }

    #[test]
    fn deterministic_batches_match() {
        let mut a = Level3Env::new(77, 240);
        let mut b = Level3Env::new(77, 240);
        for _ in 0..200 {
            let aa = a.teacher_action();
            let bb = b.teacher_action();
            assert_eq!(aa, bb);
            assert_eq!(a.step(aa), b.step(bb));
        }
    }

    #[test]
    fn level5_active_opponent_is_deterministic_and_material() {
        let mut material_episodes = 0;
        let mut _illegal_teacher_actions = 0;
        for seed in 0..50 {
            let mut a = Level3Env::new_level5(seed, 240);
            let mut b = Level3Env::new_level5(seed, 240);
            let mut terminal = None;
            for _ in 0..480 {
                let mut obs_a = vec![0; OBS_SIZE];
                let mut mask_a = vec![0; ACTION_SIZE];
                let mut obs_b = vec![0; OBS_SIZE];
                let mut mask_b = vec![0; ACTION_SIZE];
                a.observe(&mut obs_a, &mut mask_a);
                b.observe(&mut obs_b, &mut mask_b);
                assert_eq!(obs_a, obs_b, "observation mismatch on seed {seed}");
                assert_eq!(mask_a, mask_b, "mask mismatch on seed {seed}");
                let action_a = a.teacher_action();
                let action_b = b.teacher_action();
                assert_eq!(action_a, action_b);
                _illegal_teacher_actions += usize::from(mask_a[action_a] == 0);
                let result_a = a.step(action_a);
                let result_b = b.step(action_b);
                assert_eq!(result_a, result_b, "terminal mismatch on seed {seed}");
                if result_a.done {
                    terminal = Some(result_a);
                    break;
                }
            }
            let terminal = terminal.unwrap_or_else(|| panic!("seed {seed} did not terminate"));
            if terminal.opponent_score > 0 || terminal.opponent_workers > 1 {
                material_episodes += 1;
            }
        }
        assert!(
            material_episodes > 0,
            "active opponent never changed material state"
        );
        // Occupation of the teacher's fixed planned crop is an expected readiness diagnostic,
        // not a determinism failure.  D0 decides feasibility from aggregate completion floors.
    }

    #[test]
    fn level5_recovery_replans_only_the_dynamic_mode() {
        fn occupy_planned_crop(env: &mut Level3Env) -> (i8, i8) {
            let occupied = env.planned_crop;
            let plant = env.state.n_plants as usize;
            env.state.p_type[plant] = 0;
            env.state.p_x[plant] = occupied.0;
            env.state.p_y[plant] = occupied.1;
            env.state.p_size[plant] = 1;
            env.state.p_health[plant] = 6;
            env.state.p_fruits[plant] = 0;
            env.state.p_cd[plant] = 1;
            env.state.p_wet[plant] = false;
            env.state.n_plants += 1;
            occupied
        }

        let mut fixed = Level3Env::new_level5(1_000, 240);
        let fixed_occupied = occupy_planned_crop(&mut fixed);
        fixed.refresh_planned_crop();
        assert_eq!(fixed.planned_crop, fixed_occupied);

        let mut recovery = Level3Env::new_level5_recovery(1_000, 240);
        let recovery_occupied = occupy_planned_crop(&mut recovery);
        recovery.refresh_planned_crop();
        assert_ne!(recovery.planned_crop, recovery_occupied);
        assert!(recovery
            .state
            .plant_at(recovery.planned_crop.0, recovery.planned_crop.1)
            .is_none());
    }

    #[test]
    fn level5_recovery_batches_are_deterministic_and_teacher_actions_are_legal() {
        for seed in 1_000..1_020 {
            let mut left = Level3Env::new_level5_recovery(seed, 240);
            let mut right = Level3Env::new_level5_recovery(seed, 240);
            loop {
                let mut left_obs = vec![0; OBS_SIZE];
                let mut left_mask = vec![0; ACTION_SIZE];
                let mut right_obs = vec![0; OBS_SIZE];
                let mut right_mask = vec![0; ACTION_SIZE];
                left.observe(&mut left_obs, &mut left_mask);
                right.observe(&mut right_obs, &mut right_mask);
                assert_eq!(left_obs, right_obs, "observation mismatch on seed {seed}");
                assert_eq!(left_mask, right_mask, "mask mismatch on seed {seed}");
                let left_action = left.teacher_action();
                let right_action = right.teacher_action();
                assert_eq!(left_action, right_action);
                assert_eq!(
                    left_mask[left_action], 1,
                    "illegal teacher action on seed {seed}, turn {}",
                    left.turns
                );
                let left_terminal = left.step(left_action);
                let right_terminal = right.step(right_action);
                assert_eq!(
                    left_terminal, right_terminal,
                    "terminal mismatch on seed {seed}"
                );
                if left_terminal.done {
                    break;
                }
            }
        }
    }

    #[test]
    fn level5_natural_forager_is_deterministic_and_never_trains() {
        let mut positive_score_episodes = 0;
        for seed in 500..550 {
            let mut a = Level3Env::new_level5_forager(seed, 240);
            let mut b = Level3Env::new_level5_forager(seed, 240);
            let terminal = loop {
                let action_a = a.teacher_action();
                let action_b = b.teacher_action();
                assert_eq!(action_a, action_b);
                let result_a = a.step(action_a);
                let result_b = b.step(action_b);
                assert_eq!(result_a, result_b, "terminal mismatch on seed {seed}");
                assert_eq!(
                    (0..a.state.n_units as usize)
                        .filter(|&unit| a.state.u_pl[unit] == 1)
                        .count(),
                    1,
                    "forager trained on seed {seed}"
                );
                if result_a.done {
                    break result_a;
                }
            };
            assert_eq!(terminal.opponent_workers, 1);
            positive_score_episodes += usize::from(terminal.opponent_score > 0);
        }
        assert!(
            positive_score_episodes > 0,
            "forager never banked natural fruit"
        );
    }

    #[test]
    fn level5_natural_planter_is_deterministic_renewable_and_never_trains() {
        let mut crop_episodes = 0;
        let mut renewable_episodes = 0;
        for seed in 0..50 {
            let mut left = Level3Env::new_level5_planter(seed, 240);
            let mut right = Level3Env::new_level5_planter(seed, 240);
            let terminal = loop {
                let preview = left.natural_planter_commands();
                assert!(preview.train.is_none());
                for ui in 0..left.state.n_units as usize {
                    if left.state.u_pl[ui] == 1 {
                        assert!(matches!(
                            preview.acts[ui],
                            FAct::Move(_) | FAct::Harvest | FAct::Drop | FAct::Plant(_)
                        ));
                    }
                }
                let left_action = left.teacher_action();
                let right_action = right.teacher_action();
                assert_eq!(left_action, right_action);
                let mut observation = vec![0; OBS_SIZE];
                let mut mask = vec![0; ACTION_SIZE];
                left.observe(&mut observation, &mut mask);
                assert_eq!(
                    mask[left_action], 1,
                    "illegal planter teacher action on seed {seed}, turn {}",
                    left.turns
                );
                let left_terminal = left.step(left_action);
                let right_terminal = right.step(right_action);
                assert_eq!(
                    left_terminal, right_terminal,
                    "terminal mismatch on seed {seed}"
                );
                assert_eq!(
                    (0..left.state.n_units as usize)
                        .filter(|&unit| left.state.u_pl[unit] == 1)
                        .count(),
                    1,
                    "planter trained on seed {seed}"
                );
                if left_terminal.done {
                    break left_terminal;
                }
            };
            crop_episodes += usize::from(terminal.opponent_created_crops > 0);
            renewable_episodes += usize::from(terminal.opponent_renewable_harvests > 0);
        }
        assert!(crop_episodes > 0, "planter never established a crop");
        assert!(
            renewable_episodes > 0,
            "planter never harvested its own crop"
        );
    }

    #[test]
    fn level5_one_shot_reaper_is_deterministic_and_never_trains_or_reaps_twice() {
        let mut destruction_episodes = 0;
        for seed in 0..50 {
            let mut left = Level3Env::new_level5_reaper(seed, 240);
            let mut right = Level3Env::new_level5_reaper(seed, 240);
            let terminal = loop {
                let preview = left.one_shot_reaper_commands();
                assert!(preview.train.is_none());
                for ui in 0..left.state.n_units as usize {
                    if left.state.u_pl[ui] == 1 {
                        assert!(matches!(
                            preview.acts[ui],
                            FAct::Move(_)
                                | FAct::Harvest
                                | FAct::Drop
                                | FAct::Plant(_)
                                | FAct::Chop
                        ));
                    }
                }
                let left_action = left.teacher_action();
                let right_action = right.teacher_action();
                assert_eq!(left_action, right_action);
                let left_terminal = left.step(left_action);
                let right_terminal = right.step(right_action);
                assert_eq!(left_terminal, right_terminal, "seed {seed}");
                assert!(left.opponent_crop_destructions <= 1);
                assert_eq!(
                    (0..left.state.n_units as usize)
                        .filter(|&unit| left.state.u_pl[unit] == 1)
                        .count(),
                    1
                );
                if left_terminal.done {
                    break left_terminal;
                }
            };
            destruction_episodes += usize::from(terminal.opponent_crop_destructions == 1);
        }
        assert!(destruction_episodes > 0, "reaper never destroyed a crop");
    }

    #[test]
    fn level5_funded_pair_is_deterministic_funded_and_capped_at_two() {
        let mut trained_episodes = 0;
        let mut productive_episodes = 0;
        for seed in 0..50 {
            let mut left = Level3Env::new_level5_funded_pair(seed, 240);
            let mut right = Level3Env::new_level5_funded_pair(seed, 240);
            let terminal = loop {
                let left_action = left.teacher_action();
                let right_action = right.teacher_action();
                assert_eq!(left_action, right_action);
                let left_terminal = left.step(left_action);
                let right_terminal = right.step(right_action);
                assert_eq!(left_terminal, right_terminal, "seed {seed}");
                let opponent_units: Vec<usize> = (0..left.state.n_units as usize)
                    .filter(|&unit| left.state.u_pl[unit] == 1)
                    .collect();
                assert!(opponent_units.len() <= 2, "seed {seed}");
                if opponent_units.len() == 2 {
                    assert!(left.opponent_funding_deposits > 0, "seed {seed}");
                    let trained = opponent_units
                        .into_iter()
                        .find(|&unit| left.state.u_id[unit] != left.opponent_starter_id)
                        .expect("second worker is not the starter");
                    assert_eq!(
                        (
                            left.state.u_ms[trained],
                            left.state.u_cc[trained],
                            left.state.u_hp[trained],
                            left.state.u_chop[trained],
                        ),
                        OPPONENT_D5_TARGET,
                    );
                }
                assert!(left.opponent_crop_destructions <= 1, "seed {seed}");
                if left_terminal.done {
                    break left_terminal;
                }
            };
            if terminal.opponent_training_turn > 0 {
                trained_episodes += 1;
                assert_eq!(terminal.opponent_workers, 2);
                assert!(terminal.opponent_funding_deposits > 0);
            }
            productive_episodes +=
                usize::from(terminal.opponent_second_worker_productive_actions > 0);
        }
        assert!(trained_episodes > 0, "funded opponent never trained");
        assert!(
            productive_episodes > 0,
            "trained worker was never productive"
        );
    }

    #[test]
    fn level5_funded_trio_requires_two_funding_epochs_and_caps_at_three() {
        let mut third_worker_episodes = 0;
        let mut second_productive_episodes = 0;
        let mut third_productive_episodes = 0;
        for seed in 0..100 {
            let mut left = Level3Env::new_level5_funded_trio(seed, 240);
            let mut right = Level3Env::new_level5_funded_trio(seed, 240);
            let terminal = loop {
                let left_action = left.teacher_action();
                let right_action = right.teacher_action();
                assert_eq!(left_action, right_action);
                let left_terminal = left.step(left_action);
                let right_terminal = right.step(right_action);
                assert_eq!(left_terminal, right_terminal, "seed {seed}");
                let mut opponent_units: Vec<usize> = (0..left.state.n_units as usize)
                    .filter(|&unit| left.state.u_pl[unit] == 1)
                    .collect();
                opponent_units.sort_by_key(|&unit| left.state.u_id[unit]);
                assert!(opponent_units.len() <= 3, "seed {seed}");
                if opponent_units.len() >= 2 {
                    let second = opponent_units[1];
                    assert_eq!(
                        (
                            left.state.u_ms[second],
                            left.state.u_cc[second],
                            left.state.u_hp[second],
                            left.state.u_chop[second],
                        ),
                        OPPONENT_D5_TARGET,
                    );
                    assert!(left.opponent_funded_training_events >= 1, "seed {seed}");
                }
                if opponent_units.len() == 3 {
                    let third = opponent_units[2];
                    assert_eq!(
                        (
                            left.state.u_ms[third],
                            left.state.u_cc[third],
                            left.state.u_hp[third],
                            left.state.u_chop[third],
                        ),
                        OPPONENT_D6_TARGET,
                    );
                    assert_eq!(left.opponent_funded_training_events, 2, "seed {seed}");
                }
                assert!(left.opponent_crop_destructions <= 1, "seed {seed}");
                if left_terminal.done {
                    break left_terminal;
                }
            };
            if terminal.opponent_third_worker_training_turn > 0 {
                third_worker_episodes += 1;
                assert_eq!(terminal.opponent_workers, 3);
                assert_eq!(terminal.opponent_funded_training_events, 2);
            }
            second_productive_episodes +=
                usize::from(terminal.opponent_second_worker_productive_actions > 0);
            third_productive_episodes +=
                usize::from(terminal.opponent_third_worker_productive_actions > 0);
        }
        assert!(
            third_worker_episodes > 0,
            "opponent never trained worker three"
        );
        assert!(
            second_productive_episodes > 0,
            "standard chopper was never productive"
        );
        assert!(third_productive_episodes > 0, "feeder was never productive");
    }

    #[test]
    fn level5_sustained_trio_never_terminates_before_turn_120() {
        for seed in 0..30 {
            let mut left = Level3Env::new_level5_funded_trio_sustained(seed, 240);
            let mut right = Level3Env::new_level5_funded_trio_sustained(seed, 240);
            let terminal = loop {
                let mut observation = vec![0; OBS_SIZE];
                let mut mask = vec![0; ACTION_SIZE];
                left.observe(&mut observation, &mut mask);
                let left_action = left.teacher_action();
                let right_action = right.teacher_action();
                assert_eq!(left_action, right_action);
                assert_eq!(mask[left_action], 1, "seed {seed}, turn {}", left.turns);
                let left_terminal = left.step(left_action);
                let right_terminal = right.step(right_action);
                assert_eq!(left_terminal, right_terminal, "seed {seed}");
                if left_terminal.done {
                    break left_terminal;
                }
            };
            assert!(terminal.success, "seed {seed}: {terminal:?}");
            assert!(terminal.turns >= 120, "seed {seed}: {terminal:?}");
            assert!(terminal.opponent_workers <= 3);
            if terminal.opponent_third_worker_training_turn > 0 {
                assert_eq!(terminal.opponent_funded_training_events, 2);
            }
        }
    }

    #[test]
    fn level5_sustained_trio_180_is_distinct_and_never_terminates_early() {
        for seed in 0..30 {
            let turn_120 = Level3Env::new_level5_funded_trio_sustained(seed, 240);
            let mut turn_180 = Level3Env::new_level5_funded_trio_sustained_180(seed, 240);
            assert_eq!(turn_120.min_success_turn, 120);
            assert_eq!(turn_180.min_success_turn, 180);
            let terminal = loop {
                let mut observation = vec![0; OBS_SIZE];
                let mut mask = vec![0; ACTION_SIZE];
                turn_180.observe(&mut observation, &mut mask);
                let selected = turn_180.teacher_action();
                assert_eq!(mask[selected], 1, "seed {seed}, turn {}", turn_180.turns);
                let terminal = turn_180.step(selected);
                if terminal.done {
                    break terminal;
                }
            };
            assert!(terminal.success, "seed {seed}: {terminal:?}");
            assert!(terminal.turns >= 180, "seed {seed}: {terminal:?}");
            assert!(terminal.opponent_workers <= 3);
            if terminal.opponent_third_worker_training_turn > 0 {
                assert_eq!(terminal.opponent_funded_training_events, 2);
            }
        }
    }

    #[test]
    fn level5_crop_first_trio_creates_supply_before_worker_three() {
        let mut third_worker_episodes = 0;
        for seed in 0..50 {
            let mut left = Level3Env::new_level5_crop_first_funded_trio_sustained_180(seed, 240);
            let mut right = Level3Env::new_level5_crop_first_funded_trio_sustained_180(seed, 240);
            let terminal = loop {
                let before_workers = (0..left.state.n_units as usize)
                    .filter(|&unit| left.state.u_pl[unit] == 1)
                    .count();
                let crops_before = left.opponent_created_crops;
                let selected = left.teacher_action();
                assert_eq!(selected, right.teacher_action());
                let left_terminal = left.step(selected);
                let right_terminal = right.step(selected);
                assert_eq!(left_terminal, right_terminal, "seed {seed}");
                let after_workers = (0..left.state.n_units as usize)
                    .filter(|&unit| left.state.u_pl[unit] == 1)
                    .count();
                if before_workers == 2 && after_workers == 3 {
                    assert!(
                        crops_before > 0,
                        "seed {seed} trained worker three before crop creation"
                    );
                    assert_eq!(left.opponent_funded_training_events, 2, "seed {seed}");
                }
                assert!(left.opponent_crop_destructions <= 1, "seed {seed}");
                if left_terminal.done {
                    break left_terminal;
                }
            };
            assert!(terminal.success, "seed {seed}: {terminal:?}");
            assert!(terminal.turns >= 180, "seed {seed}: {terminal:?}");
            assert!(terminal.opponent_workers <= 3);
            if terminal.opponent_third_worker_training_turn > 0 {
                third_worker_episodes += 1;
                assert!(terminal.opponent_created_crops > 0);
                assert_eq!(terminal.opponent_funded_training_events, 2);
            }
        }
        assert!(third_worker_episodes > 0);
    }

    #[test]
    fn level5_repeated_pressure_is_bounded_active_and_preserves_crop_first_scale() {
        let mut two_destruction_episodes = 0;
        let mut three_destruction_episodes = 0;
        for seed in 0..50 {
            let mut left =
                Level3Env::new_level5_crop_first_funded_trio_repeated_pressure_180(seed, 240);
            let mut right =
                Level3Env::new_level5_crop_first_funded_trio_repeated_pressure_180(seed, 240);
            let terminal = loop {
                let before_workers = (0..left.state.n_units as usize)
                    .filter(|&unit| left.state.u_pl[unit] == 1)
                    .count();
                let crops_before = left.opponent_created_crops;
                let mut observation = vec![0; OBS_SIZE];
                let mut mask = vec![0; ACTION_SIZE];
                left.observe(&mut observation, &mut mask);
                let selected = left.teacher_action();
                assert_eq!(mask[selected], 1, "seed {seed}, turn {}", left.turns);
                assert_eq!(selected, right.teacher_action());
                let left_terminal = left.step(selected);
                let right_terminal = right.step(selected);
                assert_eq!(left_terminal, right_terminal, "seed {seed}");
                let after_workers = (0..left.state.n_units as usize)
                    .filter(|&unit| left.state.u_pl[unit] == 1)
                    .count();
                if before_workers == 2 && after_workers == 3 {
                    assert!(
                        crops_before > 0,
                        "seed {seed} trained worker three before crop creation"
                    );
                    assert_eq!(left.opponent_funded_training_events, 2, "seed {seed}");
                }
                assert!(left.opponent_crop_destructions <= 3, "seed {seed}");
                if left_terminal.done {
                    break left_terminal;
                }
            };
            assert!(terminal.turns >= 180, "seed {seed}: {terminal:?}");
            assert!(terminal.opponent_workers <= 3, "seed {seed}: {terminal:?}");
            two_destruction_episodes += usize::from(terminal.opponent_crop_destructions >= 2);
            three_destruction_episodes += usize::from(terminal.opponent_crop_destructions == 3);
        }
        assert!(two_destruction_episodes > 0);
        assert!(three_destruction_episodes > 0);
    }

    #[test]
    fn level5_reacquisition_mode_changes_only_expert_labels() {
        let mut divergent_labels = 0usize;
        for seed in 0..50 {
            let mut d10 =
                Level3Env::new_level5_crop_first_funded_trio_repeated_pressure_180(seed, 240);
            let mut d11 =
                Level3Env::new_level5_crop_first_funded_trio_repeated_pressure_reacquire_180(
                    seed, 240,
                );
            loop {
                let mut d10_obs = vec![0; OBS_SIZE];
                let mut d10_mask = vec![0; ACTION_SIZE];
                let mut d11_obs = vec![0; OBS_SIZE];
                let mut d11_mask = vec![0; ACTION_SIZE];
                d10.observe(&mut d10_obs, &mut d10_mask);
                d11.observe(&mut d11_obs, &mut d11_mask);
                assert_eq!(d10_obs, d11_obs, "seed {seed}, turn {}", d10.turns);
                assert_eq!(d10_mask, d11_mask, "seed {seed}, turn {}", d10.turns);

                let d10_label = d10.teacher_action();
                let d11_label = d11.teacher_action();
                if d10_label != d11_label {
                    divergent_labels += 1;
                    let ui = d11.active_ui();
                    assert!(d11.target_built());
                    assert_eq!(ui, d11.starter_ui());
                    assert!(!d11.crop_exists());
                    assert_eq!(d11.state.u_carry[ui].iter().sum::<i8>(), 0);
                    assert_eq!(d11.state.inv[0][BANANA], 0);
                    assert_eq!(d11_mask[d11_label], 1);
                }
                let d10_terminal = d10.step(d10_label);
                let d11_terminal = d11.step(d10_label);
                assert_eq!(d10_terminal, d11_terminal, "seed {seed}");
                if d10_terminal.done {
                    break;
                }
            }
        }
        assert!(divergent_labels > 0);
    }

    #[test]
    fn level5_reacquisition_expert_is_deterministic_legal_and_active() {
        let mut successes = 0usize;
        let mut three_destruction_episodes = 0usize;
        for seed in 0..50 {
            let mut left =
                Level3Env::new_level5_crop_first_funded_trio_repeated_pressure_reacquire_180(
                    seed, 240,
                );
            let mut right =
                Level3Env::new_level5_crop_first_funded_trio_repeated_pressure_reacquire_180(
                    seed, 240,
                );
            let terminal = loop {
                let mut observation = vec![0; OBS_SIZE];
                let mut mask = vec![0; ACTION_SIZE];
                left.observe(&mut observation, &mut mask);
                let selected = left.teacher_action();
                assert_eq!(selected, right.teacher_action(), "seed {seed}");
                assert_eq!(mask[selected], 1, "seed {seed}, turn {}", left.turns);
                let left_terminal = left.step(selected);
                let right_terminal = right.step(selected);
                assert_eq!(left_terminal, right_terminal, "seed {seed}");
                assert!(left.opponent_crop_destructions <= 3, "seed {seed}");
                if left_terminal.done {
                    break left_terminal;
                }
            };
            successes += usize::from(terminal.success);
            three_destruction_episodes += usize::from(terminal.opponent_crop_destructions == 3);
            assert!(terminal.turns >= 180, "seed {seed}: {terminal:?}");
            assert!(terminal.opponent_workers <= 3, "seed {seed}: {terminal:?}");
        }
        assert!(successes >= 45);
        assert!(three_destruction_episodes > 0);
    }

    #[test]
    fn level6_teacher_is_deterministic_legal_and_return_telescopes_to_margin() {
        let mut seen = [false; LEVEL6_OPPONENTS.len()];
        for seed in 0..240 {
            let mode = level6_opponent(seed);
            seen[LEVEL6_OPPONENTS
                .iter()
                .position(|candidate| *candidate == mode)
                .expect("level-six opponent")] = true;
        }
        assert!(seen.into_iter().all(|value| value));

        for seed in 0..24 {
            let mut left = Level3Env::new_level6(seed, 30);
            let mut right = Level3Env::new_level6(seed, 30);
            assert!(left.competitive);
            assert_eq!(left.opponent_mode, level6_opponent(seed));
            let terminal = loop {
                let mut observation = vec![0; OBS_SIZE];
                let mut mask = vec![0; ACTION_SIZE];
                left.observe(&mut observation, &mut mask);
                let selected = left.teacher_action();
                assert_eq!(selected, right.teacher_action(), "seed {seed}");
                assert_eq!(mask[selected], 1, "seed {seed}, turn {}", left.turns);
                let left_terminal = left.step(selected);
                let right_terminal = right.step(selected);
                assert_eq!(left_terminal, right_terminal, "seed {seed}");
                if left_terminal.done {
                    break left_terminal;
                }
            };
            let margin = i32::from(terminal.score_gain) - i32::from(terminal.opponent_score);
            assert_eq!(terminal.turns, 30);
            assert_eq!(terminal.success, margin > 0);
            assert!(
                (terminal.episode_return - margin as f32 / 100.0).abs() <= 1e-5,
                "seed {seed}: {terminal:?}, margin={margin}"
            );
        }
    }

    #[test]
    fn level6_teacher_replans_when_baseline_occupies_the_crop_cell() {
        let seed = 8_000_107;
        let mut env = Level3Env::new_level6(seed, 300);
        assert_eq!(env.opponent_mode, OpponentMode::CompleteBaseline);
        loop {
            let mut observation = vec![0; OBS_SIZE];
            let mut mask = vec![0; ACTION_SIZE];
            env.observe(&mut observation, &mut mask);
            let selected = env.teacher_action();
            let active = env.active_ui();
            assert_eq!(
                mask[selected],
                1,
                "seed {seed}, turn {}, action {selected} (plane {}, x {}, y {}), active {:?}, planned {:?}, created {:?}",
                env.turns,
                selected / OBS_CELLS,
                selected % OBS_CELLS % OBS_WIDTH,
                selected % OBS_CELLS / OBS_WIDTH,
                (env.state.u_x[active], env.state.u_y[active]),
                env.planned_crop,
                env.created_crop,
            );
            if env.step(selected).done {
                break;
            }
        }
    }

    #[test]
    fn level4_teacher_is_legal_and_closes_every_recipe() {
        let mut seen = [false; crate::rl_level1::LEVEL2_TARGETS.len()];
        for seed in 0..200 {
            let mut env = Level3Env::new_level4(seed, 240);
            let (recipe_id, target) = level2_recipe(seed);
            assert_eq!(env.recipe_id, recipe_id);
            assert_eq!(env.target, target);
            seen[recipe_id as usize] = true;
            let mut terminal = None;
            for _ in 0..480 {
                let mut obs = vec![0; OBS_SIZE];
                let mut mask = vec![0; ACTION_SIZE];
                env.observe(&mut obs, &mut mask);
                for (offset, value) in [target.0, target.1, target.2, target.3]
                    .into_iter()
                    .enumerate()
                {
                    assert_eq!(obs[(86 + offset) * OBS_CELLS], quant(value as f32, 4.0));
                }
                let selected = env.teacher_action();
                assert_eq!(
                    mask[selected], 1,
                    "seed {seed}, recipe {recipe_id}, turn {}, phase {}",
                    env.turns, env.decision_phase
                );
                let result = env.step(selected);
                if result.done {
                    terminal = Some(result);
                    break;
                }
            }
            let terminal = terminal.unwrap_or_else(|| {
                panic!("teacher did not terminate seed {seed}, recipe {recipe_id}")
            });
            assert!(
                terminal.success,
                "teacher timed out seed {seed}, recipe {recipe_id}: {terminal:?}"
            );
            assert_eq!(terminal.recipe_id, recipe_id);
            assert_eq!(terminal.target, target);
        }
        assert!(seen.into_iter().all(|value| value));
    }

    #[test]
    fn fixed_level3_constructor_keeps_standard_chopper_contract() {
        for seed in 0..20 {
            let env = Level3Env::new(seed, 240);
            assert_eq!(env.target, LEVEL3_TARGET);
            assert_eq!(env.recipe_id, 6);
            assert_eq!(
                env.teacher_action(),
                Level3Env::new(seed, 240).teacher_action()
            );
        }
    }

    #[test]
    fn dimensions_match_shared_actor_contract() {
        assert_eq!(crate::rl_level1::OBS_CHANNELS, 104);
        assert_eq!(crate::rl_level1::OBS_HEIGHT, 11);
        assert_eq!(OBS_WIDTH, 22);
        assert_eq!(crate::rl_level1::ACTION_PLANES, 13);
    }
}
