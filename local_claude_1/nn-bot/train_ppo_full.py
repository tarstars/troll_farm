#!/usr/bin/env python3
"""Phase 3 of the neural-network bot: masked PPO over the full-game environment.

Card: `coordination/tasks/20260829-nn-bot-way-b.md` (Way B -- clone first, then PPO).

Plain words for the owner
-------------------------
The bot decides a whole turn in several small pieces, which the card calls *mini-steps*: first it
picks the training plan for the turn (one of 144 talent recipes, or "train nothing"), then it gives
one command to each of its trolls in turn-number order, and then the turn actually happens on the
board. This program plays many such games at once against our own bots and against frozen copies of
itself, and nudges the network towards the decisions that ended up scoring more. The clone -- the
network that was taught to copy the top four players -- is kept beside it as an *anchor*: a penalty
term that pulls the new network back whenever it drifts far from what the clone would have done.
The anchor's pull fades away over the run, so the network is free to become better than the clone
but is not free to forget it in the first hour.

Two heads, one body
-------------------
The network is July's `SpatialActorCritic` (a 3x3 stem, four residual blocks of width 16, about
35,000 weights) with the plan head switched on. Both heads read the same trunk. Which head is
trained on a given mini-step is decided by the environment's `phase`:

* `phase == 0` (PLAN): the 144-wide plan head;
* `phase == 1` (TROLL): the 13 x 11 x 22 = 3,146-wide per-cell head.

Internally both are written into one 3,146-wide logit row -- the plan logits go into columns 0..143
and the plan mask is zero everywhere above 143 -- so the sampling, the log-probability, the entropy
and the PPO ratio are one code path with no branch. Illegal actions are filled with
`torch.finfo(float32).min` before the softmax, exactly as July's trainer does; that is a finite
number, so no log-probability is ever `-inf` and nothing becomes NaN.

Discounting across mini-steps
-----------------------------
The turn's reward is paid **once**, on the mini-step that executes the turn; the earlier mini-steps
of that turn carry reward 0 (the amendment on the card, after chatgpt_1's audit finding 4). So the
mini-steps of one turn are consecutive steps of the same decision, and the advantage estimator uses
**discount 1 between mini-steps inside a turn** and `--gamma` only when crossing a turn boundary.
`compute_gae` does exactly that, and `tests/test_train_ppo_full.py` pins it to a closed form.

What could not be matched to the real interface (all marked in the code)
------------------------------------------------------------------------
`cgauto/rl_full_env.py` does not exist yet -- it is being built by `codex_1`. This trainer was
written against `local_claude_1/nn-bot/ENV-API.md` (branch `origin/agent/codex_1`), which freezes
the C ABI and the attribute names but leaves three things open. Each is handled by an adapter that
is one edit away from the truth:

1. **The tuple `FullVecEnv.step()` returns.** ENV-API.md says only "returns buffered mini-step
   transitions plus copied terminal metadata". `unpack_step()` therefore ignores the arity: it
   reads the board from the public attributes (`env.obs`, `env.masks`, `env.plan_masks`,
   `env.phase`, `env.active_troll`, `env.seat_view`, which ARE frozen) and finds the reward vector
   and the info object by inspection.
2. **The field names on the returned info object.** `info_field()` looks each one up through a list
   of spellings (`dones`, `turn_completed`, `episode_returns` / `returns`, `episode_seeds` /
   `seeds`, ...). A name that is missing raises with the list it tried.
3. **The signature of the `frozen_opponent` callable** (self-play). `FrozenOpponent.__call__`
   accepts the arguments positionally in the ENV-API observe order and ignores anything extra.

A fourth point is a genuine **contradiction between two signed documents**, not a gap, and is
resolved by a flag: the card says the earlier mini-steps of a turn carry reward 0, while ENV-API.md
says `FullVecEnv` "emits all buffered transitions with the identical returned scalar". With
`--reward-credit executing` (the default) the trainer keeps only the reward that arrives together
with `turn_completed == 1` and zeroes the rest, so the card's rule holds whichever way the
environment behaves. `--reward-credit as-returned` trusts the environment instead.

The bench gate (`--gate-every`) shells out to `local_claude_1/nn-bot/bench.py`. Today's bench (on
branch `origin/agent/claude_1`) has **no flag that accepts a PyTorch checkpoint** -- its `--policy`
takes only `random-legal`. `run_bench_gate()` detects that, reports `status="unavailable"` with the
reason, and training continues. The interface it will use as soon as the bench grows one is
documented on `run_bench_gate`.

Example
-------
    PYTHONPATH=. /home/tarstars/nn-venv/bin/python local_claude_1/nn-bot/train_ppo_full.py \
        --anchor-checkpoint local_claude_1/nn-bot/checkpoints/clone.pt \
        --initial-checkpoint local_claude_1/nn-bot/checkpoints/clone.pt \
        --maps local_claude_1/nn-bot/maps-slice-1000.jsonl \
        --opponent-weights '{"secure_orchard": 2, "norxondor_native": 1, "python_frozen": 2}' \
        --num-envs 32 --rollout-steps 128 --total-turn-steps 200000000 \
        --output-dir local_claude_1/nn-bot/runs --run-name ppo1
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.distributions.categorical import Categorical
from torch.nn import functional as F

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cgauto.train_level1_ppo import (  # noqa: E402
    ACTION_SIZE,
    OBS_CHANNELS,
    OBS_HEIGHT,
    OBS_WIDTH,
    PLAN_ACTION_SIZE,
    SpatialActorCritic,
    explained_variance,
    sha256,
)

PLAN_SIZE = PLAN_ACTION_SIZE
PHASE_PLAN = 0
PHASE_TROLL = 1
PHASE_EXTERNAL_WAIT = 2

#: The seven training opponents, in the fixed order of ENV-API.md's weight vector.
OPPONENT_IDS = (
    "secure_orchard",
    "norxondor_native",
    "legend_field_proxy_v2",
    "gold_elite_adaptive",
    "script_boss",
    "mybot_boss4",
    "python_frozen",
)

DEFAULT_MAPS = ROOT / "local_claude_1" / "nn-bot" / "maps-slice-1000.jsonl"
BENCH_SCRIPT = ROOT / "local_claude_1" / "nn-bot" / "bench.py"

#: Flags a future bench might use to accept a PyTorch checkpoint; the first one its --help
#: mentions is the one `run_bench_gate` passes.
BENCH_CHECKPOINT_FLAGS = (
    "--policy-checkpoint",
    "--checkpoint",
    "--torch-checkpoint",
    "--network",
    "--weights",
)


# --------------------------------------------------------------------------- environment access


def info_field(info: object, *names: str) -> np.ndarray:
    """One array off the environment's info object, tried under several spellings.

    ENV-API.md freezes the C parameter names of `tf_full_step` but not the Python attribute names
    `FullVecEnv` exposes. Every access goes through here, so adapting to the real wrapper is a
    matter of adding one alias.
    """

    if isinstance(info, dict):
        for name in names:
            if name in info:
                return np.asarray(info[name])
    else:
        for name in names:
            if hasattr(info, name):
                return np.asarray(getattr(info, name))
    raise AttributeError(
        f"the environment's step info has none of {names!r}; "
        "add the real spelling to the alias list in train_ppo_full.info_field"
    )


def unpack_step(result: object, num_envs: int) -> tuple[np.ndarray, object]:
    """`(rewards, info)` out of whatever `FullVecEnv.step()` returns.

    The observation is deliberately NOT taken from here: ENV-API.md guarantees the public
    attributes `env.obs` / `env.masks` / `env.plan_masks` / `env.phase`, and reading those is
    immune to the tuple's shape.
    """

    if isinstance(result, tuple) or isinstance(result, list):
        info = result[-1]
        for item in reversed(result[:-1]):
            if isinstance(item, np.ndarray) and item.shape == (num_envs,):
                if item.dtype.kind == "f":
                    return np.asarray(item, dtype=np.float32), info
        return np.asarray(info_field(info, "rewards", "reward"), dtype=np.float32), info
    info = result
    return np.asarray(info_field(info, "rewards", "reward"), dtype=np.float32), info


def load_fake_env_class():
    """`FakeFullVecEnv` from the neighbouring file (the directory name has a hyphen in it, so it
    is not an importable package -- the module is loaded by path)."""

    path = Path(__file__).resolve().parent / "fake_full_env.py"
    spec = importlib.util.spec_from_file_location("nn_bot_fake_full_env", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.FakeFullVecEnv


def make_env(args, frozen_opponent):
    """The real `FullVecEnv` when the Rust library is there, the fake otherwise."""

    weights = json.loads(args.opponent_weights)
    unknown = sorted(set(weights) - set(OPPONENT_IDS))
    if unknown:
        raise SystemExit(
            f"unknown opponent ids {unknown}; the pool is {list(OPPONENT_IDS)}"
        )
    if not weights or sum(float(value) for value in weights.values()) <= 0:
        raise SystemExit("at least one opponent weight must be positive")

    if args.env == "fake":
        return load_fake_env_class()(
            args.num_envs,
            args.seed,
            args.maps,
            weights,
            wood_shaping=args.wood_shaping,
            end_wood=args.end_wood,
            frozen_opponent=frozen_opponent,
        )

    from cgauto.rl_full_env import FullVecEnv  # noqa: PLC0415  (built by codex_1)

    return FullVecEnv(
        args.num_envs,
        args.seed,
        Path(args.maps),
        weights,
        wood_shaping=args.wood_shaping,
        end_wood=args.end_wood,
        frozen_opponent=frozen_opponent,
    )


# --------------------------------------------------------------------------- the two heads


def combined_logits(
    model: SpatialActorCritic, observations: torch.Tensor, phase: torch.Tensor
) -> tuple[torch.Tensor, torch.Tensor]:
    """One 3,146-wide logit row per mini-step, plus the value.

    PLAN rows carry the 144 plan logits in columns 0..143; their mask is zero above 143, so the
    per-cell logits sitting there can never be selected. TROLL rows carry the per-cell logits
    unchanged. Both heads come from a single pass through the shared trunk.
    """

    if not getattr(model, "plan_head", False):
        logits, value = model(observations)
        return logits, value
    spatial, plan, value = model.forward_with_plan(observations)
    rows = phase == PHASE_PLAN
    if bool(rows.any()):
        spatial = spatial.clone()
        spatial[rows, :PLAN_SIZE] = plan[rows]
    return spatial, value


def masked_logits(logits: torch.Tensor, legal: torch.Tensor) -> torch.Tensor:
    """July's masking: illegal actions get the finite minimum, never `-inf`."""

    return logits.masked_fill(~legal, torch.finfo(logits.dtype).min)


