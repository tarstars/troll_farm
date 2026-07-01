use std::collections::{HashMap, HashSet, VecDeque};
use super::state::{Cell, GameState, Plant, Unit};

// ── constants ────────────────────────────────────────────────────────────────

pub const PLUM: usize = 0;
pub const LEMON: usize = 1;
pub const APPLE: usize = 2;
pub const BANANA: usize = 3;
pub const IRON: usize = 4;
pub const WOOD: usize = 5;

pub const MAX_SIZE: i32 = 4;
pub const MAX_FRUITS: i32 = 3;
pub const WOOD_POINTS: i32 = 4;

pub fn item_index(name: &str) -> usize {
    match name {
        "PLUM" => PLUM,
        "LEMON" => LEMON,
        "APPLE" => APPLE,
        "BANANA" => BANANA,
        "IRON" => IRON,
        "WOOD" => WOOD,
        _ => panic!("unknown item: {}", name),
    }
}

pub fn plant_cooldown(t: &str) -> i32 {
    match t {
        "PLUM" => 8,
        "LEMON" => 8,
        "APPLE" => 9,
        "BANANA" => 6,
        _ => panic!("unknown plant type: {}", t),
    }
}

pub fn water_boost(t: &str) -> i32 {
    match t {
        "PLUM" => 5,
        "LEMON" => 5,
        "APPLE" => 7,
        "BANANA" => 2,
        _ => panic!("unknown plant for water_boost: {}", t),
    }
}

/// `(base, slope)` for a tree type's health: `health = base + slope*size`.
/// Reverse-engineered from real arena replays (10 observations, perfect fit):
/// PLUM s1..4 → 6,8,10,12 ; LEMON s2,s4 → 8,12 ; APPLE s1,s3 → 11,17 ;
/// BANANA s3,s4 → 5,6. Health only matters for chopping (chops-to-fell).
pub fn tree_health_params(t: &str) -> (i32, i32) {
    match t {
        "PLUM" | "LEMON" => (4, 2),
        "APPLE" => (8, 3),
        "BANANA" => (2, 1),
        _ => panic!("unknown plant for tree_health: {}", t),
    }
}

/// Full health of an untouched tree of the given type and size.
pub fn tree_health(t: &str, size: i32) -> i32 {
    let (base, slope) = tree_health_params(t);
    base + slope * size
}

// ── BFS ──────────────────────────────────────────────────────────────────────

const NEIGHBORS: [(i32, i32); 4] = [(0, 1), (1, 0), (0, -1), (-1, 0)];

pub fn bfs_distances(walkable: &HashSet<Cell>, sources: &[Cell]) -> HashMap<Cell, i32> {
    let mut dist: HashMap<Cell, i32> = HashMap::new();
    let mut queue: VecDeque<Cell> = VecDeque::new();
    for &cell in sources {
        if !dist.contains_key(&cell) {
            dist.insert(cell, 0);
            queue.push_back(cell);
        }
    }
    while let Some((x, y)) = queue.pop_front() {
        let d = dist[&(x, y)];
        for &(dx, dy) in &NEIGHBORS {
            let n = (x + dx, y + dy);
            if walkable.contains(&n) && !dist.contains_key(&n) {
                dist.insert(n, d + 1);
                queue.push_back(n);
            }
        }
    }
    dist
}

fn manhattan(a: Cell, b: Cell) -> i32 {
    (a.0 - b.0).abs() + (a.1 - b.1).abs()
}

/// Mirror of sim.engine.next_cell.
pub fn next_cell(walkable: &HashSet<Cell>, current: Cell, target: Cell, speed: i32) -> Cell {
    let src = bfs_distances(walkable, &[current]);

    // If target is reachable within speed, go directly
    if let Some(&d) = src.get(&target) {
        if d <= speed {
            return target;
        }
    }

    // Compute tdist: BFS from target (or nearest reachable cells if target unreachable)
    let tdist = if !src.contains_key(&target) {
        if src.is_empty() {
            return current;
        }
        let best = src.keys().map(|c| manhattan(target, *c)).min().unwrap();
        let goals: Vec<Cell> = src.keys().filter(|c| manhattan(target, **c) == best).copied().collect();
        bfs_distances(walkable, &goals)
    } else {
        bfs_distances(walkable, &[target])
    };

    // Cells reachable within speed that are also in tdist
    let in_range: Vec<Cell> = src.iter()
        .filter(|(c, d)| **d <= speed && tdist.contains_key(*c))
        .map(|(c, _)| *c)
        .collect();

    if in_range.is_empty() {
        return current;
    }

    let best_dist = in_range.iter().map(|c| tdist[c]).min().unwrap();
    // Among ties, pick the lexicographically smallest cell (Python: min())
    in_range.iter()
        .filter(|c| tdist[*c] == best_dist)
        .copied()
        .min()
        .unwrap()
}

