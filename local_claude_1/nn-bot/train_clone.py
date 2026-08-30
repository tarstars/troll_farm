#!/usr/bin/env python3
"""The clone's trainer: behaviour cloning of the four teachers, two heads, one masked loss each
(Track N, Phase 2, card `coordination/tasks/20260829-nn-bot-way-b-dataset.md`, day 6-7).

The dataset (`build_dataset.py`) stores **labels and compact states, never planes**: a row's 104
planes are 25 kB and the state they are built from is 58 bytes gzipped.  So the planes are built
here, at load time, by the **same Rust builder the environment uses**
(`tf_full_obs_from_state`, through `nn_runtime.PlaneBuilder`) -- a thin batcher around the C ABI,
never a second implementation.  `build_planes.py` stays what it is: the independent Python builder
that proves, on 1,000 states, that the two agree.

What is trained:

* `SpatialActorCritic(plan_head=True)` from `cgauto/train_level1_ppo.py` -- the July trunk, the
  13-plane per-cell head, the value head, and the per-candidate `PlanCandidateScorer` over the
  `PLAN_ACTION_SIZE`-entry plan vocabulary.  The size is **imported**, never written down here.
* two masked cross-entropies over `forward_with_plan()`: plan rows train the plan head against
  the 400-entry plan mask, command rows train the per-cell head against the 3,146-entry spatial
  mask.  Each row trains exactly one head -- a plan row carries no command and a troll row carries
  no purchase -- and a batch is the mixture the shard's own mini-step order produces.
* held out **by game** (`split` in the shard, deterministic by game id), so a held-out number is
  never a turn of a game the network trained on.  A shard built without a holdout can be split
  here instead, with `--holdout PERCENT`: the same `build_dataset.held_out` function draws the
  line, so trainer-side and builder-side splits agree game for game.
* per-verb accuracy is reported and **never gates anything**: fit statistics anti-predict transfer
  in this project (`docs/CONSTRAINTS.md`); the bench is the judge.
* the checkpoint is the four-key format PPO reads -- `model`, `optimizer`, `config`,
  `global_step` -- and `config` carries `plan_vocab_version`, so a clone trained against one plan
  vocabulary cannot be loaded by a runtime that speaks another.  `--self-test` proves the
  checkpoint loads into `train_ppo_full.load_policy`.

Usage:

    # the minutes-long smoke on the pilot rows (the day-2 slice, rebuilt with its maps)
    python3 local_claude_1/nn-bot/train_clone.py \\
        --shard local_claude_1/nn-bot/results/pilot --name pilot \\
        --epochs 1 --batch 64 --limit 4000 \\
        --out local_claude_1/nn-bot/results/clone-smoke

    # the tests (no shard needed for most of them; no PyTorch needed for the data half)
    python3 local_claude_1/nn-bot/train_clone.py --self-test
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for _path in (HERE, REPO):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

import nn_runtime as nr                                          # noqa: E402
from build_dataset import (KIND_COMMAND, KIND_PLAN, OOV, VERBS,   # noqa: E402
                           PLAN_VOCAB_VERSION, held_out, read_maps, read_shard, unflat)


def load_states(shard_dir: Path, name: str) -> dict:
    """`(game, turn, seat) -> compact state`, the per-turn snapshot the planes are built from."""
    states = {}
    with gzip.open(Path(shard_dir) / f"states-{name}.jsonl.gz", "rt") as fh:
        for line in fh:
            entry = json.loads(line)
            states[(entry["game"], entry["turn"], entry["seat"])] = entry["state"]
    return states


# --------------------------------------------------------------------------- the load-time planes

class PlaneBatcher:
    """The shard's rows, with their planes built on demand by the compiled runtime.

    A row is a context (`nn_runtime.shard_contexts`): the compact state with the earlier trolls of
    its turn staged exactly as the environment stages them, the seat, the phase, the active troll
    and the standing plan.  `build(i)` turns one context into `(obs, mask, label, kind)`.

    The contexts are held as Python dicts -- 10,000 rows are a few MB -- and the 25 kB of planes
    exist only for the rows of the batch being trained.
    """

    def __init__(self, shard_dir, name, library=nr.DEFAULT_LIBRARY, *, split=None, limit=0,
                 seed=0, holdout=0):
        self.shard_dir, self.name = Path(shard_dir), name
        self.library = library
        arrays, self.meta = read_shard(self.shard_dir, name)
        maps = read_maps(self.shard_dir, name)
        states = load_states(self.shard_dir, name)
        if holdout and int(self.meta.get("holdout_percent") or 0):
            raise SystemExit(
                f"--holdout {holdout} on a shard already built with "
                f"--holdout {self.meta['holdout_percent']}: re-split at load time would move "
                "games across the line the shard drew; drop the flag or rebuild the shard")
        self.holdout = holdout
        contexts = []
        for context in nr.shard_contexts(arrays, states, maps):
            # `--holdout` draws the split here, by game, with the builder's own function -- so a
            # dataset built without one can still be judged on games it never trained on.
            row_split = held_out(int(context["game"]), holdout) if holdout else context["split"]
            if split is not None and row_split != split:
                continue
            if context["kind"] == KIND_PLAN and context["label"] == OOV:
                continue                      # censused as unsupported: it has no label to fit
            contexts.append(context)
        if limit and len(contexts) > limit:
            rng = np.random.default_rng(seed)
            keep = np.sort(rng.choice(len(contexts), size=limit, replace=False))
            contexts = [contexts[i] for i in keep]
        self.contexts = contexts
        self._builder = None

    def __len__(self):
        return len(self.contexts)

    @property
    def builder(self):
        """One `PlaneBuilder` per process: a DataLoader worker builds its own after the fork."""
        if self._builder is None:
            self._builder = nr.PlaneBuilder(self.library)
        return self._builder

    def build(self, i):
        context = self.contexts[i]
        plan_phase = context["kind"] == KIND_PLAN
        obs, mask, plan_mask = self.builder.observe(
            context["state"], context["seat"], context["active_troll"], context["phase"],
            context["plan_index"], want_mask=not plan_phase, want_plan_mask=plan_phase)
        planes = np.frombuffer(obs, dtype=np.uint8).reshape(
            nr.OBS_CHANNELS, nr.GRID_H, nr.GRID_W)
        legal = np.frombuffer(plan_mask if plan_phase else mask, dtype=np.uint8)
        return planes, legal, context["label"], context["kind"], context["verb"]

    def counts(self):
        c = Counter(context["kind"] for context in self.contexts)
        return {"plan": c[KIND_PLAN], "command": c[KIND_COMMAND], "rows": len(self.contexts),
                "games": len({context["game"] for context in self.contexts})}


def collate(items):
    """A batch: planes, the two masks padded apart, labels, and the row kind."""
    import torch                                                  # noqa: PLC0415

    planes = np.stack([it[0] for it in items])
    kinds = np.array([it[3] for it in items], dtype=np.int64)
    labels = np.array([it[2] for it in items], dtype=np.int64)
    verbs = np.array([it[4] for it in items], dtype=np.int64)
    plan_mask = np.zeros((len(items), nr.PLAN_ACTION_SIZE), dtype=np.uint8)
    action_mask = np.zeros((len(items), nr.ACTION_SIZE), dtype=np.uint8)
    for row, it in enumerate(items):
        if it[3] == KIND_PLAN:
            plan_mask[row] = it[1]
        else:
            action_mask[row] = it[1]
    return (torch.from_numpy(planes), torch.from_numpy(action_mask),
            torch.from_numpy(plan_mask), torch.from_numpy(labels),
            torch.from_numpy(kinds), torch.from_numpy(verbs))


class _TorchDataset:
    """`torch.utils.data.Dataset` over the batcher, defined lazily so the data half imports
    without PyTorch (the card's disk rule: the VM may not be able to hold torch)."""

    def __init__(self, batcher):
        self.batcher = batcher

    def __len__(self):
        return len(self.batcher)

    def __getitem__(self, i):
        return self.batcher.build(i)


# --------------------------------------------------------------------------- the two losses

def masked_cross_entropy(logits, mask, target):
    """Cross-entropy over the legal entries only, the way the environment samples.

    Illegal entries are pushed to the dtype's minimum before the log-softmax, which is
    `SpatialActorCritic.action_and_value`'s own masking; a row whose target the mask forbids is a
    contradiction and raises rather than training on it.
    """
    import torch                                                  # noqa: PLC0415
    from torch.nn import functional as F                          # noqa: PLC0415

    legal = mask.bool()
    if not torch.all(legal.gather(1, target.unsqueeze(1))):
        bad = (~legal.gather(1, target.unsqueeze(1)).squeeze(1)).nonzero().flatten().tolist()
        raise ValueError(f"rows {bad[:8]} carry a label the mask forbids; the shard and the "
                         f"runtime disagree -- run build_dataset.py --codec-test")
    masked = logits.masked_fill(~legal, torch.finfo(logits.dtype).min)
    return F.cross_entropy(masked, target, reduction="sum")


def epoch_pass(model, loader, optimizer, *, train: bool, device):
    """One pass. Returns the two losses, the two accuracies and the per-verb tally."""
    import torch                                                  # noqa: PLC0415

    totals = Counter()
    per_verb = Counter()
    per_verb_hit = Counter()
    model.train(train)
    for planes, action_mask, plan_mask, labels, kinds, verbs in loader:
        planes = planes.to(device)
        is_plan = kinds == KIND_PLAN
        with torch.set_grad_enabled(train):
            action_logits, plan_logits, _ = model.forward_with_plan(planes)
            loss = planes.new_zeros((), dtype=torch.float32)
            if is_plan.any():
                rows = is_plan.nonzero().flatten()
                plan_loss = masked_cross_entropy(
                    plan_logits[rows], plan_mask[rows].to(device), labels[rows].to(device))
                loss = loss + plan_loss
                totals["plan_loss"] += float(plan_loss.detach())
                totals["plan_rows"] += len(rows)
                choice = plan_logits[rows].masked_fill(
                    ~plan_mask[rows].to(device).bool(),
                    torch.finfo(plan_logits.dtype).min).argmax(1).cpu()
                totals["plan_hit"] += int((choice == labels[rows]).sum())
            if (~is_plan).any():
                rows = (~is_plan).nonzero().flatten()
                command_loss = masked_cross_entropy(
                    action_logits[rows], action_mask[rows].to(device), labels[rows].to(device))
                loss = loss + command_loss
                totals["command_loss"] += float(command_loss.detach())
                totals["command_rows"] += len(rows)
                choice = action_logits[rows].masked_fill(
                    ~action_mask[rows].to(device).bool(),
                    torch.finfo(action_logits.dtype).min).argmax(1).cpu()
                hit = choice == labels[rows]
                totals["command_hit"] += int(hit.sum())
                for verb, ok in zip(verbs[rows].tolist(), hit.tolist()):
                    per_verb[verb] += 1
                    per_verb_hit[verb] += int(ok)
            if train:
                rows_here = max(1, len(labels))
                optimizer.zero_grad(set_to_none=True)
                (loss / rows_here).backward()
                optimizer.step()
    report = {
        "plan_rows": totals["plan_rows"], "command_rows": totals["command_rows"],
        "plan_loss": totals["plan_loss"] / max(1, totals["plan_rows"]),
        "command_loss": totals["command_loss"] / max(1, totals["command_rows"]),
        "plan_accuracy": totals["plan_hit"] / max(1, totals["plan_rows"]),
        "command_accuracy": totals["command_hit"] / max(1, totals["command_rows"]),
        "per_verb": {VERBS[v]: {"rows": per_verb[v],
                                "accuracy": per_verb_hit[v] / max(1, per_verb[v])}
                     for v in sorted(per_verb)},
    }
    return report


# --------------------------------------------------------------------------- the checkpoint

def checkpoint_config(meta, args, counts) -> dict:
    """What the checkpoint remembers about itself.

    `plan_vocab_version` is the one field a loader refuses on (`train_ppo_full.py`
    `check_checkpoint_version`): the same plan index means a different talent set under another
    vocabulary, so a clone must name the one it was trained against.
    """
    return {
        "trainer": "local_claude_1/nn-bot/train_clone.py",
        "task": "20260829-nn-bot-way-b-dataset",
        "plan_vocab_version": PLAN_VOCAB_VERSION,
        "plan_action_size": nr.PLAN_ACTION_SIZE,
        "action_size": nr.ACTION_SIZE,
        "obs_channels": nr.OBS_CHANNELS,
        "shard": str(args.shard), "shard_name": args.name,
        "shard_plan_vocab_version": meta.get("plan_vocab_version"),
        "shard_rows": meta.get("rows"),
        "epochs": args.epochs, "batch": args.batch, "learning_rate": args.lr,
        "seed": args.seed,
        "holdout_percent": args.holdout or meta.get("holdout_percent"),
        "holdout_drawn_by": "trainer" if args.holdout else "builder",
        "train_rows": counts["train"], "held_out_rows": counts["held_out"],
        "library": str(args.library),
    }


def save_checkpoint(path, model, optimizer, config, global_step):
    import torch                                                  # noqa: PLC0415

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model": model.state_dict(), "optimizer": optimizer.state_dict(),
                "config": config, "global_step": int(global_step)}, Path(path))
    return Path(path)


