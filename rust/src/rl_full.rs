//! Full-game, real-map neural-policy environment.
//!
//! The public ABI is documented in `local_claude_1/nn-bot/ENV-API.md` and the
//! observation layout in `local_claude_1/nn-bot/OBS-PLANES.md`.  This module
//! deliberately uses the exact referee [`GameState`] and [`engine::step`]
//! instead of a second mechanics port.

use std::collections::HashSet;

use serde::{Deserialize, Serialize};

use crate::game::engine::{
    bfs_distances, item_index, next_cell, recompute_scores, training_cost, APPLE, BANANA, IRON,
    LEMON, PLUM, WOOD,
};
use crate::game::state::{from_ascii, Cell, GameState, Plant, Unit};

pub const TF_FULL_OBS_CHANNELS: usize = 104;
pub const TF_FULL_HEIGHT: usize = 11;
pub const TF_FULL_WIDTH: usize = 22;
pub const TF_FULL_CELLS: usize = TF_FULL_HEIGHT * TF_FULL_WIDTH;
pub const TF_FULL_OBS_SIZE: usize = TF_FULL_OBS_CHANNELS * TF_FULL_CELLS;
pub const TF_FULL_ACTION_PLANES: usize = 13;
pub const TF_FULL_ACTION_SIZE: usize = TF_FULL_ACTION_PLANES * TF_FULL_CELLS;
pub const TF_FULL_PLAN_SIZE: usize = 144;
pub const TF_FULL_MAX_RECORDED_TRAINS: usize = 4;
pub const TF_FULL_MAX_TROLLS_PER_PLAYER: usize = 12;

const FRUIT_NAMES: [&str; 4] = ["PLUM", "LEMON", "APPLE", "BANANA"];

#[inline]
fn spatial(cell: Cell) -> usize {
    cell.1 as usize * TF_FULL_WIDTH + cell.0 as usize
}

#[inline]
fn action_index(plane: usize, cell: Cell) -> usize {
    plane * TF_FULL_CELLS + spatial(cell)
}

#[inline]
fn quant(value: i32, scale: i32) -> u8 {
    if scale <= 0 {
        return 0;
    }
    let value = value.clamp(0, scale) as f64;
    (255.0 * value / scale as f64).round() as u8
}

#[inline]
fn view_cell(game: &GameState, seat: usize, cell: Cell) -> Cell {
    if seat == 0 {
        cell
    } else {
        (game.width - 1 - cell.0, game.height - 1 - cell.1)
    }
}

#[inline]
fn absolute_cell(game: &GameState, seat: usize, cell: Cell) -> Cell {
    view_cell(game, seat, cell)
}

#[inline]
fn manhattan(left: Cell, right: Cell) -> i32 {
    (left.0 - right.0).abs() + (left.1 - right.1).abs()
}

fn own_units(game: &GameState, seat: usize) -> Vec<&Unit> {
    let mut units: Vec<_> = game
        .units
        .iter()
        .filter(|unit| unit.player as usize == seat)
        .collect();
    units.sort_by_key(|unit| unit.id);
    units
}

#[derive(Clone, Debug, Deserialize)]
struct JsonPlant {
    #[serde(rename = "type")]
    plant_type: String,
    x: i32,
    y: i32,
    size: i32,
    health: i32,
    fruits: i32,
    #[serde(alias = "cur_cd")]
    cooldown: i32,
}

impl From<JsonPlant> for Plant {
    fn from(value: JsonPlant) -> Self {
        Self {
            plant_type: value.plant_type,
            x: value.x,
            y: value.y,
            size: value.size,
            health: value.health,
            fruits: value.fruits,
            cooldown: value.cooldown,
        }
    }
}

#[derive(Clone, Debug, Deserialize)]
struct MapRecord {
    w: i32,
    h: i32,
    rows: Vec<String>,
    trees0: Vec<JsonPlant>,
}

