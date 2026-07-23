//! Emit dense exact one-deviation q6 continuations for the offline D112 teacher.

use std::fs::{File, OpenOptions};
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::time::Instant;

use troll_farm::rl_macro::{MacroOpponentMode, MacroTerminal};
use troll_farm::rl_q6_proposal::{
    collect_q6_teacher_dataset, Q6TeacherArm, Q6TeacherBaseline, Q6_ACTION_FEATURES, Q6_EXPERTS,
    Q6_EXPERT_FEATURES, Q6_STATE_FEATURES,
};

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

fn read_experts(path: &str) -> (Vec<[f32; Q6_EXPERT_FEATURES]>, u64) {
    let source = BufReader::new(File::open(path).expect("open D112 q6 expert population"));
    let mut lines = source.lines();
    let expected_header = ["policy", "kind", "budget"]
        .into_iter()
        .map(str::to_string)
        .chain((0..Q6_EXPERT_FEATURES).map(|index| format!("param_{index:03}")))
        .collect::<Vec<_>>()
        .join("\t");
    assert_eq!(
        lines.next().expect("D112 expert header").unwrap(),
        expected_header
    );
    let mut experts = Vec::new();
    let mut bank_hash = 0xcbf29ce484222325;
    for line in lines {
        let fields: Vec<_> = line
            .expect("read D112 expert row")
            .split('\t')
            .map(str::to_string)
            .collect();
        assert_eq!(fields.len(), Q6_EXPERT_FEATURES + 3);
        if fields[1] != "four" {
            continue;
        }
        assert_eq!(parse::<u32>(&fields[2], "D112 expert budget"), 4);
        assert_eq!(fields[0], format!("four_{:02}", experts.len()));
        let values: Vec<f32> = fields[3..]
            .iter()
            .map(|value| {
                let parsed = parse::<f32>(value, "D112 expert weight");
                assert!(parsed.is_finite());
                parsed
            })
            .collect();
        let values: [f32; Q6_EXPERT_FEATURES] =
            values.try_into().expect("D112 expert feature width");
        for value in values {
            mix(&mut bank_hash, u64::from(value.to_bits()));
        }
        experts.push(values);
    }
    assert_eq!(experts.len(), Q6_EXPERTS);
    (experts, bank_hash)
}

fn terminal_header() -> Vec<&'static str> {
    vec![
        "turn",
        "own_score",
        "opponent_score",
        "margin",
        "own_reward",
        "opponent_reward",
        "margin_reward",
        "own_return",
        "opponent_return",
        "margin_return",
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
    ]
}

fn terminal_columns(terminal: MacroTerminal) -> Vec<String> {
    vec![
        terminal.turn.to_string(),
        terminal.own_score.to_string(),
        terminal.opponent_score.to_string(),
        (terminal.own_score - terminal.opponent_score).to_string(),
        format!("{:.8}", terminal.own_reward),
        format!("{:.8}", terminal.opponent_reward),
        format!("{:.8}", terminal.margin_reward),
        format!("{:.8}", terminal.own_return),
        format!("{:.8}", terminal.opponent_return),
        format!("{:.8}", terminal.margin_return),
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
    ]
}

fn task_columns(map_seed: i64, seat: usize, opponent: usize) -> Vec<String> {
    vec![
        map_seed.to_string(),
        seat.to_string(),
        MacroOpponentMode::from_index(opponent).label().to_string(),
    ]
}

fn write_baselines(path: &str, rows: &[Q6TeacherBaseline], expert_bank_hash: u64) {
    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(path)
        .expect("create D112 baselines");
    let mut writer = BufWriter::new(target);
    let mut header = vec!["map_seed", "seat", "opponent", "boundary_count"];
    header.extend(terminal_header());
    header.push("expert_bank_hash");
    writeln!(writer, "{}", header.join("\t")).expect("write D112 baseline header");
    for row in rows {
        let mut columns = task_columns(row.task.map_seed, row.task.seat, row.task.opponent);
        columns.push(row.boundary_count.to_string());
        columns.extend(terminal_columns(row.terminal));
        columns.push(expert_bank_hash.to_string());
        writeln!(writer, "{}", columns.join("\t")).expect("write D112 baseline");
    }
}

fn optional(value: Option<usize>) -> String {
    value.map_or_else(|| "-1".to_string(), |value| value.to_string())
}

