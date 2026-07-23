"""Tests for D63a agent-held workforce-transition modeling."""

from __future__ import annotations

from cgauto.analyze_d63a_workforce_transition import (
    agent_bucket,
    agent_partition,
    gate_model_a,
    gate_model_b,
    materialize_features,
    model_report,
)


def agents(partition: str, count: int) -> list[int]:
    result = []
    candidate = 1
    while len(result) < count:
        if agent_partition(candidate) == partition:
            result.append(candidate)
        candidate += 1
    return result


def test_agent_partition_is_stable_and_policy_held() -> None:
    agent_id = 6_479_768
    assert agent_bucket(agent_id) == agent_bucket(agent_id)
    assert agent_partition(agent_id) in {"discovery", "validation"}
    assert len({agent_partition(agent_id) for _ in range(10)}) == 1


def test_missing_numeric_feature_gets_fixed_sentinel_and_indicator() -> None:
    names, matrix = materialize_features(
        [
            {"features": {"distance": 3.0, "constant": True}},
            {"features": {"distance": None, "constant": True}},
        ],
        "features",
    )

    assert names == ["constant", "distance", "distance__missing"]
    assert matrix.tolist() == [[1.0, 3.0, 0.0], [1.0, -1.0, 1.0]]


def test_fixed_logistic_model_transfers_across_held_agents_and_passes_gates() -> None:
    rows = []
    for partition in ("discovery", "validation"):
        for agent_id in agents(partition, 4):
            for occurrence in range(10):
                label = occurrence % 2
                rows.append(
                    {
                        "game_id": agent_id * 100 + occurrence,
                        "agent_id": agent_id,
                        "partition": partition,
                        "label": label,
                        "features": {
                            "signal": 10.0 if label else -10.0,
                            "nuisance": float((agent_id + occurrence) % 3),
                        },
                    }
                )

    report = model_report(rows, "features", "label", "fixture")

    assert report["fit"]["converged"]
    assert report["validation"]["roc_auc"] == 1.0
    assert report["validation"]["balanced_accuracy_at_0_5"] == 1.0
    assert gate_model_a(report)["status"] == "pass"
    assert gate_model_b(report)["status"] == "pass"

