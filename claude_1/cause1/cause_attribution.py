#!/usr/bin/env python3
r"""OSC-032/033 — WHY the chop list was empty, and why the bot played with one troll.

Task `20260821-osc032-033-cause-attribution` (coordinator-chartered at the owner's request,
2026-08-21). Work owner claude_1, instrument reviewer codex_1, integrator local_claude_1.

**Measurement only.** No fix, no candidate, no behaviour change, no harm/benefit judgment and no
class-wide claim. Whether a rejection was a bug or correct caution is the OWNER's ruling
afterwards, and this file must not pre-empt it.

## What is new here, and what is reused

Reused unchanged: `make_route_probe.py`'s seven accepted anchors and the manifest mechanism;
`coverage.check_parity` for the parity gate; `route_census`'s `PS3FINAL`/`PS3ROUTE` grammar for
the route each turn took; `trace_detectors` for the referee's own per-turn world state; and
`hstarve1/oracle.py` for the eligible-action set. The predecessor's artifacts are not touched:
the clause anchors live on a SEPARATE subject (`door1-clause`), and `make_route_probe.py` with
the new anchors off still reproduces `routeprobe-door1-champion.rs` and both p1p2 probes
byte-identically.

New, because nothing existing could answer it: the CLAUSE TAP (`clause_tap.py`). The route probe
says the generator returned through `IDLE_REGEN_FALLBACK` because `chops.is_empty()`; it cannot
say which of `chop_candidates`' eight rejecting conditions emptied it, on which tree. No existing
instrument reads inside that loop.

## The three hypotheses, and what would decide each

- **H-A (the owner's):** the opening starved — the plum/lemon the training cost needed was denied
  or out of reach — so the deadline abandoned it and the bot played one-troll to the end.
  Decided by `PS4OPEN` / `PS4DEADLINE`: the turn `opening_abandoned` flips, by which branch, and
  the cost-versus-inventory gap on that turn.
- **H-B:** a one-troll bot can never replant, because the replant block requires `own units >= 2`.
  Decided by `PS4REPLANT`: which of the seven conjuncts were false, per turn.
- **H-C:** live reachable trees existed and each failed a named clause. Decided by `PS4CHOP` /
  `PS4HARV`, joined per turn against the oracle's eligible set on the same tree.

Nothing above is a premise. Each is reported CONFIRMED / REFUTED / NOT SEPARABLE with its
evidence line at G-3, and the run fails rather than reporting when a gate does not hold.

Run:  python3 claude_1/cause1/cause_attribution.py
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
import clause_tap as CT         # noqa: E402
import coverage as C            # noqa: E402
import fixture_harness as H     # noqa: E402
import fuzz_panel as fp         # noqa: E402
import oracle as OR             # noqa: E402
import route_census as RC       # noqa: E402
import trace_detectors as td    # noqa: E402

FIXTURES = ["OSC-032", "OSC-033"]
SUBJECT = "door1-clause"
MANIFEST = HERE / "route-probe-manifest-clause-2026-08-21.json"
CAUSE_TABLE = REPO / "claude_1/hstarve1/cause-table-pool3-2026-08-17.json"
OUT = HERE / "cause-attribution-2026-08-21.json"

# The card names turns 35-90 as the span where the both-ways control must fire, because the
# ACCEPTED route table records `main:CHOPS` on 29 of them for OSC-032. It is required where the
# card names it (OSC-032) and only reported for OSC-033, whose employed chop turns fall in the
# `early` branch before turn 35 — requiring a fixture to be employed in a span it never was would
# be a gate on the corpus, not on the tap.
NAMED_CONTROL = {"OSC-032": (35, 90), "OSC-033": (35, 90)}
NAMED_CONTROL_REQUIRED = ("OSC-032",)
# The reject side is not testable on these two fixtures (see clause_tap.both_ways); this is the
# corpus-wide control that tests it, and the run refuses to report a cause without it.
CONTROL_ARTIFACT = HERE / "clause-control-2026-08-21.json"


def route_rows_all_units(err):
    """(unit, turn) -> the ONE route row, with its trailing key=value fields."""
    finals, routes = {}, {}
    for line in err.splitlines():
        m = RC.RE_FINAL.match(line)
        if m:
            finals[(int(m.group(1)), int(m.group(2)))] = {
                "n": int(m.group(3)), "endgame": m.group(4) == "true",
                "early": m.group(5) == "true", "committed": m.group(6) == "true",
                "train_now": m.group(7) == "true"}
            continue
        m = RC.RE_ROUTE.match(line)
        if m:
            key = (int(m.group(1)), int(m.group(2)))
            row = {"fn": m.group(3), "route": m.group(4), **CT.kv(m.group(5))}
            routes.setdefault(key, []).append(row)
    out = {}
    for key, rows in routes.items():
        if len(rows) > 1:
            raise CT.ClauseGateError(
                f"unit {key[0]} turn {key[1]}: {len(rows)} route rows for one turn. A unit takes "
                f"ONE return path per turn; more than one means the tap double-counts.")
        out[key] = rows[0]
    missing = sorted(set(finals) - set(out))
    if missing:
        raise CT.ClauseGateError(
            f"{len(missing)} (unit, turn) pairs produced a PS3FINAL with no route row, first "
            f"{missing[:5]}. Full-game route coverage is the predecessor's ACCEPTED gate and it "
            f"must still hold on this subject; a route this instrument cannot see means no cause "
            f"may be attributed on that turn.")
    return finals, out


def world_state(tr, t, uid):
    """The REFEREE's view of turn t, not the bot's. Reachability is from the audited unit's cell."""
    st = tr.state(t)
    u = tr.unit(uid, t)
    reach = OR.reachable_from(tr, u.cell) if u is not None else {}
    own = [x for x in st.units if x.player == 0]
    opp = [x for x in st.units if x.player == 1]
    return {
        "turn": t,
        "own_unit_count": len(own),
        "audited_unit": None if u is None else {
            "id": u.id, "cell": list(u.cell), "speed": u.speed, "capacity": u.capacity,
            "harvest_power": u.harvest_power, "chop_power": u.chop_power,
            "carry": list(u.carry), "total_carried": u.total_carried()},
        "plants": [{"cell": list(p.cell), "kind": p.kind, "size": p.size, "health": p.health,
                    "fruits": p.fruits, "cooldown": p.cooldown,
                    "reachable_from_audited_unit": p.cell in reach,
                    "steps_from_audited_unit": reach.get(p.cell)} for p in st.plants],
        "shack_inventory": list(st.inventories[0]),
        "opponent_units": [{"id": x.id, "cell": list(x.cell), "total_carried": x.total_carried(),
                            "chop_power": x.chop_power} for x in opp],
    }


