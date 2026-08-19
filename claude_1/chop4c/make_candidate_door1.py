#!/usr/bin/env python3
r"""Phase 2 — build the Door-1 candidate from the CURE-C resident.

Accepted predicate (`codex_1` r5, owner Door-1 ruling): **on-tree**. Historical damage alone
infers nothing; assumed opponent chopping requires positive chop power actually observed on the
tree. Adjacent and graph-reach are NOT selected.

The edit is the smallest one that implements exactly that: `predicted_opp_chop` keeps its on-tree
sum and drops the "below full health, therefore someone is chopping it at 1/turn" fallback. The
`tree_health` comparison it used disappears with it, because nothing else reads it here.

Guards, same discipline as cure C: refuses on a wrong subject digest, a non-unique anchor, or a
diff larger than one hunk. Nothing else in the subject may move.
"""
import difflib, hashlib, subprocess, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
RESIDENT = REPO / "cgauto/submissions/submitted-sub41153619-cure-c-quiet.rs"
RESIDENT_SHA = "ad3bfefe4b2326f4f6b4a270dc862ea19a0e319a1cddfde44b96cc6f6d35a5d1"
OUT = REPO / "claude_1/chop4c/candidate-door1.rs"

OLD = '''                if on_tree>0{
                    return on_tree;
                    }
                let expected=tree_health(plant.kind,plant.size);
                if plant.health<expected{
                    1
                }
                else{
                    0
                }
                }'''
NEW = '''                if on_tree>0{
                    return on_tree;
                    }
                0
                }'''


def main():
    src = RESIDENT.read_text()
    got = hashlib.sha256(src.encode()).hexdigest()
    if got != RESIDENT_SHA:
        print(f"REFUSING: subject digest differs\n  want {RESIDENT_SHA}\n  got  {got}")
        return 1
    if src.count(OLD) != 1:
        print(f"REFUSING: anchor matched {src.count(OLD)} times, want exactly 1")
        return 1
    out = src.replace(OLD, NEW)

    # exactly one hunk, and it must be the intended one
    diff = list(difflib.unified_diff(src.splitlines(), out.splitlines(),
                                     "resident", "candidate", lineterm="", n=0))
    hunks = [l for l in diff if l.startswith("@@")]
    if len(hunks) != 1:
        print(f"REFUSING: {len(hunks)} diff hunks, want exactly 1")
        return 1
    removed = [l for l in diff if l.startswith("-") and not l.startswith("---")]
    if any("on_tree" in l for l in removed):
        print("REFUSING: the on-tree evidence path must not be touched")
        return 1

    OUT.write_text(out)
    print(f"wrote {OUT.relative_to(REPO)}")
    print(f"  sha256 {hashlib.sha256(out.encode()).hexdigest()}")
    print(f"  one hunk, {len(removed)} lines removed; on-tree path untouched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
