import csv

import pytest

from cgauto.make_d105a_quantized_expert_population import (
    FEATURES,
    build_population,
    quantize,
)


def test_quantize_uses_symmetric_signed_range_and_ties_to_even():
    weights = [0.0] * FEATURES
    weights[:7] = [-1.0, -0.5, -1 / 14, 0.0, 1 / 14, 0.5, 1.0]
    values = quantize(weights, 4)
    assert values[:7] == [-7, -4, 0, 0, 0, 4, 7]
    assert min(values) >= -7
    assert max(values) <= 7


@pytest.mark.parametrize(
    ("bits", "raw_bytes", "base85_bytes"),
    [(4, 4_896, 6_120), (6, 7_344, 9_180), (8, 9_792, 12_240)],
)
def test_build_population_has_exact_grid_and_packed_size(
    tmp_path, bits, raw_bytes, base85_bytes
):
    source = (
        tmp_path.parent.parent.parent
        / "data"
        / "analysis"
        / "live-agent-6553250"
        / "d98a-bounded-whole-game-joint-assignment-population.tsv"
    )
    # pytest's temporary path is outside the repository; resolve through this module instead.
    from cgauto.analyze_d104a_d98_expert_proposal_coverage import D98_POPULATION

    source = D98_POPULATION
    target = tmp_path / f"q{bits}.tsv"
    audit = build_population(source, target, bits)
    assert audit["raw_packed_bytes"] == raw_bytes
    assert audit["base85_payload_bytes"] == base85_bytes
    with target.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert len(rows) == 64
    assert [row["policy"] for row in rows] == [f"four_{index:02}" for index in range(64)]
    qmax = (1 << (bits - 1)) - 1
    coefficients = [
        int(row[f"param_{index:03}"])
        for row in rows
        for index in range(FEATURES)
    ]
    assert min(coefficients) >= -qmax
    assert max(coefficients) <= qmax
