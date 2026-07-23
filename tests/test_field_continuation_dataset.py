from cgauto.field_continuation_dataset import actual_signature


def snapshot(workers: int) -> dict:
    return {
        "score": 10,
        "fruit": 2,
        "wood": 2,
        "workers": workers,
        "successful_plants": 3,
        "harvested_fruit": 4,
        "chops_landed": 5,
        "dropped_items": 6,
    }


def test_actual_signature_requires_and_extracts_frozen_checkpoints() -> None:
    row = {
        "game_id": 7,
        "turns": 140,
        "final": {"opponent": snapshot(3)},
        "timeline": {
            "50": {"opponent": snapshot(1)},
            "100": {"opponent": snapshot(2)},
        },
    }
    result = actual_signature(row)
    assert result["turns"] == 140
    assert result["checkpoints"]["50"]["workers"] == 1
    assert result["checkpoints"]["100"]["workers"] == 2
    assert result["final"]["workers"] == 3
