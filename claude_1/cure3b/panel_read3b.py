#!/usr/bin/env python3
"""Read Candidate 3b's panel against the NINE pre-commitments written into the card at 15:16Z.

The card (`coordination/tasks/20260826-candidate-3b-stuck-holder-release.md`) fixed every gate
before this panel was generated. This script evaluates each of them and prints PASS/FAIL per gate;
any FAIL closes the task under "Dead means" with no retune. It reads the panel's own
`games.jsonl.gz` command streams, never the summary rows, so "changed" means the command stream
changed.

Candidate 3's archives are read alongside 3b's, because three gates are comparative: the own-score
floor is Candidate 3's +25 minus 5, `m061` is compared to the champion's 75/82, and "no game
Candidate 3 won is lost" is a per-game comparison against Candidate 3's own arm.

    python3 claude_1/cure3b/panel_read3b.py
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "narrate7"))
import narrate7 as n7  # noqa: E402

GAMES3B = {arm: Path(f"/tmp/claude-1000/cure3b/{arm}/games/games.jsonl.gz")
           for arm in ("ruleoff", "candidate", "instrument")}
GAMES3 = {arm: Path(f"/tmp/claude-1000/cure3/{arm}/games/games.jsonl.gz")
          for arm in ("ruleoff", "candidate")}

# The champion's own scores on the two `m061` seats, from D-3's inputs manifest and the panel's
# own parent rows — the number gate 4 is measured against.
M061_CHAMPION = {("m061", 0): 75, ("m061", 1): 82}
# The four panel loop games of §9.3. The other two of "all six" are the fixtures OSC-006/OSC-007,
# read by `containment3b.py`, not here.
LOOP_GAMES = [("m078", 0), ("m090", 0), ("m090", 1), ("m118", 1)]
OWN_SCORE_FLOOR = 20      # Candidate 3's +25 outside m061, minus the card's 5-point tolerance
KA_CEILING = 60


def load(path):
    out = {}
    with gzip.open(path, "rt") as fh:
        for line in fh:
            row = json.loads(line)
            out[(row["map_id"], row["seat"])] = row
    return out


def command_lines(row):
    return row["artifacts"]["candidate_commands"].rstrip("\n").split("\n")


def parent_lines(row):
    """The champion's own stream in OUR seat — stripped of `MSG` like the arm's, because the
    champion emits an announcement fragment of its own on turn 1. Comparing a stripped arm line
    against an unstripped parent line reports a divergence on turn 1 of every game and is the
    first thing that went wrong when this gate was measured."""
    return [n7.strip_msg(l)
            for l in row["artifacts"]["parent_commands"].rstrip("\n").split("\n")]


def stripped(row):
    return [n7.strip_msg(l) for l in command_lines(row)]


def won(row):
    return row["candidate"]["score"] > row["candidate"].get("opp_score", 0)


def main() -> int:
    a = {arm: load(p) for arm, p in GAMES3B.items()}
    c3 = {arm: load(p) for arm, p in GAMES3.items()}
    keys = sorted(a["candidate"])
    gates, report = {}, {"games": len(keys)}

    # ---- gate 1: containment, at COMMAND level on all 240 panel games -----------------------
    # Not a score comparison: two streams can total the same score and still be different play.
    ro_diff = [k for k in keys if stripped(a["ruleoff"][k]) != parent_lines(a["ruleoff"][k])]
    report["containment_games_differing"] = len(ro_diff)
    report["containment_first_differing"] = [f"{m}:{s}" for m, s in ro_diff[:5]]
    report["containment_score_identical"] = all(
        a["ruleoff"][k]["candidate"]["score"] == a["ruleoff"][k]["parent"]["score"] for k in keys)
    gates["1_containment_ruleoff_byte_identical"] = not ro_diff

    # ---- probe parity: the instrument must be the candidate in play, or nothing read is about it
    probe_diff = [k for k in keys if stripped(a["instrument"][k]) != stripped(a["candidate"][k])]
    report["probe_parity_games_differing"] = len(probe_diff)
    report["probe_parity_first_differing"] = [f"{m}:{s}" for m, s in probe_diff[:5]]
    gates["0_probe_parity"] = not probe_diff

    # ---- the v7 census over the whole panel, plus gates 2 and 6 -----------------------------
    census = n7.new_census()
    errors, ka_by_game, xc_by_game, rs_by_game = [], {}, {}, {}
    for k in keys:
        lines = command_lines(a["instrument"][k])
        ka_max = xc = rs = 0
        for line in lines:
            frags = n7.msg_fragments(line)
            if len(frags) != 1:
                continue
            _t, _u, _o, _b, meta = n7.decode(frags[0].strip())
            ka_max = max(ka_max, meta["ka"])
            xc += meta["xc"]
            rs += meta["rs"]
        errs = n7.check_telemetry(f"{k[0]}:{k[1]}", None, lines, census, rule_off=False)
        errors.extend(f"{k[0]}:{k[1]}: {e}" for e in errs[:3])
        ka_by_game[f"{k[0]}:{k[1]}"] = ka_max
        if xc:
            xc_by_game[f"{k[0]}:{k[1]}"] = xc
        if rs:
            rs_by_game[f"{k[0]}:{k[1]}"] = rs
    report["telemetry_errors"] = len(errors)
    report["telemetry_errors_sample"] = errors[:20]
    report["ka_max_over_panel"] = max(ka_by_game.values())
    report["ka_max_by_game_top"] = dict(sorted(ka_by_game.items(), key=lambda kv: -kv[1])[:10])
    report["xc_by_game"] = xc_by_game
    report["rs_fires_by_game"] = rs_by_game
    report["rs_total"] = sum(rs_by_game.values())
    gates["6_ka_max_below_60"] = report["ka_max_over_panel"] < KA_CEILING
    gates["2_xc_zero_on_loop_games"] = all(
        xc_by_game.get(f"{m}:{s}", 0) == 0 for m, s in LOOP_GAMES)
    report["loop_games_xc"] = {f"{m}:{s}": xc_by_game.get(f"{m}:{s}", 0) for m, s in LOOP_GAMES}

    # ---- gate 3 and gate 8: own-score deltas vs the rule-off arm, every changed game named ---
    deltas = []
    for k in keys:
        d = a["candidate"][k]["candidate"]["score"] - a["ruleoff"][k]["candidate"]["score"]
        if d:
            deltas.append({"map": k[0], "seat": k[1], "delta_own_points": d,
                           "candidate3b": a["candidate"][k]["candidate"]["score"],
                           "ruleoff": a["ruleoff"][k]["candidate"]["score"],
                           "class": a["candidate"][k]["class"],
                           "profile": a["candidate"][k]["profile"],
                           "rs_fires": rs_by_game.get(f"{k[0]}:{k[1]}", 0)})
    outside = [d for d in deltas if d["map"] != "m061"]
    report["own_score_deltas"] = deltas
    report["own_score_delta_total"] = sum(d["delta_own_points"] for d in deltas)
    report["own_score_delta_outside_m061"] = sum(d["delta_own_points"] for d in outside)
    report["changed_games_commands"] = sum(
        1 for k in keys if stripped(a["candidate"][k]) != stripped(a["ruleoff"][k]))
    report["changed_games_own_score"] = len(deltas)
    gates["3_own_score_outside_m061_at_least_20"] = (
        report["own_score_delta_outside_m061"] >= OWN_SCORE_FLOOR)
    gates["8_every_changed_game_named"] = len(deltas) == len(report["own_score_deltas"])

    # ---- gate 4: m061, both seats within 10 of the champion ----------------------------------
    m061 = {}
    for k, champ in M061_CHAMPION.items():
        got = a["candidate"][k]["candidate"]["score"]
        m061[f"{k[0]}:{k[1]}"] = {"candidate3b": got, "champion": champ, "gap": got - champ,
                                  "candidate3": c3["candidate"][k]["candidate"]["score"]}
    report["m061"] = m061
    gates["4_m061_within_10_of_champion"] = all(abs(v["gap"]) <= 10 for v in m061.values())

    # ---- gate 5: no game Candidate 3 won is lost by 3b ---------------------------------------
    lost = [f"{m}:{s}" for (m, s) in keys
            if won(c3["candidate"][(m, s)]) and not won(a["candidate"][(m, s)])]
    report["candidate3_wins"] = sum(1 for k in keys if won(c3["candidate"][k]))
    report["candidate3b_wins"] = sum(1 for k in keys if won(a["candidate"][k]))
    report["games_won_by_3_lost_by_3b"] = lost
    gates["5_no_candidate3_win_lost"] = not lost

    # ---- 3b vs 3, so the panel says what the ONE added cause did -----------------------------
    vs3 = []
    for k in keys:
        d = a["candidate"][k]["candidate"]["score"] - c3["candidate"][k]["candidate"]["score"]
        same = stripped(a["candidate"][k]) == stripped(c3["candidate"][k])
        if d or not same:
            vs3.append({"map": k[0], "seat": k[1], "delta_vs_candidate3": d,
                        "commands_identical": same,
                        "rs_fires": rs_by_game.get(f"{k[0]}:{k[1]}", 0)})
    report["vs_candidate3"] = vs3
    report["vs_candidate3_score_total"] = sum(v["delta_vs_candidate3"] for v in vs3)
    report["vs_candidate3_games_touched"] = len(vs3)

    report["gates"] = gates
    report["verdict"] = "PASS" if all(gates.values()) else "FAIL"
    report["gates_failed"] = sorted(k for k, v in gates.items() if not v)
    out = HERE / "results" / "panel-read3b.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    for name in sorted(gates):
        print(f"  {'PASS' if gates[name] else 'FAIL'}  {name}")
    brief = {k: v for k, v in report.items() if k not in
             ("own_score_deltas", "ka_max_by_game_top", "telemetry_errors_sample",
              "vs_candidate3", "gates")}
    print(json.dumps(brief, indent=2, sort_keys=True))
    print(f"-> {out}")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
