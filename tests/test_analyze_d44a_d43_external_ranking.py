import numpy as np

from cgauto.analyze_d44a_d43_external_ranking import (
    average_tie_ranks,
    clustered_contrast,
    correlation,
    residualize,
    spearman,
    top_mask,
)


def test_average_tie_ranks() -> None:
    actual = average_tie_ranks(np.asarray([3.0, 1.0, 1.0, 2.0]))
    np.testing.assert_allclose(actual, [3.0, 0.5, 0.5, 2.0])


def test_spearman_detects_monotone_direction() -> None:
    left = np.asarray([1.0, 2.0, 3.0, 4.0])
    assert spearman(left, left) == 1.0
    assert spearman(left, left[::-1]) == -1.0
    assert correlation(left, left) == 1.0


def test_top_mask_has_exact_count_and_tie_order() -> None:
    scores = np.asarray([0.1, 0.4, 0.4, 0.2])
    sample_ids = np.arange(4)
    selected = top_mask(scores, sample_ids, 2)
    np.testing.assert_array_equal(selected, [False, True, True, False])


def test_residualize_removes_group_means() -> None:
    values = np.asarray([1.0, 3.0, 10.0, 14.0])
    groups = np.asarray(["a", "a", "b", "b"])
    actual = residualize(values, groups)
    np.testing.assert_allclose(actual, [-1.0, 1.0, -2.0, 2.0])


def test_clustered_contrast_uses_only_maps_with_both_halves() -> None:
    values = np.asarray([5.0, 1.0, 8.0, 2.0, 99.0])
    maps = np.asarray([1, 1, 2, 2, 3])
    high = np.asarray([True, False, True, False, True])
    low = np.asarray([False, True, False, True, False])
    actual = clustered_contrast(values, maps, high, low)
    assert actual["maps"] == 2
    assert actual["mean"] == 5.0
