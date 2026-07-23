import hashlib
from pathlib import Path

from cgauto.make_norxondor_three_worker_candidate import (
    build_source,
    extract_game_module,
)
from cgauto.compact_rust_source import compact


REPO = Path(__file__).resolve().parent.parent
PROTOCOL = REPO / "rust/src/bin/yamo_orchard_live.rs"
POLICY = REPO / "rust/src/norxondor_three_worker_live_bot.rs"


def test_extracts_only_verified_game_module() -> None:
    result = extract_game_module(PROTOCOL.read_text())
    assert result.startswith("pub mod game {")
    assert "pub mod protocol" in result
    assert "pub mod bot" not in result
    assert "SecureOrchardBot" not in result


def test_candidate_is_deterministic_single_file_and_under_limit() -> None:
    formatted = build_source(PROTOCOL.read_text(), POLICY.read_text())
    first = compact(formatted)
    second = compact(build_source(PROTOCOL.read_text(), POLICY.read_text()))
    assert first == second
    assert len(first.encode()) <= 100_000
    assert "#[path" not in first
    assert "mod yamo" not in first
    assert "NorxondorThreeWorkerBot" in first
    assert hashlib.sha256(first.encode()).hexdigest() == hashlib.sha256(second.encode()).hexdigest()

