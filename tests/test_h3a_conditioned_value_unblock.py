"""Semantic tests for the H3a Phase-A trigger preflight analyzer.

The five eligibility fixtures mirror the frozen reconstruction record
`h3a-pressure-treatment-reconstruction-result-2026-07-31.json`, whose archived treatment
returns 25.0 for an eligible ETA-6 tracked tree at input score 12.5 and 12.5 (unchanged) for
each ineligible case. Here we assert the *predicate* those fixtures encode, since this
analyzer decides eligibility rather than applying the score transformation.
"""

from __future__ import annotations

import importlib.util
import os

import pytest

_MOD = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "claude_1",
    "h3a-conditioned-value-unblock-preflight.py",
)
_spec = importlib.util.spec_from_file_location("h3a_preflight", _MOD)
h3a = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(h3a)


# --------------------------------------------------------------------------
# Resident primitives — must match rust/src/bin/yamo_orchard_live.rs exactly
# --------------------------------------------------------------------------


def test_ceil_div_matches_resident_including_sentinel() -> None:
    assert h3a.ceil_div(0, 1) == 0
    assert h3a.ceil_div(1, 1) == 1
    assert h3a.ceil_div(6, 1) == 6
    assert h3a.ceil_div(7, 2) == 4  # (7+2-1)//2
    assert h3a.ceil_div(12, 2) == 6
    # b <= 0 returns the resident's 10_000 sentinel, never a division error.
    assert h3a.ceil_div(5, 0) == 10_000
    assert h3a.ceil_div(5, -3) == 10_000


def test_bfs_is_four_neighbour_and_respects_walkability() -> None:
    walkable = {(x, 0) for x in range(5)} | {(0, y) for y in range(5)}
    dist = h3a.bfs_distances(walkable, [(0, 0)])
    assert dist[(0, 0)] == 0
    assert dist[(4, 0)] == 4
    assert dist[(0, 4)] == 4
    # Diagonal movement must not exist: (1,1) is unreachable on this cross.
    assert (1, 1) not in dist


def test_bfs_excludes_unwalkable_cells() -> None:
    walkable = {(0, 0), (1, 0), (3, 0)}  # gap at (2,0)
    dist = h3a.bfs_distances(walkable, [(0, 0)])
    assert dist[(1, 0)] == 1
    assert (3, 0) not in dist


# --------------------------------------------------------------------------
# Eligibility fixtures — the five archived cases
# --------------------------------------------------------------------------

WALKABLE = {(x, 0) for x in range(12)}


def _row(trees, troll_x=0, speed=1):
    return {
        "turn": 100,
        "resident_trolls": [
            {"troll_id": 1, "x": troll_x, "y": 0, "movement_speed": speed}
        ],
        "trees": trees,
    }


def _tree(x, created_by="seat0", health=10, fruits=1, species="APPLE"):
    return {
        "x": x,
        "y": 0,
        "created_by": created_by,
        "health": health,
        "fruits": fruits,
        "species": species,
    }


def test_fixture_eligible_at_eta_6() -> None:
    hits = h3a.eligible_trees_at(_row([_tree(6)]), WALKABLE, "seat0", False)
    assert len(hits) == 1
    assert hits[0]["eta"] == 6  # inclusive threshold


def test_fixture_ineligible_at_eta_7() -> None:
    assert h3a.eligible_trees_at(_row([_tree(7)]), WALKABLE, "seat0", False) == []


def test_fixture_ineligible_untracked_initial_tree() -> None:
    """An `initial` tree is not an opponent crop, however close it is."""
    assert h3a.eligible_trees_at(_row([_tree(1, created_by="initial")]), WALKABLE, "seat0", False) == []


def test_fixture_ineligible_own_crop() -> None:
    """Our own planted crop is not a tracked opponent crop."""
    assert h3a.eligible_trees_at(_row([_tree(1, created_by="seat1")]), WALKABLE, "seat0", False) == []


def test_fixture_ineligible_non_tree_dead_stump() -> None:
    """health <= 0 is not an existing tree."""
    assert h3a.eligible_trees_at(_row([_tree(1, health=0)]), WALKABLE, "seat0", False) == []


def test_fixture_ineligible_unreachable() -> None:
    """A tree off the walkable component has no BFS distance and cannot be eligible."""
    assert h3a.eligible_trees_at(_row([_tree(3)]), {(0, 0), (1, 0)}, "seat0", False) == []


def test_eta_scales_with_movement_speed() -> None:
    """ETA is ceil_div(distance, speed): distance 12 at speed 2 is ETA 6, still eligible."""
    assert h3a.eligible_trees_at(_row([_tree(12)], speed=2), WALKABLE | {(12, 0)}, "seat0", False)
    assert h3a.eligible_trees_at(_row([_tree(12)], speed=1), WALKABLE | {(12, 0)}, "seat0", False) == []


def test_require_fruits_narrows_to_harvest_branch() -> None:
    row = _row([_tree(2, fruits=0)])
    assert h3a.eligible_trees_at(row, WALKABLE, "seat0", False)  # chop branch admits it
    assert h3a.eligible_trees_at(row, WALKABLE, "seat0", True) == []  # harvest branch does not


