#!/usr/bin/env python3
"""D172a Phase 3 (admission/selection) and Phase 4 (veto/confirmation).

Runs the Rust `eval` subcommand (rust/src/bin/d172a_dense_counterfactual_corpus.rs)
closed-loop for each Phase-3 fit's exported weights on the frozen LOBO
selection blocks, applies the frozen admission gates, selects one fit per
the frozen tie-break, then (subcommands) runs the veto panel and, if it
passes, the sealed one-shot confirmation block.

Reuses `summarize_rows`/`veto_gates`/`confirmation_gates`/`clustered_ci`/
`rows_digest` from `cgauto/analyze_d170a_family_robust_option_policy.py`
UNMODIFIED (identical formulas per the D172a protocol) -- only
`admission_gates` differs (D172a swaps D170a's `mean_own_score_delta >=
-0.5` for `activation in 5-60% of tasks`, using the SAME `budget_used_rate`
field `summarize_rows` already computes), so that one gate function is new
here.

See
`data/analysis/live-agent-6553250/d172a-dense-counterfactual-option-policy-protocol-2026-07-28.md`
and `...-lock.json`.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cgauto.analyze_d170a_family_robust_option_policy import (  # noqa: E402
    clustered_ci,
    confirmation_gates,
    rows_digest,
    summarize_rows,
    veto_gates,
)
from cgauto.train_d172a_dense_counterfactual_option_policy import (  # noqa: E402
    BASE,
    EXTERNAL,
    FUNCTION_CLASSES,
    LOCK,
    PROTOCOL,
    git_rev,
    output_paths,
    sha256,
)

ROOT = Path(__file__).resolve().parents[1]
RUST_BIN = ROOT / "rust" / "target" / "release" / "d172a_dense_counterfactual_corpus"

TAU = 1.0  # frozen runtime threshold, per the lock

SELECTION_SEED_BASE = 9_861_000
SELECTION_BLOCKS = 8
SELECTION_BLOCK_MAPS = 16
SELECTION_MAP_POOL = SELECTION_BLOCKS * SELECTION_BLOCK_MAPS  # 128
VETO_SEED_BASE = 9_844_136
VETO_MAP_POOL = 64  # the same D169a/D170a/D170b consumed 1,024-task panel; veto-only
CONFIRMATION_SEED_BASE = 9_862_000
CONFIRMATION_MAP_POOL = 64  # 1,024 sealed tasks; opened exactly once


def all_fit_keys() -> list[tuple[str, int]]:
    return [(fc, seed) for fc, spec in FUNCTION_CLASSES.items() for seed in spec["seeds"]]


def run_eval(weights_path: Path, seed_base: int, map_pool: int, threads: int, output: Path) -> list[dict]:
    if not RUST_BIN.exists():
        raise FileNotFoundError(f"missing {RUST_BIN}; build with cargo build --release --bin d172a_dense_counterfactual_corpus")
    env = dict(os.environ)
    env["RAYON_NUM_THREADS"] = "1"
    env["LC_ALL"] = "C"
    subprocess.run(
        [
            str(RUST_BIN), "eval", str(weights_path), str(TAU),
            str(seed_base), str(map_pool), str(output), str(threads),
        ],
        check=True,
        env=env,
    )
    rows = []
    with open(output) as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    expected = map_pool * 2 * 8
    if len(rows) != expected:
        raise RuntimeError(f"expected {expected} eval rows, got {len(rows)} from {output}")
    return rows


def admission_gates(summary: dict) -> dict:
    gates = {
        "lobo_pooled_mean_at_least_1_5": summary["pooled_mean"] >= 1.5,
        "worst_held_block_at_least_0": summary["worst_block"] >= 0.0,
        "worst_family_mean_at_least_minus1": summary["worst_family"] >= -1.0,
        "activation_in_5_to_60_pct_of_tasks": 0.05 <= summary["budget_used_rate"] <= 0.60,
        "crop_workforce_safety_exact": summary["crop_safety_exact"],
        "catastrophes_le_control": summary["catastrophes_policy"] <= summary["catastrophes_control"],
    }
    return {"gates": gates, "admitted": all(gates.values())}


def eval_output_path(tag: str, block: str) -> Path:
    EXTERNAL.mkdir(parents=True, exist_ok=True)
    return EXTERNAL / f"d172a-eval-{tag}-{block}.jsonl"


def phase3(threads: int, output: Path) -> dict:
    fit_summaries = []
    for function_class, seed in all_fit_keys():
        tag = f"{function_class}-seed{seed}"
        paths = output_paths(function_class, seed)
        result_path = paths["result"]
        weights_path = paths["weights"]
        if not result_path.exists() or not weights_path.exists():
            fit_summaries.append({"function_class": function_class, "seed": seed, "status": "missing_fit"})
            continue
        eval_path = eval_output_path(tag, f"selection-{SELECTION_SEED_BASE}")
        started = time.perf_counter()
        rows = run_eval(weights_path, SELECTION_SEED_BASE, SELECTION_MAP_POOL, threads, eval_path)
        elapsed = time.perf_counter() - started
        summary = summarize_rows(rows, block_seed_base=SELECTION_SEED_BASE, block_maps=SELECTION_BLOCK_MAPS)
        admission = admission_gates(summary)
        fit_summaries.append(
            {
                "function_class": function_class,
                "seed": seed,
                "status": "evaluated",
                "weights_sha256": sha256(weights_path),
                "eval_seconds": elapsed,
                "rows_digest_sha256": rows_digest(rows),
                "summary": summary,
                "admission": admission,
            }
        )
        print(
            json.dumps(
                {
                    "event": "phase3_fit",
                    "function_class": function_class,
                    "seed": seed,
                    "pooled_mean": summary["pooled_mean"],
                    "worst_block": summary["worst_block"],
                    "worst_family": summary["worst_family"],
                    "budget_used_rate": summary["budget_used_rate"],
                    "admitted": admission["admitted"],
                },
                sort_keys=True,
            ),
            flush=True,
        )

    admitted = [f for f in fit_summaries if f.get("status") == "evaluated" and f["admission"]["admitted"]]
    selected = None
    if admitted:
        admitted_sorted = sorted(
            admitted,
            key=lambda f: (-f["summary"]["worst_block"], -f["summary"]["pooled_mean"], f["seed"]),
        )
        selected = {"function_class": admitted_sorted[0]["function_class"], "seed": admitted_sorted[0]["seed"]}

    result = {
        "schema": "troll-farm-d172a-phase3-admission-selection-v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_rev": git_rev(),
        "threads": threads,
        "tau": TAU,
        "selection_seed_base": SELECTION_SEED_BASE,
        "selection_map_pool": SELECTION_MAP_POOL,
        "selection_blocks": SELECTION_BLOCKS,
        "fits": fit_summaries,
        "admitted_count": len(admitted),
        "selected": selected,
        "decision": "selection_admitted" if selected else "CLOSED-AT-SELECTION",
        "inputs": {"lock": sha256(LOCK), "protocol": sha256(PROTOCOL)},
    }
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"admitted_count": len(admitted), "selected": selected}, sort_keys=True))
    return result


def phase4_veto(function_class: str, seed: int, threads: int, output: Path) -> dict:
    tag = f"{function_class}-seed{seed}"
    weights_path = output_paths(function_class, seed)["weights"]
    eval_path = eval_output_path(tag, f"veto-{VETO_SEED_BASE}")
    started = time.perf_counter()
    rows = run_eval(weights_path, VETO_SEED_BASE, VETO_MAP_POOL, threads, eval_path)
    elapsed = time.perf_counter() - started
    summary = summarize_rows(rows)
    verdict = veto_gates(summary)
    result = {
        "schema": "troll-farm-d172a-phase4-veto-v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_rev": git_rev(),
        "function_class": function_class,
        "seed": seed,
        "threads": threads,
        "tau": TAU,
        "veto_seed_base": VETO_SEED_BASE,
        "veto_map_pool": VETO_MAP_POOL,
        "eval_seconds": elapsed,
        "weights_sha256": sha256(weights_path),
        "rows_digest_sha256": rows_digest(rows),
        "summary": summary,
        "verdict": verdict,
        "decision": "veto_pass" if verdict["veto_pass"] else "CLOSED",
        "inputs": {"lock": sha256(LOCK), "protocol": sha256(PROTOCOL)},
    }
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"veto_pass": verdict["veto_pass"], "summary": summary}, sort_keys=True))
    return result


def phase4_confirm(function_class: str, seed: int, threads: int, output: Path) -> dict:
    if output.exists():
        raise SystemExit(f"refusing to overwrite {output}: the sealed confirmation block may be opened exactly once")
    tag = f"{function_class}-seed{seed}"
    weights_path = output_paths(function_class, seed)["weights"]
    eval_path = eval_output_path(tag, f"confirmation-{CONFIRMATION_SEED_BASE}")
    if eval_path.exists():
        raise SystemExit(f"refusing to overwrite {eval_path}: the sealed confirmation block may be opened exactly once")
    started = time.perf_counter()
    rows = run_eval(weights_path, CONFIRMATION_SEED_BASE, CONFIRMATION_MAP_POOL, threads, eval_path)
    elapsed = time.perf_counter() - started
    summary = summarize_rows(rows)
    ci = clustered_ci(rows)
    verdict = confirmation_gates(summary, ci)
    result = {
        "schema": "troll-farm-d172a-phase4-confirmation-v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_rev": git_rev(),
        "function_class": function_class,
        "seed": seed,
        "threads": threads,
        "tau": TAU,
        "confirmation_seed_base": CONFIRMATION_SEED_BASE,
        "confirmation_map_pool": CONFIRMATION_MAP_POOL,
        "sealed_block_opened_exactly_once": True,
        "eval_seconds": elapsed,
        "weights_sha256": sha256(weights_path),
        "rows_digest_sha256": rows_digest(rows),
        "summary": summary,
        "clustered_ci": ci,
        "verdict": verdict,
        "decision": "CONFIRMED" if verdict["confirmation_pass"] else "CLOSED",
        "inputs": {"lock": sha256(LOCK), "protocol": sha256(PROTOCOL)},
    }
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"confirmation_pass": verdict["confirmation_pass"], "summary": summary, "ci": ci}, sort_keys=True))
    return result


def verify_thread_parity(function_class: str, seed: int, seed_base: int, map_pool: int) -> dict:
    weights_path = output_paths(function_class, seed)["weights"]
    digests = {}
    for threads in (1, 20):
        eval_path = eval_output_path(f"{function_class}-seed{seed}", f"parity-{threads}-{seed_base}")
        rows = run_eval(weights_path, seed_base, map_pool, threads, eval_path)
        digests[threads] = rows_digest(rows)
    return {"digests": digests, "byte_identical_1_vs_20_threads": digests[1] == digests[20]}


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p3 = sub.add_parser("phase3")
    p3.add_argument("--threads", type=int, default=1)
    p3.add_argument("--output", type=Path, default=BASE / "d172a-dense-counterfactual-option-policy-phase3-result.json")

    p4v = sub.add_parser("phase4-veto")
    p4v.add_argument("--function-class", required=True, choices=list(FUNCTION_CLASSES))
    p4v.add_argument("--seed", type=int, required=True)
    p4v.add_argument("--threads", type=int, default=1)
    p4v.add_argument("--output", type=Path, default=BASE / "d172a-dense-counterfactual-option-policy-phase4-veto-result.json")

    p4c = sub.add_parser("phase4-confirm")
    p4c.add_argument("--function-class", required=True, choices=list(FUNCTION_CLASSES))
    p4c.add_argument("--seed", type=int, required=True)
    p4c.add_argument("--threads", type=int, default=1)
    p4c.add_argument("--output", type=Path, default=BASE / "d172a-dense-counterfactual-option-policy-phase4-confirmation-result.json")

    parity = sub.add_parser("thread-parity")
    parity.add_argument("--function-class", required=True, choices=list(FUNCTION_CLASSES))
    parity.add_argument("--seed", type=int, required=True)
    parity.add_argument("--seed-base", type=int, default=VETO_SEED_BASE)
    parity.add_argument("--map-pool", type=int, default=4)

    args = parser.parse_args()
    if args.command == "phase3":
        phase3(args.threads, args.output)
    elif args.command == "phase4-veto":
        phase4_veto(args.function_class, args.seed, args.threads, args.output)
    elif args.command == "phase4-confirm":
        phase4_confirm(args.function_class, args.seed, args.threads, args.output)
    elif args.command == "thread-parity":
        result = verify_thread_parity(args.function_class, args.seed, args.seed_base, args.map_pool)
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
