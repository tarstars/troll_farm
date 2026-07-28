"""Focused unit tests for cgauto.waste_sweep, on tiny synthetic decoded fixtures.

No test touches the on-disk corpus (data/raw/games, data/processed/*): every
DecodedGame here is built directly from hand-written states/trajectory/map rows via
``cgauto.waste_sweep.build_decoded_game``, matching the fixture-helper conventions
already used by tests/test_top_player_opening_analysis.py.  The two tests for the
comparative-baseline corpus-index helpers (``agent_game_ids``/``resident_game_ids``)
are the one exception that touches disk -- they point the module's ``GAMES_INDEX``
constant at a throwaway ``tmp_path`` file instead of the real corpus index, so they
stay hermetic and fast without depending on real corpus content/size.
"""

import json
from types import SimpleNamespace

import cgauto.waste_sweep as ws

# A small fully-open 7x7 map: own shack (player 0) at the center with all four doors
# walkable, opponent shack (player 1) in a corner with two walkable doors.  No water/
# iron/obstacles, so BFS distance always equals Manhattan distance -- this keeps the
# geometry in every test easy to hand-verify.
OPEN_MAP_ROWS = [
    ".......",
    ".......",
    ".......",
    "...0...",
    ".......",
    ".......",
    "......1",
]
OWN_SHACK = (3, 3)
OWN_DOORS = [(4, 3), (2, 3), (3, 4), (3, 2)]  # adjacent(OWN_SHACK), all walkable


def unit(unit_id, player, x, y, *, carry=None, stats=(1, 1, 1, 1)):
    ms, cc, hp, chop = stats
    return {
        "id": unit_id,
        "player": player,
        "x": x,
        "y": y,
        "ms": ms,
        "cc": cc,
        "hp": hp,
        "chop": chop,
        "carry": list(carry or [0] * 6),
    }


def plant(x, y, *, kind="PLUM", fruits=1, health=6):
    return {
        "type": kind,
        "x": x,
        "y": y,
        "stage": 4 + fruits,
        "size": 4,
        "fruits": fruits,
        "cooldown": 1,
        "health": health,
        "cooldown_effective": 8,
    }


def state(turn, units, plants=None, *, bank0=None, bank1=None):
    return {
        "resolved_turn": turn,
        "inventories": [list(bank0 or [0] * 6), list(bank1 or [0] * 6)],
        "units": units,
        "plants": list(plants or []),
    }


def commands_row(turn, *, commands0="", commands1=""):
    return {"t": turn, "inv0": [0] * 6, "inv1": [0] * 6, "commands0": commands0, "commands1": commands1}


def make_game(states, trajectory, *, me=0, map_rows=OPEN_MAP_ROWS, scores=(0, 0), ranks=(0, 1)):
    return ws.build_decoded_game(
        game_id=1,
        me=me,
        map_rows=map_rows,
        states=states,
        trajectory=trajectory,
        scores=scores,
        ranks=list(ranks),
    )


# ---------------------------------------------------------------------------
# Small pure helpers
# ---------------------------------------------------------------------------


def test_manhattan_distance():
    assert ws.manhattan((0, 0), (3, 4)) == 7
    assert ws.manhattan((2, 2), (2, 2)) == 0


def test_carried_value_ignores_iron_and_weights_wood_by_four():
    assert ws.carried_value([1, 2, 3, 4, 99, 5]) == 1 + 2 + 3 + 4 + 4 * 5


def test_training_cost_uses_worker_count_and_four_squared_stats():
    assert ws.training_cost(2, (2, 3, 1, 2)) == [6, 11, 3, 0, 6, 0]


def test_training_pay_indices_skips_iron_without_iron_terrain():
    assert ws.training_pay_indices(iron_present=False) == (0, 1, 2)
    assert ws.training_pay_indices(iron_present=True) == (0, 1, 2, ws.IRON_INDEX)


def test_training_affordable_respects_iron_presence():
    bank = [10, 10, 10, 10, 0, 0]  # no IRON banked at all
    talents = (1, 1, 1, 1)  # cost = [2, 2, 2, 0, 2, 0]
    assert ws.training_affordable(1, talents, bank, iron_present=False) is True
    assert ws.training_affordable(1, talents, bank, iron_present=True) is False


def test_training_blocked_checks_own_shack_occupancy():
    shack = (0, 0)
    assert ws.training_blocked([unit(0, 0, 0, 0)], shack) is True
    assert ws.training_blocked([unit(0, 0, 1, 0)], shack) is False


def test_crossover_turn_is_last_nonnegative_index_plus_one():
    assert ws._crossover_turn([0, 5, -3, -10]) == 2
    assert ws._crossover_turn([0, -1, -1]) == 1
    assert ws._crossover_turn([-1, -1, -1]) == 0


