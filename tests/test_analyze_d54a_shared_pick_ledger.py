from cgauto.analyze_d54a_shared_pick_ledger import CONFIGS, MODELS


def test_frozen_v5_catalog_crosses_eight_configs_without_pruning():
    assert len(MODELS) == 8
    assert len(set(MODELS)) == 8
    assert all(label.startswith("legend_v5_") for label in MODELS)
    assert {config["first_name"] for config in CONFIGS.values()} == {
        "hp2",
        "balanced",
    }
    assert {config["max_workers"] for config in CONFIGS.values()} == {3, 4}
    assert {config["post_producers"] for config in CONFIGS.values()} == {1, 2}
