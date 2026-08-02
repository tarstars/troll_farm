//! Regenerate exact open-game decision states for the H3a trigger preflight.
//!
//! Input is one header plus hex-encoded paired command lines. Output interleaves a map
//! record, outcome-blind pre-turn decision records, and post-turn validation records.

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as FmtWrite;
use std::io::{self, Read};

use troll_farm::game::a2_referee_parity::{self, RefereeGame};
use troll_farm::game::state::{Cell, GameState, Plant, Unit};

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum Creator {
    Initial,
    Seat0,
    Seat1,
}

impl Creator {
    fn for_player(player: usize) -> Self {
        match player {
            0 => Self::Seat0,
            1 => Self::Seat1,
            _ => panic!("unexpected player {player}"),
        }
    }

    fn label(self) -> &'static str {
        match self {
            Self::Initial => "initial",
            Self::Seat0 => "seat0",
            Self::Seat1 => "seat1",
        }
    }
}

#[derive(Clone, Debug)]
struct PlantIntent {
    player: usize,
    unit_id: i32,
    plant_type: String,
}

#[derive(Clone, Debug)]
struct CreatedPlant {
    cell: Cell,
    plant_type: String,
    creator: Creator,
    planter_ids: Vec<i32>,
}

fn decode_hex(value: &str) -> String {
    assert_eq!(value.len() % 2, 0, "hex command has odd length");
    let mut bytes = Vec::with_capacity(value.len() / 2);
    for index in (0..value.len()).step_by(2) {
        bytes.push(u8::from_str_radix(&value[index..index + 2], 16).expect("command hex"));
    }
    String::from_utf8(bytes).expect("command UTF-8")
}

fn json_escape_into(buf: &mut String, text: &str) {
    buf.push('"');
    for character in text.chars() {
        match character {
            '"' => buf.push_str("\\\""),
            '\\' => buf.push_str("\\\\"),
            '\n' => buf.push_str("\\n"),
            '\r' => buf.push_str("\\r"),
            '\t' => buf.push_str("\\t"),
            value if value.is_control() => write!(buf, "\\u{:04x}", value as u32).unwrap(),
            value => buf.push(value),
        }
    }
    buf.push('"');
}

fn sorted_cells(values: &std::collections::HashSet<Cell>) -> Vec<Cell> {
    let mut cells: Vec<_> = values.iter().copied().collect();
    cells.sort_unstable();
    cells
}

fn write_cell(buf: &mut String, cell: Cell) {
    write!(buf, "[{},{}]", cell.0, cell.1).unwrap();
}

fn write_cells(buf: &mut String, cells: &[Cell]) {
    buf.push('[');
    for (index, cell) in cells.iter().enumerate() {
        if index > 0 {
            buf.push(',');
        }
        write_cell(buf, *cell);
    }
    buf.push(']');
}

fn write_inventory(buf: &mut String, inventory: &[i32; 6]) {
    write!(
        buf,
        "[{},{},{},{},{},{}]",
        inventory[0], inventory[1], inventory[2], inventory[3], inventory[4], inventory[5]
    )
    .unwrap();
}

fn write_commands(buf: &mut String, raw: &str) {
    buf.push('[');
    let mut written = 0;
    for command in raw.split(';').map(str::trim).filter(|value| !value.is_empty()) {
        if written > 0 {
            buf.push(',');
        }
        json_escape_into(buf, command);
        written += 1;
    }
    buf.push(']');
}

fn normalize_numeric_plant_aliases(raw: &str) -> String {
    raw.split(';')
        .map(|command| {
            let mut fields: Vec<_> = command.split_whitespace().collect();
            if fields.len() == 3
                && (fields[0].eq_ignore_ascii_case("PICK")
                    || fields[0].eq_ignore_ascii_case("PLANT"))
            {
                fields[2] = match fields[2] {
                    "0" => "PLUM",
                    "1" => "LEMON",
                    "2" => "APPLE",
                    "3" => "BANANA",
                    value => value,
                };
            }
            fields.join(" ")
        })
        .collect::<Vec<_>>()
        .join(";")
}