impl MapRecord {
    fn to_game(&self, inventories: [[i32; 6]; 2]) -> Result<GameState, String> {
        if self.w <= 0
            || self.h <= 0
            || self.w as usize > TF_FULL_WIDTH
            || self.h as usize > TF_FULL_HEIGHT
            || self.rows.len() != self.h as usize
            || self
                .rows
                .iter()
                .any(|row| row.chars().count() != self.w as usize)
        {
            return Err("map dimensions or rows do not match the full environment".to_string());
        }
        let row_refs: Vec<_> = self.rows.iter().map(String::as_str).collect();
        let mut game = from_ascii(&row_refs);
        if game.width != self.w || game.height != self.h {
            return Err("parsed map dimensions differ from record".to_string());
        }
        game.inventories = inventories;
        game.plants = self.trees0.clone().into_iter().map(Plant::from).collect();
        recompute_scores(&mut game);
        Ok(game)
    }
}

#[derive(Clone, Debug, Deserialize)]
struct JsonUnit {
    id: i32,
    player: i32,
    x: i32,
    y: i32,
    ms: i32,
    cc: i32,
    hp: i32,
    chop: i32,
    carry: [i32; 6],
}

impl From<JsonUnit> for Unit {
    fn from(value: JsonUnit) -> Self {
        Self {
            id: value.id,
            player: value.player,
            x: value.x,
            y: value.y,
            ms: value.ms,
            cc: value.cc,
            hp: value.hp,
            chop: value.chop,
            carry: value.carry,
        }
    }
}

#[derive(Clone, Copy, Debug, Deserialize, Serialize)]
struct StagedAction {
    troll_id: i32,
    action_index: i32,
}

#[derive(Clone, Debug, Deserialize)]
struct JsonState {
    w: i32,
    h: i32,
    rows: Vec<String>,
    turn: i32,
    inv: [[i32; 6]; 2],
    units: Vec<JsonUnit>,
    plants: Vec<JsonPlant>,
    #[serde(default)]
    staged_actions: Vec<StagedAction>,
}

impl JsonState {
    fn to_game(&self) -> Result<GameState, String> {
        let record = MapRecord {
            w: self.w,
            h: self.h,
            rows: self.rows.clone(),
            trees0: self.plants.clone(),
        };
        let mut game = record.to_game(self.inv)?;
        game.turn = self.turn;
        game.units = self.units.clone().into_iter().map(Unit::from).collect();
        game.next_id = game.units.iter().map(|unit| unit.id).max().unwrap_or(-1) + 1;
        recompute_scores(&mut game);
        Ok(game)
    }
}

fn decode_plan(plan_index: usize) -> Option<(i32, i32, i32, i32)> {
    if plan_index >= TF_FULL_PLAN_SIZE {
        return None;
    }
    if plan_index == 0 {
        return Some((0, 0, 0, 0));
    }
    let chop = (plan_index % 4) as i32;
    let rest = plan_index / 4;
    let harvest = (rest % 3) as i32;
    let rest = rest / 3;
    let carry = (rest % 4) as i32 + 1;
    let movement = (rest / 4) as i32 + 1;
    Some((movement, carry, harvest, chop))
}

fn legal_plan_mask(game: &GameState, seat: usize, output: &mut [u8]) {
    output.fill(0);
    output[0] = 1;
    if own_units(game, seat).len() >= TF_FULL_MAX_TROLLS_PER_PLAYER {
        return;
    }
    for (index, slot) in output.iter_mut().enumerate().skip(1) {
        let (_, carry, harvest, chop) = decode_plan(index).expect("bounded plan index");
        *slot = u8::from(!(harvest == 0 && chop == 0) && harvest <= carry);
    }
}

fn staged_game(game: &GameState, seat: usize, staged: &[StagedAction]) -> GameState {
    let mut shown = game.clone();
    for staged_action in staged {
        let index = staged_action.action_index.max(0) as usize;
        if index >= TF_FULL_ACTION_SIZE || index / TF_FULL_CELLS != 0 {
            continue;
        }
        let relative = (
            (index % TF_FULL_CELLS) % TF_FULL_WIDTH,
            (index % TF_FULL_CELLS) / TF_FULL_WIDTH,
        );
        let target = absolute_cell(game, seat, (relative.0 as i32, relative.1 as i32));
        let Some(unit) = shown
            .units
            .iter_mut()
            .find(|unit| unit.id == staged_action.troll_id && unit.player as usize == seat)
        else {
            continue;
        };
        let destination = next_cell(&game.walkable, unit.pos(), target, unit.ms);
        unit.x = destination.0;
        unit.y = destination.1;
    }
    shown
}

