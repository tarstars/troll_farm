#!/usr/bin/env python3
"""D172a Phase 2 (signal floor) + Phase 3 (fits) — dense counterfactual-
credit option policy.

Loads the Phase-1 labeled corpus (exact per-(state,option) counterfactual
values from `rust/src/bin/d172a_dense_counterfactual_corpus.rs`'s `corpus`
subcommand), computes the frozen signal-floor gate, and (if it clears) fits
the two frozen function classes (linear per-option scorer; small MLP with a
16-unit shared trunk and 13 per-option linear heads), two seeds each, Huber
loss, one deterministic thread per fit. Exports plain-text weight files the
Rust `eval` subcommand consumes directly (no serde dependency in the Rust
crate). See
`data/analysis/live-agent-6553250/d172a-dense-counterfactual-option-policy-protocol-2026-07-28.md`
and `...-lock.json`.

Usage:
    python -m cgauto.train_d172a_dense_counterfactual_option_policy phase2
    python -m cgauto.train_d172a_dense_counterfactual_option_policy phase3 --function-class linear --seed 172101
    python -m cgauto.train_d172a_dense_counterfactual_option_policy phase3 --all
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
EXTERNAL = ROOT / "artifacts" / "experiments" / "d172a-dense-counterfactual-option-policy"
PROTOCOL = BASE / "d172a-dense-counterfactual-option-policy-protocol-2026-07-28.md"
LOCK = BASE / "d172a-dense-counterfactual-option-policy-lock.json"
CORPUS_GLOB = str(EXTERNAL / "corpus" / "d172a-corpus.shard-*.tsv")

INPUT_FEATURES = 81
ARMS = 13
HIDDEN = 16

ARM_LABELS = (
    "opt_return",
    "opt_fruit_t072", "opt_fruit_t104", "opt_fruit_t136", "opt_fruit_trig",
    "opt_iron_t072", "opt_iron_t104", "opt_iron_t136", "opt_iron_trig",
    "opt_protect_t072", "opt_protect_t104", "opt_protect_t136", "opt_protect_trig",
)
assert len(ARM_LABELS) == ARMS

FUNCTION_CLASSES = {
    "linear": {"seeds": [172101, 172102]},
    "mlp": {"seeds": [172201, 172202]},
}

# Frozen BEFORE any Phase 3 outcome is seen (git-committed here at authoring
# time); never retuned after a fit's loss/eval numbers are observed. Chosen
# as unremarkable, standard defaults for models this small (<=1,533 params)
# and a corpus this size (~10^4-10^5 rows) -- not searched or tuned.
TRAIN_CONFIG = {
    "epochs": 200,
    "batch_size": 4096,
    "lr": 1.0e-3,
    "adam_eps": 1.0e-8,
    "weight_decay": 0.0,
    "huber_delta": 1.0,
    "val_fraction": 0.1,
}

SIGNAL_FLOOR_RATE = 0.08
SIGNAL_FLOOR_LABEL = 2.0
SIGNAL_FLOOR_MIN_FAMILIES = 6


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_rev() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()


class LinearScorer(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.head = nn.Linear(INPUT_FEATURES, ARMS)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(x)


class MlpScorer(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.trunk = nn.Sequential(nn.Linear(INPUT_FEATURES, HIDDEN), nn.ReLU())
        self.head = nn.Linear(HIDDEN, ARMS)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(self.trunk(x))


def build_model(function_class: str) -> nn.Module:
    if function_class == "linear":
        return LinearScorer()
    if function_class == "mlp":
        return MlpScorer()
    raise ValueError(f"unknown function class {function_class!r}")


def count_params(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())


def load_corpus(shard_glob: str = CORPUS_GLOB) -> dict:
    paths = sorted(glob.glob(shard_glob))
    if not paths:
        raise RuntimeError(f"no corpus shards match {shard_glob}")
    map_seed: list[int] = []
    seat: list[int] = []
    opponent: list[int] = []
    opponent_name: list[str] = []
    turn: list[int] = []
    arm_index: list[int] = []  # 0-based (0..12)
    arm_label: list[str] = []
    label: list[float] = []
    feature_rows: list[np.ndarray] = []
    for path in paths:
        with open(path) as handle:
            header = handle.readline().rstrip("\n").split("\t")
            col = {name: index for index, name in enumerate(header)}
            for line in handle:
                fields = line.rstrip("\n").split("\t")
                map_seed.append(int(fields[col["map_seed"]]))
                seat.append(int(fields[col["seat"]]))
                opponent.append(int(fields[col["opponent_index"]]))
                opponent_name.append(fields[col["opponent"]])
                turn.append(int(fields[col["turn"]]))
                arm_index.append(int(fields[col["arm_index"]]) - 1)
                arm_label.append(fields[col["arm_label"]])
                label.append(float(fields[col["label"]]))
                feature_rows.append(
                    np.fromstring(fields[col["features"]], sep=",", dtype=np.float32)
                )
    X = np.stack(feature_rows).astype(np.float32)
    if X.shape[1] != INPUT_FEATURES:
        raise RuntimeError(f"corpus feature width {X.shape[1]} != {INPUT_FEATURES}")
    return {
        "paths": paths,
        "map_seed": np.array(map_seed, dtype=np.int64),
        "seat": np.array(seat, dtype=np.int64),
        "opponent": np.array(opponent, dtype=np.int64),
        "opponent_name": np.array(opponent_name),
        "turn": np.array(turn, dtype=np.int64),
        "arm_index": np.array(arm_index, dtype=np.int64),
        "arm_label": np.array(arm_label),
        "label": np.array(label, dtype=np.float32),
        "X": X,
    }


def phase2_signal_floor(corpus: dict) -> dict:
    """Frozen floor: >=8% of armable STATES (not rows) have max-option
    label >= +2.0, present in both seats and >=6 families. A "state" groups
    every simultaneously-offered candidate at one (map_seed,seat,opponent,
    turn)."""
    n = len(corpus["label"])
    groups: dict[tuple[int, int, int, int], list[int]] = {}
    for i in range(n):
        key = (
            int(corpus["map_seed"][i]),
            int(corpus["seat"][i]),
            int(corpus["opponent"][i]),
            int(corpus["turn"][i]),
        )
        groups.setdefault(key, []).append(i)
    total_states = len(groups)
    qualifying_keys = []
    for key, idxs in groups.items():
        max_label = max(float(corpus["label"][i]) for i in idxs)
        if max_label >= SIGNAL_FLOOR_LABEL:
            qualifying_keys.append(key)
    rate = len(qualifying_keys) / total_states if total_states else 0.0
    seats_covered = sorted({key[1] for key in qualifying_keys})
    families_covered = sorted(
        {str(corpus["opponent_name"][groups[key][0]]) for key in qualifying_keys}
    )
    rate_gate = rate >= SIGNAL_FLOOR_RATE
    seat_gate = seats_covered == [0, 1]
    family_gate = len(families_covered) >= SIGNAL_FLOOR_MIN_FAMILIES
    return {
        "total_rows": n,
        "total_states": total_states,
        "qualifying_states": len(qualifying_keys),
        "rate": rate,
        "rate_gate_ge_0_08": rate_gate,
        "seats_covered": seats_covered,
        "both_seats_covered": seat_gate,
        "families_covered": families_covered,
        "families_covered_count": len(families_covered),
        "families_gate_ge_6": family_gate,
        "pass": bool(rate_gate and seat_gate and family_gate),
    }


def export_weights(model: nn.Module, function_class: str, path: Path) -> None:
    with torch.no_grad():
        if function_class == "linear":
            w = model.head.weight.detach().cpu().numpy()
            b = model.head.bias.detach().cpu().numpy()
            tokens = ["LINEAR", str(INPUT_FEATURES), str(ARMS)]
            tokens += [f"{v:.9g}" for v in w.reshape(-1)]
            tokens += [f"{v:.9g}" for v in b.reshape(-1)]
        elif function_class == "mlp":
            w1 = model.trunk[0].weight.detach().cpu().numpy()
            b1 = model.trunk[0].bias.detach().cpu().numpy()
            w2 = model.head.weight.detach().cpu().numpy()
            b2 = model.head.bias.detach().cpu().numpy()
            tokens = ["MLP", str(INPUT_FEATURES), str(HIDDEN), str(ARMS)]
            tokens += [f"{v:.9g}" for v in w1.reshape(-1)]
            tokens += [f"{v:.9g}" for v in b1.reshape(-1)]
            tokens += [f"{v:.9g}" for v in w2.reshape(-1)]
            tokens += [f"{v:.9g}" for v in b2.reshape(-1)]
        else:
            raise ValueError(function_class)
    path.write_text(" ".join(tokens) + "\n")


def train_fit(function_class: str, seed: int, corpus: dict, *, threads: int = 1) -> dict:
    torch.set_num_threads(threads)
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)

    X = torch.from_numpy(corpus["X"])
    arm_index = torch.from_numpy(corpus["arm_index"])
    label = torch.from_numpy(corpus["label"])
    n = X.shape[0]

    perm = rng.permutation(n)
    n_val = int(n * TRAIN_CONFIG["val_fraction"])
    val_idx = torch.from_numpy(perm[:n_val])
    train_idx = perm[n_val:]

    model = build_model(function_class)
    params = count_params(model)
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=TRAIN_CONFIG["lr"],
        eps=TRAIN_CONFIG["adam_eps"],
        weight_decay=TRAIN_CONFIG["weight_decay"],
    )
    huber = nn.HuberLoss(delta=TRAIN_CONFIG["huber_delta"])

    batch_size = TRAIN_CONFIG["batch_size"]
    history = []
    started = time.perf_counter()
    for epoch in range(TRAIN_CONFIG["epochs"]):
        epoch_perm = rng.permutation(len(train_idx))
        epoch_idx = train_idx[epoch_perm]
        total_loss = 0.0
        total_count = 0
        for start in range(0, len(epoch_idx), batch_size):
            batch = torch.from_numpy(epoch_idx[start:start + batch_size])
            xb = X[batch]
            ab = arm_index[batch]
            yb = label[batch]
            preds_all = model(xb)
            preds = preds_all.gather(1, ab.unsqueeze(1)).squeeze(1)
            loss = huber(preds, yb)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += float(loss.item()) * len(batch)
            total_count += len(batch)
        train_loss = total_loss / max(total_count, 1)
        with torch.no_grad():
            val_preds_all = model(X[val_idx])
            val_preds = val_preds_all.gather(1, arm_index[val_idx].unsqueeze(1)).squeeze(1)
            val_loss = float(huber(val_preds, label[val_idx]).item())
        history.append({"epoch": epoch, "train_loss": train_loss, "val_loss": val_loss})
    elapsed = time.perf_counter() - started

    return {
        "model": model,
        "params": params,
        "history": history,
        "elapsed_s": elapsed,
        "n_train": int(len(train_idx)),
        "n_val": int(n_val),
        "final_train_loss": history[-1]["train_loss"],
        "final_val_loss": history[-1]["val_loss"],
    }


def output_paths(function_class: str, seed: int) -> dict:
    tag = f"{function_class}-seed{seed}"
    EXTERNAL.mkdir(parents=True, exist_ok=True)
    return {
        "result": BASE / f"d172a-dense-counterfactual-option-policy-{tag}-result.json",
        "weights": EXTERNAL / f"d172a-{tag}-weights.txt",
        "checkpoint_pt": EXTERNAL / f"d172a-{tag}-checkpoint.pt",
    }


def run_phase2(output: Path) -> dict:
    corpus = load_corpus()
    gate = phase2_signal_floor(corpus)
    result = {
        "schema": "troll-farm-d172a-phase2-signal-floor-v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_rev": git_rev(),
        "corpus_shards": len(corpus["paths"]),
        "gate": gate,
        "decision": "signal_floor_pass" if gate["pass"] else "CLOSED-AT-SIGNAL",
        "inputs": {"lock": sha256(LOCK), "protocol": sha256(PROTOCOL)},
    }
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(gate, indent=2, sort_keys=True))
    return result


def run_phase3_fit(function_class: str, seed: int, threads: int) -> dict:
    corpus = load_corpus()
    paths = output_paths(function_class, seed)
    outcome = train_fit(function_class, seed, corpus, threads=threads)
    model = outcome.pop("model")
    export_weights(model, function_class, paths["weights"])
    torch.save({"model": model.state_dict(), "function_class": function_class, "seed": seed}, paths["checkpoint_pt"])
    result = {
        "schema": "troll-farm-d172a-phase3-fit-v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_rev": git_rev(),
        "function_class": function_class,
        "seed": seed,
        "threads": threads,
        "train_config": TRAIN_CONFIG,
        "params": outcome["params"],
        "param_cap": 12288,
        "within_param_cap": outcome["params"] <= 12288,
        "n_train": outcome["n_train"],
        "n_val": outcome["n_val"],
        "final_train_loss": outcome["final_train_loss"],
        "final_val_loss": outcome["final_val_loss"],
        "elapsed_s": outcome["elapsed_s"],
        "history_tail": outcome["history"][-5:],
        "weights_path": str(paths["weights"]),
        "weights_sha256": sha256(paths["weights"]),
        "checkpoint_pt_sha256": sha256(paths["checkpoint_pt"]),
        "inputs": {"lock": sha256(LOCK), "protocol": sha256(PROTOCOL)},
    }
    paths["result"].write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "history_tail"}, indent=2, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p2 = sub.add_parser("phase2")
    p2.add_argument("--output", type=Path, default=BASE / "d172a-dense-counterfactual-option-policy-phase2-result.json")

    p3 = sub.add_parser("phase3")
    p3.add_argument("--function-class", choices=list(FUNCTION_CLASSES))
    p3.add_argument("--seed", type=int)
    p3.add_argument("--threads", type=int, default=1)
    p3.add_argument("--all", action="store_true")

    args = parser.parse_args()
    if args.command == "phase2":
        result = run_phase2(args.output)
        return 0 if result["gate"]["pass"] else 1
    if args.command == "phase3":
        if args.all:
            for function_class, spec in FUNCTION_CLASSES.items():
                for seed in spec["seeds"]:
                    run_phase3_fit(function_class, seed, args.threads)
            return 0
        if not args.function_class or args.seed is None:
            parser.error("phase3 requires --function-class and --seed, or --all")
        run_phase3_fit(args.function_class, args.seed, args.threads)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
