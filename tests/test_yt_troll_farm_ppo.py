from pathlib import Path

from cgauto.yt_troll_farm_ppo import (
    DEFAULT_FINAL_PAYLOAD_DIR,
    DEFAULT_FINAL_RUN_NAME,
    DEFAULT_YT_ROOT,
    WEIGHTS_RELATIVE,
    benchmark_trainer_args,
    final_trainer_args,
    run_paths,
)


def test_benchmark_arguments_freeze_d11_schedule_and_only_vary_backend() -> None:
    local = benchmark_trainer_args(
        run_name="local", device="cpu", initial_weights="weights.npz"
    )
    remote = benchmark_trainer_args(
        run_name="remote", device="cuda", initial_weights="weights.npz"
    )
    assert local[local.index("--model-seed") + 1] == "137"
    assert local[local.index("--train-seed-base") + 1] == "7200000"
    assert local[local.index("--total-transitions") + 1] == "1000000"
    assert local[local.index("--stage-a-transitions") + 1] == "1000000"
    assert local[local.index("--teacher-aux-coef") + 1] == "0.10"
    assert local[local.index("--gate-profile") + 1] == "level5"
    assert local[local.index("--device") + 1] == "cpu"
    assert remote[remote.index("--device") + 1] == "cuda"

    normalized_local = [
        "RUN" if value == "local" else "DEVICE" if value == "cpu" else value
        for value in local
    ]
    normalized_remote = [
        "RUN" if value == "remote" else "DEVICE" if value == "cuda" else value
        for value in remote
    ]
    assert normalized_local == normalized_remote


def test_dedicated_yt_paths_do_not_use_math_project_namespace() -> None:
    paths = run_paths(DEFAULT_YT_ROOT, "benchmark")
    assert DEFAULT_YT_ROOT == "//home/delivery_ml/research/tarstars/troll_farm"
    assert "math_through_eml" not in paths["run"]
    assert paths["output"].endswith("/outputs/troll_farm_output.tar.gz")
    assert WEIGHTS_RELATIVE == Path(
        "data/analysis/live-agent-6553250/"
        "curriculum-level5-seed-reacquisition-d11-bc-weights.npz"
    )


def test_final_arguments_only_change_preregistered_seed_and_schedule() -> None:
    benchmark = benchmark_trainer_args(
        run_name="benchmark", device="cuda", initial_weights="weights.npz"
    )
    final = final_trainer_args(
        run_name="final", device="cuda", initial_weights="weights.npz"
    )
    expected_changes = {
        "--run-name": ("benchmark", "final"),
        "--model-seed": ("137", "139"),
        "--train-seed-base": ("7200000", "7400000"),
        "--total-transitions": ("1000000", "4000000"),
    }
    assert len(benchmark) == len(final)
    for index, (before, after) in enumerate(zip(benchmark, final)):
        if before == after:
            continue
        assert index > 0
        assert benchmark[index - 1] in expected_changes
        assert expected_changes[benchmark[index - 1]] == (before, after)
    assert final[final.index("--stage-a-transitions") + 1] == "1000000"
    assert DEFAULT_FINAL_PAYLOAD_DIR.name == "d11-ppo-final-seed139"
    assert DEFAULT_FINAL_RUN_NAME == "d11-ppo-final-seed139-20260720"