// ── plant helpers ─────────────────────────────────────────────────────────────

/// Tick all plants: decrement cooldown, grow size or add fruit when cd reaches 0.
pub fn tick_plants(game: &mut GameState) {
    for p in game.plants.iter_mut() {
        if p.cooldown > 0 {
            p.cooldown -= 1;
        }
        // Recompute growth_cd here requires water info; we need to handle this inline.
        // We compute the effective cooldown from the game's water set.
        if p.cooldown == 0 && p.health > 0 {
            if p.size < MAX_SIZE {
                p.size += 1;
                // Growing a size adds health (real trees: health = base + slope*size).
                // Adding the slope preserves any chop damage already taken.
                p.health += tree_health_params(&p.plant_type).1;
                // Can't call growth_cd with &mut p and &game simultaneously.
                // Compute inline.
                let mut cd = plant_cooldown(&p.plant_type);
                let (px, py) = (p.x, p.y);
                let near_water = game.water.iter().any(|(wx, wy)| {
                    (px - wx).abs() + (py - wy).abs() == 1
                });
                if near_water {
                    cd -= water_boost(&p.plant_type);
                }
                p.cooldown = cd;
            } else if p.fruits < MAX_FRUITS {
                p.fruits += 1;
                let mut cd = plant_cooldown(&p.plant_type);
                let (px, py) = (p.x, p.y);
                let near_water = game.water.iter().any(|(wx, wy)| {
                    (px - wx).abs() + (py - wy).abs() == 1
                });
                if near_water {
                    cd -= water_boost(&p.plant_type);
                }
                p.cooldown = cd;
            }
        }
    }
}

/// Recompute scores from inventories: sum of fruits (0..4) + WOOD_POINTS * wood.
pub fn recompute_scores(game: &mut GameState) {
    for p in 0..2 {
        let inv = &game.inventories[p];
        game.scores[p] = inv[0] + inv[1] + inv[2] + inv[3] + WOOD_POINTS * inv[WOOD];
    }
}

// ── apply functions ───────────────────────────────────────────────────────────

fn plant_at_pos(plants: &[Plant], cell: Cell) -> Option<usize> {
    plants.iter().position(|p| p.pos() == cell)
}

fn near_shack(game: &GameState, unit: &Unit) -> bool {
    let (sx, sy) = game.shacks[unit.player as usize];
    (unit.x - sx).abs() + (unit.y - sy).abs() <= 1
}

