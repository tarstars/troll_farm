//! Full-game, real-map neural-policy environment.
//!
//! The public ABI is documented in `local_claude_1/nn-bot/ENV-API.md` and the
//! observation layout in `local_claude_1/nn-bot/OBS-PLANES.md`.  This module
//! deliberately uses the exact referee [`GameState`] and [`engine::step`]
//! instead of a second mechanics port.

use std::collections::HashSet;
use std::ffi::CStr;
use std::fs;
use std::os::raw::c_char;

use rayon::prelude::*;
use serde::{Deserialize, Serialize};

use crate::game::engine::{
    bfs_distances, has_stalled, item_index, next_cell, recompute_scores, step, training_cost,
    APPLE, BANANA, IRON, LEMON, PLUM, WOOD,
};
use crate::game::official_mapgen::Sha1Prng;
use crate::game::state::{from_ascii, Cell, GameState, Plant, Unit};
use crate::resident_policy::bot::moisan::SecureOrchardBot;
use crate::resident_policy::bot::Bot as ResidentBot;
use crate::resident_policy::game::{
    GameState as ResidentState, Plant as ResidentPlant, PlantKind, Stats as ResidentStats,
    Unit as ResidentUnit,
};
use crate::strategies::gold_elite::GoldElite;
use crate::strategies::legend_field_proxy::{LegendFieldProxyV2, LegendFieldProxyV2Config};
use crate::strategies::mybot::MyBot;
use crate::strategies::norxondor_native::NorxondorNative;
use crate::strategies::script_boss::ScriptBoss;
use crate::strategies::Strategy;

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

#[derive(Clone, Debug, Deserialize, Serialize)]
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

impl From<&Plant> for JsonPlant {
    fn from(value: &Plant) -> Self {
        Self {
            plant_type: value.plant_type.clone(),
            x: value.x,
            y: value.y,
            size: value.size,
            health: value.health,
            fruits: value.fruits,
            cooldown: value.cooldown,
        }
    }
}

#[derive(Clone, Debug, Deserialize, Serialize)]
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

#[derive(Clone, Debug)]
struct MoveRouting {
    distances: Vec<i16>,
}

impl MoveRouting {
    fn new(game: &GameState) -> Self {
        let mut distances = vec![-1; TF_FULL_CELLS * TF_FULL_CELLS];
        let mut sources: Vec<_> = game.walkable.iter().copied().collect();
        sources.extend(game.shacks);
        sources.sort_unstable();
        sources.dedup();
        for source in sources {
            for (target, distance) in bfs_distances(&game.walkable, &[source]) {
                distances[spatial(source) * TF_FULL_CELLS + spatial(target)] = distance as i16;
            }
        }
        Self { distances }
    }

    fn distance(&self, source: Cell, target: Cell) -> Option<i32> {
        let distance = self.distances[spatial(source) * TF_FULL_CELLS + spatial(target)];
        (distance >= 0).then_some(i32::from(distance))
    }

    fn next_cell(&self, game: &GameState, current: Cell, target: Cell, speed: i32) -> Cell {
        let Some(total_distance) = self.distance(current, target) else {
            return next_cell(&game.walkable, current, target, speed);
        };
        if total_distance <= speed {
            return target;
        }
        let mut best: Option<(i32, Cell)> = None;
        for y in 0..game.height {
            for x in 0..game.width {
                let candidate = (x, y);
                let Some(from_source) = self.distance(current, candidate) else {
                    continue;
                };
                if from_source > speed {
                    continue;
                }
                let Some(to_target) = self.distance(candidate, target) else {
                    continue;
                };
                let option = (to_target, candidate);
                if best.is_none_or(|current_best| option < current_best) {
                    best = Some(option);
                }
            }
        }
        best.map_or(current, |(_, cell)| cell)
    }
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

fn staged_game(
    game: &GameState,
    seat: usize,
    staged: &[StagedAction],
    routing: Option<&MoveRouting>,
) -> GameState {
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
        let destination = routing.map_or_else(
            || next_cell(&game.walkable, unit.pos(), target, unit.ms),
            |routes| routes.next_cell(game, unit.pos(), target, unit.ms),
        );
        unit.x = destination.0;
        unit.y = destination.1;
    }
    shown
}

