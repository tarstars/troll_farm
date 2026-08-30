#!/usr/bin/env python3
"""The one adapter between a Python caller and the compiled full-game runtime (Track N, Phase 2,
card `coordination/tasks/20260829-nn-bot-way-b-dataset.md`).

Everything in here exists because the parent card's amendments after chatgpt_1's bench audit
(2026-08-29 17:38Z) say the bench must present the network *exactly* what the environment presents.
Two callers need that -- `bench.py` (the network playing the July Python referee) and
`train_clone.py` (the clone's planes built at load time) -- and a second implementation of any of
it is precisely the drift the card forbids.  So there is one:

* `PlaneBuilder` -- the compiled `tf_full_obs_from_state`, `tf_full_decode_action`,
  `tf_full_encode_command`, `tf_full_decode_plan` and the size/version queries, over `ctypes`.
  The planes, the 3,146-entry spatial mask and the 400-entry plan mask all come from here
  (**amendment 1**), and the library's `tf_full_plan_version()` is checked against the vocabulary
  this repository speaks before a single row is built.
* `state_json_from_referee` / `state_json_from_shard` -- the strict superset of
  `Reconstructor.snapshot()` that `tf_full_obs_from_state` documents (`ENV-API.md`), built once
  from the bench's referee and once from a dataset shard's compact state, so the two callers
  cannot disagree about what a state *is*.
* `plan_trains` -- **amendment 2**: the plan is an always-legal target, and TRAIN is emitted only
  when the environment's own dry run says the command succeeds.  The environment's dry run
  (`rust/src/rl_full.rs::train_succeeds`) clones the state, inserts `TRAIN ms cc hp chop` at the
  head of that seat's command list, runs one full referee turn and asks whether the seat's unit
  count grew -- which is why the bank is the post-MOVE/post-PICK bank and the shack occupancy is
  the one the turn really produces.  `plan_trains` is that same procedure against the bench's
  referee, in one place.
* `stall_check` -- **amendment 3**: the game ends when the referee's own persistent
  grace/stuck/mercy rule ends it.  This calls `sim.engine.has_stalled` -- the project's Python
  port of `game::engine::has_stalled`, counter and all -- through a thin view of the bench's
  referee, and returns the turn and the reason.  Nothing here re-implements the rule.
* `SeatRendering` -- **amendment 4**: the compiled single-file bot always believes it is player 0
  (`fuzz_panel.materialize`: the reader's tent is `0`, its units are player 0), so playing it on
  the referee's seat 1 means rendering the seat's own view -- inventories in the reader's order,
  unit rows relabelled, the map header's tent characters swapped.  The transformation is an
  involution and is tested as one.

Nothing in this module holds a handle or mutates a referee.
"""
from __future__ import annotations

import copy
import ctypes
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for _path in (REPO, HERE):                                      # sim.engine, build_dataset
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

OBS_CHANNELS = 104
GRID_H = 11
GRID_W = 22
CELLS = GRID_H * GRID_W                                         # 242
OBS_SIZE = OBS_CHANNELS * CELLS                                 # 25,168
ACTION_PLANES = 13
ACTION_SIZE = ACTION_PLANES * CELLS                             # 3,146
PLAN_ACTION_SIZE = 400
PLAN_VOCAB_VERSION = "v400-2026-08-29"
PHASE_PLAN, PHASE_TROLL = 0, 1
ITEM_NAMES = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")
DEFAULT_LIBRARY = REPO / "rust" / "target" / "release" / "libtroll_farm.so"

#: The verb of each action plane, in the July order the environment decodes
#: (`ENV-API.md`, "Spatial action index").
VERBS = ("MOVE", "HARVEST", "CHOP", "DROP", "MINE",
         "PLANT_PLUM", "PLANT_LEMON", "PLANT_APPLE", "PLANT_BANANA",
         "PICK_PLUM", "PICK_LEMON", "PICK_APPLE", "PICK_BANANA")


def flat(plane: int, x: int, y: int) -> int:
    return plane * CELLS + y * GRID_W + x


