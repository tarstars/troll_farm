//! Evaluate the frozen D98 bounded whole-game concrete-assignment population.

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

const FEATURES: usize = 153;
const GLOBAL_FEATURES: usize = 56;
const SHARED_FEATURES: usize = 46;
const CANDIDATE_FEATURES: usize = 44;
const ORDINALS: usize = 3;
const JOBS: usize = 4;
const OWNERS: usize = 4;
const OWNER_LABELS: [&str; OWNERS] = ["natural", "own", "opponent", "ambiguous"];
const JOB_LABELS: [&str; 6] = ["idle", "bank", "fell", "harvest", "renew", "mine"];

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum PolicyKind {
    Zero,
    One,
    Four,
}

impl PolicyKind {
    fn label(self) -> &'static str {
        match self {
            Self::Zero => "zero",
            Self::One => "one",
            Self::Four => "four",
        }
    }
}

#[derive(Clone, Debug)]
struct Policy {
    label: String,
    kind: PolicyKind,
    budget: u32,
    weights: [f32; FEATURES],
    hash: u64,
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
    opponent: usize,
}

#[derive(Clone, Debug)]
struct CatalogOption {
    index: usize,
    action: usize,
    prior_rank: usize,
    teacher: bool,
    job_kind: usize,
    owner: Option<usize>,
}

#[derive(Clone, Copy, Debug, Default)]
struct AssignmentStats {
    option_batches: u32,
    eligible_batches: u32,
    scored_assignments: u32,
    intervention_batches: u32,
    nonkeep_assignments: u32,
    joint_batches: u32,
    max_scored_per_batch: u32,
    safety_rejections: u32,
    catalog_options: u32,
    job_counts: [u32; JOBS],
    owner_counts: [u32; OWNERS],
    option_hash: u64,
}

#[derive(Clone, Copy, Debug)]
struct Outcome {
    terminal: MacroTerminal,
    reward_identity_error: f32,
    terminal_live_own_plants: usize,
    action_planes: [u32; MACRO_ACTION_PLANES],
}

struct Row {
    policy: usize,
    task: Task,
    outcome: Outcome,
    stats: AssignmentStats,
}

fn parse<T: std::str::FromStr>(value: &str, label: &str) -> T {
    value
        .parse()
        .unwrap_or_else(|_| panic!("invalid {label}: {value:?}"))
}

fn mix(hash: &mut u64, value: u64) {
    for byte in value.to_le_bytes() {
        *hash ^= u64::from(byte);
        *hash = hash.wrapping_mul(0x100000001b3);
    }
}

fn read_policies(path: &str) -> Vec<Policy> {
    let source = BufReader::new(File::open(path).expect("open D98 population"));
    let mut lines = source.lines();
    let expected_header = ["policy", "kind", "budget"]
        .into_iter()
        .map(str::to_string)
        .chain((0..FEATURES).map(|index| format!("param_{index:03}")))
        .collect::<Vec<_>>()
        .join("\t");
    assert_eq!(
        lines.next().expect("D98 population header").unwrap(),
        expected_header
    );
    let mut policies = Vec::new();
    for line in lines {
        let line = line.expect("read D98 population row");
        let fields: Vec<_> = line.split('\t').collect();
        assert_eq!(fields.len(), FEATURES + 3);
        let kind = match fields[1] {
            "zero" => PolicyKind::Zero,
            "one" => PolicyKind::One,
            "four" => PolicyKind::Four,
            other => panic!("unknown D98 policy kind: {other}"),
        };
        let budget = parse(fields[2], "D98 budget");
        assert_eq!(budget, if kind == PolicyKind::One { 1 } else { 4 });
        let mut weights = [0.0f32; FEATURES];
        let mut hash = 0xcbf29ce484222325;
        for (target, value) in weights.iter_mut().zip(&fields[3..]) {
            *target = parse(value, "D98 weight");
            assert!(target.is_finite());
            mix(&mut hash, u64::from(target.to_bits()));
        }
        if kind == PolicyKind::Zero {
            assert!(weights.iter().all(|weight| *weight == 0.0));
        }
        policies.push(Policy {
            label: fields[0].to_string(),
            kind,
            budget,
            weights,
            hash,
        });
    }
    assert_eq!(policies.len(), 129);
    assert_eq!(policies[0].label, "zero_control");
    for index in 0..64 {
        let one = &policies[1 + 2 * index];
        let four = &policies[2 + 2 * index];
        assert_eq!(one.label, format!("one_{index:02}"));
        assert_eq!(four.label, format!("four_{index:02}"));
        assert_eq!(one.weights, four.weights, "D98 matched weights");
        assert_eq!(one.hash, four.hash, "D98 matched policy hash");
    }
    assert_eq!(
        policies
            .iter()
            .map(|policy| policy.label.as_str())
            .collect::<BTreeSet<_>>()
            .len(),
        policies.len()
    );
    policies
}

