#!/usr/bin/env python3
"""Control C-15, fixture half — every changed fixture named, with its score delta.

G-0 §8 requires every game changed in play to be named. This is that list for the 34 frozen
situations: the champion base against `arm-instrument.rs`, scored with `fuzz_panel.score` (the
panel's own scoring function, not a re-implementation), plus the opponent's score so a delta
cannot be read as a gain when it is the opponent that fell.

    python3 claude_1/cure2/named_costs_fixtures.py [OSC-006,OSC-007]
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for _p in ("claude_1/t1", "claude_1/pipeline", "claude_1/banana-restoration-r2"):
    sys.path.insert(0, str(REPO / _p))

import fixture_harness as fh          # noqa: E402
import fuzz_panel as fp               # noqa: E402
import regression_tests as rt         # noqa: E402
import semantic_harness as sh         # noqa: E402

BASE = REPO / "cgauto" / "submissions" / "candidate-door1-pure-deletion.rs"
ARM = HERE / "arm-instrument.rs"


def main() -> int:
    only = sys.argv[1].split(",") if len(sys.argv) > 1 else None
    cfg = json.loads(fh.CONFIG.read_text())
    sits = fh.load_situations(only)
    rows = []
    with tempfile.TemporaryDirectory(prefix="cure2-costs-") as wd:
        wd = Path(wd)
        bins = {}
        for name, src in (("base", BASE), ("arm", ARM)):
            binary = wd / f"{name}.bin"
            sh.compile_text(src.read_text(), binary, crate=f"cure2_costs_{name}")
            bins[name] = binary
        for sit in sits:
            got = {}
            for name, binary in bins.items():
                spec = fh.spec_for(sit, cfg)
                ref = fp.make_referee(spec)
                rt.run_binary_custom(binary, ref, int(cfg["turns"]))
                got[name] = (fp.score(ref.inv), fp.score(ref.opp_inv), list(ref.inv))
            delta = got["arm"][0] - got["base"][0]
            rows.append({"id": sit["id"], "base_score": got["base"][0],
                         "arm_score": got["arm"][0], "delta": delta,
                         "base_opponent": got["base"][1], "arm_opponent": got["arm"][1],
                         "base_inventory": got["base"][2], "arm_inventory": got["arm"][2]})
            mark = "SAME" if delta == 0 else ("BETTER" if delta > 0 else "WORSE")
            print(f"  {mark:<7} {sit['id']:<10} base {got['base'][0]:>5}  "
                  f"arm {got['arm'][0]:>5}  delta {delta:+}")
    changed = [r for r in rows if r["delta"]]
    report = {
        "control": "C-15 named costs (34 frozen fixtures)",
        "task": "20260825-dance-cure-candidate-2-swap",
        "base": str(BASE.relative_to(REPO)), "arm": str(ARM.relative_to(REPO)),
        "fixtures": len(rows), "changed_score": len(changed),
        "better": sum(1 for r in changed if r["delta"] > 0),
        "worse": sum(1 for r in changed if r["delta"] < 0),
        "total_delta": sum(r["delta"] for r in rows),
        "rows": rows,
    }
    out = HERE / "results" / "named-costs-fixtures.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"\n  {len(changed)} of {len(rows)} fixtures changed score: "
          f"{report['better']} better, {report['worse']} worse, "
          f"net {report['total_delta']:+} -> {out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
