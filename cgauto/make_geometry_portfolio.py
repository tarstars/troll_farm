#!/usr/bin/env python3
"""Build a banana-gated secure-orchard/live portfolio as one Rust source."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def make_geometry_portfolio(source: str, threshold: int = 5) -> str:
    replacements = (
        (
            "use std::collections::{BTreeMap,BTreeSet};",
            "use std::collections::{BTreeMap,BTreeSet};use std::sync::atomic::{AtomicBool,"
            "Ordering};pub static PORTFOLIO_GEOMETRY:AtomicBool=AtomicBool::new(false);",
        ),
        (
            "fn initialize(&mut self,view:&GameState){self.initialized=true;self.starter_id=",
            "fn initialize(&mut self,view:&GameState){self.initialized=true;if !PORTFOLIO_GEOMETRY."
            "load(Ordering::Relaxed){self.minimum_enemy_eta=12;self.require_idle_starter=false;"
            "self.minimum_enemy_door_distance=14;self.minimum_worker_speed=2;}self.starter_id=",
        ),
        (
            "use crate::bot::moisan::SecureOrchardBot;",
            "use crate::bot::moisan::{SecureOrchardBot,PORTFOLIO_GEOMETRY};",
        ),
        (
            "while let Some(view)=read_turn(&mut reader,&map,turn){let commands=bot.commands(&view);",
            "while let Some(view)=read_turn(&mut reader,&map,turn){if turn==1{let banana_fruits="
            "view.plants.iter().filter(|plant|plant.kind==crate::game::PlantKind::Banana).map("
            f"|plant|plant.fruits).sum::<i32>();PORTFOLIO_GEOMETRY.store(banana_fruits<={threshold},"
            "std::sync::atomic::Ordering::Relaxed);}let commands=bot.commands(&view);",
        ),
    )
    result = source
    for before, after in replacements:
        count = result.count(before)
        if count != 1:
            raise RuntimeError(
                f"expected one geometry-portfolio replacement site, found {count}: {before}"
            )
        result = result.replace(before, after, 1)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="secure-orchard source")
    parser.add_argument("output", type=Path)
    parser.add_argument("--threshold", type=int, default=5)
    args = parser.parse_args()
    if args.threshold < 0:
        raise SystemExit("--threshold must be nonnegative")
    candidate = make_geometry_portfolio(args.source.read_text(), args.threshold)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(candidate)
    digest = hashlib.sha256(candidate.encode()).hexdigest()
    args.output.with_name(args.output.name + ".sha256").write_text(
        f"{digest}  {args.output.name}\n"
    )
    print(f"generated banana-{args.threshold} geometry/live portfolio: {len(candidate)} bytes")
    print(f"sha256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
