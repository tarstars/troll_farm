//! Replay consumed D42 states and export the exact 154-feature D43 actor ABI.

use std::collections::{BTreeMap, BTreeSet};
use std::fs::{File, OpenOptions};
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

use troll_farm::d41b_prior_kernel::exact_prior_order;
use troll_farm::rl_macro::{
    CompleteMacroEnv, MacroCandidateObservation, MacroOpponentMode, MACRO_MAX_CANDIDATES,
    MACRO_TOTAL_TURNS,
};

const FEATURES: usize = 154;
const EXPECTED_ROWS: usize = 1_087;

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
    opponent: usize,
}

#[derive(Clone, Debug)]
struct Sample {
    sample_id: usize,
    task: Task,
    decision_ordinal: usize,
    turn: i32,
    branch: u8,
    candidate_count: usize,
    teacher_action: i32,
    alternative_action: i32,
    residual_gap: f32,
}

#[derive(Clone, Debug)]
struct Row {
    sample: Sample,
    features: [f32; FEATURES],
}

fn parse<T: std::str::FromStr>(value: &str, label: &str) -> T {
    value
        .parse()
        .unwrap_or_else(|_| panic!("invalid {label}: {value:?}"))
}

fn read_manifest(path: &str) -> Vec<Sample> {
    let source = BufReader::new(File::open(path).expect("open D44a manifest"));
    let mut lines = source.lines();
    let header = lines.next().expect("D44a manifest header").unwrap();
    assert_eq!(
        header,
        "sample_id\tcohort\tmap_seed\ttask_index\tseat\topponent_index\topponent\tdecision_ordinal\tturn\tbranch_index\tbranch\tphase\tcandidate_count\tteacher_action\talternative_action\tresidual_gap\tcontrol_hash"
    );
    let mut samples = Vec::new();
    for line in lines {
        let line = line.expect("read D44a manifest row");
        let fields: Vec<_> = line.split('\t').collect();
        assert_eq!(fields.len(), 17, "malformed D44a manifest row");
        let opponent = parse(fields[5], "opponent index");
        let branch = parse(fields[9], "branch index");
        assert_eq!(MacroOpponentMode::from_index(opponent).label(), fields[6]);
        assert_eq!(
            ["train", "deficit", "evacuation", "rate"][branch as usize],
            fields[10]
        );
        samples.push(Sample {
            sample_id: parse(fields[0], "sample ID"),
            task: Task {
                map_seed: parse(fields[2], "map seed"),
                seat: parse(fields[4], "seat"),
                opponent,
            },
            decision_ordinal: parse(fields[7], "decision ordinal"),
            turn: parse(fields[8], "turn"),
            branch,
            candidate_count: parse(fields[12], "candidate count"),
            teacher_action: parse(fields[13], "teacher action"),
            alternative_action: parse(fields[14], "alternative action"),
            residual_gap: parse(fields[15], "residual gap"),
        });
    }
    assert_eq!(
        samples.len(),
        EXPECTED_ROWS,
        "unexpected D44a manifest size"
    );
    assert_eq!(
        samples
            .iter()
            .map(|sample| sample.sample_id)
            .collect::<BTreeSet<_>>(),
        (0..EXPECTED_ROWS).collect(),
        "D44a sample IDs are not complete"
    );
    samples
}

fn d43_features(observation: &MacroCandidateObservation, residual_gap: f32) -> [f32; FEATURES] {
    let order = exact_prior_order(
        &observation.features,
        &observation.actions,
        observation.branch as u8,
    );
    assert!(order.len() >= 2, "D44a state lost rank one");
    let rank_zero = &observation.features[order[0]];
    let rank_one = &observation.features[order[1]];
    let mut values = Vec::with_capacity(FEATURES);
    values.extend_from_slice(&rank_zero[..17]);
    values.extend_from_slice(&rank_zero[17..44]);
    values.extend_from_slice(&rank_one[17..44]);
    values.extend(
        rank_one[17..44]
            .iter()
            .zip(&rank_zero[17..44])
            .map(|(one, zero)| one - zero),
    );
    for feature in 17..44 {
        values.push(
            observation
                .features
                .iter()
                .map(|row| row[feature])
                .sum::<f32>()
                / observation.features.len() as f32,
        );
    }
    for feature in 17..44 {
        values.push(
            observation
                .features
                .iter()
                .map(|row| row[feature])
                .fold(f32::NEG_INFINITY, f32::max),
        );
    }
    values.push(residual_gap);
    values.push(observation.features.len() as f32 / MACRO_MAX_CANDIDATES as f32);
    assert_eq!(values.len(), FEATURES);
    assert!(values.iter().all(|value| value.is_finite()));
    values.try_into().expect("D44a exact feature count")
}

