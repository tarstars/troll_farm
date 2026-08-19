#!/usr/bin/env python3
r"""Gate-1 unified runner: attribution + ACCEPT-opportunity accounting, one review unit.

codex_1's seven points, each enforced here and observable in the output:
 1. one stable identity `(call, plant)` shared by the caller terminal and the attribution;
 2. exactly one ordered attribution per `PREDICT_TREE_NONE` terminal;
 3. controls observed rejecting dropped, duplicate, reordered and alien-id rows;
 4. exact `OSC-001..OSC-034` assertion and per-fixture stdout parity;
 5. per-fixture and aggregate attribution + ACCEPT-opportunity cross-sums;
 6. the cure-C fictional-chop mismatch control observed firing;
 7. runner, config and result committed together.

Nothing is carried over from the withdrawn inline runs; every number below is derived here.
"""
import collections, hashlib, json, re, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
for p in ("claude_1/t1", "claude_1/hstarve1", "claude_1/pipeline"):
    sys.path.insert(0, str(REPO / p))
import coverage as C          # noqa: E402
import fixture_harness as H   # noqa: E402

GATE = re.compile(r"^UGATE call=(\d+) turn=(\d+) unit=(\d+) plants=(\d+) gate=(PASS|REJECT)$")
TERM = re.compile(r"^UTERM call=(\d+) plant=(\d+) turn=(\d+) clause=(\w+)$")
ATTR = re.compile(r"^UATTR call=(\d+) plant=(-?\d+) opp_chop=(-?\d+) on_tree_recomputed=(-?\d+) "
                  r"verdict=(EVIDENCE_BASED|UNEXPLAINED)$")
FIXTURES = [f"OSC-{i:03d}" for i in range(1, 35)]
SUBJECTS = {
    "cure-C-resident": ("cgauto/submissions/submitted-sub41153619-cure-c-quiet.rs",
                        "claude_1/chop4c/unified-cureC.rs",
                        "ad3bfefe4b2326f4f6b4a270dc862ea19a0e319a1cddfde44b96cc6f6d35a5d1"),
    "door1-candidate": ("claude_1/chop4c/candidate-door1.rs",
                        "claude_1/chop4c/unified-door1.rs",
                        "547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0"),
}


class GateError(RuntimeError):
    """Fail closed."""


class _NoReorderPair(Exception):
    """This fixture cannot host the reorder control; try the next one."""


def parse_join(err):
    """Point 1+2: join each PREDICT_TREE_NONE terminal to exactly one attribution, in order."""
    gates, terms, attrs = [], [], []
    for ln in err.splitlines():
        if ln.startswith("UGATE "):
            m = GATE.fullmatch(ln)
            if not m:
                raise GateError(f"UNPARSED UGATE: {ln!r}")
            gates.append((int(m.group(1)), m.group(5)))
        elif ln.startswith("UTERM "):
            m = TERM.fullmatch(ln)
            if not m:
                raise GateError(f"UNPARSED UTERM: {ln!r}")
            terms.append((int(m.group(1)), int(m.group(2)), m.group(4)))
        elif ln.startswith("UATTR "):
            m = ATTR.fullmatch(ln)
            if not m:
                raise GateError(f"UNPARSED UATTR: {ln!r}")
            attrs.append((int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)),
                          m.group(5)))
    rejects = [t for t in terms if t[2] == "PREDICT_TREE_NONE"]
    if len(rejects) != len(attrs):
        raise GateError(f"{len(rejects)} PREDICT_TREE_NONE terminals vs {len(attrs)} "
                        f"attributions — must be exactly one each")
    joined = []
    for (rc, rp, _), (ac, ap, opp, ot, verdict) in zip(rejects, attrs):
        if (rc, rp) != (ac, ap):
            raise GateError(f"identity mismatch: terminal {(rc, rp)} vs attribution {(ac, ap)} "
                            f"— the join is not one-to-one and ordered")
        joined.append({"call": rc, "plant": rp, "opp_chop": opp, "on_tree": ot,
                       "verdict": verdict})
    return gates, terms, joined


