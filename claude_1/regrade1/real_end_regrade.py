#!/usr/bin/env python3
r"""20260821-p4-stalls-real-end-regrade — how far past the REAL end of the game each of the 34
recorded oscillation windows extends.

Task `20260821-p4-stalls-real-end-regrade` (coordinator-chartered 2026-08-21T09:30Z, policy
`coordination/messages/local_claude_1/20260821T093404Z-...`). Work owner claude_1, reviewer
codex_1, integrator local_claude_1.

**Measurement only.** No fix, no candidate, no behaviour change, no re-ruling of any case, no
class-wide claim beyond these 34, no Arena action.

## What this measures, and what it does NOT

The fixture harness (`claude_1/banana-restoration-r2/regression_tests.py:run_binary_custom`, and
the parity-checked copy `coverage.run_diagnostic`) plays a FIXED `cfg["turns"]` horizon and never
calls the referee's end condition. The referee's own rule is `Board.hasStalled`
(`rust/src/game/engine.rs:819`), frozen-ported as `sim.engine.has_stalled`. OSC-032/033 were
found (G-3, ACCEPTED `20260821T090757Z`) to lie WHOLLY past that end. This file asks the same
question of all 34.

What a row here says: on the champion re-run of this fixture's own game, the referee would have
ended at turn N, and K of the window's turns fall at or after N. What it does NOT say: that the
case's ruling was wrong. Rulings already made stand; this is an annotation. See §"NOT CHANGED"
in the note.

## TWO ARMS, because "the champion re-run" and "the recorded window" are two different games

The card asks for the real end turn "on the champion re-run". The champion is
`claude_1/chop4c/candidate-door1.rs` (547fa706). The 34 windows were NOT recorded from it: the
frozen library's own provenance names its subject as
`cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs` (98628e98), judged against
itself on the panel floor. On 21 of the 34 fixtures the champion emits DIFFERENT commands inside
the frozen window, so "the champion's end turn" and "the recorded window" would be turn numbers
drawn from two different games — this project's most expensive recurring error, and the exact
thing the card is trying to correct for.

So both arms are run and reported separately:

- **SUBJECT arm (98628e98)** — the bot that produced the windows. Its replay reproduces the
  frozen window commands, so its end turn and the recorded window ARE the same game. **This is
  the arm that answers "is this recorded window artifact".**
- **CHAMPION arm (547fa706)** — literally what the card asked, kept because it is what G-3 ran
  and what the OSC-032/033 ruling rests on. Where the champion diverges from the frozen window,
  the row is marked `REPLAY_MISMATCH` and its window comparison is NOT used.

The command-identity gate below is what separates them, and running both arms is also what makes
that gate non-vacuous: it must AGREE on the subject and DISAGREE on the champion. A gate that has
only ever agreed is not evidence of agreement.

## Reuse, and the one deliberate delta from G-3

The stall adapter is the ACCEPTED G-3 one, reused BY IMPORT, not by copy:
`g3_finding.to_sim_state` and `g3_finding.check_adapter_fidelity` are called here unmodified, and
`g3_finding.stall_negative_control` is run unchanged as the constructed-state control. The file's
sha256 is recorded in the artifact so G-1 can verify it is the accepted bytes.

The delta: G-3's own `stall_projection` raises when a fixture never stalls (its per-fixture
non-vacuity gate). That gate is correct for two fixtures both known to go bare, and WRONG here —
across 34 cases "the game never ends inside the horizon" is an expected, informative answer, and
a per-fixture raise would make it impossible to report. So the projection loop is re-expressed
with the SAME body and a CORPUS-level non-vacuity gate, exactly as the card's G-2 specifies
("the predicate seen False on a plant-bearing turn and True on a bare one somewhere in the
corpus"). Nothing else about the adapter changes; the per-turn identity control stays and is
called on every turn of every fixture.

## The three ways this run could lie to itself, and the control for each

- **The replay could be a DIFFERENT game from the recorded one.** Then "the window" and "the end
  turn" would be turn numbers from two different games — this project's most expensive recurring
  error. Two controls: `fixture_harness.spec_for` already refuses a rebuild whose map differs
  from the frozen `static_map_rows`, and this file adds a RECORDED-WINDOW COMMAND IDENTITY gate —
  the replayed command line on every turn of the recorded window must equal the line the library
  froze for that turn. A fixture that fails it is reported as such and contributes no numbers.
- **The rebuilt state could differ from the referee's.** Per turn, `check_adapter_fidelity`
  (G-3's, unmodified) requires plant canonical records, units and BOTH inventories to match.
- **The predicate could be vacuous.** Corpus non-vacuity (both answers observed) plus G-3's
  four constructed states, two that must stall and two that must not.

Fail-closed: any fixture whose spec, replay or adapter cannot be built stops the run. A quietly
skipped fixture would make "34" a lie.

Run:  python3 claude_1/regrade1/real_end_regrade.py
"""
from __future__ import annotations

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
sys.path.insert(0, str(REPO))
import cause_attribution as CA   # noqa: E402
import coverage as C             # noqa: E402
import fixture_harness as H      # noqa: E402
import fuzz_panel as fp          # noqa: E402
import g3_finding as G3          # noqa: E402  (the ACCEPTED adapter, imported not copied)
import trace_detectors as td     # noqa: E402
from sim import engine as SE     # noqa: E402  (the FROZEN port; never modified, never wrapped)

