//! Renewable-safe semi-Markov batch-option environment for D62.

use rayon::prelude::*;

use crate::d41b_prior_kernel::exact_prior_order;
use crate::rl_macro::{
    CompleteMacroEnv, MacroCandidateObservation, MacroDecisionStage, MacroOpponentMode,
    MacroSelectionBranch, MacroTerminal, MacroTrainGoal, PlantOwner, MACRO_CELLS,
    MACRO_TOTAL_TURNS,
};

pub const BATCH_OPTION_FEATURES: usize = 56;
pub const BATCH_OPTION_ACTIONS: usize = 4;

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
#[repr(u8)]
pub enum BatchOptionMode {
    Balanced = 0,
    Harvest = 1,
    Renew = 2,
    Fell = 3,
}

impl BatchOptionMode {
    pub const ALL: [Self; BATCH_OPTION_ACTIONS] =
        [Self::Balanced, Self::Harvest, Self::Renew, Self::Fell];

    pub fn from_index(index: usize) -> Self {
        Self::ALL[index]
    }

    fn job_feature(self) -> Option<usize> {
        match self {
            Self::Balanced => None,
            Self::Harvest => Some(20 + 3),
            Self::Renew => Some(20 + 4),
            Self::Fell => Some(20 + 2),
        }
    }
}

fn owner_index(owner: PlantOwner) -> usize {
    match owner {
        PlantOwner::Natural => 0,
        PlantOwner::Own => 1,
        PlantOwner::Opponent => 2,
        PlantOwner::Ambiguous => 3,
    }
}

pub struct BatchOptionEnv {
    pub macro_env: CompleteMacroEnv,
    last_mode: Option<BatchOptionMode>,
    mode_batches: [u32; BATCH_OPTION_ACTIONS],
}

impl BatchOptionEnv {
    pub fn new(map_seed: i64, seat: usize, opponent_mode: MacroOpponentMode) -> Self {
        let macro_env = CompleteMacroEnv::new(map_seed, seat, opponent_mode);
        assert_eq!(macro_env.stage(), MacroDecisionStage::Train);
        Self {
            macro_env,
            last_mode: None,
            mode_batches: [0; BATCH_OPTION_ACTIONS],
        }
    }

    pub fn live_own_plants(&self) -> usize {
        self.macro_env
            .state
            .plants
            .iter()
            .filter(|plant| plant.health > 0)
            .filter(|plant| self.macro_env.owners().get(&plant.pos()) == Some(&PlantOwner::Own))
            .count()
    }

    pub fn legal_mask(&self) -> [u8; BATCH_OPTION_ACTIONS] {
        if self.live_own_plants() == 0 {
            [1, 0, 0, 0]
        } else {
            [1; BATCH_OPTION_ACTIONS]
        }
    }

    pub fn opening_source_mask(&self) -> [u8; 4] {
        std::array::from_fn(|kind| {
            u8::from(self.macro_env.opening_bank_seed_source_available(kind))
        })
    }

