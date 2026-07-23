//! Closed-loop opening-establishment portfolio environment for D71.

use rayon::prelude::*;

use crate::rl_batch_option::{
    BatchOptionEnv, BatchOptionTerminal, BATCH_OPTION_ACTIONS, BATCH_OPTION_FEATURES,
};
use crate::rl_macro::{MacroDecisionStage, MacroOpponentMode, MacroTerminal, PlantOwner};

pub const OPENING_PORTFOLIO_ACTIONS: usize = 8;
pub const OPENING_PORTFOLIO_FEATURES: usize = BATCH_OPTION_FEATURES + 16;

#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
pub struct OpeningPortfolioMemory {
    pub source_attempts: [u16; 4],
    pub source_creations: [u16; 4],
    pub renewable_receipts: u16,
    pub ended_own_generations: u16,
    pub reinvested_generations: u16,
    pub live_own_generations: u16,
    pub previous_was_source: bool,
    pub last_source_turn: Option<i32>,
    pub source_in_flight: bool,
}

#[derive(Clone, Copy, Debug)]
pub struct OpeningPortfolioStep {
    pub terminal: MacroTerminal,
    pub source_assigned: bool,
}

pub struct OpeningPortfolioEnv {
    pub batch: BatchOptionEnv,
    source_attempts: [u16; 4],
    previous_was_source: bool,
    last_source_turn: Option<i32>,
    terminal: MacroTerminal,
}

impl OpeningPortfolioEnv {
    pub fn new(map_seed: i64, seat: usize, opponent_mode: MacroOpponentMode) -> Self {
        Self {
            batch: BatchOptionEnv::new(map_seed, seat, opponent_mode),
            source_attempts: [0; 4],
            previous_was_source: false,
            last_source_turn: None,
            terminal: MacroTerminal::default(),
        }
    }

    pub fn memory(&self) -> OpeningPortfolioMemory {
        let source_creations = self.batch.macro_env.explicit_source_creations();
        let live = self
            .batch
            .macro_env
            .state
            .plants
            .iter()
            .filter(|plant| plant.health > 0)
            .filter(|plant| {
                self.batch.macro_env.owners().get(&plant.pos()) == Some(&PlantOwner::Own)
            })
            .count()
            .min(u16::MAX as usize) as u16;
        OpeningPortfolioMemory {
            source_attempts: self.source_attempts,
            source_creations,
            renewable_receipts: self.terminal.own_owned_crop_harvest_units,
            ended_own_generations: self.terminal.own_created_crops.saturating_sub(live),
            reinvested_generations: self.terminal.own_reinvested_crops,
            live_own_generations: live,
            previous_was_source: self.previous_was_source,
            last_source_turn: self.last_source_turn,
            source_in_flight: self.batch.macro_env.opening_source_in_flight(),
        }
    }

    pub fn legal_mask(&self) -> [u8; OPENING_PORTFOLIO_ACTIONS] {
        let ordinary = self.batch.legal_mask();
        let sources = self.batch.opening_source_mask();
        std::array::from_fn(|index| {
            if index < BATCH_OPTION_ACTIONS {
                ordinary[index]
            } else {
                sources[index - BATCH_OPTION_ACTIONS]
            }
        })
    }

    pub fn features(&self) -> [f32; OPENING_PORTFOLIO_FEATURES] {
        let base = self.batch.features();
        let memory = self.memory();
        let mut result = [0.0f32; OPENING_PORTFOLIO_FEATURES];
        result[..BATCH_OPTION_FEATURES].copy_from_slice(&base);
        for kind in 0..4 {
            result[56 + kind] = memory.source_attempts[kind] as f32 / 10.0;
            result[60 + kind] = memory.source_creations[kind] as f32 / 10.0;
        }
        result[64] = memory.renewable_receipts as f32 / 40.0;
        result[65] = memory.ended_own_generations as f32 / 20.0;
        result[66] = memory.reinvested_generations as f32 / 20.0;
        result[67] = memory.live_own_generations as f32 / 20.0;
        result[68] = f32::from(memory.renewable_receipts > 0);
        result[69] = f32::from(memory.previous_was_source);
        result[70] = memory
            .last_source_turn
            .map(|turn| (self.batch.macro_env.state.turn - turn).max(0) as f32 / 300.0)
            .unwrap_or(1.0);
        result[71] = f32::from(memory.source_in_flight);
        assert!(result.iter().all(|value| value.is_finite()));
        result
    }

