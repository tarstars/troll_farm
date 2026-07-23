#!/usr/bin/env python3
"""Build the exact CompactGold >30 rollout-gated standalone candidate."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.compact_rust_source import compact  # noqa: E402
from cgauto.make_live_variant import replace_once  # noqa: E402
from cgauto.slim_live_source import _remove_item, slim  # noqa: E402


DEFAULT_PARENT = (
    REPO
    / "cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage.min.rs"
)
DEFAULT_ENGINE = REPO / "rust/src/game/engine.rs"
DEFAULT_STATE = REPO / "rust/src/game/state.rs"
DEFAULT_MODEL = REPO / "rust/src/strategies/compact_gold.rs"


def make_selectable_parent(source: str) -> str:
    """Add an inactive-by-default exact opening option to the promoted parent."""

    result = replace_once(
        source,
        "external_protected_tree:Option<Cell>,}",
        "external_protected_tree:Option<Cell>,first_worker_max_bank_hp0:bool,}",
        "selectable Yamo field",
    )
    result = replace_once(
        result,
        "external_protected_tree:None,}}",
        "external_protected_tree:None,first_worker_max_bank_hp0:false,}}",
        "selectable Yamo default",
    )
    normal_desired = (
        "let desired=self.desired_second.map(|objective|objective.stats)"
        ".unwrap_or_else(Self::fallback_second_troll);"
    )
    selectable_desired = (
        "let own_count=view.units.iter().filter(|unit|unit.player==0).count();"
        "let max_level=|item:usize|{let available=(view.inventories[0][item]-"
        "own_count as i32).max(0);let mut level=0;while level<3&&(level+1)*(level+1)"
        "<=available{level+=1;}level.max(1)};let desired=if self."
        "first_worker_max_bank_hp0&&own_count==1{Stats{movement_speed:max_level(PLUM),"
        "carry_capacity:max_level(LEMON),harvest_power:0,chop_power:max_level(IRON)}}"
        "else{self.desired_second.map(|objective|objective.stats).unwrap_or_else("
        "Self::fallback_second_troll)};"
    )
    result = replace_once(
        result, normal_desired, selectable_desired, "selectable first worker"
    )
    constructor = (
        "pub fn new()->Self{Self::with_policy(YamoBot::"
        "tuned_carry_regeneration_transit_idle_harvest(),8,false,11,1,)}"
    )
    return replace_once(
        result,
        constructor,
        constructor
        + "pub fn max_bank_first_hp0()->Self{let mut bot=Self::new();"
        "bot.inner.first_worker_max_bank_hp0=true;bot}",
        "selectable option constructor",
    )


def deployment_state(source: str) -> str:
    marker = "/// Parse an ASCII grid into a GameState."
    if source.count(marker) != 1:
        raise ValueError("could not isolate deployment state structs")
    return source.split(marker, 1)[0]


def deployment_model(source: str) -> str:
    result = replace_once(
        source,
        "use crate::game::engine::{training_cost, BANANA, IRON};",
        "use super::engine::{training_cost, BANANA, IRON};",
        "CompactGold engine import",
    )
    return replace_once(
        result,
        "use crate::game::state::{Cell, GameState, Plant, Unit};",
        "use super::state::{Cell, GameState, Plant, Unit};",
        "CompactGold state import",
    )


def deployment_engine(source: str) -> str:
    """Remove the public wrapper unused by the exact combined step function."""

    return _remove_item(source, "pub fn apply_chop(")


def rollout_module(state_source: str, engine_source: str, model_source: str) -> str:
    state = deployment_state(state_source)
    model = deployment_model(model_source)
    engine = deployment_engine(engine_source)
    return f"""
mod rollout {{
    pub mod state {{ {state} }}
    pub mod engine {{ {engine} }}
    pub trait Strategy {{
        fn name(&self) -> &str;
        fn decide(&self, game: &state::GameState, player: usize) -> Vec<String>;
    }}
    pub mod compact_gold {{ {model} }}

    use crate::bot::moisan::SecureOrchardBot;
    use crate::bot::Bot;
    use crate::game::types::{{
        GameState as YamoState, Plant as YamoPlant, PlantKind, Stats, Unit as YamoUnit,
    }};
    use self::compact_gold::CompactGold;
    use self::state::{{GameState, Plant, Unit}};
    use std::collections::BTreeSet;

    fn from_yamo(view: &YamoState) -> GameState {{
        GameState {{
            width: view.width,
            height: view.height,
            walkable: view.walkable.iter().copied().collect(),
            shacks: view.shacks,
            inventories: view.inventories,
            units: view.units.iter().map(|unit| Unit {{
                id: unit.id,
                player: unit.player as i32,
                x: unit.cell.0,
                y: unit.cell.1,
                ms: unit.stats.movement_speed,
                cc: unit.stats.carry_capacity,
                hp: unit.stats.harvest_power,
                chop: unit.stats.chop_power,
                carry: unit.carry,
            }}).collect(),
            plants: view.plants.iter().map(|plant| Plant {{
                plant_type: plant.kind.as_str().to_string(),
                x: plant.cell.0,
                y: plant.cell.1,
                size: plant.size,
                health: plant.health,
                fruits: plant.fruits,
                cooldown: plant.cooldown,
            }}).collect(),
            scores: view.scores,
            turn: view.turn,
            next_id: view.next_id,
            iron: view.iron.iter().copied().collect(),
            water: view.water.iter().copied().collect(),
        }}
    }}

