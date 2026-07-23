#[path = "yamo_orchard_live.rs"]
mod yamo;

pub use yamo::{bot, game};

use std::collections::{BTreeSet, HashSet};
use std::io;

use troll_farm::game::engine::{item_index, step, training_cost};
use troll_farm::game::state::{GameState, Plant as EnginePlant, Unit as EngineUnit};
use troll_farm::strategies::ownership_aware_farm::OwnershipAwareFarm;
use troll_farm::strategies::Strategy;
use yamo::bot::moisan::SecureOrchardBot;
use yamo::bot::Bot;
use yamo::game::protocol::{read_line, read_static_map, read_turn};
use yamo::game::{GameState as YamoState, Plant, PlantKind, Stats, Unit};

const ROOT_TURN: i32 = 75;
const CHECKPOINT_TURN: i32 = 125;
const HORIZON: usize = 50;

fn engine_state(view: YamoState) -> GameState {
    GameState {
        width: view.width,
        height: view.height,
        walkable: view.walkable.into_iter().collect(),
        shacks: view.shacks,
        inventories: view.inventories,
        units: view
            .units
            .into_iter()
            .map(|unit| EngineUnit {
                id: unit.id,
                player: unit.player as i32,
                x: unit.cell.0,
                y: unit.cell.1,
                ms: unit.stats.movement_speed,
                cc: unit.stats.carry_capacity,
                hp: unit.stats.harvest_power,
                chop: unit.stats.chop_power,
                carry: unit.carry,
            })
            .collect(),
        plants: view
            .plants
            .into_iter()
            .map(|plant| EnginePlant {
                plant_type: plant.kind.as_str().to_string(),
                x: plant.cell.0,
                y: plant.cell.1,
                size: plant.size,
                health: plant.health,
                fruits: plant.fruits,
                cooldown: plant.cooldown,
            })
            .collect(),
        scores: view.scores,
        turn: view.turn,
        next_id: view.next_id,
        iron: view.iron.into_iter().collect(),
        water: view.water.into_iter().collect(),
    }
}

