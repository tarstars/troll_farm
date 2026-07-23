//! Exact paired D41d rank-one action continuations from a frozen state manifest.

use std::collections::{BTreeMap, BTreeSet};
use std::fs::File;
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

use troll_farm::d41b_prior_kernel::exact_prior_order;
use troll_farm::rl_macro::{CompleteMacroEnv, MacroOpponentMode, MacroTerminal, MACRO_TOTAL_TURNS};

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
    opponent: usize,
}

#[derive(Clone, Debug)]
struct Sample {
    sample_id: usize,
    cohort: String,
    task: Task,
    task_index: u64,
    opponent_label: String,
    decision_ordinal: usize,
    turn: i32,
    branch: u8,
    branch_label: String,
    phase: String,
    candidate_count: usize,
    teacher_action: i32,
    alternative_action: i32,
    residual_gap: f32,
    control_hash: String,
}

#[derive(Clone, Debug)]
struct Row {
    sample: Sample,
    baseline: MacroTerminal,
    treatment: MacroTerminal,
    elapsed_us: u128,
}

fn parse<T: std::str::FromStr>(value: &str, label: &str) -> T {
    value
        .parse()
        .unwrap_or_else(|_| panic!("invalid {label}: {value:?}"))
}

fn read_manifest(path: &str, limit: Option<usize>) -> Vec<Sample> {
    let source = BufReader::new(File::open(path).expect("open D41d manifest"));
    let mut lines = source.lines();
    let header = lines.next().expect("D41d manifest header").unwrap();
    assert_eq!(
        header,
        "sample_id\tcohort\tmap_seed\ttask_index\tseat\topponent_index\topponent\tdecision_ordinal\tturn\tbranch_index\tbranch\tphase\tcandidate_count\tteacher_action\talternative_action\tresidual_gap\tcontrol_hash"
    );
    let mut samples = Vec::new();
    for line in lines {
        if limit.is_some_and(|maximum| samples.len() >= maximum) {
            break;
        }
        let line = line.expect("read D41d manifest row");
        let fields: Vec<_> = line.split('\t').collect();
        assert_eq!(fields.len(), 17, "malformed D41d manifest row");
        let opponent = parse(fields[5], "opponent index");
        let branch = parse(fields[9], "branch index");
        assert_eq!(MacroOpponentMode::from_index(opponent).label(), fields[6]);
        assert_eq!(
            ["train", "deficit", "evacuation", "rate"][branch as usize],
            fields[10]
        );
        samples.push(Sample {
            sample_id: parse(fields[0], "sample ID"),
            cohort: fields[1].to_string(),
            task: Task {
                map_seed: parse(fields[2], "map seed"),
                seat: parse(fields[4], "seat"),
                opponent,
            },
            task_index: parse(fields[3], "task index"),
            opponent_label: fields[6].to_string(),
            decision_ordinal: parse(fields[7], "decision ordinal"),
            turn: parse(fields[8], "turn"),
            branch,
            branch_label: fields[10].to_string(),
            phase: fields[11].to_string(),
            candidate_count: parse(fields[12], "candidate count"),
            teacher_action: parse(fields[13], "teacher action"),
            alternative_action: parse(fields[14], "alternative action"),
            residual_gap: parse(fields[15], "residual gap"),
            control_hash: fields[16].to_string(),
        });
    }
    assert!(!samples.is_empty(), "empty D41d manifest");
    assert_eq!(
        samples.len(),
        samples
            .iter()
            .map(|sample| sample.sample_id)
            .collect::<BTreeSet<_>>()
            .len(),
        "duplicate D41d sample ID"
    );
    samples
}

fn make_env(task: Task) -> CompleteMacroEnv {
    CompleteMacroEnv::new(
        task.map_seed,
        task.seat,
        MacroOpponentMode::from_index(task.opponent),
    )
}

fn baseline(task: Task) -> MacroTerminal {
    let mut env = make_env(task);
    env.run_work_conserving_deficit_heuristic()
}

