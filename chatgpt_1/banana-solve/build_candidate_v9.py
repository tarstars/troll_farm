#!/usr/bin/env python3
"""Ninth owner-directed Banana R2 build: service-radius tether.

This uses v6's candidate-founded mother and ETA-trend response, but not v7's
pre-founding delay or v8's permanent WAIT-on-mother hold.  When the wrapper has
no immediate lifecycle action, the inner policy may use the resident normally
inside a BFS radius of two from the exact mother.  A MOVE whose realized
landing would leave that radius is redirected toward the mother (or WAITs if
already inside).  Thus:

* the resident cannot wander across the map and make a later conversion
  infeasible;
* nearby banking and home-ring work still progress;
* the resident is not a permanent stationary obstacle at the mother cell.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("banana_owner_v6", HERE / "build_candidate_v6.py")
v6 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = v6
spec.loader.exec_module(v6)
base_patch = v6.patch_i1


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def patch_i1(text: str) -> str:
    text = base_patch(text)
    marker = '''            if harms_mother || steals_seed || plants_banana_invalid || move_returns_to_b {
                commands[slot] = "WAIT".to_string();
                peer_move_rewritten |= move_returns_to_b;
            }
'''
    replacement = '''            let mut resident_leaves_service_radius = false;
            if wrapper_action.is_none()
                && Some(unit.id) == self.banana_worker
                && commands[slot].starts_with("MOVE ")
            {
                if let Some(mother) = self.banana_mother_cell(view) {
                    let parts: Vec<&str> = commands[slot].split_whitespace().collect();
                    if parts.len() == 4 {
                        if let (Ok(x), Ok(y)) =
                            (parts[2].parse::<i32>(), parts[3].parse::<i32>())
                        {
                            let landing = next_cell(
                                &view.walkable,
                                unit.cell,
                                (x, y),
                                unit.stats.movement_speed,
                            );
                            let dist = bfs_distances(&view.walkable, &[mother]);
                            let landing_dist = dist.get(&landing).copied().unwrap_or(10_000);
                            if landing_dist > 2 {
                                let current_dist =
                                    dist.get(&unit.cell).copied().unwrap_or(10_000);
                                commands[slot] = if current_dist > 2 {
                                    format!(
                                        "MOVE {} {} {}",
                                        unit.id,
                                        mother.0,
                                        mother.1,
                                    )
                                } else {
                                    "WAIT".to_string()
                                };
                                resident_leaves_service_radius = true;
                            }
                        }
                    }
                }
            }
            if harms_mother || steals_seed || plants_banana_invalid || move_returns_to_b {
                commands[slot] = "WAIT".to_string();
            }
            peer_move_rewritten |= move_returns_to_b || resident_leaves_service_radius;
'''
    return replace_once(text, marker, replacement, "resident service-radius tether")


if __name__ == "__main__":
    raise SystemExit(v6.v5.v4.v3.main(patch_i1))