def unflat(index: int) -> tuple[int, int, int]:
    plane, rest = divmod(index, CELLS)
    y, x = divmod(rest, GRID_W)
    return plane, x, y


# --------------------------------------------------------------------------- the compiled runtime

class PlaneBuilder:
    """`tf_full_obs_from_state` and the codec helpers, over `ctypes`.

    One instance owns one `CDLL`.  It is **not** shared across processes: a DataLoader worker
    builds its own (`ctypes` handles do not survive a fork intact on every platform, and the cost
    is a millisecond).
    """

    def __init__(self, library: str | Path = DEFAULT_LIBRARY, *,
                 expect_version: str | None = PLAN_VOCAB_VERSION):
        self.path = Path(library)
        if not self.path.exists():
            raise FileNotFoundError(
                f"{self.path} is not built; run "
                f"`cargo build --manifest-path rust/Cargo.toml --release --lib`")
        self.lib = ctypes.CDLL(str(self.path))

        self.lib.tf_full_obs_size.restype = ctypes.c_size_t
        self.lib.tf_full_action_size.restype = ctypes.c_size_t
        self.lib.tf_full_plan_size.restype = ctypes.c_size_t
        self.lib.tf_full_plan_version.restype = ctypes.c_char_p
        self.lib.tf_full_obs_from_state.restype = ctypes.c_int
        self.lib.tf_full_obs_from_state.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_size_t, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_ubyte,
            ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte),
            ctypes.POINTER(ctypes.c_ubyte)]
        self.lib.tf_full_decode_action.restype = ctypes.c_int
        self.lib.tf_full_decode_action.argtypes = [
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_size_t]
        self.lib.tf_full_encode_command.restype = ctypes.c_int
        self.lib.tf_full_encode_command.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_size_t, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.lib.tf_full_decode_plan.restype = ctypes.c_int
        self.lib.tf_full_decode_plan.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int8)]

        self.obs_size = int(self.lib.tf_full_obs_size())
        self.action_size = int(self.lib.tf_full_action_size())
        self.plan_size = int(self.lib.tf_full_plan_size())
        self.plan_version = self.lib.tf_full_plan_version().decode()
        sizes = (self.obs_size, self.action_size, self.plan_size)
        if sizes != (OBS_SIZE, ACTION_SIZE, PLAN_ACTION_SIZE):
            raise RuntimeError(
                f"{self.path} reports sizes {sizes}, this code speaks "
                f"{(OBS_SIZE, ACTION_SIZE, PLAN_ACTION_SIZE)}; refusing to build a plane")
        if expect_version is not None and self.plan_version != expect_version:
            raise RuntimeError(
                f"{self.path} speaks plan vocabulary {self.plan_version!r}, this code speaks "
                f"{expect_version!r}; the same plan index means a different talent set")

    # -- the planes --------------------------------------------------------
    def observe(self, state: dict, seat: int, active_troll: int, phase: int, plan_index: int,
                *, prior_target_trained: bool = False,
                want_mask: bool = True, want_plan_mask: bool = True):
        """`(obs, mask_or_None, plan_mask_or_None)` as `bytes`, straight from the library.

        A nonzero status is raised, never normalized: the environment refuses an impossible
        context (a masked plan, a staged prefix that is not the earlier trolls' own, a phase that
        does not match the active troll) and a caller that silently repaired one would be showing
        the network a state no game reaches.
        """
        payload = json.dumps(state, separators=(",", ":")).encode()
        buffer = (ctypes.c_ubyte * len(payload)).from_buffer_copy(payload)
        obs = (ctypes.c_ubyte * OBS_SIZE)()
        mask = (ctypes.c_ubyte * ACTION_SIZE)() if want_mask else None
        plan_mask = (ctypes.c_ubyte * PLAN_ACTION_SIZE)() if want_plan_mask else None
        code = self.lib.tf_full_obs_from_state(
            buffer, len(payload), int(seat), int(active_troll), int(phase), int(plan_index),
            1 if prior_target_trained else 0, obs, mask, plan_mask)
        if code != 0:
            raise RuntimeError(
                f"tf_full_obs_from_state returned {code} "
                f"(seat={seat}, active_troll={active_troll}, phase={phase}, plan={plan_index})")
        return (bytes(obs),
                bytes(mask) if mask is not None else None,
                bytes(plan_mask) if plan_mask is not None else None)

    # -- the codec ---------------------------------------------------------
    def decode_action(self, action_index: int, troll_id: int, seat: int, w: int, h: int) -> str:
        out = (ctypes.c_ubyte * 64)()
        code = self.lib.tf_full_decode_action(
            int(action_index), int(troll_id), int(seat), int(w), int(h), out, 64)
        if code < 0:
            raise ValueError(f"tf_full_decode_action({action_index}, {troll_id}, seat {seat}) "
                             f"returned {code}")
        return bytes(out[:code]).decode()

    def encode_command(self, command: str, troll_id: int, seat: int, w: int, h: int,
                       troll_x: int, troll_y: int) -> int:
        payload = command.encode()
        buffer = (ctypes.c_ubyte * len(payload)).from_buffer_copy(payload)
        code = self.lib.tf_full_encode_command(
            buffer, len(payload), int(troll_id), int(seat), int(w), int(h),
            int(troll_x), int(troll_y))
        if code < 0:
            raise ValueError(f"tf_full_encode_command({command!r}, troll {troll_id}, "
                             f"seat {seat}) returned {code}")
        return int(code)

    def decode_plan(self, plan_index: int) -> tuple[int, int, int, int]:
        out = (ctypes.c_int8 * 4)()
        code = self.lib.tf_full_decode_plan(int(plan_index), out)
        if code < 0:
            raise ValueError(f"tf_full_decode_plan({plan_index}) returned {code}")
        return tuple(int(v) for v in out)


