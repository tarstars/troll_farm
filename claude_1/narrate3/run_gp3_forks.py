#!/usr/bin/env python3
"""Live controls for NARRATE v3: forks of the instrument that must change the measurement.

A field that always agrees with the field beside it measures nothing. These forks each break ONE
thing and the expected complaint is written down before the run:

  attest-absent    telemetry-only: forces `available` to ABSENT for the lowest own id. Play must
                   stay byte-identical (it touches no selection input) and ABSENT rows must appear
                   on the wire, decoding as neither NONE nor a concrete target. This is the only
                   attestation of the third state, because the 34 fixtures never produce an empty
                   candidate vector on their own.
  poison-worst     `available` takes the WORST candidate instead of the best. The lone-unit tie
                   parity check must FIRE: on a one-unit turn production IS the lone-unit max_by.
  poison-pair      pair compatibility always refused, so the best-pair branch can never fire.
                   Play must diverge and the discarded-want census must move.
  poison-score     the pair branch keeps the worst-scoring pair. Play must diverge and the
                   discarded-want census must move.

The poisons are expected to FAIL parity. That is the point: a poison that still passes would mean
the gate is inert.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUBSET = "OSC-001,OSC-004,OSC-009,OSC-017,OSC-025,OSC-031"

FORKS = [
    ("attest-absent", "fork-attest-absent.rs", None,
     "parity holds and ABSENT appears, distinct from NONE and from a concrete target"),
    # Full corpus, not the subset: the subset contains ZERO lone-unit turns, so the tie-parity
    # check would be vacuous there. The full 34 carry 619 of them.
    ("poison-worst", "fork-poison-worst-available.rs", None,
     "the lone-unit tie parity check FIRES, and the discarded-want census collapses"),
    ("poison-pair", "fork-poison-pair-incompatible.rs", SUBSET,
     "play diverges from the base and the discarded-want census moves"),
    ("poison-score", "fork-poison-score-loss.rs", SUBSET,
     "play diverges from the base and the discarded-want census moves"),
]


def run(instrument, only, out):
    cmd = [sys.executable, str(HERE / "run_gp3_parity.py"),
           "--instrument", str(HERE / instrument), "--out", str(out)]
    if only:
        cmd += ["--only", only]
    subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
    return json.loads(out.read_text())


def main():
    dest = HERE / "results"
    dest.mkdir(parents=True, exist_ok=True)
    honest_full = json.loads((dest / "gp3-parity-2026-08-23.json").read_text())
    honest_subset = run("instrument-swap-r1-narrate-v3.rs", SUBSET,
                        dest / "gp3-fork-honest-subset.json")
    controls = []
    for name, path, only, expectation in FORKS:
        rep = run(path, only, dest / f"gp3-fork-{name}.json")
        ref = honest_full if only is None else honest_subset
        cen, refcen = rep["census"], ref["census"]
        if name == "attest-absent":
            fired = (rep["byte_identical_without_msg"] == rep["fixtures"]
                     and cen["available_states"]["ABSENT"] > 0
                     and refcen["available_states"]["ABSENT"] == 0)
            observed = {"parity": f"{rep['byte_identical_without_msg']}/{rep['fixtures']}",
                        "absent_rows": cen["available_states"]["ABSENT"],
                        "absent_rows_honest": refcen["available_states"]["ABSENT"],
                        "telemetry_errors": rep["telemetry_error_count"]}
        elif name == "poison-worst":
            fired = (rep["telemetry_error_count"] > 0
                     and any("tie parity" in e for e in rep["telemetry_errors"])
                     and cen["discarded_want"] != refcen["discarded_want"])
            observed = {"telemetry_errors": rep["telemetry_error_count"],
                        "first_errors": rep["telemetry_errors"][:2],
                        "discarded_want": cen["discarded_want"],
                        "discarded_want_honest": refcen["discarded_want"],
                        "lone_unit_turns": cen["lone_unit_turns"]}
        else:
            fired = (rep["byte_identical_without_msg"] < rep["fixtures"]
                     and cen["discarded_want"] != refcen["discarded_want"])
            observed = {"parity": f"{rep['byte_identical_without_msg']}/{rep['fixtures']}",
                        "discarded_want": cen["discarded_want"],
                        "discarded_want_honest": refcen["discarded_want"]}
        controls.append({"fork": name, "expected": expectation, "fired": fired,
                         "observed": observed})
        print(f"  {'OK    ' if fired else 'FAILED'} {name:<14} {observed}")

    ok = all(c["fired"] for c in controls)
    out = {"gate": "G-P (NARRATE v3) live forks", "subset": SUBSET,
           "honest_full_census": honest_full["census"],
           "honest_subset_census": honest_subset["census"],
           "controls": controls, "all_fired": ok}
    (dest / "gp3-fork-controls-2026-08-23.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"\n  FORK CONTROLS: {'ALL FIRED' if ok else 'A CONTROL DID NOT FIRE'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
