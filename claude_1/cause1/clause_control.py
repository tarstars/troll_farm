#!/usr/bin/env python3
r"""The REJECTION-SIDE control for the clause tap — task `20260821-osc032-033-cause-attribution`.

## Why this file exists at all

The first run of `cause_attribution.py` came back with a result I did not expect and must not
hide: across BOTH fixtures, over 400 measured calls, the clause tap emitted **zero** rejection
rows. Every `PS4CHOP` row it produced said `ACCEPTED`, and `PS4HARV` produced none at all,
because on the turns in question `view.plants` was empty — the loop body never ran.

That makes the charter's both-ways control pass in the direction the card asked for (the tap is
observed saying `ACCEPTED` on the fixtures' own employed turns, so it is not a constant
"rejected") and leaves the OPPOSITE risk completely untested: on these two fixtures a tap that
could only ever say `ACCEPTED` would look exactly the same. Eight of the nine chop clauses and
all seven idle-harvest clauses would be unobserved code.

I have shipped an instrument whose branch could not fire before and reported the zero as a
measurement. So the clause set is not reported as validated on the strength of the two audited
fixtures. This control runs the SAME probe binary over the whole 34-situation fixture corpus and
reports, per clause, whether it was OBSERVED firing — and names the ones that were not, instead
of leaving the reader to assume the set was exercised.

## What it gates, and what it only reports

GATE (fail-closed): at least one rejection clause of each family must be observed firing
somewhere in the corpus. If the reject side never fires anywhere, the tap is indistinguishable
from a constant and the G-1 package says so rather than shipping.

REPORTED, NOT GATED: the per-clause observed/unobserved table. Requiring all sixteen clauses to
fire on a 34-fixture corpus would be a gate on the corpus, not on the instrument, and would
tempt me to hunt for a board that lights up the last one. An unobserved clause is recorded as
unobserved — a known limit of the evidence, carried into the G-1 note in words.

Run:  python3 claude_1/cause1/clause_control.py
"""
from __future__ import annotations

import collections
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for p in ("claude_1/t1", "claude_1/hstarve1", "claude_1/banana-restoration-r2",
          "claude_1/pipeline", "claude_1/picker2", "claude_1/cause1"):
    sys.path.insert(0, str(REPO / p))
import clause_tap as CT         # noqa: E402
import coverage as C            # noqa: E402
import fixture_harness as H     # noqa: E402

MANIFEST = HERE / "route-probe-manifest-clause-2026-08-21.json"
SUBJECT = "door1-clause"
OUT = HERE / "clause-control-2026-08-21.json"


def main():
    man = json.loads(MANIFEST.read_text())[SUBJECT]
    cfg = json.loads(H.CONFIG.read_text())
    sits = H.load_situations()
    chop = collections.Counter()
    harv = collections.Counter()
    per_fixture = {}
    with tempfile.TemporaryDirectory(prefix="cause1-ctl-") as wd:
        wd = Path(wd)
        for d in ("p", "c"):
            (wd / d).mkdir()
        print(f"compiling champion {man['source_sha256'][:12]} + the clause tap ...")
        plain = H.compile_candidate(REPO / man["source"], wd / "p")
        probe = H.compile_candidate(REPO / man["probe"], wd / "c")
        for sit in sits:
            sid = sit["id"]
            # Parity is re-checked on EVERY situation, not only the two audited ones: the probe
            # is only allowed to print, everywhere it runs.
            err = C.check_parity(sit, cfg, plain, probe)
            parsed = CT.parse(err)
            fc, fh = collections.Counter(), collections.Counter()
            for gs in parsed["chop"].values():
                for g in gs:
                    if g["clause"] != "ENTERED":
                        fc[f"FN:{g['clause']}"] += 1
                    for p in g["plants"]:
                        fc[p["clause"]] += 1
            for gs in parsed["harvest"].values():
                for g in gs:
                    if g["clause"] != "ENTERED":
                        fh[f"FN:{g['clause']}"] += 1
                    for p in g["plants"]:
                        fh[p["clause"]] += 1
            chop.update(fc)
            harv.update(fh)
            per_fixture[sid] = {"chop": dict(fc), "harvest": dict(fh)}
            print(f"  {sid}  chop {dict(fc)}  harvest {dict(fh)}")

    chop_rejects = {k: v for k, v in chop.items() if k != "ACCEPTED"}
    harv_rejects = {k: v for k, v in harv.items() if k != "ACCEPTED"}
    unobserved_chop = [c for c in CT.CHOP_CLAUSES if c not in chop]
    unobserved_harv = [c for c in CT.HARV_CLAUSES if c not in harv]

    print(f"\nchop clauses observed      {dict(chop)}")
    print(f"chop clauses NOT observed  {unobserved_chop}")
    print(f"harvest clauses observed   {dict(harv)}")
    print(f"harvest NOT observed       {unobserved_harv}")

    failures = []
    if not chop_rejects:
        failures.append(
            "no rejection clause of `chop_candidates` fired anywhere in the 34-situation corpus, "
            "so on this evidence the chop tap is indistinguishable from a constant ACCEPTED.")
    if not harv_rejects:
        failures.append(
            "no rejection clause of `idle_harvest_candidates` fired anywhere in the corpus, so "
            "on this evidence the idle-harvest tap is indistinguishable from a constant.")
    if failures:
        raise CT.ClauseGateError("the rejection-side control FAILED and the clause set may not "
                                 "be reported as exercised:\n  " + "\n  ".join(failures))

    OUT.write_text(json.dumps({
        "task": "20260821-osc032-033-cause-attribution",
        "control": "rejection side of the clause tap, over the whole fixture corpus",
        "why": "on OSC-032 and OSC-033 the tap emitted ZERO rejection rows because view.plants "
               "was empty on the audited turns; the charter's both-ways control therefore tests "
               "only the ACCEPTED direction and leaves every rejecting clause unobserved",
        "probe": {"path": man["probe"], "sha256": man["probe_sha256"]},
        "situations": [s["id"] for s in sits],
        "gate": "at least one rejection clause of each family must be OBSERVED firing; the "
                "per-clause table is reported, not gated, so an unobserved clause is recorded as "
                "a limit of the evidence rather than hunted for",
        "chop_clause_counts": dict(chop),
        "chop_clauses_unobserved": unobserved_chop,
        "idle_harvest_clause_counts": dict(harv),
        "idle_harvest_clauses_unobserved": unobserved_harv,
        "per_fixture": per_fixture}, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
