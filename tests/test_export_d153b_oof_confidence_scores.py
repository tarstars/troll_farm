from cgauto import export_d153b_oof_confidence_scores as d153b


def test_score_export_uses_stable_fixed_precision():
    assert d153b.score(1 / 3) == "0.333333333"
    assert d153b.score(0.0) == "0.000000000"
    assert d153b.SCORE_FIELDS[0:2] == ("seed", "held_fold")