    pub fn features(&self) -> [f32; BATCH_OPTION_FEATURES] {
        assert_eq!(self.macro_env.stage(), MacroDecisionStage::Train);
        let own = self.macro_env.seat;
        let opponent = 1 - own;
        let own_units: Vec<_> = self
            .macro_env
            .state
            .units
            .iter()
            .filter(|unit| unit.player as usize == own)
            .collect();
        let opponent_units: Vec<_> = self
            .macro_env
            .state
            .units
            .iter()
            .filter(|unit| unit.player as usize == opponent)
            .collect();
        let mut result = [0.0f32; BATCH_OPTION_FEATURES];
        result[0] = 1.0;
        result[1] = self.macro_env.state.turn as f32 / MACRO_TOTAL_TURNS as f32;
        result[2] = own_units.len() as f32 / 3.0;
        result[3] = opponent_units.len() as f32 / 3.0;
        result[4] = self.macro_env.state.scores[own] as f32 / 400.0;
        result[5] = self.macro_env.state.scores[opponent] as f32 / 400.0;
        result[6] = (self.macro_env.state.scores[own] - self.macro_env.state.scores[opponent])
            as f32
            / 400.0;
        for item in 0..6 {
            result[7 + item] = self.macro_env.state.inventories[own][item] as f32 / 20.0;
            result[13 + item] = self.macro_env.state.inventories[opponent][item] as f32 / 20.0;
            result[19 + item] =
                own_units.iter().map(|unit| unit.carry[item]).sum::<i32>() as f32 / 20.0;
            result[25 + item] = opponent_units
                .iter()
                .map(|unit| unit.carry[item])
                .sum::<i32>() as f32
                / 20.0;
        }
        let mut plant_counts = [0usize; 4];
        let mut fruit_counts = [0i32; 4];
        for plant in self
            .macro_env
            .state
            .plants
            .iter()
            .filter(|plant| plant.health > 0)
        {
            let owner = *self
                .macro_env
                .owners()
                .get(&plant.pos())
                .expect("batch-option live plant provenance");
            let index = owner_index(owner);
            plant_counts[index] += 1;
            fruit_counts[index] = fruit_counts[index].saturating_add(plant.fruits);
        }
        for index in 0..4 {
            result[31 + index] = plant_counts[index] as f32 / 20.0;
            result[35 + index] = fruit_counts[index] as f32 / 40.0;
        }
        result[39] = f32::from(plant_counts[owner_index(PlantOwner::Own)] > 0);
        result[40] = f32::from(plant_counts[owner_index(PlantOwner::Opponent)] > 0);
        result[41 + self.macro_env.train_goal().action_plane()] = 1.0;
        if let Some(mode) = self.last_mode {
            result[44 + mode as usize] = 1.0;
        }
        for mode in BatchOptionMode::ALL {
            result[48 + mode as usize] = self.mode_batches[mode as usize] as f32 / 100.0;
        }
        result[52] = self.macro_env.state.water.len() as f32 / MACRO_CELLS as f32;
        result[53] = self.macro_env.state.walkable.len() as f32 / MACRO_CELLS as f32;
        result[54] = own_units.iter().map(|unit| unit.hp).sum::<i32>() as f32 / 12.0;
        result[55] = own_units.iter().map(|unit| unit.chop).sum::<i32>() as f32 / 12.0;
        assert!(result.iter().all(|value| value.is_finite()));
        result
    }

    fn unsafe_last_own_fell(
        observation: &MacroCandidateObservation,
        candidate: usize,
        own_live_plants: usize,
    ) -> bool {
        own_live_plants <= 1
            && observation.features[candidate][20 + 2] > 0.5
            && observation.features[candidate][30 + owner_index(PlantOwner::Own)] > 0.5
    }

    fn renewable_safe_action(
        &self,
        observation: &MacroCandidateObservation,
        mode: BatchOptionMode,
    ) -> usize {
        let teacher = observation.actions[observation.teacher_index] as usize;
        if observation.branch != MacroSelectionBranch::Rate {
            return teacher;
        }
        let own_live_plants = self.live_own_plants();
        let order = exact_prior_order(
            &observation.features,
            &observation.actions,
            observation.branch as u8,
        );
        let safe =
            |candidate: usize| !Self::unsafe_last_own_fell(observation, candidate, own_live_plants);
        let requested = mode.job_feature().and_then(|feature| {
            order.iter().copied().find(|candidate| {
                observation.features[*candidate][feature] > 0.5 && safe(*candidate)
            })
        });
        let selected = requested.unwrap_or_else(|| {
            order
                .iter()
                .copied()
                .find(|candidate| safe(*candidate))
                .expect("batch-option idle candidate is renewable-safe")
        });
        observation.actions[selected] as usize
    }

    fn step_internal(
        &mut self,
        mode_index: usize,
        opening_source: Option<usize>,
    ) -> (MacroTerminal, bool) {
        assert_eq!(self.macro_env.stage(), MacroDecisionStage::Train);
        assert!(mode_index < BATCH_OPTION_ACTIONS);
        if let Some(kind) = opening_source {
            assert!(kind < 4, "opening source kind outside fruit range");
            assert_eq!(
                self.opening_source_mask()[kind],
                1,
                "illegal opening source option"
            );
        } else {
            assert_eq!(self.legal_mask()[mode_index], 1, "illegal batch option");
        }
        let mode = BatchOptionMode::from_index(mode_index);
        self.last_mode = Some(mode);
        self.mode_batches[mode_index] = self.mode_batches[mode_index].saturating_add(1);

        let train_observation = self.macro_env.candidate_observation();
        assert_eq!(train_observation.branch, MacroSelectionBranch::Train);
        let train_action = if opening_source.is_some() {
            train_observation
                .actions
                .iter()
                .copied()
                .map(|action| action as usize)
                .find(|action| action / MACRO_CELLS == MacroTrainGoal::None.action_plane())
                .expect("opening source batch has no-TRAIN action")
        } else {
            train_observation.actions[train_observation.teacher_index] as usize
        };
        let mut terminal = self.macro_env.step(train_action);
        let mut rewards = [terminal.own_reward, terminal.opponent_reward];
        let mut margin_reward = terminal.margin_reward;
        let mut source_assigned = false;
        while !terminal.done && self.macro_env.stage() == MacroDecisionStage::Worker {
            terminal = if !source_assigned {
                if let Some(kind) = opening_source {
                    if let Some(result) = self.macro_env.step_opening_bank_seed_source_current(kind)
                    {
                        source_assigned = true;
                        result
                    } else {
                        let observation = self.macro_env.candidate_observation();
                        let action = self.renewable_safe_action(&observation, mode);
                        self.macro_env.step(action)
                    }
                } else {
                    let observation = self.macro_env.candidate_observation();
                    let action = self.renewable_safe_action(&observation, mode);
                    self.macro_env.step(action)
                }
            } else {
                let observation = self.macro_env.candidate_observation();
                let action = self.renewable_safe_action(&observation, mode);
                self.macro_env.step(action)
            };
            rewards[0] += terminal.own_reward;
            rewards[1] += terminal.opponent_reward;
            margin_reward += terminal.margin_reward;
        }
        assert!(terminal.done || self.macro_env.stage() == MacroDecisionStage::Train);
        terminal.own_reward = rewards[0];
        terminal.opponent_reward = rewards[1];
        terminal.margin_reward = margin_reward;
        (terminal, source_assigned)
    }

