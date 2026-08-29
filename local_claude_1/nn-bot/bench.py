#!/usr/bin/env python3
"""The bench for the neural-network bot (Track N, Phase 2, card
`coordination/tasks/20260829-nn-bot-way-b-dataset.md`).

One seat is played by a **Python policy** (the clone, later; a random-legal policy today), the
other by a **compiled single-file bot** (the champion's actual submitted file), over the July
Python referee -- `claude_1/pipeline/fuzz_panel.py`'s `FuzzReferee`, which applies both players'
command lines as ONE `engine.rs::step` transition (`apply_two`). The compiled bot is seat 0
because the referee's `turn_text()` is seat 0's view, which is the protocol a real bot reads; the
Python policy is seat 1 and reads the referee's state directly, which is exactly what the plane
builder will consume.

This is the bench, not the training environment: it is the same referee, the same compile and the
same pipes the July gates used, so a number here is comparable with the smoke and panel numbers
already on file.

Per game it reports: both seats' score, who won, every TRAIN (talents, turn, seat), timeouts,
illegal commands (a command the mask says is not legal -- by construction zero for the random
policy; the number that matters once a network chooses), referee parse errors, and loops (a troll
that stands on one cell 30 turns with cargo it could deposit). Every game is saved turn by turn so
the owner can read it.

    # day-1 proof: the random-legal policy against the champion's file, 24 real maps
    python3 local_claude_1/nn-bot/bench.py --maps local_claude_1/third-troll/smoke-maps-seed0.jsonl

    # read one saved game turn by turn
    python3 local_claude_1/nn-bot/bench.py --read local_claude_1/nn-bot/results/bench-replays.jsonl --game 3

The policy interface (the clone drops in unchanged):

    class Policy:
        def plan(self, view) -> tuple[int, int, int, int] | None:   # TRAIN talents, or None
        def command(self, view, troll_id) -> str                    # one command for one troll

`view` is a `SeatView`: the board, both inventories, the trolls, and `legal(troll_id)` -- the same
legality this bench uses to count illegal commands, and the mask the network will be given.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import selectors
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for _p in ("claude_1/pipeline", "claude_1/banana-restoration-r2"):
    sys.path.insert(0, str(REPO / _p))

import fuzz_panel as fp             # noqa: E402
import semantic_harness as sh       # noqa: E402

CHAMPION = REPO / "cgauto" / "submissions" / "candidate-champion-denial-off-v6-instrument.rs"
MAPS = REPO / "local_claude_1" / "third-troll" / "smoke-maps-seed0.jsonl"
TURNS = 300
TURN_TIMEOUT_S = 5.0          # a real turn is milliseconds; this only catches a hung process
LOOP_TURNS = 30               # "a troll on one cell 30 turns with cargo it could deposit"
ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def rel(path: Path) -> str:
    """A repo-relative path when the file is in the repo, its own path otherwise."""
    try:
        return str(Path(path).resolve().relative_to(REPO))
    except ValueError:
        return str(path)


def score_of(inv) -> int:
    """The game's score: one point a fruit, four a wood (`WOOD_POINTS`, engine.rs)."""
    return sum(inv[0:4]) + fp.WOOD_POINTS * inv[5]


# --------------------------------------------------------------------------- the seat's view

