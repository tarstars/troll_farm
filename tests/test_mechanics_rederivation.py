from pathlib import Path

from cgauto.mechanics_rederivation_audit import (
    REFEREE_COMMIT,
    d33_evidence,
    known_boundaries,
    local_dynamic_checks,
    rust_engine_evidence,
)


def test_local_dynamic_mechanics_edges_match_primary_source_expectations() -> None:
    checks = local_dynamic_checks()

    assert len(checks) >= 10
    assert {item["status"] for item in checks} == {"MATCH"}


def test_d33_official_map_generator_is_still_the_frozen_exact_source() -> None:
    result = d33_evidence()

    assert result["status"] == "MATCH"
    assert result["confirmation_games"] == result["confirmation_passes"] == 120
    assert result["failure_counts"] == {}
    assert result["frozen_source_sha256"] == result["current_source_sha256"]


def test_rust_engine_is_still_the_frozen_source_with_expected_mechanics() -> None:
    result = rust_engine_evidence()

    assert result["status"] == "MATCH"
    assert result["expected_sha256"] == result["frozen_source_sha256"]
    assert result["frozen_source_sha256"] == result["current_source_sha256"]
    assert {item["status"] for item in result["anchors"].values()} == {"MATCH"}


def test_known_a2_boundaries_are_detected_from_source_shapes() -> None:
    referee_sources = {
        "src/main/java/engine/Board.java": (
            "return closest.get(random.nextInt(closest.size()));"
        ),
        "src/main/java/engine/task/Task.java": "if (unit.getPlayer() == player)",
    }

    boundaries = known_boundaries(referee_sources)

    assert [item["status"] for item in boundaries] == ["MISMATCH", "MISMATCH"]
    assert boundaries[0]["impact"].startswith("A2_BLOCKING")
    assert "ZERO_INVALID_COMMAND" in boundaries[1]["impact"]


def test_primary_referee_pin_is_a_full_git_sha() -> None:
    assert len(REFEREE_COMMIT) == 40
    int(REFEREE_COMMIT, 16)


def test_audit_does_not_vendor_primary_referee_source() -> None:
    repo = Path(__file__).resolve().parents[1]

    assert not (repo / "referee").exists()
    assert not (repo / "Troll-Farm").exists()
