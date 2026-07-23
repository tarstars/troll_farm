//! Trace the lifecycle of D65a's planted source roots on its four consumed tasks.

use std::cmp::Reverse;
use std::fs::OpenOptions;
use std::io::{BufWriter, Write};

use troll_farm::game::engine::{training_cost, IRON};
use troll_farm::rl_macro::{
    CompleteMacroEnv, MacroDecisionStage, MacroOpponentMode, MacroTerminal, MacroTrainGoal,
    PlantOwner, MACRO_CELLS,
};

const SEEDS: [i64; 2] = [9_830_002, 9_830_014];
const FRUITS: [&str; 4] = ["plum", "lemon", "apple", "banana"];

#[derive(Clone, Copy, Debug)]
struct SourceRoot {
    kind: usize,
    cell: (i32, i32),
}

#[derive(Clone, Copy, Debug)]
struct Stock {
    bank: [i32; 6],
    carry: [i32; 6],
    ripe: [i32; 6],
    own_plants: [i32; 4],
    own_ripe: [i32; 4],
    deficit: [i32; 6],
}

fn own_worker_count(env: &CompleteMacroEnv) -> usize {
    env.state
        .units
        .iter()
        .filter(|unit| unit.player as usize == env.seat)
        .count()
}

fn fruit_index(name: &str) -> usize {
    match name {
        "PLUM" => 0,
        "LEMON" => 1,
        "APPLE" => 2,
        "BANANA" => 3,
        other => panic!("unknown D65i fruit {other}"),
    }
}

fn stage_label(stage: MacroDecisionStage) -> &'static str {
    match stage {
        MacroDecisionStage::Train => "train",
        MacroDecisionStage::Worker => "worker",
    }
}

fn goal_label(goal: MacroTrainGoal) -> &'static str {
    match goal {
        MacroTrainGoal::None => "none",
        MacroTrainGoal::Producer => "producer",
        MacroTrainGoal::Chopper => "chopper",
    }
}

fn owner_label(owner: Option<PlantOwner>) -> &'static str {
    match owner {
        None => "none",
        Some(PlantOwner::Natural) => "natural",
        Some(PlantOwner::Own) => "own",
        Some(PlantOwner::Opponent) => "opponent",
        Some(PlantOwner::Ambiguous) => "ambiguous",
    }
}

fn optional_fruit_label(kind: Option<usize>) -> &'static str {
    kind.map_or("none", |kind| FRUITS[kind])
}

fn optional_cell_text(cell: Option<(i32, i32)>) -> String {
    cell.map_or_else(
        || "none".to_string(),
        |cell| format!("{},{}", cell.0, cell.1),
    )
}

fn vector_text<const N: usize>(values: [i32; N]) -> String {
    values
        .iter()
        .map(ToString::to_string)
        .collect::<Vec<_>>()
        .join(",")
}

fn stock(env: &CompleteMacroEnv) -> Stock {
    let bank = env.state.inventories[env.seat];
    let mut carry = [0i32; 6];
    for unit in env
        .state
        .units
        .iter()
        .filter(|unit| unit.player as usize == env.seat)
    {
        for (total, amount) in carry.iter_mut().zip(unit.carry) {
            *total = total.saturating_add(amount);
        }
    }
    let mut ripe = [0i32; 6];
    let mut own_plants = [0i32; 4];
    let mut own_ripe = [0i32; 4];
    for plant in env.state.plants.iter().filter(|plant| plant.health > 0) {
        let kind = fruit_index(&plant.plant_type);
        ripe[kind] = ripe[kind].saturating_add(plant.fruits);
        if env.owners().get(&plant.pos()) == Some(&PlantOwner::Own) {
            own_plants[kind] += 1;
            own_ripe[kind] = own_ripe[kind].saturating_add(plant.fruits);
        }
    }
    let mut cost = training_cost(1, MacroTrainGoal::Producer.spec().expect("producer spec"));
    if env.state.iron.is_empty() {
        cost[IRON] = 0;
    }
    let mut deficit = [0i32; 6];
    for index in 0..6 {
        deficit[index] = (cost[index] - bank[index] - carry[index] - ripe[index]).max(0);
    }
    Stock {
        bank,
        carry,
        ripe,
        own_plants,
        own_ripe,
        deficit,
    }
}

