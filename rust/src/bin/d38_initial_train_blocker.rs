//! Audit D38's turn-one resource and shack-occupancy blocker.

use std::fs::File;
use std::io::{BufWriter, Write};

use troll_farm::game::engine::{training_cost, IRON};
use troll_farm::rl_macro::{CompleteMacroEnv, MacroOpponentMode, MacroTrainGoal};

fn main() {
    let args: Vec<_> = std::env::args().collect();
    let start_seed = args
        .get(1)
        .map_or(9_630_000, |value| value.parse::<i64>().expect("start seed"));
    let map_count = args
        .get(2)
        .map_or(16, |value| value.parse::<usize>().expect("map count"));
    let output = args
        .get(3)
        .cloned()
        .unwrap_or_else(|| "d38-initial-train-blocker.tsv".to_string());
    let mut writer = BufWriter::new(File::create(&output).expect("create D38 blocker output"));
    writeln!(writer, "map_seed\tseat\tplum\tlemon\tapple\tbanana\tiron\twood\tdeficit_plum\tdeficit_lemon\tdeficit_apple\tdeficit_iron\tresource_deficit\tshack_occupied\tfirst_worker_job\ttarget_x\ttarget_y\tpredicted_reduction").expect("write D38 blocker header");

    for map_seed in start_seed..start_seed + map_count as i64 {
        for seat in 0..2 {
            let mut env = CompleteMacroEnv::new(map_seed, seat, MacroOpponentMode::Resident);
            let inventory = env.state.inventories[seat];
            let mut cost = training_cost(1, MacroTrainGoal::Producer.spec().unwrap());
            if env.state.iron.is_empty() {
                cost[IRON] = 0;
            }
            let mut deficit = [0; 6];
            for index in 0..6 {
                deficit[index] = (cost[index] - inventory[index]).max(0);
            }
            let shack_occupied =
                env.state.units.iter().any(|unit| {
                    unit.player as usize == seat && unit.pos() == env.state.shacks[seat]
                });
            let train = env.deficit_heuristic_action();
            env.step(train);
            let worker_action = env.deficit_heuristic_action();
            let unit = env
                .state
                .units
                .iter()
                .find(|unit| Some(unit.id) == env.current_unit_id())
                .expect("initial D38 worker");
            let job = env
                .jobs_for_current_unit()
                .into_iter()
                .find(|job| job.action(&env.state, seat, unit) == worker_action)
                .expect("selected initial D38 job");
            let predicted_reduction: i32 = deficit
                .into_iter()
                .zip(job.predicted_deposit)
                .map(|(needed, deposit)| needed.min(deposit))
                .sum();
            let (target_x, target_y) = job.target.unwrap_or((-1, -1));
            writeln!(
                writer,
                "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
                map_seed,
                seat,
                inventory[0],
                inventory[1],
                inventory[2],
                inventory[3],
                inventory[4],
                inventory[5],
                deficit[0],
                deficit[1],
                deficit[2],
                deficit[IRON],
                deficit.iter().sum::<i32>(),
                usize::from(shack_occupied),
                job.kind.label(),
                target_x,
                target_y,
                predicted_reduction,
            )
            .expect("write D38 blocker row");
        }
    }
    writer.flush().expect("flush D38 blocker output");
}
