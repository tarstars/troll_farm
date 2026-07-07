#![allow(dead_code, unused)]
// CodinGame Spring Challenge 2026 - Troll Farm bot (Rust port of Python v0.7.1)
// Single-file submission. stdlib only.

use std::collections::{HashMap, HashSet, VecDeque};
use std::io::{self, BufRead, Write};
use std::cell::RefCell;

// ── constants ───────────────────────────────────────────────────────────────

const VERSION: &str = "1.33.0-hoard"; // B2: hoard bands + Scale training ladder (Tempo-inert)
// (the sequential cascade jobs.rs was REMOVED for submission size — 100 KB cap; it lives in
// git history and in the frozen v1.26.0 artifacts for instant fallback)
mod state;
pub use state::*;
pub mod motion;
pub mod planner;
pub mod tactics;
// Flip to true for a SIM-FIDELITY validation run: echoes the full per-turn state
// to stderr (captured in the replay) so we can replay a real game through the sim
// and compare turn-by-turn. Off by default (no effect on play or stdout parity).
const DEBUG: bool = false;



// ── WOOD-RACE bot (v1.0) — beats the Silver Boss ~68% in the local sim ─────────
// Mirror of strategies::mybot (validated in the referee-faithful Rust sim). Strategy:
//   * GREEDY expansion to ~4 trolls (train the cheapest affordable troll each turn),
//     jumping the queue to build TWO fast (ms2,cc2,chop2) choppers as soon as afford-
//     able; the rest are speed harvesters. Mine iron to fund the choppers' chop cost.
//   * Choppers fell the best tree (close + big) with a DENIAL bias toward the foe's
//     shack -- felling starves the opponent's fruit while banking 4pt-each wood.
//   * Harvesters grab the NEAREST ripe fruit (max throughput) and seed a tiny base
//     plum orchard; everyone banks when full.
// The boss is a similar wood/denial bot; our edge is faster (ms2) choppers that win
// the race to contested trees + higher fruit throughput (nearest-ripe harvesting).
// Cheap pure chopper (ms1, cc2, hp0, chop2): swept best vs silver_boss at 87% (vs the
// old ms2 (2,2,1,2) at 81%). cc2 = 2 wood/fell is essential; dropping ms+hp saves plum
// +apple for a stronger economy while still winning the denial race (DW=3) + woodfarm.
// hp0 (was hp1): saves n+1 APPLE per chopper; the only loss is a rarely-reachable
// fruit-harvest fallback. Confirmed on BOTH boss models at 1000 seeds (2026-07-02):
// scriptboss 59.8→60.9% (margin +14.7→+18.2), silverboss 77.5→78.4% (+24.1→+26.9).
const MB_CHOPPER: (i32, i32, i32, i32) = (2, 3, 0, 3); // v1.12.0: cc3/chop3 SUPER-chopper (fell fast, bank every 3) — the nmahoude throughput lever
const MB_NCHOPPERS: i32 = 1; // ONE super-chopper; the other trolls are HARVESTERS that fund it + feed the farm
// chop1 harvesters (+n+1 iron each): every fruit troll can also FELL the base
// farm's young bananas (the "mower"). Blueprint from arena replays: 250-pt bots
// sustain 0.30 wood/turn vs our 0.07; fellers must live AT the farm, and the
// denial choppers can't. Both-model win at 1000 seeds: scriptboss 63.0->64.3%
// (margin +25.8->+31.6), silverboss 85.1->87.5% (+51.4->+54.1); wood 90->105.
const MB_HARVESTERS: [(i32, i32, i32, i32); 3] = [(2, 2, 2, 0), (1, 2, 2, 0), (1, 1, 1, 0)];
const MB_MAX_TROLLS: usize = 4;
const MB_MAX_ORCHARD: usize = 2;
const MB_MIN_TURNS_LEFT: i32 = 20;
// Denial-heavy chopper targeting (swept 2026-07-01 in the faithful sim): DW=3, WT=0
// lifts the bot from 67.6% -> 78.0% vs silver_boss. Our cheap fast choppers win the
// race to the BOSS's trees and starve its wood+fruit; biasing hard toward the enemy
// shack (and dropping the tree-size preference) is decisively better than balanced.
const MB_DENIAL_W: i32 = 0;
const MB_SIZE_W: i32 = 0;

