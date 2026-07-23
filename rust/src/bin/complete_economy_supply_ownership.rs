//! Provenance diagnostic for the top complete economy against adaptive Gold.

#[path = "yamo_orchard_live.rs"]
mod yamo;

pub use yamo::{bot, game};

use std::collections::{BTreeSet, HashMap, HashSet};
use std::fs::File;
use std::io::Write;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

use troll_farm::game::engine::{has_stalled, item_index, step, BANANA, WOOD};
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::game::state::{Cell, GameState};
use troll_farm::strategies::gold_elite::{GoldEconomyConfig, GoldElite};
use troll_farm::strategies::Strategy;
use yamo::bot::moisan::SecureOrchardBot;
use yamo::bot::Bot;
use yamo::game::{GameState as YamoState, Plant, PlantKind, Stats, Unit};

const TOTAL_TURNS: i32 = 300;
const CHECKPOINTS: [i32; 5] = [100, 150, 200, 250, 300];

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum Origin {
    Natural = 0,
    Ours = 1,
    Opponent = 2,
    Unknown = 3,
}

#[derive(Clone, Copy, Default)]
struct Attribution {
    wood: [[i32; 4]; 2],
    fruit: [[[i32; 4]; 4]; 2],
    early_fruit: [[[i32; 4]; 4]; 2],
    successful_plants: [usize; 2],
    early_successful_plants: [usize; 2],
    phase_successful_plants: [[usize; 5]; 2],
    ambiguous_births: usize,
}

impl Attribution {
    fn add_wood(&mut self, collector: usize, origin: Origin, amount: i32) {
        self.wood[collector][origin as usize] += amount;
    }

    fn add_fruit(
        &mut self,
        collector: usize,
        origin: Origin,
        kind: usize,
        amount: i32,
        early: bool,
    ) {
        self.fruit[collector][origin as usize][kind] += amount;
        if early {
            self.early_fruit[collector][origin as usize][kind] += amount;
        }
    }

    fn total_wood(&self) -> i32 {
        self.wood.iter().flatten().sum()
    }

    fn assigned_wood(&self) -> i32 {
        self.total_wood()
            - self.wood[0][Origin::Unknown as usize]
            - self.wood[1][Origin::Unknown as usize]
    }
}

#[derive(Clone, Copy, Default)]
struct StockSnapshot {
    recorded: bool,
    opponent_score: i32,
    opponent_wood: i32,
    opponent_workers: usize,
    opponent_successful_plants: usize,
    banked_banana: i32,
    carried_banana: i32,
    opponent_banana_crops: usize,
    opponent_unfruited_banana_crops: usize,
    opponent_crop_banana_fruits: i32,
    natural_banana_fruits: i32,
    our_crop_banana_fruits: i32,
}

#[derive(Clone, Copy)]
struct StockFlow {
    checkpoints: [StockSnapshot; 5],
    post100_exposure_turns: usize,
    zero_immediate_seed_turns: usize,
    zero_owned_seed_turns: usize,
    lineage_absent_turns: usize,
    low_redundancy_turns: usize,
    current_zero_owned_streak: usize,
    max_zero_owned_streak: usize,
    minimum_immediate_seeds: i32,
    minimum_owned_seed_stock: i32,
}

impl Default for StockFlow {
    fn default() -> Self {
        Self {
            checkpoints: [StockSnapshot::default(); 5],
            post100_exposure_turns: 0,
            zero_immediate_seed_turns: 0,
            zero_owned_seed_turns: 0,
            lineage_absent_turns: 0,
            low_redundancy_turns: 0,
            current_zero_owned_streak: 0,
            max_zero_owned_streak: 0,
            minimum_immediate_seeds: i32::MAX,
            minimum_owned_seed_stock: i32::MAX,
        }
    }
}

#[derive(Clone, Copy)]
struct Outcome {
    own_score: i32,
    opponent_score: i32,
    own_inventory_wood: i32,
    opponent_inventory_wood: i32,
    terminal_turn: i32,
    attribution: Attribution,
    stock: StockFlow,
}

