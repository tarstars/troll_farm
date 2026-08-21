#!/usr/bin/env python3
r"""The CLAUSE TAP reader — task `20260821-osc032-033-cause-attribution`, gate G-1.

The predecessor task (`20260821-osc032-033-no-goal-instrument`, all gates accepted) settled
*which return path* handed back the seeded `WAIT`: on every window turn of both fixtures it was
`main:IDLE_REGEN_FALLBACK` with `chops.is_empty()`. It deliberately did not measure *why* the
chop list was empty. This module reads the tap that does.

**Measurement only.** Nothing here proposes a change, names a bug, or judges whether a rejection
was right. Bug-versus-correct-caution is the OWNER's ruling afterwards.

## What the tap emits, and why it cannot be a taxonomy I invented

Every clause name below is a `continue`/`return` that already existed in the champion source.
The probe edits (`make_route_probe.py`, subject `door1-clause`) only split `a||b` guards into
their two named halves and turn one iterator chain into the same loop. So the tap cannot report
a reason the generator does not have, and it cannot omit one: the loop body has exactly one exit
per plant, and every exit carries a row.

  PS4CHOPFN unit turn clause=<FN_NO_CHOP_POWER|FN_NO_FREE_CAPACITY|ENTERED> ... plants=<n>
  PS4CHOP   unit turn plant=<x>,<y> kind clause=<one of CHOP_CLAUSES> ...
  PS4HARVFN unit turn clause=<FN_CARRYING|FN_NO_HARVEST_POWER|ENTERED> ... plants=<n>
  PS4HARV   unit turn plant=<x>,<y> kind clause=<one of HARV_CLAUSES> ...
  PS4REPLANT unit turn c1..c7 ...            — the replant block's seven conjuncts
  PS4OPEN   turn ...                          — the opening, AFTER enforce_training_deadline
  PS4DEADLINE turn event=<...> [reason=<...>] — the deadline, and which branch abandoned

## The gates, all fail-closed

1. **one call-group per unit-turn** for the chop tap. `commands()` picks ONE generator and each
   generator calls `chop_candidates` at most once, so a second group means the tap double-counts
   and no clause may be reported.
2. **exact coverage inside a group**: an `ENTERED` group carries exactly one row per entry of
   `view.plants` (the count the tap itself printed), with no repeated plant cell. A plant with no
   named clause fails the run — it is not silently dropped.
3. **no rows without a call**: a non-`ENTERED` group carries zero plant rows.
4. **clause names are closed sets.** An unknown clause is an error, not an "other" bucket.
5. **cross-check against the ACCEPTED route probe**: the number of `ACCEPTED` chop rows must equal
   the `chops=` count the `PS3ROUTE` row printed for the same unit and turn, and a route that
   provably never calls `chop_candidates` must have no chop group at all. This is what makes
   "the tap cannot name a clause on a plant the generator accepted" a measurement rather than a
   claim about my own edit.
"""
from __future__ import annotations

import re

CHOP_CLAUSES = ("PLANT_DEAD", "UNREACHABLE_FROM_UNIT", "PREDICT_TREE_NONE",
                "PREDICTED_SIZE_NONPOSITIVE", "PREDICTED_HEALTH_NONPOSITIVE",
                "CHOP_OUTCOME_NONE", "TRIP_LONGER_THAN_GAME", "WOOD_NONPOSITIVE", "ACCEPTED")
HARV_CLAUSES = ("PLANT_DEAD", "NO_FRUITS", "OPPONENT_EMPTY_HANDED_ON_CELL",
                "UNREACHABLE_FROM_UNIT", "NO_PATH_TO_SHACK_DOOR", "TRIP_LONGER_THAN_GAME",
                "ACCEPTED")

# The routes whose source path reaches `chop_candidates`, read off the champion source rather
# than guessed: main's tail computes `chops` before IDLE_REGEN_FALLBACK / NOCHOP_BANK / CHOPS,
# endgame computes it before CHOP_CURRENT / CONVERSION_TAIL, and early's tail calls it directly.
# Every other route returns first.
ROUTES_CALLING_CHOP = {"main:IDLE_REGEN_FALLBACK", "main:NOCHOP_BANK", "main:CHOPS",
                       "endgame:CHOP_CURRENT", "endgame:CONVERSION_TAIL",
                       "early:EARLY_CHOP_FALLBACK"}

RE_CHOPFN = re.compile(r"^PS4CHOPFN unit=(-?\d+) turn=(\d+) clause=(\w+) (.*)$")
RE_CHOP = re.compile(r"^PS4CHOP unit=(-?\d+) turn=(\d+) plant=(-?\d+),(-?\d+) kind=(\w+) "
                     r"clause=(\w+) ?(.*)$")
