from cgauto.analyze_d50a_phase_population import (
    MODELS,
    activation_gates,
    support_gates,
)


def test_frozen_model_labels_are_unique_and_complete():
    assert len(MODELS) == 120
    assert len(set(MODELS)) == 120
    assert sum(label.startswith("d50_anchor_") for label in MODELS) == 8
    assert sum(label.startswith("d50_t100_") for label in MODELS) == 56
    assert sum(label.startswith("d50_t150_") for label in MODELS) == 56


def test_activation_gates_hold_the_frozen_boundaries():
    passing = activation_gates(
        repeat_exact=True,
        grid_exact=True,
        anchors_exact=True,
        openings_exact=True,
        changed_cells=7_168,
        active_policies=80,
    )
    assert all(passing.values())
    assert not activation_gates(
        repeat_exact=True,
        grid_exact=True,
        anchors_exact=True,
        openings_exact=True,
        changed_cells=7_167,
        active_policies=80,
    )["at_least_40_percent_switch_cells_active"]
    assert not activation_gates(
        repeat_exact=True,
        grid_exact=True,
        anchors_exact=True,
        openings_exact=True,
        changed_cells=7_168,
        active_policies=79,
    )["at_least_80_switch_policies_active_on_10_percent_maps"]


def test_support_gates_are_conjunctive():
    support = {
        "confirmation": {
            "overall": {
                "augmented": {"macro": 56, "full": 36},
                "increment": {"macro": 5, "full": 3},
            },
            "catastrophic": {
                "augmented": {"macro": 7},
                "increment": {"macro": 3},
            },
            "worker_rich": {
                "augmented": {"macro": 12},
                "increment": {"macro": 4},
            },
            "rich_immediate": {
                "augmented": {"macro": 4, "full": 1},
                "increment": {"macro": 2, "full": 1},
            },
        }
    }
    assert all(support_gates(support, True).values())
    support["confirmation"]["rich_immediate"]["augmented"]["full"] = 0
    gates = support_gates(support, True)
    assert not gates["rich_full_at_least_1_of_9"]
    assert not all(gates.values())