fn reserved_cells(game: &GameState, seat: usize, staged: &[StagedAction]) -> HashSet<Cell> {
    let shown = staged_game(game, seat, staged);
    staged
        .iter()
        .filter_map(|action| {
            shown
                .units
                .iter()
                .find(|unit| unit.id == action.troll_id && unit.player as usize == seat)
                .map(Unit::pos)
        })
        .collect()
}

fn legal_action_mask(
    game: &GameState,
    seat: usize,
    active_troll_id: i32,
    staged: &[StagedAction],
    output: &mut [u8],
) -> Result<(), String> {
    output.fill(0);
    let shown = staged_game(game, seat, staged);
    let unit = shown
        .units
        .iter()
        .find(|unit| unit.id == active_troll_id && unit.player as usize == seat)
        .ok_or_else(|| "active troll does not belong to viewing seat".to_string())?;
    let reservations = reserved_cells(game, seat, staged);
    let reachable = bfs_distances(&game.walkable, &[unit.pos()]);
    for &target in &game.walkable {
        if !reachable.contains_key(&target) {
            continue;
        }
        let destination = next_cell(&game.walkable, unit.pos(), target, unit.ms);
        if reservations.contains(&destination) {
            continue;
        }
        output[action_index(0, view_cell(game, seat, target))] = 1;
    }
    let current_view = view_cell(game, seat, unit.pos());
    output[action_index(0, current_view)] = 1;
    let current = unit.pos();
    let plant = game
        .plants
        .iter()
        .find(|plant| plant.pos() == current && plant.health > 0);
    if unit.hp > 0 && unit.free() > 0 && plant.is_some_and(|plant| plant.fruits > 0) {
        output[action_index(1, current_view)] = 1;
    }
    if unit.chop > 0 && plant.is_some() {
        output[action_index(2, current_view)] = 1;
    }
    if unit.total() > 0 && manhattan(current, game.shacks[seat]) <= 1 {
        output[action_index(3, current_view)] = 1;
    }
    if unit.chop > 0
        && unit.free() > 0
        && game.iron.iter().any(|iron| manhattan(*iron, current) == 1)
    {
        output[action_index(4, current_view)] = 1;
    }
    for kind in 0..4 {
        if game.walkable.contains(&current)
            && !game.plants.iter().any(|plant| plant.pos() == current)
            && unit.carry[kind] > 0
        {
            output[action_index(5 + kind, current_view)] = 1;
        }
        if unit.free() > 0
            && manhattan(current, game.shacks[seat]) <= 1
            && game.inventories[seat][kind] > 0
        {
            output[action_index(9 + kind, current_view)] = 1;
        }
    }
    Ok(())
}

fn set_cell(output: &mut [u8], plane: usize, cell: Cell, value: u8) {
    if cell.0 >= 0
        && cell.1 >= 0
        && (cell.0 as usize) < TF_FULL_WIDTH
        && (cell.1 as usize) < TF_FULL_HEIGHT
    {
        output[plane * TF_FULL_CELLS + spatial(cell)] = value;
    }
}

fn broadcast(output: &mut [u8], game: &GameState, plane: usize, value: u8) {
    for y in 0..game.height {
        for x in 0..game.width {
            set_cell(output, plane, (x, y), value);
        }
    }
}

fn distance_plane(
    output: &mut [u8],
    game: &GameState,
    seat: usize,
    plane: usize,
    sources: &[Cell],
) {
    let distances = bfs_distances(&game.walkable, sources);
    for y in 0..game.height {
        for x in 0..game.width {
            let cell = (x, y);
            let value = distances.get(&cell).copied().unwrap_or(40).clamp(0, 40);
            set_cell(output, plane, view_cell(game, seat, cell), quant(value, 40));
        }
    }
}

