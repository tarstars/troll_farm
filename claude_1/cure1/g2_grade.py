#!/usr/bin/env python3
"""**The G-2 grade** — the Candidate 1 hold rule read on 160 real ladder games.

Task `20260825-dance-cure-candidate-1-hold`.  Ordered by
`local_claude_1/20260825T103500Z-…-policy.md` (G-2), package handed over at
`local_claude_1/20260825T113500Z-…-handoff.md` (`agent/local_claude_1@5d51b8c7`).  The grading
plan was published *before* the package existed, in `claude_1/20260825T105100Z-…-update.md`;
this module runs that plan and adds nothing to it.

## What is imported, not re-stated

  * the adapter `replay_to_trace`, unmodified;
  * the detectors `trace_detectors.detect_d1/d2/d3`, unmodified;
  * the accepted real-game fact table and classes, `dance1/dance_facts`, unmodified — F1…F7,
    `mech`, the r3 class precedence, ruled DEFINITIONS_ACCEPTED by codex_1 `20260824T172730Z`;
  * `R_pos`, `regressive_baseline.measure_game`, the *same function object* that produced the
    pre-committed v3 bar, called with the v4 join in place of the v3 one;
  * the liveness primitives `fuzz_panel.progress_turns / stall_windows / live_horizon`, so the
    real-game long-stall proxy is the panel's own P4 arithmetic and not a new opinion;
  * the v4 grammar `narrate4.decode` through the join `narrate4/narrate4_join.py`.

`dance_facts` is called with `version="v3"`.  That is not a mislabel and it is not a
modification: v4 is v3's payload **plus** `r=`/`b=`, the `chosen` / `available` fields carry the
identical spellings, and `version` selects exactly two predicates — F4's per-turn target sequence
and the `AVAILABLE_REAL_TARGET` tag — both of which read only those two fields.  The v4-only
fields are read by the new layer in this module and never by the accepted classifier.

## The clauses, as fixed before the read

  (a) F7 `DANCER_PROGRESS` share >= the v3 instrument pass's 52 of 80 = 65.00 %;
  (b) `R_pos` <= 3.8386 per 1,000 own troll-turns (half of the pre-committed 7.6771 baseline);
  kill: idle-with-work (`H`+`W`) share > 1.5 %; D-3 > 0; long-stall share of games above the
  champion's; any P1/P2 row migrating to a parked or stalled shape.

## The limit carried into the grade, unsoftened

`R_pos` is an outcome measure over positions; `r=R` is a resolver decision label.  Clause (b) is
graded `R_pos` on **both** sides.  The crosswalk between them is computed here for the first time
— the G-2 replays are the first corpus carrying positions and `r=` together — and is published as
a finding about the instrument, never folded into the gate.

    python3 claude_1/cure1/g2_grade.py [--games …] [--agent 6659743]
"""
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for _p in (HERE, REPO / "claude_1" / "dance1", REPO / "claude_1" / "adapter1",
           REPO / "claude_1" / "banana-restoration-r2", REPO / "claude_1" / "narrate1",
           REPO / "claude_1" / "narrate4", REPO / "claude_1" / "pipeline", REPO):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import dance_facts as df                    # noqa: E402
import fuzz_panel as fp                     # noqa: E402
import narrate4_join as n4j                 # noqa: E402
import regressive_baseline as rb            # noqa: E402
import replay_to_trace as rt                # noqa: E402
import trace_detectors as td                # noqa: E402

DEFAULT_GAMES = Path("/tmp/claude-1000/cure1/g2/games-agent6659743-submission41192036.jsonl.gz")
GAMES_SHA256 = "050d1ceb65ba1f03e67065f311920cb4aab19eb0e6564a1f285477d2dc5c6a38"
DEFAULT_AGENT = 6659743
#: the arm that was played, checked against `arm-manifest.json`'s instrument
ARM_SHA256 = "cc4b308705883f10192065dd205a36eb78baee3c1068a0697131b791f3d46e9b"
BASELINE = HERE / "results" / "regressive-baseline-v3.json"
OUT = HERE / "results" / "g2-grade.json"

