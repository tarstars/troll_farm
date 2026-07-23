//! Evaluate D72's frozen recurrent opening-portfolio population.

use std::fs::{File, OpenOptions};
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::time::Instant;

use rayon::prelude::*;

use troll_farm::rl_macro::{MacroDecisionStage, MacroOpponentMode, MacroTerminal};
use troll_farm::rl_opening_portfolio::{
    OpeningPortfolioEnv, OpeningPortfolioMemory, OPENING_PORTFOLIO_ACTIONS,
    OPENING_PORTFOLIO_FEATURES,
};

const SEED_BASE: i64 = 9_804_000;
const MAPS: usize = 8;
const HIDDEN: usize = 12;
const PARAMETERS: usize = HIDDEN * OPENING_PORTFOLIO_FEATURES
    + HIDDEN * HIDDEN
    + HIDDEN
    + OPENING_PORTFOLIO_ACTIONS * HIDDEN
    + OPENING_PORTFOLIO_ACTIONS;

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
enum Family {
    Control,
    OrdinaryRnn,
    PortfolioRnn,
}

impl Family {
    fn label(self) -> &'static str {
        match self {
            Self::Control => "control",
            Self::OrdinaryRnn => "ordinary_rnn",
            Self::PortfolioRnn => "portfolio_rnn",
        }
    }
}

#[derive(Clone, Debug)]
enum PolicyKind {
    Balanced,
    Cyclic,
    Rnn {
        parameters: Vec<f32>,
        portfolio: bool,
    },
}

#[derive(Clone, Debug)]
struct Policy {
    label: String,
    family: Family,
    kind: PolicyKind,
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
    action_counts: [u32; OPENING_PORTFOLIO_ACTIONS],
    pre_crop_boundaries: u32,
    pre_crop_two_seed_legal: u32,
    repeated_source_attempts: u32,
    source_attempts_after_death: u32,
    in_flight_boundaries: u32,
    finite_feature_failures: u32,
    finite_recurrent_failures: u32,
    legal_mask_failures: u32,
    source_assignment_failures: u32,
    boundary_failures: u32,
    reward_identity_error: f32,
    recurrent_hash: u64,
    maximum_hidden_abs: f32,
}