fn fill_observation(
    game: &GameState,
    seat: usize,
    active_troll_id: i32,
    phase: i32,
    plan_index: usize,
    prior_target_trained: bool,
    staged: &[StagedAction],
    output: &mut [u8],
) -> Result<(), String> {
    if output.len() != TF_FULL_OBS_SIZE || seat > 1 || !matches!(phase, 0 | 1) {
        return Err("invalid observation scalar or buffer contract".to_string());
    }
    output.fill(0);
    let shown = staged_game(game, seat, staged);
    for y in 0..game.height {
        for x in 0..game.width {
            let absolute = (x, y);
            let cell = view_cell(game, seat, absolute);
            set_cell(output, 0, cell, 255);
            if game.walkable.contains(&absolute) {
                set_cell(output, 1, cell, 255);
            } else if game.water.contains(&absolute) {
                set_cell(output, 2, cell, 255);
            } else if game.iron.contains(&absolute) {
                set_cell(output, 4, cell, 255);
            } else if absolute != game.shacks[0] && absolute != game.shacks[1] {
                set_cell(output, 3, cell, 255);
            }
            if absolute == game.shacks[seat] {
                set_cell(output, 5, cell, 255);
            }
            if absolute == game.shacks[1 - seat] {
                set_cell(output, 6, cell, 255);
            }
            if game.iron.iter().any(|iron| manhattan(*iron, absolute) == 1) {
                set_cell(output, 40, cell, 255);
            }
            if game
                .water
                .iter()
                .any(|water| manhattan(*water, absolute) == 1)
            {
                set_cell(output, 41, cell, 255);
            }
        }
    }
    for plant in &game.plants {
        if plant.health <= 0 {
            continue;
        }
        let cell = view_cell(game, seat, plant.pos());
        set_cell(output, 7, cell, 255);
        if let Ok(kind) = std::panic::catch_unwind(|| item_index(&plant.plant_type)) {
            if kind < 4 {
                set_cell(output, 8 + kind, cell, 255);
            }
        }
        set_cell(output, 12, cell, quant(plant.size, 4));
        set_cell(output, 13, cell, quant(plant.health, 20));
        set_cell(output, 14, cell, quant(plant.fruits, 3));
        set_cell(output, 15, cell, quant(plant.cooldown, 9));
    }
    for unit in &shown.units {
        let own = unit.player as usize == seat;
        let cell = view_cell(game, seat, unit.pos());
        let base = if own { 18 } else { 28 };
        set_cell(output, if own { 16 } else { 17 }, cell, 255);
        set_cell(output, base, cell, quant(unit.ms, 3));
        set_cell(output, base + 1, cell, quant(unit.cc, 4));
        set_cell(output, base + 2, cell, quant(unit.hp, 3));
        set_cell(output, base + 3, cell, quant(unit.chop, 3));
        for kind in 0..6 {
            set_cell(output, base + 4 + kind, cell, quant(unit.carry[kind], 4));
        }
        set_cell(
            output,
            if own { 93 } else { 95 },
            cell,
            quant(unit.total(), 4),
        );
        set_cell(
            output,
            if own { 94 } else { 96 },
            cell,
            quant(unit.free(), 4),
        );
        let full = unit.total() == unit.cc;
        let only_nonfruit = unit.carry[PLUM..=BANANA].iter().all(|value| *value == 0);
        if full {
            set_cell(output, if own { 100 } else { 102 }, cell, 255);
            if only_nonfruit {
                set_cell(output, if own { 101 } else { 103 }, cell, 255);
            }
        }
        if own && phase == 1 && unit.id == active_troll_id {
            set_cell(output, 99, cell, 255);
        }
    }
    distance_plane(output, game, seat, 38, &[game.shacks[seat]]);
    distance_plane(output, game, seat, 39, &[game.shacks[1 - seat]]);
    for kind in 0..4 {
        let sources: Vec<_> = game
            .plants
            .iter()
            .filter(|plant| {
                plant.health > 0
                    && FRUIT_NAMES
                        .get(kind)
                        .is_some_and(|name| *name == plant.plant_type)
            })
            .map(Plant::pos)
            .collect();
        distance_plane(output, game, seat, 88 + kind, &sources);
    }
    let mine_sources: Vec<_> = game
        .walkable
        .iter()
        .copied()
        .filter(|cell| game.iron.iter().any(|iron| manhattan(*iron, *cell) == 1))
        .collect();
    distance_plane(output, game, seat, 92, &mine_sources);

    broadcast(output, game, 42, quant(game.turn, 300));
    for kind in 0..6 {
        broadcast(
            output,
            game,
            43 + kind,
            quant(
                game.inventories[seat][kind],
                if kind == WOOD { 128 } else { 64 },
            ),
        );
        broadcast(
            output,
            game,
            49 + kind,
            quant(
                game.inventories[1 - seat][kind],
                if kind == WOOD { 128 } else { 64 },
            ),
        );
    }
    broadcast(output, game, 55, quant(game.scores[seat], 1024));
    broadcast(output, game, 56, quant(game.scores[1 - seat], 1024));
    let ours = own_units(game, seat);
    let theirs = own_units(game, 1 - seat);
    broadcast(output, game, 57, quant(ours.len() as i32, 12));
    broadcast(output, game, 58, quant(theirs.len() as i32, 12));

    if plan_index != 0 {
        let target = decode_plan(plan_index).ok_or_else(|| "bad plan index".to_string())?;
        broadcast(output, game, 59, 255);
        broadcast(output, game, 60, quant(target.0, 3));
        broadcast(output, game, 61, quant(target.1, 4));
        broadcast(output, game, 62, quant(target.2, 2));
        broadcast(output, game, 63, quant(target.3, 3));
        let mut cost = training_cost(ours.len() as i32, target);
        if game.iron.is_empty() {
            cost[IRON] = 0;
        }
        for (offset, kind) in [PLUM, LEMON, APPLE, IRON].into_iter().enumerate() {
            broadcast(output, game, 64 + offset, quant(cost[kind], 32));
            broadcast(
                output,
                game,
                68 + offset,
                quant((cost[kind] - game.inventories[seat][kind]).max(0), 32),
            );
        }
    }
    let aggregate = |units: &[&Unit], field: fn(&Unit) -> i32| {
        (
            units.iter().map(|unit| field(unit)).max().unwrap_or(0),
            units.iter().map(|unit| field(unit)).sum::<i32>(),
        )
    };
    let fields: [fn(&Unit) -> i32; 4] = [
        |unit| unit.ms,
        |unit| unit.cc,
        |unit| unit.hp,
        |unit| unit.chop,
    ];
    let scales = [3, 4, 3, 3];
    let sum_scales = [36, 48, 36, 36];
    for (index, field) in fields.into_iter().enumerate() {
        let (own_max, own_sum) = aggregate(&ours, field);
        let (opp_max, opp_sum) = aggregate(&theirs, field);
        broadcast(output, game, 72 + index, quant(own_max, scales[index]));
        broadcast(output, game, 76 + index, quant(own_sum, sum_scales[index]));
        broadcast(output, game, 80 + index, quant(opp_max, scales[index]));
        broadcast(output, game, 84 + index, quant(opp_sum, sum_scales[index]));
    }
    if phase == 1 {
        broadcast(output, game, 97, 255);
    }
    if phase == 0 && prior_target_trained {
        broadcast(output, game, 98, 255);
    }
    Ok(())
}

