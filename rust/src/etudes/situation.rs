//! Situation format: a serializable Troll Farm position + a search horizon.
//!
//! Text format (one Situation per text block):
//! ```text
//! MAP <width> <height>
//! <height grid rows: '.'=walkable '#'=wall '0'/'1'=shack '+'=iron '~'=water>
//! INV0 <plum> <lemon> <apple> <banana> <iron> <wood>
//! INV1 <plum> <lemon> <apple> <banana> <iron> <wood>
//! UNIT <id> <player> <x> <y> <ms> <cc> <hp> <chop> <carry x6>   (0 or more)
//! PLANT <type> <x> <y> <size> <health> <fruits> <cooldown>       (0 or more)
//! TURN <n>
//! SCORES <p0> <p1>
//! HORIZON <n>
//! PROVE <-|0|1>
//! ```
//! `from_ascii` (game::state) builds the terrain (walkable/shacks/iron/water); the explicit
//! UNIT/PLANT/INV/TURN/SCORES lines then override the defaults `from_ascii` seeds (its two
//! placeholder units at the shacks, empty plants/inventories, turn=1).

use crate::game::state::{from_ascii, GameState, Plant, Unit};

#[derive(Debug, Clone)]
pub struct Situation {
    pub state: GameState,
    pub horizon: u32,
    pub prove_side: Option<usize>,
}

/// Parse a Situation from its text form (see module docs for the format).
pub fn from_text(text: &str) -> Situation {
    let lines: Vec<&str> = text.lines().collect();
    assert!(!lines.is_empty(), "empty situation text");

    let map_parts: Vec<&str> = lines[0].split_whitespace().collect();
    assert_eq!(
        map_parts.first().copied(),
        Some("MAP"),
        "situation text must start with a MAP line"
    );
    let width: i32 = map_parts[1].parse().expect("MAP width");
    let height: i32 = map_parts[2].parse().expect("MAP height");
    let h = height as usize;
    assert!(
        lines.len() >= 1 + h,
        "not enough grid rows for declared MAP height"
    );
    let grid_rows: Vec<&str> = lines[1..1 + h].to_vec();

    let mut state = from_ascii(&grid_rows);
    debug_assert_eq!(state.width, width);
    debug_assert_eq!(state.height, height);

    // The explicit lines below are authoritative; from_ascii only seeds terrain.
    state.units.clear();
    state.plants.clear();
    state.inventories = [[0; 6]; 2];
    state.scores = [0, 0];
    state.turn = 1;

    let mut horizon: u32 = 0;
    let mut prove_side: Option<usize> = None;

    for line in &lines[1 + h..] {
        let line = line.trim();
        if line.is_empty() {
            continue;
        }
        let parts: Vec<&str> = line.split_whitespace().collect();
        match parts[0] {
            "INV0" => state.inventories[0] = parse_carry6(&parts[1..]),
            "INV1" => state.inventories[1] = parse_carry6(&parts[1..]),
            "UNIT" => state.units.push(parse_unit(&parts[1..])),
            "PLANT" => state.plants.push(parse_plant(&parts[1..])),
            "TURN" => state.turn = parts[1].parse().expect("TURN"),
            "SCORES" => {
                state.scores = [
                    parts[1].parse().expect("SCORES p0"),
                    parts[2].parse().expect("SCORES p1"),
                ]
            }
            "HORIZON" => horizon = parts[1].parse().expect("HORIZON"),
            "PROVE" => {
                prove_side = match parts[1] {
                    "-" => None,
                    "0" => Some(0),
                    "1" => Some(1),
                    other => panic!("bad PROVE value: {other}"),
                }
            }
            other => panic!("unknown situation line keyword: {other}"),
        }
    }

    // Keep next_id ahead of any explicitly-authored unit id (matters if a future etude trains).
    state.next_id = state.units.iter().map(|u| u.id + 1).max().unwrap_or(0);

    Situation {
        state,
        horizon,
        prove_side,
    }
}