def anchor_kl(
    policy_masked: torch.Tensor, anchor_masked: torch.Tensor, legal: torch.Tensor
) -> tuple[torch.Tensor, torch.Tensor]:
    """`KL(anchor || policy)` over the legal actions, and the top-1 agreement.

    Zero when the two networks are the same, which is the state at step 0 of a run started from
    the clone with the clone as its own anchor.
    """

    policy_logp = F.log_softmax(policy_masked, dim=-1)
    anchor_logp = F.log_softmax(anchor_masked, dim=-1)
    weight = anchor_logp.exp()
    term = weight * (anchor_logp - policy_logp)
    term = torch.where(legal, term, torch.zeros_like(term))
    kl = term.sum(dim=-1).mean()
    agreement = (
        (policy_masked.argmax(dim=-1) == anchor_masked.argmax(dim=-1)).float().mean()
    )
    return kl, agreement


def anchor_coefficient(args, turn_steps: int) -> float:
    """`--anchor-coef` decayed linearly to `--anchor-coef-final` over `--anchor-decay-steps`."""

    if args.anchor_decay_steps <= 0:
        return float(args.anchor_coef)
    fraction = min(1.0, max(0.0, turn_steps / float(args.anchor_decay_steps)))
    return float(
        args.anchor_coef + (args.anchor_coef_final - args.anchor_coef) * fraction
    )


