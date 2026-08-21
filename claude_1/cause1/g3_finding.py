#!/usr/bin/env python3
r"""OSC-032/033 G-3 — the finding: why there was nothing to do, and whether a real game got there.

Task `20260821-osc032-033-cause-attribution`, gate G-3. Work owner claude_1, reviewer codex_1,
integrator local_claude_1. Runs only after G-1 (ACCEPTED `20260821T081645Z`) and G-2 (ACCEPTED
`20260821T084613Z`).

**Measurement only.** No fix, no candidate, no behaviour change, and NO bug-versus-correct-caution
ruling — that one is the owner's, afterwards, and this file must not pre-empt it.

## What this adds to the G-1/G-2-accepted instrument, and why

`cause_attribution.py` already delivers the card's original deliverables 1, 4 and 5 and is
accepted; nothing in it changes here and its artifact is not rewritten. The coordinator's
amendment (`20260821T082713Z`, card at `6d50a8cb`) asks four questions it does not answer:

1. **When and how the map went bare** — the last plant's death turn and kind, WHO felled it, and
   whether replant material sat in the shack at that moment.
2. **Would a real game have reached those turns** — the referee ends on `Board.hasStalled`; the
   frozen port is `sim.engine.has_stalled`. The replay harness (`regression_tests.run_binary_custom`)
   runs a FIXED `cfg["turns"]` horizon and never calls it, so the idle-turn counts are the
   harness's, not the referee's. This computes the referee's own end turn.
3. **The opening** — for each item the training cost was short of, whether a live reachable source
   of that kind existed on any turn before the deadline, and whether an opponent stood on it.
4. **The replant block** — whether any conjunct OTHER than `c5_own_units_ge_2` was also false.

Plus original deliverable 3 outside the windows, where plants actually exist.

## The three places this instrument could lie to itself, and the control for each

- **The stall projection is the whole of question 2.** It is computed by the FROZEN
  `sim.engine.has_stalled`, unmodified and unwrapped — this file builds a real
  `sim.state.GameState` from the referee trace and hands it over. Two controls: an ADAPTER
  FIDELITY gate (the rebuilt state must agree with the trace state on plant records, unit cells
  and both inventories, per turn, by identity) and a NON-VACUITY gate (the predicate must be
  observed returning False on a plant-bearing turn AND True on a bare board; a predicate observed
  in only one direction is not a predicate). Scores come from `sim.engine.recompute_scores`, not
  from a formula written here — a second formula would let "score" mean one thing to the mercy
  rule and another to this file.
- **"Who felled it" is the easiest wrong-reason in the card.** The unit standing on the tree when
  it vanished is not evidence that it chopped it. Attribution is taken ONLY from an actual
  `CHOP` command in the trace for that unit on that turn with the unit on the plant's cell.
  Where no own command explains the disappearance the record says `UNATTRIBUTED_OWN_SIDE` and
  says why, rather than naming the opponent: **the transcript carries our side's commands only**,
  so "the opponent did it" is never directly observable here and is not claimed.
- **A source "existed" is not "was reachable and alive".** The pre-deadline source scan requires
  health > 0 and BFS-reachability from the audited unit's own cell on that turn, reusing
  `oracle.reachable_from` rather than a second reachability notion.

Run:  python3 claude_1/cause1/g3_finding.py
"""
from __future__ import annotations

import collections
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for p in ("claude_1/t1", "claude_1/hstarve1", "claude_1/banana-restoration-r2",
          "claude_1/pipeline", "claude_1/picker2", "claude_1/cause1"):
    sys.path.insert(0, str(REPO / p))
sys.path.insert(0, str(REPO))
import cause_attribution as CA   # noqa: E402  (the accepted run path, reused wholesale)
import clause_tap as CT          # noqa: E402
import coverage as C             # noqa: E402
import fixture_harness as H      # noqa: E402
import fuzz_panel as fp          # noqa: E402
import oracle as OR              # noqa: E402
import trace_detectors as td     # noqa: E402
from sim import engine as SE     # noqa: E402  (the FROZEN port; never modified, never wrapped)
from sim import state as SS      # noqa: E402

