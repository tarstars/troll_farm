#!/usr/bin/env python3
"""Build a READ-ONLY variant of the gate (a different `gate*.rs.in`, optional text substitutions) into
`results/variants/<name>/` -- never into cgauto/submissions -- through the same chain, and run the gate read on it. For the
sensitivities the coordinator asked for (04:18Z): v1's forest read at one instead of half, etc.

    python3 claude_1/wood-charging-gate/variant_read.py --gate gate-v1.rs.in --sub 'forest = 4.0 *' 'forest = 8.0 *' --name v1-forest-x2
"""
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(REPO / "local_claude_1" / "third-troll"))
import make_third_troll as mk           # noqa: E402
import make_wood_gate as mwg            # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--gate", default="gate-v1.rs.in")
ap.add_argument("--sub", nargs=2, action="append", default=[])
ap.add_argument("--name", required=True)
ap.add_argument("--scratch", type=Path, default=HERE / "results" / "variants")
args = ap.parse_args()
gate = (HERE / args.gate).read_text()
for old, new in args.sub:
    assert gate.count(old) == 1, (old, gate.count(old))
    gate = gate.replace(old, new)
out = args.scratch / args.name; out.mkdir(parents=True, exist_ok=True)
mwg.REPL_GATE["text"] = gate + "            fn fallback_second_troll() -> Stats {\n"
mk.REPLACEMENTS = mwg.REPLACEMENTS; mk.STACKED = False
mk.ARM = out / "arm.rs"; mk.READABLE_EDITED = out / "readable.rs"; mk.SUBMISSION = out / f"candidate-wood-gate-variant-{args.name}.rs"
mk.REPORT = out / "round-trip.json"; mk.DIFF = out / "diff.diff"
rc = mk.main()
if rc:
    sys.exit(rc)
res = HERE / "results" / f"gate-read-{args.name}.json"
rc = subprocess.call([sys.executable, str(HERE / "gate_read.py"), "--arm", str(mk.ARM), "--out", str(res)])
# keep the round-trip record (with the arm's sha256); the variant's source files are rebuilt by this script
for f in (mk.ARM, mk.READABLE_EDITED, mk.SUBMISSION, mk.DIFF, out / "arm.rs.sha256", out / "readable.rs.sha256", out / f"candidate-wood-gate-variant-{args.name}.rs.sha256"):
    if f.exists():
        f.unlink()
sys.exit(rc)