SUBJECT_BOT = "cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs"
SUBJECT_BOT_SHA256 = "98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29"

LIB_INDEX = (REPO / "claude_1/banana-restoration-r2/oscillation-library-98628e98/library/"
                    "index.json")
G3_SRC = REPO / "claude_1/cause1/g3_finding.py"
OUT = HERE / "real-end-regrade-2026-08-21.json"


class RegradeError(Exception):
    """Anything that would make a number here mean something other than it says."""


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_window_commands(sid, sit, command_lines):
    """The replay must be THIS recorded episode.

    The library froze the command line the subject emitted on every turn of the window. If the
    re-run emits a different line on any of them, the window's turn numbers and this run's end
    turn belong to two different games and no comparison between them is meaningful.
    """
    recorded = sit["window"].get("commands") or []
    if not recorded:
        raise RegradeError(
            f"{sid}: the frozen situation carries no window commands, so the replay cannot be "
            f"shown to be this episode. Fail-closed rather than compare turn numbers across "
            f"two possibly different games.")
    bad = []
    for entry in recorded:
        t = int(entry["turn"])
        if not 1 <= t <= len(command_lines):
            bad.append((t, entry["line"], "<past the replayed horizon>"))
            continue
        got = command_lines[t - 1].strip()
        if got != entry["line"].strip():
            bad.append((t, entry["line"], got))
    return {"window_turns_checked": len(recorded), "mismatches": len(bad),
            "first_mismatches": bad[:5]}


# The library's frozen entry state, positionally decoded. Field order taken from the viewer that
# renders it (claude_1/viewer/build_viewer.py:491-496), which is the only reader in the repo:
#   plants: [kind, x, y, size, health, fruits, cooldown]
#   units:  [id, side(0=ours), x, y, speed, cap, harv, chop, carry x6]
#   inventories: {"own": [...6], "opponent": [...6]}  ->  trace inventories[0], [1]


