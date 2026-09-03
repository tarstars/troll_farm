#!/usr/bin/env python3
"""Send the self-play PPO trainer to the YTsaurus cluster as a plain CPU job.

Plain words for the owner
-------------------------
Today the self-play trainer runs on this one machine with fourteen cores. The cluster
(YTsaurus, the company's compute cluster; "Cypress" below is its file tree, whose paths start
with `//`) can give one job sixty-four cores instead. This program packs everything the trainer
needs into one archive, puts that archive into Cypress, and starts a *vanilla operation* -- YT's
name for "just run this command in a container", as opposed to a MapReduce. Nothing about the
learning changes: the very same `train_ppo_full.py` runs with the very same arguments, only with
more cores and against a slice of the map corpus that was uploaded with it.

It is modelled on July's `cgauto/yt_troll_farm_ppo.py`, which sent the older D11 trainer to a
*GPU* worker, and differs from it in four ways:

1. **No GPU.** The network is tiny (about 35,000 weights) and the cost of a step is the Rust game
   engine, not the matrix multiply, so a graphics card would sit idle. There is no `gpu_limit` in
   the specification and no CUDA check in the job; `--cpu-limit` (default 64) is the knob that
   matters, and the pool tree and the pool have **no default at all** -- the coordinator must
   name a CPU pool, because July's GPU pool would be the wrong place to land.
2. **A different payload.** Only the files this trainer actually imports, plus the compiled Rust
   game library `libtroll_farm.so`, plus a slice of the map corpus, plus the clone checkpoint the
   run starts from and is anchored to.
3. **The threads follow the cores.** `RAYON_NUM_THREADS` (the Rust engine's worker count) and the
   trainer's own `--threads` are both set to the job's core count.
4. **A dry run.** `prepare --dry-run` builds the archive on this machine, prints every file with
   its size and its sha256 (a content fingerprint), and prints the exact specification that would
   be submitted -- without touching the network.

What is kept from July unchanged: the secure-vault token (the job needs a token to write its
results back into Cypress, and YT hands it to the job through a "secure vault" so it never
appears in the operation's public specification), the two porto layers (the container's Ubuntu
jammy root filesystem plus a Python 3.11 delta), the prebuilt runtime wheelhouse in Cypress (an
8.5 GB archive of wheels holding torch 2.4.1 -- it is a CUDA build, but a CUDA build of torch
runs perfectly well on a machine with no GPU, so nothing needs uploading), the Cypress layout
`<root>/runs/<run-name>/{inputs,outputs,logs}`, and the monitor/retrieve pair.

The four commands
-----------------
    # 1. build the archive here and look at it (no network)
    python3 local_claude_1/nn-bot/yt_ppo_launcher.py prepare --run-name ppo-a --dry-run

    # 2. upload it and start the operation (the coordinator supplies the pool)
    python3 local_claude_1/nn-bot/yt_ppo_launcher.py start --run-name ppo-a \
        --pool-tree <cpu tree> --pool <cpu pool> --async

    # 3. watch it
    python3 local_claude_1/nn-bot/yt_ppo_launcher.py monitor --run-name ppo-a

    # 4. bring the checkpoints home
    python3 local_claude_1/nn-bot/yt_ppo_launcher.py retrieve --run-name ppo-a --output-dir <dir>

Run it with the system `python3`: that is the interpreter that has `yt.wrapper` installed. It
needs neither torch nor numpy -- the checkpoint is copied as a file, not loaded.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
NN_BOT = ROOT / "local_claude_1" / "nn-bot"

sys.path.insert(0, str(NN_BOT))
from cut_maps import cut_maps, default_maps_source  # noqa: E402

# --------------------------------------------------------------------------- July's constants

DEFAULT_YT_PROXY = "watt.yt.yandex.net"
DEFAULT_YT_ROOT = "//home/delivery_ml/research/tarstars/troll_farm"
DEFAULT_RUNTIME = (
    "//home/delivery_ml/research/tarstars/mle/math_through_eml/runtime/"
    "wheelhouse_torch241_cu121_py310.tar.gz"
)
DEFAULT_LAYERS = (
    "//porto_layers/base/jammy/porto_layer_search_ubuntu_jammy_app_lastest.tar.gz",
    "//porto_layers/delta/python/jammy/"
    "porto_delta_layer_ubuntu_jammy_python311_2024-01-24.tar.gz",
)
MATH_PROJECT_SRC = Path("/home/tarstars/prj/math_through_eml/src")

# --------------------------------------------------------------------------- this run's constants

DEFAULT_CLONE = Path("/home/tarstars/nn-data/clone-2026-08-30-a/clone-pilot.pt")
#: `docs/storage-policy.md` names `yt_work` the staging root for YT payloads and downloads, and
#: `.gitignore` already keeps it out of the repository. A prepared payload is twelve to sixty
#: megabytes of maps; it must not land in the tracked tree.
DEFAULT_PAYLOAD_PARENT = ROOT / "yt_work" / "ppo"
DEFAULT_RUN_NAME = "ppo-a"
ENTRYPOINT_SOURCE = NN_BOT / "yt_ppo_entrypoint.py"

#: The seven-opponent mixture of the command that runs on this machine today.
DEFAULT_OPPONENT_WEIGHTS = json.dumps(
    {
        "secure_orchard": 2,
        "norxondor_native": 2,
        "legend_field_proxy_v2": 1,
        "gold_elite_adaptive": 1,
        "script_boss": 0.5,
        "mybot_boss4": 0.5,
        "python_frozen": 3,
    },
    separators=(",", ":"),
)

#: Where things sit *inside* the archive. Three of these are load-bearing:
#:
#: * `train_ppo_full.py` computes its repository root as its own directory's grandparent and puts
#:   it on the import path, so it must keep the `local_claude_1/nn-bot/` prefix;
#: * `cgauto/rl_full_env.py` computes the root as its own parent and looks for the game library at
#:   `<root>/rust/target/release/libtroll_farm.so`. It takes a `library=` argument, but
#:   `train_ppo_full.py` has no `--library` flag to pass one, so the only route is to put the file
#:   exactly where the default expects it. That is what this layout does.
#: * the two of them therefore share one root, which is the archive's root.
PAYLOAD_LIBRARY = Path("rust/target/release/libtroll_farm.so")
PAYLOAD_MAPS = Path("data/maps.jsonl")
PAYLOAD_CLONE = Path("checkpoints/clone.pt")
PAYLOAD_TRAINER = Path("local_claude_1/nn-bot/train_ppo_full.py")

#: Every Python file the trainer reaches, found by following the imports rather than by copying
#: the directory. `train_ppo_full` imports `cgauto.train_level1_ppo` (the network and the shared
#: helpers), which imports the five level environments; `cgauto.rl_full_env` is imported inside
#: `make_env`. `fake_full_env.py` is loaded by path only when `--env fake` is asked for; it is
#: 27 kB and it makes a no-Rust smoke run possible inside the job, so it travels too.
#: `nn_runtime.py` and `bench.py` are NOT here: nothing on the training path imports them
#: (`bench.py` is only shelled out to by the `--gate-every` gate, and this run sets it to 0).
PAYLOAD_MODULES = (
    Path("cgauto/rl_level1_env.py"),
    Path("cgauto/rl_level2_env.py"),
    Path("cgauto/rl_level3_env.py"),
    Path("cgauto/rl_level4_env.py"),
    Path("cgauto/rl_level5_env.py"),
    Path("cgauto/rl_full_env.py"),
    Path("cgauto/train_level1_ppo.py"),
    PAYLOAD_TRAINER,
    Path("local_claude_1/nn-bot/fake_full_env.py"),
)

#: The trainer writes its checkpoints and its summary here; the entrypoint rewrites this to an
#: absolute path inside the job's working directory and tars the directory back at the end.
OUTPUT_DIR_ARG = "outputs"

#: Throughput placeholder for `--hours`. Nobody has measured this trainer on 64 cluster cores yet;
#: this is the local machine's order of magnitude, stated per sixteen cores so it scales with
#: `--cpu-limit`. It is deliberately an *under*-estimate after the safety factor below, because a
#: budget that is too large means the job is killed by its time limit before it can pack its
#: results, while a budget that is too small merely finishes early with everything saved.
DEFAULT_RATE_PER_16_CORES = 2500.0
HOURS_SAFETY_FACTOR = 0.8

#: What the run on this machine actually reads, today, 2026-08-30: 578 decisions a second with
#: `--threads 14` and 128 environments (`/home/tarstars/nn-data/ppo-2026-08-30-a/train.log`,
#: 1,228 updates), which is 661 per sixteen cores. The placeholder above is therefore about four
#: times optimistic, and `--hours` says so out loud rather than quietly promising a budget the job
#: cannot reach. Nobody has measured the cluster's cores, and they need not behave like these, so
#: the honest move for the first job is `--hours` with `--rate-per-16-cores 660`, or simply a
#: `--total-turn-steps` the coordinator has chosen.
MEASURED_RATE_PER_16_CORES = 661.0
MEASUREMENT_NOTE = (
    "the rate is a placeholder, not a measurement: the run on the home machine reads about "
    f"{MEASURED_RATE_PER_16_CORES:.0f} decisions a second per sixteen cores (578/s at "
    "--threads 14, 2026-08-30), so a budget built on 2500 will take roughly four times the "
    "hours asked for; pass --rate-per-16-cores or --total-turn-steps once the cluster's own "
    "throughput is known"
)
#: Extra wall-clock the job gets on top of `--hours`: unpacking the 8.5 GB wheelhouse, installing
#: it, and tarring the results back all happen outside the training loop.
WRAP_HOURS = 1.0
DEFAULT_TOTAL_TURN_STEPS = 200_000_000
DEFAULT_JOB_TIME_LIMIT_HOURS = 12.0

DEFAULT_CPU_LIMIT = 64
DEFAULT_MEMORY_LIMIT = 64 * 1024**3
DEFAULT_HEARTBEAT_MINUTES = 5

REQUIRED_UPLOADS = (
    "troll_farm_payload.tar.gz",
    "yt_run_config.json",
    "yt_ppo_entrypoint.py",
)


# --------------------------------------------------------------------------- small helpers


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


_SIZE_UNITS = {
    "": 1,
    "B": 1,
    "K": 1024,
    "KB": 1024,
    "KIB": 1024,
    "M": 1024**2,
    "MB": 1024**2,
    "MIB": 1024**2,
    "G": 1024**3,
    "GB": 1024**3,
    "GIB": 1024**3,
    "T": 1024**4,
    "TB": 1024**4,
    "TIB": 1024**4,
}


def parse_size(text: str | int) -> int:
    """`"64GiB"`, `"64G"` or a plain byte count, all into bytes."""

    if isinstance(text, int):
        return text
    match = re.fullmatch(r"\s*([0-9]+(?:\.[0-9]+)?)\s*([A-Za-z]*)\s*", str(text))
    if not match:
        raise argparse.ArgumentTypeError(f"cannot read a size out of {text!r}")
    unit = match.group(2).upper()
    if unit not in _SIZE_UNITS:
        raise argparse.ArgumentTypeError(f"unknown size unit {match.group(2)!r}")
    return int(float(match.group(1)) * _SIZE_UNITS[unit])


def non_negative_int(text: str) -> int:
    """An `int` that refuses negative values.

    `--gpu-limit` is a count of GPUs to reserve; a negative count is not a smaller reservation,
    it is nonsense that would otherwise slip past `> 0` checks silently (see `build_spec`, where
    a negative value used to skip the `gpu_limit()` call but still print a "GPU slot" title).
    """

    value = int(text)
    if value < 0:
        raise argparse.ArgumentTypeError(f"must not be negative, got {value}")
    return value


def human_bytes(count: int) -> str:
    value = float(count)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if value < 1024 or unit == "GiB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{value:.1f} GiB"


def run_paths(root: str, run_name: str) -> dict[str, str]:
    """July's Cypress layout, unchanged: `<root>/runs/<run>/{inputs,outputs,logs}`."""

    run_dir = f"{root.rstrip('/')}/runs/{run_name}"
    return {
        "run": run_dir,
        "inputs": f"{run_dir}/inputs",
        "outputs": f"{run_dir}/outputs",
        "logs": f"{run_dir}/logs",
        "output": f"{run_dir}/outputs/troll_farm_output.tar.gz",
        "log": f"{run_dir}/logs/yt_job.log",
    }