    pub fn step(&mut self, action: usize) -> OpeningPortfolioStep {
        assert_eq!(self.batch.macro_env.stage(), MacroDecisionStage::Train);
        assert!(action < OPENING_PORTFOLIO_ACTIONS);
        assert_eq!(
            self.legal_mask()[action],
            1,
            "illegal opening-portfolio action"
        );
        if action < BATCH_OPTION_ACTIONS {
            self.previous_was_source = false;
            self.terminal = self.batch.step(action);
            OpeningPortfolioStep {
                terminal: self.terminal,
                source_assigned: false,
            }
        } else {
            let kind = action - BATCH_OPTION_ACTIONS;
            self.source_attempts[kind] = self.source_attempts[kind].saturating_add(1);
            self.previous_was_source = true;
            self.last_source_turn = Some(self.batch.macro_env.state.turn);
            let (terminal, source_assigned) = self.batch.step_with_opening_source(kind);
            self.terminal = terminal;
            OpeningPortfolioStep {
                terminal: self.terminal,
                source_assigned,
            }
        }
    }
}

struct OpeningRecurrentSlot {
    task_index: u64,
    env: OpeningPortfolioEnv,
}

pub struct OpeningRecurrentBatch {
    slots: Vec<OpeningRecurrentSlot>,
    seed_base: i64,
    next_task_index: u64,
}

impl OpeningRecurrentBatch {
    pub fn new(num_envs: usize, seed_base: i64) -> Self {
        assert!(num_envs > 0);
        let slots = (0..num_envs)
            .map(|task_index| Self::make_slot(seed_base, task_index as u64))
            .collect();
        Self {
            slots,
            seed_base,
            next_task_index: num_envs as u64,
        }
    }

    fn task(seed_base: i64, task_index: u64) -> (i64, usize, usize) {
        let per_map = 2 * MacroOpponentMode::ALL.len() as u64;
        let within_map = task_index % per_map;
        let map_seed = seed_base + (task_index / per_map) as i64;
        let seat = (within_map / MacroOpponentMode::ALL.len() as u64) as usize;
        let opponent = (within_map % MacroOpponentMode::ALL.len() as u64) as usize;
        (map_seed, seat, opponent)
    }

    fn make_slot(seed_base: i64, task_index: u64) -> OpeningRecurrentSlot {
        let (map_seed, seat, opponent) = Self::task(seed_base, task_index);
        OpeningRecurrentSlot {
            task_index,
            env: OpeningPortfolioEnv::new(map_seed, seat, MacroOpponentMode::from_index(opponent)),
        }
    }

    pub fn len(&self) -> usize {
        self.slots.len()
    }

    pub fn is_empty(&self) -> bool {
        self.slots.is_empty()
    }

    pub fn observe(&mut self, features: &mut [f32], masks: &mut [u8]) {
        assert_eq!(features.len(), self.len() * OPENING_PORTFOLIO_FEATURES);
        assert_eq!(masks.len(), self.len() * BATCH_OPTION_ACTIONS);
        self.slots
            .par_iter_mut()
            .zip(features.par_chunks_mut(OPENING_PORTFOLIO_FEATURES))
            .zip(masks.par_chunks_mut(BATCH_OPTION_ACTIONS))
            .for_each(|((slot, feature_chunk), mask_chunk)| {
                feature_chunk.copy_from_slice(&slot.env.features());
                mask_chunk.copy_from_slice(&slot.env.legal_mask()[..BATCH_OPTION_ACTIONS]);
            });
    }

    pub fn step(
        &mut self,
        selected_modes: &[i32],
        rewards: &mut [f32],
        terminals: &mut [BatchOptionTerminal],
    ) {
        assert_eq!(selected_modes.len(), self.len());
        assert_eq!(rewards.len(), self.len());
        assert_eq!(terminals.len(), self.len());
        terminals.fill(BatchOptionTerminal::default());
        let results: Vec<_> = self
            .slots
            .par_iter_mut()
            .zip(selected_modes.par_iter())
            .map(|(slot, mode)| {
                assert!((0..BATCH_OPTION_ACTIONS as i32).contains(mode));
                slot.env.step(*mode as usize).terminal
            })
            .collect();
        for (index, result) in results.into_iter().enumerate() {
            let slot = &mut self.slots[index];
            rewards[index] = result.margin_reward;
            if result.done {
                terminals[index] = BatchOptionTerminal {
                    done: 1,
                    seat: slot.env.batch.macro_env.seat as u8,
                    opponent: slot.env.batch.macro_env.opponent_mode.id(),
                    own_workers: result.own_workers,
                    map_seed: slot.env.batch.macro_env.map_seed,
                    task_index: slot.task_index,
                    own_score: result.own_score,
                    opponent_score: result.opponent_score,
                    successful_trains: result.successful_trains,
                    _padding: 0,
                    own_created_crops: result.own_created_crops,
                    invalid_direct_commands: result.invalid_direct_commands,
                    provenance_failures: result.provenance_failures,
                    deposit_prediction_failures: result.deposit_prediction_failures,
                    invalidated_jobs: result.invalidated_jobs,
                    action_hash: result.action_hash,
                    state_hash: result.state_hash,
                };
                let task_index = self.next_task_index;
                self.next_task_index += 1;
                self.slots[index] = Self::make_slot(self.seed_base, task_index);
            }
        }
    }
}

