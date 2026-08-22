#!/usr/bin/env python3
r"""Control: can the de-novo direction be SEEN on this data at all?

Both decompositions returned **0 de-novo**, and `phase2_decompose.py` therefore reports
`both_directions_exercised: false`. A zero from a check that has never been observed rejecting is
worth nothing — that is the inert-check failure this programme shipped three times in 08-15→17.

So the control is the cheapest possible one: **swap the arms**. Feed the same two panels to the
same `decompose()` with the floor playing the candidate's role. Every game the real run called
HEALED must come back as DE-NOVO. If it does, the de-novo bucket demonstrably fills on this exact
data with this exact code, and the real run's 0 is a measurement rather than a silence.

This proves the DIRECTION is observable. It does not prove the candidate causes no regression
anywhere — only that on these 240 keyed games, no game blocks under the candidate that did not
block under its matched floor.

Run:  python3 claude_1/picker2/denovo_direction_control.py
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "chop4c"))
import phase2_decompose as D     # noqa: E402

PAIRS = {
    "cureC": ("claude_1/picker2/panel-cureC-cand.json", "claude_1/chop4c/osc031-phase2-floor.json"),
    "door1": ("claude_1/picker2/panel-door1-cand.json", "claude_1/picker2/panel-door1-floor.json"),
}
OUT = HERE / "denovo-direction-control-2026-08-20.json"


def main():
    report, ok = {}, True
    for base, (cp, fp) in PAIRS.items():
        _, cand = D.load(cp)
        _, floor = D.load(fp)
        real = D.decompose(cand, floor)
        swapped = D.decompose(floor, cand)          # floor plays the candidate's role
        # The identity that must hold if the buckets mean what they say.
        agrees = ({(r["map_id"], r["seat"]) for r in real["healed"]} ==
                  {(r["map_id"], r["seat"]) for r in swapped["de_novo"]})
        live = len(swapped["de_novo"]) > 0 and agrees
        ok &= live
        report[base] = {
            "real_de_novo": len(real["de_novo"]), "real_healed": len(real["healed"]),
            "swapped_de_novo": len(swapped["de_novo"]),
            "swapped_de_novo_equals_real_healed": agrees,
            "de_novo_direction_observable": live,
            "de_novo_keys_when_swapped": [f"{r['map_id']}/seat{r['seat']}"
                                          for r in swapped["de_novo"]]}
        print(f"  {base}: real de-novo {len(real['de_novo'])}, real healed {len(real['healed'])}; "
              f"arms swapped -> de-novo {len(swapped['de_novo'])} "
              f"(same keys as healed: {agrees}) -> direction "
              f"{'OBSERVABLE' if live else 'NOT OBSERVABLE'}")
    OUT.write_text(json.dumps(
        {"task": "20260820-pair-selector-anti-benching", "phase": 2,
         "control": "swap the arms; every HEALED game must reappear as DE-NOVO",
         "claim_supported": "the de-novo bucket fills on this data with this code, so the real "
                            "run's 0 de-novo is a measurement and not an inert check",
         "not_claimed": "that the candidate regresses nowhere outside these 240 keyed games",
         "bases": report, "met": ok}, indent=2, sort_keys=True) + "\n")
    print(f"  de-novo direction control: {'MET' if ok else 'NOT MET'}")
    print(f"wrote {OUT}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