FIXTURES = ["OSC-032", "OSC-033"]
OUT = HERE / "g3-finding-2026-08-21.json"
# bot/main.py:ITEM_INDEX order, and the order every carry/inventory 6-vector in this repo uses.
ITEMS = ["PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD"]
# The kinds a shack can replant from; iron and wood are not seeds.
SEED_ITEMS = ["PLUM", "LEMON", "APPLE", "BANANA"]


class G3Error(Exception):
    """Anything that would make a G-3 number mean something other than it says."""


# ---------------------------------------------------------------------------
# question 2 — the referee's own end turn, from the frozen port


def to_sim_state(tr, t):
    """Rebuild a real `sim.state.GameState` for turn `t` from the REFEREE trace.

    Deliberately constructs the frozen module's own dataclasses rather than a duck-typed shim:
    `has_stalled` is then reading the fields it was written against. `scores` is filled by the
    frozen `recompute_scores`, not by arithmetic written here.
    """
    st, sm = tr.state(t), tr.smap
    game = SS.GameState(
        width=sm.width, height=sm.height,
        walkable=set(sm.walkable), shacks=list(sm.shacks),
        inventories=[list(st.inventories[0]), list(st.inventories[1])],
        units=[SS.SimUnit(id=u.id, player=u.player, x=u.cell[0], y=u.cell[1], ms=u.speed,
                          cc=u.capacity, hp=u.harvest_power, chop=u.chop_power,
                          carry=list(u.carry)) for u in st.units],
        plants=[SS.SimPlant(type=p.kind, x=p.cell[0], y=p.cell[1], size=p.size, health=p.health,
                            fruits=p.fruits, cooldown=p.cooldown) for p in st.plants],
        scores=[0, 0], turn=t, next_id=0,
        iron=set(sm.iron), water=set(sm.water))
    SE.recompute_scores(game)
    return game


def check_adapter_fidelity(sid, tr, t, game):
    """The rebuilt state must BE the trace's state, by identity, or the projection is of a
    different game. Compares plant canonical records as a multiset, unit (id, cell, player,
    speed, carry) as a set, and both inventories."""
    st = tr.state(t)
    want_p = sorted(CA.trace_plant_records(st))
    got_p = sorted(CA.canonical_plant_record((p.x, p.y), p.type, p.health, p.size, p.fruits,
                                             p.cooldown) for p in game.plants)
    if want_p != got_p:
        raise G3Error(
            f"{sid} turn {t}: the state handed to has_stalled holds plants {got_p}, the referee "
            f"trace holds {want_p}. The stall projection would be of a different board.")
    want_u = sorted((u.id, u.player, tuple(u.cell), u.speed, tuple(u.carry)) for u in st.units)
    got_u = sorted((u.id, u.player, u.pos, u.ms, tuple(u.carry)) for u in game.units)
    if want_u != got_u:
        raise G3Error(
            f"{sid} turn {t}: rebuilt units {got_u} != trace units {want_u}. `has_stalled` reads "
            f"unit cell, player, ms and carry; a mismatch in any of them changes its answer.")
    want_i = [list(st.inventories[0]), list(st.inventories[1])]
    if [list(x) for x in game.inventories] != want_i:
        raise G3Error(
            f"{sid} turn {t}: rebuilt inventories {game.inventories} != trace {want_i}. The "
            f"stuck/mercy half of the rule reads both players' inventories.")