fn make_env(task: Task) -> CompleteMacroEnv {
    CompleteMacroEnv::new(
        task.map_seed,
        task.seat,
        MacroOpponentMode::from_index(task.opponent),
    )
}

fn live_own_crops(env: &CompleteMacroEnv) -> usize {
    env.state
        .plants
        .iter()
        .filter(|plant| plant.health > 0)
        .filter(|plant| env.owners().get(&plant.pos()) == Some(&PlantOwner::Own))
        .count()
}

fn owner_index(owner: PlantOwner) -> usize {
    match owner {
        PlantOwner::Natural => 0,
        PlantOwner::Own => 1,
        PlantOwner::Opponent => 2,
        PlantOwner::Ambiguous => 3,
    }
}

fn batch_features(env: &CompleteMacroEnv, completed_batches: u32) -> [f32; GLOBAL_FEATURES] {
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
        let index = owner_index(*env.owners().get(&plant.pos()).expect("D98 provenance"));
        plant_counts[index] += 1;
        fruit_counts[index] = fruit_counts[index].saturating_add(plant.fruits);
    }
    for index in 0..4 {
        result[31 + index] = plant_counts[index] as f32 / 20.0;
        result[35 + index] = fruit_counts[index] as f32 / 40.0;
    }
    result[39] = f32::from(plant_counts[1] > 0);
    result[40] = f32::from(plant_counts[2] > 0);
    result[41 + env.train_goal().action_plane()] = 1.0;
    if completed_batches > 0 {
        result[44] = 1.0;
    }
    result[48] = completed_batches as f32 / 100.0;
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
        .expect("D98 worker ordinal")
}

fn one_hot_index(
    features: &[f32; CANDIDATE_FEATURES],
    start: usize,
    count: usize,
) -> Option<usize> {
    let selected: Vec<_> = (0..count)
        .filter(|offset| features[start + *offset] > 0.5)
        .collect();
    if selected.len() == 1 {
        Some(selected[0])
    } else {
        None
    }
}

fn catalog(observation: &MacroCandidateObservation, own_crops: usize) -> (Vec<CatalogOption>, u32) {
    assert_eq!(observation.branch, MacroSelectionBranch::Rate);
    let order = exact_prior_order(
        &observation.features,
        &observation.actions,
        observation.branch as u8,
    );
    assert_eq!(order[0], observation.teacher_index);
    let teacher_features = &observation.features[order[0]];
    let teacher_kind = one_hot_index(teacher_features, 20, 6).expect("D98 teacher job kind");
    let mut result = vec![CatalogOption {
        index: order[0],
        action: observation.actions[order[0]] as usize,
        prior_rank: 0,
        teacher: true,
        job_kind: teacher_kind,
        owner: one_hot_index(teacher_features, 30, 4),
    }];
    let mut classes = BTreeSet::new();
    let mut rejected = 0u32;
    for (rank, index) in order.into_iter().enumerate().skip(1) {
        let features = &observation.features[index];
        let Some(job_kind) = one_hot_index(features, 20, 6) else {
            continue;
        };
        if !(2..=5).contains(&job_kind) {
            continue;
        }
        let owner = one_hot_index(features, 30, 4);
        if job_kind != 5 && owner.is_none() {
            continue;
        }
        if job_kind == 2 && own_crops <= 1 && owner == Some(1) {
            rejected += 1;
            continue;
        }
        let class = if job_kind == 5 {
            "mine".to_string()
        } else {
            format!("{}:{}", JOB_LABELS[job_kind], OWNER_LABELS[owner.unwrap()])
        };
        if classes.insert(class) {
            result.push(CatalogOption {
                index,
                action: observation.actions[index] as usize,
                prior_rank: rank,
                teacher: false,
                job_kind,
                owner,
            });
        }
    }
    (result, rejected)
}