# --------------------------------------------------------------------------
# Predicate semantics
# --------------------------------------------------------------------------


def test_activation_is_first_crossing_and_sticky() -> None:
    rows = [
        {"turn": 1, "visible_opponent_unit_count": 1},
        {"turn": 2, "visible_opponent_unit_count": 2},
        {"turn": 3, "visible_opponent_unit_count": 3},
        {"turn": 4, "visible_opponent_unit_count": 2},  # a loss must not revoke activation
    ]
    assert h3a.activation_turn(rows) == 3


def test_activation_none_when_never_three() -> None:
    rows = [{"turn": t, "visible_opponent_unit_count": 2} for t in range(1, 20)]
    assert h3a.activation_turn(rows) is None


def test_activation_requires_three_not_two() -> None:
    rows = [{"turn": 1, "visible_opponent_unit_count": 2}]
    assert h3a.activation_turn(rows) is None


def test_collapse_start_finds_first_sign_flip() -> None:
    assert h3a.collapse_start([10.0, 20.0, 30.0, -5.0, -50.0, -80.0]) == 150


def test_collapse_start_ignores_missing_checkpoints() -> None:
    """A game shorter than 300 turns has absent checkpoints; absent is not zero."""
    assert h3a.collapse_start([10.0, 20.0, None, None, None, None]) is None


def test_collapse_start_none_when_never_ahead() -> None:
    assert h3a.collapse_start([-1.0, -2.0, -3.0, -4.0, -5.0, -6.0]) is None


# --------------------------------------------------------------------------
# Gate arithmetic
# --------------------------------------------------------------------------


def _games(cat_flags, win_flags, cat_elig=None):
    cat_elig = cat_elig if cat_elig is not None else cat_flags
    g = {}
    for i, (a, e) in enumerate(zip(cat_flags, cat_elig)):
        g[i] = {
            "cohort": "catastrophe",
            "activates_by_boundary": a,
            "activation_turn": 10 if a else 999,
            "collapse_start": 200,
            "first_eligible": {"turn": 20} if e else None,
        }
    for j, a in enumerate(win_flags):
        g[100 + j] = {
            "cohort": "matched_win",
            "activates_by_boundary": a,
            "activation_turn": 10 if a else None,
            "collapse_start": None,
            "first_eligible": None,
        }
    return {"games": g}


def test_gate_thresholds_are_the_pinned_ones() -> None:
    r = h3a.gates(_games([True] * 8 + [False] * 2, [False] * 7))
    assert r["gate1_activation_by_150"]["pass"] is True   # exactly 8/10
    assert r["gate4_eligible_after_activation"]["pass"] is True  # 8 >= 6

    r = h3a.gates(_games([True] * 7 + [False] * 3, [False] * 7))
    assert r["gate1_activation_by_150"]["pass"] is False  # 7/10 fails


def test_gate3_allows_at_most_one_false_positive_of_seven() -> None:
    assert h3a.gates(_games([True] * 10, [True] + [False] * 6))["gate3_false_positive"]["pass"] is True
    assert h3a.gates(_games([True] * 10, [True] * 2 + [False] * 5))["gate3_false_positive"]["pass"] is False


def test_gate4_needs_six_of_ten() -> None:
    assert h3a.gates(_games([True] * 10, [False] * 7, [True] * 6 + [False] * 4))[
        "gate4_eligible_after_activation"
    ]["pass"] is True
    assert h3a.gates(_games([True] * 10, [False] * 7, [True] * 5 + [False] * 5))[
        "gate4_eligible_after_activation"
    ]["pass"] is False


# --------------------------------------------------------------------------
# Regression against the real package
# --------------------------------------------------------------------------


def test_real_package_reproduces_the_published_gate_verdict() -> None:
    maps, decisions, manifest = h3a.load()
    assert len(maps) == 17
    assert sum(len(v) for v in decisions.values()) == 5100
    assert manifest["sealed_data_included"] is False
    assert manifest["exact_ids_only"] is True

    result = h3a.analyze(maps, decisions, manifest, h3a.margins_by_game_from_sides())
    g = h3a.gates(result)
    assert g["gate1_activation_by_150"]["value"] == 9
    assert g["gate2_precedes_collapse"]["value"] == 10
    assert g["gate3_false_positive"]["value"] == 0
    assert g["gate4_eligible_after_activation"]["value"] == 9
    assert all(d["pass"] for d in g.values())


def test_no_matched_win_activates_before_the_boundary() -> None:
    """Gate 3's separation is the load-bearing half; assert it directly."""
    maps, decisions, manifest = h3a.load()
    result = h3a.analyze(maps, decisions, manifest, h3a.margins_by_game_from_sides())
    wins = [v for v in result["games"].values() if v["cohort"] == "matched_win"]
    assert len(wins) == 7
    assert not any(v["activates_by_boundary"] for v in wins)