def stall_projection(sid, tr):
    """Replay `sim.engine.has_stalled` over the referee's own per-turn states.

    Returns the first turn it says the game is over, the reason, and the counter trace. The
    counter is threaded exactly as the frozen port's docstring requires: initialised to zero and
    fed back in, never reset by this file.
    """
    counter = 0
    rows, ended_turn, ended_reason = [], None, None
    saw_false_with_plants = saw_true = False
    for t in range(1, tr.T + 1):
        game = to_sim_state(tr, t)
        check_adapter_fidelity(sid, tr, t, game)
        stalled, counter = SE.has_stalled(game, counter)
        reason = SE.stall_reason(game, counter)
        rows.append({"turn": t, "plants": len(game.plants), "stalled": stalled,
                     "turns_until_end": counter, "reason": reason})
        if game.plants and not stalled:
            saw_false_with_plants = True
        if stalled:
            saw_true = True
            if ended_turn is None:
                ended_turn, ended_reason = t, reason
    # NON-VACUITY. A predicate observed in one direction only has not been shown to be a
    # predicate; had the adapter silently produced empty plant lists, "the game ended at once"
    # would be the artifact and would look exactly like a finding.
    if not saw_false_with_plants:
        raise G3Error(
            f"{sid}: has_stalled was never observed returning False on a plant-bearing turn, so "
            f"its True answers carry no information and no end turn may be reported.")
    if not saw_true:
        raise G3Error(
            f"{sid}: has_stalled never returned True over {tr.T} turns even though the board goes "
            f"bare; either the adapter or the reading is wrong and no end turn may be reported.")
    # ROBUSTNESS, reported not gating. The end above is the FULL rule. On these fixtures it is
    # the mercy clause that fires, and mercy depends on the OPPONENT being stuck and behind —
    # a property of this replayed opponent, not of the map. So also report where the grace
    # counter alone would have ended it, with the mercy and both-stuck clauses set aside. It is
    # the weaker, more conservative number and it is the one to quote if the opponent is in
    # doubt.
    grace_only = next((r["turn"] for r in rows
                       if r["plants"] == 0 and r["turns_until_end"] <= 0), None)
    return {"first_stalled_turn": ended_turn, "reason": ended_reason,
            "harness_horizon_turns": tr.T,
            "turns_after_the_referee_would_have_ended": tr.T - ended_turn,
            "grace_only_end_turn": grace_only,
            "grace_only_note": "the turn the no-plants grace counter alone would have expired, "
                               "ignoring the mercy and both-stuck clauses; conservative bound "
                               "that does not depend on the opponent's state",
            "per_turn": rows}


def stall_negative_control():
    """Show the projection is capable of BOTH answers on states this file constructs.

    Without it, "the game would have ended at turn N" rests on a predicate that has only ever
    been seen agreeing with the outcome the run wanted.
    """
    walk = {(x, y) for x in range(5) for y in range(5)}
    shacks = [(0, 0), (4, 4)]

    def mk(plants, carry0, inv0):
        return SS.GameState(
            width=5, height=5, walkable=set(walk), shacks=list(shacks),
            inventories=[list(inv0), [0] * 6],
            units=[SS.SimUnit(id=0, player=0, x=2, y=2, ms=1, cc=2, hp=1, chop=1,
                              carry=list(carry0)),
                   SS.SimUnit(id=1, player=1, x=3, y=3, ms=1, cc=2, hp=1, chop=1,
                              carry=[0] * 6)],
            plants=plants, scores=[0, 0], turn=1, next_id=2)

    cases = []
    # 1. a plant exists -> never stalled, counter reset
    g = mk([SS.SimPlant(type="PLUM", x=2, y=2, size=4, health=4, fruits=0, cooldown=0)],
           [0] * 6, [0] * 6)
    SE.recompute_scores(g)
    stalled, counter = SE.has_stalled(g, 0)
    cases.append({"case": "plant_exists_unit_on_it", "stalled": stalled, "must_be": False,
                  "turns_until_end": counter,
                  "note": "counter is set to walk-home/ms + 6 because the unit stands on the plant"})
    if counter <= 0:
        raise G3Error("control: a unit standing on a plant must set a positive grace counter; "
                      f"got {counter}. The grace half of the rule would be inert.")
    # 2. bare board, counter already 1 -> decrements to 0 -> grace expired
    g2 = mk([], [0] * 6, [0] * 6)
    SE.recompute_scores(g2)
    stalled2, counter2 = SE.has_stalled(g2, 1)
    cases.append({"case": "bare_board_grace_expires", "stalled": stalled2, "must_be": True,
                  "turns_until_end": counter2, "reason": SE.stall_reason(g2, counter2)})
    # 3. bare board with grace remaining and BOTH sides holding fruit -> not stalled
    g3 = mk([], [1, 0, 0, 0, 0, 0], [0] * 6)
    g3.units[1].carry = [1, 0, 0, 0, 0, 0]
    SE.recompute_scores(g3)
    stalled3, counter3 = SE.has_stalled(g3, 5)
    cases.append({"case": "bare_board_both_hold_fruit_grace_left", "stalled": stalled3,
                  "must_be": False, "turns_until_end": counter3})
    # 4. bare board, grace left, both sides empty-handed -> both stuck -> stalled
    g4 = mk([], [0] * 6, [0] * 6)
    SE.recompute_scores(g4)
    stalled4, counter4 = SE.has_stalled(g4, 5)
    cases.append({"case": "bare_board_both_stuck_grace_left", "stalled": stalled4,
                  "must_be": True, "turns_until_end": counter4,
                  "reason": SE.stall_reason(g4, counter4)})
    bad = [c for c in cases if c["stalled"] != c["must_be"]]
    if bad:
        raise G3Error(f"the stall predicate control did not behave: {bad}")
    return cases