RE_HARVFN = re.compile(r"^PS4HARVFN unit=(-?\d+) turn=(\d+) clause=(\w+) (.*)$")
RE_HARV = re.compile(r"^PS4HARV unit=(-?\d+) turn=(\d+) plant=(-?\d+),(-?\d+) kind=(\w+) "
                     r"clause=(\w+) ?(.*)$")
RE_REPLANT = re.compile(r"^PS4REPLANT unit=(-?\d+) turn=(\d+) (.*)$")
RE_OPEN = re.compile(r"^PS4OPEN turn=(\d+) (.*)$")
RE_DEADLINE = re.compile(r"^PS4DEADLINE turn=(\d+) event=(\w+) ?(.*)$")


class ClauseGateError(Exception):
    """A tap contract that did not hold. Nothing is reported when one of these is raised."""


def kv(rest):
    out = {}
    for tok in rest.split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            out[k] = v
    return out


def parse(err):
    """Stream order matters: groups are opened by an FN row and closed by the next one."""
    chop_groups, harv_groups = {}, {}
    replant, opening, deadline = {}, {}, []
    cur_chop = cur_harv = None
    for line in err.splitlines():
        m = RE_CHOPFN.match(line)
        if m:
            unit, turn = int(m.group(1)), int(m.group(2))
            cur_chop = {"clause": m.group(3), "fields": kv(m.group(4)), "plants": []}
            chop_groups.setdefault((unit, turn), []).append(cur_chop)
            continue
        m = RE_CHOP.match(line)
        if m:
            if cur_chop is None:
                raise ClauseGateError(
                    f"a PS4CHOP row for unit {m.group(1)} turn {m.group(2)} arrived with no open "
                    f"PS4CHOPFN group — a plant row outside a call is unattributable.")
            cur_chop["plants"].append(
                {"cell": [int(m.group(3)), int(m.group(4))], "kind": m.group(5),
                 "clause": m.group(6), "fields": kv(m.group(7))})
            continue
        m = RE_HARVFN.match(line)
        if m:
            unit, turn = int(m.group(1)), int(m.group(2))
            cur_harv = {"clause": m.group(3), "fields": kv(m.group(4)), "plants": []}
            harv_groups.setdefault((unit, turn), []).append(cur_harv)
            continue
        m = RE_HARV.match(line)
        if m:
            if cur_harv is None:
                raise ClauseGateError(
                    f"a PS4HARV row for unit {m.group(1)} turn {m.group(2)} arrived with no open "
                    f"PS4HARVFN group — a plant row outside a call is unattributable.")
            cur_harv["plants"].append(
                {"cell": [int(m.group(3)), int(m.group(4))], "kind": m.group(5),
                 "clause": m.group(6), "fields": kv(m.group(7))})
            continue
        m = RE_REPLANT.match(line)
        if m:
            replant[(int(m.group(1)), int(m.group(2)))] = kv(m.group(3))
            continue
        m = RE_OPEN.match(line)
        if m:
            opening[int(m.group(1))] = kv(m.group(2))
            continue
        m = RE_DEADLINE.match(line)
        if m:
            deadline.append({"turn": int(m.group(1)), "event": m.group(2),
                             **kv(m.group(3))})
    return {"chop": chop_groups, "harvest": harv_groups, "replant": replant,
            "opening": opening, "deadline": deadline}


def _check_groups(sid, label, groups, clauses, one_group_only):
    for (unit, turn), gs in sorted(groups.items()):
        if one_group_only and len(gs) > 1:
            raise ClauseGateError(
                f"{sid} unit {unit} turn {turn}: {len(gs)} {label} call-groups. `commands()` picks "
                f"ONE generator and each generator calls the function at most once per unit-turn, "
                f"so a second group means the tap double-counts; no clause may be reported.")
        for g in gs:
            if g["clause"] != "ENTERED":
                if g["plants"]:
                    raise ClauseGateError(
                        f"{sid} unit {unit} turn {turn}: {label} returned at the function guard "
                        f"({g['clause']}) yet {len(g['plants'])} plant rows were emitted — a "
                        f"clause on a plant the function never looked at.")
                continue
            want = int(g["fields"]["plants"])
            if len(g["plants"]) != want:
                raise ClauseGateError(
                    f"{sid} unit {unit} turn {turn}: {label} entered with {want} plants on the "
                    f"board but named a clause on {len(g['plants'])}. Fail-closed: a plant with "
                    f"no named clause is not reported as if it had one.")
            cells = [tuple(p["cell"]) for p in g["plants"]]
            if len(set(cells)) != len(cells):
                dupes = sorted({c for c in cells if cells.count(c) > 1})
                raise ClauseGateError(
                    f"{sid} unit {unit} turn {turn}: {label} named more than one clause on "
                    f"plant(s) {dupes} — one plant per turn takes ONE exit.")
            bad = sorted({p["clause"] for p in g["plants"]} - set(clauses))
            if bad:
                raise ClauseGateError(
                    f"{sid} unit {unit} turn {turn}: unknown {label} clause(s) {bad}. The clause "
                    f"set is closed by construction; an unknown name means the probe and this "
                    f"reader have drifted apart.")


