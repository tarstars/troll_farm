#!/usr/bin/env python3
"""Replay KEEP trajectories and attach exact observations to MC teacher rows."""

from __future__ import annotations

import argparse
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
import csv
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.rl_resident_residual_env import (  # noqa: E402
    OBS_CHANNELS,
    OBS_HEIGHT,
    OBS_WIDTH,
    ResidentResidualVecEnv,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_index_rows(path: Path) -> list[dict[str, int]]:
    fields = {
        "scenario",
        "sample_slot",
        "candidate_index",
        "candidate_count",
        "x",
        "y",
        "legal_actions",
        "alternative_action",
        "alternative_plane",
    }
    rows = []
    with path.open(newline="") as handle:
        for source in csv.DictReader(handle, delimiter="\t"):
            rows.append({field: int(source[field]) for field in fields})
    return rows


def validate_contiguous(rows: list[dict[str, int]]) -> tuple[int, int, int]:
    scenarios = sorted({row["scenario"] for row in rows})
    if not scenarios or scenarios != list(range(scenarios[0], scenarios[-1] + 1)):
        raise ValueError("observation export requires one contiguous scenario block")
    per_scenario = defaultdict(int)
    for row in rows:
        per_scenario[row["scenario"]] += 1
    counts = set(per_scenario.values())
    if len(counts) != 1:
        raise ValueError("every scenario must have the same number of teacher rows")
    samples = counts.pop()
    if any(
        {row["sample_slot"] for row in rows if row["scenario"] == scenario}
        != set(range(samples))
        for scenario in scenarios
    ):
        raise ValueError("sample slots are incomplete")
    return scenarios[0], scenarios[-1] + 1, samples


def export_observations(
    rows: list[dict[str, int]],
    output: Path,
    *,
    num_envs: int,
    max_turns: int = 300,
    hash_output: bool = True,
) -> dict:
    start, stop, samples = validate_contiguous(rows)
    targets: dict[int, dict[int, int]] = defaultdict(dict)
    candidate_totals: dict[int, int] = {}
    for output_index, row in enumerate(rows):
        scenario = row["scenario"]
        candidate = row["candidate_index"]
        if candidate in targets[scenario]:
            raise ValueError(f"duplicate candidate {scenario}/{candidate}")
        targets[scenario][candidate] = output_index
        prior = candidate_totals.setdefault(scenario, row["candidate_count"])
        if prior != row["candidate_count"]:
            raise ValueError(f"inconsistent candidate total for scenario {scenario}")

    output.parent.mkdir(parents=True, exist_ok=True)
    observations = np.lib.format.open_memmap(
        output,
        mode="w+",
        dtype=np.uint8,
        shape=(len(rows), OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH),
    )
    captured = np.zeros(len(rows), dtype=np.uint8)
    counters: dict[int, int] = defaultdict(int)
    current = np.arange(start, start + num_envs, dtype=np.uint64)
    next_seed = start + num_envs
    completed = 0
    decisions = 0
    started = time.perf_counter()
    with ResidentResidualVecEnv(
        num_envs, start, max_turns=max_turns
    ) as env:
        while completed < stop - start:
            keep = env.keep_actions()
            flat_masks = env.masks.reshape(num_envs, -1)
            for slot in range(num_envs):
                scenario = int(current[slot])
                if not start <= scenario < stop:
                    continue
                alternatives = np.flatnonzero(flat_masks[slot])
                alternatives = alternatives[alternatives != keep[slot]]
                candidate_base = counters[scenario]
                for offset, alternative in enumerate(alternatives):
                    candidate = candidate_base + offset
                    output_index = targets[scenario].get(candidate)
                    if output_index is None:
                        continue
                    row = rows[output_index]
                    alternative = int(alternative)
                    if alternative != row["alternative_action"]:
                        raise RuntimeError(
                            f"action mismatch {scenario}/{candidate}: "
                            f"{alternative} != {row['alternative_action']}"
                        )
                    active_cells = np.flatnonzero(env.obs[slot, 6].reshape(-1))
                    expected_cell = row["y"] * OBS_WIDTH + row["x"]
                    if active_cells.tolist() != [expected_cell]:
                        raise RuntimeError(
                            f"active-cell mismatch {scenario}/{candidate}: "
                            f"{active_cells.tolist()} != {[expected_cell]}"
                        )
                    if alternative % (OBS_HEIGHT * OBS_WIDTH) != expected_cell:
                        raise RuntimeError(f"alternative-cell mismatch {scenario}/{candidate}")
                    if alternative // (OBS_HEIGHT * OBS_WIDTH) != row["alternative_plane"]:
                        raise RuntimeError(f"alternative-plane mismatch {scenario}/{candidate}")
                    if int(flat_masks[slot].sum()) != row["legal_actions"]:
                        raise RuntimeError(f"legal-action mismatch {scenario}/{candidate}")
                    observations[output_index] = env.obs[slot]
                    captured[output_index] = 1
                counters[scenario] += len(alternatives)
            _, _, _, info = env.step(keep)
            decisions += num_envs
            for slot in np.flatnonzero(info.dones):
                scenario = int(current[slot])
                if int(info.scenario_seeds[slot]) != scenario:
                    raise RuntimeError(
                        f"scenario tracker mismatch: {info.scenario_seeds[slot]} != {scenario}"
                    )
                if start <= scenario < stop:
                    if counters[scenario] != candidate_totals[scenario]:
                        raise RuntimeError(
                            f"candidate total mismatch {scenario}: "
                            f"{counters[scenario]} != {candidate_totals[scenario]}"
                        )
                    completed += 1
                current[slot] = next_seed
                next_seed += 1
    if not np.all(captured):
        missing = np.flatnonzero(captured == 0)[:20].tolist()
        raise RuntimeError(f"failed to reconstruct teacher rows {missing}")
    observations.flush()
    del observations
    elapsed = time.perf_counter() - started
    return {
        "schema": 1,
        "scenario_start": start,
        "scenario_stop_exclusive": stop,
        "scenarios": stop - start,
        "samples_per_scenario": samples,
        "rows": len(rows),
        "shape": [len(rows), OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH],
        "dtype": "uint8",
        "captured": int(captured.sum()),
        "decisions": decisions,
        "elapsed_seconds": elapsed,
        "decisions_per_second": decisions / elapsed,
        "output": str(output),
        "output_sha256": sha256(output) if hash_output else None,
    }


def _export_chunk(arguments: tuple) -> dict:
    rows, output, num_envs, max_turns = arguments
    return export_observations(
        rows,
        output,
        num_envs=num_envs,
        max_turns=max_turns,
        hash_output=False,
    )


def export_parallel(
    rows: list[dict[str, int]],
    output: Path,
    *,
    workers: int,
    num_envs: int,
    max_turns: int = 300,
) -> dict:
    start, stop, samples = validate_contiguous(rows)
    workers = max(1, min(workers, stop - start))
    if workers == 1:
        return export_observations(
            rows, output, num_envs=num_envs, max_turns=max_turns
        )
    scenario_chunks = [
        values.tolist()
        for values in np.array_split(np.arange(start, stop), workers)
        if len(values)
    ]
    indexed = defaultdict(list)
    for index, row in enumerate(rows):
        indexed[row["scenario"]].append((index, row))
    chunks = []
    temporary_paths = []
    for worker, scenarios in enumerate(scenario_chunks):
        entries = [entry for scenario in scenarios for entry in indexed[int(scenario)]]
        indexes = [entry[0] for entry in entries]
        chunk_rows = [entry[1] for entry in entries]
        temporary = output.with_name(f".{output.name}.part{worker}.npy")
        temporary_paths.append(temporary)
        chunks.append((indexes, chunk_rows, temporary))
    started = time.perf_counter()
    try:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            reports = list(
                executor.map(
                    _export_chunk,
                    [
                        (chunk_rows, temporary, num_envs, max_turns)
                        for _, chunk_rows, temporary in chunks
                    ],
                )
            )
        output.parent.mkdir(parents=True, exist_ok=True)
        observations = np.lib.format.open_memmap(
            output,
            mode="w+",
            dtype=np.uint8,
            shape=(len(rows), OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH),
        )
        for (indexes, _, temporary), report in zip(chunks, reports, strict=True):
            part = np.load(temporary, mmap_mode="r")
            if len(indexes) and indexes == list(range(indexes[0], indexes[-1] + 1)):
                observations[indexes[0] : indexes[-1] + 1] = part
            else:
                observations[indexes] = part
            if report["captured"] != len(indexes):
                raise RuntimeError(f"incomplete parallel chunk {temporary}")
        observations.flush()
        del observations
    finally:
        for temporary in temporary_paths:
            temporary.unlink(missing_ok=True)
    elapsed = time.perf_counter() - started
    return {
        "schema": 1,
        "scenario_start": start,
        "scenario_stop_exclusive": stop,
        "scenarios": stop - start,
        "samples_per_scenario": samples,
        "rows": len(rows),
        "shape": [len(rows), OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH],
        "dtype": "uint8",
        "captured": sum(report["captured"] for report in reports),
        "decisions": sum(report["decisions"] for report in reports),
        "elapsed_seconds": elapsed,
        "decisions_per_second": sum(report["decisions"] for report in reports) / elapsed,
        "workers": workers,
        "worker_reports": reports,
        "output": str(output),
        "output_sha256": sha256(output),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--num-envs", type=int, default=20)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--max-turns", type=int, default=300)
    args = parser.parse_args()
    rows = read_index_rows(args.labels)
    payload = export_parallel(
        rows,
        args.output,
        workers=args.workers,
        num_envs=args.num_envs,
        max_turns=args.max_turns,
    )
    payload["labels"] = str(args.labels)
    payload["labels_sha256"] = sha256(args.labels)
    payload["exporter"] = str(Path(__file__).relative_to(REPO))
    payload["exporter_sha256"] = sha256(Path(__file__))
    args.metadata.parent.mkdir(parents=True, exist_ok=True)
    args.metadata.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
