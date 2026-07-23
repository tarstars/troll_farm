from cgauto.field_continuation_coverage import FEATURES
from cgauto.field_economy_catalog_calibration import CATALOG, STRUCTURAL_CATALOG, analyze


MAPPING = {
    "score": "score",
    "fruit": "fruit",
    "wood": "wood",
    "workers": "workers",
    "plants": "successful_plants",
    "harvested_fruit": "harvested_fruit",
    "chops": "chops_landed",
    "dropped_items": "dropped_items",
}


def snapshot(kind: int) -> dict:
    return {
        "score": 300 if kind == 0 else 160,
        "fruit": 10,
        "wood": 70 if kind == 0 else 35,
        "workers": 3 if kind == 0 else 2,
        "successful_plants": 30 if kind != 2 else 10,
        "harvested_fruit": 60,
        "chops_landed": 90,
        "dropped_items": 80,
    }


def observed() -> dict:
    records = []
    for game_id in range(1000, 1160):
        kind = game_id % 3
        command = "MOVE 1 2 2"
        if kind == 0:
            command = "TRAIN 2 2 2 1;MOVE 1 2 2"
        records.append(
            {
                "game_id": game_id,
                "opponent": "field-opponent",
                "opponent_starter_id": 1,
                "actual_first_command": command,
                "margin": -120 if game_id % 4 == 0 else 5,
                "catastrophic": game_id % 4 == 0,
                "worker_rich": kind == 0,
                "actual": {
                    "turns": 150,
                    "checkpoints": {"50": snapshot(kind), "100": snapshot(kind)},
                    "final": snapshot(kind),
                },
            }
        )
    return {"records": records}


def baseline() -> dict:
    return {
        "game_rows": [
            {
                "game_id": record["game_id"],
                "macro_supported": False,
                "fully_supported": False,
                "exact_opening_supported": False,
            }
            for record in observed()["records"]
        ]
    }


def local_rows(offset: int = 0, catalog: tuple[str, ...] = CATALOG) -> list[dict]:
    rows = []
    for record in observed()["records"]:
        for model in catalog:
            row = {
                "game_id": record["game_id"],
                "model": model,
                "first_commands": record["actual_first_command"],
                "terminal_turn": 150,
            }
            for checkpoint, prefix in (
                ("50", "t50"),
                ("100", "t100"),
                ("final", "final"),
            ):
                actual = (
                    record["actual"]["final"]
                    if checkpoint == "final"
                    else record["actual"]["checkpoints"][checkpoint]
                )
                for feature in FEATURES:
                    row[f"{prefix}_{feature}"] = actual[MAPPING[feature]] + offset
            rows.append(row)
    return rows


def test_exact_catalog_passes_frozen_calibration_gates() -> None:
    report = analyze(observed(), baseline(), local_rows())
    assert report["model_cells"] == 4960
    assert 1 <= len(report["selected_models"]) <= 3
    assert report["macro_viable"] is True
    assert report["catalog_useful"] is True


def test_distant_catalog_fails_macro_calibration() -> None:
    report = analyze(observed(), baseline(), local_rows(offset=1000))
    assert report["macro_viable"] is False
    assert report["catalog_useful"] is False


def test_structural_catalog_uses_its_frozen_grid() -> None:
    report = analyze(
        observed(),
        baseline(),
        local_rows(catalog=STRUCTURAL_CATALOG),
        STRUCTURAL_CATALOG,
    )
    assert report["model_cells"] == 1760
    assert report["catalog_useful"] is True
