//! Evaluate arbitrary D76 four-mode recurrent-readout populations.

use std::fs::{File, OpenOptions};
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::time::Instant;

use rayon::prelude::*;

use troll_farm::rl_macro::{MacroDecisionStage, MacroOpponentMode, MacroTerminal};
use troll_farm::rl_opening_portfolio::{OpeningPortfolioEnv, OPENING_PORTFOLIO_FEATURES};

const ACTIONS: usize = 4;
const HIDDEN: usize = 12;
const PARAMETERS: usize =
    HIDDEN * OPENING_PORTFOLIO_FEATURES + HIDDEN * HIDDEN + HIDDEN + ACTIONS * HIDDEN + ACTIONS;

#[derive(Clone, Debug)]
struct Policy {
    label: String,
    parameters: Option<Vec<f32>>,
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
    opponent: usize,
}

#[derive(Clone, Copy, Debug)]
struct Telemetry {
    boundary_decisions: u32,
    action_counts: [u32; ACTIONS],
    unlocked_decisions: u32,
    unlocked_action_counts: [u32; ACTIONS],
    finite_feature_failures: u32,
    finite_recurrent_failures: u32,
    legal_mask_failures: u32,
    boundary_failures: u32,
    reward_identity_error: f32,
    recurrent_hash: u64,
    maximum_hidden_abs: f32,
}

impl Default for Telemetry {
    fn default() -> Self {
        Self {
            boundary_decisions: 0,
            action_counts: [0; ACTIONS],
            unlocked_decisions: 0,
            unlocked_action_counts: [0; ACTIONS],
            finite_feature_failures: 0,
            finite_recurrent_failures: 0,
            legal_mask_failures: 0,
            boundary_failures: 0,
            reward_identity_error: 0.0,
            recurrent_hash: 0xcbf29ce484222325,
            maximum_hidden_abs: 0.0,
        }
    }
}

#[derive(Clone, Debug)]
struct Row {
    policy: usize,
    task: Task,
    terminal: MacroTerminal,
    telemetry: Telemetry,
}

fn parse<T: std::str::FromStr>(value: &str, label: &str) -> T {
    value
        .parse()
        .unwrap_or_else(|_| panic!("invalid {label}: {value:?}"))
}

fn read_policies(path: &str) -> Vec<Policy> {
    let source = BufReader::new(File::open(path).expect("open D76 population"));
    let mut lines = source.lines();
    let expected = std::iter::once("policy".to_string())
        .chain((0..PARAMETERS).map(|index| format!("param_{index:04}")))
        .collect::<Vec<_>>()
        .join("\t");
    assert_eq!(
        lines.next().expect("D76 population header").unwrap(),
        expected
    );
    let mut labels = std::collections::BTreeSet::new();
    let mut policies = vec![Policy {
        label: "balanced".to_string(),
        parameters: None,
    }];
    for line in lines {
        let line = line.expect("read D76 population row");
        let fields: Vec<_> = line.split('\t').collect();
        assert_eq!(fields.len(), PARAMETERS + 1);
        assert!(!fields[0].is_empty() && !fields[0].contains(char::is_whitespace));
        assert!(fields[0] != "balanced", "reserved D76 control label");
        assert!(labels.insert(fields[0].to_string()), "duplicate D76 policy");
        let parameters = fields[1..]
            .iter()
            .map(|value| {
                let parsed = parse::<f32>(value, "D76 parameter");
                assert!(parsed.is_finite());
                parsed
            })
            .collect();
        policies.push(Policy {
            label: fields[0].to_string(),
            parameters: Some(parameters),
        });
    }
    assert!(policies.len() >= 2, "empty D76 recurrent population");
    policies
}

fn tasks(seed_base: i64, maps: usize) -> Vec<Task> {
    (0..maps * 2 * MacroOpponentMode::ALL.len())
        .map(|task_index| {
            let opponents = MacroOpponentMode::ALL.len();
            let per_map = 2 * opponents;
            let within = task_index % per_map;
            Task {
                map_seed: seed_base + (task_index / per_map) as i64,
                seat: within / opponents,
                opponent: within % opponents,
            }
        })
        .collect()
}

