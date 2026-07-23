//! Interactive referee-protocol parity audit for the frozen D11 live integration.

use std::io::{BufRead, BufReader, Read, Write};
use std::process::{Child, ChildStdin, ChildStdout, Command, Stdio};
use std::time::Instant;

use troll_farm::game::fast::{cid, FastState, NavTable};
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::game::state::GameState;
use troll_farm::rl_level1::{level2_recipe, ACTION_SIZE, OBS_SIZE, OBS_WIDTH};
use troll_farm::rl_level3::{Level3Env, Level3Terminal};

const OBS_CELLS: usize = 11 * 22;

struct Bot {
    child: Child,
    input: Option<ChildStdin>,
    output: BufReader<ChildStdout>,
}

impl Bot {
    fn spawn(path: &str, recipe: u8) -> Self {
        let mut child = Command::new(path)
            .arg("--audit")
            .arg(recipe.to_string())
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .unwrap_or_else(|error| panic!("cannot spawn {path}: {error}"));
        let input = child.stdin.take().expect("child stdin");
        let output = BufReader::new(child.stdout.take().expect("child stdout"));
        Self {
            child,
            input: Some(input),
            output,
        }
    }

    fn send(&mut self, text: &str) {
        let input = self.input.as_mut().expect("open child stdin");
        input.write_all(text.as_bytes()).expect("write child input");
        input.flush().expect("flush child input");
    }

    fn receive(&mut self) -> Option<String> {
        let mut line = String::new();
        (self.output.read_line(&mut line).ok()? != 0)
            .then(|| line.trim_end_matches(['\n', '\r']).to_string())
    }

    fn finish(mut self) -> (i32, String) {
        drop(self.input.take());
        let status = self.child.wait().expect("wait for child");
        let mut stderr = String::new();
        self.child
            .stderr
            .take()
            .expect("child stderr")
            .read_to_string(&mut stderr)
            .expect("read child stderr");
        (status.code().unwrap_or(-1), stderr)
    }
}

fn grid(game: &GameState) -> String {
    let rows: Vec<String> = (0..game.height)
        .map(|y| {
            (0..game.width)
                .map(|x| {
                    let cell = (x, y);
                    if cell == game.shacks[0] {
                        '0'
                    } else if cell == game.shacks[1] {
                        '1'
                    } else if game.iron.contains(&cell) {
                        '+'
                    } else if game.water.contains(&cell) {
                        '~'
                    } else if game.walkable.contains(&cell) {
                        '.'
                    } else {
                        '#'
                    }
                })
                .collect()
        })
        .collect();
    format!("{} {}\n{}\n", game.width, game.height, rows.join("\n"))
}

fn plant_name(kind: u8) -> &'static str {
    ["PLUM", "LEMON", "APPLE", "BANANA"]
        .get(kind as usize)
        .copied()
        .unwrap_or("BANANA")
}

fn turn_block(state: &FastState) -> String {
    let mut text = String::new();
    for player in 0..2 {
        let inv = state.inv[player];
        text.push_str(&format!(
            "{} {} {} {} {} {}\n",
            inv[0], inv[1], inv[2], inv[3], inv[4], inv[5]
        ));
    }
    text.push_str(&format!("{}\n", state.n_plants));
    for index in 0..state.n_plants as usize {
        text.push_str(&format!(
            "{} {} {} {} {} {} {}\n",
            plant_name(state.p_type[index]),
            state.p_x[index],
            state.p_y[index],
            state.p_size[index],
            state.p_health[index],
            state.p_fruits[index],
            state.p_cd[index]
        ));
    }
    text.push_str(&format!("{}\n", state.n_units));
    for index in 0..state.n_units as usize {
        let carry = state.u_carry[index];
        text.push_str(&format!(
            "{} {} {} {} {} {} {} {} {} {} {} {} {} {}\n",
            state.u_id[index],
            state.u_pl[index],
            state.u_x[index],
            state.u_y[index],
            state.u_ms[index],
            state.u_cc[index],
            state.u_hp[index],
            state.u_chop[index],
            carry[0],
            carry[1],
            carry[2],
            carry[3],
            carry[4],
            carry[5]
        ));
    }
    text
}

fn fnv(data: &[u8]) -> u64 {
    let mut hash = 0xcbf2_9ce4_8422_2325u64;
    for &byte in data {
        hash ^= byte as u64;
        hash = hash.wrapping_mul(0x0100_0000_01b3);
    }
    hash
}

