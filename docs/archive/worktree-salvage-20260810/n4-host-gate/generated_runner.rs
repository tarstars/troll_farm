// N4 Phase-A exact resident candidate-pair surface census.
//
// The Python orchestrator verifies and instruments the byte-locked resident snapshot,
// writes it to a temporary path, and sets N4_INSTRUMENTED_RESIDENT for this include.
#[allow(dead_code, unused_imports)]
mod control_resident {
    include!(env!("N4_INSTRUMENTED_RESIDENT"));
}

use rayon::prelude::*;
use std::fs::File;
use std::io::{BufWriter, Write};
use std::time::Instant;

use troll_farm::game::a2_referee_parity;
use troll_farm::game::engine::has_stalled;
use troll_farm::game::state::{Cell, GameState};
use troll_farm::rl_macro::{MacroOpponentMode, MACRO_TOTAL_TURNS};
use troll_farm::strategies::compact_gold::CompactGold;
use troll_farm::strategies::gold_elite::GoldElite;
use troll_farm::strategies::legend_field_proxy::{LegendFieldProxyV2, LegendFieldProxyV2Config};
use troll_farm::strategies::mybot::MyBot;
use troll_farm::strategies::norxondor_native::NorxondorNative;
use troll_farm::strategies::script_boss::ScriptBoss;
use troll_farm::strategies::silver_boss::SilverBoss;
use troll_farm::strategies::Strategy;

const START_SEED: i64 = 9_854_000;
const MAPS: i64 = 128;
const FAMILIES: usize = 8;

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    seed: i64,
    seat: usize,
    opponent: usize,
}

enum Opponent {
    Resident(control_resident::bot::moisan::SecureOrchardBot),
    Local(Box<dyn Strategy>),
}

impl Opponent {
    fn new(mode: MacroOpponentMode) -> Self {
        match mode {
            MacroOpponentMode::Resident => {
                Self::Resident(control_resident::bot::moisan::SecureOrchardBot::new())
            }
            MacroOpponentMode::GoldAdaptive => Self::Local(Box::new(GoldElite::adaptive())),
            MacroOpponentMode::CompactGold => Self::Local(Box::new(CompactGold::new())),
            MacroOpponentMode::NorxondorThree => {
                Self::Local(Box::new(NorxondorNative::new(true)))
            }
            MacroOpponentMode::LegendBalanced => Self::Local(Box::new(
                LegendFieldProxyV2::configured(LegendFieldProxyV2Config {
                    producer_spec: (2, 2, 1, 1),
                    chopper_spec: (2, 2, 0, 2),
                    late_chop: true,
                }),
            )),
            MacroOpponentMode::MyBot => Self::Local(Box::new(MyBot::new())),
            MacroOpponentMode::ScriptBoss => Self::Local(Box::new(ScriptBoss::new())),
            MacroOpponentMode::SilverBoss => Self::Local(Box::new(SilverBoss::new())),
        }
    }

    fn commands(&mut self, game: &GameState, player: usize) -> Vec<String> {
        match self {
            Self::Resident(bot) => {
                use control_resident::bot::Bot as _;
                bot.commands(&control_view(game, player))
            }
            Self::Local(strategy) => strategy.decide(game, player),
        }
    }
}

fn control_view(game: &GameState, player: usize) -> control_resident::game::GameState {
    let opponent = 1 - player;
    control_resident::game::GameState {
        width: game.width,
        height: game.height,
        walkable: game.walkable.iter().copied().collect(),
        shacks: [game.shacks[player], game.shacks[opponent]],
        inventories: [game.inventories[player], game.inventories[opponent]],
        units: game
            .units
            .iter()
            .map(|unit| control_resident::game::Unit {
                id: unit.id,
                player: usize::from(unit.player as usize != player),
                cell: unit.pos(),
                stats: control_resident::game::Stats {
                    movement_speed: unit.ms,
                    carry_capacity: unit.cc,
                    harvest_power: unit.hp,
                    chop_power: unit.chop,
                },
                carry: unit.carry,
            })
            .collect(),
        plants: game
            .plants
            .iter()
            .map(|plant| control_resident::game::Plant {
                kind: control_resident::game::PlantKind::parse(&plant.plant_type)
                    .expect("known plant type"),
                cell: plant.pos(),
                size: plant.size,
                health: plant.health,
                fruits: plant.fruits,
                cooldown: plant.cooldown,
            })
            .collect(),
        scores: [game.scores[player], game.scores[opponent]],
        turn: game.turn,
        next_id: game.next_id,
        iron: game.iron.iter().copied().collect(),
        water: game.water.iter().copied().collect(),
    }
}