impl Default for Telemetry {
    fn default() -> Self {
        Self {
            boundary_decisions: 0,
            action_counts: [0; OPENING_PORTFOLIO_ACTIONS],
            pre_crop_boundaries: 0,
            pre_crop_two_seed_legal: 0,
            repeated_source_attempts: 0,
            source_attempts_after_death: 0,
            in_flight_boundaries: 0,
            finite_feature_failures: 0,
            finite_recurrent_failures: 0,
            legal_mask_failures: 0,
            source_assignment_failures: 0,
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
    memory: OpeningPortfolioMemory,
    telemetry: Telemetry,
}

fn parse<T: std::str::FromStr>(value: &str, label: &str) -> T {
    value
        .parse()
        .unwrap_or_else(|_| panic!("invalid {label}: {value:?}"))
}

fn read_policies(path: &str) -> Vec<Policy> {
    let source = BufReader::new(File::open(path).expect("open D72 population"));
    let mut lines = source.lines();
    let expected = std::iter::once("policy".to_string())
        .chain((0..PARAMETERS).map(|index| format!("param_{index:04}")))
        .collect::<Vec<_>>()
        .join("\t");
    assert_eq!(
        lines.next().expect("D72 population header").unwrap(),
        expected
    );
    let mut recurrent = Vec::new();
    for line in lines {
        let line = line.expect("read D72 population row");
        let fields: Vec<_> = line.split('\t').collect();
        assert_eq!(fields.len(), PARAMETERS + 1);
        let parameters: Vec<f32> = fields[1..]
            .iter()
            .map(|value| {
                let parsed = parse::<f32>(value, "D72 parameter");
                assert!(parsed.is_finite());
                parsed
            })
            .collect();
        recurrent.push((fields[0].to_string(), parameters));
    }
    assert_eq!(recurrent.len(), 32);
    let mut policies = vec![
        Policy {
            label: "balanced".to_string(),
            family: Family::Control,
            kind: PolicyKind::Balanced,
        },
        Policy {
            label: "cyclic".to_string(),
            family: Family::Control,
            kind: PolicyKind::Cyclic,
        },
    ];
    for (label, parameters) in &recurrent {
        policies.push(Policy {
            label: format!("ordinary_{label}"),
            family: Family::OrdinaryRnn,
            kind: PolicyKind::Rnn {
                parameters: parameters.clone(),
                portfolio: false,
            },
        });
    }
    for (label, parameters) in recurrent {
        policies.push(Policy {
            label: format!("portfolio_{label}"),
            family: Family::PortfolioRnn,
            kind: PolicyKind::Rnn {
                parameters,
                portfolio: true,
            },
        });
    }
    assert_eq!(policies.len(), 66);
    policies
}

fn task(task_index: usize) -> Task {
    let opponents = MacroOpponentMode::ALL.len();
    let per_map = 2 * opponents;
    let within = task_index % per_map;
    Task {
        map_seed: SEED_BASE + (task_index / per_map) as i64,
        seat: within / opponents,
        opponent: within % opponents,
    }
}

fn source_attempt_total(memory: OpeningPortfolioMemory) -> u16 {
    memory.source_attempts.iter().copied().sum()
}

fn cyclic_action(
    mask: &[u8; OPENING_PORTFOLIO_ACTIONS],
    memory: OpeningPortfolioMemory,
    decision: u32,
) -> usize {
    let attempts = source_attempt_total(memory) as usize;
    if attempts < 6 {
        for offset in 0..4 {
            let kind = (attempts + offset) % 4;
            if mask[4 + kind] == 1 {
                return 4 + kind;
            }
        }
    }
    for offset in 0..4 {
        let action = (decision as usize + offset) % 4;
        if mask[action] == 1 {
            return action;
        }
    }
    unreachable!("balanced must remain legal")
}

fn recurrent_action(
    parameters: &[f32],
    portfolio: bool,
    features: &[f32; OPENING_PORTFOLIO_FEATURES],
    mask: &[u8; OPENING_PORTFOLIO_ACTIONS],
    hidden: &mut [f32; HIDDEN],
) -> (usize, bool) {
    let wx_offset = 0;
    let wh_offset = wx_offset + HIDDEN * OPENING_PORTFOLIO_FEATURES;
    let bh_offset = wh_offset + HIDDEN * HIDDEN;
    let wo_offset = bh_offset + HIDDEN;
    let bo_offset = wo_offset + OPENING_PORTFOLIO_ACTIONS * HIDDEN;
    assert_eq!(bo_offset + OPENING_PORTFOLIO_ACTIONS, PARAMETERS);
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
    for action in 0..OPENING_PORTFOLIO_ACTIONS {
        let legal = mask[action] == 1 && (portfolio || action < 4);
        if !legal {
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
        best.expect("D72 recurrent policy has no legal action").0,
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
        assert!(telemetry.boundary_decisions <= 5_000, "D72 decision loop");
        let features = env.features();
        telemetry.finite_feature_failures = telemetry
            .finite_feature_failures
            .saturating_add(u32::from(features.iter().any(|value| !value.is_finite())));
        let mut mask = env.legal_mask();
        let memory = env.memory();
        let own_created =
            u32::from(memory.ended_own_generations) + u32::from(memory.live_own_generations);
        if own_created == 0 {
            telemetry.pre_crop_boundaries = telemetry.pre_crop_boundaries.saturating_add(1);
            telemetry.pre_crop_two_seed_legal = telemetry.pre_crop_two_seed_legal.saturating_add(
                u32::from(mask[4..].iter().filter(|value| **value == 1).count() >= 2),
            );
            telemetry.legal_mask_failures = telemetry
                .legal_mask_failures
                .saturating_add(u32::from(mask[1..4] != [0, 0, 0]));
        }
        telemetry.legal_mask_failures = telemetry
            .legal_mask_failures
            .saturating_add(u32::from(mask[0] != 1));
        telemetry.in_flight_boundaries = telemetry
            .in_flight_boundaries
            .saturating_add(u32::from(memory.source_in_flight));

        let (action, recurrent_finite) = match &policy.kind {
            PolicyKind::Balanced => (0, true),
            PolicyKind::Cyclic => (
                cyclic_action(&mask, memory, telemetry.boundary_decisions - 1),
                true,
            ),
            PolicyKind::Rnn {
                parameters,
                portfolio,
            } => {
                if !portfolio {
                    mask[4..].fill(0);
                }
                recurrent_action(parameters, *portfolio, &features, &mask, &mut hidden)
            }
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
            .saturating_add(u32::from(env.legal_mask()[action] != 1));
        telemetry.action_counts[action] = telemetry.action_counts[action].saturating_add(1);
        if action >= 4 {
            telemetry.repeated_source_attempts = telemetry
                .repeated_source_attempts
                .saturating_add(u32::from(source_attempt_total(memory) > 0));
            telemetry.source_attempts_after_death = telemetry
                .source_attempts_after_death
                .saturating_add(u32::from(memory.ended_own_generations > 0));
        }
        mix(
            &mut telemetry.recurrent_hash,
            telemetry.boundary_decisions as u64,
        );
        mix(&mut telemetry.recurrent_hash, action as u64);
        for value in hidden {
            mix(&mut telemetry.recurrent_hash, u64::from(value.to_bits()));
        }
        let result = env.step(action);
        telemetry.source_assignment_failures = telemetry
            .source_assignment_failures
            .saturating_add(u32::from(action >= 4 && !result.source_assigned));
        telemetry.boundary_failures = telemetry.boundary_failures.saturating_add(u32::from(
            !result.terminal.done && env.batch.macro_env.stage() != MacroDecisionStage::Train,
        ));
        if result.terminal.done {
            break result.terminal;
        }
    };
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
        memory: env.memory(),
        telemetry,
    }
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(
        args.len(),
        4,
        "usage: d72_recurrent_opening_population POPULATION OUTPUT THREADS"
    );
    let policies = read_policies(&args[1]);
    let output = &args[2];
    let threads: usize = parse(&args[3], "threads");
    assert!((1..=64).contains(&threads));
    let work: Vec<_> = (0..policies.len())
        .flat_map(|policy| {
            (0..MAPS * 2 * MacroOpponentMode::ALL.len()).map(move |index| (policy, task(index)))
        })
        .collect();
    let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(threads)
        .build()
        .expect("build D72 thread pool");
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
        .expect("create D72 output without overwrite");
    let mut writer = BufWriter::new(target);
    writeln!(writer, "policy\tfamily\tmap_seed\tseat\topponent\tturn\town_score\topponent_score\tmargin\town_workers\topponent_workers\tsuccessful_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tdeposit_prediction_failures\tselected_decisions\tselected_jobs\tselected_nonidle_jobs\tselected_renew_jobs\town_created_crops\topponent_created_crops\tambiguous_created_crops\town_owned_crop_harvest_units\town_reinvested_crops\taction_hash\tstate_hash\tboundary_decisions\taction_balanced\taction_harvest\taction_renew\taction_fell\taction_seed_plum\taction_seed_lemon\taction_seed_apple\taction_seed_banana\tattempt_plum\tattempt_lemon\tattempt_apple\tattempt_banana\tcreated_plum\tcreated_lemon\tcreated_apple\tcreated_banana\trenewable_receipts\tended_own_generations\treinvested_generations\tlive_own_generations\trepeated_source_attempts\tsource_attempts_after_death\tin_flight_boundaries\tpre_crop_boundaries\tpre_crop_two_seed_legal\tfinite_feature_failures\tfinite_recurrent_failures\tlegal_mask_failures\tsource_assignment_failures\tboundary_failures\treward_identity_error\trecurrent_hash\tmaximum_hidden_abs").expect("write D72 header");
    for row in &rows {
        let policy = &policies[row.policy];
        let terminal = row.terminal;
        let memory = row.memory;
        let telemetry = row.telemetry;
        let fields = [
            policy.label.clone(),
            policy.family.label().to_string(),
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
            telemetry.action_counts[4].to_string(),
            telemetry.action_counts[5].to_string(),
            telemetry.action_counts[6].to_string(),
            telemetry.action_counts[7].to_string(),
            memory.source_attempts[0].to_string(),
            memory.source_attempts[1].to_string(),
            memory.source_attempts[2].to_string(),
            memory.source_attempts[3].to_string(),
            memory.source_creations[0].to_string(),
            memory.source_creations[1].to_string(),
            memory.source_creations[2].to_string(),
            memory.source_creations[3].to_string(),
            memory.renewable_receipts.to_string(),
            memory.ended_own_generations.to_string(),
            memory.reinvested_generations.to_string(),
            memory.live_own_generations.to_string(),
            telemetry.repeated_source_attempts.to_string(),
            telemetry.source_attempts_after_death.to_string(),
            telemetry.in_flight_boundaries.to_string(),
            telemetry.pre_crop_boundaries.to_string(),
            telemetry.pre_crop_two_seed_legal.to_string(),
            telemetry.finite_feature_failures.to_string(),
            telemetry.finite_recurrent_failures.to_string(),
            telemetry.legal_mask_failures.to_string(),
            telemetry.source_assignment_failures.to_string(),
            telemetry.boundary_failures.to_string(),
            format!("{:.8}", telemetry.reward_identity_error),
            telemetry.recurrent_hash.to_string(),
            format!("{:.8}", telemetry.maximum_hidden_abs),
        ];
        writeln!(writer, "{}", fields.join("\t")).expect("write D72 row");
    }
    writer.flush().expect("flush D72 output");
    eprintln!(
        "saved {} D72 rows in {:.3}s ({:.1} boundary transitions/s)",
        rows.len(),
        started.elapsed().as_secs_f64(),
        rows.iter()
            .map(|row| row.telemetry.boundary_decisions as u64)
            .sum::<u64>() as f64
            / started.elapsed().as_secs_f64(),
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn zero_parameters_break_legal_ties_by_action_order() {
        let parameters = vec![0.0; PARAMETERS];
        let features = [0.0; OPENING_PORTFOLIO_FEATURES];
        let mask = [1; OPENING_PORTFOLIO_ACTIONS];
        let mut hidden = [0.0; HIDDEN];
        let (action, finite) = recurrent_action(&parameters, true, &features, &mask, &mut hidden);
        assert!(finite);
        assert_eq!(action, 0);
    }

    #[test]
    fn ordinary_ablation_never_selects_source_action() {
        let mut parameters = vec![0.0; PARAMETERS];
        let output_bias = PARAMETERS - OPENING_PORTFOLIO_ACTIONS;
        parameters[output_bias + 4] = 100.0;
        parameters[output_bias + 2] = 1.0;
        let features = [0.0; OPENING_PORTFOLIO_FEATURES];
        let mask = [1; OPENING_PORTFOLIO_ACTIONS];
        let mut hidden = [0.0; HIDDEN];
        let (action, finite) = recurrent_action(&parameters, false, &features, &mask, &mut hidden);
        assert!(finite);
        assert_eq!(action, 2);
    }
}
