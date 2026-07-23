//! Run D66a's consumed source-to-net-surplus lease gate.

use std::cmp::Reverse;
use std::fs::OpenOptions;
use std::io::{BufWriter, Write};

use troll_farm::game::engine::{training_cost, IRON};
use troll_farm::rl_macro::{
    CompleteMacroEnv, MacroDecisionStage, MacroOpponentMode, MacroTerminal, MacroTrainGoal,
    PlantOwner, MACRO_ACTION_PLANES, MACRO_CELLS,
};

const SEEDS: [i64; 2] = [9_830_002, 9_830_014];

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
enum Policy {
    D40Control,
    SourceSurplusLease,
}

impl Policy {
    const ALL: [Self; 2] = [Self::D40Control, Self::SourceSurplusLease];

    fn label(self) -> &'static str {
        match self {
            Self::D40Control => "d40_control",
            Self::SourceSurplusLease => "source_surplus_lease",
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
}

#[derive(Clone, Copy, Debug)]
struct LeaseTelemetry {
    activations: [u8; 4],
    first_turns: [i32; 4],
    first_state_hash: u64,
    activation_hash: u64,
    pick_commands: u16,
    plant_commands: u16,
    harvest_commands: u16,
    drop_commands: u16,
    wait_commands: u16,
    duration_turns: u16,
    max_duration_turns: u16,
    bootstrap_failures: u16,
    lease_failures: u16,
    lease_after_worker_two: u16,
    first_worker_two_turn: i32,
    first_worker_three_turn: i32,
    max_workers: u8,
    finite_state_failures: u16,
}

impl LeaseTelemetry {
    fn new() -> Self {
        Self {
            activations: [0; 4],
            first_turns: [-1; 4],
            first_state_hash: 0,
            activation_hash: 0xcbf29ce484222325,
            pick_commands: 0,
            plant_commands: 0,
            harvest_commands: 0,
            drop_commands: 0,
            wait_commands: 0,
            duration_turns: 0,
            max_duration_turns: 0,
            bootstrap_failures: 0,
            lease_failures: 0,
            lease_after_worker_two: 0,
            first_worker_two_turn: -1,
            first_worker_three_turn: -1,
            max_workers: 1,
            finite_state_failures: 0,
        }
    }

    fn activations(&self) -> u8 {
        self.activations.iter().copied().sum()
    }

    fn mix(&mut self, value: u64) {
        for byte in value.to_le_bytes() {
            self.activation_hash ^= u64::from(byte);
            self.activation_hash = self.activation_hash.wrapping_mul(0x100000001b3);
        }
    }

