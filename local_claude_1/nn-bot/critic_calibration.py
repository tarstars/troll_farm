#!/usr/bin/env python3
"""Is the critic's "how good is this position?" number true -- measured against what happened.

Card: `coordination/tasks/20260829-nn-bot-way-b.md`.
Charter: `coordination/messages/local_claude_1/20260831T074500Z-20260829-nn-bot-way-b-gate0-handoff.md`
(Gate 0, claude_1's half, delivery 2). Asked for by chatgpt_1's review of 2026-08-31, section 5.

Plain words for the owner
-------------------------
The network carries a *critic*: at every decision it also outputs one number, its estimate of how
the game will end from here. PPO uses that number twice -- as the baseline the advantage is
measured against, and as the target the value loss fits -- so if it is wrong, the training signal
is wrong.

The trainer already logs `explained_variance`, but it computes it against **its own bootstrapped
returns**: the critic is being marked against a target that contains the critic's own opinion. A
number near 0.9 there means "self-consistent", not "true". This program marks it against what
actually happened instead: it plays complete games, and for every position the network saw it
compares the critic's prediction with the **realized return-to-go** -- the rewards that really did
arrive afterwards, under training's own reward definition and scale, discounted the trainer's way.

Then it reports, overall and sliced:

* **slope** and **intercept** of a least-squares line of the realized return on the prediction. A
  perfect critic gives slope 1 and intercept 0. Slope below 1 means the critic exaggerates the
  spread of outcomes; slope above 1 means it is too timid. The intercept is its bias.
* **correlation** -- does the prediction move with the outcome at all (the ranking question)?
* **explained variance** -- `1 - Var(realized - predicted) / Var(realized)`. Unlike the
  correlation this punishes bias and scale error. 0 means "no better than predicting the average",
  and it can be negative.
* **bias** -- mean predicted minus mean realized, in reward units.

The slices are the ones the review asked for: **game-turn bucket** (is it blind early and sharp
late?), **map size** (does it transfer across the four board sizes?) and **seat** (does it know
which side of the board it is on?).

Nothing here trains, submits, or touches the platform. The checkpoint file is never written to and
the network is used under `torch.no_grad()` throughout.

What "the realized return-to-go" is, exactly
--------------------------------------------
The trainer pays a turn's reward once, on the mini-step that executes the turn, multiplies it by
`--reward-scale`, and discounts across turn boundaries only (no time passes between the plan row
and the troll rows of one turn -- `compute_gae`'s rule). So for a stored row `t`:

    G_t = r_t + d_t * G_{t+1},   d_t = gamma if row t executed a turn else 1.0

with `G` past the end of the episode equal to zero, because the episode is played to its **real
end** -- the whole point of the exercise is that no bootstrap enters the target. Rows belonging to
an episode that had not finished when collection stopped are discarded, and the report says how
many.

The undiscounted sum is reported next to the discounted one, because with gamma near 1 the two
answer slightly different questions and the difference is worth seeing.

Flags
-----
Like `grad_decompose.py`, this takes **the trainer's own argument parser** and adds its own, so a
run's command line can be pasted in and the measurement is made under that run's reward settings
(`--reward-scale`, `--reward-credit`, `--gamma`, `--wood-shaping`, `--end-wood`, the opponent pool
and the maps). `--initial-checkpoint` is the checkpoint under test.

Example (the fake environment, no Rust library and no checkpoint needed):

    PYTHONPATH=. /home/tarstars/venvs/nn-bot/bin/python local_claude_1/nn-bot/critic_calibration.py \
        --env fake --num-envs 8 --episodes 8 --decoding argmax \
        --maps /nonexistent/maps.jsonl --label smoke --out /tmp/calibration.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torch.distributions.categorical import Categorical

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cgauto.train_level1_ppo import sha256  # noqa: E402


def load_trainer():
    """`train_ppo_full.py` from the neighbouring file (the directory name has a hyphen in it, so
    it is not an importable package -- the module is loaded by path, as the tests do)."""

    path = Path(__file__).resolve().parent / "train_ppo_full.py"
    spec = importlib.util.spec_from_file_location("nn_bot_train_ppo_full", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


tpf = load_trainer()

#: The trainer's own objects, not copies of its source: if the trainer changes how an observation
#: enters the network or how a turn's reward is credited, this measurement changes with it.
combined_logits = tpf.combined_logits
masked_logits = tpf.masked_logits
build_legal = tpf.build_legal
rollout_actions = tpf.rollout_actions
PHASE_PLAN = tpf.PHASE_PLAN
PHASE_TROLL = tpf.PHASE_TROLL
PHASE_EXTERNAL_WAIT = tpf.PHASE_EXTERNAL_WAIT


# --------------------------------------------------------------------- the realized return-to-go


def returns_to_go(
    rewards: np.ndarray, turn_boundary: np.ndarray, gamma: float
) -> np.ndarray:
    """The trainer's discounting, run backwards over one complete episode.

    `rewards[i]` is the reward stored on row `i` (already scaled and already credited by the
    trainer's rule); `turn_boundary[i]` says whether that row executed a turn. Time passes only
    across a turn boundary, so the discount is applied only there -- the same asymmetry
    `compute_gae` uses. Nothing is bootstrapped: the episode ran to its end, so the return past
    the last row is zero.
    """

    out = np.zeros(len(rewards), dtype=np.float64)
    carried = 0.0
    for index in reversed(range(len(rewards))):
        discount = float(gamma) if turn_boundary[index] > 0 else 1.0
        carried = float(rewards[index]) + discount * carried
        out[index] = carried
    return out


# ------------------------------------------------------------------------------- the statistics


def calibration(predicted: np.ndarray, realized: np.ndarray) -> dict:
    """Slope, intercept, correlation, explained variance and bias -- or `null` where undefined.

    `null` rather than 0.0 wherever a statistic has no meaning: a slope needs the predictions to
    vary, a correlation needs both to vary, an explained variance needs the outcome to vary. A
    zero printed in those places would read as a finding.
    """

    count = int(len(predicted))
    if count == 0:
        return {"rows": 0}
    predicted = np.asarray(predicted, dtype=np.float64)
    realized = np.asarray(realized, dtype=np.float64)
    predicted_var = float(predicted.var())
    realized_var = float(realized.var())
    residual = realized - predicted

    slope = intercept = correlation = None
    if predicted_var > 0:
        covariance = float(((predicted - predicted.mean()) * (realized - realized.mean())).mean())
        slope = covariance / predicted_var
        intercept = float(realized.mean() - slope * predicted.mean())
        if realized_var > 0:
            correlation = covariance / float(np.sqrt(predicted_var * realized_var))

    return {
        "rows": count,
        "slope": slope,
        "intercept": intercept,
        "correlation": correlation,
        "explained_variance": (
            float(1.0 - residual.var() / realized_var) if realized_var > 0 else None
        ),
        "bias_predicted_minus_realized": float(predicted.mean() - realized.mean()),
        "root_mean_square_error": float(np.sqrt((residual**2).mean())),
        "mean_absolute_error": float(np.abs(residual).mean()),
        "predicted_mean": float(predicted.mean()),
        "predicted_std": float(np.sqrt(predicted_var)),
        "realized_mean": float(realized.mean()),
        "realized_std": float(np.sqrt(realized_var)),
    }


#: The game-turn edges the report slices on. A game is 300 turns; the buckets are deliberately
#: finer early, where the critic has the least to go on and the plan decisions are made.
DEFAULT_TURN_BUCKETS = (0, 10, 25, 50, 100, 150, 200, 300)


def bucket_label(value: int, edges) -> str:
    """`"50-99"` for a turn index in that band, `"300+"` past the last edge."""

    for lower, upper in zip(edges, edges[1:]):
        if lower <= value < upper:
            return f"{lower}-{upper - 1}"
    return f"{edges[-1]}+"


def sliced(rows: dict, key: str, labels: np.ndarray) -> dict:
    """The calibration statistics computed separately for every distinct value of one column."""

    out = {}
    for label in sorted(set(labels.tolist())):
        mask = labels == label
        out[str(label)] = calibration(rows["predicted"][mask], rows["realized"][mask])
    return {"slice": key, "groups": out}


# ------------------------------------------------------------------------------- the collection


def play(args, model, device, frozen_model=None) -> dict:
    """Play complete episodes with the trainer's own collection path and record every row.

    The environment, the legal-action mask, the observation's route into the network and the
    action choice are all the trainer's own functions. What is written here is the bookkeeping:
    per slot, the rows of the episode currently in flight, closed out into the result when the
    environment reports `done` for that slot and thrown away if collection stops first.

    `--decoding` chooses how commands are decided:

    * `scope` (the default) -- exactly what the run does, `rollout_actions` under the run's
      `--train-scope`, so under `plan-critic` troll rows already use masked argmax;
    * `sampled` -- temperature-1 sampling everywhere, the classic PPO rollout;
    * `argmax` -- masked argmax everywhere, the decoding the submitted bot actually ships with.

    One property to expect in the output rather than to suspect: inside one turn there is no
    discount and the turn's reward is paid once on the executing mini-step, so the plan row and
    the troll rows of the same turn carry the **identical** realized return. A difference between
    the plan and troll rows of the `row_class` slice is therefore a difference in the critic's
    predictions, not in what happened -- though the two classes' *means* still differ, because a
    turn has one plan row and as many troll rows as the side has trolls.
    """

    frozen = tpf.FrozenOpponent(model if frozen_model is None else frozen_model, device)
    env = tpf.make_env(args, frozen)

    slots = [
        {"value": [], "reward": [], "boundary": [], "phase": [], "turn": [], "valid": []}
        for _ in range(args.num_envs)
    ]
    turn_index = np.zeros(args.num_envs, dtype=np.int64)
    seat = np.zeros(args.num_envs, dtype=np.int64)
    seat[:] = np.asarray(env.seat_view)

    episodes: list[dict] = []
    columns: dict[str, list] = {
        key: []
        for key in ("predicted", "realized", "realized_undiscounted", "turn", "valid_cells",
                    "seat", "phase", "episode", "reward")
    }
    steps_taken = 0
    unfinished_rows = 0

    try:
        while len(episodes) < int(args.episodes) and steps_taken < int(args.max_mini_steps):
            phase_np = np.asarray(env.phase)
            if (phase_np == PHASE_EXTERNAL_WAIT).any():
                raise RuntimeError(
                    "phase 2 EXTERNAL_WAIT reached the instrument; the environment is supposed "
                    "to drive the python_frozen opponent itself"
                )
            legal_np = build_legal(
                np.asarray(env.masks), np.asarray(env.plan_masks), phase_np
            )
            if not legal_np.any(axis=1).all():
                raise RuntimeError("a mini-step arrived with an empty action mask")

            observations_np = np.ascontiguousarray(env.obs)
            observations = torch.from_numpy(observations_np).to(device)
            phase_t = torch.from_numpy(phase_np.astype(np.int64)).to(device)
            legal_t = torch.from_numpy(legal_np).to(device).bool()
            with torch.no_grad():
                logits, values = combined_logits(model, observations, phase_t)
                policy_masked = masked_logits(logits, legal_t)
                if args.decoding == "argmax":
                    actions = policy_masked.argmax(dim=-1)
                elif args.decoding == "sampled":
                    actions = Categorical(logits=policy_masked).sample()
                else:  # "scope": the run's own path
                    actions, _ = rollout_actions(policy_masked, phase_t, args.train_scope)

            values_np = values.cpu().numpy()
            # Plane 0 is the board-validity mask, the one the trunk pools over; its cell count is
            # the board's size and is available whatever the environment is.
            valid_cells = observations_np[:, 0].reshape(args.num_envs, -1).astype(bool).sum(axis=1)

            rewards, info = env.step(actions.cpu().numpy().astype(np.int32, copy=False))
            rewards = np.asarray(rewards, dtype=np.float32)
            completed = np.asarray(info.turn_completed)
            if args.reward_credit == "executing":
                rewards = np.where(completed > 0, rewards, np.float32(0.0))
            rewards = rewards * float(args.reward_scale)
            steps_taken += 1

            for slot in range(args.num_envs):
                record = slots[slot]
                record["value"].append(float(values_np[slot]))
                record["reward"].append(float(rewards[slot]))
                record["boundary"].append(int(completed[slot]))
                record["phase"].append(int(phase_np[slot]))
                record["turn"].append(int(turn_index[slot]))
                record["valid"].append(int(valid_cells[slot]))
            turn_index += (completed > 0).astype(np.int64)

            for slot in np.flatnonzero(np.asarray(info.dones)):
                slot = int(slot)
                record = slots[slot]
                reward_array = np.asarray(record["reward"], dtype=np.float64)
                boundary_array = np.asarray(record["boundary"], dtype=np.int64)
                discounted = returns_to_go(reward_array, boundary_array, args.gamma)
                undiscounted = returns_to_go(reward_array, boundary_array, 1.0)
                index = len(episodes)
                columns["predicted"].extend(record["value"])
                columns["realized"].extend(discounted.tolist())
                columns["realized_undiscounted"].extend(undiscounted.tolist())
                columns["turn"].extend(record["turn"])
                columns["valid_cells"].extend(record["valid"])
                columns["phase"].extend(record["phase"])
                columns["reward"].extend(record["reward"])
                columns["seat"].extend([int(seat[slot])] * len(record["value"]))
                columns["episode"].extend([index] * len(record["value"]))
                own = float(info.score_own[slot])
                opponent = float(info.score_opp[slot])
                episodes.append(
                    {
                        "rows": len(record["value"]),
                        "turns": int(info.episode_turns[slot]),
                        "win": int(info.wins[slot]),
                        "margin": own - opponent,
                        "score_own": own,
                        "score_opp": opponent,
                        "seat": int(seat[slot]),
                        "opponent_id": int(info.opponent_ids[slot]),
                        "map_index": int(info.map_indices[slot]),
                        "valid_cells": int(record["valid"][0]),
                        "realized_return_at_start": float(discounted[0]),
                        "realized_return_undiscounted": float(undiscounted[0]),
                        "predicted_value_at_start": float(record["value"][0]),
                        "illegal": int(info.illegal_commands[slot]),
                    }
                )
                slots[slot] = {key: [] for key in record}
                turn_index[slot] = 0
                # The environment has already reset this slot; its new seat is the one to record.
                seat[slot] = int(np.asarray(env.seat_view)[slot])
    finally:
        unfinished_rows = sum(len(record["value"]) for record in slots)
        close = getattr(env, "close", None)
        if callable(close):
            close()

    rows = {key: np.asarray(value) for key, value in columns.items()}
    return {
        "rows": rows,
        "episodes": episodes,
        "mini_steps": steps_taken,
        "unfinished_rows_discarded": int(unfinished_rows),
        "episodes_requested": int(args.episodes),
        "hit_mini_step_cap": bool(
            len(episodes) < int(args.episodes) and steps_taken >= int(args.max_mini_steps)
        ),
    }


# ------------------------------------------------------------------------------------- the run


def build_parser() -> argparse.ArgumentParser:
    """The trainer's parser, plus this instrument's own flags."""

    parser = tpf.build_parser()
    parser.description = (
        "independent critic calibration: predicted value against the realized return-to-go of "
        "complete episodes (card 20260829-nn-bot-way-b, Gate 0)"
    )
    group = parser.add_argument_group("the instrument")
    group.add_argument("--label", default=None, help="a name for this measurement in the report")
    group.add_argument("--out", default=None, help="write the JSON report here as well as to stdout")
    group.add_argument(
        "--episodes",
        type=int,
        default=64,
        help="how many COMPLETE episodes to collect; rows of episodes still in flight when the "
        "last one finishes are discarded and counted",
    )
    group.add_argument(
        "--decoding",
        choices=("scope", "sampled", "argmax"),
        default="scope",
        help="'scope' plays exactly as the run does under its --train-scope; 'sampled' is "
        "temperature-1 everywhere; 'argmax' is the shipped bot's decoding everywhere",
    )
    group.add_argument(
        "--max-mini-steps",
        type=int,
        default=200000,
        help="safety cap on collection; the report says if it was hit before --episodes was met",
    )
    group.add_argument(
        "--turn-buckets",
        default=",".join(str(edge) for edge in DEFAULT_TURN_BUCKETS),
        help="comma-separated game-turn edges for the by-turn slice",
    )
    group.add_argument(
        "--per-episode",
        action="store_true",
        default=False,
        help="include the per-episode table in the report (one row per game)",
    )
    return parser


def report_for(args, collected: dict) -> dict:
    """The statistics: overall, by turn bucket, by map size, by seat, by row class."""

    rows = collected["rows"]
    edges = [int(edge) for edge in str(args.turn_buckets).split(",") if edge.strip()]
    if not rows["predicted"].size:
        return {"overall": {"rows": 0}, "slices": {}}

    turn_labels = np.array([bucket_label(int(turn), edges) for turn in rows["turn"]])
    phase_labels = np.where(rows["phase"] == PHASE_PLAN, "plan", "troll")
    return {
        "overall": calibration(rows["predicted"], rows["realized"]),
        "overall_undiscounted": calibration(rows["predicted"], rows["realized_undiscounted"]),
        "slices": {
            "game_turn": sliced(rows, "game_turn", turn_labels),
            "map_size_valid_cells": sliced(rows, "map_size_valid_cells", rows["valid_cells"]),
            "seat": sliced(rows, "seat", rows["seat"]),
            "row_class": sliced(rows, "row_class", phase_labels),
        },
    }


def measure(args) -> dict:
    torch.manual_seed(args.seed)
    np.random.seed(args.seed % (2**32))
    torch.set_num_threads(max(1, args.threads))
    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise SystemExit("--device cuda requires an available CUDA device")
    started = time.perf_counter()

    model, checkpoint_sha = tpf.load_policy(args.initial_checkpoint, device)
    model.eval()
    for parameter in model.parameters():
        parameter.requires_grad_(False)

    frozen_model = frozen_sha = None
    if args.frozen_checkpoint:
        # The trainer plays seat 1 with `--frozen-checkpoint` when it is given; the measurement
        # must face the same opponent, or the realized returns are from a different game.
        frozen_model, frozen_sha = tpf.load_policy(args.frozen_checkpoint, device)

    collected = play(args, model, device, frozen_model)
    statistics = report_for(args, collected)
    episodes = collected["episodes"]

    report = {
        "event": "critic-calibration",
        "label": args.label
        or (Path(args.initial_checkpoint).stem if args.initial_checkpoint else "fresh"),
        "checkpoint": args.initial_checkpoint,
        "checkpoint_sha256": checkpoint_sha,
        "frozen_checkpoint": args.frozen_checkpoint,
        "frozen_checkpoint_sha256": frozen_sha,
        "instrument": {
            "critic_calibration_sha256": sha256(Path(__file__).resolve()),
            "train_ppo_full_sha256": sha256(Path(tpf.__file__).resolve()),
            "torch_version": torch.__version__,
            "plan_target_memory": tpf.PLAN_TARGET_MEMORY,
            "plan_vocab_version": tpf.PLAN_VOCAB_VERSION,
        },
        "config": {
            key: value
            for key, value in sorted(vars(args).items())
            if key not in ("checkpoint_every", "gate_every", "gate_games", "gate_maps", "gate_bot")
        },
        "collection": {
            "episodes_completed": len(episodes),
            "episodes_requested": collected["episodes_requested"],
            "rows": int(collected["rows"]["predicted"].size),
            "mini_steps": collected["mini_steps"],
            "unfinished_rows_discarded": collected["unfinished_rows_discarded"],
            "hit_mini_step_cap": collected["hit_mini_step_cap"],
            "decoding": args.decoding,
            "train_scope": args.train_scope,
            "reward_scale": float(args.reward_scale),
            "reward_credit": args.reward_credit,
            "gamma": float(args.gamma),
            "mean_margin": (
                float(np.mean([row["margin"] for row in episodes])) if episodes else None
            ),
            "win_rate": (
                float(np.mean([row["win"] for row in episodes])) if episodes else None
            ),
            "mean_turns": (
                float(np.mean([row["turns"] for row in episodes])) if episodes else None
            ),
            "illegal_commands": int(sum(row["illegal"] for row in episodes)),
        },
        "calibration": statistics,
        "timing": {"total_seconds": time.perf_counter() - started},
    }
    if args.per_episode:
        report["episodes"] = episodes

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    return report


def main(argv: list[str] | None = None) -> dict:
    args = build_parser().parse_args(argv)
    report = measure(args)
    print(json.dumps(report, sort_keys=True, default=str), flush=True)
    return report


if __name__ == "__main__":
    main()
