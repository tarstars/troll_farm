#!/usr/bin/env python3
r"""G-4c.2 — reconcile the compiled enumeration and prove the harness can FAIL.

codex_1's binding conditions for the three impossibility proofs:
  1. prove the harness invokes the actual subject functions   -> make_domain_probe.py byte-identity
  2. justify and exhaust the complete valid-engine-state domain
  3. reconcile executed cardinality
  4. fail on unexpected/uncovered tuples
  5. include mutation controls
  (no Python or handwritten tree-math replica is admissible)

Conditions 3-5 live here. The expected cardinality is NOT hand-written: the health bound per
(kind, size) is read out of the SUBJECT's own `tree_health_params` table by regex, so the
reconciliation cannot drift from the code it audits. That is domain arithmetic over the subject's
constants, not a reimplementation of the tree math — nothing here recomputes growth or chopping.

The mutation control is the part that makes a green run mean anything: the probe is rebuilt with
a deliberately weakened invariant and MUST then report violations. A verifier that has only ever
printed zero is not evidence of zero.
"""
import re, subprocess, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "claude_1/t1"))
sys.path.insert(0, str(REPO / "claude_1/hstarve1"))
sys.path.insert(0, str(REPO / "claude_1/pipeline"))
sys.path.insert(0, str(REPO / "claude_1/chop4c"))
import fixture_harness as H          # noqa: E402
import make_domain_probe as MDP      # noqa: E402

FRUITS, COOLDOWN, NEAR_WATER, OPP, TRAVEL = 4, 10, 2, 22, 301  # probe loop ranges
CHOP_POWER, FREE_CAP = 21, 5


class DomainError(RuntimeError):
    """Fail closed."""


def subject_health_bounds():
    """max legal health per (kind, size), read from the SUBJECT's tree_health_params."""
    src = MDP.RESIDENT.read_text()
    m = re.search(r"pub fn tree_health_params\(kind:PlantKind\)->\(i32,i32\)\{\s*match kind\{\s*"
                  r"PlantKind::Plum\|PlantKind::Lemon=>\((\d+),(\d+)\),"
                  r"PlantKind::Apple=>\((\d+),(\d+)\),"
                  r"PlantKind::Banana=>\((\d+),(\d+)\)", src)
    if not m:
        raise DomainError("could not read tree_health_params from the subject — refusing to "
                          "hand-write the bound it audits")
    g = [int(x) for x in m.groups()]
    params = {"Plum": (g[0], g[1]), "Lemon": (g[0], g[1]),
              "Apple": (g[2], g[3]), "Banana": (g[4], g[5])}
    return {(k, s): b + sl * s for k, (b, sl) in params.items() for s in range(1, 5)}


def run_probe(rs_path, expect_ok=True):
    wd = Path(tempfile.mkdtemp(prefix="c4c-dom-"))
    (wd / "p").mkdir()
    b = H.compile_candidate(rs_path, wd / "p")
    r = subprocess.run([str(b)], env={"C4C_DOMAIN_PROBE": "1", "PATH": "/usr/bin:/bin"},
                       capture_output=True, text=True, timeout=2400)
    if r.returncode != 0 and expect_ok:
        raise DomainError(f"probe exited {r.returncode}: {r.stderr[-400:]}")
    stats = {}
    for ln in r.stdout.splitlines():
        if ln.startswith("C4CDOMAIN executed=") or ln.startswith("C4CDOMAIN violations"):
            for kv in ln.split()[1:]:
                if "=" in kv:
                    k, v = kv.split("=", 1)
                    stats[k] = int(v) if v.isdigit() else v
    viol = [l for l in r.stdout.splitlines() if l.startswith("VIOLATION")]
    return stats, viol


