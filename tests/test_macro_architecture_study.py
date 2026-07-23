from cgauto.macro_architecture_study import merge_with_live, training_activation


def test_merge_reuses_matching_live_controls_and_attaches_deltas() -> None:
    control = {
        "rows": [
            {
                "seed": 1,
                "policy": "live",
                "opponent": "race",
                "paired_margin": 4,
                "paired_wood_edge": 2,
            }
        ]
    }
    candidate = [
        {
            "seed": 1,
            "policy": "hybrid_macro",
            "opponent": "race",
            "paired_margin": 7,
            "paired_wood_edge": 1,
        }
    ]

    rows = merge_with_live(control, candidate)

    hybrid = next(row for row in rows if row["policy"] == "hybrid_macro")
    assert hybrid["delta_vs_live_margin"] == 3
    assert hybrid["delta_vs_live_wood"] == -1


def test_training_activation_compares_candidate_to_live_per_cell() -> None:
    rows = [
        {"seed": 1, "opponent": "race", "policy": "live", "policy_command_counts": {"TRAIN": 2}},
        {"seed": 1, "opponent": "race", "policy": "hybrid_macro", "policy_command_counts": {"TRAIN": 4}},
        {"seed": 2, "opponent": "race", "policy": "live", "policy_command_counts": {"TRAIN": 2}},
        {"seed": 2, "opponent": "race", "policy": "hybrid_macro", "policy_command_counts": {"TRAIN": 2}},
    ]

    result = training_activation(rows)

    assert result["paired_cell_train_count_distribution"] == {"2": 1, "4": 1}
    assert result["paired_cells_above_live_train_count"] == 1
    assert result["paired_cells_above_live_rate"] == 0.5
    assert result["extra_train_commands"] == 2
    assert result["activated"] is True
