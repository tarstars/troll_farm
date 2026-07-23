#!/usr/bin/env python3
"""Build the cross-validated banana-5 stack/live portfolio as one Rust source."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


REPLACEMENTS = (
    (
        "use std::collections::{BTreeMap,BTreeSet};",
        "use std::collections::{BTreeMap,BTreeSet};use std::sync::atomic::{AtomicBool,Ordering};"
        "pub static PORTFOLIO_STACK:AtomicBool=AtomicBool::new(false);",
    ),
    (
        "if safe_regeneration&&carried==0&&view.turn>=100",
        "if PORTFOLIO_STACK.load(Ordering::Relaxed)&&safe_regeneration&&carried==0&&"
        "view.turn>=100",
    ),
    (
        "fn initialize(&mut self,view:&GameState){self.initialized=true;self.starter_id=",
        "fn initialize(&mut self,view:&GameState){self.initialized=true;if !PORTFOLIO_STACK.load("
        "Ordering::Relaxed){self.minimum_enemy_eta=12;self.require_idle_starter=false;self."
        "minimum_enemy_door_distance=14;self.minimum_worker_speed=2;}self.starter_id=",
    ),
    (
        "use crate::bot::moisan::SecureOrchardBot;",
        "use crate::bot::moisan::{SecureOrchardBot,PORTFOLIO_STACK};",
    ),
    (
        "while let Some(view)=read_turn(&mut reader,&map,turn){let commands=bot.commands(&view);",
        "while let Some(view)=read_turn(&mut reader,&map,turn){if turn==1{let banana_fruits="
        "view.plants.iter().filter(|plant|plant.kind==crate::game::PlantKind::Banana).map("
        "|plant|plant.fruits).sum::<i32>();PORTFOLIO_STACK.store(banana_fruits<=5,std::sync::"
        "atomic::Ordering::Relaxed);}let commands=bot.commands(&view);",
    ),
)


def make_portfolio(source: str) -> str:
    result = source
    for before, after in REPLACEMENTS:
        count = result.count(before)
        if count != 1:
            raise RuntimeError(f"expected one portfolio replacement site, found {count}: {before}")
        result = result.replace(before, after, 1)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="composed stack source")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    candidate = make_portfolio(args.source.read_text())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(candidate)
    digest = hashlib.sha256(candidate.encode()).hexdigest()
    args.output.with_name(args.output.name + ".sha256").write_text(
        f"{digest}  {args.output.name}\n"
    )
    print(f"generated banana-5 stack/live portfolio: {len(candidate)} bytes")
    print(f"sha256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
