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


def parse_rows(err):
    """STRICT: every `PRED` line must parse, or nothing is counted.

    A regex that silently skips malformed rows cannot tell "this case never occurred" from
    "this row was dropped" — the defect that made the 4c clause table unable to support a
    negative statement.
    """
    rows = []
    for ln in err.splitlines():
        if not ln.startswith("PRED "):
            continue
        m = ROW.match(ln)
        if not m:
            raise RunnerError(f"UNPARSED PRED row, refusing to count anything: {ln!r}")
        on, adj, inr, dam, hp = m.groups()
        if dam not in ("true", "false"):
            raise RunnerError(f"non-boolean damaged flag: {ln!r}")
        rows.append((int(on), int(adj), int(inr), dam, int(hp)))
    if not rows:
        raise RunnerError("no PRED rows at all — the probe emitted nothing to measure")
    return rows


def tally(rows):
    c = collections.Counter()
    for on, adj, inr, dam, _hp in rows:
        c["calls"] += 1
        if on > 0:
            c["on_tree_fires"] += 1
        elif dam == "true":
            c["evidence_free_firings"] += 1
            if adj > 0:
                c["admit_adjacent"] += 1
            if inr > 0:
                c["admit_inreach"] += 1
            if (adj > 0) != (inr > 0):
                c["adjacent_inreach_disagree"] += 1
    return c


def negative_controls(err):
    """The parser MUST fail on corrupted input, or a clean run proves nothing."""
    lines = [l for l in err.splitlines() if l.startswith("PRED ")]
    cases = {
        "malformed row": "\n".join(lines[:1] + ["PRED cell=oops"] + lines[1:]),
        "truncated row": "\n".join([lines[0].rsplit(" ", 1)[0]] + lines[1:]),
        "non-integer field": "\n".join([lines[0].replace("on_tree=", "on_tree=x", 1)] + lines[1:]),
        "no rows at all": "",
    }
    for name, corrupted in cases.items():
        try:
            parse_rows(corrupted)
        except RunnerError:
            print(f"  negative control OK — parser rejects: {name}")
        else:
            raise RunnerError(f"NEGATIVE CONTROL FAILED: parser accepted {name}")


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
    controls_done = False
    for sit in H.load_situations(None):
        err = C.check_parity(sit, cfg, plain, instr)      # point 2: raises on divergence
        rows = parse_rows(err)                            # strict: no silent skips
        c = tally(rows)
        if c["calls"] != len(rows):
            raise RunnerError(f"{sit['id']}: tally {c['calls']} != parsed rows {len(rows)}")
        byfix[sit["id"]] = {"parity": "IDENTICAL", **c}
        tot.update(c)
        if not controls_done:
            controls_done = True
            negative_controls(err)

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

    if not controls_done:
        raise RunnerError("negative controls never ran — a clean result would prove nothing")
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
