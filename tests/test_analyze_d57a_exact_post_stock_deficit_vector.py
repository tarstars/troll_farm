from cgauto.analyze_d57a_exact_post_stock_deficit_vector import (
    CONFIGS,
    MODELS,
    workforce_transition_summary,
)


def test_frozen_v7_catalog_crosses_eight_configs_without_pruning():
    assert len(MODELS) == 8
    assert len(set(MODELS)) == 8
    assert all(label.startswith("legend_v7_") for label in MODELS)
    assert {config["first_name"] for config in CONFIGS.values()} == {
        "hp2",
        "balanced",
    }
    assert {config["max_workers"] for config in CONFIGS.values()} == {3, 4}
    assert {config["post_producers"] for config in CONFIGS.values()} == {1, 2}


def test_workforce_transition_summary_preserves_promotions_and_demotions():
    summary = workforce_transition_summary([(2, 3), (3, 3), (4, 2)])
    assert summary["transitions"] == {"2_to_3": 1, "3_to_3": 1, "4_to_2": 1}
    assert summary["promoted_cells"] == 1
    assert summary["unchanged_cells"] == 1
    assert summary["demoted_cells"] == 1
    assert summary["net_worker_delta"] == -1
