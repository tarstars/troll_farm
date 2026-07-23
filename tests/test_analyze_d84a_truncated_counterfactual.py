from cgauto.analyze_d84a_truncated_counterfactual import choose_arm, percentile


def arm(name: str, liquid_margin: int, available: int = 1) -> dict[str, str]:
    return {
        "arm": name,
        "liquid_margin": str(liquid_margin),
        "arm_available": str(available),
    }


def test_selector_abstains_on_control_tie() -> None:
    arms = {
        "control": arm("control", 10),
        "fell": arm("fell", 10),
        "harvest": arm("harvest", 9),
        "renew": arm("renew", 8),
    }
    assert choose_arm(arms) == "control"


def test_selector_uses_frozen_semantic_tie_order_and_availability() -> None:
    arms = {
        "control": arm("control", 10),
        "fell": arm("fell", 12),
        "harvest": arm("harvest", 12),
        "renew": arm("renew", 20, available=0),
    }
    assert choose_arm(arms) == "harvest"


def test_percentile_uses_nearest_rank() -> None:
    assert percentile(range(1, 101), 0.50) == 50
    assert percentile(range(1, 101), 0.95) == 95
