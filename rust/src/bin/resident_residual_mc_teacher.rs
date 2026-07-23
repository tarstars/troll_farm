//! Exact one-intervention Monte Carlo labels for resident residual decisions.

use std::fs::File;
use std::io::Write;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use std::time::Instant;

use troll_farm::rl_resident_residual::{
    ResidentResidualEnv, ResidentResidualProbe, ResidentResidualTerminal, RESIDUAL_OBS_CELLS,
};

const OPPONENTS: [&str; 6] = [
    "resident",
    "gold_adaptive",
    "compact_gold",
    "norx_native_three",
    "legend_balanced",
    "mybot",
];

fn verb(command: &str) -> &str {
    command.split_whitespace().next().unwrap_or("WAIT")
}

#[derive(Clone, Copy)]
struct SplitMix64(u64);

impl SplitMix64 {
    fn next(&mut self) -> u64 {
        self.0 = self.0.wrapping_add(0x9e37_79b9_7f4a_7c15);
        let mut value = self.0;
        value = (value ^ (value >> 30)).wrapping_mul(0xbf58_476d_1ce4_e5b9);
        value = (value ^ (value >> 27)).wrapping_mul(0x94d0_49bb_1331_11eb);
        value ^ (value >> 31)
    }
}

struct Event {
    candidate_index: usize,
    env: ResidentResidualEnv,
    action: usize,
    alternative_command: String,
    probe: ResidentResidualProbe,
}

#[derive(Debug)]
struct LabelRow {
    sample_slot: usize,
    candidate_index: usize,
    candidate_count: usize,
    probe: ResidentResidualProbe,
    action: usize,
    alternative_command: String,
    baseline: ResidentResidualTerminal,
    alternative: ResidentResidualTerminal,
    elapsed_us: u128,
}

fn terminal_signature(terminal: ResidentResidualTerminal) -> (i32, i32, u16, u8, u8) {
    (
        terminal.margin,
        terminal.wood_edge,
        terminal.turns,
        terminal.workers,
        terminal.opponent_workers,
    )
}

fn sample_scenario(scenario: u64, samples: usize) -> Result<Vec<LabelRow>, String> {
    let mut env = ResidentResidualEnv::new(scenario, 300);
    let mut rng = SplitMix64(scenario ^ 0xd16a_6d63_7465_6163);
    let mut reservoir: Vec<Event> = Vec::with_capacity(samples);
    let mut candidates = 0usize;
    let baseline;
    loop {
        let keep = env.keep_action();
        for action in env
            .legal_actions()
            .into_iter()
            .filter(|action| *action != keep)
        {
            let event = Event {
                candidate_index: candidates,
                alternative_command: env.command_for_action(action),
                probe: env.probe(),
                env: env.clone(),
                action,
            };
            candidates += 1;
            if reservoir.len() < samples {
                reservoir.push(event);
            } else {
                let replacement = (rng.next() % candidates as u64) as usize;
                if replacement < samples {
                    reservoir[replacement] = event;
                }
            }
        }
        let terminal = env.step(keep);
        if terminal.done {
            baseline = terminal;
            break;
        }
    }
    if reservoir.len() != samples {
        return Err(format!(
            "scenario {scenario} exposes only {} alternative events",
            reservoir.len()
        ));
    }
    let mut fidelity = reservoir[0].env.clone();
    let fidelity_terminal = fidelity.finish_with_keep();
    if terminal_signature(fidelity_terminal) != terminal_signature(baseline) {
        return Err(format!(
            "scenario {scenario} clone fidelity mismatch: {:?} != {:?}",
            terminal_signature(fidelity_terminal),
            terminal_signature(baseline)
        ));
    }

    let mut labels = Vec::with_capacity(samples);
    for (sample_slot, event) in reservoir.into_iter().enumerate() {
        let started = Instant::now();
        let mut alternative_env = event.env;
        let first = alternative_env.step(event.action);
        let alternative = if first.done {
            first
        } else {
            alternative_env.finish_with_keep()
        };
        labels.push(LabelRow {
            sample_slot,
            candidate_index: event.candidate_index,
            candidate_count: candidates,
            probe: event.probe,
            action: event.action,
            alternative_command: event.alternative_command,
            baseline,
            alternative,
            elapsed_us: started.elapsed().as_micros(),
        });
    }
    Ok(labels)
}

