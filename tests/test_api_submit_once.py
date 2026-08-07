import hashlib
from pathlib import Path

from cgauto import api_submit_once


def source(tmp_path: Path) -> tuple[Path, str]:
    path = tmp_path / "bot.rs"
    path.write_text("fn main() {}\n")
    return path, hashlib.sha256(path.read_bytes()).hexdigest()


def test_submit_uses_one_canonical_mutation_call(monkeypatch, tmp_path: Path) -> None:
    path, digest = source(tmp_path)
    calls = []

    def fake_call(service, method, payload):
        calls.append((service, method, payload))
        if method == "generateSessionFromPuzzlePrettyId":
            return 200, '{"handle":"private-handle"}'
        return 200, "41000001"

    monkeypatch.setattr(api_submit_once, "call", fake_call)
    result = api_submit_once.submit_once(path, digest)
    assert result["accepted"] is True
    assert result["submission_id"] == 41000001
    assert result["mutation_calls"] == 1
    assert [(service, method) for service, method, _ in calls] == [
        ("Puzzle", "generateSessionFromPuzzlePrettyId"),
        ("TestSession", "submit"),
    ]


def test_ambiguous_submit_stops_without_fallback(monkeypatch, tmp_path: Path) -> None:
    path, digest = source(tmp_path)
    calls = []

    def fake_call(service, method, payload):
        calls.append((service, method, payload))
        if method == "generateSessionFromPuzzlePrettyId":
            return 200, '{"handle":"private-handle"}'
        return None, "TimeoutError"

    monkeypatch.setattr(api_submit_once, "call", fake_call)
    result = api_submit_once.submit_once(path, digest)
    assert result["accepted"] is False
    assert result["ambiguous"] is True
    assert result["mutation_calls"] == 1
    assert len(calls) == 2