fn decode_action_text(
    action: usize,
    troll_id: i32,
    width: i32,
    height: i32,
) -> Result<String, i32> {
    if action >= TF_FULL_ACTION_SIZE || width <= 0 || height <= 0 {
        return Err(-2);
    }
    let plane = action / TF_FULL_CELLS;
    let cell = action % TF_FULL_CELLS;
    let x = (cell % TF_FULL_WIDTH) as i32;
    let y = (cell / TF_FULL_WIDTH) as i32;
    if x >= width || y >= height {
        return Err(-2);
    }
    let text = match plane {
        0 => format!("MOVE {troll_id} {x} {y}"),
        1 => format!("HARVEST {troll_id}"),
        2 => format!("CHOP {troll_id}"),
        3 => format!("DROP {troll_id}"),
        4 => format!("MINE {troll_id}"),
        5..=8 => format!("PLANT {troll_id} {}", FRUIT_NAMES[plane - 5]),
        9..=12 => format!("PICK {troll_id} {}", FRUIT_NAMES[plane - 9]),
        _ => return Err(-2),
    };
    Ok(text)
}

fn encode_command_text(
    command: &str,
    expected_troll_id: i32,
    width: i32,
    height: i32,
) -> Result<usize, i32> {
    let parts: Vec<_> = command.split_whitespace().collect();
    if parts.len() < 2 || width <= 0 || height <= 0 {
        return Err(-2);
    }
    let id = parts[1].parse::<i32>().map_err(|_| -2)?;
    if id != expected_troll_id {
        return Err(-2);
    }
    let plane = match parts[0] {
        "MOVE" if parts.len() == 4 => {
            let x = parts[2].parse::<i32>().map_err(|_| -2)?;
            let y = parts[3].parse::<i32>().map_err(|_| -2)?;
            if x < 0 || y < 0 || x >= width || y >= height {
                return Err(-2);
            }
            return Ok(action_index(0, (x, y)));
        }
        "HARVEST" if parts.len() == 2 => 1,
        "CHOP" if parts.len() == 2 => 2,
        "DROP" if parts.len() == 2 => 3,
        "MINE" if parts.len() == 2 => 4,
        "PLANT" if parts.len() == 3 => {
            5 + FRUIT_NAMES
                .iter()
                .position(|name| *name == parts[2])
                .ok_or(-2)?
        }
        "PICK" if parts.len() == 3 => {
            9 + FRUIT_NAMES
                .iter()
                .position(|name| *name == parts[2])
                .ok_or(-2)?
        }
        _ => return Err(-2),
    };
    // Non-spatial commands carry no coordinate.  The state-aware caller moves
    // this canonical plane index to the active troll's cell.
    Ok(plane * TF_FULL_CELLS)
}

