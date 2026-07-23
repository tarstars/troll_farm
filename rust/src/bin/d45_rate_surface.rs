//! Evaluate complete D40-anchored policies on a compact 32-parameter rate surface.

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

const PARAMETERS: usize = 32;

#[derive(Clone, Debug)]
struct Genome {
    label: String,
    theta: [f32; PARAMETERS],
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
    opponent: usize,
}

struct Work {
    genome: usize,
    task: Task,
}

struct Row {
    genome: usize,
    task: Task,
    terminal: MacroTerminal,
    action_planes: [u32; MACRO_ACTION_PLANES],
}

fn parse<T: std::str::FromStr>(value: &str, label: &str) -> T {
    value
        .parse()
        .unwrap_or_else(|_| panic!("invalid {label}: {value:?}"))
}

fn read_genomes(path: &str) -> Vec<Genome> {
    let source = BufReader::new(File::open(path).expect("open D45 parameter catalog"));
    let mut lines = source.lines();
    let expected = std::iter::once("genome".to_string())
        .chain((0..PARAMETERS).map(|index| format!("param_{index:02}")))
        .collect::<Vec<_>>()
        .join("\t");
    assert_eq!(
        lines.next().expect("D45 parameter header").unwrap(),
        expected
    );
    let mut genomes = Vec::new();
    for line in lines {
        let line = line.expect("read D45 parameter row");
        let fields: Vec<_> = line.split('\t').collect();
        assert_eq!(fields.len(), PARAMETERS + 1);
        let mut theta = [0.0f32; PARAMETERS];
        for (target, value) in theta.iter_mut().zip(&fields[1..]) {
            *target = parse(value, "D45 parameter");
            assert!(target.is_finite());
        }
        genomes.push(Genome {
            label: fields[0].to_string(),
            theta,
        });
    }
    assert!(!genomes.is_empty(), "empty D45 parameter catalog");
    assert_eq!(
        genomes
            .iter()
            .filter(|genome| genome.label == "zero")
            .count(),
        1,
        "D45 catalog requires one zero genome"
    );
    genomes
}

fn policy_features(row: &[f32; 44]) -> [f32; PARAMETERS] {
    let mut values = [0.0f32; PARAMETERS];
    values[..18].copy_from_slice(&row[20..38]);
    values[18] = row[42];
    values[19] = row[43];
    for kind in 0..6 {
        values[20 + kind] = (row[1] - 0.5) * row[20 + kind];
        values[26 + kind] = row[2] * row[20 + kind];
    }
    assert!(values.iter().all(|value| value.is_finite()));
    values
}

fn parametric_action(observation: &MacroCandidateObservation, theta: &[f32; PARAMETERS]) -> usize {
    let order = exact_prior_order(
        &observation.features,
        &observation.actions,
        observation.branch as u8,
    );
    if observation.branch != MacroSelectionBranch::Rate {
        return observation.actions[order[0]] as usize;
    }
    let denominator = (order.len().saturating_sub(1)).max(1) as f32;
    let mut best_candidate = order[0];
    let mut best_rank = 0usize;
    let mut best_score = f32::NEG_INFINITY;
    for (rank, &candidate) in order.iter().enumerate() {
        let features = policy_features(&observation.features[candidate]);
        let score = -(rank as f32) / denominator
            + theta
                .iter()
                .zip(features)
                .map(|(weight, feature)| weight * feature)
                .sum::<f32>();
        assert!(score.is_finite());
        let action = observation.actions[candidate];
        let best_action = observation.actions[best_candidate];
        if score.total_cmp(&best_score).is_gt()
            || (score.total_cmp(&best_score).is_eq() && (rank, action) < (best_rank, best_action))
        {
            best_candidate = candidate;
            best_rank = rank;
            best_score = score;
        }
    }
    observation.actions[best_candidate] as usize
}

