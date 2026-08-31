#!/usr/bin/env python3
"""What actually runs inside the cluster job: unpack, install, train, pack the results back.

Plain words for the owner
-------------------------
The cluster starts one container with sixty-four cores and nothing in it but Ubuntu and Python.
This program is the first thing that runs there. In order it:

1. unpacks `troll_farm_payload.tar.gz` (the archive the launcher built) into `./payload`;
2. checks every file in it against the fingerprints the launcher recorded, so a truncated upload
   is caught before three hours of compute are spent on it;
3. installs torch and numpy from the *wheelhouse* -- an archive of prebuilt Python packages that
   already sits in the cluster's file tree, installed with the network switched off (`--no-index`)
   because cluster jobs cannot reach the public package index. The wheelhouse holds a CUDA build
   of torch; a CUDA build runs perfectly well on a machine without a graphics card, which is what
   this job is;
4. checks that the compiled Rust game library is where the environment code expects it and that
   it can actually be loaded;
5. runs `local_claude_1/nn-bot/train_ppo_full.py` with the arguments the launcher recorded --
   the same run that happens on the home machine, with the core count raised to the job's;
6. every few minutes prints one short line to the job's error stream saying how far the training
   has got: the update number, the decisions a second, the win rate, and the newest checkpoint's
   name and size. That line is what `yt_ppo_launcher.py monitor` shows, so progress can be
   watched without downloading anything. The heartbeat only reads local files; it writes nothing
   to the cluster's file tree;
7. when training ends, tars `outputs/` -- every checkpoint, the training summary, the training
   log -- and writes that one archive back into the cluster's file tree, which is where
   `yt_ppo_launcher.py retrieve` picks it up.

It is July's `cgauto/yt_troll_farm_ppo_entrypoint.py` with the GPU requirement removed, the
heartbeat added, and the trainer swapped for the self-play one.
"""

from __future__ import annotations

import ctypes
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tarfile
import threading
import time
import traceback
import zipfile
from datetime import datetime, timezone
from pathlib import Path

WORK = Path.cwd()
OUTPUTS = WORK / "outputs"
LOG_PATH = OUTPUTS / "yt_job.log"
TRAIN_LOG = OUTPUTS / "train.log"
PAYLOAD_ROOT = WORK / "payload"

#: Where `cgauto/rl_full_env.py` looks for the game library when nobody passes it a path. The
#: trainer has no `--library` flag, so this is not a preference -- it is the only place the file
#: can be.
LIBRARY_RELATIVE = Path("rust/target/release/libtroll_farm.so")

_LOG_LOCK = threading.Lock()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def log(event: str, *, stderr: bool = False, **payload: object) -> None:
    """One JSON line, on the job's output stream and in the run's own log file.

    A failure to write the log file is swallowed: the job exists to train, and losing a line of
    bookkeeping must never be the thing that kills six hours of compute.
    """

    record = {"event": event, "utc": utc_now(), **payload}
    line = "[troll-farm-yt] " + json.dumps(record, sort_keys=True, default=str)
    print(line, file=sys.stderr if stderr else sys.stdout, flush=True)
    try:
        with _LOG_LOCK:
            LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with LOG_PATH.open("a", encoding="utf-8") as output:
                output.write(line + "\n")
    except OSError:
        pass


# --------------------------------------------------------------------------- July's plumbing