# --------------------------------------------------------------------------- advantages


def compute_gae(
    rewards: np.ndarray,
    values: np.ndarray,
    dones: np.ndarray,
    turn_boundary: np.ndarray,
    next_value: np.ndarray,
    gamma: float,
    gae_lambda: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Generalised advantage estimation with a per-step discount.

    The discount applied from mini-step `t` to `t+1` is `gamma` when `t` executed the turn
    (`turn_boundary[t]`) and `1.0` when `t+1` is another mini-step of the same turn. An episode end
    (`dones[t]`) cuts both the bootstrap and the trace, as usual.

    All arrays are `[steps, envs]`; `next_value` is `[envs]`, the value of the observation that
    follows the last stored mini-step.
    """

    steps = rewards.shape[0]
    advantages = np.zeros_like(rewards, dtype=np.float32)
    last = np.zeros(rewards.shape[1], dtype=np.float32)
    for index in reversed(range(steps)):
        nonterminal = (1.0 - dones[index]).astype(np.float32)
        following = next_value if index == steps - 1 else values[index + 1]
        discount = np.where(turn_boundary[index] > 0, np.float32(gamma), np.float32(1.0))
        delta = rewards[index] + discount * following * nonterminal - values[index]
        last = delta + discount * np.float32(gae_lambda) * nonterminal * last
        advantages[index] = last
    return advantages, advantages + values


# --------------------------------------------------------------------------- self-play opponent


class FrozenOpponent:
    """A snapshot of the policy, played as seat 1 by the environment's `python_frozen` opponent.

    NOT MATCHED TO THE REAL INTERFACE: ENV-API.md fixes the C calls but declares only
    `frozen_opponent: Callable | None` on the Python side. This object accepts the arguments in the
    order `tf_full_opponent_observe` writes them -- `(obs, masks, plan_masks, phase, active_troll,
    seat_view, needs_action)` -- takes everything after `plan_masks` as optional, and ignores extra
    keywords. It returns `int32[num_envs]`, the masked argmax for every waiting slot and `-1`
    everywhere else, which is what ENV-API.md's "submits the masked argmax through
    `tf_full_opponent_step`" describes.
    """

    def __init__(self, model: SpatialActorCritic, device: torch.device) -> None:
        self.model = copy.deepcopy(model).to(device).eval()
        for parameter in self.model.parameters():
            parameter.requires_grad_(False)
        self.device = device
        self.calls = 0

    def refresh(self, live: SpatialActorCritic) -> None:
        self.model.load_state_dict(copy.deepcopy(live.state_dict()))
        self.model.eval()

    @torch.no_grad()
    def __call__(
        self,
        obs: np.ndarray,
        masks: np.ndarray,
        plan_masks: np.ndarray,
        phase: np.ndarray,
        active_troll: np.ndarray | None = None,
        seat_view: np.ndarray | None = None,
        needs_action: np.ndarray | None = None,
        **_: object,
    ) -> np.ndarray:
        self.calls += 1
        count = obs.shape[0]
        actions = np.full(count, -1, dtype=np.int32)
        phase = np.asarray(phase)
        waiting = (
            np.asarray(needs_action).astype(bool)
            if needs_action is not None
            else (phase >= 0)
        )
        rows = np.flatnonzero(waiting)
        if not len(rows):
            return actions
        legal = build_legal(masks[rows], plan_masks[rows], phase[rows])
        observations = torch.from_numpy(np.ascontiguousarray(obs[rows])).to(self.device)
        phase_t = torch.from_numpy(phase[rows].astype(np.int64)).to(self.device)
        legal_t = torch.from_numpy(legal).to(self.device).bool()
        logits, _ = combined_logits(self.model, observations, phase_t)
        actions[rows] = (
            masked_logits(logits, legal_t).argmax(dim=-1).cpu().numpy().astype(np.int32)
        )
        return actions


# --------------------------------------------------------------------------- masks


def build_legal(
    masks: np.ndarray, plan_masks: np.ndarray, phase: np.ndarray
) -> np.ndarray:
    """The mask actually used, one 3,146-wide row per mini-step.

    A PLAN row is the 144 plan entries in columns 0..143 and zero above; a TROLL row is the
    13 x 11 x 22 per-cell mask flattened. This is exactly the row the loss re-uses later, so the
    rollout stores it verbatim.
    """

    count = masks.shape[0]
    legal = np.zeros((count, ACTION_SIZE), dtype=np.uint8)
    plan_rows = phase == PHASE_PLAN
    troll_rows = phase == PHASE_TROLL
    if plan_rows.any():
        legal[plan_rows, :PLAN_SIZE] = plan_masks[plan_rows]
    if troll_rows.any():
        legal[troll_rows] = masks[troll_rows].reshape(-1, ACTION_SIZE)
    return legal


# --------------------------------------------------------------------------- the bench gate


def run_bench_gate(
    checkpoint_path: str | Path,
    *,
    script: Path = BENCH_SCRIPT,
    maps: Path | None = None,
    bot: Path | None = None,
    games: int = 0,
    seed: int = 0,
    out_dir: Path | None = None,
    python: str = sys.executable,
    timeout: float = 3600.0,
) -> dict:
    """Play the checkpoint against the champion's compiled file through `bench.py`.

    THE HOOK. `local_claude_1/nn-bot/bench.py` is built by `claude_1` on branch
    `origin/agent/claude_1`. Its CLI today is `--maps --bot --turns --games --seed --policy
    --train-p --out --replays --no-replays --read --game`, and `--policy` accepts only
    `random-legal`: **there is no way to hand it a PyTorch checkpoint yet**. This function looks in
    the bench's own `--help` for one of `BENCH_CHECKPOINT_FLAGS`; if none is there it returns
    `{"status": "unavailable", ...}` and training carries on unharmed.

    The interface it expects once the bench grows one:

        python3 local_claude_1/nn-bot/bench.py --policy-checkpoint <run.pt> \
            --maps <maps.jsonl> --bot <champion.rs> --games N --seed S --out <report.json>

    and a report JSON holding at least `games`, `policy_wins`, `policy_score_mean`,
    `bot_score_mean`, `illegal_commands_total`, `timeouts_total`, `referee_errors_total`,
    `games_with_a_loop` -- the keys today's `bench.py` already writes.
    """

    script = Path(script)
    if not script.exists():
        return {
            "status": "unavailable",
            "reason": f"{script} is not on disk (it lives on branch origin/agent/claude_1)",
        }
    try:
        help_text = subprocess.run(
            [python, str(script), "--help"],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=str(ROOT),
        ).stdout
    except Exception as error:  # pragma: no cover - defensive
        return {"status": "error", "reason": f"bench --help failed: {error!r}"}

    flag = next((name for name in BENCH_CHECKPOINT_FLAGS if name in help_text), None)
    if flag is None:
        return {
            "status": "unavailable",
            "reason": (
                "bench.py has no checkpoint flag "
                f"(tried {list(BENCH_CHECKPOINT_FLAGS)}); its --policy takes only the "
                "random-legal policy today, so a network cannot be benched yet"
            ),
        }

    out_dir = Path(out_dir or (ROOT / "local_claude_1" / "nn-bot" / "results"))
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / f"gate-{Path(checkpoint_path).stem}.json"
    command = [
        python,
        str(script),
        flag,
        str(checkpoint_path),
        "--seed",
        str(seed),
        "--out",
        str(report_path),
        "--no-replays",
    ]
    if maps is not None:
        command += ["--maps", str(maps)]
    if bot is not None:
        command += ["--bot", str(bot)]
    if games:
        command += ["--games", str(games)]
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, timeout=timeout, cwd=str(ROOT)
        )
    except Exception as error:  # pragma: no cover - defensive
        return {"status": "error", "reason": repr(error), "command": command}
    if completed.returncode != 0 or not report_path.exists():
        return {
            "status": "error",
            "reason": f"bench exited {completed.returncode}",
            "stderr": completed.stderr[-2000:],
            "command": command,
        }
    report = json.loads(report_path.read_text())
    games_played = max(1, int(report.get("games", 0)))
    return {
        "status": "ok",
        "command": command,
        "report": str(report_path),
        "games": report.get("games"),
        "win_rate": report.get("policy_wins", 0) / games_played,
        "score_margin": (
            float(report.get("policy_score_mean", 0.0))
            - float(report.get("bot_score_mean", 0.0))
        ),
        "illegal_commands_total": report.get("illegal_commands_total"),
        "timeouts_total": report.get("timeouts_total"),
        "referee_errors_total": report.get("referee_errors_total"),
        "games_with_a_loop": report.get("games_with_a_loop"),
    }


# --------------------------------------------------------------------------- rollout storage


class RolloutBuffer:
    """One update's worth of mini-steps, `[rollout_steps, num_envs]` in every array."""

    def __init__(self, steps: int, envs: int) -> None:
        self.steps = steps
        self.envs = envs
        shape = (steps, envs)
        self.obs = np.zeros(
            (steps, envs, OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH), dtype=np.uint8
        )
        self.legal = np.zeros((steps, envs, ACTION_SIZE), dtype=np.uint8)
        self.phase = np.zeros(shape, dtype=np.int64)
        self.actions = np.zeros(shape, dtype=np.int64)
        self.logprobs = np.zeros(shape, dtype=np.float32)
        self.values = np.zeros(shape, dtype=np.float32)
        self.rewards = np.zeros(shape, dtype=np.float32)
        self.dones = np.zeros(shape, dtype=np.float32)
        self.turn_boundary = np.zeros(shape, dtype=np.uint8)

    @property
    def size(self) -> int:
        return self.steps * self.envs

    def flat(self) -> dict[str, np.ndarray]:
        count = self.size
        return {
            "obs": self.obs.reshape(count, OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH),
            "legal": self.legal.reshape(count, ACTION_SIZE),
            "phase": self.phase.reshape(count),
            "actions": self.actions.reshape(count),
            "logprobs": self.logprobs.reshape(count),
            "values": self.values.reshape(count),
        }


# --------------------------------------------------------------------------- the run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="masked PPO over the full-game Troll Farm environment (card "
        "20260829-nn-bot-way-b, Phase 3)"
    )
    parser.add_argument("--run-name", default="ppo-full-1")
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "local_claude_1" / "nn-bot" / "runs"),
        help="checkpoints and the run summary land here",
    )
    parser.add_argument("--seed", type=int, default=1_000_000)
    parser.add_argument("--num-envs", type=int, default=32)
    parser.add_argument("--rollout-steps", type=int, default=128)
    parser.add_argument(
        "--total-turn-steps",
        type=int,
        default=200_000_000,
        help="the budget, counted in mini-step decisions (one network decision each)",
    )
    parser.add_argument("--minibatch-size", type=int, default=512)
    parser.add_argument("--update-epochs", type=int, default=4)
    parser.add_argument("--learning-rate", type=float, default=2.5e-4)
    parser.add_argument("--anneal-lr", action="store_true", default=True)
    parser.add_argument("--no-anneal-lr", dest="anneal_lr", action="store_false")
    parser.add_argument("--gamma", type=float, default=0.997)
    parser.add_argument("--gae-lambda", type=float, default=0.95)
    parser.add_argument("--clip-coef", type=float, default=0.2)
    parser.add_argument("--entropy-coef", type=float, default=0.01)
    parser.add_argument("--value-coef", type=float, default=0.5)
    parser.add_argument("--max-grad-norm", type=float, default=0.5)
    parser.add_argument("--target-kl", type=float, default=0.03)
    parser.add_argument(
        "--reward-scale",
        type=float,
        default=0.02,
        help="every reward is multiplied by this before the advantage; the end-of-game score "
        "difference can be a hundred points and the value head is one small linear layer",
    )
    parser.add_argument("--threads", type=int, default=14)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")

    parser.add_argument("--initial-checkpoint", default=None, help="start from the clone")
    parser.add_argument(
        "--anchor-checkpoint",
        default=None,
        help="the behaviour-cloned network the policy is pulled towards",
    )
    parser.add_argument("--anchor-coef", type=float, default=0.1)
    parser.add_argument("--anchor-coef-final", type=float, default=0.0)
    parser.add_argument("--anchor-decay-steps", type=int, default=50_000_000)

    parser.add_argument("--maps", default=str(DEFAULT_MAPS))
    parser.add_argument("--wood-shaping", type=float, default=0.5)
    parser.add_argument("--end-wood", type=float, default=3.5)
    parser.add_argument(
        "--opponent-weights",
        default='{"secure_orchard": 1.0}',
        help='JSON over the seven pool ids, e.g. \'{"secure_orchard": 2, "python_frozen": 1}\'',
    )
    parser.add_argument(
        "--frozen-checkpoint",
        default=None,
        help="the initial python_frozen self-play opponent; refreshed from the live policy",
    )
    parser.add_argument("--frozen-refresh-updates", type=int, default=20)
    parser.add_argument(
        "--reward-credit",
        choices=("executing", "as-returned"),
        default="executing",
        help="'executing' keeps the turn's reward only on the mini-step that executed the turn "
        "(the card's rule); 'as-returned' trusts the environment's per-mini-step reward",
    )
    parser.add_argument("--checkpoint-every", type=int, default=25)
    parser.add_argument("--gate-every", type=int, default=0, help="0 = never")
    parser.add_argument("--gate-games", type=int, default=0)
    parser.add_argument("--gate-maps", default=None)
    parser.add_argument("--gate-bot", default=None)
    parser.add_argument(
        "--env",
        choices=("full", "fake"),
        default="full",
        help="'fake' uses local_claude_1/nn-bot/fake_full_env.py -- for the tests and for a "
        "dry run before the Rust library exists",
    )
    parser.add_argument("--episode-window", type=int, default=1000)
    return parser


