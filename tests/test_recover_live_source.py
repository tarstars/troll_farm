"""Unit tests for the read-only IDE-source recovery helper."""

import hashlib

import pytest

from cgauto.recover_live_source import find_source, write_exact


def test_find_source_walks_nested_payload() -> None:
    assert find_source({"current": {"answer": {"code": "fn main() {}"}}}) == "fn main() {}"


def test_find_source_requires_unique_candidate() -> None:
    with pytest.raises(RuntimeError, match="found 2"):
        find_source(["fn main() {}", {"code": "fn main(){println!(\"x\");}"}])


def test_write_exact_writes_checksum_and_refuses_drift(tmp_path) -> None:
    output = tmp_path / "live.rs"
    digest = write_exact(output, "fn main() {}")

    assert digest == hashlib.sha256(b"fn main() {}").hexdigest()
    assert output.read_text() == "fn main() {}"
    assert output.with_name("live.rs.sha256").read_text() == f"{digest}  live.rs\n"

    with pytest.raises(RuntimeError, match="refusing to overwrite"):
        write_exact(output, "fn main() { panic!() }")