fn source_kind(env: &CompleteMacroEnv, bootstrapped: u8) -> Option<usize> {
    if env.stage() != MacroDecisionStage::Train
        || env.train_goal() != MacroTrainGoal::Producer
        || own_worker_count(env) != 1
    {
        return None;
    }
    let current = stock(env);
    let mut cost = training_cost(1, MacroTrainGoal::Producer.spec().expect("producer spec"));
    if env.state.iron.is_empty() {
        cost[IRON] = 0;
    }
    if (0..6).all(|index| current.bank[index] >= cost[index]) {
        return None;
    }
    (0..4)
        .filter(|kind| {
            current.deficit[*kind] > 0
                && current.bank[*kind] > 0
                && bootstrapped & (1u8 << *kind) == 0
        })
        .max_by_key(|kind| (current.deficit[*kind], Reverse(*kind)))
}

fn source_states(env: &CompleteMacroEnv, roots: &[SourceRoot]) -> String {
    roots
        .iter()
        .map(|root| {
            let plant = env
                .state
                .plants
                .iter()
                .find(|plant| plant.pos() == root.cell && plant.health > 0);
            match plant {
                Some(plant) => format!(
                    "{}@{},{}:1:{}:{}:{}:{}:{}:{}",
                    FRUITS[root.kind],
                    root.cell.0,
                    root.cell.1,
                    plant.plant_type.to_ascii_lowercase(),
                    owner_label(env.owners().get(&root.cell).copied()),
                    plant.size,
                    plant.health,
                    plant.fruits,
                    plant.cooldown,
                ),
                None => format!(
                    "{}@{},{}:0:none:none:-1:-1:-1:-1",
                    FRUITS[root.kind], root.cell.0, root.cell.1
                ),
            }
        })
        .collect::<Vec<_>>()
        .join(";")
}

fn mix(hash: &mut u64, value: u64) {
    for byte in value.to_le_bytes() {
        *hash ^= u64::from(byte);
        *hash = hash.wrapping_mul(0x100000001b3);
    }
}

