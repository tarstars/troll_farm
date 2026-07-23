from cgauto.field_continuation_coverage import analyze, FEATURES, MODELS


def snapshot(workers: int = 2) -> dict:
    return {
        "score": 100,
        "fruit": 4,
        "wood": 24,
        "workers": workers,
        "successful_plants": 20,
        "harvested_fruit": 30,
        "chops_landed": 70,
        "dropped_items": 40,
    }


def observed() -> dict:
    return {
        "records": [
            {
                "game_id": game_id,
                "opponent": "field-opponent",
                "opponent_starter_id": 1,
                "actual_first_command": "MOVE 1 2 2",
                "margin": -120 if game_id < 32 else 5,
                "catastrophic": game_id < 32,
                "worker_rich": game_id % 2 == 0,
                "actual": {
                    "turns": 150,
                    "checkpoints": {"50": snapshot(), "100": snapshot()},
                    "final": snapshot(3 if game_id % 2 == 0 else 2),
                },
            }
            for game_id in range(160)
        ]
    }


def local_rows(offset: int = 0) -> list[dict]:
    rows = []
    data = observed()
    for record in data["records"]:
        for model in MODELS:
            row = {
                "game_id": record["game_id"],
                "model": model,
                "first_commands": "MOVE 1 2 2",
                "terminal_turn": 150,
            }
            for checkpoint, prefix in (("50", "t50"), ("100", "t100"), ("final", "final")):
                actual = (
                    record["actual"]["final"]
                    if checkpoint == "final"
                    else record["actual"]["checkpoints"][checkpoint]
                )
                mapping = {
                    "score": "score",
                    "fruit": "fruit",
                    "wood": "wood",
                    "workers": "workers",
                    "plants": "successful_plants",
                    "harvested_fruit": "harvested_fruit",
                    "chops": "chops_landed",
                    "dropped_items": "dropped_items",
                }
                for feature in FEATURES:
                    row[f"{prefix}_{feature}"] = actual[mapping[feature]] + offset
            rows.append(row)
    return rows


def test_analyze_passes_exactly_covered_field() -> None:
    report = analyze(observed(), local_rows())
    assert report["games"] == 160
    assert report["model_cells"] == 1280
    assert report["coverage"]["overall"]["fully_supported"] == 160
    assert report["zoo_adequate"] is True


def test_analyze_rejects_uncovered_field() -> None:
    report = analyze(observed(), local_rows(offset=1000))
    assert report["coverage"]["overall"]["fully_supported"] == 0
    assert report["zoo_adequate"] is False
    assert report["missing_archetypes"]
