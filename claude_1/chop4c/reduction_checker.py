#!/usr/bin/env python3
r"""G-4c.2 r3 — the saturation cutoffs as a MECHANICALLY CHECKED reduction.

codex_1 held that the cutoffs were reasoned, not checked, and that examples beyond the boundary
would still be sampling. This proves the reduction instead, by the construction they approved:
**checked subject-operation identities + prerequisite bounds measured over the exhaustive
domain**, with a mutation for every arm.

Their binding refinement is the load-bearing part: the `chop_power` bound must cover
`PredictedTree.health` AFTER growth, not the initial plant health. My posted construction had
used the wrong quantity; `predict_tree` grows the tree and adds health before returning.

THE THREE REDUCTIONS

  opp_chop >= 20        identity: `opp_chop` is read exactly once in `predict_tree`, as
                        `health-=opp_chop` guarded by `if opp_chop>0`, immediately followed by
                        `if health<=0 {return None}`.
                        bound: initial legal health <= 20 (from `tree_health_params`).
                        case travel==0: the loop body never executes, so `opp_chop` is unread and
                        the result cannot depend on it.
                        case travel>=1: the first iteration subtracts opp_chop from health<=20,
                        so any opp_chop>=20 yields health<=0 and returns None. Every larger value
                        does the same. => enumerating 0..=21 covers all behaviours.

  chop_power >= 20      identity: `chop_power` is read exactly once in `chop_outcome`'s loop, as
                        `health-=chop_power`, immediately followed by
                        `if health<=0 {return Some((turns,size))}`.
                        bound: `predicted.health <= 20` MEASURED over the whole enumerated
                        prediction domain (max_pred_health), not argued from initial health.
                        => any chop_power>=20 fells on iteration 1 identically.

  free_capacity >= 4    identity: wood is computed exactly once, as
                        `final_size.min(unit.free_capacity())`.
                        bound: `final_size <= 4` MEASURED over the domain (max_final_size).
                        => min() saturates; larger capacities give the same wood.

MUTATIONS. Each identity and each bound is mutated and the checker MUST reject. An arm that has
only ever agreed is not evidence — the rule that produced this whole round.
"""
import re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "claude_1/chop4c"))
import make_domain_probe as MDP  # noqa: E402

SUBJECT = MDP.RESIDENT.read_text()

IDENTITIES = {
    "opp_chop read once, subtract-then-None-guard": (
        r"let opp_chop=Self::predicted_opp_chop\(view,plant\);", 1,
        r"if opp_chop>0\{\s*health-=opp_chop;\s*if health<=0\{\s*return None;", 1),
    "chop_power read once in the felling loop, subtract-then-Some-exit": (
        r"if chop_power<=0\{\s*return None;", 1,
        r"health-=chop_power;\s*if health<=0\{\s*return Some\(\(turns,size\)\);", 1),
    "wood computed once as min(final_size, free_capacity)": (
        r"let wood=final_size\.min\(unit\.free_capacity\(\)\);", 1,
        r"let wood=final_size\.min\(unit\.free_capacity\(\)\);", 1),
}


class ReductionError(RuntimeError):
    """Fail closed."""


def check_identities(src, label="subject"):
    for name, (pat_a, n_a, pat_b, n_b) in IDENTITIES.items():
        for pat, want in ((pat_a, n_a), (pat_b, n_b)):
            got = len(re.findall(pat, src))
            if got != want:
                raise ReductionError(f"[{label}] identity FAILED — {name}: pattern matched "
                                     f"{got} times, want {want}")
    # opp_chop must not be read anywhere else in predict_tree
    body = src[src.index("fn predict_tree("):src.index("fn chop_outcome(")]
    # \b matters: `predicted_opp_chop` CONTAINS `opp_chop`, and counting the substring made the
    # checker report 4 and fail on the honest subject. The identity is about the local variable.
    reads = len(re.findall(r"\bopp_chop\b", body))
    if reads != 3:   # binding, `if opp_chop>0`, `health-=opp_chop`
        raise ReductionError(f"[{label}] identity FAILED — opp_chop appears {reads} times in "
                             f"predict_tree, want exactly 3 (bind, guard, subtract)")
    return True


