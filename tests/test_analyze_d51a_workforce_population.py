from cgauto.analyze_d51a_workforce_population import (
    MODELS,
    mechanical_gates,
    support_gates,
    trigger_is_valid,
)


def test_frozen_catalog_has_8_anchors_and_56_switches():
    assert len(MODELS) == 64
    assert len(set(MODELS)) == 64
    assert sum(label.startswith("d51_anchor_") for label in MODELS) == 8


def test_trigger_validation_uses_workforce_history():
    base = {"third_worker_turn": 80, "switch_score": 55, "terminal_turn": 300}
    assert trigger_is_valid(
        {"trigger": "w3_now"}, {**base, "switch_turn": 80}
    )
    assert trigger_is_valid(
        {"trigger": "w3_plus25"}, {**base, "switch_turn": 105}
    )
    assert trigger_is_valid(
        {"trigger": "w3_plus50"}, {**base, "switch_turn": 130}
    )
    assert trigger_is_valid(
        {"trigger": "w3_score60"},
        {**base, "switch_turn": 120, "switch_score": 60},
    )
    assert not trigger_is_valid(
        {"trigger": "w3_plus25"}, {**base, "switch_turn": 106}
    )


def test_mechanical_gates_hold_exact_boundaries():
    gates = mechanical_gates(
        repeat_exact=True,
        anchors_exact=True,
        openings_exact=True,
        trigger_failures=0,
        triggered_policies=45,
        changed_cells=3_136,
    )
    assert all(gates.values())


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
        },
        "discovery": {
            "overall": {"increment": {"macro": 5}},
            "catastrophic": {"increment": {"macro": 1}},
            "worker_rich": {"increment": {"macro": 3}},
            "rich_immediate": {"increment": {"macro": 1, "full": 1}},
        },
    }
    assert all(support_gates(support, True).values())
    support["discovery"]["rich_immediate"]["increment"]["full"] = 0
    assert not all(support_gates(support, True).values())
