from cgauto.analyze_d79a_spatial_job_population import (
    gate_report,
    oracle_metrics,
    population_metrics,
    summarize_policy,
    task_key,
)


def make_row(
    policy: str,
    task: int,
    margin: int,
    workers: int = 3,
    crop: int = 1,
    changed: bool = True,
) -> dict[str, str]:
    return {
        "map_seed": str(task),
        "seat": "0",
        "opponent": "opponent",
        "policy": policy,
        "margin": str(margin),
        "own_score": str(100 + margin),
        "opponent_score": "100",
        "own_workers": str(workers),
        "own_created_crops": str(crop),
        "action_hash": f"{policy}-{task}" if changed else f"zero-{task}",
        "rate_decisions": "20",
        "rate_overrides": "5",
        "selected_prior_rank_sum": "7",
        "selected_prior_rank_max": "2",
        "near_opponent_targets": "1",
        "bank": "1",
        "fell_bank": "1",
        "harvest_bank": "1",
        "renew": "0",
        "mine_bank": "0",
    }


def test_summarize_and_population_metrics_apply_frozen_thresholds() -> None:
    zero_rows = [make_row("zero", task, 10, changed=False) for task in range(10)]
    zero = {task_key(row): row for row in zero_rows}
    summaries = {"zero": summarize_policy(zero_rows, zero)}
    for index in range(32):
        rows = [make_row(f"random_{index:02d}", task, index - 10) for task in range(10)]
        summaries[f"random_{index:02d}"] = summarize_policy(rows, zero)
        summaries[f"random_{index:02d}"]["rate_overrides"] = 128
    metrics = population_metrics(summaries)
    assert metrics["random_mean_margin_span"] == 31
    assert metrics["random_means_above_zero"] == 11
    assert metrics["random_means_below_zero"] == 20
    assert len(metrics["active_action_hash_policies"]) == 0
    assert len(metrics["active_override_and_plane_policies"]) == 32
    assert len(metrics["crop_safe_policies"]) == 32


def test_oracle_uses_only_crop_and_worker_safe_arms() -> None:
    zero = [make_row("zero", 1, 0), make_row("zero", 2, 0)]
    unsafe_crop = [make_row("unsafe_crop", 1, 100, crop=0), make_row("unsafe_crop", 2, 100, crop=0)]
    unsafe_workers = [
        make_row("unsafe_workers", 1, 90, workers=1),
        make_row("unsafe_workers", 2, 90, workers=1),
    ]
    safe = [make_row("safe", 1, 30), make_row("safe", 2, 10)]
    actual = oracle_metrics(
        {
            "zero": zero,
            "unsafe_crop": unsafe_crop,
            "unsafe_workers": unsafe_workers,
            "safe": safe,
        }
    )
    assert actual["mean_margin_gain"] == 20
    assert actual["strict_improvement_rate"] == 1
    assert actual["selected_policy_counts"] == {"safe": 2}


def test_gate_report_orders_failure_adjudication() -> None:
    surface = {
        "active_action_hash_policies": [str(index) for index in range(24)],
        "active_override_and_plane_policies": [str(index) for index in range(24)],
        "active_near_opponent_policies": [str(index) for index in range(24)],
        "crop_safe_policies": [str(index) for index in range(24)],
        "worker_three_safe_policies": [str(index) for index in range(24)],
        "random_mean_margin_span": 30,
        "random_means_above_zero": 1,
        "random_means_below_zero": 1,
    }
    oracle = {
        "mean_margin_gain": 20,
        "strict_improvement_rate": 0.5,
        "mean_own_score_delta": 0,
        "mean_opponent_score_delta": 1,
        "opponent_mean_margin_gains": {f"o{index}": 1 for index in range(8)},
    }
    integrity = {
        "complete_repeats": True,
        "population_reconstruction_mismatches": 0,
        "zero_parity_failures": 0,
        "mechanics_and_numeric_failures": 0,
        "telemetry_consistency_failures": 0,
    }
    *_, decision = gate_report(surface, oracle, integrity)
    assert decision == "pass_freeze_interface_open_d80"
    integrity["zero_parity_failures"] = 1
    *_, decision = gate_report(surface, oracle, integrity)
    assert decision == "integrity_failure"
