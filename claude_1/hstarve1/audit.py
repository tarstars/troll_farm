#!/usr/bin/env python3
"""H-STARVE-1 — run the instrumented build over specimens and emit the CAUSE table.

Labels are the coordinator's four: STUCK_COMMITMENT / NO_WORK_ON_MAP / GENERATOR_GAP / OTHER.

**Packet-lite SLICE, never packet completeness.** This captures one unit's routing branch and
candidate count on each turn. It is not the §4-§17 Decision Packet contract and must never be
cited as one.

**Non-interference is verified, not assumed.** `check_noninterference()` runs the uninstrumented
resident and the instrumented build on the same spec and requires byte-identical command streams.
If they differ, the diagnostics describe a different bot and the table is void.
"""
import json, re, subprocess, sys, tempfile, collections
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "claude_1/t1"))
import fixture_harness as H   # noqa: E402
import fuzz_panel as fp       # noqa: E402

INSTR = REPO / "claude_1/hstarve1/instrumented-hstarve1.rs"
HS1 = re.compile(r"HS1 turn=(\d+) unit=(\d+) cell=(-?\d+),(-?\d+) branch=(\w+) "
                 r"endgame=(\w+) committed=(\w+) n=(\d+) all_none=(\w+)")


def run_capturing_stderr(binary, referee, turns):
    """Mirror of regression_tests.run_binary_custom that also captures stderr."""
    header = referee.map_header()
    transcript_parts, command_lines = [header], []
    proc = subprocess.Popen([str(binary)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)
    try:
        proc.stdin.write(header); proc.stdin.flush()
        for _ in range(turns):
            block = referee.turn_text()
            transcript_parts.append(block)
            proc.stdin.write(block); proc.stdin.flush()
            line = proc.stdout.readline()
            if not line:
                break
            line = line.rstrip("\n")
            command_lines.append(line)
            referee.apply(line)
        proc.stdin.close()
    finally:
        err = proc.stderr.read()
        proc.wait()
    return "".join(transcript_parts), "\n".join(command_lines) + "\n", err


def check_noninterference(sit, cfg, plain_bin, instr_bin):
    spec = H.spec_for(sit, cfg)
    import regression_tests as rt
    _, c_plain = rt.run_binary_custom(Path(plain_bin), fp.make_referee(spec), int(cfg["turns"]))
    _, c_instr, _ = run_capturing_stderr(instr_bin, fp.make_referee(spec), int(cfg["turns"]))
    return c_plain.strip() == c_instr.strip()


def classify(rows, sit):
    """Assign a CAUSE for the idle unit of this situation."""
    w = sit["window"]
    lo, hi = w["turn_start"], w["turn_end"]
    # the parked unit: an own unit that is NOT the dancer named in the window
    per_unit = collections.defaultdict(list)
    for r in rows:
        if lo <= r["turn"] <= hi:
            per_unit[r["unit"]].append(r)
    parked = {u: rs for u, rs in per_unit.items() if u != w["unit"]}
    out = []
    for uid, rs in sorted(parked.items()):
        empty = [r for r in rs if r["n"] == 0]
        allnone = [r for r in rs if r["all_none"]]
        committed = [r for r in rs if r["committed"]]
        midgame_commit = [r for r in committed if not r["endgame"]]
        if midgame_commit and (empty or allnone):
            cause = "STUCK_COMMITMENT"
        elif empty and not committed:
            cause = "GENERATOR_GAP"
        elif allnone and not empty:
            # UNSUPPORTED BY THIS INSTRUMENT. "All candidates are WAIT" is the GENERATOR'S
            # OUTPUT, not a fact about the world. Calling it NO_WORK_ON_MAP assumes the
            # conclusion: a generator that fails to see available work produces the same
            # signal. Distinguishing the two needs the world-state predicate
            # `fuzz_panel.work_remaining(tr, t)` (:1756), which this slice does not read.
            cause = "ALL_WAIT_CAUSE_UNDETERMINED"
        elif not rs:
            cause = "OTHER"
        else:
            cause = "OTHER"
        out.append({
            "situation": sit["id"], "parked_unit": uid, "cause": cause,
            "turns_observed": len(rs), "turns_empty_candidates": len(empty),
            "turns_all_wait": len(allnone), "turns_committed": len(committed),
            "turns_committed_midgame": len(midgame_commit),
            "branches": dict(collections.Counter(r["branch"] for r in rs)),
        })
    return out


def parse(err):
    rows = []
    for m in HS1.finditer(err):
        rows.append({"turn": int(m.group(1)), "unit": int(m.group(2)),
                     "cell": (int(m.group(3)), int(m.group(4))), "branch": m.group(5),
                     "endgame": m.group(6) == "true", "committed": m.group(7) == "true",
                     "n": int(m.group(8)), "all_none": m.group(9) == "true"})
    return rows


def main():
    only = sys.argv[1].split(",") if len(sys.argv) > 1 else None
    cfg = json.loads(H.CONFIG.read_text())
    sits = H.load_situations(only)
    table = []
    with tempfile.TemporaryDirectory(prefix="hs1-") as wd:
        di, dp = Path(wd) / "i", Path(wd) / "p"
        di.mkdir(); dp.mkdir()
        instr = H.compile_candidate(INSTR, di)
        plain = H.compile_candidate(H.RESIDENT, dp)
        first = True
        for sit in sits:
            if first:
                ok = check_noninterference(sit, cfg, plain, instr)
                print(f"non-interference on {sit['id']}: "
                      f"{'IDENTICAL command stream' if ok else 'DIFFERS — TABLE IS VOID'}")
                if not ok:
                    return 1
                first = False
            spec = H.spec_for(sit, cfg)
            _, _, err = run_capturing_stderr(instr, fp.make_referee(spec), int(cfg["turns"]))
            rows = parse(err)
            table.extend(classify(rows, sit))
    counts = collections.Counter(r["cause"] for r in table)
    print(f"\nCAUSE table — {len(table)} parked-unit observations over {len(sits)} situations")
    for r in table:
        print(f"  {r['situation']}  unit {r['parked_unit']}  {r['cause']:<18} "
              f"obs={r['turns_observed']:>3} empty={r['turns_empty_candidates']:>3} "
              f"allWAIT={r['turns_all_wait']:>3} commit(mid)={r['turns_committed_midgame']:>3} "
              f"{r['branches']}")
    print(f"\ntotals: {dict(counts)}")
    out = REPO / "claude_1/hstarve1/cause-table-2026-08-16.json"
    out.write_text(json.dumps({"table": table, "totals": dict(counts)}, indent=1,
                              sort_keys=True) + "\n")
    print(f"wrote {out.relative_to(REPO)}")
    print("\nNOTE: ALL_WAIT_CAUSE_UNDETERMINED is deliberate. Separating NO_WORK_ON_MAP from")
    print("GENERATOR_GAP needs fuzz_panel.work_remaining(tr,t) (:1756), which this slice does")
    print("not read. Labelling it NO_WORK_ON_MAP would assume the conclusion.")
    print("\nLABEL: Packet-lite SLICE. Routing branch + candidate count for one unit per turn.")
    print("NOT Decision Packet completeness and must never be cited as such.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