def check_trace_agrees_with_tap(sid, parsed, tr, uid):
    """The gate that LICENSES joining the referee's view to the bot's clauses.

    The card asks for "work was available" and "the bot said no" to become the same sentence
    about the same tree. That is only meaningful if the referee-side trace and the bot-side tap
    are describing the same turn. They come from two different readers of two different streams,
    and nothing so far has forced them to agree, so this checks it rather than assuming it:
    on every turn where the tap printed a call, the number of plants it saw must equal the
    number the trace holds, and the audited unit's capabilities must match too.

    A mismatch means the join is meaningless and no cause is attributed.
    """
    checked = 0
    for label, groups, power in (("chop", parsed["chop"], "chop_power"),
                                 ("idle-harvest", parsed["harvest"], "harvest_power")):
        for (unit, turn), gs in sorted(groups.items()):
            if unit != uid:
                continue
            st, u = tr.state(turn), tr.unit(uid, turn)
            for g in gs:
                want = int(g["fields"]["plants"])
                if len(st.plants) != want:
                    raise CT.ClauseGateError(
                        f"{sid} unit {unit} turn {turn}: the {label} tap saw {want} plants, the "
                        f"referee trace holds {len(st.plants)}. The bot-side and referee-side "
                        f"readers are not describing the same turn, so the oracle's eligible set "
                        f"and the generator's clause may not be joined.")
                got = g["fields"].get(power)
                if got is not None and u is not None and int(got) != getattr(u, power):
                    raise CT.ClauseGateError(
                        f"{sid} unit {unit} turn {turn}: the {label} tap printed {power}={got}, "
                        f"the referee trace holds {getattr(u, power)}.")
                checked += 1
    if not checked:
        raise CT.ClauseGateError(
            f"{sid}: no tap call could be cross-checked against the referee trace, so the "
            f"agreement gate is inert and proves nothing.")
    return checked