/// Apply move commands. intents: {unit_id -> target_cell}
/// Per-player resolution: highest id wins a contested cell; circular swaps resolved;
/// if still blocked, force resolve (resolve_blocking flag).
pub fn apply_moves(game: &mut GameState, intents: &HashMap<i32, Cell>) {
    // Process each player separately
    for player in 0..2i32 {
        // Collect unit ids for this player
        let player_unit_ids: Vec<i32> = game.units.iter()
            .filter(|u| u.player == player)
            .map(|u| u.id)
            .collect();

        // Build target map for this player's units
        // We need the actual unit positions to call next_cell
        let unit_positions: HashMap<i32, Cell> = game.units.iter()
            .filter(|u| u.player == player)
            .map(|u| (u.id, u.pos()))
            .collect();
        let unit_ms: HashMap<i32, i32> = game.units.iter()
            .filter(|u| u.player == player)
            .map(|u| (u.id, u.ms))
            .collect();

        let mut target: HashMap<i32, Cell> = HashMap::new();
        for &uid in &player_unit_ids {
            if let Some(&dest) = intents.get(&uid) {
                let pos = unit_positions[&uid];
                let ms = unit_ms[&uid];
                target.insert(uid, next_cell(&game.walkable, pos, dest, ms));
            } else {
                target.insert(uid, unit_positions[&uid]);
            }
        }

        // occupied = positions of all this player's units
        let mut occupied: HashSet<Cell> = player_unit_ids.iter().map(|id| unit_positions[id]).collect();

        // movers: units that want to move to a different cell
        let mut movers: Vec<i32> = player_unit_ids.iter()
            .filter(|id| target[id] != unit_positions[id])
            .copied()
            .collect();

        // Sort by descending id so highest id wins
        movers.sort_by(|a, b| b.cmp(a));

        let mut progress = true;
        let mut resolve_blocking = false;
        while progress {
            progress = false;

            // Count how many movers want each cell
            let mut freq: HashMap<Cell, i32> = HashMap::new();
            for &uid in &movers {
                let cell = target[&uid];
                *freq.entry(cell).or_insert(0) += 1;
            }

            let mut to_remove: Vec<i32> = Vec::new();
            // We iterate in order (descending id) since movers is sorted
            for &uid in &movers {
                let cell = target[&uid];
                // Get current position of the unit (may have moved in a prior iteration)
                let cur_cell = game.units.iter().find(|u| u.id == uid).map(|u| u.pos()).unwrap();
                if (resolve_blocking || freq[&cell] == 1) && !occupied.contains(&cell) {
                    occupied.remove(&cur_cell);
                    occupied.insert(cell);
                    // Update actual unit position
                    if let Some(u) = game.units.iter_mut().find(|u| u.id == uid) {
                        u.x = cell.0;
                        u.y = cell.1;
                    }
                    to_remove.push(uid);
                    progress = true;
                    resolve_blocking = false;
                }
            }
            movers.retain(|id| !to_remove.contains(id));

            if progress {
                continue;
            }

            // Try to resolve circular swaps
            // Build pos_to_uid map for remaining movers (using current positions)
            let mover_pos: HashMap<Cell, i32> = movers.iter()
                .filter_map(|uid| {
                    game.units.iter().find(|u| u.id == *uid).map(|u| (u.pos(), *uid))
                })
                .collect();

            let mut swap_resolved = false;
            'outer: for &start in &movers {
                let mut path: Vec<i32> = vec![start];
                loop {
                    let last_target = target[path.last().unwrap()];
                    let nxt_uid = mover_pos.get(&last_target).copied();
                    match nxt_uid {
                        None => break,
                        Some(nxt) => {
                            if nxt == path[0] {
                                // Found a cycle — swap all units in path
                                for &uid in &path {
                                    let t = target[&uid];
                                    if let Some(u) = game.units.iter_mut().find(|u| u.id == uid) {
                                        u.x = t.0;
                                        u.y = t.1;
                                    }
                                }
                                movers.retain(|id| !path.contains(id));
                                progress = true;
                                swap_resolved = true;
                                break 'outer;
                            }
                            if path.contains(&nxt) {
                                break;
                            }
                            path.push(nxt);
                        }
                    }
                }
            }

            if !swap_resolved && !resolve_blocking {
                resolve_blocking = true;
                progress = true;
            }
        }
    }
}

