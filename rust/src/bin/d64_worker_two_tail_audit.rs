//! Trace exact D40 stock flow on the four D64 worker-two safety failures.

use std::fs::OpenOptions;
use std::io::{BufWriter, Write};

use troll_farm::game::engine::{training_cost, IRON};
use troll_farm::rl_macro::{
    CompleteMacroEnv, MacroDecisionStage, MacroOpponentMode, MacroSelectionBranch, MacroTrainGoal,
    PlantOwner, MACRO_CELLS,
};

const SEEDS: [i64; 2] = [9_830_002, 9_830_014];
const OPPONENTS: [MacroOpponentMode; 2] =
    [MacroOpponentMode::Resident, MacroOpponentMode::GoldAdaptive];

fn worker_count(env: &CompleteMacroEnv) -> usize {
    env.state
        .units
        .iter()
        .filter(|unit| unit.player as usize == env.seat)
        .count()
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

fn branch_label(branch: MacroSelectionBranch) -> &'static str {
    match branch {
        MacroSelectionBranch::Train => "train",
        MacroSelectionBranch::Deficit => "deficit",
        MacroSelectionBranch::Evacuation => "evacuation",
        MacroSelectionBranch::Rate => "rate",
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

fn fruit_label(index: Option<usize>) -> &'static str {
    match index {
        None => "none",
        Some(0) => "plum",
        Some(1) => "lemon",
        Some(2) => "apple",
        Some(3) => "banana",
        Some(other) => panic!("unexpected D64i fruit index {other}"),
    }
}

fn vector_text(values: [i32; 6]) -> String {
    values
        .iter()
        .map(ToString::to_string)
        .collect::<Vec<_>>()
        .join(",")
}

fn deficit(cost: [i32; 6], stock: [i32; 6]) -> [i32; 6] {
    let mut result = [0; 6];
    for index in 0..6 {
        result[index] = (cost[index] - stock[index]).max(0);
    }
    result
}

fn add(left: [i32; 6], right: [i32; 6]) -> [i32; 6] {
    let mut result = [0; 6];
    for index in 0..6 {
        result[index] = left[index].saturating_add(right[index]);
    }
    result
}

fn mix(hash: &mut u64, value: u64) {
    for byte in value.to_le_bytes() {
        *hash ^= u64::from(byte);
        *hash = hash.wrapping_mul(0x100000001b3);
    }
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(args.len(), 2, "usage: d64_worker_two_tail_audit OUTPUT");
    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&args[1])
        .expect("create D64i output without overwrite");
    let mut writer = BufWriter::new(target);
    writeln!(writer, "map_seed\tseat\topponent\tcohort\tdecision\tturn_before\tturn_after\tstage\tworkers_before\tworkers_after\ttrain_goal\tbranch\taction_plane\tjob_kind\tjob_fruit\tjob_owner\tjob_predicted_deposit\tbank\tcarry\tripe\tplant_counts\tplant_fruits\tactive_predicted_deposit\tbank_deficit\tbank_carry_deficit\tbank_carry_ripe_deficit\tbank_deficit_total\tbank_carry_deficit_total\tbank_carry_ripe_deficit_total\tshack_occupied\tcurrent_on_shack\tlive_own_plants\tcreated_worker_two\tdone\tsuccessful_trains\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tdeposit_prediction_failures\tstate_hash_before\tstate_hash_after\ttrace_hash").expect("write D64i header");

    for map_seed in SEEDS {
        for seat in 0..2 {
            for opponent_mode in OPPONENTS {
                let cohort = if opponent_mode == MacroOpponentMode::Resident {
                    "target"
                } else {
                    "control"
                };
                let mut env = CompleteMacroEnv::new(map_seed, seat, opponent_mode);
                let mut decision_index = 0usize;
                let mut trace_hash = 0xcbf29ce484222325u64;
                loop {
                    decision_index += 1;
                    assert!(decision_index <= 5_000, "D64i decision loop");
                    let observation = env.candidate_observation();
                    let stage = env.stage();
                    let workers_before = worker_count(&env);
                    let turn_before = env.state.turn;
                    let state_hash_before = env.state_hash();
                    let goal = env.train_goal();
                    let branch = observation.branch;
                    let action = observation.actions[observation.teacher_index] as usize;
                    let action_plane = action / MACRO_CELLS;
                    let selected_job = if stage == MacroDecisionStage::Worker {
                        let unit_id = env.current_unit_id().expect("D64i current worker");
                        let unit = env
                            .state
                            .units
                            .iter()
                            .find(|unit| unit.id == unit_id)
                            .expect("D64i current unit");
                        env.jobs_for_current_unit()
                            .into_iter()
                            .find(|job| job.action(&env.state, seat, unit) == action)
                    } else {
                        None
                    };
                    let job_kind = selected_job.as_ref().map_or("none", |job| job.kind.label());
                    let job_fruit = selected_job.as_ref().and_then(|job| job.fruit_kind);
                    let job_owner = selected_job.as_ref().and_then(|job| job.owner);
                    let job_deposit = selected_job
                        .as_ref()
                        .map_or([0; 6], |job| job.predicted_deposit);

                    let bank = env.state.inventories[seat];
                    let mut carry = [0; 6];
                    for unit in env
                        .state
                        .units
                        .iter()
                        .filter(|unit| unit.player as usize == seat)
                    {
                        carry = add(carry, unit.carry);
                    }
                    let mut ripe = [0; 6];
                    let mut plant_counts = [0; 6];
                    let mut plant_fruits = [0; 6];
                    for plant in env.state.plants.iter().filter(|plant| plant.health > 0) {
                        let index = match plant.plant_type.as_str() {
                            "PLUM" => 0,
                            "LEMON" => 1,
                            "APPLE" => 2,
                            "BANANA" => 3,
                            other => panic!("unknown D64i plant {other}"),
                        };
                        plant_counts[index] += 1;
                        plant_fruits[index] += plant.fruits;
                        ripe[index] += plant.fruits;
                    }
                    let mut active_deposit = [0; 6];
                    for job in env.active_jobs() {
                        active_deposit = add(active_deposit, job.predicted_deposit);
                    }
                    let mut cost = training_cost(1, MacroTrainGoal::Producer.spec().unwrap());
                    if env.state.iron.is_empty() {
                        cost[IRON] = 0;
                    }
                    let bank_carry = add(bank, carry);
                    let bank_carry_ripe = add(bank_carry, ripe);
                    let bank_deficit = deficit(cost, bank);
                    let bank_carry_deficit = deficit(cost, bank_carry);
                    let bank_carry_ripe_deficit = deficit(cost, bank_carry_ripe);
                    let shack_occupied = env.state.units.iter().any(|unit| {
                        unit.player as usize == seat && unit.pos() == env.state.shacks[seat]
                    });
                    let current_on_shack = env
                        .current_unit_id()
                        .and_then(|id| env.state.units.iter().find(|unit| unit.id == id))
                        .is_some_and(|unit| unit.pos() == env.state.shacks[seat]);
                    let live_own_plants = env
                        .state
                        .plants
                        .iter()
                        .filter(|plant| plant.health > 0)
                        .filter(|plant| env.owners().get(&plant.pos()) == Some(&PlantOwner::Own))
                        .count();

                    mix(&mut trace_hash, turn_before as u64);
                    mix(&mut trace_hash, action as u64);
                    let terminal = env.step(action);
                    let workers_after = worker_count(&env);
                    let created_worker_two = workers_before < 2 && workers_after >= 2;
                    let state_hash_after = env.state_hash();
                    writeln!(
                        writer,
                        "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
                        map_seed,
                        seat,
                        opponent_mode.label(),
                        cohort,
                        decision_index,
                        turn_before,
                        env.state.turn,
                        stage_label(stage),
                        workers_before,
                        workers_after,
                        goal_label(goal),
                        branch_label(branch),
                        action_plane,
                        job_kind,
                        fruit_label(job_fruit),
                        owner_label(job_owner),
                        vector_text(job_deposit),
                        vector_text(bank),
                        vector_text(carry),
                        vector_text(ripe),
                        vector_text(plant_counts),
                        vector_text(plant_fruits),
                        vector_text(active_deposit),
                        vector_text(bank_deficit),
                        vector_text(bank_carry_deficit),
                        vector_text(bank_carry_ripe_deficit),
                        bank_deficit.iter().sum::<i32>(),
                        bank_carry_deficit.iter().sum::<i32>(),
                        bank_carry_ripe_deficit.iter().sum::<i32>(),
                        usize::from(shack_occupied),
                        usize::from(current_on_shack),
                        live_own_plants,
                        usize::from(created_worker_two),
                        usize::from(terminal.done),
                        terminal.successful_trains,
                        terminal.invalidated_jobs,
                        terminal.invalid_direct_commands,
                        terminal.provenance_failures,
                        terminal.deposit_prediction_failures,
                        state_hash_before,
                        state_hash_after,
                        trace_hash,
                    )
                    .expect("write D64i row");
                    if terminal.done || (cohort == "control" && created_worker_two) {
                        break;
                    }
                }
            }
        }
    }
    writer.flush().expect("flush D64i output");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn frozen_cohort_and_cost_are_exact() {
        assert_eq!(SEEDS, [9_830_002, 9_830_014]);
        assert_eq!(OPPONENTS.len(), 2);
        let env = CompleteMacroEnv::new(SEEDS[0], 0, MacroOpponentMode::Resident);
        let cost = training_cost(1, MacroTrainGoal::Producer.spec().unwrap());
        assert_eq!(cost[0], 5);
        assert_eq!(cost[1], 5);
        assert_eq!(cost[2], 2);
        assert!(env.state.inventories[0][0] < cost[0]);
    }

    #[test]
    fn deficit_layers_are_monotone() {
        let cost = [5, 5, 2, 0, 2, 0];
        let bank = [2, 4, 7, 4, 10, 0];
        let carry = [2, 1, 0, 0, 0, 0];
        let ripe = [4, 0, 0, 0, 0, 0];
        let bank_deficit = deficit(cost, bank);
        let carry_deficit = deficit(cost, add(bank, carry));
        let ripe_deficit = deficit(cost, add(add(bank, carry), ripe));
        assert!(bank_deficit.iter().sum::<i32>() >= carry_deficit.iter().sum());
        assert!(carry_deficit.iter().sum::<i32>() >= ripe_deficit.iter().sum());
    }
}
