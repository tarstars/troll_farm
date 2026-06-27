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


def test_rust_has_no_nested_reference_patterns():
    """CG's rustc rejects explicit `&x` reference patterns nested in a tuple
    destructure under a `&Item`-taking closure (filter/find/any/...). Our local
    rustc 1.75 accepts them, so the edition compile-checks miss it -- this has
    broken the CG paste twice. Guard with a source scan: flag `|( ... &ident ... )`.
    """
    import re
    src = (_RUST_DIR / "src" / "main.rs").read_text()
    bad = []
    for i, line in enumerate(src.splitlines(), 1):
        if line.lstrip().startswith("//"):
            continue
        # Inspect each closure's PARAMETER list (between its two pipes). The unsafe
        # shape is a tuple destructure containing `&ident` (e.g. `|(c, &d)|`); a
        # top-level `|&x|` has no `(` in its params and is fine.
        for m in re.finditer(r"\|([^|]*)\|", line):
            params = m.group(1)
            if "(" in params and re.search(r"&[a-z_]", params):
                bad.append((i, line.strip()))
    assert not bad, (
        "nested `&` reference pattern(s) -- CG rustc rejects these; bind without "
        "`&` and deref in the body:\n" + "\n".join(f"  L{n}: {t}" for n, t in bad)
    )


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
