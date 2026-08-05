#!/usr/bin/env python3
"""CONVERSION_RACE_ORACLE — the single named conversion-race oracle.

Spec text (invariant-spec-2026-08-04.md, Revision 2026-08-05, integrator
ruling in the round-3 host review
data/analysis/live-agent-6553250/banana-restoration-r2-round3-host-review-2026-08-05.md
and ACK
coordination/messages/local_codex_1/20260805T143001Z-20260802-banana-restoration-r2-ack.md):

  CONVERSION_RACE_ORACLE decides the I-10a convert-vs-abandon branch and the
  D-8 conversion exemption. It is a deterministic pure function evaluated in
  ONE absolute time frame anchored at the decision turn t (the turn whose
  state S_t is being acted on).

  Inputs: the walkable set; the mother cell c; the mother plant state at t
  (size, health, fruits, cooldown); the resident's cell, movement speed and
  chop power at t; every opponent unit's cell, movement speed and harvest
  power at t; near-water flag of c.

  Outputs: feasible (bool), completion_turn (absolute), and
  opponent_harvest_turn (absolute).

  Semantics (exact travel + growth + fruit + action timing; the state at
  turn u+1 results from the commands of turn u followed by the growth tick,
  i.e. state(t+k) of an unchopped tree = predict_tree(S_t.plant, k)):

  - eta_res = ceil(bfs_dist(walkable, resident_cell, c) / speed): the
    resident's first CHOP on c is executable at turn t + eta_res.
  - exact_chops = growth-aware chop count from the ARRIVAL-state tree
    predict_tree(plant, eta_res), via chop_outcome arithmetic (each turn the
    chop lands first, then the cooldown ticks and a size-below-4 tree at
    cooldown 0 grows +1 size / +1 health and resets its cooldown).
  - completion_turn = t + eta_res + exact_chops - 1: the absolute turn on
    which the FINAL chop lands (the tree is gone in state
    completion_turn + 1).
  - eta_opp = min over opponent units with harvest_power > 0 of
    ceil(bfs_dist(walkable, unit_cell, c) / speed) (UNREACHABLE = 10000 if
    none); the earliest turn an opponent can STAND on c is t + eta_opp.
  - first_fruit_turn = t + r where r = min{k >= 0 :
    predict_tree(plant, k).fruits > 0} under unchopped natural growth
    (r = 0 if fruits > 0 at t; UNREACHABLE if fruit never appears).
  - opponent_harvest_turn = max(t + eta_opp, first_fruit_turn): HARVEST is
    executable only when standing on c with fruits > 0, so the opponent's
    earliest EXECUTABLE HARVEST needs both arrival and ripeness. Arrival
    alone is NOT loss; ripeness alone is NOT loss.
  - feasible iff completion_turn < opponent_harvest_turn, STRICT: the
    equal-turn race (final chop and first executable harvest on the same
    turn) is contested and conceded to the opponent, consistent with I-7
    tie handling. Unreachable travel, zero chop power, or an unfellable
    tree make feasible False.

  This oracle — under this one name — drives all four artifacts: the I-10a
  convert clause of the spec, the candidate implementation, regression R-3,
  and the D-8 exemption in trace_detectors. Neither predicted-cooldown
  ripen proxies nor arrival-only deadlines are permitted anywhere.

Deterministic, stdlib only. The growth/chop arithmetic below mirrors the
candidate's MoisanBot::predict_tree / MoisanBot::chop_outcome
(research-banana-r2.rs) and is cross-checked against trace_detectors'
mirrors by this module's self-test (python3 conversion_race_oracle.py).
"""

from __future__ import annotations

from collections import deque

UNREACHABLE = 10000            # spec sec. 0: unreachable ETA sentinel

BANANA_PLANT_COOLDOWN = 6      # game::rules plant_cooldown(Banana)
BANANA_WATER_BOOST = 2         # game::rules water_boost(Banana)
BANANA_HEALTH_SLOPE = 1        # tree_health_params(Banana).1

_FRUIT_HORIZON = 400           # > TOTAL_TURNS = 300: growth search bound


