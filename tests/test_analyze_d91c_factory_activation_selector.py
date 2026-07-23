from cgauto.analyze_d91c_factory_activation_selector import selector_predicate


def row(plants: int = 20, fruits: int = 27, bananas: int = 6) -> dict:
    return {
        "banana_factory_activation_plants": plants,
        "banana_factory_activation_fruits": fruits,
        "banana_factory_activation_banana_plants": bananas,
    }


def test_selector_accepts_exact_frozen_boundary() -> None:
    assert selector_predicate(row())


def test_selector_rejects_each_one_step_boundary_failure() -> None:
    assert not selector_predicate(row(plants=21))
    assert not selector_predicate(row(fruits=26))
    assert not selector_predicate(row(bananas=5))
