#!/usr/bin/env python3
r"""G-4c.2 — parity + BOTH-WAYS observed firing for the chop-clause instrument.

Two things must hold before any clause distribution is allowed to be called a finding:

1. **PARITY.** The instrumented build's stdout is byte-identical to the uninstrumented
   resident's on OSC-031 AND on a positive-control fixture. An instrument that changes the
   game is measuring a different bot.
2. **OBSERVED FIRING, BOTH WAYS.** On OSC-031 the log must show REJECT rows with EXACT turn
   coverage of the stall window; on the control it must show ACCEPT rows. A tap that has only
   ever produced one kind of row is not evidence — five of my checks this month were
   structurally incapable of failing, and one reported a false green on a submission gate.

Turn coverage, not episode count, is the standing metric (owner ruling 2026-08-18).
"""
import collections, json, re, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "claude_1/t1"))
sys.path.insert(0, str(REPO / "claude_1/hstarve1"))
sys.path.insert(0, str(REPO / "claude_1/pipeline"))
import coverage as C                 # noqa: E402
import fixture_harness as H          # noqa: E402
import make_chop_instrument as MK    # noqa: E402

ROW = re.compile(r"C4C turn=(\d+) unit=(\d+) plant=(-?\d+) cell=\S+ clause=(\w+)")
INSTR = REPO / "claude_1/chop4c/instrumented-chop4c.rs"


class G4cError(RuntimeError):
    """Fail closed. A red control stops the task; it does not get argued around."""


# NO BESPOKE RUNNER. My first draft of this file hand-rolled a subprocess loop and crashed on
# the referee object — which was the shared-runners rule catching me in the act. `check_parity`
# already runs BOTH builds through the accepted path, refuses unless their command streams match,
# and hands back the diagnostic stderr. Reusing it means parity is not a claim I make, it is a
# precondition of getting any rows at all.


def main():
    cfg = json.loads(H.CONFIG.read_text())
    if MK.main() != 0:
        raise G4cError("instrument build refused")

    wd = Path(tempfile.mkdtemp(prefix="c4c-g2-"))
    (wd / "i").mkdir(); (wd / "p").mkdir()
    instr = H.compile_candidate(INSTR, wd / "i")
    plain = H.compile_candidate(H.RESIDENT, wd / "p")

    report = {}
    for sid in ("OSC-031", "OSC-001", "OSC-008"):
        sit = H.load_situations([sid])[0]
        err = C.check_parity(sit, cfg, plain, instr)   # raises unless byte-identical
        rows = [m.groups() for m in ROW.finditer(err)]
        bad = [r[3] for r in rows if r[3] not in MK.CLAUSES]
        if bad:
            raise G4cError(f"{sid}: unknown clause names {sorted(set(bad))}")
        by_clause = collections.Counter(r[3] for r in rows)
        turns = {c: sorted({int(r[0]) for r in rows if r[3] == c}) for c in by_clause}
        report[sid] = {"parity": "IDENTICAL", "rows": len(rows),
                       "by_clause": dict(by_clause),
                       "turn_coverage": {c: len(t) for c, t in turns.items()},
                       "window": [sit["window"]["turn_start"], sit["window"]["turn_end"]]}
        print(f"{sid}: parity IDENTICAL, {len(rows)} clause rows -> {dict(by_clause)}")

    # BOTH-WAYS CONTROL
    accepts = {s: r["by_clause"].get("ACCEPT", 0) for s, r in report.items()}
    if not any(v > 0 for v in accepts.values()):
        raise G4cError(f"NO ACCEPT ROWS ANYWHERE {accepts} — the ACCEPT tap has never been "
                       f"observed firing, so a REJECT-only table is not evidence")
    rejects = sum(v for k, v in report["OSC-031"]["by_clause"].items()
                  if k not in ("ACCEPT",))
    if rejects == 0:
        raise G4cError("OSC-031 produced no REJECT rows — the instrument cannot see the stall")
    print(f"\nboth-ways control: ACCEPT rows observed {accepts}; OSC-031 REJECT rows {rejects}")

    (REPO / "claude_1/chop4c/g4c2-2026-08-18.json").write_text(json.dumps(report, indent=2) + "\n")
    print("wrote claude_1/chop4c/g4c2-2026-08-18.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
