//! Evaluate D40-anchored policies on the frozen D48a economic-bonus surface.

use std::fs::{File, OpenOptions};
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

use troll_farm::d41b_prior_kernel::exact_prior_order;
use troll_farm::rl_macro::{
    CompleteMacroEnv, MacroCandidateObservation, MacroOpponentMode, MacroSelectionBranch,
    MacroTerminal, MACRO_ACTION_PLANES, MACRO_CELLS,
};

const FEATURES: usize = 44;

#[derive(Clone, Debug)]
struct Policy {
    label: String,
    provenance_scale: f64,
    renew_scale: f64,
    bank_scale: f64,
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

struct Row {
    policy: usize,
    task: Task,
    terminal: MacroTerminal,
    action_planes: [u32; MACRO_ACTION_PLANES],
    reward_identity_error: f32,
}

fn parse<T: std::str::FromStr>(value: &str, label: &str) -> T {
    value
        .parse()
        .unwrap_or_else(|_| panic!("invalid {label}: {value:?}"))
}

fn read_policies(path: &str) -> Vec<Policy> {
    let source = BufReader::new(File::open(path).expect("open D48 policy catalog"));
    let mut lines = source.lines();
    assert_eq!(
        lines.next().expect("D48 policy header").unwrap(),
        "policy\tprovenance_scale\trenew_scale\tbank_scale"
    );
    let mut policies = Vec::new();
    for line in lines {
        let line = line.expect("read D48 policy row");
        let fields: Vec<_> = line.split('\t').collect();
        assert_eq!(fields.len(), 4);
        let policy = Policy {
            label: fields[0].to_string(),
            provenance_scale: parse(fields[1], "provenance scale"),
            renew_scale: parse(fields[2], "renew scale"),
            bank_scale: parse(fields[3], "bank scale"),
        };
        assert!(
            policy.provenance_scale.is_finite()
                && policy.renew_scale.is_finite()
                && policy.bank_scale.is_finite()
        );
        policies.push(policy);
    }
    assert!(!policies.is_empty(), "empty D48 policy catalog");
    assert_eq!(
        policies
            .iter()
            .filter(|policy| policy.label == "anchor")
            .count(),
        1,
        "D48 catalog requires one anchor"
    );
    policies
}

fn scaled(value: f32, scale: i32) -> i32 {
    (value * scale as f32).round() as i32
}

fn kind(row: &[f32; FEATURES]) -> usize {
    (0..6)
        .max_by(|left, right| row[20 + *left].total_cmp(&row[20 + *right]))
        .expect("nonempty D48 job-kind range")
}

fn economic_value(row: &[f32; FEATURES], policy: &Policy) -> f64 {
    let job_kind = kind(row);
    let eta = scaled(row[26], 300).max(1);
    let reward = scaled(row[27], 40);
    let base = 1_000 * reward / eta;
    let provenance_bonus = if row[32] > 0.5 {
        20_000
    } else if row[33] > 0.5 {
        10_000
    } else {
        0
    };
    let renew_bonus = if job_kind == 4 { 15_000 } else { 0 };
    let bank_bonus = if job_kind == 1 { 8_000 } else { 0 };
    f64::from(base)
        + policy.provenance_scale * f64::from(provenance_bonus)
        + policy.renew_scale * f64::from(renew_bonus)
        + policy.bank_scale * f64::from(bank_bonus)
}

fn policy_action(observation: &MacroCandidateObservation, policy: &Policy) -> usize {
    let order = exact_prior_order(
        &observation.features,
        &observation.actions,
        observation.branch as u8,
    );
    if observation.branch != MacroSelectionBranch::Rate {
        return observation.actions[order[0]] as usize;
    }
    let mut best_candidate = order[0];
    let mut best_rank = 0usize;
    let mut best_value = f64::NEG_INFINITY;
    let mut best_eta = i32::MAX;
    let mut best_kind = usize::MAX;
    for (rank, &candidate) in order.iter().enumerate() {
        let row = &observation.features[candidate];
        let value = economic_value(row, policy);
        let eta = scaled(row[26], 300);
        let job_kind = kind(row);
        let tie = (eta, job_kind, rank);
        let best_tie = (best_eta, best_kind, best_rank);
        if value.total_cmp(&best_value).is_gt()
            || (value.total_cmp(&best_value).is_eq() && tie < best_tie)
        {
            best_candidate = candidate;
            best_rank = rank;
            best_value = value;
            best_eta = eta;
            best_kind = job_kind;
        }
    }
    observation.actions[best_candidate] as usize
}

fn play(task: Task, policy_index: usize, policy: &Policy) -> Row {
    let mut env = CompleteMacroEnv::new(
        task.map_seed,
        task.seat,
        MacroOpponentMode::from_index(task.opponent),
    );
    let mut action_planes = [0u32; MACRO_ACTION_PLANES];
    let mut terminal = MacroTerminal::default();
    let mut decisions = 0usize;
    let mut last_turn = env.state.turn;
    let mut stagnant = 0usize;
    while !terminal.done {
        decisions += 1;
        assert!(decisions <= 5_000, "D48 decision loop on {task:?}");
        let observation = env.candidate_observation();
        let action = policy_action(&observation, policy);
        assert!(
            env.legal_actions().contains(&action),
            "D48 chose illegal action"
        );
        action_planes[action / MACRO_CELLS] += 1;
        terminal = env.step(action);
        if env.state.turn == last_turn {
            stagnant += 1;
        } else {
            last_turn = env.state.turn;
            stagnant = 0;
        }
        assert!(stagnant <= 16, "D48 zero-time loop on {task:?}");
    }
    let reward_identity_error = (100.0 * terminal.margin_return
        - (terminal.own_score - terminal.opponent_score) as f32)
        .abs();
    Row {
        policy: policy_index,
        task,
        terminal,
        action_planes,
        reward_identity_error,
    }
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(
        args.len(),
        6,
        "usage: d48_bonus_surface POLICIES START_SEED MAPS OUTPUT THREADS"
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
                rows.lock().expect("D48 row lock").push(row);
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D48 worker thread");
    }
    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole D48 row owner")
        .into_inner()
        .expect("D48 row lock");
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
        .expect("create D48 output without overwrite");
    let mut writer = BufWriter::new(target);
    writeln!(writer, "map_seed\tseat\topponent\tpolicy\tturn\town_score\topponent_score\tmargin\town_return\topponent_return\tmargin_return\town_workers\topponent_workers\tsuccessful_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tselected_decisions\tselected_jobs\tselected_nonidle_jobs\tselected_renew_jobs\town_created_crops\topponent_created_crops\tambiguous_created_crops\taction_hash\tstate_hash\ttrain_none\ttrain_producer\ttrain_chopper\tidle\tbank\tfell_bank\tharvest_bank\trenew\tmine_bank\tdeposit_prediction_failures\treward_identity_error").expect("write D48 header");
    for row in &rows {
        let terminal = row.terminal;
        writeln!(
            writer,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{:.6}\t{:.6}\t{:.6}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{:.9}",
            row.task.map_seed,
            row.task.seat,
            MacroOpponentMode::from_index(row.task.opponent).label(),
            policies[row.policy].label,
            terminal.turn,
            terminal.own_score,
            terminal.opponent_score,
            terminal.own_score - terminal.opponent_score,
            terminal.own_return,
            terminal.opponent_return,
            terminal.margin_return,
            terminal.own_workers,
            terminal.opponent_workers,
            terminal.successful_trains,
            terminal.completed_jobs,
            terminal.invalidated_jobs,
            terminal.invalid_direct_commands,
            terminal.provenance_failures,
            terminal.selected_decisions,
            terminal.selected_jobs,
            terminal.selected_nonidle_jobs,
            terminal.selected_renew_jobs,
            terminal.own_created_crops,
            terminal.opponent_created_crops,
            terminal.ambiguous_created_crops,
            terminal.action_hash,
            terminal.state_hash,
            row.action_planes[0],
            row.action_planes[1],
            row.action_planes[2],
            row.action_planes[3],
            row.action_planes[4],
            row.action_planes[5],
            row.action_planes[6],
            row.action_planes[7],
            row.action_planes[8],
            terminal.deposit_prediction_failures,
            row.reward_identity_error,
        )
        .expect("write D48 row");
    }
    writer.flush().expect("flush D48 output");
    eprintln!(
        "saved {} D48 rows in {:.3}s to {}",
        rows.len(),
        started.elapsed().as_secs_f64(),
        output,
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    fn anchor() -> Policy {
        Policy {
            label: "anchor".to_string(),
            provenance_scale: 1.0,
            renew_scale: 1.0,
            bank_scale: 1.0,
        }
    }

    #[test]
    fn anchor_matches_exact_d40_actions() {
        let policy = anchor();
        for opponent in [0, 1, 4, 7] {
            let mut env =
                CompleteMacroEnv::new(9_778_000, 0, MacroOpponentMode::from_index(opponent));
            for _ in 0..160 {
                let observation = env.candidate_observation();
                let expected = observation.actions[observation.teacher_index] as usize;
                assert_eq!(policy_action(&observation, &policy), expected);
                if env.step(expected).done {
                    break;
                }
            }
        }
    }

    #[test]
    fn economic_value_reconstructs_literal_bonus_formula() {
        let mut row = [0.0f32; FEATURES];
        row[24] = 1.0;
        row[26] = 10.0 / 300.0;
        row[27] = 4.0 / 40.0;
        row[32] = 1.0;
        assert_eq!(economic_value(&row, &anchor()), 35_400.0);
        let policy = Policy {
            label: "scaled".to_string(),
            provenance_scale: 0.0,
            renew_scale: 2.0,
            bank_scale: 1.0,
        };
        assert_eq!(economic_value(&row, &policy), 30_400.0);
    }
}
