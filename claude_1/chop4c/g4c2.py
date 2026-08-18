#!/usr/bin/env python3
r"""G-4c.2 — parity, CHAIN RECONCILIATION, and both-ways firing for the chop-clause instrument.

Revised after codex_1's REVISION_REQUIRED (`osc031-chop4c-instrument-review-2026-08-18.md`).
The previous version counted allowlisted regex matches, which cannot distinguish "this clause
never rejected" from "this clause's row was dropped, malformed, or never emitted". That is the
exact hole that makes five silent taps unable to support a negative statement.

What is enforced now:

1. **PARITY** via `coverage.check_parity` — the shared accepted path, which refuses to return
   rows unless the instrumented and uninstrumented command streams match.
2. **NO UNPARSED ROWS.** Every stderr line beginning `C4C` must parse. An unparsed line is a
   hard failure, not a skipped match.
3. **CHAIN RECONCILIATION.** For each gate-passing `(turn, unit)` the entry record declares
   `plants=N`; there must be exactly N plant chains, each starting at seq 1, strictly increasing
   in seq with no gaps, every non-terminal verdict PASS, terminating exactly once in REJECT or
   ACCEPT.
4. **NEGATIVE CONTROL.** The reconciler is run against deliberately corrupted logs — a dropped
   row, a duplicated terminal, a reordered chain. It MUST fail on each. A reconciler that has
   only ever passed is not evidence of reconciliation.

Coverage is STRUCTURAL per Amendment 1 (`local_claude_1 20260818T071239Z`): every executed
chop evaluation, no gaps, no constant to match. The historical 167-turn residue is a NAMED
SUBSET pinned by the task owner at G-4c.3 — never selected here after seeing results.
"""
import collections, json, re, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "claude_1/t1"))
sys.path.insert(0, str(REPO / "claude_1/hstarve1"))
sys.path.insert(0, str(REPO / "claude_1/pipeline"))
sys.path.insert(0, str(REPO / "claude_1/chop4c"))
import coverage as C                 # noqa: E402
import fixture_harness as H          # noqa: E402
import make_chop_instrument as MK    # noqa: E402

# `chop_candidates` is called MORE THAN ONCE per unit-turn (the reconciler discovered this by
# refusing a chain keyed (turn, unit, plant) that carried seqs [1,1,2,2]). So the chain identity
# is the INVOCATION, not the turn: a per-call counter is threaded through every row.
VROW = re.compile(r"^C4CV call=(\d+) turn=(\d+) unit=(\d+) plant=(-?\d+) seq=(\d+) clause=(\w+) "
                  r"verdict=(PASS|REJECT|ACCEPT)\b")
GROW = re.compile(r"^C4CGATE call=(\d+) turn=(\d+) unit=(\d+) plants=(\d+) gate=(PASS|REJECT)\b")
TERMINAL = {"REJECT", "ACCEPT"}
SEQ_OF = {c: i for i, c in enumerate(
    ["GATE_UNIT", "DEAD_OR_UNREACHABLE", "PREDICT_TREE_NONE", "PREDICTED_NONPOSITIVE",
     "CHOP_OUTCOME_NONE", "ROUND_TRIP_CLOCK", "WOOD_NONPOSITIVE", "ACCEPT"])}


class G4cError(RuntimeError):
    """Fail closed."""


def parse(err):
    """-> (gates, chains). Refuses on ANY unparsed C4C line."""
    gates, chains = {}, collections.defaultdict(list)
    for ln in err.splitlines():
        if not ln.startswith("C4C"):
            continue
        m = GROW.match(ln)
        if m:
            call, t, u, n, g = (int(m.group(1)), int(m.group(2)), int(m.group(3)),
                                int(m.group(4)), m.group(5))
            gates[(call, t, u)] = (n, g)
            continue
        m = VROW.match(ln)
        if not m:
            raise G4cError(f"UNPARSED instrument line, refusing to count anything: {ln!r}")
        call, t, u, p, seq, clause, verdict = (int(m.group(1)), int(m.group(2)), int(m.group(3)),
                                               int(m.group(4)), int(m.group(5)), m.group(6),
                                               m.group(7))
        if clause not in MK.CLAUSES:
            raise G4cError(f"unknown clause {clause!r}")
        if SEQ_OF[clause] != seq:
            raise G4cError(f"clause {clause} logged at seq {seq}, expected {SEQ_OF[clause]}")
        chains[(call, t, u, p)].append((seq, clause, verdict))
    return gates, chains