def controls(err):
    """Point 3: the join must reject each corruption."""
    ls = [l for l in err.splitlines() if l.startswith(("UGATE ", "UTERM ", "UATTR "))]
    ia = next(i for i, l in enumerate(ls) if l.startswith("UATTR "))
    alien = re.sub(r"call=\d+", "call=999999", ls[ia], count=1)
    # A swap of two IDENTICAL rows is a no-op and would "pass" while testing nothing. Require a
    # pair that genuinely differs; if this fixture has none, it cannot host the reorder control.
    swap = ls[:]
    js = [i for i, l in enumerate(swap) if l.startswith("UATTR ")]
    pair = next(((a, b) for a in js for b in js if a < b and swap[a] != swap[b]), None)
    if pair is None:
        raise _NoReorderPair()
    swap[pair[0]], swap[pair[1]] = swap[pair[1]], swap[pair[0]]
    cases = {
        "dropped attribution": ls[:ia] + ls[ia + 1:],
        "duplicated attribution": ls[:ia + 1] + [ls[ia]] + ls[ia + 1:],
        "reordered attributions": swap,
        "alien identity": [alien if i == ia else l for i, l in enumerate(ls)],
    }
    for name, lines in cases.items():
        try:
            parse_join("\n".join(lines))
        except GateError:
            print(f"    control OK — rejects: {name}")
        else:
            raise GateError(f"CONTROL FAILED: join accepted {name}")


def chain_controls(counts):
    """A cross-sum that has only ever balanced is not evidence. Falsify each side and require
    the identity to break."""
    def check(c):
        later = sum(c["terminal_" + k] for k in ("PREDICTED_NONPOSITIVE", "CHOP_OUTCOME_NONE",
                                                 "ROUND_TRIP_CLOCK", "WOOD_NONPOSITIVE"))
        if c["terminal_SEQ2_PASS"] != c["terminal_ACCEPT"] + later:
            raise GateError("chain identity broken")
        if c["seq2_rows"] != c["terminal_PREDICT_TREE_NONE"] + c["terminal_SEQ2_PASS"]:
            raise GateError("seq2 identity broken")
    cases = {
        "dropped downstream terminal": {"terminal_WOOD_NONPOSITIVE": -1},
        "dropped ACCEPT terminal": {"terminal_ACCEPT": -1},
        "falsified seq2 PASS": {"terminal_SEQ2_PASS": +1},
        "falsified seq2 row count": {"seq2_rows": +1},
    }
    for name, delta in cases.items():
        m = collections.Counter(counts)
        for k, d in delta.items():
            m[k] += d
        try:
            check(m)
        except GateError:
            print(f"    chain control OK — rejects: {name}")
        else:
            raise GateError(f"CHAIN CONTROL FAILED: accepted {name}")