fn write_troll(buf: &mut String, input_index: usize, unit: &Unit) {
    write!(
        buf,
        "{{\"input_index\":{},\"troll_id\":{},\"global_player\":{},\"x\":{},\"y\":{},\"movement_speed\":{},\"carry_capacity\":{},\"harvest_power\":{},\"chop_power\":{},\"carrying\":[{},{},{},{},{},{}]}}",
        input_index,
        unit.id,
        unit.player,
        unit.x,
        unit.y,
        unit.ms,
        unit.cc,
        unit.hp,
        unit.chop,
        unit.carry[0],
        unit.carry[1],
        unit.carry[2],
        unit.carry[3],
        unit.carry[4],
        unit.carry[5]
    )
    .unwrap();
}

fn write_trolls(buf: &mut String, game: &GameState, player: usize) {
    buf.push('[');
    let mut written = 0;
    for (input_index, unit) in game.units.iter().enumerate() {
        if unit.player as usize != player {
            continue;
        }
        if written > 0 {
            buf.push(',');
        }
        write_troll(buf, input_index, unit);
        written += 1;
    }
    buf.push(']');
}

fn write_tree(
    buf: &mut String,
    tree_index: usize,
    plant: &Plant,
    provenance: &BTreeMap<Cell, Creator>,
) {
    let creator = provenance
        .get(&plant.pos())
        .copied()
        .expect("every visible tree has provenance");
    write!(
        buf,
        "{{\"tree_index\":{},\"x\":{},\"y\":{},\"species\":" ,
        tree_index, plant.x, plant.y
    )
    .unwrap();
    json_escape_into(buf, &plant.plant_type);
    write!(
        buf,
        ",\"size\":{},\"health\":{},\"fruits\":{},\"cooldown\":{},\"created_by\":",
        plant.size, plant.health, plant.fruits, plant.cooldown
    )
    .unwrap();
    json_escape_into(buf, creator.label());
    buf.push('}');
}

fn write_map(game_id: i64, seed: i64, seat: usize, game: &GameState) -> String {
    let mut buf = String::with_capacity(4096);
    write!(
        buf,
        "{{\"kind\":\"map\",\"schema_version\":1,\"game_id\":{},\"referee_seed\":{},\"seat\":{},\"width\":{},\"height\":{},\"walkable\":" ,
        game_id, seed, seat, game.width, game.height
    )
    .unwrap();
    write_cells(&mut buf, &sorted_cells(&game.walkable));
    buf.push_str(",\"shacks\":[");
    write_cell(&mut buf, game.shacks[seat]);
    buf.push(',');
    write_cell(&mut buf, game.shacks[1 - seat]);
    buf.push_str("],\"iron\":");
    write_cells(&mut buf, &sorted_cells(&game.iron));
    buf.push_str(",\"water\":");
    write_cells(&mut buf, &sorted_cells(&game.water));
    buf.push_str(",\"initial_inventories\":[");
    write_inventory(&mut buf, &game.inventories[seat]);
    buf.push(',');
    write_inventory(&mut buf, &game.inventories[1 - seat]);
    write!(buf, "],\"initial_tree_count\":{}}}", game.plants.len()).unwrap();
    buf
}

