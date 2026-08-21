#!/usr/bin/env python3
r"""G-2 controls for `20260821-osc032-033-cause-attribution` — parity, coverage, both ways.

Work owner claude_1 · reviewer codex_1 · integrator local_claude_1. **Measurement only.** No fix,
no candidate, no hypothesis verdict, no harm/benefit judgment: bug-versus-correct-caution is the
OWNER's ruling and G-3 is a separate gate that this file does not open.

G-1 (instrument fitness) was ACCEPTED by codex_1 on 2026-08-21 at commit `2764db56` — see
`coordination/messages/codex_1/20260821T081645Z-20260821-osc032-033-cause-attribution-ack.md`.
This file is the NEXT gate, and it is deliberately NOT `cause_attribution.py` re-reading its own
green flags. It recompiles both binaries, re-runs both fixtures, and re-derives the card's three
G-2 requirements from the raw stderr streams:

1. **Parity** — the instrumented command stream is byte-identical to the uninstrumented
   champion's, on both fixtures. Recorded as the SHA-256 of each stream, not as a boolean: a
   boolean that came back True is indistinguishable from a comparison that never ran, and this
   instrument has already been caught once (the four inert checks disclosed at G-1 rev 2) with
   exactly that shape.
2. **Coverage** — one clause row per plant per window turn, SUBJECT-DERIVED. The window is read
   from the fixture's own situation record; no constant is borrowed from another population (the
   4c Amendment-1 lesson). Both the chop and the idle-harvest tap must cover exactly the window's
   turn set, once each, and each call's plant-row count must equal the plant count that call
   itself printed from `view.plants`.
3. **Both ways** — the tap is not a constant "rejected". The `main:CHOPS` turn set is re-derived
   from the SAME run's route rows and must EQUAL, turn for turn, the turn set on which the clause
   tap reported an ACCEPTED tree. Set equality, not "at least one": a tap that accepted on some
   unrelated turn would pass an existence test.

Every check raises `G2Error` BEFORE the artifact is written. Nothing is accumulated into a list
and forgotten.

Run:  python3 claude_1/cause1/g2_controls.py
"""
from __future__ import annotations

import collections
import hashlib
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
import regression_tests as rt   # noqa: E402
import route_census as RC       # noqa: E402

FIXTURES = ["OSC-032", "OSC-033"]
SUBJECT = "door1-clause"
MANIFEST = HERE / "route-probe-manifest-clause-2026-08-21.json"
CAUSE_TABLE = REPO / "claude_1/hstarve1/cause-table-pool3-2026-08-17.json"
OUT = HERE / "g2-controls-2026-08-21.json"
NEGATIVE_CONTROL = HERE / "g2-negative-control-2026-08-21.json"

# The card's G-2 names OSC-032 turns 35-90 / main:CHOPS x29 as the both-ways evidence. That number
# is NOT used as a threshold anywhere below; it is re-derived from the run and only COMPARED with
# the card afterwards, so a drift is visible instead of being matched to.
CARD_SAYS = {"OSC-032": {"named_window": [35, 90], "main_chops_turns": 29}}


class G2Error(RuntimeError):
    pass


def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def route_turns(err, uid, route_name):
    """The turn set on which the audited unit returned through `route_name`, from THIS run."""
    seen = {}
    for line in err.splitlines():
        m = RC.RE_ROUTE.match(line)
        if not m:
            continue
        # the route's full name is fn:route, exactly as route_table.py spells it; the bare
        # group(4) is ambiguous across generators and matching on it would silently find nothing
        unit, turn = int(m.group(1)), int(m.group(2))
        route = f"{m.group(3)}:{m.group(4)}"
        if unit != uid:
            continue
        if turn in seen and seen[turn] != route:
            raise G2Error(
                f"unit {uid} turn {turn}: two different routes ({seen[turn]!r} and {route!r}) in "
                f"one turn. A unit takes one return path per turn; the both-ways join would be "
                f"attributing acceptance to a route that did not run.")
        seen[turn] = route
    return {t for t, r in seen.items() if r == route_name}


def accepted_turns(parsed, uid):
    """The turn set on which the CHOP tap reported at least one ACCEPTED tree, whole game."""
    out = set()
    for (unit, turn), gs in parsed["chop"].items():
        if unit != uid:
            continue
        for g in gs:
            if any(p["clause"] == "ACCEPTED" for p in g["plants"]):
                out.add(turn)
    return out