def check_entry_state(sid, sit, tr):
    """The replay's board AT THE WINDOW'S FIRST TURN must be the board the library froze.

    This is the gate the window-command comparison alone CANNOT be: on a window whose every
    recorded line is `WAIT`, a completely different game replays the same commands and passes.
    OSC-032 is exactly that case — the frozen entry state at turn 91 still carries a live PLUM,
    while one of the two arms has had a bare board since turn 82, and both emit WAIT throughout.
    A guard that agrees there is agreeing about nothing.
    """
    ws = sit["world_state_at_entry"]
    e = int(ws["turn"])
    lo = int(sit["window"]["turn_start"])
    if e != lo:
        raise RegradeError(f"{sid}: frozen entry state is turn {e} but the window starts at "
                           f"{lo}; the two cannot be compared.")
    if not 1 <= e <= tr.T:
        raise RegradeError(f"{sid}: entry turn {e} lies outside the replayed horizon {tr.T}.")
    st = tr.state(e)
    diffs = []
    want_p = sorted((p[0], p[1], p[2], p[3], p[4], p[5], p[6]) for p in ws["plants"])
    got_p = sorted((p.kind, p.cell[0], p.cell[1], p.size, p.health, p.fruits, p.cooldown)
                   for p in st.plants)
    if want_p != got_p:
        diffs.append({"field": "plants", "frozen": want_p, "replay": got_p})
    want_u = sorted((u[0], u[1], u[2], u[3], u[4], u[5], u[6], u[7], tuple(u[8:]))
                    for u in ws["units"])
    got_u = sorted((u.id, u.player, u.cell[0], u.cell[1], u.speed, u.capacity, u.harvest_power,
                    u.chop_power, tuple(u.carry)) for u in st.units)
    if want_u != got_u:
        diffs.append({"field": "units", "frozen": want_u, "replay": got_u})
    want_i = [list(ws["inventories"]["own"]), list(ws["inventories"]["opponent"])]
    got_i = [list(st.inventories[0]), list(st.inventories[1])]
    if want_i != got_i:
        diffs.append({"field": "inventories", "frozen": want_i, "replay": got_i})
    return {"entry_turn": e, "matches": not diffs, "diffs": diffs}


def project(sid, tr):
    """`sim.engine.has_stalled` replayed over the referee's own per-turn states.

    Body identical to G-3's `stall_projection`; the per-fixture non-vacuity raise is lifted to
    the corpus (see the module docstring), so the counts it needs are RETURNED rather than
    checked here.
    """
    counter = 0
    rows, ended_turn, ended_reason = [], None, None
    saw_false_with_plants = saw_true_on_bare = False
    for t in range(1, tr.T + 1):
        game = G3.to_sim_state(tr, t)            # G-3's, unmodified
        G3.check_adapter_fidelity(sid, tr, t, game)   # G-3's, unmodified — every turn
        stalled, counter = SE.has_stalled(game, counter)
        reason = SE.stall_reason(game, counter)
        rows.append({"turn": t, "plants": len(game.plants), "stalled": stalled,
                     "turns_until_end": counter, "reason": reason})
        if game.plants and not stalled:
            saw_false_with_plants = True
        if stalled and not game.plants:
            saw_true_on_bare = True
        if stalled and ended_turn is None:
            ended_turn, ended_reason = t, reason
    grace_only = next((r["turn"] for r in rows
                       if r["plants"] == 0 and r["turns_until_end"] <= 0), None)
    return {
        "first_stalled_turn": ended_turn,
        "reason": ended_reason,
        "harness_horizon_turns": tr.T,
        "turns_the_harness_played_past_the_real_end":
            0 if ended_turn is None else tr.T - ended_turn + 1,
        "grace_only_end_turn": grace_only,
        "grace_only_note": "the turn the no-plants grace counter alone would have expired, "
                           "ignoring the mercy and both-stuck clauses; the conservative bound, "
                           "and the one to quote when the opponent's state is in doubt",
        "saw_false_with_plants": saw_false_with_plants,
        "saw_true_on_bare": saw_true_on_bare,
        "per_turn_tail": rows[-8:],
    }


def window_verdict(lo, hi, end_turn):
    """How much of the recorded window the real referee would never have played.

    `end_turn` is the FIRST turn on which the referee says the game is over, so turns >= end_turn
    are the artifact ones. `None` means the referee never ended it inside the horizon.
    """
    total = hi - lo + 1
    if end_turn is None:
        return {"window": [lo, hi], "window_turns": total, "real_end_turn": None,
                "window_turns_past_the_real_end": 0, "verdict": "REAL_THROUGHOUT",
                "note": "the referee never ends this game inside the harness horizon"}
    past = max(0, hi - max(lo, end_turn) + 1) if hi >= end_turn else 0
    if past == 0:
        verdict = "REAL_THROUGHOUT"
    elif past >= total:
        verdict = "WHOLLY_ARTIFACT"
    else:
        verdict = "PARTLY_ARTIFACT"
    return {"window": [lo, hi], "window_turns": total, "real_end_turn": end_turn,
            "window_turns_past_the_real_end": past,
            "window_turns_the_referee_would_have_played": total - past,
            "verdict": verdict}