/// Apply harvest commands. unit_ids: list of unit ids that want to harvest.
pub fn apply_harvest(game: &mut GameState, unit_ids: &[i32]) {
    // Group harvesting units by cell
    let mut cells: HashMap<Cell, Vec<i32>> = HashMap::new();
    for &uid in unit_ids {
        if let Some(u) = game.units.iter().find(|u| u.id == uid) {
            let pos = u.pos();
            if let Some(pi) = plant_at_pos(&game.plants, pos) {
                if game.plants[pi].fruits > 0 {
                    cells.entry(pos).or_default().push(uid);
                }
            }
        }
    }

    for (cell, troll_ids) in &cells {
        let pi = match plant_at_pos(&game.plants, *cell) {
            Some(i) => i,
            None => continue,
        };
        let idx = item_index(&game.plants[pi].plant_type.clone());

        // Harvest: for round i=1..MAX_FRUITS, each troll with hp>=i and carry space takes one fruit
        // The Python loop goes `for i in range(1, MAX_FRUITS+1)` but breaks if fruits==0.
        // Note: "last fruit can duplicate" — fruit count can go to 0 but we still let all trolls
        // that satisfy the condition (hp >= i, free > 0) take one. Once fruits==0, we decrement
        // plant.fruits to -N (Python does `if plant.fruits > 0: plant.fruits -= 1`).
        // Actually re-reading Python: it decrements `if plant.fruits > 0` — so last fruit stops depleting.
        // But multiple trolls CAN get the last fruit.
        for i in 1..=MAX_FRUITS {
            if game.plants[pi].fruits == 0 {
                break;
            }
            for &uid in troll_ids {
                // Re-find unit each time since we mutate carry
                let (u_hp, u_total, u_cc) = game.units.iter()
                    .find(|u| u.id == uid)
                    .map(|u| (u.hp, u.total(), u.cc))
                    .unwrap_or((0, 0, 0));
                if u_hp >= i && u_total < u_cc {
                    if let Some(u) = game.units.iter_mut().find(|u| u.id == uid) {
                        u.carry[idx] += 1;
                    }
                    if game.plants[pi].fruits > 0 {
                        game.plants[pi].fruits -= 1;
                    }
                }
            }
        }
    }
}

/// Apply drop commands: units near shack drop carry into inventory.
pub fn apply_drop(game: &mut GameState, unit_ids: &[i32]) {
    for &uid in unit_ids {
        let (player, is_near, carry) = {
            let u = match game.units.iter().find(|u| u.id == uid) {
                Some(u) => u,
                None => continue,
            };
            let is_near = near_shack(game, u);
            (u.player as usize, is_near, u.carry)
        };
        if !is_near {
            continue;
        }
        for i in 0..6 {
            game.inventories[player][i] += carry[i];
        }
        if let Some(u) = game.units.iter_mut().find(|u| u.id == uid) {
            u.carry = [0; 6];
        }
    }
}

/// Apply pick commands: units near shack pick item from inventory into carry.
pub fn apply_pick(game: &mut GameState, picks: &[(i32, String)]) {
    for (uid, type_name) in picks {
        let (player, is_near, is_free) = {
            let u = match game.units.iter().find(|u| u.id == *uid) {
                Some(u) => u,
                None => continue,
            };
            (u.player as usize, near_shack(game, u), u.free() > 0)
        };
        if !is_near || !is_free {
            continue;
        }
        let idx = item_index(type_name);
        if game.inventories[player][idx] > 0 {
            game.inventories[player][idx] -= 1;
            if let Some(u) = game.units.iter_mut().find(|u| u.id == *uid) {
                u.carry[idx] += 1;
            }
        }
    }
}

/// Apply plant commands: units plant a seed from their carry at their position.
pub fn apply_plant(game: &mut GameState, plants: &[(i32, String)]) {
    for (uid, type_name) in plants {
        let (pos, carry_count) = {
            let u = match game.units.iter().find(|u| u.id == *uid) {
                Some(u) => u,
                None => continue,
            };
            let idx = item_index(type_name);
            (u.pos(), u.carry[idx])
        };
        // Must be on walkable cell, no existing plant there, and have the item
        if !game.walkable.contains(&pos) {
            continue;
        }
        if plant_at_pos(&game.plants, pos).is_some() {
            continue;
        }
        if carry_count <= 0 {
            continue;
        }
        let idx = item_index(type_name);
        if let Some(u) = game.units.iter_mut().find(|u| u.id == *uid) {
            u.carry[idx] -= 1;
        }
        game.plants.push(Plant {
            plant_type: type_name.clone(),
            x: pos.0,
            y: pos.1,
            size: 0,
            health: tree_health(type_name, 0),
            fruits: 0,
            cooldown: 0,
        });
    }
}

/// Training cost for nth troll with given talents (ms, cc, hp, chop).
pub fn training_cost(n: i32, talents: (i32, i32, i32, i32)) -> [i32; 6] {
    let (ms, cc, hp, chop) = talents;
    let mut cost = [0i32; 6];
    cost[PLUM] = n + ms * ms;
    cost[LEMON] = n + cc * cc;
    cost[APPLE] = n + hp * hp;
    cost[IRON] = n + chop * chop;
    cost
}