def ceil_div(a: int, b: int) -> int:
    """MoisanBot::ceil_div — b <= 0 yields the UNREACHABLE sentinel."""
    if b <= 0:
        return UNREACHABLE
    return -(-a // b)


def bfs_distances(walkable, sources):
    """4-neighbour BFS distance map over ``walkable`` from ``sources``."""
    walkable = set(walkable)
    dist = {}
    queue = deque()
    for cell in sources:
        if cell not in dist:
            dist[cell] = 0
            queue.append(cell)
    while queue:
        (x, y) = queue.popleft()
        d = dist[(x, y)]
        for nxt in ((x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)):
            if nxt in walkable and nxt not in dist:
                dist[nxt] = d + 1
                queue.append(nxt)
    return dist


def effective_cooldown(near_water: bool) -> int:
    return (BANANA_PLANT_COOLDOWN - BANANA_WATER_BOOST if near_water
            else BANANA_PLANT_COOLDOWN)


def predict_tree(size, health, fruits, cooldown, turns, near_water=False):
    """Growth-only forward simulation over ``turns`` growth ticks (mirror of
    MoisanBot::predict_tree). Returns (size, health, fruits, cooldown)."""
    for _ in range(turns):
        if cooldown > 0:
            cooldown -= 1
        if cooldown == 0 and health > 0:
            if size < 4:
                size += 1
                health += BANANA_HEALTH_SLOPE
                cooldown = effective_cooldown(near_water)
            elif fruits < 3:
                fruits += 1
                cooldown = effective_cooldown(near_water)
    return size, health, fruits, cooldown


def exact_chop_turns(size, health, cooldown, chop_power, near_water=False):
    """Growth-aware chop-turn count to fell a banana tree (mirror of
    MoisanBot::chop_outcome): the chop lands first, then the cooldown ticks
    and a size-below-4 tree at cooldown 0 grows. UNREACHABLE if
    chop_power <= 0 or the tree survives 100 chop turns."""
    if chop_power <= 0:
        return UNREACHABLE
    for turns in range(1, 101):
        health -= chop_power
        if health <= 0:
            return turns
        if cooldown > 0:
            cooldown -= 1
        if cooldown == 0 and size < 4:
            size += 1
            health += BANANA_HEALTH_SLOPE
            cooldown = effective_cooldown(near_water)
    return UNREACHABLE


def first_fruit_delay(size, health, fruits, cooldown, near_water=False):
    """r = min{k >= 0 : predict_tree(plant, k).fruits > 0} under unchopped
    natural growth; 0 if fruits are present now, UNREACHABLE if no fruit
    appears within the horizon (dead or unfellable states included)."""
    if fruits > 0:
        return 0
    if health <= 0:
        return UNREACHABLE
    s, h, f, cd = size, health, fruits, cooldown
    for k in range(1, _FRUIT_HORIZON + 1):
        s, h, f, cd = predict_tree(s, h, f, cd, 1, near_water)
        if f > 0:
            return k
    return UNREACHABLE


def conversion_race_oracle(*, decision_turn, walkable, mother_cell, plant,
                           resident_cell, resident_speed,
                           resident_chop_power, opponents, near_water=False):
    """CONVERSION_RACE_ORACLE (see module docstring for the normative text).

    plant     : (size, health, fruits, cooldown) of the mother at
                ``decision_turn``.
    opponents : iterable of (cell, movement_speed, harvest_power) for every
                opponent unit at ``decision_turn``.

    Returns a dict with the three normative outputs — ``feasible``,
    ``completion_turn``, ``opponent_harvest_turn`` — plus the derived
    quantities ``eta_res``, ``exact_chop_turns``, ``eta_opp`` and
    ``first_fruit_turn`` for reporting. Absolute turns that can never occur
    are reported as decision_turn + UNREACHABLE.
    """
    t = decision_turn
    size, health, fruits, cooldown = plant
    dist = bfs_distances(set(walkable) | {mother_cell}, [mother_cell])

    d_res = dist.get(resident_cell)
    eta_res = (ceil_div(d_res, max(resident_speed, 1))
               if d_res is not None else UNREACHABLE)

    if eta_res >= UNREACHABLE or resident_chop_power <= 0:
        chops = UNREACHABLE
    else:
        arrival_plant = predict_tree(size, health, fruits, cooldown,
                                     eta_res, near_water)
        chops = exact_chop_turns(arrival_plant[0], arrival_plant[1],
                                 arrival_plant[3], resident_chop_power,
                                 near_water)
    if eta_res >= UNREACHABLE or chops >= UNREACHABLE:
        completion_turn = t + UNREACHABLE
    else:
        completion_turn = t + eta_res + chops - 1

    eta_opp = UNREACHABLE
    for (cell, speed, harvest_power) in opponents:
        if harvest_power <= 0:
            continue
        d = dist.get(cell)
        if d is None:
            continue
        eta_opp = min(eta_opp, ceil_div(d, max(speed, 1)))

    ripe = first_fruit_delay(size, health, fruits, cooldown, near_water)
    if eta_opp >= UNREACHABLE or ripe >= UNREACHABLE:
        opponent_harvest_turn = t + UNREACHABLE
    else:
        opponent_harvest_turn = max(t + eta_opp, t + ripe)

    feasible = (completion_turn < t + UNREACHABLE
                and completion_turn < opponent_harvest_turn)
    return {
        "feasible": feasible,
        "completion_turn": completion_turn,
        "opponent_harvest_turn": opponent_harvest_turn,
        "eta_res": eta_res,
        "exact_chop_turns": chops,
        "eta_opp": eta_opp,
        "first_fruit_turn": t + ripe if ripe < UNREACHABLE
        else t + UNREACHABLE,
    }


def _self_test():
    # Review counterexample (round-3 terminal failure): size 2, health 4,
    # cooldown 1, chop 1 needs FIVE growth-aware chops (static claims 4).
    assert exact_chop_turns(2, 4, 1, 1) == 5
    assert exact_chop_turns(2, 4, 5, 1) == 4
    assert predict_tree(2, 4, 0, 1, 1) == (3, 5, 0, 6)

    # Cross-check the arithmetic mirrors against trace_detectors on a state
    # grid (single source of race semantics; shared growth arithmetic).
    import trace_detectors as td
    for size in (1, 2, 3, 4):
        for health in (1, 2, 3, 2 + size):
            for cd in (0, 1, 3, 6):
                for wet in (False, True):
                    assert (exact_chop_turns(size, health, cd, 1, wet)
                            == td.banana_exact_chop_turns(size, health, cd,
                                                          1, wet))
                    for k in (0, 1, 4, 9):
                        assert (predict_tree(size, health, 0, cd, k, wet)
                                == td.banana_predict_tree(size, health, 0,
                                                          cd, k, wet))

    walk = {(x, y) for x in range(14) for y in range(5)} - {(1, 1), (13, 1)}

    # r3a boundary (infeasible by exactly one turn — the strict tie):
    # size-4 mother, health 5, fruits 0, cd 6; resident 2 away, opponent
    # harvester 2 away. completion 1+2+5-1 = 7 == harvest max(1+2, 1+6) = 7.
    r = conversion_race_oracle(
        decision_turn=1, walkable=walk, mother_cell=(2, 2),
        plant=(4, 5, 0, 6), resident_cell=(2, 0), resident_speed=1,
        resident_chop_power=1, opponents=[((4, 2), 1, 1)])
    assert (r["completion_turn"], r["opponent_harvest_turn"]) == (7, 7)
    assert r["feasible"] is False

    # r3b boundary (feasible by exactly one turn): health 4 -> completion 6.
    r = conversion_race_oracle(
        decision_turn=1, walkable=walk, mother_cell=(2, 2),
        plant=(4, 4, 0, 6), resident_cell=(2, 0), resident_speed=1,
        resident_chop_power=1, opponents=[((4, 2), 1, 1)])
    assert (r["completion_turn"], r["opponent_harvest_turn"]) == (6, 7)
    assert r["feasible"] is True

    # Unripe young mother: arrival is NOT loss — ripeness dominates.
    r = conversion_race_oracle(
        decision_turn=11, walkable=walk, mother_cell=(2, 2),
        plant=(2, 4, 0, 4), resident_cell=(0, 1), resident_speed=1,
        resident_chop_power=1, opponents=[((3, 0), 1, 1)])
    assert (r["completion_turn"], r["opponent_harvest_turn"]) == (18, 27)
    assert r["feasible"] is True

    # No harvest-capable opponent: any completable conversion is feasible.
    r = conversion_race_oracle(
        decision_turn=1, walkable=walk, mother_cell=(2, 2),
        plant=(4, 4, 0, 6), resident_cell=(2, 0), resident_speed=1,
        resident_chop_power=1, opponents=[((4, 2), 1, 0)])
    assert r["feasible"] is True and r["eta_opp"] == UNREACHABLE

    # Zero chop power: never feasible.
    r = conversion_race_oracle(
        decision_turn=1, walkable=walk, mother_cell=(2, 2),
        plant=(4, 4, 0, 6), resident_cell=(2, 0), resident_speed=1,
        resident_chop_power=0, opponents=[((4, 2), 1, 1)])
    assert r["feasible"] is False

    print("conversion_race_oracle self-test: OK")


if __name__ == "__main__":
    _self_test()
