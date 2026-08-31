"""Tests for the CPU-only YTsaurus launcher of the self-play PPO trainer.

Three things are pinned here, and they are the three that can silently break a six-hour cluster
job long after the launcher has stopped printing:

1. **The payload is complete.** The archive is extracted into a temporary directory and the
   trainer is imported out of *that* directory, with the repository nowhere on the import path.
   If a single module were missing from the list in `yt_ppo_launcher.PAYLOAD_MODULES`, the import
   fails here rather than in the cluster. Only the import is exercised -- constructing the
   environment would need the compiled Rust library to load, which is a separate matter.
2. **The job configuration round-trips.** Every argument the launcher bakes into
   `yt_run_config.json` is fed back to the trainer's own argument parser, so a flag that the
   trainer does not have (or that changed its name) is caught on this machine.
3. **The map cutter is honest.** It keeps exactly every k-th record and nothing else.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NN_BOT = ROOT / "local_claude_1" / "nn-bot"
MAPS_SLICE = NN_BOT / "maps-slice-1000.jsonl"
LIBRARY = ROOT / "rust" / "target" / "release" / "libtroll_farm.so"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


launcher = _load("yt_ppo_launcher_under_test", NN_BOT / "yt_ppo_launcher.py")
entrypoint = _load("yt_ppo_entrypoint_under_test", NN_BOT / "yt_ppo_entrypoint.py")
cut_maps_module = _load("cut_maps_under_test", NN_BOT / "cut_maps.py")


def _trainer():
    """The trainer module, loaded on demand.

    Two interpreters run this file. The virtual environment at `/home/tarstars/nn-venv` has torch
    and numpy but not `yt.wrapper`; the system `python3` has `yt.wrapper` but not torch. Loading
    the trainer lazily lets each of them run the tests it can and skip the rest, so both the
    payload tests and the specification test are actually executed somewhere.
    """

    pytest.importorskip("torch", reason="the trainer's own parser needs torch")
    if "train_ppo_full_for_launcher_test" not in sys.modules:
        _load("train_ppo_full_for_launcher_test", NN_BOT / "train_ppo_full.py")
    return sys.modules["train_ppo_full_for_launcher_test"]


def _fake_clone(tmp_path: Path) -> Path:
    """A stand-in for the clone checkpoint: the launcher copies it, it never loads it."""

    clone = tmp_path / "clone-pilot.pt"
    clone.write_bytes(b"not really a checkpoint, but the launcher only copies bytes")
    return clone


def _prepare(tmp_path: Path, *extra: str):
    payload_dir = tmp_path / "payload-dir"
    args = launcher.build_parser().parse_args(
        [
            "prepare",
            "--run-name",
            "test-run",
            "--payload-dir",
            str(payload_dir),
            "--clone",
            str(_fake_clone(tmp_path)),
            "--maps",
            str(MAPS_SLICE),
            *extra,
        ]
    )
    launcher.resolve_defaults(args)
    manifest = launcher.prepare_payload(args)
    return args, payload_dir, manifest


# --------------------------------------------------------------------------- the map cutter


def test_cutter_keeps_every_kth_record_of_the_thousand_map_slice(tmp_path: Path) -> None:
    source_lines = [line for line in MAPS_SLICE.read_text().splitlines() if line.strip()]
    assert len(source_lines) >= 900  # the slice on disk

    destination = tmp_path / "every5.jsonl"
    report = cut_maps_module.cut_maps(MAPS_SLICE, destination, every=5)

    kept = [line for line in destination.read_text().splitlines() if line.strip()]
    assert kept == source_lines[::5]
    assert report["lines_read"] == len(source_lines)
    assert report["lines_kept"] == len(kept)
    assert report["destination_bytes"] == destination.stat().st_size
    # every record is still one whole map
    assert all("map_hash" in json.loads(line) for line in kept[:20])


def test_cutter_with_every_one_is_a_faithful_copy(tmp_path: Path) -> None:
    destination = tmp_path / "all.jsonl"
    report = cut_maps_module.cut_maps(MAPS_SLICE, destination, every=1)
    source_lines = [line for line in MAPS_SLICE.read_text().splitlines() if line.strip()]
    assert report["lines_kept"] == report["lines_read"] == len(source_lines)
    assert destination.read_text().splitlines() == source_lines


def test_cutter_refuses_a_zero_stride(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        cut_maps_module.cut_maps(MAPS_SLICE, tmp_path / "x.jsonl", every=0)


# --------------------------------------------------------------------------- the payload


@pytest.mark.skipif(not LIBRARY.is_file(), reason="the Rust library has not been built here")
def test_payload_holds_exactly_the_files_the_job_needs(tmp_path: Path) -> None:
    _, payload_dir, manifest = _prepare(tmp_path)
    with tarfile.open(payload_dir / "troll_farm_payload.tar.gz") as archive:
        members = sorted(archive.getnames())

    expected = sorted(
        [str(path) for path in launcher.PAYLOAD_MODULES]
        + [
            str(launcher.PAYLOAD_LIBRARY),
            str(launcher.PAYLOAD_MAPS),
            str(launcher.PAYLOAD_CLONE),
            "payload_content_manifest.json",
        ]
    )
    assert members == expected
    # The library's location is load-bearing: `cgauto/rl_full_env.py` resolves it relative to its
    # own parent and the trainer has no flag to override it.
    assert "rust/target/release/libtroll_farm.so" in members
    assert manifest["payload_uncompressed_bytes"] == sum(
        row["bytes"] for row in manifest["content"]
    )
    for name in launcher.REQUIRED_UPLOADS + ("payload_manifest.json",):
        assert (payload_dir / name).is_file()


@pytest.mark.skipif(not LIBRARY.is_file(), reason="the Rust library has not been built here")
def test_the_trainer_imports_out_of_the_extracted_payload(tmp_path: Path) -> None:
    trainer = _trainer()
    _, payload_dir, _ = _prepare(tmp_path)
    extracted = tmp_path / "extracted"
    with tarfile.open(payload_dir / "troll_farm_payload.tar.gz") as archive:
        archive.extractall(extracted)

    probe = (
        "import importlib.util, sys, json;"
        "import cgauto.train_level1_ppo as t;"
        "import cgauto.rl_full_env as e;"
        "spec = importlib.util.spec_from_file_location("
        "'trainer', 'local_claude_1/nn-bot/train_ppo_full.py');"
        "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m);"
        "print(json.dumps({'plan': t.PLAN_VOCAB_VERSION, 'env_plan': e.PLAN_VOCAB_VERSION,"
        " 'opponents': list(m.OPPONENT_IDS), 'root': str(m.ROOT)}))"
    )
    environment = {
        key: value
        for key, value in os.environ.items()
        if key not in ("PYTHONPATH", "PYTHONHOME")
    }
    environment["PYTHONPATH"] = str(extracted)
    completed = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=extracted,
        env=environment,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert completed.returncode == 0, completed.stderr[-4000:]
    result = json.loads(completed.stdout.strip().splitlines()[-1])
    # The trainer computes its own root as its grandparent directory; inside the payload that must
    # land on the payload root, or `--maps data/maps.jsonl` and the library path both break.
    assert Path(result["root"]) == extracted.resolve()
    assert result["plan"] == result["env_plan"]
    assert result["opponents"] == list(trainer.OPPONENT_IDS)


# --------------------------------------------------------------------------- the job config


@pytest.mark.skipif(not LIBRARY.is_file(), reason="the Rust library has not been built here")
def test_job_config_round_trips_through_the_trainers_own_parser(tmp_path: Path) -> None:
    trainer = _trainer()
    args, payload_dir, _ = _prepare(tmp_path, "--cpu-limit", "48")
    config = json.loads((payload_dir / "yt_run_config.json").read_text())

    parsed = trainer.build_parser().parse_args(config["trainer_args"])
    assert parsed.env == "full"
    assert parsed.maps == str(launcher.PAYLOAD_MAPS)
    assert (
        parsed.initial_checkpoint
        == parsed.anchor_checkpoint
        == parsed.frozen_checkpoint
        == str(launcher.PAYLOAD_CLONE)
    )
    assert parsed.threads == 48  # the prepared core count
    assert parsed.device == "cpu"
    assert parsed.gate_every == 0
    assert parsed.output_dir == launcher.OUTPUT_DIR_ARG
    assert parsed.run_name == "test-run" == config["run_name"]
    # the opponent mixture survives as JSON the trainer can read
    assert set(json.loads(parsed.opponent_weights)) <= set(trainer.OPPONENT_IDS)
    # the trainer's own divisibility rule
    assert (parsed.num_envs * parsed.rollout_steps) % parsed.minibatch_size == 0

    # ...and the entrypoint's two rewrites, the only ones it is allowed to make.
    rewritten = entrypoint.rewrite_trainer_args(config, cpu_limit=64)
    reparsed = trainer.build_parser().parse_args(rewritten)
    assert reparsed.threads == 64
    assert Path(reparsed.output_dir).is_absolute()
    assert Path(reparsed.output_dir).name == launcher.OUTPUT_DIR_ARG
    untouched = {"--threads", "--output-dir"}
    for index, token in enumerate(config["trainer_args"]):
        if token.startswith("--") and token not in untouched:
            assert rewritten[index] == token
            assert rewritten[index + 1] == config["trainer_args"][index + 1]


@pytest.mark.skipif(not LIBRARY.is_file(), reason="the Rust library has not been built here")
def test_the_five_new_trainer_flags_round_trip_with_non_default_values(tmp_path: Path) -> None:
    """`--gamma`, `--wood-shaping`, `--end-wood`, `--critic-warmup-updates` and `--actor-lr-scale`
    must reach the job exactly as the coordinator names them, through `yt_run_config.json` and
    into the trainer's own parser -- not silently fall back to the trainer's defaults."""

    trainer = _trainer()
    _, payload_dir, _ = _prepare(
        tmp_path,
        "--gamma", "0.99",
        "--wood-shaping", "0.75",
        "--end-wood", "4.5",
        "--critic-warmup-updates", "50",
        "--actor-lr-scale", "0.25",
        "--train-scope", "plan-critic",
        "--entropy-coef", "0.0",
    )
    config = json.loads((payload_dir / "yt_run_config.json").read_text())
    for flag in (
        "--gamma",
        "--wood-shaping",
        "--end-wood",
        "--critic-warmup-updates",
        "--actor-lr-scale",
        "--train-scope",
        "--entropy-coef",
    ):
        assert flag in config["trainer_args"]

    parsed = trainer.build_parser().parse_args(config["trainer_args"])
    assert parsed.gamma == pytest.approx(0.99)
    assert parsed.wood_shaping == pytest.approx(0.75)
    assert parsed.end_wood == pytest.approx(4.5)
    assert parsed.critic_warmup_updates == 50
    assert parsed.actor_lr_scale == pytest.approx(0.25)
    assert parsed.train_scope == "plan-critic"
    assert parsed.entropy_coef == pytest.approx(0.0)


@pytest.mark.skipif(not LIBRARY.is_file(), reason="the Rust library has not been built here")
def test_the_five_new_trainer_flags_default_to_the_trainers_own_defaults(tmp_path: Path) -> None:
    """Named on neither the launcher's command line nor the job config, the job must still ask
    the trainer for exactly its own defaults -- not zero, not `None`, not some other placeholder."""

    trainer = _trainer()
    _, payload_dir, _ = _prepare(tmp_path)
    config = json.loads((payload_dir / "yt_run_config.json").read_text())

    parsed = trainer.build_parser().parse_args(config["trainer_args"])
    assert parsed.gamma == pytest.approx(0.997)
    assert parsed.wood_shaping == pytest.approx(0.5)
    assert parsed.end_wood == pytest.approx(3.5)
    assert parsed.critic_warmup_updates == 0
    assert parsed.actor_lr_scale == pytest.approx(1.0)


@pytest.mark.skipif(not LIBRARY.is_file(), reason="the Rust library has not been built here")
def test_hours_become_a_conservative_batch_aligned_budget(tmp_path: Path) -> None:
    trainer = _trainer()
    _, payload_dir, manifest = _prepare(tmp_path, "--hours", "6")
    budget = manifest["budget"]
    assert budget["source"] == "--hours"
    assert budget["total_turn_steps"] % budget["batch_size"] == 0
    # 64 cores, 2,500 decisions a second per 16 cores, then the 0.8 safety factor
    assert budget["assumed_decisions_per_second"] == pytest.approx(8000.0)
    assert budget["total_turn_steps"] <= 6 * 3600 * 8000

    config = json.loads((payload_dir / "yt_run_config.json").read_text())
    parsed = trainer.build_parser().parse_args(config["trainer_args"])
    assert parsed.total_turn_steps == budget["total_turn_steps"]


@pytest.mark.skipif(not LIBRARY.is_file(), reason="the Rust library has not been built here")
def test_an_explicit_step_budget_overrides_hours(tmp_path: Path) -> None:
    _, _, manifest = _prepare(tmp_path, "--hours", "6", "--total-turn-steps", "1234000")
    assert manifest["budget"]["source"] == "--total-turn-steps"
    assert manifest["budget"]["total_turn_steps"] == 1234000


def test_the_hours_estimate_scales_with_the_cores_and_stays_under_the_raw_rate() -> None:
    small = launcher.total_turn_steps_for_hours(1.0, 16, batch_size=4096)
    large = launcher.total_turn_steps_for_hours(1.0, 64, batch_size=4096)
    assert large > 3.5 * small  # four times the cores, minus the batch rounding
    assert small < 3600 * 2500  # the safety factor keeps it below the raw placeholder rate


# --------------------------------------------------------------------------- the specification


def test_start_refuses_to_run_without_a_cpu_pool() -> None:
    parser = launcher.build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["start", "--run-name", "x"])
    parsed = parser.parse_args(
        ["start", "--run-name", "x", "--pool-tree", "tree", "--pool", "pool"]
    )
    assert parsed.cpu_limit == 64
    assert parsed.memory_limit == 64 * 1024**3


def test_memory_sizes_are_read_in_human_units() -> None:
    assert launcher.parse_size("64GiB") == 64 * 1024**3
    assert launcher.parse_size("64G") == 64 * 1024**3
    assert launcher.parse_size("68719476736") == 64 * 1024**3


@pytest.mark.skipif(not LIBRARY.is_file(), reason="the Rust library has not been built here")
def test_the_specification_asks_for_cores_and_never_for_a_gpu(tmp_path: Path) -> None:
    pytest.importorskip("yt.wrapper", reason="the spec builder needs the system python3")
    args, _, _ = _prepare(tmp_path, "--pool-tree", "cpu_tree", "--pool", "cpu_pool")
    args.job_time_limit_ms = 3600 * 1000
    preview = launcher.spec_preview(args, launcher.run_paths(args.root, args.run_name))
    task = preview["tasks"]["train"]

    assert "gpu_limit" not in task
    assert task["cpu_limit"] == 64
    assert task["memory_limit"] == 64 * 1024**3
    assert task["command"] == "python3 yt_ppo_entrypoint.py"
    assert task["layer_paths"] == list(launcher.DEFAULT_LAYERS)
    assert task["environment"]["RAYON_NUM_THREADS"] == "64"
    assert task["environment"]["TROLL_FARM_CPU_LIMIT"] == "64"
    assert task["environment"]["YT_ALLOW_HTTP_REQUESTS_TO_YT_FROM_JOB"] == "1"
    assert preview["pool"] == "cpu_pool"
    assert preview["pool_trees"] == ["cpu_tree"]
    names = [row["file_name"] for row in task["file_paths_named"]]
    assert names == [*launcher.REQUIRED_UPLOADS, "runtime_wheelhouse.tar.gz"]
    assert any("wheelhouse_torch241_cu121_py310" in path for path in task["file_paths"])


@pytest.mark.skipif(not LIBRARY.is_file(), reason="the Rust library has not been built here")
def test_prepare_dry_run_can_preview_a_reserved_gpu_slot(tmp_path: Path) -> None:
    """`prepare --dry-run --gpu-limit 1` must show the same GPU-slot spec `start` would submit --
    that offline preview is the whole point of adding `--gpu-limit` to `prepare` as well."""

    pytest.importorskip("yt.wrapper", reason="the spec builder needs the system python3")
    args, _, _ = _prepare(
        tmp_path, "--pool-tree", "gpu_tree", "--pool", "gpu_pool", "--gpu-limit", "1"
    )
    assert args.gpu_limit == 1
    args.job_time_limit_ms = 3600 * 1000
    preview = launcher.spec_preview(args, launcher.run_paths(args.root, args.run_name))
    task = preview["tasks"]["train"]

    assert task["gpu_limit"] == 1
    # the reservation must not disturb the pool/tree the coordinator chose...
    assert preview["pool"] == "gpu_pool"
    assert preview["pool_trees"] == ["gpu_tree"]
    # ...nor the fact that training itself still runs on the CPU...
    assert task["environment"]["CUDA_VISIBLE_DEVICES"] == ""
    # ...and the title must say plainly that the GPU is reserved, not used.
    assert preview["title"] == "Troll Farm self-play PPO (CPU on a GPU slot x1) test-run"


def test_gpu_limit_rejects_negative_values() -> None:
    """A negative `--gpu-limit` is not a smaller reservation, it is nonsense: `gpu_limit > 0`
    would silently see it as "no GPU" while the title still called it a GPU slot. Both
    subcommands must refuse it outright, at argument-parsing time."""

    parser = launcher.build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["prepare", "--gpu-limit", "-1"])
    with pytest.raises(SystemExit):
        parser.parse_args(
            ["start", "--run-name", "x", "--pool-tree", "tree", "--pool", "pool",
             "--gpu-limit", "-1"]
        )


# --------------------------------------------------------------------------- the job's entrypoint


def test_heartbeat_reads_the_latest_update_out_of_the_training_log(tmp_path: Path) -> None:
    train_log = tmp_path / "train.log"
    train_log.write_text(
        "\n".join(
            [
                'not json at all',
                json.dumps({"event": "start", "run_name": "x"}, sort_keys=True),
                json.dumps({"event": "update", "update": 1, "turn_steps": 4096}, sort_keys=True),
                json.dumps(
                    {"event": "update", "update": 2, "turn_steps": 8192, "win_rate": 0.5},
                    sort_keys=True,
                ),
                "{ truncated line that never fini",
            ]
        )
        + "\n"
    )
    latest = entrypoint._tail_update(train_log)
    assert latest is not None
    assert latest["update"] == 2
    assert latest["win_rate"] == 0.5
    assert entrypoint._tail_update(tmp_path / "absent.log") is None


@pytest.mark.skipif(not LIBRARY.is_file(), reason="the Rust library has not been built here")
def test_the_entrypoint_finds_and_loads_the_library_at_the_default_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, payload_dir, _ = _prepare(tmp_path)
    extracted = tmp_path / "extracted-lib"
    with tarfile.open(payload_dir / "troll_farm_payload.tar.gz") as archive:
        archive.extractall(extracted)
    monkeypatch.setattr(entrypoint, "LOG_PATH", tmp_path / "outputs" / "yt_job.log")

    report = entrypoint.check_library(extracted)
    assert Path(report["path"]) == extracted / entrypoint.LIBRARY_RELATIVE
    # The library answers, which means the container's C library is new enough for it.
    assert report["plan_vocabulary"]

    with pytest.raises(FileNotFoundError):
        entrypoint.check_library(tmp_path / "nowhere")


def test_cypress_layout_matches_julys() -> None:
    paths = launcher.run_paths(launcher.DEFAULT_YT_ROOT, "ppo-a")
    assert paths["run"].endswith("/runs/ppo-a")
    assert paths["inputs"].endswith("/runs/ppo-a/inputs")
    assert paths["output"].endswith("/outputs/troll_farm_output.tar.gz")
    assert paths["log"].endswith("/logs/yt_job.log")