enum Policy {
    Resident(SecureOrchardBot),
    Farm(GoldElite),
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
enum Profile {
    Resident,
    Farm,
    Adaptive,
}

impl Profile {
    fn label(self) -> &'static str {
        match self {
            Self::Resident => "resident",
            Self::Farm => "lean_m2c2h0k2",
            Self::Adaptive => "adaptive_density",
        }
    }

    fn policy(self) -> Policy {
        match self {
            Self::Resident => Policy::Resident(SecureOrchardBot::new()),
            Self::Farm => Policy::Farm(top_farm()),
            Self::Adaptive => Policy::Farm(GoldElite::adaptive()),
        }
    }
}

impl Policy {
    fn commands(&mut self, game: &GameState, player: usize) -> Vec<String> {
        match self {
            Self::Resident(bot) => bot.commands(&yamo_view(game, player)),
            Self::Farm(bot) => bot.decide(game, player),
        }
    }
}

fn top_farm() -> GoldElite {
    GoldElite::configured(GoldEconomyConfig {
        max_trolls: 2,
        choppers: 1,
        stagger: 0,
        spec1: (2, 2, 0, 2),
        spec2: (2, 2, 0, 2),
        planters: 0,
        hold_until: 0,
        farm_cap: 12,
        co_fell: false,
        adaptive: false,
    })
}