fn write_decision(
    game_id: i64,
    seat: usize,
    game: &GameState,
    provenance: &BTreeMap<Cell, Creator>,
    issued_commands: &str,
) -> String {
    assert_eq!(game.plants.len(), provenance.len(), "provenance cardinality");
    let mut buf = String::with_capacity(8192);
    write!(
        buf,
        "{{\"kind\":\"decision\",\"schema_version\":1,\"game_id\":{},\"turn\":{},\"seat\":{},\"next_id\":{},\"inventories\":[",
        game_id, game.turn, seat, game.next_id
    )
    .unwrap();
    write_inventory(&mut buf, &game.inventories[seat]);
    buf.push(',');
    write_inventory(&mut buf, &game.inventories[1 - seat]);
    buf.push_str("],\"resident_trolls\":");
    write_trolls(&mut buf, game, seat);
    buf.push_str(",\"opponent_trolls\":");
    write_trolls(&mut buf, game, 1 - seat);
    let opponent_units = game
        .units
        .iter()
        .filter(|unit| unit.player as usize == 1 - seat)
        .count();
    write!(
        buf,
        ",\"visible_opponent_unit_count\":{},\"trees\":[",
        opponent_units
    )
    .unwrap();
    for (tree_index, plant) in game.plants.iter().enumerate() {
        if tree_index > 0 {
            buf.push(',');
        }
        write_tree(&mut buf, tree_index, plant, provenance);
    }
    buf.push_str("],\"issued_commands\":");
    write_commands(&mut buf, issued_commands);
    buf.push('}');
    buf
}

fn parse_plant_intents(raw: &str, player: usize) -> Vec<PlantIntent> {
    raw.split(';')
        .filter_map(|command| {
            let fields: Vec<_> = command.split_whitespace().collect();
            if fields.len() != 3 || !fields[0].eq_ignore_ascii_case("PLANT") {
                return None;
            }
            Some(PlantIntent {
                player,
                unit_id: fields[1].parse().expect("plant unit id"),
                plant_type: fields[2].to_ascii_uppercase(),
            })
        })
        .collect()
}

fn update_provenance(
    game: &GameState,
    before_cells: &BTreeSet<Cell>,
    intents: &[PlantIntent],
    provenance: &mut BTreeMap<Cell, Creator>,
) -> Vec<CreatedPlant> {
    let after_cells: BTreeSet<_> = game.plants.iter().map(Plant::pos).collect();
    let mut created = Vec::new();
    for cell in after_cells.difference(before_cells) {
        let plant = game
            .plants
            .iter()
            .find(|candidate| candidate.pos() == *cell)
            .expect("new plant exists");
        let matching: Vec<_> = intents
            .iter()
            .filter(|intent| {
                intent.plant_type == plant.plant_type
                    && game
                        .units
                        .iter()
                        .find(|unit| unit.id == intent.unit_id)
                        .is_some_and(|unit| unit.pos() == *cell && unit.player as usize == intent.player)
            })
            .collect();
        assert!(!matching.is_empty(), "new tree without a matching landed plant intent");
        let creators: BTreeSet<_> = matching.iter().map(|intent| intent.player).collect();
        assert_eq!(creators.len(), 1, "ambiguous multi-player tree creation");
        let player = *creators.iter().next().unwrap();
        let creator = Creator::for_player(player);
        assert!(provenance.insert(*cell, creator).is_none(), "reused live tree cell");
        let mut planter_ids: Vec<_> = matching.iter().map(|intent| intent.unit_id).collect();
        planter_ids.sort_unstable();
        planter_ids.dedup();
        created.push(CreatedPlant {
            cell: *cell,
            plant_type: plant.plant_type.clone(),
            creator,
            planter_ids,
        });
    }
    provenance.retain(|cell, _| after_cells.contains(cell));
    assert_eq!(provenance.len(), after_cells.len(), "provenance coverage");
    created
}

