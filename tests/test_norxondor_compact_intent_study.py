from __future__ import annotations

from cgauto.norxondor_compact_intent_study import fit_tree, node_count, predict


def sample(value: str, label: str) -> dict:
    return {"features": {"role": value}, "label": label}


def test_categorical_tree_learns_an_equality_split() -> None:
    rows = [sample("wood", "GO_CHOP") for _ in range(4)] + [
        sample("farm", "GO_HARVEST") for _ in range(4)
    ]
    tree = fit_tree(rows, ("role",), max_depth=2, min_leaf=2)
    assert node_count(tree) == 3
    assert predict(tree, sample("wood", "unused")) == "GO_CHOP"
    assert predict(tree, sample("farm", "unused")) == "GO_HARVEST"


def test_tree_stays_leaf_when_minimum_leaf_blocks_split() -> None:
    rows = [sample("wood", "GO_CHOP"), sample("farm", "GO_HARVEST")]
    tree = fit_tree(rows, ("role",), max_depth=2, min_leaf=2)
    assert node_count(tree) == 1