fn score_features(
    global: &[f32; GLOBAL_FEATURES],
    shared: &[f32; SHARED_FEATURES],
    candidate: &[f32; CANDIDATE_FEATURES],
    ordinal: usize,
    position: usize,
    remaining_budget: u32,
    prior_rank: usize,
    candidate_count: usize,
) -> [f32; FEATURES] {
    let mut result = [0.0f32; FEATURES];
    result[..GLOBAL_FEATURES].copy_from_slice(global);
    result[GLOBAL_FEATURES..GLOBAL_FEATURES + SHARED_FEATURES].copy_from_slice(shared);
    let candidate_start = GLOBAL_FEATURES + SHARED_FEATURES;
    result[candidate_start..candidate_start + CANDIDATE_FEATURES].copy_from_slice(candidate);
    let ordinal_start = candidate_start + CANDIDATE_FEATURES;
    result[ordinal_start + ordinal] = 1.0;
    let position_start = ordinal_start + ORDINALS;
    result[position_start + position] = 1.0;
    result[position_start + 2] = remaining_budget as f32 / 4.0;
    result[position_start + 3] = prior_rank as f32 / candidate_count as f32;
    assert!(result.iter().all(|value| value.is_finite()));
    result
}

fn dot(weights: &[f32; FEATURES], features: &[f32; FEATURES]) -> f32 {
    weights
        .iter()
        .zip(features)
        .map(|(weight, feature)| weight * feature)
        .sum()
}

fn choose(
    env: &CompleteMacroEnv,
    observation: &MacroCandidateObservation,
    policy: &Policy,
    global: &[f32; GLOBAL_FEATURES],
    position: usize,
    remaining_budget: u32,
) -> (CatalogOption, usize, u32, u64) {
    let (options, rejected) = catalog(observation, live_own_crops(env));
    let unit_id = env.current_unit_id().expect("D98 scored worker");
    let ordinal = worker_ordinal(env, unit_id);
    let shared = env.d42_shared_context();
    let mut selected = options[0].clone();
    let mut best_score = 0.0f32;
    let mut hash = 0xcbf29ce484222325;
    mix(&mut hash, options.len() as u64);
    for option in &options {
        mix(&mut hash, option.action as u64);
        mix(&mut hash, option.prior_rank as u64);
        mix(&mut hash, option.job_kind as u64);
        mix(
            &mut hash,
            option.owner.map_or(u64::MAX, |owner| owner as u64),
        );
        if option.teacher {
            continue;
        }
        let features = score_features(
            global,
            &shared,
            &observation.features[option.index],
            ordinal,
            position,
            remaining_budget,
            option.prior_rank,
            observation.actions.len(),
        );
        let score = dot(&policy.weights, &features);
        assert!(score.is_finite());
        if score.total_cmp(&best_score).is_gt() {
            selected = option.clone();
            best_score = score;
        }
    }
    (selected, options.len(), rejected, hash)
}

fn finish_batch(stats: &mut AssignmentStats, scored: u32, nonkeep: u32) {
    stats.max_scored_per_batch = stats.max_scored_per_batch.max(scored);
    if nonkeep >= 2 {
        stats.joint_batches += 1;
    }
}

