#!/usr/bin/env python3
r"""Is the REUSED cure-C floor actually this candidate's matched floor?

The cure-C arm does not re-run its floor: it reuses `claude_1/chop4c/osc031-phase2-floor.json`
(cure-C `ad3bfefe…` judged against itself). That reuse is only legitimate if the two arms faced
the identical corpus, so this compares the two CONFIGS field by field and the two RESULT files on
their corpus provenance. Any difference outside the deliberately-different identity fields fails.

The door-1 arm re-runs its own floor, so it is checked the same way against its own config — a
check that only ever runs on the reused case would never have been observed rejecting.

Run:  python3 claude_1/picker2/check_floor_match.py
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
PIPE = REPO / "claude_1/pipeline"

# Fields that MUST differ (they name which bot plays) and are excluded by name, not by guesswork.
# `games_dir` / `bin_cache_dir` are scratch LOCATIONS and `processes` is a scheduling knob; none
# is a corpus input. They are excluded BY NAME and the exclusion list is written into the result
# file, so nothing is quietly dropped from the comparison.
IDENTITY = {"candidate", "parent", "run_identity", "task", "notes",
            "games_dir", "bin_cache_dir", "processes"}

PAIRS = {
    "cureC": (PIPE / "picker2-cureC-cand-config.json", PIPE / "osc031-phase2-floor-config.json",
              HERE / "panel-cureC-cand.json", REPO / "claude_1/chop4c/osc031-phase2-floor.json",
              "REUSED floor (not re-run tonight)"),
    "door1": (PIPE / "picker2-door1-cand-config.json", PIPE / "picker2-door1-floor-config.json",
              HERE / "panel-door1-cand.json", HERE / "panel-door1-floor.json",
              "floor re-run tonight"),
}
OUT = HERE / "floor-match-2026-08-20.json"


def main():
    report, ok = {}, True
    for base, (ccfg, fcfg, cres, fres, note) in PAIRS.items():
        c, f = json.loads(ccfg.read_text()), json.loads(fcfg.read_text())
        keys = (set(c) | set(f)) - IDENTITY
        diffs = [k for k in sorted(keys)
                 if json.dumps(c.get(k), sort_keys=True) != json.dumps(f.get(k), sort_keys=True)]
        cr, fr = json.loads(cres.read_text()), json.loads(fres.read_text())
        prov = [k for k in ("corpus_version", "instrument_version", "engine_sha256",
                            "referee_sha256")
                if cr.get(k) != fr.get(k)]
        # The floor must be the candidate's own parent judged against itself.
        lineage = (fr["candidate_sha256"] == fr["parent_sha256"] and
                   cr["parent_sha256"] == fr["candidate_sha256"])
        good = not diffs and not prov and lineage
        ok &= good
        report[base] = {"note": note, "compared_config_fields": sorted(keys),
                        "excluded_identity_fields": sorted(IDENTITY),
                        "config_differences": diffs, "result_provenance_differences": prov,
                        "floor_is_self_judged_parent_of_candidate": lineage,
                        "candidate_parent_sha256": cr["parent_sha256"],
                        "floor_sha256": fr["candidate_sha256"], "matched": good}
        print(f"  {base} ({note}): config diffs {diffs or 'none'}; provenance diffs "
              f"{prov or 'none'}; lineage {'OK' if lineage else 'WRONG'} -> "
              f"{'MATCHED' if good else 'NOT MATCHED'}")
    OUT.write_text(json.dumps({"task": "20260820-pair-selector-anti-benching", "phase": 2,
                               "bases": report, "met": ok}, indent=2, sort_keys=True) + "\n")
    print(f"  matched-floor check: {'MET' if ok else 'NOT MET'}")
    print(f"wrote {OUT}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