fn recurrent_action(
    parameters: &[f32],
    features: &[f32; OPENING_PORTFOLIO_FEATURES],
    mask: &[u8; ACTIONS],
    hidden: &mut [f32; HIDDEN],
) -> (usize, bool) {
    let wx_offset = 0;
    let wh_offset = wx_offset + HIDDEN * OPENING_PORTFOLIO_FEATURES;
    let bh_offset = wh_offset + HIDDEN * HIDDEN;
    let wo_offset = bh_offset + HIDDEN;
    let bo_offset = wo_offset + ACTIONS * HIDDEN;
    assert_eq!(bo_offset + ACTIONS, PARAMETERS);
    let previous = *hidden;
    for row in 0..HIDDEN {
        let mut value = parameters[bh_offset + row];
        for column in 0..OPENING_PORTFOLIO_FEATURES {
            value += parameters[wx_offset + row * OPENING_PORTFOLIO_FEATURES + column]
                * features[column];
        }
        for column in 0..HIDDEN {
            value += parameters[wh_offset + row * HIDDEN + column] * previous[column];
        }
        hidden[row] = value.tanh();
    }
    let mut best = None;
    let mut finite = hidden.iter().all(|value| value.is_finite());
    for action in 0..ACTIONS {
        if mask[action] == 0 {
            continue;
        }
        let mut logit = parameters[bo_offset + action];
        for column in 0..HIDDEN {
            logit += parameters[wo_offset + action * HIDDEN + column] * hidden[column];
        }
        finite &= logit.is_finite();
        if best.map_or(true, |(_, score): (usize, f32)| {
            logit.total_cmp(&score).is_gt()
        }) {
            best = Some((action, logit));
        }
    }
    (
        best.expect("D76 recurrent policy has no legal action").0,
        finite,
    )
}

fn mix(hash: &mut u64, value: u64) {
    for byte in value.to_le_bytes() {
        *hash ^= u64::from(byte);
        *hash = hash.wrapping_mul(0x100000001b3);
    }
}

