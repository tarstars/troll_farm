#!/usr/bin/env python3
r"""Phase 3b REACH on real games -- the panel.  A number is reported only with its controls.

Charter: `local_claude_1` RULING `20260823T131400Z` (`20260820-pair-selector-anti-benching`) --
"run the Phase 3b candidate against this real corpus and answer one question: on how many of the
2,903 nothing/nothing turns would the un-discarded options have given the troll something real to
do?  Report the count, and the per-game distribution.  Report zero as zero if that is the answer."

This is a REACH measurement.  It grades nothing, opens no gate, promotes no candidate, decomposes
no cost, and takes no Arena action.

## The two claims, kept apart

The reviewer's question (codex_1, per the ruling) is whether the comparison can distinguish
"the option was restored" from "the option was restored and would have been selected".  It can,
because both arms are run through `select_recording` + `resolve_move_conflicts` over the identical
state, so every reach row is reported at BOTH altitudes:

- **RESTORED**: the unit's `available` (unit-local best, the same `max_by` expression the live
  instrument used) becomes a concrete target on the EXTEND arm while it was `NONE` on the base.
- **SELECTED**: the same unit's `chosen` -- what joint pairing actually gave it -- becomes a
  concrete target.  SELECTED is a subset of RESTORED by construction and is the smaller,
  stronger number.

## Gates, each fail-the-run

- **Probe inertness** on every game: the probe's command stream must equal the uninstrumented v3
  instrument's.  A probe that changes behaviour is measuring a different bot.
- **Re-execution parity**: a game contributes rows only if the re-executed stream equals the
  seat's recorded stdout for the whole game.  Refused games are counted and named, never
  partially used.
- **Telemetry identity**: on every verified game the base arm's `(chosen, available)` per unit per
  turn must equal the NARRATE v3 rows the bot PRINTED in that replay.  This is what makes the base
  arm the live bot rather than a plausible re-implementation of it.
- **Confinement**: any row where the arms' `available` differs must sit on a turn/unit where the
  idle-regeneration fallback actually fired.  A difference anywhere else means the flag leaked.
- **Not-vacuous**: if the verified corpus reaches zero nothing/nothing rows the panel reports
  UNMEASURED, not a zero reach.  A green over an empty set is the 08-15 -> 21 failure mode.
- **The controls**: the null fork must produce exactly zero reach and zero command differences;
  the poisoned fork must move both.  A fork that cannot move is inert and its zero is worthless.

Run:  python3 claude_1/reach1/run_reach_panel.py --games-dir DIR
"""
from __future__ import annotations

import argparse, glob, hashlib, json, os, subprocess, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "claude_1" / "adapter1"))

import reach_drive                                  # noqa: E402
import replay_to_trace as rt                        # noqa: E402

CONCRETE_PREFIXES = ("TREE(", "BANK(", "CELL(", "SHACK")


def concrete(target: str) -> bool:
    """A real thing to do: neither `NONE` (an explicit WAIT was best) nor `ABSENT` (no vector)."""
    return target.startswith(CONCRETE_PREFIXES)


def corpus_digest(paths):
    sha = hashlib.sha256()
    for path in paths:
        sha.update(os.path.basename(path).encode())
        sha.update(hashlib.sha256(Path(path).read_bytes()).hexdigest().encode())
    return sha.hexdigest()


def run_plain(binary, transcript):
    proc = subprocess.run([str(binary)], input=transcript, capture_output=True, text=True)
    return proc.stdout


def sweep(paths, probe, plain=None):
    games = []
    inert_failures = []
    for path in paths:
        row = reach_drive.drive(path, probe)
        if plain is not None:
            game = reach_drive.load_game(path)
            transcript, _, _ = rt.adapt(game, agent_id=reach_drive.AGENT_ID)
            if run_plain(plain, transcript) != run_plain(probe, transcript):
                inert_failures.append(row["game_id"])
        games.append(row)
    return games, inert_failures


