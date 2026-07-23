from __future__ import annotations

from cgauto.d12_resident_idle_readiness import (
    CANDIDATE,
    CONTROL,
    FROZEN_OPPONENTS,
    FROZEN_SEEDS,
    analyze,
)


def fixture_rows() -> list[dict]:
    rows = []
    for seed in FROZEN_SEEDS:
        for seat in range(2):
            for opponent_index, opponent in enumerate(FROZEN_OPPONENTS):
                cell_index = seat * len(FROZEN_OPPONENTS) + opponent_index
                delta = 0
                if seed < 12 and cell_index < 6:
                    delta = 2
                if seed == 8 and cell_index == 0:
                    delta = -1
                for policy in (CONTROL, CANDIDATE):
                    rows.append(
                        {
                            "seed": seed,
                            "seat": seat,
                            "opponent": opponent,
                            "policy": policy,
                            "adopt_worker": int(policy == CANDIDATE),
                            "margin": delta if policy == CANDIDATE else 0,
                            "wood_edge": delta if policy == CANDIDATE else 0,
                            "workers": 2,
                            "shadow_decisions": 100,
                            "resident_wait_actor_action": 10,
                            "overrides": int(policy == CANDIDATE),
                        }
                    )
    return rows


def test_distributed_effect_passes_readiness(tmp_path):
    source = tmp_path / "readiness.tsv"
    source.write_text("fixture\n")
    result = analyze(fixture_rows(), source)

    assert result["effect"]["changed_cells"] == 24
    assert result["effect"]["positive_changed_cells"] == 23
    assert result["effect"]["negative_changed_cells"] == 1
    assert result["readiness"]["ready_for_counterfactual_labeling"] is True


def test_one_map_concentration_fails_readiness(tmp_path):
    source = tmp_path / "readiness.tsv"
    source.write_text("fixture\n")
    rows = fixture_rows()
    for row in rows:
        if row["policy"] == CANDIDATE and row["seed"] == 8 and row["margin"] > 0:
            row["margin"] *= 100
    result = analyze(rows, source)

    assert (
        result["readiness"]["gates"][
            "largest_positive_map_share_at_most_60_percent"
        ]
        is False
    )
    assert result["readiness"]["ready_for_counterfactual_labeling"] is False