fn inferred_broadcast(hash: u64, width: usize, height: usize) -> Option<u8> {
    (0u8..=255).find(|&value| {
        let mut candidate = [0u8; OBS_CELLS];
        for y in 0..height {
            for x in 0..width {
                candidate[y * OBS_WIDTH + x] = value;
            }
        }
        fnv(&candidate) == hash
    })
}

fn encoded_distance(distance: u8) -> u8 {
    (255.0 * distance as f32 / 40.0).round().clamp(0.0, 255.0) as u8
}

#[derive(Debug)]
struct Record {
    observation_hash: u64,
    mask_hash: u64,
    action: usize,
    channel_hashes: Vec<u64>,
}

fn parse_audit(line: &str) -> Result<(Vec<Record>, String), String> {
    let (audit, commands) = line
        .split_once('|')
        .ok_or_else(|| "missing audit separator".to_string())?;
    let fields: Vec<&str> = audit.split_whitespace().collect();
    if fields.first() != Some(&"AUDIT") || fields.len() < 2 {
        return Err("invalid audit prefix".to_string());
    }
    let count: usize = fields[1]
        .parse()
        .map_err(|_| "invalid audit count".to_string())?;
    let width = if fields.len() == 2 + 3 * count {
        3
    } else if fields.len() == 2 + 4 * count {
        4
    } else {
        return Err(format!(
            "audit field count {} for {count} records",
            fields.len()
        ));
    };
    let mut records = Vec::with_capacity(count);
    for index in 0..count {
        let base = 2 + width * index;
        records.push(Record {
            observation_hash: fields[base]
                .parse()
                .map_err(|_| "invalid observation hash".to_string())?,
            mask_hash: fields[base + 1]
                .parse()
                .map_err(|_| "invalid mask hash".to_string())?,
            action: fields[base + 2]
                .parse()
                .map_err(|_| "invalid action".to_string())?,
            channel_hashes: if width == 4 {
                fields[base + 3]
                    .split(',')
                    .map(|value| {
                        value
                            .parse()
                            .map_err(|_| "invalid channel hash".to_string())
                    })
                    .collect::<Result<Vec<u64>, String>>()?
            } else {
                Vec::new()
            },
        });
    }
    Ok((records, commands.to_string()))
}

fn own_units(state: &FastState) -> Vec<usize> {
    let mut units: Vec<usize> = (0..state.n_units as usize)
        .filter(|&index| state.u_pl[index] == 0)
        .collect();
    units.sort_by_key(|&index| state.u_id[index]);
    units
}

fn target_built(state: &FastState, target: (i8, i8, i8, i8)) -> bool {
    let own = own_units(state);
    let Some(&starter) = own.first() else {
        return false;
    };
    own.into_iter().any(|index| {
        index != starter
            && (
                state.u_ms[index],
                state.u_cc[index],
                state.u_hp[index],
                state.u_chop[index],
            ) == target
    })
}

fn expected_command(action: usize, id: i16) -> String {
    let plane = action / OBS_CELLS;
    let cell = action % OBS_CELLS;
    let x = cell % OBS_WIDTH;
    let y = cell / OBS_WIDTH;
    match plane {
        0 => format!("MOVE {id} {x} {y}"),
        1 => format!("HARVEST {id}"),
        2 => format!("CHOP {id}"),
        3 => format!("DROP {id}"),
        4 => format!("MINE {id}"),
        5..=8 => format!("PLANT {id} {}", plant_name((plane - 5) as u8)),
        9..=12 => format!("PICK {id} {}", plant_name((plane - 9) as u8)),
        _ => "WAIT".to_string(),
    }
}

#[derive(Default)]
struct Totals {
    games: usize,
    turns: usize,
    decisions: usize,
    trains: usize,
    crops: usize,
    harvests: usize,
    destructions: usize,
    first_response_ns: Vec<u64>,
    warm_response_ns: Vec<u64>,
}

fn fail(seed: u64, turn: usize, message: impl AsRef<str>) -> ! {
    eprintln!(
        "D11 live parity failure seed={seed} turn={turn}: {}",
        message.as_ref()
    );
    std::process::exit(1);
}