#[no_mangle]
pub extern "C" fn tf_opening_recurrent_features() -> usize {
    OPENING_PORTFOLIO_FEATURES
}

#[no_mangle]
pub extern "C" fn tf_opening_recurrent_actions() -> usize {
    BATCH_OPTION_ACTIONS
}

#[no_mangle]
pub extern "C" fn tf_opening_recurrent_terminal_size() -> usize {
    std::mem::size_of::<BatchOptionTerminal>()
}

#[no_mangle]
pub extern "C" fn tf_opening_recurrent_create(
    num_envs: usize,
    seed_base: i64,
) -> *mut OpeningRecurrentBatch {
    if num_envs == 0 || seed_base == 0 {
        return std::ptr::null_mut();
    }
    Box::into_raw(Box::new(OpeningRecurrentBatch::new(num_envs, seed_base)))
}

#[no_mangle]
pub unsafe extern "C" fn tf_opening_recurrent_destroy(handle: *mut OpeningRecurrentBatch) {
    if !handle.is_null() {
        drop(Box::from_raw(handle));
    }
}

#[no_mangle]
pub unsafe extern "C" fn tf_opening_recurrent_observe(
    handle: *mut OpeningRecurrentBatch,
    features: *mut f32,
    masks: *mut u8,
) -> i32 {
    if handle.is_null() || features.is_null() || masks.is_null() {
        return -1;
    }
    let batch = &mut *handle;
    let feature_slice =
        std::slice::from_raw_parts_mut(features, batch.len() * OPENING_PORTFOLIO_FEATURES);
    let mask_slice = std::slice::from_raw_parts_mut(masks, batch.len() * BATCH_OPTION_ACTIONS);
    batch.observe(feature_slice, mask_slice);
    0
}

#[no_mangle]
pub unsafe extern "C" fn tf_opening_recurrent_step(
    handle: *mut OpeningRecurrentBatch,
    selected_modes: *const i32,
    features: *mut f32,
    masks: *mut u8,
    rewards: *mut f32,
    terminals: *mut BatchOptionTerminal,
) -> i32 {
    if handle.is_null()
        || selected_modes.is_null()
        || features.is_null()
        || masks.is_null()
        || rewards.is_null()
        || terminals.is_null()
    {
        return -1;
    }
    let batch = &mut *handle;
    let selected_slice = std::slice::from_raw_parts(selected_modes, batch.len());
    let reward_slice = std::slice::from_raw_parts_mut(rewards, batch.len());
    let terminal_slice = std::slice::from_raw_parts_mut(terminals, batch.len());
    batch.step(selected_slice, reward_slice, terminal_slice);
    tf_opening_recurrent_observe(handle, features, masks)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::rl_batch_option::BatchOptionMode;

    #[test]
    fn initial_features_and_masks_are_finite() {
        let env = OpeningPortfolioEnv::new(9_803_000, 0, MacroOpponentMode::Resident);
        assert!(env.features().iter().all(|value| value.is_finite()));
        assert_eq!(env.legal_mask()[0], 1);
        assert_eq!(&env.legal_mask()[1..4], &[0, 0, 0]);
        assert!(env.legal_mask()[4..].iter().any(|value| *value == 1));
    }

    #[test]
    fn ordinary_balanced_path_matches_batch_environment() {
        let mut expected = BatchOptionEnv::new(9_803_000, 0, MacroOpponentMode::Resident);
        let mut actual = OpeningPortfolioEnv::new(9_803_000, 0, MacroOpponentMode::Resident);
        loop {
            let left = expected.step(BatchOptionMode::Balanced as usize);
            let right = actual.step(0).terminal;
            assert_eq!(left, right);
            if left.done {
                break;
            }
        }
    }

    #[test]
    fn every_ordinary_mode_matches_batch_environment() {
        for mode in 0..BATCH_OPTION_ACTIONS {
            let mut expected = BatchOptionEnv::new(9_810_999, 1, MacroOpponentMode::GoldAdaptive);
            let mut actual =
                OpeningPortfolioEnv::new(9_810_999, 1, MacroOpponentMode::GoldAdaptive);
            loop {
                let selected = if expected.legal_mask()[mode] == 1 {
                    mode
                } else {
                    0
                };
                let left = expected.step(selected);
                let right = actual.step(selected).terminal;
                assert_eq!(left, right);
                if left.done {
                    break;
                }
            }
        }
    }

    #[test]
    fn legal_source_action_is_assigned_and_remembered() {
        let mut env = OpeningPortfolioEnv::new(9_803_000, 0, MacroOpponentMode::Resident);
        let action = (4..8)
            .find(|action| env.legal_mask()[*action] == 1)
            .expect("initial legal source action");
        let result = env.step(action);
        assert!(result.source_assigned);
        assert_eq!(env.memory().source_attempts.iter().sum::<u16>(), 1);
        assert!(env.features()[69] > 0.5);
    }
}