/// Apply train command for a player.
pub fn apply_train(game: &mut GameState, player: i32, talents: (i32, i32, i32, i32)) {
    let p = player as usize;
    let n = game.units.iter().filter(|u| u.player == player).count() as i32;
    let cost = training_cost(n, talents);
    let inv = &game.inventories[p];

    // IRON (slot 4) only charged if iron terrain present (Bronze league guard)
    let pay: &[usize] = if !game.iron.is_empty() {
        &[0, 1, 2, 3, 4, 5]
    } else {
        &[0, 1, 2, 3, 5]
    };

    // Check affordability
    if pay.iter().any(|&i| inv[i] < cost[i]) {
        return;
    }

    // Check shack is unoccupied
    let shack = game.shacks[p];
    if game.units.iter().any(|u| u.pos() == shack) {
        return;
    }

    // Deduct cost
    for &i in pay {
        game.inventories[p][i] -= cost[i];
    }

    let (ms, cc, hp, chop) = talents;
    let nid = game.next_id;
    game.units.push(Unit {
        id: nid,
        player,
        x: shack.0,
        y: shack.1,
        ms,
        cc,
        hp,
        chop,
        carry: [0; 6],
    });
    game.next_id += 1;
}

/// Apply chop commands.
pub fn apply_chop(game: &mut GameState, unit_ids: &[i32]) {
    // Group choppers by cell
    let mut cells: HashMap<Cell, Vec<i32>> = HashMap::new();
    for &uid in unit_ids {
        if let Some(u) = game.units.iter().find(|u| u.id == uid) {
            if u.chop == 0 {
                continue;
            }
            let pos = u.pos();
            if plant_at_pos(&game.plants, pos).is_some() {
                cells.entry(pos).or_default().push(uid);
            }
        }
    }

    let mut dead_indices: Vec<usize> = Vec::new();

    for (cell, chopper_ids) in &cells {
        let pi = match plant_at_pos(&game.plants, *cell) {
            Some(i) => i,
            None => continue,
        };

        // Deal chop damage
        for &uid in chopper_ids {
            let chop_power = game.units.iter().find(|u| u.id == uid).map(|u| u.chop).unwrap_or(0);
            let health = &mut game.plants[pi].health;
            *health = (*health - chop_power).max(0);
        }

        if game.plants[pi].health <= 0 {
            let plant_size = game.plants[pi].size;
            let mut remaining = plant_size;
            // Distribute wood to choppers: loop plant_size times; last wood can duplicate
            let mut i = 0;
            while i < plant_size && remaining > 0 {
                for &uid in chopper_ids {
                    let free = game.units.iter().find(|u| u.id == uid).map(|u| u.free()).unwrap_or(0);
                    if free > 0 {
                        if let Some(u) = game.units.iter_mut().find(|u| u.id == uid) {
                            u.carry[WOOD] += 1;
                            remaining -= 1;
                        }
                    }
                }
                i += 1;
            }
            dead_indices.push(pi);
        }
    }

    // Remove dead plants (in reverse order to keep indices valid)
    dead_indices.sort();
    dead_indices.dedup();
    for pi in dead_indices.into_iter().rev() {
        game.plants.remove(pi);
    }
}

/// Apply mine commands.
pub fn apply_mine(game: &mut GameState, unit_ids: &[i32]) {
    for &uid in unit_ids {
        let (ux, uy, u_chop, u_free) = match game.units.iter().find(|u| u.id == uid) {
            Some(u) => (u.x, u.y, u.chop, u.free()),
            None => continue,
        };
        if u_chop == 0 || u_free <= 0 {
            continue;
        }
        // Check if adjacent to any iron cell
        let near_iron = game.iron.iter().any(|(ix, iy)| {
            (ux - ix).abs() + (uy - iy).abs() == 1
        });
        if near_iron {
            let amount = u_chop.min(u_free);
            if let Some(u) = game.units.iter_mut().find(|u| u.id == uid) {
                u.carry[IRON] += amount;
            }
        }
    }
}

// ── command parsing ───────────────────────────────────────────────────────────

