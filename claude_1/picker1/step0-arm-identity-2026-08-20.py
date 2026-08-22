#!/usr/bin/env python3
"""Phase 1 STEP 0 — the byte-identity the unblock ruling rests on, MEASURED not inherited.

The owner unblocked Phase 1 on the premise that the pair-selector code is byte-identical in both
bots of the running platform session, so the probe's answer cannot depend on tonight's verdict.
This measures that premise and prints exactly how far it reaches.
"""
import hashlib, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
ARMS = {"cure-C (Door-1 floor, Phase-1 pinned subject)":
        REPO / "cgauto/submissions/submitted-sub41153619-cure-c-quiet.rs",
        "Door-1 candidate (challenger)": REPO / "claude_1/chop4c/candidate-door1.rs"}
REGIONS = {
    "select() block  (fn wait .. fn move_command)":
        ("            fn wait()->Candidate{", "            fn move_command(command:&str)"),
    "candidate assembly (by_id .. select call)":
        ("                let mut by_id=BTreeMap::new();",
         "let mut selected=MoisanBot::select(by_id,&view.inventories[0]);"),
    "Candidate/Target types":
        ("#[derive(Clone,Copy,Debug,Eq,PartialEq,Ord,PartialOrd)]enum Target{", "struct MoisanBot;"),
}


def region(src, a, b):
    i = src.index(a); j = src.index(b, i); return src[i:j + len(b)]


def main():
    srcs = {k: p.read_text() for k, p in ARMS.items()}
    for k, p in ARMS.items():
        print(f"{k}\n  {p.relative_to(REPO)}\n  sha256 {hashlib.sha256(srcs[k].encode()).hexdigest()}")
    names = list(srcs)
    print("\nwhole-file diff:")
    import difflib
    hunks = [l for l in difflib.unified_diff(srcs[names[0]].splitlines(), srcs[names[1]].splitlines(),
                                             lineterm="", n=0)]
    print("  changed lines:", sum(1 for l in hunks if l[:1] in "+-" and l[:3] not in ("+++", "---")),
          " hunks:", sum(1 for l in hunks if l.startswith("@@")))
    ok = True
    print("\nselection-region identity:")
    for name, (a, b) in REGIONS.items():
        ra, rb = region(srcs[names[0]], a, b), region(srcs[names[1]], a, b)
        same = ra == rb
        ok &= same
        print(f"  {'IDENTICAL' if same else 'DIFFERS  '}  {name:44} "
              f"sha256={hashlib.sha256(ra.encode()).hexdigest()[:16]} bytes={len(ra)}")
    print("\nreach of the premise, stated precisely:")
    print("  The selection CODE is identical in both arms. The one changed hunk is in")
    print("  `predicted_opp_chop`, which feeds `predict_tree`, which feeds candidate SCORES —")
    print("  so select()'s INPUTS can differ between arms wherever that forecast participates.")
    print("  The mechanism (which clause benches, which term dominates) is therefore arm-")
    print("  independent; the per-turn ARITHMETIC below is pinned to the cure-C subject, which")
    print("  is what the charter pins Phase 1 to.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
