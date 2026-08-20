#!/usr/bin/env python3
r"""Phase-2 gate: warm p95 per-turn latency — P1's cost MEASURED, not argued.

P1 adds a per-pair call (`self_blocked`) inside the two-unit cross product, which is the hot loop
of `select()`. The card's instruction is explicit: measure it. All FOUR arms are timed — both
bases and both their candidates — because a candidate's latency means nothing without its own
base beside it, and the two bases are not interchangeable.

`claude_1/t1/latency_probe.py`'s `timed_run`, `WARMUP` and `BUDGET_MS` are imported, not
restated. A second copy of a timing loop is a second copy of the arithmetic — the defect codex_1
required removed from the gate-1 runner on 2026-08-19.

Run:  python3 claude_1/picker2/latency.py
"""
import json, statistics, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for p in ("claude_1/t1", "claude_1/pipeline", "claude_1/banana-restoration-r2"):
    sys.path.insert(0, str(REPO / p))
import fixture_harness as H      # noqa: E402
import fuzz_panel as fp          # noqa: E402
import latency_probe as LP       # noqa: E402  -- THE timing path, not a copy

ARMS = {
    "cureC-base": REPO / "cgauto/submissions/submitted-sub41153619-cure-c-quiet.rs",
    "cureC-p1p2": HERE / "candidate-cureC-p1p2.rs",
    "door1-base": REPO / "claude_1/chop4c/candidate-door1.rs",
    "door1-p1p2": HERE / "candidate-door1-p1p2.rs",
}
SITUATIONS = ["OSC-004", "OSC-013", "OSC-017", "OSC-034"]
OUT = HERE / "latency-2026-08-20.json"


def main():
    cfg = json.loads(H.CONFIG.read_text())
    sits = H.load_situations(SITUATIONS)
    out, worst_ok = {}, True
    for label, src in ARMS.items():
        allw = []
        with tempfile.TemporaryDirectory(prefix="ps2-lat-") as wd:
            b = H.compile_candidate(src, Path(wd))
            for sit in sits:
                spec = H.spec_for(sit, cfg)
                warm = LP.timed_run(b, fp.make_referee(spec), int(cfg["turns"]))[LP.WARMUP:]
                allw.extend(warm)
        p95 = statistics.quantiles(allw, n=100)[94]
        ok = p95 < LP.BUDGET_MS
        worst_ok &= ok
        out[label] = {"warm_turns": len(allw), "median_ms": round(statistics.median(allw), 4),
                      "p95_ms": round(p95, 4), "max_ms": round(max(allw), 4),
                      "budget_ms": LP.BUDGET_MS, "met": ok}
        print(f"  {label:11} {len(allw)} warm turns  median {statistics.median(allw):.4f} ms  "
              f"p95 {p95:.4f} ms  max {max(allw):.4f} ms  -> {'MET' if ok else 'NOT MET'}")
    for base in ("cureC", "door1"):
        d = out[f"{base}-p1p2"]["p95_ms"] - out[f"{base}-base"]["p95_ms"]
        out[f"{base}-p1p2"]["p95_delta_vs_base_ms"] = round(d, 4)
        print(f"  {base}: P1+P2 costs {d:+.4f} ms at p95 vs its own base")
    out["_limits"] = ("Measured on this host under no competing load, on four situations rather "
                      "than the 240-game corpus; the timing includes the Python referee's own "
                      "per-turn work, so it OVERSTATES the bot's cost rather than understating "
                      "it. The candidate and base arms play DIFFERENT games after P1 diverges, "
                      "so the delta is a comparison of two trajectories, not of the same turns.")
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"  latency gate (warm p95 < {LP.BUDGET_MS:.0f} ms, all four arms): "
          f"{'MET' if worst_ok else 'NOT MET'}")
    print(f"wrote {OUT}")
    return 0 if worst_ok else 1


if __name__ == "__main__":
    sys.exit(main())
