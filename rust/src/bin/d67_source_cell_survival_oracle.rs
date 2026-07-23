//! Exhaust every D65-admissible source cell at the four consumed missing-species roots.

use std::cmp::Reverse;
use std::fs::OpenOptions;
use std::io::{BufWriter, Write};

use troll_farm::game::engine::{bfs_distances, training_cost, IRON};
use troll_farm::game::state::Cell;
use troll_farm::rl_macro::{
    CompleteMacroEnv, MacroDecisionStage, MacroOpponentMode, MacroTerminal, MacroTrainGoal,
    PlantOwner,
};

const SEEDS: [i64; 2] = [9_830_002, 9_830_014];
const FRUITS: [&str; 4] = ["plum", "lemon", "apple", "banana"];

#[derive(Clone, Copy, Debug)]
struct CandidateCell {
    cell: Cell,
    rank: usize,
    worker_distance: i32,
    own_door_distance: i32,
    opponent_door_distance: i32,
    safety_margin: i32,
    wet: bool,
}

struct Prefix {
    env: CompleteMacroEnv,
    terminal: MacroTerminal,
    bootstrapped: u8,
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
        other => panic!("unknown D67 fruit {other}"),
    }
}

fn fruit_label(kind: usize) -> &'static str {
    FRUITS[kind]
}

fn manhattan(left: Cell, right: Cell) -> i32 {
    (left.0 - right.0).abs() + (left.1 - right.1).abs()
}

fn shack_doors(env: &CompleteMacroEnv, player: usize) -> Vec<Cell> {
    let (x, y) = env.state.shacks[player];
    [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]
        .into_iter()
        .filter(|cell| env.state.walkable.contains(cell))
        .collect()
}

fn stock(env: &CompleteMacroEnv) -> ([i32; 6], [i32; 6], [i32; 6]) {
    let bank = env.state.inventories[env.seat];
    let mut carry = [0i32; 6];
    let mut ripe = [0i32; 6];
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
    for plant in env.state.plants.iter().filter(|plant| plant.health > 0) {
        ripe[fruit_index(&plant.plant_type)] =
            ripe[fruit_index(&plant.plant_type)].saturating_add(plant.fruits);
    }
    (bank, carry, ripe)
}

fn vector_text(values: [i32; 6]) -> String {
    values
        .iter()
        .map(ToString::to_string)
        .collect::<Vec<_>>()
        .join(",")
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
    let (bank, carry, ripe) = stock(env);
    if (0..6).all(|index| bank[index] >= cost[index]) {
        return None;
    }
    let deficit = std::array::from_fn::<_, 6, _>(|index| {
        (cost[index] - bank[index] - carry[index] - ripe[index]).max(0)
    });
    (0..4)
        .filter(|kind| deficit[*kind] > 0 && bank[*kind] > 0 && bootstrapped & (1u8 << *kind) == 0)
        .max_by_key(|kind| (deficit[*kind], Reverse(*kind)))
}

fn missing_species(map_seed: i64) -> usize {
    match map_seed {
        9_830_002 => 1,
        9_830_014 => 0,
        other => panic!("unexpected D67 seed {other}"),
    }
}

fn exact_prefix(map_seed: i64, seat: usize) -> Prefix {
    let missing = missing_species(map_seed);
    let mut env = CompleteMacroEnv::new(map_seed, seat, MacroOpponentMode::Resident);
    let mut terminal = MacroTerminal::default();
    let mut bootstrapped = 0u8;
    let mut decisions = 0usize;
    loop {
        decisions += 1;
        assert!(decisions <= 100, "D67 prefix decision loop");
        if let Some(kind) = source_kind(&env, bootstrapped) {
            if kind == missing {
                return Prefix {
                    env,
                    terminal,
                    bootstrapped,
                };
            }
            let outcome = env
                .install_bank_seed_source(kind)
                .expect("D67 exact earlier D65 source");
            terminal = outcome.terminal;
            bootstrapped |= 1u8 << kind;
            assert!(!terminal.done, "D67 prefix ended before missing source");
            continue;
        }
        let observation = env.candidate_observation();
        terminal = env.step(observation.actions[observation.teacher_index] as usize);
        assert!(!terminal.done, "D67 prefix never reached missing source");
    }
}