thread_local! {
    // xorshift RNG for the watchdog sidestep — FIXED seed: fully deterministic
    // (sequence position is state-driven). Survivor of the RHEA machinery cut.
    static RH_RNG: RefCell<u64> = RefCell::new(0x9E3779B97F4A7C15);
}

fn rh_rand() -> u64 {
    RH_RNG.with(|rng| {
        let mut r = rng.borrow_mut();
        *r ^= *r << 13;
        *r ^= *r >> 7;
        *r ^= *r << 17;
        *r
    })
}

// (decide_sched, the RHEA fast engine + searcher, and the v1.0.x legacy deciders were
// REMOVED 2026-07-06 for the 100 KB submission cap — run() calls decide_elite only.
// Full history: git; frozen artifacts: cgauto/submissions/.)

// B1/B2: the meta selector consumed by tactics::phase_for. Tempo is the live meta
// (phase-inert: phase_for(Tempo, _) == Phase::Tempo always, so every phase-gated band in
// planner.rs/tactics.rs is a no-op) — Tempo is equality-proven byte-identical to the
// pre-phase champion. Scale (Hoard→Factory at T_SWITCH) now has real Hoard-phase behavior
// (fell suppression + denial exception + wallet band + training ladder) but is still not
// selected live. See rust/src/botmain/tactics.rs and planner.rs.
const GE_META: tactics::Meta = tactics::Meta::Tempo;
const GE_SPEC: (i32, i32, i32, i32) = (2, 3, 0, 2); // cc=3 chopper (Boss-5 mechanism: capture 3 wood/size-3 tree)
const GE_MAX_TROLLS: i32 = 2; // 3rd hand DORMANT until the farm-death disease is treated (it never trains through a dead farm gate; v1.28.1 telemetry 0/8)
const GE_FEEDER_SPEC: (i32, i32, i32, i32) = (1, 1, 1, 0); // cheap hands: 3 plum/3 lemon/3 apple at n=2 (half the old feeder price)
const GE_FEEDER_T: i32 = 60; // after the chopper economy stabilizes
const GE_FEEDER_FARM: usize = 3; // map-distance farm now; the feeder's JOB is to grow it
const GE_CHOP_DELAY: i32 = 0; // NO delay: train chopper early (denial > accumulation, proven 2026-07-05)
const GE_CHOP_FARM: usize = 3; // train as soon as affordable (early aggression, v1.4.5 regime)
const GE_FARM_R: i32 = 2; // v1.13.0: TIGHT farm hugging the shack — halves the chopper's bank-trip distance (the throughput bottleneck)
const GE_FARM_MAX: usize = 12; // v1.19.0: fill the radius-2 area (~12 cells) — more trees maturing in parallel = chopper idles less
const GE_FELL_SIZE: i32 = 2; // NATIVE/contested trees: fell at size 2 = DENIAL (grab before opponent)
const GE_CHOP_R: i32 = 5; // v1.13.0 LIVE roam (GE_CHOP_R=3 was marginally better in bursts but within noise; kept 5)
const GE_LIQ_T: i32 = 34; // turns_rem <= this: fell anything reachable (A1 liq44 REJECTED by gatekeeper 2026-07-07)
const GE_STARTER_CHOP: bool = true; // let a chop-capable starter help fell
const GE_MIN_TURNS_LEFT: i32 = 20; // no training inside the last 20 turns
const GE_SEED_RESERVE: usize = 2; // protect K most-mature farm bananas as seed sources
const GE_FARM_FELL: i32 = 3; // OUR farm bananas: fell at size 3 = PRODUCTION (cc=3 captures all 3)