#[derive(Debug, Default)]
pub struct ParsedCmds {
    pub moves: HashMap<i32, Cell>,
    pub harvest: Vec<i32>,
    pub plant: Vec<(i32, String)>,
    pub chop: Vec<i32>,
    pub pick: Vec<(i32, String)>,
    pub train: Vec<(i32, i32, i32, i32)>,
    pub drop: Vec<i32>,
    pub mine: Vec<i32>,
}

pub fn parse_cmds(cmds: &[String]) -> ParsedCmds {
    let mut p = ParsedCmds::default();
    let mut used: HashSet<i32> = HashSet::new();

    for raw in cmds {
        let parts: Vec<&str> = raw.trim().split_whitespace().collect();
        if parts.is_empty() {
            continue;
        }
        let verb = parts[0].to_uppercase();
        let verb = verb.as_str();

        match verb {
            "MSG" | "WAIT" => continue,
            "TRAIN" => {
                if parts.len() >= 5 {
                    let ms: i32 = parts[1].parse().unwrap_or(0);
                    let cc: i32 = parts[2].parse().unwrap_or(0);
                    let hp: i32 = parts[3].parse().unwrap_or(0);
                    let chop: i32 = parts[4].parse().unwrap_or(0);
                    p.train.push((ms, cc, hp, chop));
                }
                continue;
            }
            _ => {}
        }

        if parts.len() < 2 {
            continue;
        }
        let uid: i32 = match parts[1].parse() {
            Ok(v) => v,
            Err(_) => continue,
        };
        if used.contains(&uid) {
            continue;
        }
        used.insert(uid);

        match verb {
            "MOVE" => {
                if parts.len() >= 4 {
                    let x: i32 = parts[2].parse().unwrap_or(0);
                    let y: i32 = parts[3].parse().unwrap_or(0);
                    p.moves.insert(uid, (x, y));
                }
            }
            "HARVEST" => p.harvest.push(uid),
            "DROP" => p.drop.push(uid),
            "CHOP" => p.chop.push(uid),
            "MINE" => p.mine.push(uid),
            "PLANT" => {
                if parts.len() >= 3 {
                    p.plant.push((uid, parts[2].to_uppercase()));
                }
            }
            "PICK" => {
                if parts.len() >= 3 {
                    p.pick.push((uid, parts[2].to_uppercase()));
                }
            }
            _ => {}
        }
    }
    p
}

// ── step ─────────────────────────────────────────────────────────────────────

/// Execute one full game turn.
/// Priority order: MOVE, HARVEST, PLANT, CHOP, PICK, TRAIN, DROP, MINE,
/// then tick_plants, recompute_scores, turn++.
pub fn step(game: &mut GameState, cmds0: &[String], cmds1: &[String]) {
    let a = parse_cmds(cmds0);
    let b = parse_cmds(cmds1);

    // Merge move intents from both players
    let mut all_moves = a.moves.clone();
    all_moves.extend(b.moves.iter());
    apply_moves(game, &all_moves);

    // Harvest
    let mut all_harvest = a.harvest.clone();
    all_harvest.extend(b.harvest.iter());
    apply_harvest(game, &all_harvest);

    // Plant
    let mut all_plant = a.plant.clone();
    all_plant.extend(b.plant.iter().cloned());
    apply_plant(game, &all_plant);

    // Chop
    let mut all_chop = a.chop.clone();
    all_chop.extend(b.chop.iter());
    apply_chop(game, &all_chop);

    // Pick
    let mut all_pick = a.pick.clone();
    all_pick.extend(b.pick.iter().cloned());
    apply_pick(game, &all_pick);

    // Train (per player)
    for talents in &a.train {
        apply_train(game, 0, *talents);
    }
    for talents in &b.train {
        apply_train(game, 1, *talents);
    }

    // Drop
    let mut all_drop = a.drop.clone();
    all_drop.extend(b.drop.iter());
    apply_drop(game, &all_drop);

    // Mine
    let mut all_mine = a.mine.clone();
    all_mine.extend(b.mine.iter());
    apply_mine(game, &all_mine);

    tick_plants(game);
    recompute_scores(game);
    game.turn += 1;
}
