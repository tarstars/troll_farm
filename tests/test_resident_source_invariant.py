"""The byte-sacred resident source invariant, as a first-class guard.

AGENTS.md, coordination/multi-agent-protocol.md sec 7 and coordination/peer-prompt.md sec 4
all state that rust/src/bin/yamo_orchard_live.rs must stay byte-exact at SHA-256 prefix
fff6669b, because rust/src/lib.rs re-exports it as troll_farm::resident_policy and any
working-tree diff silently contaminates every concurrently running experiment.

Two things this file fixes:

1. The invariant was asserted only incidentally, inside tests/test_analyze_resident_denial_scoring.py,
   which is a test about denial scoring. A guard on the project's most load-bearing hazard
   should not be a side effect of an unrelated test.

2. **The rule names one file; two must hold.** rust/src/d171a_control_resident_snapshot.rs is
   a byte-identical second copy, pulled in as a module via `#[path = ...]` by
   cgauto/n4_candidate_pair_value_audit.py, cgauto/n6_denial_weight_sweep.py and several
   experiment runners. Nothing checked it. If the two ever diverge, experiments that go
   through the snapshot path silently measure a different program from the one the
   protocol pins -- the wrong-artefact failure class this project has logged repeatedly.
"""

import hashlib
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

SACRED_SHA256 = "fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f"

# Both are library-visible entry points to the same resident program.
PINNED_PATHS = (
    "rust/src/bin/yamo_orchard_live.rs",
    "rust/src/d171a_control_resident_snapshot.rs",
)


def _digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_every_pinned_resident_path_exists() -> None:
    for rel in PINNED_PATHS:
        assert (ROOT / rel).is_file(), f"pinned resident source is missing: {rel}"


def test_every_pinned_resident_path_matches_the_sacred_digest() -> None:
    actual = {rel: _digest(ROOT / rel) for rel in PINNED_PATHS}
    wrong = {rel: got for rel, got in actual.items() if got != SACRED_SHA256}
    assert not wrong, (
        "resident source digest drift -- every concurrently running experiment is "
        f"contaminated until this is restored byte-exact.\n  expected {SACRED_SHA256}\n"
        + "".join(f"  got      {got}  {rel}\n" for rel, got in wrong.items())
    )


def test_the_two_pinned_paths_are_byte_identical() -> None:
    primary, snapshot = (ROOT / rel for rel in PINNED_PATHS)
    assert primary.read_bytes() == snapshot.read_bytes(), (
        f"{PINNED_PATHS[0]} and {PINNED_PATHS[1]} have diverged. Experiments reached "
        "through the snapshot path would measure a different program from the one the "
        "protocol pins."
    )
