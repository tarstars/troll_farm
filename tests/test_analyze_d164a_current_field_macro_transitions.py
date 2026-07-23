from cgauto import analyze_d164a_current_field_macro_transitions as d164


def event(turn, ordinal, verb, *, target=None, created=None, success=True):
    return {
        "turn": turn,
        "ordinal": ordinal,
        "workforce": 2,
        "verb": verb,
        "target_origin": target,
        "created_origin": created,
        "success": success,
    }


def cohort(rate, *, support=None):
    result = {
        "motif_rates": {motif: rate for motif in d164.MOTIFS},
    }
    if support is not None:
        result["motif_agent_support"] = {
            motif: support for motif in d164.MOTIFS
        }
    return result


def test_role_compression_and_handoff_subsequences_are_ordered():
    rows = [
        event(1, 0, "PLANT", created="actor"),
        event(2, 0, "HARVEST", target="actor"),
        event(3, 0, "CHOP", target="opponent"),
        event(4, 0, "CHOP", target="opponent"),
        event(5, 0, "HARVEST", target="actor"),
    ]
    roles = d164.compressed_roles(rows)
    assert roles == ["P", "S", "P"]
    assert d164.has_subsequence(roles, ("P", "S"))
    assert d164.has_subsequence(roles, ("P", "S", "P"))
    assert not d164.has_subsequence(roles, ("S", "P", "S"))


def test_same_worker_horizon_rejects_cross_worker_and_late_matches():
    starts = [event(10, 0, "HARVEST", target="actor")]
    assert d164.later_same_worker(
        starts, [event(42, 0, "PLANT", created="actor")]
    )
    assert not d164.later_same_worker(
        starts, [event(43, 0, "PLANT", created="actor")]
    )
    assert not d164.later_same_worker(
        starts, [event(20, 1, "PLANT", created="actor")]
    )


def test_frozen_field_gate_opens_only_new_handoff_primitives():
    cohorts = {
        "rank_1_5": cohort(0.50, support=4),
        "rank_6_20": cohort(0.30),
        "resident": cohort(0.05),
    }
    matrix = {row["motif"]: row for row in d164.build_matrix(cohorts)}
    assert matrix["same_worker_renewal_cycle"]["field_stable_missing"]
    assert not matrix["same_worker_renewal_cycle"]["eligible_new_primitive"]
    assert matrix["bidirectional_producer_suppressor_handoff"][
        "eligible_new_primitive"
    ]


def test_field_gate_requires_reference_prevalence_and_three_top_agents():
    cohorts = {
        "rank_1_5": cohort(0.50, support=2),
        "rank_6_20": cohort(0.19),
        "resident": cohort(0.00),
    }
    assert not any(row["field_stable_missing"] for row in d164.build_matrix(cohorts))


def test_exact_same_kind_simultaneous_birth_is_reclassified_as_joint():
    before = {
        "units": [
            {"id": 0, "player": 0, "x": 8, "y": 5},
            {"id": 2, "player": 1, "x": 8, "y": 5},
        ],
        "plants": [],
    }
    after = {
        "units": before["units"],
        "plants": [{"x": 8, "y": 5, "type": "BANANA"}],
    }
    trajectory = {"commands0": "PLANT 0 BANANA", "commands1": "PLANT 2 BANANA"}
    assert d164.joint_plant_creators(before, after, trajectory, (8, 5)) == {0, 1}
    generations = {
        "1:8:5": {
            "birth_turn": 1,
            "cell": [8, 5],
            "kind": "BANANA",
            "origin": "ambiguous",
        }
    }
    events = [
        {
            "created_generation": "1:8:5",
            "created_origin": "ambiguous",
            "target_generation": None,
            "target_origin": None,
        }
    ]
    quality = {"ambiguous_births": 1}
    assert d164.resolve_joint_births(
        events, generations, quality, [before, after], [trajectory]
    ) == 1
    assert generations["1:8:5"]["origin"] == "joint"
    assert events[0]["created_origin"] == "joint"
    assert quality == {"ambiguous_births": 0, "joint_births": 1}
