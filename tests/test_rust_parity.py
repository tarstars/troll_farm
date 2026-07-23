"""Submission-source safety guards.

The old Python bot and ``rust/src/main.rs`` intentionally represent different historical
strategies, so comparing them turn-by-turn no longer guards the live submission. The relevant
contract is now the immutable agent-6553250 artifact versus its formatted development copy.
"""
import hashlib
import importlib.util
import shutil
import subprocess
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent
_RUST_DIR = _REPO / "rust"
_LIVE_EXACT = _REPO / "cgauto" / "submissions" / "agent-6553250-yamo-orchard-live.min.rs"
_LIVE_FORMATTED = _RUST_DIR / "src" / "bin" / "yamo_orchard_live.rs"
_LIVE_SHA256 = "09fac1fefa24eac657dba16a75d802eee38e1269f4aa44413e1ca103df36fe7a"


def _load_parity():
    spec = importlib.util.spec_from_file_location("parity", _RUST_DIR / "parity.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("source", [_RUST_DIR / "src" / "main.rs", _LIVE_FORMATTED])
def test_rust_has_no_nested_reference_patterns(source):
    """CG's rustc rejects explicit `&x` reference patterns nested in a tuple
    destructure under a `&Item`-taking closure (filter/find/any/...). Our local
    rustc 1.75 accepts them, so the edition compile-checks miss it -- this has
    broken the CG paste twice. Guard with a source scan: flag `|( ... &ident ... )`.
    """
    import re
    src = source.read_text()
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


def test_live_artifact_checksum():
    assert hashlib.sha256(_LIVE_EXACT.read_bytes()).hexdigest() == _LIVE_SHA256


@pytest.mark.skipif(shutil.which("cargo") is None, reason="cargo/rustc not installed")
def test_live_exact_matches_formatted_source(tmp_path):
    build = subprocess.run(
        ["cargo", "build", "--release", "--bin", "yamo_orchard_live"], cwd=_RUST_DIR,
        capture_output=True, text=True,
    )
    assert build.returncode == 0, f"cargo build --release failed:\n{build.stderr}"

    exact_binary = tmp_path / "live_exact"
    compile_exact = subprocess.run(
        [
            "rustc",
            "--edition",
            "2021",
            "-O",
            "--crate-name",
            "yamo_live_exact",
            str(_LIVE_EXACT),
            "-o",
            str(exact_binary),
        ],
        capture_output=True,
        text=True,
    )
    assert compile_exact.returncode == 0, compile_exact.stderr

    parity = _load_parity()
    lines, _ = parity.build_full_input(0)
    input_text = "\n".join(lines) + "\n"
    formatted_binary = _RUST_DIR / "target" / "release" / "yamo_orchard_live"
    exact = subprocess.run(
        [exact_binary], input=input_text, capture_output=True, text=True, timeout=60
    )
    formatted = subprocess.run(
        [formatted_binary], input=input_text, capture_output=True, text=True, timeout=60
    )
    assert exact.returncode == formatted.returncode == 0
    assert exact.stdout == formatted.stdout
