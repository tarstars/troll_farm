from cgauto.analyze_d124a_d119_fine_gate_calibration import (
    OFFSETS,
    block_stability_gates,
    candidate_id,
    descriptively_feasible,
)


def test_offset_grid_is_frozen_and_exact():
    assert len(OFFSETS) == 11
    assert OFFSETS[0] == -0.50
    assert OFFSETS[-1] == 0.00
    assert all(
        round(right - left, 10) == 0.05
        for left, right in zip(OFFSETS, OFFSETS[1:])
    )


def test_candidate_id_preserves_fine_offset_resolution():
    assert candidate_id(11903, -0.15) == "11903:-0.15"
    assert candidate_id(11901, 0.0) == "11901:+0.00"


def test_block_stability_requires_every_block_nonnegative():
    stable = {str(index): {"mean_margin_delta": 0.0} for index in range(5)}
    assert all(block_stability_gates(stable).values())
    stable["3"]["mean_margin_delta"] = -0.001
    assert not all(block_stability_gates(stable).values())


def test_descriptive_feasibility_requires_every_gate_family():
    passing = {"gate": True}
    assert descriptively_feasible(passing, passing, passing, passing)
    assert not descriptively_feasible(
        passing, {"gate": False}, passing, passing
    )