fn step(
    env: &mut CompleteMacroEnv,
    action: usize,
    planes: &mut [u32; MACRO_ACTION_PLANES],
) -> MacroTerminal {
    assert!(env.legal_actions().contains(&action), "D98 illegal action");
    planes[action / MACRO_CELLS] += 1;
    env.step(action)
}

fn finish(env: &CompleteMacroEnv, terminal: MacroTerminal, planes: [u32; 9]) -> Outcome {
    let reward_identity_error = [
        (terminal.own_return - terminal.own_score as f32 / 100.0).abs(),
        (terminal.opponent_return - terminal.opponent_score as f32 / 100.0).abs(),
        (terminal.margin_return - (terminal.own_score - terminal.opponent_score) as f32 / 100.0)
            .abs(),
    ]
    .into_iter()
    .fold(0.0f32, f32::max);
    Outcome {
        terminal,
        reward_identity_error,
        terminal_live_own_plants: live_own_crops(env),
        action_planes: planes,
    }
}

fn play_control(task: Task) -> Outcome {
    let mut env = make_env(task);
    let mut planes = [0u32; MACRO_ACTION_PLANES];
    loop {
        let observation = env.candidate_observation();
        let terminal = step(
            &mut env,
            observation.actions[observation.teacher_index] as usize,
            &mut planes,
        );
        if terminal.done {
            return finish(&env, terminal, planes);
        }
    }
}

fn play(task: Task, policy_index: usize, policy: &Policy) -> Row {
    let mut env = make_env(task);
    let mut stats = AssignmentStats {
        option_hash: 0xcbf29ce484222325,
        ..AssignmentStats::default()
    };
    let mut planes = [0u32; MACRO_ACTION_PLANES];
    let mut global = [0.0f32; GLOBAL_FEATURES];
    let mut batch_open = false;
    let mut batch_scored = 0u32;
    let mut batch_nonkeep = 0u32;
    let mut batch_eligible_recorded = false;
    let mut decisions = 0usize;
    let mut terminal;
    loop {
        decisions += 1;
        assert!(decisions <= 5_000, "D98 decision loop: {task:?}");
        let observation = env.candidate_observation();
        if env.stage() == MacroDecisionStage::Train {
            if batch_open {
                finish_batch(&mut stats, batch_scored, batch_nonkeep);
            }
            global = batch_features(&env, stats.option_batches);
            stats.option_batches += 1;
            batch_open = true;
            batch_scored = 0;
            batch_nonkeep = 0;
            batch_eligible_recorded = false;
        }
        let can_score = env.stage() == MacroDecisionStage::Worker
            && observation.branch == MacroSelectionBranch::Rate
            && batch_scored < 2
            && live_own_crops(&env) > 0
            && env.state.turn <= MACRO_TOTAL_TURNS - 30
            && (batch_nonkeep > 0 || stats.intervention_batches < policy.budget);
        let action = if can_score {
            if !batch_eligible_recorded {
                stats.eligible_batches += 1;
                batch_eligible_recorded = true;
            }
            let remaining = policy.budget.saturating_sub(stats.intervention_batches);
            let (selected, catalog_size, rejected, catalog_hash) = choose(
                &env,
                &observation,
                policy,
                &global,
                batch_scored as usize,
                remaining,
            );
            stats.scored_assignments += 1;
            stats.catalog_options += catalog_size as u32;
            stats.safety_rejections += rejected;
            batch_scored += 1;
            mix(&mut stats.option_hash, env.state.turn as u64);
            mix(&mut stats.option_hash, batch_scored as u64);
            mix(&mut stats.option_hash, catalog_hash);
            mix(&mut stats.option_hash, selected.action as u64);
            if !selected.teacher {
                if batch_nonkeep == 0 {
                    stats.intervention_batches += 1;
                }
                batch_nonkeep += 1;
                stats.nonkeep_assignments += 1;
                stats.job_counts[selected.job_kind - 2] += 1;
                if let Some(owner) = selected.owner {
                    stats.owner_counts[owner] += 1;
                }
            }
            selected.action
        } else {
            observation.actions[observation.teacher_index] as usize
        };
        terminal = step(&mut env, action, &mut planes);
        if terminal.done {
            break;
        }
    }
    if batch_open {
        finish_batch(&mut stats, batch_scored, batch_nonkeep);
    }
    assert!(stats.intervention_batches <= policy.budget);
    assert!(stats.max_scored_per_batch <= 2);
    assert!(stats.joint_batches <= stats.intervention_batches);
    Row {
        policy: policy_index,
        task,
        outcome: finish(&env, terminal, planes),
        stats,
    }
}

