import pytest

from cgauto.replay_conditioned_continuation import (
    ACTION_VERBS,
    MAP_FEATURES,
    TARGET_FIELDS,
    analyze,
    build_examples,
)


def fixtures() -> tuple[dict, dict]:
    scheduler_rows = []
    census_rows = []
    for index in range(21):
        game_id = 9000 + index
        partition = "discovery" if index < 12 else "confirmation"
        signal = index % 3
        base = {field: 10 for field in TARGET_FIELDS}
        recent50 = {field: signal * 2 for field in TARGET_FIELDS}
        future50 = {field: signal * 2 for field in TARGET_FIELDS}
        recent100 = {field: signal * 3 for field in TARGET_FIELDS}
        future100 = {field: signal * 3 for field in TARGET_FIELDS}
        phase50 = {verb: signal * 5 for verb in ACTION_VERBS}
        phase100 = {verb: signal * 7 for verb in ACTION_VERBS}
        scheduler_rows.append(
            {
                "game_id": game_id,
                "opponent": f"opponent-{index}",
                "partition": partition,
                "has_iron": True,
                "training_events": [
                    {"ordinal": 1, "turn": 1, "spec": [signal + 1, 2, 1, 1]}
                ],
                "snapshots": {"50": base, "100": base},
                "intervals": [
                    {"start_turn": 1, "end_turn": 50, "increments": recent50},
                    {"start_turn": 51, "end_turn": 100, "increments": future50},
                    {"start_turn": 101, "end_turn": 150, "increments": future100},
                ],
                "scheduler": {
                    "phase_actions": {"001-050": phase50, "051-100": phase100}
                },
            }
        )
        opening = {name: 1 for name in MAP_FEATURES}
        census_rows.append({"game_id": game_id, "opening": opening})
    return {"rows": scheduler_rows}, {"rows": census_rows}


def test_predictive_history_passes_frozen_gates() -> None:
    scheduler, census = fixtures()
    report = analyze(scheduler, census)
    assert report["games"] == 21
    assert report["examples"] == 42
    assert report["passed"] is True
    assert all(report["gates"].values())
    assert set(report["selected_k"]) == {"map", "state", "history"}


def test_feature_blocks_do_not_expose_identity_or_future() -> None:
    scheduler, census = fixtures()
    examples = build_examples(scheduler, census)
    assert len(examples) == 42
    for example in examples:
        feature_names = set().union(*example["features"].values())
        assert not any("opponent" in name or "future" in name for name in feature_names)
        assert all(isinstance(value, float) for block in example["features"].values() for value in block.values())


def test_missing_required_interval_is_rejected() -> None:
    scheduler, census = fixtures()
    scheduler["rows"][0]["intervals"].pop()
    with pytest.raises(ValueError, match="intervals for 101-150"):
        build_examples(scheduler, census)

