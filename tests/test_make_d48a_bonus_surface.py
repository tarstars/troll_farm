from cgauto.make_d48a_bonus_surface import catalog


def test_catalog_is_exact_anchor_and_zero_double_pairs() -> None:
    rows = catalog()
    assert rows[0] == ("anchor", 1.0, 1.0, 1.0)
    assert [row[0] for row in rows] == [
        "anchor",
        "provenance_zero",
        "provenance_double",
        "renew_zero",
        "renew_double",
        "bank_zero",
        "bank_double",
    ]
    assert len({row[1:] for row in rows}) == 7