fn treatment(sample: &Sample) -> MacroTerminal {
    let mut env = make_env(sample.task);
    for ordinal in 0..5_000usize {
        let observation = env.candidate_observation();
        let teacher_action = observation.actions[observation.teacher_index];
        if ordinal == sample.decision_ordinal {
            let turn = (observation.features[0][1] * MACRO_TOTAL_TURNS as f32).round() as i32;
            assert_eq!(turn, sample.turn, "D41d replay turn mismatch");
            assert_eq!(
                observation.branch as u8, sample.branch,
                "D41d branch mismatch"
            );
            assert_eq!(
                observation.actions.len(),
                sample.candidate_count,
                "D41d candidate-count mismatch"
            );
            assert_eq!(
                teacher_action, sample.teacher_action,
                "D41d teacher-action mismatch"
            );
            let order = exact_prior_order(
                &observation.features,
                &observation.actions,
                observation.branch as u8,
            );
            assert!(order.len() >= 2, "D41d proposal state became singleton");
            assert_eq!(
                observation.actions[order[1]], sample.alternative_action,
                "D41d rank-one action mismatch"
            );
            let terminal = env.step(sample.alternative_action as usize);
            return if terminal.done {
                terminal
            } else {
                env.run_work_conserving_deficit_heuristic()
            };
        }
        let terminal = env.step(teacher_action as usize);
        assert!(!terminal.done, "D41d task ended before manifest decision");
    }
    panic!("D41d manifest decision loop");
}