def call_shape(parsed, uid, lo, hi):
    """How many plants were ON THE BOARD each time the generator asked. The answer, not a detail.

    A clause histogram that comes back empty has two completely different causes — the loop
    rejected nothing, or the loop never ran because there was nothing to iterate — and they look
    identical in a totals line. This separates them.
    """
    chop, harv = collections.Counter(), collections.Counter()
    for (unit, turn), gs in parsed["chop"].items():
        if unit == uid and lo <= turn <= hi and gs[0]["clause"] == "ENTERED":
            chop[int(gs[0]["fields"]["plants"])] += 1
    for (unit, turn), gs in parsed["harvest"].items():
        if unit == uid and lo <= turn <= hi and gs[0]["clause"] == "ENTERED":
            harv[int(gs[0]["fields"]["plants"])] += 1
    return ({str(k): v for k, v in sorted(chop.items())},
            {str(k): v for k, v in sorted(harv.items())})


def opening_rows(parsed, turns):
    rows, flip = [], None
    for t in range(1, turns + 1):
        o = parsed["opening"].get(t)
        if o is None:
            continue
        abandoned = o["opening_abandoned"] == "true"
        if abandoned and flip is None:
            flip = t
        rows.append({"turn": t, **{k: v for k, v in o.items()}})
    return rows, flip


def missing_items(open_row):
    """Which item of the training cost the shack was short of, on that turn. Plain subtraction."""
    out = {}
    for item in ("plum", "lemon", "apple", "iron"):
        if item == "iron" and open_row.get("iron_on_map") == "false":
            continue
        need = int(open_row[f"cost_{item}"]) - int(open_row[f"inv_{item}"])
        if need > 0:
            out[item] = need
    return out


def clause_histogram(parsed, lo, hi, uid):
    chop, harv = collections.Counter(), collections.Counter()
    for (unit, turn), gs in parsed["chop"].items():
        if unit != uid or not (lo <= turn <= hi):
            continue
        if gs[0]["clause"] != "ENTERED":
            chop[f"FN:{gs[0]['clause']}"] += 1
            continue
        for p in gs[0]["plants"]:
            chop[p["clause"]] += 1
    for (unit, turn), gs in parsed["harvest"].items():
        if unit != uid or not (lo <= turn <= hi):
            continue
        if gs[0]["clause"] != "ENTERED":
            harv[f"FN:{gs[0]['clause']}"] += 1
            continue
        for p in gs[0]["plants"]:
            harv[p["clause"]] += 1
    return dict(chop), dict(harv)


def replant_rows(parsed, uid, lo, hi):
    """Which of the seven conjuncts were false, per window turn, and how often each."""
    false_counts = collections.Counter()
    rows, seen = [], 0
    for (unit, turn), r in sorted(parsed["replant"].items()):
        if unit != uid or not (lo <= turn <= hi):
            continue
        seen += 1
        falses = sorted(k for k, v in r.items() if k.startswith("c") and v == "false")
        for k in falses:
            false_counts[k] += 1
        rows.append({"turn": turn, "false_conjuncts": falses, "all": r["all"] == "true"})
    return {"window_turns_measured": seen,
            "conjunct_false_counts": dict(false_counts),
            "always_false_conjuncts": sorted(k for k, v in false_counts.items() if v == seen)
            if seen else [],
            "turns_all_seven_true": [r["turn"] for r in rows if r["all"]]}


def oracle_rows(tr, uid, lo, hi):
    out = {}
    for t in range(lo, hi + 1):
        out[t] = sorted(OR.eligible_actions(tr, uid, t))
    return out


