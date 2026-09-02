#!/usr/bin/env python3
"""Price step 5's levers offline, from one collected rollout."""

from __future__ import annotations

import dataclasses
import importlib.util
import pathlib
import sys
from typing import Any

import numpy as np


@dataclasses.dataclass(frozen=True)
class WindowCut:
    """One rollout window and the bootstrap value at its own edge."""

    start: int
    stop: int
    next_value: np.ndarray


def window_cuts(
    window: int, values: np.ndarray, final_next_value: np.ndarray
) -> list[WindowCut]:
    """Cut a collected buffer into contiguous windows of `window` steps.

    Each cut bootstraps from the stored value of the step just past its edge, so a short window
    is handed exactly the information a short rollout would have had. Only the last cut, whose
    edge is the buffer's own edge, uses the recorded `final_next_value`.
    """

    num_steps = values.shape[0]
    if window <= 0 or num_steps % window:
        raise ValueError(
            f"window {window} must divide the buffer's {num_steps} steps evenly"
        )
    cuts = []
    for start in range(0, num_steps, window):
        stop = start + window
        edge = final_next_value if stop == num_steps else values[stop]
        cuts.append(WindowCut(start, stop, np.asarray(edge, dtype=np.float32)))
    return cuts


ROOT = pathlib.Path(__file__).resolve().parents[2]
TRAINER = ROOT / "local_claude_1" / "nn-bot" / "train_ppo_full.py"

_TRAINER_MODULE = None


def load_trainer():
    """Load the trainer module, so the decomposition of record is the one that runs here.

    The numbers this instrument reports must be comparable with the Gate-0 telemetry, which
    means reusing `compute_gae` and `rollout_credit_telemetry` themselves rather than a
    re-implementation that could drift from them.
    """

    global _TRAINER_MODULE
    if _TRAINER_MODULE is None:
        spec = importlib.util.spec_from_file_location("train_ppo_full", TRAINER)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        _TRAINER_MODULE = module
    return _TRAINER_MODULE


@dataclasses.dataclass(frozen=True)
class Rollout:
    """One collected buffer: (steps, envs) arrays plus the value at the buffer's own edge."""

    rewards: np.ndarray
    values: np.ndarray
    dones: np.ndarray
    turn_boundary: np.ndarray
    phase: np.ndarray
    final_next_value: np.ndarray


def price_window(
    rollout: Rollout, window: int, gamma: float, gae_lambda: float
) -> dict[str, dict[str, float | int | None]]:
    """Measure what the learning signal is made of when the rollout is `window` steps long."""

    trainer = load_trainer()
    cuts = window_cuts(window, rollout.values, rollout.final_next_value)
    totals = {
        name: {"rows": 0, "reward": 0.0, "critic": 0.0, "traced": 0.0}
        for name in ("plan", "troll")
    }
    for cut in cuts:
        piece = slice(cut.start, cut.stop)
        advantages, _ = trainer.compute_gae(
            rollout.rewards[piece],
            rollout.values[piece],
            rollout.dones[piece],
            rollout.turn_boundary[piece],
            cut.next_value,
            gamma,
            gae_lambda,
        )
        telemetry = trainer.rollout_credit_telemetry(
            rollout.rewards[piece],
            rollout.values[piece],
            rollout.dones[piece],
            rollout.turn_boundary[piece],
            cut.next_value,
            rollout.phase[piece],
            advantages,
            gamma,
            gae_lambda,
        )
        for name, block in totals.items():
            measured = telemetry[name]
            rows = int(measured["rows"])
            block["rows"] += rows
            block["reward"] += float(measured["reward_component_abs_sum"])
            block["critic"] += float(measured["critic_component_abs_sum"])
            if measured["terminal_traced_fraction"] is not None:
                block["traced"] += float(measured["terminal_traced_fraction"]) * rows

    priced: dict[str, dict[str, float | int | None]] = {}
    for name, block in totals.items():
        source = block["reward"] + block["critic"]
        priced[name] = {
            "rows": block["rows"],
            "observed_reward_share": block["reward"] / source if source > 0 else None,
            "critic_share": block["critic"] / source if source > 0 else None,
            "terminal_traced_fraction": (
                block["traced"] / block["rows"] if block["rows"] else None
            ),
        }
    return priced


@dataclasses.dataclass(frozen=True)
class Collected:
    """A rollout plus the two things that prove a replay was the same game."""

    rollout: Rollout
    actions: np.ndarray
    state_hash: np.ndarray


