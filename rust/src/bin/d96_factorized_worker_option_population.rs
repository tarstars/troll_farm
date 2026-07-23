//! Evaluate the frozen D96 matched global/factorized worker-option population.

use std::collections::{BTreeMap, BTreeSet};
use std::fs::{File, OpenOptions};
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

use troll_farm::d41b_prior_kernel::exact_prior_order;
use troll_farm::rl_macro::{
    CompleteMacroEnv, MacroCandidateObservation, MacroDecisionStage, MacroOpponentMode,
    MacroSelectionBranch, MacroTerminal, PlantOwner, MACRO_ACTION_PLANES, MACRO_CELLS,
    MACRO_TOTAL_TURNS,
};

const GLOBAL_FEATURES: usize = 56;
const WORKER_FEATURES: usize = 53;
const MODES: usize = 4;
const GLOBAL_PARAMETERS: usize = GLOBAL_FEATURES * MODES;
const WORKER_PARAMETERS: usize = WORKER_FEATURES * MODES;
const ORDINALS: usize = 3;

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
#[repr(usize)]
enum Mode {
    Balanced = 0,
    Harvest = 1,
    Renew = 2,
    Fell = 3,
}

impl Mode {
    const ALL: [Self; MODES] = [Self::Balanced, Self::Harvest, Self::Renew, Self::Fell];

