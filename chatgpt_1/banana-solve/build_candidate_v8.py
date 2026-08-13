#!/usr/bin/env python3
"""Eighth owner-directed Banana R2 build: a live mother keeps its resident.

Round-6's generic starvation release was correct for an empty/finished feature,
but wrong while the exact candidate-founded mother was merely waiting for its
next growth tick.  It released the starter after three idle turns, allowing
the inner policy to send it across the map; a later approach then made safe
conversion impossible and the opponent farmed the mother.

This layer makes Idle with a live latched mother a service hold: MOVE back to
the mother or WAIT on it.  Release remains available when no mother exists.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("banana_owner_v7", HERE / "build_candidate_v7.py")
v7 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = v7
spec.loader.exec_module(v7)
base_patch = v7.patch_i1


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def patch_i1(text: str) -> str:
    text = base_patch(text)
    marker = '''        if chosen.1 == BananaTask::Idle {
            self.banana_idle_streak += 1;
'''
    replacement = '''        if chosen.1 == BananaTask::Idle {
            // A live exact mother is not starvation.  Its next productive
            // action is time-gated by growth; keep the resident within ETA 0
            // rather than releasing it to a distant inner task.  This makes a
            // later ETA decrease observable while conversion is still
            // feasible and prevents opponent farming after a long idle gap.
            if let Some(mother) = self.banana_mother_cell(view) {
                self.banana_idle_streak = 0;
                self.banana_target = Some((BananaTask::Harvest, mother));
                self.banana_hold_age = 0;
                self.banana_blocked_turns = 0;
                self.banana_last_cell = Some(worker.cell);
                self.banana_last_move = worker.cell != mother;
                self.banana_best_dist = None;
                return Some(if worker.cell == mother {
                    "WAIT".to_string()
                } else {
                    format!("MOVE {} {} {}", worker.id, mother.0, mother.1)
                });
            }
            self.banana_idle_streak += 1;
'''
    return replace_once(text, marker, replacement, "live-mother idle hold")


if __name__ == "__main__":
    raise SystemExit(v7.v6.v5.v4.v3.main(patch_i1))
