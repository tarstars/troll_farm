#!/usr/bin/env python3
"""RED-phase regression checks R-1 / R-2 for the banana-restoration-r2 task.

Two named regression checks, implemented as pure trace analyses over the
(transcript, commands) pair produced by the mini-referee of
``make_banana_traces.py`` (or any byte-compatible trace):

  R-1 "one-seed-reservation"      -> invariant I-9  (surplus rule)
  R-2 "unripe-contested-response" -> invariant I-10a (ownership-loss response)
  R-3 "conversion-race-boundary"  -> I-10a CONVERSION_RACE_ORACLE boundary
      pair (round 4; spec Revision 2026-08-05: r3a infeasible by exactly the
      strict tie -> must abandon; r3b feasible by exactly one turn -> must
      convert, where every voided legacy deadline says infeasible)
  R-4 "flip-response-reachability"-> I-10a end-to-end: the CANDIDATE ITSELF
      plants the mother, leaves it in its normal lifecycle, a real I-7 flip
      occurs, CONVERSION_RACE_ORACLE says feasible, and the convert response
      must begin by flip turn + 1 (round 4; round-3 host review terminal
      gap 1: the t5 evidence was scripted, the real candidate camps or
      WAITs)

All are runnable from the CLI against any candidate binary (or source, which
is then compiled) and R-1 additionally in trace-file mode against an existing
committed trace. Every check is falsifiable in both directions: R-1/R-2 were
built to FAIL on rejected SHA f29efd0e..., R-3b/R-4 FAIL on current SHA
2f58edef... (its voided max(eta_opp, predicted.cooldown) deadline refuses the
oracle-feasible conversions), and the ``controls`` subcommand proves each
verdict reachable on synthetic traces (including a doomed-chop FAIL control
for r3a).

Usage:
  regression_tests.py r1-trace --transcript F --commands F
  regression_tests.py r1-bin  (--binary F | --source F)   # runs t1 lifecycle
  regression_tests.py r2-bin  (--binary F | --source F)   # runs t3/t4 dynamic
  regression_tests.py r3-bin  (--binary F | --source F)   # runs r3a/r3b pair
  regression_tests.py r4-bin  (--binary F | --source F)   # runs r4 flip reach
  regression_tests.py controls                            # control traces
  regression_tests.py all     (--binary F | --source F)   # everything above

Exit code 0 iff every requested check reports PASS (for ``controls``: iff the
compliant synthetic traces PASS, i.e. the checks are not vacuous-always-FAIL).

Deterministic, stdlib only. This module never modifies the candidate, the
harness fixtures, the detectors, or the committed traces.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import semantic_harness as sh            # noqa: E402  (compiler)
import trace_detectors as td             # noqa: E402  (trace parser / BFS)
import make_banana_traces as mbt         # noqa: E402  (referees + scenarios)
import conversion_race_oracle as cro     # noqa: E402  (CONVERSION_RACE_ORACLE)

BANANA = 3          # carry/inventory slot of BANANA
BIG = 10 ** 6


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def resident_id(tr: td.Trace) -> int:
    """The resident = the starter = min-id own unit at turn 1 (spec B3:
    'the starter (min-id unit at turn 1) ... is the resident and performs
    all banana work')."""
    return min(u.id for u in tr.state(1).own_units())


def dist_map_to(tr: td.Trace, cell):
    """BFS distance map toward ``cell`` over the walkable set (plus the cell
    itself, which on the trace maps is walkable anyway)."""
    walk = set(tr.smap.walkable) | {cell}
    return td.bfs_distances(walk, [cell])


def travel_eta(dist_map, cell, speed) -> int:
    d = dist_map.get(cell)
    if d is None:
        return BIG
    return td.ceil_div(d, max(speed, 1))


def ownership_flip_turn(tr: td.Trace, mother, opp_id):
    """First turn t at which I-7 ownership of the mother cell is false:
    NOT (eta_res(c,t) < eta_opp_h(c,t)) with strict inequality, ties treated
    as not owned ('ties are treated as not owned', I-7). Returns
    (t, eta_res, eta_opp) or None if ownership never flips in the trace."""
    rid = resident_id(tr)
    dmap = dist_map_to(tr, mother)
    for t in range(1, tr.T + 1):
        res = tr.unit(rid, t)
        opp = tr.unit(opp_id, t)
        if res is None or opp is None:
            continue
        eta_res = travel_eta(dmap, res.cell, res.speed)
        eta_opp = travel_eta(dmap, opp.cell, opp.speed)
        if not (eta_res < eta_opp):
            return t, eta_res, eta_opp
    return None


def trace_oracle(tr: td.Trace, t: int, mother):
    """CONVERSION_RACE_ORACLE evaluated on trace state ``S_t`` (spec
    Revision 2026-08-05): resident = the committed harvester (the starter),
    opponents = every opponent unit with its stats at ``t``. Returns the
    oracle dict, or None if the mother plant or the resident is absent."""
    rid = resident_id(tr)
    st = tr.state(t)
    plant = st.plant_at(mother)
    res = tr.unit(rid, t)
    if plant is None or res is None:
        return None
    return cro.conversion_race_oracle(
        decision_turn=t,
        walkable=set(tr.smap.walkable),
        mother_cell=mother,
        plant=(plant.size, plant.health, plant.fruits, plant.cooldown),
        resident_cell=res.cell,
        resident_speed=res.speed,
        resident_chop_power=res.chop_power,
        opponents=[(u.cell, u.speed, u.harvest_power)
                   for u in st.opp_units()],
        near_water=tr.near_water(mother))


def legacy_deadline_table(tr: td.Trace, t: int, mother, opp_id):
    """Literal reproductions of the three VOIDED conversion deadlines (spec
    Revision 2026-08-05) at trace turn ``t`` — reported for documentation so
    a trace shows where the divergent definitions disagree with
    CONVERSION_RACE_ORACLE. Never used for a verdict."""
    rid = resident_id(tr)
    st = tr.state(t)
    plant = st.plant_at(mother)
    res = tr.unit(rid, t)
    opp = tr.unit(opp_id, t)
    if plant is None or res is None or opp is None:
        return None
    dmap = dist_map_to(tr, mother)
    eta_res = travel_eta(dmap, res.cell, res.speed)
    eta_opp = travel_eta(dmap, opp.cell, opp.speed)
    near_water = tr.near_water(mother)
    predicted = td.banana_predict_tree(
        plant.size, plant.health, plant.fruits, plant.cooldown,
        min(eta_res, 300), near_water)
    chops = td.banana_exact_chop_turns(
        predicted[0], predicted[1], predicted[3],
        max(res.chop_power, 1), near_water)
    ripen_proxy = 0 if plant.fruits > 0 else predicted[3]
    arrival = t + eta_res if t + eta_res <= tr.T else None
    d8_old = None
    if arrival is not None:
        p_arr = tr.state(arrival).plant_at(mother)
        opp_arr = tr.unit(opp_id, arrival)
        if p_arr is not None and opp_arr is not None:
            exact_at_start = td.banana_exact_chop_turns(
                p_arr.size, p_arr.health, p_arr.cooldown,
                max(res.chop_power, 1), near_water)
            eta_opp_at_start = travel_eta(dmap, opp_arr.cell, opp_arr.speed)
            d8_old = {"exact_chops_at_chop_start": exact_at_start,
                      "eta_opp_at_chop_start": eta_opp_at_start,
                      "accepts": exact_at_start < eta_opp_at_start}
    return {
        "voided_spec_old_lt_eta_opp":
            {"lhs_eta_res_plus_chops": eta_res + chops, "rhs_eta_opp":
             eta_opp, "accepts": eta_res + chops < eta_opp},
        "voided_code_max_eta_opp_predicted_cooldown":
            {"lhs_eta_res_plus_chops": eta_res + chops,
             "rhs_deadline": max(eta_opp, ripen_proxy),
             "accepts": eta_res + chops < max(eta_opp, ripen_proxy)},
        "voided_d8_arrival_only": d8_old,
    }


# ---------------------------------------------------------------------------
# R-1 "one-seed-reservation" (targets I-9)
# ---------------------------------------------------------------------------

def r1_one_seed_reservation(tr: td.Trace) -> dict:
    """R-1 "one-seed-reservation" — regression check for invariant I-9.

    Spec language (invariant-spec-2026-08-04.md, B3):

      "I-9 (surplus rule). Replant demand (an empty eligible Ring cell
      within horizon I-5) has priority for at most one carried seed; every
      additional carried banana is surplus and must be on a bank path
      (monotone door approach as in I-19, then DROP)."

    and its ambiguity resolution: "bank vs replant priority? -> Resolve: I-9
    (one seed for replant, rest banked)."

    Derived trace predicate: replant may reserve AT MOST ONE carried banana.
    The moment the resident's banana carry exceeds 1, everything beyond one
    seed is surplus and must reach the bank (a DROP issued at a door) before
    it may be spent on planting. Therefore a *surplus window* opens at the
    first turn t with carry(t) > 1 and closes only when the resident banks
    (issues DROP while standing on a door cell) or the carried bananas are
    gone. Every ``PLANT <resident> BANANA`` issued while the window is open
    is a violation: it means harvested seeds are being replanted beyond the
    one-seed reservation with no intervening bank of the surplus. This is
    exactly the rejected candidate's committed t55-t61 lifecycle pattern
    (harvest x2 at t55/56, carry 2 at t57, PLANT at t58 and t61, first DROP
    only at t79).

    FAIL iff at least one such PLANT exists. Reported per violation: the
    turn, the resident's banana carry before the command, and the turn the
    unbanked-surplus window opened.
    """
    rid = resident_id(tr)
    violations = []
    banks = []
    window_open = False
    window_since = None
    for t in range(1, tr.T + 1):
        unit = tr.unit(rid, t)
        if unit is None:
            continue
        carry = unit.carry[BANANA]
        if carry > 1:
            if not window_open:
                window_open = True
                window_since = t
        elif carry == 0:
            window_open = False
            window_since = None
        cmd = tr.cmd_of(rid, t)
        if cmd is None:
            continue
        if (cmd.verb == "PLANT" and cmd.args and cmd.args[0] == "BANANA"
                and window_open):
            violations.append({
                "turn": t,
                "carry_before": carry,
                "surplus_since_turn": window_since,
            })
        if cmd.verb == "DROP" and unit.cell in tr.doors:
            banks.append(t)
            window_open = False
            window_since = None
    return {
        "check": "R-1 one-seed-reservation",
        "invariant": "I-9",
        "resident": rid,
        "verdict": "FAIL" if violations else "PASS",
        "violations": violations,
        "bank_turns": banks[:20],
    }


# ---------------------------------------------------------------------------
# R-2 "unripe-contested-response" (targets I-10a)
# ---------------------------------------------------------------------------

R2_DOC = """Spec language (invariant-spec-2026-08-04.md, B4):

  "I-10a (dynamic ownership-loss response ...). If ownership of a live own
  banana asset is lost after plant time (I-7 flips false at some t through
  opponent movement), the resident responds deterministically at the first
  such t: if a ripe fruit is harvestable immediately, harvest now; otherwise
  convert (chop at current size, orthogonal arithmetic of B2) iff the
  conversion completes strictly before eta_opp, else abandon (no further
  commands invested in the asset)."
"""


def r2_abandon(tr: td.Trace, mother=None, opp_id=5) -> dict:
    """R-2 variant A "unripe-contested-abandon" — regression check for I-10a.

    Scenario contract (t3_abandon): the mother is UNRIPE at the ownership
    flip and conversion is impossible (travel + ceil(health/chop_power)
    chop turns cannot complete strictly before the opponent's earliest
    harvest), so I-10a requires the Abandoned transition: "no further
    commands invested in the asset". FAIL if after the flip turn the
    resident keeps investing: any MOVE targeted at the mother cell, any
    PLANT, or any HARVEST/CHOP while standing on the mother cell.
    """ + R2_DOC
    mother = mother or mbt.MOTHER_CELL
    rid = resident_id(tr)
    flip = ownership_flip_turn(tr, mother, opp_id)
    if flip is None:
        return {"check": "R-2a unripe-contested-abandon", "invariant": "I-10a",
                "verdict": "ERROR",
                "reason": "scenario invalid: ownership never flips"}
    flip_t, eta_res, eta_opp = flip
    st = tr.state(flip_t)
    plant = st.plant_at(mother)
    unripe_at_flip = plant is not None and plant.fruits == 0
    violations = []
    for t in range(flip_t, tr.T + 1):
        unit = tr.unit(rid, t)
        cmd = tr.cmd_of(rid, t)
        if unit is None or cmd is None:
            continue
        if cmd.verb == "MOVE" and cmd.args and cmd.args[0] == mother:
            violations.append({"turn": t, "command": cmd.raw,
                               "why": "MOVE toward the lost mother"})
        elif cmd.verb == "PLANT":
            violations.append({"turn": t, "command": cmd.raw,
                               "why": "PLANT after ownership flip"})
        elif cmd.verb in ("HARVEST", "CHOP") and unit.cell == mother:
            violations.append({"turn": t, "command": cmd.raw,
                               "why": cmd.verb + " on the lost mother"})
    return {
        "check": "R-2a unripe-contested-abandon",
        "invariant": "I-10a",
        "resident": rid,
        "mother": list(mother),
        "flip_turn": flip_t,
        "eta_res_at_flip": eta_res,
        "eta_opp_at_flip": eta_opp,
        "unripe_at_flip": unripe_at_flip,
        "verdict": "FAIL" if violations else "PASS",
        "violations": violations,
    }


def r2_convert(tr: td.Trace, mother=None, opp_id=5) -> dict:
    """R-2 variant B "unripe-contested-convert" — regression check for I-10a.

    Scenario contract (t4_convert): the mother is UNRIPE at the ownership
    flip and conversion IS possible — CONVERSION_RACE_ORACLE (spec Revision
    2026-08-05) reports feasible: the absolute final-chop turn is strictly
    before the opponent's absolute earliest EXECUTABLE HARVEST turn (travel
    AND ripeness). I-10a then requires "convert (chop at current size)".
    FAIL if the resident never begins the conversion: no CHOP issued while
    standing on the mother cell at any turn of the trace.
    """ + R2_DOC
    mother = mother or mbt.MOTHER_CELL
    rid = resident_id(tr)
    flip = ownership_flip_turn(tr, mother, opp_id)
    if flip is None:
        return {"check": "R-2b unripe-contested-convert", "invariant": "I-10a",
                "verdict": "ERROR",
                "reason": "scenario invalid: ownership never flips"}
    flip_t, eta_res, eta_opp = flip
    # Conversion-feasibility report at the flip turn, via
    # CONVERSION_RACE_ORACLE (spec Revision 2026-08-05; the former
    # max(eta_opp, ripen-proxy) fields are void — documented change 3).
    orc = trace_oracle(tr, flip_t, mother)
    feas = None
    if orc is not None:
        feas = {
            "turn": flip_t,
            "completion_turn": orc["completion_turn"],
            "opponent_harvest_turn": orc["opponent_harvest_turn"],
            "conversion_possible": orc["feasible"],
        }
    chops = []
    for t in range(1, tr.T + 1):
        unit = tr.unit(rid, t)
        cmd = tr.cmd_of(rid, t)
        if (unit is not None and cmd is not None and cmd.verb == "CHOP"
                and unit.cell == mother and tr.state(t).plant_at(mother)):
            chops.append(t)
    return {
        "check": "R-2b unripe-contested-convert",
        "invariant": "I-10a",
        "resident": rid,
        "mother": list(mother),
        "flip_turn": flip_t,
        "eta_res_at_flip": eta_res,
        "eta_opp_at_flip": eta_opp,
        "feasibility_at_flip": feas,
        "chop_turns_on_mother": chops[:20],
        "verdict": "PASS" if chops else "FAIL",
        "violations": [] if chops else [
            {"why": "conversion was possible but no CHOP on the mother "
                    "cell was ever issued (candidate falls through to "
                    "normal investment / waiting instead of converting)"}],
    }


# ---------------------------------------------------------------------------
# R-3 "conversion-race-boundary" (targets I-10a via CONVERSION_RACE_ORACLE;
# round 4, spec Revision 2026-08-05 — supersedes the round-3
# "growth-aware-conversion" closed-loop scenario, whose doom was defined by
# opponent ARRIVAL only; under the unified oracle that old scenario's chop
# was actually feasible: first fruit turn 23, completion turn 9. Documented
# expected-value change 4.)
# ---------------------------------------------------------------------------

# Unit-level oracle sanity (STAYS, per the round-3 review): the review's
# exact counterexample. A size-2 banana at health 4, cooldown 1, against
# chop power 1 needs FIVE growth-aware chops (the tree grows after chop 1:
# +1 size, +1 health), while the rejected static arithmetic
# ceil(health / chop_power) claims four.
assert td.banana_exact_chop_turns(2, 4, 1, 1) == 5
assert td.ceil_div(4, 1) == 4
assert cro.exact_chop_turns(2, 4, 1, 1) == 5    # the oracle's own mirror


def _mother_chop_turns(tr: td.Trace, mother):
    rid = resident_id(tr)
    return [t for t in range(1, tr.T + 1)
            if (tr.unit(rid, t) is not None
                and tr.cmd_of(rid, t) is not None
                and tr.cmd_of(rid, t).verb == "CHOP"
                and tr.unit(rid, t).cell == mother
                and tr.state(t).plant_at(mother) is not None)]


def r3a_infeasible_tie(tr: td.Trace, mother=None, opp_id=5) -> dict:
    """R-3a "conversion-race-boundary / infeasible-by-one" — I-10a abandon
    side of the CONVERSION_RACE_ORACLE boundary (spec Revision 2026-08-05).

    Scenario contract (scenario_r3a_boundary): I-7 ownership of the
    near-ripe size-4 mother is lost at turn 1 (tie), and the oracle says
    the conversion misses by exactly the strict tie:
    completion_turn == opponent_harvest_turn. I-10a requires abandon.

    FAIL iff the resident starts a chop on the mother whose chop-start
    oracle evaluation is infeasible (the doomed chop); PASS iff no doomed
    chop is started. ERROR if the scenario is invalid (no flip, or the
    flip-turn oracle is not exactly at the infeasible tie).
    """
    mother = mother or mbt.MOTHER_CELL
    rid = resident_id(tr)
    flip = ownership_flip_turn(tr, mother, opp_id)
    if flip is None:
        return {"check": "R-3a conversion-race-boundary/infeasible-tie",
                "invariant": "I-10a", "verdict": "ERROR",
                "reason": "scenario invalid: ownership never flips"}
    flip_t, eta_res, eta_opp = flip
    orc = trace_oracle(tr, flip_t, mother)
    if (orc is None or orc["feasible"]
            or orc["completion_turn"] != orc["opponent_harvest_turn"]):
        return {"check": "R-3a conversion-race-boundary/infeasible-tie",
                "invariant": "I-10a", "verdict": "ERROR",
                "reason": "scenario invalid: flip-turn oracle is not the "
                          "exact infeasible tie", "oracle": orc}
    chops = _mother_chop_turns(tr, mother)
    violations = []
    analysis = None
    if chops:
        t0 = chops[0]
        start_orc = trace_oracle(tr, t0, mother)
        analysis = {"chop_start_turn": t0, "oracle_at_chop_start": start_orc}
        if start_orc is None or not start_orc["feasible"]:
            violations.append({
                "why": "doomed chop: CONVERSION_RACE_ORACLE at chop-start "
                       "turn %d is infeasible (completion %s, opponent "
                       "harvest %s) — I-10a requires abandon"
                       % (t0,
                          None if start_orc is None
                          else start_orc["completion_turn"],
                          None if start_orc is None
                          else start_orc["opponent_harvest_turn"]),
                "chop_turns_on_mother": chops[:20]})
    return {
        "check": "R-3a conversion-race-boundary/infeasible-tie",
        "invariant": "I-10a",
        "resident": rid,
        "mother": list(mother),
        "flip_turn": flip_t,
        "eta_res_at_flip": eta_res,
        "eta_opp_at_flip": eta_opp,
        "oracle_at_flip": orc,
        "chop_analysis": analysis,
        "verdict": "FAIL" if violations else "PASS",
        "violations": violations,
    }


def r3b_feasible_edge(tr: td.Trace, mother=None, opp_id=5) -> dict:
    """R-3b "conversion-race-boundary / feasible-by-one" — I-10a convert
    side of the CONVERSION_RACE_ORACLE boundary (spec Revision 2026-08-05).

    Scenario contract (scenario_r3b_boundary): identical geometry to R-3a
    with one health point less; the oracle says the conversion wins by
    exactly one turn (completion_turn == opponent_harvest_turn - 1), while
    EVERY voided legacy deadline (spec-old "< eta_opp", candidate
    "< max(eta_opp, predicted.cooldown)", D-8-old arrival-only) answers
    infeasible — the discriminating geometry demanded by the round-3
    review. I-10a requires convert.

    FAIL iff the resident never begins the conversion (no CHOP on the
    mother in the whole trace). The voided-deadline table is attached for
    documentation. ERROR if the scenario is invalid.
    """
    mother = mother or mbt.MOTHER_CELL
    rid = resident_id(tr)
    flip = ownership_flip_turn(tr, mother, opp_id)
    if flip is None:
        return {"check": "R-3b conversion-race-boundary/feasible-edge",
                "invariant": "I-10a", "verdict": "ERROR",
                "reason": "scenario invalid: ownership never flips"}
    flip_t, eta_res, eta_opp = flip
    orc = trace_oracle(tr, flip_t, mother)
    if (orc is None or not orc["feasible"]
            or orc["completion_turn"] != orc["opponent_harvest_turn"] - 1):
        return {"check": "R-3b conversion-race-boundary/feasible-edge",
                "invariant": "I-10a", "verdict": "ERROR",
                "reason": "scenario invalid: flip-turn oracle is not "
                          "feasible by exactly one turn", "oracle": orc}
    chops = _mother_chop_turns(tr, mother)
    return {
        "check": "R-3b conversion-race-boundary/feasible-edge",
        "invariant": "I-10a",
        "resident": rid,
        "mother": list(mother),
        "flip_turn": flip_t,
        "eta_res_at_flip": eta_res,
        "eta_opp_at_flip": eta_opp,
        "oracle_at_flip": orc,
        "voided_legacy_deadlines_at_flip":
            legacy_deadline_table(tr, flip_t, mother, opp_id),
        "chop_turns_on_mother": chops[:20],
        "verdict": "PASS" if chops else "FAIL",
        "violations": [] if chops else [
            {"why": "CONVERSION_RACE_ORACLE says the conversion wins by "
                    "exactly one turn (completion %d < opponent harvest "
                    "%d) but no CHOP on the mother was ever issued — the "
                    "candidate's voided deadline refuses the feasible "
                    "conversion and abandons"
                    % (orc["completion_turn"],
                       orc["opponent_harvest_turn"])}],
    }


# ---------------------------------------------------------------------------
# R-4 "flip-response-reachability" (round 4; round-3 host review terminal
# gap 1: t5 was scripted — the REAL candidate must plant, lose, and respond)
# ---------------------------------------------------------------------------

def r4_flip_response_reachability(tr: td.Trace, mother=None,
                                  opp_id=5) -> dict:
    """R-4 "flip-response-reachability" — end-to-end I-10a regression
    (spec Revision 2026-08-05; round-3 host review terminal gap 1).

    Scenario contract (scenario_r4_flip_reach): the CANDIDATE ITSELF (not a
    script) PICKs the bootstrap seed and PLANTs the diagonal mother, later
    leaves it during its normal lifecycle (orthogonal wood chop + bank),
    the moving opponent harvester flips I-7 ownership of the mother, and
    CONVERSION_RACE_ORACLE at the flip turn reports feasible.

    PASS iff the oracle-prescribed convert response BEGINS within the I-10a
    window — at the flip turn f, or at f + 1 at the latest (I-10a rev.
    2026-08-05: f itself may legitimately be spent completing a committed
    banking DROP) — where "begins" = the resident issues CHOP standing on
    the mother, or a MOVE that targets the mother cell or strictly reduces
    its BFS distance to the mother — AND at least one CHOP lands on the
    mother later in the trace. FAIL otherwise (the observed post-flip
    command window is reported as evidence). ERROR if the scenario is
    invalid: the candidate never planted the mother itself, ownership never
    flipped while the mother was alive, or the flip-turn oracle is not
    feasible.
    """
    mother = mother or mbt.MOTHER_CELL
    rid = resident_id(tr)
    # (1) candidate-driven: the resident itself planted the mother.
    plant_turn = None
    for t in range(1, tr.T + 1):
        unit = tr.unit(rid, t)
        cmd = tr.cmd_of(rid, t)
        if (unit is not None and cmd is not None and cmd.verb == "PLANT"
                and cmd.args and cmd.args[0] == "BANANA"
                and unit.cell == mother):
            plant_turn = t
            break
    if plant_turn is None:
        return {"check": "R-4 flip-response-reachability",
                "invariant": "I-10a", "verdict": "ERROR",
                "reason": "scenario invalid: the candidate never planted "
                          "the mother itself"}
    # (2) first I-7 ownership loss while the own-planted mother is alive.
    dmap = dist_map_to(tr, mother)
    flip = None
    for t in range(plant_turn + 1, tr.T + 1):
        if tr.state(t).plant_at(mother) is None:
            continue
        res = tr.unit(rid, t)
        opp = tr.unit(opp_id, t)
        if res is None or opp is None:
            continue
        eta_res = travel_eta(dmap, res.cell, res.speed)
        eta_opp = travel_eta(dmap, opp.cell, opp.speed)
        if not (eta_res < eta_opp):
            flip = (t, eta_res, eta_opp)
            break
    if flip is None:
        return {"check": "R-4 flip-response-reachability",
                "invariant": "I-10a", "verdict": "ERROR",
                "reason": "scenario invalid: ownership of the own-planted "
                          "mother never flips", "plant_turn": plant_turn}
    flip_t, eta_res, eta_opp = flip
    # (3) the oracle must prescribe convert.
    orc = trace_oracle(tr, flip_t, mother)
    if orc is None or not orc["feasible"]:
        return {"check": "R-4 flip-response-reachability",
                "invariant": "I-10a", "verdict": "ERROR",
                "reason": "scenario invalid: CONVERSION_RACE_ORACLE at the "
                          "flip turn is not feasible", "oracle": orc}
    # (4) the response window: f .. f+1.
    def is_response(t):
        unit = tr.unit(rid, t)
        cmd = tr.cmd_of(rid, t)
        if unit is None or cmd is None:
            return False
        if cmd.verb == "CHOP" and unit.cell == mother:
            return True
        if cmd.verb == "MOVE" and cmd.args:
            if cmd.args[0] == mother:
                return True
            nxt = tr.unit(rid, t + 1) if t + 1 <= tr.T else None
            if nxt is not None:
                d_now = dmap.get(unit.cell, BIG)
                d_nxt = dmap.get(nxt.cell, BIG)
                return d_nxt < d_now
        return False

    window = [t for t in (flip_t, flip_t + 1) if t <= tr.T]
    begun = [t for t in window if is_response(t)]
    chops = _mother_chop_turns(tr, mother)
    observed = []
    for t in range(flip_t, min(flip_t + 10, tr.T) + 1):
        cmd = tr.cmd_of(rid, t)
        observed.append({"turn": t,
                         "resident_command":
                             cmd.raw if cmd is not None else "WAIT"})
    violations = []
    if not begun:
        violations.append({
            "why": "no convert response begun in the I-10a window [%d, %d]:"
                   " the oracle prescribes CHOP (feasible: completion %d < "
                   "opponent harvest %d) but the resident emits no CHOP on "
                   "the mother and no MOVE toward it"
                   % (flip_t, flip_t + 1, orc["completion_turn"],
                      orc["opponent_harvest_turn"]),
            "observed_post_flip_window": observed})
    elif not chops:
        violations.append({
            "why": "response begun in the window but no CHOP ever lands on "
                   "the mother", "observed_post_flip_window": observed})
    return {
        "check": "R-4 flip-response-reachability",
        "invariant": "I-10a",
        "resident": rid,
        "mother": list(mother),
        "plant_turn": plant_turn,
        "flip_turn": flip_t,
        "eta_res_at_flip": eta_res,
        "eta_opp_at_flip": eta_opp,
        "oracle_at_flip": orc,
        "response_window": window,
        "response_begun_turns": begun,
        "chop_turns_on_mother": chops[:20],
        "post_flip_commands": observed,
        "verdict": "FAIL" if violations else "PASS",
        "violations": violations,
    }


# ---------------------------------------------------------------------------
# Trace production (no writes into traces/)
# ---------------------------------------------------------------------------

def run_binary(binary: Path, referee, turns: int):
    """Closed-loop run of a compiled candidate against a referee instance.
    Same protocol as make_banana_traces.run_scenario but writes no files;
    returns (transcript_text, commands_text)."""
    header = f"{len(mbt.MAP[0])} {len(mbt.MAP)}\n" + "\n".join(mbt.MAP) + "\n"
    transcript_parts = [header]
    command_lines = []
    with subprocess.Popen(
        [str(binary)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        text=True,
    ) as proc:
        proc.stdin.write(header)
        proc.stdin.flush()
        for _ in range(turns):
            block = referee.turn_text()
            transcript_parts.append(block)
            proc.stdin.write(block)
            proc.stdin.flush()
            line = proc.stdout.readline()
            if not line:
                raise RuntimeError("candidate closed stdout early")
            line = line.rstrip("\n")
            command_lines.append(line)
            referee.apply(line)
            referee.grow()
        proc.stdin.close()
    return "".join(transcript_parts), "\n".join(command_lines) + "\n"


def run_scripted(referee, policy, turns: int):
    """Closed-loop run of a Python turn policy (turn, referee) -> command
    line. Used for the compliant synthetic control traces."""
    header = f"{len(mbt.MAP[0])} {len(mbt.MAP)}\n" + "\n".join(mbt.MAP) + "\n"
    transcript_parts = [header]
    command_lines = []
    for turn in range(1, turns + 1):
        transcript_parts.append(referee.turn_text())
        line = policy(turn, referee)
        command_lines.append(line)
        referee.apply(line)
        referee.grow()
    return "".join(transcript_parts), "\n".join(command_lines) + "\n"


def build(transcript, commands) -> td.Trace:
    return td.build_trace(transcript, commands)


# ---------------------------------------------------------------------------
# Compliant synthetic control traces (near-miss controls)
# ---------------------------------------------------------------------------

def control_r1():
    """Near-miss control for R-1: the resident harvests TWO bananas (carry
    exceeds 1, the surplus window opens), then banks at a door (DROP)
    BEFORE any replant, then harvests one seed and plants it with carry
    exactly 1. Compliant with I-9, so R-1 must PASS."""
    referee = mbt.Referee(
        inventory=[0, 0, 0, 0, 0, 0],
        plants={(2, 2): {"kind": "BANANA", "size": 4, "health": 6,
                         "fruits": 3, "cd": 6}},
        units={
            0: mbt.unit_row(0, 0, (2, 2), cap=2, harvest=1, chop=1),
            1: mbt.unit_row(1, 0, (11, 3), cap=1, harvest=0, chop=0),
            5: mbt.unit_row(5, 1, (13, 0), cap=2, harvest=1, chop=1),
        },
    )
    script = {
        1: "HARVEST 0;WAIT",       # carry 1
        2: "HARVEST 0;WAIT",       # carry 2 -> surplus window opens
        3: "MOVE 0 2 1;WAIT",      # monotone door approach
        4: "DROP 0;WAIT",          # bank at the (2,1) door -> window closes
        5: "MOVE 0 2 2;WAIT",
        6: "HARVEST 0;WAIT",       # carry 1 (the one-seed reservation)
        7: "MOVE 0 1 2;WAIT",
        8: "PLANT 0 BANANA;WAIT",  # replant with carry == 1: compliant
        9: "WAIT",
        10: "WAIT",
    }
    return run_scripted(referee, lambda t, _r: script.get(t, "WAIT"), 10)


def control_r2_abandon():
    """Near-miss control for R-2a: same t3_abandon dynamic scenario, but the
    resident abandons at (indeed before) the flip: it retreats to the bank
    door and idles — no MOVE targeted at the mother, no PLANT, no
    HARVEST/CHOP on the mother. Compliant with I-10a, so R-2a must PASS."""
    referee = mbt.scenario_t3_abandon()
    script = {1: "MOVE 0 1 2;WAIT", 2: "MOVE 0 1 2;WAIT",
              3: "MOVE 0 1 2;WAIT", 4: "MOVE 0 1 2;WAIT"}
    return run_scripted(referee, lambda t, _r: script.get(t, "WAIT"), 20)


def control_r3a_compliant():
    """Near-miss control for R-3a: same scenario_r3a_boundary dynamic
    scenario, but the resident obeys I-10a at the turn-1 flip: the oracle
    tie (completion 7 == opponent harvest 7) means abandon — it retreats
    and idles, never chopping the lost mother. Compliant, R-3a must PASS."""
    referee = mbt.scenario_r3a_boundary()
    script = {1: "MOVE 0 11 0;WAIT", 2: "MOVE 0 11 0;WAIT",
              3: "MOVE 0 11 0;WAIT", 4: "MOVE 0 11 0;WAIT"}
    return run_scripted(referee, lambda t, _r: script.get(t, "WAIT"), 20)


def control_r3a_doomed():
    """FAIL-direction control for R-3a (non-vacuity): a greedy mutant walks
    onto the tie-boundary mother and chops anyway (chop start turn 3,
    oracle completion 3 + 5 - 1 = 7 == opponent harvest 7 -> doomed).
    R-3a must FAIL on this trace."""
    referee = mbt.scenario_r3a_boundary()
    script = {1: "MOVE 0 2 2;WAIT", 2: "MOVE 0 2 2;WAIT",
              3: "CHOP 0;WAIT", 4: "CHOP 0;WAIT", 5: "CHOP 0;WAIT",
              6: "CHOP 0;WAIT", 7: "CHOP 0;WAIT"}
    return run_scripted(referee, lambda t, _r: script.get(t, "WAIT"), 20)


def control_r3b_compliant():
    """Near-miss control for R-3b: same scenario_r3b_boundary scenario; the
    resident converts at the feasible edge (travel turns 1-2, chops turns
    3-6, completion turn 6 < opponent harvest turn 7, tree gone before the
    fruit ripens), then banks the wood. Compliant, R-3b must PASS."""
    referee = mbt.scenario_r3b_boundary()
    script = {1: "MOVE 0 2 2;WAIT", 2: "MOVE 0 2 2;WAIT",
              3: "CHOP 0;WAIT", 4: "CHOP 0;WAIT", 5: "CHOP 0;WAIT",
              6: "CHOP 0;WAIT", 7: "MOVE 0 2 1;WAIT", 8: "DROP 0;WAIT"}
    return run_scripted(referee, lambda t, _r: script.get(t, "WAIT"), 20)


def control_r4_compliant():
    """Near-miss control for R-4: same scenario_r4_flip_reach dynamics with
    the candidate's own turn 1-11 prefix (PICK, found the mother, chop the
    orthogonal wood tree, bank), then the I-10a-compliant response: the
    flip lands at turn 11 (banking DROP) and the convert response begins at
    turn 12 (MOVE toward the mother), chops run turns 15-19 (completion 19
    < opponent harvest 27), wood banked. Compliant, R-4 must PASS."""
    referee = mbt.scenario_r4_flip_reach()
    script = {1: "PICK 0 BANANA;WAIT", 2: "MOVE 0 2 2;WAIT",
              3: "PLANT 0 BANANA;WAIT",
              4: "MOVE 0 0 1;WAIT", 5: "MOVE 0 0 1;WAIT",
              6: "MOVE 0 0 1;WAIT",
              7: "CHOP 0;WAIT", 8: "CHOP 0;WAIT", 9: "CHOP 0;WAIT",
              10: "CHOP 0;WAIT", 11: "DROP 0;WAIT",
              12: "MOVE 0 2 2;WAIT", 13: "MOVE 0 2 2;WAIT",
              14: "MOVE 0 2 2;WAIT",
              15: "CHOP 0;WAIT", 16: "CHOP 0;WAIT", 17: "CHOP 0;WAIT",
              18: "CHOP 0;WAIT", 19: "CHOP 0;WAIT",
              20: "MOVE 0 2 1;WAIT", 21: "DROP 0;WAIT"}
    return run_scripted(referee, lambda t, _r: script.get(t, "WAIT"), 26)


def control_r2_convert():
    """Near-miss control for R-2b: same t4_convert dynamic scenario; the
    resident steps onto the mother and chops it down (health 2, chop 1:
    done by turn 3, strictly before the opponent's earliest harvest, which
    the 30-turn ripening bounds below). Compliant with I-10a convert, so
    R-2b must PASS."""
    referee = mbt.scenario_t4_convert()
    script = {1: "MOVE 0 2 2;WAIT", 2: "CHOP 0;WAIT", 3: "CHOP 0;WAIT",
              4: "MOVE 0 2 1;WAIT", 5: "DROP 0;WAIT"}
    return run_scripted(referee, lambda t, _r: script.get(t, "WAIT"), 20)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def compile_source(source_path: Path, workdir: Path) -> Path:
    binary = workdir / "rt_candidate"
    sh.compile_text(source_path.read_text(), binary, "rt_candidate")
    return binary


def emit(report: dict) -> bool:
    print(json.dumps(report, indent=1, sort_keys=True))
    return report.get("verdict") == "PASS"


def cmd_r1_trace(args) -> bool:
    tr = build(Path(args.transcript).read_text(),
               Path(args.commands).read_text())
    return emit(r1_one_seed_reservation(tr))


def cmd_r1_bin(binary: Path, outdir) -> bool:
    transcript, commands = run_binary(binary, mbt.scenario_t1(), 300)
    if outdir:
        Path(outdir, "r1-t1_lifecycle-transcript.txt").write_text(transcript)
        Path(outdir, "r1-t1_lifecycle-commands.txt").write_text(commands)
    return emit(r1_one_seed_reservation(build(transcript, commands)))


def cmd_r2_bin(binary: Path, outdir) -> bool:
    ok = True
    for name, factory, turns, checker in (
        ("t3_abandon", mbt.scenario_t3_abandon, 20, r2_abandon),
        ("t4_convert", mbt.scenario_t4_convert, 20, r2_convert),
    ):
        transcript, commands = run_binary(binary, factory(), turns)
        if outdir:
            Path(outdir, f"r2-{name}-transcript.txt").write_text(transcript)
            Path(outdir, f"r2-{name}-commands.txt").write_text(commands)
        ok = emit(checker(build(transcript, commands))) and ok
    return ok


def cmd_r3_bin(binary: Path, outdir) -> bool:
    ok = True
    for name, factory, checker in (
        ("r3a_boundary", mbt.scenario_r3a_boundary, r3a_infeasible_tie),
        ("r3b_boundary", mbt.scenario_r3b_boundary, r3b_feasible_edge),
    ):
        transcript, commands = run_binary(binary, factory(), 20)
        if outdir:
            Path(outdir, f"{name}-transcript.txt").write_text(transcript)
            Path(outdir, f"{name}-commands.txt").write_text(commands)
        ok = emit(checker(build(transcript, commands))) and ok
    return ok


def cmd_r4_bin(binary: Path, outdir) -> bool:
    transcript, commands = run_binary(binary, mbt.scenario_r4_flip_reach(),
                                      26)
    if outdir:
        Path(outdir, "r4-flip-reach-transcript.txt").write_text(transcript)
        Path(outdir, "r4-flip-reach-commands.txt").write_text(commands)
    return emit(r4_flip_response_reachability(build(transcript, commands)))


def cmd_controls() -> bool:
    ok = True
    for label, (transcript, commands), checker, expected in (
        ("control-r1-compliant", control_r1(), r1_one_seed_reservation,
         "PASS"),
        ("control-r2a-compliant", control_r2_abandon(), r2_abandon, "PASS"),
        ("control-r2b-compliant", control_r2_convert(), r2_convert, "PASS"),
        ("control-r3a-compliant", control_r3a_compliant(),
         r3a_infeasible_tie, "PASS"),
        ("control-r3a-doomed", control_r3a_doomed(), r3a_infeasible_tie,
         "FAIL"),
        ("control-r3b-compliant", control_r3b_compliant(), r3b_feasible_edge,
         "PASS"),
        ("control-r4-compliant", control_r4_compliant(),
         r4_flip_response_reachability, "PASS"),
    ):
        report = checker(build(transcript, commands))
        report["control"] = label
        report["expected_verdict"] = expected
        print(json.dumps(report, indent=1, sort_keys=True))
        ok = (report.get("verdict") == expected) and ok
    return ok


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["r1-trace", "r1-bin", "r2-bin",
                                         "r3-bin", "r4-bin", "controls",
                                         "all"])
    parser.add_argument("--transcript")
    parser.add_argument("--commands")
    parser.add_argument("--binary")
    parser.add_argument("--source")
    parser.add_argument("--outdir", help="optional directory for the raw "
                        "trace files produced by the binary modes")
    args = parser.parse_args(argv)
    if args.outdir:
        Path(args.outdir).mkdir(parents=True, exist_ok=True)

    if args.mode == "controls":
        return 0 if cmd_controls() else 1
    if args.mode == "r1-trace":
        if not (args.transcript and args.commands):
            parser.error("r1-trace requires --transcript and --commands")
        return 0 if cmd_r1_trace(args) else 1

    with tempfile.TemporaryDirectory(prefix="banana-rt-") as workdir:
        if args.binary:
            binary = Path(args.binary)
        elif args.source:
            binary = compile_source(Path(args.source), Path(workdir))
        else:
            parser.error(f"{args.mode} requires --binary or --source")
        ok = True
        if args.mode in ("r1-bin", "all"):
            ok = cmd_r1_bin(binary, args.outdir) and ok
        if args.mode in ("r2-bin", "all"):
            ok = cmd_r2_bin(binary, args.outdir) and ok
        if args.mode in ("r3-bin", "all"):
            ok = cmd_r3_bin(binary, args.outdir) and ok
        if args.mode in ("r4-bin", "all"):
            ok = cmd_r4_bin(binary, args.outdir) and ok
        if args.mode == "all":
            ok = cmd_controls() and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