class SeatView:
    """What a policy sees: one seat's board, read straight off the referee.

    Read-only by discipline (nothing here writes to the referee). `legal()` is the mask: every
    command the referee's own preconditions would let this troll's fragment do this turn, in the
    July action order (MOVE, HARVEST, CHOP, DROP, MINE, PLANT x4, PICK x4) -- the same order the
    network's 13-plane head decodes into (`rl_level1.rs:490-508`).
    """

    def __init__(self, ref, seat: int):
        self.ref = ref
        self.seat = seat
        self.turn = ref.turn

    # -- the board ---------------------------------------------------------
    @property
    def inv(self):
        return list(self.ref._inv_of(self.seat))

    @property
    def opp_inv(self):
        return list(self.ref._inv_of(1 - self.seat))

    @property
    def shack(self):
        return self.ref.shacks[self.seat]

    def trolls(self, seat=None):
        seat = self.seat if seat is None else seat
        return {uid: u for uid, u in sorted(self.ref.units.items()) if u["player"] == seat}

    @property
    def plants(self):
        return self.ref.plants

    def reachable(self, cell):
        """Cells this troll can path to at all (the engine's BFS over walkable cells)."""
        return self.ref._bfs_from([cell])

    # -- the mask ----------------------------------------------------------
    def legal(self, uid) -> list[str]:
        u = self.ref.units.get(uid)
        if u is None or u["player"] != self.seat:
            return []
        ref = self.ref
        cell = u["cell"]
        free = u["cap"] - sum(u["carry"])
        out = ["WAIT"]

        # MOVE: delineate's rule -- any walkable cell with a path from the troll.
        for target in sorted(ref.walk):
            if target in self.reachable(cell):
                out.append("MOVE %d %d %d" % (uid, target[0], target[1]))

        plant = ref.plants.get(cell)
        if plant is not None and plant["fruits"] > 0 and u["harvest"] >= 1 and free > 0:
            out.append("HARVEST %d" % uid)
        if plant is not None and u["chop"] > 0:
            out.append("CHOP %d" % uid)

        near_shack = ref._near_shack(u)
        if near_shack and sum(u["carry"]) > 0:
            out.append("DROP %d" % uid)
        if u["chop"] > 0 and free > 0 and any(
                fp._manhattan(cell, iron) == 1 for iron in ref.irons):
            out.append("MINE %d" % uid)
        if plant is None and cell in ref.walk:
            for kind in fp.PLANTABLE_KINDS:
                if u["carry"][fp.ITEM_INDEX[kind]] > 0:
                    out.append("PLANT %d %s" % (uid, kind))
        if near_shack and free > 0:
            inv = self.inv
            for kind in fp.PLANTABLE_KINDS:
                if inv[fp.ITEM_INDEX[kind]] > 0:
                    out.append("PICK %d %s" % (uid, kind))
        return out

    def affordable_plans(self) -> list[tuple]:
        """Every TRAIN this seat could pay for this turn (speed 1-3, carry 1-4, harvest 0-2,
        chop 0-3 -- the parent card's 144-entry plan space), plus the engine's own two
        conditions via `can_train`."""
        out = []
        for ms in range(1, 4):
            for cc in range(1, 5):
                for hp in range(0, 3):
                    for chop in range(0, 4):
                        talents = (ms, cc, hp, chop)
                        if self.ref.can_train(talents, self.seat) is None:
                            out.append(talents)
        return out


# --------------------------------------------------------------------------- policies

class RandomLegalPolicy:
    """The day-1 proof of the pipeline: every troll takes a uniformly random legal command, and a
    random affordable plan is trained with probability `--train-p` a turn. It will lose every
    game -- that is expected, and it is reported as a loss."""

    name = "random-legal"

    def __init__(self, seed: int = 0, train_p: float = 0.02):
        self.rng = random.Random(seed)
        self.train_p = train_p

    def plan(self, view: SeatView):
        if self.rng.random() >= self.train_p:
            return None
        plans = view.affordable_plans()
        return self.rng.choice(plans) if plans else None

    def command(self, view: SeatView, uid: int) -> str:
        legal = view.legal(uid)
        return self.rng.choice(legal) if legal else "WAIT"


# --------------------------------------------------------------------------- the game

def make_referee(rec, inventory):
    plants = {}
    for t in rec["trees0"]:
        plants[(t["x"], t["y"])] = {"kind": t["type"], "size": t["size"], "health": t["health"],
                                    "fruits": t["fruits"], "cd": t["cur_cd"]}
    p0, p1 = tuple(rec["shacks"]["p0"]), tuple(rec["shacks"]["p1"])
    units = {
        0: {"player": 0, "cell": p0, "speed": 1, "cap": 1, "harvest": 1, "chop": 1, "carry": [0] * 6},
        1: {"player": 1, "cell": p1, "speed": 1, "cap": 1, "harvest": 1, "chop": 1, "carry": [0] * 6},
    }
    # `profile` drives the referee's built-in scripted opponent, which this bench never uses:
    # both command lines are supplied by name through `apply_two`.
    ref = fp.FuzzReferee(rec["rows"], list(inventory), plants, units, "idle")
    ref.opp_inv = list(inventory)
    return ref


class BotProcess:
    """The compiled single-file bot on seat 0, over pipes, with a per-turn timeout."""

    def __init__(self, binary: Path, header: str):
        self.proc = subprocess.Popen([str(binary)], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, text=True, bufsize=1)
        self.sel = selectors.DefaultSelector()
        self.sel.register(self.proc.stdout, selectors.EVENT_READ)
        self.timeouts = 0
        self.proc.stdin.write(header)
        self.proc.stdin.flush()

    def turn(self, block: str) -> str:
        try:
            self.proc.stdin.write(block)
            self.proc.stdin.flush()
        except BrokenPipeError:
            return ""
        if not self.sel.select(TURN_TIMEOUT_S):
            self.timeouts += 1
            return ""
        line = self.proc.stdout.readline()
        return line.rstrip("\n") if line else ""

    def close(self):
        try:
            self.proc.stdin.close()
        except Exception:
            pass
        self.sel.close()
        try:
            self.proc.wait(timeout=5)
        except Exception:
            self.proc.kill()


