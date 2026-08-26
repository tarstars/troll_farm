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
  PS4CHOPOUT unit turn i=<k> target=<x>,<y> command=<...>   — the RETURNED vector, element k
  PS4CHOPLIST unit turn returned=<n>                        — its length, closing the call
  PS4HARVOUT / PS4HARVLIST                                  — the same, for idle-harvest
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
5. **per-plant identity against the returned vector.** `PS4CHOPOUT` is read off `out` AFTER the
   loop — the vector the generator actually returns — not off the loop's control flow. The
   ordered target cells of that vector must equal the ordered cells of this call's own
   `clause=ACCEPTED` rows, element for element. Cardinality alone cannot carry this: the same
   `chops=` count survives when acceptance is attached to the wrong cell, which is precisely what
   a count-only join fails to catch. A pushed candidate with no `ACCEPTED` row, an `ACCEPTED` row
   on a cell that was never pushed, or a same-count-different-cells permutation all fail the run.
   A call that returned at the function guard must emit no list at all.
6. **cross-check against the ACCEPTED route probe**: the length of that returned vector must equal
   the `chops=` count the `PS3ROUTE` row printed for the same unit and turn, and a route that
   provably never calls `chop_candidates` must have no chop group at all. Gate 5 is what makes
   "the tap cannot name a rejecting clause on a plant the generator accepted" a per-plant
   measurement rather than a claim about my own edit; gate 6 ties that vector to the accepted
   probe's own reading of the same call.
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
RE_CHOPOUT = re.compile(r"^PS4CHOPOUT unit=(-?\d+) turn=(\d+) i=(\d+) target=(\S+) command=(\S+)$")
RE_CHOPLIST = re.compile(r"^PS4CHOPLIST unit=(-?\d+) turn=(\d+) returned=(\d+)$")
RE_HARVOUT = re.compile(r"^PS4HARVOUT unit=(-?\d+) turn=(\d+) i=(\d+) target=(\S+) command=(\S+)$")
RE_HARVLIST = re.compile(r"^PS4HARVLIST unit=(-?\d+) turn=(\d+) returned=(\d+)$")
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
        m = RE_CHOPOUT.match(line)
        if m:
            if cur_chop is None:
                raise ClauseGateError(
                    f"a PS4CHOPOUT row for unit {m.group(1)} turn {m.group(2)} arrived with no "
                    f"open PS4CHOPFN group — a returned candidate outside a call is unattributable.")
            cur_chop["returned"].append(
                {"i": int(m.group(3)), "target": m.group(4), "command": m.group(5)})
            continue
        m = RE_CHOPLIST.match(line)
        if m:
            if cur_chop is None:
                raise ClauseGateError(
                    f"a PS4CHOPLIST row for unit {m.group(1)} turn {m.group(2)} arrived with no "
                    f"open PS4CHOPFN group.")
            cur_chop["returned_n"] = int(m.group(3))
            continue
        m = RE_CHOPFN.match(line)
        if m:
            unit, turn = int(m.group(1)), int(m.group(2))
            cur_chop = {"clause": m.group(3), "fields": kv(m.group(4)), "plants": [],
                        "returned": [], "returned_n": None}
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
        m = RE_HARVOUT.match(line)
        if m:
            if cur_harv is None:
                raise ClauseGateError(
                    f"a PS4HARVOUT row for unit {m.group(1)} turn {m.group(2)} arrived with no "
                    f"open PS4HARVFN group — a returned candidate outside a call is unattributable.")
            cur_harv["returned"].append(
                {"i": int(m.group(3)), "target": m.group(4), "command": m.group(5)})
            continue
        m = RE_HARVLIST.match(line)
        if m:
            if cur_harv is None:
                raise ClauseGateError(
                    f"a PS4HARVLIST row for unit {m.group(1)} turn {m.group(2)} arrived with no "
                    f"open PS4HARVFN group.")
            cur_harv["returned_n"] = int(m.group(3))
            continue
        m = RE_HARVFN.match(line)
        if m:
            unit, turn = int(m.group(1)), int(m.group(2))
            cur_harv = {"clause": m.group(3), "fields": kv(m.group(4)), "plants": [],
                        "returned": [], "returned_n": None}
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