fn write_validation(turn: i32, referee: &RefereeGame, created: &[CreatedPlant]) -> String {
    let game = &referee.game;
    let mut buf = String::with_capacity(4096);
    write!(buf, "{{\"kind\":\"validation\",\"turn\":{},\"inventories\":[", turn).unwrap();
    write_inventory(&mut buf, &game.inventories[0]);
    buf.push(',');
    write_inventory(&mut buf, &game.inventories[1]);
    buf.push_str("],\"units\":[");
    for (index, unit) in game.units.iter().enumerate() {
        if index > 0 {
            buf.push(',');
        }
        write!(buf, "[{},{},{},{}]", unit.id, unit.player, unit.x, unit.y).unwrap();
    }
    buf.push_str("],\"created\":[");
    for (index, plant) in created.iter().enumerate() {
        if index > 0 {
            buf.push(',');
        }
        write!(buf, "{{\"x\":{},\"y\":{},\"species\":", plant.cell.0, plant.cell.1).unwrap();
        json_escape_into(&mut buf, &plant.plant_type);
        buf.push_str(",\"created_by\":");
        json_escape_into(&mut buf, plant.creator.label());
        buf.push_str(",\"planter_ids\":[");
        for (planter_index, unit_id) in plant.planter_ids.iter().enumerate() {
            if planter_index > 0 {
                buf.push(',');
            }
            write!(buf, "{}", unit_id).unwrap();
        }
        buf.push_str("]}");
    }
    write!(
        buf,
        "],\"legality_issue_count\":{},\"critical_issue_count\":{},\"unclassified_issue_count\":{},\"issue_reasons\":{{",
        referee.legality.issue_count(),
        referee.legality.critical_issue_count(),
        referee.legality.unclassified_issue_count()
    )
    .unwrap();
    for (index, (reason, count)) in referee.legality.reason_counts().iter().enumerate() {
        if index > 0 {
            buf.push(',');
        }
        json_escape_into(&mut buf, reason);
        write!(buf, ":{}", count).unwrap();
    }
    buf.push_str("}}");
    buf
}

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).expect("read command replay input");
    let mut lines = input.lines();
    let header = lines.next().expect("input header");
    let header_fields: Vec<_> = header.split('\t').collect();
    assert_eq!(header_fields.len(), 4, "header fields");
    let game_id: i64 = header_fields[0].parse().expect("game id");
    let seed: i64 = header_fields[1].parse().expect("referee seed");
    let seat: usize = header_fields[2].parse().expect("resident seat");
    let turn_count: i32 = header_fields[3].parse().expect("turn count");
    assert!(seat < 2, "resident seat");

    let mut referee = a2_referee_parity::generate_official(seed);
    let mut provenance: BTreeMap<Cell, Creator> = referee
        .game
        .plants
        .iter()
        .map(|plant| (plant.pos(), Creator::Initial))
        .collect();
    assert_eq!(provenance.len(), referee.game.plants.len(), "initial tree cells unique");
    println!("{}", write_map(game_id, seed, seat, &referee.game));

    for expected_turn in 1..=turn_count {
        let line = lines.next().expect("turn input");
        let fields: Vec<_> = line.split('\t').collect();
        assert_eq!(fields.len(), 5, "turn fields");
        let turn: i32 = fields[0].parse().expect("turn number");
        assert_eq!(turn, expected_turn, "turn sequence");
        assert_eq!(referee.game.turn, turn, "referee turn");
        let commands0 = decode_hex(fields[1]);
        let commands1 = decode_hex(fields[2]);
        let forced_commands0 = decode_hex(fields[3]);
        let forced_commands1 = decode_hex(fields[4]);
        let issued = if seat == 0 { &commands0 } else { &commands1 };
        println!(
            "{}",
            write_decision(game_id, seat, &referee.game, &provenance, issued)
        );

        let before_cells: BTreeSet<_> = referee.game.plants.iter().map(Plant::pos).collect();
        let referee_commands0 = normalize_numeric_plant_aliases(&forced_commands0);
        let referee_commands1 = normalize_numeric_plant_aliases(&forced_commands1);
        let mut intents = parse_plant_intents(&referee_commands0, 0);
        intents.extend(parse_plant_intents(&referee_commands1, 1));
        a2_referee_parity::step(
            &mut referee,
            &[referee_commands0],
            &[referee_commands1],
        );
        let created = update_provenance(&referee.game, &before_cells, &intents, &mut provenance);
        println!("{}", write_validation(turn, &referee, &created));
    }
    assert!(lines.next().is_none(), "unexpected input after final turn");
}