def safe_extract_tar(archive_path: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    with tarfile.open(archive_path, "r:*") as archive:
        for member in archive.getmembers():
            target = (destination / member.name).resolve()
            if target != root and root not in target.parents:
                raise RuntimeError(f"unsafe tar member: {member.name!r}")
        archive.extractall(destination)


def run_tee(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    log_path: Path = LOG_PATH,
) -> None:
    """Run a command, echoing its output to stdout and appending it to `log_path`."""

    log("command_start", command=command, cwd=str(cwd), log=str(log_path))
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
    with log_path.open("a", encoding="utf-8") as output:
        for line in process.stdout:
            print(line, end="", flush=True)
            output.write(line)
            output.flush()
    return_code = process.wait()
    log("command_complete", command=command[:2], return_code=return_code)
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
    """July's offline installer, unchanged: the wheelhouse, `--no-index`, then a fallback unzip."""

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
    os.environ["PYTHONPATH"] = str(deps) + os.pathsep + os.environ.get("PYTHONPATH", "")
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
    """A write into the cluster: the final bundle, and the heartbeat's mid-run salvage copies."""

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


# --------------------------------------------------------------------------- CPU-only additions


def resolve_cpu_limit(config: dict) -> int:
    """How many cores this job actually has, in the order the launcher intends."""

    for candidate in (
        os.environ.get("TROLL_FARM_CPU_LIMIT"),
        config.get("cpu_limit_at_prepare"),
        os.cpu_count(),
    ):
        try:
            value = int(candidate)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            continue
        if value > 0:
            return value
    return 1


def rewrite_trainer_args(config: dict, cpu_limit: int) -> list[str]:
    """Two substitutions and no others: the thread count and the output directory.

    `--threads` follows the job's core count (the launcher baked in whatever it assumed when the
    archive was built, which need not be what the job was finally started with). `--output-dir` is
    turned from the relative `outputs` into the absolute path inside the job's working directory,
    so the results never end up buried in the unpacked payload.
    """

    arguments = list(config["trainer_args"])
    if config.get("threads_follow_cpu_limit", True) and "--threads" in arguments:
        arguments[arguments.index("--threads") + 1] = str(cpu_limit)
    if "--output-dir" in arguments:
        arguments[arguments.index("--output-dir") + 1] = str(OUTPUTS)
    return arguments


def check_library(payload_root: Path) -> dict:
    """The game library must be loadable, and it must be at the path the environment expects."""

    library = payload_root / LIBRARY_RELATIVE
    if not library.is_file():
        raise FileNotFoundError(
            f"the compiled game library is missing at {library}; `cgauto/rl_full_env.py` has no "
            "way to be told another path from `train_ppo_full.py`"
        )
    handle = ctypes.CDLL(str(library))
    handle.tf_full_plan_version.restype = ctypes.c_char_p
    version = handle.tf_full_plan_version()
    report = {
        "path": str(library),
        "bytes": library.stat().st_size,
        "plan_vocabulary": version.decode() if version else None,
    }
    log("library_ready", **report)
    return report


def _tail_update(path: Path, window: int = 200_000) -> dict | None:
    """The last `{"event": "update", ...}` line the trainer printed, or None."""

    try:
        size = path.stat().st_size
        with path.open("rb") as source:
            source.seek(max(0, size - window))
            chunk = source.read().decode("utf-8", "replace")
    except OSError:
        return None
    for line in reversed(chunk.splitlines()):
        line = line.strip()
        if not line.startswith("{") or '"event": "update"' not in line:
            continue
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue
    return None


def heartbeat_loop(stop: threading.Event, minutes: float, started: float) -> None:
    """Every `minutes`, one line on the job's error stream: how far the training has got.

    The printing is local-only. Every sixth beat (about half an hour at the default period) the
    loop also uploads a **mid-run salvage copy** — the newest checkpoint and the training log —
    next to the job's final output path, as `mid-run-latest.pt` and `mid-run-train.log`. That is
    what survives when the operation is killed from outside (a wall-clock limit, a preemption
    with no restart): the 2026-08-31 01:29Z deaths of ppo-yt-a and ppo-yt-c lost thirteen hours
    of checkpoints each for want of exactly this. The salvage upload runs in its own try/except:
    a flaky upload must never disturb a job that is training happily.

    Read a salvage copy without the launcher:
    `yt --proxy <proxy> read-file <runs>/<name>/outputs/mid-run-latest.pt > local.pt`.
    """

    period = max(30.0, minutes * 60.0)
    beat = 0
    while not stop.wait(period):
        beat += 1
        latest = None
        try:
            checkpoints = sorted(OUTPUTS.glob("*.pt"), key=lambda p: p.stat().st_mtime)
            latest = checkpoints[-1] if checkpoints else None
            update = _tail_update(TRAIN_LOG) or {}
            log(
                "heartbeat",
                stderr=True,
                elapsed_minutes=round((time.perf_counter() - started) / 60.0, 1),
                update=update.get("update"),
                turn_steps=update.get("turn_steps"),
                turns_completed=update.get("turns_completed"),
                turn_steps_per_second=update.get("overall_turn_steps_per_second"),
                mean_referee_margin=update.get("mean_referee_margin"),
                win_rate=update.get("win_rate"),
                entropy=update.get("entropy"),
                checkpoints=len(checkpoints),
                latest_checkpoint=latest.name if latest else None,
                latest_checkpoint_bytes=latest.stat().st_size if latest else None,
                train_log_bytes=TRAIN_LOG.stat().st_size if TRAIN_LOG.exists() else 0,
            )
        except Exception as error:  # pragma: no cover - a heartbeat must never kill the run
            print(f"[troll-farm-yt] heartbeat failed: {error!r}", file=sys.stderr, flush=True)
        if beat % 6 != 0:
            continue
        try:
            final_output = os.environ.get("TROLL_FARM_YT_OUTPUT_FILE")
            if final_output and latest is not None:
                remote_dir = final_output.rsplit("/", 1)[0]
                upload_file(latest, f"{remote_dir}/mid-run-latest.pt")
                if TRAIN_LOG.exists():
                    upload_file(TRAIN_LOG, f"{remote_dir}/mid-run-train.log")
        except Exception as error:  # pragma: no cover - salvage must never kill the run
            print(f"[troll-farm-yt] mid-run salvage failed: {error!r}", file=sys.stderr,
                  flush=True)


def bundle_outputs(config: dict, metadata: dict) -> Path:
    """Everything worth keeping in one archive: `outputs/` plus the two input records."""

    metadata_path = OUTPUTS / "yt_job_metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8"
    )
    produced = sorted(path for path in OUTPUTS.rglob("*") if path.is_file())
    if not any(path.suffix == ".pt" for path in produced):
        log("no_checkpoint_produced", files=[path.name for path in produced])
    output = WORK / "troll_farm_output.tar.gz"
    with tarfile.open(output, "w:gz") as archive:
        for path in produced:
            archive.add(path, arcname=str(Path("outputs") / path.relative_to(OUTPUTS)))
        archive.add(WORK / "yt_run_config.json", arcname="yt_run_config.json")
        archive.add(
            PAYLOAD_ROOT / "payload_content_manifest.json",
            arcname="payload_content_manifest.json",
        )
    log(
        "output_bundled",
        path=str(output),
        bytes=output.stat().st_size,
        sha256=sha256(output),
        files=len(produced),
    )
    return output


