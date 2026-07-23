import pytest

from cgauto.analyze_d121a_d119_retrospective_grid import candidate_id, pearson


def test_candidate_id_is_exact_and_stable():
    assert candidate_id(11901, 0.0) == "11901:+0.0"
    assert candidate_id(11904, -1.0) == "11904:-1.0"


def test_pearson_handles_direction_and_constant_vectors():
    assert pearson([1.0, 2.0, 3.0], [2.0, 4.0, 6.0]) == pytest.approx(1.0)
    assert pearson([1.0, 2.0, 3.0], [6.0, 4.0, 2.0]) == pytest.approx(-1.0)
    assert pearson([1.0, 1.0, 1.0], [2.0, 3.0, 4.0]) == 0.0
