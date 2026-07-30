from cgauto.endgame_opponent_plant_contest import (
    bootstrap_mean_interval,
    decide_verdict,
    ids_hash,
    percentile,
)


def common_kwargs():
    return {
        "source_integrity": True,
        "decode_integrity": True,
        "target_integrity": True,
        "target_count": 40,
        "target_games": 25,
        "positive_targets": 22,
        "positive_games": 12,
    }


def test_ids_hash_is_order_explicit():
    assert ids_hash([1, 2]) != ids_hash([2, 1])
    assert ids_hash([1, 2]) == ids_hash([1, 2])


def test_percentile_interpolates():
    assert percentile([0.0, 10.0], 0.25) == 2.5
    assert percentile([3.0], 0.975) == 3.0


def test_bootstrap_is_deterministic_and_game_level():
    first = bootstrap_mean_interval([0.0, 0.0, 6.0], reps=500, seed=11)
    second = bootstrap_mean_interval([0.0, 0.0, 6.0], reps=500, seed=11)
    assert first == second
    assert first["mean"] == 2.0


def test_no_material_requires_upper_interval_below_gate():
    verdict, gates = decide_verdict(**common_kwargs(), ci_lo=1.0, ci_hi=19.999)
    assert verdict == "NO_MATERIAL_CONTEST_OPPORTUNITY"
    assert gates["support_pass"]
    assert gates["ci_upper_lt_20"]


def test_material_requires_positive_support_and_lower_interval():
    verdict, gates = decide_verdict(**common_kwargs(), ci_lo=20.0, ci_hi=30.0)
    assert verdict == "MATERIAL_CONTEST_OPPORTUNITY"
    assert gates["material_pass"]


def test_overlap_or_integrity_failure_is_unidentifiable():
    verdict, _ = decide_verdict(**common_kwargs(), ci_lo=10.0, ci_hi=25.0)
    assert verdict == "UNIDENTIFIABLE"
    broken = common_kwargs()
    broken["target_integrity"] = False
    verdict, gates = decide_verdict(**broken, ci_lo=1.0, ci_hi=2.0)
    assert verdict == "UNIDENTIFIABLE"
    assert not gates["support_pass"]