def load_policy(path: str | None, device: torch.device) -> tuple[SpatialActorCritic, str | None]:
    """A plan-head network, restored from a checkpoint when one is given.

    A July checkpoint has no `plan.*` keys. That is allowed: the trunk, the per-cell head and the
    value head are restored and the plan head starts fresh, which is the honest way to begin PPO
    from a network that never had a plan head. Any other missing or unexpected key is an error.
    """

    model = SpatialActorCritic(plan_head=True)
    digest = None
    if path:
        checkpoint = torch.load(Path(path), map_location="cpu", weights_only=False)
        state = checkpoint["model"] if "model" in checkpoint else checkpoint
        missing, unexpected = model.load_state_dict(state, strict=False)
        stray = [name for name in missing if not name.startswith("plan.")]
        if stray or unexpected:
            raise SystemExit(
                f"checkpoint {path} does not fit SpatialActorCritic(plan_head=True): "
                f"missing={stray}, unexpected={list(unexpected)}"
            )
        if missing:
            print(
                json.dumps(
                    {
                        "event": "note",
                        "message": "the checkpoint has no plan head; it starts freshly initialised",
                        "checkpoint": str(path),
                        "fresh_keys": sorted(missing),
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
        digest = sha256(Path(path))
    return model.to(device), digest


def load_anchor(path: str, device: torch.device) -> tuple[SpatialActorCritic, str, bool]:
    """The clone, frozen. Returns the model, its sha256 and whether it has a plan head.

    A clone without a plan head still anchors the per-cell head; the plan rows are then left out
    of the anchor term and the log says so.
    """

    checkpoint = torch.load(Path(path), map_location="cpu", weights_only=False)
    state = checkpoint["model"] if "model" in checkpoint else checkpoint
    has_plan = any(key.startswith("plan.") for key in state)
    model = SpatialActorCritic(plan_head=has_plan)
    model.load_state_dict(state, strict=True)
    model.to(device).eval()
    for parameter in model.parameters():
        parameter.requires_grad_(False)
    return model, sha256(Path(path)), has_plan


def train(args) -> dict:
    torch.manual_seed(args.seed)
    np.random.seed(args.seed % (2**32))
    torch.set_num_threads(max(1, args.threads))
    try:
        torch.set_num_interop_threads(min(4, max(1, args.threads)))
    except RuntimeError:
        # torch allows this only once per process; a second run inside the same interpreter
        # (the tests) keeps whatever was set first.
        pass
    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise SystemExit("--device cuda requires an available CUDA device")
    rng = np.random.default_rng(args.seed)

    batch_size = args.num_envs * args.rollout_steps
    if batch_size % args.minibatch_size:
        raise SystemExit("the rollout batch must divide by the minibatch size")
    total_updates = max(1, args.total_turn_steps // batch_size)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    model, initial_sha = load_policy(args.initial_checkpoint, device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate, eps=1e-5)

    anchor = anchor_sha = None
    anchor_has_plan = False
    if args.anchor_checkpoint:
        anchor, anchor_sha, anchor_has_plan = load_anchor(args.anchor_checkpoint, device)

    frozen = None
    frozen_sha = None
    if args.frozen_checkpoint:
        seed_model, frozen_sha = load_policy(args.frozen_checkpoint, device)
        frozen = FrozenOpponent(seed_model, device)
    else:
        frozen = FrozenOpponent(model, device)

    config = {
        **vars(args),
        "batch_size": batch_size,
        "total_updates": total_updates,
        "parameter_count": sum(p.numel() for p in model.parameters()),
        "torch_version": torch.__version__,
        "initial_checkpoint_sha256": initial_sha,
        "anchor_checkpoint_sha256": anchor_sha,
        "anchor_has_plan_head": anchor_has_plan,
        "frozen_checkpoint_sha256": frozen_sha,
        "turn_step_definition": "one learner mini-step decision (PLAN or TROLL)",
    }
    print(json.dumps({"event": "start", **config}, sort_keys=True, default=str), flush=True)

    buffer = RolloutBuffer(args.rollout_steps, args.num_envs)
    episode_window: list[dict] = []
    logs: list[dict] = []
    gates: list[dict] = []
    turn_steps = 0
    turns_completed = 0
    start_wall = time.perf_counter()

    env = make_env(args, frozen)
    try:
        for update in range(1, total_updates + 1):
            update_start = time.perf_counter()
            for step_index in range(args.rollout_steps):
                phase_np = np.asarray(env.phase)
                if (phase_np == PHASE_EXTERNAL_WAIT).any():
                    raise RuntimeError(
                        "phase 2 EXTERNAL_WAIT reached the trainer; ENV-API.md's FullVecEnv.step "
                        "is supposed to drive the python_frozen opponent itself"
                    )
                legal_np = build_legal(
                    np.asarray(env.masks), np.asarray(env.plan_masks), phase_np
                )
                if not legal_np.any(axis=1).all():
                    raise RuntimeError("a mini-step arrived with an empty action mask")

                np.copyto(buffer.obs[step_index], env.obs)
                buffer.legal[step_index] = legal_np
                buffer.phase[step_index] = phase_np

                observations = torch.from_numpy(np.ascontiguousarray(env.obs)).to(device)
                phase_t = torch.from_numpy(phase_np.astype(np.int64)).to(device)
                legal_t = torch.from_numpy(legal_np).to(device).bool()
                with torch.no_grad():
                    logits, values = combined_logits(model, observations, phase_t)
                    distribution = Categorical(logits=masked_logits(logits, legal_t))
                    actions = distribution.sample()
                    logprobs = distribution.log_prob(actions)

                actions_np = actions.cpu().numpy().astype(np.int64)
                buffer.actions[step_index] = actions_np
                buffer.logprobs[step_index] = logprobs.cpu().numpy()
                buffer.values[step_index] = values.cpu().numpy()

                result = env.step(actions_np.astype(np.int32, copy=False))
                rewards, info = unpack_step(result, args.num_envs)
                dones = info_field(info, "dones", "done").astype(np.float32)
                try:
                    completed = info_field(
                        info, "turn_completed", "turns_completed", "turn_done"
                    ).astype(np.uint8)
                except AttributeError:
                    # Documented fallback: without turn_completed, a turn executed exactly when
                    # the next mini-step is a PLAN again (or the episode ended).
                    completed = (
                        (np.asarray(env.phase) == PHASE_PLAN) | (dones > 0)
                    ).astype(np.uint8)
                boundary = ((completed > 0) | (dones > 0)).astype(np.uint8)

                if args.reward_credit == "executing":
                    rewards = np.where(completed > 0, rewards, np.float32(0.0))
                buffer.rewards[step_index] = rewards * args.reward_scale
                buffer.dones[step_index] = dones
                buffer.turn_boundary[step_index] = boundary
                turn_steps += args.num_envs
                turns_completed += int((completed > 0).sum())

                for slot in np.flatnonzero(dones > 0):
                    own = float(info_field(info, "score_own", "scores_own")[slot])
                    opponent = float(info_field(info, "score_opp", "scores_opp")[slot])
                    episode_window.append(
                        {
                            "return": float(
                                info_field(info, "episode_returns", "returns")[slot]
                            ),
                            "turns": int(
                                info_field(info, "episode_turns", "turns")[slot]
                            ),
                            "win": int(info_field(info, "wins", "win")[slot]),
                            "score_own": own,
                            "score_opp": opponent,
                            "margin": own - opponent,
                            "opponent_id": int(
                                info_field(info, "opponent_ids", "opponents")[slot]
                            ),
                            "illegal": int(
                                info_field(
                                    info, "illegal_commands", "illegal"
                                )[slot]
                            ),
                        }
                    )
                episode_window = episode_window[-args.episode_window :]
            rollout_elapsed = time.perf_counter() - update_start

            phase_np = np.asarray(env.phase)
            with torch.no_grad():
                _, bootstrap = combined_logits(
                    model,
                    torch.from_numpy(np.ascontiguousarray(env.obs)).to(device),
                    torch.from_numpy(phase_np.astype(np.int64)).to(device),
                )
            advantages, returns = compute_gae(
                buffer.rewards,
                buffer.values,
                buffer.dones,
                buffer.turn_boundary,
                bootstrap.cpu().numpy(),
                args.gamma,
                args.gae_lambda,
            )

            flat = buffer.flat()
            flat_advantages = advantages.reshape(buffer.size)
            flat_returns = returns.reshape(buffer.size)
            coefficient = anchor_coefficient(args, turn_steps)

            indices = np.arange(buffer.size)
            clip_fractions: list[float] = []
            approx_kl = 0.0
            policy_loss_value = value_loss_value = entropy_value = 0.0
            anchor_loss_value = anchor_agreement_value = None
            epochs_run = 0
            for epoch in range(args.update_epochs):
                rng.shuffle(indices)
                for start in range(0, buffer.size, args.minibatch_size):
                    rows = indices[start : start + args.minibatch_size]
                    mb_obs = torch.from_numpy(flat["obs"][rows]).to(device)
                    mb_legal = torch.from_numpy(flat["legal"][rows]).to(device).bool()
                    mb_phase = torch.from_numpy(flat["phase"][rows]).to(device)
                    mb_actions = torch.from_numpy(flat["actions"][rows]).to(device)
                    mb_old_logprobs = torch.from_numpy(flat["logprobs"][rows]).to(device)

                    logits, new_value = combined_logits(model, mb_obs, mb_phase)
                    policy_masked = masked_logits(logits, mb_legal)
                    distribution = Categorical(logits=policy_masked)
                    new_logprob = distribution.log_prob(mb_actions)
                    entropy = distribution.entropy()

                    log_ratio = new_logprob - mb_old_logprobs
                    ratio = log_ratio.exp()
                    with torch.no_grad():
                        approx_kl = float(((ratio - 1.0) - log_ratio).mean())
                        clip_fractions.append(
                            float(((ratio - 1.0).abs() > args.clip_coef).float().mean())
                        )

                    mb_advantages = torch.from_numpy(flat_advantages[rows]).to(device)
                    mb_advantages = (mb_advantages - mb_advantages.mean()) / (
                        mb_advantages.std() + 1e-8
                    )
                    policy_loss = torch.maximum(
                        -mb_advantages * ratio,
                        -mb_advantages
                        * ratio.clamp(1.0 - args.clip_coef, 1.0 + args.clip_coef),
                    ).mean()
                    value_loss = 0.5 * (
                        new_value - torch.from_numpy(flat_returns[rows]).to(device)
                    ).pow(2).mean()
                    entropy_loss = entropy.mean()
                    loss = (
                        policy_loss
                        - args.entropy_coef * entropy_loss
                        + args.value_coef * value_loss
                    )

                    if anchor is not None and coefficient != 0.0:
                        keep = (
                            torch.ones_like(mb_phase, dtype=torch.bool)
                            if anchor_has_plan
                            else (mb_phase == PHASE_TROLL)
                        )
                        if bool(keep.any()):
                            with torch.no_grad():
                                anchor_logits, _ = combined_logits(
                                    anchor, mb_obs[keep], mb_phase[keep]
                                )
                                anchor_masked = masked_logits(
                                    anchor_logits, mb_legal[keep]
                                )
                            kl, agreement = anchor_kl(
                                policy_masked[keep], anchor_masked, mb_legal[keep]
                            )
                            loss = loss + coefficient * kl
                            anchor_loss_value = float(kl.detach())
                            anchor_agreement_value = float(agreement.detach())

                    optimizer.zero_grad(set_to_none=True)
                    loss.backward()
                    nn.utils.clip_grad_norm_(model.parameters(), args.max_grad_norm)
                    optimizer.step()
                    policy_loss_value = float(policy_loss.detach())
                    value_loss_value = float(value_loss.detach())
                    entropy_value = float(entropy_loss.detach())
                epochs_run = epoch + 1
                if args.target_kl > 0 and approx_kl > args.target_kl:
                    break

            if args.anneal_lr:
                optimizer.param_groups[0]["lr"] = args.learning_rate * max(
                    0.0, 1.0 - update / total_updates
                )
            if (
                args.frozen_refresh_updates > 0
                and update % args.frozen_refresh_updates == 0
            ):
                frozen.refresh(model)

            update_elapsed = time.perf_counter() - update_start
            wall = time.perf_counter() - start_wall
            recent = episode_window
            log = {
                "event": "update",
                "update": update,
                "turn_steps": turn_steps,
                "turns_completed": turns_completed,
                "policy_loss": policy_loss_value,
                "value_loss": value_loss_value,
                "entropy": entropy_value,
                "anchor_coef": coefficient,
                "anchor_loss": anchor_loss_value,
                "anchor_agreement": anchor_agreement_value,
                "approx_kl": approx_kl,
                "clip_fraction": float(np.mean(clip_fractions)) if clip_fractions else None,
                "explained_variance": explained_variance(
                    flat["values"], flat_returns
                ),
                "epochs_run": epochs_run,
                "learning_rate": optimizer.param_groups[0]["lr"],
                "episodes_recent": len(recent),
                "mean_episode_return": (
                    float(np.mean([row["return"] for row in recent])) if recent else None
                ),
                "mean_referee_margin": (
                    float(np.mean([row["margin"] for row in recent])) if recent else None
                ),
                "win_rate": (
                    float(np.mean([row["win"] for row in recent])) if recent else None
                ),
                "mean_episode_turns": (
                    float(np.mean([row["turns"] for row in recent])) if recent else None
                ),
                "plan_step_fraction": float(
                    (buffer.phase == PHASE_PLAN).mean()
                ),
                "rollout_turn_steps_per_second": batch_size / max(rollout_elapsed, 1e-9),
                "turn_steps_per_second": batch_size / max(update_elapsed, 1e-9),
                "overall_turn_steps_per_second": turn_steps / max(wall, 1e-9),
                "wall_seconds": wall,
            }
            logs.append(log)
            print(json.dumps(log, sort_keys=True), flush=True)

            checkpoint_path = None
            if args.checkpoint_every > 0 and (
                update % args.checkpoint_every == 0 or update == total_updates
            ):
                checkpoint_path = save_checkpoint(
                    output_dir, args, model, optimizer, config, log, gates
                )
            if args.gate_every > 0 and update % args.gate_every == 0:
                if checkpoint_path is None:
                    checkpoint_path = save_checkpoint(
                        output_dir, args, model, optimizer, config, log, gates
                    )
                gate = run_bench_gate(
                    checkpoint_path,
                    maps=Path(args.gate_maps) if args.gate_maps else None,
                    bot=Path(args.gate_bot) if args.gate_bot else None,
                    games=args.gate_games,
                    seed=args.seed,
                    out_dir=output_dir / "gates",
                )
                gate["update"] = update
                gate["turn_steps"] = turn_steps
                gate["checkpoint"] = str(checkpoint_path)
                gates.append(gate)
                print(json.dumps({"event": "gate", **gate}, sort_keys=True), flush=True)
    finally:
        close = getattr(env, "close", None)
        if callable(close):
            close()

    elapsed = time.perf_counter() - start_wall
    summary = {
        "event": "complete",
        "run_name": args.run_name,
        "config": config,
        "turn_steps": turn_steps,
        "turns_completed": turns_completed,
        "updates_completed": len(logs),
        "elapsed_wall_seconds": elapsed,
        "overall_turn_steps_per_second": turn_steps / max(elapsed, 1e-9),
        "gates": gates,
        "logs": logs,
    }
    summary_path = output_dir / f"{args.run_name}-training-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps(summary, sort_keys=True, default=str), flush=True)
    return summary


def save_checkpoint(
    output_dir: Path,
    args,
    model: SpatialActorCritic,
    optimizer: torch.optim.Optimizer,
    config: dict,
    log: dict,
    gates: list[dict],
) -> Path:
    """July's four-key checkpoint: model, optimizer, config, evaluation."""

    checkpoint = {
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
        "config": config,
        "evaluation": {
            "update": log["update"],
            "turn_steps": log["turn_steps"],
            "turns_completed": log["turns_completed"],
            "mean_episode_return": log["mean_episode_return"],
            "mean_referee_margin": log["mean_referee_margin"],
            "win_rate": log["win_rate"],
            "entropy": log["entropy"],
            "explained_variance": log["explained_variance"],
            "gates": gates[-3:],
        },
    }
    path = output_dir / f"{args.run_name}-update{log['update']:06d}.pt"
    torch.save(checkpoint, path)
    torch.save(checkpoint, output_dir / f"{args.run_name}-latest.pt")
    return path


def main(argv: list[str] | None = None) -> dict:
    args = build_parser().parse_args(argv)
    return train(args)


if __name__ == "__main__":
    main()
