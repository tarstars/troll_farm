#!/usr/bin/env python3
"""Generate D22 exact one-disagreement counterfactual continuations."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np
import torch

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.rl_level1_env import ACTION_SIZE, DEFAULT_LIBRARY  # noqa: E402
from cgauto.rl_level2_env import LEVEL2_RECIPE_NAMES, level2_recipe  # noqa: E402
from cgauto.rl_level6_env import (  # noqa: E402
    Level6VecEnv,
    level6_opponent,
)
from cgauto.train_level1_ppo import SpatialActorCritic, sha256  # noqa: E402


ANALYSIS = REPO / "data" / "analysis" / "live-agent-6553250"
BASELINE_CHECKPOINT = (
    ANALYSIS / "curriculum-level5-seed-reacquisition-d11-ppo-final-local-l5b.pt"
)
PROPOSAL_CHECKPOINT = ANALYSIS / "d21-competitive-ppo-pilot-seed2107-final.pt"
PROTOCOL = ANALYSIS / "d22-d21-disagreement-monte-carlo-protocol-2026-07-20.md"
OUTPUT = ANALYSIS / "d22-d21-disagreement-monte-carlo-8300000-8300239.json"
BASELINE_SHA256 = "44c9a9ed3a232c01fccf9b99b16c3c785b26a1e2c656cb6c40674137138d8de6"
PROPOSAL_SHA256 = "d51dd99260aa33b447c1371a8f1857a0771f7421c9b90a13322d9bf01f78c8cb"
SEED_BASE = 8_300_000
EPISODES = 240
SEED_STOP = SEED_BASE + EPISODES
NUM_ENVS = 240
MAX_TURNS = 300
TURN_BANDS = ((0, 75), (75, 150), (150, 225), (225, 300))
MASK64 = (1 << 64) - 1


def splitmix64(value: int) -> int:
    value &= MASK64
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & MASK64
    return (value ^ (value >> 31)) & MASK64


def event_priority(seed: int, decision_index: int, band: int) -> int:
    return splitmix64(
        seed
        ^ 0x4432_3264_6973_6167
        ^ ((decision_index + 1) * 0x9E3779B97F4A7C15)
        ^ ((band + 1) * 0xD1B54A32D192ED03)
    )


def state_signature(observation: np.ndarray, mask: np.ndarray) -> str:
    digest = hashlib.sha256()
    digest.update(observation.tobytes())
    digest.update(mask.tobytes())
    return digest.hexdigest()


def load_actor(path: Path) -> SpatialActorCritic:
    saved = torch.load(path, map_location="cpu", weights_only=False)
    model = SpatialActorCritic()
    model.load_state_dict(saved["model"], strict=True)
    model.eval()
    return model


@torch.inference_mode()
def deterministic_actions(model: SpatialActorCritic, env: Level6VecEnv) -> np.ndarray:
    selected, _, _, _ = model.action_and_value(
        torch.from_numpy(env.obs),
        torch.from_numpy(env.masks),
        deterministic=True,
    )
    return selected.numpy().astype(np.int32, copy=False)


def terminal_row(info, index: int) -> dict:
    own_score = int(info.score_gains[index])
    opponent_score = int(info.opponent_scores[index])
    margin = own_score - opponent_score
    episode_return = float(info.returns[index])
    seed = int(info.seeds[index])
    opponent_id, opponent = level6_opponent(seed)
    recipe_id, target = level2_recipe(seed)
    return {
        "seed": seed,
        "opponent_id": opponent_id,
        "opponent": opponent,
        "recipe_id": recipe_id,
        "recipe": LEVEL2_RECIPE_NAMES[recipe_id],
        "target": list(target),
        "turn": int(info.turns[index]),
        "return": episode_return,
        "return_margin_error": abs(episode_return * 100.0 - margin),
        "own_score": own_score,
        "opponent_score": opponent_score,
        "margin": margin,
        "training_completed": int(info.training_turns[index]) > 0,
        "created_crop": bool(info.created_crops[index]),
        "renewable_harvests": int(info.renewable_harvests[index]),
    }


def discover(
    baseline: SpatialActorCritic,
    proposal: SpatialActorCritic,
) -> dict:
    completed: dict[int, dict] = {}
    selected: dict[tuple[int, int], dict] = {}
    disagreements_by_band = [0, 0, 0, 0]
    inspected_states = 0
    baseline_illegal = 0
    proposal_illegal = 0
    decisions: dict[int, int] = {}
    transitions = 0
    started = time.perf_counter()
    with Level6VecEnv(NUM_ENVS, SEED_BASE, max_turns=MAX_TURNS) as env:
        while len(completed) < EPISODES:
            turns, phases, seeds = env.current_metadata()
            baseline_actions = deterministic_actions(baseline, env)
            proposal_actions = deterministic_actions(proposal, env)
            legal = env.masks.reshape(NUM_ENVS, ACTION_SIZE)
            for index in range(NUM_ENVS):
                seed = int(seeds[index])
                if not SEED_BASE <= seed < SEED_STOP:
                    continue
                inspected_states += 1
                baseline_illegal += int(legal[index, baseline_actions[index]] == 0)
                proposal_illegal += int(legal[index, proposal_actions[index]] == 0)
                decision_index = decisions.get(seed, 0)
                turn = int(turns[index])
                if baseline_actions[index] != proposal_actions[index] and turn < MAX_TURNS:
                    band = min(turn // 75, 3)
                    disagreements_by_band[band] += 1
                    priority = event_priority(seed, decision_index, band)
                    key = (seed, band)
                    previous = selected.get(key)
                    if previous is None or priority < previous["priority"]:
                        opponent_id, opponent = level6_opponent(seed)
                        recipe_id, target = level2_recipe(seed)
                        selected[key] = {
                            "seed": seed,
                            "band": band,
                            "band_start": TURN_BANDS[band][0],
                            "band_stop_exclusive": TURN_BANDS[band][1],
                            "turn": turn,
                            "phase": int(phases[index]),
                            "decision_index": decision_index,
                            "priority": priority,
                            "baseline_action": int(baseline_actions[index]),
                            "baseline_plane": int(baseline_actions[index]) // 242,
                            "proposal_action": int(proposal_actions[index]),
                            "proposal_plane": int(proposal_actions[index]) // 242,
                            "state_signature": state_signature(
                                env.obs[index], env.masks[index]
                            ),
                            "opponent_id": opponent_id,
                            "opponent": opponent,
                            "recipe_id": recipe_id,
                            "recipe": LEVEL2_RECIPE_NAMES[recipe_id],
                            "target": list(target),
                        }
                decisions[seed] = decision_index + 1
            _, _, _, info = env.step(baseline_actions)
            transitions += NUM_ENVS
            for index in np.flatnonzero(info.dones):
                seed = int(info.seeds[index])
                if SEED_BASE <= seed < SEED_STOP:
                    completed[seed] = terminal_row(info, int(index))
    events = [selected[key] for key in sorted(selected)]
    return {
        "elapsed_seconds": time.perf_counter() - started,
        "transitions": transitions,
        "inspected_states": inspected_states,
        "baseline_illegal_actions": baseline_illegal,
        "proposal_illegal_actions": proposal_illegal,
        "raw_disagreements_by_band": disagreements_by_band,
        "selected_events": events,
        "terminal_rows": [completed[seed] for seed in range(SEED_BASE, SEED_STOP)],
    }


def replay(
    baseline: SpatialActorCritic,
    events: dict[int, dict],
    *,
    label: str,
) -> dict:
    completed: dict[int, dict] = {}
    decisions: dict[int, int] = {}
    intervened: set[int] = set()
    violations: list[str] = []
    illegal_actions = 0
    transitions = 0
    started = time.perf_counter()
    with Level6VecEnv(NUM_ENVS, SEED_BASE, max_turns=MAX_TURNS) as env:
        while len(completed) < EPISODES:
            turns, phases, seeds = env.current_metadata()
            actions = deterministic_actions(baseline, env)
            legal = env.masks.reshape(NUM_ENVS, ACTION_SIZE)
            for index in range(NUM_ENVS):
                seed = int(seeds[index])
                if not SEED_BASE <= seed < SEED_STOP:
                    continue
                decision_index = decisions.get(seed, 0)
                event = events.get(seed)
                if event is not None and decision_index == event["decision_index"]:
                    if seed in intervened:
                        violations.append(f"{label}: duplicate intervention on seed {seed}")
                    if int(turns[index]) != event["turn"] or int(phases[index]) != event["phase"]:
                        violations.append(f"{label}: metadata mismatch on seed {seed}")
                    if int(actions[index]) != event["baseline_action"]:
                        violations.append(f"{label}: baseline action mismatch on seed {seed}")
                    if state_signature(env.obs[index], env.masks[index]) != event[
                        "state_signature"
                    ]:
                        violations.append(f"{label}: state signature mismatch on seed {seed}")
                    proposal_action = event["proposal_action"]
                    if legal[index, proposal_action] == 0:
                        violations.append(f"{label}: illegal stored proposal on seed {seed}")
                    actions[index] = proposal_action
                    intervened.add(seed)
                illegal_actions += int(legal[index, actions[index]] == 0)
                decisions[seed] = decision_index + 1
            _, _, _, info = env.step(actions)
            transitions += NUM_ENVS
            for index in np.flatnonzero(info.dones):
                seed = int(info.seeds[index])
                if SEED_BASE <= seed < SEED_STOP:
                    completed[seed] = terminal_row(info, int(index))
                    if seed in events and seed not in intervened:
                        violations.append(f"{label}: missed intervention on seed {seed}")
    return {
        "label": label,
        "elapsed_seconds": time.perf_counter() - started,
        "transitions": transitions,
        "illegal_actions": illegal_actions,
        "violations": violations,
        "intervened_seeds": sorted(intervened),
        "terminal_rows": [completed[seed] for seed in range(SEED_BASE, SEED_STOP)],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-checkpoint", type=Path, default=BASELINE_CHECKPOINT)
    parser.add_argument("--proposal-checkpoint", type=Path, default=PROPOSAL_CHECKPOINT)
    parser.add_argument("--protocol", type=Path, default=PROTOCOL)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--threads", type=int, default=14)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")
    if sha256(args.baseline_checkpoint) != BASELINE_SHA256:
        raise SystemExit("D22 baseline checkpoint hash mismatch")
    if sha256(args.proposal_checkpoint) != PROPOSAL_SHA256:
        raise SystemExit("D22 proposal checkpoint hash mismatch")
    if not args.protocol.exists():
        raise SystemExit(f"missing frozen D22 protocol: {args.protocol}")
    torch.set_num_threads(args.threads)
    torch.set_num_interop_threads(min(4, args.threads))
    baseline = load_actor(args.baseline_checkpoint)
    proposal = load_actor(args.proposal_checkpoint)

    print(json.dumps({"event": "discover", "seed_base": SEED_BASE, "episodes": EPISODES}))
    discovery = discover(baseline, proposal)
    events = discovery["selected_events"]
    by_band = [sum(event["band"] == band for event in events) for band in range(4)]
    print(
        json.dumps(
            {
                "event": "discovered",
                "selected_events": len(events),
                "selected_by_band": by_band,
                "raw_disagreements_by_band": discovery["raw_disagreements_by_band"],
                "elapsed_seconds": discovery["elapsed_seconds"],
            }
        ),
        flush=True,
    )

    repeat = replay(baseline, {}, label="baseline_repeat")
    print(
        json.dumps(
            {
                "event": "baseline_repeat",
                "elapsed_seconds": repeat["elapsed_seconds"],
                "violations": repeat["violations"],
            }
        ),
        flush=True,
    )

    arms = []
    event_lookup = {(event["seed"], event["band"]): event for event in events}
    baseline_rows = {row["seed"]: row for row in discovery["terminal_rows"]}
    for band in range(4):
        band_events = {
            seed: event_lookup[(seed, band)]
            for seed in range(SEED_BASE, SEED_STOP)
            if (seed, band) in event_lookup
        }
        arm = replay(baseline, band_events, label=f"band_{band}")
        alternative_rows = {row["seed"]: row for row in arm["terminal_rows"]}
        arm["outcomes"] = [
            {
                **event,
                "baseline_margin": baseline_rows[seed]["margin"],
                "alternative_margin": alternative_rows[seed]["margin"],
                "advantage": (
                    alternative_rows[seed]["margin"] - baseline_rows[seed]["margin"]
                ),
                "baseline_own_score": baseline_rows[seed]["own_score"],
                "alternative_own_score": alternative_rows[seed]["own_score"],
                "baseline_opponent_score": baseline_rows[seed]["opponent_score"],
                "alternative_opponent_score": alternative_rows[seed]["opponent_score"],
                "new_catastrophe": (
                    baseline_rows[seed]["margin"] > -100
                    and alternative_rows[seed]["margin"] <= -100
                ),
                "alternative_return_margin_error": alternative_rows[seed][
                    "return_margin_error"
                ],
                "alternative_turn": alternative_rows[seed]["turn"],
            }
            for seed, event in sorted(band_events.items())
        ]
        arms.append(arm)
        print(
            json.dumps(
                {
                    "event": "arm_complete",
                    "band": band,
                    "interventions": len(arm["outcomes"]),
                    "elapsed_seconds": arm["elapsed_seconds"],
                    "illegal_actions": arm["illegal_actions"],
                    "violations": arm["violations"],
                }
            ),
            flush=True,
        )

    payload = {
        "schema": 1,
        "scope": (
            "D22 discovery-only exact one-D21-action Monte Carlo continuations; "
            "no policy, candidate, holdout, submission, or Arena authorization"
        ),
        "config": {
            "seed_base": SEED_BASE,
            "seed_stop_exclusive": SEED_STOP,
            "episodes": EPISODES,
            "num_envs": NUM_ENVS,
            "max_turns": MAX_TURNS,
            "turn_bands": [list(band) for band in TURN_BANDS],
            "baseline_checkpoint": str(args.baseline_checkpoint),
            "baseline_checkpoint_sha256": sha256(args.baseline_checkpoint),
            "proposal_checkpoint": str(args.proposal_checkpoint),
            "proposal_checkpoint_sha256": sha256(args.proposal_checkpoint),
            "protocol": str(args.protocol),
            "protocol_sha256": sha256(args.protocol),
            "environment_library": str(DEFAULT_LIBRARY),
            "environment_library_sha256": sha256(Path(DEFAULT_LIBRARY)),
            "generator": str(Path(__file__).relative_to(REPO)),
            "generator_sha256": sha256(Path(__file__)),
            "threads": args.threads,
        },
        "discovery": discovery,
        "baseline_repeat": repeat,
        "arms": arms,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"event": "saved", "output": str(args.output)}), flush=True)


if __name__ == "__main__":
    main()