def check(sid, parsed, route_rows):
    """All five gates. `route_rows` maps (unit, turn) -> the ACCEPTED probe's one route row."""
    _check_groups(sid, "chop", parsed["chop"], CHOP_CLAUSES, one_group_only=True)
    _check_groups(sid, "idle-harvest", parsed["harvest"], HARV_CLAUSES, one_group_only=False)

    for (unit, turn), gs in sorted(parsed["chop"].items()):
        row = route_rows.get((unit, turn))
        if row is None:
            raise ClauseGateError(
                f"{sid} unit {unit} turn {turn}: the clause tap saw a chop call on a turn the "
                f"ACCEPTED route probe named no route for. The two taps are reading different "
                f"turns and nothing may be joined.")
        tag = f"{row['fn']}:{row['route']}"
        if tag not in ROUTES_CALLING_CHOP:
            raise ClauseGateError(
                f"{sid} unit {unit} turn {turn}: route {tag} returns before `chop_candidates` in "
                f"the champion source, yet the clause tap recorded a call. Either the route map "
                f"is wrong or an edit moved the call; no cause is reported either way.")
        got = sum(1 for p in gs[0]["plants"] if p["clause"] == "ACCEPTED")
        want = row.get("chops")
        if want is None:
            continue
        if got != int(want):
            raise ClauseGateError(
                f"{sid} unit {unit} turn {turn}: the clause tap ACCEPTED {got} plants but the "
                f"accepted route probe reported chops={want} on the same call. The tap is not "
                f"reading the list the generator built.")
    for (unit, turn), row in sorted(route_rows.items()):
        tag = f"{row['fn']}:{row['route']}"
        if tag in ROUTES_CALLING_CHOP and (unit, turn) not in parsed["chop"]:
            raise ClauseGateError(
                f"{sid} unit {unit} turn {turn}: route {tag} calls `chop_candidates` but the "
                f"clause tap recorded no call — a turn the instrument cannot read.")


def both_ways(sid, parsed, audited_window, named_window=None):
    """G-2's both-ways control: the tap must be OBSERVED saying ACCEPTED, not only rejecting.

    Two windows, and neither is chosen after seeing the answer:

    * the **structural** one — every turn OUTSIDE the fixture's own charter window. The audited
      window is all-`WAIT` by construction (that is what makes these the cases nobody can
      explain), so an in-window `ACCEPTED` is not expected and its absence must not be read as
      the control passing. Each fixture therefore supplies its own control from its own employed
      turns, exactly as the predecessor's accepted gate does; one fixture's non-constancy is
      never another's control.
    * the **named** one — turns 35-90, which the card names because OSC-032 carries `main:CHOPS`
      on 29 of them per the ACCEPTED route table. It is checked where the card names it and
      reported, not required, elsewhere.

    The OPPOSITE direction — that the tap can say something other than `ACCEPTED` — is NOT
    testable on these two fixtures: `view.plants` is empty on the audited turns, so no rejecting
    clause has anything to reject. It is controlled separately and corpus-wide by
    `clause_control.py`, and this function reports the in-fixture reject count so the zero is
    visible rather than implied.
    """
    lo, hi = audited_window

    def tally(pred):
        acc = rej = 0
        turns = []
        for (unit, turn), gs in sorted(parsed["chop"].items()):
            if not pred(turn):
                continue
            n = sum(1 for p in gs[0]["plants"] if p["clause"] == "ACCEPTED")
            acc += n
            rej += sum(1 for p in gs[0]["plants"] if p["clause"] != "ACCEPTED")
            if n:
                turns.append(turn)
        return acc, rej, sorted(set(turns))

    out_acc, out_rej, out_turns = tally(lambda t: not (lo <= t <= hi))
    in_acc, in_rej, _ = tally(lambda t: lo <= t <= hi)
    row = {"audited_window": [lo, hi],
           "outside_window_accepted_plant_rows": out_acc,
           "outside_window_rejected_plant_rows": out_rej,
           "outside_window_turns_with_an_accepted_tree": out_turns,
           "in_window_accepted_plant_rows": in_acc,
           "in_window_rejected_plant_rows": in_rej,
           "tap_observed_accepting_on_this_fixture": out_acc > 0,
           "reject_side_exercised_on_this_fixture": (out_rej + in_rej) > 0}
    if named_window:
        nlo, nhi = named_window
        n_acc, n_rej, n_turns = tally(lambda t: nlo <= t <= nhi)
        row["named_control_window"] = [nlo, nhi]
        row["named_window_accepted_plant_rows"] = n_acc
        row["named_window_rejected_plant_rows"] = n_rej
        row["named_window_turns_with_an_accepted_tree"] = n_turns
        row["named_control_satisfied"] = n_acc > 0
    return row
