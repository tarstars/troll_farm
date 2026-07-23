#!/usr/bin/env python3
"""Export the frozen spatial actor with per-output-channel symmetric int8 weights."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import OrderedDict
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import torch

from cgauto.train_level1_ppo import SpatialActorCritic, sha256


ACTOR_LAYERS = (
    "stem.0",
    "tower.0.conv1",
    "tower.0.conv2",
    "tower.1.conv1",
    "tower.1.conv2",
    "tower.2.conv1",
    "tower.2.conv2",
    "tower.3.conv1",
    "tower.3.conv2",
    "actor",
)
FORMAT = "troll-farm-spatial-actor-int8-per-output-v1"


def _tensor_digest(state: Mapping[str, torch.Tensor], names: list[str]) -> str:
    digest = hashlib.sha256()
    for name in names:
        encoded = name.encode("utf-8")
        array = np.ascontiguousarray(state[name].detach().cpu().numpy().astype("<f4"))
        digest.update(len(encoded).to_bytes(4, "little"))
        digest.update(encoded)
        digest.update(array.ndim.to_bytes(4, "little"))
        for extent in array.shape:
            digest.update(int(extent).to_bytes(8, "little"))
        digest.update(array.tobytes())
    return digest.hexdigest()


def quantize_actor_state(
    source_state: Mapping[str, torch.Tensor],
) -> tuple[OrderedDict[str, torch.Tensor], bytes, list[dict[str, Any]]]:
    """Return dequantized f32 state, compact payload, and ordered layer metadata."""

    expected = SpatialActorCritic().state_dict()
    if set(source_state) != set(expected):
        missing = sorted(set(expected) - set(source_state))
        extra = sorted(set(source_state) - set(expected))
        raise ValueError(f"checkpoint model key mismatch: missing={missing}, extra={extra}")

    converted: OrderedDict[str, torch.Tensor] = OrderedDict(
        (name, tensor.detach().cpu().clone()) for name, tensor in source_state.items()
    )
    payload = bytearray()
    layers: list[dict[str, Any]] = []

    for layer_index, prefix in enumerate(ACTOR_LAYERS):
        weight_name = f"{prefix}.weight"
        bias_name = f"{prefix}.bias"
        weight = np.ascontiguousarray(
            source_state[weight_name].detach().cpu().numpy().astype(np.float32)
        )
        bias = np.ascontiguousarray(
            source_state[bias_name].detach().cpu().numpy().astype("<f4")
        )
        if weight.ndim != 4 or bias.shape != (weight.shape[0],):
            raise ValueError(
                f"unsupported convolution tensors for {prefix}: "
                f"weight={weight.shape}, bias={bias.shape}"
            )

        flattened = weight.reshape(weight.shape[0], -1)
        scales = (np.max(np.abs(flattened), axis=1) / 127.0).astype(np.float32)
        scales = np.where(scales == 0.0, np.float32(1.0), scales).astype("<f4")
        broadcast_shape = (-1,) + (1,) * (weight.ndim - 1)
        quantized = np.rint(weight / scales.reshape(broadcast_shape))
        quantized = np.clip(quantized, -127, 127).astype(np.int8)
        dequantized = quantized.astype(np.float32) * scales.reshape(broadcast_shape)
        converted[weight_name] = torch.from_numpy(np.ascontiguousarray(dequantized))

        weight_offset = len(payload)
        weight_bytes = quantized.tobytes(order="C")
        payload.extend(weight_bytes)
        scale_offset = len(payload)
        scale_bytes = scales.tobytes(order="C")
        payload.extend(scale_bytes)
        bias_offset = len(payload)
        bias_bytes = bias.tobytes(order="C")
        payload.extend(bias_bytes)

        layers.append(
            {
                "index": layer_index,
                "name": prefix,
                "weight_name": weight_name,
                "bias_name": bias_name,
                "weight_shape": list(weight.shape),
                "weight_count": int(weight.size),
                "output_channels": int(weight.shape[0]),
                "kernel": [int(weight.shape[2]), int(weight.shape[3])],
                "weight_offset": weight_offset,
                "weight_bytes": len(weight_bytes),
                "scale_offset": scale_offset,
                "scale_bytes": len(scale_bytes),
                "bias_offset": bias_offset,
                "bias_bytes": len(bias_bytes),
                "maximum_absolute_weight_error": float(
                    np.max(np.abs(weight - dequantized))
                ),
            }
        )

    return converted, bytes(payload), layers


def export_actor(
    checkpoint: Path,
    *,
    payload_path: Path,
    manifest_path: Path,
    verification_checkpoint_path: Path,
) -> dict[str, Any]:
    checkpoint = checkpoint.resolve()
    saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
    if not isinstance(saved, dict) or "model" not in saved:
        raise ValueError("checkpoint must contain a model state dictionary")
    source_state = saved["model"]
    converted, payload, layers = quantize_actor_state(source_state)

    actor_names = [
        name
        for prefix in ACTOR_LAYERS
        for name in (f"{prefix}.weight", f"{prefix}.bias")
    ]
    source_sha = sha256(checkpoint)
    payload_sha = hashlib.sha256(payload).hexdigest()
    manifest: dict[str, Any] = {
        "format": FORMAT,
        "source_checkpoint": str(checkpoint),
        "source_checkpoint_sha256": source_sha,
        "observation_shape": [104, 11, 22],
        "action_shape": [13, 11, 22],
        "actor_parameter_count": int(sum(source_state[name].numel() for name in actor_names)),
        "critic_parameter_count_omitted": int(
            sum(tensor.numel() for name, tensor in source_state.items() if name.startswith("critic."))
        ),
        "quantization": {
            "weights": "signed-int8 symmetric per output channel",
            "scale": "f32 max_abs/127; all-zero channel scale 1",
            "rounding": "numpy.rint nearest-even",
            "clip": [-127, 127],
            "bias": "unaltered little-endian f32",
            "runtime_accumulation": "f32 after dequantization",
        },
        "payload_bytes": len(payload),
        "payload_sha256": payload_sha,
        "source_actor_tensor_sha256": _tensor_digest(source_state, actor_names),
        "dequantized_actor_tensor_sha256": _tensor_digest(converted, actor_names),
        "maximum_absolute_weight_error": max(
            layer["maximum_absolute_weight_error"] for layer in layers
        ),
        "layers": layers,
    }

    payload_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    verification_checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    payload_path.write_bytes(payload)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    verification = {
        "model": converted,
        "source_checkpoint": str(checkpoint),
        "source_checkpoint_sha256": source_sha,
        "deployment_quantization": manifest,
    }
    torch.save(verification, verification_checkpoint_path)

    result = dict(manifest)
    result.update(
        {
            "payload_path": str(payload_path),
            "manifest_path": str(manifest_path),
            "manifest_sha256": sha256(manifest_path),
            "verification_checkpoint_path": str(verification_checkpoint_path),
            "verification_checkpoint_sha256": sha256(verification_checkpoint_path),
        }
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("--payload", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--verification-checkpoint", type=Path, required=True)
    args = parser.parse_args()
    result = export_actor(
        args.checkpoint,
        payload_path=args.payload,
        manifest_path=args.manifest,
        verification_checkpoint_path=args.verification_checkpoint,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