    fn observe_workers(&mut self, env: &CompleteMacroEnv) {
        let workers = own_worker_count(env);
        self.max_workers = self.max_workers.max(workers as u8);
        if self.first_worker_two_turn < 0 && workers >= 2 {
            self.first_worker_two_turn = env.state.turn;
        }
        if self.first_worker_three_turn < 0 && workers >= 3 {
            self.first_worker_three_turn = env.state.turn;
        }
    }
}

#[derive(Clone, Debug)]
struct Row {
    policy: Policy,
    task: Task,
    terminal: MacroTerminal,
    reward_identity_error: f32,
    telemetry: LeaseTelemetry,
    terminal_live_own_plants: usize,
    action_planes: [u32; MACRO_ACTION_PLANES],
}

fn own_worker_count(env: &CompleteMacroEnv) -> usize {
    env.state
        .units
        .iter()
        .filter(|unit| unit.player as usize == env.seat)
        .count()
}

fn live_own_plants(env: &CompleteMacroEnv) -> usize {
    env.state
        .plants
        .iter()
        .filter(|plant| plant.health > 0)
        .filter(|plant| env.owners().get(&plant.pos()) == Some(&PlantOwner::Own))
        .count()
}

fn fruit_index(name: &str) -> usize {
    match name {
        "PLUM" => 0,
        "LEMON" => 1,
        "APPLE" => 2,
        "BANANA" => 3,
        other => panic!("unknown D66 fruit {other}"),
    }
}

fn source_kind(env: &CompleteMacroEnv, bootstrapped: u8) -> Option<usize> {
    if env.stage() != MacroDecisionStage::Train
        || env.train_goal() != MacroTrainGoal::Producer
        || own_worker_count(env) != 1
    {
        return None;
    }
    let mut cost = training_cost(1, MacroTrainGoal::Producer.spec().expect("producer spec"));
    if env.state.iron.is_empty() {
        cost[IRON] = 0;
    }
    let bank = env.state.inventories[env.seat];
    if (0..6).all(|index| bank[index] >= cost[index]) {
        return None;
    }
    let mut stock = bank;
    for unit in env
        .state
        .units
        .iter()
        .filter(|unit| unit.player as usize == env.seat)
    {
        for (available, carried) in stock.iter_mut().zip(unit.carry) {
            *available = available.saturating_add(carried);
        }
    }
    for plant in env.state.plants.iter().filter(|plant| plant.health > 0) {
        let kind = fruit_index(&plant.plant_type);
        stock[kind] = stock[kind].saturating_add(plant.fruits);
    }
    let deficit = std::array::from_fn::<_, 6, _>(|index| (cost[index] - stock[index]).max(0));
    (0..4)
        .filter(|kind| deficit[*kind] > 0 && bank[*kind] > 0 && bootstrapped & (1u8 << *kind) == 0)
        .max_by_key(|kind| (deficit[*kind], Reverse(*kind)))
}

fn play(task: Task, policy: Policy) -> Row {
    let mut env = CompleteMacroEnv::new(task.map_seed, task.seat, MacroOpponentMode::Resident);
    let mut terminal = MacroTerminal::default();
    let mut telemetry = LeaseTelemetry::new();
    let mut action_planes = [0u32; MACRO_ACTION_PLANES];
    let mut bootstrapped = 0u8;
    let mut decisions = 0usize;
    let mut last_turn = env.state.turn;
    let mut stagnant = 0usize;
    while !terminal.done {
        decisions += 1;
        assert!(decisions <= 5_000, "D66 decision loop on {task:?}");
        if policy == Policy::SourceSurplusLease {
            if let Some(kind) = source_kind(&env, bootstrapped) {
                let turn = env.state.turn;
                let state_hash = env.state_hash();
                let workers_before = own_worker_count(&env);
                let bank_before = env.state.inventories[env.seat][kind];
                let invalidated_before = terminal.invalidated_jobs;
                let crops_before = live_own_plants(&env);
                telemetry.lease_after_worker_two = telemetry
                    .lease_after_worker_two
                    .saturating_add(u16::from(workers_before >= 2));
                match env.install_bank_seed_source_surplus_lease(kind) {
                    Some(outcome) => {
                        bootstrapped |= 1u8 << kind;
                        telemetry.activations[kind] = telemetry.activations[kind].saturating_add(1);
                        if telemetry.first_turns[kind] < 0 {
                            telemetry.first_turns[kind] = turn;
                        }
                        if telemetry.first_state_hash == 0 {
                            telemetry.first_state_hash = state_hash;
                        }
                        telemetry.mix(state_hash);
                        telemetry.mix(turn as u64);
                        telemetry.mix(kind as u64);
                        telemetry.mix(outcome.target.0 as u64);
                        telemetry.mix(outcome.target.1 as u64);
                        telemetry.pick_commands = telemetry
                            .pick_commands
                            .saturating_add(outcome.pick_commands);
                        telemetry.plant_commands = telemetry
                            .plant_commands
                            .saturating_add(outcome.plant_commands);
                        telemetry.harvest_commands = telemetry
                            .harvest_commands
                            .saturating_add(outcome.harvest_commands);
                        telemetry.drop_commands = telemetry
                            .drop_commands
                            .saturating_add(outcome.drop_commands);
                        let duration = (outcome.end_turn - outcome.start_turn).max(0) as u16;
                        telemetry.duration_turns =
                            telemetry.duration_turns.saturating_add(duration);
                        telemetry.max_duration_turns = telemetry.max_duration_turns.max(duration);
                        telemetry.wait_commands = telemetry
                            .wait_commands
                            .saturating_add(outcome.wait_commands);
                        action_planes[7] = action_planes[7].saturating_add(1);
                        terminal = outcome.terminal;
                        telemetry.lease_failures =
                            telemetry.lease_failures.saturating_add(u16::from(
                                outcome.pick_commands != 1
                                    || outcome.plant_commands != 1
                                    || outcome.harvest_commands != 2
                                    || outcome.drop_commands != 1
                                    || terminal.invalidated_jobs != invalidated_before
                                    || env.state.inventories[env.seat][kind] != bank_before + 1
                                    || live_own_plants(&env) < crops_before + 1,
                            ));
                        telemetry.observe_workers(&env);
                    }
                    None => {
                        telemetry.bootstrap_failures =
                            telemetry.bootstrap_failures.saturating_add(1);
                    }
                }
                if terminal.done {
                    break;
                }
                if env.state.turn == last_turn {
                    stagnant += 1;
                } else {
                    last_turn = env.state.turn;
                    stagnant = 0;
                }
                assert!(stagnant <= 16, "D66 zero-time lease loop on {task:?}");
                if bootstrapped & (1u8 << kind) != 0 {
                    continue;
                }
            }
        }
        let observation = env.candidate_observation();
        let action = observation.actions[observation.teacher_index] as usize;
        assert!(env.legal_actions().contains(&action));
        action_planes[action / MACRO_CELLS] = action_planes[action / MACRO_CELLS].saturating_add(1);
        terminal = env.step(action);
        telemetry.observe_workers(&env);
        if env.state.turn == last_turn {
            stagnant += 1;
        } else {
            last_turn = env.state.turn;
            stagnant = 0;
        }
        assert!(stagnant <= 16, "D66 zero-time loop on {task:?}");
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
        policy,
        task,
        terminal,
        reward_identity_error,
        telemetry,
        terminal_live_own_plants: live_own_plants(&env),
        action_planes,
    }
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(args.len(), 2, "usage: d66_source_net_surplus_lease OUTPUT");
    let mut rows = Vec::new();
    for policy in Policy::ALL {
        for map_seed in SEEDS {
            for seat in 0..2 {
                rows.push(play(Task { map_seed, seat }, policy));
            }
        }
    }
    rows.sort_by_key(|row| (row.policy, row.task));
    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&args[1])
        .expect("create D66 output without overwrite");
    let mut writer = BufWriter::new(target);
    writeln!(writer, "map_seed\tseat\topponent\tpolicy\tturn\town_score\topponent_score\tmargin\town_return\topponent_return\tmargin_return\treward_identity_error\town_workers\topponent_workers\tsuccessful_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tdeposit_prediction_failures\tselected_decisions\tselected_jobs\tselected_nonidle_jobs\tselected_renew_jobs\town_created_crops\topponent_created_crops\tambiguous_created_crops\taction_hash\tstate_hash\tactivations\tactivation_plum\tactivation_lemon\tactivation_apple\tactivation_banana\tfirst_activation_plum_turn\tfirst_activation_lemon_turn\tfirst_activation_apple_turn\tfirst_activation_banana_turn\tfirst_activation_state_hash\tactivation_hash\tpick_commands\tplant_commands\tharvest_commands\tdrop_commands\twait_commands\tduration_turns\tmax_duration_turns\tbootstrap_failures\tlease_failures\tlease_after_worker_two\tfirst_worker_two_turn\tfirst_worker_three_turn\tmax_workers\tfinite_state_failures\tterminal_live_own_plants\ttrain_none\ttrain_producer\ttrain_chopper\tidle\tbank\tfell_bank\tharvest_bank\trenew\tmine_bank").expect("write D66 header");
    for row in rows {
        let terminal = row.terminal;
        let t = row.telemetry;
        let fields = vec![
            row.task.map_seed.to_string(),
            row.task.seat.to_string(),
            "resident".to_string(),
            row.policy.label().to_string(),
            terminal.turn.to_string(),
            terminal.own_score.to_string(),
            terminal.opponent_score.to_string(),
            (terminal.own_score - terminal.opponent_score).to_string(),
            format!("{:.8}", terminal.own_return),
            format!("{:.8}", terminal.opponent_return),
            format!("{:.8}", terminal.margin_return),
            format!("{:.8}", row.reward_identity_error),
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
            terminal.action_hash.to_string(),
            terminal.state_hash.to_string(),
            t.activations().to_string(),
            t.activations[0].to_string(),
            t.activations[1].to_string(),
            t.activations[2].to_string(),
            t.activations[3].to_string(),
            t.first_turns[0].to_string(),
            t.first_turns[1].to_string(),
            t.first_turns[2].to_string(),
            t.first_turns[3].to_string(),
            t.first_state_hash.to_string(),
            t.activation_hash.to_string(),
            t.pick_commands.to_string(),
            t.plant_commands.to_string(),
            t.harvest_commands.to_string(),
            t.drop_commands.to_string(),
            t.wait_commands.to_string(),
            t.duration_turns.to_string(),
            t.max_duration_turns.to_string(),
            t.bootstrap_failures.to_string(),
            t.lease_failures.to_string(),
            t.lease_after_worker_two.to_string(),
            t.first_worker_two_turn.to_string(),
            t.first_worker_three_turn.to_string(),
            t.max_workers.to_string(),
            t.finite_state_failures.to_string(),
            row.terminal_live_own_plants.to_string(),
            row.action_planes[0].to_string(),
            row.action_planes[1].to_string(),
            row.action_planes[2].to_string(),
            row.action_planes[3].to_string(),
            row.action_planes[4].to_string(),
            row.action_planes[5].to_string(),
            row.action_planes[6].to_string(),
            row.action_planes[7].to_string(),
            row.action_planes[8].to_string(),
        ];
        writeln!(writer, "{}", fields.join("\t")).expect("write D66 row");
    }
    writer.flush().expect("flush D66 output");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn frozen_consumed_grid_has_eight_rows() {
        let rows = Policy::ALL
            .into_iter()
            .flat_map(|policy| {
                SEEDS.into_iter().flat_map(move |map_seed| {
                    (0..2).map(move |seat| play(Task { map_seed, seat }, policy))
                })
            })
            .collect::<Vec<_>>();
        assert_eq!(rows.len(), 8);
        assert!(rows.iter().all(|row| row.terminal.done));
    }

    #[test]
    fn first_consumed_lease_is_mechanically_accounted() {
        let row = play(
            Task {
                map_seed: 9_830_002,
                seat: 0,
            },
            Policy::SourceSurplusLease,
        );
        assert!(row.telemetry.activations() >= 1);
        assert_eq!(
            row.telemetry.pick_commands,
            row.telemetry.activations() as u16
        );
        assert_eq!(
            row.telemetry.plant_commands,
            row.telemetry.activations() as u16
        );
        assert_eq!(row.terminal.invalid_direct_commands, 0);
        assert_eq!(row.terminal.provenance_failures, 0);
    }
}