def collect(env, decide, steps: int) -> Collected:
    """Step `env` for `steps` mini-steps, recording what the credit decomposition needs.

    `decide(env) -> (actions, values)` is injected so the same collection serves a network-free
    test and the clone.
    """

    width = env.num_envs
    rewards = np.zeros((steps, width), dtype=np.float32)
    values = np.zeros((steps, width), dtype=np.float32)
    dones = np.zeros((steps, width), dtype=np.float32)
    turn_boundary = np.zeros((steps, width), dtype=np.float32)
    phase = np.zeros((steps, width), dtype=np.int64)
    actions = np.zeros((steps, width), dtype=np.int32)
    state_hash = np.zeros((steps, width), dtype=np.uint64)

    for step in range(steps):
        phase[step] = env.phase
        chosen, valued = decide(env)
        actions[step] = chosen
        values[step] = valued
        reward, info = env.step(chosen)
        # `--reward-credit executing`, the trainer's default and the setting every run of
        # record used: a turn's reward is kept only on the mini-step that executed the turn.
        # The within-turn trace factor of 1.0 carries it to that turn's other mini-steps.
        rewards[step] = np.where(
            np.asarray(info.turn_completed) > 0, reward, np.float32(0.0)
        )
        dones[step] = info.dones
        turn_boundary[step] = info.turn_completed
        state_hash[step] = info.state_hash

    _, final_next_value = decide(env)
    return Collected(
        rollout=Rollout(
            rewards=rewards,
            values=values,
            dones=dones,
            turn_boundary=turn_boundary,
            phase=phase,
            final_next_value=np.asarray(final_next_value, dtype=np.float32),
        ),
        actions=actions,
        state_hash=state_hash,
    )


def clone_decider(checkpoint, train_scope: str = "plan-critic", seed: int = 1):
    """Decide with the clone exactly as the trainer's rollout loop does.

    Same `combined_logits` / `masked_logits` / `rollout_actions` path and the same scope, so the
    rows this instrument prices are the rows a real run would have collected.
    """

    import torch  # noqa: PLC0415  (kept out of the module's import cost for the pure tests)

    trainer = load_trainer()
    device = torch.device("cpu")
    model, _ = trainer.load_policy(str(checkpoint), device)
    model.eval()
    generator_seeded = torch.manual_seed(seed)
    del generator_seeded

    def decide(env):
        phase_np = np.asarray(env.phase)
        legal_np = trainer.build_legal(
            np.asarray(env.masks), np.asarray(env.plan_masks), phase_np
        )
        observations = torch.from_numpy(np.ascontiguousarray(env.obs)).to(device)
        phase_t = torch.from_numpy(phase_np.astype(np.int64)).to(device)
        legal_t = torch.from_numpy(legal_np).to(device).bool()
        with torch.no_grad():
            logits, values = trainer.combined_logits(model, observations, phase_t)
            actions, _ = trainer.rollout_actions(
                trainer.masked_logits(logits, legal_t), phase_t, train_scope
            )
        return (
            actions.cpu().numpy().astype(np.int64),
            values.cpu().numpy().astype(np.float32),
        )

    return decide


@dataclasses.dataclass(frozen=True)
class Replayed:
    """What a recorded action sequence pays under a different reward split."""

    rewards: np.ndarray
    dones: np.ndarray
    turn_boundary: np.ndarray
    state_hash: np.ndarray


def replay(env, actions: np.ndarray) -> Replayed:
    """Step `env` through a recorded action sequence, recording only what the reward split moves.

    No network runs here: the actions are fixed, so the game is fixed, and the only thing that
    can differ from the collection is what the environment paid for it.
    """

    steps, width = actions.shape
    rewards = np.zeros((steps, width), dtype=np.float32)
    dones = np.zeros((steps, width), dtype=np.float32)
    turn_boundary = np.zeros((steps, width), dtype=np.float32)
    state_hash = np.zeros((steps, width), dtype=np.uint64)

    for step in range(steps):
        reward, info = env.step(np.asarray(actions[step], dtype=np.int32))
        completed = np.asarray(info.turn_completed)
        rewards[step] = np.where(completed > 0, reward, np.float32(0.0))
        dones[step] = info.dones
        turn_boundary[step] = completed
        state_hash[step] = info.state_hash

    return Replayed(
        rewards=rewards,
        dones=dones,
        turn_boundary=turn_boundary,
        state_hash=state_hash,
    )


def price_tail(
    rollout: Rollout, burn_in: int, window: int, gamma: float, gae_lambda: float
) -> dict[str, dict[str, float | int | None]]:
    """Price only the rows after `burn_in`, which is where the environments have staggered."""

    tail = Rollout(
        rewards=rollout.rewards[burn_in:],
        values=rollout.values[burn_in:],
        dones=rollout.dones[burn_in:],
        turn_boundary=rollout.turn_boundary[burn_in:],
        phase=rollout.phase[burn_in:],
        final_next_value=rollout.final_next_value,
    )
    return price_window(tail, window, gamma, gae_lambda)


def _split_pair(text: str) -> tuple[float, float]:
    shaping, _, end = text.partition("+")
    return float(shaping), float(end)


