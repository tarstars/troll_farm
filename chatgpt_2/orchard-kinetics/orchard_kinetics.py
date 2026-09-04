#!/usr/bin/env python3
"""Exact single-tree orchard kinetics used by the Troll Farm referee.

This is deliberately a *micro-instrument*, not a game solver.  It mirrors the
PLANT, CHOP and end-of-turn plant-tick rules in ``rust/src/game/engine.rs`` so
that design work can put a planting turn and a chopping turn on the same
timeline without hand-waving.

Timeline convention
-------------------
A tree is planted during game turn ``p``.  ``state_at_end_offset(..., 0)`` is
its state after the end-of-turn tick of that same turn.  Therefore a tree
planted on turn ``p`` has age ``T - p`` in ``cohort_standing_points`` when
observed after the end-of-turn tick of turn ``T``.

The module does not model movement, banking, worker contention, opponent
actions, ownership inference or the referee's simultaneous multi-chopper
last-wood duplication.  Those remain responsibilities of the exact map search.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, replace
from math import ceil
from typing import Iterable

MAX_SIZE = 4
MAX_FRUITS = 3
WOOD_POINTS = 4

SPECIES: dict[str, dict[str, int]] = {
    "PLUM": {"cooldown": 8, "water_boost": 5, "base": 4, "slope": 2},
    "LEMON": {"cooldown": 8, "water_boost": 5, "base": 4, "slope": 2},
    "APPLE": {"cooldown": 9, "water_boost": 7, "base": 8, "slope": 3},
    "BANANA": {"cooldown": 6, "water_boost": 2, "base": 2, "slope": 1},
}


@dataclass(frozen=True)
class TreeState:
    kind: str
    size: int
    health: int
    fruits: int
    cooldown: int


@dataclass(frozen=True)
class Milestones:
    kind: str
    near_water: bool
    effective_cooldown: int
    full_size_end_offset: int
    first_fruit_end_offset: int
    mature_health: int
    gross_mature_wood_points: int


def _normalise_kind(kind: str) -> str:
    normalised = kind.upper()
    if normalised not in SPECIES:
        raise ValueError(f"unknown plant kind: {kind!r}")
    return normalised


def effective_cooldown(kind: str, near_water: bool) -> int:
    """Return the exact cooldown reset used by the referee."""
    spec = SPECIES[_normalise_kind(kind)]
    return spec["cooldown"] - (spec["water_boost"] if near_water else 0)


def tree_health(kind: str, size: int) -> int:
    """Return untouched health at ``size``."""
    if not 0 <= size <= MAX_SIZE:
        raise ValueError(f"size must be in 0..={MAX_SIZE}, got {size}")
    spec = SPECIES[_normalise_kind(kind)]
    return spec["base"] + spec["slope"] * size


def planted_state(kind: str) -> TreeState:
    """State immediately after PLANT and before that turn's plant tick."""
    kind = _normalise_kind(kind)
    return TreeState(kind, size=0, health=tree_health(kind, 0), fruits=0, cooldown=0)


def tick(state: TreeState, near_water: bool) -> TreeState:
    """Mirror ``tick_plants`` for one live tree."""
    if state.health <= 0:
        return state
    cooldown = max(0, state.cooldown - 1) if state.cooldown > 0 else 0
    size = state.size
    health = state.health
    fruits = state.fruits
    if cooldown == 0:
        if size < MAX_SIZE:
            size += 1
            # Growth adds the slope; it does not heal accumulated damage.
            health += SPECIES[state.kind]["slope"]
            cooldown = effective_cooldown(state.kind, near_water)
        elif fruits < MAX_FRUITS:
            fruits += 1
            cooldown = effective_cooldown(state.kind, near_water)
    return TreeState(state.kind, size, health, fruits, cooldown)


def plant_turn_end_state(kind: str, near_water: bool) -> TreeState:
    """State after the end-of-turn tick on the PLANT turn."""
    return tick(planted_state(kind), near_water)


def state_at_end_offset(kind: str, near_water: bool, offset: int) -> TreeState:
    """State at end of PLANT turn + ``offset`` subsequent turns."""
    if offset < 0:
        raise ValueError("offset must be non-negative")
    state = plant_turn_end_state(kind, near_water)
    for _ in range(offset):
        state = tick(state, near_water)
    return state