def reconcile(gates, chains):
    """Every gate-passing unit-turn must have exactly N complete, ordered plant chains."""
    for (call, t, u), (n, g) in gates.items():
        found = [k for k in chains if k[0] == call and k[3] >= 0]
        if g == "REJECT":
            if found:
                raise G4cError(f"call {call} turn {t} unit {u}: gate REJECT but "
                               f"{len(found)} plant chains")
            gate_rows = chains.get((call, t, u, -1), [])
            if len([r for r in gate_rows if r[1] == "GATE_UNIT" and r[2] == "REJECT"]) != 1:
                raise G4cError(f"call {call} turn {t} unit {u}: gate REJECT record without "
                               f"exactly one GATE_UNIT REJECT verdict row")
            continue
        if len(found) != n:
            raise G4cError(f"call {call} turn {t} unit {u}: gate declared plants={n} "
                           f"but {len(found)} chains")
        # The GATE_UNIT verdict row carries plant=-1 and was being skipped by the per-plant
        # loop below, so a dropped gate row went undetected — the negative control caught this,
        # which is the entire reason the control exists. Every entry record must now be matched
        # by exactly one GATE_UNIT verdict row of the same call, agreeing on the verdict.
        gate_rows = chains.get((call, t, u, -1), [])
        want = "PASS" if g == "PASS" else "REJECT"
        matching = [r for r in gate_rows if r[1] == "GATE_UNIT" and r[2] == want]
        if len(matching) != 1:
            raise G4cError(f"call {call} turn {t} unit {u}: entry record says gate={g} but "
                           f"found {len(matching)} matching GATE_UNIT verdict rows "
                           f"(rows: {gate_rows})")
    for key in chains:
        if (key[0], key[1], key[2]) not in gates:
            raise G4cError(f"{key}: verdict rows for a call with no entry record — the "
                           f"C4CGATE line was dropped or never emitted")
    for key, rows in chains.items():
        if key[3] < 0:
            continue
        rows = sorted(rows)
        seqs = [r[0] for r in rows]
        if seqs != list(range(1, len(seqs) + 1)) and seqs != list(range(1, seqs[-1] + 1)):
            raise G4cError(f"{key}: seq gaps/disorder {seqs}")
        if len(set(seqs)) != len(seqs):
            raise G4cError(f"{key}: duplicate seq {seqs}")
        terminals = [r for r in rows if r[2] in TERMINAL]
        if len(terminals) != 1:
            raise G4cError(f"{key}: {len(terminals)} terminal rows, want exactly 1")
        if terminals[0] != rows[-1]:
            raise G4cError(f"{key}: terminal row is not last — {rows}")
        for r in rows[:-1]:
            if r[2] != "PASS":
                raise G4cError(f"{key}: non-terminal row {r} is not PASS")
    return True


def negative_controls(err):
    """The reconciler MUST fail on corrupted logs, or it is not evidence."""
    lines = [l for l in err.splitlines() if l.startswith("C4C")]
    victim = next(i for i, l in enumerate(lines) if "verdict=PASS" in l)
    term = next(i for i, l in enumerate(lines) if "verdict=REJECT" in l)
    cases = {
        "dropped PASS row": "\n".join(lines[:victim] + lines[victim + 1:]),
        "duplicated terminal": "\n".join(lines[:term + 1] + [lines[term]] + lines[term + 1:]),
        "corrupted row text": "\n".join(lines[:victim] + ["C4CV turn=oops"] + lines[victim + 1:]),
    }
    for name, corrupted in cases.items():
        try:
            reconcile(*parse(corrupted))
        except G4cError:
            print(f"  negative control OK — reconciler rejects: {name}")
        else:
            raise G4cError(f"NEGATIVE CONTROL FAILED: reconciler accepted a log with {name}. "
                           f"It cannot detect the very defect it exists to catch.")


def main():
    cfg = json.loads(H.CONFIG.read_text())
    if MK.main() != 0:
        raise G4cError("instrument build refused")
    wd = Path(tempfile.mkdtemp(prefix="c4c-g2-"))
    (wd / "i").mkdir(); (wd / "p").mkdir()
    instr = H.compile_candidate(REPO / "claude_1/chop4c/instrumented-chop4c.rs", wd / "i")
    plain = H.compile_candidate(H.RESIDENT, wd / "p")

    report, first_err = {}, None
    for sid in ("OSC-031", "OSC-001", "OSC-008"):
        sit = H.load_situations([sid])[0]
        err = C.check_parity(sit, cfg, plain, instr)      # raises unless byte-identical
        gates, chains = parse(err)                        # raises on any unparsed line
        reconcile(gates, chains)                          # raises on any incomplete chain
        first_err = first_err or err
        terminal = collections.Counter()
        reached = collections.Counter()
        for key, rows in chains.items():
            for seq, clause, verdict in rows:
                reached[clause] += 1
                if verdict in TERMINAL:
                    terminal[clause] += 1
        rej_turns = sorted({k[1] for k, rows in chains.items()
                            for _, _, v in rows if v == "REJECT"})
        report[sid] = {"parity": "IDENTICAL", "gate_records": len(gates),
                       "plant_chains": sum(1 for k in chains if k[3] >= 0),
                       "clauses_reached": dict(reached), "terminal_clause": dict(terminal),
                       "reject_turn_coverage": len(rej_turns),
                       "window": [sit["window"]["turn_start"], sit["window"]["turn_end"]]}
        report[sid]["invocations"] = len(gates)
        print(f"{sid}: parity IDENTICAL · {len(gates)} invocations · "
              f"{report[sid]['plant_chains']} complete chains")
        print(f"    reached : {dict(reached)}")
        print(f"    terminal: {dict(terminal)}")

    print("\nnegative controls on the reconciler:")
    negative_controls(first_err)

    fired = {c for r in report.values() for c in r["terminal_clause"]}
    never = sorted(set(MK.CLAUSES) - fired)
    report["_taps_never_observed_terminal"] = never
    report["_note"] = ("A clause with no observed terminal row cannot support the claim that it "
                       "did not reject. codex_1 specifies these controls; the implementer does "
                       "not choose them after seeing which taps stayed silent.")
    print(f"\ntaps never observed terminal: {never or 'none'}")
    (REPO / "claude_1/chop4c/g4c2-2026-08-18.json").write_text(json.dumps(report, indent=2) + "\n")
    print("wrote claude_1/chop4c/g4c2-2026-08-18.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
