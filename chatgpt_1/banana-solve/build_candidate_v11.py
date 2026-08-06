#!/usr/bin/env python3
"""Eleventh owner-directed Banana R2 build: global zero-oscillation layer.

The owner explicitly requires inherited oscillations to be fixed rather than
reclassified.  This layer therefore runs after the final inner/banana command
selection on every turn, including dormant, disabled and completed banana
states.

It enforces two production rules on the final command vector:

* every wood carrier emits DROP on a door or an exact MOVE landing whose BFS
  distance to the door set is strictly smaller than its current distance;
* any MOVE whose referee-realized landing would continue an A-B-A-B return is
  replaced by one WAIT (or avoided while selecting a carrier landing).

The one-turn repeat breaks D-1's contiguous alternating run.  For wood
carriers it can occur only after at least one strict progress turn, so D-4's
consecutive-no-progress counter cannot reach two.  Wood carriers are resolved
with priority after exact progress landings are selected.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "banana_owner_v4", HERE / "build_candidate_v4.py"
)
v4 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = v4
spec.loader.exec_module(v4)
base_patch = v4.patch_i1


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def replace_last_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count < 1:
        raise AssertionError(f"{label}: expected at least one match")
    head, tail = text.rsplit(old, 1)
    return head + new + tail


def patch_i1(text: str) -> str:
    text = base_patch(text)

    text = replace_once(
        text,
        '''    banana_peer_history: std::collections::BTreeMap<i32, (Cell, Cell)>,
}
''',
        '''    banana_peer_history: std::collections::BTreeMap<i32, (Cell, Cell)>,
    // Global final-command history. Unlike banana_peer_history this is live
    // in every phase and is the hard D-1/D-4 gate mechanism.
    stability_history: std::collections::BTreeMap<i32, (Cell, Cell)>,
}
''',
        "global stability field",
    )
    text = replace_once(
        text,
        '''            banana_peer_history: std::collections::BTreeMap::new(),
        }
''',
        '''            banana_peer_history: std::collections::BTreeMap::new(),
            stability_history: std::collections::BTreeMap::new(),
        }
''',
        "global stability init",
    )

    # Structural identity is intentionally narrower now: the final stability
    # layer must run even when banana logic is dormant or disabled, because the
    # owner requires inherited oscillations to be fixed too.  The inner command
    # vector is still unchanged unless a hard stability rule fires.
    text = replace_once(
        text,
        '''        if wrapper_action.is_none() && claim.is_none() && !active && !lost {
            // Structural identity: no post-edit outside banana activation
            // (dormant/disabled/never-lost-abandoned turns).
            return commands;
        }
''',
        '''        // No early return here: the global stability layer below is
        // active in every lifecycle phase. Dormant commands remain byte-equal
        // unless an actual D-1/D-4 prevention rule fires.
''',
        "remove stability-bypassing early return",
    )

    helper_marker = '''}

impl Bot for BananaBot {
'''
    helper = r'''    /// Referee-realized MOVE landing for one final command.
    fn stability_landing(view: &GameState, unit: &Unit, command: &str) -> Option<Cell> {
        let fields: Vec<&str> = command.split_whitespace().collect();
        if fields.len() != 4 || !fields[0].eq_ignore_ascii_case("MOVE") {
            return None;
        }
        let id: i32 = fields[1].parse().ok()?;
        if id != unit.id {
            return None;
        }
        let target = (fields[2].parse().ok()?, fields[3].parse().ok()?);
        Some(next_cell(
            &view.walkable,
            unit.cell,
            target,
            unit.stats.movement_speed,
        ))
    }

    /// Final hard stability layer. It is intentionally independent of banana
    /// activation and therefore repairs inherited parent oscillations too.
    fn stability_finalize(&mut self, view: &GameState, commands: &mut Vec<String>) {
        let mut unit_ids: Vec<i32> = view
            .units
            .iter()
            .filter(|unit| unit.player == 0)
            .map(|unit| unit.id)
            .collect();
        unit_ids.sort_unstable();

        let doors: Vec<Cell> = ortho_neighbors(view.shacks[0])
            .into_iter()
            .filter(|cell| view.walkable.contains(cell))
            .collect();
        let door_set: BTreeSet<Cell> = doors.iter().copied().collect();
        let door_dist = bfs_distances(&view.walkable, &doors);

        // A carrier landing may never use the current cell of a non-carrier.
        // This makes the exact progress assignment independent of whether a
        // later oscillation veto turns that non-carrier's MOVE into WAIT.
        let non_carrier_cells: BTreeSet<Cell> = view
            .units
            .iter()
            .filter(|unit| {
                unit.player == 0 && unit.carry[crate::game::types::WOOD] == 0
            })
            .map(|unit| unit.cell)
            .collect();

        let mut carriers: Vec<&Unit> = view
            .units
            .iter()
            .filter(|unit| {
                unit.player == 0 && unit.carry[crate::game::types::WOOD] > 0
            })
            .collect();
        carriers.sort_by_key(|unit| {
            (
                door_dist.get(&unit.cell).copied().unwrap_or(10_000),
                unit.id,
            )
        });

        let mut carrier_landings = BTreeSet::new();
        let mut priority = BTreeSet::new();
        for unit in carriers {
            priority.insert(unit.id);
            let Some(slot) = SecureOrchardBot::unit_action_slot(
                commands,
                &unit_ids,
                unit.id,
            ) else {
                continue;
            };
            if door_set.contains(&unit.cell) {
                commands[slot] = format!("DROP {}", unit.id);
                continue;
            }
            let Some(current_distance) = door_dist.get(&unit.cell).copied() else {
                // No reachable bank route: do not manufacture a target.
                commands[slot] = "WAIT".to_string();
                continue;
            };
            let from = bfs_distances(&view.walkable, &[unit.cell]);
            let (older, previous) = self
                .stability_history
                .get(&unit.id)
                .copied()
                .unwrap_or((unit.cell, unit.cell));
            let returning = older == unit.cell && previous != unit.cell;

            let mut options: Vec<(i32, i32, Cell)> = from
                .iter()
                .filter_map(|(cell, steps)| {
                    let next_distance = door_dist.get(cell).copied()?;
                    if *steps <= unit.stats.movement_speed
                        && next_distance < current_distance
                        && !non_carrier_cells.contains(cell)
                        && !carrier_landings.contains(cell)
                    {
                        Some((next_distance, *steps, *cell))
                    } else {
                        None
                    }
                })
                .collect();
            options.sort_unstable();

            let selected = options
                .iter()
                .find(|(_, _, cell)| !returning || *cell != previous)
                .copied();
            if let Some((_distance, _steps, landing)) = selected {
                carrier_landings.insert(landing);
                commands[slot] = format!(
                    "MOVE {} {} {}",
                    unit.id,
                    landing.0,
                    landing.1,
                );
            } else {
                // A single stationary turn is allowed. The history update
                // below makes the next turn non-returning, so this cannot
                // create two consecutive D-4 no-progress transitions.
                commands[slot] = "WAIT".to_string();
            }
        }

        if !priority.is_empty() {
            MoisanBot::resolve_move_conflicts_with_priority(
                view,
                commands,
                &priority,
            );
        }

        // Inspect the actually resolved landing. One repeated cell is enough
        // to break the contiguous A-B-A-B sequence long before D-1's k>=3
        // threshold. Carrier targets were selected away from non-carrier
        // current cells, so converting a non-carrier MOVE to WAIT cannot block
        // a carrier's exact landing.
        for unit in view.units.iter().filter(|unit| unit.player == 0) {
            let Some(slot) = SecureOrchardBot::unit_action_slot(
                commands,
                &unit_ids,
                unit.id,
            ) else {
                continue;
            };
            let (older, previous) = self
                .stability_history
                .get(&unit.id)
                .copied()
                .unwrap_or((unit.cell, unit.cell));
            let returning = older == unit.cell && previous != unit.cell;
            let lands_on_previous = Self::stability_landing(
                view,
                unit,
                &commands[slot],
            ) == Some(previous);
            if returning && lands_on_previous {
                commands[slot] = "WAIT".to_string();
            }
            self.stability_history
                .insert(unit.id, (previous, unit.cell));
        }
        self.stability_history
            .retain(|id, _| view.unit(*id).is_some());
    }

'''
    text = replace_once(
        text,
        helper_marker,
        helper + helper_marker,
        "global stability helper insertion",
    )

    text = replace_last_once(
        text,
        '''        commands
    }
}''',
        '''        self.stability_finalize(view, &mut commands);
        commands
    }
}''',
        "global stability final call",
    )
    return text


if __name__ == "__main__":
    raise SystemExit(v4.v3.main(patch_i1))