def check_bounds(bounds):
    if bounds["max_pred_health"] > 20:
        raise ReductionError(f"bound FAILED — max predicted health {bounds['max_pred_health']} "
                             f"> 20; the chop_power cutoff is NOT justified")
    if bounds["max_pred_size"] > 4:
        raise ReductionError(f"bound FAILED — max predicted size {bounds['max_pred_size']} > 4; "
                             f"the growth cap the other bounds rely on does not hold")
    if bounds["max_final_size"] > 4:
        raise ReductionError(f"bound FAILED — max final_size {bounds['max_final_size']} > 4; "
                             f"the free_capacity cutoff is NOT justified")
    if bounds["travel0_some"] <= 0 or bounds["travel_ge1_some"] <= 0:
        raise ReductionError("bound FAILED — both travel cases must be observed non-empty; "
                             "the opp_chop case split is otherwise untested")
    return True


def run(bounds):
    """Bounds MUST come from a parsed probe run. There is no manual path — codex_1's r3 blocker:
    a checker taking CLI numbers accepted fabricated values while calling them measurements."""

    print("subject-operation identities:")
    check_identities(SUBJECT)
    for name in IDENTITIES:
        print(f"  OK — {name}")
    print("  OK — opp_chop appears exactly 3 times in predict_tree (bind, guard, subtract)")

    print("\nprerequisite bounds, measured over the exhaustive domain:")
    check_bounds(bounds)
    print(f"  OK — max predicted health {bounds['max_pred_health']} <= 20 "
          f"(post-growth, per codex_1's refinement)")
    print(f"  OK — max predicted size {bounds['max_pred_size']} <= 4")
    print(f"  OK — max final_size {bounds['max_final_size']} <= 4")
    print(f"  OK — both travel cases observed: travel==0 {bounds['travel0_some']}, "
          f"travel>=1 {bounds['travel_ge1_some']}")

    print("\nreduction conclusions:")
    print("  opp_chop      >= 20 -> travel==0 unread; travel>=1 forces None. cutoff 21 covers all")
    print("  chop_power    >= 20 -> fells on iteration 1. cutoff 21 covers all")
    print("  free_capacity >= 4  -> min() saturates. cutoff 5 covers all")

    print("\nmutation controls (each MUST be rejected):")
    muts = {
        "identity: opp_chop guard removed":
            (SUBJECT.replace("if opp_chop>0{", "if true{", 1), None),
        "identity: chop_power subtract renamed":
            (SUBJECT.replace("health-=chop_power;", "health-=chop_power+0;", 1), None),
        "identity: wood min() replaced":
            (SUBJECT.replace("let wood=final_size.min(unit.free_capacity());",
                             "let wood=final_size;", 1), None),
        "bound: predicted health 21":
            (None, dict(bounds, max_pred_health=21)),
        "bound: final_size 5":
            (None, dict(bounds, max_final_size=5)),
        "bound: travel==0 case never observed":
            (None, dict(bounds, travel0_some=0)),
        "bound: travel>=1 case never observed":
            (None, dict(bounds, travel_ge1_some=0)),
        "bound: predicted size 5 (growth cap broken)":
            (None, dict(bounds, max_pred_size=5)),
    }
    for name, (msrc, mbounds) in muts.items():
        try:
            if msrc is not None:
                check_identities(msrc, label="mutant")
            else:
                check_bounds(mbounds)
        except ReductionError:
            print(f"  OK — rejected: {name}")
        else:
            raise ReductionError(f"MUTATION CONTROL FAILED: {name} was ACCEPTED. The reduction "
                                 f"checker cannot detect the defect it exists to detect.")
    print("\nsaturation reduction: mechanically checked, all arms mutation-tested")
    return 0


if __name__ == "__main__":
    raise SystemExit("REFUSING: this checker has no manual-measurement path. Run "
                     "g4c2_domain.py, which parses the probe's emitted bound row and calls it.")
