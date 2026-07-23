#!/usr/bin/env python3
"""Entrypoint for one frozen Troll Farm PPO job on a YTsaurus GPU worker."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tarfile
import time
import traceback
import zipfile
from datetime import datetime, timezone
from pathlib import Path


WORK = Path.cwd()
LOG_PATH = WORK / "yt_job.log"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def log(event: str, **payload: object) -> None:
    record = {"event": event, "utc": utc_now(), **payload}
    line = "[troll-farm-yt] " + json.dumps(record, sort_keys=True, default=str)
    print(line, flush=True)
    with LOG_PATH.open("a", encoding="utf-8") as output:
        output.write(line + "\n")


def safe_extract_tar(archive_path: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    with tarfile.open(archive_path, "r:*") as archive:
        for member in archive.getmembers():
            target = (destination / member.name).resolve()
            if target != root and root not in target.parents:
                raise RuntimeError(f"unsafe tar member: {member.name!r}")
        archive.extractall(destination)


def run_tee(command: list[str], *, cwd: Path, env: dict[str, str]) -> None:
    log("command_start", command=command, cwd=str(cwd))
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    assert process.stdout is not None
    with LOG_PATH.open("a", encoding="utf-8") as output:
        for line in process.stdout:
            print(line, end="", flush=True)
            output.write(line)
    return_code = process.wait()
    log("command_complete", command=command, return_code=return_code)
    if return_code:
        raise subprocess.CalledProcessError(return_code, command)


def module_available(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except ModuleNotFoundError:
        return False


def extract_wheels_directly(wheel_paths: list[Path], destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for wheel_path in wheel_paths:
        with zipfile.ZipFile(wheel_path) as archive:
            archive.extractall(destination)
    log(
        "runtime_wheels_extracted_directly",
        wheel_count=len(wheel_paths),
        destination=str(destination),
    )


def ensure_runtime() -> tuple[Path | None, float]:
    start = time.perf_counter()
    if module_available("torch") and module_available("numpy") and module_available(
        "yt.wrapper"
    ):
        log("runtime_dependencies_preinstalled")
        return None, time.perf_counter() - start

    archive_path = Path(os.environ.get("TROLL_FARM_RUNTIME_ARCHIVE", ""))
    if not archive_path.exists():
        raise FileNotFoundError(f"runtime archive is unavailable: {archive_path}")
    wheelhouse = WORK / "runtime_wheelhouse"
    safe_extract_tar(archive_path, wheelhouse)
    wheel_paths = sorted(wheelhouse.rglob("*.whl"))
    if not wheel_paths:
        raise RuntimeError("runtime archive contains no wheels")
    wheel_dirs = sorted({path.parent for path in wheel_paths})
    deps = WORK / "python_deps"
    deps.mkdir(exist_ok=True)
    python = sys.executable or shutil.which("python3") or "python3"
    command = [
        python,
        "-m",
        "pip",
        "install",
        "--no-cache-dir",
        "--target",
        str(deps),
        "--no-index",
    ]
    for wheel_dir in wheel_dirs:
        command.extend(["--find-links", str(wheel_dir)])
    command.extend(
        [
            "torch==2.4.1+cu121",
            "numpy>=1.26,<3",
            "ytsaurus-client>=0.13.48",
        ]
    )
    try:
        run_tee(command, cwd=WORK, env=os.environ.copy())
    except (subprocess.CalledProcessError, FileNotFoundError):
        extract_wheels_directly(wheel_paths, deps)
    sys.path.insert(0, str(deps))
    os.environ["PYTHONPATH"] = str(deps) + os.pathsep + os.environ.get(
        "PYTHONPATH", ""
    )
    if not all(module_available(name) for name in ("torch", "numpy", "yt.wrapper")):
        raise RuntimeError("offline runtime installation did not expose required modules")
    elapsed = time.perf_counter() - start
    log("runtime_ready", seconds=elapsed, dependency_root=str(deps))
    return deps, elapsed


def secure_token() -> str | None:
    for name in ("token", "yt_token", "YT_TOKEN"):
        value = os.environ.get("YT_SECURE_VAULT_" + name)
        if value:
            return value
    return None


def yt_client():
    import yt.wrapper as yt

    return yt.YtClient(
        proxy=os.environ.get("YT_PROXY", "watt.yt.yandex.net"),
        token=secure_token(),
        config={
            "write_parallel": {"enable": False},
            "proxy": {
                "heavy_request_timeout": 120_000,
                "request_timeout": 100_000,
                "retries": {"total_timeout": 300_000},
            },
        },
    )


def upload_file(local_path: Path, remote_path: str) -> None:
    client = yt_client()
    if client.exists(remote_path):
        client.remove(remote_path, force=True)
    with local_path.open("rb") as source:
        client.write_file(
            remote_path,
            source,
            force_create=True,
            size_hint=local_path.stat().st_size,
        )
    log("artifact_uploaded", path=remote_path, bytes=local_path.stat().st_size)


def validate_payload(payload_root: Path) -> dict[str, object]:
    manifest_path = payload_root / "payload_content_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for row in manifest["files"]:
        path = payload_root / str(row["path"])
        actual = sha256(path)
        if actual != row["sha256"]:
            raise RuntimeError(f"payload hash mismatch for {row['path']}: {actual}")
    log("payload_validated", files=len(manifest["files"]))
    return manifest


def bundle_outputs(
    payload_root: Path,
    config: dict[str, object],
    metadata: dict[str, object],
) -> Path:
    metadata_path = WORK / "yt_benchmark_metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    run_name = str(config["run_name"])
    analysis = payload_root / "data" / "analysis" / "live-agent-6553250"
    artifacts = sorted(analysis.glob(f"curriculum-level5-{run_name}*"))
    if not artifacts:
        raise RuntimeError(f"training produced no artifacts for {run_name}")
    output = WORK / "troll_farm_output.tar.gz"
    with tarfile.open(output, "w:gz") as archive:
        archive.add(metadata_path, arcname=metadata_path.name)
        archive.add(LOG_PATH, arcname=LOG_PATH.name)
        archive.add(WORK / "yt_run_config.json", arcname="yt_run_config.json")
        archive.add(
            payload_root / "payload_content_manifest.json",
            arcname="payload_content_manifest.json",
        )
        for path in artifacts:
            archive.add(path, arcname=str(path.relative_to(payload_root)))
    log(
        "output_bundled",
        path=str(output),
        bytes=output.stat().st_size,
        sha256=sha256(output),
        artifacts=[str(path.relative_to(payload_root)) for path in artifacts],
    )
    return output


def main() -> int:
    entry_start = time.perf_counter()
    entry_started_utc = utc_now()
    LOG_PATH.write_text("", encoding="utf-8")
    log("entrypoint_start", python=sys.version)
    config = json.loads((WORK / "yt_run_config.json").read_text(encoding="utf-8"))
    payload_archive = WORK / "troll_farm_payload.tar.gz"
    payload_root = WORK / "payload"
    try:
        extract_start = time.perf_counter()
        safe_extract_tar(payload_archive, payload_root)
        extract_seconds = time.perf_counter() - extract_start
        manifest = validate_payload(payload_root)
        deps, runtime_seconds = ensure_runtime()

        import numpy
        import torch

        if not torch.cuda.is_available() or torch.cuda.device_count() < 1:
            raise RuntimeError("CUDA GPU is unavailable in the allocated job")
        gpu_name = torch.cuda.get_device_name(0)
        log(
            "compute_ready",
            torch=torch.__version__,
            numpy=numpy.__version__,
            cuda_available=torch.cuda.is_available(),
            cuda_device_count=torch.cuda.device_count(),
            gpu_name=gpu_name,
            payload_extract_seconds=extract_seconds,
        )

        child_env = os.environ.copy()
        for key in list(child_env):
            if key.startswith("YT_SECURE_VAULT_") or key == "YT_TOKEN":
                child_env.pop(key, None)
        roots = [str(payload_root)]
        if deps is not None:
            roots.insert(0, str(deps))
        child_env["PYTHONPATH"] = os.pathsep.join(roots)
        child_env["OMP_NUM_THREADS"] = str(config["threads"])
        child_env["MKL_NUM_THREADS"] = str(config["threads"])
        python = sys.executable or shutil.which("python3") or "python3"
        command = [python, "-m", "cgauto.train_level1_ppo", *config["trainer_args"]]
        train_start = time.perf_counter()
        run_tee(command, cwd=payload_root, env=child_env)
        train_seconds = time.perf_counter() - train_start

        summary_path = (
            payload_root
            / "data"
            / "analysis"
            / "live-agent-6553250"
            / f"curriculum-level5-{config['run_name']}-training-summary.json"
        )
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        metadata = {
            "run_name": config["run_name"],
            "operation_role": config["purpose"],
            "entrypoint_started_utc": entry_started_utc,
            "entrypoint_completed_utc": utc_now(),
            "payload_archive_sha256": sha256(payload_archive),
            "payload_manifest_sha256": sha256(
                payload_root / "payload_content_manifest.json"
            ),
            "payload_files": len(manifest["files"]),
            "payload_extract_seconds": extract_seconds,
            "runtime_setup_seconds": runtime_seconds,
            "training_wall_seconds": train_seconds,
            "entrypoint_wall_seconds_before_upload": time.perf_counter() - entry_start,
            "torch_version": torch.__version__,
            "numpy_version": numpy.__version__,
            "gpu_name": gpu_name,
            "training_summary": {
                key: summary.get(key)
                for key in (
                    "global_step",
                    "elapsed_wall_seconds",
                    "elapsed_cpu_seconds",
                    "aggregate_host_cpu_percent",
                    "overall_transitions_per_second",
                    "stage_a_passed",
                    "stage_b_passed",
                    "evaluations",
                )
            },
        }
        output = bundle_outputs(payload_root, config, metadata)
        upload_file(output, os.environ["TROLL_FARM_YT_OUTPUT_FILE"])
        upload_file(LOG_PATH, os.environ["TROLL_FARM_YT_LOG_FILE"])
        log("entrypoint_complete", total_seconds=time.perf_counter() - entry_start)
        return 0
    except Exception as error:
        log("entrypoint_failed", error=repr(error), traceback=traceback.format_exc())
        remote_log = os.environ.get("TROLL_FARM_YT_LOG_FILE", "")
        if remote_log:
            try:
                upload_file(LOG_PATH, remote_log)
            except Exception as upload_error:
                log("failure_log_upload_failed", error=repr(upload_error))
        raise


if __name__ == "__main__":
    raise SystemExit(main())
