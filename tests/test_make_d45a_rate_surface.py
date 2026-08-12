from cgauto.make_d45a_rate_surface import DIRECTIONS, PARAMETERS, catalog


def test_catalog_is_exact_zero_plus_minus_matrix() -> None:
    rows = catalog()
    assert len(rows) == 17
    assert rows[0] == ("zero", [0.0] * PARAMETERS)
    assert len({label for label, _ in rows}) == 17
    for direction, (label, coordinate, amplitude) in enumerate(DIRECTIONS):
        plus_label, plus = rows[1 + 2 * direction]
        minus_label, minus = rows[2 + 2 * direction]
        assert plus_label == f"{label}_plus"
        assert minus_label == f"{label}_minus"
        assert [index for index, value in enumerate(plus) if value] == [coordinate]
        assert [index for index, value in enumerate(minus) if value] == [coordinate]
        assert plus[coordinate] == amplitude
        assert minus[coordinate] == -amplitude


def test_direction_coordinates_are_unique_and_in_range() -> None:
    coordinates = [coordinate for _, coordinate, _ in DIRECTIONS]
    assert len(coordinates) == len(set(coordinates))
    assert coordinates == [1, 2, 3, 4, 5, 12, 24, 28]
    assert PARAMETERS == 32
