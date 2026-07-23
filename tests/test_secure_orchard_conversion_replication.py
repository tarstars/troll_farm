from __future__ import annotations

from cgauto.secure_orchard_conversion_replication import (
    analyze_replication,
    build_manifest,
)


def player() -> dict:
    return {"playerAgentId": 6560353, "submissionId": 41012883}


def test_manifest_freezes_exactly_the_older_disjoint_block() -> None:
    battles = [
        {"gameId": game_id, "done": True, "players": [player()]}
        for game_id in range(160, 0, -1)
    ]
    recent = list(range(160, 80, -1))
    manifest = build_manifest(battles, recent)
    assert manifest["replication"]["game_ids"] == list(range(80, 0, -1))
    assert manifest["excluded_recent_80"]["count"] == 80


def row(index: int, active: bool, loss: bool = False) -> dict:
    forces = 50 if active else 0
    return {
        "game_id": index,
        "opponent": f"opponent-{index % 4}",
        "margin": -1 if loss else 1,
        "probe_resident_stdout_equal": True,
        "unknown_diff_updates": 0,
        "resident_full_stream_exact": index < 40,
        "all_forces_on_ripe_apple": True,
        "admissible_forced_harvests": forces,
        "post_seed_replacement_forces": max(0, forces - 1),
        "final": {
            "apple": forces,
            "wood": 10,
            "successful_plants": 1,
            "opponent_crops": 2,
            "opponent_crop_wood": 3,
        },
    }


def test_replication_passes_only_with_all_predeclared_floors() -> None:
    rows = [row(index, index < 5, index < 2) for index in range(80)]
    report = analyze_replication(rows, [], {"replication": {"count": 80}})
    assert report["passed"]
    assert report["sustained_activated_games"] == 5
    assert report["activated_losses"] == 2
    assert report["post_seed_replacement_forces"] == 245


def test_replication_rejects_below_activation_floor() -> None:
    rows = [row(index, index < 4, index < 2) for index in range(80)]
    report = analyze_replication(rows, [], {"replication": {"count": 80}})
    assert not report["passed"]
    assert not report["integrity_and_replication_checks"][
        "minimum_sustained_activated_games"
    ]