fn yamo_view(game: &GameState, player: usize) -> YamoState {
    let opponent = 1 - player;
    YamoState {
        width: game.width,
        height: game.height,
        walkable: game.walkable.iter().copied().collect::<BTreeSet<_>>(),
        shacks: [game.shacks[player], game.shacks[opponent]],
        inventories: [game.inventories[player], game.inventories[opponent]],
        units: game
            .units
            .iter()
            .map(|unit| Unit {
                id: unit.id,
                player: usize::from(unit.player as usize != player),
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
        scores: [game.scores[player], game.scores[opponent]],
        turn: game.turn,
        next_id: game.next_id,
        iron: game.iron.iter().copied().collect::<BTreeSet<_>>(),
        water: game.water.iter().copied().collect::<BTreeSet<_>>(),
    }
}

fn command_unit_ids(commands: &[String], action: &str) -> HashSet<i32> {
    commands
        .iter()
        .filter_map(|command| {
            let mut fields = command.split_whitespace();
            if fields.next()? != action {
                return None;
            }
            fields.next()?.parse().ok()
        })
        .collect()
}

fn plant_attempts(game: &GameState, player: usize, commands: &[String]) -> HashSet<Cell> {
    commands
        .iter()
        .filter_map(|command| {
            let mut fields = command.split_whitespace();
            if fields.next()? != "PLANT" {
                return None;
            }
            let id: i32 = fields.next()?.parse().ok()?;
            game.units
                .iter()
                .find(|unit| unit.id == id && unit.player as usize == player)
                .map(|unit| unit.pos())
        })
        .collect()
}

fn banana_stock(
    game: &GameState,
    seat: usize,
    provenance: &HashMap<Cell, Origin>,
) -> (i32, i32, usize, usize, i32, i32, i32) {
    let opponent = 1 - seat;
    let banked = game.inventories[opponent][BANANA];
    let carried = game
        .units
        .iter()
        .filter(|unit| unit.player as usize == opponent)
        .map(|unit| unit.carry[BANANA])
        .sum();
    let mut opponent_crops = 0;
    let mut opponent_unfruited = 0;
    let mut opponent_crop_fruits = 0;
    let mut natural_fruits = 0;
    let mut our_crop_fruits = 0;
    for plant in game
        .plants
        .iter()
        .filter(|plant| plant.plant_type == "BANANA")
    {
        match provenance
            .get(&plant.pos())
            .copied()
            .unwrap_or(Origin::Unknown)
        {
            Origin::Opponent => {
                opponent_crops += 1;
                opponent_unfruited += usize::from(plant.fruits == 0);
                opponent_crop_fruits += plant.fruits;
            }
            Origin::Natural => natural_fruits += plant.fruits,
            Origin::Ours => our_crop_fruits += plant.fruits,
            Origin::Unknown => {}
        }
    }
    (
        banked,
        carried,
        opponent_crops,
        opponent_unfruited,
        opponent_crop_fruits,
        natural_fruits,
        our_crop_fruits,
    )
}

fn observe_stock_turn(
    game: &GameState,
    seat: usize,
    provenance: &HashMap<Cell, Origin>,
    stock: &mut StockFlow,
) {
    if game.turn <= 100 {
        return;
    }
    let (banked, carried, crops, _, crop_fruits, _, _) = banana_stock(game, seat, provenance);
    let immediate = banked + carried;
    let owned = immediate + crop_fruits;
    stock.post100_exposure_turns += 1;
    stock.zero_immediate_seed_turns += usize::from(immediate == 0);
    stock.zero_owned_seed_turns += usize::from(owned == 0);
    stock.lineage_absent_turns += usize::from(owned == 0 && crops == 0);
    stock.low_redundancy_turns += usize::from(immediate <= 1 && crops <= 1);
    stock.minimum_immediate_seeds = stock.minimum_immediate_seeds.min(immediate);
    stock.minimum_owned_seed_stock = stock.minimum_owned_seed_stock.min(owned);
    if owned == 0 {
        stock.current_zero_owned_streak += 1;
        stock.max_zero_owned_streak = stock
            .max_zero_owned_streak
            .max(stock.current_zero_owned_streak);
    } else {
        stock.current_zero_owned_streak = 0;
    }
}

fn capture_checkpoint(
    game: &GameState,
    seat: usize,
    provenance: &HashMap<Cell, Origin>,
    attribution: &Attribution,
) -> StockSnapshot {
    let opponent = 1 - seat;
    let (
        banked_banana,
        carried_banana,
        opponent_banana_crops,
        opponent_unfruited_banana_crops,
        opponent_crop_banana_fruits,
        natural_banana_fruits,
        our_crop_banana_fruits,
    ) = banana_stock(game, seat, provenance);
    StockSnapshot {
        recorded: true,
        opponent_score: game.scores[opponent],
        opponent_wood: game.inventories[opponent][WOOD],
        opponent_workers: game
            .units
            .iter()
            .filter(|unit| unit.player as usize == opponent)
            .count(),
        opponent_successful_plants: attribution.successful_plants[1],
        banked_banana,
        carried_banana,
        opponent_banana_crops,
        opponent_unfruited_banana_crops,
        opponent_crop_banana_fruits,
        natural_banana_fruits,
        our_crop_banana_fruits,
    }
}

fn phase_index(turn: i32) -> usize {
    match turn {
        ..=100 => 0,
        101..=150 => 1,
        151..=200 => 2,
        201..=250 => 3,
        _ => 4,
    }
}

fn play(initial: &GameState, seat: usize, profile: Profile) -> Outcome {
    let mut game = initial.clone();
    let mut ours = profile.policy();
    let theirs = GoldElite::adaptive();
    let mut provenance: HashMap<Cell, Origin> = game
        .plants
        .iter()
        .map(|plant| (plant.pos(), Origin::Natural))
        .collect();
    let mut attribution = Attribution::default();
    let mut stock = StockFlow::default();
    let mut turns_until_end = 0;
    while game.turn <= TOTAL_TURNS {
        observe_stock_turn(&game, seat, &provenance, &mut stock);
        let ours_commands = ours.commands(&game, seat);
        let theirs_commands = theirs.decide(&game, 1 - seat);
        let commands = if seat == 0 {
            [ours_commands, theirs_commands]
        } else {
            [theirs_commands, ours_commands]
        };
        let before_plants: HashSet<_> = game.plants.iter().map(|plant| plant.pos()).collect();
        let attempts = [
            plant_attempts(&game, 0, &commands[0]),
            plant_attempts(&game, 1, &commands[1]),
        ];
        let chop_ids = [
            command_unit_ids(&commands[0], "CHOP"),
            command_unit_ids(&commands[1], "CHOP"),
        ];
        let harvest_ids = [
            command_unit_ids(&commands[0], "HARVEST"),
            command_unit_ids(&commands[1], "HARVEST"),
        ];
        let before_plant_kind: HashMap<_, _> = game
            .plants
            .iter()
            .map(|plant| (plant.pos(), item_index(&plant.plant_type)))
            .collect();
        let before_units: HashMap<_, _> = game
            .units
            .iter()
            .map(|unit| (unit.id, (unit.player as usize, unit.pos(), unit.carry)))
            .collect();
        let resolved_turn = game.turn;

        step(&mut game, &commands[0], &commands[1]);

        let after_units: HashMap<_, _> = game
            .units
            .iter()
            .map(|unit| (unit.id, unit.carry))
            .collect();
        for player in 0..2 {
            for id in &chop_ids[player] {
                let Some((actual_player, cell, before_carry)) = before_units.get(id) else {
                    continue;
                };
                let Some(after_carry) = after_units.get(id) else {
                    continue;
                };
                let gained = after_carry[WOOD] - before_carry[WOOD];
                if gained <= 0 || *actual_player != player {
                    continue;
                }
                let relative_collector = usize::from(player != seat);
                let origin = provenance.get(cell).copied().unwrap_or(Origin::Unknown);
                attribution.add_wood(relative_collector, origin, gained);
            }
            for id in &harvest_ids[player] {
                let Some((actual_player, cell, before_carry)) = before_units.get(id) else {
                    continue;
                };
                let Some(after_carry) = after_units.get(id) else {
                    continue;
                };
                if *actual_player != player {
                    continue;
                }
                let Some(kind) = before_plant_kind.get(cell).copied() else {
                    continue;
                };
                let gained = after_carry[kind] - before_carry[kind];
                if gained <= 0 {
                    continue;
                }
                let relative_collector = usize::from(player != seat);
                let origin = provenance.get(cell).copied().unwrap_or(Origin::Unknown);
                attribution.add_fruit(
                    relative_collector,
                    origin,
                    kind,
                    gained,
                    resolved_turn <= 100,
                );
            }
        }

        let after_plants: HashSet<_> = game.plants.iter().map(|plant| plant.pos()).collect();
        provenance.retain(|cell, _| after_plants.contains(cell));
        for cell in after_plants.difference(&before_plants) {
            let claimants: Vec<_> = (0..2)
                .filter(|player| attempts[*player].contains(cell))
                .collect();
            let origin = match claimants.as_slice() {
                [player] => {
                    let relative_player = usize::from(*player != seat);
                    attribution.successful_plants[relative_player] += 1;
                    if resolved_turn <= 100 {
                        attribution.early_successful_plants[relative_player] += 1;
                    }
                    attribution.phase_successful_plants[relative_player]
                        [phase_index(resolved_turn)] += 1;
                    if relative_player == 0 {
                        Origin::Ours
                    } else {
                        Origin::Opponent
                    }
                }
                _ => {
                    attribution.ambiguous_births += 1;
                    Origin::Unknown
                }
            };
            provenance.insert(*cell, origin);
        }
        if let Some(index) = CHECKPOINTS
            .iter()
            .position(|checkpoint| *checkpoint == resolved_turn)
        {
            stock.checkpoints[index] = capture_checkpoint(&game, seat, &provenance, &attribution);
        }
        if has_stalled(&game, &mut turns_until_end) {
            break;
        }
    }
    Outcome {
        own_score: game.scores[seat],
        opponent_score: game.scores[1 - seat],
        own_inventory_wood: game.inventories[seat][WOOD],
        opponent_inventory_wood: game.inventories[1 - seat][WOOD],
        terminal_turn: game.turn,
        attribution,
        stock,
    }
}

#[derive(Clone, Copy)]
struct Task {
    seed: u64,
    seat: usize,
}

struct Row {
    task: Task,
    profile: Profile,
    outcome: Outcome,
}

fn run_task(task: Task) -> [Row; 3] {
    let initial = generate_bronze(task.seed);
    [
        Row {
            task,
            profile: Profile::Resident,
            outcome: play(&initial, task.seat, Profile::Resident),
        },
        Row {
            task,
            profile: Profile::Farm,
            outcome: play(&initial, task.seat, Profile::Farm),
        },
        Row {
            task,
            profile: Profile::Adaptive,
            outcome: play(&initial, task.seat, Profile::Adaptive),
        },
    ]
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    let output = args
        .get(1)
        .cloned()
        .unwrap_or_else(|| "complete-economy-supply-ownership.tsv".to_string());
    let threads = args
        .get(2)
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or(20)
        .max(1);
    let tasks = Arc::new(
        (0..30)
            .flat_map(|seed| (0..2).map(move |seat| Task { seed, seat }))
            .collect::<Vec<_>>(),
    );
    let next = Arc::new(AtomicUsize::new(0));
    let mut rows = std::thread::scope(|scope| {
        let handles: Vec<_> = (0..threads)
            .map(|_| {
                let tasks = Arc::clone(&tasks);
                let next = Arc::clone(&next);
                scope.spawn(move || {
                    let mut local = Vec::new();
                    loop {
                        let index = next.fetch_add(1, Ordering::Relaxed);
                        if index >= tasks.len() {
                            break;
                        }
                        local.extend(run_task(tasks[index]));
                    }
                    local
                })
            })
            .collect();
        handles
            .into_iter()
            .flat_map(|handle| handle.join().expect("ownership worker"))
            .collect::<Vec<_>>()
    });
    rows.sort_by_key(|row| (row.task.seed, row.task.seat, row.profile));
    let mut writer = std::io::BufWriter::new(File::create(&output).expect("create output"));
    let origins = ["natural", "ours", "opponent", "unknown"];
    let kinds = ["plum", "lemon", "apple", "banana"];
    let mut header = vec![
        "seed",
        "seat",
        "profile",
        "own_score",
        "opponent_score",
        "margin",
        "own_inventory_wood",
        "opponent_inventory_wood",
        "terminal_turn",
        "own_successful_plants",
        "opponent_successful_plants",
        "own_early_successful_plants",
        "opponent_early_successful_plants",
        "ambiguous_births",
        "total_chop_wood",
        "assigned_chop_wood",
        "own_from_natural",
        "own_from_ours",
        "own_from_opponent",
        "own_from_unknown",
        "opponent_from_natural",
        "opponent_from_ours",
        "opponent_from_opponent",
        "opponent_from_unknown",
    ]
    .into_iter()
    .map(str::to_string)
    .collect::<Vec<_>>();
    for phase in ["fruit", "early_fruit"] {
        for collector in ["own", "opponent"] {
            for origin in origins {
                for kind in kinds {
                    header.push(format!("{collector}_{phase}_from_{origin}_{kind}"));
                }
            }
        }
    }
    for collector in ["own", "opponent"] {
        for phase in ["1_100", "101_150", "151_200", "201_250", "251_300"] {
            header.push(format!("{collector}_successful_plants_{phase}"));
        }
    }
    header.extend(
        [
            "post100_exposure_turns",
            "zero_immediate_seed_turns",
            "zero_owned_seed_turns",
            "lineage_absent_turns",
            "low_redundancy_turns",
            "max_zero_owned_streak",
            "minimum_immediate_seeds",
            "minimum_owned_seed_stock",
        ]
        .into_iter()
        .map(str::to_string),
    );
    for checkpoint in CHECKPOINTS {
        for field in [
            "recorded",
            "opponent_score",
            "opponent_wood",
            "opponent_workers",
            "opponent_successful_plants",
            "banked_banana",
            "carried_banana",
            "opponent_banana_crops",
            "opponent_unfruited_banana_crops",
            "opponent_crop_banana_fruits",
            "natural_banana_fruits",
            "our_crop_banana_fruits",
        ] {
            header.push(format!("t{checkpoint}_{field}"));
        }
    }
    writeln!(writer, "{}", header.join("\t")).expect("write header");
    for row in rows {
        let out = row.outcome;
        let wood = out.attribution.wood;
        let mut fields = vec![
            row.task.seed.to_string(),
            row.task.seat.to_string(),
            row.profile.label().to_string(),
            out.own_score.to_string(),
            out.opponent_score.to_string(),
            (out.own_score - out.opponent_score).to_string(),
            out.own_inventory_wood.to_string(),
            out.opponent_inventory_wood.to_string(),
            out.terminal_turn.to_string(),
            out.attribution.successful_plants[0].to_string(),
            out.attribution.successful_plants[1].to_string(),
            out.attribution.early_successful_plants[0].to_string(),
            out.attribution.early_successful_plants[1].to_string(),
            out.attribution.ambiguous_births.to_string(),
            out.attribution.total_wood().to_string(),
            out.attribution.assigned_wood().to_string(),
            wood[0][0].to_string(),
            wood[0][1].to_string(),
            wood[0][2].to_string(),
            wood[0][3].to_string(),
            wood[1][0].to_string(),
            wood[1][1].to_string(),
            wood[1][2].to_string(),
            wood[1][3].to_string(),
        ];
        for matrix in [out.attribution.fruit, out.attribution.early_fruit] {
            for collector in matrix {
                for origin in collector {
                    fields.extend(origin.into_iter().map(|value| value.to_string()));
                }
            }
        }
        for collector in out.attribution.phase_successful_plants {
            fields.extend(collector.into_iter().map(|value| value.to_string()));
        }
        fields.extend([
            out.stock.post100_exposure_turns.to_string(),
            out.stock.zero_immediate_seed_turns.to_string(),
            out.stock.zero_owned_seed_turns.to_string(),
            out.stock.lineage_absent_turns.to_string(),
            out.stock.low_redundancy_turns.to_string(),
            out.stock.max_zero_owned_streak.to_string(),
            (if out.stock.minimum_immediate_seeds == i32::MAX {
                -1
            } else {
                out.stock.minimum_immediate_seeds
            })
            .to_string(),
            (if out.stock.minimum_owned_seed_stock == i32::MAX {
                -1
            } else {
                out.stock.minimum_owned_seed_stock
            })
            .to_string(),
        ]);
        for snapshot in out.stock.checkpoints {
            fields.extend([
                i32::from(snapshot.recorded).to_string(),
                snapshot.opponent_score.to_string(),
                snapshot.opponent_wood.to_string(),
                snapshot.opponent_workers.to_string(),
                snapshot.opponent_successful_plants.to_string(),
                snapshot.banked_banana.to_string(),
                snapshot.carried_banana.to_string(),
                snapshot.opponent_banana_crops.to_string(),
                snapshot.opponent_unfruited_banana_crops.to_string(),
                snapshot.opponent_crop_banana_fruits.to_string(),
                snapshot.natural_banana_fruits.to_string(),
                snapshot.our_crop_banana_fruits.to_string(),
            ]);
        }
        writeln!(writer, "{}", fields.join("\t")).expect("write row");
    }
    eprintln!("saved {} scenarios x 3 profiles to {}", tasks.len(), output);
}

#[cfg(test)]
mod tests {
    use super::*;
    use troll_farm::game::engine::APPLE;

    #[test]
    fn attribution_matrix_tracks_known_and_unknown_wood() {
        let mut attribution = Attribution::default();
        attribution.add_wood(0, Origin::Ours, 3);
        attribution.add_wood(1, Origin::Unknown, 2);
        attribution.add_fruit(1, Origin::Natural, APPLE, 2, true);
        assert_eq!(attribution.total_wood(), 5);
        assert_eq!(attribution.assigned_wood(), 3);
        assert_eq!(attribution.fruit[1][Origin::Natural as usize][APPLE], 2);
        assert_eq!(
            attribution.early_fruit[1][Origin::Natural as usize][APPLE],
            2
        );
    }

    #[test]
    fn diagnostic_profiles_complete_on_one_common_map() {
        let rows = run_task(Task { seed: 0, seat: 0 });
        assert_eq!(rows[0].profile, Profile::Resident);
        assert_eq!(rows[1].profile, Profile::Farm);
        assert_eq!(rows[2].profile, Profile::Adaptive);
        assert!(rows.iter().all(|row| row.outcome.terminal_turn > 1));
    }

    #[test]
    fn stock_flow_records_banana_lineage_buffers() {
        let mut game = generate_bronze(0);
        let seat = 0;
        let opponent = 1;
        game.turn = 101;
        game.inventories[opponent][BANANA] = 2;
        let provenance = game
            .plants
            .iter()
            .map(|plant| (plant.pos(), Origin::Natural))
            .collect();
        let mut stock = StockFlow::default();
        observe_stock_turn(&game, seat, &provenance, &mut stock);
        assert_eq!(stock.post100_exposure_turns, 1);
        assert_eq!(stock.zero_immediate_seed_turns, 0);
        assert_eq!(stock.minimum_immediate_seeds, 2);
    }
}