    fn yamo_view(game: &GameState) -> YamoState {{
        YamoState {{
            width: game.width,
            height: game.height,
            walkable: game.walkable.iter().copied().collect::<BTreeSet<_>>(),
            shacks: game.shacks,
            inventories: game.inventories,
            units: game.units.iter().map(|unit| YamoUnit {{
                id: unit.id,
                player: unit.player as usize,
                cell: unit.pos(),
                stats: Stats {{
                    movement_speed: unit.ms,
                    carry_capacity: unit.cc,
                    harvest_power: unit.hp,
                    chop_power: unit.chop,
                }},
                carry: unit.carry,
            }}).collect(),
            plants: game.plants.iter().map(|plant| YamoPlant {{
                kind: PlantKind::parse(&plant.plant_type).expect("known plant type"),
                cell: plant.pos(),
                size: plant.size,
                health: plant.health,
                fruits: plant.fruits,
                cooldown: plant.cooldown,
            }}).collect(),
            scores: game.scores,
            turn: game.turn,
            next_id: game.next_id,
            iron: game.iron.iter().copied().collect::<BTreeSet<_>>(),
            water: game.water.iter().copied().collect::<BTreeSet<_>>(),
        }}
    }}

    fn simulate(initial: &GameState, option: bool, started: &std::time::Instant) -> Option<i32> {{
        let mut game = initial.clone();
        let mut ours = if option {{
            SecureOrchardBot::max_bank_first_hp0()
        }} else {{
            SecureOrchardBot::new()
        }};
        let theirs = CompactGold::new();
        let mut turns_until_end = 0;
        while game.turn <= 300 {{
            if started.elapsed().as_millis() >= 700 {{
                return None;
            }}
            let our_commands = ours.commands(&yamo_view(&game));
            let their_commands = theirs.decide(&game, 1);
            engine::step(&mut game, &our_commands, &their_commands);
            if engine::has_stalled(&game, &mut turns_until_end) {{
                break;
            }}
        }}
        Some(game.scores[0] - game.scores[1])
    }}

    pub fn select(view: &YamoState) -> bool {{
        let initial = from_yamo(view);
        let started = std::time::Instant::now();
        let (control, option) = std::thread::scope(|scope| {{
            let control = scope.spawn(|| simulate(&initial, false, &started));
            let option = scope.spawn(|| simulate(&initial, true, &started));
            (control.join(), option.join())
        }});
        matches!((control, option), (Ok(Some(control)), Ok(Some(option))) if option - control > 30)
    }}
}}
"""


def live_main() -> str:
    return (
        "fn main(){let stdin=io::stdin();let stdout=io::stdout();let mut reader="
        "io::BufReader::new(stdin.lock());let mut out=io::BufWriter::new(stdout.lock());"
        "let Some(map)=read_static_map(&mut reader)else{return;};let mut bot=None;let mut "
        "turn=1;while let Some(view)=read_turn(&mut reader,&map,turn){if bot.is_none(){bot="
        "Some(if rollout::select(&view){SecureOrchardBot::max_bank_first_hp0()}else{"
        "SecureOrchardBot::new()});}let commands=bot.as_mut().unwrap().commands(&view);"
        "writeln!(out,\"{}\",commands.join(\";\")).expect(\"write command line\");out.flush()"
        ".expect(\"flush command line\");turn+=1;}}"
    )


def compose(
    parent_source: str,
    state_source: str,
    engine_source: str,
    model_source: str,
) -> str:
    parent = slim(make_selectable_parent(parent_source)).rstrip()
    module = rollout_module(state_source, engine_source, model_source)
    parent = replace_once(
        parent,
        "use std::io::{self,Write};",
        module + "use std::io::{self,Write};",
        "rollout module insertion",
    )
    main_start = parent.rfind("fn main(){")
    if main_start < 0 or not parent.endswith("}"):
        raise ValueError("could not isolate standalone main")
    return compact(parent[:main_start] + live_main())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--parent", type=Path, default=DEFAULT_PARENT)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--engine", type=Path, default=DEFAULT_ENGINE)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    args = parser.parse_args()
    result = compose(
        args.parent.read_text(),
        args.state.read_text(),
        args.engine.read_text(),
        args.model.read_text(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result)
    digest = hashlib.sha256(result.encode()).hexdigest()
    args.output.with_name(args.output.name + ".sha256").write_text(
        f"{digest}  {args.output.name}\n"
    )
    print(f"generated {len(result)} byte rollout candidate -> {args.output}")
    print(f"sha256 {digest}")


if __name__ == "__main__":
    main()
