import csv
import json

from cgauto.local_model_rollout_transfer import (
    EXPECTED_MODELS,
    choose,
    evaluate_selector,
    grid_rows,
    league_outcomes,
    protocol_record,
    read_rollouts,
)
from sim.state import from_ascii


def test_protocol_record_preserves_exact_static_and_turn_one_state() -> None:
    game = from_ascii(["0.+", ".~1"], talents=(1, 1, 1, 1))
    game.inventories = [[2, 3, 4, 5, 6, 0], [7, 8, 9, 10, 11, 0]]

    assert grid_rows(game) == ["0.+", ".~1"]
    record = protocol_record(17, game)

    assert record.startswith(
        "SEED 17\n3 2\n0.+\n.~1\n2 3 4 5 6 0\n7 8 9 10 11 0\n"
    )
    assert record.endswith("2\n0 0 0 0 1 1 1 1 0 0 0 0 0 0\n1 1 2 1 1 1 1 1 0 0 0 0 0 0\n")


def test_league_outcomes_keeps_both_seat_deltas(tmp_path) -> None:
    payload = {
        "opponents": {"alpha": {}, "motion": {}},
        "rows": [
            {
                "seed": 3,
                "opponent": "alpha",
                "policy": "live",
                "seat_margins": [10, 20],
            },
            {
                "seed": 3,
                "opponent": "alpha",
                "policy": "adaptivehp0",
                "seat_margins": [15, 17],
            },
        ],
    }
    path = tmp_path / "league.json"
    path.write_text(json.dumps(payload))

    seeds, opponents, outcomes = league_outcomes(
        [path], "adaptivehp0", {"motion"}
    )

    assert seeds == [3]
    assert opponents == ("alpha",)
    assert outcomes[(3, 0)] == {"alpha": 5}
    assert outcomes[(3, 1)] == {"alpha": -3}


def test_unanimous_selector_rejects_one_local_model_disagreement() -> None:
    positive = {model: 2.0 for model in EXPECTED_MODELS}
    mixed = dict(positive, mybot=-1.0)

    assert choose(positive, "unanimous-positive", 0)
    assert not choose(mixed, "unanimous-positive", 0)
    assert choose(mixed, "positive-mean", 0)


def test_selector_reports_seed_clustered_actual_outcomes() -> None:
    seeds = [1, 2]
    opponents = ("alpha", "beta")
    outcomes = {
        (1, 0): {"alpha": 8, "beta": 4},
        (1, 1): {"alpha": 4, "beta": 0},
        (2, 0): {"alpha": -8, "beta": -4},
        (2, 1): {"alpha": 20, "beta": 20},
    }
    rollouts = {
        key: {model: (1 if key == (1, 0) else -1) for model in EXPECTED_MODELS}
        for key in outcomes
    }

    result = evaluate_selector(
        seeds,
        opponents,
        outcomes,
        rollouts,
        "unanimous-positive",
    )

    assert result["selected_cell_count"] == 1
    assert result["selected_seed_count"] == 1
    assert result["seed_clustered_summary"]["mean"] == 1.5
    assert result["worst_opponent_mean"] == 1


def test_read_rollouts_requires_complete_model_rows(tmp_path) -> None:
    path = tmp_path / "rollouts.tsv"
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t")
        writer.writerow(
            [
                "seed",
                "seat",
                "model",
                "control_margin",
                "option_margin",
                "delta",
                "elapsed_us",
            ]
        )
        for model in EXPECTED_MODELS:
            writer.writerow([4, 0, model, 10, 12, 2, 100])

    assert read_rollouts(path)[(4, 0)] == {
        model: 2.0 for model in EXPECTED_MODELS
    }
