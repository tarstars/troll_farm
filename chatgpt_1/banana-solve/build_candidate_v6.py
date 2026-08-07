#!/usr/bin/env python3
"""Sixth owner-directed Banana R2 build: dynamic mother service.

A mother that was private at founding can become unsafe later.  This layer
persists the previous opponent harvester/chopper ETAs for the exact latched
mother and distinguishes a static nearby unit from one that is actually
closing:

* while an unripe mother could be reached before first fruit, the resident
  camps/services the mother instead of wandering to a distant wood job;
* when either opponent ETA decreases, the resident immediately performs the
  exact growth-aware conversion if it still completes strictly before arrival;
* a static far opponent does not destroy the renewable lifecycle: once the
  remaining ripening time is shorter than its current ETA, ordinary harvest
  service resumes.

No same-turn wood prediction or multi-chopper power handoff is introduced.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("banana_owner_v5", HERE / "build_candidate_v5.py")
v5 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = v5
spec.loader.exec_module(v5)
base_patch = v5.patch_i1


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def patch_i1(text: str) -> str:
    text = base_patch(text)
    text = replace_once(
        text,
        '''    banana_peer_history: std::collections::BTreeMap<i32, (Cell, Cell)>,
}
''',
        '''    banana_peer_history: std::collections::BTreeMap<i32, (Cell, Cell)>,
    // Previous ETAs to the exact latched mother.  A falling ETA is an
    // observable approach; a static far opponent is not treated as movement.
    banana_prev_h_eta: Option<i32>,
    banana_prev_x_eta: Option<i32>,
}
''',
        "mother ETA fields",
    )
    text = replace_once(
        text,
        '''            banana_peer_history: std::collections::BTreeMap::new(),
        }
''',
        '''            banana_peer_history: std::collections::BTreeMap::new(),
            banana_prev_h_eta: None,
            banana_prev_x_eta: None,
        }
''',
        "mother ETA init",
    )
    text = replace_once(
        text,
        '''            self.banana_mother = Some(chosen.2);
''',
        '''            self.banana_mother = Some(chosen.2);
            self.banana_prev_h_eta = None;
            self.banana_prev_x_eta = None;
''',
        "reset ETA history on founding",
    )

    old_eta = '''            let eta_opp = Self::banana_opponent_eta(view, mother, false);
            let banking_drop_now = worker.carry[crate::game::types::WOOD] > 0
                && is_adjacent(worker.cell, view.shacks[0]);
'''
    new_eta = '''            let eta_opp = Self::banana_opponent_eta(view, mother, false);
            let eta_chop = Self::banana_opponent_eta(view, mother, true);
            let h_approaching = self
                .banana_prev_h_eta
                .map(|previous| eta_opp < previous)
                .unwrap_or(false);
            let x_approaching = self
                .banana_prev_x_eta
                .map(|previous| eta_chop < previous)
                .unwrap_or(false);
            self.banana_prev_h_eta = Some(eta_opp);
            self.banana_prev_x_eta = Some(eta_chop);
            let banking_drop_now = worker.carry[crate::game::types::WOOD] > 0
                && is_adjacent(worker.cell, view.shacks[0]);

            // Dynamic mother service.  The wrapper observes one full state
            // before classifying motion: a far static opponent leaves ETAs
            // unchanged, while a closing opponent makes one or both ETAs
            // strictly decrease.  Cargo banking remains higher priority.
            if !banking_drop_now && worker.total_carried() == 0 {
                if let Some(plant) = Self::banana_live(view, mother) {
                    if plant.fruits == 0 {
                        let ripe = MoisanBot::ticks_until_fruit(view, plant);
                        let h_threatens = eta_opp <= ripe;
                        let x_threatens = eta_chop <= ripe;
                        let approaching =
                            (h_approaching && h_threatens)
                                || (x_approaching && x_threatens);
                        if approaching {
                            let mut deadline = 10_000;
                            if h_approaching && h_threatens {
                                deadline = deadline.min(eta_opp);
                            }
                            if x_approaching && x_threatens {
                                deadline = deadline.min(eta_chop);
                            }
                            let conversion = if worker.stats.chop_power > 0
                                && resident_eta < 10_000
                            {
                                let arrival = Self::banana_predict_growth(
                                    view,
                                    plant,
                                    resident_eta,
                                );
                                MoisanBot::chop_outcome(
                                    view,
                                    plant,
                                    arrival,
                                    worker.stats.chop_power,
                                )
                                .map(|(turns, _wood)| resident_eta + turns - 1)
                            } else {
                                None
                            };
                            if conversion
                                .map(|completion| completion < deadline)
                                .unwrap_or(false)
                            {
                                // A real closing threat: convert immediately,
                                // latching the exact mother until it falls.
                                self.banana_target =
                                    Some((BananaTask::Chop, mother));
                                self.banana_hold_age = 0;
                                self.banana_blocked_turns = 0;
                                self.banana_last_cell = Some(worker.cell);
                                self.banana_last_move = worker.cell != mother;
                                self.banana_best_dist = None;
                                self.banana_idle_streak = 0;
                                return Some(if worker.cell == mother {
                                    format!("CHOP {}", worker.id)
                                } else {
                                    format!(
                                        "MOVE {} {} {}",
                                        worker.id,
                                        mother.0,
                                        mother.1,
                                    )
                                });
                            }
                        }
                        if h_threatens || x_threatens {
                            // The threat is currently static (or a first
                            // observation).  Keep the resident on the mother
                            // until either it becomes harvest-safe or motion
                            // is observed on the next turn.
                            self.banana_target =
                                Some((BananaTask::Harvest, mother));
                            self.banana_hold_age = 0;
                            self.banana_blocked_turns = 0;
                            self.banana_last_cell = Some(worker.cell);
                            self.banana_last_move = worker.cell != mother;
                            self.banana_best_dist = None;
                            self.banana_idle_streak = 0;
                            return Some(if worker.cell == mother {
                                "WAIT".to_string()
                            } else {
                                format!(
                                    "MOVE {} {} {}",
                                    worker.id,
                                    mother.0,
                                    mother.1,
                                )
                            });
                        }
                    }
                }
            }
'''
    return replace_once(text, old_eta, new_eta, "dynamic mother service")


if __name__ == "__main__":
    raise SystemExit(v5.v4.v3.main(patch_i1))
