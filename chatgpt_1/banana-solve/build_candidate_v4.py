#!/usr/bin/env python3
"""Fourth owner-directed Banana R2 build.

Extends v3's peer safeguards to the resident itself: a wrapper MOVE whose
realized landing would complete the next A-B-A-B return is replaced by one
WAIT, breaking a sustained two-cell loop while preserving the commitment for
the next turn.  When the wrapper releases the resident, v3's peer path owns the
single history update instead of double-writing it.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("banana_owner_v3", HERE / "build_candidate_v3.py")
v3 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = v3
spec.loader.exec_module(v3)
base_patch = v3.patch_i1


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def patch_i1(text: str) -> str:
    text = base_patch(text)
    text = replace_once(
        text,
        "        let wrapper_action: Option<String> = match self\n",
        "        let mut wrapper_action: Option<String> = match self\n",
        "mutable wrapper action",
    )

    marker = '''        // F-C2 persistent claim (rev. 2026-08-06): the protected-cell
'''
    resident_guard = '''        // Break a resident two-cell return before it becomes a sustained
        // A-B-A-B loop.  The task/target latch is deliberately left intact:
        // one stationary turn forces the existing blocked/progress accounting
        // to re-evaluate rather than manufacturing a new target.  When the
        // wrapper emits no action, the post-edit peer path below owns this
        // history update so the resident is not recorded twice in one turn.
        if wrapper_action.is_some() {
            if let Some(worker_id) = self.banana_worker {
                if let Some(worker) = view.unit(worker_id) {
                    let (older, previous) = self
                        .banana_peer_history
                        .get(&worker_id)
                        .copied()
                        .unwrap_or((worker.cell, worker.cell));
                    let returns_to_a = older == worker.cell && previous != worker.cell;
                    let move_returns_to_b = wrapper_action
                        .as_ref()
                        .filter(|action| returns_to_a && action.starts_with("MOVE "))
                        .map(|action| {
                            let parts: Vec<&str> = action.split_whitespace().collect();
                            if parts.len() == 4 {
                                match (parts[2].parse::<i32>(), parts[3].parse::<i32>()) {
                                    (Ok(x), Ok(y)) => next_cell(
                                        &view.walkable,
                                        worker.cell,
                                        (x, y),
                                        worker.stats.movement_speed,
                                    ) == previous,
                                    _ => false,
                                }
                            } else {
                                false
                            }
                        })
                        .unwrap_or(false);
                    self.banana_peer_history
                        .insert(worker_id, (previous, worker.cell));
                    if move_returns_to_b {
                        wrapper_action = Some("WAIT".to_string());
                    }
                }
            }
        }

'''
    text = replace_once(text, marker, resident_guard + marker, "resident bounce guard")
    return text


if __name__ == "__main__":
    raise SystemExit(v3.main(patch_i1))
