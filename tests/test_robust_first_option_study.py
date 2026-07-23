from __future__ import annotations

from cgauto.robust_first_option_study import choose, leave_one_model_out


def option(deltas: dict[str, int], *, active: bool = True, train: str = "TRAIN 1 1 0 1") -> dict:
    return {"deltas": deltas, "active": active, "first_train": train}


def test_choose_abstains_on_any_visible_loss_and_prefers_worst_delta() -> None:
    models = ("a", "b", "c")
    options = {
        "control": option({"a": 0, "b": 0, "c": 0}, active=False, train="-"),
        "fragile": option({"a": 50, "b": 20, "c": -1}),
        "robust": option({"a": 7, "b": 6, "c": 5}),
        "weaker": option({"a": 4, "b": 4, "c": 4}),
    }
    selected = choose(options, models)
    assert selected is not None
    assert selected["option"] == "robust"
    assert selected["selection_worst_delta"] == 5


def test_choose_prefers_lower_train_cost_after_value_tie() -> None:
    models = ("a", "b")
    options = {
        "control": option({"a": 0, "b": 0}, active=False, train="-"),
        "expensive": option({"a": 5, "b": 5}, train="TRAIN 3 3 0 3"),
        "cheap": option({"a": 5, "b": 5}, train="TRAIN 1 1 0 1"),
    }
    assert choose(options, models)["option"] == "cheap"


def test_leave_one_model_out_exposes_hidden_regression() -> None:
    models = ("a", "b", "c")
    cells = {
        (0, 0): {
            "control": option({"a": 0, "b": 0, "c": 0}, active=False, train="-"),
            "candidate": option({"a": 5, "b": 5, "c": -10}),
        },
        (0, 1): {
            "control": option({"a": 0, "b": 0, "c": 0}, active=False, train="-"),
            "candidate": option({"a": 0, "b": 0, "c": 0}, active=False),
        },
    }
    report = leave_one_model_out(cells, models)
    held_c = next(row for row in report["held_models"] if row["held_model"] == "c")
    assert held_c["selected_cell_count"] == 1
    assert held_c["held_model_seed_balanced"]["mean"] == -5
    assert report["worst_held_model_mean"] == -5
