#!/usr/bin/env python3
"""Build the frozen binary D29b Rust numerical-parity corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct

import numpy as np

from cgauto.d29_spatial_option_critic import (
    SPATIAL_SIZE,
    build_dataset,
    configure_torch,
    load_checkpoint,
    predict_model,
    prediction_hash,
    read_labels,
    read_scalars,
    read_spatial,
)


MAGIC = b"D29BPRT1"
THRESHOLD = np.float32(4.0)
EXPECTED_CHECKPOINT_SHA256 = (
    "9d4ef336880ac2ae57e868f05cb99646f94bb2e92a7d1aedd0ad1a22d12b33ba"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def feature_name_hash(names: tuple[str, ...]) -> str:
    return hashlib.sha256("\0".join(names).encode()).hexdigest()


def parse_partition(raw: list[str]) -> dict:
    name, seed_start, seed_count, spatial, scalar, labels = raw
    return {
        "name": name,
        "seed_start": int(seed_start),
        "seed_count": int(seed_count),
        "spatial": Path(spatial),
        "scalar": Path(scalar),
        "labels": Path(labels),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument(
        "--partition",
        nargs=6,
        action="append",
        metavar=("NAME", "SEED_START", "SEED_COUNT", "SPATIAL", "SCALAR", "LABELS"),
        required=True,
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    checkpoint_sha = sha256(args.checkpoint)
    if checkpoint_sha != EXPECTED_CHECKPOINT_SHA256:
        raise SystemExit("D29b parity checkpoint differs from the frozen checkpoint")
    partitions = [parse_partition(raw) for raw in args.partition]
    total_rows = sum(part["seed_count"] * 16 for part in partitions)

    configure_torch()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(args.output.name + ".tmp")
    partition_results = []
    common_names: tuple[str, ...] | None = None
    row_cursor = 0
    with temporary.open("wb") as stream:
        stream.write(
            struct.pack(
                "<8sIIIf", MAGIC, total_rows, SPATIAL_SIZE, 426, float(THRESHOLD)
            )
        )
        for partition in partitions:
            spatial, spatial_checks = read_spatial(partition["spatial"])
            scalars, names = read_scalars(partition["scalar"])
            labels = read_labels([partition["labels"]])
            data, integrity = build_dataset(
                spatial,
                scalars,
                labels,
                names,
                partition["seed_start"],
                partition["seed_count"],
                spatial_checks,
            )
            if not integrity["complete"]:
                raise ValueError(
                    f"D29b parity input integrity failed for {partition['name']}"
                )
            if common_names is None:
                common_names = names
            elif names != common_names:
                raise ValueError("D29b scalar feature order differs across partitions")
            if len(names) != 426:
                raise ValueError(f"D29b scalar feature count differs: {len(names)}")
            model, metadata, _ = load_checkpoint(args.checkpoint, names)
            predictions = predict_model(
                model, metadata, data, np.arange(len(data["keys"]))
            ).astype("<f4", copy=False)
            decisions = predictions > THRESHOLD
            start = row_cursor
            for index in range(len(data["keys"])):
                stream.write(
                    np.ascontiguousarray(data["grids"][index], dtype="<i2").tobytes()
                )
                stream.write(
                    np.ascontiguousarray(data["scalars"][index], dtype="<f4").tobytes()
                )
                stream.write(
                    struct.pack(
                        "<fB", float(predictions[index]), int(decisions[index])
                    )
                )
                row_cursor += 1
            partition_results.append(
                {
                    "name": partition["name"],
                    "seed_start": partition["seed_start"],
                    "seed_count": partition["seed_count"],
                    "row_start": start,
                    "row_stop": row_cursor,
                    "rows": len(data["keys"]),
                    "prediction_decision_hash": prediction_hash(
                        predictions, decisions
                    ),
                    "spatial_sha256": sha256(partition["spatial"]),
                    "scalar_sha256": sha256(partition["scalar"]),
                    "labels_sha256": sha256(partition["labels"]),
                }
            )
    if row_cursor != total_rows:
        raise ValueError(f"D29b parity row count differs: {row_cursor} != {total_rows}")
    temporary.replace(args.output)

    assert common_names is not None
    manifest = {
        "schema": 1,
        "format": "troll-farm-d29b-rust-parity-v1",
        "magic": MAGIC.decode(),
        "threshold": float(THRESHOLD),
        "rows": total_rows,
        "spatial_values_per_row": SPATIAL_SIZE,
        "scalar_values_per_row": len(common_names),
        "row_bytes": 2 * SPATIAL_SIZE + 4 * len(common_names) + 5,
        "header_bytes": struct.calcsize("<8sIIIf"),
        "corpus": str(args.output),
        "corpus_bytes": args.output.stat().st_size,
        "corpus_sha256": sha256(args.output),
        "checkpoint": str(args.checkpoint),
        "checkpoint_sha256": checkpoint_sha,
        "feature_name_sha256": feature_name_hash(common_names),
        "partitions": partition_results,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest_temporary = args.manifest.with_name(args.manifest.name + ".tmp")
    manifest_temporary.write_text(json.dumps(manifest, indent=1) + "\n")
    manifest_temporary.replace(args.manifest)
    print(json.dumps(manifest, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
