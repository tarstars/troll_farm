from __future__ import annotations

import hashlib
import json
from pathlib import Path

from cgauto.verify_b4_4_claims import (
    EXPECTED_ANCHORS,
    anchors_match,
    birth_band,
    load_games_and_prefix_hashes,
    summarize_replay_rows,
)


def test_birth_bands_preserve_early_and_late_purpose_boundary() -> None:
    assert birth_band(1) == "early_1_50"
    assert birth_band(50) == "early_1_50"
    assert birth_band(51) == "middle_51_250"
    assert birth_band(250) == "middle_51_250"
    assert birth_band(251) == "late_251_plus"


def test_prefix_hashes_are_over_exact_newline_records(tmp_path: Path) -> None:
    path = tmp_path / "games.jsonl"
    lines = [
        json.dumps({"gameId": 1}) + "\n",
        json.dumps({"gameId": 2}) + "\n",
        json.dumps({"gameId": 3}) + "\n",
    ]
    path.write_text("".join(lines))
    games, hashes = load_games_and_prefix_hashes(path, (1, 2, 3))
    assert [row["_n2_record_index"] for row in games] == [1, 2, 3]
    assert hashes[2] == hashlib.sha256("".join(lines[:2]).encode()).hexdigest()
    assert hashes[3] == hashlib.sha256("".join(lines).encode()).hexdigest()


def test_anchor_check_is_joint_not_occurrence_only() -> None:
    structural = dict(EXPECTED_ANCHORS)
    structural["resident_mean_roster"] = 2
    structural["resident_median_roster"] = 2
    matched, checks = anchors_match(structural)
    assert matched
    structural["peer_weak_agents"] = 12
    matched, checks = anchors_match(structural)
    assert not matched
    assert not checks["peer_weak_agents"]
    structural = dict(EXPECTED_ANCHORS)
    structural["resident_mean_roster"] = 2
    structural["resident_median_roster"] = 2
    structural.pop("clean_games")
    matched, checks = anchors_match(structural)
    assert not matched
    assert not checks["clean_games"]


def test_replay_summary_keeps_conditional_coverage_and_generation_purpose() -> None:
    rows = [
        {
            "first_plant_turn": 22,
            "actor_created": 2,
            "actor_created_reaped": 1,
            "has_self_plant_self_chop": True,
            "generation_outcomes": [
                {
                    "band": "early_1_50",
                    "actor_harvested": True,
                    "actor_chopped": False,
                    "opponent_harvested": False,
                    "opponent_chopped": False,
                    "survived_to_end": True,
                    "actor_fruit_gained": 4,
                    "actor_wood_gained": 0,
                },
                {
                    "band": "late_251_plus",
                    "actor_harvested": False,
                    "actor_chopped": True,
                    "opponent_harvested": False,
                    "opponent_chopped": False,
                    "survived_to_end": False,
                    "actor_fruit_gained": 0,
                    "actor_wood_gained": 3,
                },
            ],
        },
        {
            "first_plant_turn": None,
            "actor_created": 0,
            "actor_created_reaped": 0,
            "has_self_plant_self_chop": False,
            "generation_outcomes": [],
        },
    ]
    summary = summarize_replay_rows(rows)
    assert summary["first_plant_turn"]["n_reached"] == 1
    assert summary["first_plant_turn"]["n_total"] == 2
    assert summary["first_plant_turn"]["coverage"] == 0.5
    assert summary["actor_generations"]["pooled_reaped_coverage"] == 0.5
    assert (
        summary["generation_outcomes_by_birth_band"]["early_1_50"][
            "actor_fruit_gained"
        ]
        == 4
    )
    assert (
        summary["generation_outcomes_by_birth_band"]["late_251_plus"][
            "actor_wood_gained"
        ]
        == 3
    )