def main():
    if MDP.main() != 0:
        raise DomainError("probe build refused")
    probe = REPO / "claude_1/chop4c/domain-probe.rs"

    # ---- condition 3: cardinality reconciliation, from the SUBJECT's constants
    bounds = subject_health_bounds()
    health_terms = sum(bounds.values())          # sum over (kind,size) of legal health values
    expected = health_terms * FRUITS * COOLDOWN * NEAR_WATER * OPP * TRAVEL
    print(f"expected tuples = {health_terms}(health) x {FRUITS} x {COOLDOWN} x {NEAR_WATER} "
          f"x {OPP} x {TRAVEL} = {expected}")

    stats, viol = run_probe(probe)
    print(f"probe: executed={stats['executed']} predict_some={stats['predict_some']} "
          f"predict_none={stats['predict_none']} chop_some={stats['chop_some']} "
          f"chop_none={stats['chop_none']}")
    if stats["executed"] != expected:
        raise DomainError(f"CARDINALITY MISMATCH: executed {stats['executed']} != declared "
                          f"{expected}. The domain is not exhausted as justified; refusing.")
    print(f"  cardinality reconciles exactly ({expected})")

    # ---- condition 4: every tuple must be accounted for by exactly one outcome
    if stats["predict_some"] + stats["predict_none"] != stats["executed"]:
        raise DomainError("UNCOVERED TUPLES: predict_some + predict_none != executed")
    print("  every tuple accounted for by exactly one predict_tree outcome")

    # PER-PREDICATE cardinality (codex_1 G-4c.2 point 2): reconciling only prediction calls left
    # the nested chop_outcome and wood evaluations unaudited.
    want_chop = stats["predict_some"] * CHOP_POWER
    if stats["chop_calls"] != want_chop:
        raise DomainError(f"chop_outcome evaluations {stats['chop_calls']} != predict_some x "
                          f"{CHOP_POWER} = {want_chop}")
    if stats["chop_some"] + stats["chop_none"] != stats["chop_calls"]:
        raise DomainError("UNCOVERED: chop_some + chop_none != chop_calls")
    want_wood = stats["chop_some"] * FREE_CAP
    if stats["wood_evals"] != want_wood:
        raise DomainError(f"wood evaluations {stats['wood_evals']} != chop_some x {FREE_CAP} "
                          f"= {want_wood}")
    print(f"  chop_outcome evaluations reconcile ({want_chop}); wood evaluations reconcile "
          f"({want_wood})")

    # ---- the three invariants, as measured
    for k in ("predicted_nonpositive", "chop_outcome_none", "wood_nonpositive"):
        if stats[k] != 0:
            raise DomainError(f"invariant {k} VIOLATED {stats[k]} times — this is a finding "
                              f"about the subject, not a harness bug; reporting, not adjusting")
    print(f"  invariants hold across all {expected} tuples (0 violations, {len(viol)} rows)")

    # ---- condition 5: MUTATION CONTROLS. A verifier that has only printed zero proves nothing.
    print("\nmutation controls (each MUST report violations):")
    text = probe.read_text()
    mutations = {
        "weakened PREDICTED_NONPOSITIVE guard (<=0 -> <=1)":
            ("if pred.size<=0||pred.health<=0{v_pred_nonpos+=1;",
             "if pred.size<=1||pred.health<=0{v_pred_nonpos+=1;"),
        "weakened WOOD_NONPOSITIVE guard (<=0 -> <=1)":
            ("if final_size>0&&free_cap>0&&wood<=0{v_wood_nonpos+=1;",
             "if final_size>0&&free_cap>0&&wood<=1{v_wood_nonpos+=1;"),
    }
    # CHOP_OUTCOME_NONE had no mutation control (codex_1 point 3). Truncating the subject's own
    # felling loop to a single iteration forces None for any tree not felled in one hit, so the
    # harness must report chop_outcome_none > 0.
    # `for turns in 1..=100{` occurs three times in the subject; anchor on chop_outcome's own
    # preceding line so the mutation lands in the function under proof and nowhere else.
    mutations["truncated chop_outcome loop (1..=100 -> 1..=1)"] = (
        "let mut cooldown=predicted.cooldown;\n                for turns in 1..=100{",
        "let mut cooldown=predicted.cooldown;\n                for turns in 1..=1{")
    mut_path = REPO / "claude_1/chop4c/domain-probe-mutant.rs"
    for name, (old, new) in mutations.items():
        if text.count(old) != 1:
            raise DomainError(f"mutation anchor not unique for {name}")
        mut_path.write_text(text.replace(old, new))
        mstats, mviol = run_probe(mut_path, expect_ok=True)
        total = (mstats["predicted_nonpositive"] + mstats["chop_outcome_none"]
                 + mstats["wood_nonpositive"])
        if total == 0:
            raise DomainError(f"MUTATION CONTROL FAILED: {name} produced 0 violations. The "
                              f"harness cannot detect the defect it exists to detect.")
        print(f"  OK — {name}: {total} violations detected")
    mut_path.unlink()
    print("\nG-4c.2 impossibility proofs: conditions 1-5 satisfied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
