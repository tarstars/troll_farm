from __future__ import annotations

import pytest

from cgauto.d11_native_layer_analysis import EXPECTED_POLICIES, analyze, validate


def fixture_rows() -> list[dict]:
    deltas = {
        "resident": 0,
        "native_actor_all": 6,
        "native_resident_starter_actor_second": 7,
        "native_actor_starter_resident_second": 6.5,
    }
    rows = []
    for seed in range(8):
        for seat in range(2):
            for policy in EXPECTED_POLICIES:
                rows.append(
                    {
                        "seed": seed,
                        "seat": seat,
                        "opponent": "resident",
                        "policy": policy,
                        "adopt_worker": int(policy != "resident"),
                        "margin": deltas[policy],
                        "wood_edge": deltas[policy],
                        "workers": 2,
                        "trained_ms": 2,
                        "trained_cc": 2,
                        "trained_hp": 0,
                        "trained_chop": 2,
                        "plant_commands": 1,
                        "harvest_commands": 2,
                        "chop_commands": 3,
                        "drop_commands": 4,
                        "move_commands": 5,
                    }
                )
    return rows


def test_one_worker_role_tie_break_prefers_actor_starter(tmp_path):
    source = tmp_path / "layers.tsv"
    source.write_text("fixture\n")
    result = analyze(fixture_rows(), source)

    assert set(result["selection"]["eligible_policies"]) == EXPECTED_POLICIES - {
        "resident"
    }
    assert (
        result["selection"]["selected_policy"]
        == "native_actor_starter_resident_second"
    )


def test_native_layer_validation_rejects_missing_cell():
    rows = fixture_rows()
    rows.pop()

    with pytest.raises(ValueError, match="incomplete native layer catalog"):
        validate(rows)
