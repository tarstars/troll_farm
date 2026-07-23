import pytest

from cgauto.validate_opponent_crop_dual_value_candidate import activate_research_source


def test_activate_research_source_changes_only_main_constructor() -> None:
    source = "prefix\n    let mut bot = SecureOrchardBot::new();\nsuffix\n"
    activated = activate_research_source(source)
    assert "SecureOrchardBot::opponent_crop_dual_value_e6();" in activated
    assert "SecureOrchardBot::new();" not in activated


def test_activate_research_source_fails_closed() -> None:
    with pytest.raises(ValueError, match="found 0"):
        activate_research_source("no constructor")
