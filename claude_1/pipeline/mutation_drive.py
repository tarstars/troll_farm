#!/usr/bin/env python3
"""Mutation drive for the fuzz panel (committed, not scratch).

Review B9 of `chatgpt_1/referee-train-repair-r2-review-2026-08-10.md` required
the mutation evidence to be reproducible from the committed packet.  The
DEFINITIONS live in `test_fuzz_panel.MUTATIONS` (id, blocker, pinning test,
exact `old` -> `new` byte edit of `fuzz_panel.py`); this is the driver that
applies each one, runs the whole self-test suite against the mutant and
records CAUGHT / SURVIVED.

A blocker closed by code that no test pins is not closed: a SURVIVOR is a
reportable defect in the test suite, not a curiosity.

    python3 mutation_drive.py                  # every mutation
    python3 mutation_drive.py M11 M12          # a subset, by id prefix

The mutant is written to `fuzz_panel.py` itself and the original bytes are
restored in a `finally`, with a sha256 check at the end -- a mutation driver
that leaves a mutant behind would poison every later result.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "fuzz_panel.py"

sys.path.insert(0, str(HERE))
from test_fuzz_panel import MUTATIONS          # noqa: E402


def run_suite() -> tuple[bool, str]:
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "test_fuzz_panel"],
        cwd=str(HERE), capture_output=True, text=True)
    return proc.returncode == 0, proc.stderr


def failing_tests(stderr: str) -> list:
    out = []
    for line in stderr.splitlines():
        if line.startswith(("FAIL: ", "ERROR: ")):
            out.append(line.split(" ", 1)[1].split(" (")[0])
    seen, uniq = set(), []
    for name in out:
        if name not in seen:
            seen.add(name)
            uniq.append(name)
    return uniq


def main(argv) -> int:
    wanted = argv[1:]
    original = TARGET.read_bytes()
    digest = hashlib.sha256(original).hexdigest()
    rows, survivors = [], []
    try:
        for mut in MUTATIONS:
            if wanted and not any(mut["id"].startswith(w) for w in wanted):
                continue
            src = original.decode()
            if src.count(mut["old"]) != 1:
                raise SystemExit("anchor rotted: %s" % mut["id"])
            TARGET.write_text(src.replace(mut["old"], mut["new"]))
            green, stderr = run_suite()
            names = failing_tests(stderr)
            rows.append((mut["id"], mut["blocker"], not green, names))
            if green:
                survivors.append(mut["id"])
            print("%-34s %-52s %s" % (
                mut["id"], mut["blocker"],
                "SURVIVED" if green else "CAUGHT by %d test(s): %s"
                % (len(names), ", ".join(names[:3]))))
    finally:
        TARGET.write_bytes(original)
        assert hashlib.sha256(TARGET.read_bytes()).hexdigest() == digest

    print()
    print("| id | blocker | result | failing tests | first caught by |")
    print("|---|---|---|---|---|")
    for mid, blocker, caught, names in rows:
        print("| `%s` | %s | **%s** | %d | `%s` |"
              % (mid, blocker, "CAUGHT" if caught else "SURVIVED",
                 len(names), names[0] if names else "-"))
    print()
    print("%d of %d caught, %d survived%s"
          % (len(rows) - len(survivors), len(rows), len(survivors),
             (": " + ", ".join(survivors)) if survivors else ""))
    return 1 if survivors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