fn candidate_cells(env: &CompleteMacroEnv) -> Vec<CandidateCell> {
    assert_eq!(own_worker_count(env), 1);
    let unit = env
        .state
        .units
        .iter()
        .find(|unit| unit.player as usize == env.seat)
        .expect("D67 sole worker");
    let from_distance = bfs_distances(&env.state.walkable, &[unit.pos()]);
    let own_distance = bfs_distances(&env.state.walkable, &shack_doors(env, env.seat));
    let opponent_distance = bfs_distances(&env.state.walkable, &shack_doors(env, 1 - env.seat));
    let mut cells: Vec<_> = env
        .state
        .walkable
        .iter()
        .copied()
        .filter(|cell| manhattan(*cell, env.state.shacks[env.seat]) <= 4)
        .filter(|cell| !env.state.plants.iter().any(|plant| plant.pos() == *cell))
        .filter(|cell| !env.state.units.iter().any(|other| other.pos() == *cell))
        .filter_map(|cell| {
            let worker = *from_distance.get(&cell)?;
            let own = *own_distance.get(&cell)?;
            let opponent = *opponent_distance.get(&cell)?;
            (own < opponent).then_some((cell, worker, own, opponent))
        })
        .map(|(cell, worker, own, opponent)| {
            let wet = env
                .state
                .water
                .iter()
                .any(|water| manhattan(*water, cell) == 1);
            CandidateCell {
                cell,
                rank: 0,
                worker_distance: worker,
                own_door_distance: own,
                opponent_door_distance: opponent,
                safety_margin: opponent - own,
                wet,
            }
        })
        .collect();
    cells.sort_by_key(|candidate| {
        (
            candidate.worker_distance,
            usize::from(!candidate.wet),
            candidate.cell,
        )
    });
    for (rank, candidate) in cells.iter_mut().enumerate() {
        candidate.rank = rank;
    }
    cells
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(
        args.len(),
        2,
        "usage: d67_source_cell_survival_oracle OUTPUT"
    );
    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&args[1])
        .expect("create D67 output without overwrite");
    let mut writer = BufWriter::new(target);
    writeln!(writer, "map_seed\tseat\tmissing_species\tprefix_turn\tprefix_state_hash\tprefix_action_hash\tprefix_bootstrap_mask\tprefix_bank\tprefix_carry\tprefix_ripe\tcandidate_count\ttarget_rank\ttarget_x\ttarget_y\tworker_distance\town_door_distance\topponent_door_distance\tsafety_margin\twet\toriginal_target\tturn_after\tduration_turns\tpick_commands\tplant_commands\twait_commands\tharvest_commands\tdrop_commands\tbank_delta\tinvalidated_delta\tinvalid_direct_delta\tprovenance_delta\tdeposit_prediction_delta\troot_present_after\tsuccess\toutcome_action_hash\toutcome_state_hash\ttrace_hash").expect("write D67 header");

    for map_seed in SEEDS {
        for seat in 0..2 {
            let base = exact_prefix(map_seed, seat);
            let missing = missing_species(map_seed);
            assert_eq!(source_kind(&base.env, base.bootstrapped), Some(missing));
            let candidates = candidate_cells(&base.env);
            assert!(!candidates.is_empty(), "D67 empty candidate domain");
            let prefix_hash = base.env.state_hash();
            let prefix_turn = base.env.state.turn;
            let prefix_action_hash = base.terminal.action_hash;
            let prefix_selected = base.terminal.selected_decisions;
            let prefix_invalidated = base.terminal.invalidated_jobs;
            let prefix_direct = base.terminal.invalid_direct_commands;
            let prefix_provenance = base.terminal.provenance_failures;
            let prefix_deposit = base.terminal.deposit_prediction_failures;
            let (prefix_bank, prefix_carry, prefix_ripe) = stock(&base.env);

            for candidate in &candidates {
                let mut root = exact_prefix(map_seed, seat);
                assert_eq!(root.env.state_hash(), prefix_hash);
                assert_eq!(root.env.state.turn, prefix_turn);
                assert_eq!(root.terminal.action_hash, prefix_action_hash);
                assert_eq!(root.terminal.selected_decisions, prefix_selected);
                let bank_before = root.env.state.inventories[seat][missing];
                let outcome = root
                    .env
                    .install_bank_seed_source_surplus_lease_at(missing, candidate.cell)
                    .expect("D67 explicit candidate target");
                let bank_delta = root.env.state.inventories[seat][missing] - bank_before;
                let root_present = root.env.state.plants.iter().any(|plant| {
                    plant.pos() == candidate.cell
                        && plant.health > 0
                        && fruit_index(&plant.plant_type) == missing
                }) && root.env.owners().get(&candidate.cell)
                    == Some(&PlantOwner::Own);
                let success = outcome.pick_commands == 1
                    && outcome.plant_commands == 1
                    && outcome.harvest_commands == 2
                    && outcome.drop_commands == 1
                    && bank_delta == 1
                    && outcome.terminal.invalidated_jobs == prefix_invalidated
                    && outcome.terminal.invalid_direct_commands == prefix_direct
                    && outcome.terminal.provenance_failures == prefix_provenance
                    && outcome.terminal.deposit_prediction_failures == prefix_deposit;
                let mut trace_hash = 0xcbf29ce484222325u64;
                for value in [
                    prefix_hash,
                    candidate.cell.0 as u64,
                    candidate.cell.1 as u64,
                    outcome.terminal.state_hash,
                    outcome.pick_commands as u64,
                    outcome.plant_commands as u64,
                    outcome.wait_commands as u64,
                    outcome.harvest_commands as u64,
                    outcome.drop_commands as u64,
                ] {
                    for byte in value.to_le_bytes() {
                        trace_hash ^= u64::from(byte);
                        trace_hash = trace_hash.wrapping_mul(0x100000001b3);
                    }
                }
                let fields = vec![
                    map_seed.to_string(),
                    seat.to_string(),
                    fruit_label(missing).to_string(),
                    prefix_turn.to_string(),
                    prefix_hash.to_string(),
                    prefix_action_hash.to_string(),
                    root.bootstrapped.to_string(),
                    vector_text(prefix_bank),
                    vector_text(prefix_carry),
                    vector_text(prefix_ripe),
                    candidates.len().to_string(),
                    candidate.rank.to_string(),
                    candidate.cell.0.to_string(),
                    candidate.cell.1.to_string(),
                    candidate.worker_distance.to_string(),
                    candidate.own_door_distance.to_string(),
                    candidate.opponent_door_distance.to_string(),
                    candidate.safety_margin.to_string(),
                    u8::from(candidate.wet).to_string(),
                    u8::from(candidate.rank == 0).to_string(),
                    outcome.end_turn.to_string(),
                    (outcome.end_turn - outcome.start_turn).to_string(),
                    outcome.pick_commands.to_string(),
                    outcome.plant_commands.to_string(),
                    outcome.wait_commands.to_string(),
                    outcome.harvest_commands.to_string(),
                    outcome.drop_commands.to_string(),
                    bank_delta.to_string(),
                    (outcome.terminal.invalidated_jobs - prefix_invalidated).to_string(),
                    (outcome.terminal.invalid_direct_commands - prefix_direct).to_string(),
                    (outcome.terminal.provenance_failures - prefix_provenance).to_string(),
                    (outcome.terminal.deposit_prediction_failures - prefix_deposit).to_string(),
                    u8::from(root_present).to_string(),
                    u8::from(success).to_string(),
                    outcome.terminal.action_hash.to_string(),
                    outcome.terminal.state_hash.to_string(),
                    trace_hash.to_string(),
                ];
                writeln!(writer, "{}", fields.join("\t")).expect("write D67 row");
            }
        }
    }
    writer.flush().expect("flush D67 output");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn enumerated_rank_zero_matches_default_target() {
        for map_seed in SEEDS {
            for seat in 0..2 {
                let mut prefix = exact_prefix(map_seed, seat);
                let candidates = candidate_cells(&prefix.env);
                let outcome = prefix
                    .env
                    .install_bank_seed_source_surplus_lease(missing_species(map_seed))
                    .expect("D67 default target");
                assert_eq!(outcome.target, candidates[0].cell);
            }
        }
    }

    #[test]
    fn prefix_reconstruction_is_exact() {
        let first = exact_prefix(9_830_002, 0);
        let second = exact_prefix(9_830_002, 0);
        assert_eq!(first.env.state.turn, 11);
        assert_eq!(first.env.state_hash(), second.env.state_hash());
        assert_eq!(first.terminal.action_hash, second.terminal.action_hash);
        assert_eq!(source_kind(&first.env, first.bootstrapped), Some(1));
    }
}
