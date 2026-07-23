from cgauto import run_d151a_conditional_second_counterfactual as d151


def test_conditional_feature_hash_is_ordered_and_stable():
    state = ["0.000000000"] * 64
    actions = [
        (0, ["0.000000000"] * 379),
        (2, ["1.000000000"] * 379),
    ]
    first = d151.conditional_feature_hash(state, actions)
    assert first == d151.conditional_feature_hash(state, actions)
    changed = [*actions]
    changed[1] = (2, ["2.000000000", *(["1.000000000"] * 378)])
    assert first != d151.conditional_feature_hash(state, changed)


def test_parse_slots_accepts_sparse_ordered_legal_set():
    assert d151.parse_slots("0,1,4,9") == (0, 1, 4, 9)
