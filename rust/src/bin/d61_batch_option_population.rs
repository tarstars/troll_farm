//! Evaluate the frozen D61 renewable-safe state-conditioned batch-option population.

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

const FEATURES: usize = 56;
const MODES: usize = 4;
const PARAMETERS: usize = FEATURES * MODES;

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
    Linear,
}

#[derive(Clone, Debug)]
struct Policy {
    label: String,
    kind: PolicyKind,
    theta: [f32; PARAMETERS],
}

fn parse<T: std::str::FromStr>(value: &str, label: &str) -> T {
    value
        .parse()
        .unwrap_or_else(|_| panic!("invalid {label}: {value:?}"))
}

fn read_policies(path: &str) -> Vec<Policy> {
    let source = BufReader::new(File::open(path).expect("open D61 policy population"));
    let mut lines = source.lines();
    let expected = std::iter::once("policy".to_string())
        .chain(std::iter::once("kind".to_string()))
        .chain((0..PARAMETERS).map(|index| format!("param_{index:03}")))
        .collect::<Vec<_>>()
        .join("\t");
    assert_eq!(
        lines.next().expect("D61 population header").unwrap(),
        expected
    );
    let mut policies = Vec::new();
    for line in lines {
        let line = line.expect("read D61 population row");
        let fields: Vec<_> = line.split('\t').collect();
        assert_eq!(fields.len(), PARAMETERS + 2);
        let kind = match fields[1] {
            "control" => PolicyKind::Control,
            "balanced" => PolicyKind::Constant(Mode::Balanced),
            "harvest" => PolicyKind::Constant(Mode::Harvest),
            "renew" => PolicyKind::Constant(Mode::Renew),
            "fell" => PolicyKind::Constant(Mode::Fell),
            "linear" => PolicyKind::Linear,
            other => panic!("unknown D61 policy kind: {other}"),
        };
        let mut theta = [0.0f32; PARAMETERS];
        for (target, value) in theta.iter_mut().zip(&fields[2..]) {
            *target = parse(value, "D61 population parameter");
            assert!(target.is_finite());
        }
        if kind != PolicyKind::Linear {
            assert!(theta.iter().all(|value| *value == 0.0));
        }
        policies.push(Policy {
            label: fields[0].to_string(),
            kind,
            theta,
        });
    }
    assert_eq!(policies.len(), 69, "D61 policy-count contract");
    let labels: std::collections::BTreeSet<_> = policies
        .iter()
        .map(|policy| policy.label.as_str())
        .collect();
    assert_eq!(labels.len(), policies.len(), "duplicate D61 policy label");
    assert_eq!(
        policies
            .iter()
            .filter(|policy| policy.kind == PolicyKind::Control)
            .count(),
        1
    );
    assert_eq!(
        policies
            .iter()
            .filter(|policy| policy.kind == PolicyKind::Linear)
            .count(),
        64
    );
    policies
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

#[derive(Clone, Copy, Debug, Default)]
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
) -> [f32; FEATURES] {
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
    let mut result = [0.0f32; FEATURES];
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
        let owner = *env
            .owners()
            .get(&plant.pos())
            .expect("D61 live plant provenance");
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

fn linear_mode(theta: &[f32; PARAMETERS], features: &[f32; FEATURES]) -> Mode {
    let mut best = Mode::Balanced;
    let mut best_score = f32::NEG_INFINITY;
    for mode in Mode::ALL {
        let offset = mode as usize * FEATURES;
        let score = theta[offset..offset + FEATURES]
            .iter()
            .zip(features)
            .map(|(weight, feature)| weight * feature)
            .sum::<f32>();
        assert!(score.is_finite());
        if score.total_cmp(&best_score).is_gt() {
            best = mode;
            best_score = score;
        }
    }
    best
}

fn policy_mode(policy: &Policy, features: &[f32; FEATURES]) -> Mode {
    match policy.kind {
        PolicyKind::Control | PolicyKind::Constant(Mode::Balanced) => Mode::Balanced,
        PolicyKind::Constant(mode) => mode,
        PolicyKind::Linear => linear_mode(&policy.theta, features),
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
    let selected = if let Some(candidate) = requested {
        candidate
    } else {
        order
            .iter()
            .copied()
            .find(|candidate| safe(*candidate))
            .expect("D61 idle candidate is renewable-safe")
    };
    let action = observation.actions[selected] as usize;
    (action, requested.is_some(), action != teacher, rejected)
}

fn mix_option_hash(hash: &mut u64, value: u64) {
    for byte in value.to_le_bytes() {
        *hash ^= u64::from(byte);
        *hash = hash.wrapping_mul(0x100000001b3);
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
        ..OptionStats::default()
    };
    let mut current_mode = Mode::Balanced;
    let mut last_mode = None;
    let mut action_planes = [0u32; MACRO_ACTION_PLANES];
    let mut decisions = 0usize;
    let mut last_turn = env.state.turn;
    let mut stagnant = 0usize;
    while !terminal.done {
        decisions += 1;
        assert!(decisions <= 5_000, "D61 decision loop on {task:?}");
        let observation = env.candidate_observation();
        if env.stage() == MacroDecisionStage::Train {
            let features = batch_features(&env, last_mode, options.mode_batches);
            options.feature_evaluations += 1;
            let locked = policy.kind != PolicyKind::Control && live_own_plants(&env) == 0;
            current_mode = if locked {
                Mode::Balanced
            } else {
                policy_mode(policy, &features)
            };
            options.batches += 1;
            options.locked_batches += u32::from(locked);
            options.mode_batches[current_mode as usize] += 1;
            options.mode_switches +=
                u32::from(last_mode.is_some_and(|previous| previous != current_mode));
            mix_option_hash(&mut options.option_hash, options.batches as u64);
            mix_option_hash(&mut options.option_hash, env.state.turn as u64);
            mix_option_hash(&mut options.option_hash, current_mode as u64);
            last_mode = Some(current_mode);
        }
        let exact_balanced_anchor = matches!(
            policy.kind,
            PolicyKind::Control | PolicyKind::Constant(Mode::Balanced)
        );
        let action = if exact_balanced_anchor {
            observation.actions[observation.teacher_index] as usize
        } else {
            let (action, eligible, overridden, rejected) =
                renewable_safe_action(&observation, current_mode, live_own_plants(&env));
            options.semantic_eligible += u32::from(eligible);
            options.semantic_overrides += u32::from(overridden);
            options.safe_fell_rejections += rejected;
            action
        };
        assert!(
            env.legal_actions().contains(&action),
            "D61 chose illegal action on {task:?}"
        );
        action_planes[action / MACRO_CELLS] += 1;
        terminal = env.step(action);
        if env.state.turn == last_turn {
            stagnant += 1;
        } else {
            last_turn = env.state.turn;
            stagnant = 0;
        }
        assert!(stagnant <= 16, "D61 zero-time loop on {task:?}");
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
        6,
        "usage: d61_batch_option_population POPULATION START_SEED MAPS OUTPUT THREADS"
    );
    let policies = Arc::new(read_policies(&args[1]));
    let start_seed = parse(&args[2], "start seed");
    let maps: usize = parse(&args[3], "maps");
    let output = &args[4];
    let threads: usize = parse(&args[5], "threads");
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
                rows.lock().expect("D61 row lock").push(row);
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D61 worker thread");
    }
    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole D61 row owner")
        .into_inner()
        .expect("D61 row lock");
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
        .expect("create D61 output without overwrite");
    let mut writer = BufWriter::new(target);
    writeln!(writer, "map_seed\tseat\topponent\tpolicy\tkind\tturn\town_score\topponent_score\tmargin\town_return\topponent_return\tmargin_return\treward_identity_error\town_workers\topponent_workers\tsuccessful_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tdeposit_prediction_failures\tselected_decisions\tselected_jobs\tselected_nonidle_jobs\tselected_renew_jobs\town_created_crops\topponent_created_crops\tambiguous_created_crops\taction_hash\tstate_hash\toption_batches\tlocked_batches\tbalanced_batches\tharvest_batches\trenew_batches\tfell_batches\tmode_switches\tsafe_fell_rejections\tsemantic_eligible\tsemantic_overrides\tfeature_evaluations\toption_hash\tterminal_live_own_plants\ttrain_none\ttrain_producer\ttrain_chopper\tidle\tbank\tfell_bank\tharvest_bank\trenew\tmine_bank").expect("write D61 header");
    for row in &rows {
        let policy = &policies[row.policy];
        let terminal = row.terminal;
        let kind = match policy.kind {
            PolicyKind::Control => "control",
            PolicyKind::Constant(mode) => mode.label(),
            PolicyKind::Linear => "linear",
        };
        writeln!(
            writer,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{:.8}\t{:.8}\t{:.8}\t{:.8}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
            row.task.map_seed,
            row.task.seat,
            MacroOpponentMode::from_index(row.task.opponent).label(),
            policy.label,
            kind,
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
        )
        .expect("write D61 row");
    }
    writer.flush().expect("flush D61 output");
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

    fn constant_policy(label: &str, mode: Mode, control: bool) -> Policy {
        Policy {
            label: label.to_string(),
            kind: if control {
                PolicyKind::Control
            } else {
                PolicyKind::Constant(mode)
            },
            theta: [0.0; PARAMETERS],
        }
    }

    #[test]
    fn feature_layout_is_finite_and_complete() {
        let env = CompleteMacroEnv::new(9_801_000, 0, MacroOpponentMode::LegendBalanced);
        let features = batch_features(&env, None, [0; MODES]);
        assert_eq!(features.len(), FEATURES);
        assert!(features.iter().all(|value| value.is_finite()));
        assert_eq!(features[0], 1.0);
        assert_eq!(features[39], 0.0);
    }

    #[test]
    fn linear_ties_choose_balanced() {
        assert_eq!(
            linear_mode(&[0.0; PARAMETERS], &[0.0; FEATURES]),
            Mode::Balanced
        );
    }

    #[test]
    fn last_own_crop_is_not_a_legal_fell_target() {
        let mut features = vec![[0.0f32; 44]; 2];
        features[0][20 + 2] = 1.0;
        features[0][30 + owner_index(PlantOwner::Own)] = 1.0;
        features[1][20] = 1.0;
        let actions = vec![5 * MACRO_CELLS as i32, 3 * MACRO_CELLS as i32];
        let order = exact_prior_order(&features, &actions, MacroSelectionBranch::Rate as u8);
        let observation = MacroCandidateObservation {
            actions,
            features,
            teacher_index: order[0],
            branch: MacroSelectionBranch::Rate,
        };
        let (action, eligible, _, rejected) = renewable_safe_action(&observation, Mode::Fell, 1);
        assert!(!eligible);
        assert!(rejected >= 1);
        let selected = observation
            .actions
            .iter()
            .position(|candidate| *candidate as usize == action)
            .unwrap();
        assert!(!unsafe_last_own_fell(&observation, selected, 1));
    }

    #[test]
    fn safe_balanced_reproduces_direct_d40() {
        let task = Task {
            map_seed: 9_801_000,
            seat: 0,
            opponent: 4,
        };
        let control = play(
            task,
            0,
            &constant_policy("d40_control", Mode::Balanced, true),
        );
        let safe = play(
            task,
            1,
            &constant_policy("safe_balanced", Mode::Balanced, false),
        );
        assert_eq!(control.terminal, safe.terminal);
        assert_eq!(control.action_planes, safe.action_planes);
        assert_eq!(safe.options.semantic_overrides, 0);
    }
}
