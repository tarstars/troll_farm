//! Parity check: play engine.rs games (schedbot vs silverboss), mirror every
//! turn's commands into FastState/step_fast, and compare state each turn.
//! Usage: fastcheck [seeds]
use troll_farm::game::engine::{has_stalled, step};
use troll_farm::game::fast::{cid, FAct, FCmds, FastState, NavTable};
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::strategies::{roster, Strategy};

fn to_fcmds(g: &troll_farm::game::state::GameState, cmds: &[String], player: u8, w: i8) -> FCmds {
    let mut fc = FCmds::default();
    // unit slot mapping: FastState keeps insertion order == g.units order
    let idx_of = |id: i32| -> Option<usize> { g.units.iter().position(|u| u.id == id) };
    for raw in cmds {
        let p: Vec<&str> = raw.trim().split_whitespace().collect();
        if p.is_empty() {
            continue;
        }
        match p[0] {
            "TRAIN" if p.len() >= 5 => {
                fc.train = Some((
                    p[1].parse().unwrap_or(0),
                    p[2].parse().unwrap_or(0),
                    p[3].parse().unwrap_or(0),
                    p[4].parse().unwrap_or(0),
                ));
            }
            "MOVE" if p.len() >= 4 => {
                if let (Ok(id), Ok(x), Ok(y)) =
                    (p[1].parse::<i32>(), p[2].parse::<i8>(), p[3].parse::<i8>())
                {
                    if let Some(ui) = idx_of(id) {
                        if g.units[ui].player as u8 == player {
                            fc.acts[ui] = FAct::Move(cid(x, y, w) as u8);
                        }
                    }
                }
            }
            "HARVEST" | "CHOP" | "DROP" | "MINE" if p.len() >= 2 => {
                if let Ok(id) = p[1].parse::<i32>() {
                    if let Some(ui) = idx_of(id) {
                        if g.units[ui].player as u8 == player {
                            fc.acts[ui] = match p[0] {
                                "HARVEST" => FAct::Harvest,
                                "CHOP" => FAct::Chop,
                                "DROP" => FAct::Drop,
                                _ => FAct::Mine,
                            };
                        }
                    }
                }
            }
            "PLANT" | "PICK" if p.len() >= 3 => {
                if let Ok(id) = p[1].parse::<i32>() {
                    if let Some(ui) = idx_of(id) {
                        if g.units[ui].player as u8 == player {
                            let ty = troll_farm::game::fast::type_idx(p[2]);
                            fc.acts[ui] = if p[0] == "PLANT" {
                                FAct::Plant(ty)
                            } else {
                                FAct::Pick(ty)
                            };
                        }
                    }
                }
            }
            _ => {}
        }
    }
    fc
}

fn main() {
    // SINGLE-STEP parity with per-turn resync: rebuild FastState from the engine
    // state each turn, apply one step of both, compare. Position diffs from
    // pathing tie-breaks are counted separately from hard rule mismatches.
    let seeds: u64 = std::env::args()
        .nth(1)
        .and_then(|s| s.parse().ok())
        .unwrap_or(20);
    let bots = roster();
    let a = bots.iter().find(|b| b.name() == "schedbot").unwrap();
    let b = bots.iter().find(|b| b.name() == "silverboss").unwrap();
    let mut pos_diffs = 0u64;
    let mut inv_diffs = 0u64;
    let mut plant_diffs = 0u64;
    let mut steps_total = 0u64;
    for seed in 0..seeds {
        let mut g = generate_bronze(seed);
        let mut turns_until_end = 0;
        let nav = NavTable::build(&g);
        for _ in 0..300 {
            let c0 = a.decide(&g, 0);
            let c1 = b.decide(&g, 1);
            let mut fs = FastState::from_game(&g);
            let fc = [to_fcmds(&g, &c0, 0, fs.w), to_fcmds(&g, &c1, 1, fs.w)];
            troll_farm::game::fast::step_fast(&mut fs, &nav, &fc);
            step(&mut g, &c0, &c1);
            steps_total += 1;
            // compare inventories (score-relevant, position-independent-ish)
            for p in 0..2 {
                for i in 0..6 {
                    if fs.inv[p][i] as i32 != g.inventories[p][i] {
                        inv_diffs += 1;
                    }
                }
            }
            if fs.n_plants as usize != g.plants.len() {
                plant_diffs += 1;
            }
            // positions
            for u in &g.units {
                if let Some(ui) = (0..fs.n_units as usize).find(|&k| fs.u_id[k] as i32 == u.id) {
                    if fs.u_x[ui] as i32 != u.x || fs.u_y[ui] as i32 != u.y {
                        pos_diffs += 1;
                    }
                }
            }
            if has_stalled(&g, &mut turns_until_end) {
                break;
            }
        }
    }
    println!(
        "single-step parity over {} seeds ({} steps): inv diffs {}  plant-count diffs {}  pos diffs {} ({:.2}%)",
        seeds, steps_total, inv_diffs, plant_diffs, pos_diffs,
        100.0 * pos_diffs as f64 / steps_total.max(1) as f64
    );
}
