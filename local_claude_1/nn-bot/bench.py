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

**Amended 2026-08-30 (day 6-7) for the four amendments the parent card carries after chatgpt_1's
bench audit -- before a trained clone is judged, the bench must present the network exactly what
the environment presents.**

1. **The planes and the masks come from the compiled runtime.**  A tensor policy is shown, for
   every mini-step, the observation, the 3,146-entry spatial mask and the 400-entry plan mask that
   `tf_full_obs_from_state` builds -- through `nn_runtime.PlaneBuilder`, the same call the
   environment and the clone's trainer make.  There is no bench-side plane or mask code, and the
   staged prefix of the turn's earlier trolls is passed in as the environment stages it.
2. **The plan is a target; TRAIN is emitted by the environment's own dry run.**  Every in-range
   plan is legal (`nn_runtime`/`ENV-API.md`), and `nn_runtime.plan_trains` -- one adapter, shared
   -- clones the referee, prepends the TRAIN and runs the whole turn, so the purchase is billed
   against the post-MOVE/post-PICK bank with the shack occupancy the turn really produces.
3. **The game ends when the referee ends it.**  `nn_runtime.stall_check` runs
   `sim.engine.has_stalled` -- the port of `game::engine::has_stalled`, persistent counter and
   all -- after every turn, and the row records the ending turn and its reason.  The turn cap is
   the referee's 300, not the end condition.
4. **Both seats.**  `--both-seats` plays every map twice, the Python policy on seat 0 and on seat
   1.  The compiled bot always believes it is player 0 (the protocol has no seat field), so its
   view is rendered by `nn_runtime.SeatRendering`; that transformation is tested by `--self-test`,
   together with the runtime codec's own seat rotation.

The day-1 random-legal policy stays exactly what it was -- a proof of the pipes over the text
mask -- and `--policy random-mask` is the same proof over the amended tensor path, so the path a
network takes is exercised without a checkpoint.

The policy interfaces (the clone drops in unchanged):

    class TextPolicy:            # the day-1 proof
        def plan(self, view) -> tuple[int, int, int, int] | None:   # TRAIN talents, or None
        def command(self, view, troll_id) -> str                    # one command for one troll

    class TensorPolicy:          # the amended path: planes and masks from the compiled runtime
        def plan_index(self, obs: bytes, plan_mask: bytes) -> int
        def action_index(self, obs: bytes, mask: bytes) -> int

`view` is a `SeatView`: the board, both inventories, the trolls, and `legal(troll_id)` -- the same
legality the day-1 policy uses.
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

sys.path.insert(0, str(HERE))
import nn_runtime as nr             # noqa: E402

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


class RandomMaskPolicy:
    """The same proof of the pipes, over the amended path: uniform over the *runtime's* mask.

    It exists so that the tensor path -- planes, spatial mask, plan mask, the staged prefix, the
    decode back to command text -- is exercised on real maps without a trained checkpoint and
    without PyTorch.  Like the day-1 policy it will lose; that is reported as a loss.
    """

    name = "random-mask"

    def __init__(self, seed: int = 0, train_p: float = 0.02):
        self.rng = random.Random(seed)
        self.train_p = train_p

    def plan_index(self, obs: bytes, plan_mask: bytes) -> int:
        if self.rng.random() >= self.train_p:
            return 0                                  # "train nothing", always legal
        legal = [i for i, ok in enumerate(plan_mask) if ok and i != 0]
        return self.rng.choice(legal) if legal else 0

    def action_index(self, obs: bytes, mask: bytes) -> int:
        legal = [i for i, ok in enumerate(mask) if ok]
        if not legal:                                 # MOVE/current is the nonempty fallback
            raise RuntimeError("the runtime offered an empty mask")
        return self.rng.choice(legal)


