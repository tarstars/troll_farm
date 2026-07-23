#!/usr/bin/env python3
"""Compare the f32 D11 actor with its frozen dequantized int8 conversion."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path
from typing import Any

import numpy as np
import torch

from cgauto.rl_level1_env import ACTION_PLANES, OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH
from cgauto.rl_level5_env import Level5CropFirstRepeatedPressureReacquire180VecEnv
from cgauto.train_level1_ppo import SpatialActorCritic, sha256


CORPUS_MAGIC = b"TFD11CORPUS1\0\0\0\0"
CORPUS_HEADER = struct.Struct("<16s7I")


def load_model(path: Path) -> SpatialActorCritic:
    saved = torch.load(path, map_location="cpu", weights_only=False)
    model = SpatialActorCritic()
    model.load_state_dict(saved["model"], strict=True)
    model.eval()
    return model


def encode_corpus(observations: np.ndarray, masks: np.ndarray) -> tuple[bytes, str]:
    observations = np.ascontiguousarray(observations, dtype=np.uint8)
    masks = np.ascontiguousarray(masks, dtype=np.uint8)
    if observations.ndim != 4 or masks.ndim != 4:
        raise ValueError("corpus arrays must be NCHW")
    if observations.shape[0] != masks.shape[0]:
        raise ValueError("observation and mask counts differ")
    if observations.shape[1:] != (OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH):
        raise ValueError(f"unexpected observation shape {observations.shape}")
    if masks.shape[1:] != (ACTION_PLANES, OBS_HEIGHT, OBS_WIDTH):
        raise ValueError(f"unexpected mask shape {masks.shape}")
    header = CORPUS_HEADER.pack(
        CORPUS_MAGIC,
        observations.shape[0],
        OBS_CHANNELS,
        OBS_HEIGHT,
        OBS_WIDTH,
        ACTION_PLANES,
        OBS_HEIGHT,
        OBS_WIDTH,
    )
    raw = header + observations.tobytes(order="C") + masks.tobytes(order="C")
    return zlib.compress(raw, level=9), hashlib.sha256(raw).hexdigest()


def decode_corpus(encoded: bytes) -> tuple[np.ndarray, np.ndarray, str]:
    raw = zlib.decompress(encoded)
    if len(raw) < CORPUS_HEADER.size:
        raise ValueError("truncated corpus header")
    magic, count, obs_channels, obs_height, obs_width, planes, mask_height, mask_width = (
        CORPUS_HEADER.unpack_from(raw)
    )
    if magic != CORPUS_MAGIC:
        raise ValueError("invalid corpus magic")
    obs_shape = (count, obs_channels, obs_height, obs_width)
    mask_shape = (count, planes, mask_height, mask_width)
    obs_bytes = int(np.prod(obs_shape))
    mask_bytes = int(np.prod(mask_shape))
    expected = CORPUS_HEADER.size + obs_bytes + mask_bytes
    if len(raw) != expected:
        raise ValueError(f"corpus length {len(raw)} != expected {expected}")
    observations = np.frombuffer(
        raw, dtype=np.uint8, count=obs_bytes, offset=CORPUS_HEADER.size
    ).reshape(obs_shape).copy()
    masks = np.frombuffer(
        raw,
        dtype=np.uint8,
        count=mask_bytes,
        offset=CORPUS_HEADER.size + obs_bytes,
    ).reshape(mask_shape).copy()
    return observations, masks, hashlib.sha256(raw).hexdigest()


@torch.inference_mode()
def compare_trace(
    source_checkpoint: Path,
    converted_checkpoint: Path,
    *,
    seed_base: int,
    decisions: int,
    num_envs: int,
    corpus_samples: int,
    threads: int,
    corpus_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    if decisions <= 0 or decisions % num_envs:
        raise ValueError("decisions must be a positive multiple of num_envs")
    if not 0 < corpus_samples <= decisions:
        raise ValueError("corpus_samples must be in [1, decisions]")
    torch.set_num_threads(threads)
    source = load_model(source_checkpoint)
    converted = load_model(converted_checkpoint)

    compared = 0
    agreements = 0
    source_illegal = 0
    converted_illegal = 0
    source_nonfinite = 0
    converted_nonfinite = 0
    maximum_absolute_logit_difference = 0.0
    sum_absolute_logit_difference = 0.0
    logit_count = 0
    saved_observations: list[np.ndarray] = []
    saved_masks: list[np.ndarray] = []
    remaining_corpus = corpus_samples

    with Level5CropFirstRepeatedPressureReacquire180VecEnv(
        num_envs, seed_base, max_turns=240
    ) as env:
        while compared < decisions:
            observations_np = env.obs.copy()
            masks_np = env.masks.copy()
            observations = torch.from_numpy(observations_np)
            masks = torch.from_numpy(masks_np)
            source_logits, _ = source(observations)
            converted_logits, _ = converted(observations)
            source_nonfinite += int((~torch.isfinite(source_logits)).sum().item())
            converted_nonfinite += int((~torch.isfinite(converted_logits)).sum().item())

            difference = (source_logits - converted_logits).abs()
            maximum_absolute_logit_difference = max(
                maximum_absolute_logit_difference, float(difference.max().item())
            )
            sum_absolute_logit_difference += float(difference.sum().item())
            logit_count += difference.numel()

            legal = masks.reshape(num_envs, -1).bool()
            minimum = torch.finfo(source_logits.dtype).min
            source_actions = source_logits.masked_fill(~legal, minimum).argmax(dim=1)
            converted_actions = converted_logits.masked_fill(~legal, minimum).argmax(dim=1)
            flat_masks = masks.reshape(num_envs, -1)
            rows = torch.arange(num_envs)
            source_illegal += int((flat_masks[rows, source_actions] == 0).sum().item())
            converted_illegal += int((flat_masks[rows, converted_actions] == 0).sum().item())
            agreements += int((source_actions == converted_actions).sum().item())

            if remaining_corpus:
                take = min(remaining_corpus, num_envs)
                saved_observations.append(observations_np[:take])
                saved_masks.append(masks_np[:take])
                remaining_corpus -= take

            env.step(source_actions.numpy())
            compared += num_envs

    corpus_observations = np.concatenate(saved_observations, axis=0)
    corpus_masks = np.concatenate(saved_masks, axis=0)
    encoded, raw_sha = encode_corpus(corpus_observations, corpus_masks)
    corpus_path.parent.mkdir(parents=True, exist_ok=True)
    corpus_path.write_bytes(encoded)

    result: dict[str, Any] = {
        "source_checkpoint": str(source_checkpoint),
        "source_checkpoint_sha256": sha256(source_checkpoint),
        "converted_checkpoint": str(converted_checkpoint),
        "converted_checkpoint_sha256": sha256(converted_checkpoint),
        "opponent_mode": "crop-first-funded-trio-repeated-pressure-reacquire-180",
        "seed_base": seed_base,
        "decisions": decisions,
        "num_envs": num_envs,
        "threads": threads,
        "masked_argmax_agreements": agreements,
        "masked_argmax_agreement_rate": agreements / decisions,
        "source_illegal_actions": source_illegal,
        "converted_illegal_actions": converted_illegal,
        "source_nonfinite_logits": source_nonfinite,
        "converted_nonfinite_logits": converted_nonfinite,
        "maximum_absolute_logit_difference": maximum_absolute_logit_difference,
        "mean_absolute_logit_difference": sum_absolute_logit_difference / logit_count,
        "trace_gate_passed": (
            agreements / decisions >= 0.995
            and source_illegal == 0
            and converted_illegal == 0
            and source_nonfinite == 0
            and converted_nonfinite == 0
        ),
        "corpus_path": str(corpus_path),
        "corpus_samples": corpus_samples,
        "corpus_raw_sha256": raw_sha,
        "corpus_compressed_bytes": len(encoded),
        "corpus_compressed_sha256": hashlib.sha256(encoded).hexdigest(),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    result["output_path"] = str(output_path)
    result["output_sha256"] = sha256(output_path)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_checkpoint", type=Path)
    parser.add_argument("converted_checkpoint", type=Path)
    parser.add_argument("--seed-base", type=int, default=7_600_000)
    parser.add_argument("--decisions", type=int, default=10_000)
    parser.add_argument("--num-envs", type=int, default=100)
    parser.add_argument("--corpus-samples", type=int, default=512)
    parser.add_argument("--threads", type=int, default=14)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = compare_trace(
        args.source_checkpoint,
        args.converted_checkpoint,
        seed_base=args.seed_base,
        decisions=args.decisions,
        num_envs=args.num_envs,
        corpus_samples=args.corpus_samples,
        threads=args.threads,
        corpus_path=args.corpus,
        output_path=args.output,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