/// v1.4.0 live decider: the gold-elite pure-production strategy. The standalone
/// bot is always player 0 (my_trolls). A 1:1 port of GoldElite::decide with an
/// added turn-1 MSG and an anti-stall watchdog (below).
fn decide_elite(state: &State) -> Vec<String> {
    if state.turn == 1 {
        motion::reset();
        tactics::reset();
        planner::reset();
    }
    let mut my: Vec<Troll> = state.my_trolls.clone();
    my.sort_by_key(|t| t.id);

    // L1: tactical plan → L2: per-troll job assignment → L3: motion post-pass
    let plan = tactics::plan(state, &my);
    let mut cmd_by_id = planner::assign(state, &plan, &my);
    if DEBUG && state.turn % 5 == 0 {
        eprintln!(
            "@TFFARM t={} farm={} seeds={} n={} flaps={} phase={:?}",
            state.turn, plan.farm_now, state.my_inventory[BANANA], my.len(), planner::flaps(), plan.phase
        );
    }

    // R6a: JOINT MOVE RESOLUTION — the manager's motion stage. Collect every MOVE's goal,
    // choose all landing cells together (max total progress; swaps/chains exploited;
    // stationary teammates hard obstacles), and pin each MOVE to its landing cell. When
    // the joint optimum keeps a troll in place, the original MOVE is left as issued (the
    // engine blocks it harmlessly; the watchdog below still guards real stalls).
    let intents: Vec<(i32, Cell)> = cmd_by_id
        .iter()
        .filter_map(|(id, c)| {
            let p: Vec<&str> = c.split_whitespace().collect();
            if p.len() == 4 && p[0] == "MOVE" {
                Some((*id, (p[2].parse().ok()?, p[3].parse().ok()?)))
            } else {
                None
            }
        })
        .collect();
    let landing = motion::solve_moves(state, &my, &intents);
    for (id, cell) in landing {
        let cur = my.iter().find(|t| t.id == id).map(|t| t.pos());
        if cur != Some(cell) {
            cmd_by_id.insert(id, format!("MOVE {} {} {}", id, cell.0, cell.1));
        }
    }
    // anti-stall watchdog (R3b: motion layer) — sidestep trolls self-blocked 2+ turns
    motion::watchdog(state, &my, &mut cmd_by_id);

    let mut actions: Vec<String> = Vec::new();
    if state.turn == 1 {
        actions.push(format!("MSG v{}", VERSION));
    }
    let mut ids: Vec<i32> = cmd_by_id.keys().copied().collect();
    ids.sort();
    for id in ids {
        actions.push(cmd_by_id[&id].clone());
    }

    if plan.train_now
        && TOTAL_TURNS - state.turn > GE_MIN_TURNS_LEFT
        && !my.iter().any(|u| u.pos() == plan.shack)
    {
        actions.push(format!("TRAIN {} {} {} {}", plan.train_spec.0, plan.train_spec.1, plan.train_spec.2, plan.train_spec.3));
    }

    if actions.is_empty() {
        actions.push("WAIT".into());
    }
    actions
}

// ── I/O parsing ───────────────────────────────────────────────────────────────

fn parse_grid(grid_lines: &[String]) -> (HashSet<Cell>, Cell, Cell, HashSet<Cell>, HashSet<Cell>) {
    let mut walkable = HashSet::new();
    let mut iron = HashSet::new();
    let mut water = HashSet::new();
    let mut my_shack = (0i32, 0i32);
    let mut opp_shack = (0i32, 0i32);
    for (y, line) in grid_lines.iter().enumerate() {
        for (x, ch) in line.chars().enumerate() {
            let cell = (x as i32, y as i32);
            match ch {
                '0' => my_shack = cell,
                '1' => opp_shack = cell,
                '.' => { walkable.insert(cell); }
                '+' => { iron.insert(cell); }
                '~' => { water.insert(cell); }
                _ => {} // '#' and others are rocks
            }
        }
    }
    (walkable, my_shack, opp_shack, iron, water)
}

fn read_line(reader: &mut impl BufRead) -> Option<String> {
    let mut s = String::new();
    match reader.read_line(&mut s) {
        Ok(0) => None,
        Ok(_) => Some(s.trim_end_matches('\n').trim_end_matches('\r').to_string()),
        Err(_) => None,
    }
}