fn pct(value: &str) -> String {
    let mut out = String::new();
    for byte in value.as_bytes() {
        if byte.is_ascii_alphanumeric() || matches!(*byte, b'_' | b'-' | b'.') {
            out.push(*byte as char);
        } else {
            out.push_str(&format!("%{:02X}", byte));
        }
    }
    out
}

fn encode_commands(commands: &[String]) -> String {
    commands.iter().map(|command| pct(command)).collect::<Vec<_>>().join(";")
}

fn verb(command: &str) -> &str {
    command.split_whitespace().next().unwrap_or("WAIT")
}


fn unit_bound(commands: &[String]) -> Vec<String> {
    commands
        .iter()
        .filter(|command| {
            matches!(
                verb(command),
                "WAIT" | "MOVE" | "HARVEST" | "CHOP" | "DROP" | "MINE" | "PLANT" | "PICK"
            )
        })
        .cloned()
        .collect()
}

fn plant_present(game: &GameState, cell: Cell) -> bool {
    game.plants.iter().any(|plant| plant.pos() == cell)
}

fn state_resource_signature(game: &GameState) -> (Vec<[i32; 6]>, [[i32; 6]; 2], Vec<(i32, i32, i32, i32, i32, i32)>) {
    let mut carries: Vec<_> = game.units.iter().map(|unit| unit.carry).collect();
    carries.sort();
    let mut plants: Vec<_> = game
        .plants
        .iter()
        .map(|plant| (plant.x, plant.y, plant.size, plant.health, plant.fruits, plant.cooldown))
        .collect();
    plants.sort();
    (carries, game.inventories, plants)
}

fn candidate_blob(probe: &control_resident::bot::moisan::N4Probe) -> String {
    probe
        .candidates
        .iter()
        .map(|candidate| {
            let (x, y) = candidate.target_cell.unwrap_or((-1, -1));
            format!(
                "{}~{}~{}~{:.12}~{}~{}~{}~{}~{}~{}~{}~{}~{}~{}",
                candidate.unit_id,
                candidate.index,
                pct(&candidate.command),
                candidate.score,
                candidate.target_kind,
                x,
                y,
                candidate.route_distance.unwrap_or(-1),
                candidate.predicted_size.unwrap_or(-1),
                candidate.predicted_health.unwrap_or(-1),
                candidate.predicted_cooldown.unwrap_or(-1),
                candidate.fell_turns.unwrap_or(-1),
                candidate.fell_size.unwrap_or(-1),
                usize::from(candidate.opponent_crop_target),
            )
        })
        .collect::<Vec<_>>()
        .join("|")
}

fn candidate_signature(candidate: &control_resident::bot::moisan::N4CandidateProbe) -> String {
    let (x, y) = candidate.target_cell.unwrap_or((-1, -1));
    format!("{}:{}:{}:{}", verb(&candidate.command), candidate.target_kind, x, y)
}

fn target_set(
    probe: &control_resident::bot::moisan::N4Probe,
    first: usize,
    second: usize,
) -> Vec<(i32, i32)> {
    let mut cells = [first, second]
        .iter()
        .filter_map(|index| probe.candidates[*index].target_cell)
        .collect::<Vec<_>>();
    cells.sort();
    cells
}

struct PendingRow {
    line: String,
}

