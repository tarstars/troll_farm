from __future__ import annotations

from cgauto.d16_resident_residual_mc_density import START, STOP, analyze


def fixture(positive: bool = True) -> list[dict]:
    rows = []
    for scenario in range(START, STOP):
        for slot in range(10):
            advantage = 0
            if positive and slot < 2:
                advantage = 2
            rows.append(
                {
                    "scenario": scenario,
                    "map_seed": scenario // 12,
                    "seat": (scenario // 6) % 2,
                    "opponent": str(scenario % 6),
                    "sample_slot": slot,
                    "candidate_count": 100,
                    "alternative_plane": 1 + scenario % 2,
                    "ordinal": slot % 2,
                    "margin_advantage": advantage,
                    "wood_advantage": advantage,
                    "new_catastrophe": 0,
                    "elapsed_us": 10,
                    "resident_verb": "MOVE",
                    "alternative_verb": "CHOP" if scenario % 2 else "HARVEST",
                    "turn": 20 + slot * 25,
                    "ms": 1,
                    "cc": 1,
                    "hp": 1,
                    "chop": 1,
                }
            )
    return rows


def test_distributed_positive_teacher_passes(tmp_path):
    source = tmp_path / "labels.tsv"
    source.write_text("fixture\n")
    result = analyze(fixture(), source)

    assert result["overall"]["positive_labels"] == 480
    assert result["density_gate"]["eligible_for_larger_distillation_corpus"] is True


def test_zero_advantage_teacher_fails(tmp_path):
    source = tmp_path / "labels.tsv"
    source.write_text("fixture\n")
    result = analyze(fixture(positive=False), source)

    assert result["overall"]["positive_labels"] == 0
    assert result["density_gate"]["eligible_for_larger_distillation_corpus"] is False
