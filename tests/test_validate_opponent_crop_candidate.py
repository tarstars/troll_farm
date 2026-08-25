from __future__ import annotations

import pytest

from cgauto.validate_opponent_crop_candidate import (
    activate_research_source,
    percentile,
)


def test_activation_is_retired_and_refuses_loudly() -> None:
    # Owner ruling 2026-08-11 (B7/3a). The live source recovered on 2026-07-29
    # contains TWO identical opponent_crop_priority(100, 6, 1, 1) constructors, so
    # this function's unique-anchor safety premise is gone: activating it against
    # today's source could modify the wrong site. It must refuse every input. The
    # maintained equivalent is validate_opponent_crop_dual_value_candidate's
    # activate_research_source, which carries its own green seal test.
    with pytest.raises(RuntimeError, match="retired"):
        activate_research_source("anything")


def test_percentile_uses_nearest_observation() -> None:
    assert percentile([4, 1, 3, 2], 0.5) == 3