fn row_for_pair(
    task: Task,
    probe: &control_resident::bot::moisan::N4Probe,
    pair: Option<&control_resident::bot::moisan::N4PairProbe>,
    live_pair: Option<&control_resident::bot::moisan::N4PairProbe>,
    live_full: &[String],
    alternative_full: &[String],
    baseline_next: &GameState,
    alternative_next: &GameState,
    latency_us: u128,
    candidates: &str,
) -> PendingRow {
    let pair_count = probe.pairs.len();
    let pair_index = pair.map(|value| value.index as i64).unwrap_or(-1);
    let is_live = pair
        .zip(live_pair)
        .is_some_and(|(left, right)| left.index == right.index);
    let live_score = live_pair.map(|value| value.score).unwrap_or(f64::NAN);
    let pair_score = pair.map(|value| value.score).unwrap_or(f64::NAN);
    let score_gap = live_score - pair_score;

    let semantic_distinct = match (pair, live_pair) {
        (Some(pair), Some(live)) => {
            let left = [pair.first_index, pair.second_index]
                .iter()
                .map(|index| candidate_signature(&probe.candidates[*index]))
                .collect::<Vec<_>>();
            let right = [live.first_index, live.second_index]
                .iter()
                .map(|index| candidate_signature(&probe.candidates[*index]))
                .collect::<Vec<_>>();
            left != right
        }
        _ => false,
    };

    let pair_commands = pair.map(|value| value.commands.clone()).unwrap_or_default();
    let changed = pair_commands != probe.selected_pre;
    let overlap_move_residual = changed
        && !pair_commands.is_empty()
        && pair_commands.iter().all(|command| verb(command) == "MOVE")
        && probe.selected_pre.iter().all(|command| verb(command) == "MOVE");
    let overlap_threatened_crop = pair.is_some_and(|value| {
        probe.candidates[value.first_index].opponent_crop_target
            || probe.candidates[value.second_index].opponent_crop_target
    });

    let boundary_collision = pair.is_some_and(|_| unit_bound(alternative_full) != pair_commands);
    let boundary_route_order = match (pair, live_pair) {
        (Some(pair), Some(live)) => {
            target_set(probe, pair.first_index, pair.second_index)
                == target_set(probe, live.first_index, live.second_index)
                && pair_commands != live.commands
        }
        _ => false,
    };
    let boundary_bank = pair.is_some_and(|value| {
        [value.first_index, value.second_index].iter().any(|index| {
            let candidate = &probe.candidates[*index];
            matches!(candidate.target_kind, "bank" | "shack")
                && candidate.route_distance.is_some_and(|distance| distance <= 3)
                || matches!(verb(&candidate.command), "DROP" | "PICK")
        })
    }) || state_resource_signature(baseline_next).0 != state_resource_signature(alternative_next).0
        || baseline_next.inventories != alternative_next.inventories;
    let boundary_tree = pair.is_some_and(|value| {
        [value.first_index, value.second_index].iter().any(|index| {
            let candidate = &probe.candidates[*index];
            candidate.target_kind == "tree"
                && (candidate.predicted_cooldown.is_some_and(|value| value <= 3)
                    || candidate.fell_turns.is_some_and(|value| value <= 3))
        })
    }) || state_resource_signature(baseline_next).2 != state_resource_signature(alternative_next).2;
    let boundary_disappearance = pair.is_some_and(|value| {
        [value.first_index, value.second_index].iter().any(|index| {
            let candidate = &probe.candidates[*index];
            candidate.target_kind == "tree"
                && candidate.target_cell.is_some_and(|cell| {
                    plant_present(baseline_next, cell) != plant_present(alternative_next, cell)
                })
        })
    });

    let line = vec![
        "pair".to_string(),
        task.seed.to_string(),
        task.seat.to_string(),
        task.opponent.to_string(),
        pct(MacroOpponentMode::from_index(task.opponent).label()),
        probe.turn.to_string(),
        latency_us.to_string(),
        pair_count.to_string(),
        "1".to_string(),
        usize::from(live_pair.is_some()).to_string(),
        pair_index.to_string(),
        usize::from(is_live).to_string(),
        encode_commands(live_full),
        encode_commands(&probe.selected_pre),
        encode_commands(&probe.selected_final),
        encode_commands(&pair_commands),
        encode_commands(alternative_full),
        format!("{live_score:.12}"),
        format!("{pair_score:.12}"),
        format!("{score_gap:.12}"),
        usize::from(semantic_distinct).to_string(),
        usize::from(boundary_bank).to_string(),
        usize::from(boundary_tree).to_string(),
        usize::from(boundary_collision).to_string(),
        usize::from(boundary_disappearance).to_string(),
        usize::from(boundary_route_order).to_string(),
        usize::from(overlap_move_residual).to_string(),
        usize::from(overlap_threatened_crop).to_string(),
        "0".to_string(),
        "0".to_string(),
        "0".to_string(),
        candidates.to_string(),
        "0".to_string(),
    ]
    .join("\t");
    PendingRow { line }
}