def loop_runs(cells_by_turn, carried_by_turn) -> int:
    """The longest run of consecutive turns a troll stood on one cell while carrying something it
    could have banked. `cells_by_turn` and `carried_by_turn` are per-turn lists for one troll."""
    best = run = 0
    prev = None
    for cell, carrying in zip(cells_by_turn, carried_by_turn):
        if cell == prev and carrying:
            run += 1
            best = max(best, run)
        else:
            run = 0
        prev = cell
    return best


def play(rec, draw, binary: Path, policy, turns: int, keep_replay: bool):
    """One game: the compiled bot (seat 0) against the Python policy (seat 1)."""
    ref = make_referee(rec, draw)
    bot = BotProcess(binary, ref.map_header())
    seat = 1
    view = SeatView(ref, seat)
    illegal = []           # commands the policy proposed that the mask rejects
    policy_trains, replay = [], []
    tracks = {}            # troll id -> {"cells": [...], "carrying": [...]}
    policy_time = 0.0

    for turn in range(1, turns + 1):
        block = ref.turn_text()
        bot_line = bot.turn(block)

        t0 = time.perf_counter()
        view.turn = turn
        frags = []
        plan = policy.plan(view)
        if plan is not None:
            if ref.can_train(tuple(plan), seat) is None:
                frags.append("TRAIN %d %d %d %d" % tuple(plan))
                policy_trains.append({"turn": turn, "talents": list(plan)})
            else:
                illegal.append({"turn": turn, "command": "TRAIN %d %d %d %d" % tuple(plan),
                                "why": ref.can_train(tuple(plan), seat)})
        for uid in sorted(view.trolls()):
            cmd = policy.command(view, uid)
            if cmd == "WAIT" or not cmd:
                continue
            if cmd not in view.legal(uid):
                illegal.append({"turn": turn, "command": cmd, "why": "not in the mask"})
                continue
            frags.append(cmd)
        policy_time += time.perf_counter() - t0
        policy_line = ";".join(frags)

        for uid, u in view.trolls().items():
            tr = tracks.setdefault(uid, {"cells": [], "carrying": []})
            tr["cells"].append(tuple(u["cell"]))
            tr["carrying"].append(sum(u["carry"]) > 0)

        if keep_replay:
            replay.append({"turn": turn, "bot": bot_line, "policy": policy_line,
                           "score": [score_of(ref.inv), score_of(ref.opp_inv)]})
        ref.apply_two(bot_line, policy_line)
        ref.grow()

    bot.close()
    bot_trains = [{"turn": e["turn"], "talents": e["talents"], "spawned": e["spawned"]}
                  for e in ref.train_events if e["player"] == 0]
    policy_events = [{"turn": e["turn"], "talents": e["talents"], "spawned": e["spawned"]}
                     for e in ref.train_events if e["player"] == 1]
    loops = {str(uid): loop_runs(tr["cells"], tr["carrying"]) for uid, tr in tracks.items()}
    bot_score, policy_score = score_of(ref.inv), score_of(ref.opp_inv)
    return {
        "map_hash": rec["map_hash"],
        "start_inventory": list(draw),
        "turns": turns,
        "bot_score": bot_score,
        "policy_score": policy_score,
        "policy_won": policy_score > bot_score,
        "bot_trains": bot_trains,
        "policy_trains": policy_events,
        "policy_trains_requested": policy_trains,
        "policy_trolls": len(view.trolls()),
        "bot_trolls": len(view.trolls(0)),
        "timeouts": bot.timeouts,
        "illegal_commands": illegal,
        "referee_errors": dict(ref.error_counts),
        "loops": loops,
        "worst_loop": max(loops.values()) if loops else 0,
        "policy_seconds": round(policy_time, 2),
        "replay": replay,
    }


# --------------------------------------------------------------------------- the owner's read