fn write_rows(path: &str, rows: &[LabelRow]) -> Result<(), String> {
    let mut output = std::io::BufWriter::new(
        File::create(path).map_err(|error| format!("create {path}: {error}"))?,
    );
    writeln!(
        output,
        "scenario\tmap_seed\tseat\topponent\tsample_slot\tcandidate_index\tcandidate_count\tturn\tunit_id\tordinal\tworker_count\tx\ty\tms\tcc\thp\tchop\tfree\tcarry0\tcarry1\tcarry2\tcarry3\tcarry4\tcarry5\tinv0\tinv1\tinv2\tinv3\tinv4\tinv5\tstate_score\tstate_opponent_score\tstate_margin\tstate_wood_edge\tplants\tlocal_plant_type\tlocal_plant_health\tlocal_plant_fruits\tnear_home\tnear_iron\tresident_command\tresident_verb\tresident_plane\tprevious_command\tprevious_verb\tprevious_plane\tother_command\tother_verb\tother_plane\tintent_age\tlegal_actions\talternative_action\talternative_plane\talternative_command\talternative_verb\tbaseline_margin\talternative_margin\tmargin_advantage\tbaseline_wood_edge\talternative_wood_edge\twood_advantage\tbaseline_turn\talternative_turn\tturn_delta\tbaseline_workers\talternative_workers\tbaseline_opponent_workers\talternative_opponent_workers\tnew_catastrophe\telapsed_us"
    )
    .map_err(|error| format!("write header: {error}"))?;
    for row in rows {
        let probe = &row.probe;
        let mut fields = vec![
            probe.scenario_seed.to_string(),
            probe.map_seed.to_string(),
            probe.seat.to_string(),
            OPPONENTS[probe.opponent as usize].to_string(),
            row.sample_slot.to_string(),
            row.candidate_index.to_string(),
            row.candidate_count.to_string(),
            probe.turn.to_string(),
            probe.unit_id.to_string(),
            probe.ordinal.to_string(),
            probe.worker_count.to_string(),
            probe.x.to_string(),
            probe.y.to_string(),
            probe.ms.to_string(),
            probe.cc.to_string(),
            probe.hp.to_string(),
            probe.chop.to_string(),
            probe.free.to_string(),
        ];
        fields.extend(probe.carry.iter().map(ToString::to_string));
        fields.extend(probe.inventory.iter().map(ToString::to_string));
        fields.extend([
            probe.score.to_string(),
            probe.opponent_score.to_string(),
            (probe.score - probe.opponent_score).to_string(),
            probe.wood_edge.to_string(),
            probe.plants.to_string(),
            probe.local_plant_type.clone(),
            probe.local_plant_health.to_string(),
            probe.local_plant_fruits.to_string(),
            usize::from(probe.near_home).to_string(),
            usize::from(probe.near_iron).to_string(),
            probe.resident_command.clone(),
            verb(&probe.resident_command).to_string(),
            probe.resident_plane.to_string(),
            probe.previous_command.clone(),
            verb(&probe.previous_command).to_string(),
            probe.previous_plane.to_string(),
            probe.other_command.clone(),
            verb(&probe.other_command).to_string(),
            probe.other_plane.to_string(),
            probe.intent_age.to_string(),
            probe.legal_actions.to_string(),
            row.action.to_string(),
            (row.action / RESIDUAL_OBS_CELLS).to_string(),
            row.alternative_command.clone(),
            verb(&row.alternative_command).to_string(),
            row.baseline.margin.to_string(),
            row.alternative.margin.to_string(),
            (row.alternative.margin - row.baseline.margin).to_string(),
            row.baseline.wood_edge.to_string(),
            row.alternative.wood_edge.to_string(),
            (row.alternative.wood_edge - row.baseline.wood_edge).to_string(),
            row.baseline.turns.to_string(),
            row.alternative.turns.to_string(),
            (i32::from(row.alternative.turns) - i32::from(row.baseline.turns)).to_string(),
            row.baseline.workers.to_string(),
            row.alternative.workers.to_string(),
            row.baseline.opponent_workers.to_string(),
            row.alternative.opponent_workers.to_string(),
            usize::from(row.baseline.margin > -100 && row.alternative.margin <= -100).to_string(),
            row.elapsed_us.to_string(),
        ]);
        writeln!(output, "{}", fields.join("\t")).map_err(|error| format!("write row: {error}"))?;
    }
    output
        .flush()
        .map_err(|error| format!("flush {path}: {error}"))
}

