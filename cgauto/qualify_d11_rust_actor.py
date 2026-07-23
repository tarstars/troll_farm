#!/usr/bin/env python3
"""Qualify the frozen generated Rust D11 actor against Python and its latency gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import struct
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import torch

from cgauto.compare_d11_actor_export import decode_corpus, load_model
from cgauto.rl_level1_env import ACTION_PLANES, OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH


INPUT_MAGIC = b"TFD11IN1"
OUTPUT_MAGIC = b"TFD11OU1"
HEADER = struct.Struct("<8sI")
OBSERVATION_BYTES = OBS_CHANNELS * OBS_HEIGHT * OBS_WIDTH
ACTION_COUNT = ACTION_PLANES * OBS_HEIGHT * OBS_WIDTH
OUTPUT_RECORD_BYTES = ACTION_COUNT * 4 + 4


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def encode_runner_input(observations: np.ndarray, masks: np.ndarray) -> bytes:
    observations = np.ascontiguousarray(observations, dtype=np.uint8)
    masks = np.ascontiguousarray(masks, dtype=np.uint8)
    if observations.ndim != 4 or observations.shape[1:] != (
        OBS_CHANNELS,
        OBS_HEIGHT,
        OBS_WIDTH,
    ):
        raise ValueError(f"unexpected observation shape {observations.shape}")
    if masks.ndim != 4 or masks.shape != (
        observations.shape[0],
        ACTION_PLANES,
        OBS_HEIGHT,
        OBS_WIDTH,
    ):
        raise ValueError(f"unexpected mask shape {masks.shape}")
    return (
        HEADER.pack(INPUT_MAGIC, observations.shape[0])
        + observations.tobytes(order="C")
        + masks.tobytes(order="C")
    )


def decode_runner_output(data: bytes, expected_count: int) -> tuple[np.ndarray, np.ndarray]:
    if len(data) < HEADER.size:
        raise ValueError("truncated runner output")
    magic, count = HEADER.unpack_from(data)
    if magic != OUTPUT_MAGIC or count != expected_count:
        raise ValueError(f"unexpected runner output header magic={magic!r} count={count}")
    expected_bytes = HEADER.size + count * OUTPUT_RECORD_BYTES
    if len(data) != expected_bytes:
        raise ValueError(f"runner output length {len(data)} != {expected_bytes}")
    body = memoryview(data)[HEADER.size:]
    logits = np.ndarray(
        (count, ACTION_COUNT),
        dtype="<f4",
        buffer=body,
        strides=(OUTPUT_RECORD_BYTES, 4),
    ).copy()
    actions = np.ndarray(
        (count,),
        dtype="<u4",
        buffer=body,
        offset=ACTION_COUNT * 4,
        strides=(OUTPUT_RECORD_BYTES,),
    ).astype(np.int64)
    return logits, actions


@torch.inference_mode()
def python_reference(
    checkpoint: Path,
    observations: np.ndarray,
    masks: np.ndarray,
    *,
    threads: int,
    batch_size: int,
) -> tuple[np.ndarray, np.ndarray]:
    torch.set_num_threads(threads)
    model = load_model(checkpoint)
    chunks: list[np.ndarray] = []
    for start in range(0, len(observations), batch_size):
        logits, _ = model(torch.from_numpy(observations[start : start + batch_size]))
        chunks.append(logits.cpu().numpy())
    combined = np.ascontiguousarray(np.concatenate(chunks), dtype=np.float32)
    legal = masks.reshape(len(masks), -1).astype(bool)
    masked = np.where(legal, combined, np.float32(-np.inf))
    return combined, masked.argmax(axis=1)


def qualify(
    source_path: Path,
    binary_path: Path,
    checkpoint: Path,
    corpus_path: Path,
    payload_path: Path,
    output_path: Path,
    *,
    rustc: str,
    threads: int,
    batch_size: int,
    benchmark_pairs: int,
) -> dict[str, Any]:
    source_path = source_path.resolve()
    binary_path = binary_path.resolve()
    checkpoint = checkpoint.resolve()
    corpus_path = corpus_path.resolve()
    payload_path = payload_path.resolve()
    output_path = output_path.resolve()
    compiler = shutil.which(rustc)
    if compiler is None:
        raise ValueError(f"compiler not found: {rustc}")
    compiler_path = Path(compiler).resolve()
    compiler_version = subprocess.run(
        [compiler, "--version", "--verbose"],
        check=True,
        capture_output=True,
        text=True,
    )
    compile_result = subprocess.run(
        [compiler, "--edition=2021", "-O", str(source_path), "-o", str(binary_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if compile_result.returncode != 0:
        raise RuntimeError(f"rustc failed:\n{compile_result.stderr}")

    encoded_corpus = corpus_path.read_bytes()
    observations, masks, corpus_raw_sha = decode_corpus(encoded_corpus)
    runner_input = encode_runner_input(observations, masks)
    reference_logits, reference_actions = python_reference(
        checkpoint,
        observations,
        masks,
        threads=threads,
        batch_size=batch_size,
    )
    parity_process = subprocess.run(
        [str(binary_path)],
        input=runner_input,
        capture_output=True,
        check=False,
        timeout=600,
    )
    if parity_process.returncode != 0:
        raise RuntimeError(
            f"Rust parity runner exited {parity_process.returncode}: "
            f"{parity_process.stderr.decode('utf-8', errors='replace')}"
        )
    rust_logits, rust_actions = decode_runner_output(parity_process.stdout, len(observations))
    absolute_difference = np.abs(
        rust_logits.astype(np.float64) - reference_logits.astype(np.float64)
    )
    flattened_masks = masks.reshape(len(masks), -1)
    rows = np.arange(len(masks))
    illegal_actions = int(np.count_nonzero(flattened_masks[rows, rust_actions] == 0))
    agreements = int(np.count_nonzero(rust_actions == reference_actions))
    reference_nonfinite = int(np.count_nonzero(~np.isfinite(reference_logits)))
    rust_nonfinite = int(np.count_nonzero(~np.isfinite(rust_logits)))
    parity_gate_passed = (
        float(absolute_difference.max()) <= 1e-4
        and agreements == len(observations)
        and illegal_actions == 0
        and reference_nonfinite == 0
        and rust_nonfinite == 0
        and not parity_process.stderr
    )
    benchmark: dict[str, Any] | None = None
    benchmark_stderr = ""
    timing_gate_passed = False
    if parity_gate_passed:
        benchmark_process = subprocess.run(
            [str(binary_path), "--bench", str(benchmark_pairs)],
            input=runner_input,
            capture_output=True,
            check=False,
            timeout=600,
        )
        benchmark_stderr = benchmark_process.stderr.decode("utf-8", errors="replace")
        if benchmark_process.returncode != 0:
            raise RuntimeError(
                f"Rust benchmark exited {benchmark_process.returncode}: {benchmark_stderr}"
            )
        benchmark = json.loads(benchmark_process.stdout)
        timing_gate_passed = (
            benchmark["iterations"] >= 1_000
            and benchmark["initialization_first_pair_ns"] <= 1_000_000_000
            and benchmark["p95_pair_ns"] <= 45_000_000
            and benchmark["maximum_pair_ns"] <= 50_000_000
            and not benchmark_stderr
        )
    source_bytes = source_path.stat().st_size
    source_gate_passed = source_bytes < 100_000
    result: dict[str, Any] = {
        "source_path": str(source_path),
        "source_bytes": source_bytes,
        "source_sha256": sha256_path(source_path),
        "binary_path": str(binary_path),
        "binary_bytes": binary_path.stat().st_size,
        "binary_sha256": sha256_path(binary_path),
        "payload_path": str(payload_path),
        "payload_bytes": payload_path.stat().st_size,
        "payload_sha256": sha256_path(payload_path),
        "checkpoint": str(checkpoint),
        "checkpoint_sha256": sha256_path(checkpoint),
        "corpus_path": str(corpus_path),
        "corpus_samples": len(observations),
        "corpus_compressed_bytes": len(encoded_corpus),
        "corpus_compressed_sha256": sha256_bytes(encoded_corpus),
        "corpus_raw_sha256": corpus_raw_sha,
        "compiler_path": str(compiler_path),
        "compiler_sha256": sha256_path(compiler_path),
        "compiler_version": compiler_version.stdout.strip(),
        "compiler_version_sha256": sha256_bytes(compiler_version.stdout.encode()),
        "reference_threads": threads,
        "reference_batch_size": batch_size,
        "compared_logits": int(reference_logits.size),
        "maximum_absolute_logit_difference": float(absolute_difference.max()),
        "mean_absolute_logit_difference": float(absolute_difference.mean()),
        "masked_argmax_agreements": agreements,
        "masked_argmax_agreement_rate": agreements / len(observations),
        "rust_illegal_actions": illegal_actions,
        "reference_nonfinite_logits": reference_nonfinite,
        "rust_nonfinite_logits": rust_nonfinite,
        "compile_stdout": compile_result.stdout,
        "compile_stderr": compile_result.stderr,
        "runner_stderr": parity_process.stderr.decode("utf-8", errors="replace"),
        "benchmark_stderr": benchmark_stderr,
        "benchmark": benchmark,
        "parity_gate_passed": parity_gate_passed,
        "timing_gate_passed": timing_gate_passed,
        "source_gate_passed": source_gate_passed,
        "phase_d_gate_passed": parity_gate_passed and timing_gate_passed,
        "phase_e_kernel_source_gate_passed": source_gate_passed,
    }
    if not math.isfinite(result["maximum_absolute_logit_difference"]):
        result["parity_gate_passed"] = False
        result["phase_d_gate_passed"] = False
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result["output_path"] = str(output_path)
    result["output_sha256"] = sha256_path(output_path)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("corpus", type=Path)
    parser.add_argument("payload", type=Path)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--rustc", default="rustc")
    parser.add_argument("--threads", type=int, default=14)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--benchmark-pairs", type=int, default=1_000)
    args = parser.parse_args()
    if args.threads <= 0 or args.batch_size <= 0 or args.benchmark_pairs < 1_000:
        raise SystemExit("threads/batch-size must be positive and benchmark-pairs >= 1000")
    result = qualify(
        args.source,
        args.binary,
        args.checkpoint,
        args.corpus,
        args.payload,
        args.output,
        rustc=args.rustc,
        threads=args.threads,
        batch_size=args.batch_size,
        benchmark_pairs=args.benchmark_pairs,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