/// Serialize a Situation to its text form. Canonical order: units sorted by id, plants sorted
/// by (x, y) — so `from_text(to_text(s))` is stable regardless of construction order.
pub fn to_text(sit: &Situation) -> String {
    let st = &sit.state;
    let mut out = String::new();
    out.push_str(&format!("MAP {} {}\n", st.width, st.height));
    for y in 0..st.height {
        let mut row = String::with_capacity(st.width as usize);
        for x in 0..st.width {
            let cell = (x, y);
            let ch = if cell == st.shacks[0] {
                '0'
            } else if cell == st.shacks[1] {
                '1'
            } else if st.iron.contains(&cell) {
                '+'
            } else if st.water.contains(&cell) {
                '~'
            } else if st.walkable.contains(&cell) {
                '.'
            } else {
                '#'
            };
            row.push(ch);
        }
        out.push_str(&row);
        out.push('\n');
    }

    out.push_str(&format!("INV0 {}\n", fmt6(&st.inventories[0])));
    out.push_str(&format!("INV1 {}\n", fmt6(&st.inventories[1])));

    let mut units: Vec<&Unit> = st.units.iter().collect();
    units.sort_by_key(|u| u.id);
    for u in units {
        out.push_str(&format!(
            "UNIT {} {} {} {} {} {} {} {} {}\n",
            u.id,
            u.player,
            u.x,
            u.y,
            u.ms,
            u.cc,
            u.hp,
            u.chop,
            fmt6(&u.carry)
        ));
    }

    let mut plants: Vec<&Plant> = st.plants.iter().collect();
    plants.sort_by_key(|p| (p.x, p.y));
    for p in plants {
        out.push_str(&format!(
            "PLANT {} {} {} {} {} {} {}\n",
            p.plant_type, p.x, p.y, p.size, p.health, p.fruits, p.cooldown
        ));
    }

    out.push_str(&format!("TURN {}\n", st.turn));
    out.push_str(&format!("SCORES {} {}\n", st.scores[0], st.scores[1]));
    out.push_str(&format!("HORIZON {}\n", sit.horizon));
    out.push_str(&format!(
        "PROVE {}",
        match sit.prove_side {
            None => "-".to_string(),
            Some(p) => p.to_string(),
        }
    ));
    out
}

fn parse_carry6(nums: &[&str]) -> [i32; 6] {
    let mut out = [0i32; 6];
    assert!(nums.len() >= 6, "expected 6 ints, got {:?}", nums);
    for (i, slot) in out.iter_mut().enumerate() {
        *slot = nums[i]
            .parse()
            .unwrap_or_else(|_| panic!("bad int {:?} in carry list {:?}", nums[i], nums));
    }
    out
}

fn parse_unit(fields: &[&str]) -> Unit {
    assert!(fields.len() >= 14, "UNIT needs 14 fields, got {:?}", fields);
    let n: Vec<i32> = fields
        .iter()
        .map(|f| {
            f.parse()
                .unwrap_or_else(|_| panic!("bad UNIT field {:?}", f))
        })
        .collect();
    Unit {
        id: n[0],
        player: n[1],
        x: n[2],
        y: n[3],
        ms: n[4],
        cc: n[5],
        hp: n[6],
        chop: n[7],
        carry: [n[8], n[9], n[10], n[11], n[12], n[13]],
    }
}

fn parse_plant(fields: &[&str]) -> Plant {
    assert!(fields.len() >= 7, "PLANT needs 7 fields, got {:?}", fields);
    Plant {
        plant_type: fields[0].to_string(),
        x: fields[1].parse().expect("PLANT x"),
        y: fields[2].parse().expect("PLANT y"),
        size: fields[3].parse().expect("PLANT size"),
        health: fields[4].parse().expect("PLANT health"),
        fruits: fields[5].parse().expect("PLANT fruits"),
        cooldown: fields[6].parse().expect("PLANT cooldown"),
    }
}

fn fmt6(a: &[i32; 6]) -> String {
    format!("{} {} {} {} {} {}", a[0], a[1], a[2], a[3], a[4], a[5])
}