# ---------------------------------------------------------------------------
# question 1 — when and how the map went bare


def bare_map_record(sid, tr, uid):
    """The last plant-bearing turn, what died, who is EVIDENCED to have felled it, and whether
    the shack could have replanted at that moment."""
    with_plants = [t for t in range(1, tr.T + 1) if tr.state(t).plants]
    if not with_plants:
        raise G3Error(f"{sid}: no turn of the replay carries a plant at all; there is no "
                      f"'went bare' event to describe.")
    last = max(with_plants)
    if last == tr.T:
        return {"went_bare": False, "last_plant_bearing_turn": last,
                "note": "the board still carries a plant on the final harness turn"}
    gap = [t for t in range(1, tr.T + 1) if not tr.state(t).plants]
    st = tr.state(last)
    survivors = list(st.plants)
    inv = list(st.inventories[0])
    # ATTRIBUTION, from commands only. Our transcript carries OUR side's commands; an opponent
    # chop is not observable here and is therefore never claimed.
    deaths = []
    for p in survivors:
        cmd = tr.cmd_of(uid, last)
        u = tr.unit(uid, last)
        own_chop = (cmd is not None and cmd.verb == "CHOP" and u is not None
                    and tuple(u.cell) == tuple(p.cell))
        deaths.append({
            "cell": list(p.cell), "kind": p.kind, "size": p.size,
            "health_on_its_last_turn": p.health, "fruits_on_its_last_turn": p.fruits,
            "felled_by": "OWN_UNIT_CHOP" if own_chop else "UNATTRIBUTED_OWN_SIDE",
            "evidence": (f"trace command on turn {last}: {cmd.raw!r}, audited unit on the "
                         f"plant's own cell {list(p.cell)}, chop_power "
                         f"{u.chop_power}, plant health {p.health}") if own_chop else
                        ("no CHOP command by the audited unit on this cell this turn; the "
                         "transcript carries our side's commands only, so no felling agent is "
                         "named"),
            "audited_unit_chop_power": None if u is None else u.chop_power,
        })
    return {
        "went_bare": True,
        "last_plant_bearing_turn": last,
        "first_bare_turn": min(gap),
        "bare_turns": len(gap),
        "last_plants": deaths,
        "shack_inventory_at_that_moment": dict(zip(ITEMS, inv)),
        "replant_material_in_shack": {k: inv[ITEMS.index(k)] for k in SEED_ITEMS
                                      if inv[ITEMS.index(k)] > 0},
        "replant_material_present": any(inv[ITEMS.index(k)] > 0 for k in SEED_ITEMS),
    }


# ---------------------------------------------------------------------------
# question 3 — the opening's missing items and whether a source ever existed