def test_causality_context_relation_to_crossover():
    # game.margin (the game's *final* margin) is deliberately different from any
    # margin_series entry, to keep "catastrophe" (a game-level property) visibly
    # distinct from the episode-level margin_before/after_episode readings.
    game = SimpleNamespace(margin_series=[0, 10, -5, -20, -30], crossover_turn=2, margin=-150, won=False)

    before = ws.causality_context(game, start_turn=1, end_turn=1)
    assert before["relation_to_crossover"] == "before_crossover"

    straddling = ws.causality_context(game, start_turn=2, end_turn=3)
    assert straddling["relation_to_crossover"] == "straddles_crossover"

    after = ws.causality_context(game, start_turn=3, end_turn=4)
    assert after["margin_before_episode"] == -5
    assert after["margin_after_episode"] == -30
    assert after["margin_delta_during_episode"] == -25
    assert after["relation_to_crossover"] == "after_crossover"
    assert after["catastrophe"] is True


# ---------------------------------------------------------------------------
# RunTracker
# ---------------------------------------------------------------------------


def test_run_tracker_extends_while_marked_and_closes_on_sweep():
    tracker = ws.RunTracker()
    tracker.mark("a", 1, {"x": 1})
    tracker.mark("a", 2, {"x": 2})
    finished = tracker.sweep(active_keys=set())  # "a" not re-marked -> the run closes
    assert len(finished) == 1
    assert finished[0]["start"] == 1
    assert finished[0]["end"] == 2
    assert finished[0]["details"] == [{"x": 1}, {"x": 2}]
    assert tracker.sweep(active_keys=set()) == []  # nothing left open


def test_run_tracker_flush_returns_still_open_runs():
    tracker = ws.RunTracker()
    tracker.mark("b", 3)
    assert tracker.flush() == [{"key": "b", "start": 3, "end": 3, "details": []}]
    assert tracker.flush() == []


# ---------------------------------------------------------------------------
# legal_productive_actions / command_precondition_met
# ---------------------------------------------------------------------------


def test_legal_actions_harvest_needs_ripe_fruit_capacity_and_harvest_power():
    cell = (2, 0)
    walkable = {cell}
    u = unit(0, 0, *cell, stats=(1, 1, 1, 0))
    ripe = {cell: plant(*cell, fruits=2)}
    assert ws.legal_productive_actions(u, ripe, [0] * 6, shack=(9, 9), walkable=walkable) == {"HARVEST"}

    zero_hp = unit(0, 0, *cell, stats=(1, 1, 0, 0))
    assert ws.legal_productive_actions(zero_hp, ripe, [0] * 6, shack=(9, 9), walkable=walkable) == set()


def test_legal_actions_chop_requires_free_capacity():
    """Regression test (B3.6 false positive, waste_sweep.py:371-372): a full-capacity
    chopper legitimately gets no wood -- both the engine (sim/engine.py apply_chop only
    pays choppers with free capacity when the tree dies this turn) and the live bot's
    own chop_candidates() (rust/src/bin/yamo_orchard_live.rs, which bails out whenever
    ``unit.free_capacity() <= 0``) agree CHOP is not worth doing once a unit is full.
    So CHOP must not be reported as a legal *productive* action for a unit with zero
    free carry capacity, even though the command itself still deals damage and remains
    legal at the command-precondition level (see the paired test below)."""

    cell = (2, 0)
    full = unit(0, 0, *cell, carry=[0, 0, 0, 0, 0, 3], stats=(1, 3, 0, 2))  # cc=3, carry=3: free=0
    ripe = {cell: plant(*cell, fruits=0)}  # no fruit -- CHOP is the only candidate action
    assert ws.legal_productive_actions(full, ripe, [0] * 6, shack=(9, 9), walkable={cell}) == set()

    has_room = unit(0, 0, *cell, carry=[0, 0, 0, 0, 0, 1], stats=(1, 3, 0, 2))  # cc=3, carry=1: free=2
    assert ws.legal_productive_actions(has_room, ripe, [0] * 6, shack=(9, 9), walkable={cell}) == {"CHOP"}


def test_command_precondition_chop_ignores_capacity_unlike_legal_productive_actions():
    """CHOP always deals damage regardless of capacity (apply_chop applies
    ``plant.health -= u.chop`` unconditionally for every chopper standing on the cell);
    only the wood *payout*, on a kill, is capacity-gated.  So unlike
    legal_productive_actions' CHOP gate (B3.6, tested above), this precondition -- used
    by repeated_failed_command to decide whether a command had *any* state effect --
    must NOT require free capacity: a full-capacity chopper's repeated CHOP command is
    still doing something (chipping the tree down), not a no-op."""

    cell = (2, 0)
    ripe = {cell: plant(*cell)}
    full = unit(0, 0, *cell, carry=[0, 0, 0, 0, 0, 3], stats=(1, 3, 1, 2))  # cc=3, carry=3: free=0
    assert ws.command_precondition_met("CHOP", ["CHOP", "0"], full, ripe, [0] * 6, (9, 9), set(), {cell}) is True


