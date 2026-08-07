#!/usr/bin/env python3
"""Third owner-directed Banana R2 build.

Adds two production safeguards to the conservative v1 arm:
* prevent any inner-controlled banana PLANT that violates the bounded/safe
  ring predicate (outside-ring, late, occupied, or opponent-unsafe);
* stop an attributable peer A-B-A bounce before it can become a sustained
  three-cycle D-1 episode, then re-run same-player move resolution.

The module exposes ``main(patcher=...)`` so later refinement layers can compose
this exact patch without executing the build at import time.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("banana_owner_v1", HERE / "build_candidate.py")
builder = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = builder
spec.loader.exec_module(builder)
base_patch = builder.patch_i1


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def patch_i1(text: str) -> str:
    text = base_patch(text)
    text = replace_once(
        text,
        '''    banana_mother: Option<Cell>,
}
''',
        '''    banana_mother: Option<Cell>,
    // Last two observed cells of every inner-controlled peer.  This is used
    // only after banana activation to stop a candidate-attributable A-B-A
    // return before it becomes a sustained oscillation.
    banana_peer_history: std::collections::BTreeMap<i32, (Cell, Cell)>,
}
''',
        "peer history field",
    )
    text = replace_once(
        text,
        '''            banana_mother: None,
        }
''',
        '''            banana_mother: None,
            banana_peer_history: std::collections::BTreeMap::new(),
        }
''',
        "peer history init",
    )

    loop_start = '''        for unit in view
            .units
            .iter()
            .filter(|unit| unit.player == 0 && Some(unit.id) != wrapper_worker)
        {
'''
    text = replace_once(
        text,
        loop_start,
        '''        let mut peer_move_rewritten = false;
        let ring = Self::banana_ring(view);
        for unit in view
            .units
            .iter()
            .filter(|unit| unit.player == 0 && Some(unit.id) != wrapper_worker)
        {
''',
        "post-edit loop setup",
    )

    old_decision = '''            let steals_seed = active
                && !self.banana_bootstrap_used
                && commands[slot].starts_with("PICK ")
                && commands[slot].ends_with(" BANANA");
            if harms_mother || steals_seed {
                commands[slot] = "WAIT".to_string();
            }
'''
    new_decision = '''            let steals_seed = active
                && !self.banana_bootstrap_used
                && commands[slot].starts_with("PICK ")
                && commands[slot].ends_with(" BANANA");
            // The inner economy may know about bananas, but while this
            // feature is active/lost every banana PLANT must satisfy the same
            // bounded, late-cutoff, occupancy, and opponent-safety predicate
            // as the resident's own candidate generator.
            let plants_banana_invalid = commands[slot].starts_with("PLANT ")
                && commands[slot].ends_with(" BANANA")
                && (!ring.contains(&unit.cell)
                    || !Self::banana_vacant_ok(view, unit, unit.cell, true));

            let (older, previous) = self
                .banana_peer_history
                .get(&unit.id)
                .copied()
                .unwrap_or((unit.cell, unit.cell));
            let returns_to_a = older == unit.cell && previous != unit.cell;
            let move_returns_to_b = if returns_to_a && commands[slot].starts_with("MOVE ") {
                let parts: Vec<&str> = commands[slot].split_whitespace().collect();
                if parts.len() == 4 {
                    match (parts[2].parse::<i32>(), parts[3].parse::<i32>()) {
                        (Ok(x), Ok(y)) => next_cell(
                            &view.walkable,
                            unit.cell,
                            (x, y),
                            unit.stats.movement_speed,
                        ) == previous,
                        _ => false,
                    }
                } else {
                    false
                }
            } else {
                false
            };
            self.banana_peer_history
                .insert(unit.id, (previous, unit.cell));

            if harms_mother || steals_seed || plants_banana_invalid || move_returns_to_b {
                commands[slot] = "WAIT".to_string();
                peer_move_rewritten |= move_returns_to_b;
            }
'''
    text = replace_once(text, old_decision, new_decision, "bounded peer post-edit")

    old_resolver = '''        if let Some(worker_id) = wrapper_worker {
            MoisanBot::resolve_move_conflicts_with_priority(
                view,
                &mut commands,
                &BTreeSet::from([worker_id]),
            );
        }
'''
    new_resolver = '''        if wrapper_worker.is_some() || peer_move_rewritten {
            // If a peer MOVE was changed to WAIT, its current cell becomes
            // stationary and the old landing assignment is no longer valid.
            // Re-resolve once. Loaded wood carriers outrank the resident;
            // otherwise retain the normal resident preference.
            let mut priority = BTreeSet::new();
            for unit in view.units.iter().filter(|unit| {
                unit.player == 0 && unit.carry[crate::game::types::WOOD] > 0
            }) {
                priority.insert(unit.id);
            }
            if priority.is_empty() {
                if let Some(worker_id) = wrapper_worker {
                    priority.insert(worker_id);
                }
            }
            MoisanBot::resolve_move_conflicts_with_priority(
                view,
                &mut commands,
                &priority,
            );
        }
'''
    text = replace_once(text, old_resolver, new_resolver, "peer-safe resolver")
    return text


def main(patcher=patch_i1) -> int:
    builder.patch_i1 = patcher
    return builder.main()


if __name__ == "__main__":
    raise SystemExit(main())