fn run() -> Result<(), String> {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 6 {
        return Err(
            "usage: resident_residual_mc_teacher <output.tsv> <scenario-start> <scenario-count> <samples-per-scenario> <threads>"
                .to_string(),
        );
    }
    let output = &args[1];
    let start = args[2]
        .parse::<u64>()
        .map_err(|_| "invalid scenario-start".to_string())?;
    let count = args[3]
        .parse::<u64>()
        .map_err(|_| "invalid scenario-count".to_string())?;
    let samples = args[4]
        .parse::<usize>()
        .map_err(|_| "invalid samples-per-scenario".to_string())?;
    let threads = args[5]
        .parse::<usize>()
        .map_err(|_| "invalid threads".to_string())?
        .clamp(1, 64);
    if count == 0 || samples == 0 {
        return Err("scenario-count and samples-per-scenario must be positive".to_string());
    }
    let scenarios: Vec<_> = (start..start + count).collect();
    let total = scenarios.len();
    let completed = Arc::new(AtomicUsize::new(0));
    let chunk_size = scenarios.len().div_ceil(threads);
    let groups = std::thread::scope(|scope| {
        let handles: Vec<_> = scenarios
            .chunks(chunk_size)
            .map(|chunk| {
                let completed = Arc::clone(&completed);
                scope.spawn(move || {
                    let mut rows = Vec::with_capacity(chunk.len() * samples);
                    for &scenario in chunk {
                        rows.extend(sample_scenario(scenario, samples)?);
                        let done = completed.fetch_add(1, Ordering::Relaxed) + 1;
                        if done % 12 == 0 || done == total {
                            eprintln!("completed {done}/{total} scenarios");
                        }
                    }
                    Ok::<_, String>(rows)
                })
            })
            .collect();
        handles
            .into_iter()
            .map(|handle| {
                handle
                    .join()
                    .map_err(|_| "worker thread panicked".to_string())?
            })
            .collect::<Result<Vec<_>, String>>()
    })?;
    let mut rows: Vec<_> = groups.into_iter().flatten().collect();
    rows.sort_by_key(|row| (row.probe.scenario_seed, row.sample_slot));
    write_rows(output, &rows)?;
    eprintln!(
        "wrote {} exact one-intervention labels to {output}",
        rows.len()
    );
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("resident_residual_mc_teacher: {error}");
        std::process::exit(1);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn deterministic_reservoir_and_continuations() {
        let left = sample_scenario(360_000, 2).expect("first sample");
        let right = sample_scenario(360_000, 2).expect("repeat sample");
        assert_eq!(left.len(), 2);
        assert_eq!(
            left.iter()
                .map(|row| row.candidate_index)
                .collect::<Vec<_>>(),
            right
                .iter()
                .map(|row| row.candidate_index)
                .collect::<Vec<_>>()
        );
        assert_eq!(
            left.iter()
                .map(|row| row.alternative.margin - row.baseline.margin)
                .collect::<Vec<_>>(),
            right
                .iter()
                .map(|row| row.alternative.margin - row.baseline.margin)
                .collect::<Vec<_>>()
        );
    }
}
