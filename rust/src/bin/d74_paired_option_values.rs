//! Evaluate D74's frozen same-state ordinary-option continuations.

use std::collections::BTreeSet;
use std::fs::{File, OpenOptions};
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::time::Instant;

use rayon::prelude::*;

use troll_farm::rl_macro::{MacroOpponentMode, MacroTerminal};
use troll_farm::rl_opening_portfolio::{OpeningPortfolioEnv, OPENING_PORTFOLIO_FEATURES};

const ACTIONS: usize = 4;
const ACTION_LABELS: [&str; ACTIONS] = ["balanced", "harvest", "renew", "fell"];

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
    opponent: usize,
}

#[derive(Clone, Debug)]
struct Sample {
    sample_id: usize,
    partition: String,
    task: Task,
    task_index: u64,
    opponent_label: String,
    decision_ordinal: usize,
    turn: i32,
    phase: String,
    feature_hash: String,
    features: [f32; OPENING_PORTFOLIO_FEATURES],
}

#[derive(Clone, Debug)]
struct Row {
    sample: Sample,
    mode: usize,
    terminal: MacroTerminal,
    reward_identity_error: f32,
}

fn parse<T: std::str::FromStr>(value: &str, label: &str) -> T {
    value
        .parse()
        .unwrap_or_else(|_| panic!("invalid {label}: {value:?}"))
}

fn manifest_header() -> String {
    let mut fields = vec![
        "sample_id".to_string(),
        "partition".to_string(),
        "map_seed".to_string(),
        "task_index".to_string(),
        "seat".to_string(),
        "opponent_index".to_string(),
        "opponent".to_string(),
        "decision_ordinal".to_string(),
        "turn".to_string(),
        "phase".to_string(),
        "legal_mask".to_string(),
        "feature_hash".to_string(),
        "selection_hash".to_string(),
    ];
    fields.extend((0..OPENING_PORTFOLIO_FEATURES).map(|index| format!("feature_{index:02}")));
    fields.join("\t")
}

fn read_manifest(path: &str) -> Vec<Sample> {
    let source = BufReader::new(File::open(path).expect("open D74 manifest"));
    let mut lines = source.lines();
    assert_eq!(
        lines.next().expect("D74 manifest header").unwrap(),
        manifest_header()
    );
    let mut samples = Vec::new();
    for line in lines {
        let line = line.expect("read D74 manifest row");
        let fields: Vec<_> = line.split('\t').collect();
        assert_eq!(fields.len(), 13 + OPENING_PORTFOLIO_FEATURES);
        let opponent = parse(fields[5], "opponent index");
        assert_eq!(MacroOpponentMode::from_index(opponent).label(), fields[6]);
        assert_eq!(fields[10], "1111");
        let features = std::array::from_fn(|index| parse(fields[13 + index], "feature"));
        assert!(features.iter().all(|value: &f32| value.is_finite()));
        samples.push(Sample {
            sample_id: parse(fields[0], "sample ID"),
            partition: fields[1].to_string(),
            task: Task {
                map_seed: parse(fields[2], "map seed"),
                seat: parse(fields[4], "seat"),
                opponent,
            },
            task_index: parse(fields[3], "task index"),
            opponent_label: fields[6].to_string(),
            decision_ordinal: parse(fields[7], "decision ordinal"),
            turn: parse(fields[8], "turn"),
            phase: fields[9].to_string(),
            feature_hash: fields[11].to_string(),
            features,
        });
    }
    assert!(!samples.is_empty(), "empty D74 manifest");
    assert_eq!(
        samples.len(),
        samples
            .iter()
            .map(|sample| sample.sample_id)
            .collect::<BTreeSet<_>>()
            .len(),
        "duplicate D74 sample ID"
    );
    samples
}

fn features_exact(left: &[f32], right: &[f32]) -> bool {
    left.iter()
        .zip(right)
        .all(|(left, right)| left.to_bits() == right.to_bits())
}

