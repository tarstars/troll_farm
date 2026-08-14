import copy

import numpy as np

from codex_1 import f1_opponent_archetype_readiness as f1


def fixture_record():
    state0 = {
        "u": [
            [10, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
            [20, 1, 4, 2, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
        ],
        "p": [[2, 2, "BANANA", 1, 3, 0, 2]],
        "b": [[3, 4, 5, 6, 7, 8], [8, 7, 6, 5, 4, 3]],
    }
    state1 = {
        "u": [
            [10, 0, 2, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0],
            [20, 1, 4, 3, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
            [21, 1, 4, 2, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
        ],
        "p": [[2, 2, "BANANA", 2, 4, 1, 1]],
        "b": [[3, 5, 5, 6, 7, 8], [8, 7, 6, 5, 4, 3]],
    }
    return {
        "seed": 9_854_000,
        "seat": 0,
        "opp": 7,
        "opp_name": "forbidden-label",
        "arm": "referee",
        "map_rows": ["0...+", ".#~..", "....1"],
        "turns": 1,
        "scores": [999, 0],
        "states": [state0, state1],
        "c0": [["TRAIN"]],
        "c1": [["PLANT 2 BANANA"]],
    }


def test_command_and_label_deletion_is_byte_identical():
    source = fixture_record()
    clean = copy.deepcopy(source)
    for key in f1.FORBIDDEN_INPUT_FIELDS:
        clean.pop(key, None)
    left = f1.feature_vector(source, horizon=1, variant="cumulative")
    right = f1.feature_vector(clean, horizon=1, variant="cumulative")
    assert left.dtype == np.float64
    assert left.tobytes() == right.tobytes()


def test_transition_features_detect_birth_and_movement_without_commands():
    names, values = f1.named_features(fixture_record(), horizon=1, variant="cumulative")
    feature = dict(zip(names, values, strict=True))
    assert feature["transition_opp_births"] == 1 / 8
    assert feature["transition_own_manhattan_movement"] == 1 / 512
    assert feature["transition_opp_manhattan_movement"] == 1 / 512


def test_group_folds_keep_every_seed_block_whole():
    seeds = np.repeat(np.arange(9_854_000, 9_854_010), 16)
    folds = f1.outer_fold_ids(seeds)
    for seed in np.unique(seeds):
        assert len(set(folds[seeds == seed])) == 1
    assert set(folds) == {0, 1, 2, 3, 4}


def test_portable_linear_scorer_preserves_pipeline_predictions():
    features = np.asarray(
        [[float(row), float(column), float(row == column)] for row in range(8) for column in range(8)]
    )
    labels = np.repeat(np.arange(8), 8)
    model = f1._linear_model(0.1).fit(features, labels)
    artifact = f1.portable_linear_artifact(model, ["a", "b", "c"])
    expected = model.predict(features)
    observed = np.argmax(f1.portable_linear_scores(artifact, features), axis=1)
    assert np.array_equal(expected, observed)
    assert artifact["serialized_bytes"] < 20_000


def test_verdict_gate_uses_turn40_and_requires_every_integrity_check():
    passing = f1.synthetic_passing_gate_metrics()
    assert f1.readiness_verdict({40: passing, 80: passing}, integrity=True) == "EARLY_PROXY_SIGNAL"
    assert f1.readiness_verdict({40: passing, 80: passing}, integrity=False) == "BLOCKED_LEAKAGE_OR_INTEGRITY"
    failing40 = copy.deepcopy(passing)
    failing40["macro_f1"] = 0.49
    assert f1.readiness_verdict({40: failing40, 80: passing}, integrity=True) == "LATE_ONLY_PROXY_SIGNAL"


def test_within_seed_permutation_keeps_seat_pairs_on_one_family_mapping():
    seeds = np.repeat([1, 2], 16)
    seats = np.tile(np.repeat([0, 1], 8), 2)
    labels = np.tile(np.tile(np.arange(8), 2), 2)
    shuffled = f1.permute_labels_within_seed(seeds, seats, labels, repetition=17)
    for seed in (1, 2):
        for family in range(8):
            idx = (seeds == seed) & (labels == family)
            assert len(set(shuffled[idx])) == 1
    assert sorted(shuffled[(seeds == 1) & (seats == 0)]) == list(range(8))