fn row_without_probe(task: Task, turn: i32, live_full: &[String], latency_us: u128) -> PendingRow {
    let line = vec![
        "pair".to_string(),
        task.seed.to_string(),
        task.seat.to_string(),
        task.opponent.to_string(),
        pct(MacroOpponentMode::from_index(task.opponent).label()),
        turn.to_string(),
        latency_us.to_string(),
        "0".to_string(),
        "0".to_string(),
        "0".to_string(),
        "-1".to_string(),
        "0".to_string(),
        encode_commands(live_full),
        "".to_string(),
        "".to_string(),
        "".to_string(),
        encode_commands(live_full),
        "NaN".to_string(),
        "NaN".to_string(),
        "NaN".to_string(),
        "0".to_string(),
        "0".to_string(),
        "0".to_string(),
        "0".to_string(),
        "0".to_string(),
        "0".to_string(),
        "0".to_string(),
        "0".to_string(),
        "0".to_string(),
        "0".to_string(),
        "0".to_string(),
        "".to_string(),
        "0".to_string(),
    ]
    .join("\t");
    PendingRow { line }
}

fn task_without_two_worker_state(task: Task) -> PendingRow {
    let line = vec![
        "task".to_string(),
        task.seed.to_string(),
        task.seat.to_string(),
        task.opponent.to_string(),
        pct(MacroOpponentMode::from_index(task.opponent).label()),
        "0".to_string(),
        "0".to_string(),
        "0".to_string(),
        "1".to_string(),
        "1".to_string(),
        "-1".to_string(),
        "0".to_string(),
        "".to_string(),
        "".to_string(),
        "".to_string(),
        "".to_string(),
        "".to_string(),
        "NaN".to_string(),
        "NaN".to_string(),
        "NaN".to_string(),
        "0".to_string(),
        "0".to_string(),
        "0".to_string(),
        "0".to_string(),
        "0".to_string(),
        "0".to_string(),
        "0".to_string(),
        "0".to_string(),
        "0".to_string(),
        "0".to_string(),
        "0".to_string(),
        "NO_TWO_WORKER_STATE".to_string(),
        "0".to_string(),
    ]
    .join("\t");
    PendingRow { line }
}

fn run_task(task: Task) -> Result<Vec<String>, String> {
    use control_resident::bot::Bot as _;
    let mut referee = a2_referee_parity::generate_official(task.seed);
    let mut ours = control_resident::bot::moisan::SecureOrchardBot::new();
    let mut theirs = Opponent::new(MacroOpponentMode::from_index(task.opponent));
    let mut turns_until_end = 0;
    let mut pending = Vec::new();

    loop {
        let player = task.seat;
        let opponent = 1 - player;
        let view = control_view(&referee.game, player);
        let own_count = view.units.iter().filter(|unit| unit.player == 0).count();
        let bot_before = ours.clone();
        control_resident::bot::moisan::n4_clear_probe();
        let started = Instant::now();
        let ours_commands = ours.commands(&view);
        let baseline_probe = control_resident::bot::moisan::n4_take_probe();
        let theirs_commands = theirs.commands(&referee.game, opponent);
        let baseline_commands = if player == 0 {
            [ours_commands.clone(), theirs_commands.clone()]
        } else {
            [theirs_commands.clone(), ours_commands.clone()]
        };
        let mut baseline_next = referee.clone();
        a2_referee_parity::step(
            &mut baseline_next,
            &baseline_commands[0],
            &baseline_commands[1],
        );

        if own_count == 2 {
            if let Some(probe) = baseline_probe {
                let live_pair = probe
                    .pairs
                    .iter()
                    .find(|pair| pair.commands == probe.selected_pre);
                let candidates = candidate_blob(&probe);
                if probe.pairs.is_empty() {
                    let elapsed = started.elapsed().as_micros();
                    pending.push(row_for_pair(
                        task,
                        &probe,
                        None,
                        live_pair,
                        &ours_commands,
                        &ours_commands,
                        &baseline_next.game,
                        &baseline_next.game,
                        elapsed,
                        &candidates,
                    ));
                } else {
                    let mut pair_rows = Vec::new();
                    for pair in &probe.pairs {
                        let mut alternative_bot = bot_before.clone();
                        alternative_bot.n4_force_pair(pair.commands.clone());
                        control_resident::bot::moisan::n4_clear_probe();
                        let alternative_ours = alternative_bot.commands(&view);
                        let _ = control_resident::bot::moisan::n4_take_probe();
                        let alternative_commands = if player == 0 {
                            [alternative_ours.clone(), theirs_commands.clone()]
                        } else {
                            [theirs_commands.clone(), alternative_ours.clone()]
                        };
                        let mut alternative_next = referee.clone();
                        a2_referee_parity::step(
                            &mut alternative_next,
                            &alternative_commands[0],
                            &alternative_commands[1],
                        );
                        pair_rows.push((pair, alternative_ours, alternative_next.game));
                    }
                    let elapsed = started.elapsed().as_micros();
                    for (index, (pair, alternative_ours, alternative_next)) in
                        pair_rows.into_iter().enumerate()
                    {
                        pending.push(row_for_pair(
                            task,
                            &probe,
                            Some(pair),
                            live_pair,
                            &ours_commands,
                            &alternative_ours,
                            &baseline_next.game,
                            &alternative_next,
                            elapsed,
                            if index == 0 { &candidates } else { "" },
                        ));
                    }
                }
            } else {
                pending.push(row_without_probe(
                    task,
                    view.turn,
                    &ours_commands,
                    started.elapsed().as_micros(),
                ));
            }
        }

        referee = baseline_next;
        let done = referee.game.turn > MACRO_TOTAL_TURNS
            || has_stalled(&referee.game, &mut turns_until_end);
        if done {
            break;
        }
    }

    if pending.is_empty() {
        pending.push(task_without_two_worker_state(task));
    }
    let terminal_own = referee.game.scores[task.seat];
    let terminal_opponent = referee.game.scores[1 - task.seat];
    Ok(pending
        .into_iter()
        .map(|row| format!("{}\t{}\t{}", row.line, terminal_own, terminal_opponent))
        .collect())
}