def test_legal_actions_plant_requires_walkable_empty_cell_and_carried_seed():
    cell = (2, 0)
    carrying_seed = unit(0, 0, *cell, carry=[1, 0, 0, 0, 0, 0], stats=(1, 1, 1, 0))
    assert ws.legal_productive_actions(carrying_seed, {}, [0] * 6, shack=(9, 9), walkable={cell}) == {"PLANT"}

    not_walkable = ws.legal_productive_actions(carrying_seed, {}, [0] * 6, shack=(9, 9), walkable=set())
    assert "PLANT" not in not_walkable


def test_legal_actions_pick_and_bank_require_being_near_shack():
    shack = (0, 0)
    near = unit(0, 0, 0, 1, carry=[0, 0, 0, 0, 0, 2], stats=(1, 3, 1, 0))
    bank_with_seed = [3, 0, 0, 0, 0, 0]
    assert ws.legal_productive_actions(near, {}, bank_with_seed, shack=shack, walkable={(0, 1)}) == {
        "PICK",
        "BANK",
    }

    far = unit(0, 0, 5, 5, carry=[0, 0, 0, 0, 0, 2], stats=(1, 3, 1, 0))
    assert ws.legal_productive_actions(far, {}, bank_with_seed, shack=shack, walkable={(5, 5)}) == set()


def test_command_precondition_chop_needs_plant_and_nonzero_chop_power():
    cell = (2, 0)
    ripe = {cell: plant(*cell)}
    weak = unit(0, 0, *cell, stats=(1, 1, 1, 0))
    strong = unit(0, 0, *cell, stats=(1, 1, 1, 3))
    assert ws.command_precondition_met("CHOP", ["CHOP", "0"], weak, ripe, [0] * 6, (9, 9), set(), {cell}) is False
    assert ws.command_precondition_met("CHOP", ["CHOP", "0"], strong, ripe, [0] * 6, (9, 9), set(), {cell}) is True


def test_command_precondition_pick_checks_bank_stock():
    shack = (0, 0)
    near = unit(0, 0, 0, 1, stats=(1, 3, 1, 0))
    assert (
        ws.command_precondition_met("PICK", ["PICK", "0", "PLUM"], near, {}, [1, 0, 0, 0, 0, 0], shack, set(), set())
        is True
    )
    assert (
        ws.command_precondition_met("PICK", ["PICK", "0", "PLUM"], near, {}, [0, 0, 0, 0, 0, 0], shack, set(), set())
        is False
    )


def test_command_precondition_mine_checks_adjacency_and_chop_power():
    ore = {(3, 0)}
    adjacent_unit = unit(0, 0, 2, 0, stats=(1, 3, 1, 2))
    far_unit = unit(0, 0, 5, 5, stats=(1, 3, 1, 2))
    assert ws.command_precondition_met("MINE", ["MINE", "0"], adjacent_unit, {}, [0] * 6, (9, 9), ore, set()) is True
    assert ws.command_precondition_met("MINE", ["MINE", "0"], far_unit, {}, [0] * 6, (9, 9), ore, set()) is False


def test_command_precondition_move_is_not_covered_here():
    u = unit(0, 0, 0, 0)
    assert ws.command_precondition_met("MOVE", ["MOVE", "0", "1", "1"], u, {}, [0] * 6, (9, 9), set(), set()) is None


# ---------------------------------------------------------------------------
# Detector 1: idle_with_work
# ---------------------------------------------------------------------------


def test_idle_with_work_flags_wait_run_with_legal_harvest_then_closes_on_harvest():
    cell = (2, 3)
    idle_unit = unit(0, 0, *cell, stats=(1, 1, 1, 0))
    ripe = plant(*cell, kind="BANANA", fruits=2)
    states = [
        state(0, [idle_unit], [ripe]),
        state(1, [idle_unit], [ripe]),
        state(2, [idle_unit], [ripe]),
        state(3, [unit(0, 0, *cell, carry=[0, 0, 0, 1, 0, 0], stats=(1, 1, 1, 0))], [dict(ripe, fruits=1)]),
    ]
    trajectory = [
        commands_row(1, commands0="WAIT"),
        commands_row(2, commands0="WAIT"),
        commands_row(3, commands0="HARVEST 0"),
    ]
    game = make_game(states, trajectory)

    episodes = ws.detect_idle_with_work(game)

    assert len(episodes) == 1
    episode = episodes[0]
    assert episode["unit_id"] == 0
    assert (episode["start_turn"], episode["end_turn"], episode["duration"]) == (1, 2, 2)
    assert episode["detail"]["legal_actions_seen"] == ["HARVEST"]
    assert episode["detail"]["verb_counts"] == {"WAIT": 2}


