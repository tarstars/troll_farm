from cgauto.field_continuation_coverage import FEATURES
from cgauto.legend_field_proxy_calibration import CATALOG, V2_CATALOG, analyze


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


def snapshot() -> dict:
    return {
        "score": 400,
        "fruit": 30,
        "wood": 90,
        "workers": 4,
        "successful_plants": 50,
        "harvested_fruit": 120,
        "chops_landed": 110,
        "dropped_items": 200,
    }


def observed() -> dict:
    return {
        "records": [
            {
                "game_id": game_id,
                "opponent": "rich-field",
                "opponent_starter_id": 1,
                "actual_first_command": "TRAIN 2 2 2 1;MOVE 1 2 2",
                "margin": -120 if game_id % 4 == 0 else 5,
                "catastrophic": game_id % 4 == 0,
                "worker_rich": True,
                "actual": {
                    "turns": 150,
                    "checkpoints": {"50": snapshot(), "100": snapshot()},
                    "final": snapshot(),
                },
            }
            for game_id in range(2000, 2160)
        ]
    }


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


def test_exact_proxy_passes_all_held_out_gates() -> None:
    report = analyze(observed(), baseline(), local_rows())
    assert report["model_cells"] == 1280
    assert report["passed"] is True


def test_distant_proxy_fails_held_out_gates() -> None:
    report = analyze(observed(), baseline(), local_rows(offset=1000))
    assert report["passed"] is False


def test_exact_v2_proxy_uses_its_frozen_catalog() -> None:
    report = analyze(
        observed(),
        baseline(),
        local_rows(catalog=V2_CATALOG),
        V2_CATALOG,
        "v2",
    )
    assert report["model_cells"] == 1280
    assert report["passed"] is True
    assert len(report["rich_game_nearest"]) == 160
    assert all(row["macro_covers"] for row in report["rich_game_nearest"])
    assert set(report["rich_catalog_summary"]) == set(V2_CATALOG)
