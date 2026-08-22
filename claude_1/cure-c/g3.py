#!/usr/bin/env python3
"""Cure C — GATE G3. Warm p95 per-turn latency and thread parity.

Task `20260817-cure-c-implementation` §3.3: *"warm p95 < 50 ms (per-turn probe, T-1 pattern);
thread parity (1-proc == N-proc, row-identical)."*

Independent of the G1 clause-3 and G2 rulings, so it is measured now rather than left as an
unknown for whichever way those go.

## Latency

Reuses `claude_1/t1/latency_probe.timed_run` rather than re-timing by hand — a second timing loop
would measure a slightly different thing and the two numbers would not be comparable. The
resident is measured in the same run, so the candidate's cost is reported as a DIFFERENCE against
a baseline taken on the same host in the same conditions, not as an absolute against a budget that
nothing else was held to.

The probe's own stated limit still applies and is not softened here: it is one host under no
competing load, it includes the Python referee's per-turn work, and it covers three situations
rather than the full corpus. It therefore OVERSTATES the bot's cost.

## Thread parity, with a negative control

Parity is checked by hashing every game row (minus wall-clock fields) from a `processes=8` run and
a `processes=1` run of the SAME config.

**A comparator that has only ever returned "identical" is not evidence of identity.** So the same
comparator is run against the floor JSON, where it must report a DIFFERENCE. Without that, a
row-extractor that silently dropped every field would report perfect parity forever — which is
exactly the inert-check failure this task already hit once, on the P4 field that did not exist.
"""
from __future__ import annotations

import hashlib
import json
import statistics
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1/t1"))
import fixture_harness as H     # noqa: E402
import fuzz_panel as fp         # noqa: E402
import latency_probe as L       # noqa: E402

CANDIDATE = HERE / "candidate-cure-c-quiet.rs"
EIGHT_PROC = HERE / "g2-candidate.json"
ONE_PROC = HERE / "g3-parity-1proc.json"
FLOOR = HERE / "g2-matched-floor.json"
BUDGET_MS = 50.0
VOLATILE = ("wall_time_seconds",)


class G3Error(Exception):
    """Fail-closed."""


def row_digest(path):
    d = json.loads(Path(path).read_text())
    rows = {}
    for g in d["games"]:
        r = {k: v for k, v in g.items() if k not in VOLATILE}
        rows[(g["map_id"], g["seat"])] = json.dumps(r, sort_keys=True)
    if not rows:
        raise G3Error(f"{path}: no rows extracted — the comparator would report parity vacuously")
    blob = "".join(rows[k] for k in sorted(rows))
    return rows, hashlib.sha256(blob.encode()).hexdigest()


def latency(label, src, cfg, sits):
    warm = []
    with tempfile.TemporaryDirectory(prefix="curec-g3-") as wd:
        binary = H.compile_candidate(src, Path(wd))
        for sit in sits:
            lat = L.timed_run(binary, fp.make_referee(H.spec_for(sit, cfg)), int(cfg["turns"]))
            warm.extend(lat[L.WARMUP:])
    p95 = statistics.quantiles(warm, n=100)[94]
    print(f"  {label:<18} warm turns {len(warm)}  median {statistics.median(warm):.3f} ms  "
          f"p95 {p95:.3f} ms  max {max(warm):.3f} ms")
    return {"warm_turns": len(warm), "median_ms": statistics.median(warm),
            "p95_ms": p95, "max_ms": max(warm)}


def main():
    cfg = json.loads(H.CONFIG.read_text())
    sits = H.load_situations(["OSC-001", "OSC-012", "OSC-031"])

    print("=== G3.1 warm p95 per-turn latency (candidate reported against the resident) ===")
    res = latency("resident", H.RESIDENT, cfg, sits)
    cand = latency("cure-C candidate", CANDIDATE, cfg, sits)
    lat_ok = cand["p95_ms"] < BUDGET_MS
    print(f"  budget {BUDGET_MS:.0f} ms -> {'MET' if lat_ok else 'NOT MET'} "
          f"(candidate p95 {cand['p95_ms']:.3f} ms; resident {res['p95_ms']:.3f} ms)")

    print("\n=== G3.2 thread parity: processes=8 vs processes=1, same config ===")
    rows8, h8 = row_digest(EIGHT_PROC)
    rows1, h1 = row_digest(ONE_PROC)
    if set(rows8) != set(rows1):
        raise G3Error("the two runs cover different games")
    differing = [k for k in rows8 if rows8[k] != rows1[k]]
    par_ok = not differing and h8 == h1
    print(f"  rows {len(rows8)}  differing {len(differing)}")
    print(f"  8-proc sha256 {h8}")
    print(f"  1-proc sha256 {h1}")
    print(f"  parity: {'IDENTICAL' if par_ok else 'DIFFERS'}")

    # NEGATIVE CONTROL — the same comparator against a run that MUST differ.
    rows_f, hf = row_digest(FLOOR)
    if hf == h8:
        raise G3Error("negative control FAILED: the comparator cannot distinguish the candidate "
                      "run from the floor run, so its 'identical' verdict means nothing")
    print(f"  negative control: floor rows hash {hf[:16]}… — comparator DOES distinguish runs")

    passed = lat_ok and par_ok
    out = HERE / "g3-results-2026-08-17.json"
    out.write_text(json.dumps({
        "gate": "G3", "task": "20260817-cure-c-implementation",
        "latency": {"resident": res, "candidate": cand, "budget_ms": BUDGET_MS,
                    "verdict": "MET" if lat_ok else "NOT MET",
                    "limit": "one host, no competing load, includes the Python referee's own "
                             "per-turn work, three situations — overstates the bot's cost"},
        "thread_parity": {"rows": len(rows8), "differing_rows": len(differing),
                          "sha256_8proc": h8, "sha256_1proc": h1,
                          "negative_control_floor_sha256": hf,
                          "verdict": "IDENTICAL" if par_ok else "DIFFERS"},
        "verdict": "PASS" if passed else "FAIL",
    }, indent=1, sort_keys=True) + "\n")
    print(f"\nG3: {'PASS' if passed else 'FAIL'} — wrote {out.relative_to(REPO)}")
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except G3Error as e:
        print(f"G3: FAIL — {e}")
        sys.exit(2)
