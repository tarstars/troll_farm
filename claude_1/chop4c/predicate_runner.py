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

# FULL-MATCH schemas for BOTH row kinds (r3 point 1). Anchored at both ends: a partial match
# would let trailing garbage ride along unnoticed.
PRED = re.compile(r"^PRED eval=(\d+) cell=(-?\d+),(-?\d+) on_tree=(\d+) adjacent=(\d+) "
                  r"inreach=(\d+) damaged=(true|false) health=(-?\d+)$")
# Both tails enumerated exactly. The previous ` .*$` wildcard meant `fullmatch` proved nothing
# about the end of the row — a strict-looking check that could not reject trailing fields.
# TWO FULL ROW SCHEMAS, one per exit, so the tail is COUPLED to the exit value. The previous
# single pattern matched `exit=(NONE|SOME)` and then allowed either tail independently, which
# accepted semantically crossed rows (`exit=NONE … end_health=…`). It looked strict and was not.
_HEAD = (r"^WHY eval=(\d+) turn=(\d+) cell=(-?\d+),(-?\d+) exit={exit} "
         r"opp_chop=(-?\d+) start_health=(-?\d+) horizon=(-?\d+) ")
WHY_NONE = re.compile(_HEAD.format(exit="NONE") + r"died_at_iter=-?\d+$")
WHY_SOME = re.compile(_HEAD.format(exit="SOME") + r"end_health=-?\d+ end_size=-?\d+$")


class _WhyMatch:
    """Uniform accessor so callers keep group numbering with the exit value re-inserted."""

    def __init__(self, m, exit_):
        self._m, self._exit = m, exit_

    def group(self, n):
        if n == 5:
            return self._exit
        return self._m.group(n if n < 5 else n - 1)


def why_fullmatch(line):
    for rx, ex in ((WHY_NONE, "NONE"), (WHY_SOME, "SOME")):
        m = rx.fullmatch(line)
        if m:
            return _WhyMatch(m, ex)
    return None
EXPECTED_FIXTURES = [f"OSC-{i:03d}" for i in range(1, 35)]
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


def reconcile(err):
    """r3 point 2: exactly one PRED provenance row to exactly one subsequent WHY exit row per
    `predict_tree` execution, in EMITTED ORDER, joined on the stable eval id AND the cell.

    The previous runner counted PRED rows alone. That cannot detect a dropped, duplicated or
    reordered exit row, so it could not support any claim about which evaluations were measured.
    """
    pairs, pending = [], {}
    order = []
    for ln in err.splitlines():
        if ln.startswith("PRED "):
            m = PRED.fullmatch(ln)
            if not m:
                raise RunnerError(f"UNPARSED PRED row: {ln!r}")
            ev = int(m.group(1))
            if ev in pending:
                raise RunnerError(f"DUPLICATE provenance for eval {ev}")
            pending[ev] = (int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)),
                           int(m.group(6)), m.group(7))
            order.append(ev)
        elif ln.startswith("WHY "):
            m = why_fullmatch(ln)
            if not m:
                raise RunnerError(f"UNPARSED WHY row: {ln!r}")
            ev = int(m.group(1))
            if ev not in pending:
                raise RunnerError(f"exit row for eval {ev} with no preceding provenance row")
            if order[len(pairs)] != ev:
                raise RunnerError(f"REORDERED: expected eval {order[len(pairs)]}, got {ev}")
            cx, cy, on, adj, inr, dam = pending.pop(ev)
            if (cx, cy) != (int(m.group(3)), int(m.group(4))):
                raise RunnerError(f"ALIEN identity: eval {ev} cell {(cx, cy)} vs "
                                  f"{(int(m.group(3)), int(m.group(4)))}")
            pairs.append({"eval": ev, "on_tree": on, "adjacent": adj, "inreach": inr,
                          "damaged": dam, "exit": m.group(5)})
    if pending:
        raise RunnerError(f"{len(pending)} provenance rows never reached an exit row: "
                          f"{sorted(pending)[:5]}")
    if not pairs:
        raise RunnerError("no reconciled pairs at all")
    return pairs


def tally(pairs):
    """r3 point 5: counts derived from RECONCILED PAIRS, not from the row list they came from."""
    c = collections.Counter()
    for pr in pairs:
        on, adj, inr, dam = pr["on_tree"], pr["adjacent"], pr["inreach"], pr["damaged"]
        c["calls"] += 1
        c["exit_" + pr["exit"]] += 1
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