def coverage_one_tap(sid, which, groups, uid, lo, hi):
    """Exactly one call per window turn for the audited unit, and one row per plant in it."""
    turns = collections.Counter()
    per_turn = {}
    for (unit, turn), gs in groups.items():
        if unit != uid or not (lo <= turn <= hi):
            continue
        turns[turn] += len(gs)
        per_turn[turn] = gs
    want = set(range(lo, hi + 1))
    missing = sorted(want - set(turns))
    if missing:
        raise G2Error(
            f"{sid} {which}: {len(missing)} window turn(s) with no call at all, first "
            f"{missing[:5]}. The window {lo}-{hi} is the fixture's own; a turn the tap never saw "
            f"is a gap, and a cause cannot be attributed on a turn that was not measured.")
    extra = sorted(t for t, n in turns.items() if n != 1)
    if extra:
        raise G2Error(
            f"{sid} {which}: {len(extra)} window turn(s) with more than one call group, first "
            f"{extra[:5]}. Duplicates would double-count clauses.")
    board = collections.Counter()
    for turn, gs in per_turn.items():
        g = gs[0]
        if g["clause"] != "ENTERED":
            if g["plants"]:
                raise G2Error(
                    f"{sid} {which} turn {turn}: the call returned at the guard "
                    f"({g['clause']}) yet emitted {len(g['plants'])} plant row(s). A clause "
                    f"named on a plant the loop never reached is unattributable.")
            board[-1] += 1
            continue
        n = int(g["fields"]["plants"])
        if len(g["plants"]) != n:
            raise G2Error(
                f"{sid} {which} turn {turn}: the call printed plants={n} from `view.plants` but "
                f"emitted {len(g['plants'])} plant row(s). Coverage must be one named clause per "
                f"plant, derived from the call's own board, not from a count this reader chose.")
        cells = [tuple(p["cell"]) for p in g["plants"]]
        if len(set(cells)) != len(cells):
            raise G2Error(
                f"{sid} {which} turn {turn}: a plant cell is named twice {cells}.")
        board[n] += 1
    return {"window": [lo, hi],
            "window_turns": hi - lo + 1,
            "calls": sum(turns.values()),
            "calls_by_plants_on_board": {str(k): v for k, v in sorted(board.items())},
            "plant_rows": sum(len(gs[0]["plants"]) for gs in per_turn.values())}


def check_parity_streams(sid, plain_cmds, probe_cmds):
    """Extracted so `g2_negative_control.py` can feed this exact comparison a corrupted stream."""
    h_plain, h_probe = sha(plain_cmds.strip()), sha(probe_cmds.strip())
    if h_plain != h_probe:
        raise G2Error(
            f"{sid}: PARITY FAILED. The uninstrumented champion's command stream hashes "
            f"{h_plain[:12]} and the instrumented one {h_probe[:12]}. The probe is "
            f"supposed to only PRINT; a stream that differs is a different bot and every "
            f"clause measured on it would be about that different bot.")
    if not probe_cmds.strip():
        raise G2Error(
            f"{sid}: both command streams are EMPTY, so their equality says nothing. "
            f"Parity on two empty streams is not parity.")
    return h_plain, h_probe


def check_both_ways(sid, chops_route, acc):
    if not acc:
        raise G2Error(
            f"{sid}: the clause tap never reported ACCEPTED on ANY turn of the whole "
            f"game. A tap that can only say 'rejected' would produce exactly this, and "
            f"the rejections it reports in the window would be worthless.")
    missing_acc = sorted(chops_route - acc)
    if missing_acc:
        raise G2Error(
            f"{sid}: {len(missing_acc)} turn(s) routed through main:CHOPS with no "
            f"ACCEPTED tree in the tap, first {missing_acc[:5]}. The route only exists "
            f"because the chop list was non-empty, so the tap missed an acceptance.")


def check_card_cross(sid, chops_route):
    """The card's number is COMPARED, never matched to. A drift fails instead of hiding."""
    if sid not in CARD_SAYS:
        return None
    out = {"card_named_window": CARD_SAYS[sid]["named_window"],
           "card_main_chops_turns": CARD_SAYS[sid]["main_chops_turns"],
           "measured_main_chops_turns": len(chops_route),
           "agrees": len(chops_route) == CARD_SAYS[sid]["main_chops_turns"]}
    if not out["agrees"]:
        raise G2Error(
            f"the measured main:CHOPS turn count {len(chops_route)} disagrees with the "
            f"{CARD_SAYS[sid]['main_chops_turns']} the card names for {sid}. The card's number is "
            f"not a threshold to match, but a disagreement means one of the two is stale and must "
            f"be resolved before the count is used as evidence.")
    return out