fn play(task: Task, genome: usize, theta: &[f32; PARAMETERS]) -> Row {
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
        assert!(decisions <= 5_000, "D45 decision loop on {task:?}");
        let observation = env.candidate_observation();
        let action = parametric_action(&observation, theta);
        assert!(
            env.legal_actions().contains(&action),
            "D45 chose illegal action"
        );
        action_planes[action / MACRO_CELLS] += 1;
        terminal = env.step(action);
        if env.state.turn == last_turn {
            stagnant += 1;
        } else {
            last_turn = env.state.turn;
            stagnant = 0;
        }
        assert!(stagnant <= 16, "D45 zero-time loop on {task:?}");
    }
    Row {
        genome,
        task,
        terminal,
        action_planes,
    }
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(
        args.len(),
        6,
        "usage: d45_rate_surface PARAMS START_SEED MAPS OUTPUT THREADS"
    );
    let genomes = Arc::new(read_genomes(&args[1]));
    let start_seed = parse(&args[2], "start seed");
    let maps: usize = parse(&args[3], "maps");
    let output = &args[4];
    let threads: usize = parse(&args[5], "threads");
    assert!(maps > 0 && threads > 0);
    let work: Vec<_> = (0..genomes.len())
        .flat_map(|genome| {
            (start_seed..start_seed + maps as i64).flat_map(move |map_seed| {
                (0..2).flat_map(move |seat| {
                    (0..MacroOpponentMode::ALL.len()).map(move |opponent| Work {
                        genome,
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
            let genomes = Arc::clone(&genomes);
            let work = Arc::clone(&work);
            let next = Arc::clone(&next);
            let rows = Arc::clone(&rows);
            thread::spawn(move || loop {
                let index = next.fetch_add(1, Ordering::Relaxed);
                let Some(item) = work.get(index) else {
                    break;
                };
                let row = play(item.task, item.genome, &genomes[item.genome].theta);
                rows.lock().expect("D45 row lock").push(row);
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D45 worker thread");
    }
    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole D45 row owner")
        .into_inner()
        .expect("D45 row lock");
    rows.sort_by_key(|row| {
        (
            genomes[row.genome].label.clone(),
            row.task.map_seed,
            row.task.seat,
            row.task.opponent,
        )
    });

    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(output)
        .expect("create D45 output without overwrite");
    let mut writer = BufWriter::new(target);
    writeln!(writer, "map_seed\tseat\topponent\tgenome\tturn\town_score\topponent_score\tmargin\town_return\topponent_return\tmargin_return\town_workers\topponent_workers\tsuccessful_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tselected_decisions\tselected_jobs\tselected_nonidle_jobs\tselected_renew_jobs\town_created_crops\topponent_created_crops\tambiguous_created_crops\taction_hash\tstate_hash\ttrain_none\ttrain_producer\ttrain_chopper\tidle\tbank\tfell_bank\tharvest_bank\trenew\tmine_bank\tdeposit_prediction_failures").expect("write D45 header");
    for row in &rows {
        let terminal = row.terminal;
        writeln!(
            writer,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{:.6}\t{:.6}\t{:.6}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
            row.task.map_seed,
            row.task.seat,
            MacroOpponentMode::from_index(row.task.opponent).label(),
            genomes[row.genome].label,
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
        )
        .expect("write D45 row");
    }
    writer.flush().expect("flush D45 output");
    eprintln!(
        "saved {} genomes x {} maps x 16 tasks = {} rows in {:.3}s",
        genomes.len(),
        maps,
        rows.len(),
        started.elapsed().as_secs_f64(),
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn zero_parameters_preserve_exact_d40_actions() {
        let theta = [0.0; PARAMETERS];
        for opponent in [0, 1, 4, 7] {
            let mut env =
                CompleteMacroEnv::new(9_670_000, 0, MacroOpponentMode::from_index(opponent));
            for _ in 0..120 {
                let observation = env.candidate_observation();
                let selected = parametric_action(&observation, &theta);
                assert_eq!(
                    selected,
                    observation.actions[observation.teacher_index] as usize
                );
                if env.step(selected).done {
                    break;
                }
            }
        }
    }

    #[test]
    fn policy_feature_layout_is_finite() {
        let env = CompleteMacroEnv::new(9_670_001, 1, MacroOpponentMode::GoldAdaptive);
        let observation = env.candidate_observation();
        for row in &observation.features {
            let features = policy_features(row);
            assert!(features.iter().all(|value| value.is_finite()));
            assert_eq!(&features[..18], &row[20..38]);
            assert_eq!(features[18], row[42]);
            assert_eq!(features[19], row[43]);
        }
    }
}