fn parse_turn(
    reader: &mut impl BufRead,
    walkable: &HashSet<Cell>,
    my_shack: Cell,
    opp_shack: Cell,
    turn: i32,
    iron_cells: &HashSet<Cell>,
    water_cells: &HashSet<Cell>,
) -> Option<State> {
    let inv0_line = read_line(reader)?;
    let my_inventory: Vec<i32> = inv0_line.split_whitespace()
        .map(|v| v.parse().unwrap())
        .collect();
    let inv1_line = read_line(reader)?;
    let opp_inventory: Vec<i32> = inv1_line.split_whitespace()
        .map(|v| v.parse().unwrap())
        .collect();

    let tree_count_line = read_line(reader)?;
    let tree_count: usize = tree_count_line.trim().parse().unwrap();
    let mut trees = Vec::with_capacity(tree_count);
    for _ in 0..tree_count {
        let line = read_line(reader)?;
        let parts: Vec<&str> = line.split_whitespace().collect();
        trees.push(Tree {
            tree_type: parts[0].to_string(),
            x: parts[1].parse().unwrap(),
            y: parts[2].parse().unwrap(),
            size: parts[3].parse().unwrap(),
            health: parts[4].parse().unwrap(),
            fruits: parts[5].parse().unwrap(),
            cooldown: parts[6].parse().unwrap(),
        });
    }

    let troll_count_line = read_line(reader)?;
    let troll_count: usize = troll_count_line.trim().parse().unwrap();
    let mut my_trolls = Vec::new();
    let mut opp_trolls = Vec::new();
    for _ in 0..troll_count {
        let line = read_line(reader)?;
        let f: Vec<i32> = line.split_whitespace()
            .map(|v| v.parse().unwrap())
            .collect();
        // id player x y ms cc hp chop carry[6]
        let troll = Troll {
            id: f[0],
            x: f[2],
            y: f[3],
            movement_speed: f[4],
            carry_capacity: f[5],
            harvest_power: f[6],
            chop_power: f[7],
            carry: [f[8], f[9], f[10], f[11], f[12], f[13]],
        };
        if f[1] == 0 {
            my_trolls.push(troll);
        } else {
            opp_trolls.push(troll);
        }
    }

    let my_inv: [i32; 6] = [my_inventory[0], my_inventory[1], my_inventory[2],
                            my_inventory[3], my_inventory[4], my_inventory[5]];
    let opp_inv: [i32; 6] = [opp_inventory[0], opp_inventory[1], opp_inventory[2],
                             opp_inventory[3], opp_inventory[4], opp_inventory[5]];

    Some(State {
        walkable: walkable.clone(),
        my_shack,
        opp_shack,
        my_inventory: my_inv,
        opp_inventory: opp_inv,
        trees,
        my_trolls,
        opp_trolls,
        turn,
        iron_cells: iron_cells.clone(),
        water_cells: water_cells.clone(),
    })
}

// ── main ──────────────────────────────────────────────────────────────────────

