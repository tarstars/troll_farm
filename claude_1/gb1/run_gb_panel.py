#!/usr/bin/env python3
r"""G-b on real games — the panel.  PASS requires the sweep AND the controls, together.

G-b (Phase 3b design r2 §5) asks whether the ruled EXTEND fallback is command-inert on states
where it duplicates bank candidates.  RULING 1 (`local_claude_1`, `20260823T094600Z`) put its
subject on **real games**: Delta-B fires zero times on the 34 fixtures, and Delta-B states are not
to be synthesised.  This panel runs it on the 149 real ladder games of agent `6652424`.

Gates, each fail-the-run:

- **Probe inertness** on every game: the probe's command stream must equal the uninstrumented
  binary's.  A probe that changes behaviour is measuring a different bot.
- **The re-execution parity gate**: a game contributes Delta-B states only if the re-executed
  stream equals the seat's recorded stdout for the whole game.  Refused games are counted and
  named, never partially used.
- **§2 mutual exclusion**: a fallback entry with `carried>0` and a replant `PICK` in `out` refutes
  §2 and fails the run.
- **§5 step 3**: every Delta-B tick's multiset delta must be duplicate, element-identical bank
  candidates -- nothing added, removed or altered.
- **§5 step 4**: on every Delta-B tick, the selected-and-resolved command of the Delta-B unit must
  be identical between the two variants.  Differences on a SIBLING unit are Delta-A and are
  reported as such, never as Delta-B non-inertness.
- **Not-vacuous**: if the parity-verified corpus reaches zero Delta-B states, the panel reports
  **UNMEASURED**, not PASS.  A green over an empty set is the 08-15 -> 21 failure mode.
- **The controls**: 8/8 must fire, control 4 (the poisoned EXTEND arm) above all.

Run:  python3 claude_1/gb1/run_gb_panel.py --games-dir DIR
"""
from __future__ import annotations

import argparse, glob, hashlib, json, os, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "claude_1" / "adapter1"))

import gb_controls                                  # noqa: E402
import gb_drive                                     # noqa: E402
import replay_to_trace as rt                        # noqa: E402


def corpus_digest(paths):
    sha = hashlib.sha256()
    for path in paths:
        sha.update(os.path.basename(path).encode())
        sha.update(hashlib.sha256(Path(path).read_bytes()).hexdigest().encode())
    return sha.hexdigest()


