//! Export deployable root/arm features for the consumed D82 rollout bank.

use std::fs::OpenOptions;
use std::io::{BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

use troll_farm::d41b_prior_kernel::exact_prior_order;
use troll_farm::rl_macro::{
    CompleteMacroEnv, MacroOpponentMode, MacroSelectionBranch, D42_JOB_CONTEXT_FEATURES,
    D42_SHARED_CONTEXT_FEATURES, MACRO_CANDIDATE_FEATURES, MACRO_CELLS,
};

const FEATURES: usize =
    D42_SHARED_CONTEXT_FEATURES + 2 * (MACRO_CANDIDATE_FEATURES + D42_JOB_CONTEXT_FEATURES) + 3;

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
enum Arm {
    Control,
    Fell,
    Harvest,
    Renew,
}

impl Arm {
    fn label(self) -> &'static str {
        match self {
            Self::Control => "control",
            Self::Fell => "fell",
            Self::Harvest => "harvest",
            Self::Renew => "renew",
        }
    }

    fn from_plane(plane: usize) -> Self {
        match plane {
            5 => Self::Fell,
            6 => Self::Harvest,
            7 => Self::Renew,
            _ => panic!("nonsemantic D83 plane {plane}"),
        }
    }

    fn one_hot(self) -> [f32; 3] {
        match self {
            Self::Control => [0.0, 0.0, 0.0],
            Self::Fell => [1.0, 0.0, 0.0],
            Self::Harvest => [0.0, 1.0, 0.0],
            Self::Renew => [0.0, 0.0, 1.0],
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
    opponent: usize,
}

struct FeatureRow {
    task: Task,
    arm: Arm,
    root_seen: u32,
    root_turn: i32,
    root_state_hash: u64,
    root_candidate_count: u32,
    prior_rank: i32,
    action: i32,
    values: [f32; FEATURES],
}

fn parse<T: std::str::FromStr>(value: &str, label: &str) -> T {
    value
        .parse()
        .unwrap_or_else(|_| panic!("invalid {label}: {value:?}"))
}

fn threatened_own_crop(action: i32, features: &[f32; 44], context: &[f32; 16]) -> bool {
    matches!(action as usize / MACRO_CELLS, 5..=7) && features[31] > 0.5 && context[13] > 0.5
}

fn feature_vector(
    shared: &[f32; D42_SHARED_CONTEXT_FEATURES],
    control: &[f32; MACRO_CANDIDATE_FEATURES],
    control_context: &[f32; D42_JOB_CONTEXT_FEATURES],
    response: &[f32; MACRO_CANDIDATE_FEATURES],
    response_context: &[f32; D42_JOB_CONTEXT_FEATURES],
    arm: Arm,
) -> [f32; FEATURES] {
    let mut values = [0.0f32; FEATURES];
    let mut offset = 0;
    for source in [
        shared.as_slice(),
        control.as_slice(),
        control_context.as_slice(),
        response.as_slice(),
        response_context.as_slice(),
        arm.one_hot().as_slice(),
    ] {
        values[offset..offset + source.len()].copy_from_slice(source);
        offset += source.len();
    }
    assert_eq!(offset, FEATURES);
    assert!(values.iter().all(|value| value.is_finite()));
    values
}

fn trace(task: Task) -> Vec<FeatureRow> {
    let mut env = CompleteMacroEnv::new(
        task.map_seed,
        task.seat,
        MacroOpponentMode::from_index(task.opponent),
    );
    loop {
        let observation = env.candidate_observation();
        let teacher = observation.actions[observation.teacher_index];
        if observation.branch == MacroSelectionBranch::Rate {
            let order = exact_prior_order(
                &observation.features,
                &observation.actions,
                observation.branch as u8,
            );
            assert_eq!(observation.actions[order[0]], teacher);
            let mut responses: [Option<(usize, usize)>; 3] = [None; 3];
            for (rank, &candidate) in order.iter().enumerate() {
                let action = observation.actions[candidate];
                let plane = action as usize / MACRO_CELLS;
                if !(5..=7).contains(&plane)
                    || observation.features[candidate][31] <= 0.5
                    || action == teacher
                    || responses[plane - 5].is_some()
                {
                    continue;
                }
                let context = env.d42_job_context(action);
                if threatened_own_crop(action, &observation.features[candidate], &context) {
                    responses[plane - 5] = Some((rank, candidate));
                }
            }
            if responses.iter().any(Option::is_some) {
                let shared = env.d42_shared_context();
                let control_candidate = order[0];
                let control_context = env.d42_job_context(teacher);
                let root_turn = env.state.turn;
                let root_state_hash = env.state_hash();
                let root_candidate_count = observation.actions.len() as u32;
                let mut rows = vec![FeatureRow {
                    task,
                    arm: Arm::Control,
                    root_seen: 1,
                    root_turn,
                    root_state_hash,
                    root_candidate_count,
                    prior_rank: 0,
                    action: teacher,
                    values: feature_vector(
                        &shared,
                        &observation.features[control_candidate],
                        &control_context,
                        &observation.features[control_candidate],
                        &control_context,
                        Arm::Control,
                    ),
                }];
                for (plane_offset, response) in responses.into_iter().enumerate() {
                    let Some((rank, candidate)) = response else {
                        continue;
                    };
                    let arm = Arm::from_plane(plane_offset + 5);
                    let action = observation.actions[candidate];
                    let context = env.d42_job_context(action);
                    rows.push(FeatureRow {
                        task,
                        arm,
                        root_seen: 1,
                        root_turn,
                        root_state_hash,
                        root_candidate_count,
                        prior_rank: rank as i32,
                        action,
                        values: feature_vector(
                            &shared,
                            &observation.features[control_candidate],
                            &control_context,
                            &observation.features[candidate],
                            &context,
                            arm,
                        ),
                    });
                }
                return rows;
            }
        }
        if env.step(teacher as usize).done {
            return vec![FeatureRow {
                task,
                arm: Arm::Control,
                root_seen: 0,
                root_turn: -1,
                root_state_hash: 0,
                root_candidate_count: 0,
                prior_rank: -1,
                action: -1,
                values: [0.0; FEATURES],
            }];
        }
    }
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(
        args.len(),
        5,
        "usage: d83_threatened_response_features START_SEED MAPS OUTPUT THREADS"
    );
    let start_seed = parse(&args[1], "start seed");
    let maps: usize = parse(&args[2], "maps");
    let output = &args[3];
    let threads: usize = parse(&args[4], "threads");
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
    let tasks = Arc::new(tasks);
    let next = Arc::new(AtomicUsize::new(0));
    let rows = Arc::new(Mutex::new(Vec::new()));
    let started = Instant::now();
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
                let mut traced = trace(task);
                rows.lock().expect("D83 row lock").append(&mut traced);
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D83 worker thread");
    }
    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole D83 row owner")
        .into_inner()
        .expect("D83 row lock");
    rows.sort_by_key(|row| (row.task, row.arm));

    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(output)
        .expect("create D83 output without overwrite");
    let mut writer = BufWriter::new(target);
    write!(writer, "map_seed\tseat\topponent\tarm\troot_seen\troot_turn\troot_state_hash\troot_candidate_count\tprior_rank\taction").expect("write D83 identity header");
    for feature in 0..FEATURES {
        write!(writer, "\tfeature_{feature:03}").expect("write D83 feature header");
    }
    writeln!(writer).expect("finish D83 header");
    for row in &rows {
        write!(
            writer,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
            row.task.map_seed,
            row.task.seat,
            MacroOpponentMode::from_index(row.task.opponent).label(),
            row.arm.label(),
            row.root_seen,
            row.root_turn,
            row.root_state_hash,
            row.root_candidate_count,
            row.prior_rank,
            row.action,
        )
        .expect("write D83 identity row");
        for value in row.values {
            write!(writer, "\t{value:.8}").expect("write D83 feature");
        }
        writeln!(writer).expect("finish D83 row");
    }
    writer.flush().expect("flush D83 output");
    eprintln!(
        "saved {} D83 feature rows in {:.3}s",
        rows.len(),
        started.elapsed().as_secs_f64(),
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn feature_layout_has_169_values() {
        assert_eq!(FEATURES, 169);
        let values = feature_vector(
            &[0.0; 46],
            &[0.0; 44],
            &[0.0; 16],
            &[0.0; 44],
            &[0.0; 16],
            Arm::Renew,
        );
        assert_eq!(&values[166..], &[0.0, 0.0, 1.0]);
    }

    #[test]
    fn traced_semantic_rows_preserve_threat_features() {
        let rows = trace(Task {
            map_seed: 9_914_000,
            seat: 0,
            opponent: 4,
        });
        assert_eq!(rows[0].arm, Arm::Control);
        for row in rows.iter().skip(1) {
            assert_eq!(row.values[106 + 31], 1.0);
            assert_eq!(row.values[150 + 13], 1.0);
            assert!(row.values.iter().all(|value| value.is_finite()));
        }
    }
}