def test_idle_with_work_flags_non_productive_move():
    cell = (0, 0)  # walkable, empty, and far from the shack -- isolates PLANT from BANK
    carrying_seed = unit(0, 0, *cell, carry=[1, 0, 0, 0, 0, 0], stats=(1, 1, 1, 0))
    states = [
        state(0, [carrying_seed]),
        state(1, [unit(0, 0, 1, 0, carry=[1, 0, 0, 0, 0, 0], stats=(1, 1, 1, 0))]),
    ]
    trajectory = [commands_row(1, commands0="MOVE 0 1 0")]
    game = make_game(states, trajectory)

    episodes = ws.detect_idle_with_work(game)

    assert len(episodes) == 1
    assert episodes[0]["detail"]["legal_actions_seen"] == ["PLANT"]
    assert episodes[0]["detail"]["verb_counts"] == {"MOVE": 1}


def test_idle_with_work_empty_when_nothing_legal_is_available():
    stranded = unit(0, 0, 0, 1, stats=(1, 1, 1, 0))  # empty-handed, far from shack, no plant nearby
    states = [state(0, [stranded]), state(1, [stranded])]
    trajectory = [commands_row(1, commands0="WAIT")]
    game = make_game(states, trajectory)

    assert ws.detect_idle_with_work(game) == []


# ---------------------------------------------------------------------------
# Detector 2: unbanked_carry
# ---------------------------------------------------------------------------


def test_unbanked_carry_flags_sustained_loitering_at_a_door():
    door = OWN_DOORS[0]
    loiterer = unit(0, 0, *door, carry=[0, 0, 0, 0, 0, 1], stats=(1, 3, 1, 1))
    states = [state(0, [loiterer])]
    trajectory = []
    for turn in range(1, ws.UNBANKED_CARRY_MIN_RUN + 1):
        states.append(state(turn, [loiterer]))
        trajectory.append(commands_row(turn, commands0="WAIT"))
    game = make_game(states, trajectory)

    episodes = ws.detect_unbanked_carry(game)

    assert len(episodes) == 1
    episode = episodes[0]
    assert (episode["start_turn"], episode["end_turn"]) == (1, ws.UNBANKED_CARRY_MIN_RUN)
    assert episode["duration"] == ws.UNBANKED_CARRY_MIN_RUN
    assert episode["detail"]["closest_door_distance"] == 0
    assert episode["detail"]["carried_value_at_end"] == 4


def test_unbanked_carry_below_threshold_is_not_flagged():
    door = OWN_DOORS[0]
    loiterer = unit(0, 0, *door, carry=[0, 0, 0, 0, 0, 1], stats=(1, 3, 1, 1))
    states = [state(0, [loiterer])]
    trajectory = []
    for turn in range(1, ws.UNBANKED_CARRY_MIN_RUN):  # one turn short of the threshold
        states.append(state(turn, [loiterer]))
        trajectory.append(commands_row(turn, commands0="WAIT"))
    game = make_game(states, trajectory)

    assert ws.detect_unbanked_carry(game) == []


def test_unbanked_carry_ignores_a_long_distance_commute_that_banks_on_arrival():
    """Regression test: a unit that spends many turns walking home from far away
    (genuinely out of door range almost the whole time) and then banks immediately on
    arrival must not be misclassified as loitering near its own door."""

    far_cell = (6, 0)  # Manhattan distance 5 to the nearest own door -- well outside radius 2
    near_door = OWN_DOORS[1]
    states = [state(0, [unit(0, 0, *far_cell, carry=[0, 0, 0, 0, 0, 1], stats=(3, 3, 1, 1))])]
    trajectory = []
    for turn in range(1, 8):
        states.append(state(turn, [unit(0, 0, *far_cell, carry=[0, 0, 0, 0, 0, 1], stats=(3, 3, 1, 1))]))
        trajectory.append(commands_row(turn, commands0="WAIT"))
    states.append(state(8, [unit(0, 0, *near_door, carry=[0, 0, 0, 0, 0, 1], stats=(3, 3, 1, 1))]))
    trajectory.append(commands_row(8, commands0=f"MOVE 0 {near_door[0]} {near_door[1]}"))
    states.append(state(9, [unit(0, 0, *near_door, carry=[0, 0, 0, 0, 0, 0], stats=(3, 3, 1, 1))]))
    trajectory.append(commands_row(9, commands0="DROP 0"))
    game = make_game(states, trajectory)

    assert ws.detect_unbanked_carry(game) == []