def main(argv: list[str] | None = None) -> int:
    """Collect once with the clone, then price every split and window on that one collection."""

    import argparse  # noqa: PLC0415
    import hashlib  # noqa: PLC0415
    import json  # noqa: PLC0415
    import time  # noqa: PLC0415

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clone", required=True)
    parser.add_argument("--maps", required=True)
    parser.add_argument("--num-envs", type=int, default=64)
    parser.add_argument("--seed", type=int, default=909)
    parser.add_argument("--burn-in", type=int, default=896)
    parser.add_argument("--steps", type=int, default=1024)
    parser.add_argument("--split", action="append", default=None, help="shaping+end, e.g. 2+2")
    parser.add_argument("--window", action="append", type=int, default=None)
    parser.add_argument("--gamma", type=float, default=0.999)
    parser.add_argument("--gae-lambda", type=float, default=0.95)
    parser.add_argument("--train-scope", default="plan-critic")
    parser.add_argument("--opponent", default="champion_exact")
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    splits = [_split_pair(text) for text in (args.split or ["0+4", "2+2", "0.5+3.5"])]
    windows = args.window or [32, 128]

    import torch  # noqa: PLC0415

    torch.set_num_threads(args.threads)
    if str(ROOT) not in sys.path:  # the repo root, so `cgauto` imports when run as a script
        sys.path.insert(0, str(ROOT))
    from cgauto.rl_full_env import FullVecEnv  # noqa: PLC0415

    maps = pathlib.Path(args.maps)
    weights = {args.opponent: 1.0}

    def build(shaping: float, end: float):
        return FullVecEnv(
            args.num_envs, args.seed, maps, weights, wood_shaping=shaping, end_wood=end
        )

    started = time.perf_counter()
    decide = clone_decider(args.clone, train_scope=args.train_scope, seed=args.seed)
    reference = splits[0]
    with build(*reference) as env:
        collected = collect(env, decide, args.burn_in + args.steps)
    collect_seconds = time.perf_counter() - started

    rewards_by_split = {reference: collected.rollout.rewards}
    identical_game = {reference: True}
    for shaping, end in splits[1:]:
        with build(shaping, end) as env:
            again = replay(env, collected.actions)
        identical_game[(shaping, end)] = bool(
            np.array_equal(again.state_hash, collected.state_hash)
            and np.array_equal(again.turn_boundary, collected.rollout.turn_boundary)
            and np.array_equal(again.dones, collected.rollout.dones)
        )
        rewards_by_split[(shaping, end)] = again.rewards

    priced: dict[str, Any] = {}
    for (shaping, end), rewards in rewards_by_split.items():
        rollout = dataclasses.replace(collected.rollout, rewards=rewards)
        tail = slice(args.burn_in, None)
        label = f"{shaping:g}+{end:g}"
        priced[label] = {
            "identical_game": identical_game[(shaping, end)],
            "nonzero_reward_rows": int(np.count_nonzero(rewards[tail])),
            "reward_abs_sum": float(np.abs(rewards[tail]).sum()),
            "windows": {
                str(window): price_tail(
                    rollout, args.burn_in, window, args.gamma, args.gae_lambda
                )
                for window in windows
            },
        }

    result = {
        "schema": "troll-farm-lever-price-v1",
        "clone_sha256": hashlib.sha256(
            pathlib.Path(args.clone).read_bytes()
        ).hexdigest(),
        "argv": sys.argv[1:] if argv is None else argv,
        "settings": {
            "num_envs": args.num_envs,
            "seed": args.seed,
            "burn_in": args.burn_in,
            "steps": args.steps,
            "gamma": args.gamma,
            "gae_lambda": args.gae_lambda,
            "train_scope": args.train_scope,
            "opponent": args.opponent,
            "reward_credit": "executing",
        },
        "collect_seconds": collect_seconds,
        "turns_completed": int(collected.rollout.turn_boundary[args.burn_in:].sum()),
        "episode_endings": int(collected.rollout.dones[args.burn_in:].sum()),
        "splits": priced,
    }
    pathlib.Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True))

    print(f"clone {result['clone_sha256'][:12]}  rows after burn-in: "
          f"{args.steps * args.num_envs}  turns {result['turns_completed']}  "
          f"endings {result['episode_endings']}")
    for label, block in priced.items():
        for window, classes in block["windows"].items():
            plan = classes["plan"]
            share = plan["observed_reward_share"]
            traced = plan["terminal_traced_fraction"]
            print(
                f"  split {label:>9}  window {window:>3}  "
                f"plan observed-reward share "
                f"{'n/a' if share is None else format(share * 100, '6.2f') + ' %'}"
                f"   terminal-traced {traced * 100:5.2f} %"
                f"   reward rows {block['nonzero_reward_rows']}"
                f"   same game {block['identical_game']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