def opening_sources(sid, tr, uid, parsed, abandon_turn):
    """For each item the cost was short of at the deadline: did a live, reachable source of that
    kind exist on any turn before the deadline, and did an opponent ever stand on it?"""
    if abandon_turn is None:
        raise G3Error(f"{sid}: the opening was never abandoned; question 3 assumes it was.")
    missing = CA.missing_items(parsed["opening"][abandon_turn])
    out = {}
    for item, short_by in missing.items():
        kind = item.upper()
        if kind == "IRON":
            out[item] = {"short_by": short_by, "source": "IRON terrain, not a plant",
                         "iron_cells_on_map": len(tr.smap.iron)}
            continue
        alive, reachable, with_fruit, opp_on_it = [], [], [], []
        best_trip = None
        for t in range(1, abandon_turn):
            st, u = tr.state(t), tr.unit(uid, t)
            reach = OR.reachable_from(tr, u.cell) if u is not None else {}
            opp_cells = {tuple(x.cell) for x in st.units if x.player == 1}
            for p in st.plants:
                if p.kind != kind or p.health <= 0:
                    continue
                alive.append(t)
                if p.cell in reach:
                    reachable.append(t)
                    if p.fruits > 0:
                        with_fruit.append(t)
                        # LOWER BOUND ONLY on banking ONE fruit of this kind starting at t:
                        # walk to the tree, one HARVEST turn, walk to a shack door, one DROP
                        # turn. It ignores the shortfall being more than one fruit, the other
                        # kinds competing for the same turns, capacity, and everything the unit
                        # was actually doing. A bound that is already past the deadline settles
                        # the question; a bound inside it settles NOTHING and must not be read
                        # as "there was time".
                        home = tr.door_dist.get(p.cell)
                        if home is not None:
                            ms = max(u.speed, 1)
                            trip = -(-reach[p.cell] // ms) + 1 + -(-home // ms) + 1
                            cand = {"from_turn": t, "steps_unit_to_source": reach[p.cell],
                                    "steps_source_to_shack_door": home, "unit_speed": ms,
                                    "earliest_turn_one_fruit_could_be_banked": t + trip,
                                    "deadline_turn": abandon_turn,
                                    "bound_is_past_the_deadline": t + trip > abandon_turn}
                            if best_trip is None or (cand["earliest_turn_one_fruit_could_be_banked"]
                                                     < best_trip["earliest_turn_one_fruit_could_be_banked"]):
                                best_trip = cand
                if tuple(p.cell) in opp_cells:
                    opp_on_it.append(t)
                break
        out[item] = {
            "short_by": short_by,
            "turns_before_deadline": abandon_turn - 1,
            "turns_a_live_source_existed_anywhere": len(alive),
            "turns_a_live_source_was_reachable": len(reachable),
            "turns_a_reachable_live_source_carried_fruit": len(with_fruit),
            "first_turn_reachable_with_fruit": with_fruit[0] if with_fruit else None,
            "turns_an_opponent_unit_stood_on_a_source": len(opp_on_it),
            "kind_ever_on_the_map_at_all": bool(alive),
            "one_fruit_round_trip_lower_bound": best_trip,
        }
    return {"abandon_turn": abandon_turn, "missing_at_abandon": missing, "per_item": out}


def min_second_troll_cost(tr):
    """The cheapest second troll the opening could ever ask for, and whether the map could pay.

    Source-derived, not assumed: `opening_options` (candidate-door1.rs:842) enumerates
    movement_speed 1..=3, carry_capacity 1..=max, chop_power 1..=max with harvest_power fixed at
    0, and `training_cost` (bot/main.py:128) charges n + stat^2 per item with n = own unit count.
    With n = 1 the floor over every option is PLUM 2, LEMON 2, APPLE 1 — APPLE because n alone
    already costs 1 at harvest_power 0. IRON is charged only when `view.iron` is non-empty
    (`training_affordable`, :899).

    Against that floor this reports, MEASURED over the whole replay, the best the shack ever held
    and whether a plant of each kind ever stood on the map at all. A floor the map cannot pay
    means no second troll was ever affordable, on any turn, under any stats.
    """
    floor = {"PLUM": 2, "LEMON": 2, "APPLE": 1}
    best = {k: 0 for k in floor}
    on_map = {k: False for k in floor}
    for t in range(1, tr.T + 1):
        st = tr.state(t)
        for k in floor:
            best[k] = max(best[k], st.inventories[0][ITEMS.index(k)])
            if any(p.kind == k and p.health > 0 for p in st.plants):
                on_map[k] = True
    # TWO DIFFERENT THINGS, and collapsing them is the error this task is most prone to.
    # "the shack never held enough" is an OUTCOME — it can mean the fruit existed and was never
    # delivered. "no live source ever existed" is a property of the MAP and is the only one of
    # the two that makes the shortfall unfixable by playing better. On OSC-032 PLUM is in the
    # first set and not the second: a fruiting plum stood reachable for all 34 pre-deadline
    # turns and the shack still ended on zero.
    never_held = sorted(k for k in floor if best[k] < floor[k])
    never_sourced = sorted(k for k in floor if not on_map[k] and best[k] < floor[k])
    return {
        "floor_over_every_opening_option": floor,
        "floor_source": "opening_options ms 1..3 / cc 1..max / chop 1..max, harvest_power 0 "
                        "(candidate-door1.rs:842) x training_cost n + stat^2 (bot/main.py:128) "
                        "with n = 1",
        "iron_charged": len(tr.smap.iron) > 0,
        "best_shack_holding_over_the_whole_replay": best,
        "kind_ever_alive_on_the_map": on_map,
        "items_the_shack_never_held_enough_of": never_held,
        "items_no_live_source_ever_existed_for": never_sourced,
        "second_troll_affordable_on_any_turn_under_any_stats": not never_held,
        "second_troll_impossible_from_turn_1_by_map_content": bool(never_sourced),
    }


def opponent_capability(tr):
    """Chop power of every opponent unit seen — the denial half of H-A needs it."""
    powers = collections.Counter()
    for t in range(1, tr.T + 1):
        for u in tr.state(t).units:
            if u.player == 1:
                powers[u.chop_power] += 1
    return {"opponent_unit_turns_by_chop_power": {str(k): v for k, v in sorted(powers.items())}}


# ---------------------------------------------------------------------------
# question 4 + deliverable 3 outside the windows


def replant_full(parsed, uid):
    """Every replant row of the WHOLE game, not just the window, and the co-false conjuncts."""
    rows, false_counts, co_false = [], collections.Counter(), collections.Counter()
    for (unit, turn), r in sorted(parsed["replant"].items()):
        if unit != uid:
            continue
        falses = sorted(k for k, v in r.items() if k.startswith("c") and v == "false")
        for k in falses:
            false_counts[k] += 1
        others = [k for k in falses if k != "c5_own_units_ge_2"]
        co_false[",".join(others) if others else "(none)"] += 1
        rows.append({"turn": turn, "false_conjuncts": falses})
    n = len(rows)
    if not n:
        raise G3Error("no replant rows at all; question 4 cannot be answered.")
    return {
        "turns_measured": n,
        "conjunct_false_counts": dict(false_counts),
        "always_false_conjuncts": sorted(k for k, v in false_counts.items() if v == n),
        "turns_all_seven_true": [r["turn"] for r in rows if not r["false_conjuncts"]],
        "co_false_with_c5_own_units_ge_2": dict(co_false),
    }


def out_of_window_clause_rows(parsed, uid, lo, hi):
    """Deliverable 3 where it is not vacuous: named clause per plant per turn OUTSIDE the window.

    The windows carry an empty board on every audited turn (G-2 recorded that honestly), so the
    per-plant direction of deliverable 3 has content only here.
    """
    out, counts = [], collections.Counter()
    for label, groups in (("chop", parsed["chop"]), ("idle_harvest", parsed["harvest"])):
        for (unit, turn), gs in sorted(groups.items()):
            if unit != uid or lo <= turn <= hi:
                continue
            g = gs[0]
            if g["clause"] != "ENTERED":
                counts[f"{label}:FN:{g['clause']}"] += 1
                continue
            for p in g["plants"]:
                counts[f"{label}:{p['clause']}"] += 1
            if g["plants"]:
                out.append({"call": label, "turn": turn, "plants": g["plants"]})
    if not out:
        raise G3Error(
            "no out-of-window call saw a plant, so deliverable 3 is vacuous EVERYWHERE on this "
            "fixture and the clause tap attributed nothing to any real tree.")
    return {"rows": out, "clause_counts": dict(counts)}


def hc_observation_denominator(sid, tr, uid, parsed, routes):
    """The honest denominator for H-C: of the turns that HAD a plant on the board, on how many
    was the chop generator actually asked, and what did it say?

    H-C claims live reachable trees were REJECTED by a named clause. "No rejection was recorded"
    only refutes it over the turns where the generator was asked and entered the loop. On every
    other plant-bearing turn the bot returned by some earlier route and the clause question was
    never put, so H-C is UNOBSERVED there, not refuted. Reporting the accepted count without this
    denominator would be exactly the shape of claim this task exists to avoid.
    """
    plant_turns = [t for t in range(1, tr.T + 1) if tr.state(t).plants]
    entered, guard_return, no_group = [], [], []
    accepted_rows = rejected_rows = 0
    reject_clauses = collections.Counter()
    for t in plant_turns:
        gs = parsed["chop"].get((uid, t))
        if not gs:
            no_group.append(t)
            continue
        g = gs[0]
        if g["clause"] != "ENTERED":
            guard_return.append({"turn": t, "guard": g["clause"]})
            continue
        entered.append(t)
        for pl in g["plants"]:
            if pl["clause"] == "ACCEPTED":
                accepted_rows += 1
            else:
                rejected_rows += 1
                reject_clauses[pl["clause"]] += 1
    return {
        "plant_bearing_turns": len(plant_turns),
        "turns_the_chop_generator_entered_the_loop": len(entered),
        "turns_it_returned_at_a_function_guard": len(guard_return),
        "guard_returns": guard_return[:20],
        "turns_with_no_chop_call_at_all_route_never_reached_it": len(no_group),
        "routes_on_those_turns": dict(collections.Counter(
            routes[(uid, t)]["fn"] + ":" + routes[(uid, t)]["route"]
            for t in no_group if (uid, t) in routes)),
        "accepted_plant_rows": accepted_rows,
        "rejected_plant_rows": rejected_rows,
        "rejection_clauses_seen": dict(reject_clauses),
        "h_c_is_unobserved_on_turns": len(no_group) + len(guard_return),
    }


# ---------------------------------------------------------------------------


def main():
    units = {r["situation"]: r["unit"]
             for r in json.loads(CA.CAUSE_TABLE.read_text())["table"]}
    man = json.loads(CA.MANIFEST.read_text())[CA.SUBJECT]
    cfg = json.loads(H.CONFIG.read_text())
    sits = {s["id"]: s for s in H.load_situations(FIXTURES)}
    turns = int(cfg["turns"])

    print("stall-predicate control ...")
    control = stall_negative_control()
    for c in control:
        print(f"  {c['case']:38s} stalled={c['stalled']} (required {c['must_be']})")

    fixtures = []
    with tempfile.TemporaryDirectory(prefix="g3-") as wd:
        wd = Path(wd)
        for d in ("p", "c"):
            (wd / d).mkdir()
        print(f"compiling champion {man['source_sha256'][:12]} + the clause tap ...")
        plain = H.compile_candidate(REPO / man["source"], wd / "p")
        probe = H.compile_candidate(REPO / man["probe"], wd / "c")
        for sid in FIXTURES:
            sit, uid = sits[sid], units[sid]
            lo, hi = sit["window"]["turn_start"], sit["window"]["turn_end"]
            err = C.check_parity(sit, cfg, plain, probe)     # the G-2 parity gate, unchanged
            finals, routes = CA.route_rows_all_units(err)
            parsed = CT.parse(err)
            CT.check(sid, parsed, routes)
            spec = H.spec_for(sit, cfg)
            transcript, commands, _ = C.run_diagnostic(probe, fp.make_referee(spec), turns)
            tr = td.build_trace(transcript, commands)
            CA.check_trace_agrees_with_tap(sid, parsed, tr, uid)

            _, abandon = CA.opening_rows(parsed, turns)
            bare = bare_map_record(sid, tr, uid)
            stall = stall_projection(sid, tr)
            row = {
                "id": sid, "unit": uid, "window": [lo, hi],
                "q1_map_went_bare": bare,
                "q2_referee_stall_projection": stall,
                "q2_window_turns_after_the_referee_end": {
                    "audited_window": [lo, hi],
                    "window_turns_in_the_harness": hi - lo + 1,
                    "window_turns_the_referee_would_have_played_full_rule":
                        max(0, min(hi, stall["first_stalled_turn"] - 1) - lo + 1),
                    "window_turns_the_referee_would_have_played_grace_only":
                        max(0, min(hi, (stall["grace_only_end_turn"] or hi + 1) - 1) - lo + 1),
                },
                "q3_opening": opening_sources(sid, tr, uid, parsed, abandon),
                "q3_opponent": opponent_capability(tr),
                "q3_min_second_troll_cost": min_second_troll_cost(tr),
                "q4_replant_full_game": replant_full(parsed, uid),
                "d3_out_of_window_clause_rows": out_of_window_clause_rows(parsed, uid, lo, hi),
                "q5_hc_observation_denominator":
                    hc_observation_denominator(sid, tr, uid, parsed, routes),
            }
            fixtures.append(row)
            print(f"  {sid} unit {uid} window {lo}-{hi}")
            print(f"      bare from turn {bare.get('first_bare_turn')}; last plants "
                  f"{[(p['kind'], p['felled_by']) for p in bare.get('last_plants', [])]}")
            print(f"      shack held {bare.get('replant_material_in_shack')}")
            print(f"      REFEREE would have ended at turn {stall['first_stalled_turn']} "
                  f"({stall['reason']}); harness ran to {stall['harness_horizon_turns']}, "
                  f"{stall['turns_after_the_referee_would_have_ended']} turns past it; "
                  f"grace-only bound {stall['grace_only_end_turn']}")
            print(f"      opening abandoned {row['q3_opening']['abandon_turn']}, short of "
                  f"{row['q3_opening']['missing_at_abandon']}")
            for item, d in row["q3_opening"]["per_item"].items():
                if "kind_ever_on_the_map_at_all" in d:
                    print(f"        {item:6s} short {d['short_by']}  ever_on_map="
                          f"{d['kind_ever_on_the_map_at_all']}  reachable_turns="
                          f"{d['turns_a_live_source_was_reachable']}  opp_on_source="
                          f"{d['turns_an_opponent_unit_stood_on_a_source']}")
            print(f"      replant co-false with c5: {row['q4_replant_full_game']['co_false_with_c5_own_units_ge_2']}")
            m = row["q3_min_second_troll_cost"]
            print(f"      min second-troll cost {m['floor_over_every_opening_option']}; best "
                  f"shack holding ever {m['best_shack_holding_over_the_whole_replay']}; never "
                  f"held enough {m['items_the_shack_never_held_enough_of']}; NO SOURCE EVER "
                  f"{m['items_no_live_source_ever_existed_for']}")
            h = row["q5_hc_observation_denominator"]
            print(f"      H-C denominator: {h['plant_bearing_turns']} plant-bearing turns, "
                  f"generator entered on {h['turns_the_chop_generator_entered_the_loop']}, "
                  f"{h['accepted_plant_rows']} accepted / {h['rejected_plant_rows']} rejected "
                  f"plant rows, UNOBSERVED on {h['h_c_is_unobserved_on_turns']}")
            print(f"      routes on the unasked turns: {h['routes_on_those_turns']}")

    OUT.write_text(json.dumps({
        "task": "20260821-osc032-033-cause-attribution",
        "gate": "G-3",
        "scope": "measurement only; no fix, no candidate, no behaviour change, no class-wide "
                 "claim; bug-versus-correct-caution is the OWNER's ruling and is not made here",
        "base": {"name": CA.SUBJECT, "source": man["source"],
                 "source_sha256": man["source_sha256"]},
        "probe": {"path": man["probe"], "sha256": man["probe_sha256"]},
        "frozen_predicate": {
            "module": "sim/engine.py", "function": "has_stalled",
            "note": "unmodified and unwrapped; this file builds sim.state.GameState from the "
                    "referee trace and hands it over. Scores from sim.engine.recompute_scores.",
            "rust_original": "rust/src/game/engine.rs:819 has_stalled (referee v1.0.5 "
                             "Board.hasStalled)"},
        "harness_note": "claude_1/banana-restoration-r2/regression_tests.py:run_binary_custom "
                        "runs a FIXED cfg['turns'] horizon and never calls a stall check, which "
                        "is why the replay reaches turns a real game would not.",
        "stall_predicate_control": control,
        "gates": [
            "parity: the clause probe's command stream is byte-identical to the uninstrumented "
            "champion's on both fixtures (the G-2-accepted gate, re-run here unchanged)",
            "clause-tap gates 1-5 and the referee/tap IDENTITY agreement gate, re-run unchanged",
            "adapter fidelity, per turn: the sim.state.GameState handed to the frozen predicate "
            "matches the referee trace by plant canonical record, unit (id, player, cell, ms, "
            "carry) and BOTH inventories; a mismatch fails the run",
            "stall non-vacuity, per fixture: has_stalled must be observed returning False on a "
            "plant-bearing turn AND True on a bare one, or no end turn is reported",
            "stall predicate control: four constructed states, two that must stall and two that "
            "must not, covering the grace counter, the both-stuck rule and the fruit-held escape",
            "felling attribution is command-evidenced or UNATTRIBUTED; standing on the tree is "
            "not accepted as evidence, and the opponent is never named because the transcript "
            "carries our side's commands only",
            "deliverable 3 out-of-window: at least one call must have seen a real plant, or the "
            "run fails rather than reporting a vacuous per-plant attribution",
        ],
        "fixtures": fixtures}, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
