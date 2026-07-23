from __future__ import annotations

import hashlib
from pathlib import Path

from cgauto.slim_live_source import (
    DEAD_FRAGMENTS,
    DEAD_ITEMS,
    SPECIALIZED_DEAD_FRAGMENTS,
    SPECIALIZED_DEAD_ITEMS,
    _remove_item,
    slim,
)


REPO = Path(__file__).resolve().parent.parent
LIVE = REPO / "cgauto/submissions/agent-6553250-yamo-orchard-live.min.rs"
STACK = (
    REPO
    / "cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage.min.rs"
)


def digest(source: str) -> str:
    return hashlib.sha256(source.encode()).hexdigest()


def test_slim_live_frees_only_the_locked_dead_surface() -> None:
    original = LIVE.read_text()
    result = slim(original)

    assert len(original) == 90_133
    assert len(result) == 62_311
    assert digest(result) == "025468a87d1807a6027f8af4c1662dfc89beb68b9fe0ef9ed1047fadf39c218f"
    assert "pub fn tuned_carry_regeneration_transit_idle_harvest()" in result
    assert "pub fn new()" in result
    assert all(marker not in result for marker in DEAD_ITEMS)
    assert all(fragment not in result for fragment in DEAD_FRAGMENTS)
    assert all(marker not in result for marker in SPECIALIZED_DEAD_ITEMS)
    assert all(fragment not in result for fragment in SPECIALIZED_DEAD_FRAGMENTS)


def test_slim_stack_preserves_the_candidate_delta_and_same_savings() -> None:
    live = slim(LIVE.read_text())
    original = STACK.read_text()
    result = slim(original)

    assert len(original) == 90_547
    assert len(result) == 62_725
    assert len(result) - len(live) == len(original) - len(LIVE.read_text()) == 414
    assert digest(result) == "a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55"


def test_item_removal_ignores_braces_inside_literals() -> None:
    source = 'pub fn dead(){let text=format!("{{value}}");}pub fn keep(){}'
    assert _remove_item(source, "pub fn dead()") == "pub fn keep(){}"