fn main() -> Result<(), String> {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 3 && args.len() != 4 {
        return Err("usage: n4_candidate_pair_surface <output.tsv> <threads> [map_count]".to_string());
    }
    let output = &args[1];
    let threads: usize = args[2].parse().map_err(|_| "invalid threads".to_string())?;
    let map_count: i64 = if args.len() == 4 {
        args[3].parse().map_err(|_| "invalid map_count".to_string())?
    } else {
        MAPS
    };
    if !(1..=MAPS).contains(&map_count) {
        return Err(format!("map_count must be 1..={MAPS}"));
    }
    let tasks: Vec<Task> = (START_SEED..START_SEED + map_count)
        .flat_map(|seed| {
            (0..2).flat_map(move |seat| {
                (0..FAMILIES).map(move |opponent| Task { seed, seat, opponent })
            })
        })
        .collect();
    let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(threads)
        .build()
        .map_err(|error| format!("thread pool: {error}"))?;
    let rows: Vec<Result<(Task, Vec<String>), String>> = pool.install(|| {
        tasks
            .par_iter()
            .map(|task| run_task(*task).map(|rows| (*task, rows)))
            .collect()
    });
    let mut collected = Vec::new();
    for row in rows {
        collected.push(row?);
    }
    collected.sort_by_key(|value| value.0);
    let mut writer = BufWriter::new(File::create(output).map_err(|error| error.to_string())?);
    writeln!(
        writer,
        "row_type\tseed\tseat\topp\topp_name\tturn\tlatency_us\tpair_count\tprobe_present\tlive_pair_found\tpair_index\tis_live\tlive_full\tlive_pre\tlive_final\talt_pre\talt_final\tlive_score\talt_score\tscore_gap\tsemantic_distinct\tboundary_bank\tboundary_tree\tboundary_collision\tboundary_disappearance\tboundary_route_order\toverlap_move_residual\toverlap_threatened_crop\toverlap_d163_d168\toverlap_primitive_mutation\toverlap_static_option\tcandidates_blob\tterminal_margin_used_for_eligibility\tterminal_own_score\tterminal_opponent_score"
    )
    .map_err(|error| error.to_string())?;
    for (_, task_rows) in collected {
        for row in task_rows {
            writeln!(writer, "{row}").map_err(|error| error.to_string())?;
        }
    }
    writer.flush().map_err(|error| error.to_string())?;
    Ok(())
}