    fn label(self) -> &'static str {
        match self {
            Self::Balanced => "balanced",
            Self::Harvest => "harvest",
            Self::Renew => "renew",
            Self::Fell => "fell",
        }
    }

    fn job_feature(self) -> Option<usize> {
        match self {
            Self::Balanced => None,
            // MacroJobKind order: idle, bank, fell, harvest, renew, mine.
            Self::Harvest => Some(20 + 3),
            Self::Renew => Some(20 + 4),
            Self::Fell => Some(20 + 2),
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum PolicyKind {
    Control,
    Constant(Mode),
    GlobalLinear,
    FactorZero,
    FactorRandom,
}

impl PolicyKind {
    fn label(self) -> &'static str {
        match self {
            Self::Control => "control",
            Self::Constant(mode) => mode.label(),
            Self::GlobalLinear => "linear",
            Self::FactorZero => "factor_zero",
            Self::FactorRandom => "factor_random",
        }
    }

    fn is_factor(self) -> bool {
        matches!(self, Self::FactorZero | Self::FactorRandom)
    }
}

#[derive(Clone, Debug)]
struct Policy {
    label: String,
    kind: PolicyKind,
    base_label: String,
    global: [f32; GLOBAL_PARAMETERS],
    worker: [f32; WORKER_PARAMETERS],
}

fn parse<T: std::str::FromStr>(value: &str, label: &str) -> T {
    value
        .parse()
        .unwrap_or_else(|_| panic!("invalid {label}: {value:?}"))
}

fn expected_header(prefix: &[&str], parameters: usize) -> String {
    prefix
        .iter()
        .map(|value| value.to_string())
        .chain((0..parameters).map(|index| format!("param_{index:03}")))
        .collect::<Vec<_>>()
        .join("\t")
}

fn read_global_policies(path: &str) -> Vec<Policy> {
    let source = BufReader::new(File::open(path).expect("open D61 population"));
    let mut lines = source.lines();
    assert_eq!(
        lines.next().expect("D61 population header").unwrap(),
        expected_header(&["policy", "kind"], GLOBAL_PARAMETERS)
    );
    let mut policies = Vec::new();
    for line in lines {
        let line = line.expect("read D61 population row");
        let fields: Vec<_> = line.split('\t').collect();
        assert_eq!(fields.len(), GLOBAL_PARAMETERS + 2);
        let kind = match fields[1] {
            "control" => PolicyKind::Control,
            "balanced" => PolicyKind::Constant(Mode::Balanced),
            "harvest" => PolicyKind::Constant(Mode::Harvest),
            "renew" => PolicyKind::Constant(Mode::Renew),
            "fell" => PolicyKind::Constant(Mode::Fell),
            "linear" => PolicyKind::GlobalLinear,
            other => panic!("unknown D61 policy kind: {other}"),
        };
        let mut global = [0.0f32; GLOBAL_PARAMETERS];
        for (target, value) in global.iter_mut().zip(&fields[2..]) {
            *target = parse(value, "D61 weight");
            assert!(target.is_finite());
        }
        if kind != PolicyKind::GlobalLinear {
            assert!(global.iter().all(|value| *value == 0.0));
        }
        policies.push(Policy {
            label: fields[0].to_string(),
            kind,
            base_label: fields[0].to_string(),
            global,
            worker: [0.0; WORKER_PARAMETERS],
        });
    }
    assert_eq!(policies.len(), 69, "D61 policy-count contract");
    policies
}

fn append_factor_policies(policies: &mut Vec<Policy>, path: &str) {
    let bases: BTreeMap<_, _> = policies
        .iter()
        .filter(|policy| policy.kind == PolicyKind::GlobalLinear)
        .map(|policy| (policy.label.clone(), policy.global))
        .collect();
    assert_eq!(bases.len(), 64);
    let source = BufReader::new(File::open(path).expect("open D96 population"));
    let mut lines = source.lines();
    assert_eq!(
        lines.next().expect("D96 population header").unwrap(),
        expected_header(&["policy", "kind", "base"], WORKER_PARAMETERS)
    );
    let mut factors = Vec::new();
    for line in lines {
        let line = line.expect("read D96 population row");
        let fields: Vec<_> = line.split('\t').collect();
        assert_eq!(fields.len(), WORKER_PARAMETERS + 3);
        let kind = match fields[1] {
            "factor_zero" => PolicyKind::FactorZero,
            "factor_random" => PolicyKind::FactorRandom,
            other => panic!("unknown D96 policy kind: {other}"),
        };
        let mut worker = [0.0f32; WORKER_PARAMETERS];
        for (target, value) in worker.iter_mut().zip(&fields[3..]) {
            *target = parse(value, "D96 residual weight");
            assert!(target.is_finite());
        }
        if kind == PolicyKind::FactorZero {
            assert!(worker.iter().all(|value| *value == 0.0));
        }
        factors.push(Policy {
            label: fields[0].to_string(),
            kind,
            base_label: fields[2].to_string(),
            global: *bases.get(fields[2]).expect("known D96 base policy"),
            worker,
        });
    }
    assert_eq!(factors.len(), 128, "D96 factor-policy count");
    policies.extend(factors);
    assert_eq!(policies.len(), 197, "D96 complete policy count");
    assert_eq!(
        policies
            .iter()
            .map(|policy| policy.label.as_str())
            .collect::<BTreeSet<_>>()
            .len(),
        policies.len(),
        "duplicate D96 policy label"
    );
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
    opponent: usize,
}

struct Work {
    policy: usize,
    task: Task,
}

#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
struct OptionStats {
    batches: u32,
    locked_batches: u32,
    mode_batches: [u32; MODES],
    mode_switches: u32,
    safe_fell_rejections: u32,
    semantic_eligible: u32,
    semantic_overrides: u32,
    feature_evaluations: u32,
    option_hash: u64,
    worker_feature_evaluations: u32,
    worker_mode_switches: u32,
    multi_rate_batches: u32,
    mixed_rate_batches: u32,
    ordinal_modes: [[u32; MODES]; ORDINALS],
    worker_option_hash: u64,
}

struct Row {
    policy: usize,
    task: Task,
    terminal: MacroTerminal,
    reward_identity_error: f32,
    options: OptionStats,
    terminal_live_own_plants: usize,
    action_planes: [u32; MACRO_ACTION_PLANES],
}

fn owner_index(owner: PlantOwner) -> usize {
    match owner {
        PlantOwner::Natural => 0,
        PlantOwner::Own => 1,
        PlantOwner::Opponent => 2,
        PlantOwner::Ambiguous => 3,
    }
}

fn live_own_plants(env: &CompleteMacroEnv) -> usize {
    env.state
        .plants
        .iter()
        .filter(|plant| plant.health > 0)
        .filter(|plant| env.owners().get(&plant.pos()) == Some(&PlantOwner::Own))
        .count()
}

fn batch_features(
    env: &CompleteMacroEnv,
    last_mode: Option<Mode>,
    mode_batches: [u32; MODES],
) -> [f32; GLOBAL_FEATURES] {
    let own = env.seat;
    let opponent = 1 - own;
    let own_units: Vec<_> = env
        .state
        .units
        .iter()
        .filter(|unit| unit.player as usize == own)
        .collect();
    let opponent_units: Vec<_> = env
        .state
        .units
        .iter()
        .filter(|unit| unit.player as usize == opponent)
        .collect();
    let mut result = [0.0f32; GLOBAL_FEATURES];
    result[0] = 1.0;
    result[1] = env.state.turn as f32 / MACRO_TOTAL_TURNS as f32;
    result[2] = own_units.len() as f32 / 3.0;
    result[3] = opponent_units.len() as f32 / 3.0;
    result[4] = env.state.scores[own] as f32 / 400.0;
    result[5] = env.state.scores[opponent] as f32 / 400.0;
    result[6] = (env.state.scores[own] - env.state.scores[opponent]) as f32 / 400.0;
    for item in 0..6 {
        result[7 + item] = env.state.inventories[own][item] as f32 / 20.0;
        result[13 + item] = env.state.inventories[opponent][item] as f32 / 20.0;
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
    for plant in env.state.plants.iter().filter(|plant| plant.health > 0) {
        let index = owner_index(*env.owners().get(&plant.pos()).expect("D96 provenance"));
        plant_counts[index] += 1;
        fruit_counts[index] = fruit_counts[index].saturating_add(plant.fruits);
    }
    for index in 0..4 {
        result[31 + index] = plant_counts[index] as f32 / 20.0;
        result[35 + index] = fruit_counts[index] as f32 / 40.0;
    }
    result[39] = f32::from(plant_counts[owner_index(PlantOwner::Own)] > 0);
    result[40] = f32::from(plant_counts[owner_index(PlantOwner::Opponent)] > 0);
    result[41 + env.train_goal().action_plane()] = 1.0;
    if let Some(mode) = last_mode {
        result[44 + mode as usize] = 1.0;
    }
    for mode in Mode::ALL {
        result[48 + mode as usize] = mode_batches[mode as usize] as f32 / 100.0;
    }
    result[52] = env.state.water.len() as f32 / MACRO_CELLS as f32;
    result[53] = env.state.walkable.len() as f32 / MACRO_CELLS as f32;
    result[54] = own_units.iter().map(|unit| unit.hp).sum::<i32>() as f32 / 12.0;
    result[55] = own_units.iter().map(|unit| unit.chop).sum::<i32>() as f32 / 12.0;
    assert!(result.iter().all(|value| value.is_finite()));
    result
}

fn worker_ordinal(env: &CompleteMacroEnv, unit_id: i32) -> usize {
    let mut ids: Vec<_> = env
        .state
        .units
        .iter()
        .filter(|unit| unit.player as usize == env.seat)
        .map(|unit| unit.id)
        .collect();
    ids.sort_unstable();
    ids.iter()
        .position(|id| *id == unit_id)
        .expect("current D96 worker ordinal")
}

fn worker_features(
    env: &CompleteMacroEnv,
    previous: &BTreeMap<i32, Mode>,
) -> ([f32; WORKER_FEATURES], usize, i32) {
    let unit_id = env.current_unit_id().expect("D96 worker-stage unit");
    let ordinal = worker_ordinal(env, unit_id);
    assert!(ordinal < ORDINALS);
    let shared = env.d42_shared_context();
    let mut result = [0.0f32; WORKER_FEATURES];
    result[..46].copy_from_slice(&shared);
    result[46 + ordinal] = 1.0;
    if let Some(mode) = previous.get(&unit_id) {
        result[49 + *mode as usize] = 1.0;
    }
    assert!(result.iter().all(|value| value.is_finite()));
    (result, ordinal, unit_id)
}

fn dot(weights: &[f32], features: &[f32]) -> f32 {
    weights
        .iter()
        .zip(features)
        .map(|(weight, feature)| weight * feature)
        .sum()
}

fn global_mode(weights: &[f32; GLOBAL_PARAMETERS], features: &[f32; GLOBAL_FEATURES]) -> Mode {
    let mut best = Mode::Balanced;
    let mut best_score = f32::NEG_INFINITY;
    for mode in Mode::ALL {
        let offset = mode as usize * GLOBAL_FEATURES;
        let score = dot(&weights[offset..offset + GLOBAL_FEATURES], features);
        assert!(score.is_finite());
        if score.total_cmp(&best_score).is_gt() {
            best = mode;
            best_score = score;
        }
    }
    best
}

fn factor_mode(
    policy: &Policy,
    global: &[f32; GLOBAL_FEATURES],
    worker: &[f32; WORKER_FEATURES],
) -> Mode {
    let mut best = Mode::Balanced;
    let mut best_score = f32::NEG_INFINITY;
    for mode in Mode::ALL {
        let global_offset = mode as usize * GLOBAL_FEATURES;
        let worker_offset = mode as usize * WORKER_FEATURES;
        let score = dot(
            &policy.global[global_offset..global_offset + GLOBAL_FEATURES],
            global,
        ) + dot(
            &policy.worker[worker_offset..worker_offset + WORKER_FEATURES],
            worker,
        );
        assert!(score.is_finite());
        if score.total_cmp(&best_score).is_gt() {
            best = mode;
            best_score = score;
        }
    }
    best
}

fn policy_base_mode(policy: &Policy, features: &[f32; GLOBAL_FEATURES]) -> Mode {
    match policy.kind {
        PolicyKind::Control | PolicyKind::Constant(Mode::Balanced) => Mode::Balanced,
        PolicyKind::Constant(mode) => mode,
        PolicyKind::GlobalLinear | PolicyKind::FactorZero | PolicyKind::FactorRandom => {
            global_mode(&policy.global, features)
        }
    }
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
    observation: &MacroCandidateObservation,
    mode: Mode,
    own_live_plants: usize,
) -> (usize, bool, bool, u32) {
    let teacher = observation.actions[observation.teacher_index] as usize;
    if observation.branch != MacroSelectionBranch::Rate {
        return (teacher, false, false, 0);
    }
    let order = exact_prior_order(
        &observation.features,
        &observation.actions,
        observation.branch as u8,
    );
    let mut rejected = 0u32;
    let mut safe = |candidate: usize| {
        let unsafe_fell = unsafe_last_own_fell(observation, candidate, own_live_plants);
        rejected += u32::from(unsafe_fell);
        !unsafe_fell
    };
    let requested = mode.job_feature().and_then(|feature| {
        order
            .iter()
            .copied()
            .find(|candidate| observation.features[*candidate][feature] > 0.5 && safe(*candidate))
    });
    let selected = requested.unwrap_or_else(|| {
        order
            .iter()
            .copied()
            .find(|candidate| safe(*candidate))
            .expect("D96 idle candidate is renewable-safe")
    });
    let action = observation.actions[selected] as usize;
    (action, requested.is_some(), action != teacher, rejected)
}

fn mix_hash(hash: &mut u64, value: u64) {
    for byte in value.to_le_bytes() {
        *hash ^= u64::from(byte);
        *hash = hash.wrapping_mul(0x100000001b3);
    }
}

fn finish_batch(options: &mut OptionStats, rate_count: u32, rate_mask: u8) {
    if rate_count >= 2 {
        options.multi_rate_batches = options.multi_rate_batches.saturating_add(1);
        options.mixed_rate_batches = options
            .mixed_rate_batches
            .saturating_add(u32::from(rate_mask.count_ones() >= 2));
    }
}

fn play(task: Task, policy_index: usize, policy: &Policy) -> Row {
    let mut env = CompleteMacroEnv::new(
        task.map_seed,
        task.seat,
        MacroOpponentMode::from_index(task.opponent),
    );
    let mut terminal = MacroTerminal::default();
    let mut options = OptionStats {
        option_hash: 0xcbf29ce484222325,
        worker_option_hash: 0xcbf29ce484222325,
        ..OptionStats::default()
    };
    let mut base_mode = Mode::Balanced;
    let mut last_base_mode = None;
    let mut global = [0.0f32; GLOBAL_FEATURES];
    let mut batch_locked = false;
    let mut previous_worker_modes = BTreeMap::new();
    let mut rate_count = 0u32;
    let mut rate_mask = 0u8;
    let mut batch_open = false;
    let mut action_planes = [0u32; MACRO_ACTION_PLANES];
    let mut decisions = 0usize;
    let mut last_turn = env.state.turn;
    let mut stagnant = 0usize;
    while !terminal.done {
        decisions += 1;
        assert!(decisions <= 5_000, "D96 decision loop on {task:?}");
        let observation = env.candidate_observation();
        if env.stage() == MacroDecisionStage::Train {
            if batch_open {
                finish_batch(&mut options, rate_count, rate_mask);
            }
            rate_count = 0;
            rate_mask = 0;
            batch_open = true;
            global = batch_features(&env, last_base_mode, options.mode_batches);
            options.feature_evaluations = options.feature_evaluations.saturating_add(1);
            batch_locked = policy.kind != PolicyKind::Control && live_own_plants(&env) == 0;
            base_mode = if batch_locked {
                Mode::Balanced
            } else {
                policy_base_mode(policy, &global)
            };
            options.batches = options.batches.saturating_add(1);
            options.locked_batches = options
                .locked_batches
                .saturating_add(u32::from(batch_locked));
            options.mode_batches[base_mode as usize] =
                options.mode_batches[base_mode as usize].saturating_add(1);
            options.mode_switches = options.mode_switches.saturating_add(u32::from(
                last_base_mode.is_some_and(|previous| previous != base_mode),
            ));
            mix_hash(&mut options.option_hash, options.batches as u64);
            mix_hash(&mut options.option_hash, env.state.turn as u64);
            mix_hash(&mut options.option_hash, base_mode as u64);
            last_base_mode = Some(base_mode);
        }

        let exact_balanced_anchor = matches!(
            policy.kind,
            PolicyKind::Control | PolicyKind::Constant(Mode::Balanced)
        );
        let action = if exact_balanced_anchor {
            observation.actions[observation.teacher_index] as usize
        } else {
            let mut selected_mode = base_mode;
            let mut worker_identity = None;
            if env.stage() == MacroDecisionStage::Worker {
                let (worker, ordinal, unit_id) = worker_features(&env, &previous_worker_modes);
                options.worker_feature_evaluations =
                    options.worker_feature_evaluations.saturating_add(1);
                if policy.kind.is_factor() && !batch_locked {
                    selected_mode = factor_mode(policy, &global, &worker);
                }
                options.ordinal_modes[ordinal][selected_mode as usize] =
                    options.ordinal_modes[ordinal][selected_mode as usize].saturating_add(1);
                worker_identity = Some((ordinal, unit_id));
            }
            let (action, eligible, overridden, rejected) =
                renewable_safe_action(&observation, selected_mode, live_own_plants(&env));
            options.semantic_eligible = options
                .semantic_eligible
                .saturating_add(u32::from(eligible));
            options.semantic_overrides = options
                .semantic_overrides
                .saturating_add(u32::from(overridden));
            options.safe_fell_rejections = options.safe_fell_rejections.saturating_add(rejected);
            if observation.branch == MacroSelectionBranch::Rate {
                if let Some((ordinal, unit_id)) = worker_identity {
                    options.worker_mode_switches =
                        options.worker_mode_switches.saturating_add(u32::from(
                            previous_worker_modes
                                .get(&unit_id)
                                .is_some_and(|previous| *previous != selected_mode),
                        ));
                    previous_worker_modes.insert(unit_id, selected_mode);
                    rate_count = rate_count.saturating_add(1);
                    rate_mask |= 1 << selected_mode as usize;
                    mix_hash(&mut options.worker_option_hash, env.state.turn as u64);
                    mix_hash(&mut options.worker_option_hash, ordinal as u64);
                    mix_hash(&mut options.worker_option_hash, unit_id as u64);
                    mix_hash(&mut options.worker_option_hash, selected_mode as u64);
                    mix_hash(&mut options.worker_option_hash, action as u64);
                }
            }
            action
        };
        assert!(
            env.legal_actions().contains(&action),
            "D96 chose illegal action on {task:?}"
        );
        action_planes[action / MACRO_CELLS] += 1;
        terminal = env.step(action);
        if env.state.turn == last_turn {
            stagnant += 1;
        } else {
            last_turn = env.state.turn;
            stagnant = 0;
        }
        assert!(stagnant <= 16, "D96 zero-time loop on {task:?}");
    }
    if batch_open {
        finish_batch(&mut options, rate_count, rate_mask);
    }
    let reward_identity_error = [
        (terminal.own_return - terminal.own_score as f32 / 100.0).abs(),
        (terminal.opponent_return - terminal.opponent_score as f32 / 100.0).abs(),
        (terminal.margin_return - (terminal.own_score - terminal.opponent_score) as f32 / 100.0)
            .abs(),
    ]
    .into_iter()
    .fold(0.0f32, f32::max);
    Row {
        policy: policy_index,
        task,
        terminal,
        reward_identity_error,
        options,
        terminal_live_own_plants: live_own_plants(&env),
        action_planes,
    }
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(
        args.len(),
        7,
        "usage: d96_factorized_worker_option_population D61_POP D96_POP START_SEED MAPS OUTPUT THREADS"
    );
    let mut policy_rows = read_global_policies(&args[1]);
    append_factor_policies(&mut policy_rows, &args[2]);
    let policies = Arc::new(policy_rows);
    let start_seed = parse(&args[3], "start seed");
    let maps: usize = parse(&args[4], "maps");
    let output = &args[5];
    let threads: usize = parse(&args[6], "threads");
    assert!(maps > 0 && threads > 0);
    let work: Vec<_> = (0..policies.len())
        .flat_map(|policy| {
            (start_seed..start_seed + maps as i64).flat_map(move |map_seed| {
                (0..2).flat_map(move |seat| {
                    (0..MacroOpponentMode::ALL.len()).map(move |opponent| Work {
                        policy,
                        task: Task {
                            map_seed,
                            seat,
                            opponent,
                        },
                    })
                })
            })
        })
        .collect();
    let work = Arc::new(work);
    let next = Arc::new(AtomicUsize::new(0));
    let rows = Arc::new(Mutex::new(Vec::with_capacity(work.len())));
    let started = Instant::now();
    let handles: Vec<_> = (0..threads.min(work.len()))
        .map(|_| {
            let policies = Arc::clone(&policies);
            let work = Arc::clone(&work);
            let next = Arc::clone(&next);
            let rows = Arc::clone(&rows);
            thread::spawn(move || loop {
                let index = next.fetch_add(1, Ordering::Relaxed);
                let Some(item) = work.get(index) else {
                    break;
                };
                let row = play(item.task, item.policy, &policies[item.policy]);
                rows.lock().expect("D96 row lock").push(row);
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D96 worker thread");
    }
    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole D96 row owner")
        .into_inner()
        .expect("D96 row lock");
    rows.sort_by_key(|row| {
        (
            policies[row.policy].label.clone(),
            row.task.map_seed,
            row.task.seat,
            row.task.opponent,
        )
    });

    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(output)
        .expect("create D96 output without overwrite");
    let mut writer = BufWriter::new(target);
    writeln!(writer, "map_seed\tseat\topponent\tpolicy\tkind\tbase_policy\tturn\town_score\topponent_score\tmargin\town_return\topponent_return\tmargin_return\treward_identity_error\town_workers\topponent_workers\tsuccessful_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tdeposit_prediction_failures\tselected_decisions\tselected_jobs\tselected_nonidle_jobs\tselected_renew_jobs\town_created_crops\topponent_created_crops\tambiguous_created_crops\taction_hash\tstate_hash\toption_batches\tlocked_batches\tbalanced_batches\tharvest_batches\trenew_batches\tfell_batches\tmode_switches\tsafe_fell_rejections\tsemantic_eligible\tsemantic_overrides\tfeature_evaluations\toption_hash\tterminal_live_own_plants\ttrain_none\ttrain_producer\ttrain_chopper\tidle\tbank\tfell_bank\tharvest_bank\trenew\tmine_bank\tworker_feature_evaluations\tworker_mode_switches\tmulti_rate_batches\tmixed_rate_batches\tworker_option_hash\to0_balanced\to0_harvest\to0_renew\to0_fell\to1_balanced\to1_harvest\to1_renew\to1_fell\to2_balanced\to2_harvest\to2_renew\to2_fell").expect("write D96 header");
    for row in &rows {
        let policy = &policies[row.policy];
        let terminal = row.terminal;
        writeln!(
            writer,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{:.8}\t{:.8}\t{:.8}\t{:.8}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
            row.task.map_seed,
            row.task.seat,
            MacroOpponentMode::from_index(row.task.opponent).label(),
            policy.label,
            policy.kind.label(),
            policy.base_label,
            terminal.turn,
            terminal.own_score,
            terminal.opponent_score,
            terminal.own_score - terminal.opponent_score,
            terminal.own_return,
            terminal.opponent_return,
            terminal.margin_return,
            row.reward_identity_error,
            terminal.own_workers,
            terminal.opponent_workers,
            terminal.successful_trains,
            terminal.completed_jobs,
            terminal.invalidated_jobs,
            terminal.invalid_direct_commands,
            terminal.provenance_failures,
            terminal.deposit_prediction_failures,
            terminal.selected_decisions,
            terminal.selected_jobs,
            terminal.selected_nonidle_jobs,
            terminal.selected_renew_jobs,
            terminal.own_created_crops,
            terminal.opponent_created_crops,
            terminal.ambiguous_created_crops,
            terminal.action_hash,
            terminal.state_hash,
            row.options.batches,
            row.options.locked_batches,
            row.options.mode_batches[Mode::Balanced as usize],
            row.options.mode_batches[Mode::Harvest as usize],
            row.options.mode_batches[Mode::Renew as usize],
            row.options.mode_batches[Mode::Fell as usize],
            row.options.mode_switches,
            row.options.safe_fell_rejections,
            row.options.semantic_eligible,
            row.options.semantic_overrides,
            row.options.feature_evaluations,
            row.options.option_hash,
            row.terminal_live_own_plants,
            row.action_planes[0],
            row.action_planes[1],
            row.action_planes[2],
            row.action_planes[3],
            row.action_planes[4],
            row.action_planes[5],
            row.action_planes[6],
            row.action_planes[7],
            row.action_planes[8],
            row.options.worker_feature_evaluations,
            row.options.worker_mode_switches,
            row.options.multi_rate_batches,
            row.options.mixed_rate_batches,
            row.options.worker_option_hash,
            row.options.ordinal_modes[0][0],
            row.options.ordinal_modes[0][1],
            row.options.ordinal_modes[0][2],
            row.options.ordinal_modes[0][3],
            row.options.ordinal_modes[1][0],
            row.options.ordinal_modes[1][1],
            row.options.ordinal_modes[1][2],
            row.options.ordinal_modes[1][3],
            row.options.ordinal_modes[2][0],
            row.options.ordinal_modes[2][1],
            row.options.ordinal_modes[2][2],
            row.options.ordinal_modes[2][3],
        )
        .expect("write D96 row");
    }
    writer.flush().expect("flush D96 output");
    eprintln!(
        "saved {} policies x {} maps x 16 tasks = {} rows in {:.3}s",
        policies.len(),
        maps,
        rows.len(),
        started.elapsed().as_secs_f64(),
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    fn linear_policy(kind: PolicyKind, worker: [f32; WORKER_PARAMETERS]) -> Policy {
        let mut global = [0.0; GLOBAL_PARAMETERS];
        global[GLOBAL_FEATURES] = 0.25;
        Policy {
            label: "test".to_string(),
            kind,
            base_label: "test".to_string(),
            global,
            worker,
        }
    }

    #[test]
    fn zero_worker_residual_preserves_global_mode() {
        let policy = linear_policy(PolicyKind::FactorZero, [0.0; WORKER_PARAMETERS]);
        let mut global = [0.0; GLOBAL_FEATURES];
        global[0] = 1.0;
        let worker = [0.5; WORKER_FEATURES];
        assert_eq!(global_mode(&policy.global, &global), Mode::Harvest);
        assert_eq!(factor_mode(&policy, &global, &worker), Mode::Harvest);
    }

    #[test]
    fn worker_features_are_finite_and_identify_ordinal() {
        let mut env = CompleteMacroEnv::new(9_801_000, 0, MacroOpponentMode::Resident);
        let train = env.candidate_observation();
        env.step(train.actions[train.teacher_index] as usize);
        assert_eq!(env.stage(), MacroDecisionStage::Worker);
        let (features, ordinal, _) = worker_features(&env, &BTreeMap::new());
        assert!(features.iter().all(|value| value.is_finite()));
        assert_eq!(features[46 + ordinal], 1.0);
        assert_eq!(features[46..49].iter().sum::<f32>(), 1.0);
    }

    #[test]
    fn zero_residual_episode_matches_global_parent() {
        let task = Task {
            map_seed: 9_801_000,
            seat: 1,
            opponent: 3,
        };
        let global = linear_policy(PolicyKind::GlobalLinear, [0.0; WORKER_PARAMETERS]);
        let factor = linear_policy(PolicyKind::FactorZero, [0.0; WORKER_PARAMETERS]);
        let left = play(task, 0, &global);
        let right = play(task, 1, &factor);
        assert_eq!(left.terminal, right.terminal);
        assert_eq!(left.action_planes, right.action_planes);
        assert_eq!(left.options.batches, right.options.batches);
        assert_eq!(left.options.mode_batches, right.options.mode_batches);
        assert_eq!(left.options.option_hash, right.options.option_hash);
    }
}