#[no_mangle]
pub extern "C" fn tf_full_obs_size() -> usize {
    TF_FULL_OBS_SIZE
}

#[no_mangle]
pub extern "C" fn tf_full_action_size() -> usize {
    TF_FULL_ACTION_SIZE
}

#[no_mangle]
pub extern "C" fn tf_full_plan_size() -> usize {
    TF_FULL_PLAN_SIZE
}

#[no_mangle]
pub unsafe extern "C" fn tf_full_decode_action(
    action: i32,
    troll_id: i32,
    width: i32,
    height: i32,
    output_utf8: *mut u8,
    output_capacity: usize,
) -> i32 {
    if output_utf8.is_null() {
        return -1;
    }
    let text = match usize::try_from(action)
        .map_err(|_| -2)
        .and_then(|index| decode_action_text(index, troll_id, width, height))
    {
        Ok(text) => text,
        Err(status) => return status,
    };
    if output_capacity <= text.len() {
        return -6;
    }
    let output = std::slice::from_raw_parts_mut(output_utf8, output_capacity);
    output[..text.len()].copy_from_slice(text.as_bytes());
    output[text.len()] = 0;
    text.len() as i32
}

#[no_mangle]
pub unsafe extern "C" fn tf_full_encode_command(
    command_utf8: *const u8,
    command_length: usize,
    expected_troll_id: i32,
    width: i32,
    height: i32,
) -> i32 {
    if command_utf8.is_null() {
        return -1;
    }
    let bytes = std::slice::from_raw_parts(command_utf8, command_length);
    let command = match std::str::from_utf8(bytes) {
        Ok(command) => command,
        Err(_) => return -2,
    };
    match encode_command_text(command, expected_troll_id, width, height) {
        Ok(index) => index as i32,
        Err(status) => status,
    }
}

#[no_mangle]
pub unsafe extern "C" fn tf_full_decode_plan(plan_index: i32, talents_4: *mut i8) -> i32 {
    if talents_4.is_null() {
        return -1;
    }
    let plan = match usize::try_from(plan_index).ok().and_then(decode_plan) {
        Some(plan) => plan,
        None => return -2,
    };
    let output = std::slice::from_raw_parts_mut(talents_4, 4);
    output.copy_from_slice(&[plan.0 as i8, plan.1 as i8, plan.2 as i8, plan.3 as i8]);
    0
}

