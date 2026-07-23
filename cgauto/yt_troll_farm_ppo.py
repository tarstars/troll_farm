#!/usr/bin/env python3
"""Prepare, launch, monitor, and retrieve the frozen D11 PPO YT benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
DEFAULT_PAYLOAD_DIR = ANALYSIS / "yt" / "d11-ppo-benchmark-seed137"
DEFAULT_RUN_NAME = "d11-ppo-benchmark-seed137-20260720"
DEFAULT_FINAL_PAYLOAD_DIR = ANALYSIS / "yt" / "d11-ppo-final-seed139"
DEFAULT_FINAL_RUN_NAME = "d11-ppo-final-seed139-20260720"
DEFAULT_YT_ROOT = "//home/delivery_ml/research/tarstars/troll_farm"
DEFAULT_YT_PROXY = "watt.yt.yandex.net"
DEFAULT_RUNTIME = (
    "//home/delivery_ml/research/tarstars/mle/math_through_eml/runtime/"
    "wheelhouse_torch241_cu121_py310.tar.gz"
)
DEFAULT_POOL_TREE = "gpu_starfield_24g_cloud"
DEFAULT_POOL = "research_gpu"
DEFAULT_LAYERS = (
    "//porto_layers/base/jammy/porto_layer_search_ubuntu_jammy_app_lastest.tar.gz",
    "//porto_layers/delta/python/jammy/"
    "porto_delta_layer_ubuntu_jammy_python311_2024-01-24.tar.gz",
)
MATH_PROJECT_SRC = Path("/home/tarstars/prj/math_through_eml/src")

PROTOCOL = ANALYSIS / "curriculum-level5-seed-reacquisition-d11-learning-protocol-2026-07-20.md"
CLONE_CHECKPOINT = ANALYSIS / "curriculum-level5-seed-reacquisition-d11-bc.pt"
TEACHER_BASELINE = ANALYSIS / "curriculum-level5-seed-reacquisition-d11-learning-teacher-6500-6999.json"
RANDOM_BASELINE = ANALYSIS / "curriculum-level5-seed-reacquisition-d11-learning-random-6500-6999.json"
WEIGHTS_RELATIVE = Path(
    "data/analysis/live-agent-6553250/"
    "curriculum-level5-seed-reacquisition-d11-bc-weights.npz"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def benchmark_trainer_args(
    *, run_name: str, device: str, initial_weights: str
) -> list[str]:
    return [
        "--curriculum-level",
        "5",
        "--level5-opponent-mode",
        "crop-first-funded-trio-repeated-pressure-reacquire-180",
        "--run-name",
        run_name,
        "--model-seed",
        "137",
        "--train-seed-base",
        "7200000",
        "--eval-seed-base",
        "6500",
        "--num-envs",
        "100",
        "--rollout-steps",
        "100",
        "--total-transitions",
        "1000000",
        "--stage-a-transitions",
        "1000000",
        "--eval-episodes",
        "500",
        "--max-turns",
        "240",
        "--update-epochs",
        "4",
        "--minibatch-size",
        "1000",
        "--learning-rate",
        "0.00025",
        "--gamma",
        "0.99",
        "--gae-lambda",
        "0.95",
        "--clip-coef",
        "0.2",
        "--entropy-coef",
        "0.01",
        "--value-coef",
        "0.5",
        "--reward-scale",
        "0.01",
        "--max-grad-norm",
        "0.5",
        "--threads",
        "14",
        "--device",
        device,
        "--target-kl",
        "0.03",
        "--gate-profile",
        "level5",
        "--protocol",
        str(Path("data/analysis/live-agent-6553250") / PROTOCOL.name),
        "--random-baseline",
        str(Path("data/analysis/live-agent-6553250") / RANDOM_BASELINE.name),
        "--teacher-baseline",
        str(Path("data/analysis/live-agent-6553250") / TEACHER_BASELINE.name),
        "--teacher-aux-coef",
        "0.10",
        "--initial-weights-npz",
        initial_weights,
    ]


def final_trainer_args(
    *, run_name: str, device: str, initial_weights: str
) -> list[str]:
    """Return the preregistered four-million-transition D11 schedule."""
    args = benchmark_trainer_args(
        run_name=run_name,
        device=device,
        initial_weights=initial_weights,
    )
    replacements = {
        "--model-seed": "139",
        "--train-seed-base": "7400000",
        "--total-transitions": "4000000",
    }
    for option, value in replacements.items():
        args[args.index(option) + 1] = value
    return args


def payload_sources(weights_path: Path) -> list[tuple[Path, Path]]:
    return [
        (ROOT / "cgauto" / "rl_level1_env.py", Path("cgauto/rl_level1_env.py")),
        (ROOT / "cgauto" / "rl_level2_env.py", Path("cgauto/rl_level2_env.py")),
        (ROOT / "cgauto" / "rl_level3_env.py", Path("cgauto/rl_level3_env.py")),
        (ROOT / "cgauto" / "rl_level4_env.py", Path("cgauto/rl_level4_env.py")),
        (ROOT / "cgauto" / "rl_level5_env.py", Path("cgauto/rl_level5_env.py")),
        (
            ROOT / "cgauto" / "train_level1_ppo.py",
            Path("cgauto/train_level1_ppo.py"),
        ),
        (
            ROOT / "rust" / "target" / "release" / "libtroll_farm.so",
            Path("rust/target/release/libtroll_farm.so"),
        ),
        (
            PROTOCOL,
            Path("data/analysis/live-agent-6553250") / PROTOCOL.name,
        ),
        (
            TEACHER_BASELINE,
            Path("data/analysis/live-agent-6553250") / TEACHER_BASELINE.name,
        ),
        (
            RANDOM_BASELINE,
            Path("data/analysis/live-agent-6553250") / RANDOM_BASELINE.name,
        ),
        (weights_path, WEIGHTS_RELATIVE),
    ]


def _tar_filter(info: tarfile.TarInfo) -> tarfile.TarInfo:
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    info.mtime = 0
    return info


def prepare_payload(
    payload_dir: Path,
    *,
    force: bool = False,
    profile: str = "benchmark",
) -> dict[str, Any]:
    if profile not in ("benchmark", "final"):
        raise ValueError(f"unknown payload profile: {profile}")
    required = [PROTOCOL, CLONE_CHECKPOINT, TEACHER_BASELINE, RANDOM_BASELINE]
    missing = [path for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing frozen inputs: {missing}")
    if payload_dir.exists():
        if not force:
            raise FileExistsError(f"payload directory already exists: {payload_dir}")
        shutil.rmtree(payload_dir)
    payload_dir.mkdir(parents=True)

    from cgauto.train_level1_ppo import (
        SpatialActorCritic,
        save_model_weights_npz,
    )

    import torch

    saved = torch.load(CLONE_CHECKPOINT, map_location="cpu", weights_only=False)
    model = SpatialActorCritic()
    model.load_state_dict(saved["model"])
    weights_path = payload_dir / WEIGHTS_RELATIVE.name
    save_model_weights_npz(model, weights_path)

    files = payload_sources(weights_path)
    content_rows = []
    for source, relative in files:
        if not source.exists():
            raise FileNotFoundError(source)
        content_rows.append(
            {
                "path": str(relative),
                "bytes": source.stat().st_size,
                "sha256": sha256(source),
            }
        )
    content_purpose = (
        "D11 one-million-transition PPO local/YT throughput benchmark"
        if profile == "benchmark"
        else "D11 preregistered four-million-transition PPO run"
    )
    content_manifest = {
        "purpose": content_purpose,
        "created_utc": utc_now(),
        "clone_checkpoint": str(CLONE_CHECKPOINT.relative_to(ROOT)),
        "clone_checkpoint_sha256": sha256(CLONE_CHECKPOINT),
        "files": content_rows,
    }
    content_manifest_path = payload_dir / "payload_content_manifest.json"
    content_manifest_path.write_text(
        json.dumps(content_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    files.append((content_manifest_path, Path("payload_content_manifest.json")))

    archive_path = payload_dir / "troll_farm_payload.tar.gz"
    with tarfile.open(archive_path, "w:gz") as archive:
        for source, relative in files:
            archive.add(source, arcname=str(relative), filter=_tar_filter)

    config_run_name = (
        "seed-reacquisition-d11-ppo-benchmark-yt"
        if profile == "benchmark"
        else "seed-reacquisition-d11-ppo-final-yt"
    )
    trainer_args_factory = (
        benchmark_trainer_args if profile == "benchmark" else final_trainer_args
    )
    config = {
        "purpose": (
            "throughput_benchmark_only"
            if profile == "benchmark"
            else "conditional_four_million_ppo"
        ),
        "created_utc": utc_now(),
        "run_name": config_run_name,
        "threads": 14,
        "trainer_args": trainer_args_factory(
            run_name=config_run_name,
            device="cuda",
            initial_weights=str(WEIGHTS_RELATIVE),
        ),
    }
    config_path = payload_dir / "yt_run_config.json"
    config_path.write_text(
        json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    entrypoint_path = payload_dir / "yt_troll_farm_ppo_entrypoint.py"
    shutil.copy2(ROOT / "cgauto" / "yt_troll_farm_ppo_entrypoint.py", entrypoint_path)

    manifest = {
        "purpose": config["purpose"],
        "created_utc": utc_now(),
        "frozen_protocol_sha256": sha256(PROTOCOL),
        "clone_checkpoint_sha256": sha256(CLONE_CHECKPOINT),
        "files": {
            path.name: {"bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in (archive_path, config_path, entrypoint_path)
        },
    }
    manifest_path = payload_dir / "payload_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def _load_yt_helpers():
    if str(MATH_PROJECT_SRC) not in sys.path:
        sys.path.insert(0, str(MATH_PROJECT_SRC))
    try:
        import yt.wrapper as yt
        from math_through_eml.yt_utils import (
            fetch_yav_value,
            get_yt_client,
            resolve_yt_token,
        )
        from yt.wrapper.ypath import YPath
    except ImportError as error:
        raise RuntimeError(
            "YT commands require the math_through_eml environment"
        ) from error
    return yt, YPath, fetch_yav_value, get_yt_client, resolve_yt_token


def _client(args: argparse.Namespace):
    _, _, _, get_yt_client, _ = _load_yt_helpers()
    return get_yt_client(
        args.proxy,
        token=args.token,
        token_path=args.token_path,
        max_upload_thread_count=1,
    )


def run_paths(root: str, run_name: str) -> dict[str, str]:
    run_dir = f"{root.rstrip('/')}/runs/{run_name}"
    return {
        "run": run_dir,
        "inputs": f"{run_dir}/inputs",
        "outputs": f"{run_dir}/outputs",
        "output": f"{run_dir}/outputs/troll_farm_output.tar.gz",
        "log": f"{run_dir}/outputs/yt_job.log",
    }


def upload_payload(args: argparse.Namespace) -> dict[str, str]:
    payload_dir = Path(args.payload_dir)
    required = (
        "troll_farm_payload.tar.gz",
        "yt_run_config.json",
        "yt_troll_farm_ppo_entrypoint.py",
        "payload_manifest.json",
    )
    for name in required:
        if not (payload_dir / name).exists():
            raise FileNotFoundError(payload_dir / name)
    client = _client(args)
    paths = run_paths(args.root, args.run_name)
    for path in (
        args.root.rstrip("/"),
        f"{args.root.rstrip('/')}/runs",
        paths["run"],
        paths["inputs"],
        paths["outputs"],
    ):
        client.create("map_node", path, recursive=True, ignore_existing=True)
    for name in required:
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
    print(json.dumps(paths, indent=2, sort_keys=True))
    return paths


def _job_token(args: argparse.Namespace) -> str | None:
    _, _, fetch_yav_value, _, resolve_yt_token = _load_yt_helpers()
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


def launch(args: argparse.Namespace):
    yt, YPath, _, _, _ = _load_yt_helpers()
    client = _client(args)
    paths = run_paths(args.root, args.run_name)
    expected = [
        f"{paths['inputs']}/troll_farm_payload.tar.gz",
        f"{paths['inputs']}/yt_run_config.json",
        f"{paths['inputs']}/yt_troll_farm_ppo_entrypoint.py",
        args.runtime_archive,
    ]
    missing = [path for path in expected if not client.exists(path)]
    if missing:
        raise RuntimeError(f"missing remote inputs: {missing}")
    named = lambda path, name: YPath(path, attributes={"file_name": name})
    file_paths = [
        named(expected[0], "troll_farm_payload.tar.gz"),
        named(expected[1], "yt_run_config.json"),
        named(expected[2], "yt_troll_farm_ppo_entrypoint.py"),
        named(args.runtime_archive, "runtime_wheelhouse.tar.gz"),
    ]
    environment = {
        "YT_ALLOW_HTTP_REQUESTS_TO_YT_FROM_JOB": "1",
        "YT_PROXY": args.proxy,
        "TROLL_FARM_RUNTIME_ARCHIVE": "./runtime_wheelhouse.tar.gz",
        "TROLL_FARM_YT_OUTPUT_FILE": paths["output"],
        "TROLL_FARM_YT_LOG_FILE": paths["log"],
    }
    task = (
        yt.TaskSpecBuilder("train")
        .job_count(1)
        .gpu_limit(1)
        .cpu_limit(args.cpu_limit)
        .memory_limit(args.memory_limit)
        .job_time_limit(args.job_time_limit_ms)
        .environment(environment)
        .file_paths(file_paths)
        .layer_paths(args.layer_paths)
        .command("python3 yt_troll_farm_ppo_entrypoint.py")
    )
    spec = (
        yt.VanillaSpecBuilder()
        .max_failed_job_count(1)
        .max_stderr_count(150)
        .title(f"Troll Farm D11 PPO {args.run_name}")
        .pool(args.pool)
        .pool_trees([args.pool_tree])
        .task("train", task)
    )
    token = _job_token(args)
    if token:
        spec = spec.secure_vault_variable("token", token)
    operation = client.run_operation(spec, sync=not args.asynchronous)
    client.set(f"{paths['run']}/@troll_farm_last_operation_id", str(operation.id))
    client.set(f"{paths['run']}/@troll_farm_output_file", paths["output"])
    client.set(f"{paths['run']}/@troll_farm_log_file", paths["log"])
    result = {"operation_id": str(operation.id), **paths}
    print(json.dumps(result, indent=2, sort_keys=True))
    return operation


def operation_id(client, paths: dict[str, str], explicit: str) -> str:
    if explicit:
        return explicit
    attr = f"{paths['run']}/@troll_farm_last_operation_id"
    if not client.exists(attr):
        raise RuntimeError(f"operation id attribute is absent: {attr}")
    return str(client.get(attr))


def show_status(args: argparse.Namespace) -> dict[str, Any]:
    yt, _, _, _, _ = _load_yt_helpers()
    client = _client(args)
    paths = run_paths(args.root, args.run_name)
    op_id = operation_id(client, paths, args.operation_id)
    operation = yt.Operation(op_id, client=client)
    status = {
        "operation_id": op_id,
        "state": str(operation.get_state()),
        "progress": operation.get_progress(),
        "output_exists": client.exists(paths["output"]),
        "log_exists": client.exists(paths["log"]),
    }
    print(json.dumps(status, indent=2, sort_keys=True, default=str))
    if args.stderr_tail:
        lines: list[str] = []
        for job in operation.get_jobs_with_error_or_stderr():
            if job.get("stderr"):
                lines.extend(str(job["stderr"]).splitlines())
        for line in lines[-args.stderr_tail :]:
            print(line)
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


def download(args: argparse.Namespace) -> dict[str, Any]:
    client = _client(args)
    paths = run_paths(args.root, args.run_name)
    if not client.exists(paths["output"]):
        raise FileNotFoundError(paths["output"])
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / "troll_farm_output.tar.gz"
    with archive_path.open("wb") as output:
        for chunk in client.read_file(paths["output"]):
            output.write(chunk)
    extract_dir = output_dir / "extracted"
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    _safe_extract(archive_path, extract_dir)
    result = {
        "archive": str(archive_path),
        "bytes": archive_path.stat().st_size,
        "sha256": sha256(archive_path),
        "extract_dir": str(extract_dir),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def _run_local(
    args: argparse.Namespace,
    *,
    run_name: str,
    trainer_args_factory,
    timing_name: str,
) -> int:
    payload_dir = Path(args.payload_dir)
    weights = payload_dir / WEIGHTS_RELATIVE.name
    if not weights.exists():
        raise FileNotFoundError(weights)
    command = [
        sys.executable,
        "-m",
        "cgauto.train_level1_ppo",
        *trainer_args_factory(
            run_name=run_name,
            device="cpu",
            initial_weights=str(weights),
        ),
    ]
    start = time.perf_counter()
    completed = subprocess.run(command, cwd=ROOT, env={**os.environ, "PYTHONPATH": "."})
    metadata = {
        "command": command,
        "return_code": completed.returncode,
        "outer_wall_seconds": time.perf_counter() - start,
        "completed_utc": utc_now(),
    }
    path = ANALYSIS / timing_name
    path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    return completed.returncode


def run_local(args: argparse.Namespace) -> int:
    return _run_local(
        args,
        run_name="seed-reacquisition-d11-ppo-benchmark-local",
        trainer_args_factory=benchmark_trainer_args,
        timing_name=(
            "curriculum-level5-seed-reacquisition-d11-ppo-benchmark-local-"
            "outer-timing.json"
        ),
    )


def run_final_local(args: argparse.Namespace) -> int:
    return _run_local(
        args,
        run_name="seed-reacquisition-d11-ppo-final-local",
        trainer_args_factory=final_trainer_args,
        timing_name=(
            "curriculum-level5-seed-reacquisition-d11-ppo-final-local-"
            "outer-timing.json"
        ),
    )


def add_yt_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--run-name", default=DEFAULT_RUN_NAME)
    parser.add_argument("--root", default=DEFAULT_YT_ROOT)
    parser.add_argument("--proxy", default=os.environ.get("YT_PROXY", DEFAULT_YT_PROXY))
    parser.add_argument("--token", default=os.environ.get("YT_TOKEN"))
    parser.add_argument(
        "--token-path",
        default=os.environ.get("YT_TOKEN_PATH", str(Path.home() / ".yt" / "token")),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare = subparsers.add_parser("prepare")
    prepare.add_argument("--payload-dir")
    prepare.add_argument("--profile", choices=("benchmark", "final"), default="benchmark")
    prepare.add_argument("--force", action="store_true")

    local = subparsers.add_parser("run-local")
    local.add_argument("--payload-dir", default=str(DEFAULT_PAYLOAD_DIR))

    final_local = subparsers.add_parser("run-final-local")
    final_local.add_argument("--payload-dir", default=str(DEFAULT_PAYLOAD_DIR))

    upload = subparsers.add_parser("upload")
    upload.add_argument("--payload-dir", default=str(DEFAULT_PAYLOAD_DIR))
    add_yt_args(upload)

    start = subparsers.add_parser("launch")
    add_yt_args(start)
    start.add_argument("--runtime-archive", default=DEFAULT_RUNTIME)
    start.add_argument("--pool-tree", default=DEFAULT_POOL_TREE)
    start.add_argument("--pool", default=DEFAULT_POOL)
    start.add_argument("--cpu-limit", type=int, default=16)
    start.add_argument("--memory-limit", type=int, default=32 * 1024**3)
    start.add_argument("--job-time-limit-ms", type=int, default=6 * 60 * 60 * 1000)
    start.add_argument("--layer-path", dest="layer_paths", action="append")
    start.add_argument("--async", dest="asynchronous", action="store_true")
    start.add_argument("--job-token", default=os.environ.get("YT_JOB_TOKEN", ""))
    start.add_argument("--job-token-path", default=os.environ.get("YT_JOB_TOKEN_PATH", ""))
    start.add_argument("--job-token-yav-secret", default="tarstars")
    start.add_argument("--job-token-yav-key", default="yt_token")
    start.add_argument("--job-token-yav-oauth-token", default="")

    status = subparsers.add_parser("status")
    add_yt_args(status)
    status.add_argument("--operation-id", default="")
    status.add_argument("--stderr-tail", type=int, default=80)

    retrieve = subparsers.add_parser("download")
    add_yt_args(retrieve)
    retrieve.add_argument(
        "--output-dir",
        default=str(ANALYSIS / "yt" / "d11-ppo-benchmark-seed137-output"),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "prepare":
        default_dir = (
            DEFAULT_PAYLOAD_DIR
            if args.profile == "benchmark"
            else DEFAULT_FINAL_PAYLOAD_DIR
        )
        prepare_payload(
            Path(args.payload_dir) if args.payload_dir else default_dir,
            force=args.force,
            profile=args.profile,
        )
    elif args.command == "run-local":
        return run_local(args)
    elif args.command == "run-final-local":
        return run_final_local(args)
    elif args.command == "upload":
        upload_payload(args)
    elif args.command == "launch":
        if args.layer_paths is None:
            args.layer_paths = list(DEFAULT_LAYERS)
        launch(args)
    elif args.command == "status":
        show_status(args)
    elif args.command == "download":
        download(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