# --------------------------------------------------------------------------- the state document

def state_json_from_referee(ref, turn: int, *, staged: list | None = None) -> dict:
    """The `ENV-API.md` state document, read off the bench's `FuzzReferee`.

    The referee keeps plants in a dict keyed by cell and units in a dict keyed by id; the
    document wants lists with the reconstruction's field names.  `staged` is the strictly
    ascending prefix of this seat's earlier troll decisions, exactly as the environment stages
    them; it is omitted (not empty) in PLAN phase, because the environment refuses a staged
    action there.
    """
    plants = [{"type": p["kind"], "x": cell[0], "y": cell[1], "size": p["size"],
               "health": p["health"], "fruits": p["fruits"], "cooldown": p["cd"]}
              for cell, p in sorted(ref.plants.items())]
    units = [{"id": uid, "player": u["player"], "x": u["cell"][0], "y": u["cell"][1],
              "ms": u["speed"], "cc": u["cap"], "hp": u["harvest"], "chop": u["chop"],
              "carry": list(u["carry"])}
             for uid, u in sorted(ref.units.items())]
    state = {
        "w": len(ref.rows[0]), "h": len(ref.rows), "rows": list(ref.rows),
        "turn": int(turn),
        "inv": [list(ref.inv), list(ref.opp_inv)],
        "units": units,
        "plants": plants,
    }
    if staged:
        state["staged_actions"] = [{"troll_id": int(t), "action_index": int(a)}
                                   for t, a in staged]
    return state


def state_json_from_shard(state: dict, game_map: dict, *, staged: list | None = None) -> dict:
    """The same document from a dataset shard: the compact per-turn state plus its map.

    `state` is what `build_dataset.py` writes (`turn`, `inv`, `units`, `plants` -- the exact
    reconstruction's snapshot), and `game_map` is that game's `{w, h, rows}`.  The shard stores
    them apart because one map serves every turn of a game.
    """
    document = {"w": game_map["w"], "h": game_map["h"], "rows": list(game_map["rows"]),
                "turn": int(state["turn"]), "inv": state["inv"],
                "units": state["units"], "plants": state["plants"]}
    if staged:
        document["staged_actions"] = [{"troll_id": int(t), "action_index": int(a)}
                                      for t, a in staged]
    return document