# ---------------------------------------------------------------------------
# Detector 3: harvest_slack
# ---------------------------------------------------------------------------


def test_harvest_slack_flags_persistent_ripe_fruit_near_a_capable_worker():
    cell = (2, 3)
    nearby = unit(0, 0, 1, 3, stats=(1, 1, 1, 0))  # Manhattan distance 1 from cell, hp=1
    ripe = plant(*cell, kind="PLUM", fruits=2)
    states = [state(0, [nearby], [ripe])]
    trajectory = []
    for turn in range(1, ws.HARVEST_SLACK_MIN_RUN + 1):
        states.append(state(turn, [nearby], [ripe]))
        trajectory.append(commands_row(turn, commands0="WAIT"))
    game = make_game(states, trajectory)

    episodes = ws.detect_harvest_slack(game)

    assert len(episodes) == 1
    episode = episodes[0]
    assert episode["cell"] == list(cell)
    assert episode["duration"] == ws.HARVEST_SLACK_MIN_RUN
    assert episode["detail"]["fruits_at_start"] == 2
    assert episode["detail"]["fruits_at_end"] == 2
    assert episode["detail"]["any_capable_worker_seen"] is True


def test_harvest_slack_below_threshold_is_not_flagged():
    cell = (2, 3)
    nearby = unit(0, 0, 1, 3, stats=(1, 1, 1, 0))
    ripe = plant(*cell, fruits=2)
    states = [state(0, [nearby], [ripe])]
    trajectory = []
    for turn in range(1, ws.HARVEST_SLACK_MIN_RUN):  # one short of the threshold
        states.append(state(turn, [nearby], [ripe]))
        trajectory.append(commands_row(turn, commands0="WAIT"))
    game = make_game(states, trajectory)

    assert ws.detect_harvest_slack(game) == []


def test_harvest_slack_marks_incapable_only_worker_distinctly():
    cell = (2, 3)
    chopper = unit(0, 0, 1, 3, stats=(1, 1, 0, 2))  # harvest_power 0 -- can never harvest
    ripe = plant(*cell, fruits=2)
    states = [state(0, [chopper], [ripe])]
    trajectory = []
    for turn in range(1, ws.HARVEST_SLACK_MIN_RUN + 1):
        states.append(state(turn, [chopper], [ripe]))
        trajectory.append(commands_row(turn, commands0="WAIT"))
    game = make_game(states, trajectory)

    episodes = ws.detect_harvest_slack(game)

    assert len(episodes) == 1
    assert episodes[0]["detail"]["any_capable_worker_seen"] is False


def test_harvest_slack_marks_full_capacity_only_worker_as_not_capable():
    """Regression test, same bug class as B3.6: a worker with harvest_power >= 1 but
    zero free carry capacity cannot actually harvest anything -- apply_harvest requires
    free capacity (``u.total < u.cc``) for even the first fruit -- so it must not count
    as a "capable" worker just because its harvest_power stat alone looks sufficient."""

    cell = (2, 3)
    full_carry = unit(0, 0, 1, 3, carry=[0, 0, 0, 3, 0, 0], stats=(1, 3, 1, 0))  # hp=1, free=0
    ripe = plant(*cell, fruits=2)
    states = [state(0, [full_carry], [ripe])]
    trajectory = []
    for turn in range(1, ws.HARVEST_SLACK_MIN_RUN + 1):
        states.append(state(turn, [full_carry], [ripe]))
        trajectory.append(commands_row(turn, commands0="WAIT"))
    game = make_game(states, trajectory)

    episodes = ws.detect_harvest_slack(game)

    assert len(episodes) == 1
    assert episodes[0]["detail"]["any_capable_worker_seen"] is False


def test_harvest_slack_excludes_strictly_opponent_territory():
    cell = (6, 5)  # one BFS step from the opponent's shack, far from the resident's
    on_top_of_it = unit(0, 0, *cell, stats=(1, 1, 1, 0))
    ripe = plant(*cell, fruits=2)
    states = [state(0, [on_top_of_it], [ripe])]
    trajectory = []
    for turn in range(1, ws.HARVEST_SLACK_MIN_RUN + 1):
        states.append(state(turn, [on_top_of_it], [ripe]))
        trajectory.append(commands_row(turn, commands0="WAIT"))
    game = make_game(states, trajectory)

    assert ws.detect_harvest_slack(game) == []


# ---------------------------------------------------------------------------
# Detector 4: door_queue
# ---------------------------------------------------------------------------