def read_replay(path: Path, want: int) -> int:
    with open(path) as fh:
        for i, line in enumerate(fh, 1):
            game = json.loads(line)
            if want not in (0, i):
                continue
            print(f"game {i}  map {game['map_hash']}  bot {game['bot_score']} vs policy "
                  f"{game['policy_score']}  ({'policy won' if game['policy_won'] else 'bot won'})")
            for t in game["replay"]:
                print(f"  t{t['turn']:>3}  bot: {t['bot'][:70]:<70}  policy: {t['policy'][:60]}")
            print()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--maps", type=Path, default=MAPS,
                    help="a map slice in smoke.py's --write-records format")
    ap.add_argument("--bot", type=Path, default=CHAMPION, help="the compiled seat's single file")
    ap.add_argument("--turns", type=int, default=TURNS)
    ap.add_argument("--games", type=int, default=0, help="0 = every map in the slice")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--policy", default="random-legal", choices=["random-legal"])
    ap.add_argument("--train-p", type=float, default=0.02)
    ap.add_argument("--out", type=Path, default=HERE / "results" / "bench.json")
    ap.add_argument("--replays", type=Path, default=HERE / "results" / "bench-replays.jsonl")
    ap.add_argument("--no-replays", action="store_true")
    ap.add_argument("--read", type=Path, default=None, help="print a saved replay file")
    ap.add_argument("--game", type=int, default=0, help="with --read: one game (1-based), 0 = all")
    args = ap.parse_args()

    if args.read is not None:
        return read_replay(args.read, args.game)

    plan = []
    with open(args.maps) as fh:
        for line in fh:
            item = json.loads(line)
            plan.append((item["rec"], item["draw"]))
    if args.games:
        plan = plan[:args.games]
    bot_text = args.bot.read_text()
    print(f"maps {len(plan)} from {args.maps}\nseat 0 (compiled) {args.bot.name} sha "
          f"{sha(bot_text)[:16]}\nseat 1 (python)   {args.policy} seed {args.seed}\n")

    rows = []
    with tempfile.TemporaryDirectory(prefix="nn-bench-") as wd:
        binary = Path(wd) / "bot.bin"
        sh.compile_text(bot_text, binary, crate="nn_bench_bot")
        if not args.no_replays:
            args.replays.parent.mkdir(parents=True, exist_ok=True)
        replay_fh = None if args.no_replays else open(args.replays, "w")
        for i, (rec, draw) in enumerate(plan):
            policy = RandomLegalPolicy(seed=args.seed + i, train_p=args.train_p)
            row = play(rec, draw, binary, policy, args.turns, keep_replay=replay_fh is not None)
            if replay_fh is not None:
                replay_fh.write(json.dumps(row, sort_keys=True) + "\n")
            row.pop("replay", None)
            rows.append(row)
            t0 = row["policy_trains"][0]["talents"] if row["policy_trains"] else None
            b0 = row["bot_trains"][0]["talents"] if row["bot_trains"] else None
            print(f"  {i+1:>2}/{len(plan)} {row['map_hash']}  bot {row['bot_score']:>4} vs policy "
                  f"{row['policy_score']:>4}  {'POLICY' if row['policy_won'] else 'bot   '}  "
                  f"bot trolls {row['bot_trolls']} (1st train {b0}), policy trolls "
                  f"{row['policy_trolls']} (1st {t0})  illegal {len(row['illegal_commands'])}  "
                  f"timeouts {row['timeouts']}  worst loop {row['worst_loop']}  "
                  f"referee errors {sum(row['referee_errors'].values())}")
        if replay_fh is not None:
            replay_fh.close()

    n = len(rows)
    wins = sum(r["policy_won"] for r in rows)
    report = {
        "what": "bench: one seat a Python policy, one seat a compiled single-file bot, over the "
                "July Python referee (fuzz_panel.FuzzReferee.apply_two)",
        "bot": rel(args.bot), "bot_sha256": sha(bot_text),
        "policy": args.policy, "seed": args.seed, "train_p": args.train_p,
        "maps": rel(args.maps), "games": n, "turns": args.turns,
        "policy_wins": wins,
        "policy_score_mean": round(sum(r["policy_score"] for r in rows) / n, 1),
        "bot_score_mean": round(sum(r["bot_score"] for r in rows) / n, 1),
        "illegal_commands_total": sum(len(r["illegal_commands"]) for r in rows),
        "timeouts_total": sum(r["timeouts"] for r in rows),
        "referee_errors_total": sum(sum(r["referee_errors"].values()) for r in rows),
        "games_with_a_loop": sum(1 for r in rows if r["worst_loop"] >= LOOP_TURNS),
        "policy_seconds_total": round(sum(r["policy_seconds"] for r in rows), 1),
        "replays": None if args.no_replays else rel(args.replays),
        "rows": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    print(f"\n| games | policy wins | policy score (mean) | bot score (mean) | illegal | timeouts "
          f"| referee errors | games with a loop |")
    print(f"| {n} | {wins} | {report['policy_score_mean']} | {report['bot_score_mean']} | "
          f"{report['illegal_commands_total']} | {report['timeouts_total']} | "
          f"{report['referee_errors_total']} | {report['games_with_a_loop']} |")
    print(f"\nreport -> {args.out}"
          + ("" if args.no_replays else f"; replays -> {args.replays} "
                                        f"(read: --read {args.replays} --game 1)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