#[allow(clippy::too_many_arguments)]
fn write_row(
    writer: &mut BufWriter<std::fs::File>,
    map_seed: i64,
    seat: usize,
    decision: usize,
    event: &str,
    turn_before: i32,
    stage: MacroDecisionStage,
    goal: MacroTrainGoal,
    workers_before: usize,
    action: usize,
    job_kind: &str,
    job_fruit: Option<usize>,
    job_target: Option<(i32, i32)>,
    job_owner: Option<PlantOwner>,
    selected_source_root: bool,
    bootstrap_kind: Option<usize>,
    bootstrap_target: Option<(i32, i32)>,
    pre: Stock,
    post: Stock,
    sources_before: &str,
    sources_after: &str,
    activations: [u8; 4],
    pick_commands: u16,
    plant_commands: u16,
    terminal: MacroTerminal,
    env: &CompleteMacroEnv,
    state_hash_before: u64,
    trace_hash: u64,
) {
    let fields = vec![
        map_seed.to_string(),
        seat.to_string(),
        decision.to_string(),
        event.to_string(),
        turn_before.to_string(),
        env.state.turn.to_string(),
        stage_label(stage).to_string(),
        goal_label(goal).to_string(),
        workers_before.to_string(),
        own_worker_count(env).to_string(),
        (action / MACRO_CELLS).to_string(),
        action.to_string(),
        job_kind.to_string(),
        optional_fruit_label(job_fruit).to_string(),
        optional_cell_text(job_target),
        owner_label(job_owner).to_string(),
        u8::from(selected_source_root).to_string(),
        optional_fruit_label(bootstrap_kind).to_string(),
        optional_cell_text(bootstrap_target),
        vector_text(pre.bank),
        vector_text(post.bank),
        vector_text(pre.carry),
        vector_text(post.carry),
        vector_text(pre.ripe),
        vector_text(post.ripe),
        vector_text(pre.own_plants),
        vector_text(post.own_plants),
        vector_text(pre.own_ripe),
        vector_text(post.own_ripe),
        vector_text(pre.deficit),
        vector_text(post.deficit),
        sources_before.to_string(),
        sources_after.to_string(),
        vector_text(activations.map(i32::from)),
        pick_commands.to_string(),
        plant_commands.to_string(),
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
        terminal.own_workers.to_string(),
        terminal.own_score.to_string(),
        terminal.opponent_score.to_string(),
        (terminal.own_score - terminal.opponent_score).to_string(),
        terminal.action_hash.to_string(),
        state_hash_before.to_string(),
        terminal.state_hash.to_string(),
        trace_hash.to_string(),
        u8::from(terminal.done).to_string(),
    ];
    writeln!(writer, "{}", fields.join("\t")).expect("write D65i trace row");
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(args.len(), 2, "usage: d65_source_survival_audit OUTPUT");
    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&args[1])
        .expect("create D65i output without overwrite");
    let mut writer = BufWriter::new(target);
    writeln!(writer, "map_seed\tseat\tdecision\tevent\tturn_before\tturn_after\tstage\ttrain_goal\tworkers_before\tworkers_after\taction_plane\taction\tjob_kind\tjob_fruit\tjob_target\tjob_owner\tselected_source_root\tbootstrap_fruit\tbootstrap_target\tbank_before\tbank_after\tcarry_before\tcarry_after\tripe_before\tripe_after\town_plants_before\town_plants_after\town_ripe_before\town_ripe_after\tbill_deficit_before\tbill_deficit_after\tsources_before\tsources_after\tactivation_vector\tpick_commands\tplant_commands\tsuccessful_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tdeposit_prediction_failures\tselected_decisions\tselected_jobs\tselected_nonidle_jobs\tselected_renew_jobs\town_created_crops\town_workers\town_score\topponent_score\tmargin\taction_hash\tstate_hash_before\tstate_hash_after\ttrace_hash\tdone").expect("write D65i header");

    for map_seed in SEEDS {
        for seat in 0..2 {
            let mut env = CompleteMacroEnv::new(map_seed, seat, MacroOpponentMode::Resident);
            let mut terminal = MacroTerminal::default();
            let mut roots: Vec<SourceRoot> = Vec::new();
            let mut bootstrapped = 0u8;
            let mut activations = [0u8; 4];
            let mut pick_commands = 0u16;
            let mut plant_commands = 0u16;
            let mut decision = 0usize;
            let mut trace_hash = 0xcbf29ce484222325u64;
            while !terminal.done {
                decision += 1;
                assert!(decision <= 5_000, "D65i decision loop");
                let turn_before = env.state.turn;
                let stage = env.stage();
                let goal = env.train_goal();
                let workers_before = own_worker_count(&env);
                let pre = stock(&env);
                let state_hash_before = env.state_hash();
                let sources_before = source_states(&env, &roots);

                if let Some(kind) = source_kind(&env, bootstrapped) {
                    let outcome = env
                        .install_bank_seed_source(kind)
                        .expect("D65i exact source transaction");
                    assert_eq!(outcome.pick_commands, 1);
                    assert_eq!(outcome.plant_commands, 1);
                    bootstrapped |= 1u8 << kind;
                    activations[kind] = activations[kind].saturating_add(1);
                    pick_commands = pick_commands.saturating_add(outcome.pick_commands);
                    plant_commands = plant_commands.saturating_add(outcome.plant_commands);
                    roots.push(SourceRoot {
                        kind,
                        cell: outcome.target,
                    });
                    terminal = outcome.terminal;
                    let action = 7 * MACRO_CELLS
                        + outcome.target.1 as usize * 22
                        + outcome.target.0 as usize;
                    mix(&mut trace_hash, state_hash_before);
                    mix(&mut trace_hash, action as u64);
                    mix(&mut trace_hash, terminal.state_hash);
                    write_row(
                        &mut writer,
                        map_seed,
                        seat,
                        decision,
                        "bootstrap",
                        turn_before,
                        stage,
                        goal,
                        workers_before,
                        action,
                        "bank_seed_source",
                        Some(kind),
                        Some(outcome.target),
                        Some(PlantOwner::Own),
                        false,
                        Some(kind),
                        Some(outcome.target),
                        pre,
                        stock(&env),
                        &sources_before,
                        &source_states(&env, &roots),
                        activations,
                        pick_commands,
                        plant_commands,
                        terminal,
                        &env,
                        state_hash_before,
                        trace_hash,
                    );
                    continue;
                }

                let observation = env.candidate_observation();
                let action = observation.actions[observation.teacher_index] as usize;
                let selected_job = if stage == MacroDecisionStage::Worker {
                    let unit_id = env.current_unit_id().expect("D65i current unit");
                    let unit = env
                        .state
                        .units
                        .iter()
                        .find(|unit| unit.id == unit_id)
                        .expect("D65i selected unit");
                    env.jobs_for_current_unit()
                        .into_iter()
                        .find(|job| job.action(&env.state, seat, unit) == action)
                } else {
                    None
                };
                let job_kind = selected_job.as_ref().map_or("none", |job| job.kind.label());
                let job_fruit = selected_job.as_ref().and_then(|job| job.fruit_kind);
                let job_target = selected_job.as_ref().and_then(|job| job.target);
                let job_owner = selected_job.as_ref().and_then(|job| job.owner);
                let selected_source_root =
                    job_target.is_some_and(|target| roots.iter().any(|root| root.cell == target));
                terminal = env.step(action);
                mix(&mut trace_hash, state_hash_before);
                mix(&mut trace_hash, action as u64);
                mix(&mut trace_hash, terminal.state_hash);
                write_row(
                    &mut writer,
                    map_seed,
                    seat,
                    decision,
                    "d40",
                    turn_before,
                    stage,
                    goal,
                    workers_before,
                    action,
                    job_kind,
                    job_fruit,
                    job_target,
                    job_owner,
                    selected_source_root,
                    None,
                    None,
                    pre,
                    stock(&env),
                    &sources_before,
                    &source_states(&env, &roots),
                    activations,
                    pick_commands,
                    plant_commands,
                    terminal,
                    &env,
                    state_hash_before,
                    trace_hash,
                );
            }
            assert_eq!(decision as u32, terminal.selected_decisions);
        }
    }
    writer.flush().expect("flush D65i output");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn source_state_encoding_is_stable() {
        let mut env = CompleteMacroEnv::new(9_830_002, 0, MacroOpponentMode::Resident);
        let train = env.candidate_observation();
        env.step(train.actions[train.teacher_index] as usize);
        let worker = env.candidate_observation();
        env.step(worker.actions[worker.teacher_index] as usize);
        let outcome = env.install_bank_seed_source(0).expect("source root");
        let text = source_states(
            &env,
            &[SourceRoot {
                kind: 0,
                cell: outcome.target,
            }],
        );
        assert!(text.starts_with("plum@"));
        assert!(text.contains(":1:plum:own:"));
    }

    #[test]
    fn frozen_source_trigger_starts_with_plum() {
        for seed in SEEDS {
            for seat in 0..2 {
                let mut env = CompleteMacroEnv::new(seed, seat, MacroOpponentMode::Resident);
                let train = env.candidate_observation();
                env.step(train.actions[train.teacher_index] as usize);
                let worker = env.candidate_observation();
                env.step(worker.actions[worker.teacher_index] as usize);
                assert_eq!(source_kind(&env, 0), Some(0));
            }
        }
    }
}