fn parallel_baselines(tasks: &[Task], threads: usize) -> BTreeMap<Task, Outcome> {
    let tasks = Arc::new(tasks.to_vec());
    let next = Arc::new(AtomicUsize::new(0));
    let outcomes = Arc::new(Mutex::new(BTreeMap::new()));
    let handles: Vec<_> = (0..threads.min(tasks.len()))
        .map(|_| {
            let tasks = Arc::clone(&tasks);
            let next = Arc::clone(&next);
            let outcomes = Arc::clone(&outcomes);
            thread::spawn(move || loop {
                let index = next.fetch_add(1, Ordering::Relaxed);
                let Some(&task) = tasks.get(index) else {
                    break;
                };
                outcomes
                    .lock()
                    .expect("D98 baseline lock")
                    .insert(task, play_control(task));
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D98 baseline worker");
    }
    Arc::try_unwrap(outcomes)
        .ok()
        .expect("sole D98 baselines")
        .into_inner()
        .expect("D98 baseline lock")
}

fn parallel_rows(
    policies: Arc<Vec<Policy>>,
    tasks: &[Task],
    baselines: &BTreeMap<Task, Outcome>,
    threads: usize,
) -> Vec<Row> {
    let work: Vec<_> = (0..policies.len())
        .flat_map(|policy| tasks.iter().copied().map(move |task| (policy, task)))
        .collect();
    let work = Arc::new(work);
    let baselines = Arc::new(baselines.clone());
    let next = Arc::new(AtomicUsize::new(0));
    let rows = Arc::new(Mutex::new(Vec::with_capacity(work.len())));
    let handles: Vec<_> = (0..threads.min(work.len()))
        .map(|_| {
            let policies = Arc::clone(&policies);
            let work = Arc::clone(&work);
            let baselines = Arc::clone(&baselines);
            let next = Arc::clone(&next);
            let rows = Arc::clone(&rows);
            thread::spawn(move || loop {
                let index = next.fetch_add(1, Ordering::Relaxed);
                let Some(&(policy, task)) = work.get(index) else {
                    break;
                };
                let row = play(task, policy, &policies[policy]);
                if policies[policy].kind == PolicyKind::Zero {
                    let expected = baselines[&task];
                    assert_eq!(row.outcome.terminal, expected.terminal, "D98 zero terminal");
                    assert_eq!(
                        row.outcome.action_planes, expected.action_planes,
                        "D98 zero action planes"
                    );
                }
                rows.lock().expect("D98 row lock").push(row);
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D98 population worker");
    }
    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole D98 rows")
        .into_inner()
        .expect("D98 row lock");
    rows.sort_by_key(|row| {
        (
            policies[row.policy].label.clone(),
            row.task.map_seed,
            row.task.seat,
            row.task.opponent,
        )
    });
    rows
}

fn terminal_header() -> Vec<&'static str> {
    vec![
        "turn",
        "own_score",
        "opponent_score",
        "margin",
        "own_return",
        "opponent_return",
        "margin_return",
        "reward_identity_error",
        "own_workers",
        "opponent_workers",
        "successful_trains",
        "completed_jobs",
        "invalidated_jobs",
        "invalid_direct_commands",
        "provenance_failures",
        "deposit_prediction_failures",
        "selected_decisions",
        "selected_jobs",
        "selected_nonidle_jobs",
        "selected_renew_jobs",
        "own_created_crops",
        "opponent_created_crops",
        "ambiguous_created_crops",
        "own_owned_crop_harvest_units",
        "own_reinvested_crops",
        "action_hash",
        "state_hash",
        "terminal_live_own_plants",
        "train_none",
        "train_producer",
        "train_chopper",
        "idle",
        "bank",
        "fell_bank",
        "harvest_bank",
        "renew",
        "mine_bank",
    ]
}

fn terminal_columns(outcome: Outcome) -> Vec<String> {
    let terminal = outcome.terminal;
    let mut result = vec![
        terminal.turn.to_string(),
        terminal.own_score.to_string(),
        terminal.opponent_score.to_string(),
        (terminal.own_score - terminal.opponent_score).to_string(),
        format!("{:.8}", terminal.own_return),
        format!("{:.8}", terminal.opponent_return),
        format!("{:.8}", terminal.margin_return),
        format!("{:.8}", outcome.reward_identity_error),
        terminal.own_workers.to_string(),
        terminal.opponent_workers.to_string(),
        terminal.successful_trains.to_string(),
        terminal.completed_jobs.to_string(),
        terminal.invalidated_jobs.to_string(),
        terminal.invalid_direct_commands.to_string(),
        terminal.provenance_failures.to_string(),
        terminal.deposit_prediction_failures.to_string(),
        terminal.selected_decisions.to_string(),
        terminal.selected_jobs.to_string(),
        terminal.selected_nonidle_jobs.to_string(),
        terminal.selected_renew_jobs.to_string(),
        terminal.own_created_crops.to_string(),
        terminal.opponent_created_crops.to_string(),
        terminal.ambiguous_created_crops.to_string(),
        terminal.own_owned_crop_harvest_units.to_string(),
        terminal.own_reinvested_crops.to_string(),
        terminal.action_hash.to_string(),
        terminal.state_hash.to_string(),
        outcome.terminal_live_own_plants.to_string(),
    ];
    result.extend(
        outcome
            .action_planes
            .into_iter()
            .map(|value| value.to_string()),
    );
    result
}

fn write_baselines(path: &str, baselines: &BTreeMap<Task, Outcome>) {
    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(path)
        .expect("create D98 baseline output");
    let mut writer = BufWriter::new(target);
    let mut header = vec!["map_seed", "seat", "opponent"];
    header.extend(terminal_header());
    writeln!(writer, "{}", header.join("\t")).expect("write D98 baseline header");
    for (task, outcome) in baselines {
        let mut columns = vec![
            task.map_seed.to_string(),
            task.seat.to_string(),
            MacroOpponentMode::from_index(task.opponent)
                .label()
                .to_string(),
        ];
        columns.extend(terminal_columns(*outcome));
        writeln!(writer, "{}", columns.join("\t")).expect("write D98 baseline row");
    }
    writer.flush().expect("flush D98 baseline output");
}

fn write_rows(path: &str, rows: &[Row], policies: &[Policy]) {
    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(path)
        .expect("create D98 population output");
    let mut writer = BufWriter::new(target);
    let mut header = vec!["map_seed", "seat", "opponent", "policy", "kind", "budget"];
    header.extend(terminal_header());
    header.extend([
        "option_batches",
        "eligible_batches",
        "scored_assignments",
        "intervention_batches",
        "nonkeep_assignments",
        "joint_batches",
        "max_scored_per_batch",
        "safety_rejections",
        "catalog_options",
        "concrete_fell",
        "concrete_harvest",
        "concrete_renew",
        "concrete_mine",
        "owner_natural",
        "owner_own",
        "owner_opponent",
        "owner_ambiguous",
        "option_hash",
        "policy_hash",
    ]);
    writeln!(writer, "{}", header.join("\t")).expect("write D98 population header");
    for row in rows {
        let policy = &policies[row.policy];
        let mut columns = vec![
            row.task.map_seed.to_string(),
            row.task.seat.to_string(),
            MacroOpponentMode::from_index(row.task.opponent)
                .label()
                .to_string(),
            policy.label.clone(),
            policy.kind.label().to_string(),
            policy.budget.to_string(),
        ];
        columns.extend(terminal_columns(row.outcome));
        columns.extend([
            row.stats.option_batches.to_string(),
            row.stats.eligible_batches.to_string(),
            row.stats.scored_assignments.to_string(),
            row.stats.intervention_batches.to_string(),
            row.stats.nonkeep_assignments.to_string(),
            row.stats.joint_batches.to_string(),
            row.stats.max_scored_per_batch.to_string(),
            row.stats.safety_rejections.to_string(),
            row.stats.catalog_options.to_string(),
            row.stats.job_counts[0].to_string(),
            row.stats.job_counts[1].to_string(),
            row.stats.job_counts[2].to_string(),
            row.stats.job_counts[3].to_string(),
            row.stats.owner_counts[0].to_string(),
            row.stats.owner_counts[1].to_string(),
            row.stats.owner_counts[2].to_string(),
            row.stats.owner_counts[3].to_string(),
            row.stats.option_hash.to_string(),
            policy.hash.to_string(),
        ]);
        writeln!(writer, "{}", columns.join("\t")).expect("write D98 population row");
    }
    writer.flush().expect("flush D98 population output");
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(
        args.len(),
        7,
        "usage: d98_bounded_joint_assignment_population POPULATION START_SEED MAPS OUTPUT BASELINE_OUTPUT THREADS"
    );
    let policies = Arc::new(read_policies(&args[1]));
    let start_seed: i64 = parse(&args[2], "D98 start seed");
    let maps: usize = parse(&args[3], "D98 maps");
    let threads: usize = parse(&args[6], "D98 threads");
    assert!(maps > 0 && threads > 0);
    let tasks: Vec<_> = (start_seed..start_seed + maps as i64)
        .flat_map(|map_seed| {
            (0..2).flat_map(move |seat| {
                (0..MacroOpponentMode::ALL.len()).map(move |opponent| Task {
                    map_seed,
                    seat,
                    opponent,
                })
            })
        })
        .collect();
    let started = Instant::now();
    let baselines = parallel_baselines(&tasks, threads);
    let baseline_seconds = started.elapsed().as_secs_f64();
    let population_started = Instant::now();
    let rows = parallel_rows(Arc::clone(&policies), &tasks, &baselines, threads);
    let population_seconds = population_started.elapsed().as_secs_f64();
    write_baselines(&args[5], &baselines);
    write_rows(&args[4], &rows, &policies);
    eprintln!(
        "saved {} baselines in {:.3}s and {} rows in {:.3}s ({:.3} episodes/s)",
        baselines.len(),
        baseline_seconds,
        rows.len(),
        population_seconds,
        rows.len() as f64 / population_seconds,
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    fn zero_policy() -> Policy {
        Policy {
            label: "zero_control".to_string(),
            kind: PolicyKind::Zero,
            budget: 4,
            weights: [0.0; FEATURES],
            hash: 0,
        }
    }

    #[test]
    fn zero_policy_matches_exact_control() {
        let task = Task {
            map_seed: 9_821_000,
            seat: 1,
            opponent: 3,
        };
        let control = play_control(task);
        let row = play(task, 0, &zero_policy());
        assert_eq!(row.outcome.terminal, control.terminal);
        assert_eq!(row.outcome.action_planes, control.action_planes);
        assert_eq!(row.stats.intervention_batches, 0);
        assert!(row.stats.scored_assignments > 0);
    }

    #[test]
    fn score_feature_layout_is_finite_and_complete() {
        let global = [0.25; GLOBAL_FEATURES];
        let shared = [0.5; SHARED_FEATURES];
        let candidate = [0.75; CANDIDATE_FEATURES];
        let features = score_features(&global, &shared, &candidate, 2, 1, 3, 7, 10);
        assert!(features.iter().all(|value| value.is_finite()));
        assert_eq!(features.len(), FEATURES);
        assert_eq!(features[148], 1.0);
        assert_eq!(features[150], 1.0);
        assert_eq!(features[151], 0.75);
        assert_eq!(features[152], 0.7);
    }
}