fn yamo_view(game: &GameState) -> YamoState {
    YamoState {
        width: game.width,
        height: game.height,
        walkable: game.walkable.iter().copied().collect::<BTreeSet<_>>(),
        shacks: game.shacks,
        inventories: game.inventories,
        units: game
            .units
            .iter()
            .map(|unit| Unit {
                id: unit.id,
                player: unit.player as usize,
                cell: unit.pos(),
                stats: Stats {
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
            .map(|plant| Plant {
                kind: PlantKind::parse(&plant.plant_type).expect("known plant type"),
                cell: plant.pos(),
                size: plant.size,
                health: plant.health,
                fruits: plant.fruits,
                cooldown: plant.cooldown,
            })
            .collect(),
        scores: game.scores,
        turn: game.turn,
        next_id: game.next_id,
        iron: game.iron.iter().copied().collect::<BTreeSet<_>>(),
        water: game.water.iter().copied().collect::<BTreeSet<_>>(),
    }
}

fn commands(line: &str) -> Vec<String> {
    line.split(';')
        .map(str::trim)
        .filter(|value| !value.is_empty() && !value.to_ascii_uppercase().starts_with("MSG "))
        .map(str::to_string)
        .collect()
}

fn action_commands(values: Vec<String>) -> Vec<String> {
    values
        .into_iter()
        .filter(|value| !value.to_ascii_uppercase().starts_with("MSG "))
        .collect()
}

fn unit<'a>(game: &'a GameState, player: i32, id: i32) -> Option<&'a EngineUnit> {
    game.units
        .iter()
        .find(|unit| unit.player == player && unit.id == id)
}

fn near(left: (i32, i32), right: (i32, i32)) -> bool {
    (left.0 - right.0).abs() + (left.1 - right.1).abs() <= 1
}

fn item(name: &str) -> Option<usize> {
    match name {
        "PLUM" | "LEMON" | "APPLE" | "BANANA" | "IRON" | "WOOD" => Some(item_index(name)),
        _ => None,
    }
}

fn train_supported(game: &GameState, player: i32, fields: &[&str]) -> bool {
    if fields.len() < 5 {
        return false;
    }
    let Some(talents) = fields[1..5]
        .iter()
        .map(|value| value.parse::<i32>().ok())
        .collect::<Option<Vec<_>>>()
        .and_then(|values| {
            (values.len() == 4).then_some((values[0], values[1], values[2], values[3]))
        })
    else {
        return false;
    };
    let count = game
        .units
        .iter()
        .filter(|unit| unit.player == player)
        .count() as i32;
    let cost = training_cost(count, talents);
    let pay: &[usize] = if game.iron.is_empty() {
        &[0, 1, 2, 3, 5]
    } else {
        &[0, 1, 2, 3, 4, 5]
    };
    pay.iter()
        .all(|index| game.inventories[player as usize][*index] >= cost[*index])
        && !game
            .units
            .iter()
            .any(|unit| unit.pos() == game.shacks[player as usize])
}

fn command_supported(game: &GameState, player: i32, command: &str) -> bool {
    let fields: Vec<_> = command.split_whitespace().collect();
    let Some(verb) = fields.first().map(|value| value.to_ascii_uppercase()) else {
        return false;
    };
    if verb == "TRAIN" {
        return train_supported(game, player, &fields);
    }
    if fields.len() < 2 {
        return false;
    }
    let Some(id) = fields[1].parse::<i32>().ok() else {
        return false;
    };
    let Some(unit) = unit(game, player, id) else {
        return false;
    };
    match verb.as_str() {
        "MOVE" => {
            fields.len() >= 4
                && fields[2].parse::<i32>().is_ok()
                && fields[3].parse::<i32>().is_ok()
        }
        "HARVEST" => {
            unit.hp > 0
                && unit.free() > 0
                && game
                    .plants
                    .iter()
                    .any(|plant| plant.pos() == unit.pos() && plant.fruits > 0)
        }
        "DROP" => near(unit.pos(), game.shacks[player as usize]),
        "CHOP" => unit.chop > 0 && game.plants.iter().any(|plant| plant.pos() == unit.pos()),
        "MINE" => {
            unit.chop > 0 && unit.free() > 0 && game.iron.iter().any(|cell| near(unit.pos(), *cell))
        }
        "PLANT" => {
            let Some(index) = fields
                .get(2)
                .map(|value| value.to_ascii_uppercase())
                .and_then(|value| item(&value))
            else {
                return false;
            };
            game.walkable.contains(&unit.pos())
                && !game.plants.iter().any(|plant| plant.pos() == unit.pos())
                && unit.carry[index] > 0
        }
        "PICK" => {
            let Some(index) = fields
                .get(2)
                .map(|value| value.to_ascii_uppercase())
                .and_then(|value| item(&value))
            else {
                return false;
            };
            near(unit.pos(), game.shacks[player as usize])
                && unit.free() > 0
                && game.inventories[player as usize][index] > 0
        }
        _ => false,
    }
}

fn support(game: &GameState, player: i32, values: &[String]) -> (usize, usize) {
    let mut used = HashSet::new();
    let mut total = 0usize;
    let mut supported = 0usize;
    for command in values {
        let fields: Vec<_> = command.split_whitespace().collect();
        let Some(verb) = fields.first().map(|value| value.to_ascii_uppercase()) else {
            continue;
        };
        if verb == "WAIT" || verb == "MSG" {
            continue;
        }
        if verb != "TRAIN" {
            let Some(id) = fields.get(1).and_then(|value| value.parse::<i32>().ok()) else {
                total += 1;
                continue;
            };
            if !used.insert(id) {
                continue;
            }
        }
        total += 1;
        supported += usize::from(command_supported(game, player, command));
    }
    (total, supported)
}

fn unit_economy(game: &GameState) -> Vec<(i32, i32, i32, i32, i32, i32, [i32; 6])> {
    let mut values: Vec<_> = game
        .units
        .iter()
        .map(|unit| {
            (
                unit.id,
                unit.player,
                unit.ms,
                unit.cc,
                unit.hp,
                unit.chop,
                unit.carry,
            )
        })
        .collect();
    values.sort_unstable();
    values
}

fn unit_positions(game: &GameState) -> Vec<(i32, i32, i32)> {
    let mut values: Vec<_> = game
        .units
        .iter()
        .map(|unit| (unit.id, unit.x, unit.y))
        .collect();
    values.sort_unstable();
    values
}

fn plants(game: &GameState) -> Vec<(String, i32, i32, i32, i32, i32, i32)> {
    let mut values: Vec<_> = game
        .plants
        .iter()
        .map(|plant| {
            (
                plant.plant_type.clone(),
                plant.x,
                plant.y,
                plant.size,
                plant.health,
                plant.fruits,
                plant.cooldown,
            )
        })
        .collect();
    values.sort_unstable();
    values
}

fn main() {
    let stdin = io::stdin();
    let mut reader = io::BufReader::new(stdin.lock());
    let map = read_static_map(&mut reader).expect("D31 static map");
    let mut resident = SecureOrchardBot::new();
    let mut root = None;
    let mut official = None;
    for turn in 1..=CHECKPOINT_TURN {
        let view = read_turn(&mut reader, &map, turn).expect("D31 official view");
        if turn < ROOT_TURN {
            resident.commands(&view);
        } else if turn == ROOT_TURN {
            root = Some(engine_state(view));
        } else if turn == CHECKPOINT_TURN {
            official = Some(engine_state(view));
        }
    }
    let marker = read_line(&mut reader).expect("D31 command marker");
    assert_eq!(marker, "COMMANDS 50");
    let mut recorded = Vec::with_capacity(HORIZON);
    for _ in 0..HORIZON {
        let ours = commands(&read_line(&mut reader).expect("recorded resident command"));
        let theirs = commands(&read_line(&mut reader).expect("recorded opponent command"));
        recorded.push((ours, theirs));
    }

    let root = root.expect("turn-75 root");
    let official = official.expect("turn-125 official state");
    let mut control = root.clone();
    let mut option = root;
    let farm = OwnershipAwareFarm::new();
    let mut exact_turns = 0usize;
    let mut exact_prefix = 0usize;
    let mut prefix_open = true;
    let mut root_command_exact = false;
    let mut control_total = 0usize;
    let mut control_supported = 0usize;
    let mut option_total = 0usize;
    let mut option_supported = 0usize;
    for (index, (recorded_ours, recorded_theirs)) in recorded.iter().enumerate() {
        let ours = action_commands(resident.commands(&yamo_view(&control)));
        let exact = ours == *recorded_ours;
        if index == 0 {
            root_command_exact = exact;
        }
        exact_turns += usize::from(exact);
        if prefix_open && exact {
            exact_prefix += 1;
        } else {
            prefix_open = false;
        }
        let (total, supported) = support(&control, 1, recorded_theirs);
        control_total += total;
        control_supported += supported;
        step(&mut control, &ours, recorded_theirs);

        let option_ours = farm.decide(&option, 0);
        let (total, supported) = support(&option, 1, recorded_theirs);
        option_total += total;
        option_supported += supported;
        step(&mut option, &option_ours, recorded_theirs);
    }

    let scores_exact = control.scores == official.scores;
    let inventories_exact = control.inventories == official.inventories;
    let unit_economy_exact =
        unit_economy(&control) == unit_economy(&official) && control.next_id == official.next_id;
    let plants_exact = plants(&control) == plants(&official);
    let positions_exact = unit_positions(&control) == unit_positions(&official);
    let material_exact = scores_exact && inventories_exact && unit_economy_exact && plants_exact;
    let full_exact = material_exact && positions_exact;
    let control_margin = control.scores[0] - control.scores[1];
    let option_margin = option.scores[0] - option.scores[1];
    let official_margin = official.scores[0] - official.scores[1];
    println!(
        concat!(
            "{{\"root_command_exact\":{},\"exact_command_turns\":{},",
            "\"exact_command_prefix\":{},\"scores_exact\":{},",
            "\"inventories_exact\":{},\"unit_economy_exact\":{},",
            "\"plants_exact\":{},\"positions_exact\":{},",
            "\"material_exact\":{},\"full_exact\":{},",
            "\"control_score0\":{},\"control_score1\":{},\"control_margin\":{},",
            "\"official_score0\":{},\"official_score1\":{},\"official_margin\":{},",
            "\"option_score0\":{},\"option_score1\":{},\"option_margin\":{},",
            "\"option_minus_control_score0\":{},\"option_minus_control_score1\":{},",
            "\"option_minus_control_margin\":{},",
            "\"control_opponent_actions\":{},\"control_opponent_supported\":{},",
            "\"option_opponent_actions\":{},\"option_opponent_supported\":{}}}"
        ),
        root_command_exact,
        exact_turns,
        exact_prefix,
        scores_exact,
        inventories_exact,
        unit_economy_exact,
        plants_exact,
        positions_exact,
        material_exact,
        full_exact,
        control.scores[0],
        control.scores[1],
        control_margin,
        official.scores[0],
        official.scores[1],
        official_margin,
        option.scores[0],
        option.scores[1],
        option_margin,
        option.scores[0] - control.scores[0],
        option.scores[1] - control.scores[1],
        option_margin - control_margin,
        control_total,
        control_supported,
        option_total,
        option_supported,
    );
}