    pub fn step(&mut self, mode_index: usize) -> MacroTerminal {
        self.step_internal(mode_index, None).0
    }

    pub fn step_with_opening_source(&mut self, fruit_kind: usize) -> (MacroTerminal, bool) {
        self.step_internal(BatchOptionMode::Balanced as usize, Some(fruit_kind))
    }
}

struct BatchOptionSlot {
    task_index: u64,
    env: BatchOptionEnv,
}

#[repr(C)]
#[derive(Clone, Copy, Debug, Default)]
pub struct BatchOptionTerminal {
    pub done: u8,
    pub seat: u8,
    pub opponent: u8,
    pub own_workers: u8,
    pub map_seed: i64,
    pub task_index: u64,
    pub own_score: i32,
    pub opponent_score: i32,
    pub successful_trains: u8,
    pub _padding: u8,
    pub own_created_crops: u16,
    pub invalid_direct_commands: u16,
    pub provenance_failures: u16,
    pub deposit_prediction_failures: u16,
    pub invalidated_jobs: u16,
    pub action_hash: u64,
    pub state_hash: u64,
}

pub struct BatchOptionBatch {
    slots: Vec<BatchOptionSlot>,
    seed_base: i64,
    next_task_index: u64,
}

impl BatchOptionBatch {
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

    fn make_slot(seed_base: i64, task_index: u64) -> BatchOptionSlot {
        let (map_seed, seat, opponent) = Self::task(seed_base, task_index);
        BatchOptionSlot {
            task_index,
            env: BatchOptionEnv::new(map_seed, seat, MacroOpponentMode::from_index(opponent)),
        }
    }

    pub fn len(&self) -> usize {
        self.slots.len()
    }

    pub fn is_empty(&self) -> bool {
        self.slots.is_empty()
    }

