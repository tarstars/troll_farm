#!/usr/bin/env python3
"""Controls for the post-B5 tree tests: a check that cannot fail is not a check.

Part 1 - the PRE-PATCH control: the runner as it stands on origin/main, driven
to the same completed block, records the verdict and STOPS. That is the gap the
patch fills, demonstrated rather than asserted.

Part 2 - MUTANTS: five one-line mutations of the patched runner, each of which
must turn the suite red. A mutation that survives means the guard naming it is
decorative.

    python3 claude_1/night-tree/mutation_control.py     # exit 0 = all controls held
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[2]
RUNNER = REPO / "cgauto/night_runner.py"
SUITE = REPO / "claude_1/night-tree/test_post_b5_tree.py"

MUTANTS = [
    ("band is closed at the bar",
     "return (\"extension\" if MATERIALITY_FLOOR <= abs(mean) < bar_for(n)",
     "return (\"extension\" if MATERIALITY_FLOOR <= abs(mean) <= bar_for(n)"),
    ("the bar ignores the block size (n=10 graded against the n=5 bar)",
     "PREREGISTERED_BARS = {5: 1.315, 10: 0.930}",
     "PREREGISTERED_BARS = {5: 1.315, 10: 1.315}"),
    ("extension appends three pairs, not five",
     "EXTENSION_PAIRS = 5", "EXTENSION_PAIRS = 3"),
    ("the session-3 switch is never applied",
     "        if switch is not None:\n            state, state_path, ledger = switch",
     "        if False:\n            state, state_path, ledger = switch"),
    ("a lint-rejected morning sheet is committed anyway",
     "    if lint.returncode == 0:\n        return path",
     "    if True:\n        return path"),
    ("the extension forgets to submit the next arm",
     "                nxt = submit_next(state, state_path, ledger)\n                next_note = (\n                    f\"The score landed",
     "                nxt = state[\"plan\"][len(state[\"reads\"])]\n                next_note = (\n                    f\"The score landed"),
]


def run_suite() -> tuple[int, str]:
    proc = subprocess.run([sys.executable, str(SUITE)], cwd=REPO,
                          capture_output=True, text=True)
    return proc.returncode, proc.stderr


def prepatch_control() -> str:
    """Drive origin/main's runner to a completed block; show that it stops."""
    src = subprocess.run(["git", "show", "origin/main:cgauto/night_runner.py"],
                         cwd=REPO, capture_output=True, text=True, check=True).stdout
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="prepatch-"))
    mod_path = tmp / "night_runner_prepatch.py"
    mod_path.write_text(src)
    spec = importlib.util.spec_from_file_location("nr_prepatch", mod_path)
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)

    sys.path.insert(0, str(REPO / "claude_1/night-tree"))
    suite = importlib.util.spec_from_file_location("suite", SUITE)
    smod = importlib.util.module_from_spec(suite)
    suite.loader.exec_module(smod)

    st = smod.completed_state(2.0)
    st["reads"] = st["reads"][:-1]
    sp, lg = tmp / "state.json", tmp / "ledger.md"
    sp.write_text(json.dumps(st, indent=1))
    lg.write_text("# ledger\n")
    old.submit = lambda arm: {"submission_id": 1, "accepted": True}
    old.read_arena = lambda: {"rank": 30, "total": 176, "league": "Legend",
                              "score": 21.0, "agent_id": "6600001",
                              "battles": 160, "read_at": "01:20:00Z"}
    old.git_publish = lambda *a, **k: None
    argv = sys.argv[:]
    sys.argv = ["night_runner.py", "--state", str(sp), "--ledger", str(lg)]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = old.main()
    sys.argv = argv
    ledger = lg.read_text()
    assert rc == 0, rc
    assert "BLOCK COMPLETE" in ledger, ledger
    for absent in ("EXTENSION", "SESSION 3", "A6"):
        assert absent not in ledger, f"pre-patch runner already does {absent}"
    return (f"pre-patch runner: exit {rc}, stdout {buf.getvalue().strip()!r}; "
            f"ledger has BLOCK COMPLETE and NO extension, NO session 3, "
            f"no further submission")


def main() -> int:
    print("== part 1: pre-patch control ==")
    print(" ", prepatch_control())

    print("\n== part 2: mutants (each must turn the suite red) ==")
    original = RUNNER.read_text()
    rc, _ = run_suite()
    if rc != 0:
        print("  ABORT: the suite is not green before mutation")
        return 1
    print("  baseline: suite green on the unmutated runner")
    survivors = []
    try:
        for name, old, new in MUTANTS:
            if original.count(old) != 1:
                survivors.append((name, f"anchor matched {original.count(old)}x"))
                continue
            RUNNER.write_text(original.replace(old, new))
            rc, err = run_suite()
            failed = [l for l in err.splitlines() if l.startswith(("FAIL:", "ERROR:"))]
            status = "KILLED" if rc != 0 else "SURVIVED"
            print(f"  {status:8} {name}  ({len(failed)} test(s) red)")
            for line in failed[:3]:
                print(f"           {line}")
            if rc == 0:
                survivors.append((name, "suite stayed green"))
    finally:
        RUNNER.write_text(original)
    rc, _ = run_suite()
    print(f"\n  restored runner: suite {'green' if rc == 0 else 'RED'}")
    if survivors or rc != 0:
        for name, why in survivors:
            print(f"  SURVIVOR: {name} — {why}")
        return 1
    print("\nall controls held")
    return 0


if __name__ == "__main__":
    sys.exit(main())
