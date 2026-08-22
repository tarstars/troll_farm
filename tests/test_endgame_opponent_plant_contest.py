from types import SimpleNamespace

from cgauto.endgame_opponent_plant_contest import (
    action_summary,
    bootstrap_mean_interval,
    cohort_game_ids_from_manifest,
    decide_verdict,
    generation_fate,
    generation_identity_checks,
    ids_hash,
    is_target_generation,
    percentile,
    subject_eta_at_birth,
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


def test_action_extraction_uses_successful_generation_cargo_only():
    events = [
        {
            "success": True,
            "target_generation": "g1",
            "verb": "HARVEST",
            "turn": 7,
            "gained": {"APPLE": 2},
        },
        {
            "success": True,
            "target_generation": "g1",
            "verb": "CHOP",
            "turn": 8,
            "gained": {"WOOD": 1},
        },
        {
            "success": False,
            "target_generation": "g1",
            "verb": "HARVEST",
            "turn": 6,
            "gained": {"APPLE": 9},
        },
        {
            "success": True,
            "target_generation": "other",
            "verb": "CHOP",
            "turn": 5,
            "gained": {"WOOD": 9},
        },
    ]
    summary = action_summary(events, "g1")
    assert summary == {
        "first_turn": 7,
        "first_verb": "HARVEST",
        "harvest_actions": 1,
        "fruit_gained": 2,
        "chop_actions": 1,
        "wood_gained": 1,
        "extracted_score_equivalent": 6,
    }


def test_generation_death_and_feller_follow_exact_lineage():
    lineage = [{}, {"cell": "g1"}, {"cell": "g1"}, {}]
    subject_events = [
        {
            "success": True,
            "verb": "CHOP",
            "target_generation": "g1",
            "turn": 3,
        }
    ]
    assert generation_fate("g1", 1, lineage, subject_events, []) == {
        "death_turn": 3,
        "feller": "subject",
        "survived_to_end": False,
    }
    assert generation_fate("g1", 1, lineage[:3], subject_events, []) == {
        "death_turn": None,
        "feller": None,
        "survived_to_end": True,
    }


def test_eta_at_birth_uses_post_birth_state_and_ceil_division():
    game = SimpleNamespace(
        states=[
            {"units": [{"player": 0, "x": 3, "y": 0, "ms": 1}]},
            {
                "units": [
                    {"player": 0, "x": 0, "y": 0, "ms": 2},
                    {"player": 1, "x": 3, "y": 0, "ms": 9},
                ]
            },
        ],
        board={"walkable": {(0, 0), (1, 0), (2, 0), (3, 0)}},
        me=0,
    )
    assert subject_eta_at_birth(game, 1, (3, 0)) == 2
    assert subject_eta_at_birth(game, 1, (9, 9)) is None


def test_target_filter_is_strict_on_turn_origin_and_pre_turn_margin():
    margin = [0] * 250 + [1, 1, 1]
    assert not is_target_generation({"origin": "opponent"}, 250, margin)
    assert is_target_generation({"origin": "opponent"}, 251, margin)
    assert not is_target_generation({"origin": "actor"}, 251, margin)
    zero_margin = margin.copy()
    zero_margin[250] = 0
    assert not is_target_generation({"origin": "opponent"}, 251, zero_margin)


def test_unique_successful_plant_and_cross_orientation_identity():
    generation_id = "251:4,5"
    meta = {
        "origin": "opponent",
        "birth_turn": 251,
        "cell": [4, 5],
        "kind": "APPLE",
    }
    counterpart = {**meta, "origin": "actor"}
    subject_lineage = [{} for _ in range(252)]
    opponent_lineage = [{} for _ in range(252)]
    subject_lineage[251][(4, 5)] = generation_id
    opponent_lineage[251][(4, 5)] = generation_id
    plant = {
        "success": True,
        "verb": "PLANT",
        "created_generation": generation_id,
        "created_origin": "actor",
    }
    assert generation_identity_checks(
        generation_id,
        meta,
        251,
        counterpart,
        subject_lineage,
        opponent_lineage,
        [plant],
    ) == (True, True)
    assert generation_identity_checks(
        generation_id,
        meta,
        251,
        counterpart,
        subject_lineage,
        opponent_lineage,
        [plant, plant],
    ) == (True, False)
    wrong = {**counterpart, "kind": "LEMON"}
    assert generation_identity_checks(
        generation_id,
        meta,
        251,
        wrong,
        subject_lineage,
        opponent_lineage,
        [plant],
    ) == (False, True)


def test_frozen_manifest_selection_is_sorted_and_agent_exact():
    manifest = {
        "entries": [
            {"cohort": "resident", "agent_id": 6561795, "game_id": 2},
            {"cohort": "resident", "agent_id": 6561795, "game_id": 1},
            {"cohort": "yamo", "agent_id": 6479814, "game_id": 3},
        ]
    }
    assert cohort_game_ids_from_manifest(manifest) == {
        "resident": [1, 2],
        "yamo": [3],
    }
    manifest["entries"][0]["agent_id"] = -1
    try:
        cohort_game_ids_from_manifest(manifest)
    except ValueError as exc:
        assert "agent mismatch" in str(exc)
    else:
        raise AssertionError("mismatched frozen-manifest agent was accepted")
