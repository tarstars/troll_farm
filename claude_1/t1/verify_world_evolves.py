#!/usr/bin/env python3
"""T-1 — prove the fixture harness runs an EVOLVING world, not a frozen one.

Written after the H-STARVE-1 runner bug (`88114a18`): my audit runner omitted
`referee.grow()`, so every measurement it produced came from a world where no plant ripened.
The T-1 harness uses the shared `regression_tests.run_binary_custom`, which calls both
`apply()` and `grow()` — but "it uses the shared runner, therefore it is fine" is an assertion,
and the whole lesson of that bug is that I assert instead of measuring.

So this measures it. A frozen world cannot ripen fruit and cannot consume plants; an evolving
one does both.
"""
import json, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fixture_harness as H


def main():
    cfg = json.loads(H.CONFIG.read_text())
    sit = H.load_situations(["OSC-006"])[0]
    with tempfile.TemporaryDirectory(prefix="t1-world-") as wd:
        binary = H.compile_candidate(H.RESIDENT, Path(wd))
        tr, _, _, _ = H.run_situation(sit, binary, cfg)

    fruit = [sum(p.fruits for p in tr.state(t).plants) for t in range(1, tr.T + 1)]
    size = [sum(p.size for p in tr.state(t).plants) for t in range(1, tr.T + 1)]
    ripened = [t for t, v in enumerate(fruit, 1) if v]

    checks = [
        ("fruit RIPENS at some point (impossible in a frozen world)", bool(ripened),
         f"turns {ripened[:6]}{'…' if len(ripened) > 6 else ''}"),
        ("total plant size CHANGES over the game", len(set(size)) > 1,
         f"{len(set(size))} distinct totals, {size[0]} -> {size[-1]}"),
    ]
    ok = True
    for name, passed, detail in checks:
        print(f"  {'OK  ' if passed else 'BAD '} {name}  [{detail}]")
        ok = ok and passed
    print("\nT-1 world evolution:", "VERIFIED" if ok else "FROZEN — same bug as H-STARVE-1")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
