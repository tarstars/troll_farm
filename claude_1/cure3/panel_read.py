#!/usr/bin/env python3
"""Read the three Candidate 3 panel runs against r5 §9's pre-commitments.

Reads the panel's own `games.jsonl.gz` artifacts (the full command streams) rather than the
summary rows, so "changed" means *the command stream changed*, not "the score changed" — the two
are different questions and §9.4's pre-registered guess is about the first.

    python3 claude_1/cure3/panel_read.py
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "narrate6"))
import narrate6 as n6  # noqa: E402

GAMES = {arm: Path(f"/tmp/claude-1000/cure3/{arm}/games/games.jsonl.gz")
         for arm in ("ruleoff", "candidate", "instrument")}


def load(arm):
    out = {}
    with gzip.open(GAMES[arm], "rt") as fh:
        for line in fh:
            row = json.loads(line)
            out[(row["map_id"], row["seat"])] = row
    return out


def command_lines(row):
    """The panel stores the stream with a trailing newline; `split` then yields a final empty
    element that is not a turn. Dropping it here rather than tolerating an empty MSG count keeps
    the decoder strict."""
    return row["artifacts"]["candidate_commands"].rstrip("\n").split("\n")


def stripped(row):
    return [n6.strip_msg(l) for l in command_lines(row)]


def main() -> int:
    arms = {arm: load(arm) for arm in GAMES}
    keys = sorted(arms["candidate"])
    report = {"games": len(keys)}

    # r5 §9.1, the panel half of the containment gate: rule-off vs the parent the panel itself ran.
    ro_own = sum(arms["ruleoff"][k]["candidate"]["score"] for k in keys)
    ro_par = sum(arms["ruleoff"][k]["parent"]["score"] for k in keys)
    report["containment_ruleoff_own_total"] = ro_own
    report["containment_parent_total"] = ro_par
    report["containment_score_identical"] = ro_own == ro_par
    report["containment_games_score_differ"] = sum(
        1 for k in keys
        if arms["ruleoff"][k]["candidate"]["score"] != arms["ruleoff"][k]["parent"]["score"])

    # r5 §9, the probe parity gate: the instrument arm with MSG stripped must be byte-identical
    # in play to the candidate arm, or nothing read off the instrument describes the candidate.
    probe_diff = [k for k in keys
                  if stripped(arms["instrument"][k]) != stripped(arms["candidate"][k])]
    report["probe_parity_games_differing"] = len(probe_diff)
    report["probe_parity"] = "PASS" if not probe_diff else "FAIL"
    report["probe_parity_first_differing"] = probe_diff[:5]

    # r5 §9.4, the changed set — the number FIRST, at command level.
    changed = [k for k in keys if stripped(arms["candidate"][k]) != stripped(arms["ruleoff"][k])]
    report["changed_games_commands"] = len(changed)
    report["changed_share_commands"] = round(len(changed) / len(keys), 4)
    score_changed = [k for k in keys
                     if arms["candidate"][k]["candidate"]["score"]
                     != arms["ruleoff"][k]["candidate"]["score"]]
    report["changed_games_own_score"] = len(score_changed)

    # r5 §9.11, every changed game named with its delta in own-score points.
    deltas = []
    for k in sorted(score_changed):
        delta = (arms["candidate"][k]["candidate"]["score"]
                 - arms["ruleoff"][k]["candidate"]["score"])
        deltas.append({"map": k[0], "seat": k[1], "delta_own_points": delta,
                       "candidate": arms["candidate"][k]["candidate"]["score"],
                       "ruleoff": arms["ruleoff"][k]["candidate"]["score"],
                       "class": arms["candidate"][k]["class"],
                       "profile": arms["candidate"][k]["profile"]})
    report["own_score_delta_total"] = sum(d["delta_own_points"] for d in deltas)
    report["own_score_games_up"] = sum(1 for d in deltas if d["delta_own_points"] > 0)
    report["own_score_games_down"] = sum(1 for d in deltas if d["delta_own_points"] < 0)
    report["own_score_deltas"] = deltas

    # §9.5 / §9.6, the detector movements, every one named.
    dets = {}
    for arm in GAMES:
        total = {}
        for k in keys:
            for name, count in arms[arm][k]["detector_counts"].items():
                total[name] = total.get(name, 0) + count
        dets[arm] = total
    report["detector_totals"] = dets
    report["detector_movement_candidate_vs_ruleoff"] = {
        name: dets["candidate"].get(name, 0) - dets["ruleoff"].get(name, 0)
        for name in sorted(set(dets["ruleoff"]) | set(dets["candidate"]))
        if dets["candidate"].get(name, 0) != dets["ruleoff"].get(name, 0)}
    report["blocking_games"] = {arm: sum(1 for k in keys if arms[arm][k]["block"])
                                for arm in GAMES}

    # the v6 census over the whole panel, and the §9.10 risk gate on `ka`.
    census = n6.new_census()
    errors = []
    ka_by_game = {}
    for k in keys:
        lines = command_lines(arms["instrument"][k])
        before = census["ka_max"]
        errs = n6.check_telemetry(f"{k[0]}:{k[1]}", None, lines, census, rule_off=False)
        errors.extend(f"{k[0]}:{k[1]}: {e}" for e in errs[:3])
        if census["ka_max"] != before:
            ka_by_game[f"{k[0]}:{k[1]}"] = census["ka_max"]
    report["telemetry_errors"] = len(errors)
    report["telemetry_errors_sample"] = errors[:20]
    report["census"] = census
    report["risk_gate_ka_ge_30"] = census["ka_max"] >= 30
    report["ka_max_by_game_running"] = ka_by_game

    # r5 §9.3, the pre-committed BLOCK: `xc` on the recorded exchange turns of the loop games.
    loop_games = [("m078", 0), ("m090", 0), ("m090", 1), ("m118", 1)]
    loop = {}
    for k in loop_games:
        if k not in arms["instrument"]:
            loop[f"{k[0]}:{k[1]}"] = "ABSENT FROM THIS CORPUS"
            continue
        turns = []
        for index, line in enumerate(command_lines(arms["instrument"][k]), 1):
            frags = n6.msg_fragments(line)
            if len(frags) != 1:
                continue
            _t, _u, _o, _b, meta = n6.decode(frags[0].strip())
            if meta["xc"]:
                turns.append({"turn": index, "xc": meta["xc"]})
        loop[f"{k[0]}:{k[1]}"] = {"contested_turns": turns, "xc_total": sum(t["xc"] for t in turns)}
    report["loop_games_xc"] = loop

    out = HERE / "results" / "panel-read.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    keep = {k: v for k, v in report.items() if k not in
            ("own_score_deltas", "census", "ka_max_by_game_running",
             "telemetry_errors_sample", "probe_parity_first_differing")}
    print(json.dumps(keep, indent=2, sort_keys=True))
    print(f"-> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
