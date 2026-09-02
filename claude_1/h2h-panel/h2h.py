#!/usr/bin/env python3
"""The head-to-head panel: two compiled single-file bots against each other on real maps.

Plain words for the owner
-------------------------
The July bench (`local_claude_1/nn-bot/bench.py`) plays ONE compiled bot against a Python policy.
Track P needs two compiled bots against each other: a candidate (the port of norxondor_gorgonax)
against the champion of record, on real maps, on both seats, so that every map is a paired
observation (the same map, the same start inventory, the candidate once on each seat). This
driver does exactly that and nothing else:

  * the referee is the July Python referee (`fuzz_panel.FuzzReferee`), one `engine.rs::step`
    transition a turn (`_execute`), the same one the bench and the network gates run on;
  * each bot is a subprocess reading the protocol on its own seat (`nn_runtime.SeatRendering`:
    the reader is always "player 0", so the seat-1 bot is shown the exchanged board);
  * the game ends by the referee's stall rule or at 300 turns, as on the ladder;
  * the rows come out in the shape `local_claude_1/nn-bot/gate1.py` reads (`map_hash`,
    `policy_seat`, `policy_won`, `policy_score`, `bot_score`, and the three fault totals), so
    the frozen clustered bootstrap reads two of these files as treatment and control unchanged.

Vocabulary, kept from the bench so the readers need no change: the **policy** is the bot under
test (`--policy`, the candidate); the **bot** is its opponent (`--bot`, the champion).
`policy_seat` is the seat the candidate sits on; `policy_won` is a strict win (a tie is not).

The one thing that had to be new: the bench's `apply_two` raises when the seat-1 line has a
command error, because that seat was the bench's own policy and an error there was a bug in the
instrument. Here both lines are bot output, so `apply_pair` parses both, counts errors on both,
and raises on neither; a bot that emits an illegal command is reported, never crashes the panel.

Reading
-------
Besides the rows the report carries a paired reading: per map, the candidate's win indicator and
score margin averaged over its two seats, then the same clustered bootstrap over maps that
`gate1.py` uses over cells (10,000 draws, seed 1). A map carries both seats in every draw, so the
two seats of one map are never treated as independent games.

Use
---
    python3 claude_1/h2h-panel/h2h.py --policy cgauto/submissions/candidate-X.rs \
        --bot cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs \
        --panel claude_1/h2h-panel/panel-200-seed1.jsonl --jobs 4 --out results/X-vs-champion.json
    python3 claude_1/h2h-panel/h2h.py --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import os
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "local_claude_1" / "nn-bot"))

import bench                            # noqa: E402  (brings fuzz_panel, semantic_harness, nn_runtime)
import gate1                            # noqa: E402
import nn_runtime as nr                 # noqa: E402
import semantic_harness as sh           # noqa: E402

CHAMPION = REPO / "cgauto" / "submissions" / "candidate-champion-denial-off-v6-instrument.rs"
PANEL = HERE / "panel-200-seed1.jsonl"
TURNS = bench.TURNS
BOOTSTRAP_DRAWS = 10000
BOOTSTRAP_SEED = 1


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    try:
        return str(Path(path).resolve().relative_to(REPO))
    except ValueError:
        return str(path)


# --------------------------------------------------------------------------- the symmetric turn

def apply_pair(ref, line0: str, line1: str) -> tuple[int, int]:
    """Both seats' command lines as ONE `engine.rs::step` transition, errors counted on both.

    Returns the number of command errors found on each line. Seat 0's errors go where the
    referee keeps them (`error_counts`, `command_errors`); seat 1's go to the same shape under
    `seat1_error_counts` / `seat1_command_errors`, added here because the referee has no place
    for an opponent that is an untrusted bot.
    """
    p0 = ref.parse_commands(line0, ref.turn)
    ref._retain(p0.errors, line0)
    p1 = ref.parse_commands(line1, ref.turn)
    if not hasattr(ref, "seat1_error_counts"):
        ref.seat1_error_counts, ref.seat1_command_errors = {}, []
    for err in p1.errors:
        ref.seat1_error_counts[err["kind"]] = ref.seat1_error_counts.get(err["kind"], 0) + 1
        ref.seat1_command_errors.append(err)
    ref.opponent_commands.append(line1)
    ref._execute(p0, p1)
    ref.turn += 1
    return len(p0.errors), len(p1.errors)


def play(rec, draw, policy_bin: Path, bot_bin: Path, policy_seat: int, turns: int = TURNS,
         keep_replay: bool = False) -> dict:
    """One game on `rec` with start inventory `draw`; the policy on `policy_seat`."""
    if policy_seat not in (0, 1):
        raise ValueError(f"policy_seat {policy_seat} is not 0 or 1")
    bot_seat = 1 - policy_seat
    ref = bench.make_referee(rec, draw)
    renderings = {0: nr.SeatRendering(0), 1: nr.SeatRendering(1)}
    binaries = {policy_seat: policy_bin, bot_seat: bot_bin}
    procs = {seat: bench.BotProcess(binaries[seat], renderings[seat].map_header(ref))
             for seat in (0, 1)}
    replay = []
    errors = {0: 0, 1: 0}
    turns_until_end = 0
    ended_turn, ended_reason = turns, "turn_limit"
    try:
        for turn in range(1, turns + 1):
            lines = {seat: procs[seat].turn(renderings[seat].turn_text(ref)) for seat in (0, 1)}
            if keep_replay:
                replay.append({"turn": turn, "seat0": lines[0], "seat1": lines[1],
                               "score": [bench.score_of(ref.inv), bench.score_of(ref.opp_inv)]})
            e0, e1 = apply_pair(ref, lines[0], lines[1])
            errors[0] += e0
            errors[1] += e1
            ref.grow()
            stalled, turns_until_end, reason = nr.stall_check(ref, turns_until_end)
            if stalled:
                ended_turn, ended_reason = turn, reason
                break
    finally:
        for proc in procs.values():
            proc.close()
    inv_of = (ref.inv, ref.opp_inv)
    policy_score = bench.score_of(inv_of[policy_seat])
    bot_score = bench.score_of(inv_of[bot_seat])
    trains = {seat: [{"turn": e["turn"], "talents": e["talents"], "spawned": e["spawned"]}
                     for e in ref.train_events if e["player"] == seat] for seat in (0, 1)}
    trolls = {seat: sum(1 for u in ref.units.values() if u["player"] == seat) for seat in (0, 1)}
    seat_errors = {0: dict(ref.error_counts), 1: dict(getattr(ref, "seat1_error_counts", {}))}
    return {
        "map_hash": rec["map_hash"],
        "start_inventory": list(draw),
        "policy_seat": policy_seat,
        "turns": ended_turn,
        "ended_reason": ended_reason,
        "policy_score": policy_score,
        "bot_score": bot_score,
        "policy_won": policy_score > bot_score,
        "tie": policy_score == bot_score,
        "policy_trains": trains[policy_seat],
        "bot_trains": trains[bot_seat],
        "policy_trolls": trolls[policy_seat],
        "bot_trolls": trolls[bot_seat],
        "policy_timeouts": procs[policy_seat].timeouts,
        "bot_timeouts": procs[bot_seat].timeouts,
        "timeouts": procs[policy_seat].timeouts + procs[bot_seat].timeouts,
        "policy_command_errors": errors[policy_seat],
        "bot_command_errors": errors[bot_seat],
        "policy_command_error_counts": seat_errors[policy_seat],
        "bot_command_error_counts": seat_errors[bot_seat],
        "replay": replay,
    }


# --------------------------------------------------------------------------- the reading

def paired_reading(rows: list[dict], draws: int = BOOTSTRAP_DRAWS, seed: int = BOOTSTRAP_SEED) -> dict:
    """Per map: the candidate's win indicator and margin averaged over its seats; then the
    clustered bootstrap over maps (`gate1.clustered_bootstrap`, the gates' own)."""
    by_map: dict[str, list[dict]] = {}
    for r in rows:
        by_map.setdefault(r["map_hash"], []).append(r)
    win_per_map = {m: sum(1.0 if r["policy_won"] else 0.0 for r in rs) / len(rs)
                   for m, rs in by_map.items()}
    margin_per_map = {m: sum(r["policy_score"] - r["bot_score"] for r in rs) / len(rs)
                      for m, rs in by_map.items()}
    w_point, w_lo, w_hi = gate1.clustered_bootstrap(win_per_map, draws, seed)
    m_point, m_lo, m_hi = gate1.clustered_bootstrap(margin_per_map, draws, seed)
    both_seats = sum(1 for rs in by_map.values() if all(r["policy_won"] for r in rs))
    neither = sum(1 for rs in by_map.values() if not any(r["policy_won"] for r in rs))
    return {
        "unit": "map (both seats carried together)",
        "maps": len(by_map),
        "games": len(rows),
        "wins": sum(1 for r in rows if r["policy_won"]),
        "ties": sum(1 for r in rows if r["tie"]),
        "losses": sum(1 for r in rows if not r["policy_won"] and not r["tie"]),
        "win_rate": round(w_point, 4),
        "win_rate_interval_95": [round(w_lo, 4), round(w_hi, 4)],
        "win_rate_interval_above_half": bool(w_lo > 0.5),
        "win_rate_interval_below_half": bool(w_hi < 0.5),
        "margin_mean": round(m_point, 2),
        "margin_interval_95": [round(m_lo, 2), round(m_hi, 2)],
        "maps_won_on_both_seats": both_seats,
        "maps_won_on_neither_seat": neither,
        "bootstrap": {"draws": draws, "seed": seed},
    }


# --------------------------------------------------------------------------- the schedule

_WORKER: dict = {}


def _init_worker(policy_bin: str, bot_bin: str, turns: int, keep_replay: bool) -> None:
    _WORKER.update(policy_bin=Path(policy_bin), bot_bin=Path(bot_bin), turns=turns,
                   keep_replay=keep_replay)


def _run_one(item) -> tuple[int, dict]:
    index, rec, draw, seat = item
    row = play(rec, draw, _WORKER["policy_bin"], _WORKER["bot_bin"], seat,
               _WORKER["turns"], _WORKER["keep_replay"])
    return index, row


def load_panel(path: Path, limit: int = 0) -> list[tuple[dict, list]]:
    plan = []
    with open(path) as fh:
        for line in fh:
            if line.strip():
                item = json.loads(line)
                plan.append((item["rec"], item["draw"]))
    return plan[:limit] if limit else plan


def run_panel(policy_src: Path, bot_src: Path, panel: Path, *, seats=(0, 1), limit: int = 0,
              jobs: int = 1, turns: int = TURNS, replays: Path | None = None,
              progress=None) -> dict:
    plan = load_panel(panel, limit)
    schedule = [(i, rec, draw, seat) for i, ((rec, draw), seat)
                in enumerate((p, s) for p in plan for s in seats)]
    policy_text, bot_text = policy_src.read_text(), bot_src.read_text()
    t0 = time.time()
    rows: list[dict | None] = [None] * len(schedule)
    with tempfile.TemporaryDirectory(prefix="h2h-") as wd:
        policy_bin, bot_bin = Path(wd) / "policy.bin", Path(wd) / "bot.bin"
        sh.compile_text(policy_text, policy_bin, crate="h2h_policy")
        sh.compile_text(bot_text, bot_bin, crate="h2h_bot")
        compiled = time.time()
        keep = replays is not None
        replay_fh = open(replays, "w") if keep else None
        try:
            if jobs <= 1:
                _init_worker(str(policy_bin), str(bot_bin), turns, keep)
                results = map(_run_one, schedule)
            else:
                ctx = mp.get_context("fork")
                pool = ctx.Pool(jobs, initializer=_init_worker,
                                initargs=(str(policy_bin), str(bot_bin), turns, keep))
                results = pool.imap_unordered(_run_one, schedule)
            done = 0
            for index, row in results:
                if replay_fh is not None:
                    replay_fh.write(json.dumps({"map_hash": row["map_hash"],
                                                "policy_seat": row["policy_seat"],
                                                "turns": row["replay"]}) + "\n")
                row = dict(row)
                row.pop("replay")
                rows[index] = row
                done += 1
                if progress:
                    progress(done, len(schedule), row)
            if jobs > 1:
                pool.close()
                pool.join()
        finally:
            if replay_fh is not None:
                replay_fh.close()
    wall = time.time() - t0
    out_rows = [r for r in rows if r is not None]
    n = len(out_rows)
    report = {
        "instrument": "h2h.py -- two compiled single-file bots, July Python referee "
                      "(fuzz_panel.FuzzReferee, one engine.rs::step a turn), both seats, "
                      "paired by map",
        "policy": rel(policy_src), "policy_sha256": sha_text(policy_text),
        "bot": rel(bot_src), "bot_sha256": sha_text(bot_text),
        "panel": rel(panel), "panel_sha256": sha_file(panel),
        "maps_played": len(plan), "seats": list(seats), "turns": turns, "games": n,
        "policy_wins": sum(1 for r in out_rows if r["policy_won"]),
        "wins_by_seat": {str(s): sum(1 for r in out_rows if r["policy_seat"] == s and r["policy_won"])
                         for s in seats},
        "games_by_seat": {str(s): sum(1 for r in out_rows if r["policy_seat"] == s) for s in seats},
        "policy_score_mean": round(sum(r["policy_score"] for r in out_rows) / n, 1) if n else None,
        "bot_score_mean": round(sum(r["bot_score"] for r in out_rows) / n, 1) if n else None,
        # the three totals gate1.Bench reads as execution faults; any nonzero = not cleanly played
        "illegal_commands_total": sum(r["policy_command_errors"] for r in out_rows),
        "referee_errors_total": sum(r["bot_command_errors"] for r in out_rows),
        "timeouts_total": sum(r["timeouts"] for r in out_rows),
        "fault_meaning": {"illegal_commands_total": "command errors on the policy's lines",
                          "referee_errors_total": "command errors on the bot's lines",
                          "timeouts_total": "turns past 5 s on either seat"},
        "ended_reasons": {reason: sum(1 for r in out_rows if r["ended_reason"] == reason)
                          for reason in sorted({r["ended_reason"] for r in out_rows})},
        "reading": paired_reading(out_rows) if n else None,
        "compile_seconds": round(compiled - t0, 1),
        "wall_seconds": round(wall, 1),
        "games_per_hour": round(3600 * n / (wall - (compiled - t0)), 1) if n and wall > compiled - t0 else None,
        "jobs": jobs,
        "rows": out_rows,
    }
    return report


# --------------------------------------------------------------------------- self-test

def self_test() -> int:
    """The checks that need no compiled bot; the ones that do are in test_h2h.py."""
    import fuzz_panel as fp  # noqa: F401
    failures = 0

    def check(label, ok):
        nonlocal failures
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")
        failures += 0 if ok else 1

    rec = bench._test_map()
    ref = bench.make_referee(rec, [5, 5, 5, 5, 5, 0])
    e0, e1 = apply_pair(ref, "WAIT", "BOGUS 1")
    check("apply_pair counts a seat-1 error instead of raising", (e0, e1) == (0, 1)
          and ref.seat1_error_counts and not ref.error_counts)
    e0, e1 = apply_pair(ref, "FLY 0", "WAIT")
    check("apply_pair counts a seat-0 error on the referee", (e0, e1) == (1, 0)
          and sum(ref.error_counts.values()) == 1)
    check("the turn advanced twice (the referee starts at 1)", ref.turn == 3)

    rows = [{"map_hash": f"m{i}", "policy_seat": s, "policy_won": True, "tie": False,
             "policy_score": 10, "bot_score": 0} for i in range(20) for s in (0, 1)]
    r = paired_reading(rows, draws=200)
    check("all wins -> interval above one half", r["win_rate_interval_above_half"]
          and r["maps"] == 20 and r["games"] == 40)
    rows = [{"map_hash": f"m{i}", "policy_seat": s, "policy_won": (i + s) % 2 == 0, "tie": False,
             "policy_score": 5 if (i + s) % 2 == 0 else 0, "bot_score": 0 if (i + s) % 2 == 0 else 5}
            for i in range(20) for s in (0, 1)]
    r = paired_reading(rows, draws=200)
    check("split seats -> exactly one half, zero-width interval", r["win_rate"] == 0.5
          and r["win_rate_interval_95"] == [0.5, 0.5] and r["margin_mean"] == 0.0)
    print(f"\n  {'PASS' if not failures else 'FAIL'}  {failures} failure(s)")
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--policy", type=Path, default=CHAMPION, help="the bot under test (single .rs file)")
    ap.add_argument("--bot", type=Path, default=CHAMPION, help="its opponent (single .rs file)")
    ap.add_argument("--panel", type=Path, default=PANEL,
                    help="map records with draws (smoke.py --write-records format)")
    ap.add_argument("--maps", type=int, default=0, help="play only the first N maps (0 = all)")
    ap.add_argument("--seats", default="0,1", help="the policy's seats, e.g. 0,1 or 1")
    ap.add_argument("--turns", type=int, default=TURNS)
    ap.add_argument("--jobs", type=int, default=max(1, os.cpu_count() or 1))
    ap.add_argument("--out", type=Path, default=HERE / "results" / "h2h.json")
    ap.add_argument("--replays", type=Path, default=None, help="keep every command line here (jsonl)")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    seats = tuple(int(s) for s in args.seats.split(","))

    def progress(done, total, row):
        if not args.quiet:
            print(f"  {done:>4}/{total} {row['map_hash']} seat {row['policy_seat']}  policy "
                  f"{row['policy_score']:>4} vs bot {row['bot_score']:>4}  "
                  f"{'POLICY' if row['policy_won'] else 'tie   ' if row['tie'] else 'bot   '}  "
                  f"t{row['turns']} {row['ended_reason']}", flush=True)

    print(f"policy {args.policy.name}\nbot    {args.bot.name}\npanel  {args.panel} "
          f"x seats {list(seats)}  jobs {args.jobs}", flush=True)
    report = run_panel(args.policy, args.bot, args.panel, seats=seats, limit=args.maps,
                       jobs=args.jobs, turns=args.turns, replays=args.replays, progress=progress)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    r = report["reading"]
    print(f"\n| games | policy wins | ties | win rate [95%] | margin [95%] | faults (policy/bot/timeouts) | games/h |\n"
          f"|---|---|---|---|---|---|---|\n"
          f"| {report['games']} | {report['policy_wins']} | {r['ties']} | {r['win_rate']} "
          f"{r['win_rate_interval_95']} | {r['margin_mean']} {r['margin_interval_95']} | "
          f"{report['illegal_commands_total']}/{report['referee_errors_total']}/{report['timeouts_total']} | "
          f"{report['games_per_hour']} |\n-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
