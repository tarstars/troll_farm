//! Evaluate the frozen D60 workforce-phase semantic plan interface over exact D40.

use std::fs::OpenOptions;
use std::io::{BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

use troll_farm::d41b_prior_kernel::exact_prior_order;
use troll_farm::rl_macro::{
    CompleteMacroEnv, MacroCandidateObservation, MacroOpponentMode, MacroSelectionBranch,
    MacroTerminal, MACRO_ACTION_PLANES, MACRO_CELLS,
};

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
enum Mode {
    Balanced,
    Harvest,
    Renew,
    Fell,
}

impl Mode {
    const ALL: [Self; 4] = [Self::Balanced, Self::Harvest, Self::Renew, Self::Fell];

    fn label(self) -> &'static str {
        match self {
            Self::Balanced => "balanced",
            Self::Harvest => "harvest",
            Self::Renew => "renew",
            Self::Fell => "fell",
        }
    }

    fn job_feature(self) -> Option<usize> {
        match self {
            Self::Balanced => None,
            // MacroJobKind order: idle, bank, fell, harvest, renew, mine.
            Self::Harvest => Some(20 + 3),
            Self::Renew => Some(20 + 4),
            Self::Fell => Some(20 + 2),
        }
    }
}

#[derive(Clone, Debug)]
struct Plan {
    label: String,
    pre3: Mode,
    post3: Mode,
    direct_control: bool,
}

fn plan_catalog() -> Vec<Plan> {
    let mut plans = vec![Plan {
        label: "d40_control".to_string(),
        pre3: Mode::Balanced,
        post3: Mode::Balanced,
        direct_control: true,
    }];
    for pre3 in Mode::ALL {
        for post3 in Mode::ALL {
            plans.push(Plan {
                label: format!("pre3_{}__post3_{}", pre3.label(), post3.label()),
                pre3,
                post3,
                direct_control: false,
            });
        }
    }
    plans
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
    opponent: usize,
}

#[derive(Clone, Copy, Debug, Default)]
struct PhaseCounters {
    rate: u32,
    eligible: u32,
    overrides: u32,
}

struct Work {
    plan: usize,
    task: Task,
}

struct Row {
    plan: usize,
    task: Task,
    terminal: MacroTerminal,
    reward_identity_error: f32,
    pre3: PhaseCounters,
    post3: PhaseCounters,
    action_planes: [u32; MACRO_ACTION_PLANES],
}

fn parse<T: std::str::FromStr>(value: &str, label: &str) -> T {
    value
        .parse()
        .unwrap_or_else(|_| panic!("invalid {label}: {value:?}"))
}

fn own_workers(env: &CompleteMacroEnv) -> usize {
    env.state
        .units
        .iter()
        .filter(|unit| unit.player as usize == env.seat)
        .count()
}

fn workforce_mode(plan: &Plan, workers: usize) -> Mode {
    if workers < 2 {
        Mode::Balanced
    } else if workers == 2 {
        plan.pre3
    } else {
        plan.post3
    }
}

fn semantic_action(observation: &MacroCandidateObservation, mode: Mode) -> (usize, bool, bool) {
    let teacher = observation.actions[observation.teacher_index] as usize;
    let Some(feature) = mode.job_feature() else {
        return (teacher, false, false);
    };
    if observation.branch != MacroSelectionBranch::Rate {
        return (teacher, false, false);
    }
    let order = exact_prior_order(
        &observation.features,
        &observation.actions,
        observation.branch as u8,
    );
    let selected = order
        .into_iter()
        .find(|candidate| observation.features[*candidate][feature] > 0.5)
        .map(|candidate| observation.actions[candidate] as usize);
    match selected {
        Some(action) => (action, true, action != teacher),
        None => (teacher, false, false),
    }
}