# --------------------------------------------------------------------------- amendment 2

def plan_trains(ref, seat: int, plan_index: int, own_line: str, opponent_line: str,
                builder: PlaneBuilder) -> tuple[bool, tuple[int, int, int, int] | None]:
    """The environment's own dry run: would this turn's TRAIN succeed?

    `rust/src/rl_full.rs::train_succeeds` clones the state, inserts the TRAIN command at the head
    of the seat's command list, runs one whole referee turn and asks whether the seat gained a
    troll.  This is that, against the bench's referee: a deep copy, `apply_two` with the command
    prepended, and the same question.  Running the whole turn is the point -- the bank the TRAIN
    is charged against is the post-MOVE/post-PICK bank, and the shack must be free after the
    turn's own movement.

    Returns `(emitted, talents)`.  Plan 0 ("train nothing") never emits.
    """
    if plan_index == 0:
        return False, None
    talents = builder.decode_plan(plan_index)
    if tuple(talents) == (0, 0, 0, 0):
        return False, None
    command = "TRAIN %d %d %d %d" % tuple(talents)
    probe = copy.deepcopy(ref)
    before = sum(1 for u in probe.units.values() if u["player"] == seat)
    line_own = command if not own_line else command + ";" + own_line
    if seat == 0:
        probe.apply_two(line_own, opponent_line)
    else:
        probe.apply_two(opponent_line, line_own)
    after = sum(1 for u in probe.units.values() if u["player"] == seat)
    return (after > before), tuple(talents)


# --------------------------------------------------------------------------- amendment 3

class _StallUnit:
    __slots__ = ("player", "pos", "ms", "carry")

    def __init__(self, player, pos, ms, carry):
        self.player, self.pos, self.ms, self.carry = player, pos, ms, carry


class _StallPlant:
    __slots__ = ("pos",)

    def __init__(self, pos):
        self.pos = pos


class _StallView:
    """The handful of fields `sim.engine.has_stalled` reads, off the bench's referee."""

    def __init__(self, ref):
        self.plants = [_StallPlant(cell) for cell in ref.plants]
        self.units = [_StallUnit(u["player"], tuple(u["cell"]), u["speed"], list(u["carry"]))
                      for u in ref.units.values()]
        self.walkable = ref.walk
        self.shacks = [tuple(ref.shacks[0]), tuple(ref.shacks[1])]
        self.inventories = [list(ref.inv), list(ref.opp_inv)]
        self.scores = [score_of(ref.inv), score_of(ref.opp_inv)]


def score_of(inv) -> int:
    """One point a fruit, four a wood (`sim/engine.py::recompute_scores`)."""
    return sum(inv[0:4]) + 4 * inv[5]


def stall_check(ref, turns_until_end: int) -> tuple[bool, int, str | None]:
    """`sim.engine.has_stalled` on the bench's referee: `(stalled, counter, reason)`.

    The counter is persistent and must be fed back in on the next turn -- that is the referee's
    rule, and a bench that restarted it every turn would never end a game early.
    """
    from sim.engine import has_stalled, stall_reason              # noqa: PLC0415

    view = _StallView(ref)
    stalled, counter = has_stalled(view, turns_until_end)
    return stalled, counter, (stall_reason(view, counter) if stalled else None)


# --------------------------------------------------------------------------- amendment 4

