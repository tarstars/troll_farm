#!/usr/bin/env python3
"""Generate the in-process Strategy wrapper around the readable champion.

The policy body is copied mechanically from the hash-pinned readable source.  The
only transformations are namespace qualification and removal of the standalone
stdin/stdout main.  The adapter below converts the research engine's GameState to
the exact player-relative standalone view.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from cgauto.compact_rust_source import compact  # noqa: E402


DEFAULT_SOURCE = (
    ROOT
    / "local_claude_1"
    / "denial-ablation"
    / "champion-denial-off-v6-instrument.rs"
)
AUTHORITATIVE_TARGET = (
    ROOT / "cgauto" / "submissions" / "candidate-champion-denial-off-v6-instrument.rs"
)
DEFAULT_OUTPUT = ROOT / "rust" / "src" / "strategies" / "champion_exact.rs"
SOURCE_SHA256 = "321723933c2a0cfb6bfcd62c57e0d25b6783ffb8ddcfea37c05b053e2e46cd4f"
TARGET_SHA256 = "0e92f8fa1e9097dd3df81989e222be8810f3cebdcd3efc950f84353f0bd1d57c"
MAIN_MARKER = "\nuse std::io::{self, Write};\n"


ADAPTER = r'''

use std::cell::RefCell;

use super::Strategy;
use crate::game::state::GameState;
use source::bot::moisan::YamoBot;
use source::bot::Bot as ChampionBot;
use source::game::types::{
    GameState as ChampionState, Plant as ChampionPlant, PlantKind, Stats as ChampionStats,
    Unit as ChampionUnit,
};

pub struct ChampionExact {
    bot: RefCell<YamoBot>,
}

impl ChampionExact {
    pub fn new() -> Self {
        Self {
            bot: RefCell::new(YamoBot::tuned_carry_regeneration_transit_idle_harvest()),
        }
    }
}

impl Default for ChampionExact {
    fn default() -> Self {
        Self::new()
    }
}

fn champion_view(game: &GameState, seat: usize) -> ChampionState {
    ChampionState {
        width: game.width,
        height: game.height,
        walkable: game.walkable.iter().copied().collect(),
        shacks: [game.shacks[seat], game.shacks[1 - seat]],
        inventories: [game.inventories[seat], game.inventories[1 - seat]],
        units: game
            .units
            .iter()
            .map(|unit| ChampionUnit {
                id: unit.id,
                player: usize::from(unit.player as usize != seat),
                cell: unit.pos(),
                stats: ChampionStats {
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
                Some(ChampionPlant {
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

impl Strategy for ChampionExact {
    fn name(&self) -> &str {
        "champion_exact"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        assert!(player < 2, "champion seat must be 0 or 1");
        let mut bot = self.bot.borrow_mut();
        if game.turn == 1 {
            *bot = YamoBot::tuned_carry_regeneration_transit_idle_harvest();
        }
        bot.commands(&champion_view(game, player))
    }
}
'''


def generated_text(source_path: Path, target_path: Path) -> str:
    raw = source_path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != SOURCE_SHA256:
        raise SystemExit(
            f"champion source hash drift: expected {SOURCE_SHA256}, got {digest}"
        )
    target_raw = target_path.read_bytes()
    target_digest = hashlib.sha256(target_raw).hexdigest()
    if target_digest != TARGET_SHA256:
        raise SystemExit(
            f"authoritative champion hash drift: expected {TARGET_SHA256}, "
            f"got {target_digest}"
        )
    text = raw.decode("utf-8")
    target_text = target_raw.decode("utf-8")
    if compact(text) != target_text.rstrip("\r\n"):
        raise SystemExit(
            "readable instrument arm is not token-identical to the authoritative champion"
        )
    if text.count(MAIN_MARKER) != 1:
        raise SystemExit("champion source must contain exactly one standalone-main marker")
    policy = text.split(MAIN_MARKER, 1)[0]
    expected_game_paths = policy.count("crate::game::")
    expected_bot_paths = policy.count("crate::bot::")
    if (expected_game_paths, expected_bot_paths) != (8, 0):
        raise SystemExit(
            "unexpected absolute paths before main: "
            f"crate::game={expected_game_paths}, crate::bot={expected_bot_paths}"
        )
    policy = "\n".join(line.rstrip() for line in policy.splitlines())
    policy = policy.replace("mod game {", "pub(crate) mod game {", 1)
    policy = policy.replace("mod bot {", "pub(crate) mod bot {", 1)
    policy = policy.replace(
        "crate::game::", "crate::strategies::champion_exact::source::game::"
    )
    if "crate::game::" in policy or "crate::bot::" in policy:
        raise SystemExit("unqualified standalone module path remains")
    header = f'''// @generated by codex_1/nn_bot/generate_champion_exact.py; do not edit.
// Authoritative target: cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs
// Authoritative SHA-256: {TARGET_SHA256}
// Token-identical readable arm: local_claude_1/denial-ablation/champion-denial-off-v6-instrument.rs
// Readable arm SHA-256: {SOURCE_SHA256}
#![allow(dead_code, unused_imports, unused_mut, unused_variables)]

pub(crate) mod source {{
'''
    return header + policy + "\n}\n" + ADAPTER.lstrip("\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--target", type=Path, default=AUTHORITATIVE_TARGET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = generated_text(args.source, args.target)
    if args.check:
        actual = args.output.read_text() if args.output.exists() else ""
        if actual != expected:
            raise SystemExit(f"generated wrapper drift: {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(expected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