def main():
    man = json.loads(CA.MANIFEST.read_text())[CA.SUBJECT]
    cfg = json.loads(H.CONFIG.read_text())
    turns = int(cfg["turns"])
    index = json.loads(LIB_INDEX.read_text())
    meta = {s["id"]: s for s in index["situations"]}
    sits = H.load_situations()
    if len(sits) != 34 or len(meta) != 34:
        raise RegradeError(f"expected the frozen 34; got {len(sits)} situations and "
                           f"{len(meta)} index rows. The card's scope IS the 34.")
    subject_src = REPO / SUBJECT_BOT
    if sha256_of(subject_src) != SUBJECT_BOT_SHA256:
        raise RegradeError(
            f"{SUBJECT_BOT} is not the library's subject bytes ({SUBJECT_BOT_SHA256[:12]}); "
            f"replaying it would not reproduce the recorded episodes.")

    print("stall-predicate control (G-3's, unmodified) ...")
    control = G3.stall_negative_control()
    for c in control:
        print(f"  {c['case']:38s} stalled={c['stalled']} (required {c['must_be']})")

    arms = [
        {"arm": "subject", "source": SUBJECT_BOT, "sha256": SUBJECT_BOT_SHA256,
         "role": "the bot that PRODUCED the 34 recorded windows (library provenance "
                 "bot_source_sha256); its end turn and the recorded window are the same game"},
        {"arm": "champion", "source": man["source"], "sha256": man["source_sha256"],
         "role": "the champion the card names; what G-3 ran. Where it diverges from the frozen "
                 "window commands its window comparison is not used"},
    ]

    per_arm = {}
    corpus = {}
    with tempfile.TemporaryDirectory(prefix="regrade-") as wd:
        wd = Path(wd)
        for a in arms:
            arm = a["arm"]
            d = wd / arm
            d.mkdir()
            print(f"\ncompiling {arm} {a['sha256'][:12]} ({a['source']}) ...")
            binary = H.compile_candidate(REPO / a["source"], d)
            rows = []
            false_with_plants = true_on_bare = 0
            for sit in sorted(sits, key=lambda s: s["id"]):
                sid = sit["id"]
                lo, hi = sit["window"]["turn_start"], sit["window"]["turn_end"]
                spec = H.spec_for(sit, cfg)      # refuses a rebuild that is not this map
                transcript, commands, _ = C.run_diagnostic(binary, fp.make_referee(spec), turns)
                command_lines = commands.rstrip("\n").split("\n")
                ident = check_window_commands(sid, sit, command_lines)
                tr = td.build_trace(transcript, commands)
                if tr.T != turns:
                    raise RegradeError(f"{sid}: trace covers {tr.T} turns, config asks {turns}.")
                entry = check_entry_state(sid, sit, tr)
                stall = project(sid, tr)
                false_with_plants += int(stall["saw_false_with_plants"])
                true_on_bare += int(stall["saw_true_on_bare"])
                verdict = window_verdict(lo, hi, stall["first_stalled_turn"])
                reasons = []
                if ident["mismatches"]:
                    reasons.append(f"{ident['mismatches']} of "
                                   f"{ident['window_turns_checked']} frozen window command "
                                   f"lines differ")
                if not entry["matches"]:
                    reasons.append("the board at the window's first turn differs from the "
                                   "frozen entry state ("
                                   + ", ".join(d["field"] for d in entry["diffs"]) + ")")
                if reasons:
                    verdict["reproduces_the_recorded_episode"] = False
                    verdict["verdict_before_mismatch"] = verdict["verdict"]
                    verdict["verdict"] = "REPLAY_MISMATCH"
                    verdict["mismatch_reasons"] = reasons
                    verdict["note"] = (
                        "this arm does not reproduce the recorded episode, so its end turn and "
                        "this window belong to two different games; the comparison is not used")
                else:
                    verdict["reproduces_the_recorded_episode"] = True
                rows.append({
                    "id": sid, "kind": meta[sid]["kind"], "mechanism": meta[sid]["mechanism"],
                    "unit": sit["window"].get("unit"),
                    "recorded_window_identity": ident,
                    "recorded_entry_state_identity": entry,
                    "real_end": stall, "regrade": verdict})
                print(f"  {sid} {meta[sid]['kind']:11s} window {lo:3d}-{hi:3d} "
                      f"({verdict['window_turns']:3d}t)  real end "
                      f"{str(stall['first_stalled_turn']):>6s} "
                      f"(grace-only {str(stall['grace_only_end_turn']):>6s})  past-end "
                      f"{verdict['window_turns_past_the_real_end']:3d}  {verdict['verdict']}"
                      + ("" if verdict["reproduces_the_recorded_episode"]
                         else "  !! " + "; ".join(verdict["mismatch_reasons"])))
            per_arm[arm] = rows
            corpus[arm] = {"fixtures_with_false_on_a_plant_bearing_turn": false_with_plants,
                           "fixtures_with_true_on_a_bare_board": true_on_bare,
                           "fixtures": len(rows),
                           "fixtures_reproducing_the_recorded_episode":
                               sum(1 for r in rows
                                   if r["regrade"]["reproduces_the_recorded_episode"]),
                           "fixtures_matching_the_frozen_entry_state":
                               sum(1 for r in rows
                                   if r["recorded_entry_state_identity"]["matches"])}

    # CORPUS NON-VACUITY, per the card's G-2, on the arm the table is built from.
    if not corpus["subject"]["fixtures_with_false_on_a_plant_bearing_turn"]:
        raise RegradeError("has_stalled was never observed returning False on a plant-bearing "
                           "turn anywhere in the corpus; no end turn may be reported.")
    if not corpus["subject"]["fixtures_with_true_on_a_bare_board"]:
        raise RegradeError("has_stalled was never observed returning True on a bare board "
                           "anywhere in the corpus; no end turn may be reported.")
    # THE COMMAND-IDENTITY GATE'S OWN NON-VACUITY. It must be capable of both answers, or
    # "the subject reproduces every window" is not evidence of anything.
    sub_ok = corpus["subject"]["fixtures_reproducing_the_recorded_episode"]
    champ_ok = corpus["champion"]["fixtures_reproducing_the_recorded_episode"]
    if sub_ok != 34:
        raise RegradeError(
            f"the SUBJECT bot reproduces only {sub_ok}/34 recorded episodes. It is the bot the "
            f"library recorded, so a mismatch means the replay pipeline does not reconstruct "
            f"the recorded episodes and NO row here is trustworthy.")
    if champ_ok == 34:
        raise RegradeError(
            "the command-identity gate accepted every fixture on BOTH arms, so it has never "
            "been observed rejecting and is not evidence that the subject arm is the recorded "
            "game.")

    def summarise(rows):
        return {v: sorted(r["id"] for r in rows if r["regrade"]["verdict"] == v)
                for v in ("WHOLLY_ARTIFACT", "PARTLY_ARTIFACT", "REAL_THROUGHOUT",
                          "REPLAY_MISMATCH")}

    sub = {r["id"]: r for r in per_arm["subject"]}
    champ = {r["id"]: r for r in per_arm["champion"]}
    disagree = sorted(i for i in sub
                      if sub[i]["real_end"]["first_stalled_turn"]
                      != champ[i]["real_end"]["first_stalled_turn"])

    art = {
        "task": "20260821-p4-stalls-real-end-regrade",
        "gate": "G-2/G-3 evidence",
        "scope": "measurement only; no fix, no candidate, no re-ruling, no class-wide claim "
                 "beyond these 34, no Arena action",
        "not_changed": "Rulings already made stand — the 18 BUG (benching class), the six BUG "
                       "(4b sittings) and the 8 FIXED. This file only annotates each case with "
                       "the turn the real referee would have ended its game. Any proposal to "
                       "re-open a ruling is a question for the owner, not a finding here.",
        "primary_arm": "subject",
        "primary_arm_note": "The table that answers the card's question is the SUBJECT arm: the "
                            "34 windows were recorded from 98628e98, not from the champion, and "
                            "only that arm's end turn belongs to the same game as the window. "
                            "The champion arm is reported because the card names it and because "
                            "the OSC-032/033 ruling rests on it.",
        "arms": arms,
        "library": {"path": str(LIB_INDEX.relative_to(REPO)),
                    "library_sha256": index["library_sha256"],
                    "situation_count": index["situation_count"],
                    "subject_bot": SUBJECT_BOT, "subject_bot_sha256": SUBJECT_BOT_SHA256},
        "config": {"path": str(H.CONFIG.relative_to(REPO)), "turns": turns},
        "adapter_reuse": {
            "file": str(G3_SRC.relative_to(REPO)),
            "sha256": sha256_of(G3_SRC),
            "imported_unmodified": ["to_sim_state", "check_adapter_fidelity",
                                    "stall_negative_control"],
            "delta": "G-3's own stall_projection raises when a fixture never stalls (per-fixture "
                     "non-vacuity). Across 34 cases 'never ends inside the horizon' is an "
                     "expected answer, so the loop is re-expressed here with the same body and "
                     "a CORPUS-level non-vacuity gate, as the card's G-2 specifies. The per-turn "
                     "identity control is unchanged and runs on every turn of every fixture of "
                     "both arms.",
        },
        "frozen_predicate": {
            "module": "sim/engine.py", "function": "has_stalled",
            "note": "unmodified and unwrapped; states are built from the referee trace by G-3's "
                    "to_sim_state and handed over. Scores from sim.engine.recompute_scores.",
            "rust_original": "rust/src/game/engine.rs:819 has_stalled (referee v1.0.5 "
                             "Board.hasStalled)"},
        "harness_note": "regression_tests.run_binary_custom runs a FIXED cfg['turns'] horizon "
                        "and never calls a stall check, which is why recorded windows can reach "
                        "turns a real game would not.",
        "gates": [
            "spec fidelity: fixture_harness.spec_for refuses a rebuild whose map differs from "
            "the frozen static_map_rows",
            "recorded-episode identity, both arms, TWO independent comparisons: (a) the "
            "re-run's command line on every frozen window turn equals the library's, and (b) "
            "the replay's board at the window's first turn equals the library's frozen "
            "world_state_at_entry (plants, units, both inventories). (b) exists because (a) "
            "alone passes trivially on an all-WAIT window. Non-vacuous by construction — the "
            "pair must accept all 34 on the subject arm and reject at least one on the champion "
            "arm, or the run fails",
            "adapter fidelity, per turn, every fixture, both arms: G-3's check_adapter_fidelity",
            "corpus non-vacuity: has_stalled observed False on a plant-bearing turn and True on "
            "a bare board somewhere in the 34",
            "stall predicate control: G-3's four constructed states, unmodified",
            "subject-bot digest checked against the library provenance before compiling",
            "fail-closed: any fixture whose spec, replay, trace or adapter cannot be built stops "
            "the run; the count 34 must mean 34",
        ],
        "corpus_non_vacuity": corpus,
        "stall_predicate_control": control,
        "summary": {"subject": summarise(per_arm["subject"]),
                    "champion": summarise(per_arm["champion"])},
        "arms_disagree_on_the_real_end_turn": disagree,
        "rows": {"subject": per_arm["subject"], "champion": per_arm["champion"]},
    }
    OUT.write_text(json.dumps(art, indent=2, sort_keys=True) + "\n")
    for arm in ("subject", "champion"):
        s = art["summary"][arm]
        print(f"\n[{arm}] WHOLLY artifact ({len(s['WHOLLY_ARTIFACT'])}): "
              f"{s['WHOLLY_ARTIFACT']}")
        print(f"[{arm}] PARTLY artifact ({len(s['PARTLY_ARTIFACT'])}): {s['PARTLY_ARTIFACT']}")
        print(f"[{arm}] real throughout ({len(s['REAL_THROUGHOUT'])})")
        print(f"[{arm}] replay mismatch ({len(s['REPLAY_MISMATCH'])}): {s['REPLAY_MISMATCH']}")
    print(f"\narms disagree on the real end turn for {len(disagree)}/34: {disagree}")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