    pub fn observe(&mut self, features: &mut [f32], masks: &mut [u8]) {
        assert_eq!(features.len(), self.len() * BATCH_OPTION_FEATURES);
        assert_eq!(masks.len(), self.len() * BATCH_OPTION_ACTIONS);
        self.slots
            .par_iter_mut()
            .zip(features.par_chunks_mut(BATCH_OPTION_FEATURES))
            .zip(masks.par_chunks_mut(BATCH_OPTION_ACTIONS))
            .for_each(|((slot, feature_chunk), mask_chunk)| {
                feature_chunk.copy_from_slice(&slot.env.features());
                mask_chunk.copy_from_slice(&slot.env.legal_mask());
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
            .map(|(slot, mode)| slot.env.step(*mode as usize))
            .collect();
        for (index, result) in results.into_iter().enumerate() {
            let slot = &mut self.slots[index];
            rewards[index] = result.margin_reward;
            if result.done {
                terminals[index] = BatchOptionTerminal {
                    done: 1,
                    seat: slot.env.macro_env.seat as u8,
                    opponent: slot.env.macro_env.opponent_mode.id(),
                    own_workers: result.own_workers,
                    map_seed: slot.env.macro_env.map_seed,
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
pub extern "C" fn tf_batch_option_features() -> usize {
    BATCH_OPTION_FEATURES
}

#[no_mangle]
pub extern "C" fn tf_batch_option_actions() -> usize {
    BATCH_OPTION_ACTIONS
}

#[no_mangle]
pub extern "C" fn tf_batch_option_terminal_size() -> usize {
    std::mem::size_of::<BatchOptionTerminal>()
}

#[no_mangle]
pub extern "C" fn tf_batch_option_create(num_envs: usize, seed_base: i64) -> *mut BatchOptionBatch {
    if num_envs == 0 || seed_base == 0 {
        return std::ptr::null_mut();
    }
    Box::into_raw(Box::new(BatchOptionBatch::new(num_envs, seed_base)))
}

#[no_mangle]
pub unsafe extern "C" fn tf_batch_option_destroy(handle: *mut BatchOptionBatch) {
    if !handle.is_null() {
        drop(Box::from_raw(handle));
    }
}

#[no_mangle]
pub unsafe extern "C" fn tf_batch_option_observe(
    handle: *mut BatchOptionBatch,
    features: *mut f32,
    masks: *mut u8,
) -> i32 {
    if handle.is_null() || features.is_null() || masks.is_null() {
        return -1;
    }
    let batch = &mut *handle;
    let feature_slice =
        std::slice::from_raw_parts_mut(features, batch.len() * BATCH_OPTION_FEATURES);
    let mask_slice = std::slice::from_raw_parts_mut(masks, batch.len() * BATCH_OPTION_ACTIONS);
    batch.observe(feature_slice, mask_slice);
    0
}

#[no_mangle]
pub unsafe extern "C" fn tf_batch_option_step(
    handle: *mut BatchOptionBatch,
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
    tf_batch_option_observe(handle, features, masks)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn initial_state_is_locked_and_finite() {
        let env = BatchOptionEnv::new(9_801_000, 0, MacroOpponentMode::Resident);
        assert_eq!(env.legal_mask(), [1, 0, 0, 0]);
        assert!(env.features().iter().all(|value| value.is_finite()));
    }

    #[test]
    fn constant_modes_match_corrected_d61_reference() {
        let expected = [
            // own, opponent, workers, crops, action hash, state hash
            (
                265,
                206,
                3,
                55,
                3_416_965_577_717_159_937,
                17_027_867_748_348_252_103,
            ),
            (
                119,
                172,
                3,
                5,
                13_013_393_439_420_392_713,
                12_502_044_954_707_265_778,
            ),
            (
                253,
                205,
                3,
                58,
                5_446_374_069_512_431_611,
                14_693_140_504_312_139_015,
            ),
            (
                129,
                132,
                3,
                5,
                16_337_996_767_651_694_930,
                8_332_985_751_291_164_089,
            ),
        ];
        for (mode, expected) in BatchOptionMode::ALL.into_iter().zip(expected) {
            let mut env = BatchOptionEnv::new(9_801_000, 0, MacroOpponentMode::Resident);
            let mut reward = 0.0f32;
            let terminal = loop {
                let selected = if env.legal_mask()[mode as usize] == 1 {
                    mode as usize
                } else {
                    BatchOptionMode::Balanced as usize
                };
                let result = env.step(selected);
                reward += result.margin_reward;
                if result.done {
                    break result;
                }
            };
            assert_eq!(terminal.own_score, expected.0);
            assert_eq!(terminal.opponent_score, expected.1);
            assert_eq!(terminal.own_workers, expected.2);
            assert_eq!(terminal.own_created_crops, expected.3);
            assert_eq!(terminal.action_hash, expected.4);
            assert_eq!(terminal.state_hash, expected.5);
            assert!((reward - terminal.margin_return).abs() < 1.0e-4);
        }
    }

    #[test]
    fn vector_batch_auto_resets_in_task_order() {
        let mut batch = BatchOptionBatch::new(2, 9_802_000);
        let mut features = vec![0.0; 2 * BATCH_OPTION_FEATURES];
        let mut masks = vec![0; 2 * BATCH_OPTION_ACTIONS];
        batch.observe(&mut features, &mut masks);
        assert_eq!(&masks[..BATCH_OPTION_ACTIONS], &[1, 0, 0, 0]);
        let mut terminals = vec![BatchOptionTerminal::default(); 2];
        let mut rewards = vec![0.0; 2];
        for _ in 0..200 {
            batch.step(&[0, 0], &mut rewards, &mut terminals);
            if terminals.iter().any(|terminal| terminal.done != 0) {
                assert!(terminals
                    .iter()
                    .filter(|terminal| terminal.done != 0)
                    .all(|terminal| terminal.task_index < 2));
                return;
            }
        }
        panic!("batch-option vector environment did not finish an episode");
    }
}