def classify(games):
    """The joint table and the reach counts, over the games handed in (already parity-verified)."""
    joint = Counter()
    nothing_nothing = 0
    restored, selected = 0, 0
    per_game_nn, per_game_restored, per_game_selected = {}, {}, {}
    restored_shapes, selected_shapes = Counter(), Counter()
    examples = []
    confinement_failures = []
    for game in games:
        falls = {tuple(k) for k in game["fallback_keys"]}
        gid = game["game_id"]
        per_game_nn[gid] = per_game_restored[gid] = per_game_selected[gid] = 0
        for row in game["rows"]:
            key = (row["bchosen"], row["bavail"])
            joint[("CONCRETE" if concrete(key[0]) else key[0],
                   "CONCRETE" if concrete(key[1]) else key[1])] += 1
            if row["bavail"] != row["cavail"] and (row["turn"], row["unit"]) not in falls:
                confinement_failures.append({"game": gid, "turn": row["turn"],
                                             "unit": row["unit"],
                                             "bavail": row["bavail"], "cavail": row["cavail"]})
            if row["bchosen"] == "NONE" and row["bavail"] == "NONE":
                nothing_nothing += 1
                per_game_nn[gid] += 1
                if concrete(row["cavail"]):
                    restored += 1
                    per_game_restored[gid] += 1
                    restored_shapes[row["cavail"].split("(")[0]] += 1
                    if concrete(row["cchosen"]):
                        selected += 1
                        per_game_selected[gid] += 1
                        selected_shapes[row["cchosen"].split("(")[0]] += 1
                    if len(examples) < 25:
                        examples.append({"game": gid, "turn": row["turn"], "unit": row["unit"],
                                         "cavail": row["cavail"], "cchosen": row["cchosen"]})
    return {
        "joint_table": {"%s/%s" % k: v for k, v in sorted(joint.items())},
        "unit_rows": sum(joint.values()),
        "nothing_nothing": nothing_nothing,
        "restored": restored,
        "selected": selected,
        "restored_shapes": dict(restored_shapes),
        "selected_shapes": dict(selected_shapes),
        "per_game_nothing_nothing": per_game_nn,
        "per_game_restored": per_game_restored,
        "per_game_selected": per_game_selected,
        "examples": examples,
        "confinement_failures": confinement_failures[:20],
        "confinement_failure_count": len(confinement_failures),
    }