def test_door_queue_flags_clustered_carriers_that_do_not_all_bank():
    door = OWN_DOORS[0]
    at_door = unit(0, 0, *door, carry=[0, 0, 0, 0, 0, 1], stats=(1, 1, 1, 0))
    beside_door = unit(1, 0, door[0] - 1, door[1], carry=[0, 0, 0, 0, 0, 1], stats=(1, 1, 1, 0))
    states = [state(0, [at_door, beside_door])]
    trajectory = []
    for turn in range(1, 3):
        states.append(state(turn, [at_door, beside_door]))  # neither ever drops
        trajectory.append(commands_row(turn, commands0="WAIT;WAIT"))
    game = make_game(states, trajectory)

    episodes = ws.detect_door_queue(game)

    assert len(episodes) == 1
    episode = episodes[0]
    assert episode["door"] == list(door)
    assert set(episode["detail"]["units_involved"]) == {0, 1}
    assert episode["detail"]["turns_with_zero_banked"] == 2


def test_door_queue_plant_spending_last_seed_is_not_mistaken_for_banking():
    """Regression test: PLANT can zero out a unit's carry (spending its one seed)
    without ever touching the bank -- that must not count as "banked"."""

    door = OWN_DOORS[0]
    planter = unit(0, 0, *door, carry=[1, 0, 0, 0, 0, 0], stats=(1, 1, 1, 0))
    bystander = unit(1, 0, door[0] - 1, door[1], carry=[0, 0, 0, 0, 0, 1], stats=(1, 1, 1, 0))
    states = [
        state(0, [planter, bystander]),
        state(
            1,
            [
                unit(0, 0, *door, carry=[0, 0, 0, 0, 0, 0], stats=(1, 1, 1, 0)),
                bystander,
            ],
            [plant(*door, kind="PLUM", fruits=0)],
        ),
    ]
    trajectory = [commands_row(1, commands0="PLANT 0 PLUM;WAIT")]
    game = make_game(states, trajectory)

    episodes = ws.detect_door_queue(game)

    assert len(episodes) == 1
    assert episodes[0]["detail"]["turns_with_zero_banked"] == 1
    assert episodes[0]["detail"]["turns_with_partial_banked"] == 0


def test_door_queue_not_flagged_when_every_carrier_banks():
    door = OWN_DOORS[0]
    at_door = unit(0, 0, *door, carry=[0, 0, 0, 0, 0, 1], stats=(1, 1, 1, 0))
    beside_door = unit(1, 0, door[0] - 1, door[1], carry=[0, 0, 0, 0, 0, 1], stats=(1, 1, 1, 0))
    states = [
        state(0, [at_door, beside_door]),
        state(
            1,
            [
                unit(0, 0, *door, carry=[0] * 6, stats=(1, 1, 1, 0)),
                unit(1, 0, door[0] - 1, door[1], carry=[0] * 6, stats=(1, 1, 1, 0)),
            ],
        ),
    ]
    trajectory = [commands_row(1, commands0="DROP 0;DROP 1")]
    game = make_game(states, trajectory)

    assert ws.detect_door_queue(game) == []


def test_door_queue_not_flagged_with_a_single_carrier():
    door = OWN_DOORS[0]
    lone = unit(0, 0, *door, carry=[0, 0, 0, 0, 0, 1], stats=(1, 1, 1, 0))
    states = [state(0, [lone]), state(1, [lone])]
    trajectory = [commands_row(1, commands0="WAIT")]
    game = make_game(states, trajectory)

    assert ws.detect_door_queue(game) == []


# ---------------------------------------------------------------------------
# Detector 5: late_train_window
# ---------------------------------------------------------------------------


def test_late_train_window_flags_a_neglected_affordable_stretch():
    talents = (1, 1, 1, 1)
    afford = [5, 5, 5, 5, 0, 0]
    starter = unit(0, 0, 0, 0, stats=(1, 1, 1, 1))
    states = [state(0, [starter], bank0=afford)]
    trajectory = []
    for turn in range(1, ws.LATE_TRAIN_MIN_RUN + 1):
        states.append(state(turn, [starter], bank0=afford))
        trajectory.append(commands_row(turn, commands0="WAIT"))
    trained_turn = ws.LATE_TRAIN_MIN_RUN + 1
    states.append(state(trained_turn, [starter, unit(1, 0, 0, 0, stats=talents)], bank0=afford))
    trajectory.append(commands_row(trained_turn, commands0="TRAIN 1 1 1 1"))
    game = make_game(states, trajectory)

    assert game.train_events == [{"turn": trained_turn, "talents": talents, "n_before": 1}]
    episodes = ws.detect_late_train_window(game)

    assert len(episodes) == 1
    episode = episodes[0]
    assert (episode["start_turn"], episode["end_turn"]) == (1, ws.LATE_TRAIN_MIN_RUN)
    assert episode["detail"]["reference_talents"] == list(talents)
    assert episode["detail"]["own_workers_during_window"] == 1