def sweep(games_dir: Path, probe: Path, plain: Path):
    paths = sorted(glob.glob(str(games_dir / "*.json.gz")))
    games, probe_inert_failures = [], []
    for path in paths:
        row = gb_drive.drive(path, probe)
        game = gb_drive.load_game(path)
        transcript, _, _ = rt.adapt(game, agent_id=gb_drive.AGENT_ID)
        plain_out, _ = gb_controls._drive_text(plain, transcript)
        probe_out, _ = gb_controls._drive_text(probe, transcript)
        if plain_out != probe_out:
            probe_inert_failures.append(row["game_id"])
        games.append(row)
    return paths, games, probe_inert_failures


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--games-dir", required=True)
    ap.add_argument("--bin-dir", default="~/.cache/troll-farm/gb-real")
    ap.add_argument("--out", default=str(HERE / "results" / "gb-real-panel-2026-08-23.json"))
    args = ap.parse_args(argv)

    games_dir = Path(args.games_dir).expanduser()
    bins = Path(args.bin_dir).expanduser()
    probe, poison, plain = bins / "probe", bins / "probe-poison", bins / "instrument"

    paths, games, inert_fail = sweep(games_dir, probe, plain)
    verified = [g for g in games if g["parity"]]
    refused = [g for g in games if not g["parity"]]

    db_verified = [(g["game_id"], t) for g in verified for t in g["delta_b_ticks"]]
    db_refused = [(g["game_id"], t) for g in refused for t in g["delta_b_ticks"]]
    violations = [v for g in games for v in g["violations"]]

    dup_only_failures = [(gid, t["turn"], t["unit"]) for gid, t in db_verified
                         if not t["duplicates_only"]]

    # §5 step 4 on the verified corpus, attributed.
    db_index = {(g["game_id"], t["turn"], t["unit"]) for g in verified for t in g["delta_b_ticks"]}
    step4_failures, sibling_only = [], []
    for g in verified:
        for fork in g["fork_turns"]:
            if fork["same"]:
                continue
            if fork["delta_b_unit_changed"]:
                step4_failures.append({"game": g["game_id"], "turn": fork["turn"],
                                       "differing": fork["differing"],
                                       "unit_ids": fork["differing_unit_ids"]})
            elif any((g["game_id"], fork["turn"], u) in db_index for u in fork["delta_b_units"]):
                sibling_only.append({"game": g["game_id"], "turn": fork["turn"],
                                     "differing": fork["differing"],
                                     "unit_ids": fork["differing_unit_ids"]})

    controls = gb_controls.run(games_dir, probe, poison, plain)

    measured = len(db_verified) > 0
    passed = (not inert_fail and not violations and not dup_only_failures
              and not step4_failures and all(c["fired"] for c in controls) and measured)

    result = {
        "corpus": {"games": len(paths), "digest_sha256": corpus_digest(paths),
                   "agent_id": gb_drive.AGENT_ID, "dir": str(games_dir)},
        "subject_sha256": hashlib.sha256(
            (REPO / "claude_1" / "narrate1" / "instrument-swap-r1-narrate-v2.rs").read_bytes()
        ).hexdigest(),
        "probe_inertness_failures": inert_fail,
        "parity": {
            "verified_games": len(verified), "refused_games": len(refused),
            "refused": [{"game": g["game_id"], "first_divergent_turn": g["first_divergent_turn"],
                         "traced_turns": g["traced_turns"]} for g in refused],
        },
        "census_verified": {
            "traced_turns": sum(g["traced_turns"] for g in verified),
            "fallback_entries": sum(g["fallback_entries"] for g in verified),
            "fallback_entries_carrying": sum(g["fallback_entries_carrying"] for g in verified),
            "delta_a_ticks": sum(len(g["delta_a_ticks"]) for g in verified),
            "delta_b_ticks": len(db_verified),
        },
        "census_refused_games_not_counted": {
            "fallback_entries": sum(g["fallback_entries"] for g in refused),
            "delta_b_ticks": len(db_refused),
            # Named so a reviewer can see there is no admissible tick being left on the table:
            # a Delta-B tick STRICTLY BEFORE a game's first divergent turn would be reached by a
            # command-identical prefix.  Reported, never counted toward the gate.
            "detail": [
                {"game": g["game_id"], "turn": t["turn"], "unit": t["unit"],
                 "first_divergent_turn": g["first_divergent_turn"],
                 "before_divergence": t["turn"] < g["first_divergent_turn"],
                 "duplicates_only": t["duplicates_only"]}
                for g in refused for t in g["delta_b_ticks"]],
        },
        "delta_b_detail_verified": [
            {"game": gid, **{k: v for k, v in t.items() if k != "extra_from_out"}}
            for gid, t in db_verified],
        "mutual_exclusion_violations": violations,
        "duplicates_only_failures": dup_only_failures,
        "step4_delta_b_unit_changed": step4_failures,
        "fork_differences_attributed_to_sibling_delta_a": sibling_only,
        "controls": controls,
        "measured": measured,
        "status": "PASS" if passed else ("UNMEASURED" if not measured else "FAIL"),
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ("delta_b_detail_verified", "controls", "parity")},
                     indent=2, sort_keys=True))
    print("parity: %d verified / %d refused" % (len(verified), len(refused)))
    print("controls: %d/%d fired" % (sum(c["fired"] for c in controls), len(controls)))
    print("status:", result["status"])
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
