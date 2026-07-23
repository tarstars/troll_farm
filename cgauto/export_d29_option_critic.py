#!/usr/bin/env python3
"""Export the frozen D29 critic with per-output-channel int8 weights."""

from __future__ import annotations

import argparse
from collections import OrderedDict
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from cgauto.d29_spatial_option_critic import decode_array, encode_array


FORMAT = "troll-farm-d29-option-critic-int8-per-output-v1"
PROTOCOL_SHA256 = "59422146871b8beb7de72547dcb12f42cfea14dd22cad23188d9b38bcb42b3db"
LAYERS = ("conv1", "conv2", "scalar", "hidden", "output")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def append_array(payload: bytearray, name: str, value: np.ndarray) -> dict[str, Any]:
    array = np.ascontiguousarray(value, dtype="<f4")
    encoded = array.tobytes(order="C")
    result = {
        "name": name,
        "shape": list(array.shape),
        "dtype": "little-endian-f32",
        "offset": len(payload),
        "bytes": len(encoded),
        "sha256": sha256_bytes(encoded),
    }
    payload.extend(encoded)
    return result


def quantize(
    checkpoint_path: Path,
) -> tuple[bytes, dict[str, Any], dict[str, Any]]:
    checkpoint_bytes = checkpoint_path.read_bytes()
    checkpoint = json.loads(checkpoint_bytes)
    state = {
        name: decode_array(value).astype(np.float32, copy=False)
        for name, value in checkpoint["state"].items()
    }
    expected = {
        f"{layer}.{suffix}" for layer in LAYERS for suffix in ("weight", "bias")
    }
    if set(state) != expected:
        raise ValueError(
            f"D29 checkpoint tensors differ: missing={sorted(expected - set(state))}, "
            f"extra={sorted(set(state) - expected)}"
        )

    payload = bytearray()
    converted: OrderedDict[str, np.ndarray] = OrderedDict()
    layers: list[dict[str, Any]] = []
    for layer_index, layer in enumerate(LAYERS):
        weight_name = f"{layer}.weight"
        bias_name = f"{layer}.bias"
        weight = np.ascontiguousarray(state[weight_name], dtype=np.float32)
        bias = np.ascontiguousarray(state[bias_name], dtype="<f4")
        if weight.ndim not in (2, 4) or bias.shape != (weight.shape[0],):
            raise ValueError(
                f"unsupported D29 tensors for {layer}: {weight.shape}, {bias.shape}"
            )
        flattened = weight.reshape(weight.shape[0], -1)
        scales = (np.max(np.abs(flattened), axis=1) / 127.0).astype(np.float32)
        scales = np.where(scales == 0.0, np.float32(1.0), scales).astype("<f4")
        broadcast = (-1,) + (1,) * (weight.ndim - 1)
        quantized = np.rint(weight / scales.reshape(broadcast))
        quantized = np.clip(quantized, -127, 127).astype(np.int8)
        dequantized = np.ascontiguousarray(
            quantized.astype(np.float32) * scales.reshape(broadcast), dtype=np.float32
        )
        converted[weight_name] = dequantized
        converted[bias_name] = bias.copy()

        weight_bytes = quantized.tobytes(order="C")
        weight_offset = len(payload)
        payload.extend(weight_bytes)
        scale_bytes = scales.tobytes(order="C")
        scale_offset = len(payload)
        payload.extend(scale_bytes)
        bias_bytes = bias.tobytes(order="C")
        bias_offset = len(payload)
        payload.extend(bias_bytes)
        layers.append(
            {
                "index": layer_index,
                "name": layer,
                "weight_name": weight_name,
                "bias_name": bias_name,
                "weight_shape": list(weight.shape),
                "weight_count": int(weight.size),
                "output_channels": int(weight.shape[0]),
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

    runtime_arrays = [
        append_array(payload, "scalar_mean", decode_array(checkpoint["scalar_mean"])),
        append_array(payload, "scalar_std", decode_array(checkpoint["scalar_std"])),
        append_array(
            payload,
            "plane_scales",
            np.asarray(checkpoint["plane_scales"], dtype=np.float32),
        ),
        append_array(
            payload,
            "target_mean_std",
            np.asarray(
                [checkpoint["target_mean"], checkpoint["target_std"]],
                dtype=np.float32,
            ),
        ),
    ]

    payload_bytes = bytes(payload)
    manifest: dict[str, Any] = {
        "format": FORMAT,
        "schema": 1,
        "protocol_sha256": PROTOCOL_SHA256,
        "source_checkpoint": str(checkpoint_path.resolve()),
        "source_checkpoint_sha256": sha256_bytes(checkpoint_bytes),
        "model_seed": int(checkpoint["model_seed"]),
        "epochs": int(checkpoint["epochs"]),
        "quantile": float(checkpoint["quantile"]),
        "spatial_shape": [36, 11, 22],
        "scalar_feature_count": len(checkpoint["feature_names"]),
        "feature_names": checkpoint["feature_names"],
        "weight_count": sum(layer["weight_count"] for layer in layers),
        "bias_count": sum(layer["output_channels"] for layer in layers),
        "quantization": {
            "weights": "signed-int8 symmetric per output channel/row",
            "scale": "f32 max_abs/127; all-zero channel scale 1",
            "rounding": "numpy.rint nearest-even",
            "clip": [-127, 127],
            "bias_and_normalization": "unaltered/effective little-endian f32",
            "runtime": "startup dequantization and f32 accumulation",
        },
        "layers": layers,
        "runtime_arrays": runtime_arrays,
        "maximum_absolute_weight_error": max(
            layer["maximum_absolute_weight_error"] for layer in layers
        ),
        "payload_bytes": len(payload_bytes),
        "payload_sha256": sha256_bytes(payload_bytes),
    }
    verification = {
        "schema": checkpoint["schema"],
        "model_seed": checkpoint["model_seed"],
        "epochs": checkpoint["epochs"],
        "quantile": checkpoint["quantile"],
        "feature_names": checkpoint["feature_names"],
        "plane_scales": checkpoint["plane_scales"],
        "scalar_mean": checkpoint["scalar_mean"],
        "scalar_std": checkpoint["scalar_std"],
        "target_mean": float(np.float32(checkpoint["target_mean"])),
        "target_std": float(np.float32(checkpoint["target_std"])),
        "state": {
            name: encode_array(converted[name]) for name in sorted(converted)
        },
        "deployment_quantization": {
            "format": FORMAT,
            "protocol_sha256": PROTOCOL_SHA256,
            "source_checkpoint_sha256": manifest["source_checkpoint_sha256"],
            "payload_sha256": manifest["payload_sha256"],
        },
    }
    return payload_bytes, manifest, verification


def atomic_write(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(value)
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("--payload", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--verification-checkpoint", type=Path, required=True)
    args = parser.parse_args()

    payload, manifest, verification = quantize(args.checkpoint)
    manifest_bytes = (
        json.dumps(manifest, indent=1, sort_keys=True, separators=(",", ": ")) + "\n"
    ).encode()
    verification_bytes = (
        json.dumps(verification, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode()
    atomic_write(args.payload, payload)
    atomic_write(args.manifest, manifest_bytes)
    atomic_write(args.verification_checkpoint, verification_bytes)
    result = {
        "payload": str(args.payload),
        "payload_bytes": len(payload),
        "payload_sha256": sha256_bytes(payload),
        "manifest": str(args.manifest),
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "verification_checkpoint": str(args.verification_checkpoint),
        "verification_checkpoint_sha256": sha256_bytes(verification_bytes),
        "weight_count": manifest["weight_count"],
        "bias_count": manifest["bias_count"],
        "maximum_absolute_weight_error": manifest["maximum_absolute_weight_error"],
    }
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