fn play(policy_index: usize, policy: &Policy, task: Task) -> Row {
    let mut env = OpeningPortfolioEnv::new(
        task.map_seed,
        task.seat,
        MacroOpponentMode::from_index(task.opponent),
    );
    let mut telemetry = Telemetry::default();
    let mut hidden = [0.0f32; HIDDEN];
    let terminal = loop {
        telemetry.boundary_decisions = telemetry.boundary_decisions.saturating_add(1);
        assert!(telemetry.boundary_decisions <= 5_000, "D76 decision loop");
        let features = env.features();
        telemetry.finite_feature_failures = telemetry
            .finite_feature_failures
            .saturating_add(u32::from(features.iter().any(|value| !value.is_finite())));
        let mask: [u8; ACTIONS] = env.legal_mask()[..ACTIONS]
            .try_into()
            .expect("D76 ordinary mask width");
        telemetry.legal_mask_failures = telemetry
            .legal_mask_failures
            .saturating_add(u32::from(mask[0] != 1));
        let unlocked = mask == [1; ACTIONS];
        telemetry.unlocked_decisions = telemetry
            .unlocked_decisions
            .saturating_add(u32::from(unlocked));
        let (action, recurrent_finite) = match &policy.parameters {
            None => (0, true),
            Some(parameters) => recurrent_action(parameters, &features, &mask, &mut hidden),
        };
        telemetry.finite_recurrent_failures = telemetry
            .finite_recurrent_failures
            .saturating_add(u32::from(!recurrent_finite));
        telemetry.maximum_hidden_abs = hidden
            .iter()
            .map(|value| value.abs())
            .fold(telemetry.maximum_hidden_abs, f32::max);
        telemetry.legal_mask_failures = telemetry
            .legal_mask_failures
            .saturating_add(u32::from(mask[action] != 1));
        telemetry.action_counts[action] = telemetry.action_counts[action].saturating_add(1);
        if unlocked {
            telemetry.unlocked_action_counts[action] =
                telemetry.unlocked_action_counts[action].saturating_add(1);
        }
        mix(
            &mut telemetry.recurrent_hash,
            telemetry.boundary_decisions as u64,
        );
        mix(&mut telemetry.recurrent_hash, action as u64);
        for value in hidden {
            mix(&mut telemetry.recurrent_hash, u64::from(value.to_bits()));
        }
        let result = env.step(action).terminal;
        telemetry.boundary_failures = telemetry.boundary_failures.saturating_add(u32::from(
            !result.done && env.batch.macro_env.stage() != MacroDecisionStage::Train,
        ));
        if result.done {
            break result;
        }
    };
    assert!(env.memory().source_attempts.iter().all(|value| *value == 0));
    telemetry.reward_identity_error = [
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
        telemetry,
    }
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(
        args.len(),
        7,
        "usage: d76_recurrent_readout_population POPULATION OUTPUT SEED_BASE MAPS THREADS"
    );
    let policies = read_policies(&args[1]);
    let output = &args[2];
    let seed_base: i64 = parse(&args[3], "seed base");
    let maps: usize = parse(&args[4], "map count");
    let threads: usize = parse(&args[5], "thread count");
    assert!(maps > 0 && maps <= 256);
    assert!((1..=64).contains(&threads));
    assert_eq!(args[6], "ordinary", "D76 action-family guard");
    let tasks = tasks(seed_base, maps);
    let work: Vec<_> = (0..policies.len())
        .flat_map(|policy| tasks.iter().copied().map(move |task| (policy, task)))
        .collect();
    let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(threads)
        .build()
        .expect("build D76 thread pool");
    let started = Instant::now();
    let mut rows: Vec<_> = pool.install(|| {
        work.into_par_iter()
            .map(|(policy, task)| play(policy, &policies[policy], task))
            .collect()
    });
    rows.sort_by_key(|row| (row.policy, row.task));

    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(output)
        .expect("create D76 output without overwrite");
    let mut writer = BufWriter::new(target);
    writeln!(writer, "policy\tfamily\tmap_seed\tseat\topponent\tturn\town_score\topponent_score\tmargin\town_workers\topponent_workers\tsuccessful_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tdeposit_prediction_failures\tselected_decisions\tselected_jobs\tselected_nonidle_jobs\tselected_renew_jobs\town_created_crops\topponent_created_crops\tambiguous_created_crops\town_owned_crop_harvest_units\town_reinvested_crops\taction_hash\tstate_hash\tboundary_decisions\taction_balanced\taction_harvest\taction_renew\taction_fell\tunlocked_decisions\tunlocked_balanced\tunlocked_harvest\tunlocked_renew\tunlocked_fell\tfinite_feature_failures\tfinite_recurrent_failures\tlegal_mask_failures\tboundary_failures\treward_identity_error\trecurrent_hash\tmaximum_hidden_abs").expect("write D76 header");
    for row in &rows {
        let policy = &policies[row.policy];
        let terminal = row.terminal;
        let telemetry = row.telemetry;
        let fields = [
            policy.label.clone(),
            if policy.parameters.is_some() {
                "recurrent_readout".to_string()
            } else {
                "control".to_string()
            },
            row.task.map_seed.to_string(),
            row.task.seat.to_string(),
            MacroOpponentMode::from_index(row.task.opponent)
                .label()
                .to_string(),
            terminal.turn.to_string(),
            terminal.own_score.to_string(),
            terminal.opponent_score.to_string(),
            (terminal.own_score - terminal.opponent_score).to_string(),
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
            telemetry.boundary_decisions.to_string(),
            telemetry.action_counts[0].to_string(),
            telemetry.action_counts[1].to_string(),
            telemetry.action_counts[2].to_string(),
            telemetry.action_counts[3].to_string(),
            telemetry.unlocked_decisions.to_string(),
            telemetry.unlocked_action_counts[0].to_string(),
            telemetry.unlocked_action_counts[1].to_string(),
            telemetry.unlocked_action_counts[2].to_string(),
            telemetry.unlocked_action_counts[3].to_string(),
            telemetry.finite_feature_failures.to_string(),
            telemetry.finite_recurrent_failures.to_string(),
            telemetry.legal_mask_failures.to_string(),
            telemetry.boundary_failures.to_string(),
            format!("{:.8}", telemetry.reward_identity_error),
            telemetry.recurrent_hash.to_string(),
            format!("{:.8}", telemetry.maximum_hidden_abs),
        ];
        writeln!(writer, "{}", fields.join("\t")).expect("write D76 row");
    }
    writer.flush().expect("flush D76 output");
    eprintln!(
        "saved {} D76 rows for {} policies x {} tasks in {:.3}s",
        rows.len(),
        policies.len(),
        tasks.len(),
        started.elapsed().as_secs_f64()
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parameter_geometry_is_frozen() {
        assert_eq!(PARAMETERS, 1_072);
    }

    #[test]
    fn zero_readout_chooses_balanced() {
        let parameters = vec![0.0; PARAMETERS];
        let features = [0.0; OPENING_PORTFOLIO_FEATURES];
        let mask = [1; ACTIONS];
        let mut hidden = [0.0; HIDDEN];
        let (action, finite) = recurrent_action(&parameters, &features, &mask, &mut hidden);
        assert!(finite);
        assert_eq!(action, 0);
    }

    #[test]
    fn output_bias_selects_requested_legal_mode() {
        let mut parameters = vec![0.0; PARAMETERS];
        let output_bias = PARAMETERS - ACTIONS;
        parameters[output_bias + 2] = 1.0;
        let features = [0.0; OPENING_PORTFOLIO_FEATURES];
        let mask = [1; ACTIONS];
        let mut hidden = [0.0; HIDDEN];
        let (action, finite) = recurrent_action(&parameters, &features, &mask, &mut hidden);
        assert!(finite);
        assert_eq!(action, 2);
    }
}