def test_late_train_window_not_flagged_when_blocked_by_shack_occupancy():
    """Regression test, same bug class as B3.6: a turn where TRAIN is bank-affordable
    but an own unit sits on the shack cell must not count as a neglected window --
    apply_train's own second guard (``any(u.pos == game.shacks[player] ...)``) means
    TRAIN would have failed anyway, just like repeated_failed_command's TRAIN check
    already correctly ANDs training_affordable with ``not training_blocked``."""

    talents = (1, 1, 1, 1)
    afford = [5, 5, 5, 5, 0, 0]
    blocker = unit(0, 0, *OWN_SHACK, stats=(1, 1, 1, 1))  # sits ON the shack the whole window
    states = [state(0, [blocker], bank0=afford)]
    trajectory = []
    for turn in range(1, ws.LATE_TRAIN_MIN_RUN + 1):
        states.append(state(turn, [blocker], bank0=afford))
        trajectory.append(commands_row(turn, commands0="WAIT"))
    trained_turn = ws.LATE_TRAIN_MIN_RUN + 1
    states.append(state(trained_turn, [blocker, unit(1, 0, *OWN_SHACK, stats=talents)], bank0=afford))
    trajectory.append(commands_row(trained_turn, commands0="TRAIN 1 1 1 1"))
    game = make_game(states, trajectory)

    assert game.train_events == [{"turn": trained_turn, "talents": talents, "n_before": 1}]
    assert ws.detect_late_train_window(game) == []


def test_late_train_window_empty_when_the_lag_is_short():
    talents = (1, 1, 1, 1)
    not_afford = [0] * 6
    afford = [5, 5, 5, 5, 0, 0]
    starter = unit(0, 0, 0, 0, stats=(1, 1, 1, 1))
    states = [
        state(0, [starter], bank0=not_afford),
        state(1, [starter], bank0=afford),  # becomes affordable going into turn 2
        state(2, [starter, unit(1, 0, 0, 0, stats=talents)], bank0=afford),  # trains on the very next turn
    ]
    trajectory = [
        commands_row(1, commands0="WAIT"),
        commands_row(2, commands0="TRAIN 1 1 1 1"),
    ]
    game = make_game(states, trajectory)

    assert ws.detect_late_train_window(game) == []


def test_late_train_window_empty_when_the_resident_never_trains():
    afford = [5, 5, 5, 5, 0, 0]
    starter = unit(0, 0, 0, 0, stats=(1, 1, 1, 1))
    states = [state(0, [starter], bank0=afford)]
    trajectory = []
    for turn in range(1, ws.LATE_TRAIN_MIN_RUN + 3):
        states.append(state(turn, [starter], bank0=afford))
        trajectory.append(commands_row(turn, commands0="WAIT"))
    game = make_game(states, trajectory)

    assert game.train_events == []
    assert ws.detect_late_train_window(game) == []


# ---------------------------------------------------------------------------
# Detector 6: repeated_failed_command
# ---------------------------------------------------------------------------


def test_repeated_failed_command_flags_three_identical_failures():
    stranded = unit(0, 0, 0, 0, stats=(1, 1, 1, 1))  # no plant anywhere -- HARVEST always fails
    states = [state(0, [stranded])]
    trajectory = []
    for turn in range(1, ws.REPEATED_FAILED_COMMAND_MIN_RUN + 1):
        states.append(state(turn, [stranded]))
        trajectory.append(commands_row(turn, commands0="HARVEST 0"))
    game = make_game(states, trajectory)

    episodes = ws.detect_repeated_failed_command(game)

    assert len(episodes) == 1
    episode = episodes[0]
    assert episode["unit_id"] == 0
    assert episode["detail"]["command"] == "HARVEST 0"
    assert episode["detail"]["repeat_count"] == ws.REPEATED_FAILED_COMMAND_MIN_RUN
    assert (episode["start_turn"], episode["end_turn"]) == (1, ws.REPEATED_FAILED_COMMAND_MIN_RUN)


def test_repeated_failed_command_below_threshold_is_not_flagged():
    stranded = unit(0, 0, 0, 0, stats=(1, 1, 1, 1))
    states = [state(0, [stranded])]
    trajectory = []
    for turn in range(1, ws.REPEATED_FAILED_COMMAND_MIN_RUN):  # one short
        states.append(state(turn, [stranded]))
        trajectory.append(commands_row(turn, commands0="HARVEST 0"))
    game = make_game(states, trajectory)

    assert ws.detect_repeated_failed_command(game) == []


