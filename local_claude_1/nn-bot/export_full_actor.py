#!/usr/bin/env python3
"""Export the full-game spatial actor and train-plan scorer as one int8 payload."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import OrderedDict
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import torch

from cgauto.train_level1_ppo import (
    PLAN_ACTION_SIZE,
    PLAN_VOCAB_VERSION,
    SpatialActorCritic,
    sha256,
)


CONV_LAYERS = (
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
LINEAR_LAYERS = ("plan.mlp.0", "plan.mlp.2")
NULL_BIAS = "plan.null_bias"
OMITTED_PREFIX = "critic."
FORMAT = "troll-farm-full-actor-int8-refined-v1"
LAYER_BITS = {"actor": 16, "plan.mlp.0": 16, "plan.mlp.2": 16}
QUANTIZATION_GROUP_SIZE = 64
PLAN_SANITIZER = {"phase": "plan", "zero_planes": list(range(59, 72)) + [98]}


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


def _quantize_layer(
    source_state: Mapping[str, torch.Tensor],
    converted: OrderedDict[str, torch.Tensor],
    payload: bytearray,
    prefix: str,
    layer_index: int,
) -> dict[str, Any]:
    weight_name = f"{prefix}.weight"
    bias_name = f"{prefix}.bias"
    weight = np.ascontiguousarray(
        source_state[weight_name].detach().cpu().numpy().astype(np.float32)
    )
    bias = np.ascontiguousarray(
        source_state[bias_name].detach().cpu().numpy().astype("<f4")
    )
    if weight.ndim not in (2, 4) or bias.shape != (weight.shape[0],):
        raise ValueError(
            f"unsupported layer tensors for {prefix}: weight={weight.shape}, bias={bias.shape}"
        )

    flattened = weight.reshape(weight.shape[0], -1)
    bits = LAYER_BITS.get(prefix, 16)
    maximum = (1 << (bits - 1)) - 1
    step = 1 << (bits - 8)
    group_size = QUANTIZATION_GROUP_SIZE
    groups_per_output = (flattened.shape[1] + group_size - 1) // group_size
    scales = np.empty((flattened.shape[0], groups_per_output), dtype="<f4")
    quantized = np.empty_like(flattened, dtype=np.int32)
    for group in range(groups_per_output):
        start = group * group_size
        stop = min(start + group_size, flattened.shape[1])
        values = flattened[:, start:stop]
        scale = (np.max(np.abs(values), axis=1) / maximum).astype(np.float32)
        scale = np.where(scale == 0.0, np.float32(1.0), scale)
        for _ in range(4):
            integers = np.clip(np.rint(values / scale[:, None]), -maximum, maximum)
            denominator = np.sum(integers * integers, axis=1)
            fitted = np.divide(
                np.sum(values * integers, axis=1),
                denominator,
                out=scale.astype(np.float64),
                where=denominator != 0,
            ).astype(np.float32)
            scale = np.where(fitted > 0.0, fitted, scale)
        scales[:, group] = scale
        quantized[:, start:stop] = np.clip(
            np.rint(values / scale[:, None]), -maximum, maximum
        ).astype(np.int32)
    # The signed int8 is the coarse payload. Packed residual bits refine each integer without
    # changing the exporter's signed-int8/per-group-scale contract.
    coarse = np.floor_divide(quantized, step).astype(np.int8)
    refinement = (quantized - coarse.astype(np.int32) * step).astype(np.uint8).reshape(-1)
    refinement_bits = bits - 8
    packed_refinement = np.zeros(
        (refinement.size * refinement_bits + 7) // 8, dtype=np.uint8
    )
    for index, value in enumerate(refinement):
        bit = index * refinement_bits
        packed_refinement[bit // 8] |= int(value) << (bit % 8) & 0xFF
        if bit % 8 + refinement_bits > 8:
            packed_refinement[bit // 8 + 1] |= int(value) >> (8 - bit % 8)
    integers = coarse.astype(np.int32) * step + refinement.reshape(coarse.shape)
    dequantized = np.empty_like(flattened, dtype=np.float32)
    for group in range(groups_per_output):
        start = group * group_size
        stop = min(start + group_size, flattened.shape[1])
        dequantized[:, start:stop] = (
            integers[:, start:stop].astype(np.float32) * scales[:, group : group + 1]
        )
    coarse = coarse.reshape(weight.shape)
    dequantized = dequantized.reshape(weight.shape)
    converted[weight_name] = torch.from_numpy(np.ascontiguousarray(dequantized))

    weight_offset = len(payload)
    weight_bytes = coarse.tobytes(order="C")
    payload.extend(weight_bytes)
    refinement_offset = len(payload)
    refinement_bytes = packed_refinement.tobytes(order="C")
    payload.extend(refinement_bytes)
    scale_offset = len(payload)
    scale_bytes = scales.tobytes(order="C")
    payload.extend(scale_bytes)
    bias_offset = len(payload)
    bias_bytes = bias.tobytes(order="C")
    payload.extend(bias_bytes)
    return {
        "index": layer_index,
        "name": prefix,
        "kind": "conv2d" if weight.ndim == 4 else "linear",
        "weight_name": weight_name,
        "bias_name": bias_name,
        "weight_shape": list(weight.shape),
        "weight_count": int(weight.size),
        "output_channels": int(weight.shape[0]),
        "refinement_offset": refinement_offset,
        "refinement_bytes": len(refinement_bytes),
        "effective_bits": bits,
        "quantization_group_size": group_size,
        "groups_per_output": groups_per_output,
        "weight_offset": weight_offset,
        "weight_bytes": len(weight_bytes),
        "scale_offset": scale_offset,
        "scale_bytes": len(scale_bytes),
        "bias_offset": bias_offset,
        "bias_bytes": len(bias_bytes),
        "maximum_absolute_weight_error": float(np.max(np.abs(weight - dequantized))),
    }


def quantize_full_actor_state(
    source_state: Mapping[str, torch.Tensor],
) -> tuple[OrderedDict[str, torch.Tensor], bytes, list[dict[str, Any]], dict[str, Any]]:
    """Return dequantized verification state, payload, layer metadata and null metadata."""

    expected = SpatialActorCritic(plan_head=True).state_dict()
    if set(source_state) != set(expected):
        missing = sorted(set(expected) - set(source_state))
        extra = sorted(set(source_state) - set(expected))
        raise ValueError(f"checkpoint model key mismatch: missing={missing}, extra={extra}")
    converted: OrderedDict[str, torch.Tensor] = OrderedDict(
        (name, tensor.detach().cpu().clone()) for name, tensor in source_state.items()
    )
    payload = bytearray()
    layers = [
        _quantize_layer(source_state, converted, payload, prefix, index)
        for index, prefix in enumerate(CONV_LAYERS + LINEAR_LAYERS)
    ]
    null = np.ascontiguousarray(
        source_state[NULL_BIAS].detach().cpu().numpy().astype("<f4")
    )
    if null.shape != (1,):
        raise ValueError(f"unsupported null bias shape: {null.shape}")
    null_meta = {"name": NULL_BIAS, "offset": len(payload), "bytes": len(null.tobytes())}
    payload.extend(null.tobytes())
    return converted, bytes(payload), layers, null_meta


def export_full_actor(
    checkpoint: Path,
    *,
    payload_path: Path,
    manifest_path: Path,
    verification_checkpoint_path: Path,
) -> dict[str, Any]:
    checkpoint = checkpoint.resolve()
    saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
    if not isinstance(saved, dict) or set(saved) != {"config", "global_step", "model", "optimizer"}:
        raise ValueError("checkpoint must have exactly config/global_step/model/optimizer")
    config = saved["config"]
    if not isinstance(config, dict) or config.get("plan_vocab_version") != PLAN_VOCAB_VERSION:
        raise ValueError(
            f"checkpoint plan vocabulary {config.get('plan_vocab_version')!r} does not match "
            f"{PLAN_VOCAB_VERSION!r}"
        )
    source_state = saved["model"]
    converted, payload, layers, null_meta = quantize_full_actor_state(source_state)
    shipping_names = [name for name in source_state if not name.startswith(OMITTED_PREFIX)]
    omitted_names = [name for name in source_state if name.startswith(OMITTED_PREFIX)]
    source_sha = sha256(checkpoint)
    payload_sha = hashlib.sha256(payload).hexdigest()
    manifest: dict[str, Any] = {
        "format": FORMAT,
        "source_checkpoint": str(checkpoint),
        "source_checkpoint_sha256": source_sha,
        "checkpoint_keys": sorted(saved),
        "observation_shape": [104, 11, 22],
        "action_shape": [13, 11, 22],
        "plan_action_size": PLAN_ACTION_SIZE,
        "plan_vocab_version": PLAN_VOCAB_VERSION,
        "plan_sanitizer": PLAN_SANITIZER,
        "decoding": {"plan": "masked_argmax", "command": "masked_argmax", "beam": False},
        "shipping_parameter_count": int(sum(source_state[name].numel() for name in shipping_names)),
        "critic_parameter_count_omitted": int(
            sum(source_state[name].numel() for name in omitted_names)
        ),
        "quantization": {
            "weights": "signed-int8 coarse values plus packed unsigned residual bits per weight",
            "effective_integer": "coarse*2^(bits-8)+residual; 16 effective bits throughout",
            "group_size": 64,
            "scale": "one f32 per weight group within each output; max_abs/signed_max seed, four least-squares refits",
            "rounding": "numpy.rint nearest-even",
            "coarse_clip": [-128, 127],
            "effective_clip": [-32767, 32767],
            "bias": "unaltered little-endian f32",
            "runtime_accumulation": "f32 after dequantization",
        },
        "payload_bytes": len(payload),
        "payload_sha256": payload_sha,
        "source_shipping_tensor_sha256": _tensor_digest(source_state, shipping_names),
        "dequantized_shipping_tensor_sha256": _tensor_digest(converted, shipping_names),
        "maximum_absolute_weight_error": max(
            layer["maximum_absolute_weight_error"] for layer in layers
        ),
        "layers": layers,
        "null_bias": null_meta,
    }

    payload_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    verification_checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    payload_path.write_bytes(payload)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    verification = {
        "config": dict(config),
        "global_step": saved["global_step"],
        "model": converted,
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
    result = export_full_actor(
        args.checkpoint,
        payload_path=args.payload,
        manifest_path=args.manifest,
        verification_checkpoint_path=args.verification_checkpoint,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
