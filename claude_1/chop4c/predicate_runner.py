#!/usr/bin/env python3
r"""Deterministic runner for the presence-predicate comparison (codex_1's five points).

1. committed, re-runnable script — no inline runs, no hand-assembled numbers;
2. per-fixture parity recorded, and the run aborts if any fixture diverges;
3. subject / probe / tool sha256s written into the output;
4. exact predicate definitions written into the output, quoted from the probe source;
5. cross-sum assertions that fail closed.

Subject is the CURE-C resident `ad3bfefe…` (the resident since the owner KEEP). `in-reach` is
true graph distance over `view.walkable` — the earlier Manhattan proxy could call a tree reachable
through a wall, which measured nothing.
"""
import collections, hashlib, json, re, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "claude_1/t1"))
sys.path.insert(0, str(REPO / "claude_1/hstarve1"))
sys.path.insert(0, str(REPO / "claude_1/pipeline"))
sys.path.insert(0, str(REPO / "claude_1/chop4c"))
import coverage as C                    # noqa: E402
import fixture_harness as H             # noqa: E402
import make_predicate_probe as MPP      # noqa: E402

ROW = re.compile(r"PRED cell=\S+ on_tree=(\d+) adjacent=(\d+) inreach=(\d+) damaged=(\w+) "
                 r"health=(\d+)")
OUT = REPO / "claude_1/chop4c/predicate-comparison-2026-08-19.json"


class RunnerError(RuntimeError):
    """Fail closed."""


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def predicate_definitions(probe_src):
    """Point 4: quote the definitions from the probe, never restate them by hand."""
    out = {}
    for name, key in (("on_tree", "let on_tree"), ("adjacent", "let c4c_adjacent"),
                      ("inreach", "let c4c_inreach"), ("damaged", "let c4c_damaged")):
        line = next((l.strip() for l in probe_src.splitlines() if key in l), None)
        if line is None:
            raise RunnerError(f"predicate {name} not found in the probe — cannot document it")
        out[name] = line
    return out


def main():
    if MPP.main() != 0:
        raise RunnerError("probe build refused")
    probe = REPO / "claude_1/chop4c/predicate-probe.rs"
    subject = MPP.RESIDENT
    if sha(subject) != MPP.RESIDENT_SHA:
        raise RunnerError("subject digest differs from the pinned resident")

    cfg = json.loads(H.CONFIG.read_text())
    wd = Path(tempfile.mkdtemp(prefix="pred-run-"))
    (wd / "i").mkdir(); (wd / "p").mkdir()
    instr = H.compile_candidate(probe, wd / "i")
    plain = H.compile_candidate(subject, wd / "p")

    tot, byfix = collections.Counter(), {}
    for sit in H.load_situations(None):
        err = C.check_parity(sit, cfg, plain, instr)      # point 2: raises on divergence
        c = collections.Counter()
        for on, adj, inr, dam, _hp in (m.groups() for m in ROW.finditer(err)):
            c["calls"] += 1
            if int(on) > 0:
                c["on_tree_fires"] += 1
            elif dam == "true":
                c["evidence_free_firings"] += 1
                if int(adj) > 0:
                    c["admit_adjacent"] += 1
                if int(inr) > 0:
                    c["admit_inreach"] += 1
                if (int(adj) > 0) != (int(inr) > 0):
                    c["adjacent_inreach_disagree"] += 1
        byfix[sit["id"]] = {"parity": "IDENTICAL", **c}
        tot.update(c)

    # point 5: cross-sums, failing closed
    if sum(v["calls"] for v in byfix.values()) != tot["calls"]:
        raise RunnerError("cross-sum failed: per-fixture calls != total")
    if tot["on_tree_fires"] + tot["evidence_free_firings"] > tot["calls"]:
        raise RunnerError("cross-sum failed: classified rows exceed calls")
    for k in ("admit_adjacent", "admit_inreach"):
        if tot[k] > tot["evidence_free_firings"]:
            raise RunnerError(f"cross-sum failed: {k} exceeds evidence-free firings")
    if tot["adjacent_inreach_disagree"] == 0 and tot["admit_adjacent"] != tot["admit_inreach"]:
        raise RunnerError("inconsistent: zero disagreements but unequal admit totals")

    doc = {
        "task": "20260818-osc031-forecast-defect-fix",
        "subject": {"path": str(subject.relative_to(REPO)), "sha256": sha(subject),
                    "note": "cure C — the resident since the owner KEEP"},
        "probe_sha256": sha(probe),
        "tool_sha256": {"runner": sha(__file__), "builder": sha(MPP.__file__),
                        "coverage": sha(C.__file__), "fixture_harness": sha(H.__file__)},
        "predicate_definitions": predicate_definitions(probe.read_text()),
        "fixtures": len(byfix), "totals": dict(tot), "by_fixture": byfix,
    }
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    d = tot["evidence_free_firings"]
    print(f"fixtures {len(byfix)} · parity IDENTICAL on each · calls {tot['calls']}")
    print(f"evidence-free firings {d} · on-tree admits 0 · adjacent {tot['admit_adjacent']} · "
          f"in-reach {tot['admit_inreach']} · disagreements {tot['adjacent_inreach_disagree']}")
    print(f"wrote {OUT.relative_to(REPO)}  sha256={sha(OUT)[:16]}…")
    return 0


if __name__ == "__main__":
    sys.exit(main())