fn play(task: Task, plan_index: usize, plan: &Plan) -> Row {
    let mut env = CompleteMacroEnv::new(
        task.map_seed,
        task.seat,
        MacroOpponentMode::from_index(task.opponent),
    );
    let mut pre3 = PhaseCounters::default();
    let mut post3 = PhaseCounters::default();
    let mut action_planes = [0u32; MACRO_ACTION_PLANES];
    let mut terminal = MacroTerminal::default();
    let mut decisions = 0usize;
    let mut last_turn = env.state.turn;
    let mut stagnant = 0usize;
    while !terminal.done {
        decisions += 1;
        assert!(decisions <= 5_000, "D60 decision loop on {task:?}");
        let observation = env.candidate_observation();
        let workers = own_workers(&env);
        let mode = workforce_mode(plan, workers);
        let (action, eligible, overridden) = if plan.direct_control {
            (
                observation.actions[observation.teacher_index] as usize,
                false,
                false,
            )
        } else {
            semantic_action(&observation, mode)
        };
        if observation.branch == MacroSelectionBranch::Rate && workers >= 2 {
            let counters = if workers == 2 { &mut pre3 } else { &mut post3 };
            counters.rate += 1;
            counters.eligible += u32::from(eligible);
            counters.overrides += u32::from(overridden);
        }
        assert!(
            env.legal_actions().contains(&action),
            "D60 chose illegal action on {task:?}"
        );
        action_planes[action / MACRO_CELLS] += 1;
        terminal = env.step(action);
        if env.state.turn == last_turn {
            stagnant += 1;
        } else {
            last_turn = env.state.turn;
            stagnant = 0;
        }
        assert!(stagnant <= 16, "D60 zero-time loop on {task:?}");
    }
    let reward_identity_error = [
        (terminal.own_return - terminal.own_score as f32 / 100.0).abs(),
        (terminal.opponent_return - terminal.opponent_score as f32 / 100.0).abs(),
        (terminal.margin_return - (terminal.own_score - terminal.opponent_score) as f32 / 100.0)
            .abs(),
    ]
    .into_iter()
    .fold(0.0f32, f32::max);
    Row {
        plan: plan_index,
        task,
        terminal,
        reward_identity_error,
        pre3,
        post3,
        action_planes,
    }
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(
        args.len(),
        5,
        "usage: d60_plan_option_upper_bound START_SEED MAPS OUTPUT THREADS"
    );
    let start_seed = parse(&args[1], "start seed");
    let maps: usize = parse(&args[2], "maps");
    let output = &args[3];
    let threads: usize = parse(&args[4], "threads");
    assert!(maps > 0 && threads > 0);
    let plans = Arc::new(plan_catalog());
    let work: Vec<_> = (0..plans.len())
        .flat_map(|plan| {
            (start_seed..start_seed + maps as i64).flat_map(move |map_seed| {
                (0..2).flat_map(move |seat| {
                    (0..MacroOpponentMode::ALL.len()).map(move |opponent| Work {
                        plan,
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
            let plans = Arc::clone(&plans);
            let work = Arc::clone(&work);
            let next = Arc::clone(&next);
            let rows = Arc::clone(&rows);
            thread::spawn(move || loop {
                let index = next.fetch_add(1, Ordering::Relaxed);
                let Some(item) = work.get(index) else {
                    break;
                };
                let row = play(item.task, item.plan, &plans[item.plan]);
                rows.lock().expect("D60 row lock").push(row);
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D60 worker thread");
    }
    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole D60 row owner")
        .into_inner()
        .expect("D60 row lock");
    rows.sort_by_key(|row| {
        (
            plans[row.plan].label.clone(),
            row.task.map_seed,
            row.task.seat,
            row.task.opponent,
        )
    });

    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(output)
        .expect("create D60 output without overwrite");
    let mut writer = BufWriter::new(target);
    writeln!(writer, "map_seed\tseat\topponent\tplan\tpre3_mode\tpost3_mode\tturn\town_score\topponent_score\tmargin\town_return\topponent_return\tmargin_return\treward_identity_error\town_workers\topponent_workers\tsuccessful_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tdeposit_prediction_failures\tselected_decisions\tselected_jobs\tselected_nonidle_jobs\tselected_renew_jobs\town_created_crops\topponent_created_crops\tambiguous_created_crops\taction_hash\tstate_hash\tpre3_rate\tpre3_eligible\tpre3_overrides\tpost3_rate\tpost3_eligible\tpost3_overrides\ttrain_none\ttrain_producer\ttrain_chopper\tidle\tbank\tfell_bank\tharvest_bank\trenew\tmine_bank").expect("write D60 header");
    for row in &rows {
        let plan = &plans[row.plan];
        let terminal = row.terminal;
        writeln!(
            writer,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{:.8}\t{:.8}\t{:.8}\t{:.8}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
            row.task.map_seed,
            row.task.seat,
            MacroOpponentMode::from_index(row.task.opponent).label(),
            plan.label,
            plan.pre3.label(),
            plan.post3.label(),
            terminal.turn,
            terminal.own_score,
            terminal.opponent_score,
            terminal.own_score - terminal.opponent_score,
            terminal.own_return,
            terminal.opponent_return,
            terminal.margin_return,
            row.reward_identity_error,
            terminal.own_workers,
            terminal.opponent_workers,
            terminal.successful_trains,
            terminal.completed_jobs,
            terminal.invalidated_jobs,
            terminal.invalid_direct_commands,
            terminal.provenance_failures,
            terminal.deposit_prediction_failures,
            terminal.selected_decisions,
            terminal.selected_jobs,
            terminal.selected_nonidle_jobs,
            terminal.selected_renew_jobs,
            terminal.own_created_crops,
            terminal.opponent_created_crops,
            terminal.ambiguous_created_crops,
            terminal.action_hash,
            terminal.state_hash,
            row.pre3.rate,
            row.pre3.eligible,
            row.pre3.overrides,
            row.post3.rate,
            row.post3.eligible,
            row.post3.overrides,
            row.action_planes[0],
            row.action_planes[1],
            row.action_planes[2],
            row.action_planes[3],
            row.action_planes[4],
            row.action_planes[5],
            row.action_planes[6],
            row.action_planes[7],
            row.action_planes[8],
        )
        .expect("write D60 row");
    }
    writer.flush().expect("flush D60 output");
    eprintln!(
        "saved {} plans x {} maps x 16 tasks = {} rows in {:.3}s",
        plans.len(),
        maps,
        rows.len(),
        started.elapsed().as_secs_f64(),
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn catalog_is_control_plus_complete_unique_cartesian_product() {
        let plans = plan_catalog();
        assert_eq!(plans.len(), 17);
        let labels: std::collections::BTreeSet<_> =
            plans.iter().map(|plan| plan.label.as_str()).collect();
        assert_eq!(labels.len(), plans.len());
        assert!(labels.contains("d40_control"));
        assert!(labels.contains("pre3_balanced__post3_balanced"));
        assert!(labels.contains("pre3_fell__post3_renew"));
    }

    #[test]
    fn workforce_phase_routing_has_no_turn_clock() {
        let plan = Plan {
            label: "test".to_string(),
            pre3: Mode::Harvest,
            post3: Mode::Fell,
            direct_control: false,
        };
        assert_eq!(workforce_mode(&plan, 1), Mode::Balanced);
        assert_eq!(workforce_mode(&plan, 2), Mode::Harvest);
        assert_eq!(workforce_mode(&plan, 3), Mode::Fell);
        assert_eq!(workforce_mode(&plan, 4), Mode::Fell);
    }

    #[test]
    fn semantic_modes_choose_only_the_requested_legal_kind() {
        let mut features = vec![[0.0f32; 44]; 4];
        features[0][20] = 1.0;
        features[1][20 + 2] = 1.0;
        features[2][20 + 3] = 1.0;
        features[3][20 + 4] = 1.0;
        let actions = vec![
            3 * MACRO_CELLS as i32,
            5 * MACRO_CELLS as i32,
            6 * MACRO_CELLS as i32,
            7 * MACRO_CELLS as i32,
        ];
        let order = exact_prior_order(&features, &actions, MacroSelectionBranch::Rate as u8);
        let observation = MacroCandidateObservation {
            actions,
            features,
            teacher_index: order[0],
            branch: MacroSelectionBranch::Rate,
        };
        for (mode, expected_feature) in [
            (Mode::Fell, 20 + 2),
            (Mode::Harvest, 20 + 3),
            (Mode::Renew, 20 + 4),
        ] {
            let (action, eligible, _) = semantic_action(&observation, mode);
            assert!(eligible);
            let candidate = observation
                .actions
                .iter()
                .position(|candidate| *candidate as usize == action)
                .unwrap();
            assert!(observation.features[candidate][expected_feature] > 0.5);
        }
    }

    #[test]
    fn balanced_plan_is_exact_direct_d40() {
        let control = plan_catalog().remove(0);
        let anchor = plan_catalog()
            .into_iter()
            .find(|plan| plan.label == "pre3_balanced__post3_balanced")
            .unwrap();
        let task = Task {
            map_seed: 9_800_000,
            seat: 0,
            opponent: 4,
        };
        let left = play(task, 0, &control);
        let right = play(task, 1, &anchor);
        assert_eq!(left.terminal, right.terminal);
        assert_eq!(left.action_planes, right.action_planes);
        assert_eq!(right.pre3.eligible, 0);
        assert_eq!(right.pre3.overrides, 0);
        assert_eq!(right.post3.eligible, 0);
        assert_eq!(right.post3.overrides, 0);
    }
}