#[no_mangle]
pub unsafe extern "C" fn tf_full_obs_from_state(
    json_utf8: *const u8,
    json_length: usize,
    seat: i32,
    active_troll_id: i32,
    phase: i32,
    plan_index: i32,
    prior_target_trained: u8,
    obs: *mut u8,
    mask: *mut u8,
    plan_mask: *mut u8,
) -> i32 {
    if json_utf8.is_null() || obs.is_null() {
        return -1;
    }
    if !(0..=1).contains(&seat)
        || !matches!(phase, 0 | 1)
        || !(0..TF_FULL_PLAN_SIZE as i32).contains(&plan_index)
    {
        return -2;
    }
    let bytes = std::slice::from_raw_parts(json_utf8, json_length);
    let parsed: JsonState = match serde_json::from_slice(bytes) {
        Ok(parsed) => parsed,
        Err(_) => return -3,
    };
    let game = match parsed.to_game() {
        Ok(game) => game,
        Err(_) => return -3,
    };
    let output = std::slice::from_raw_parts_mut(obs, TF_FULL_OBS_SIZE);
    if fill_observation(
        &game,
        seat as usize,
        active_troll_id,
        phase,
        plan_index as usize,
        prior_target_trained != 0,
        &parsed.staged_actions,
        output,
    )
    .is_err()
    {
        return -2;
    }
    if !mask.is_null() {
        let output = std::slice::from_raw_parts_mut(mask, TF_FULL_ACTION_SIZE);
        output.fill(0);
        if phase == 1
            && legal_action_mask(
                &game,
                seat as usize,
                active_troll_id,
                &parsed.staged_actions,
                output,
            )
            .is_err()
        {
            return -2;
        }
    }
    if !plan_mask.is_null() {
        let output = std::slice::from_raw_parts_mut(plan_mask, TF_FULL_PLAN_SIZE);
        output.fill(0);
        if phase == 0 {
            legal_plan_mask(&game, seat as usize, output);
        }
    }
    0
}

#[cfg(test)]
mod tests {
    use super::*;

    fn tiny_state_json() -> String {
        r#"{
            "w":5,"h":3,"rows":["0...1","..+..","....."],"turn":7,
            "inv":[[4,5,6,7,8,9],[9,8,7,6,5,4]],
            "units":[
              {"id":0,"player":0,"x":0,"y":0,"ms":1,"cc":1,"hp":1,"chop":1,"carry":[0,0,0,0,0,0]},
              {"id":1,"player":1,"x":4,"y":0,"ms":1,"cc":1,"hp":1,"chop":1,"carry":[0,0,0,0,0,0]}],
            "plants":[{"type":"PLUM","x":2,"y":2,"size":4,"health":12,"fruits":3,"cooldown":8}],
            "staged_actions":[]
        }"#
        .to_string()
    }

    #[test]
    fn plan_index_round_trip_and_mask() {
        for index in 0..TF_FULL_PLAN_SIZE {
            let plan = decode_plan(index).unwrap();
            if index != 0 {
                let encoded = (((plan.0 - 1) * 4 + (plan.1 - 1)) * 3 + plan.2) * 4 + plan.3;
                assert_eq!(encoded as usize, index);
            }
        }
        let parsed: JsonState = serde_json::from_str(&tiny_state_json()).unwrap();
        let game = parsed.to_game().unwrap();
        let mut mask = [0u8; TF_FULL_PLAN_SIZE];
        legal_plan_mask(&game, 0, &mut mask);
        assert_eq!(mask[0], 1);
        assert_eq!(mask[1], 1);
        assert_eq!(mask[12], 0);
    }

    #[test]
    fn move_action_text_round_trips_every_cell() {
        for y in 0..3 {
            for x in 0..5 {
                let index = action_index(0, (x, y));
                let text = decode_action_text(index, 17, 5, 3).unwrap();
                assert_eq!(encode_command_text(&text, 17, 5, 3).unwrap(), index);
            }
        }
    }

    #[test]
    fn state_observation_has_signed_plan_phase_semantics() {
        let parsed: JsonState = serde_json::from_str(&tiny_state_json()).unwrap();
        let game = parsed.to_game().unwrap();
        let mut obs = vec![0; TF_FULL_OBS_SIZE];
        fill_observation(&game, 0, 0, 1, 0, false, &[], &mut obs).unwrap();
        assert_eq!(
            obs[97 * TF_FULL_CELLS],
            255,
            "zero plan still sets phase bit"
        );
        assert_eq!(obs[59 * TF_FULL_CELLS], 0);
        assert_eq!(obs[99 * TF_FULL_CELLS], 255);
    }
}