/// Echo per-turn state to stderr for sim validation (gated by DEBUG). At turn 1
/// it logs the map + full initial trees/trolls (to reconstruct the start); every
/// turn it logs a compact digest (both inventories + all troll positions) so a
/// captured game can be replayed through the sim and compared turn-by-turn.
fn debug_log(state: &State, grid: &[String], width: i32, height: i32) {
    if !DEBUG {
        return;
    }
    if state.turn == 1 {
        eprintln!("@TFMAP {} {}", width, height);
        for l in grid {
            eprintln!("@TFMAP {}", l.trim_end());
        }
        for t in &state.trees {
            eprintln!(
                "@TFI P {} {} {} {} {} {} {}",
                t.tree_type, t.x, t.y, t.size, t.health, t.fruits, t.cooldown
            );
        }
        for (pl, list) in [(0, &state.my_trolls), (1, &state.opp_trolls)] {
            for u in list {
                eprintln!(
                    "@TFI U {} {} {} {} {} {} {} {} {} {} {} {} {} {}",
                    u.id, pl, u.x, u.y, u.movement_speed, u.carry_capacity,
                    u.harvest_power, u.chop_power, u.carry[0], u.carry[1],
                    u.carry[2], u.carry[3], u.carry[4], u.carry[5]
                );
            }
        }
    }
    let join = |a: &[i32; 6]| a.iter().map(|v| v.to_string()).collect::<Vec<_>>().join(",");
    let mut us = String::new();
    for u in &state.my_trolls {
        us.push_str(&format!("{},0,{},{};", u.id, u.x, u.y));
    }
    for u in &state.opp_trolls {
        us.push_str(&format!("{},1,{},{};", u.id, u.x, u.y));
    }
    eprintln!("@TFD {} {} {} {}", state.turn, join(&state.my_inventory), join(&state.opp_inventory), us);

    // Compact per-turn SUMMARY (printed LAST so it's the console line that survives
    // truncation): both scores, tree count, and OPPONENT troll stats -- so we can read
    // the real Boss 4's composition (fruit vs wood) and troll build from one screenshot.
    let score = |inv: &[i32; 6]| inv[0] + inv[1] + inv[2] + inv[3] + 4 * inv[5];
    let opp_builds: Vec<String> = state
        .opp_trolls
        .iter()
        .map(|u| format!("{}:{}.{}.{}.{}", u.id, u.movement_speed, u.carry_capacity, u.harvest_power, u.chop_power))
        .collect();
    let my_builds: Vec<String> = state
        .my_trolls
        .iter()
        .map(|u| format!("{}:{}.{}.{}.{}", u.id, u.movement_speed, u.carry_capacity, u.harvest_power, u.chop_power))
        .collect();
    eprintln!(
        "@TFSUM t={} me={} opp={} trees={} myinv=[{}] oppinv=[{}] mybuilds={} oppbuilds={}",
        state.turn, score(&state.my_inventory), score(&state.opp_inventory), state.trees.len(),
        join(&state.my_inventory), join(&state.opp_inventory),
        my_builds.join(","), opp_builds.join(",")
    );
}

pub fn run() {
    let stdin = io::stdin();
    let stdout = io::stdout();
    let mut reader = io::BufReader::new(stdin.lock());
    let mut out = io::BufWriter::new(stdout.lock());

    // Read header: width height
    let header = match read_line(&mut reader) {
        Some(s) => s,
        None => return,
    };
    let mut hw = header.split_whitespace();
    let width: i32 = hw.next().unwrap().parse().unwrap();
    let height: i32 = hw.next().unwrap().parse().unwrap();

    let mut grid_lines = Vec::with_capacity(height as usize);
    for _ in 0..height {
        match read_line(&mut reader) {
            Some(line) => grid_lines.push(line),
            None => return,
        }
    }

    let (walkable, my_shack, opp_shack, iron_cells, water_cells) = parse_grid(&grid_lines);

    let mut turn = 0i32;
    loop {
        turn += 1;
        match parse_turn(&mut reader, &walkable, my_shack, opp_shack, turn, &iron_cells, &water_cells) {
            None => break,
            Some(state) => {
                debug_log(&state, &grid_lines, width, height);
                let cmds = decide_elite(&state);
                // @TFMOVE: motion-rule instrument (motion_analyze.py) — positions BEFORE
                // moving + intended MOVEs; block rate = intended-but-didn't-advance.
                if DEBUG {
                    let pos: Vec<String> = state
                        .my_trolls
                        .iter()
                        .map(|t| format!("{}@{},{}", t.id, t.x, t.y))
                        .collect();
                    let moves: Vec<String> =
                        cmds.iter().filter(|c| c.starts_with("MOVE ")).cloned().collect();
                    eprintln!("@TFMOVE t={} pos=[{}] moves=[{}]", state.turn, pos.join(" "), moves.join(" "));
                }
                writeln!(out, "{}", cmds.join(";")).unwrap();
                out.flush().unwrap();
            }
        }
    }
}
