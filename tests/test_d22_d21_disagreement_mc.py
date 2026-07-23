from __future__ import annotations

from cgauto.d22_d21_disagreement_mc import event_priority, splitmix64


def test_splitmix_and_event_priority_are_deterministic():
    values = [splitmix64(value) for value in range(20)]
    assert values == [splitmix64(value) for value in range(20)]
    assert len(set(values)) == len(values)
    assert event_priority(123, 45, 2) == event_priority(123, 45, 2)


def test_event_priority_changes_across_decisions_and_bands():
    priorities = {
        event_priority(8_300_000, decision, band)
        for decision in range(10)
        for band in range(4)
    }
    assert len(priorities) == 40