def chop(state: TreeState, total_power: int) -> tuple[TreeState | None, int]:
    """Apply one CHOP phase.

    Returns ``(new_state, wood_units)``.  This conservative single-tree helper
    returns exactly ``size`` wood on death.  The full referee can duplicate the
    last wood among simultaneous choppers; a planner must replay that separately
    rather than rely on it in an optimistic bound.
    """
    if total_power < 0:
        raise ValueError("total_power must be non-negative")
    if total_power == 0 or state.health <= 0:
        return state, 0
    health = max(0, state.health - total_power)
    if health == 0:
        return None, state.size
    return replace(state, health=health), 0


def milestones(kind: str, near_water: bool) -> Milestones:
    """Return exact idle-growth milestones after a PLANT turn."""
    kind = _normalise_kind(kind)
    full_size: int | None = None
    first_fruit: int | None = None
    for offset in range(0, 101):
        state = state_at_end_offset(kind, near_water, offset)
        if full_size is None and state.size == MAX_SIZE:
            full_size = offset
        if first_fruit is None and state.fruits > 0:
            first_fruit = offset
            break
    if full_size is None or first_fruit is None:
        raise RuntimeError(f"milestones not reached for {kind}")
    return Milestones(
        kind=kind,
        near_water=near_water,
        effective_cooldown=effective_cooldown(kind, near_water),
        full_size_end_offset=full_size,
        first_fruit_end_offset=first_fruit,
        mature_health=tree_health(kind, MAX_SIZE),
        gross_mature_wood_points=MAX_SIZE * WOOD_POINTS,
    )


def mature_fell_turns(kind: str, total_power: int) -> int:
    """CHOP turns needed for an untouched mature tree."""
    if total_power <= 0:
        raise ValueError("total_power must be positive")
    return ceil(tree_health(kind, MAX_SIZE) / total_power)


def cohort_standing_points(
    kind: str,
    near_water: bool,
    planted_turns: Iterable[int],
    at_end_turn: int,
) -> int:
    """Gross score potential of standing tree sizes at one end-of-turn state."""
    total_units = 0
    for planted_turn in planted_turns:
        if planted_turn > at_end_turn:
            continue
        age = at_end_turn - planted_turn
        total_units += state_at_end_offset(kind, near_water, age).size
    return total_units * WOOD_POINTS


def survival_probability(
    planted_turn: int,
    fell_turn: int,
    *,
    early_hazard_per_tree_turn: float = 0.0019,
    late_hazard_per_tree_turn: float = 0.008,
    split_turn: int = 100,
) -> float:
    """Independent-hazard planning approximation, not a referee rule."""
    if fell_turn < planted_turn:
        raise ValueError("fell_turn must not precede planted_turn")
    if not 0 <= early_hazard_per_tree_turn < 1:
        raise ValueError("early hazard must be in [0, 1)")
    if not 0 <= late_hazard_per_tree_turn < 1:
        raise ValueError("late hazard must be in [0, 1)")
    probability = 1.0
    for turn in range(planted_turn, fell_turn):
        hazard = (
            early_hazard_per_tree_turn if turn < split_turn else late_hazard_per_tree_turn
        )
        probability *= 1.0 - hazard
    return probability


def species_rows() -> list[dict[str, int | str | bool]]:
    rows: list[dict[str, int | str | bool]] = []
    for kind in SPECIES:
        for near_water in (True, False):
            m = milestones(kind, near_water)
            row: dict[str, int | str | bool] = asdict(m)
            for power in (1, 2, 3, 4):
                row[f"fell_turns_p{power}"] = mature_fell_turns(kind, power)
            rows.append(row)
    return rows


def _markdown_table(rows: list[dict[str, int | str | bool]]) -> str:
    header = (
        "| kind | location | cd | full size | first fruit | mature health | "
        "fell p1/p2/p3/p4 | gross points |\n"
        "|---|---:|---:|---:|---:|---:|---:|---:|\n"
    )
    body = []
    for row in rows:
        body.append(
            "| {kind} | {location} | {effective_cooldown} | "
            "{full_size_end_offset} | {first_fruit_end_offset} | "
            "{mature_health} | {fell_turns_p1}/{fell_turns_p2}/"
            "{fell_turns_p3}/{fell_turns_p4} | {gross_mature_wood_points} |".format(
                location="water" if row["near_water"] else "inland", **row
            )
        )
    return header + "\n".join(body)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    args = parser.parse_args()
    rows = species_rows()
    if args.json:
        print(json.dumps(rows, indent=2, sort_keys=True))
    else:
        print(_markdown_table(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
