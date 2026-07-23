from cgauto.yamo_resident_residual_study import analyze


def row(opponent: str, margin: int, score: int, samples: str = "100,200") -> dict:
    return {
        "seed": "0",
        "seat": "0",
        "opponent": opponent,
        "margin_delta": str(margin),
        "score_delta": str(score),
        "searches": "3",
        "accepted": "1",
        "failed_targets": "0",
        "decision_samples_us": samples,
    }


def test_gate_passes_a_fast_robust_positive_screen():
    payload = analyze([row(f"opp{index}", 3, 3) for index in range(8)])

    assert payload["research_gate"]["passed"]
    assert payload["nonnegative_opponents"] == 8
    assert payload["decision"]["direct_online_profile"]


def test_gate_rejects_slow_or_small_effect_screen():
    rows = [row(f"opp{index}", 1, 1, "100,60000") for index in range(8)]
    payload = analyze(rows)

    assert not payload["research_gate"]["passed"]
    assert not payload["research_gate"]["requirements"]["mean_margin_at_least_2"]
    assert not payload["research_gate"]["requirements"]["no_decision_over_50ms"]
    assert not payload["decision"]["own_state_distillation"]


def test_optional_event_audit_groups_target_classes():
    rows = [row(f"opp{index}", 3, 4) for index in range(8)]
    for item in rows:
        item["accepted_events"] = (
            "100,1,1,1,1,1,0,0,1,1,2,2,SHACK,0,0,0,6.0,7.0"
        )

    audit = analyze(rows)["accepted_event_audit"]

    assert audit["events"] == 8
    assert audit["target_classes"]["SHACK"]["singleton_scenarios"] == 8


def test_bank_profile_requires_twenty_accepted_deviations():
    rows = [row(f"opp{index}", 3, 3) for index in range(8)]
    for item in rows:
        item["profile"] = "bank_only"

    payload = analyze(rows)

    assert not payload["algorithmic_gate"]["passed"]
    assert not payload["algorithmic_gate"]["requirements"][
        "accepted_deviations_at_least_20"
    ]