fn reserved_cells(shown: &GameState, seat: usize, staged: &[StagedAction]) -> HashSet<Cell> {
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
    routing: Option<&MoveRouting>,
    output: &mut [u8],
) -> Result<(), String> {
    output.fill(0);
    let shown = staged_game(game, seat, staged, routing);
    let unit = shown
        .units
        .iter()
        .find(|unit| unit.id == active_troll_id && unit.player as usize == seat)
        .ok_or_else(|| "active troll does not belong to viewing seat".to_string())?;
    let reservations = reserved_cells(&shown, seat, staged);
    let reachable = bfs_distances(&game.walkable, &[unit.pos()]);
    for &target in &game.walkable {
        if !reachable.contains_key(&target) {
            continue;
        }
        let destination = routing.map_or_else(
            || next_cell(&game.walkable, unit.pos(), target, unit.ms),
            |routes| routes.next_cell(game, unit.pos(), target, unit.ms),
        );
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

fn validate_masked_action(
    game: &GameState,
    seat: usize,
    active_troll: i32,
    phase: i32,
    staged: &[StagedAction],
    routing: Option<&MoveRouting>,
    action: i32,
) -> Result<(), i32> {
    match phase {
        0 => {
            let action = usize::try_from(action).map_err(|_| -4)?;
            let mut mask = [0u8; TF_FULL_PLAN_SIZE];
            legal_plan_mask(game, seat, &mut mask);
            if action < mask.len() && mask[action] != 0 {
                Ok(())
            } else {
                Err(-4)
            }
        }
        1 => {
            let action = usize::try_from(action).map_err(|_| -4)?;
            let mut mask = vec![0u8; TF_FULL_ACTION_SIZE];
            legal_action_mask(game, seat, active_troll, staged, routing, &mut mask)
                .map_err(|_| -5)?;
            if action < mask.len() && mask[action] != 0 {
                Ok(())
            } else {
                Err(-4)
            }
        }
        _ => Err(-5),
    }
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
    routing: Option<&MoveRouting>,
    output: &mut [u8],
) -> Result<(), String> {
    if output.len() != TF_FULL_OBS_SIZE || seat > 1 || !matches!(phase, 0 | 1) {
        return Err("invalid observation scalar or buffer contract".to_string());
    }
    output.fill(0);
    let shown = staged_game(game, seat, staged, routing);
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

fn resident_view(game: &GameState, seat: usize) -> ResidentState {
    ResidentState {
        width: game.width,
        height: game.height,
        walkable: game.walkable.iter().copied().collect(),
        shacks: [game.shacks[seat], game.shacks[1 - seat]],
        inventories: [game.inventories[seat], game.inventories[1 - seat]],
        units: game
            .units
            .iter()
            .map(|unit| ResidentUnit {
                id: unit.id,
                player: usize::from(unit.player as usize != seat),
                cell: unit.pos(),
                stats: ResidentStats {
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
            .filter_map(|plant| {
                Some(ResidentPlant {
                    kind: PlantKind::parse(&plant.plant_type)?,
                    cell: plant.pos(),
                    size: plant.size,
                    health: plant.health,
                    fruits: plant.fruits,
                    cooldown: plant.cooldown,
                })
            })
            .collect(),
        scores: [game.scores[seat], game.scores[1 - seat]],
        turn: game.turn,
        next_id: game.next_id,
        iron: game.iron.iter().copied().collect(),
        water: game.water.iter().copied().collect(),
    }
}

enum FullOpponent {
    Resident(SecureOrchardBot),
    Norxondor(NorxondorNative),
    LegendField(LegendFieldProxyV2),
    GoldAdaptive(GoldElite),
    ScriptBoss(ScriptBoss),
    MyBot(MyBot),
}

impl FullOpponent {
    fn new(opponent_id: u8) -> Option<Self> {
        match opponent_id {
            0 => Some(Self::Resident(SecureOrchardBot::new())),
            1 => Some(Self::Norxondor(NorxondorNative::new(true))),
            2 => Some(Self::LegendField(LegendFieldProxyV2::configured(
                LegendFieldProxyV2Config {
                    producer_spec: (2, 2, 1, 1),
                    chopper_spec: (2, 2, 0, 2),
                    late_chop: true,
                },
            ))),
            3 => Some(Self::GoldAdaptive(GoldElite::adaptive())),
            4 => Some(Self::ScriptBoss(ScriptBoss::new())),
            5 => Some(Self::MyBot(MyBot::new())),
            6 => None,
            _ => unreachable!("validated opponent id"),
        }
    }

    fn commands(&mut self, game: &GameState, seat: usize) -> Vec<String> {
        match self {
            Self::Resident(bot) => bot.commands(&resident_view(game, seat)),
            Self::Norxondor(strategy) => strategy.decide(game, seat),
            Self::LegendField(strategy) => strategy.decide(game, seat),
            Self::GoldAdaptive(strategy) => strategy.decide(game, seat),
            Self::ScriptBoss(strategy) => strategy.decide(game, seat),
            Self::MyBot(strategy) => strategy.decide(game, seat),
        }
    }
}

#[derive(Clone, Debug, Serialize)]
struct ReplayTurn {
    turn: i32,
    commands0: Vec<String>,
    commands1: Vec<String>,
    state: ReplayState,
    state_hash: u64,
}

#[derive(Clone, Debug, Serialize)]
struct ReplayUnit {
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

#[derive(Clone, Debug, Serialize)]
struct ReplayState {
    turn: i32,
    next_id: i32,
    inventories: [[i32; 6]; 2],
    scores: [i32; 2],
    units: Vec<ReplayUnit>,
    plants: Vec<JsonPlant>,
}

impl From<&GameState> for ReplayState {
    fn from(game: &GameState) -> Self {
        let mut units: Vec<_> = game.units.iter().collect();
        units.sort_by_key(|unit| unit.id);
        let units = units
            .into_iter()
            .map(|unit| ReplayUnit {
                id: unit.id,
                player: unit.player,
                x: unit.x,
                y: unit.y,
                ms: unit.ms,
                cc: unit.cc,
                hp: unit.hp,
                chop: unit.chop,
                carry: unit.carry,
            })
            .collect();
        let mut plants: Vec<_> = game.plants.iter().collect();
        plants.sort_by_key(|plant| (plant.pos(), &plant.plant_type));
        Self {
            turn: game.turn,
            next_id: game.next_id,
            inventories: game.inventories,
            scores: game.scores,
            units,
            plants: plants.into_iter().map(JsonPlant::from).collect(),
        }
    }
}

#[derive(Clone, Debug, Serialize)]
struct ReplayRecord {
    schema_version: u8,
    episode_seed: u64,
    map_index: u32,
    map: MapRecord,
    initial_inventories: [[i32; 6]; 2],
    learned_seat: usize,
    opponent_id: u8,
    turns: Vec<ReplayTurn>,
    terminal_state_hash: u64,
}

#[derive(Clone, Copy, Debug, Default)]
struct TrainRecord {
    spec: [i8; 4],
    turn: u16,
}

#[derive(Clone, Debug, Default)]
struct TurnOutcome {
    reward: f32,
    reward_credit_count: u8,
    done: bool,
    win: bool,
    episode_turns: u16,
    episode_return: f32,
    episode_seed: u64,
    map_index: u32,
    opponent_id: u8,
    score_own: i32,
    score_opp: i32,
    trained: [TrainRecord; TF_FULL_MAX_RECORDED_TRAINS],
    trained_count: u8,
    trained_overflow: u8,
    illegal_commands: u16,
    action_hash: u64,
    state_hash: u64,
    replay: Option<Vec<u8>>,
}

fn state_hash(game: &GameState) -> u64 {
    fn mix(hash: &mut u64, value: i64) {
        for byte in value.to_le_bytes() {
            *hash ^= u64::from(byte);
            *hash = hash.wrapping_mul(0x100000001b3);
        }
    }
    let mut hash = 0xcbf29ce484222325;
    for value in [
        game.width,
        game.height,
        game.turn,
        game.next_id,
        game.scores[0],
        game.scores[1],
    ] {
        mix(&mut hash, i64::from(value));
    }
    for shack in game.shacks {
        mix(&mut hash, i64::from(shack.0));
        mix(&mut hash, i64::from(shack.1));
    }
    for inventory in game.inventories {
        for value in inventory {
            mix(&mut hash, i64::from(value));
        }
    }
    let mut units: Vec<_> = game.units.iter().collect();
    units.sort_by_key(|unit| unit.id);
    for unit in units {
        for value in [
            unit.id,
            unit.player,
            unit.x,
            unit.y,
            unit.ms,
            unit.cc,
            unit.hp,
            unit.chop,
        ] {
            mix(&mut hash, i64::from(value));
        }
        for value in unit.carry {
            mix(&mut hash, i64::from(value));
        }
    }
    let mut plants: Vec<_> = game.plants.iter().collect();
    plants.sort_by_key(|plant| (plant.pos(), &plant.plant_type));
    for plant in plants {
        for byte in plant.plant_type.as_bytes() {
            hash ^= u64::from(*byte);
            hash = hash.wrapping_mul(0x100000001b3);
        }
        for value in [
            plant.x,
            plant.y,
            plant.size,
            plant.health,
            plant.fruits,
            plant.cooldown,
        ] {
            mix(&mut hash, i64::from(value));
        }
    }
    for cells in [&game.walkable, &game.iron, &game.water] {
        let mut cells: Vec<_> = cells.iter().copied().collect();
        cells.sort_unstable();
        mix(&mut hash, cells.len() as i64);
        for cell in cells {
            mix(&mut hash, i64::from(cell.0));
            mix(&mut hash, i64::from(cell.1));
        }
    }
    hash
}

fn hash_commands(hash: &mut u64, commands0: &[String], commands1: &[String]) {
    for (seat, commands) in [commands0, commands1].into_iter().enumerate() {
        *hash ^= seat as u64;
        *hash = hash.wrapping_mul(0x100000001b3);
        for command in commands {
            for byte in command.as_bytes() {
                *hash ^= u64::from(*byte);
                *hash = hash.wrapping_mul(0x100000001b3);
            }
            *hash ^= 0xff;
            *hash = hash.wrapping_mul(0x100000001b3);
        }
    }
}

fn action_command(game: &GameState, seat: usize, staged: StagedAction) -> Result<String, i32> {
    let index = usize::try_from(staged.action_index).map_err(|_| -4)?;
    if index >= TF_FULL_ACTION_SIZE {
        return Err(-4);
    }
    let plane = index / TF_FULL_CELLS;
    if plane == 0 {
        let cell = index % TF_FULL_CELLS;
        let relative = ((cell % TF_FULL_WIDTH) as i32, (cell / TF_FULL_WIDTH) as i32);
        let target = absolute_cell(game, seat, relative);
        Ok(format!(
            "MOVE {} {} {}",
            staged.troll_id, target.0, target.1
        ))
    } else {
        decode_action_text(index, staged.troll_id, game.width, game.height)
    }
}

fn commands_from_staged(
    game: &GameState,
    seat: usize,
    staged: &[StagedAction],
) -> Result<Vec<String>, i32> {
    staged
        .iter()
        .copied()
        .map(|action| action_command(game, seat, action))
        .collect()
}

fn train_succeeds(
    game: &GameState,
    seat: usize,
    plan_index: usize,
    commands0: &[String],
    commands1: &[String],
) -> bool {
    if plan_index == 0 {
        return false;
    }
    let Some(spec) = decode_plan(plan_index) else {
        return false;
    };
    let before = own_units(game, seat).len();
    let mut probe = game.clone();
    let mut left = commands0.to_vec();
    let mut right = commands1.to_vec();
    let command = format!("TRAIN {} {} {} {}", spec.0, spec.1, spec.2, spec.3);
    if seat == 0 {
        left.insert(0, command);
    } else {
        right.insert(0, command);
    }
    step(&mut probe, &left, &right);
    own_units(&probe, seat).len() > before
}

struct FullEnv {
    state: GameState,
    routing: MoveRouting,
    map: MapRecord,
    map_index: u32,
    episode_seed: u64,
    learned_seat: usize,
    opponent_id: u8,
    opponent: Option<FullOpponent>,
    wood_shaping: f32,
    end_wood_value: f32,
    stall_counter: i32,
    episode_return: f32,
    initial_inventories: [[i32; 6]; 2],
    main_phase: i32,
    main_plan: usize,
    main_prior_target_trained: bool,
    main_roster: Vec<i32>,
    main_index: usize,
    main_staged: Vec<StagedAction>,
    external_phase: i32,
    external_plan: usize,
    external_prior_target_trained: bool,
    external_roster: Vec<i32>,
    external_index: usize,
    external_staged: Vec<StagedAction>,
    trained: Vec<TrainRecord>,
    illegal_commands: u16,
    action_hash: u64,
    replay_turns: Vec<ReplayTurn>,
}

impl FullEnv {
    fn new(
        maps: &[MapRecord],
        episode_seed: u64,
        opponent_weights: &[f32; 7],
        wood_shaping: f32,
        end_wood_value: f32,
    ) -> Result<Self, String> {
        let seed = if episode_seed == 0 {
            i64::MIN
        } else {
            episode_seed as i64
        };
        let mut random = Sha1Prng::new(seed);
        let map_index = random.next_int(maps.len() as i32) as usize;
        let learned_seat = random.next_int(2) as usize;
        let total_weight: f64 = opponent_weights
            .iter()
            .map(|weight| f64::from(*weight))
            .sum();
        let draw = f64::from(random.next_int(i32::MAX)) / f64::from(i32::MAX) * total_weight;
        let mut cumulative = 0.0;
        let mut opponent_id = 6u8;
        for (index, weight) in opponent_weights.iter().enumerate() {
            cumulative += f64::from(*weight);
            if draw < cumulative {
                opponent_id = index as u8;
                break;
            }
        }
        let mut inventories = [[0i32; 6]; 2];
        for kind in 0..5 {
            let stock = random.next_int_range(2, 11);
            inventories[0][kind] = stock;
            inventories[1][kind] = stock;
        }
        let state = maps[map_index].to_game(inventories)?;
        let routing = MoveRouting::new(&state);
        Ok(Self {
            state,
            routing,
            map: maps[map_index].clone(),
            map_index: map_index as u32,
            episode_seed,
            learned_seat,
            opponent_id,
            opponent: FullOpponent::new(opponent_id),
            wood_shaping,
            end_wood_value,
            stall_counter: 0,
            episode_return: 0.0,
            initial_inventories: inventories,
            main_phase: 0,
            main_plan: 0,
            main_prior_target_trained: false,
            main_roster: Vec::new(),
            main_index: 0,
            main_staged: Vec::new(),
            external_phase: 0,
            external_plan: 0,
            external_prior_target_trained: false,
            external_roster: Vec::new(),
            external_index: 0,
            external_staged: Vec::new(),
            trained: Vec::new(),
            illegal_commands: 0,
            action_hash: 0xcbf29ce484222325,
            replay_turns: Vec::new(),
        })
    }

    fn active_main_troll(&self) -> i32 {
        if self.main_phase == 1 {
            self.main_roster[self.main_index]
        } else {
            -1
        }
    }

    fn active_external_troll(&self) -> i32 {
        if self.external_phase == 1 {
            self.external_roster[self.external_index]
        } else {
            -1
        }
    }

    fn observe_main(&self, obs: &mut [u8], mask: &mut [u8], plan_mask: &mut [u8]) {
        obs.fill(0);
        mask.fill(0);
        plan_mask.fill(0);
        if self.main_phase == 2 {
            return;
        }
        fill_observation(
            &self.state,
            self.learned_seat,
            self.active_main_troll(),
            self.main_phase,
            self.main_plan,
            self.main_prior_target_trained,
            &self.main_staged,
            Some(&self.routing),
            obs,
        )
        .expect("internally valid full observation");
        if self.main_phase == 0 {
            legal_plan_mask(&self.state, self.learned_seat, plan_mask);
        } else {
            legal_action_mask(
                &self.state,
                self.learned_seat,
                self.active_main_troll(),
                &self.main_staged,
                Some(&self.routing),
                mask,
            )
            .expect("active full-environment troll");
        }
    }

    fn observe_external(&self, obs: &mut [u8], mask: &mut [u8], plan_mask: &mut [u8]) -> bool {
        obs.fill(0);
        mask.fill(0);
        plan_mask.fill(0);
        if self.main_phase != 2 || self.opponent_id != 6 {
            return false;
        }
        let seat = 1 - self.learned_seat;
        fill_observation(
            &self.state,
            seat,
            self.active_external_troll(),
            self.external_phase,
            self.external_plan,
            self.external_prior_target_trained,
            &self.external_staged,
            Some(&self.routing),
            obs,
        )
        .expect("internally valid external observation");
        if self.external_phase == 0 {
            legal_plan_mask(&self.state, seat, plan_mask);
        } else {
            legal_action_mask(
                &self.state,
                seat,
                self.active_external_troll(),
                &self.external_staged,
                Some(&self.routing),
                mask,
            )
            .expect("active external troll");
        }
        true
    }

    fn begin_external(&mut self) {
        self.main_phase = 2;
        self.external_phase = 0;
        self.external_plan = 0;
        self.external_roster.clear();
        self.external_index = 0;
        self.external_staged.clear();
    }

    fn finish_turn(
        &mut self,
        mut commands0: Vec<String>,
        mut commands1: Vec<String>,
    ) -> TurnOutcome {
        let learned_count_before = own_units(&self.state, self.learned_seat).len();
        let opponent_count_before = own_units(&self.state, 1 - self.learned_seat).len();
        let learned_plan_succeeds = train_succeeds(
            &self.state,
            self.learned_seat,
            self.main_plan,
            &commands0,
            &commands1,
        );
        let external_plan_succeeds = self.opponent_id == 6
            && train_succeeds(
                &self.state,
                1 - self.learned_seat,
                self.external_plan,
                &commands0,
                &commands1,
            );
        if learned_plan_succeeds {
            let spec = decode_plan(self.main_plan).expect("nonzero successful plan");
            let command = format!("TRAIN {} {} {} {}", spec.0, spec.1, spec.2, spec.3);
            if self.learned_seat == 0 {
                commands0.insert(0, command);
            } else {
                commands1.insert(0, command);
            }
        }
        if external_plan_succeeds {
            let spec = decode_plan(self.external_plan).expect("nonzero external plan");
            let command = format!("TRAIN {} {} {} {}", spec.0, spec.1, spec.2, spec.3);
            if self.learned_seat == 0 {
                commands1.insert(0, command);
            } else {
                commands0.insert(0, command);
            }
        }
        let before_wood = self.state.inventories[self.learned_seat][WOOD];
        let turn = self.state.turn;
        hash_commands(&mut self.action_hash, &commands0, &commands1);
        step(&mut self.state, &commands0, &commands1);
        let current_state_hash = state_hash(&self.state);
        self.replay_turns.push(ReplayTurn {
            turn,
            commands0,
            commands1,
            state: ReplayState::from(&self.state),
            state_hash: current_state_hash,
        });
        let learned_count_after = own_units(&self.state, self.learned_seat).len();
        let opponent_count_after = own_units(&self.state, 1 - self.learned_seat).len();
        self.main_prior_target_trained = learned_count_after > learned_count_before;
        self.external_prior_target_trained = opponent_count_after > opponent_count_before;
        if self.main_prior_target_trained {
            let spec = decode_plan(self.main_plan).expect("successful learned plan");
            self.trained.push(TrainRecord {
                spec: [spec.0 as i8, spec.1 as i8, spec.2 as i8, spec.3 as i8],
                turn: turn.clamp(0, u16::MAX as i32) as u16,
            });
        }
        let deposited = (self.state.inventories[self.learned_seat][WOOD] - before_wood).max(0);
        let mut reward = self.wood_shaping * deposited as f32;
        let done = self.state.turn > 300 || has_stalled(&self.state, &mut self.stall_counter);
        if done {
            let shaped_score = |seat: usize| {
                self.state.inventories[seat][PLUM..=BANANA]
                    .iter()
                    .sum::<i32>() as f32
                    + self.end_wood_value * self.state.inventories[seat][WOOD] as f32
            };
            reward += shaped_score(self.learned_seat) - shaped_score(1 - self.learned_seat);
        }
        self.episode_return += reward;
        let credit = 1usize.saturating_add(self.main_roster.len());
        self.main_phase = 0;
        self.main_plan = 0;
        self.main_roster.clear();
        self.main_index = 0;
        self.main_staged.clear();
        self.external_phase = 0;
        self.external_plan = 0;
        self.external_roster.clear();
        self.external_index = 0;
        self.external_staged.clear();
        let mut outcome = TurnOutcome {
            reward,
            reward_credit_count: credit.min(u8::MAX as usize) as u8,
            done,
            ..TurnOutcome::default()
        };
        if done {
            outcome.win =
                self.state.scores[self.learned_seat] > self.state.scores[1 - self.learned_seat];
            outcome.episode_turns =
                self.state.turn.saturating_sub(1).clamp(0, u16::MAX as i32) as u16;
            outcome.episode_return = self.episode_return;
            outcome.episode_seed = self.episode_seed;
            outcome.map_index = self.map_index;
            outcome.opponent_id = self.opponent_id;
            outcome.score_own = self.state.scores[self.learned_seat];
            outcome.score_opp = self.state.scores[1 - self.learned_seat];
            outcome.trained_count = self.trained.len().min(u8::MAX as usize) as u8;
            outcome.trained_overflow = self
                .trained
                .len()
                .saturating_sub(TF_FULL_MAX_RECORDED_TRAINS)
                .min(u8::MAX as usize) as u8;
            for (slot, record) in outcome.trained.iter_mut().zip(&self.trained) {
                *slot = *record;
            }
            outcome.illegal_commands = self.illegal_commands;
            outcome.action_hash = self.action_hash;
            outcome.state_hash = current_state_hash;
            let replay = ReplayRecord {
                schema_version: 1,
                episode_seed: self.episode_seed,
                map_index: self.map_index,
                map: self.map.clone(),
                initial_inventories: self.initial_inventories,
                learned_seat: self.learned_seat,
                opponent_id: self.opponent_id,
                turns: self.replay_turns.clone(),
                terminal_state_hash: current_state_hash,
            };
            outcome.replay = serde_json::to_vec(&replay).ok();
        }
        outcome
    }

    fn advance_main(&mut self, action: i32) -> Result<Option<TurnOutcome>, i32> {
        match self.main_phase {
            0 => {
                self.main_plan = action as usize;
                self.main_prior_target_trained = false;
                self.main_roster = own_units(&self.state, self.learned_seat)
                    .into_iter()
                    .map(|unit| unit.id)
                    .collect();
                self.main_index = 0;
                self.main_staged.clear();
                self.main_phase = 1;
                Ok(None)
            }
            1 => {
                self.main_staged.push(StagedAction {
                    troll_id: self.active_main_troll(),
                    action_index: action,
                });
                self.main_index += 1;
                if self.main_index < self.main_roster.len() {
                    return Ok(None);
                }
                let learned_commands =
                    commands_from_staged(&self.state, self.learned_seat, &self.main_staged)?;
                if self.opponent_id == 6 {
                    self.begin_external();
                    return Ok(None);
                }
                let opponent_commands = self
                    .opponent
                    .as_mut()
                    .expect("linked opponent")
                    .commands(&self.state, 1 - self.learned_seat);
                let (commands0, commands1) = if self.learned_seat == 0 {
                    (learned_commands, opponent_commands)
                } else {
                    (opponent_commands, learned_commands)
                };
                Ok(Some(self.finish_turn(commands0, commands1)))
            }
            2 => Ok(None),
            _ => Err(-5),
        }
    }

    fn advance_external(&mut self, action: i32) -> Result<Option<TurnOutcome>, i32> {
        if self.main_phase != 2 || self.opponent_id != 6 {
            return Ok(None);
        }
        let seat = 1 - self.learned_seat;
        match self.external_phase {
            0 => {
                self.external_plan = action as usize;
                self.external_prior_target_trained = false;
                self.external_roster = own_units(&self.state, seat)
                    .into_iter()
                    .map(|unit| unit.id)
                    .collect();
                self.external_index = 0;
                self.external_staged.clear();
                self.external_phase = 1;
                Ok(None)
            }
            1 => {
                self.external_staged.push(StagedAction {
                    troll_id: self.active_external_troll(),
                    action_index: action,
                });
                self.external_index += 1;
                if self.external_index < self.external_roster.len() {
                    return Ok(None);
                }
                let learned_commands =
                    commands_from_staged(&self.state, self.learned_seat, &self.main_staged)?;
                let external_commands =
                    commands_from_staged(&self.state, seat, &self.external_staged)?;
                let (commands0, commands1) = if self.learned_seat == 0 {
                    (learned_commands, external_commands)
                } else {
                    (external_commands, learned_commands)
                };
                Ok(Some(self.finish_turn(commands0, commands1)))
            }
            _ => Err(-5),
        }
    }
}

struct FullSlot {
    env: FullEnv,
    completed_replay: Option<Vec<u8>>,
    main_mask: Vec<u8>,
    main_plan_mask: Vec<u8>,
    external_mask: Vec<u8>,
    external_plan_mask: Vec<u8>,
    main_cache_valid: bool,
    external_cache_valid: bool,
}

impl FullSlot {
    fn new(env: FullEnv, completed_replay: Option<Vec<u8>>) -> Self {
        Self {
            env,
            completed_replay,
            main_mask: vec![0; TF_FULL_ACTION_SIZE],
            main_plan_mask: vec![0; TF_FULL_PLAN_SIZE],
            external_mask: vec![0; TF_FULL_ACTION_SIZE],
            external_plan_mask: vec![0; TF_FULL_PLAN_SIZE],
            main_cache_valid: false,
            external_cache_valid: false,
        }
    }
}

pub struct FullBatch {
    slots: Vec<FullSlot>,
    maps: Vec<MapRecord>,
    opponent_weights: [f32; 7],
    wood_shaping: f32,
    end_wood_value: f32,
    next_episode_seed: u64,
}

impl FullBatch {
    fn from_path(
        num_envs: usize,
        seed_base: u64,
        maps_path: &str,
        opponent_weights: [f32; 7],
        wood_shaping: f32,
        end_wood_value: f32,
    ) -> Result<Self, String> {
        if num_envs == 0
            || !wood_shaping.is_finite()
            || wood_shaping < 0.0
            || !end_wood_value.is_finite()
            || end_wood_value < 0.0
            || opponent_weights
                .iter()
                .any(|weight| !weight.is_finite() || *weight < 0.0)
            || opponent_weights.iter().all(|weight| *weight == 0.0)
        {
            return Err("invalid full environment constructor arguments".to_string());
        }
        let contents = fs::read_to_string(maps_path).map_err(|error| error.to_string())?;
        let maps: Vec<MapRecord> = contents
            .lines()
            .filter(|line| !line.trim().is_empty())
            .map(|line| serde_json::from_str(line).map_err(|error| error.to_string()))
            .collect::<Result<_, _>>()?;
        if maps.is_empty() {
            return Err("real-map file is empty".to_string());
        }
        for map in &maps {
            map.to_game([[2, 2, 2, 2, 2, 0]; 2])?;
        }
        let mut slots = Vec::with_capacity(num_envs);
        for index in 0..num_envs {
            slots.push(FullSlot::new(
                FullEnv::new(
                    &maps,
                    seed_base.wrapping_add(index as u64),
                    &opponent_weights,
                    wood_shaping,
                    end_wood_value,
                )?,
                None,
            ));
        }
        Ok(Self {
            slots,
            maps,
            opponent_weights,
            wood_shaping,
            end_wood_value,
            next_episode_seed: seed_base.wrapping_add(num_envs as u64),
        })
    }

    fn len(&self) -> usize {
        self.slots.len()
    }

    fn reset_slot(&mut self, index: usize, replay: Option<Vec<u8>>) {
        let seed = self.next_episode_seed;
        self.next_episode_seed = self.next_episode_seed.wrapping_add(1);
        let env = FullEnv::new(
            &self.maps,
            seed,
            &self.opponent_weights,
            self.wood_shaping,
            self.end_wood_value,
        )
        .expect("constructor-validated maps and weights");
        self.slots[index] = FullSlot::new(env, replay);
    }

    fn observe(
        &mut self,
        obs: &mut [u8],
        masks: &mut [u8],
        plan_masks: &mut [u8],
        phases: &mut [i32],
        seats: &mut [i32],
        active_trolls: &mut [i32],
    ) {
        self.slots
            .par_iter_mut()
            .zip(obs.par_chunks_mut(TF_FULL_OBS_SIZE))
            .zip(masks.par_chunks_mut(TF_FULL_ACTION_SIZE))
            .zip(plan_masks.par_chunks_mut(TF_FULL_PLAN_SIZE))
            .zip(phases.par_iter_mut())
            .zip(seats.par_iter_mut())
            .zip(active_trolls.par_iter_mut())
            .for_each(
                |((((((slot, obs), masks), plan_masks), phase), seat), active_troll)| {
                    slot.env.observe_main(obs, masks, plan_masks);
                    slot.main_mask.copy_from_slice(masks);
                    slot.main_plan_mask.copy_from_slice(plan_masks);
                    slot.main_cache_valid = true;
                    *phase = slot.env.main_phase;
                    *seat = slot.env.learned_seat as i32;
                    *active_troll = slot.env.active_main_troll();
                },
            );
    }

    fn opponent_observe(
        &mut self,
        obs: &mut [u8],
        masks: &mut [u8],
        plan_masks: &mut [u8],
        phases: &mut [i32],
        seats: &mut [i32],
        active_trolls: &mut [i32],
        needs_action: &mut [u8],
    ) {
        self.slots
            .par_iter_mut()
            .zip(obs.par_chunks_mut(TF_FULL_OBS_SIZE))
            .zip(masks.par_chunks_mut(TF_FULL_ACTION_SIZE))
            .zip(plan_masks.par_chunks_mut(TF_FULL_PLAN_SIZE))
            .zip(phases.par_iter_mut())
            .zip(seats.par_iter_mut())
            .zip(active_trolls.par_iter_mut())
            .zip(needs_action.par_iter_mut())
            .for_each(
                |(((((((slot, obs), masks), plan_masks), phase), seat), active_troll), needs)| {
                    let needed = slot.env.observe_external(obs, masks, plan_masks);
                    slot.external_mask.copy_from_slice(masks);
                    slot.external_plan_mask.copy_from_slice(plan_masks);
                    slot.external_cache_valid = needed;
                    *needs = u8::from(needed);
                    *phase = if needed { slot.env.external_phase } else { -1 };
                    *seat = if needed {
                        (1 - slot.env.learned_seat) as i32
                    } else {
                        -1
                    };
                    *active_troll = if needed {
                        slot.env.active_external_troll()
                    } else {
                        -1
                    };
                },
            );
    }
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
pub unsafe extern "C" fn tf_full_create(
    num_envs: usize,
    seed_base: u64,
    maps_path: *const c_char,
    opponent_weights_7: *const f32,
    wood_shaping: f32,
    end_wood_value: f32,
) -> *mut FullBatch {
    if maps_path.is_null() || opponent_weights_7.is_null() || num_envs == 0 {
        return std::ptr::null_mut();
    }
    let path = match CStr::from_ptr(maps_path).to_str() {
        Ok(path) if !path.is_empty() => path,
        _ => return std::ptr::null_mut(),
    };
    let weights = std::slice::from_raw_parts(opponent_weights_7, 7);
    let mut fixed = [0.0f32; 7];
    fixed.copy_from_slice(weights);
    match FullBatch::from_path(
        num_envs,
        seed_base,
        path,
        fixed,
        wood_shaping,
        end_wood_value,
    ) {
        Ok(batch) => Box::into_raw(Box::new(batch)),
        Err(_) => std::ptr::null_mut(),
    }
}

#[no_mangle]
pub unsafe extern "C" fn tf_full_destroy(handle: *mut FullBatch) {
    if !handle.is_null() {
        drop(Box::from_raw(handle));
    }
}

#[allow(clippy::too_many_arguments)]
unsafe fn observe_raw(
    batch: &mut FullBatch,
    obs: *mut u8,
    masks: *mut u8,
    plan_masks: *mut u8,
    phases: *mut i32,
    seats: *mut i32,
    active_trolls: *mut i32,
) -> i32 {
    if obs.is_null()
        || masks.is_null()
        || plan_masks.is_null()
        || phases.is_null()
        || seats.is_null()
        || active_trolls.is_null()
    {
        return -1;
    }
    let n = batch.len();
    batch.observe(
        std::slice::from_raw_parts_mut(obs, n * TF_FULL_OBS_SIZE),
        std::slice::from_raw_parts_mut(masks, n * TF_FULL_ACTION_SIZE),
        std::slice::from_raw_parts_mut(plan_masks, n * TF_FULL_PLAN_SIZE),
        std::slice::from_raw_parts_mut(phases, n),
        std::slice::from_raw_parts_mut(seats, n),
        std::slice::from_raw_parts_mut(active_trolls, n),
    );
    n as i32
}

#[no_mangle]
pub unsafe extern "C" fn tf_full_observe(
    handle: *mut FullBatch,
    obs: *mut u8,
    masks: *mut u8,
    plan_masks: *mut u8,
    phases: *mut i32,
    seats: *mut i32,
    active_trolls: *mut i32,
) -> i32 {
    if handle.is_null() {
        return -1;
    }
    observe_raw(
        &mut *handle,
        obs,
        masks,
        plan_masks,
        phases,
        seats,
        active_trolls,
    )
}

#[allow(clippy::too_many_arguments)]
unsafe fn step_raw(
    batch: &mut FullBatch,
    actions: *const i32,
    external: bool,
    obs: *mut u8,
    masks: *mut u8,
    plan_masks: *mut u8,
    phases: *mut i32,
    seats: *mut i32,
    active_trolls: *mut i32,
    rewards: *mut f32,
    turn_completed: *mut u8,
    reward_credit_count: *mut u8,
    dones: *mut u8,
    wins: *mut u8,
    episode_turns: *mut u16,
    episode_returns: *mut f32,
    episode_seeds: *mut u64,
    map_indices: *mut u32,
    opponent_ids: *mut u8,
    score_own: *mut i32,
    score_opp: *mut i32,
    trained_specs: *mut i8,
    trained_turns: *mut u16,
    trained_count: *mut u8,
    trained_overflow: *mut u8,
    illegal_commands: *mut u16,
    action_hashes: *mut u64,
    state_hashes: *mut u64,
) -> i32 {
    if actions.is_null()
        || obs.is_null()
        || masks.is_null()
        || plan_masks.is_null()
        || phases.is_null()
        || seats.is_null()
        || active_trolls.is_null()
        || rewards.is_null()
        || turn_completed.is_null()
        || reward_credit_count.is_null()
        || dones.is_null()
        || wins.is_null()
        || episode_turns.is_null()
        || episode_returns.is_null()
        || episode_seeds.is_null()
        || map_indices.is_null()
        || opponent_ids.is_null()
        || score_own.is_null()
        || score_opp.is_null()
        || trained_specs.is_null()
        || trained_turns.is_null()
        || trained_count.is_null()
        || trained_overflow.is_null()
        || illegal_commands.is_null()
        || action_hashes.is_null()
        || state_hashes.is_null()
    {
        return -1;
    }
    let n = batch.len();
    let actions = std::slice::from_raw_parts(actions, n);
    for (slot, action) in batch.slots.iter().zip(actions) {
        let env = &slot.env;
        let validation = if external {
            if env.main_phase != 2 || env.opponent_id != 6 {
                if *action == -1 {
                    Ok(())
                } else {
                    Err(-5)
                }
            } else if slot.external_cache_valid {
                let index = usize::try_from(*action).map_err(|_| -4);
                match (env.external_phase, index) {
                    (0, Ok(index))
                        if index < slot.external_plan_mask.len()
                            && slot.external_plan_mask[index] != 0 =>
                    {
                        Ok(())
                    }
                    (1, Ok(index))
                        if index < slot.external_mask.len() && slot.external_mask[index] != 0 =>
                    {
                        Ok(())
                    }
                    (0 | 1, _) => Err(-4),
                    _ => Err(-5),
                }
            } else {
                validate_masked_action(
                    &env.state,
                    1 - env.learned_seat,
                    env.active_external_troll(),
                    env.external_phase,
                    &env.external_staged,
                    Some(&env.routing),
                    *action,
                )
            }
        } else if env.main_phase == 2 {
            if *action == -1 {
                Ok(())
            } else {
                Err(-5)
            }
        } else if slot.main_cache_valid {
            let index = usize::try_from(*action).map_err(|_| -4);
            match (env.main_phase, index) {
                (0, Ok(index))
                    if index < slot.main_plan_mask.len() && slot.main_plan_mask[index] != 0 =>
                {
                    Ok(())
                }
                (1, Ok(index)) if index < slot.main_mask.len() && slot.main_mask[index] != 0 => {
                    Ok(())
                }
                (0 | 1, _) => Err(-4),
                _ => Err(-5),
            }
        } else {
            validate_masked_action(
                &env.state,
                env.learned_seat,
                env.active_main_troll(),
                env.main_phase,
                &env.main_staged,
                Some(&env.routing),
                *action,
            )
        };
        if let Err(status) = validation {
            return status;
        }
    }
    let mut outcomes = vec![TurnOutcome::default(); n];
    let results: Vec<_> = batch
        .slots
        .par_iter_mut()
        .zip(actions.par_iter())
        .map(|(slot, action)| {
            slot.main_cache_valid = false;
            slot.external_cache_valid = false;
            if external {
                if *action == -1 {
                    Ok(None)
                } else {
                    slot.env.advance_external(*action)
                }
            } else if slot.env.main_phase == 2 {
                Ok(None)
            } else {
                slot.env.advance_main(*action)
            }
        })
        .collect();
    for (index, result) in results.into_iter().enumerate() {
        let result = match result {
            Ok(result) => result,
            Err(status) => return status,
        };
        if let Some(outcome) = result {
            let done = outcome.done;
            let replay = outcome.replay.clone();
            outcomes[index] = outcome;
            if done {
                batch.reset_slot(index, replay);
            }
        }
    }

    let rewards = std::slice::from_raw_parts_mut(rewards, n);
    let turn_completed = std::slice::from_raw_parts_mut(turn_completed, n);
    let reward_credit_count = std::slice::from_raw_parts_mut(reward_credit_count, n);
    let dones = std::slice::from_raw_parts_mut(dones, n);
    let wins = std::slice::from_raw_parts_mut(wins, n);
    let episode_turns = std::slice::from_raw_parts_mut(episode_turns, n);
    let episode_returns = std::slice::from_raw_parts_mut(episode_returns, n);
    let episode_seeds = std::slice::from_raw_parts_mut(episode_seeds, n);
    let map_indices = std::slice::from_raw_parts_mut(map_indices, n);
    let opponent_ids = std::slice::from_raw_parts_mut(opponent_ids, n);
    let score_own = std::slice::from_raw_parts_mut(score_own, n);
    let score_opp = std::slice::from_raw_parts_mut(score_opp, n);
    let trained_specs =
        std::slice::from_raw_parts_mut(trained_specs, n * TF_FULL_MAX_RECORDED_TRAINS * 4);
    let trained_turns =
        std::slice::from_raw_parts_mut(trained_turns, n * TF_FULL_MAX_RECORDED_TRAINS);
    let trained_count = std::slice::from_raw_parts_mut(trained_count, n);
    let trained_overflow = std::slice::from_raw_parts_mut(trained_overflow, n);
    let illegal_commands = std::slice::from_raw_parts_mut(illegal_commands, n);
    let action_hashes = std::slice::from_raw_parts_mut(action_hashes, n);
    let state_hashes = std::slice::from_raw_parts_mut(state_hashes, n);

    rewards.fill(0.0);
    turn_completed.fill(0);
    reward_credit_count.fill(0);
    dones.fill(0);
    wins.fill(0);
    episode_turns.fill(0);
    episode_returns.fill(0.0);
    episode_seeds.fill(0);
    map_indices.fill(0);
    opponent_ids.fill(0);
    score_own.fill(0);
    score_opp.fill(0);
    trained_specs.fill(0);
    trained_turns.fill(0);
    trained_count.fill(0);
    trained_overflow.fill(0);
    illegal_commands.fill(0);
    action_hashes.fill(0);
    state_hashes.fill(0);

    for (index, outcome) in outcomes.iter().enumerate() {
        rewards[index] = outcome.reward;
        if outcome.reward_credit_count == 0 {
            continue;
        }
        turn_completed[index] = 1;
        reward_credit_count[index] = outcome.reward_credit_count;
        if !outcome.done {
            continue;
        }
        dones[index] = 1;
        wins[index] = u8::from(outcome.win);
        episode_turns[index] = outcome.episode_turns;
        episode_returns[index] = outcome.episode_return;
        episode_seeds[index] = outcome.episode_seed;
        map_indices[index] = outcome.map_index;
        opponent_ids[index] = outcome.opponent_id;
        score_own[index] = outcome.score_own;
        score_opp[index] = outcome.score_opp;
        trained_count[index] = outcome.trained_count;
        trained_overflow[index] = outcome.trained_overflow;
        illegal_commands[index] = outcome.illegal_commands;
        action_hashes[index] = outcome.action_hash;
        state_hashes[index] = outcome.state_hash;
        for train_index in 0..TF_FULL_MAX_RECORDED_TRAINS {
            let base = (index * TF_FULL_MAX_RECORDED_TRAINS + train_index) * 4;
            trained_specs[base..base + 4].copy_from_slice(&outcome.trained[train_index].spec);
            trained_turns[index * TF_FULL_MAX_RECORDED_TRAINS + train_index] =
                outcome.trained[train_index].turn;
        }
    }
    observe_raw(batch, obs, masks, plan_masks, phases, seats, active_trolls)
}

#[allow(clippy::too_many_arguments)]
#[no_mangle]
pub unsafe extern "C" fn tf_full_step(
    handle: *mut FullBatch,
    actions: *const i32,
    obs: *mut u8,
    masks: *mut u8,
    plan_masks: *mut u8,
    phases: *mut i32,
    seats: *mut i32,
    active_trolls: *mut i32,
    rewards: *mut f32,
    turn_completed: *mut u8,
    reward_credit_count: *mut u8,
    dones: *mut u8,
    wins: *mut u8,
    episode_turns: *mut u16,
    episode_returns: *mut f32,
    episode_seeds: *mut u64,
    map_indices: *mut u32,
    opponent_ids: *mut u8,
    score_own: *mut i32,
    score_opp: *mut i32,
    trained_specs: *mut i8,
    trained_turns: *mut u16,
    trained_count: *mut u8,
    trained_overflow: *mut u8,
    illegal_commands: *mut u16,
    action_hashes: *mut u64,
    state_hashes: *mut u64,
) -> i32 {
    if handle.is_null() {
        return -1;
    }
    step_raw(
        &mut *handle,
        actions,
        false,
        obs,
        masks,
        plan_masks,
        phases,
        seats,
        active_trolls,
        rewards,
        turn_completed,
        reward_credit_count,
        dones,
        wins,
        episode_turns,
        episode_returns,
        episode_seeds,
        map_indices,
        opponent_ids,
        score_own,
        score_opp,
        trained_specs,
        trained_turns,
        trained_count,
        trained_overflow,
        illegal_commands,
        action_hashes,
        state_hashes,
    )
}

#[allow(clippy::too_many_arguments)]
#[no_mangle]
pub unsafe extern "C" fn tf_full_opponent_step(
    handle: *mut FullBatch,
    actions: *const i32,
    obs: *mut u8,
    masks: *mut u8,
    plan_masks: *mut u8,
    phases: *mut i32,
    seats: *mut i32,
    active_trolls: *mut i32,
    rewards: *mut f32,
    turn_completed: *mut u8,
    reward_credit_count: *mut u8,
    dones: *mut u8,
    wins: *mut u8,
    episode_turns: *mut u16,
    episode_returns: *mut f32,
    episode_seeds: *mut u64,
    map_indices: *mut u32,
    opponent_ids: *mut u8,
    score_own: *mut i32,
    score_opp: *mut i32,
    trained_specs: *mut i8,
    trained_turns: *mut u16,
    trained_count: *mut u8,
    trained_overflow: *mut u8,
    illegal_commands: *mut u16,
    action_hashes: *mut u64,
    state_hashes: *mut u64,
) -> i32 {
    if handle.is_null() {
        return -1;
    }
    step_raw(
        &mut *handle,
        actions,
        true,
        obs,
        masks,
        plan_masks,
        phases,
        seats,
        active_trolls,
        rewards,
        turn_completed,
        reward_credit_count,
        dones,
        wins,
        episode_turns,
        episode_returns,
        episode_seeds,
        map_indices,
        opponent_ids,
        score_own,
        score_opp,
        trained_specs,
        trained_turns,
        trained_count,
        trained_overflow,
        illegal_commands,
        action_hashes,
        state_hashes,
    )
}

#[no_mangle]
pub unsafe extern "C" fn tf_full_opponent_observe(
    handle: *mut FullBatch,
    obs: *mut u8,
    masks: *mut u8,
    plan_masks: *mut u8,
    phases: *mut i32,
    seats: *mut i32,
    active_trolls: *mut i32,
    needs_action: *mut u8,
) -> i32 {
    if handle.is_null()
        || obs.is_null()
        || masks.is_null()
        || plan_masks.is_null()
        || phases.is_null()
        || seats.is_null()
        || active_trolls.is_null()
        || needs_action.is_null()
    {
        return -1;
    }
    let batch = &mut *handle;
    let n = batch.len();
    batch.opponent_observe(
        std::slice::from_raw_parts_mut(obs, n * TF_FULL_OBS_SIZE),
        std::slice::from_raw_parts_mut(masks, n * TF_FULL_ACTION_SIZE),
        std::slice::from_raw_parts_mut(plan_masks, n * TF_FULL_PLAN_SIZE),
        std::slice::from_raw_parts_mut(phases, n),
        std::slice::from_raw_parts_mut(seats, n),
        std::slice::from_raw_parts_mut(active_trolls, n),
        std::slice::from_raw_parts_mut(needs_action, n),
    );
    n as i32
}

#[no_mangle]
pub unsafe extern "C" fn tf_full_take_replay(
    handle: *mut FullBatch,
    slot: usize,
    output_json: *mut u8,
    output_capacity: usize,
) -> i64 {
    if handle.is_null() {
        return -1;
    }
    let batch = &mut *handle;
    if slot >= batch.len() {
        return -2;
    }
    let Some(replay) = batch.slots[slot].completed_replay.as_ref() else {
        return 0;
    };
    if output_json.is_null() {
        return replay.len() as i64;
    }
    if output_capacity < replay.len() {
        return -6;
    }
    let output = std::slice::from_raw_parts_mut(output_json, output_capacity);
    output[..replay.len()].copy_from_slice(replay);
    let length = replay.len() as i64;
    batch.slots[slot].completed_replay = None;
    length
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
        None,
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
                None,
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

    fn real_maps() -> Vec<MapRecord> {
        include_str!("../../local_claude_1/nn-bot/maps-slice-1000.jsonl")
            .lines()
            .take(4)
            .map(|line| serde_json::from_str(line).unwrap())
            .collect()
    }

    fn first_legal_spatial(env: &FullEnv, external: bool) -> i32 {
        let mut mask = vec![0u8; TF_FULL_ACTION_SIZE];
        if external {
            legal_action_mask(
                &env.state,
                1 - env.learned_seat,
                env.active_external_troll(),
                &env.external_staged,
                Some(&env.routing),
                &mut mask,
            )
            .unwrap();
        } else {
            legal_action_mask(
                &env.state,
                env.learned_seat,
                env.active_main_troll(),
                &env.main_staged,
                Some(&env.routing),
                &mut mask,
            )
            .unwrap();
        }
        mask.iter().position(|value| *value != 0).unwrap() as i32
    }

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
    fn cached_move_routing_matches_referee_next_cell() {
        for map in real_maps() {
            let game = map.to_game([[2, 2, 2, 2, 2, 0]; 2]).unwrap();
            let routing = MoveRouting::new(&game);
            let mut sources: Vec<_> = game.walkable.iter().copied().collect();
            sources.extend(game.shacks);
            for source in sources {
                for &target in &game.walkable {
                    for speed in 1..=3 {
                        assert_eq!(
                            routing.next_cell(&game, source, target, speed),
                            next_cell(&game.walkable, source, target, speed),
                            "source={source:?} target={target:?} speed={speed}"
                        );
                    }
                }
            }
        }
    }

    #[test]
    fn state_observation_has_signed_plan_phase_semantics() {
        let parsed: JsonState = serde_json::from_str(&tiny_state_json()).unwrap();
        let game = parsed.to_game().unwrap();
        let mut obs = vec![0; TF_FULL_OBS_SIZE];
        fill_observation(&game, 0, 0, 1, 0, false, &[], None, &mut obs).unwrap();
        assert_eq!(
            obs[97 * TF_FULL_CELLS],
            255,
            "zero plan still sets phase bit"
        );
        assert_eq!(obs[59 * TF_FULL_CELLS], 0);
        assert_eq!(obs[99 * TF_FULL_CELLS], 255);
    }

    #[test]
    fn linked_and_external_opponents_complete_legal_real_map_games() {
        let maps = real_maps();
        for opponent_id in 0..7 {
            let mut weights = [0.0f32; 7];
            weights[opponent_id] = 1.0;
            let mut env =
                FullEnv::new(&maps, 91_000 + opponent_id as u64, &weights, 0.5, 3.5).unwrap();
            let mut terminal = None;
            for _ in 0..5_000 {
                let outcome = match env.main_phase {
                    0 => env.advance_main(0).unwrap(),
                    1 => {
                        let action = first_legal_spatial(&env, false);
                        env.advance_main(action).unwrap()
                    }
                    2 => match env.external_phase {
                        0 => env.advance_external(0).unwrap(),
                        1 => {
                            let action = first_legal_spatial(&env, true);
                            env.advance_external(action).unwrap()
                        }
                        phase => panic!("bad external phase {phase}"),
                    },
                    phase => panic!("bad main phase {phase}"),
                };
                if outcome.as_ref().is_some_and(|outcome| outcome.done) {
                    terminal = outcome;
                    break;
                }
            }
            let terminal = terminal.unwrap_or_else(|| panic!("opponent {opponent_id} did not end"));
            assert_eq!(terminal.illegal_commands, 0);
            assert!(terminal.episode_turns <= 300);
            let replay = terminal.replay.expect("completed game replay");
            let decoded: serde_json::Value = serde_json::from_slice(&replay).unwrap();
            assert_eq!(
                decoded["turns"].as_array().unwrap().len(),
                terminal.episode_turns as usize
            );
        }
    }
}