fn evaluate(sample: &Sample, mode: usize) -> Row {
    let mut env = OpeningPortfolioEnv::new(
        sample.task.map_seed,
        sample.task.seat,
        MacroOpponentMode::from_index(sample.task.opponent),
    );
    let mut ordinal = 0usize;
    let terminal = loop {
        assert!(ordinal < 5_000, "D74 manifest decision loop");
        if ordinal == sample.decision_ordinal {
            let actual = env.features();
            assert_eq!(
                env.batch.macro_env.state.turn, sample.turn,
                "D74 turn mismatch"
            );
            assert_eq!(&env.legal_mask()[..ACTIONS], &[1, 1, 1, 1]);
            assert!(
                features_exact(&actual, &sample.features),
                "D74 feature-bit replay mismatch for sample {}",
                sample.sample_id
            );
            assert!(env.memory().source_attempts.iter().all(|value| *value == 0));
            let mut terminal = env.step(mode).terminal;
            while !terminal.done {
                terminal = env.step(0).terminal;
            }
            break terminal;
        }
        let terminal = env.step(0).terminal;
        assert!(!terminal.done, "D74 task ended before manifest boundary");
        ordinal += 1;
    };
    assert!(terminal.done);
    assert!(env.memory().source_attempts.iter().all(|value| *value == 0));
    let margin = terminal.own_score - terminal.opponent_score;
    let reward_identity_error = (terminal.margin_return - margin as f32 / 100.0).abs();
    Row {
        sample: sample.clone(),
        mode,
        terminal,
        reward_identity_error,
    }
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(
        args.len(),
        4,
        "usage: d74_paired_option_values MANIFEST OUTPUT THREADS"
    );
    let samples = read_manifest(&args[1]);
    let threads: usize = parse(&args[3], "thread count");
    assert!((1..=64).contains(&threads));
    let work: Vec<_> = samples
        .iter()
        .flat_map(|sample| (0..ACTIONS).map(move |mode| (sample, mode)))
        .collect();
    let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(threads)
        .build()
        .expect("build D74 thread pool");
    let started = Instant::now();
    let mut rows: Vec<_> = pool.install(|| {
        work.into_par_iter()
            .map(|(sample, mode)| evaluate(sample, mode))
            .collect()
    });
    rows.sort_by_key(|row| (row.sample.sample_id, row.mode));

    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&args[2])
        .expect("create D74 output without overwrite");
    let mut writer = BufWriter::new(target);
    writeln!(writer, "sample_id\tpartition\tmap_seed\ttask_index\tseat\topponent_index\topponent\tdecision_ordinal\tdecision_turn\tphase\tfeature_hash\tmode_index\tmode\tterminal_turn\town_score\topponent_score\tmargin\town_workers\topponent_workers\tsuccessful_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tdeposit_prediction_failures\tselected_decisions\tselected_jobs\tselected_nonidle_jobs\tselected_renew_jobs\town_created_crops\topponent_created_crops\tambiguous_created_crops\town_owned_crop_harvest_units\town_reinvested_crops\taction_hash\tstate_hash\treward_identity_error").expect("write D74 header");
    for row in &rows {
        let sample = &row.sample;
        let terminal = row.terminal;
        let fields = [
            sample.sample_id.to_string(),
            sample.partition.clone(),
            sample.task.map_seed.to_string(),
            sample.task_index.to_string(),
            sample.task.seat.to_string(),
            sample.task.opponent.to_string(),
            sample.opponent_label.clone(),
            sample.decision_ordinal.to_string(),
            sample.turn.to_string(),
            sample.phase.clone(),
            sample.feature_hash.clone(),
            row.mode.to_string(),
            ACTION_LABELS[row.mode].to_string(),
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
            format!("{:.8}", row.reward_identity_error),
        ];
        writeln!(writer, "{}", fields.join("\t")).expect("write D74 row");
    }
    writer.flush().expect("flush D74 output");
    eprintln!(
        "saved {} D74 rows for {} states in {:.3}s",
        rows.len(),
        samples.len(),
        started.elapsed().as_secs_f64()
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn decimal_round_trip_preserves_representative_float_bits() {
        let values = [0.0f32, 1.0, 0.280000001, 1.0 / 3.0, -0.0175000001];
        for value in values {
            let encoded = format!("{value:.9}");
            let decoded: f32 = encoded.parse().unwrap();
            assert_eq!(value.to_bits(), decoded.to_bits());
        }
    }
}
