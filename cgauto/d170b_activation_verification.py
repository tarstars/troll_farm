#!/usr/bin/env python3
"""D170b Delta 2 -- pre-Phase-1 activation verification (frozen; run before
any training).

All-KEEP deterministic diagnostic on the training pool (seed_base
9,850,000, map_pool 256, no training budget spent), exhaustive over every
(map_seed, seat, opponent) task exactly once -- mirroring the Phase 2/3
analyzer's own `evaluate_deterministic` exhaustive `task_index` convention
(`cgauto/analyze_d170a_family_robust_option_policy.py`), but with the
constant all-KEEP "policy" (action=0 always) instead of a trained model, so
no checkpoint is required and the training budget is never spent -- exactly
as in D170a's own field-level diagnostic
(`d170a-family-robust-option-policy-result-2026-07-28.md` root-cause
evidence #4). Reuses the frozen, unmodified `D170aVecEnv`
(`cgauto/rl_d170a_option_policy_env.py`) -- no new Rust, no training.

Gates (D170b repair protocol Delta 2, all frozen; any miss -> BLOCKED):
- each resource `_trig` arm offered at least once in >= 5% and <= 50% of
  episodes; and
- offered at least once in >= 60% of the episodes where the underlying
  trigger event (state feature 55, `opp_worker_trigger_seen`) occurs; and
- `opt_return` offered at least once in >= 8% of episodes.

See
`data/analysis/live-agent-6553250/d170b-family-robust-option-policy-repair-protocol-2026-07-28.md`
Delta 2.

Usage: python -m cgauto.d170b_activation_verification
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cgauto.rl_d170a_option_policy_env import (  # noqa: E402
    ARM_LABELS,
    ARMS,
    STATE_FEATURES,
    D170aVecEnv,
)
from cgauto.rl_macro_env import OPPONENTS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = (
    ROOT
    / "data"
    / "analysis"
    / "live-agent-6553250"
    / "d170b-activation-verification-2026-07-28.json"
)

SEED_BASE = 9_850_000
MAP_POOL = 256
NUM_ENVS = 32
TRIG_ARM_LABELS = ("opt_fruit_trig", "opt_iron_trig", "opt_protect_trig")
TRIGGER_FEATURE_INDEX = 55  # opp_worker_trigger_seen (0.0/1.0)


def fresh_accumulator() -> dict:
    return {"trigger_seen": False, "offered": set()}


def run() -> dict:
    tasks = MAP_POOL * 2 * len(OPPONENTS)
    per_task: dict[int, dict] = {}
    current = [fresh_accumulator() for _ in range(NUM_ENVS)]
    guard = 0
    guard_limit = tasks * 25 + 5_000
    started = time.perf_counter()

    with D170aVecEnv(NUM_ENVS, SEED_BASE, MAP_POOL) as env:
        inputs, pending = env.observe()
        while len(per_task) < tasks:
            guard += 1
            if guard > guard_limit:
                raise RuntimeError(
                    "D170b activation-verification iteration guard tripped"
                )
            valid_before = pending.copy()
            for slot in np.flatnonzero(valid_before):
                block = inputs[slot, STATE_FEATURES + 2 : STATE_FEATURES + 2 + ARMS]
                arm_index = int(np.argmax(block))
                current[slot]["offered"].add(ARM_LABELS[arm_index])
                if inputs[slot, TRIGGER_FEATURE_INDEX] > 0.5:
                    current[slot]["trigger_seen"] = True

            actions = np.zeros(NUM_ENVS, dtype=np.int32)  # all-KEEP, always
            inputs, pending, rewards, dones, terminals = env.step(actions)
            if np.any(rewards != 0.0):
                raise RuntimeError(
                    "D170b activation-verification: nonzero reward under all-KEEP "
                    "(budget must never be spent)"
                )
            for slot, terminal in enumerate(terminals):
                if terminal is None:
                    continue
                if terminal.budget_used:
                    raise RuntimeError(
                        "D170b activation-verification: budget_used under all-KEEP "
                        f"at slot {slot}"
                    )
                if terminal.task_index < tasks and terminal.task_index not in per_task:
                    per_task[terminal.task_index] = current[slot]
                current[slot] = fresh_accumulator()

    elapsed = time.perf_counter() - started
    episodes = [per_task[index] for index in range(tasks)]
    n = len(episodes)
    trigger_episodes = sum(1 for episode in episodes if episode["trigger_seen"])

    def offered_rate(label: str) -> float:
        return sum(1 for episode in episodes if label in episode["offered"]) / n

    def offered_rate_given_trigger(label: str) -> float | None:
        if trigger_episodes == 0:
            return None
        numerator = sum(
            1
            for episode in episodes
            if episode["trigger_seen"] and label in episode["offered"]
        )
        return numerator / trigger_episodes

    gates: dict[str, dict] = {}
    for label in TRIG_ARM_LABELS:
        unconditional = offered_rate(label)
        conditional = offered_rate_given_trigger(label)
        gates[label] = {
            "offered_at_least_once_rate": unconditional,
            "offered_at_least_once_rate_given_trigger_seen": conditional,
            "gate_offered_5pct_to_50pct_of_episodes": 0.05 <= unconditional <= 0.50,
            "gate_offered_ge_60pct_of_trigger_episodes": (
                conditional is not None and conditional >= 0.60
            ),
        }
    opt_return_rate = offered_rate("opt_return")
    gates["opt_return"] = {
        "offered_at_least_once_rate": opt_return_rate,
        "gate_offered_ge_8pct_of_episodes": opt_return_rate >= 0.08,
    }

    trig_gates_pass = all(
        gates[label]["gate_offered_5pct_to_50pct_of_episodes"]
        and gates[label]["gate_offered_ge_60pct_of_trigger_episodes"]
        for label in TRIG_ARM_LABELS
    )
    all_pass = (
        trigger_episodes > 0
        and trig_gates_pass
        and gates["opt_return"]["gate_offered_ge_8pct_of_episodes"]
    )

    return {
        "schema": "troll-farm-d170b-activation-verification-v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "seed_base": SEED_BASE,
        "map_pool": MAP_POOL,
        "num_envs": NUM_ENVS,
        "tasks": n,
        "trigger_episodes": trigger_episodes,
        "trigger_episode_rate": trigger_episodes / n,
        "gates": gates,
        "verdict": "PASS" if all_pass else "BLOCKED",
        "elapsed_seconds": elapsed,
    }


def main() -> int:
    result = run()
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
