//! Replay exact Phase 21 maps against the frozen local continuation zoo.

#[path = "yamo_orchard_live.rs"]
mod yamo;

pub use yamo::{bot, game};

use std::cell::Cell;
use std::collections::{BTreeSet, HashMap};
use std::fs::File;
use std::io::{BufReader, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

use troll_farm::game::engine::{
    apply_moves, apply_pick, has_stalled, item_index, parse_cmds, step, training_cost, ParsedCmds,
    APPLE, IRON, LEMON, PLUM, WOOD,
};
use troll_farm::game::state::{GameState, Plant as EnginePlant, Unit as EngineUnit};
use troll_farm::strategies::boss4::Boss4;
use troll_farm::strategies::boss5::Boss5;
use troll_farm::strategies::boss_real::BossReal;
use troll_farm::strategies::compact_gold::CompactGold;
use troll_farm::strategies::gold_elite::{GoldEconomyConfig, GoldElite};
use troll_farm::strategies::legend_field_proxy::{
    LegendFieldProxy, LegendFieldProxyConfig, LegendFieldProxyV2, LegendFieldProxyV2Config,
    LegendFieldProxyV3, LegendFieldProxyV3Config, LegendFieldProxyV4, LegendFieldProxyV5,
    LegendFieldProxyV6, LegendFieldProxyV7, LegendFieldProxyV8, Spec as LegendSpec,
};
use troll_farm::strategies::mybot::MyBot;
use troll_farm::strategies::norxondor_native::NorxondorNative;
use troll_farm::strategies::norxondor_research::{
    NorxondorCompact, NorxondorCooperativeSilver, NorxondorFundedSilver, NorxondorSilver,
    NorxondorSoftCooperativeSilver, NorxondorThreeWorkerSilver,
};
use troll_farm::strategies::printer_bot::PrinterBot;
use troll_farm::strategies::sched_bot::SchedBot;
use troll_farm::strategies::script_boss::ScriptBoss;
use troll_farm::strategies::silver_boss::SilverBoss;
use troll_farm::strategies::Strategy;
use yamo::bot::moisan::SecureOrchardBot;
use yamo::bot::Bot;
use yamo::game::protocol::{read_line, read_static_map, read_turn};
use yamo::game::{GameState as YamoState, Plant, PlantKind, Stats, Unit};

const TOTAL_TURNS: i32 = 300;
const FRUIT_TYPES: [&str; 4] = ["PLUM", "LEMON", "APPLE", "BANANA"];
const PENDING_ACTIONS: [&str; 8] = [
    "move", "pick", "drop", "plant", "harvest", "mine", "chop", "idle",
];
const MODELS: [&str; 8] = [
    "compact_gold",
    "gold_adaptive",
    "gold_elite",
    "mybot",
    "printer_bot",
    "sched_bot",
    "script_boss",
    "silver_boss",
];

fn baseline_model(index: usize) -> Box<dyn Strategy> {
    match index {
        0 => Box::new(CompactGold::new()),
        1 => Box::new(GoldElite::adaptive()),
        2 => Box::new(GoldElite::new()),
        3 => Box::new(MyBot::new()),
        4 => Box::new(PrinterBot::new()),
        5 => Box::new(SchedBot::new()),
        6 => Box::new(ScriptBoss::new()),
        7 => Box::new(SilverBoss::new()),
        _ => unreachable!(),
    }
}

#[derive(Clone, Debug)]
enum ModelKind {
    Baseline(usize),
    Economy(GoldEconomyConfig),
    Structural(usize),
    LegendProxy(LegendFieldProxyConfig),
    LegendProxyV2(LegendFieldProxyV2Config),
    LegendProxyV3(LegendFieldProxyV3Config),
    LegendProxyV4(LegendFieldProxyV3Config),
    LegendProxyV5(LegendFieldProxyV3Config),
    LegendProxyV6(LegendFieldProxyV3Config),
    LegendProxyV7(LegendFieldProxyV3Config),
    LegendProxyV8(LegendFieldProxyV3Config),
    PhaseComponent(usize),
    PhaseSwitch(PhaseSwitchConfig),
    WorkforceSwitch(WorkforceSwitchConfig),
}

#[derive(Clone, Debug)]
struct ModelDefinition {
    label: String,
    kind: ModelKind,
}

impl ModelDefinition {
    fn instantiate(&self) -> Box<dyn Strategy> {
        match self.kind {
            ModelKind::Baseline(index) => baseline_model(index),
            ModelKind::Economy(config) => Box::new(GoldElite::configured(config)),
            ModelKind::Structural(index) => structural_model(index),
            ModelKind::LegendProxy(config) => Box::new(LegendFieldProxy::configured(config)),
            ModelKind::LegendProxyV2(config) => Box::new(LegendFieldProxyV2::configured(config)),
            ModelKind::LegendProxyV3(config) => Box::new(LegendFieldProxyV3::configured(config)),
            ModelKind::LegendProxyV4(config) => Box::new(LegendFieldProxyV4::configured(config)),
            ModelKind::LegendProxyV5(config) => Box::new(LegendFieldProxyV5::configured(config)),
            ModelKind::LegendProxyV6(config) => Box::new(LegendFieldProxyV6::configured(config)),
            ModelKind::LegendProxyV7(config) => Box::new(LegendFieldProxyV7::configured(config)),
            ModelKind::LegendProxyV8(config) => Box::new(LegendFieldProxyV8::configured(config)),
            ModelKind::PhaseComponent(index) => phase_component(index),
            ModelKind::PhaseSwitch(config) => Box::new(PhaseSwitch::new(config)),
            ModelKind::WorkforceSwitch(config) => Box::new(WorkforceSwitch::new(config)),
        }
    }
}

fn baseline_catalog() -> Vec<ModelDefinition> {
    MODELS
        .iter()
        .enumerate()
        .map(|(index, label)| ModelDefinition {
            label: (*label).to_string(),
            kind: ModelKind::Baseline(index),
        })
        .collect()
}

#[allow(clippy::too_many_arguments)]
fn economy_config(
    max_trolls: i32,
    choppers: i32,
    stagger: i32,
    spec1: (i32, i32, i32, i32),
    spec2: (i32, i32, i32, i32),
    planters: i32,
    hold_until: i32,
    farm_cap: usize,
    adaptive: bool,
) -> GoldEconomyConfig {
    GoldEconomyConfig {
        max_trolls,
        choppers,
        stagger,
        spec1,
        spec2,
        planters,
        hold_until,
        farm_cap,
        co_fell: false,
        adaptive,
    }
}

fn economy_model(label: String, config: GoldEconomyConfig) -> ModelDefinition {
    ModelDefinition {
        label,
        kind: ModelKind::Economy(config),
    }
}

fn economy_catalog() -> Vec<ModelDefinition> {
    let default_spec = (2, 2, 0, 2);
    let mut out = Vec::new();
    for spec in [(1, 2, 0, 2), default_spec, (2, 3, 0, 2), (2, 2, 0, 3)] {
        out.push(economy_model(
            format!("lean_m{}c{}h{}k{}", spec.0, spec.1, spec.2, spec.3),
            economy_config(2, 1, 0, spec, default_spec, 0, 0, 12, false),
        ));
    }
    for stagger in [20, 60] {
        for harvest_power in [0, 1] {
            for farm_cap in [12, 20] {
                out.push(economy_model(
                    format!("dual3_s{stagger}_h{harvest_power}_cap{farm_cap}"),
                    economy_config(
                        3,
                        2,
                        stagger,
                        default_spec,
                        (2, 2, harvest_power, 2),
                        0,
                        0,
                        farm_cap,
                        false,
                    ),
                ));
            }
        }
    }
    for hold_until in [0, 60, 100] {
        for farm_cap in [12, 20] {
            out.push(economy_model(
                format!("farm3_hold{hold_until}_cap{farm_cap}"),
                economy_config(
                    3,
                    1,
                    0,
                    default_spec,
                    default_spec,
                    1,
                    hold_until,
                    farm_cap,
                    false,
                ),
            ));
        }
    }
    for stagger in [30, 60] {
        for hold_until in [0, 80, 120] {
            for farm_cap in [18, 24] {
                out.push(economy_model(
                    format!("farm4_s{stagger}_hold{hold_until}_cap{farm_cap}"),
                    economy_config(
                        4,
                        2,
                        stagger,
                        default_spec,
                        default_spec,
                        1,
                        hold_until,
                        farm_cap,
                        false,
                    ),
                ));
            }
        }
    }
    out.push(economy_model(
        "adaptive_density".to_string(),
        economy_config(4, 2, 30, default_spec, default_spec, 1, 100, 24, true),
    ));
    out
}

const STRUCTURAL_MODELS: [&str; 11] = [
    "boss4",
    "boss5",
    "boss_real",
    "norx_native_full",
    "norx_native_three",
    "norx_compact",
    "norx_silver",
    "norx_funded_silver",
    "norx_cooperative_silver",
    "norx_soft_cooperative_silver",
    "norx_three_worker_silver",
];

fn structural_model(index: usize) -> Box<dyn Strategy> {
    match index {
        0 => Box::new(Boss4),
        1 => Box::new(Boss5::new()),
        2 => Box::new(BossReal::new()),
        3 => Box::new(NorxondorNative::new(false)),
        4 => Box::new(NorxondorNative::new(true)),
        5 => Box::new(NorxondorCompact::new()),
        6 => Box::new(NorxondorSilver::new()),
        7 => Box::new(NorxondorFundedSilver::new()),
        8 => Box::new(NorxondorCooperativeSilver::new()),
        9 => Box::new(NorxondorSoftCooperativeSilver::new()),
        10 => Box::new(NorxondorThreeWorkerSilver::new()),
        _ => unreachable!(),
    }
}

fn structural_catalog() -> Vec<ModelDefinition> {
    STRUCTURAL_MODELS
        .iter()
        .enumerate()
        .map(|(index, label)| ModelDefinition {
            label: (*label).to_string(),
            kind: ModelKind::Structural(index),
        })
        .collect()
}

fn legend_proxy_catalog() -> Vec<ModelDefinition> {
    let ladders: [(&str, [LegendSpec; 3]); 2] = [
        ("hp2", [(2, 2, 2, 1), (2, 3, 1, 2), (2, 3, 1, 2)]),
        ("balanced", [(2, 2, 1, 1), (2, 3, 1, 2), (2, 3, 1, 2)]),
    ];
    let mut out = Vec::new();
    for (ladder_name, ladder) in ladders {
        for farmer_count in [1, 2] {
            for fell_start in [1, 100] {
                out.push(ModelDefinition {
                    label: format!("legend_{ladder_name}_f{farmer_count}_fell{fell_start}"),
                    kind: ModelKind::LegendProxy(LegendFieldProxyConfig {
                        ladder,
                        farmer_count,
                        fell_start,
                    }),
                });
            }
        }
    }
    out
}

fn legend_proxy_v2_catalog() -> Vec<ModelDefinition> {
    let producers: [(&str, LegendSpec); 2] = [("hp2", (2, 2, 2, 1)), ("balanced", (2, 2, 1, 1))];
    let choppers: [(&str, LegendSpec); 2] = [("cheap", (2, 2, 0, 2)), ("strong", (3, 4, 1, 3))];
    let mut out = Vec::new();
    for (producer_name, producer_spec) in producers {
        for (chopper_name, chopper_spec) in choppers {
            for (role_name, late_chop) in [("farm", false), ("late_chop", true)] {
                out.push(ModelDefinition {
                    label: format!("legend_v2_{producer_name}_{chopper_name}_{role_name}"),
                    kind: ModelKind::LegendProxyV2(LegendFieldProxyV2Config {
                        producer_spec,
                        chopper_spec,
                        late_chop,
                    }),
                });
            }
        }
    }
    out
}

fn legend_proxy_v3_catalog() -> Vec<ModelDefinition> {
    let first_specs: [(&str, LegendSpec); 2] = [("hp2", (2, 2, 2, 1)), ("balanced", (2, 2, 1, 1))];
    let mut out = Vec::new();
    for (first_name, first_spec) in first_specs {
        for max_workers in [3, 4] {
            for post_producers in [1, 2] {
                out.push(ModelDefinition {
                    label: format!("legend_v3_{first_name}_m{max_workers}_p{post_producers}"),
                    kind: ModelKind::LegendProxyV3(LegendFieldProxyV3Config {
                        first_spec,
                        max_workers,
                        post_producers,
                    }),
                });
            }
        }
    }
    out
}

fn legend_proxy_v4_catalog() -> Vec<ModelDefinition> {
    let first_specs: [(&str, LegendSpec); 2] = [("hp2", (2, 2, 2, 1)), ("balanced", (2, 2, 1, 1))];
    let mut out = Vec::new();
    for (first_name, first_spec) in first_specs {
        for max_workers in [3, 4] {
            for post_producers in [1, 2] {
                out.push(ModelDefinition {
                    label: format!("legend_v4_{first_name}_m{max_workers}_p{post_producers}"),
                    kind: ModelKind::LegendProxyV4(LegendFieldProxyV3Config {
                        first_spec,
                        max_workers,
                        post_producers,
                    }),
                });
            }
        }
    }
    out
}

fn legend_proxy_v5_catalog() -> Vec<ModelDefinition> {
    let first_specs: [(&str, LegendSpec); 2] = [("hp2", (2, 2, 2, 1)), ("balanced", (2, 2, 1, 1))];
    let mut out = Vec::new();
    for (first_name, first_spec) in first_specs {
        for max_workers in [3, 4] {
            for post_producers in [1, 2] {
                out.push(ModelDefinition {
                    label: format!("legend_v5_{first_name}_m{max_workers}_p{post_producers}"),
                    kind: ModelKind::LegendProxyV5(LegendFieldProxyV3Config {
                        first_spec,
                        max_workers,
                        post_producers,
                    }),
                });
            }
        }
    }
    out
}

fn legend_proxy_v6_catalog() -> Vec<ModelDefinition> {
    let first_specs: [(&str, LegendSpec); 2] = [("hp2", (2, 2, 2, 1)), ("balanced", (2, 2, 1, 1))];
    let mut out = Vec::new();
    for (first_name, first_spec) in first_specs {
        for max_workers in [3, 4] {
            for post_producers in [1, 2] {
                out.push(ModelDefinition {
                    label: format!("legend_v6_{first_name}_m{max_workers}_p{post_producers}"),
                    kind: ModelKind::LegendProxyV6(LegendFieldProxyV3Config {
                        first_spec,
                        max_workers,
                        post_producers,
                    }),
                });
            }
        }
    }
    out
}

fn legend_proxy_v7_catalog() -> Vec<ModelDefinition> {
    let first_specs: [(&str, LegendSpec); 2] = [("hp2", (2, 2, 2, 1)), ("balanced", (2, 2, 1, 1))];
    let mut out = Vec::new();
    for (first_name, first_spec) in first_specs {
        for max_workers in [3, 4] {
            for post_producers in [1, 2] {
                out.push(ModelDefinition {
                    label: format!("legend_v7_{first_name}_m{max_workers}_p{post_producers}"),
                    kind: ModelKind::LegendProxyV7(LegendFieldProxyV3Config {
                        first_spec,
                        max_workers,
                        post_producers,
                    }),
                });
            }
        }
    }
    out
}

fn legend_proxy_v8_catalog() -> Vec<ModelDefinition> {
    let first_specs: [(&str, LegendSpec); 2] = [("hp2", (2, 2, 2, 1)), ("balanced", (2, 2, 1, 1))];
    let mut out = Vec::new();
    for (first_name, first_spec) in first_specs {
        for max_workers in [3, 4] {
            for post_producers in [1, 2] {
                out.push(ModelDefinition {
                    label: format!("legend_v8_{first_name}_m{max_workers}_p{post_producers}"),
                    kind: ModelKind::LegendProxyV8(LegendFieldProxyV3Config {
                        first_spec,
                        max_workers,
                        post_producers,
                    }),
                });
            }
        }
    }
    out
}

const PHASE_COMPONENTS: [&str; 8] = [
    "v2_hp2_farm",
    "v2_hp2_late",
    "v2_bal_farm",
    "norx_compact",
    "farm3",
    "farm4",
    "lean",
    "norx_funded",
];

fn phase_component(index: usize) -> Box<dyn Strategy> {
    let default_spec = (2, 2, 0, 2);
    match index {
        0 => Box::new(LegendFieldProxyV2::configured(LegendFieldProxyV2Config {
            producer_spec: (2, 2, 2, 1),
            chopper_spec: default_spec,
            late_chop: false,
        })),
        1 => Box::new(LegendFieldProxyV2::configured(LegendFieldProxyV2Config {
            producer_spec: (2, 2, 2, 1),
            chopper_spec: default_spec,
            late_chop: true,
        })),
        2 => Box::new(LegendFieldProxyV2::configured(LegendFieldProxyV2Config {
            producer_spec: (2, 2, 1, 1),
            chopper_spec: default_spec,
            late_chop: false,
        })),
        3 => Box::new(NorxondorCompact::new()),
        4 => Box::new(GoldElite::configured(economy_config(
            3,
            1,
            0,
            default_spec,
            default_spec,
            1,
            0,
            20,
            false,
        ))),
        5 => Box::new(GoldElite::configured(economy_config(
            4,
            2,
            30,
            default_spec,
            default_spec,
            1,
            120,
            24,
            false,
        ))),
        6 => Box::new(GoldElite::configured(economy_config(
            2,
            1,
            0,
            (1, 2, 0, 2),
            default_spec,
            0,
            0,
            12,
            false,
        ))),
        7 => Box::new(NorxondorFundedSilver::new()),
        _ => unreachable!(),
    }
}

#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
struct PhaseSwitchConfig {
    early: usize,
    late: usize,
    cut: i32,
}

struct PhaseSwitch {
    early: Box<dyn Strategy>,
    late: Box<dyn Strategy>,
    cut: i32,
}

impl PhaseSwitch {
    fn new(config: PhaseSwitchConfig) -> Self {
        Self {
            early: phase_component(config.early),
            late: phase_component(config.late),
            cut: config.cut,
        }
    }
}

impl Strategy for PhaseSwitch {
    fn name(&self) -> &str {
        "d50_phase_switch"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        if game.turn <= self.cut {
            self.early.decide(game, player)
        } else {
            self.late.decide(game, player)
        }
    }
}

fn phase_switch_catalog() -> Vec<ModelDefinition> {
    let mut out = PHASE_COMPONENTS
        .iter()
        .enumerate()
        .map(|(index, label)| ModelDefinition {
            label: format!("d50_anchor_{label}"),
            kind: ModelKind::PhaseComponent(index),
        })
        .collect::<Vec<_>>();
    for early in 0..PHASE_COMPONENTS.len() {
        for late in 0..PHASE_COMPONENTS.len() {
            if early == late {
                continue;
            }
            for cut in [100, 150] {
                out.push(ModelDefinition {
                    label: format!(
                        "d50_t{cut}_{}_to_{}",
                        PHASE_COMPONENTS[early], PHASE_COMPONENTS[late]
                    ),
                    kind: ModelKind::PhaseSwitch(PhaseSwitchConfig { early, late, cut }),
                });
            }
        }
    }
    out
}

#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
enum WorkforceTrigger {
    WorkerThreeNow,
    WorkerThreePlus25,
    WorkerThreePlus50,
    WorkerThreeScore60,
}

impl WorkforceTrigger {
    const ALL: [Self; 4] = [
        Self::WorkerThreeNow,
        Self::WorkerThreePlus25,
        Self::WorkerThreePlus50,
        Self::WorkerThreeScore60,
    ];

    fn label(self) -> &'static str {
        match self {
            Self::WorkerThreeNow => "w3_now",
            Self::WorkerThreePlus25 => "w3_plus25",
            Self::WorkerThreePlus50 => "w3_plus50",
            Self::WorkerThreeScore60 => "w3_score60",
        }
    }

    fn ready(self, game: &GameState, player: usize, third_worker_turn: i32) -> bool {
        if third_worker_turn < 0 {
            return false;
        }
        match self {
            Self::WorkerThreeNow => true,
            Self::WorkerThreePlus25 => game.turn - third_worker_turn >= 25,
            Self::WorkerThreePlus50 => game.turn - third_worker_turn >= 50,
            Self::WorkerThreeScore60 => game.scores[player] >= 60,
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
struct WorkforceSwitchConfig {
    early: usize,
    late: usize,
    trigger: WorkforceTrigger,
}

struct WorkforceSwitch {
    early: Box<dyn Strategy>,
    late: Box<dyn Strategy>,
    trigger: WorkforceTrigger,
    third_worker_turn: Cell<i32>,
    switched: Cell<bool>,
}

impl WorkforceSwitch {
    fn new(config: WorkforceSwitchConfig) -> Self {
        Self {
            early: phase_component(config.early),
            late: phase_component(config.late),
            trigger: config.trigger,
            third_worker_turn: Cell::new(-1),
            switched: Cell::new(false),
        }
    }
}

impl Strategy for WorkforceSwitch {
    fn name(&self) -> &str {
        "d51_workforce_switch"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        if game.turn == 1 {
            self.third_worker_turn.set(-1);
            self.switched.set(false);
        }
        let workers = game
            .units
            .iter()
            .filter(|unit| unit.player as usize == player)
            .count();
        if workers >= 3 && self.third_worker_turn.get() < 0 {
            self.third_worker_turn.set(game.turn);
        }
        if self
            .trigger
            .ready(game, player, self.third_worker_turn.get())
        {
            self.switched.set(true);
        }
        if self.switched.get() {
            self.late.decide(game, player)
        } else {
            self.early.decide(game, player)
        }
    }
}

fn workforce_switch_catalog() -> Vec<ModelDefinition> {
    let mut out = PHASE_COMPONENTS
        .iter()
        .enumerate()
        .map(|(index, label)| ModelDefinition {
            label: format!("d51_anchor_{label}"),
            kind: ModelKind::PhaseComponent(index),
        })
        .collect::<Vec<_>>();
    for early in [0, 1, 2] {
        for late in [4, 5, 6, 7, 1] {
            if early == late {
                continue;
            }
            for trigger in WorkforceTrigger::ALL {
                out.push(ModelDefinition {
                    label: format!(
                        "d51_{}_{}_to_{}",
                        trigger.label(),
                        PHASE_COMPONENTS[early],
                        PHASE_COMPONENTS[late]
                    ),
                    kind: ModelKind::WorkforceSwitch(WorkforceSwitchConfig {
                        early,
                        late,
                        trigger,
                    }),
                });
            }
        }
    }
    out
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

fn read_dataset(path: &str) -> Vec<(u64, GameState)> {
    let file = File::open(path).expect("open field continuation map dataset");
    let mut reader = BufReader::new(file);
    let mut maps = Vec::new();
    while let Some(line) = read_line(&mut reader) {
        if line.is_empty() {
            continue;
        }
        let mut fields = line.split_whitespace();
        assert_eq!(fields.next(), Some("SEED"), "expected SEED record");
        let game_id = fields
            .next()
            .expect("game ID")
            .parse::<u64>()
            .expect("numeric game ID");
        let map = read_static_map(&mut reader).expect("static map record");
        let view = read_turn(&mut reader, &map, 1).expect("turn-one map record");
        maps.push((game_id, engine_state(view)));
    }
    maps
}

fn command_plant_attempts(
    game: &GameState,
    player: usize,
    commands: &[String],
) -> Vec<((i32, i32), String)> {
    commands
        .iter()
        .filter_map(|command| {
            let fields: Vec<_> = command.split_whitespace().collect();
            if fields.len() < 3 || fields[0] != "PLANT" {
                return None;
            }
            let id: i32 = fields[1].parse().ok()?;
            let unit = game
                .units
                .iter()
                .find(|unit| unit.id == id && unit.player as usize == player)?;
            Some((unit.pos(), fields[2].to_ascii_uppercase()))
        })
        .collect()
}

fn successful_opponent_chops(game: &GameState, ours: &[String], theirs: &[String]) -> usize {
    let parsed = [parse_cmds(ours), parse_cmds(theirs)];
    let mut health: HashMap<_, _> = game
        .plants
        .iter()
        .map(|plant| (plant.pos(), plant.health))
        .collect();
    let mut successes = 0;
    for (player, commands) in parsed.iter().enumerate() {
        for id in &commands.chop {
            let Some(unit) = game
                .units
                .iter()
                .find(|unit| unit.id == *id && unit.player as usize == player)
            else {
                continue;
            };
            let free = unit.cc - unit.carry.iter().sum::<i32>();
            let Some(tree_health) = health.get_mut(&unit.pos()) else {
                continue;
            };
            if unit.chop <= 0 || free <= 0 || *tree_health <= 0 {
                continue;
            }
            if player == 1 {
                successes += 1;
            }
            *tree_health -= unit.chop;
        }
    }
    successes
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct TrainFailureConditions {
    shack_occupied: bool,
    budget_short: bool,
    currency_picks: i32,
    multiple_currency_picks: bool,
    oversubscribed_resource: bool,
}

fn train_failure_conditions(
    game: &GameState,
    ours: &[String],
    theirs: &[String],
    player: usize,
    talents: LegendSpec,
) -> TrainFailureConditions {
    let parsed = [parse_cmds(ours), parse_cmds(theirs)];
    let mut before_train = game.clone();
    let mut moves = parsed[0].moves.clone();
    moves.extend(parsed[1].moves.iter());
    apply_moves(&mut before_train, &moves);
    let shack_occupied = before_train
        .units
        .iter()
        .any(|unit| unit.pos() == before_train.shacks[player]);

    let workers = game
        .units
        .iter()
        .filter(|unit| unit.player as usize == player)
        .count();
    let cost = training_cost(workers as i32, talents);
    let inventory_before_pick = before_train.inventories[player];
    let mut successful_picks = [0; 6];
    for pick in parsed[0].pick.iter().chain(parsed[1].pick.iter()) {
        let resource = item_index(&pick.1);
        let before = before_train.inventories[player][resource];
        apply_pick(&mut before_train, std::slice::from_ref(pick));
        if before_train.inventories[player][resource] < before {
            successful_picks[resource] += 1;
        }
    }
    let budget_short = [PLUM, LEMON, APPLE, IRON].into_iter().any(|resource| {
        (resource != IRON || !before_train.iron.is_empty())
            && before_train.inventories[player][resource] < cost[resource]
    });
    let currency_picks = [PLUM, LEMON, APPLE, IRON]
        .into_iter()
        .map(|resource| successful_picks[resource])
        .sum();
    let oversubscribed_resource = [PLUM, LEMON, APPLE, IRON].into_iter().any(|resource| {
        let reserved = if resource == IRON && before_train.iron.is_empty() {
            0
        } else {
            cost[resource]
        };
        successful_picks[resource] > (inventory_before_pick[resource] - reserved).max(0)
    });
    TrainFailureConditions {
        shack_occupied,
        budget_short,
        currency_picks,
        multiple_currency_picks: currency_picks >= 2,
        oversubscribed_resource,
    }
}

#[derive(Clone, Copy, Default)]
struct TrainTelemetry {
    attempts: [i32; 3],
    successes: [i32; 3],
    fail_shack_only: [i32; 3],
    fail_budget_only: [i32; 3],
    fail_both: [i32; 3],
    fail_other: [i32; 3],
    failed_currency_picks: [i32; 3],
    fail_with_multiple_currency_picks: [i32; 3],
    fail_with_oversubscribed_resource: [i32; 3],
}

impl TrainTelemetry {
    fn record_attempt(&mut self, workers_before: usize) -> usize {
        let index = workers_before
            .checked_sub(1)
            .filter(|index| *index < self.attempts.len())
            .expect("TRAIN target must be workforce two through four");
        self.attempts[index] += 1;
        index
    }

    fn record_result(&mut self, index: usize, succeeded: bool, conditions: TrainFailureConditions) {
        if succeeded {
            assert!(
                !conditions.shack_occupied && !conditions.budget_short,
                "successful TRAIN cannot have a predicted pre-TRAIN blocker"
            );
            self.successes[index] += 1;
        } else {
            match (conditions.shack_occupied, conditions.budget_short) {
                (true, false) => self.fail_shack_only[index] += 1,
                (false, true) => self.fail_budget_only[index] += 1,
                (true, true) => self.fail_both[index] += 1,
                (false, false) => self.fail_other[index] += 1,
            }
            self.failed_currency_picks[index] += conditions.currency_picks;
            self.fail_with_multiple_currency_picks[index] +=
                i32::from(conditions.multiple_currency_picks);
            self.fail_with_oversubscribed_resource[index] +=
                i32::from(conditions.oversubscribed_resource);
        }
    }
}

#[derive(Clone, Copy, Default)]
struct Events {
    trains: i32,
    plants: i32,
    plants_by_fruit: [i32; 4],
    harvested_fruit: i32,
    harvested_by_fruit: [i32; 4],
    chops: i32,
    dropped_items: i32,
}

#[derive(Clone, Copy, Default)]
struct StockFlowTelemetry {
    next_train_target: i32,
    next_cost: [i32; 4],
    inventory: [i32; 4],
    carry: [i32; 4],
    standing: [i32; 4],
    ripe: [i32; 4],
    plants: [i32; 4],
    harvested: [i32; 4],
}

#[derive(Clone, Copy)]
struct PendingBillTelemetry {
    turns: i32,
    worker_turns: i32,
    actions: [i32; 8],
    completion_actions: [i32; 8],
    class_turns: [i32; 8],
    class_progress_turns: [i32; 8],
    class_regress_turns: [i32; 8],
    progress_turns: i32,
    equal_turns: i32,
    regress_turns: i32,
    reduced_units: i32,
    increased_units: i32,
    initial_deficit: [i32; 4],
    minimum_deficit: [i32; 4],
    last_deficit: [i32; 4],
    seen: bool,
}

impl Default for PendingBillTelemetry {
    fn default() -> Self {
        Self {
            turns: 0,
            worker_turns: 0,
            actions: [0; 8],
            completion_actions: [0; 8],
            class_turns: [0; 8],
            class_progress_turns: [0; 8],
            class_regress_turns: [0; 8],
            progress_turns: 0,
            equal_turns: 0,
            regress_turns: 0,
            reduced_units: 0,
            increased_units: 0,
            initial_deficit: [0; 4],
            minimum_deficit: [0; 4],
            last_deficit: [0; 4],
            seen: false,
        }
    }
}

impl PendingBillTelemetry {
    fn record(
        &mut self,
        before: [i32; 4],
        after_without_payment: Option<[i32; 4]>,
        actions: [i32; 8],
    ) {
        if !self.seen {
            self.initial_deficit = before;
            self.minimum_deficit = before;
            self.last_deficit = before;
            self.seen = true;
        }
        self.turns += 1;
        self.worker_turns += actions.iter().sum::<i32>();
        for class in 0..PENDING_ACTIONS.len() {
            self.actions[class] += actions[class];
            self.class_turns[class] += i32::from(actions[class] > 0);
        }

        let Some(after) = after_without_payment else {
            for class in 0..PENDING_ACTIONS.len() {
                self.completion_actions[class] += actions[class];
            }
            return;
        };
        for resource in 0..4 {
            self.minimum_deficit[resource] = self.minimum_deficit[resource].min(after[resource]);
            self.last_deficit[resource] = after[resource];
        }
        let before_total: i32 = before.iter().sum();
        let after_total: i32 = after.iter().sum();
        match after_total.cmp(&before_total) {
            std::cmp::Ordering::Less => {
                self.progress_turns += 1;
                self.reduced_units += before_total - after_total;
                for class in 0..PENDING_ACTIONS.len() {
                    self.class_progress_turns[class] += i32::from(actions[class] > 0);
                }
            }
            std::cmp::Ordering::Equal => self.equal_turns += 1,
            std::cmp::Ordering::Greater => {
                self.regress_turns += 1;
                self.increased_units += after_total - before_total;
                for class in 0..PENDING_ACTIONS.len() {
                    self.class_regress_turns[class] += i32::from(actions[class] > 0);
                }
            }
        }
    }
}

fn worker_action_counts(parsed: &ParsedCmds, unit_ids: &BTreeSet<i32>) -> [i32; 8] {
    let mut counts = [0; 8];
    let mut assigned = BTreeSet::new();
    let classes: [Vec<i32>; 7] = [
        parsed.moves.keys().copied().collect(),
        parsed.pick.iter().map(|(id, _)| *id).collect(),
        parsed.drop.clone(),
        parsed.plant.iter().map(|(id, _)| *id).collect(),
        parsed.harvest.clone(),
        parsed.mine.clone(),
        parsed.chop.clone(),
    ];
    for (class, ids) in classes.iter().enumerate() {
        for id in ids {
            if unit_ids.contains(id) {
                assert!(
                    assigned.insert(*id),
                    "parsed worker action must be exclusive"
                );
                counts[class] += 1;
            }
        }
    }
    counts[7] = (unit_ids.len() - assigned.len()) as i32;
    counts
}

fn worker_three_post_stock_deficit(game: &GameState, player: usize) -> [i32; 4] {
    let mut cost = training_cost(2, (2, 3, 1, 2));
    if game.iron.is_empty() {
        cost[IRON] = 0;
    }
    let mut available = game.inventories[player];
    for unit in game
        .units
        .iter()
        .filter(|unit| unit.player as usize == player)
    {
        for resource in PLUM..=IRON {
            available[resource] += unit.carry[resource];
        }
    }
    for plant in &game.plants {
        if let Some(resource) = FRUIT_TYPES
            .iter()
            .position(|kind| *kind == plant.plant_type)
        {
            available[resource] += plant.fruits.max(0);
        }
    }
    let mut out = [0; 4];
    for (ordinal, resource) in [PLUM, LEMON, APPLE, IRON].into_iter().enumerate() {
        out[ordinal] = (cost[resource] - available[resource]).max(0);
    }
    out
}

fn next_training_spec(definition: &ModelDefinition, workers: usize) -> Option<LegendSpec> {
    let config = match definition.kind {
        ModelKind::LegendProxyV3(config)
        | ModelKind::LegendProxyV4(config)
        | ModelKind::LegendProxyV5(config)
        | ModelKind::LegendProxyV6(config)
        | ModelKind::LegendProxyV7(config)
        | ModelKind::LegendProxyV8(config) => config,
        _ => return None,
    };
    if workers == 1 {
        Some(config.first_spec)
    } else if workers < config.max_workers {
        Some((2, 3, 1, 2))
    } else {
        None
    }
}

fn stock_flow_telemetry(
    game: &GameState,
    player: usize,
    definition: &ModelDefinition,
    events: Events,
) -> StockFlowTelemetry {
    let units: Vec<_> = game
        .units
        .iter()
        .filter(|unit| unit.player as usize == player)
        .collect();
    let workers = units.len();
    let next_spec = next_training_spec(definition, workers);
    let mut next_cost = next_spec
        .map(|spec| training_cost(workers as i32, spec))
        .unwrap_or([0; 6]);
    if game.iron.is_empty() {
        next_cost[IRON] = 0;
    }
    let mut out = StockFlowTelemetry {
        next_train_target: next_spec.map_or(0, |_| workers as i32 + 1),
        plants: events.plants_by_fruit,
        harvested: events.harvested_by_fruit,
        ..StockFlowTelemetry::default()
    };
    for (ordinal, resource) in [PLUM, LEMON, APPLE, IRON].into_iter().enumerate() {
        out.next_cost[ordinal] = next_cost[resource];
        out.inventory[ordinal] = game.inventories[player][resource];
        out.carry[ordinal] = units.iter().map(|unit| unit.carry[resource]).sum();
    }
    for plant in &game.plants {
        let Some(resource) = FRUIT_TYPES
            .iter()
            .position(|kind| *kind == plant.plant_type)
        else {
            continue;
        };
        out.standing[resource] += 1;
        out.ripe[resource] += plant.fruits.max(0);
    }
    out
}

#[derive(Clone, Copy, Default)]
struct Snapshot {
    score: i32,
    fruit: i32,
    wood: i32,
    workers: i32,
    plants: i32,
    harvested_fruit: i32,
    chops: i32,
    dropped_items: i32,
}

fn snapshot(game: &GameState, events: Events) -> Snapshot {
    Snapshot {
        score: game.scores[1],
        fruit: game.inventories[1][..WOOD].iter().sum(),
        wood: game.inventories[1][WOOD],
        workers: game.units.iter().filter(|unit| unit.player == 1).count() as i32,
        plants: events.plants,
        harvested_fruit: events.harvested_fruit,
        chops: events.chops,
        dropped_items: events.dropped_items,
    }
}

#[derive(Clone)]
struct AuditRow {
    game_id: u64,
    model: usize,
    first_commands: String,
    terminal_turn: i32,
    third_worker_turn: i32,
    switch_turn: i32,
    switch_score: i32,
    train: TrainTelemetry,
    stock_flow: StockFlowTelemetry,
    pending_bill: PendingBillTelemetry,
    turn50: Option<Snapshot>,
    turn100: Option<Snapshot>,
    final_state: Snapshot,
}

fn play(
    game_id: u64,
    initial: &GameState,
    model_index: usize,
    definition: &ModelDefinition,
) -> AuditRow {
    let mut game = initial.clone();
    let mut candidate = SecureOrchardBot::opponent_crop_priority(100, 6, 1, 1);
    let opponent = definition.instantiate();
    let mut turns_until_end = 0;
    let mut events = Events::default();
    let mut first_commands = None;
    let mut third_worker_turn = -1;
    let mut switch_turn = 0;
    let mut switch_score = 0;
    let mut train = TrainTelemetry::default();
    let mut pending_bill = PendingBillTelemetry::default();
    let mut turn50 = None;
    let mut turn100 = None;
    while game.turn <= TOTAL_TURNS {
        let ours = candidate.commands(&yamo_view(&game));
        if let ModelKind::WorkforceSwitch(config) = &definition.kind {
            let workers = game.units.iter().filter(|unit| unit.player == 1).count();
            if workers >= 3 && third_worker_turn < 0 {
                third_worker_turn = game.turn;
            }
            if switch_turn == 0 && config.trigger.ready(&game, 1, third_worker_turn) {
                switch_turn = game.turn;
                switch_score = game.scores[1];
            }
        }
        let theirs = opponent.decide(&game, 1);
        if first_commands.is_none() {
            first_commands = Some(theirs.join(";"));
        }
        let opponent_units_before: HashMap<_, _> = game
            .units
            .iter()
            .filter(|unit| unit.player == 1)
            .map(|unit| (unit.id, unit.carry))
            .collect();
        let workers_before = opponent_units_before.len();
        let plant_attempts = command_plant_attempts(&game, 1, &theirs);
        let parsed = parse_cmds(&theirs);
        let pending_before = (workers_before == 2
            && next_training_spec(definition, workers_before).is_some())
        .then(|| {
            let unit_ids = opponent_units_before.keys().copied().collect();
            (
                worker_three_post_stock_deficit(&game, 1),
                worker_action_counts(&parsed, &unit_ids),
            )
        });
        assert!(
            parsed.train.len() <= 1,
            "at most one opponent TRAIN per turn"
        );
        let train_attempt = parsed.train.first().copied().map(|talents| {
            let index = train.record_attempt(workers_before);
            let conditions = train_failure_conditions(&game, &ours, &theirs, 1, talents);
            (index, conditions)
        });
        let landed_chops = successful_opponent_chops(&game, &ours, &theirs);
        step(&mut game, &ours, &theirs);
        let workers_after = game.units.iter().filter(|unit| unit.player == 1).count();
        if let Some((before, actions)) = pending_before {
            let completed = workers_after > workers_before;
            let after = (!completed).then(|| worker_three_post_stock_deficit(&game, 1));
            pending_bill.record(before, after, actions);
        }
        if let Some((index, conditions)) = train_attempt {
            train.record_result(index, workers_after > workers_before, conditions);
        }
        events.trains += workers_after.saturating_sub(workers_before) as i32;
        for (cell, kind) in plant_attempts {
            if game
                .plants
                .iter()
                .any(|plant| plant.pos() == cell && plant.plant_type == kind)
            {
                events.plants += 1;
                if let Some(resource) = FRUIT_TYPES.iter().position(|name| *name == kind) {
                    events.plants_by_fruit[resource] += 1;
                }
            }
        }
        for id in parsed.harvest {
            let Some(before) = opponent_units_before.get(&id) else {
                continue;
            };
            let Some(after) = game.units.iter().find(|unit| unit.id == id) else {
                continue;
            };
            for resource in 0..4 {
                let harvested = (after.carry[resource] - before[resource]).max(0);
                events.harvested_fruit += harvested;
                events.harvested_by_fruit[resource] += harvested;
            }
        }
        for id in parsed.drop {
            let Some(before) = opponent_units_before.get(&id) else {
                continue;
            };
            let Some(after) = game.units.iter().find(|unit| unit.id == id) else {
                continue;
            };
            events.dropped_items += (0..=WOOD)
                .map(|index| (before[index] - after.carry[index]).max(0))
                .sum::<i32>();
        }
        events.chops += landed_chops as i32;
        let resolved_turn = game.turn - 1;
        if resolved_turn == 50 {
            turn50 = Some(snapshot(&game, events));
        }
        if resolved_turn == 100 {
            turn100 = Some(snapshot(&game, events));
        }
        if has_stalled(&game, &mut turns_until_end) {
            break;
        }
    }
    let final_state = snapshot(&game, events);
    let stock_flow = stock_flow_telemetry(&game, 1, definition, events);
    AuditRow {
        game_id,
        model: model_index,
        first_commands: first_commands.unwrap_or_else(|| "-".to_string()),
        terminal_turn: game.turn - 1,
        third_worker_turn: third_worker_turn.max(0),
        switch_turn,
        switch_score,
        train,
        stock_flow,
        pending_bill,
        turn50: turn50.or(Some(final_state)),
        turn100: turn100.or(Some(final_state)),
        final_state,
    }
}

fn write_train_telemetry(writer: &mut impl Write, telemetry: TrainTelemetry) {
    for index in 0..3 {
        write!(
            writer,
            "\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
            telemetry.attempts[index],
            telemetry.successes[index],
            telemetry.fail_shack_only[index],
            telemetry.fail_budget_only[index],
            telemetry.fail_both[index],
            telemetry.fail_other[index],
            telemetry.failed_currency_picks[index],
            telemetry.fail_with_multiple_currency_picks[index],
            telemetry.fail_with_oversubscribed_resource[index],
        )
        .expect("write TRAIN telemetry");
    }
}

fn write_stock_flow(writer: &mut impl Write, telemetry: StockFlowTelemetry) {
    write!(writer, "\t{}", telemetry.next_train_target).expect("write next TRAIN target");
    for values in [
        telemetry.next_cost,
        telemetry.inventory,
        telemetry.carry,
        telemetry.standing,
        telemetry.ripe,
        telemetry.plants,
        telemetry.harvested,
    ] {
        for value in values {
            write!(writer, "\t{value}").expect("write stock-flow telemetry");
        }
    }
}

fn write_pending_bill(writer: &mut impl Write, telemetry: PendingBillTelemetry) {
    write!(writer, "\t{}\t{}", telemetry.turns, telemetry.worker_turns)
        .expect("write pending-bill duration");
    for value in telemetry.actions {
        write!(writer, "\t{value}").expect("write pending-bill action");
    }
    for value in telemetry.completion_actions {
        write!(writer, "\t{value}").expect("write pending-bill completion action");
    }
    for value in [
        telemetry.progress_turns,
        telemetry.equal_turns,
        telemetry.regress_turns,
        telemetry.reduced_units,
        telemetry.increased_units,
    ] {
        write!(writer, "\t{value}").expect("write pending-bill progress");
    }
    for class in 0..PENDING_ACTIONS.len() {
        for value in [
            telemetry.class_turns[class],
            telemetry.class_progress_turns[class],
            telemetry.class_regress_turns[class],
        ] {
            write!(writer, "\t{value}").expect("write pending-bill class progress");
        }
    }
    for values in [
        telemetry.initial_deficit,
        telemetry.minimum_deficit,
        telemetry.last_deficit,
    ] {
        for value in values {
            write!(writer, "\t{value}").expect("write pending-bill deficit vector");
        }
    }
}

fn write_snapshot(writer: &mut impl Write, value: Option<Snapshot>) {
    let value = value.unwrap_or(Snapshot {
        score: -1,
        fruit: -1,
        wood: -1,
        workers: -1,
        plants: -1,
        harvested_fruit: -1,
        chops: -1,
        dropped_items: -1,
    });
    write!(
        writer,
        "\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
        value.score,
        value.fruit,
        value.wood,
        value.workers,
        value.plants,
        value.harvested_fruit,
        value.chops,
        value.dropped_items
    )
    .expect("write snapshot");
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    let input = args.get(1).expect("map dataset path");
    let output = args
        .get(2)
        .cloned()
        .unwrap_or_else(|| "field-continuation-local.tsv".to_string());
    let threads = args
        .get(3)
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or(20)
        .max(1);
    let definitions = Arc::new(
        match args.get(4).map(String::as_str).unwrap_or("baseline") {
            "baseline" => baseline_catalog(),
            "economy" => economy_catalog(),
            "structural" => structural_catalog(),
            "legend_proxy" => legend_proxy_catalog(),
            "legend_proxy_v2" => legend_proxy_v2_catalog(),
            "legend_proxy_v3" => legend_proxy_v3_catalog(),
            "legend_proxy_v4" => legend_proxy_v4_catalog(),
            "legend_proxy_v5" => legend_proxy_v5_catalog(),
            "legend_proxy_v6" => legend_proxy_v6_catalog(),
            "legend_proxy_v7" => legend_proxy_v7_catalog(),
            "legend_proxy_v8" => legend_proxy_v8_catalog(),
            "phase_switch" => phase_switch_catalog(),
            "workforce_switch" => workforce_switch_catalog(),
            value => panic!(
                "unknown model catalog {value:?}; expected baseline, economy, structural, legend_proxy, legend_proxy_v2, legend_proxy_v3, legend_proxy_v4, legend_proxy_v5, legend_proxy_v6, legend_proxy_v7, legend_proxy_v8, phase_switch, or workforce_switch"
            ),
        },
    );
    let maps = Arc::new(read_dataset(input));
    assert_eq!(maps.len(), 160, "frozen Phase 21 map count");
    let tasks: Vec<_> = (0..maps.len())
        .flat_map(|map_index| {
            (0..definitions.len()).map(move |model_index| (map_index, model_index))
        })
        .collect();
    let tasks = Arc::new(tasks);
    let next = Arc::new(AtomicUsize::new(0));
    let mut rows = std::thread::scope(|scope| {
        let handles: Vec<_> = (0..threads)
            .map(|_| {
                let maps = Arc::clone(&maps);
                let definitions = Arc::clone(&definitions);
                let tasks = Arc::clone(&tasks);
                let next = Arc::clone(&next);
                scope.spawn(move || {
                    let mut local = Vec::new();
                    loop {
                        let index = next.fetch_add(1, Ordering::Relaxed);
                        if index >= tasks.len() {
                            break;
                        }
                        let (map_index, model_index) = tasks[index];
                        let (game_id, initial) = &maps[map_index];
                        local.push(play(
                            *game_id,
                            initial,
                            model_index,
                            &definitions[model_index],
                        ));
                    }
                    local
                })
            })
            .collect();
        handles
            .into_iter()
            .flat_map(|handle| handle.join().expect("field-continuation worker"))
            .collect::<Vec<_>>()
    });
    rows.sort_by_key(|row| (row.game_id, row.model));
    let mut writer = std::io::BufWriter::new(File::create(&output).expect("create output"));
    write!(
        writer,
        "game_id\tmodel\tfirst_commands\tterminal_turn\tthird_worker_turn\tswitch_turn\tswitch_score"
    )
    .expect("write header");
    for target in 2..=4 {
        for field in [
            "attempts",
            "successes",
            "fail_shack_only",
            "fail_budget_only",
            "fail_both",
            "fail_other",
            "failed_currency_picks",
            "fail_with_multiple_currency_picks",
            "fail_with_oversubscribed_resource",
        ] {
            write!(writer, "\ttrain{target}_{field}").expect("write TRAIN telemetry header");
        }
    }
    write!(writer, "\tnext_train_target").expect("write stock-flow target header");
    for prefix in ["next_cost", "final_inventory", "final_carry"] {
        for resource in ["plum", "lemon", "apple", "iron"] {
            write!(writer, "\t{prefix}_{resource}").expect("write stock-flow header");
        }
    }
    for prefix in [
        "final_standing",
        "final_ripe",
        "successful_plants",
        "harvested",
    ] {
        for resource in ["plum", "lemon", "apple", "banana"] {
            write!(writer, "\t{prefix}_{resource}").expect("write stock-flow header");
        }
    }
    write!(writer, "\tpending3_turns\tpending3_worker_turns")
        .expect("write pending-bill duration header");
    for action in PENDING_ACTIONS {
        write!(writer, "\tpending3_action_{action}").expect("write pending action header");
    }
    for action in PENDING_ACTIONS {
        write!(writer, "\tpending3_completion_action_{action}")
            .expect("write pending completion-action header");
    }
    for field in [
        "progress_turns",
        "equal_turns",
        "regress_turns",
        "reduced_units",
        "increased_units",
    ] {
        write!(writer, "\tpending3_{field}").expect("write pending progress header");
    }
    for action in PENDING_ACTIONS {
        for field in ["observed_turns", "progress_turns", "regress_turns"] {
            write!(writer, "\tpending3_{action}_{field}")
                .expect("write pending class-progress header");
        }
    }
    for stage in ["initial", "minimum", "last"] {
        for resource in ["plum", "lemon", "apple", "iron"] {
            write!(writer, "\tpending3_{stage}_deficit_{resource}")
                .expect("write pending deficit-vector header");
        }
    }
    for prefix in ["t50", "t100", "final"] {
        for field in [
            "score",
            "fruit",
            "wood",
            "workers",
            "plants",
            "harvested_fruit",
            "chops",
            "dropped_items",
        ] {
            write!(writer, "\t{prefix}_{field}").expect("write header field");
        }
    }
    writeln!(writer).expect("write header newline");
    for row in rows {
        let command = row.first_commands.replace(['\t', '\n', '\r'], " ");
        write!(
            writer,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}",
            row.game_id,
            definitions[row.model].label,
            command,
            row.terminal_turn,
            row.third_worker_turn,
            row.switch_turn,
            row.switch_score
        )
        .expect("write row prefix");
        write_train_telemetry(&mut writer, row.train);
        write_stock_flow(&mut writer, row.stock_flow);
        write_pending_bill(&mut writer, row.pending_bill);
        write_snapshot(&mut writer, row.turn50);
        write_snapshot(&mut writer, row.turn100);
        write_snapshot(&mut writer, Some(row.final_state));
        writeln!(writer).expect("write row newline");
    }
    eprintln!(
        "saved {} exact-map model trajectories to {}",
        tasks.len(),
        output
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn frozen_model_catalog_is_unique() {
        let catalog = baseline_catalog();
        let names: BTreeSet<_> = catalog.iter().map(|model| &model.label).collect();
        assert_eq!(catalog.len(), 8);
        assert_eq!(names.len(), 8);
    }

    #[test]
    fn frozen_economy_catalog_has_31_unique_labels_and_configs() {
        let catalog = economy_catalog();
        let labels: BTreeSet<_> = catalog.iter().map(|model| &model.label).collect();
        let configs: std::collections::HashSet<_> = catalog
            .iter()
            .map(|model| match model.kind {
                ModelKind::Economy(config) => config,
                ModelKind::Baseline(_)
                | ModelKind::Structural(_)
                | ModelKind::LegendProxy(_)
                | ModelKind::LegendProxyV2(_)
                | ModelKind::LegendProxyV3(_)
                | ModelKind::LegendProxyV4(_)
                | ModelKind::LegendProxyV5(_)
                | ModelKind::LegendProxyV6(_)
                | ModelKind::LegendProxyV7(_)
                | ModelKind::LegendProxyV8(_)
                | ModelKind::PhaseComponent(_)
                | ModelKind::PhaseSwitch(_)
                | ModelKind::WorkforceSwitch(_) => {
                    unreachable!()
                }
            })
            .collect();
        assert_eq!(catalog.len(), 31);
        assert_eq!(labels.len(), 31);
        assert_eq!(configs.len(), 31);
    }

    #[test]
    fn frozen_structural_catalog_has_11_unique_labels() {
        let catalog = structural_catalog();
        let labels: BTreeSet<_> = catalog.iter().map(|model| &model.label).collect();
        assert_eq!(catalog.len(), 11);
        assert_eq!(labels.len(), 11);
    }

    #[test]
    fn frozen_legend_proxy_catalog_has_8_unique_labels_and_configs() {
        let catalog = legend_proxy_catalog();
        let labels: BTreeSet<_> = catalog.iter().map(|model| &model.label).collect();
        let configs: std::collections::HashSet<_> = catalog
            .iter()
            .map(|model| match model.kind {
                ModelKind::LegendProxy(config) => config,
                _ => unreachable!(),
            })
            .collect();
        assert_eq!(catalog.len(), 8);
        assert_eq!(labels.len(), 8);
        assert_eq!(configs.len(), 8);
    }

    #[test]
    fn frozen_legend_proxy_v2_catalog_has_8_unique_labels_and_configs() {
        let catalog = legend_proxy_v2_catalog();
        let labels: BTreeSet<_> = catalog.iter().map(|model| &model.label).collect();
        let configs: std::collections::HashSet<_> = catalog
            .iter()
            .map(|model| match model.kind {
                ModelKind::LegendProxyV2(config) => config,
                _ => unreachable!(),
            })
            .collect();
        assert_eq!(catalog.len(), 8);
        assert_eq!(labels.len(), 8);
        assert_eq!(configs.len(), 8);
    }

    #[test]
    fn frozen_legend_proxy_v3_catalog_has_8_unique_labels_and_configs() {
        let catalog = legend_proxy_v3_catalog();
        let labels: BTreeSet<_> = catalog.iter().map(|model| &model.label).collect();
        let configs: std::collections::HashSet<_> = catalog
            .iter()
            .map(|model| match model.kind {
                ModelKind::LegendProxyV3(config) => config,
                _ => unreachable!(),
            })
            .collect();
        assert_eq!(catalog.len(), 8);
        assert_eq!(labels.len(), 8);
        assert_eq!(configs.len(), 8);
        assert!(configs.iter().all(|config| {
            matches!(config.first_spec, (2, 2, 2, 1) | (2, 2, 1, 1))
                && matches!(config.max_workers, 3 | 4)
                && matches!(config.post_producers, 1 | 2)
        }));
    }

    #[test]
    fn frozen_legend_proxy_v4_catalog_has_8_unique_labels_and_configs() {
        let catalog = legend_proxy_v4_catalog();
        let labels: BTreeSet<_> = catalog.iter().map(|model| &model.label).collect();
        let configs: std::collections::HashSet<_> = catalog
            .iter()
            .map(|model| match model.kind {
                ModelKind::LegendProxyV4(config) => config,
                _ => unreachable!(),
            })
            .collect();
        assert_eq!(catalog.len(), 8);
        assert_eq!(labels.len(), 8);
        assert_eq!(configs.len(), 8);
    }

    #[test]
    fn frozen_legend_proxy_v5_catalog_has_8_unique_labels_and_configs() {
        let catalog = legend_proxy_v5_catalog();
        let labels: BTreeSet<_> = catalog.iter().map(|model| &model.label).collect();
        let configs: std::collections::HashSet<_> = catalog
            .iter()
            .map(|model| match model.kind {
                ModelKind::LegendProxyV5(config) => config,
                _ => unreachable!(),
            })
            .collect();
        assert_eq!(catalog.len(), 8);
        assert_eq!(labels.len(), 8);
        assert_eq!(configs.len(), 8);
    }

    #[test]
    fn frozen_legend_proxy_v6_catalog_has_8_unique_labels_and_configs() {
        let catalog = legend_proxy_v6_catalog();
        let labels: BTreeSet<_> = catalog.iter().map(|model| &model.label).collect();
        let configs: std::collections::HashSet<_> = catalog
            .iter()
            .map(|model| match model.kind {
                ModelKind::LegendProxyV6(config) => config,
                _ => unreachable!(),
            })
            .collect();
        assert_eq!(catalog.len(), 8);
        assert_eq!(labels.len(), 8);
        assert_eq!(configs.len(), 8);
    }

    #[test]
    fn frozen_legend_proxy_v7_catalog_has_8_unique_labels_and_configs() {
        let catalog = legend_proxy_v7_catalog();
        let labels: BTreeSet<_> = catalog.iter().map(|model| &model.label).collect();
        let configs: std::collections::HashSet<_> = catalog
            .iter()
            .map(|model| match model.kind {
                ModelKind::LegendProxyV7(config) => config,
                _ => unreachable!(),
            })
            .collect();
        assert_eq!(catalog.len(), 8);
        assert_eq!(labels.len(), 8);
        assert_eq!(configs.len(), 8);
    }

    #[test]
    fn frozen_legend_proxy_v8_catalog_has_8_unique_labels_and_configs() {
        let catalog = legend_proxy_v8_catalog();
        let labels: BTreeSet<_> = catalog.iter().map(|model| &model.label).collect();
        let configs: std::collections::HashSet<_> = catalog
            .iter()
            .map(|model| match model.kind {
                ModelKind::LegendProxyV8(config) => config,
                _ => unreachable!(),
            })
            .collect();
        assert_eq!(catalog.len(), 8);
        assert_eq!(labels.len(), 8);
        assert_eq!(configs.len(), 8);
    }

    #[test]
    fn frozen_phase_switch_catalog_has_120_unique_definitions() {
        let catalog = phase_switch_catalog();
        let labels: BTreeSet<_> = catalog.iter().map(|model| &model.label).collect();
        let switches: std::collections::HashSet<_> = catalog
            .iter()
            .filter_map(|model| match model.kind {
                ModelKind::PhaseSwitch(config) => Some(config),
                _ => None,
            })
            .collect();
        assert_eq!(catalog.len(), 120);
        assert_eq!(labels.len(), 120);
        assert_eq!(switches.len(), 112);
        assert!(switches
            .iter()
            .all(|config| { config.early != config.late && matches!(config.cut, 100 | 150) }));
    }

    #[test]
    fn frozen_workforce_switch_catalog_has_64_unique_definitions() {
        let catalog = workforce_switch_catalog();
        let labels: BTreeSet<_> = catalog.iter().map(|model| &model.label).collect();
        let switches: std::collections::HashSet<_> = catalog
            .iter()
            .filter_map(|model| match model.kind {
                ModelKind::WorkforceSwitch(config) => Some(config),
                _ => None,
            })
            .collect();
        assert_eq!(catalog.len(), 64);
        assert_eq!(labels.len(), 64);
        assert_eq!(switches.len(), 56);
        assert!(switches.iter().all(|config| config.early != config.late));
    }

    #[test]
    fn candidate_chop_that_fells_first_suppresses_opponent_success() {
        let mut game = GameState {
            width: 3,
            height: 1,
            walkable: std::collections::HashSet::from([(0, 0), (1, 0), (2, 0)]),
            shacks: [(0, 0), (2, 0)],
            inventories: [[0; 6]; 2],
            units: Vec::new(),
            plants: Vec::new(),
            scores: [0; 2],
            turn: 1,
            next_id: 2,
            iron: std::collections::HashSet::new(),
            water: std::collections::HashSet::new(),
        };
        game.units.push(EngineUnit {
            id: 0,
            player: 0,
            x: 1,
            y: 0,
            ms: 1,
            cc: 1,
            hp: 1,
            chop: 2,
            carry: [0; 6],
        });
        game.units.push(EngineUnit {
            id: 1,
            player: 1,
            x: 1,
            y: 0,
            ms: 1,
            cc: 1,
            hp: 1,
            chop: 1,
            carry: [0; 6],
        });
        game.plants.push(EnginePlant {
            plant_type: "BANANA".to_string(),
            x: 1,
            y: 0,
            size: 1,
            health: 2,
            fruits: 0,
            cooldown: 1,
        });
        assert_eq!(
            successful_opponent_chops(&game, &["CHOP 0".into()], &["CHOP 1".into()]),
            0
        );
        assert_eq!(successful_opponent_chops(&game, &[], &["CHOP 1".into()]), 1);
    }

    #[test]
    fn train_diagnostic_separates_shack_and_post_pick_budget_conditions() {
        let mut game = GameState {
            width: 3,
            height: 1,
            walkable: std::collections::HashSet::from([(0, 0), (1, 0), (2, 0)]),
            shacks: [(0, 0), (2, 0)],
            inventories: [[0; 6]; 2],
            units: vec![EngineUnit {
                id: 1,
                player: 1,
                x: 2,
                y: 0,
                ms: 1,
                cc: 2,
                hp: 1,
                chop: 1,
                carry: [0; 6],
            }],
            plants: Vec::new(),
            scores: [0; 2],
            turn: 2,
            next_id: 2,
            iron: std::collections::HashSet::new(),
            water: std::collections::HashSet::new(),
        };
        let spec = (2, 3, 1, 2);
        game.inventories[1] = training_cost(1, spec);
        assert_eq!(
            train_failure_conditions(
                &game,
                &[],
                &["PICK 1 PLUM".into(), "TRAIN 2 3 1 2".into()],
                1,
                spec,
            ),
            TrainFailureConditions {
                shack_occupied: true,
                budget_short: true,
                currency_picks: 1,
                multiple_currency_picks: false,
                oversubscribed_resource: true,
            }
        );
        assert_eq!(
            train_failure_conditions(
                &game,
                &[],
                &["MOVE 1 1 0".into(), "TRAIN 2 3 1 2".into()],
                1,
                spec,
            ),
            TrainFailureConditions {
                shack_occupied: false,
                budget_short: false,
                currency_picks: 0,
                multiple_currency_picks: false,
                oversubscribed_resource: false,
            }
        );

        game.units.push(EngineUnit {
            id: 2,
            player: 1,
            x: 1,
            y: 0,
            ms: 1,
            cc: 2,
            hp: 1,
            chop: 1,
            carry: [0; 6],
        });
        game.inventories[1] = training_cost(2, spec);
        game.inventories[1][LEMON] += 1;
        assert_eq!(
            train_failure_conditions(
                &game,
                &[],
                &[
                    "PICK 1 LEMON".into(),
                    "PICK 2 LEMON".into(),
                    "TRAIN 2 3 1 2".into(),
                ],
                1,
                spec,
            ),
            TrainFailureConditions {
                shack_occupied: true,
                budget_short: true,
                currency_picks: 2,
                multiple_currency_picks: true,
                oversubscribed_resource: true,
            }
        );
    }

    #[test]
    fn pending_action_classes_are_mutually_exclusive_and_include_idle_workers() {
        let parsed = parse_cmds(&[
            "MOVE 1 0 0".into(),
            "HARVEST 2".into(),
            "TRAIN 2 3 1 2".into(),
        ]);
        let counts = worker_action_counts(&parsed, &BTreeSet::from([1, 2, 3]));
        assert_eq!(counts, [1, 0, 0, 0, 1, 0, 0, 1]);
        assert_eq!(counts.iter().sum::<i32>(), 3);
    }

    #[test]
    fn pending_deficit_uses_deposited_carry_ripe_and_effective_iron() {
        let game = GameState {
            width: 2,
            height: 1,
            walkable: std::collections::HashSet::from([(0, 0), (1, 0)]),
            shacks: [(0, 0), (1, 0)],
            inventories: [[0; 6], [1, 2, 3, 0, 1, 0]],
            units: vec![EngineUnit {
                id: 1,
                player: 1,
                x: 0,
                y: 0,
                ms: 1,
                cc: 3,
                hp: 1,
                chop: 1,
                carry: [1, 2, 0, 0, 1, 0],
            }],
            plants: vec![EnginePlant {
                plant_type: "LEMON".into(),
                x: 0,
                y: 0,
                size: 1,
                health: 2,
                fruits: 3,
                cooldown: 0,
            }],
            scores: [0; 2],
            turn: 1,
            next_id: 2,
            iron: std::collections::HashSet::from([(0, 0)]),
            water: std::collections::HashSet::new(),
        };
        assert_eq!(worker_three_post_stock_deficit(&game, 1), [4, 4, 0, 4]);
    }

    #[test]
    fn pending_progress_excludes_completion_but_retains_its_labor() {
        let mut telemetry = PendingBillTelemetry::default();
        telemetry.record([4, 4, 0, 4], Some([3, 4, 0, 4]), [1, 0, 0, 0, 0, 0, 0, 1]);
        telemetry.record([3, 4, 0, 4], None, [0, 0, 0, 1, 0, 0, 0, 1]);
        assert_eq!(telemetry.turns, 2);
        assert_eq!(telemetry.worker_turns, 4);
        assert_eq!(telemetry.progress_turns, 1);
        assert_eq!(telemetry.equal_turns, 0);
        assert_eq!(telemetry.regress_turns, 0);
        assert_eq!(telemetry.reduced_units, 1);
        assert_eq!(telemetry.class_turns[3], 1);
        assert_eq!(telemetry.class_progress_turns[3], 0);
        assert_eq!(telemetry.class_progress_turns[0], 1);
        assert_eq!(telemetry.completion_actions[3], 1);
        assert_eq!(telemetry.completion_actions[7], 1);
        assert_eq!(telemetry.last_deficit, [3, 4, 0, 4]);
    }

    #[test]
    fn stock_flow_uses_effective_bill_and_species_vectors() {
        let game = GameState {
            width: 2,
            height: 1,
            walkable: std::collections::HashSet::from([(0, 0), (1, 0)]),
            shacks: [(0, 0), (1, 0)],
            inventories: [[0; 6], [7, 8, 9, 0, 11, 0]],
            units: vec![EngineUnit {
                id: 1,
                player: 1,
                x: 0,
                y: 0,
                ms: 1,
                cc: 2,
                hp: 1,
                chop: 1,
                carry: [1, 2, 0, 0, 3, 0],
            }],
            plants: vec![EnginePlant {
                plant_type: "LEMON".into(),
                x: 0,
                y: 0,
                size: 1,
                health: 2,
                fruits: 3,
                cooldown: 0,
            }],
            scores: [0; 2],
            turn: 300,
            next_id: 2,
            iron: std::collections::HashSet::new(),
            water: std::collections::HashSet::new(),
        };
        let definition = ModelDefinition {
            label: "test".into(),
            kind: ModelKind::LegendProxyV5(LegendFieldProxyV3Config {
                first_spec: (2, 2, 2, 1),
                max_workers: 3,
                post_producers: 1,
            }),
        };
        let telemetry = stock_flow_telemetry(
            &game,
            1,
            &definition,
            Events {
                plants_by_fruit: [1, 2, 3, 4],
                harvested_by_fruit: [5, 6, 7, 8],
                ..Events::default()
            },
        );
        assert_eq!(telemetry.next_train_target, 2);
        assert_eq!(telemetry.next_cost, [5, 5, 5, 0]);
        assert_eq!(telemetry.inventory, [7, 8, 9, 11]);
        assert_eq!(telemetry.carry, [1, 2, 0, 3]);
        assert_eq!(telemetry.standing, [0, 1, 0, 0]);
        assert_eq!(telemetry.ripe, [0, 3, 0, 0]);
        assert_eq!(telemetry.plants, [1, 2, 3, 4]);
        assert_eq!(telemetry.harvested, [5, 6, 7, 8]);
    }
}