def distribution(per_game):
    values = sorted(per_game.values())
    if not values:
        return {}
    n = len(values)
    total = sum(values)
    top = max(1, n // 10)
    return {"games": n, "total": total, "zero_games": sum(1 for v in values if v == 0),
            "nonzero_games": sum(1 for v in values if v > 0),
            "mean": round(total / n, 4), "median": values[n // 2], "max": values[-1],
            "worst_decile_share": sum(values[-top:]),
            "histogram": dict(sorted(Counter(values).items()))}


def sel_diffs(games):
    """Whole-turn command-vector differences between the arms, over the games handed in."""
    turns_differing = 0
    for game in games:
        turns_differing += sum(1 for s in game["sels"] if not s["same"])
    return turns_differing


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--games-dir", default="~/.cache/troll-farm/reach1/games")
    ap.add_argument("--bin-dir", default="~/.cache/troll-farm/reach1")
    ap.add_argument("--out", default=str(HERE / "results" / "reach-panel-2026-08-23.json"))
    args = ap.parse_args(argv)

    games_dir = Path(args.games_dir).expanduser()
    bins = Path(args.bin_dir).expanduser()
    probe, poison, null, plain = (bins / "probe-honest", bins / "probe-poison",
                                  bins / "probe-null", bins / "instrument")
    paths = sorted(glob.glob(str(games_dir / "*.json.gz")))

    games, inert_failures = sweep(paths, probe, plain)
    verified = [g for g in games if g["parity"]]
    refused = [g for g in games if not g["parity"]]
    parse_errors = [{"game": g["game_id"], "errors": g["parse_errors"][:5]}
                    for g in games if g["parse_errors"]]
    identity_failures = [{"game": g["game_id"], "count": g["identity_mismatch_count"],
                          "first": g["identity_mismatches"][:3]}
                         for g in verified if g["identity_mismatch_count"]]

    main_result = classify(verified)
    honest_sel_diff_turns = sel_diffs(verified)

    # Controls.  The null fork must be a flat zero; the poisoned fork must move.
    null_games, _ = sweep(paths, null)
    null_verified = [g for g in null_games if g["parity"]]
    null_result = classify(null_verified)
    null_sel_diff_turns = sel_diffs(null_verified)

    poison_games, _ = sweep(paths, poison)
    poison_verified = [g for g in poison_games if g["parity"]]
    poison_result = classify(poison_verified)
    poison_sel_diff_turns = sel_diffs(poison_verified)

    controls = [
        {"id": 1, "name": "probe-inertness",
         "expect": "the probe's stdout equals the uninstrumented v3 instrument's on all 160 games",
         "observed": {"failures": inert_failures},
         "fired": not inert_failures},
        {"id": 2, "name": "telemetry-identity",
         "expect": "on every parity-verified game the base arm reproduces the NARRATE v3 rows the "
                   "bot printed on the wire, exactly",
         "observed": {"failing_games": identity_failures[:5],
                      "failing_game_count": len(identity_failures),
                      "rows_checked": sum(g["identity_checked"] for g in verified)},
         "fired": not identity_failures and sum(g["identity_checked"] for g in verified) > 0},
        {"id": 3, "name": "not-vacuous",
         "expect": "the parity-verified corpus carries at least one nothing/nothing row",
         "observed": {"nothing_nothing": main_result["nothing_nothing"]},
         "fired": main_result["nothing_nothing"] > 0},
        {"id": 4, "name": "confinement",
         "expect": "the arms' `available` differs only on turn/units where the fallback fired",
         "observed": {"failures": main_result["confinement_failure_count"],
                      "first": main_result["confinement_failures"][:3]},
         "fired": main_result["confinement_failure_count"] == 0},
        {"id": 5, "name": "null-fork-is-flat",
         "expect": "with both arms the incumbent body, reach is 0 and no turn's command vector "
                   "differs -- the measurement cannot manufacture a difference",
         "observed": {"restored": null_result["restored"], "selected": null_result["selected"],
                      "sel_diff_turns": null_sel_diff_turns,
                      "nothing_nothing": null_result["nothing_nothing"]},
         "fired": (null_result["restored"] == 0 and null_result["selected"] == 0
                   and null_sel_diff_turns == 0
                   and null_result["nothing_nothing"] == main_result["nothing_nothing"])},
        {"id": 6, "name": "poison-fork-moves",
         "expect": "with one candidate the REPLACE arm cannot produce, reach and the command "
                   "vectors both move -- the fork is not inert",
         "observed": {"restored": poison_result["restored"],
                      "selected": poison_result["selected"],
                      "sel_diff_turns": poison_sel_diff_turns,
                      "honest_restored": main_result["restored"],
                      "honest_sel_diff_turns": honest_sel_diff_turns},
         "fired": (poison_result["restored"] > main_result["restored"]
                   and poison_sel_diff_turns > 0)},
        {"id": 7, "name": "no-parse-errors",
         "expect": "every probe row and every recorded NARRATE line parses; nothing is skipped",
         "observed": {"games_with_errors": parse_errors[:5], "count": len(parse_errors)},
         "fired": not parse_errors},
        {"id": 8, "name": "fallback-actually-fires",
         "expect": "the idle-regeneration fallback fires on the verified corpus, so the EXTEND "
                   "body is reached at all",
         "observed": {"fallback_entries": sum(g["fallback_entries"] for g in verified),
                      "entries_discarding_a_list":
                          sum(g["fallback_entries_with_discard"] for g in verified),
                      "entries_discarding_a_replant_pick":
                          sum(g["fallback_discarded_picks"] for g in verified)},
         "fired": sum(g["fallback_entries"] for g in verified) > 0},
    ]

    passed = (all(c["fired"] for c in controls) and not inert_failures
              and not identity_failures and not parse_errors)

    result = {
        "task": "20260820-pair-selector-anti-benching",
        "what": "Phase 3b REACH on the v3 real-game corpus -- a reach measurement, nothing more",
        "charter": "coordination/messages/local_claude_1/"
                   "20260823T131400Z-20260820-pair-selector-anti-benching-policy.md",
        "corpus": {"games": len(paths), "agent_id": reach_drive.AGENT_ID,
                   "submission_id": 41182608,
                   "package": "local_claude_1/narrate/v3/"
                              "games-agent6652642-submission41182608.jsonl.gz",
                   "package_sha256": "0116994468cb6d23702511d0cefce28ee"
                                     "aeeb049eb8e7fc24ccdc29b886c3ceb",
                   "artifact_commit": "39269312913b00e238b5a26da82c11711c32b935",
                   "split_digest_sha256": corpus_digest(paths)},
        "subject_sha256": hashlib.sha256(
            (REPO / "claude_1" / "narrate3"
             / "instrument-swap-r1-narrate-v3.rs").read_bytes()).hexdigest(),
        "probe_sha256": {arm: hashlib.sha256(
            (HERE / ("probe-reach-%s.rs" % arm)).read_bytes()).hexdigest()
            for arm in ("honest", "poison", "null")},
        "parity": {"verified_games": len(verified), "refused_games": len(refused),
                   "refused": [{"game": g["game_id"],
                                "first_divergent_turn": g["first_divergent_turn"]}
                               for g in refused]},
        "verified_traced_turns": sum(g["traced_turns"] for g in verified),
        "answer": {
            "question": "on how many nothing/nothing turns would the un-discarded options have "
                        "given the troll something real to do?",
            "nothing_nothing_rows_on_verified_corpus": main_result["nothing_nothing"],
            "restored": main_result["restored"],
            "selected": main_result["selected"],
            "restored_shapes": main_result["restored_shapes"],
            "selected_shapes": main_result["selected_shapes"],
            "restored_distribution": distribution(main_result["per_game_restored"]),
            "selected_distribution": distribution(main_result["per_game_selected"]),
            "nothing_nothing_distribution": distribution(main_result["per_game_nothing_nothing"]),
            "examples": main_result["examples"],
            "whole_turn_command_vector_differences": honest_sel_diff_turns,
        },
        "joint_table_verified": main_result["joint_table"],
        "unit_rows_verified": main_result["unit_rows"],
        "probe_inertness_failures": inert_failures,
        "identity_failures": identity_failures[:5],
        "parse_errors": parse_errors[:5],
        "controls": controls,
        "verdict": "PASS" if passed else "FAIL",
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=1, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items()
                      if k in ("verdict", "parity", "answer", "joint_table_verified")},
                     indent=1, sort_keys=True)[:4000])
    print("controls:", [(c["id"], c["name"], c["fired"]) for c in controls])
    print("written:", args.out)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
