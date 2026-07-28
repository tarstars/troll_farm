#!/usr/bin/env python3
"""D170b Phase 2 (admission/selection) and Phase 3 (veto/confirmation).

Thin driver that reuses the D170a analyzer's core machinery
(`cgauto/analyze_d170a_family_robust_option_policy.py`, byte-unmodified —
its hash is recorded in the D170b lock, per the repair protocol's explicit
"may be reused unmodified" instruction) -- `evaluate_deterministic`,
`summarize_rows`, `admission_gates`, `veto_gates`, `confirmation_gates`,
`clustered_ci`, `load_model`, `rows_digest` are imported and called as-is,
so the gate formulas and evaluation loop cannot silently diverge from what
was already reviewed and smoke-tested. The *only* thing this driver adds is
which files to read/write: D170b's own fit checkpoints/results (`d170b-`
prefix, via `cgauto.train_d170b_family_robust_option_policy.output_paths`)
instead of D170a's, and `d170b-` prefixed phase2/3 result files. Selection
blocks, veto panel, and confirmation block seed ranges/sizes are the same
frozen constants imported from the D170a analyzer module (Delta 1/3 do not
touch Phase 2/3 ranges or gates). See
`data/analysis/live-agent-6553250/d170b-family-robust-option-policy-repair-protocol-2026-07-28.md`.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import torch

from cgauto.analyze_d170a_family_robust_option_policy import (  # noqa: E402
    CONFIRMATION_MAP_POOL,
    CONFIRMATION_SEED_BASE,
    SELECTION_BLOCK_MAPS,
    SELECTION_BLOCKS,
    SELECTION_MAP_POOL,
    SELECTION_SEED_BASE,
    VETO_MAP_POOL,
    VETO_SEED_BASE,
    admission_gates,
    clustered_ci,
    confirmation_gates,
    evaluate_deterministic,
    load_model,
    rows_digest,
    summarize_rows,
    veto_gates,
)
from cgauto.train_d170b_family_robust_option_policy import (  # noqa: E402
    BASE,
    LOCK,
    MODEL_SEEDS,
    PROTOCOL,
    REPAIR_PROTOCOL,
    VARIANT_ORDER,
    git_rev,
    output_paths,
    sha256,
)

ROOT = Path(__file__).resolve().parents[1]


def fit_result_path(variant: str, seed: int) -> Path:
    return output_paths(variant, seed)["result"]


def fit_checkpoint_path(variant: str, seed: int) -> Path:
    return output_paths(variant, seed)["checkpoint_pt"]


def all_fit_keys() -> list[tuple[str, int]]:
    return [(variant, seed) for variant in VARIANT_ORDER for seed in MODEL_SEEDS[variant]]


def phase2_fit_cache_path(variant: str, seed: int) -> Path:
    return BASE / f"d170b-family-robust-option-policy-{variant}-seed{seed}-phase2-fit.json"


def evaluate_single_fit_for_phase2(variant: str, seed: int) -> dict:
    """Evaluate one fit's checkpoint on the LOBO selection blocks. Process-
    level parallel across fits is far more effective here than
    RAYON_NUM_THREADS within one process evaluating fits sequentially (the
    bottleneck is Python/ctypes round-trip count per decision, not
    intra-round Rust compute) -- see `phase2-fit` CLI subcommand, run as N
    concurrent single-threaded OS processes, mirroring the Phase 1
    training pattern."""
    result_path = fit_result_path(variant, seed)
    if not result_path.exists():
        return {"variant": variant, "seed": seed, "status": "missing_result"}
    fit_result = json.loads(result_path.read_text())
    if fit_result["decision"] != "trained":
        return {"variant": variant, "seed": seed, "status": fit_result["decision"]}
    checkpoint = fit_checkpoint_path(variant, seed)
    model = load_model(checkpoint)
    started = time.perf_counter()
    rows = evaluate_deterministic(model, SELECTION_SEED_BASE, SELECTION_MAP_POOL)
    elapsed = time.perf_counter() - started
    summary = summarize_rows(
        rows, block_seed_base=SELECTION_SEED_BASE, block_maps=SELECTION_BLOCK_MAPS
    )
    admission = admission_gates(summary)
    return {
        "variant": variant,
        "seed": seed,
        "status": "evaluated",
        "checkpoint_sha256": sha256(checkpoint),
        "eval_seconds": elapsed,
        "rows_digest_sha256": rows_digest(rows),
        "summary": summary,
        "admission": admission,
    }


def phase2_fit_cli(variant: str, seed: int, threads: int) -> int:
    os.environ["RAYON_NUM_THREADS"] = str(threads)
    torch.set_num_threads(max(threads, 1))
    fit_summary = evaluate_single_fit_for_phase2(variant, seed)
    cache = phase2_fit_cache_path(variant, seed)
    cache.write_text(json.dumps(fit_summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"event": "phase2_fit_cli_done", **{k: fit_summary.get(k) for k in ("variant", "seed", "status")}}, sort_keys=True))
    return 0


def phase2(threads: int, output: Path) -> dict:
    os.environ["RAYON_NUM_THREADS"] = str(threads)
    torch.set_num_threads(max(threads, 1))
    fit_summaries = []
    for variant, seed in all_fit_keys():
        cache = phase2_fit_cache_path(variant, seed)
        if cache.exists():
            fit_summary = json.loads(cache.read_text())
        else:
            fit_summary = evaluate_single_fit_for_phase2(variant, seed)
        fit_summaries.append(fit_summary)
        print(
            json.dumps(
                {
                    "event": "phase2_fit",
                    "variant": variant,
                    "seed": seed,
                    "status": fit_summary["status"],
                    "pooled_mean": fit_summary.get("summary", {}).get("pooled_mean"),
                    "worst_block": fit_summary.get("summary", {}).get("worst_block"),
                    "worst_family": fit_summary.get("summary", {}).get("worst_family"),
                    "admitted": fit_summary.get("admission", {}).get("admitted"),
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
        selected = {"variant": admitted_sorted[0]["variant"], "seed": admitted_sorted[0]["seed"]}

    result = {
        "schema": "troll-farm-d170b-phase2-admission-selection-v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_rev": git_rev(),
        "threads": threads,
        "selection_seed_base": SELECTION_SEED_BASE,
        "selection_map_pool": SELECTION_MAP_POOL,
        "selection_blocks": SELECTION_BLOCKS,
        "fits": fit_summaries,
        "admitted_count": len(admitted),
        "selected": selected,
        "decision": "selection_admitted" if selected else "no_admission_close",
        "inputs": {"lock": sha256(LOCK), "protocol": sha256(PROTOCOL), "repair_protocol": sha256(REPAIR_PROTOCOL)},
    }
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"admitted_count": len(admitted), "selected": selected}, sort_keys=True))
    return result


def phase3_veto(variant: str, seed: int, threads: int, output: Path) -> dict:
    os.environ["RAYON_NUM_THREADS"] = str(threads)
    torch.set_num_threads(max(threads, 1))
    checkpoint = fit_checkpoint_path(variant, seed)
    model = load_model(checkpoint)
    started = time.perf_counter()
    rows = evaluate_deterministic(model, VETO_SEED_BASE, VETO_MAP_POOL)
    elapsed = time.perf_counter() - started
    summary = summarize_rows(rows)
    verdict = veto_gates(summary)
    result = {
        "schema": "troll-farm-d170b-phase3-veto-v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_rev": git_rev(),
        "variant": variant,
        "seed": seed,
        "threads": threads,
        "veto_seed_base": VETO_SEED_BASE,
        "veto_map_pool": VETO_MAP_POOL,
        "eval_seconds": elapsed,
        "checkpoint_sha256": sha256(checkpoint),
        "rows_digest_sha256": rows_digest(rows),
        "summary": summary,
        "verdict": verdict,
        "decision": "veto_pass" if verdict["veto_pass"] else "veto_fail_close",
        "inputs": {"lock": sha256(LOCK), "protocol": sha256(PROTOCOL), "repair_protocol": sha256(REPAIR_PROTOCOL)},
    }
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"veto_pass": verdict["veto_pass"], "summary": summary}, sort_keys=True))
    return result


def phase3_confirm(variant: str, seed: int, threads: int, output: Path) -> dict:
    if output.exists():
        raise SystemExit(
            f"refusing to overwrite {output}: the sealed confirmation block may be opened exactly once"
        )
    os.environ["RAYON_NUM_THREADS"] = str(threads)
    torch.set_num_threads(max(threads, 1))
    checkpoint = fit_checkpoint_path(variant, seed)
    model = load_model(checkpoint)
    started = time.perf_counter()
    rows = evaluate_deterministic(model, CONFIRMATION_SEED_BASE, CONFIRMATION_MAP_POOL)
    elapsed = time.perf_counter() - started
    summary = summarize_rows(rows)
    ci = clustered_ci(rows)
    verdict = confirmation_gates(summary, ci)
    result = {
        "schema": "troll-farm-d170b-phase3-confirmation-v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_rev": git_rev(),
        "variant": variant,
        "seed": seed,
        "threads": threads,
        "confirmation_seed_base": CONFIRMATION_SEED_BASE,
        "confirmation_map_pool": CONFIRMATION_MAP_POOL,
        "sealed_block_opened_exactly_once": True,
        "eval_seconds": elapsed,
        "checkpoint_sha256": sha256(checkpoint),
        "rows_digest_sha256": rows_digest(rows),
        "summary": summary,
        "clustered_ci": ci,
        "verdict": verdict,
        "decision": "CONFIRMED" if verdict["confirmation_pass"] else "confirmation_fail_close",
        "inputs": {"lock": sha256(LOCK), "protocol": sha256(PROTOCOL), "repair_protocol": sha256(REPAIR_PROTOCOL)},
    }
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"confirmation_pass": verdict["confirmation_pass"], "summary": summary, "ci": ci}, sort_keys=True))
    return result


def verify_thread_parity(variant: str, seed: int, seed_base: int, map_pool: int) -> dict:
    """Run the same deterministic evaluation at 1 and 20 Rayon threads and
    hash-compare the row set for byte identity (the frozen threading rule)."""
    checkpoint = fit_checkpoint_path(variant, seed)
    digests = {}
    for threads in (1, 20):
        os.environ["RAYON_NUM_THREADS"] = str(threads)
        torch.set_num_threads(1)
        model = load_model(checkpoint)
        rows = evaluate_deterministic(model, seed_base, map_pool)
        digests[threads] = rows_digest(rows)
    identical = digests[1] == digests[20]
    return {"digests": digests, "byte_identical_1_vs_20_threads": identical}


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p2 = sub.add_parser("phase2")
    p2.add_argument("--threads", type=int, default=1)
    p2.add_argument("--output", type=Path, default=BASE / "d170b-family-robust-option-policy-phase2-result.json")

    p2f = sub.add_parser("phase2-fit")
    p2f.add_argument("--variant", required=True, choices=VARIANT_ORDER)
    p2f.add_argument("--seed", type=int, required=True)
    p2f.add_argument("--threads", type=int, default=1)

    p3v = sub.add_parser("phase3-veto")
    p3v.add_argument("--variant", required=True, choices=VARIANT_ORDER)
    p3v.add_argument("--seed", type=int, required=True)
    p3v.add_argument("--threads", type=int, default=1)
    p3v.add_argument("--output", type=Path, default=BASE / "d170b-family-robust-option-policy-phase3-veto-result.json")

    p3c = sub.add_parser("phase3-confirm")
    p3c.add_argument("--variant", required=True, choices=VARIANT_ORDER)
    p3c.add_argument("--seed", type=int, required=True)
    p3c.add_argument("--threads", type=int, default=1)
    p3c.add_argument(
        "--output", type=Path, default=BASE / "d170b-family-robust-option-policy-phase3-confirmation-result.json"
    )

    parity = sub.add_parser("thread-parity")
    parity.add_argument("--variant", required=True, choices=VARIANT_ORDER)
    parity.add_argument("--seed", type=int, required=True)
    parity.add_argument("--seed-base", type=int, default=VETO_SEED_BASE)
    parity.add_argument("--map-pool", type=int, default=4)
    parity.add_argument("--output", type=Path, default=None)

    args = parser.parse_args()
    if args.command == "phase2":
        phase2(args.threads, args.output)
    elif args.command == "phase2-fit":
        return phase2_fit_cli(args.variant, args.seed, args.threads)
    elif args.command == "phase3-veto":
        phase3_veto(args.variant, args.seed, args.threads, args.output)
    elif args.command == "phase3-confirm":
        phase3_confirm(args.variant, args.seed, args.threads, args.output)
    elif args.command == "thread-parity":
        result = verify_thread_parity(args.variant, args.seed, args.seed_base, args.map_pool)
        print(json.dumps(result, indent=2, sort_keys=True))
        if args.output:
            args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
