#!/usr/bin/env python3
"""Card 1 item (3a): warm p95 per-turn latency for the door-1 candidate and the cure-C floor.

Reuses `claude_1/t1/latency_probe.py`'s `timed_run`, `WARMUP` and `BUDGET_MS` rather than
restating them. A second copy of a timing loop is a second copy of the arithmetic, which is the
defect codex_1 required removed from the gate-1 runner on 2026-08-19; the same rule applies here.

Both arms are measured, because a candidate's latency means nothing without the floor's beside it.
"""
import json, statistics, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "claude_1/t1"))
sys.path.insert(0, str(REPO / "claude_1/pipeline"))
import fixture_harness as H      # noqa: E402
import fuzz_panel as fp          # noqa: E402
import latency_probe as LP       # noqa: E402  -- THE timing path, not a copy

SUBJECTS = {
    "door1-candidate": REPO / "claude_1/chop4c/candidate-door1.rs",
    "cureC-floor": REPO / "cgauto/submissions/submitted-sub41153619-cure-c-quiet.rs",
}
SITUATIONS = ["OSC-001", "OSC-012", "OSC-031"]


def main():
    cfg = json.loads(H.CONFIG.read_text())
    sits = H.load_situations(SITUATIONS)
    out, worst_ok = {}, True
    for label, src in SUBJECTS.items():
        allw = []
        with tempfile.TemporaryDirectory(prefix="c4c-lat-") as wd:
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
        print(f"  {label}: {len(allw)} warm turns  median {statistics.median(allw):.3f} ms  "
              f"p95 {p95:.3f} ms  max {max(allw):.3f} ms  -> {'MET' if ok else 'NOT MET'}")
    out["_limits"] = ("Measured on this host under no competing load; timing includes the Python "
                      "referee's own per-turn work, so it OVERSTATES the bot's cost rather than "
                      "understating it. Three situations, not the full 240-game corpus.")
    (REPO / "claude_1/chop4c/osc031-phase2-latency-2026-08-19.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"  latency gate (warm p95 < {LP.BUDGET_MS:.0f} ms, both arms): "
          f"{'MET' if worst_ok else 'NOT MET'}")
    return 0 if worst_ok else 1


if __name__ == "__main__":
    sys.exit(main())