def main() -> int:
    entry_start = time.perf_counter()
    entry_started_utc = utc_now()
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("", encoding="utf-8")
    TRAIN_LOG.write_text("", encoding="utf-8")
    log("entrypoint_start", python=sys.version, work=str(WORK), cpu_count=os.cpu_count())

    config = json.loads((WORK / "yt_run_config.json").read_text(encoding="utf-8"))
    payload_archive = WORK / "troll_farm_payload.tar.gz"
    stop = threading.Event()
    heartbeat: threading.Thread | None = None
    try:
        extract_start = time.perf_counter()
        safe_extract_tar(payload_archive, PAYLOAD_ROOT)
        extract_seconds = time.perf_counter() - extract_start
        manifest = validate_payload(PAYLOAD_ROOT)
        library = check_library(PAYLOAD_ROOT)
        deps, runtime_seconds = ensure_runtime()

        import numpy
        import torch

        cpu_limit = resolve_cpu_limit(config)
        log(
            "compute_ready",
            torch=torch.__version__,
            numpy=numpy.__version__,
            cpu_limit=cpu_limit,
            cuda_available=bool(torch.cuda.is_available()),
            payload_extract_seconds=extract_seconds,
        )

        child_env = os.environ.copy()
        # The job's token must not reach the trainer; only this program writes to Cypress.
        for key in list(child_env):
            if key.startswith("YT_SECURE_VAULT_") or key == "YT_TOKEN":
                child_env.pop(key, None)
        roots = [str(PAYLOAD_ROOT)]
        if deps is not None:
            roots.insert(0, str(deps))
        child_env["PYTHONPATH"] = os.pathsep.join(roots)
        child_env["RAYON_NUM_THREADS"] = str(cpu_limit)
        child_env["OMP_NUM_THREADS"] = str(cpu_limit)
        child_env["MKL_NUM_THREADS"] = str(cpu_limit)
        child_env["CUDA_VISIBLE_DEVICES"] = ""
        # Inert today -- `cgauto/rl_full_env.py` reads no environment variable for the library --
        # but set anyway so that the day it grows one, the job already answers it.
        child_env["TF_FULL_LIBRARY"] = library["path"]
        child_env["LD_LIBRARY_PATH"] = os.pathsep.join(
            [str(PAYLOAD_ROOT / LIBRARY_RELATIVE.parent), child_env.get("LD_LIBRARY_PATH", "")]
        ).strip(os.pathsep)

        arguments = rewrite_trainer_args(config, cpu_limit)
        python = sys.executable or shutil.which("python3") or "python3"
        command = [python, str(PAYLOAD_ROOT / config["trainer_script"]), *arguments]
        log("trainer_command", command=command, output_dir=str(OUTPUTS))

        minutes = float(os.environ.get("TROLL_FARM_HEARTBEAT_MINUTES", config.get(
            "heartbeat_minutes", 5
        )))
        heartbeat = threading.Thread(
            target=heartbeat_loop, args=(stop, minutes, entry_start), daemon=True
        )
        heartbeat.start()

        train_start = time.perf_counter()
        run_tee(command, cwd=PAYLOAD_ROOT, env=child_env, log_path=TRAIN_LOG)
        train_seconds = time.perf_counter() - train_start
        stop.set()

        summary_path = OUTPUTS / f"{config['run_name']}-training-summary.json"
        summary = (
            json.loads(summary_path.read_text(encoding="utf-8"))
            if summary_path.exists()
            else {}
        )
        metadata = {
            "run_name": config["run_name"],
            "operation_role": config["purpose"],
            "entrypoint_started_utc": entry_started_utc,
            "entrypoint_completed_utc": utc_now(),
            "payload_archive_sha256": sha256(payload_archive),
            "payload_files": len(manifest["files"]),
            "payload_extract_seconds": extract_seconds,
            "runtime_setup_seconds": runtime_seconds,
            "training_wall_seconds": train_seconds,
            "cpu_limit": cpu_limit,
            "trainer_command": command,
            "torch_version": torch.__version__,
            "numpy_version": numpy.__version__,
            "library": library,
            "training_summary": {
                key: summary.get(key)
                for key in (
                    "turn_steps",
                    "turns_completed",
                    "updates_completed",
                    "elapsed_wall_seconds",
                    "overall_turn_steps_per_second",
                )
            },
        }
        output = bundle_outputs(config, metadata)
        upload_file(output, os.environ["TROLL_FARM_YT_OUTPUT_FILE"])
        upload_file(LOG_PATH, os.environ["TROLL_FARM_YT_LOG_FILE"])
        log("entrypoint_complete", total_seconds=time.perf_counter() - entry_start)
        return 0
    except Exception as error:
        stop.set()
        log("entrypoint_failed", stderr=True, error=repr(error), traceback=traceback.format_exc())
        remote_log = os.environ.get("TROLL_FARM_YT_LOG_FILE", "")
        if remote_log:
            try:
                upload_file(LOG_PATH, remote_log)
            except Exception as upload_error:
                log("failure_log_upload_failed", error=repr(upload_error))
        raise
    finally:
        stop.set()
        if heartbeat is not None:
            heartbeat.join(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