class SeatRendering:
    """What the compiled single-file bot reads when it sits on the referee's seat `seat`.

    The protocol has no seat field: the reader is always player 0, its tent is the map's `0`
    character and its inventory is the first line (`fuzz_panel.materialize`).  Playing the
    compiled bot on seat 1 therefore means rendering *its* view -- which is what this class does,
    and nothing else: the referee's own bookkeeping, ids and coordinates are untouched, so the
    commands that come back are directly applicable.

    On seat 0 every method is the identity, which is the day-1 behaviour unchanged.
    """

    def __init__(self, seat: int):
        if seat not in (0, 1):
            raise ValueError(f"seat {seat} is not 0 or 1")
        self.seat = seat

    def map_header(self, ref) -> str:
        rows = list(ref.rows)
        if self.seat == 1:
            rows = ["".join("1" if c == "0" else "0" if c == "1" else c for c in row)
                    for row in rows]
        return "%d %d\n" % (len(rows[0]), len(rows)) + "\n".join(rows) + "\n"

    def turn_text(self, ref) -> str:
        import semantic_harness as sh                             # noqa: PLC0415

        own_inv = ref.inv if self.seat == 0 else ref.opp_inv
        opp_inv = ref.opp_inv if self.seat == 0 else ref.inv
        plant_rows = tuple(
            (p["kind"], c[0], c[1], p["size"], p["health"], p["fruits"], p["cd"])
            for c, p in sorted(ref.plants.items()))
        unit_rows = tuple(
            (uid, 0 if u["player"] == self.seat else 1, u["cell"][0], u["cell"][1],
             u["speed"], u["cap"], u["harvest"], u["chop"], *u["carry"])
            for uid, u in sorted(ref.units.items()))
        return sh.turn_text(inventory=tuple(own_inv), opponent_inventory=tuple(opp_inv),
                            plants=plant_rows, units=unit_rows)


# --------------------------------------------------------------------------- the shard's contexts

def shard_contexts(arrays, states, maps):
    """One context per shard row, in the shard's own order: what the environment would show.

    `arrays` is `build_dataset.read_shard`'s dict of columns, `states` maps `(game, turn, seat)`
    to the compact per-turn state and `maps` maps the game id to its `{w, h, rows}`.  Each yielded
    context is everything `PlaneBuilder.observe` needs plus the row's label -- and the **staged
    prefix is rebuilt from the shard itself**: a troll row's earlier same-turn trolls staged the
    actions their own labels name, which is exactly what the environment stages when the policy
    plays the turn.  Row order inside a turn is the mini-step order (the plan row, then the troll
    rows in ascending id), and this asserts it rather than assuming it.
    """
    from build_dataset import KIND_COMMAND, KIND_PLAN                # noqa: PLC0415

    game = arrays["game"]
    turn = arrays["turn"]
    seat = arrays["seat"]
    kind = arrays["kind"]
    troll = arrays["troll"]
    verb = arrays["verb"]
    label = arrays["label"]
    standing = arrays["standing_plan"]
    split = arrays["split"]

    key = None
    staged: list[tuple[int, int]] = []
    for i in range(len(label)):
        here = (int(game[i]), int(turn[i]), int(seat[i]))
        if here != key:
            key, staged = here, []
        state = states.get(here)
        if state is None:
            raise KeyError(f"no compact state for game {here[0]} turn {here[1]} seat {here[2]}")
        game_map = maps.get(str(here[0])) or maps.get(here[0])
        if game_map is None:
            raise KeyError(f"no map for game {here[0]}; rebuild the shard with the maps file")
        if int(kind[i]) == KIND_PLAN:
            if staged:
                raise AssertionError(f"a plan row follows troll rows in turn {here}")
            context = dict(
                state=state_json_from_shard(state, game_map), seat=here[2],
                active_troll=-1, phase=PHASE_PLAN, plan_index=0)
        else:
            if staged and int(troll[i]) <= staged[-1][0]:
                raise AssertionError(f"troll ids out of order in turn {here}: "
                                     f"{staged[-1][0]} then {int(troll[i])}")
            context = dict(
                state=state_json_from_shard(state, game_map, staged=list(staged)),
                seat=here[2], active_troll=int(troll[i]), phase=PHASE_TROLL,
                plan_index=int(standing[i]))
            staged.append((int(troll[i]), int(label[i])))
        context.update(index=i, kind=int(kind[i]), label=int(label[i]), verb=int(verb[i]),
                       split=int(split[i]), game=here[0], turn=here[1], w=game_map["w"],
                       h=game_map["h"])
        yield context