fn parallel_baselines(samples: &[Sample], threads: usize) -> BTreeMap<Task, MacroTerminal> {
    let tasks: Vec<_> = samples
        .iter()
        .map(|sample| sample.task)
        .collect::<BTreeSet<_>>()
        .into_iter()
        .collect();
    let tasks = Arc::new(tasks);
    let next = Arc::new(AtomicUsize::new(0));
    let rows = Arc::new(Mutex::new(BTreeMap::new()));
    let handles: Vec<_> = (0..threads.min(tasks.len()))
        .map(|_| {
            let tasks = Arc::clone(&tasks);
            let next = Arc::clone(&next);
            let rows = Arc::clone(&rows);
            thread::spawn(move || loop {
                let index = next.fetch_add(1, Ordering::Relaxed);
                let Some(&task) = tasks.get(index) else {
                    break;
                };
                rows.lock()
                    .expect("D41d baseline lock")
                    .insert(task, baseline(task));
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D41d baseline thread");
    }
    Arc::try_unwrap(rows)
        .ok()
        .expect("sole D41d baseline map")
        .into_inner()
        .expect("D41d baseline map lock")
}

fn parallel_treatments(
    samples: &[Sample],
    baselines: &BTreeMap<Task, MacroTerminal>,
    threads: usize,
) -> Vec<Row> {
    let samples = Arc::new(samples.to_vec());
    let baselines = Arc::new(baselines.clone());
    let next = Arc::new(AtomicUsize::new(0));
    let rows = Arc::new(Mutex::new(Vec::with_capacity(samples.len())));
    let handles: Vec<_> = (0..threads.min(samples.len()))
        .map(|_| {
            let samples = Arc::clone(&samples);
            let baselines = Arc::clone(&baselines);
            let next = Arc::clone(&next);
            let rows = Arc::clone(&rows);
            thread::spawn(move || loop {
                let index = next.fetch_add(1, Ordering::Relaxed);
                let Some(sample) = samples.get(index) else {
                    break;
                };
                let started = Instant::now();
                let terminal = treatment(sample);
                rows.lock().expect("D41d row lock").push(Row {
                    sample: sample.clone(),
                    baseline: baselines[&sample.task],
                    treatment: terminal,
                    elapsed_us: started.elapsed().as_micros(),
                });
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D41d treatment thread");
    }
    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole D41d rows")
        .into_inner()
        .expect("D41d rows lock");
    rows.sort_by_key(|row| row.sample.sample_id);
    rows
}

fn terminal_columns(terminal: MacroTerminal) -> [String; 13] {
    [
        terminal.own_score.to_string(),
        terminal.opponent_score.to_string(),
        (terminal.own_score - terminal.opponent_score).to_string(),
        terminal.own_workers.to_string(),
        terminal.opponent_workers.to_string(),
        terminal.own_created_crops.to_string(),
        terminal.successful_trains.to_string(),
        terminal.invalidated_jobs.to_string(),
        terminal.invalid_direct_commands.to_string(),
        terminal.provenance_failures.to_string(),
        terminal.deposit_prediction_failures.to_string(),
        terminal.action_hash.to_string(),
        terminal.state_hash.to_string(),
    ]
}

fn write_rows(path: &str, rows: &[Row]) {
    let mut target = BufWriter::new(File::create(path).expect("create D41d output"));
    writeln!(target, "sample_id\tcohort\tmap_seed\ttask_index\tseat\topponent_index\topponent\tdecision_ordinal\tturn\tbranch_index\tbranch\tphase\tcandidate_count\tteacher_action\talternative_action\tresidual_gap\tcontrol_hash\tbaseline_own_score\tbaseline_opponent_score\tbaseline_margin\tbaseline_own_workers\tbaseline_opponent_workers\tbaseline_own_created_crops\tbaseline_successful_trains\tbaseline_invalidated_jobs\tbaseline_invalid_direct_commands\tbaseline_provenance_failures\tbaseline_deposit_prediction_failures\tbaseline_action_hash\tbaseline_state_hash\ttreatment_own_score\ttreatment_opponent_score\ttreatment_margin\ttreatment_own_workers\ttreatment_opponent_workers\ttreatment_own_created_crops\ttreatment_successful_trains\ttreatment_invalidated_jobs\ttreatment_invalid_direct_commands\ttreatment_provenance_failures\ttreatment_deposit_prediction_failures\ttreatment_action_hash\ttreatment_state_hash\town_score_delta\topponent_score_delta\tmargin_delta\telapsed_us").expect("write D41d header");
    for row in rows {
        let sample = &row.sample;
        let baseline = terminal_columns(row.baseline);
        let treatment = terminal_columns(row.treatment);
        let mut fields = vec![
            sample.sample_id.to_string(),
            sample.cohort.clone(),
            sample.task.map_seed.to_string(),
            sample.task_index.to_string(),
            sample.task.seat.to_string(),
            sample.task.opponent.to_string(),
            sample.opponent_label.clone(),
            sample.decision_ordinal.to_string(),
            sample.turn.to_string(),
            sample.branch.to_string(),
            sample.branch_label.clone(),
            sample.phase.clone(),
            sample.candidate_count.to_string(),
            sample.teacher_action.to_string(),
            sample.alternative_action.to_string(),
            format!("{:.9}", sample.residual_gap),
            sample.control_hash.clone(),
        ];
        fields.extend(baseline);
        fields.extend(treatment);
        fields.push((row.treatment.own_score - row.baseline.own_score).to_string());
        fields.push((row.treatment.opponent_score - row.baseline.opponent_score).to_string());
        fields.push(
            ((row.treatment.own_score - row.treatment.opponent_score)
                - (row.baseline.own_score - row.baseline.opponent_score))
                .to_string(),
        );
        fields.push(row.elapsed_us.to_string());
        writeln!(target, "{}", fields.join("\t")).expect("write D41d row");
    }
    target.flush().expect("flush D41d output");
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    let manifest = args.get(1).expect("D41d manifest path");
    let output = args.get(2).expect("D41d output path");
    let threads = args.get(3).map_or(20, |value| parse(value, "thread count"));
    let limit = args.get(4).map(|value| parse(value, "sample limit"));
    assert!(threads > 0);
    let samples = read_manifest(manifest, limit);
    let started = Instant::now();
    let baselines = parallel_baselines(&samples, threads);
    let rows = parallel_treatments(&samples, &baselines, threads);
    write_rows(output, &rows);
    eprintln!(
        "saved {} D41d rows over {} baseline tasks in {:.3}s to {}",
        rows.len(),
        baselines.len(),
        started.elapsed().as_secs_f64(),
        output,
    );
}
