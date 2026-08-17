#!/usr/bin/env python3
"""H-STARVE-1 pool #1 — exact one-row-per-turn coverage, duplicate rejection, and RUNNER PARITY.

Three of the five pool-#1 repairs live here. Each is a check that FAILS LOUDLY rather than a
property anyone asserts.

## Why parity is proved rather than argued

My bespoke audit loop caused both of yesterday's worst defects: it omitted `referee.grow()` (so
the world was frozen) and it replaced the shared runner's fail-closed `RuntimeError` on early
stdout closure with a fail-open `break`. The standing rule is now "reuse shared runners or prove
parity". Diagnostics need stderr, which the shared runner does not capture, so I cannot simply
reuse it — therefore I **prove parity on every situation**: the diagnostic runner and
`regression_tests.run_binary_custom` must produce **byte-identical command streams**, or nothing
downstream is emitted.

## Coverage, exactly

For each situation and each own unit, the instrument must emit **exactly one** `HS2` row per turn
in `[turn_start, turn_end]` — no gaps, no duplicates — and **exactly one** `HS2CHOSEN` row per
turn. Aggregate counts were the previous instrument's weakness; this checks identity per row.
"""
from __future__ import annotations

import collections, json, re, subprocess, sys, tempfile, threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "t1"))
import fixture_harness as H     # noqa: E402
import fuzz_panel as fp         # noqa: E402
import regression_tests as rt   # noqa: E402

INSTR = HERE / "instrumented-hstarve2.rs"
ROW = re.compile(r"HS2 turn=(\d+) unit=(\d+) cell=(-?\d+),(-?\d+) branch=(\w+) "
                 r"endgame=(\w+) committed=(\w+) ncand=(\d+) kinds=([^\n]*)")
CHOSEN = re.compile(r"HS2CHOSEN turn=(\d+) line=([^\n]*)")


class CoverageError(Exception):
    """Any coverage or parity failure. Nothing downstream runs after one."""


def run_diagnostic(binary, referee, turns):
    """Same loop as regression_tests.run_binary_custom, plus stderr drained on a thread.

    apply() AND grow(), and a fail-CLOSED RuntimeError on early stdout closure — both of which
    my previous runner got wrong, in the two ways that mattered most.
    """
    header = referee.map_header()
    parts, lines = [header], []
    proc = subprocess.Popen([str(binary)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)
    chunks = []
    drain = threading.Thread(target=lambda: chunks.append(proc.stderr.read()), daemon=True)
    drain.start()
    try:
        proc.stdin.write(header); proc.stdin.flush()
        for _ in range(turns):
            block = referee.turn_text()
            parts.append(block)
            proc.stdin.write(block); proc.stdin.flush()
            line = proc.stdout.readline()
            if not line:
                raise CoverageError("candidate closed stdout early (fail-closed, as the shared "
                                    "runner does; my previous loop swallowed this with `break`)")
            line = line.rstrip("\n")
            lines.append(line)
            referee.apply(line)
            referee.grow()
        proc.stdin.close()
    finally:
        proc.wait()
        drain.join(timeout=30)
    return "".join(parts), "\n".join(lines) + "\n", "".join(chunks)


def check_parity(sit, cfg, plain_bin, instr_bin):
    spec = H.spec_for(sit, cfg)
    _, c_shared = rt.run_binary_custom(Path(plain_bin), fp.make_referee(spec), int(cfg["turns"]))
    _, c_diag, err = run_diagnostic(instr_bin, fp.make_referee(spec), int(cfg["turns"]))
    if c_shared.strip() != c_diag.strip():
        raise CoverageError(
            f"{sit['id']}: diagnostic runner DIVERGES from regression_tests.run_binary_custom. "
            f"Parity is the whole licence for using a custom loop; nothing is emitted.")
    return err


def check_coverage(sit, err):
    """Exactly one row per own unit per turn, and one CHOSEN row per turn. No gaps, no dupes."""
    w = sit["window"]
    lo, hi = w["turn_start"], w["turn_end"]
    own = {u[0] for u in sit["world_state_at_entry"]["units"] if u[1] == 0}

    seen = collections.Counter()
    for m in ROW.finditer(err):
        seen[(int(m.group(1)), int(m.group(2)))] += 1
    dupes = [k for k, n in seen.items() if n > 1]
    if dupes:
        raise CoverageError(f"{sit['id']}: DUPLICATE rows for {dupes[:5]} — a unit logged twice "
                            f"in one turn means the emit point runs more than once per decision.")
    missing = [(t, u) for t in range(lo, hi + 1) for u in own if (t, u) not in seen]
    if missing:
        raise CoverageError(f"{sit['id']}: MISSING rows for {missing[:5]} "
                            f"({len(missing)} of {(hi - lo + 1) * len(own)} expected) — a gap "
                            f"means some turns were never observed and any rate is wrong.")

    chosen = collections.Counter(int(m.group(1)) for m in CHOSEN.finditer(err))
    cd = [t for t, n in chosen.items() if n > 1]
    if cd:
        raise CoverageError(f"{sit['id']}: DUPLICATE chosen rows at turns {cd[:5]}")
    cm = [t for t in range(lo, hi + 1) if t not in chosen]
    if cm:
        raise CoverageError(f"{sit['id']}: MISSING chosen rows at turns {cm[:5]}")
    return len(seen), sum(chosen.values())


def main():
    only = sys.argv[1].split(",") if len(sys.argv) > 1 else ["OSC-001", "OSC-012", "OSC-031"]
    cfg = json.loads(H.CONFIG.read_text())
    sits = H.load_situations(only)
    with tempfile.TemporaryDirectory(prefix="hs2-") as wd:
        di, dp = Path(wd) / "i", Path(wd) / "p"
        di.mkdir(); dp.mkdir()
        instr = H.compile_candidate(INSTR, di)
        plain = H.compile_candidate(H.RESIDENT, dp)
        for sit in sits:
            err = check_parity(sit, cfg, plain, instr)
            rows, chosen = check_coverage(sit, err)
            print(f"  OK   {sit['id']}: parity IDENTICAL · {rows} unit-turn rows, "
                  f"{chosen} chosen rows, no gaps, no duplicates")
    print(f"\ncoverage + parity: PASS on {len(sits)} situations")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CoverageError as e:
        print(f"  FAIL {e}")
        sys.exit(1)