fn play(binary: &str, seed: u64, totals: &mut Totals) {
    let (recipe, target) = level2_recipe(seed);
    let game = generate_bronze(seed);
    let mut env =
        Level3Env::new_level5_crop_first_funded_trio_repeated_pressure_reacquire_180(seed, 240);
    let process_started = Instant::now();
    let mut bot = Bot::spawn(binary, recipe);
    bot.send(&grid(&game));
    let mut terminal: Option<Level3Terminal> = None;
    let mut previous_actions: Vec<usize> = Vec::new();

    for referee_turn in 1..=240usize {
        let state_before = env.state;
        let built = target_built(&state_before, target);
        let own = own_units(&state_before);
        let expected_phases = if built { 2 } else { 1 };
        bot.send(&turn_block(&state_before));
        let response_started = Instant::now();
        let line = bot
            .receive()
            .unwrap_or_else(|| fail(seed, referee_turn, "child EOF"));
        let response_ns = response_started.elapsed().as_nanos() as u64;
        if referee_turn == 1 {
            totals
                .first_response_ns
                .push(process_started.elapsed().as_nanos() as u64);
        } else {
            totals.warm_response_ns.push(response_ns);
        }
        let (records, commands) =
            parse_audit(&line).unwrap_or_else(|error| fail(seed, referee_turn, error));
        if records.len() != expected_phases {
            fail(
                seed,
                referee_turn,
                format!("{} phases != expected {expected_phases}", records.len()),
            );
        }

        let mut expected_commands = Vec::new();
        if !built {
            expected_commands.push(format!(
                "TRAIN {} {} {} {}",
                target.0, target.1, target.2, target.3
            ));
        }
        let mut actions = Vec::new();
        for (phase, record) in records.iter().enumerate() {
            let mut observation = vec![0u8; OBS_SIZE];
            let mut mask = vec![0u8; ACTION_SIZE];
            env.observe(&mut observation, &mut mask);
            let reference_observation_hash = fnv(&observation);
            let reference_mask_hash = fnv(&mask);
            if record.observation_hash != reference_observation_hash {
                let changed: Vec<usize> = if record.channel_hashes.len() == OBS_SIZE / OBS_CELLS {
                    (0..record.channel_hashes.len())
                        .filter(|&channel| {
                            fnv(&observation[channel * OBS_CELLS..(channel + 1) * OBS_CELLS])
                                != record.channel_hashes[channel]
                        })
                        .collect()
                } else {
                    Vec::new()
                };
                let infer_broadcast = |channel: usize| {
                    if record.channel_hashes.len() == OBS_SIZE / OBS_CELLS {
                        inferred_broadcast(
                            record.channel_hashes[channel],
                            state_before.w as usize,
                            state_before.h as usize,
                        )
                    } else {
                        None
                    }
                };
                let source_93 = infer_broadcast(93);
                let source_101 = infer_broadcast(101);
                let mut reference_phase1_101 = None;
                let mut source_phase1_101 = None;
                let mut source_candidates = Vec::new();
                let mut reference_candidates = Vec::new();
                if phase == 0 && records.len() == 2 {
                    let _ = env.step(record.action);
                    let mut second_observation = vec![0u8; OBS_SIZE];
                    let mut second_mask = vec![0u8; ACTION_SIZE];
                    env.observe(&mut second_observation, &mut second_mask);
                    reference_phase1_101 = Some(second_observation[101 * OBS_CELLS]);
                    if records[1].channel_hashes.len() == OBS_SIZE / OBS_CELLS {
                        source_phase1_101 = inferred_broadcast(
                            records[1].channel_hashes[101],
                            state_before.w as usize,
                            state_before.h as usize,
                        );
                    }
                    let nav = NavTable::build(&game);
                    for y in 0..state_before.h {
                        for x in 0..state_before.w {
                            let cell = cid(x, y, state_before.w);
                            if !nav.walk[cell] {
                                continue;
                            }
                            let d0 = encoded_distance(nav.d(
                                cid(
                                    state_before.u_x[own[0]],
                                    state_before.u_y[own[0]],
                                    state_before.w,
                                ),
                                cell,
                            ));
                            let d1 = encoded_distance(nav.d(
                                cid(
                                    state_before.u_x[own[1]],
                                    state_before.u_y[own[1]],
                                    state_before.w,
                                ),
                                cell,
                            ));
                            if Some(d0) == source_101 && Some(d1) == source_phase1_101 {
                                source_candidates.push((x, y));
                            }
                            if d0 == observation[101 * OBS_CELLS]
                                && Some(d1) == reference_phase1_101
                            {
                                reference_candidates.push((x, y));
                            }
                        }
                    }
                }
                fail(
                    seed,
                    referee_turn,
                    format!(
                        "phase {phase} observation {:016x} != {:016x}; changed channels {changed:?}; channel93 source={source_93:?} reference={}; channel101 source={source_101:?}/{source_phase1_101:?} reference={}/{reference_phase1_101:?}; source_candidates={source_candidates:?}; reference_candidates={reference_candidates:?}; previous_actions={previous_actions:?}; own={:?}; plants={:?}",
                        record.observation_hash, reference_observation_hash,
                        observation[93 * OBS_CELLS],
                        observation[101 * OBS_CELLS],
                        own.iter().map(|&i|(state_before.u_id[i],state_before.u_x[i],state_before.u_y[i])).collect::<Vec<_>>(),
                        (0..state_before.n_plants as usize).map(|i|(state_before.p_type[i],state_before.p_x[i],state_before.p_y[i])).collect::<Vec<_>>(),
                    ),
                );
            }
            if record.mask_hash != reference_mask_hash {
                fail(
                    seed,
                    referee_turn,
                    format!(
                        "phase {phase} mask {:016x} != {:016x}",
                        record.mask_hash, reference_mask_hash
                    ),
                );
            }
            if record.action >= ACTION_SIZE || mask[record.action] == 0 {
                fail(
                    seed,
                    referee_turn,
                    format!("phase {phase} illegal action {}", record.action),
                );
            }
            actions.push(record.action);
            terminal = Some(env.step(record.action));
        }
        for (slot, &ui) in own.iter().enumerate() {
            if slot < actions.len() {
                expected_commands.push(expected_command(actions[slot], state_before.u_id[ui]));
            } else {
                expected_commands.push("WAIT".to_string());
            }
        }
        let expected_line = expected_commands.join(";");
        if commands != expected_line {
            fail(
                seed,
                referee_turn,
                format!("commands {commands:?} != {expected_line:?}"),
            );
        }
        totals.turns += 1;
        totals.decisions += records.len();
        previous_actions = actions;
        if terminal.as_ref().is_some_and(|value| value.done) {
            break;
        }
    }
    let final_state = terminal.unwrap_or_else(|| fail(seed, 240, "no terminal record"));
    if final_state.training_turn > 0 {
        totals.trains += 1;
    }
    if final_state.created_crop {
        totals.crops += 1;
    }
    if final_state.renewable_harvests > 0 {
        totals.harvests += 1;
    }
    totals.destructions += final_state.opponent_crop_destructions as usize;
    let (code, stderr) = bot.finish();
    if code != 0 || !stderr.is_empty() {
        fail(
            seed,
            totals.turns,
            format!("child exit={code} stderr={stderr:?}"),
        );
    }
    totals.games += 1;
}

