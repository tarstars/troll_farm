from __future__ import annotations

import pytest

from cgauto.validate_opponent_crop_candidate import (
    activate_research_source,
    percentile,
    RESEARCH,
)


def test_research_activation_changes_only_the_unique_main_constructor() -> None:
    source = RESEARCH.read_text()
    activated = activate_research_source(source)
    assert activated.count("opponent_crop_priority(100, 6, 1, 1)") == 1
    assert len(activated) > len(source)


def test_research_activation_refuses_source_drift() -> None:
    with pytest.raises(ValueError, match="research main anchor"):
        activate_research_source("fn main() {}")


def test_percentile_uses_nearest_observation() -> None:
    assert percentile([4, 1, 3, 2], 0.5) == 3
