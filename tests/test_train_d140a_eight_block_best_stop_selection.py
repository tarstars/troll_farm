import pytest

from cgauto.train_d140a_eight_block_best_stop_selection import validate_descriptors


def _descriptors():
    return [
        {"block_id": block, "start_seed": 9_844_000 + 16 * block, "maps": 16}
        for block in range(8)
    ]


def test_validate_descriptors_requires_ordered_nonoverlapping_eight_blocks():
    result = validate_descriptors(list(reversed(_descriptors())))
    assert [row["block_id"] for row in result] == list(range(8))


def test_validate_descriptors_rejects_overlap_and_missing_block():
    overlap = _descriptors()
    overlap[4]["start_seed"] = overlap[3]["start_seed"] + 15
    with pytest.raises(RuntimeError, match="overlap"):
        validate_descriptors(overlap)
    with pytest.raises(RuntimeError, match="0 through 7"):
        validate_descriptors(_descriptors()[:-1])