CLAUSE_A_BAR = 52.0 / 80.0 * 100.0          # 65.00 %, the v3 instrument pass's F7 share
CLAUSE_B_BAR = 3.8386                       # per 1,000 own troll-turns
IDLE_LINE = 1.5                             # %
STALL_WINDOW = 60                           # fuzz_panel P4's window, unchanged
HOLD_PROGRESS_K = 3                         # turns after a hold run in which progress is looked for


# --------------------------------------------------------------------------
# scope: R-B makes the hold INERT for a whole game on an orchard-eligible seat
# view.  The predicate is the arm's own (cure1-hold-v4.rs:756), read here off
# the adapter's reconstructed turn-1 state.
# --------------------------------------------------------------------------

def orth(cell):
    x, y = cell
    return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]


def orchard_eligible(tr) -> bool:
    walk = tr.smap.walkable
    water = tr.smap.water
    doors = sorted(c for c in orth(tr.smap.shacks[0]) if c in walk)
    if len(doors) < 2:
        return False
    st = tr.state(1)
    natural = [p.cell for p in st.plants if p.health > 0]
    if not natural:
        return False
    home = td.bfs_distances(walk, doors)
    returns = []
    for cell in natural:
        if cell not in home:
            return False
        returns.append(home[cell])
    returns.sort()
    n = len(returns)
    # integer median, exactly as the arm compares it: odd -> middle >= 8; even -> sum of the two
    # middles >= 16, which is the panel's median >= 8.0 without a float.
    median_ok = returns[n // 2] >= 8 if n % 2 else (returns[n // 2 - 1] + returns[n // 2]) >= 16
    if not median_ok:
        return False
    enemy_doors = [c for c in orth(tr.smap.shacks[1]) if c in walk]
    edist = td.bfs_distances(walk, enemy_doors)
    plant_cells = {p.cell for p in st.plants}
    for door in doors:
        if door in plant_cells:
            continue
        if not any(w in water for w in orth(door)):
            continue
        if edist.get(door, 10 ** 9) >= 11:
            return True
    return False


# --------------------------------------------------------------------------
# long-stall, the panel's own P4 arithmetic on a replay trace
# --------------------------------------------------------------------------

def long_stall(tr) -> dict:
    """Maximal progress-free runs of >= 60 turns, trimmed to the live horizon (P4's rule).

    Reported for the G-2 corpus and the champion corpus with the identical function, because the
    kill rule compares the two shares.  It is a **proxy** for the panel's P4 and is labelled one:
    P4 runs against a referee that knows the outcome of the final turn, a replay does not, so the
    last turn carries no obligation here (`stall_windows`' own default).
    """
    prog = fp.progress_turns(tr)
    horizon = fp.live_horizon(tr)
    runs = fp.stall_windows(prog, tr.T, STALL_WINDOW)
    live = []
    for run in runs:
        lo, hi = (run[0], run[1]) if isinstance(run, (tuple, list)) else (run["start"], run["end"])
        hi = min(hi, horizon - 1)
        if hi - lo + 1 >= STALL_WINDOW:
            live.append({"start": lo, "end": hi})
    return {"live_horizon": horizon, "stalls": live, "long_stall": bool(live),
            "longest": max((s["end"] - s["start"] + 1 for s in live), default=0)}


# --------------------------------------------------------------------------
# the per-game grade
# --------------------------------------------------------------------------

def grade_game(game, agent_id):
    gid = game.get("gameId")
    tr, meta = rt.adapt_to_trace(game, agent_id=agent_id)
    seat = meta["seat"]
    rows, jmeta = n4j.decode_game(game, agent_id)

    r1 = td.detect_d1(tr)
    d2 = td.detect_d2(tr)["count"]
    d3 = td.detect_d3(tr)["count"]

    branches = collections.Counter()
    per_troll = collections.Counter()
    per_troll_turns = collections.Counter()
    branch_of = {}
    longest_hold_run = 0
    by_unit = collections.defaultdict(dict)
    for row in rows:
        b = row["branch"]
        branches[b] += 1
        per_troll_turns[row["unit"]] += 1
        if b in ("H", "W"):
            per_troll[row["unit"]] += 1
        if b == "H":
            longest_hold_run = max(longest_hold_run, row["blocked"])
        branch_of[(row["turn"], row["unit"])] = b
        by_unit[row["unit"]][row["turn"]] = row

    # holds followed by the held unit's own progress, within K turns of the run's end.
    hold_runs = 0
    hold_runs_with_progress = 0
    for uid, turns in by_unit.items():
        ts = sorted(turns)
        run_end = None
        for t in ts:
            if turns[t]["branch"] == "H":
                run_end = t
                continue
            if run_end is not None:
                hold_runs += 1
                if any(df.progress_event(tr, uid, s)
                       for s in range(run_end + 1, min(run_end + HOLD_PROGRESS_K, tr.T - 1) + 1)):
                    hold_runs_with_progress += 1
                run_end = None
        if run_end is not None:                      # a run that reaches the last traced turn
            hold_runs += 1
            if any(df.progress_event(tr, uid, s)
                   for s in range(run_end + 1, min(run_end + HOLD_PROGRESS_K, tr.T - 1) + 1)):
                hold_runs_with_progress += 1

    # R_pos through the pinned baseline measure, v4 join swapped in for the v3 one.
    verdicts = {}
    rpos = rb.measure_game(game, agent_id, poison_shift=1, decode=n4j.decode_game,
                           row_sink=lambda t, u, v: verdicts.__setitem__((t, u), v))

    # the owed crosswalk, over the population BOTH labels can speak about.
    cross = collections.Counter()
    for key, b in branch_of.items():
        v = verdicts.get(key)
        rp = (v == "MOVED_REGRESSIVE")
        rr = (b == "R")
        if v is None:
            cross["r_pos_ineligible_rR" if rr else "r_pos_ineligible_not_rR"] += 1
        else:
            cross[("both" if rp and rr else "r_pos_only" if rp else
                   "r_eq_R_only" if rr else "neither")] += 1

    telemetry = {(r["turn"], r["unit"]): r for r in rows}
    episodes = []
    for ep in r1["episodes"]:
        row = df.episode_row(tr, ep, gid, agent_id, seat, telemetry, "v3", "instrument")
        window = range(ep["turn_start"], ep["turn_end"] + 1)
        seq = [branch_of.get((t, ep["unit"])) for t in window]
        row["v4_branch_sequence"] = seq
        # the D-1 split the policy asks for, read off `r=` and nothing else.
        row["block_kind"] = ("HOLD_SEEN" if "H" in seq else
                             "REGRESSIVE_NO_HOLD" if "R" in seq else "NEITHER")
        episodes.append(row)

    stall = long_stall(tr)
    return {
        "game": gid, "seat": seat, "turns": tr.T,
        "d1": r1["count"], "d2": d2, "d3": d3,
        "branches": dict(branches),
        "troll_turns": sum(branches.values()),
        "idle_with_work_turns": branches["H"] + branches["W"],
        "per_troll": {str(u): {"idle": per_troll[u], "turns": per_troll_turns[u]}
                      for u in per_troll_turns},
        "longest_hold_b": longest_hold_run,
        "hold_runs": hold_runs, "hold_runs_with_progress": hold_runs_with_progress,
        "scope_active": not orchard_eligible(tr),
        "pz_max": max((m["pz"] for m in jmeta["per_turn"].values()), default=0),
        "sp_total": sum(m["sp"] for m in jmeta["per_turn"].values()),
        "wc_total": sum(m["wc"] for m in jmeta["per_turn"].values()),
        "longest_command_line_chars": jmeta["longest_command_line_chars"],
        "opponent_narrate_turns": jmeta["opponent_narrate_turns"],
        "rpos": rpos,
        "crosswalk": dict(cross),
        "long_stall": stall,
        "episodes": episodes,
    }


def champion_stalls(path: Path, manifest: Path):
    """The champion corpus under the identical long-stall function."""
    agent_by_game = {g["game_id"]: g["agent_id"]
                     for g in json.loads(manifest.read_text())["games"]}
    games = stalls = refused = 0
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            game = json.loads(line)
            agent = agent_by_game.get(game.get("gameId"))
            if agent is None:
                refused += 1
                continue
            try:
                tr, _meta = rt.adapt_to_trace(game, agent_id=agent)
            except rt.AdapterError:
                refused += 1
                continue
            games += 1
            if long_stall(tr)["long_stall"]:
                stalls += 1
    return {"games": games, "refused": refused, "long_stall_games": stalls,
            "long_stall_share_pct": round(100.0 * stalls / games, 4) if games else None}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--games", type=Path, default=DEFAULT_GAMES)
    ap.add_argument("--agent", type=int, default=DEFAULT_AGENT)
    ap.add_argument("--expect-sha256", default=GAMES_SHA256)
    ap.add_argument("--manifest", type=Path, default=None)
    ap.add_argument("--champion-games", type=Path, default=None)
    ap.add_argument("--champion-manifest", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args(argv)

    digest = hashlib.sha256(args.games.read_bytes()).hexdigest()
    if args.expect_sha256 and digest != args.expect_sha256:
        raise SystemExit("corpus SHA-256 %s != the handed-off %s; refusing to grade an "
                         "unpinned package" % (digest, args.expect_sha256))

    per_game, refusals = [], []
    with gzip.open(args.games, "rt", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            game = json.loads(line)
            try:
                per_game.append(grade_game(game, args.agent))
            except (rt.AdapterError, n4j.Narrate4Error) as exc:
                refusals.append({"game": game.get("gameId"), "reason": str(exc)})

    games = len(per_game)
    branches = collections.Counter()
    for g in per_game:
        branches.update(g["branches"])
    troll_turns = sum(g["troll_turns"] for g in per_game)
    game_turns = sum(g["turns"] for g in per_game)
    idle = branches["H"] + branches["W"]
    d1 = sum(g["d1"] for g in per_game)
    d2 = sum(g["d2"] for g in per_game)
    d3 = sum(g["d3"] for g in per_game)

    per_troll_share = {}
    for g in per_game:
        for uid, row in g["per_troll"].items():
            per_troll_share[(g["game"], uid)] = (row["idle"], row["turns"])
    worst = max(per_troll_share.items(),
                key=lambda kv: (kv[1][0] / kv[1][1] if kv[1][1] else 0.0, kv[0]),
                default=(None, (0, 0)))
    above = [{"game": k[0], "unit": k[1], "share_pct": round(100.0 * v[0] / v[1], 4)}
             for k, v in sorted(per_troll_share.items())
             if v[1] and 100.0 * v[0] / v[1] > IDLE_LINE]

    episodes = [e for g in per_game for e in g["episodes"]]
    f7 = collections.Counter(e["f7_end"]["label"] for e in episodes)
    classes = collections.Counter(e["class"] for e in episodes)
    mechs = collections.Counter(e["mech"] for e in episodes)
    block_kind = collections.Counter(e["block_kind"] for e in episodes)
    f7_share = 100.0 * f7["DANCER_PROGRESS"] / len(episodes) if episodes else None

    regressive = sum(g["rpos"]["regressive_turns"] for g in per_game)
    rpos_troll_turns = sum(g["rpos"]["troll_turns"] for g in per_game)
    moved = sum(g["rpos"]["moved_eligible_turns"] for g in per_game)
    progressive = sum(g["rpos"]["progressive_turns"] for g in per_game)
    equal = sum(g["rpos"]["equal_turns"] for g in per_game)
    poisoned = sum(g["rpos"]["poison_regressive_turns"] for g in per_game)
    fallback_rows = sum(g["rpos"]["fallback_rows"] for g in per_game)
    regressive_nf = sum(g["rpos"]["regressive_turns_no_fallback"] for g in per_game)
    rate = 1000.0 * regressive / rpos_troll_turns if rpos_troll_turns else None

    cross = collections.Counter()
    for g in per_game:
        cross.update(g["crosswalk"])
    both, rp_only, rr_only = cross["both"], cross["r_pos_only"], cross["r_eq_R_only"]
    union = both + rp_only + rr_only

    scope_active = sum(1 for g in per_game if g["scope_active"])
    holds_in_inactive = sum(g["branches"].get("H", 0) for g in per_game if not g["scope_active"])
    hold_runs = sum(g["hold_runs"] for g in per_game)
    hold_runs_prog = sum(g["hold_runs_with_progress"] for g in per_game)
    stall_games = sum(1 for g in per_game if g["long_stall"]["long_stall"])

    baseline = json.loads(BASELINE.read_text())
    champ = None
    if args.champion_games and args.champion_manifest:
        champ = champion_stalls(args.champion_games, args.champion_manifest)

    idle_share = 100.0 * idle / troll_turns if troll_turns else None
    stall_share = 100.0 * stall_games / games if games else None
    kills = {
        "idle_with_work_share_pct": {"value": round(idle_share, 4), "line": IDLE_LINE,
                                     "result": "KILL" if idle_share > IDLE_LINE else "PASS"},
        "D-3 own-troll contention": {"value": d3, "line": 0,
                                     "result": "KILL" if d3 > 0 else "PASS"},
        "long_stall_share_pct": {
            "value": round(stall_share, 4) if stall_share is not None else None,
            "champion": champ,
            "result": ("NOT MEASURED" if champ is None else
                       "KILL" if stall_share > champ["long_stall_share_pct"] else "PASS")},
    }
    clause_a = {"f7_dancer_progress": f7["DANCER_PROGRESS"], "episodes": len(episodes),
                "share_pct": round(f7_share, 4) if f7_share is not None else None,
                "bar_pct": round(CLAUSE_A_BAR, 4),
                "v3_instrument_reference": "52 of 80",
                "hold_runs": hold_runs, "hold_runs_with_progress": hold_runs_prog,
                "result": ("NOT MEASURED (no D-1 episode in the read)" if not episodes
                           else "PASS" if f7_share >= CLAUSE_A_BAR else "FAIL")}
    clause_b = {"regressive_turns": regressive, "own_troll_turns": rpos_troll_turns,
                "rate_per_1000_troll_turns": round(rate, 4) if rate is not None else None,
                "bar": CLAUSE_B_BAR,
                "v3_baseline_rate": baseline["rate_per_1000_troll_turns"],
                "reduction_pct": (round(100.0 * (1 - rate / baseline["rate_per_1000_troll_turns"]),
                                        4) if rate is not None else None),
                "r_eq_R_turns": branches["R"],
                "r_eq_R_per_1000_troll_turns": round(1000.0 * branches["R"] / troll_turns, 4)
                                               if troll_turns else None,
                "result": "PASS" if rate is not None and rate <= CLAUSE_B_BAR else "FAIL"}

    result = {
        "task": "20260825-dance-cure-candidate-1-hold",
        "gate": "G-2",
        "package": {"path": str(args.games), "sha256": digest, "agent_id": args.agent,
                    "arm_sha256": ARM_SHA256,
                    "handoff": "coordination/messages/local_claude_1/20260825T113500Z-"
                               "20260825-dance-cure-candidate-1-hold-handoff.md",
                    "games_decoded": games, "games_refused": len(refusals)},
        "totals": {"games": games, "game_turns": game_turns, "own_troll_turns": troll_turns,
                   "branches": dict(branches), "d1_episodes": d1, "d2": d2, "d3": d3,
                   "d1_games": sum(1 for g in per_game if g["d1"]),
                   "d1_per_1000_game_turns": round(1000.0 * d1 / game_turns, 4)
                                             if game_turns else None},
        "clause_a": clause_a,
        "clause_b": clause_b,
        "kill_rules": kills,
        "scope": {"scope_active_games": scope_active, "games": games,
                  "scope_active_share_pct": round(100.0 * scope_active / games, 4)
                                            if games else None,
                  "holds_in_scope_inactive_games": holds_in_inactive,
                  "control": "K-S: the hold is inert for the whole game where the scope is "
                             "inactive, so any H there is a defect",
                  "result": "PASS" if holds_in_inactive == 0 else "FAIL"},
        "crosswalk_r_pos_vs_r_eq_R": {
            "both": both, "r_pos_only": rp_only, "r_eq_R_only": rr_only,
            "neither": cross["neither"],
            "r_pos_ineligible_rows_with_r_eq_R": cross["r_pos_ineligible_rR"],
            "r_pos_ineligible_rows_without": cross["r_pos_ineligible_not_rR"],
            "jaccard_agreement_pct": round(100.0 * both / union, 4) if union else None,
            "note": "published as a finding about the instrument; clause (b) is graded R_pos on "
                    "both sides and never on this agreement",
        },
        "idle": {"turns": idle, "share_pct": round(idle_share, 4) if idle_share else None,
                 "hold_share_pct": round(100.0 * branches["H"] / troll_turns, 4)
                                   if troll_turns else None,
                 "wait_share_pct": round(100.0 * branches["W"] / troll_turns, 4)
                                   if troll_turns else None,
                 "trolls": len(per_troll_share),
                 "worst_troll": {"game": worst[0][0] if worst[0] else None,
                                 "unit": worst[0][1] if worst[0] else None,
                                 "idle": worst[1][0], "turns": worst[1][1],
                                 "share_pct": round(100.0 * worst[1][0] / worst[1][1], 4)
                                              if worst[1][1] else None},
                 "trolls_above_the_line": above,
                 "longest_hold_b": max((g["longest_hold_b"] for g in per_game), default=0)},
        "controls": {
            "K-E exhaustiveness": {
                "moved_eligible": moved, "progressive": progressive, "equal": equal,
                "regressive": regressive,
                "result": "PASS" if progressive + equal + regressive == moved else "FAIL"},
            "K-F manhattan fallback": {
                "rows_needing_it": fallback_rows,
                "regressive_depending_on_it": regressive - regressive_nf,
                "regressive_without_it": regressive_nf,
                "result": "FIRES" if fallback_rows else "INERT"},
            "K-P poison target": {
                "poisoned": poisoned, "true": regressive,
                "ratio": round(poisoned / regressive, 3) if regressive else None,
                "result": ("PASS" if regressive and poisoned > 2 * regressive
                           else "FAIL" if regressive else "N/A")},
            "K-D decode": {
                "own_rows_decoded": troll_turns,
                "games_refused": len(refusals),
                "opponent_narrate_turns": sum(g["opponent_narrate_turns"] for g in per_game),
                "longest_command_line_chars": max((g["longest_command_line_chars"]
                                                   for g in per_game), default=0),
                "line_budget": 2000,
                "result": "PASS" if not refusals else "FAIL"},
            "K-V v4 resolver invariants": {
                "pz_max": max((g["pz_max"] for g in per_game), default=0),
                "stale_protections": sum(g["sp_total"] for g in per_game),
                "w_collisions": sum(g["wc_total"] for g in per_game)},
        },
        "f7": dict(f7), "classes": dict(classes), "mech": dict(mechs),
        "d1_block_kind_by_r": dict(block_kind),
        "long_stall": {"games": stall_games, "share_pct": round(stall_share, 4)
                       if stall_share is not None else None, "champion": champ,
                       "window": STALL_WINDOW},
        "refusals": refusals,
        "per_game": per_game,
    }
    verdicts = [clause_a["result"], clause_b["result"]] + [k["result"] for k in kills.values()]
    result["verdict"] = ("KILL" if any(v == "KILL" for v in verdicts)
                         else "FAIL" if any(v == "FAIL" for v in verdicts)
                         else "PASS")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    print("package        %s  %d games decoded, %d refused" % (digest[:12], games, len(refusals)))
    print("branches       %s over %d own troll-turns"
          % (dict(sorted(branches.items())), troll_turns))
    print("D-1 %d episodes in %d games; D-2 %d; D-3 %d"
          % (d1, result["totals"]["d1_games"], d2, d3))
    print("clause (a)     F7 DANCER_PROGRESS %s -> %s"
          % (clause_a["share_pct"], clause_a["result"]))
    print("clause (b)     R_pos %s per 1,000 troll-turns vs bar %s (v3 %s) -> %s"
          % (clause_b["rate_per_1000_troll_turns"], CLAUSE_B_BAR,
             clause_b["v3_baseline_rate"], clause_b["result"]))
    for name, row in kills.items():
        print("kill %-28s %s -> %s" % (name, row["value"], row["result"]))
    print("scope active   %s of %d games; holds where inert: %d -> %s"
          % (scope_active, games, holds_in_inactive, result["scope"]["result"]))
    print("crosswalk      both %d, R_pos-only %d, r=R-only %d (agreement %s %%)"
          % (both, rp_only, rr_only, result["crosswalk_r_pos_vs_r_eq_R"]["jaccard_agreement_pct"]))
    print("VERDICT        %s" % result["verdict"])
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