class NetworkPolicy:
    """The clone: masked decoding over `SpatialActorCritic(plan_head=True)`.

    The checkpoint is loaded by `train_ppo_full.load_policy`, which is the loader that also
    refuses a foreign plan vocabulary -- so the bench cannot judge a network against a vocabulary
    it was not trained on.

    The **plan** head is decoded either by masked argmax or by a masked sample at a temperature
    (`--plan-decoding`): a clone fits a distribution, and its argmax can be a plan the teachers
    took a minority of the time even where they bought often.  Commands are argmax by default;
    `--command-decoding sample` draws them from the masked soft-max at the same temperature, the
    way the PPO trainer plays them (a policy trained by sampling can have a mode that is not its
    typical play -- the coordinator's question of 2026-08-30 17:3xZ).  Sampling draws from a
    generator reseeded per game, so a run at one `--seed` reproduces.
    """

    def __init__(self, checkpoint: Path, deterministic: bool = True,
                 plan_decoding: str = "argmax", temperature: float = 1.0, seed: int = 0,
                 command_decoding: str = "argmax"):
        import numpy as np                                        # noqa: PLC0415

        if plan_decoding not in ("argmax", "sample"):
            raise SystemExit(f"unknown --plan-decoding {plan_decoding!r}")
        if command_decoding not in ("argmax", "sample"):
            raise SystemExit(f"unknown --command-decoding {command_decoding!r}")
        if temperature <= 0:
            raise SystemExit("--plan-temperature must be positive")
        self.plan_decoding, self.temperature = plan_decoding, temperature
        self.command_decoding = command_decoding
        self.rng = np.random.default_rng(seed)
        import importlib.util                                     # noqa: PLC0415

        import torch                                              # noqa: PLC0415

        spec = importlib.util.spec_from_file_location(
            "train_ppo_full_for_bench", HERE / "train_ppo_full.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.torch = torch
        self.model, _ = module.load_policy(str(checkpoint), torch.device("cpu"))
        self.model.eval()
        self.name = (f"network:{Path(checkpoint).name}:{self.plan_decoding}"
                     + (":commands-sampled" if command_decoding == "sample" else ""))
        self.deterministic = deterministic

    def _forward(self, obs: bytes):
        import numpy as np                                        # noqa: PLC0415

        planes = np.frombuffer(obs, dtype=np.uint8).reshape(
            1, nr.OBS_CHANNELS, nr.GRID_H, nr.GRID_W).copy()
        with self.torch.no_grad():
            return self.model.forward_with_plan(self.torch.from_numpy(planes))

    def _argmax(self, logits, mask: bytes) -> int:
        import numpy as np                                        # noqa: PLC0415

        legal = self.torch.from_numpy(
            np.frombuffer(mask, dtype=np.uint8).copy()).bool().unsqueeze(0)
        masked = logits.masked_fill(~legal, self.torch.finfo(logits.dtype).min)
        return int(masked.argmax(1).item())

    def reseed(self, seed: int) -> None:
        """One generator per game, so the schedule's order cannot change a game's draws."""
        import numpy as np                                        # noqa: PLC0415

        self.rng = np.random.default_rng(seed)

    def _sample(self, logits, mask: bytes) -> int:
        """A draw from the masked soft-max at `self.temperature`; an illegal index cannot win."""
        import numpy as np                                        # noqa: PLC0415

        legal = np.frombuffer(mask, dtype=np.uint8).copy().astype(bool)
        if not legal.any():
            raise RuntimeError("the runtime offered an empty mask")
        scores = logits.detach().numpy().reshape(-1)[: legal.size].astype(np.float64)
        scores = scores / self.temperature
        scores[~legal] = -np.inf
        scores -= scores.max()
        weights = np.exp(scores)
        total = weights.sum()
        if not np.isfinite(total) or total <= 0:                  # every legal score underflowed
            return int(np.flatnonzero(legal)[0])
        return int(self.rng.choice(legal.size, p=weights / total))

    def plan_index(self, obs: bytes, plan_mask: bytes) -> int:
        _, plan_logits, _ = self._forward(obs)
        if self.plan_decoding == "sample":
            return self._sample(plan_logits, plan_mask)
        return self._argmax(plan_logits, plan_mask)

    def action_index(self, obs: bytes, mask: bytes) -> int:
        action_logits, _, _ = self._forward(obs)
        if self.command_decoding == "sample":
            return self._sample(action_logits, mask)
        return self._argmax(action_logits, mask)


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


def play(rec, draw, binary: Path, policy, turns: int, keep_replay: bool, *,
         policy_seat: int = 1, builder=None):
    """One game: the compiled bot against the Python policy, on the seat asked for.

    `policy_seat` is the referee seat the Python policy sits on (amendment 4); the compiled bot
    takes the other one and is shown its own view by `nn_runtime.SeatRendering`, because the
    protocol has no seat field and every single-file bot believes it is player 0.  A policy with
    `action_index` is a **tensor policy** and is driven the amended way -- the planes and both
    masks from the compiled runtime, one mini-step at a time, the earlier trolls staged; a policy
    with `command` is the day-1 text policy and is driven as it was.

    The game ends when `has_stalled` ends it or after `turns` turns, whichever is first
    (amendment 3), and the ending turn and reason are reported.
    """
    ref = make_referee(rec, draw)
    bot_seat = 1 - policy_seat
    rendering = nr.SeatRendering(bot_seat)
    bot = BotProcess(binary, rendering.map_header(ref))
    view = SeatView(ref, policy_seat)
    tensor = hasattr(policy, "action_index")
    if tensor and builder is None:
        raise ValueError("a tensor policy needs the compiled runtime (--library)")
    width, height = len(rec["rows"][0]), len(rec["rows"])

    illegal = []           # commands the policy proposed that the mask rejects
    policy_trains, replay = [], []
    plans_drawn = plans_refused = 0
    tracks = {}            # troll id -> {"cells": [...], "carrying": [...]}
    policy_time = 0.0
    turns_until_end = 0
    ended_turn, ended_reason = turns, "turn_limit"

    for turn in range(1, turns + 1):
        bot_line = bot.turn(rendering.turn_text(ref))

        t0 = time.perf_counter()
        view.turn = turn
        frags, staged, plan_index = [], [], 0
        if tensor:
            # PLAN first, exactly as the environment's mini-step machine runs the turn.
            state = nr.state_json_from_referee(ref, turn)
            obs, _, plan_mask = builder.observe(state, policy_seat, -1, nr.PHASE_PLAN, 0,
                                                want_mask=False, want_plan_mask=True)
            plan_index = policy.plan_index(obs, plan_mask)
            if not plan_mask[plan_index]:
                illegal.append({"turn": turn, "command": f"PLAN {plan_index}",
                                "why": "outside the plan mask"})
                plan_index = 0
            for uid in sorted(view.trolls()):
                state = nr.state_json_from_referee(ref, turn, staged=staged)
                obs, mask, _ = builder.observe(state, policy_seat, uid, nr.PHASE_TROLL,
                                               plan_index, want_mask=True, want_plan_mask=False)
                index = policy.action_index(obs, mask)
                if not mask[index]:
                    illegal.append({"turn": turn, "command": f"action {index} for troll {uid}",
                                    "why": "outside the runtime's mask"})
                    continue
                staged.append((uid, index))
                frags.append(builder.decode_action(index, uid, policy_seat, width, height))
        else:
            plan = policy.plan(view)
            if plan is not None:
                if ref.can_train(tuple(plan), policy_seat) is None:
                    frags.append("TRAIN %d %d %d %d" % tuple(plan))
                    policy_trains.append({"turn": turn, "talents": list(plan)})
                else:
                    illegal.append({"turn": turn, "command": "TRAIN %d %d %d %d" % tuple(plan),
                                    "why": ref.can_train(tuple(plan), policy_seat)})
            for uid in sorted(view.trolls()):
                cmd = policy.command(view, uid)
                if cmd == "WAIT" or not cmd:
                    continue
                if cmd not in view.legal(uid):
                    illegal.append({"turn": turn, "command": cmd, "why": "not in the mask"})
                    continue
                frags.append(cmd)
        policy_line = ";".join(frags)

        if tensor:
            # Amendment 2: the plan is a target and the environment's own dry run decides whether
            # the TRAIN command is emitted at all -- one shared adapter, `nn_runtime.plan_trains`.
            emitted, talents = nr.plan_trains(ref, policy_seat, plan_index, policy_line,
                                              bot_line, builder)
            # A plan the head asked for and the dry run refused leaves no other trace: without
            # these two counts a report that bought nothing cannot say whether the head never
            # asked or whether every plan it asked for was unaffordable that turn.
            if plan_index:
                plans_drawn += 1
                plans_refused += 0 if emitted else 1
            if emitted:
                policy_line = ("TRAIN %d %d %d %d" % talents
                               + (";" + policy_line if policy_line else ""))
                policy_trains.append({"turn": turn, "talents": list(talents),
                                      "plan_index": plan_index})
        policy_time += time.perf_counter() - t0

        for uid, u in view.trolls().items():
            tr = tracks.setdefault(uid, {"cells": [], "carrying": []})
            tr["cells"].append(tuple(u["cell"]))
            tr["carrying"].append(sum(u["carry"]) > 0)

        if keep_replay:
            replay.append({"turn": turn, "bot": bot_line, "policy": policy_line,
                           "score": [score_of(ref.inv), score_of(ref.opp_inv)]})
        if policy_seat == 0:
            ref.apply_two(policy_line, bot_line)
        else:
            ref.apply_two(bot_line, policy_line)
        ref.grow()

        stalled, turns_until_end, reason = nr.stall_check(ref, turns_until_end)
        if stalled:
            ended_turn, ended_reason = turn, reason
            break

    bot.close()
    bot_events = [{"turn": e["turn"], "talents": e["talents"], "spawned": e["spawned"]}
                  for e in ref.train_events if e["player"] == bot_seat]
    policy_events = [{"turn": e["turn"], "talents": e["talents"], "spawned": e["spawned"]}
                     for e in ref.train_events if e["player"] == policy_seat]
    loops = {str(uid): loop_runs(tr["cells"], tr["carrying"]) for uid, tr in tracks.items()}
    inv_of = (ref.inv, ref.opp_inv)
    bot_score = score_of(inv_of[bot_seat])
    policy_score = score_of(inv_of[policy_seat])
    return {
        "map_hash": rec["map_hash"],
        "start_inventory": list(draw),
        "policy_seat": policy_seat,
        "turns": ended_turn,
        "ended_reason": ended_reason,
        "stall_counter": turns_until_end,
        "bot_score": bot_score,
        "policy_score": policy_score,
        "policy_won": policy_score > bot_score,
        "bot_trains": bot_events,
        "policy_trains": policy_events,
        "policy_trains_requested": policy_trains,
        "policy_plans_drawn": plans_drawn,
        "policy_plans_refused": plans_refused,
        "policy_trolls": len(view.trolls()),
        "bot_trolls": len(view.trolls(bot_seat)),
        "timeouts": bot.timeouts,
        "illegal_commands": illegal,
        "referee_errors": dict(ref.error_counts),
        "loops": loops,
        "worst_loop": max(loops.values()) if loops else 0,
        "policy_seconds": round(policy_time, 2),
        "replay": replay,
    }


# --------------------------------------------------------------------------- the tests

def _test_map():
    """A small hand-made map record in the bench's own `--maps` format."""
    rows = ["........",
            ".0....1.",
            "........"]
    return {"rows": rows, "shacks": {"p0": [1, 1], "p1": [6, 1]},
            "trees0": [{"type": "PLUM", "x": 3, "y": 1, "size": 3, "health": 8,
                        "fruits": 2, "cur_cd": 4}],
            "map_hash": "test"}


def self_test(library) -> int:
    """The amendments, checked rather than argued for."""
    failures = []

    def check(label, fn):
        try:
            fn()
            print(f"ok   {label}")
        except Exception as exc:                                  # noqa: BLE001
            failures.append(f"{label}: {exc}")
            print(f"FAIL {label}: {exc}")

    rec = _test_map()
    draw = [3, 3, 3, 3, 3, 0]
    builder = nr.PlaneBuilder(library)

    # 1 -- seat 0's rendering is the day-1 behaviour, byte for byte.
    def seat0_is_identity():
        ref = make_referee(rec, draw)
        rendering = nr.SeatRendering(0)
        assert rendering.map_header(ref) == ref.map_header()
        assert rendering.turn_text(ref) == ref.turn_text()
    check("seat 0's rendering is the referee's own text, unchanged", seat0_is_identity)

    # 2 -- amendment 4: seat 1's rendering is the seat-exchanged game read as player 0.
    def seat1_is_the_exchanged_game():
        ref = make_referee(rec, draw)
        ref.inv[0] += 5                                # make the two seats distinguishable
        ref.units[1]["carry"][3] = 1
        mirrored = dict(rec, shacks={"p0": rec["shacks"]["p1"], "p1": rec["shacks"]["p0"]})
        other = make_referee(mirrored, draw)
        other.inv, other.opp_inv = list(ref.opp_inv), list(ref.inv)
        other.units = {uid: dict(u, player=1 - u["player"])
                       for uid, u in ref.units.items()}
        assert nr.SeatRendering(1).turn_text(ref) == nr.SeatRendering(0).turn_text(other), \
            "seat 1's view is not the exchanged game read from seat 0"
        header = nr.SeatRendering(1).map_header(ref)
        assert header.count("0") >= 1 and header.split("\n")[2][6] == "0", \
            "seat 1's own tent must be the map's '0'"
    check("seat 1's rendering is the seat-exchanged game read as player 0", 
          seat1_is_the_exchanged_game)

    # 3 -- the runtime codec's own seat rotation (the amendment of 16:40Z), on both seats.
    def codec_rotates_both_seats():
        w, h = len(rec["rows"][0]), len(rec["rows"])
        for seat in (0, 1):
            for plane in range(nr.ACTION_PLANES):
                for (x, y) in ((0, 0), (3, 1), (7, 2)):
                    index = nr.flat(plane, x, y)
                    text = builder.decode_action(index, 0, seat, w, h)
                    troll = (x, y) if plane else (5, 2)
                    ax, ay = (troll if seat == 0
                              else (w - 1 - troll[0], h - 1 - troll[1]))
                    assert builder.encode_command(text, 0, seat, w, h, ax, ay) == index, \
                        f"{text!r} does not encode back to {index} on seat {seat}"
        move = builder.decode_action(nr.flat(0, 0, 0), 0, 1, w, h)
        assert move == f"MOVE 0 {w - 1} {h - 1}", move
    check("the runtime's codec rotates seat 1 and round-trips on both seats",
          codec_rotates_both_seats)

    # 4 -- amendment 2: the plan is a target; the dry run decides.
    def dry_run_decides():
        ref = make_referee(rec, [0, 0, 0, 0, 0, 0])
        emitted, _ = nr.plan_trains(ref, 0, 399, "", "", builder)   # (4,5,3,4) with an empty bank
        assert not emitted, "an unaffordable plan must not emit a TRAIN"
        rich = make_referee(rec, [40, 40, 40, 40, 40, 0])
        # The starter stands on its own shack at turn 1, and the referee refuses a TRAIN into an
        # occupied shack -- which is exactly the post-MOVE occupancy the dry run is for: with the
        # troll standing still the purchase fails, and with the same turn's MOVE off the shack it
        # succeeds.
        assert not nr.plan_trains(rich, 0, 1, "", "", builder)[0], \
            "a TRAIN into the occupied shack must fail"
        step_off = "MOVE 0 2 1"
        emitted, talents = nr.plan_trains(rich, 0, 1, step_off, "", builder)
        assert emitted and talents == builder.decode_plan(1), (emitted, talents)
        assert not nr.plan_trains(rich, 0, 0, step_off, "", builder)[0], "plan 0 trains nothing"
    check("TRAIN is emitted only when the environment's own dry run succeeds", dry_run_decides)

    # 5 -- amendment 3: the referee's rule ends the game, with a reason.
    def stall_rule():
        ref = make_referee(rec, draw)
        stalled, counter, reason = nr.stall_check(ref, 0)
        # With a tree standing the game cannot end, and the grace counter is the walk home of a
        # unit *standing on a plant* -- nobody is, so it stays zero.
        assert not stalled and reason is None, (stalled, counter, reason)
        ref.plants.clear()                            # no trees: the grace counter now runs down
        seen = None
        for _ in range(counter + 2):
            stalled, counter, seen = nr.stall_check(ref, counter)
            if stalled:
                break
        assert stalled and seen is not None, (stalled, counter, seen)
    check("the game ends by the referee's own has_stalled, with a reason", stall_rule)

    # 6 -- the tensor path plays a whole turn on a real referee: masks, staging, decode.
    def tensor_turn():
        ref = make_referee(rec, draw)
        policy = RandomMaskPolicy(seed=1, train_p=1.0)
        state = nr.state_json_from_referee(ref, 1)
        obs, _, plan_mask = builder.observe(state, 1, -1, nr.PHASE_PLAN, 0,
                                            want_mask=False, want_plan_mask=True)
        assert plan_mask[0] == 1, "plan 0 is always legal"
        plan_index = policy.plan_index(obs, plan_mask)
        staged, commands = [], []
        for uid in sorted(u for u, v in ref.units.items() if v["player"] == 1):
            state = nr.state_json_from_referee(ref, 1, staged=staged)
            obs, mask, _ = builder.observe(state, 1, uid, nr.PHASE_TROLL, plan_index,
                                           want_mask=True, want_plan_mask=False)
            assert any(mask), "the mask is never empty (MOVE/current is the fallback)"
            index = policy.action_index(obs, mask)
            staged.append((uid, index))
            commands.append(builder.decode_action(
                index, uid, 1, len(rec["rows"][0]), len(rec["rows"])))
        line = ";".join(commands)
        before = ref.command_error_total
        ref.apply_two("", line)
        assert ref.command_error_total == before, \
            f"the referee rejected a command the runtime's mask allowed: {line!r}"
    check("a whole turn taken through the runtime's masks is accepted by the referee",
          tensor_turn)

    # 7 -- --plan-decoding sample: the mask still binds, and one seed is one run.
    def sampled_plan_obeys_the_mask():
        import numpy as np                                        # noqa: PLC0415

        class Logits:
            """What `_sample` needs of a torch tensor -- so this check needs no PyTorch."""

            def __init__(self, values):
                self.values = np.asarray(values, dtype=np.float64)

            def detach(self):
                return self

            def numpy(self):
                return self.values

        policy = object.__new__(NetworkPolicy)
        policy.temperature = 1.0
        # An illegal index carries by far the largest logit: only the mask can keep it out.
        values = np.array([0.0, 1.0, 50.0, 2.0, 0.5])
        mask = bytes([1, 1, 0, 1, 0])
        policy.rng = np.random.default_rng(0)
        drawn = [policy._sample(Logits(values), mask) for _ in range(300)]
        assert set(drawn) <= {0, 1, 3}, f"the sample left the mask: {sorted(set(drawn))}"
        assert len(set(drawn)) > 1, "a sample that never varies is an argmax"
        policy.rng = np.random.default_rng(0)
        again = [policy._sample(Logits(values), mask) for _ in range(300)]
        assert drawn == again, "the same seed drew a different run"
        # A cold temperature is the argmax of the legal entries; a hot one spreads.
        policy.temperature = 0.01
        policy.rng = np.random.default_rng(1)
        assert {policy._sample(Logits(values), mask) for _ in range(50)} == {3}, \
            "at temperature 0.01 the best legal index must win"
        policy.temperature = 1.0
        try:
            policy._sample(Logits(values), bytes(5))
        except RuntimeError:
            pass
        else:
            raise AssertionError("an empty mask must raise")
    check("--plan-decoding sample stays inside the mask and repeats at one seed",
          sampled_plan_obeys_the_mask)

    print(f"self-test: {'PASS' if not failures else 'FAIL'} ({len(failures)} failures)")
    return 0 if not failures else 1


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
    ap.add_argument("--policy", default="random-legal",
                    choices=["random-legal", "random-mask", "network"],
                    help="random-legal is the day-1 text proof; random-mask is the same proof "
                         "over the amended tensor path; network needs --checkpoint")
    ap.add_argument("--checkpoint", type=Path, default=None,
                    help="a clone checkpoint (train_clone.py) for --policy network")
    ap.add_argument("--plan-decoding", default="argmax", choices=("argmax", "sample"),
                    help="how --policy network reads its plan head; commands stay argmax")
    ap.add_argument("--plan-temperature", type=float, default=1.0,
                    help="the temperature of --plan-decoding sample (and of --command-decoding sample)")
    ap.add_argument("--command-decoding", default="argmax", choices=("argmax", "sample"),
                    help="commands by masked argmax (default) or sampled at --plan-temperature, "
                         "as the PPO trainer plays them")
    ap.add_argument("--library", type=Path, default=Path(nr.DEFAULT_LIBRARY),
                    help="libtroll_farm.so: the planes and both masks come from it")
    ap.add_argument("--both-seats", action="store_true",
                    help="play every map twice, the policy on seat 0 and on seat 1 "
                         "(amendment 4)")
    ap.add_argument("--self-test", action="store_true",
                    help="check the seat transformation, the codec's rotation and the TRAIN "
                         "dry run, and exit")
    ap.add_argument("--train-p", type=float, default=0.02)
    ap.add_argument("--out", type=Path, default=HERE / "results" / "bench.json")
    ap.add_argument("--replays", type=Path, default=HERE / "results" / "bench-replays.jsonl")
    ap.add_argument("--no-replays", action="store_true")
    ap.add_argument("--read", type=Path, default=None, help="print a saved replay file")
    ap.add_argument("--game", type=int, default=0, help="with --read: one game (1-based), 0 = all")
    args = ap.parse_args()

    if args.self_test:
        return self_test(args.library)
    if args.read is not None:
        return read_replay(args.read, args.game)

    plan = []
    with open(args.maps) as fh:
        for line in fh:
            item = json.loads(line)
            plan.append((item["rec"], item["draw"]))
    if args.games:
        plan = plan[:args.games]
    seats = (0, 1) if args.both_seats else (1,)
    schedule = [(rec, draw, seat) for rec, draw in plan for seat in seats]
    bot_text = args.bot.read_text()
    builder = None
    if args.policy != "random-legal":
        builder = nr.PlaneBuilder(args.library)
    print(f"maps {len(plan)} from {args.maps} x {len(seats)} seat(s) = {len(schedule)} games\n"
          f"compiled  {args.bot.name} sha {sha(bot_text)[:16]}\n"
          f"python    {args.policy} seed {args.seed}"
          + (f"\nruntime   {rel(args.library)} plan vocabulary {builder.plan_version}"
             if builder else "") + "\n")

    rows = []
    with tempfile.TemporaryDirectory(prefix="nn-bench-") as wd:
        binary = Path(wd) / "bot.bin"
        sh.compile_text(bot_text, binary, crate="nn_bench_bot")
        if not args.no_replays:
            args.replays.parent.mkdir(parents=True, exist_ok=True)
        replay_fh = None if args.no_replays else open(args.replays, "w")
        if args.policy == "network" and args.checkpoint is None:
            raise SystemExit("--policy network needs --checkpoint")
        network = (NetworkPolicy(args.checkpoint, plan_decoding=args.plan_decoding,
                                 temperature=args.plan_temperature, seed=args.seed,
                                 command_decoding=args.command_decoding)
                   if args.policy == "network" else None)
        for i, (rec, draw, seat) in enumerate(schedule):
            if args.policy == "random-legal":
                policy = RandomLegalPolicy(seed=args.seed + i, train_p=args.train_p)
            elif args.policy == "random-mask":
                policy = RandomMaskPolicy(seed=args.seed + i, train_p=args.train_p)
            else:
                policy = network
                policy.reseed(args.seed + i)
            row = play(rec, draw, binary, policy, args.turns,
                       keep_replay=replay_fh is not None, policy_seat=seat, builder=builder)
            if replay_fh is not None:
                replay_fh.write(json.dumps(row, sort_keys=True) + "\n")
            row.pop("replay", None)
            rows.append(row)
            t0 = row["policy_trains"][0]["talents"] if row["policy_trains"] else None
            b0 = row["bot_trains"][0]["talents"] if row["bot_trains"] else None
            print(f"  {i+1:>2}/{len(schedule)} {row['map_hash']} seat {row['policy_seat']}  "
                  f"bot {row['bot_score']:>4} vs policy "
                  f"{row['policy_score']:>4}  {'POLICY' if row['policy_won'] else 'bot   '}  "
                  f"bot trolls {row['bot_trolls']} (1st train {b0}), policy trolls "
                  f"{row['policy_trolls']} (1st {t0})  illegal {len(row['illegal_commands'])}  "
                  f"timeouts {row['timeouts']}  worst loop {row['worst_loop']}  "
                  f"referee errors {sum(row['referee_errors'].values())}  "
                  f"end t{row['turns']} ({row['ended_reason']})")
        if replay_fh is not None:
            replay_fh.close()

    n = len(rows)
    wins = sum(r["policy_won"] for r in rows)
    report = {
        "what": "bench: one seat a Python policy, one seat a compiled single-file bot, over the "
                "July Python referee (fuzz_panel.FuzzReferee.apply_two)",
        "bot": rel(args.bot), "bot_sha256": sha(bot_text),
        "policy": args.policy, "seed": args.seed, "train_p": args.train_p,
        "checkpoint": rel(args.checkpoint) if args.checkpoint else None,
        "plan_decoding": args.plan_decoding if args.policy == "network" else None,
        "command_decoding": args.command_decoding if args.policy == "network" else None,
        "plan_temperature": (args.plan_temperature
                             if args.policy == "network" and args.plan_decoding == "sample"
                             else None),
        "library": rel(args.library) if builder else None,
        "plan_vocab_version": builder.plan_version if builder else None,
        "maps": rel(args.maps), "maps_played": len(plan),
        "seats": list(seats), "games": n, "turn_cap": args.turns,
        "games_ended_early": sum(1 for r in rows if r["ended_reason"] != "turn_limit"),
        "end_reasons": {reason: sum(1 for r in rows if r["ended_reason"] == reason)
                        for reason in sorted({r["ended_reason"] for r in rows})},
        "policy_wins_by_seat": {str(seat): sum(1 for r in rows
                                               if r["policy_seat"] == seat and r["policy_won"])
                                for seat in seats},
        "games_by_seat": {str(seat): sum(1 for r in rows if r["policy_seat"] == seat)
                          for seat in seats},
        "policy_wins": wins,
        "policy_score_mean": round(sum(r["policy_score"] for r in rows) / n, 1),
        "bot_score_mean": round(sum(r["bot_score"] for r in rows) / n, 1),
        "plans_drawn_total": sum(r["policy_plans_drawn"] for r in rows),
        "plans_refused_total": sum(r["policy_plans_refused"] for r in rows),
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
          f"| referee errors | games with a loop | ended early |")
    print(f"| {n} | {wins} | {report['policy_score_mean']} | {report['bot_score_mean']} | "
          f"{report['illegal_commands_total']} | {report['timeouts_total']} | "
          f"{report['referee_errors_total']} | {report['games_with_a_loop']} | "
          f"{report['games_ended_early']} |")
    if args.both_seats:
        print("by seat: " + ", ".join(
            f"seat {seat}: {report['policy_wins_by_seat'][str(seat)]} of "
            f"{report['games_by_seat'][str(seat)]} won" for seat in seats))
    print("end reasons: " + ", ".join(f"{k} {v}" for k, v in report["end_reasons"].items()))
    print(f"\nreport -> {args.out}"
          + ("" if args.no_replays else f"; replays -> {args.replays} "
                                        f"(read: --read {args.replays} --game 1)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