def check_returned_lists(sid, label, groups):
    """Gate 5 — the ACCEPTED rows and the RETURNED vector name the same cells, in the same order.

    `PS4{CHOP,HARV}OUT` is emitted from the vector the generator hands back, after the loop is
    over, by reading each candidate's own `Target::Tree(cell)`. The loop's `clause=ACCEPTED` rows
    come from the control flow. Comparing the two ORDERED cell sequences is what rules out the
    failure a count-only join cannot see: acceptance recorded against the wrong cell, with the
    cardinality intact.
    """
    joined = 0
    for (unit, turn), gs in sorted(groups.items()):
        for g in gs:
            if g["clause"] != "ENTERED":
                if g["returned"] or g["returned_n"] is not None:
                    raise ClauseGateError(
                        f"{sid} unit {unit} turn {turn}: {label} returned at the function guard "
                        f"({g['clause']}) yet a returned-vector row was emitted — the list row "
                        f"belongs to a call that never built a list.")
                continue
            if g["returned_n"] is None:
                raise ClauseGateError(
                    f"{sid} unit {unit} turn {turn}: {label} entered but emitted no "
                    f"PS4{'CHOP' if label == 'chop' else 'HARV'}LIST row. Without the returned "
                    f"vector the accepted side is a bare count and no clause may be reported.")
            got = g["returned"]
            if len(got) != g["returned_n"]:
                raise ClauseGateError(
                    f"{sid} unit {unit} turn {turn}: {label} returned {g['returned_n']} candidates "
                    f"but {len(got)} were listed — the list row and its elements disagree.")
            if [r["i"] for r in got] != list(range(len(got))):
                raise ClauseGateError(
                    f"{sid} unit {unit} turn {turn}: {label} returned-vector indices "
                    f"{[r['i'] for r in got]} are not 0..{len(got) - 1} in order; the elements are "
                    f"not the vector's own order and may not be joined positionally.")
            bad = [r for r in got if not RE_CELL.match(r["target"])]
            if bad:
                raise ClauseGateError(
                    f"{sid} unit {unit} turn {turn}: {label} returned a candidate whose target is "
                    f"{bad[0]['target']!r}, not a tree cell. Every candidate these two generators "
                    f"build targets the plant it was built from; anything else means the reader is "
                    f"joining candidates it does not understand.")
            returned_cells = [tuple(int(x) for x in r["target"].split(",")) for r in got]
            accepted_cells = [tuple(pl["cell"]) for pl in g["plants"] if pl["clause"] == "ACCEPTED"]
            if returned_cells != accepted_cells:
                raise ClauseGateError(
                    f"{sid} unit {unit} turn {turn}: {label} named clause=ACCEPTED on "
                    f"{accepted_cells} but the vector it returned targets {returned_cells}. The "
                    f"tap's accepted side is not the generator's accepted side — per-plant, not "
                    f"merely in count — so no clause may be attributed on any plant of this call.")
            joined += len(got)
    return joined


RE_CELL = re.compile(r"^-?\d+,-?\d+$")


def check(sid, parsed, route_rows):
    """All five gates. `route_rows` maps (unit, turn) -> the ACCEPTED probe's one route row."""
    _check_groups(sid, "chop", parsed["chop"], CHOP_CLAUSES, one_group_only=True)
    _check_groups(sid, "idle-harvest", parsed["harvest"], HARV_CLAUSES, one_group_only=False)
    check_returned_lists(sid, "chop", parsed["chop"])
    check_returned_lists(sid, "idle-harvest", parsed["harvest"])

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
        # Gate 5 has already established that these ACCEPTED rows and the returned vector name
        # the same cells in the same order, so this length is the vector's, not a bare tally.
        got = len(gs[0]["returned"])
        want = row.get("chops")
        if want is None:
            continue
        if got != int(want):
            raise ClauseGateError(
                f"{sid} unit {unit} turn {turn}: the clause tap's returned vector holds {got} "
                f"candidates but the accepted route probe reported chops={want} on the same call. "
                f"The tap is not reading the list the generator built.")
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
