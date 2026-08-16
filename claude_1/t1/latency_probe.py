#!/usr/bin/env python3
"""T-1 acceptance gate 3 — warm p95 per-turn latency.

An average is not a p95. The panel's 19.4 s over 240x200 turns averages well under a
millisecond, but the gate is a tail statistic and must be measured as one.

Method: drive the compiled candidate through the real referee, timing each turn from "state
written to stdin" to "command line read from stdout". The first `WARMUP` turns are discarded —
that is what "warm" means — and p95 is taken over the remainder.
"""
import json, statistics, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fixture_harness as H   # noqa: E402
import fuzz_panel as fp       # noqa: E402

WARMUP = 10
BUDGET_MS = 50.0


def timed_run(binary, referee, turns):
    header = referee.map_header()
    lat = []
    proc = subprocess.Popen([str(binary)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            text=True)
    try:
        proc.stdin.write(header)
        proc.stdin.flush()
        for _ in range(turns):
            block = referee.turn_text()
            t0 = time.perf_counter()
            proc.stdin.write(block)
            proc.stdin.flush()
            line = proc.stdout.readline()
            t1 = time.perf_counter()
            if not line:
                break
            lat.append((t1 - t0) * 1000.0)
            referee.apply(line.rstrip("\n"))
            referee.grow()
        proc.stdin.close()
    finally:
        proc.wait()
    return lat


def main():
    cfg = json.loads(H.CONFIG.read_text())
    cand = HERE / "candidate-t1-swap.rs"
    sits = H.load_situations(["OSC-001", "OSC-012", "OSC-031"])
    import tempfile
    allw = []
    with tempfile.TemporaryDirectory(prefix="t1-lat-") as wd:
        b = H.compile_candidate(cand, Path(wd))
        for sit in sits:
            spec = H.spec_for(sit, cfg)
            lat = timed_run(b, fp.make_referee(spec), int(cfg["turns"]))
            warm = lat[WARMUP:]
            allw.extend(warm)
            p95 = statistics.quantiles(warm, n=100)[94] if len(warm) > 20 else max(warm)
            print(f"  {sit['id']}: {len(warm)} warm turns  median {statistics.median(warm):.2f} ms"
                  f"  p95 {p95:.2f} ms  max {max(warm):.2f} ms")
    p95 = statistics.quantiles(allw, n=100)[94]
    ok = p95 < BUDGET_MS
    print(f"\npooled warm turns: {len(allw)}  median {statistics.median(allw):.2f} ms"
          f"  p95 {p95:.2f} ms  max {max(allw):.2f} ms")
    print(f"gate 3 (warm p95 < {BUDGET_MS:.0f} ms): {'MET' if ok else 'NOT MET'}")
    print("\nLIMIT: measured on this host under no competing load, and the timing includes the")
    print("Python referee's own work on each turn, so it OVERSTATES the bot's cost rather than")
    print("understating it. Three situations, not the full corpus.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
