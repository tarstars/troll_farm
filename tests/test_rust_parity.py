"""Guard that the Rust submission stays byte-identical to the Python bot.

The CodinGame submission is rust/src/main.rs; bot/main.py is the dev/sim/test
reference. Any strategy change must be applied to BOTH -- this test fails if they
drift. Skipped when the Rust toolchain isn't available.
"""
import importlib.util
import shutil
import subprocess
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent
_RUST_DIR = _REPO / "rust"


def _load_parity():
    spec = importlib.util.spec_from_file_location("parity", _RUST_DIR / "parity.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.skipif(shutil.which("cargo") is None, reason="cargo/rustc not installed")
def test_rust_bot_matches_python_bot():
    build = subprocess.run(
        ["cargo", "build", "--release"], cwd=_RUST_DIR,
        capture_output=True, text=True,
    )
    assert build.returncode == 0, f"cargo build --release failed:\n{build.stderr}"

    parity = _load_parity()
    for seed in (0, 1):
        matches, total, mismatches = parity.compare_seed(seed, verbose=False)
        assert total > 0
        assert matches == total, (
            f"Python<->Rust drift on seed {seed}: {total - matches}/{total} "
            f"turns differ, e.g. {mismatches[:3]}"
        )