fn percentile(values: &mut [u64], numerator: usize, denominator: usize) -> u64 {
    values.sort_unstable();
    values[((values.len() * numerator + denominator - 1) / denominator).saturating_sub(1)]
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 4 {
        eprintln!("usage: d11_live_parity <live-binary> <seed-base> <seed-count>");
        std::process::exit(2);
    }
    let binary = &args[1];
    let seed_base: u64 = args[2].parse().expect("seed base");
    let seed_count: u64 = args[3].parse().expect("seed count");
    let mut totals = Totals::default();
    for seed in seed_base..seed_base + seed_count {
        play(binary, seed, &mut totals);
    }
    let first_max = *totals.first_response_ns.iter().max().unwrap_or(&0);
    let warm_max = *totals.warm_response_ns.iter().max().unwrap_or(&0);
    let warm_p95 = percentile(&mut totals.warm_response_ns, 95, 100);
    println!(
        "{{\"pass\":true,\"seed_base\":{},\"seed_count\":{},\"games\":{},\"turns\":{},\"decisions\":{},\"trains\":{},\"terminal_crops\":{},\"renewable_harvest_games\":{},\"opponent_crop_destructions\":{},\"first_response_max_ns\":{},\"warm_response_p95_ns\":{},\"warm_response_max_ns\":{}}}",
        seed_base,
        seed_count,
        totals.games,
        totals.turns,
        totals.decisions,
        totals.trains,
        totals.crops,
        totals.harvests,
        totals.destructions,
        first_max,
        warm_p95,
        warm_max
    );
}