# --------------------------------------------------------------------------- the tests

def self_test(library=nr.DEFAULT_LIBRARY, shard=None, name="pilot"):
    """The trainer's own checks.  The data half runs without PyTorch; the rest is skipped then."""
    failures, skipped = [], []

    class Skip(Exception):
        """What a check raises when it needs something this invocation was not given."""

    def check(label, fn):
        try:
            fn()
            print(f"ok   {label}")
        except Skip as exc:
            skipped.append(f"{label}: {exc}")
            print(f"skip {label}: {exc}")
        except Exception as exc:                                  # noqa: BLE001
            failures.append(f"{label}: {exc}")
            print(f"FAIL {label}: {exc}")

    # 1 -- the vocabulary size is imported, never written down twice.
    def sizes():
        from cgauto.train_level1_ppo import PLAN_ACTION_SIZE as trainer_size  # noqa: PLC0415
        assert trainer_size == nr.PLAN_ACTION_SIZE, (trainer_size, nr.PLAN_ACTION_SIZE)
        import ast                                                # noqa: PLC0415
        tree = ast.parse(Path(__file__).read_text())
        literals = {node.value for node in ast.walk(tree)
                    if isinstance(node, ast.Constant) and isinstance(node.value, int)}
        assert nr.PLAN_ACTION_SIZE not in literals and nr.ACTION_SIZE not in literals, \
            "a vocabulary size is written as a literal in this file; import it instead"
    check("the plan size comes from the network's own module, nothing is hard-coded", sizes)

    # 2 -- the library and this code speak one vocabulary.
    def version():
        builder = nr.PlaneBuilder(library)
        assert builder.plan_version == PLAN_VOCAB_VERSION, builder.plan_version
    check("the compiled runtime's plan vocabulary is this one", version)

    # 3 -- the staged prefix is the turn's earlier trolls, in order, and a plan row has none.
    def staging():
        if shard is None:
            raise Skip("no --shard given; pass --shard/--name to run this one")
        arrays, _ = read_shard(shard, name)
        maps = read_maps(shard, name)
        states = load_states(Path(shard), name)
        seen = 0
        for context in nr.shard_contexts(arrays, states, maps):
            staged = context["state"].get("staged_actions", [])
            if context["kind"] == KIND_PLAN:
                assert not staged, "a plan row must stage nothing"
                assert context["active_troll"] == -1
            else:
                ids = [entry["troll_id"] for entry in staged]
                assert ids == sorted(set(ids)), ids
                assert all(i < context["active_troll"] for i in ids), (ids, context)
            seen += 1
            if seen >= 2000:
                break
        assert seen > 0
    check("the staged prefix is the turn's earlier trolls in ascending id order", staging)

    # 4 -- the trainer's `--holdout` draws the builder's own line: one side per game, right share.
    def holdout_split():
        ids = list(range(3000))
        train = {g for g in ids if not held_out(g, 20)}
        out = {g for g in ids if held_out(g, 20)}
        assert not (train & out), "a game landed on both sides of the holdout"
        assert train | out == set(ids)
        share = len(out) / len(ids)
        assert 0.15 <= share <= 0.25, f"--holdout 20 held out {100 * share:.1f} %"
        assert all(not held_out(g, 0) for g in ids), "--holdout 0 must hold nothing out"
        assert [held_out(g, 20) for g in ids] == [held_out(g, 20) for g in ids], "not stable"
        if shard is not None:
            arrays, _ = read_shard(shard, name)
            games = {int(g) for g in arrays["game"]}
            sides = {g: held_out(g, 20) for g in games}
            assert set(sides.values()) <= {0, 1}
            print(f"     shard games {len(games)}: "
                  f"{sum(sides.values())} held out at --holdout 20")
    check("--holdout splits by game with the builder's own function, one side per game",
          holdout_split)

    try:
        import torch                                              # noqa: F401,PLC0415
    except ImportError:
        print("torch is not installed here: the model half of the self-test is skipped "
              "(the card's disk rule); the coordinator runs it on the host")
        print(f"self-test: {'PASS' if not failures else 'FAIL'} "
              f"({len(failures)} failures, {len(skipped)} skipped)")
        return 0 if not failures else 1

    import torch                                                  # noqa: PLC0415
    from cgauto.train_level1_ppo import SpatialActorCritic        # noqa: PLC0415

    # 5 -- each row kind trains exactly one head.
    def one_head_per_row():
        torch.manual_seed(0)
        model = SpatialActorCritic(plan_head=True)
        planes = torch.zeros(2, nr.OBS_CHANNELS, nr.GRID_H, nr.GRID_W)
        planes[:, 0] = 1                                          # the validity plane
        action_mask = torch.ones(2, nr.ACTION_SIZE, dtype=torch.uint8)
        plan_mask = torch.ones(2, nr.PLAN_ACTION_SIZE, dtype=torch.uint8)
        labels = torch.tensor([7, 11])
        for kind, head in ((KIND_PLAN, "plan"), (KIND_COMMAND, "actor")):
            model.zero_grad(set_to_none=True)
            action_logits, plan_logits, _ = model.forward_with_plan(planes)
            if kind == KIND_PLAN:
                masked_cross_entropy(plan_logits, plan_mask, labels).backward()
            else:
                masked_cross_entropy(action_logits, action_mask, labels).backward()
            touched = {n.split(".")[0] for n, p in model.named_parameters()
                       if p.grad is not None and float(p.grad.abs().sum()) > 0}
            other = "actor" if head == "plan" else "plan"
            assert head in touched, (head, touched)
            assert other not in touched, f"a {head} row moved the {other} head: {touched}"
    check("a plan row trains the plan head and a troll row the per-cell head, not both",
          one_head_per_row)

    # 6 -- a label the mask forbids raises instead of training.
    def refuses_illegal_label():
        logits = torch.zeros(1, 8)
        mask = torch.tensor([[1, 1, 0, 0, 0, 0, 0, 0]], dtype=torch.uint8)
        try:
            masked_cross_entropy(logits, mask, torch.tensor([3]))
        except ValueError:
            return
        raise AssertionError("an illegal label must raise")
    check("a label outside the mask raises rather than being trained on", refuses_illegal_label)

    # 7 -- the four-key checkpoint loads into the PPO trainer, and a foreign vocabulary does not.
    def checkpoint_loads():
        import importlib.util                                     # noqa: PLC0415
        import tempfile                                           # noqa: PLC0415

        spec = importlib.util.spec_from_file_location(
            "train_ppo_full_for_test", HERE / "train_ppo_full.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        model = SpatialActorCritic(plan_head=True)
        optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
        config = {"plan_vocab_version": PLAN_VOCAB_VERSION,
                  "plan_action_size": nr.PLAN_ACTION_SIZE}
        with tempfile.TemporaryDirectory(prefix="clone-ckpt-") as tmp:
            path = save_checkpoint(Path(tmp) / "clone.pt", model, optimizer, config, 7)
            saved = torch.load(path, map_location="cpu", weights_only=False)
            assert set(saved) == {"model", "optimizer", "config", "global_step"}, set(saved)
            restored, _ = module.load_policy(str(path), torch.device("cpu"))
            for name_, tensor in model.state_dict().items():
                assert torch.equal(tensor, restored.state_dict()[name_]), name_
            saved["config"]["plan_vocab_version"] = "v144-2026-08-28"
            torch.save(saved, path)
            try:
                module.load_policy(str(path), torch.device("cpu"))
            except (SystemExit, ValueError, RuntimeError):
                return
            raise AssertionError("a foreign plan vocabulary must be refused")
    check("the four-key checkpoint loads into train_ppo_full.load_policy, a foreign one is "
          "refused", checkpoint_loads)

    print(f"self-test: {'PASS' if not failures else 'FAIL'} "
          f"({len(failures)} failures, {len(skipped)} skipped)")
    return 0 if not failures else 1


# --------------------------------------------------------------------------- the run

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", default=None, help="the shard directory build_dataset.py wrote")
    ap.add_argument("--name", default="pilot", help="the shard's name")
    ap.add_argument("--library", default=str(nr.DEFAULT_LIBRARY))
    ap.add_argument("--epochs", type=int, default=1)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--holdout", type=int, default=0,
                    help="percent of games held out at load time, by game, with the builder's "
                         "own deterministic split; refuses a shard that already carries one")
    ap.add_argument("--limit", type=int, default=0,
                    help="train on at most N rows (the smoke); 0 = every row")
    ap.add_argument("--workers", type=int, default=0,
                    help="DataLoader workers; each builds its own library handle")
    ap.add_argument("--out", default=None, help="the checkpoint and the report land here")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test(args.library, args.shard, args.name)
    if not args.shard:
        raise SystemExit("--shard is required (or --self-test)")

    import torch                                                  # noqa: PLC0415
    from torch.utils.data import DataLoader                       # noqa: PLC0415

    from cgauto.train_level1_ppo import SpatialActorCritic        # noqa: PLC0415

    torch.manual_seed(args.seed)
    device = torch.device("cpu")
    started = time.time()

    train_set = PlaneBatcher(args.shard, args.name, args.library, split=0, limit=args.limit,
                             seed=args.seed, holdout=args.holdout)
    held_set = PlaneBatcher(args.shard, args.name, args.library, split=1,
                            limit=max(1, args.limit // 4) if args.limit else 0, seed=args.seed,
                            holdout=args.holdout)
    counts = {"train": len(train_set), "held_out": len(held_set)}
    print(f"shard {args.shard} ({args.name}): train {train_set.counts()}, "
          f"held out {held_set.counts()}", flush=True)
    if not len(train_set):
        raise SystemExit("no training rows: is --holdout the whole shard?")

    model = SpatialActorCritic(plan_head=True).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    config = checkpoint_config(train_set.meta, args, counts)
    print(json.dumps({"event": "start", **config}, sort_keys=True), flush=True)

    def loader_for(dataset, shuffle):
        return DataLoader(_TorchDataset(dataset), batch_size=args.batch, shuffle=shuffle,
                          num_workers=args.workers, collate_fn=collate,
                          persistent_workers=bool(args.workers))

    reports, global_step = [], 0
    for epoch in range(1, args.epochs + 1):
        t0 = time.perf_counter()
        train_report = epoch_pass(model, loader_for(train_set, True), optimizer,
                                  train=True, device=device)
        train_seconds = time.perf_counter() - t0
        global_step += train_report["plan_rows"] + train_report["command_rows"]
        t0 = time.perf_counter()
        held_report = (epoch_pass(model, loader_for(held_set, False), optimizer,
                                  train=False, device=device)
                       if len(held_set) else {})
        held_seconds = time.perf_counter() - t0
        rows = train_report["plan_rows"] + train_report["command_rows"]
        entry = {"epoch": epoch, "train": train_report, "held_out": held_report,
                 "train_seconds": round(train_seconds, 2),
                 "held_out_seconds": round(held_seconds, 2),
                 "rows_per_second": round(rows / max(1e-9, train_seconds), 1)}
        reports.append(entry)
        print(json.dumps({"event": "epoch", "epoch": epoch,
                          "plan_loss": round(train_report["plan_loss"], 4),
                          "command_loss": round(train_report["command_loss"], 4),
                          "plan_accuracy": round(train_report["plan_accuracy"], 4),
                          "command_accuracy": round(train_report["command_accuracy"], 4),
                          "held_out_command_accuracy":
                              round(held_report.get("command_accuracy", float("nan")), 4),
                          "held_out_plan_accuracy":
                              round(held_report.get("plan_accuracy", float("nan")), 4),
                          "rows_per_second": entry["rows_per_second"]},
                         sort_keys=True), flush=True)

    out_dir = Path(args.out) if args.out else None
    checkpoint_path = None
    if out_dir:
        checkpoint_path = save_checkpoint(out_dir / f"clone-{args.name}.pt", model, optimizer,
                                          config, global_step)
    summary = {
        "what": "behaviour cloning of the four teachers: two masked cross-entropies over "
                "SpatialActorCritic(plan_head=True), planes built at load time by "
                "tf_full_obs_from_state",
        "config": config, "counts": counts, "epochs": reports,
        "global_step": global_step,
        "elapsed_seconds": round(time.time() - started, 1),
        "checkpoint": str(checkpoint_path) if checkpoint_path else None,
        "accuracy_is_not_a_gate": "per-verb and held-out accuracy are reported only; the bench "
                                  "judges the clone (docs/CONSTRAINTS.md)",
    }
    if out_dir:
        (out_dir / f"clone-{args.name}.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n")

    last = reports[-1]
    print("\nper-verb accuracy on the last epoch (reported, never a gate):")
    for verb, cell in sorted(last["train"]["per_verb"].items(),
                             key=lambda kv: -kv[1]["rows"]):
        print(f"  {verb:14s} {cell['rows']:6d} rows  {100*cell['accuracy']:5.1f} %")
    if last["held_out"]:
        print("held out, by verb:")
        for verb, cell in sorted(last["held_out"]["per_verb"].items(),
                                 key=lambda kv: -kv[1]["rows"]):
            print(f"  {verb:14s} {cell['rows']:6d} rows  {100*cell['accuracy']:5.1f} %")
    if checkpoint_path:
        print(f"\ncheckpoint -> {checkpoint_path} (model, optimizer, config, global_step; "
              f"plan vocabulary {PLAN_VOCAB_VERSION})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