# --------------------------------------------------------------------------- the trainer command


def total_turn_steps_for_hours(
    hours: float,
    cpu_limit: int,
    *,
    batch_size: int,
    rate_per_16_cores: float = DEFAULT_RATE_PER_16_CORES,
    safety_factor: float = HOURS_SAFETY_FACTOR,
) -> int:
    """Turn `--hours` into a `--total-turn-steps` budget, deliberately on the low side.

    A "turn step" is one decision the network makes (pick the training plan, or command one
    troll). The placeholder rate is `rate_per_16_cores` decisions a second on sixteen cores,
    scaled linearly with the core count, then multiplied by `safety_factor`. The result is
    rounded *down* to a whole number of rollout batches, because the trainer stops on a batch
    boundary anyway.
    """

    if hours <= 0:
        raise ValueError("--hours must be positive")
    per_second = rate_per_16_cores * (float(cpu_limit) / 16.0) * safety_factor
    steps = int(hours * 3600.0 * per_second)
    batches = max(1, steps // batch_size)
    return batches * batch_size


def trainer_args(
    *,
    run_name: str,
    maps: str,
    clone: str,
    opponent_weights: str,
    num_envs: int,
    rollout_steps: int,
    total_turn_steps: int,
    minibatch_size: int,
    update_epochs: int,
    threads: int,
    checkpoint_every: int,
    gate_every: int,
    episode_window: int,
    anchor_coef: float,
    anchor_coef_final: float,
    anchor_decay_steps: int,
    frozen_refresh_updates: int,
    gamma: float,
    wood_shaping: float,
    end_wood: float,
    critic_warmup_updates: int,
    actor_lr_scale: float,
    train_scope: str,
    entropy_coef: float,
    output_dir: str,
    seed: int,
    device: str = "cpu",
) -> list[str]:
    """The command that runs on this machine today, with the paths moved inside the archive.

    Every flag here appears in the local command in the task; nothing has been added to or removed
    from the recipe. The three checkpoint flags all name the same clone file: the run starts from
    it (`--initial-checkpoint`), is pulled back towards it (`--anchor-checkpoint`), and plays its
    first self-play games against it (`--frozen-checkpoint`). `gamma`, `wood_shaping`, `end_wood`,
    `critic_warmup_updates` and `actor_lr_scale` are named explicitly, rather than left to the
    trainer's own defaults, so a cluster job can be told to run with different ones.
    """

    return [
        "--env",
        "full",
        "--maps",
        maps,
        "--initial-checkpoint",
        clone,
        "--anchor-checkpoint",
        clone,
        "--anchor-coef",
        str(anchor_coef),
        "--anchor-coef-final",
        str(anchor_coef_final),
        "--anchor-decay-steps",
        str(anchor_decay_steps),
        "--frozen-checkpoint",
        clone,
        "--frozen-refresh-updates",
        str(frozen_refresh_updates),
        "--gamma",
        str(gamma),
        "--wood-shaping",
        str(wood_shaping),
        "--end-wood",
        str(end_wood),
        "--critic-warmup-updates",
        str(critic_warmup_updates),
        "--actor-lr-scale",
        str(actor_lr_scale),
        "--train-scope",
        train_scope,
        "--entropy-coef",
        str(entropy_coef),
        "--opponent-weights",
        opponent_weights,
        "--num-envs",
        str(num_envs),
        "--rollout-steps",
        str(rollout_steps),
        "--total-turn-steps",
        str(total_turn_steps),
        "--minibatch-size",
        str(minibatch_size),
        "--update-epochs",
        str(update_epochs),
        "--threads",
        str(threads),
        "--device",
        device,
        "--checkpoint-every",
        str(checkpoint_every),
        "--gate-every",
        str(gate_every),
        "--episode-window",
        str(episode_window),
        "--run-name",
        run_name,
        "--output-dir",
        output_dir,
        "--seed",
        str(seed),
    ]


# --------------------------------------------------------------------------- the payload


def _tar_filter(info: tarfile.TarInfo) -> tarfile.TarInfo:
    """July's filter: no owner, no timestamps, so the same inputs give the same archive."""

    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    info.mtime = 0
    return info


def resolve_maps(args, payload_dir: Path) -> tuple[Path, dict]:
    """The map file that travels: an explicit `--maps`, or a fresh slice of the full corpus."""

    if args.maps:
        source = Path(args.maps)
        if not source.is_file():
            raise FileNotFoundError(source)
        return source, {
            "mode": "explicit",
            "source": str(source),
            "bytes": source.stat().st_size,
        }
    source = Path(args.maps_source) if args.maps_source else default_maps_source()
    every = 1 if args.full_maps else int(args.maps_every)
    sliced = payload_dir / "maps.jsonl"
    report = cut_maps(source, sliced, every=every)
    report["mode"] = "full" if every == 1 else "slice"
    return sliced, report


def prepare_payload(args) -> dict[str, Any]:
    """Build the archive, the job configuration and the manifest in `--payload-dir`.

    Three files come out, exactly as in July: `troll_farm_payload.tar.gz` (everything the job
    unpacks), `yt_run_config.json` (the trainer's arguments), `yt_ppo_entrypoint.py` (the program
    the job actually starts). A fourth, `payload_manifest.json`, stays on this machine and in
    Cypress beside the run as a record of what was sent.
    """

    payload_dir = Path(args.payload_dir)
    if payload_dir.exists():
        if not args.force:
            raise FileExistsError(
                f"payload directory already exists: {payload_dir} (pass --force to rebuild)"
            )
        shutil.rmtree(payload_dir)
    payload_dir.mkdir(parents=True)

    clone = Path(args.clone)
    if not clone.is_file():
        raise FileNotFoundError(clone)
    library = Path(args.library)
    if not library.is_file():
        raise FileNotFoundError(
            f"missing {library}; run "
            "cargo build --manifest-path rust/Cargo.toml --release --lib"
        )
    maps_path, maps_report = resolve_maps(args, payload_dir)

    files: list[tuple[Path, Path]] = [(ROOT / relative, relative) for relative in PAYLOAD_MODULES]
    files.append((library, PAYLOAD_LIBRARY))
    files.append((maps_path, PAYLOAD_MAPS))
    files.append((clone, PAYLOAD_CLONE))

    content_rows = []
    for source, relative in files:
        if not source.is_file():
            raise FileNotFoundError(source)
        content_rows.append(
            {
                "path": str(relative),
                "bytes": source.stat().st_size,
                "sha256": sha256(source),
            }
        )

    batch_size = args.num_envs * args.rollout_steps
    if batch_size % args.minibatch_size:
        raise SystemExit(
            f"the rollout batch {batch_size} must divide by the minibatch size "
            f"{args.minibatch_size} -- the trainer refuses otherwise"
        )
    if args.total_turn_steps is not None:
        total_turn_steps = int(args.total_turn_steps)
        budget = {"source": "--total-turn-steps"}
    elif args.hours is not None:
        total_turn_steps = total_turn_steps_for_hours(
            args.hours,
            args.cpu_limit,
            batch_size=batch_size,
            rate_per_16_cores=args.rate_per_16_cores,
        )
        budget = {
            "source": "--hours",
            "hours": args.hours,
            "rate_per_16_cores": args.rate_per_16_cores,
            "safety_factor": HOURS_SAFETY_FACTOR,
            "assumed_decisions_per_second": args.rate_per_16_cores
            * (args.cpu_limit / 16.0)
            * HOURS_SAFETY_FACTOR,
            "measured_rate_per_16_cores_at_home": MEASURED_RATE_PER_16_CORES,
            "hours_at_the_measured_rate": round(
                total_turn_steps_for_hours(
                    args.hours,
                    args.cpu_limit,
                    batch_size=batch_size,
                    rate_per_16_cores=args.rate_per_16_cores,
                )
                / (MEASURED_RATE_PER_16_CORES * (args.cpu_limit / 16.0) * 3600.0),
                2,
            ),
        }
        if args.rate_per_16_cores > MEASURED_RATE_PER_16_CORES:
            budget["caution"] = MEASUREMENT_NOTE
    else:
        total_turn_steps = DEFAULT_TOTAL_TURN_STEPS
        budget = {"source": "default"}
    budget["total_turn_steps"] = total_turn_steps
    budget["batch_size"] = batch_size
    budget["updates"] = max(1, total_turn_steps // batch_size)

    arguments = trainer_args(
        run_name=args.run_name,
        maps=str(PAYLOAD_MAPS),
        clone=str(PAYLOAD_CLONE),
        opponent_weights=args.opponent_weights,
        num_envs=args.num_envs,
        rollout_steps=args.rollout_steps,
        total_turn_steps=total_turn_steps,
        minibatch_size=args.minibatch_size,
        update_epochs=args.update_epochs,
        threads=args.cpu_limit,
        checkpoint_every=args.checkpoint_every,
        gate_every=args.gate_every,
        episode_window=args.episode_window,
        anchor_coef=args.anchor_coef,
        anchor_coef_final=args.anchor_coef_final,
        anchor_decay_steps=args.anchor_decay_steps,
        frozen_refresh_updates=args.frozen_refresh_updates,
        gamma=args.gamma,
        wood_shaping=args.wood_shaping,
        end_wood=args.end_wood,
        critic_warmup_updates=args.critic_warmup_updates,
        actor_lr_scale=args.actor_lr_scale,
        train_scope=args.train_scope,
        entropy_coef=args.entropy_coef,
        output_dir=OUTPUT_DIR_ARG,
        seed=args.seed,
        device=args.device,
    )

    content_manifest = {
        "purpose": "self-play PPO over the full game, CPU-only vanilla operation",
        "created_utc": utc_now(),
        "run_name": args.run_name,
        "maps": maps_report,
        "clone": {"source": str(clone), "sha256": sha256(clone)},
        "library": {"source": str(library), "sha256": sha256(library)},
        "files": content_rows,
    }
    content_manifest_path = payload_dir / "payload_content_manifest.json"
    content_manifest_path.write_text(
        json.dumps(content_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    files.append((content_manifest_path, Path("payload_content_manifest.json")))

    archive_path = payload_dir / "troll_farm_payload.tar.gz"
    with tarfile.open(archive_path, "w:gz") as archive:
        for source, relative in files:
            archive.add(source, arcname=str(relative), filter=_tar_filter)

    config = {
        "purpose": "self_play_ppo_full_cpu",
        "created_utc": utc_now(),
        "run_name": args.run_name,
        # The entrypoint runs this file, not a module: `local_claude_1/nn-bot` has a hyphen in it
        # and is therefore not an importable package name.
        "trainer_script": str(PAYLOAD_TRAINER),
        "trainer_args": arguments,
        # The two values the job is allowed to rewrite, and nothing else.
        "output_dir_arg": OUTPUT_DIR_ARG,
        "threads_follow_cpu_limit": True,
        "cpu_limit_at_prepare": args.cpu_limit,
        "hours": args.hours,
        "budget": budget,
        "maps_in_payload": str(PAYLOAD_MAPS),
        "clone_in_payload": str(PAYLOAD_CLONE),
        "library_in_payload": str(PAYLOAD_LIBRARY),
        "heartbeat_minutes": args.heartbeat_minutes,
    }
    config_path = payload_dir / "yt_run_config.json"
    config_path.write_text(
        json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    if not ENTRYPOINT_SOURCE.is_file():
        raise FileNotFoundError(ENTRYPOINT_SOURCE)
    entrypoint_path = payload_dir / "yt_ppo_entrypoint.py"
    shutil.copy2(ENTRYPOINT_SOURCE, entrypoint_path)

    manifest = {
        "purpose": config["purpose"],
        "created_utc": utc_now(),
        "run_name": args.run_name,
        "payload_dir": str(payload_dir),
        "payload_uncompressed_bytes": sum(row["bytes"] for row in content_rows),
        "budget": budget,
        "maps": maps_report,
        "files": {
            path.name: {"bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in (archive_path, config_path, entrypoint_path)
        },
        "content": content_rows,
    }
    manifest_path = payload_dir / "payload_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


# --------------------------------------------------------------------------- the specification


def job_environment(args, paths: dict[str, str]) -> dict[str, str]:
    """What the container sees. July's five, plus the CPU-only additions."""

    return {
        # The job writes its own results back into Cypress at the end, which needs HTTP out.
        "YT_ALLOW_HTTP_REQUESTS_TO_YT_FROM_JOB": "1",
        "YT_PROXY": args.proxy,
        "TROLL_FARM_RUNTIME_ARCHIVE": "./runtime_wheelhouse.tar.gz",
        "TROLL_FARM_YT_OUTPUT_FILE": paths["output"],
        "TROLL_FARM_YT_LOG_FILE": paths["log"],
        # The core count, in the three places that read one.
        "TROLL_FARM_CPU_LIMIT": str(args.cpu_limit),
        "RAYON_NUM_THREADS": str(args.cpu_limit),
        "TROLL_FARM_HEARTBEAT_MINUTES": str(args.heartbeat_minutes),
        # There is no graphics card here; say so plainly so torch does not go looking.
        "CUDA_VISIBLE_DEVICES": "",
    }


def build_spec(args, paths: dict[str, str]):
    """The vanilla specification, built by `yt.wrapper`'s own builders (no network involved)."""

    yt, YPath = _load_yt_wrapper()
    inputs = [f"{paths['inputs']}/{name}" for name in REQUIRED_UPLOADS]
    file_paths = [
        YPath(path, attributes={"file_name": name})
        for path, name in zip(inputs, REQUIRED_UPLOADS)
    ] + [YPath(args.runtime_archive, attributes={"file_name": "runtime_wheelhouse.tar.gz"})]
    task = yt.TaskSpecBuilder("train").job_count(1)
    gpu_limit = int(getattr(args, "gpu_limit", 0) or 0)
    if gpu_limit > 0:
        # The training is CPU-only (the entrypoint pins PyTorch to the CPU with an empty
        # CUDA_VISIBLE_DEVICES); a GPU is requested only so that a GPU pool tree schedules the
        # job at all -- the owner's word of 2026-08-30 ("gpu"), the CPU tree's pools being closed
        # to immediate operations. The slot is reserved, not used.
        task = task.gpu_limit(gpu_limit)
    task = (
        task
        .cpu_limit(args.cpu_limit)
        .memory_limit(args.memory_limit)
        .job_time_limit(args.job_time_limit_ms)
        .environment(job_environment(args, paths))
        .file_paths(file_paths)
        .layer_paths(list(args.layer_paths))
        .command("python3 yt_ppo_entrypoint.py")
    )
    flavour = "CPU" if gpu_limit == 0 else f"CPU on a GPU slot x{gpu_limit}"
    spec = (
        yt.VanillaSpecBuilder()
        .max_failed_job_count(1)
        .max_stderr_count(150)
        .title(f"Troll Farm self-play PPO ({flavour}) {args.run_name}")
        .pool(args.pool)
        .pool_trees([args.pool_tree])
        .task("train", task)
    )
    return spec


def spec_preview(args, paths: dict[str, str]) -> dict[str, Any]:
    """The built specification as plain JSON, plus the file names the JSON dump hides.

    `build()` returns YSON paths whose `file_name` attribute does not survive a JSON dump, so the
    names the job will see are listed separately under `file_paths_named`.

    Building a specification is pure arithmetic on strings -- no cluster is contacted. `yt.wrapper`
    nevertheless complains on its own logger that it could not fetch a configuration patch from a
    cluster it was never given, so that logger is silenced for the duration.
    """

    import logging

    _load_yt_wrapper()  # first: importing it resets the level of its own logger
    yt_logger = logging.getLogger("Yt")
    previous = yt_logger.level
    yt_logger.setLevel(logging.CRITICAL)
    try:
        built = json.loads(json.dumps(build_spec(args, paths).build(), default=str))
    finally:
        yt_logger.setLevel(previous)
    built.pop("started_by", None)
    built["tasks"]["train"]["file_paths_named"] = [
        {"cypress_path": f"{paths['inputs']}/{name}", "file_name": name}
        for name in REQUIRED_UPLOADS
    ] + [{"cypress_path": args.runtime_archive, "file_name": "runtime_wheelhouse.tar.gz"}]
    return built


# --------------------------------------------------------------------------- YT plumbing (July's)


def _load_yt_wrapper():
    try:
        import yt.wrapper as yt
        from yt.wrapper.ypath import YPath
    except ImportError as error:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "this command needs the `ytsaurus-client` package; run it with the system python3"
        ) from error
    return yt, YPath


def _load_yt_helpers():
    """July's helper trio out of the math_through_eml project (token, client, vault)."""

    if str(MATH_PROJECT_SRC) not in sys.path:
        sys.path.insert(0, str(MATH_PROJECT_SRC))
    try:
        from math_through_eml.yt_utils import (
            fetch_yav_value,
            get_yt_client,
            resolve_yt_token,
        )
    except ImportError as error:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "YT commands require the math_through_eml environment"
        ) from error
    return fetch_yav_value, get_yt_client, resolve_yt_token


def _client(args):
    _, get_yt_client, _ = _load_yt_helpers()
    return get_yt_client(
        args.proxy,
        token=args.token,
        token_path=args.token_path,
        max_upload_thread_count=1,
    )


def _job_token(args) -> str | None:
    """The token the job gets through the secure vault. July's order, unchanged."""

    fetch_yav_value, _, resolve_yt_token = _load_yt_helpers()
    explicit = resolve_yt_token(args.job_token, args.job_token_path)
    if explicit:
        return explicit
    if args.job_token_yav_secret:
        return fetch_yav_value(
            args.job_token_yav_secret,
            args.job_token_yav_key,
            oauth_token=args.job_token_yav_oauth_token,
        )
    return None


def upload_payload(args, client) -> dict[str, str]:
    payload_dir = Path(args.payload_dir)
    for name in (*REQUIRED_UPLOADS, "payload_manifest.json"):
        if not (payload_dir / name).exists():
            raise FileNotFoundError(payload_dir / name)
    paths = run_paths(args.root, args.run_name)
    for path in (
        args.root.rstrip("/"),
        f"{args.root.rstrip('/')}/runs",
        paths["run"],
        paths["inputs"],
        paths["outputs"],
        paths["logs"],
    ):
        client.create("map_node", path, recursive=True, ignore_existing=True)
    for name in (*REQUIRED_UPLOADS, "payload_manifest.json"):
        destination_dir = paths["run"] if name == "payload_manifest.json" else paths["inputs"]
        destination = f"{destination_dir}/{name}"
        if client.exists(destination):
            client.remove(destination, force=True)
        source_path = payload_dir / name
        with source_path.open("rb") as source:
            client.write_file(
                destination,
                source,
                force_create=True,
                size_hint=source_path.stat().st_size,
            )
        print(f"uploaded {name} -> {destination}", flush=True)
    return paths


def start(args) -> dict[str, Any]:
    """Upload the payload, then run the vanilla operation."""

    payload_dir = Path(args.payload_dir)
    config = json.loads((payload_dir / "yt_run_config.json").read_text(encoding="utf-8"))
    if args.job_time_limit_hours is None:
        hours = config.get("hours")
        args.job_time_limit_hours = (
            float(hours) + WRAP_HOURS if hours else DEFAULT_JOB_TIME_LIMIT_HOURS
        )
    args.job_time_limit_ms = int(args.job_time_limit_hours * 3600 * 1000)
    if args.heartbeat_minutes is None:
        args.heartbeat_minutes = int(config.get("heartbeat_minutes", DEFAULT_HEARTBEAT_MINUTES))
    if args.cpu_limit != config.get("cpu_limit_at_prepare"):
        print(
            json.dumps(
                {
                    "note": "the job's core count differs from the one baked into the payload; "
                    "the entrypoint will rewrite the trainer's --threads to match the job",
                    "cpu_limit_now": args.cpu_limit,
                    "cpu_limit_at_prepare": config.get("cpu_limit_at_prepare"),
                }
            ),
            flush=True,
        )

    client = _client(args)
    paths = upload_payload(args, client)
    if not client.exists(args.runtime_archive):
        raise RuntimeError(f"missing runtime wheelhouse: {args.runtime_archive}")

    spec = build_spec(args, paths)
    token = _job_token(args)
    if token:
        spec = spec.secure_vault_variable("token", token)
    operation = client.run_operation(spec, sync=not args.asynchronous)
    client.set(f"{paths['run']}/@troll_farm_last_operation_id", str(operation.id))
    client.set(f"{paths['run']}/@troll_farm_output_file", paths["output"])
    client.set(f"{paths['run']}/@troll_farm_log_file", paths["log"])
    result = {"operation_id": str(operation.id), **paths}
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def operation_id(client, paths: dict[str, str], explicit: str) -> str:
    if explicit:
        return explicit
    attr = f"{paths['run']}/@troll_farm_last_operation_id"
    if not client.exists(attr):
        raise RuntimeError(f"operation id attribute is absent: {attr}")
    return str(client.get(attr))


def monitor_once(args, client, yt) -> dict[str, Any]:
    paths = run_paths(args.root, args.run_name)
    op_id = operation_id(client, paths, args.operation_id)
    operation = yt.Operation(op_id, client=client)
    status = {
        "operation_id": op_id,
        "state": str(operation.get_state()),
        "progress": operation.get_progress(),
        "output_exists": client.exists(paths["output"]),
        "log_exists": client.exists(paths["log"]),
        "checked_utc": utc_now(),
    }
    print(json.dumps(status, indent=2, sort_keys=True, default=str), flush=True)
    if args.stderr_tail:
        lines: list[str] = []
        for job in operation.get_jobs_with_error_or_stderr():
            if job.get("stderr"):
                lines.extend(str(job["stderr"]).splitlines())
        # The heartbeat lines the entrypoint prints every few minutes land here.
        for line in lines[-args.stderr_tail :]:
            print(line, flush=True)
    return status


def monitor(args) -> dict[str, Any]:
    yt, _ = _load_yt_wrapper()
    client = _client(args)
    status = monitor_once(args, client, yt)
    while args.follow and status["state"] in ("initializing", "preparing", "pending", "running"):
        time.sleep(args.interval)
        status = monitor_once(args, client, yt)
    return status


def _safe_extract(archive_path: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    with tarfile.open(archive_path, "r:*") as archive:
        for member in archive.getmembers():
            target = (destination / member.name).resolve()
            if target != root and root not in target.parents:
                raise RuntimeError(f"unsafe output member: {member.name!r}")
        archive.extractall(destination)


def retrieve(args) -> dict[str, Any]:
    client = _client(args)
    paths = run_paths(args.root, args.run_name)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    result: dict[str, Any] = {"run": paths["run"]}

    if client.exists(paths["log"]):
        log_path = output_dir / "yt_job.log"
        with log_path.open("wb") as sink:
            for chunk in client.read_file(paths["log"]):
                sink.write(chunk)
        result["log"] = str(log_path)

    if not client.exists(paths["output"]):
        raise FileNotFoundError(
            f"{paths['output']} is not there yet -- the job packs it only when training ends"
        )
    archive_path = output_dir / "troll_farm_output.tar.gz"
    with archive_path.open("wb") as sink:
        for chunk in client.read_file(paths["output"]):
            sink.write(chunk)
    extract_dir = output_dir / "extracted"
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    _safe_extract(archive_path, extract_dir)
    result.update(
        {
            "archive": str(archive_path),
            "bytes": archive_path.stat().st_size,
            "sha256": sha256(archive_path),
            "extract_dir": str(extract_dir),
            "extracted": sorted(
                str(path.relative_to(extract_dir))
                for path in extract_dir.rglob("*")
                if path.is_file()
            ),
        }
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


# --------------------------------------------------------------------------- the dry run


def print_dry_run(args, manifest: dict[str, Any]) -> None:
    payload_dir = Path(args.payload_dir)
    archive = payload_dir / "troll_farm_payload.tar.gz"
    print("=" * 78)
    print(f"payload directory : {payload_dir}")
    print(f"run name          : {args.run_name}")
    print("=" * 78)
    print(f"{'bytes':>12}  {'sha256 (first 16)':<18} path")
    for row in manifest["content"]:
        print(f"{row['bytes']:>12}  {row['sha256'][:16]:<18} {row['path']}")
    uncompressed = manifest["payload_uncompressed_bytes"]
    print("-" * 78)
    print(
        f"{uncompressed:>12}  {'':<18} TOTAL uncompressed "
        f"({human_bytes(uncompressed)}, {len(manifest['content'])} files)"
    )
    print(
        f"{archive.stat().st_size:>12}  {sha256(archive)[:16]:<18} "
        f"troll_farm_payload.tar.gz ({human_bytes(archive.stat().st_size)} compressed)"
    )
    print("=" * 78)
    maps = manifest["maps"]
    if "lines_kept" in maps:
        print(
            f"maps: {maps['mode']}, every {maps['every']}th line, "
            f"{maps['lines_kept']} of {maps['lines_read']} maps, "
            f"{human_bytes(maps['destination_bytes'])} of "
            f"{human_bytes(maps['source_bytes'])}"
        )
    else:
        print(f"maps: {json.dumps(maps, sort_keys=True)}")
    print(f"budget: {json.dumps(manifest['budget'], sort_keys=True)}")
    if "caution" in manifest["budget"]:
        print(f"CAUTION: {manifest['budget']['caution']}")
        print(
            "         at the measured rate this budget is about "
            f"{manifest['budget']['hours_at_the_measured_rate']} hours of training, "
            f"not {manifest['budget']['hours']}"
        )
    print("=" * 78)

    config = json.loads((payload_dir / "yt_run_config.json").read_text(encoding="utf-8"))
    quoted = " ".join(
        f"'{arg}'" if arg.startswith("{") else arg for arg in config["trainer_args"]
    )
    print("the command the job runs (inside the unpacked payload root):")
    print(f"  python3 {config['trainer_script']} {quoted}")
    print(
        f"  environment: RAYON_NUM_THREADS={args.cpu_limit} "
        f"OMP_NUM_THREADS={args.cpu_limit} MKL_NUM_THREADS={args.cpu_limit} "
        f"CUDA_VISIBLE_DEVICES=''"
    )
    print("=" * 78)

    paths = run_paths(args.root, args.run_name)
    if args.job_time_limit_hours is None:
        args.job_time_limit_hours = (
            float(args.hours) + WRAP_HOURS if args.hours else DEFAULT_JOB_TIME_LIMIT_HOURS
        )
    args.job_time_limit_ms = int(args.job_time_limit_hours * 3600 * 1000)
    args.pool_tree = args.pool_tree or "<REQUIRED: --pool-tree, a CPU tree>"
    args.pool = args.pool or "<REQUIRED: --pool, a CPU pool>"
    print("the specification `start` would submit:")
    try:
        preview = spec_preview(args, paths)
    except RuntimeError as error:
        print(f"  (cannot build it here: {error})")
        return
    print(json.dumps(preview, indent=2, sort_keys=True))
    print("=" * 78)
    print("Cypress paths:")
    print(json.dumps(paths, indent=2, sort_keys=True))
    print("nothing above touched the network.")


# --------------------------------------------------------------------------- the command line


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--run-name", default=DEFAULT_RUN_NAME)
    parser.add_argument("--root", default=DEFAULT_YT_ROOT)
    parser.add_argument("--payload-dir", default=None)


def add_yt(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--proxy", default=os.environ.get("YT_PROXY", DEFAULT_YT_PROXY))
    parser.add_argument("--token", default=os.environ.get("YT_TOKEN"))
    parser.add_argument(
        "--token-path",
        default=os.environ.get("YT_TOKEN_PATH", str(Path.home() / ".yt" / "token")),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="build the archive on this machine")
    add_common(prepare)
    add_yt(prepare)
    prepare.add_argument("--force", action="store_true")
    prepare.add_argument("--dry-run", action="store_true", help="build, print, submit nothing")
    prepare.add_argument("--clone", default=str(DEFAULT_CLONE))
    prepare.add_argument("--library", default=str(ROOT / PAYLOAD_LIBRARY))
    prepare.add_argument("--maps", default=None, help="ship this map file verbatim")
    prepare.add_argument("--maps-source", default=None, help="the full corpus to slice")
    prepare.add_argument("--maps-every", type=int, default=5, help="keep one map in every k")
    prepare.add_argument("--full-maps", action="store_true", help="ship the whole corpus")
    prepare.add_argument("--num-envs", type=int, default=128)
    prepare.add_argument("--rollout-steps", type=int, default=32)
    prepare.add_argument("--minibatch-size", type=int, default=1024)
    prepare.add_argument("--update-epochs", type=int, default=2)
    prepare.add_argument(
        "--total-turn-steps",
        type=int,
        default=None,
        help=f"the decision budget; wins over --hours (default {DEFAULT_TOTAL_TURN_STEPS:,})",
    )
    prepare.add_argument(
        "--hours",
        type=float,
        default=None,
        help="turn a wall-clock wish into a decision budget -- read the CAUTION it prints",
    )
    prepare.add_argument(
        "--rate-per-16-cores",
        type=float,
        default=DEFAULT_RATE_PER_16_CORES,
        help=f"decisions a second per sixteen cores for --hours; the home machine reads about "
        f"{MEASURED_RATE_PER_16_CORES:.0f}",
    )
    prepare.add_argument("--anchor-coef", type=float, default=0.1)
    prepare.add_argument("--anchor-coef-final", type=float, default=0.0)
    prepare.add_argument("--anchor-decay-steps", type=int, default=100_000_000)
    prepare.add_argument("--frozen-refresh-updates", type=int, default=100)
    # The trainer's own defaults (train_ppo_full.py), named explicitly so a cluster job can be
    # told to run with different ones instead of silently inheriting whatever the trainer defaults
    # to next.
    prepare.add_argument("--gamma", type=float, default=0.997)
    prepare.add_argument("--wood-shaping", type=float, default=0.5)
    prepare.add_argument("--end-wood", type=float, default=3.5)
    prepare.add_argument("--critic-warmup-updates", type=int, default=0)
    prepare.add_argument("--actor-lr-scale", type=float, default=1.0)
    prepare.add_argument("--train-scope", choices=("all", "plan-critic"), default="all")
    prepare.add_argument("--entropy-coef", type=float, default=0.01)
    prepare.add_argument("--opponent-weights", default=DEFAULT_OPPONENT_WEIGHTS)
    prepare.add_argument("--checkpoint-every", type=int, default=250)
    prepare.add_argument("--gate-every", type=int, default=0)
    prepare.add_argument("--episode-window", type=int, default=1000)
    prepare.add_argument("--seed", type=int, default=5)
    # 2026-09-03 (the owner: the eight-hour iteration is too long): the trainer's learning pass is
    # dense convolution work over 25,168-number observations, 60 % of an update on a CPU; the
    # cluster job already reserves a card and the wheelhouse ships CUDA torch. "cuda" hands the
    # card to the trainer (the entrypoint stops hiding it); "cpu" is the recipe every arm so far ran.
    prepare.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    prepare.add_argument("--cpu-limit", type=int, default=DEFAULT_CPU_LIMIT)
    prepare.add_argument("--memory-limit", type=parse_size, default=DEFAULT_MEMORY_LIMIT)
    prepare.add_argument("--heartbeat-minutes", type=int, default=DEFAULT_HEARTBEAT_MINUTES)
    prepare.add_argument("--pool-tree", default=None, help="only for the dry run's preview")
    prepare.add_argument("--pool", default=None, help="only for the dry run's preview")
    prepare.add_argument(
        "--gpu-limit",
        type=non_negative_int,
        default=0,
        help="GPUs to reserve, only for the dry run's preview to match `start` (0 = a CPU tree)",
    )
    prepare.add_argument("--runtime-archive", default=DEFAULT_RUNTIME)
    prepare.add_argument("--layer-path", dest="layer_paths", action="append")
    prepare.add_argument("--job-time-limit-hours", type=float, default=None)

    start_parser = subparsers.add_parser("start", help="upload the archive and run the job")
    add_common(start_parser)
    add_yt(start_parser)
    # No defaults on purpose: July's GPU pool is the wrong place for this job.
    start_parser.add_argument("--pool-tree", required=True, help="a pool tree (CPU, or a GPU tree with --gpu-limit)")
    start_parser.add_argument("--pool", required=True, help="a pool inside that tree")
    start_parser.add_argument("--cpu-limit", type=int, default=DEFAULT_CPU_LIMIT)
    start_parser.add_argument("--memory-limit", type=parse_size, default=DEFAULT_MEMORY_LIMIT)
    start_parser.add_argument("--gpu-limit", type=non_negative_int, default=0,
                              help="GPUs to reserve (0 = a CPU tree); a GPU tree needs 1 even though "
                                   "the training never touches the card")
    start_parser.add_argument("--job-time-limit-hours", type=float, default=None)
    start_parser.add_argument("--heartbeat-minutes", type=int, default=None)
    start_parser.add_argument("--runtime-archive", default=DEFAULT_RUNTIME)
    start_parser.add_argument("--layer-path", dest="layer_paths", action="append")
    start_parser.add_argument("--async", dest="asynchronous", action="store_true")
    start_parser.add_argument("--job-token", default=os.environ.get("YT_JOB_TOKEN", ""))
    start_parser.add_argument("--job-token-path", default=os.environ.get("YT_JOB_TOKEN_PATH", ""))
    start_parser.add_argument("--job-token-yav-secret", default="tarstars")
    start_parser.add_argument("--job-token-yav-key", default="yt_token")
    start_parser.add_argument("--job-token-yav-oauth-token", default="")

    monitor_parser = subparsers.add_parser("monitor", help="state, progress, the last stderr")
    add_common(monitor_parser)
    add_yt(monitor_parser)
    monitor_parser.add_argument("--operation-id", default="")
    monitor_parser.add_argument("--stderr-tail", type=int, default=40)
    monitor_parser.add_argument("--follow", action="store_true")
    monitor_parser.add_argument("--interval", type=float, default=300.0)

    retrieve_parser = subparsers.add_parser("retrieve", help="download and unpack the results")
    add_common(retrieve_parser)
    add_yt(retrieve_parser)
    retrieve_parser.add_argument("--output-dir", default=None)
    return parser


def resolve_defaults(args) -> None:
    if getattr(args, "payload_dir", None) is None:
        args.payload_dir = str(DEFAULT_PAYLOAD_PARENT / args.run_name)
    if getattr(args, "layer_paths", None) is None:
        args.layer_paths = list(DEFAULT_LAYERS)
    if getattr(args, "output_dir", "sentinel") is None:
        args.output_dir = str(DEFAULT_PAYLOAD_PARENT / f"{args.run_name}-output")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    resolve_defaults(args)
    if args.command == "prepare":
        manifest = prepare_payload(args)
        if args.dry_run:
            print_dry_run(args, manifest)
        else:
            print(json.dumps(manifest, indent=2, sort_keys=True))
    elif args.command == "start":
        start(args)
    elif args.command == "monitor":
        monitor(args)
    elif args.command == "retrieve":
        retrieve(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