def main():
    cfg = json.loads(H.CONFIG.read_text())
    sits = H.load_situations(None)
    got = sorted(s["id"] for s in sits)
    if got != FIXTURES:                                             # point 4
        raise GateError(f"fixture set is not exactly OSC-001..034: {set(FIXTURES) ^ set(got)}")

    report = {}
    for label, (subj, probe, sha) in SUBJECTS.items():
        sp, pp = REPO / subj, REPO / probe
        if hashlib.sha256(sp.read_bytes()).hexdigest() != sha:
            raise GateError(f"{label}: subject digest differs")
        wd = Path(tempfile.mkdtemp(prefix="g1u-"))
        (wd / "i").mkdir(); (wd / "p").mkdir()
        instr = H.compile_candidate(pp, wd / "i")
        plain = H.compile_candidate(sp, wd / "p")
        tot, byfix, ctl_done = collections.Counter(), {}, False
        for sit in sits:
            err = C.check_parity(sit, cfg, plain, instr)            # point 4: parity per fixture
            gates, terms, joined = parse_join(err)
            # controls need a fixture that actually contains attributions; OSC-001 has none,
            # and running them on an empty stream would "pass" while testing nothing.
            if not ctl_done and any(l.startswith("UATTR ") for l in err.splitlines()):
                try:
                    print(f"  {label}: negative controls (on {sit['id']})")
                    controls(err); ctl_done = True
                except _NoReorderPair:
                    print(f"    {sit['id']} has no two differing attributions — trying next")
            c = collections.Counter()
            c["eligible_calls"] = sum(1 for g in gates if g[1] == "PASS")
            for _, _, clause in terms:
                c["terminal_" + clause] += 1
                c["terminals"] += 1
            for j in joined:
                c[j["verdict"]] += 1
                if j["opp_chop"] != j["on_tree"]:
                    c["opp_chop_mismatch"] += 1
            # CHAIN CLOSURE (codex_1): identities over DIFFERENT row classes, so a plant
            # evaluation vanishing through an unlogged exit breaks them. The old
            # terminals==sum(terminal_*) compared emitted rows with themselves and could not.
            seq2_rows = c["terminal_PREDICT_TREE_NONE"] + c["terminal_SEQ2_PASS"]
            later = sum(c["terminal_" + k] for k in ("PREDICTED_NONPOSITIVE",
                                                     "CHOP_OUTCOME_NONE", "ROUND_TRIP_CLOCK",
                                                     "WOOD_NONPOSITIVE"))
            if c["terminal_SEQ2_PASS"] != c["terminal_ACCEPT"] + later:
                raise GateError(f"{sit['id']}: chain open — seq2 PASS {c['terminal_SEQ2_PASS']} "
                                f"!= ACCEPT {c['terminal_ACCEPT']} + later rejections {later}")
            c["seq2_rows"] = seq2_rows; c["later_rejections"] = later
            # point 5: per-fixture cross-sums, fail closed
            if c["terminal_PREDICT_TREE_NONE"] != len(joined):
                raise GateError(f"{sit['id']}: terminals != attributions")
            if c["EVIDENCE_BASED"] + c["UNEXPLAINED"] != len(joined):
                raise GateError(f"{sit['id']}: verdicts do not sum to attributions")
            byfix[sit["id"]] = dict(c); tot.update(c)
        chain_controls(tot)
        if not ctl_done:
            raise GateError(f"{label}: negative controls never ran — no fixture had attributions")
        s = sum(v for k, v in tot.items() if k.startswith("terminal_"))
        if s != tot["terminals"]:
            raise GateError(f"{label}: aggregate terminal cross-sum failed")
        report[label] = {"totals": dict(tot), "by_fixture": byfix,
                         "subject_sha256": sha, "probe_sha256":
                         hashlib.sha256(pp.read_bytes()).hexdigest()}
        print(f"    chain: seq2 rows {tot['seq2_rows']} = PTN {tot['terminal_PREDICT_TREE_NONE']}"
              f" + seq2PASS {tot['terminal_SEQ2_PASS']}; seq2PASS = ACCEPT {tot['terminal_ACCEPT']}"
              f" + later {tot['later_rejections']}")
        print(f"  {label}: eligible {tot['eligible_calls']} · terminals {tot['terminals']} "
              f"(ACCEPT {tot['terminal_ACCEPT']}, PREDICT_TREE_NONE "
              f"{tot['terminal_PREDICT_TREE_NONE']}) · EVIDENCE_BASED {tot['EVIDENCE_BASED']} · "
              f"UNEXPLAINED {tot['UNEXPLAINED']} · opp_chop mismatch {tot['opp_chop_mismatch']}")

    # point 6: the fictional-chop mismatch control must FIRE on cure C
    if report["cure-C-resident"]["totals"].get("UNEXPLAINED", 0) == 0:
        raise GateError("cure-C mismatch control did NOT fire — attribution is not evidence")
    print("\n  cure-C mismatch control FIRED (unexplained rejections present on the resident)")
    out = REPO / "claude_1/chop4c/gate1-unified-2026-08-19.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"  wrote {out.relative_to(REPO)}")
    cand = report["door1-candidate"]["totals"]
    print(f"\n  gate-1 green condition (zero UNEXPLAINED under candidate): "
          f"{'MET' if cand.get('UNEXPLAINED', 0) == 0 else 'NOT MET'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