fn write_arms(path: &str, rows: &[Q6TeacherArm], expert_bank_hash: u64) {
    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(path)
        .expect("create D112 arms");
    let mut writer = BufWriter::new(target);
    let mut header = [
        "map_seed",
        "seat",
        "opponent",
        "boundary_index",
        "baseline_boundary_count",
        "decision_ordinal",
        "root_turn",
        "root_state_hash",
        "proposal_count",
        "slot",
        "kind",
        "nonteacher",
        "first_action",
        "second_action",
        "first_teacher",
        "second_teacher",
        "first_job_kind",
        "second_job_kind",
        "first_owner",
        "second_owner",
        "first_prior_rank",
        "second_prior_rank",
        "first_target",
        "second_target",
        "supporter_count",
    ]
    .into_iter()
    .map(str::to_string)
    .collect::<Vec<_>>();
    header.extend((0..Q6_STATE_FEATURES).map(|index| format!("state_{index:03}")));
    header.extend((0..Q6_ACTION_FEATURES).map(|index| format!("action_{index:03}")));
    header.extend([
        "paired_gain".to_string(),
        "intervention_batches".to_string(),
        "encountered_boundaries".to_string(),
        "joint_batches".to_string(),
        "noncontrol_assignments".to_string(),
    ]);
    header.extend(terminal_header().into_iter().map(str::to_string));
    header.push("expert_bank_hash".to_string());
    writeln!(writer, "{}", header.join("\t")).expect("write D112 arm header");

    for row in rows {
        let mut columns = task_columns(row.task.map_seed, row.task.seat, row.task.opponent);
        columns.extend([
            row.boundary_index.to_string(),
            row.baseline_boundary_count.to_string(),
            row.decision_ordinal.to_string(),
            row.turn.to_string(),
            row.root_state_hash.to_string(),
            row.proposal_count.to_string(),
            row.slot.to_string(),
            row.kind.to_string(),
            row.nonteacher.to_string(),
            row.first_action.to_string(),
            row.second_action.to_string(),
            u8::from(row.first_teacher).to_string(),
            u8::from(row.second_teacher).to_string(),
            row.first_job_kind.to_string(),
            row.second_job_kind.to_string(),
            optional(row.first_owner),
            optional(row.second_owner),
            row.first_prior_rank.to_string(),
            row.second_prior_rank.to_string(),
            optional(row.first_target),
            optional(row.second_target),
            row.supporter_count.to_string(),
        ]);
        columns.extend(row.state_features.iter().map(|value| format!("{value:.9}")));
        columns.extend(
            row.action_features
                .iter()
                .map(|value| format!("{value:.9}")),
        );
        columns.extend([
            format!("{:.8}", row.paired_gain),
            row.intervention_batches.to_string(),
            row.encountered_boundaries.to_string(),
            row.joint_batches.to_string(),
            row.noncontrol_assignments.to_string(),
        ]);
        columns.extend(terminal_columns(row.terminal));
        columns.push(expert_bank_hash.to_string());
        writeln!(writer, "{}", columns.join("\t")).expect("write D112 arm");
    }
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(
        args.len(),
        7,
        "usage: d112_q6_dense_counterfactual_teacher EXPERTS START_SEED MAPS ARMS BASELINES THREADS"
    );
    let (experts, expert_bank_hash) = read_experts(&args[1]);
    let start_seed = parse(&args[2], "D112 start seed");
    let maps = parse(&args[3], "D112 maps");
    let threads = parse(&args[6], "D112 threads");
    let started = Instant::now();
    let dataset = collect_q6_teacher_dataset(start_seed, maps, experts, threads);
    let collection_seconds = started.elapsed().as_secs_f64();
    write_baselines(&args[5], &dataset.baselines, expert_bank_hash);
    write_arms(&args[4], &dataset.arms, expert_bank_hash);
    let total_seconds = started.elapsed().as_secs_f64();
    eprintln!(
        "saved {} D112 baselines and {} exact arms in {:.3}s total / {:.3}s collection ({:.3} arms/s end-to-end)",
        dataset.baselines.len(),
        dataset.arms.len(),
        total_seconds,
        collection_seconds,
        dataset.arms.len() as f64 / total_seconds,
    );
}