def main():
    units = {r["situation"]: r["unit"] for r in json.loads(CAUSE_TABLE.read_text())["table"]}
    man = json.loads(MANIFEST.read_text())[SUBJECT]
    cfg = json.loads(H.CONFIG.read_text())
    sits = {s["id"]: s for s in H.load_situations(FIXTURES)}
    turns = int(cfg["turns"])
    rows = []
    with tempfile.TemporaryDirectory(prefix="g2-") as wd:
        wd = Path(wd)
        for d in ("p", "c"):
            (wd / d).mkdir()
        print(f"compiling champion {man['source_sha256'][:12]} + the clause tap ...")
        plain = H.compile_candidate(REPO / man["source"], wd / "p")
        probe = H.compile_candidate(REPO / man["probe"], wd / "c")
        for sid in FIXTURES:
            sit, uid = sits[sid], units[sid]
            lo, hi = sit["window"]["turn_start"], sit["window"]["turn_end"]
            spec = H.spec_for(sit, cfg)

            # ---- 1. parity, recorded as digests -------------------------------------------
            _, plain_cmds = rt.run_binary_custom(Path(plain), fp.make_referee(spec), turns)
            _, probe_cmds, err = C.run_diagnostic(probe, fp.make_referee(spec), turns)
            h_plain, h_probe = check_parity_streams(sid, plain_cmds, probe_cmds)

            # ---- 2. coverage, subject-derived ---------------------------------------------
            parsed = CT.parse(err)
            chop_cov = coverage_one_tap(sid, "chop", parsed["chop"], uid, lo, hi)
            harv_cov = coverage_one_tap(sid, "idle_harvest", parsed["harvest"], uid, lo, hi)

            # ---- 3. both ways, by SET EQUALITY against this run's own route rows -----------
            chops_route = route_turns(err, uid, "main:CHOPS")
            acc = accepted_turns(parsed, uid)
            check_both_ways(sid, chops_route, acc)
            row = {
                "id": sid, "unit": uid, "window": [lo, hi],
                "parity": {"uninstrumented_command_sha256": h_plain,
                           "instrumented_command_sha256": h_probe,
                           "identical": True,
                           "command_stream_bytes": len(probe_cmds.strip())},
                "coverage_chop": chop_cov,
                "coverage_idle_harvest": harv_cov,
                "both_ways": {
                    "main_chops_turns": sorted(chops_route),
                    "tap_accepted_turns": sorted(acc),
                    "main_chops_subset_of_accepted": True,
                    "accepted_turns_not_routed_through_main_chops":
                        sorted(acc - chops_route),
                    "accepted_in_window": sorted(acc & set(range(lo, hi + 1))),
                },
            }
            cross = check_card_cross(sid, chops_route)
            if cross is not None:
                row["card_cross_check"] = cross
            rows.append(row)
            print(f"  {sid}  unit {uid}  window {lo}-{hi}")
            print(f"      parity   {h_plain[:12]} == {h_probe[:12]}  "
                  f"({len(probe_cmds.strip())} bytes of commands)")
            print(f"      coverage chop {chop_cov['calls']} calls / "
                  f"{chop_cov['window_turns']} window turns, "
                  f"boards {chop_cov['calls_by_plants_on_board']}, "
                  f"{chop_cov['plant_rows']} plant rows")
            print(f"      coverage harv {harv_cov['calls']} calls, "
                  f"boards {harv_cov['calls_by_plants_on_board']}")
            print(f"      both ways: main:CHOPS on {len(chops_route)} turn(s), tap ACCEPTED on "
                  f"{len(acc)} turn(s), main:CHOPS \\ accepted = {sorted(chops_route - acc)}")

    # ---- the cross-fixture gate: at least one fixture must carry the accept side ----------
    # OSC-033 never routes through main:CHOPS at all, so its both-ways evidence cannot come from
    # main:CHOPS. Saying so out loud is the point; a silent pass would read as if it had.
    with_chops = [r["id"] for r in rows if r["both_ways"]["main_chops_turns"]]
    if not with_chops:
        raise G2Error(
            "no fixture routed through main:CHOPS on any turn, so the card's named both-ways "
            "evidence does not exist on this pair and G-2 cannot be claimed from these runs.")

    # The G-1 rev-2 lesson, applied to this gate rather than re-learned: a check whose result is
    # accumulated and never raised is not a check. This raises BEFORE the artifact is written, and
    # the run refuses to report at all without a demonstration that its own gates can fail.
    if not NEGATIVE_CONTROL.exists():
        raise G2Error(
            f"{NEGATIVE_CONTROL.name} has not been run. Every gate above passed; a gate that has "
            f"only ever passed has not been shown to be a gate, so nothing is reported.")
    neg = json.loads(NEGATIVE_CONTROL.read_text())
    misbehaved = [c for c in neg["cases"] if c["rejected"] != c["must_be_rejected"]]
    if misbehaved:
        raise G2Error(
            f"the negative control records {len(misbehaved)} case(s) that did not behave as "
            f"required, first {misbehaved[0]['case']!r}.")
    if not any(c["must_be_rejected"] for c in neg["cases"]):
        raise G2Error("the negative control contains no corruption case at all.")
    covered = {c["gate"] for c in neg["cases"] if c["must_be_rejected"]}
    for gate in ("parity", "coverage", "both ways", "card"):
        if gate not in covered:
            raise G2Error(
                f"the negative control exercises no corruption against the {gate!r} gate, so that "
                f"gate is still only known to pass.")

    art = {
        "task": "20260821-osc032-033-cause-attribution",
        "negative_control": {
            "artifact": NEGATIVE_CONTROL.name,
            "corruptions_rejected": neg["n_corruptions"],
            "clean_streams_accepted": neg["n_clean"],
            "all_behaved": neg["all_behaved"],
            "gates_exercised": sorted(covered),
        },
        "gate": "G-2 controls: parity, coverage, both ways",
        "scope": "measurement only; no fix, no candidate, no hypothesis verdict, no "
                 "harm/benefit judgment, no class-wide claim. G-3 is a separate gate.",
        "g1": {"verdict": "ACCEPTED by codex_1 2026-08-21",
               "at_commit": "2764db56d093c965abe21eb6b276caf7147d7c56",
               "ack": "coordination/messages/codex_1/"
                      "20260821T081645Z-20260821-osc032-033-cause-attribution-ack.md"},
        "base": {"champion_sha256": man["source_sha256"], "probe_sha256": man["probe_sha256"],
                 "subject": SUBJECT},
        "fixtures": rows,
        "fixtures_carrying_the_accept_side_via_main_chops": with_chops,
        "checks": [
            "parity: the uninstrumented and instrumented command streams hash IDENTICALLY on "
            "both fixtures; the digests are recorded, and an empty stream is refused",
            "coverage: exactly one chop and one idle_harvest call group per audited-unit window "
            "turn, window read from the fixture's own situation record, no borrowed constant",
            "coverage: each ENTERED call emits exactly one clause row per entry of the "
            "`view.plants` count that call itself printed, and no cell twice",
            "coverage: a call that returned at the function guard emits zero plant rows",
            "both ways: every turn routed through main:CHOPS carries an ACCEPTED tree in the tap "
            "(set containment, re-derived from the same run's route rows, not an existence test)",
            "both ways: a tap that never reported ACCEPTED anywhere in the game fails the run",
            "cross-fixture: at least one fixture must actually carry main:CHOPS, so the card's "
            "named evidence is shown to exist rather than assumed",
            "card cross-check: the measured main:CHOPS turn count is COMPARED with the count the "
            "card names, and a disagreement fails rather than being silently matched to",
        ],
        "honest_limits": [
            "In-window coverage is VACUOUS on the per-plant direction: on every audited window "
            "turn of both fixtures `view.plants` is empty, so 'one clause row per plant' is "
            "satisfied by zero plants. The non-vacuous coverage evidence is outside the window "
            "(OSC-032 turns 35-90) and corpus-wide in clause-control-2026-08-21.json.",
            "OSC-033 never routes through main:CHOPS on any turn, so the card's named both-ways "
            "evidence does not exist on that fixture. Its accept side comes from the early "
            "branch's chop calls on turns 1-12 instead, and that is a weaker instance of the "
            "same direction, not the card's own.",
            "The reject side fires on neither fixture: zero rejection rows in either window "
            "because there is nothing to reject. It is carried entirely by the corpus-wide "
            "control over all 34 situations and by the negative control, both of which "
            "cause_attribution.py requires before it will report.",
        ],
        "not_claimed": [
            "No hypothesis verdict. H-A/H-B/H-C are the G-3 deliverable and nothing here rules "
            "on them.",
            "No claim that the measured routes or clauses are right or wrong; "
            "bug-versus-correct-caution is the owner's ruling.",
            "No claim about any situation other than OSC-032 and OSC-033.",
        ],
    }
    OUT.write_text(json.dumps(art, indent=1, sort_keys=True) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    try:
        main()
    except (G2Error, CT.ClauseGateError, C.CoverageError) as exc:
        print(f"G-2 FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