def main():
    units = {r["situation"]: r["unit"] for r in json.loads(CAUSE_TABLE.read_text())["table"]}
    man = json.loads(MANIFEST.read_text())[SUBJECT]
    cfg = json.loads(H.CONFIG.read_text())
    sits = {s["id"]: s for s in H.load_situations(FIXTURES)}
    turns = int(cfg["turns"])
    fixtures = []
    with tempfile.TemporaryDirectory(prefix="cause1-") as wd:
        wd = Path(wd)
        for d in ("p", "c"):
            (wd / d).mkdir()
        print(f"compiling champion {man['source_sha256'][:12]} + the clause tap ...")
        plain = H.compile_candidate(REPO / man["source"], wd / "p")
        probe = H.compile_candidate(REPO / man["probe"], wd / "c")
        for sid in FIXTURES:
            sit, uid = sits[sid], units[sid]
            lo, hi = sit["window"]["turn_start"], sit["window"]["turn_end"]
            err = C.check_parity(sit, cfg, plain, probe)      # gate: the probe only PRINTS
            finals, routes = route_rows_all_units(err)
            parsed = CT.parse(err)
            CT.check(sid, parsed, routes)                     # gates 1-5
            control = CT.both_ways(sid, parsed, (lo, hi), NAMED_CONTROL[sid])

            spec = H.spec_for(sit, cfg)
            transcript, commands, _ = C.run_diagnostic(probe, fp.make_referee(spec), turns)
            tr = td.build_trace(transcript, commands)

            cross_checked = check_trace_agrees_with_tap(sid, parsed, tr, uid)
            chop_shape, harv_shape = call_shape(parsed, uid, lo, hi)
            orows, flip = opening_rows(parsed, turns)
            chop_hist, harv_hist = clause_histogram(parsed, lo, hi, uid)
            row = {
                "id": sid,
                "unit": uid,
                "window": [lo, hi],
                "world_state_per_turn": [world_state(tr, t, uid) for t in range(1, tr.T + 1)],
                "opening_per_turn": orows,
                "opening_abandoned_turn": flip,
                "opening_missing_items_at_abandon":
                    missing_items(parsed["opening"][flip]) if flip else None,
                "deadline_events": parsed["deadline"],
                "trace_tap_agreement_rows_checked": cross_checked,
                "window_chop_entered_with_n_plants_on_board": chop_shape,
                "window_idle_harvest_entered_with_n_plants_on_board": harv_shape,
                "window_chop_clause_histogram": chop_hist,
                "window_idle_harvest_clause_histogram": harv_hist,
                "window_clause_rows": [
                    {"turn": turn, "fn_clause": gs[0]["clause"],
                     "plants": gs[0]["plants"]}
                    for (unit, turn), gs in sorted(parsed["chop"].items())
                    if unit == uid and lo <= turn <= hi],
                "window_idle_harvest_rows": [
                    {"turn": turn, "fn_clause": gs[0]["clause"], "plants": gs[0]["plants"]}
                    for (unit, turn), gs in sorted(parsed["harvest"].items())
                    if unit == uid and lo <= turn <= hi],
                "replant_conjuncts": replant_rows(parsed, uid, lo, hi),
                "oracle_eligible_per_window_turn": oracle_rows(tr, uid, lo, hi),
                "both_ways_control": control,
            }
            fixtures.append(row)
            print(f"  {sid}  unit {uid}  window {lo}-{hi}")
            print(f"      opening abandoned at turn {flip}, short of "
                  f"{row['opening_missing_items_at_abandon']}")
            print(f"      chop calls in window, by plants ON THE BOARD  {chop_shape}")
            print(f"      chop clauses (window)  {chop_hist}")
            print(f"      harvest clauses        {harv_hist}")
            print(f"      replant conjuncts always false "
                  f"{row['replant_conjuncts']['always_false_conjuncts']}")
            print(f"      both ways: {control['outside_window_accepted_plant_rows']} accepted "
                  f"outside the window (turns "
                  f"{control['outside_window_turns_with_an_accepted_tree'][:3]}...), "
                  f"named control {control['named_control_window']} -> "
                  f"{control['named_control_satisfied']}")

    failures = []
    for r in fixtures:
        c = r["both_ways_control"]
        if not c["tap_observed_accepting_on_this_fixture"]:
            failures.append(
                f"{r['id']}: the clause tap never reported ACCEPTED anywhere outside this "
                f"fixture's audited window, so on THIS fixture it cannot be shown to be anything "
                f"but a constant 'rejected'.")
        if r["id"] in NAMED_CONTROL_REQUIRED and not c["named_control_satisfied"]:
            failures.append(
                f"{r['id']}: the card's named control window {c['named_control_window']} carries "
                f"main:CHOPS on the ACCEPTED route table, yet the tap reported no ACCEPTED tree "
                f"there.")
    # The OTHER direction. On these two fixtures `view.plants` is empty on the audited turns, so
    # not one rejecting clause has anything to reject and the in-fixture reject count is zero.
    # A tap that could ONLY say ACCEPTED would look identical here, so the corpus-wide control is
    # a precondition for reporting, not an optional extra.
    if not CONTROL_ARTIFACT.exists():
        failures.append(
            f"the rejection-side control {CONTROL_ARTIFACT.name} has not been run. On these two "
            f"fixtures the tap emits ZERO rejection rows, so without it a constant-ACCEPTED tap "
            f"is indistinguishable from this one and no cause may be attributed.")
    else:
        ctl = json.loads(CONTROL_ARTIFACT.read_text())
        if ctl["probe"]["sha256"] != man["probe_sha256"]:
            failures.append(
                f"the rejection-side control was run against probe "
                f"{ctl['probe']['sha256'][:12]}, this run uses {man['probe_sha256'][:12]}. A "
                f"control on a different binary controls nothing.")
        elif not {k: v for k, v in ctl["chop_clause_counts"].items() if k != "ACCEPTED"}:
            failures.append("the rejection-side control recorded no chop rejection clause firing "
                            "anywhere in the corpus.")
    OUT.write_text(json.dumps({
        "task": "20260821-osc032-033-cause-attribution",
        "question": "which named clause of chop_candidates / idle_harvest_candidates rejected "
                    "each plant on each window turn, which of the replant block's seven "
                    "conjuncts were false, and when and why was the opening abandoned?",
        "base": {"name": SUBJECT, "source": man["source"],
                 "source_sha256": man["source_sha256"],
                 "note": "champion of record, Door-1 pure deletion; diagnostic copy only, no "
                         "candidate, no Arena, resident file and dev copy untouched"},
        "probe": {"path": man["probe"], "sha256": man["probe_sha256"],
                  "anchors": man["anchors"]},
        "gates": [
            "parity: the clause probe's command stream is byte-identical to the uninstrumented "
            "champion's, on both fixtures",
            "one chop call-group per unit-turn; a second fails the run",
            "an ENTERED group names exactly one clause per plant on the board, no plant twice",
            "a group that returned at the function guard emits no plant rows",
            "clause names are a closed set taken from the source's own exits",
            "cross-check: ACCEPTED count == the accepted route probe's chops= for the same call, "
            "and a route that cannot reach chop_candidates has no group",
            "full-game route coverage still exact on this subject (every PS3FINAL has one route)",
            "referee/bot agreement: on every tapped call the trace's plant count and the audited "
            "unit's chop/harvest power equal the tap's own printed fields, which is what licenses "
            "joining the oracle's eligible set to the generator's clause",
            "both ways PER FIXTURE: the tap is observed reporting ACCEPTED on the fixture's own "
            "employed turns outside the audited window, so a tap that can only say 'rejected' "
            "fails instead of passing; required additionally on the card's named window 35-90 "
            "for OSC-032",
            "reject side, corpus-wide: clause-control-2026-08-21.json, on the SAME probe binary, "
            "must record a rejection clause firing — on these two fixtures view.plants is empty "
            "on the audited turns, so the reject direction is untestable here and a "
            "constant-ACCEPTED tap would be indistinguishable without it",
        ],
        "scope": "measurement only; no fix, no candidate, no judgment, no class-wide claim; "
                 "bug-versus-correct-caution is the owner's ruling",
        "hypotheses_status": "NOT YET RULED — G-1 instrument review by codex_1 comes first; the "
                             "H-A/H-B/H-C verdicts are the G-3 deliverable",
        "reject_side_control": {
            "artifact": CONTROL_ARTIFACT.name,
            "chop_clause_counts": json.loads(CONTROL_ARTIFACT.read_text())["chop_clause_counts"],
            "chop_clauses_unobserved":
                json.loads(CONTROL_ARTIFACT.read_text())["chop_clauses_unobserved"],
            "idle_harvest_clause_counts":
                json.loads(CONTROL_ARTIFACT.read_text())["idle_harvest_clause_counts"],
            "idle_harvest_clauses_unobserved":
                json.loads(CONTROL_ARTIFACT.read_text())["idle_harvest_clauses_unobserved"]},
        "fixtures": fixtures}, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
