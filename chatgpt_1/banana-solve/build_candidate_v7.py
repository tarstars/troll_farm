#!/usr/bin/env python3
"""Seventh owner-directed Banana R2 build: observational founding gate.

The unsafe fuzz families all share one cause: the opponent was already moving
when the bootstrap mother was founded.  A plant-time distance threshold cannot
distinguish that from a genuinely static far opponent.  This layer observes
the closest harvester/chopper ETA to every diagonal founding cell for three
turns before the bootstrap PICK is allowed:

* any decreasing ETA resets the stability counter and leaves the resident with
  the inner economy;
* a static distant opponent reaches three stable observations and the existing
  exact current-state safety predicate may found the mother;
* after founding, v6's ETA-trend service handles a later approach.
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
    text = replace_once(
        text,
        '''    banana_prev_x_eta: Option<i32>,
}
''',
        '''    banana_prev_x_eta: Option<i32>,
    // Pre-founding observation of the nearest opponent to any eligible
    // diagonal mother cell.  The seed is not spent until both ETAs have been
    // non-decreasing for three consecutive observations.
    banana_probe_h_eta: Option<i32>,
    banana_probe_x_eta: Option<i32>,
    banana_probe_stable: i32,
}
''',
        "founding probe fields",
    )
    text = replace_once(
        text,
        '''            banana_prev_x_eta: None,
        }
''',
        '''            banana_prev_x_eta: None,
            banana_probe_h_eta: None,
            banana_probe_x_eta: None,
            banana_probe_stable: 0,
        }
''',
        "founding probe init",
    )
    text = replace_once(
        text,
        '''            self.banana_prev_x_eta = None;
''',
        '''            self.banana_prev_x_eta = None;
            self.banana_probe_h_eta = None;
            self.banana_probe_x_eta = None;
            self.banana_probe_stable = 0;
''',
        "clear founding probe",
    )

    marker = '''        // F-B3 (rev. 2026-08-06): a post-MOVE turn is blocked when the BFS
'''
    probe = '''        // Observational founding gate.  Before the one bootstrap seed is
        // withdrawn, watch every eligible diagonal cell for three turns.  A
        // moving threat resets the counter; during the probe the resident is
        // fully released to the inner economy and no banana reservation is
        // written.  Current-state safety is still rechecked by
        // banana_vacant_ok on the actual PLANT turn.
        if self.banana_mother.is_none()
            && !self.banana_bootstrap_used
            && !Self::banana_ring(view)
                .into_iter()
                .any(|cell| Self::banana_live(view, cell).is_some())
        {
            let tent = view.shacks[0];
            let mut h_eta = 10_000;
            let mut x_eta = 10_000;
            let mut has_diag = false;
            for cell in Self::banana_ring(view) {
                if is_adjacent(cell, tent) {
                    continue;
                }
                if Self::banana_vacant_ok(view, worker, cell, false) {
                    has_diag = true;
                    h_eta = h_eta.min(Self::banana_opponent_eta(
                        view,
                        cell,
                        false,
                    ));
                    x_eta = x_eta.min(Self::banana_opponent_eta(
                        view,
                        cell,
                        true,
                    ));
                }
            }
            let stable = has_diag
                && self
                    .banana_probe_h_eta
                    .map(|previous| h_eta >= previous)
                    .unwrap_or(false)
                && self
                    .banana_probe_x_eta
                    .map(|previous| x_eta >= previous)
                    .unwrap_or(false);
            self.banana_probe_h_eta = Some(h_eta);
            self.banana_probe_x_eta = Some(x_eta);
            self.banana_probe_stable = if stable {
                self.banana_probe_stable + 1
            } else {
                0
            };
            if self.banana_probe_stable < 3 {
                self.banana_last_move = false;
                self.banana_last_cell = Some(worker.cell);
                return None;
            }
        }

'''
    return replace_once(text, marker, probe + marker, "observational founding gate")


if __name__ == "__main__":
    raise SystemExit(v6.v5.v4.v3.main(patch_i1))
