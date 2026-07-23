"""Tests for D70a opening-transaction nomination."""

from __future__ import annotations

from cgauto.analyze_d70a_opening_establishment_archetype import (
    archetype_gate,
    largest_index,
    species_rule_choices,
)


def transaction(relation: str, provenance: str, **changes) -> dict:
    result = {
        "early_by_turn_10": True,
        "worker_two_relation": relation,
        "seed_provenance": provenance,
        "species": "PLUM",
        "receipt_before_worker_three": True,
        "broad_d40_source_domain": True,
        "species_rule_matches": {
            "largest_bank": True,
            "largest_d40_surplus": False,
            "banana_else_largest": False,
        },
    }
    result.update(changes)
    return result


def row(partition: str, agent: int, relation: str = "worker2_before_crop") -> dict:
    return {
        "partition": partition,
        "agent_id": agent,
        "transaction": transaction(relation, "bank_pick"),
    }


def test_species_rules_are_deterministic_and_use_plum_first_ties() -> None:
    assert largest_index([5, 5, 2, 1]) == 0
    assert largest_index([0, 0, 0, 0]) is None
    choices = species_rule_choices([5, 9, 2, 3, 0, 0])
    assert choices == {
        "largest_bank": 1,
        "largest_d40_surplus": 1,
        "banana_else_largest": 3,
    }


def test_two_supported_signatures_cover_both_partitions() -> None:
    rows = []
    for partition, base in (("discovery", 10), ("validation", 20)):
        count = 6 if partition == "discovery" else 10
        for index in range(count):
            relation = "worker2_before_crop" if index % 2 == 0 else "crop_before_worker2"
            rows.append(row(partition, base + (index // 2) % 2, relation))

    gate = archetype_gate(rows)

    assert gate["pass"]
    assert set(gate["nominated_signatures"]) == {
        "crop_before_worker2+bank_pick",
        "worker2_before_crop+bank_pick",
    }
    assert gate["selected_species_rule"] == "largest_bank"


def test_signature_fails_if_one_partition_lacks_receipt_support() -> None:
    rows = [row("discovery", 10 + index % 2) for index in range(6)]
    rows.extend(row("validation", 20 + index % 2) for index in range(10))
    for item in rows:
        if item["partition"] == "validation":
            item["transaction"]["receipt_before_worker_three"] = False

    gate = archetype_gate(rows)

    assert not gate["coverage_pass"]
    assert not gate["pass"]