fn replay_task(task: Task, samples: &[Sample]) -> Vec<Row> {
    let mut by_ordinal: BTreeMap<usize, Vec<&Sample>> = BTreeMap::new();
    for sample in samples {
        assert_eq!(sample.task, task);
        by_ordinal
            .entry(sample.decision_ordinal)
            .or_default()
            .push(sample);
    }
    let last = *by_ordinal.keys().next_back().expect("D44a task sample");
    let mut env = CompleteMacroEnv::new(
        task.map_seed,
        task.seat,
        MacroOpponentMode::from_index(task.opponent),
    );
    let mut rows = Vec::with_capacity(samples.len());
    for ordinal in 0..=last {
        let observation = env.candidate_observation();
        let teacher_action = observation.actions[observation.teacher_index];
        if let Some(at_ordinal) = by_ordinal.get(&ordinal) {
            for sample in at_ordinal {
                let turn = (observation.features[0][1] * MACRO_TOTAL_TURNS as f32).round() as i32;
                assert_eq!(turn, sample.turn, "D44a replay turn mismatch");
                assert_eq!(
                    observation.branch as u8, sample.branch,
                    "D44a branch mismatch"
                );
                assert_eq!(
                    observation.actions.len(),
                    sample.candidate_count,
                    "D44a candidate-count mismatch"
                );
                assert_eq!(
                    teacher_action, sample.teacher_action,
                    "D44a rank-zero mismatch"
                );
                let order = exact_prior_order(
                    &observation.features,
                    &observation.actions,
                    observation.branch as u8,
                );
                assert_eq!(
                    observation.actions[order[1]], sample.alternative_action,
                    "D44a rank-one mismatch"
                );
                rows.push(Row {
                    sample: (*sample).clone(),
                    features: d43_features(&observation, sample.residual_gap),
                });
            }
        }
        let terminal = env.step(teacher_action as usize);
        assert!(
            !terminal.done || ordinal == last,
            "D44a task ended before final manifest decision"
        );
    }
    assert_eq!(rows.len(), samples.len());
    rows
}

fn parallel_replay(samples: Vec<Sample>, threads: usize) -> Vec<Row> {
    let mut grouped: BTreeMap<Task, Vec<Sample>> = BTreeMap::new();
    for sample in samples {
        grouped.entry(sample.task).or_default().push(sample);
    }
    let tasks: Vec<_> = grouped.into_iter().collect();
    let tasks = Arc::new(tasks);
    let next = Arc::new(AtomicUsize::new(0));
    let rows = Arc::new(Mutex::new(Vec::with_capacity(EXPECTED_ROWS)));
    let handles: Vec<_> = (0..threads.max(1).min(tasks.len()))
        .map(|_| {
            let tasks = Arc::clone(&tasks);
            let next = Arc::clone(&next);
            let rows = Arc::clone(&rows);
            thread::spawn(move || loop {
                let index = next.fetch_add(1, Ordering::Relaxed);
                let Some((task, samples)) = tasks.get(index) else {
                    break;
                };
                let mut replayed = replay_task(*task, samples);
                rows.lock().expect("D44a row lock").append(&mut replayed);
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D44a replay worker");
    }
    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole D44a row owner")
        .into_inner()
        .expect("D44a row lock");
    rows.sort_by_key(|row| row.sample.sample_id);
    assert_eq!(rows.len(), EXPECTED_ROWS);
    rows
}

fn write_rows(path: &str, rows: &[Row]) {
    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(path)
        .expect("create D44a feature output without overwrite");
    let mut target = BufWriter::new(target);
    write!(
        target,
        "sample_id\tmap_seed\tseat\topponent_index\tdecision_ordinal"
    )
    .unwrap();
    for feature in 0..FEATURES {
        write!(target, "\tfeature_{feature:03}").unwrap();
    }
    writeln!(target).unwrap();
    for row in rows {
        write!(
            target,
            "{}\t{}\t{}\t{}\t{}",
            row.sample.sample_id,
            row.sample.task.map_seed,
            row.sample.task.seat,
            row.sample.task.opponent,
            row.sample.decision_ordinal,
        )
        .unwrap();
        for value in row.features {
            write!(target, "\t{value:.9}").unwrap();
        }
        writeln!(target).unwrap();
    }
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert!(
        (3..=4).contains(&args.len()),
        "usage: d44a_d43_external_features MANIFEST OUTPUT [THREADS]"
    );
    let threads = args.get(3).map_or(20, |value| parse(value, "threads"));
    let started = Instant::now();
    let samples = read_manifest(&args[1]);
    let tasks = samples
        .iter()
        .map(|sample| sample.task)
        .collect::<BTreeSet<_>>()
        .len();
    let rows = parallel_replay(samples, threads);
    write_rows(&args[2], &rows);
    println!(
        "{{\"event\":\"d44a_features\",\"rows\":{},\"tasks\":{},\"features\":{},\"threads\":{},\"elapsed_seconds\":{:.6}}}",
        rows.len(),
        tasks,
        FEATURES,
        threads,
        started.elapsed().as_secs_f64(),
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn d43_feature_layout_is_exact_and_finite() {
        let mut env = CompleteMacroEnv::new(9_773_003, 0, MacroOpponentMode::CompactGold);
        for _ in 0..40 {
            let observation = env.candidate_observation();
            if observation.actions.len() >= 2 {
                let order = exact_prior_order(
                    &observation.features,
                    &observation.actions,
                    observation.branch as u8,
                );
                let features = d43_features(&observation, 0.25);
                assert!(features.iter().all(|value| value.is_finite()));
                assert_eq!(&features[..17], &observation.features[order[0]][..17]);
                assert_eq!(&features[17..44], &observation.features[order[0]][17..44]);
                assert_eq!(&features[44..71], &observation.features[order[1]][17..44]);
                assert_eq!(features[152], 0.25);
                assert_eq!(
                    features[153],
                    observation.features.len() as f32 / MACRO_MAX_CANDIDATES as f32
                );
                return;
            }
            let action = observation.actions[observation.teacher_index];
            assert!(!env.step(action as usize).done);
        }
        panic!("D44a test found no two-candidate decision");
    }
}
