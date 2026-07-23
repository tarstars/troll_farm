from cgauto.analyze_d55a_terminal_train_stock_flow import (
    dominant_resource,
    readiness_category,
    select_mechanism,
)


def row(inventory, carry, ripe):
    out = {}
    for resource, cost in zip(("plum", "lemon", "apple", "iron"), (5, 5, 5, 2)):
        out[f"next_cost_{resource}"] = str(cost)
        out[f"final_inventory_{resource}"] = str(inventory.get(resource, 0))
        out[f"final_carry_{resource}"] = str(carry.get(resource, 0))
        if resource != "iron":
            out[f"final_ripe_{resource}"] = str(ripe.get(resource, 0))
    return out


def test_readiness_categories_are_ordered_and_exclusive():
    assert readiness_category(row({"plum": 5, "lemon": 5, "apple": 5, "iron": 2}, {}, {})) == "deposited_ready"
    assert readiness_category(row({"plum": 4, "lemon": 5, "apple": 5, "iron": 2}, {"plum": 1}, {})) == "carry_closes"
    assert readiness_category(row({"plum": 4, "lemon": 5, "apple": 5, "iron": 2}, {}, {"plum": 1})) == "ripe_closes"
    assert readiness_category(row({}, {}, {})) == "source_unresolved"


def test_dominance_requires_seventy_percent_and_fifteen_point_gap():
    assert dominant_resource({"plum": 0.70, "lemon": 0.55, "apple": 0.2, "iron": 0.0}) == "plum"
    assert dominant_resource({"plum": 0.70, "lemon": 0.56, "apple": 0.2, "iron": 0.0}) is None
    assert dominant_resource({"plum": 0.69, "lemon": 0.2, "apple": 0.1, "iron": 0.0}) is None


def test_source_majority_selects_specific_or_vector_acquisition():
    readiness = {
        "deposited_ready": 5,
        "carry_closes": 5,
        "ripe_closes": 5,
        "source_unresolved": 85,
    }
    assert select_mechanism(
        readiness,
        {"plum": 0.2, "lemon": 0.8, "apple": 0.4, "iron": 0.0},
    ) == "resource-specific renewable/source acquisition: lemon"
    assert select_mechanism(
        readiness,
        {"plum": 0.7, "lemon": 0.6, "apple": 0.4, "iron": 0.0},
    ) == "exact deficit-vector renewable/source acquisition"