def alien_why(line):
    """A syntactically VALID WHY row with the same eval id and a different two-number cell."""
    m = why_fullmatch(line)
    if not m:
        raise RunnerError(f"control setup failed: sample WHY row does not full-match: {line!r}")
    cx, cy = int(m.group(3)), int(m.group(4))
    out = line.replace(f"cell={cx},{cy}", f"cell={cx + 77},{cy + 77}", 1)
    if not why_fullmatch(out):
        raise RunnerError("control setup failed: alien row must remain schema-valid, else it "
                          "tests malformedness rather than identity")
    return out


def crossed(line, want_exit):
    """Build a row whose exit value carries the OTHER exit's tail."""
    head, _, tail = line.partition(" opp_chop=")
    head = re.sub(r"exit=(NONE|SOME)", f"exit={want_exit}", head)
    keep = " opp_chop=" + tail.split(" died_at_iter=")[0].split(" end_health=")[0]
    return head + keep + (" end_health=3 end_size=1" if want_exit == "NONE"
                          else " died_at_iter=4")


def negative_controls(err):
    """r3 point 4: every reconciliation failure mode must be OBSERVED failing."""
    ls = [l for l in err.splitlines() if l.startswith(("PRED ", "WHY "))]
    ip = next(i for i, l in enumerate(ls) if l.startswith("PRED "))
    iw = next(i for i, l in enumerate(ls) if l.startswith("WHY "))
    swap = ls[:]
    for a in range(len(swap) - 3):
        if swap[a].startswith("PRED") and swap[a + 2].startswith("PRED"):
            swap[a], swap[a + 2] = swap[a + 2], swap[a]
            break
    cases = {
        "dropped provenance": "\n".join(ls[:ip] + ls[ip + 1:]),
        "duplicated provenance": "\n".join(ls[:ip + 1] + [ls[ip]] + ls[ip + 1:]),
        "reordered provenance/exit": "\n".join(swap),
        # A VALID row carrying a DIFFERENT cell — the previous version spliced "99,99" in front
        # of the existing coordinates, producing `cell=99,993,4`, which the schema rejected as
        # malformed. It therefore never reached the identity branch it claimed to test.
        "alien identity (valid row, different cell)": "\n".join(
            [alien_why(ls[iw]) if i == iw else l for i, l in enumerate(ls)]),
        "trailing garbage on a PRED row": "\n".join([l + " extra=1" if i == ip else l
                                                     for i, l in enumerate(ls)]),
        "trailing garbage on a WHY row": "\n".join([l + " extra=1" if i == iw else l
                                                    for i, l in enumerate(ls)]),
        # CROSSED tails: the exit value and its tail must agree. Accepting these was the r4 hole.
        "crossed tail: exit=NONE with end_health/end_size": "\n".join(
            [crossed(l, "NONE") if i == iw else l for i, l in enumerate(ls)]),
        "crossed tail: exit=SOME with died_at_iter": "\n".join(
            [crossed(l, "SOME") if i == iw else l for i, l in enumerate(ls)]),
        "no rows at all": "",
    }
    for name, corrupted in cases.items():
        try:
            reconcile(corrupted)
        except RunnerError:
            print(f"  negative control OK — reconciler rejects: {name}")
        else:
            raise RunnerError(f"NEGATIVE CONTROL FAILED: reconciler accepted {name}")


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
    sits = H.load_situations(None)
    got = sorted(s["id"] for s in sits)
    if got != EXPECTED_FIXTURES:                          # r3 point 3
        raise RunnerError(f"fixture set is not exactly OSC-001..OSC-034: missing "
                          f"{sorted(set(EXPECTED_FIXTURES)-set(got))}, extra "
                          f"{sorted(set(got)-set(EXPECTED_FIXTURES))}")
    for sit in sits:
        err = C.check_parity(sit, cfg, plain, instr)      # point 2: raises on divergence
        pairs = reconcile(err)                            # 1:1, ordered, identity-checked
        c = tally(pairs)
        if c["exit_NONE"] + c["exit_SOME"] != c["calls"]:
            raise RunnerError(f"{sit['id']}: exits {c['exit_NONE']}+{c['exit_SOME']} != "
                              f"calls {c['calls']}")
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
