#!/usr/bin/env python3
"""Audit the rank-aware parallel macro ABI before D41c training."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import numpy as np

from cgauto.analyze_d41a_macro_bc import sha256
from cgauto.evaluate_d41b_exact_prior import compare_baseline, read_baseline
from cgauto.rl_macro_env import DEFAULT_LIBRARY, MacroVecEnv, TASKS_PER_MAP


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d41c-exact-prior-residual-ppo-protocol-2026-07-21.md"
D41B_RESULT = ANALYSIS / "d41b-exact-prior-preflight-2026-07-21.json"
D41B_BASELINE = ANALYSIS / "d41a-development-teacher-9711000-9711031.tsv"
OUTPUT = ANALYSIS / "d41c-rank-parallel-preflight-2026-07-21.json"
LEGACY_FEATURE_HASH = "306779511abd482bd0a102c9cb0949f4ff40e0180ea1895fc8cefc9c584ef4fd"


def stream_hash(seed_base: int, decisions: int, num_envs: int) -> dict:
    full = hashlib.sha256()
    legacy = hashlib.sha256()
    seen = 0
    started_wall = time.perf_counter()
    started_cpu = time.process_time()
    with MacroVecEnv(num_envs, seed_base) as env:
        while seen < decisions:
            take = min(num_envs, decisions - seen)
            selected = np.empty(num_envs, dtype=np.int32)
            for slot in range(num_envs):
                count = int(env.counts[slot])
                rank_zero = int(np.flatnonzero(env.prior_ranks[slot, :count] == 0)[0])
                selected[slot] = env.actions[slot, rank_zero]
                if slot >= take:
                    continue
                payload = (
                    env.actions[slot, :count].tobytes(),
                    env.features[slot, :count].tobytes(),
                    env.counts[slot].tobytes(),
                    env.teacher_indices[slot].tobytes(),
                    env.branches[slot].tobytes(),
                )
                for part in payload:
                    legacy.update(part)
                    full.update(part)
                full.update(env.prior_ranks[slot, :count].tobytes())
            env.step(selected)
            seen += take
    wall = time.perf_counter() - started_wall
    cpu = time.process_time() - started_cpu
    return {
        "seed_base": seed_base,
        "decisions": decisions,
        "num_envs": num_envs,
        "legacy_hash": legacy.hexdigest(),
        "full_rank_hash": full.hexdigest(),
        "wall_seconds": wall,
        "cpu_seconds": cpu,
        "effective_cpu_cores": cpu / wall,
        "decisions_per_second": decisions / wall,
    }


def terminal_smoke(seed_base: int, maps: int, num_envs: int) -> dict:
    target_tasks = maps * TASKS_PER_MAP
    completed: dict[int, dict] = {}
    returns: dict[int, float] = {index: 0.0 for index in range(target_tasks)}
    with MacroVecEnv(num_envs, seed_base) as env:
        while len(completed) < target_tasks:
            before = env.task_indices.copy()
            selected = env.actions[
                np.arange(num_envs), env.teacher_indices.astype(np.int64)
            ].copy()
            _, _, _, rewards, info = env.step(selected)
            for slot, task_index in enumerate(before):
                if int(task_index) < target_tasks:
                    returns[int(task_index)] += float(rewards[slot])
            for terminal in info.terminals:
                if terminal is not None and terminal["task_index"] < target_tasks:
                    completed[terminal["task_index"]] = terminal
    rows = [completed[index] for index in range(target_tasks)]
    identity_errors = [
        abs(100.0 * returns[index] - rows[index]["margin"])
        for index in range(target_tasks)
    ]
    return {
        "episodes": target_tasks,
        "rows": rows,
        "maximum_reward_identity_error_margin_points": max(identity_errors),
        "reward_identity": max(identity_errors) <= 1e-4,
    }


def main() -> None:
    for required in (PROTOCOL, D41B_RESULT, D41B_BASELINE, Path(DEFAULT_LIBRARY)):
        if not required.exists():
            raise SystemExit(f"missing D41c prerequisite: {required}")
    d41b = json.loads(D41B_RESULT.read_text())
    if d41b.get("pass") is not True:
        raise SystemExit("D41b did not pass")

    streams = {}
    for width in (16, 64):
        first = stream_hash(9_700_000, 4_096, width)
        repeat = stream_hash(9_700_000, 4_096, width)
        streams[str(width)] = {
            "first": first,
            "repeat": repeat,
            "aa_exact": first["full_rank_hash"] == repeat["full_rank_hash"],
        }
    chosen_width = (
        64
        if streams["64"]["first"]["decisions_per_second"]
        > streams["16"]["first"]["decisions_per_second"]
        else 16
    )

    smoke = terminal_smoke(9_711_000, 2, chosen_width)
    baseline = read_baseline(D41B_BASELINE)
    smoke_keys = {
        (row["map_seed"], row["seat"], row["opponent"])
        for row in smoke["rows"]
    }
    smoke_baseline = {key: row for key, row in baseline.items() if key in smoke_keys}
    baseline_comparison = compare_baseline(smoke["rows"], smoke_baseline)
    rank_zero_exact = all(
        stream["first"]["full_rank_hash"] == stream["repeat"]["full_rank_hash"]
        for stream in streams.values()
    )
    gates = {
        "d41b_pass": d41b["pass"] is True,
        "rank_stream_aa": rank_zero_exact,
        "legacy_feature_hash_preserved": streams["16"]["first"]["legacy_hash"]
        == LEGACY_FEATURE_HASH,
        "terminal_smoke_exact": baseline_comparison["exact"],
        "reward_identity": smoke["reward_identity"],
        "width_64_faster": chosen_width == 64,
    }
    report = {
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "d41b_result": str(D41B_RESULT),
        "d41b_result_sha256": sha256(D41B_RESULT),
        "library": str(DEFAULT_LIBRARY),
        "library_sha256": sha256(Path(DEFAULT_LIBRARY)),
        "streams": streams,
        "chosen_num_envs": chosen_width,
        "terminal_smoke": {key: value for key, value in smoke.items() if key != "rows"},
        "baseline_comparison": baseline_comparison,
        "gates": gates,
        "pass": all(gates.values()),
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