def test_repeated_failed_command_resets_when_the_command_changes():
    stranded = unit(0, 0, 0, 0, stats=(1, 1, 1, 1))
    states = [state(0, [stranded])]
    trajectory = []
    for turn, command in ((1, "HARVEST 0"), (2, "HARVEST 0"), (3, "CHOP 0"), (4, "CHOP 0")):
        states.append(state(turn, [stranded]))
        trajectory.append(commands_row(turn, commands0=command))
    game = make_game(states, trajectory)

    assert ws.detect_repeated_failed_command(game) == []


def test_repeated_failed_command_wait_is_never_a_failure():
    stranded = unit(0, 0, 0, 0, stats=(1, 1, 1, 1))
    states = [state(0, [stranded])]
    trajectory = []
    for turn in range(1, 6):
        states.append(state(turn, [stranded]))
        trajectory.append(commands_row(turn, commands0="WAIT"))
    game = make_game(states, trajectory)

    assert ws.detect_repeated_failed_command(game) == []


def test_repeated_failed_command_covers_the_train_pseudo_slot():
    off_shack = unit(0, 0, 1, 1, stats=(1, 1, 1, 1))  # not on the shack cell -- not "blocked"
    poor = [0, 0, 0, 0, 0, 0]
    states = [state(0, [off_shack], bank0=poor)]
    trajectory = []
    for turn in range(1, ws.REPEATED_FAILED_COMMAND_MIN_RUN + 1):
        states.append(state(turn, [off_shack], bank0=poor))
        trajectory.append(commands_row(turn, commands0="TRAIN 1 1 1 1"))
    game = make_game(states, trajectory)

    episodes = ws.detect_repeated_failed_command(game)

    assert len(episodes) == 1
    episode = episodes[0]
    assert episode["unit_id"] is None
    assert episode["detail"]["command"] == "TRAIN 1 1 1 1"
    assert episode["detail"]["repeat_count"] == ws.REPEATED_FAILED_COMMAND_MIN_RUN


# ---------------------------------------------------------------------------
# Comparative-baseline support: any-agent seat lookup and corpus-index filtering
# ---------------------------------------------------------------------------


def test_agent_seat_matches_by_agent_id_and_returns_none_when_absent():
    game = {"agents": [{"index": 0, "agentId": 111}, {"index": 1, "agentId": 222}]}
    assert ws.agent_seat(game, 111) == 0
    assert ws.agent_seat(game, 222) == 1
    assert ws.agent_seat(game, 999) is None
    assert ws.agent_seat({}, 111) is None


def test_agent_game_ids_filters_by_agent_and_resident_delegates(tmp_path, monkeypatch):
    index = tmp_path / "games.jsonl"
    rows = [
        {"gameId": 1, "players": [{"agentId": 111}, {"agentId": 222}]},
        {"gameId": 2, "players": [{"agentId": 333}, {"agentId": ws.RESIDENT_AGENT_ID}]},
        {"gameId": 3, "players": [{"agentId": 111}, {"agentId": 444}]},
    ]
    index.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    monkeypatch.setattr(ws, "GAMES_INDEX", index)

    assert ws.agent_game_ids(111) == [1, 3]
    assert ws.agent_game_ids(222) == [1]
    assert ws.agent_game_ids(999) == []
    assert ws.resident_game_ids() == ws.agent_game_ids(ws.RESIDENT_AGENT_ID) == [2]


# ---------------------------------------------------------------------------
# Aggregation glue
# ---------------------------------------------------------------------------


def test_summarize_detector_buckets_wins_losses_and_catastrophes():
    def episode(game_id, duration, *, won, margin):
        return {
            "game_id": game_id,
            "duration": duration,
            "start_turn": 1,
            "causality": {"game_won": won, "game_margin": margin, "catastrophe": margin <= ws.CATASTROPHE_MARGIN},
        }

    games_meta = [
        {"game_id": 1, "margin": 50, "won": True},
        {"game_id": 2, "margin": -150, "won": False},
        {"game_id": 3, "margin": 0, "won": False},
    ]
    episodes_by_game = {
        1: [episode(1, 2, won=True, margin=50)],
        2: [episode(2, 9, won=False, margin=-150), episode(2, 1, won=False, margin=-150)],
        3: [],
    }

    summary = ws.summarize_detector("idle_with_work", games_meta, episodes_by_game)

    assert summary["games_swept"] == 3
    assert summary["total_episodes"] == 3
    assert summary["games_with_episode"] == 2
    assert summary["wins"] == {"episodes": 1, "games_with_episode": 1}
    assert summary["losses"] == {"episodes": 2, "games_with_episode": 1}
    assert summary["catastrophes"] == {"episodes": 2, "games_with_episode": 1}
    assert summary["worst_episodes"][0]["duration"] == 9
