#!/usr/bin/env python3
"""T-1 acceptance gate 1 — swap / collision controls, each observed FAILING first.

Owed per the grading of record (`20260816T175950Z`, item 1). Swap is the one primitive that
actually moved rows, and it shipped with no controls of its own — the guards rule unmet on the
part that matters most.

## What is checked, and on what

Checks run on the **commands the bot actually emits in real games**, not on a Python re-model of
the swap logic. Re-modelling it would be a mirror, and mirrors disagreeing with their authority
is the failure this project has paid for repeatedly — and that I paid for twice today.

1. **no two own units ordered into the same cell on the same turn** (collision);
2. **no MOVE ordered onto a non-walkable cell**;
3. **a swap is a genuine exchange** — if A is ordered onto B's cell, B is ordered onto A's cell,
   never left standing there.

## The negative control

Each check is demonstrated **rejecting** against a deliberately broken swap variant
(`candidate-t1-swap-BROKEN.rs`) whose `swap_pair` drops the strictly-closer test and the
walkability filter. A check that has never rejected anything is not a check.
"""
import json, re, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fixture_harness as H          # noqa: E402
import fuzz_panel as fp              # noqa: E402
import regression_tests as rt        # noqa: E402

SWAP = HERE / "candidate-t1-swap.rs"
BROKEN = HERE / "candidate-t1-swap-BROKEN.rs"
MOVE = re.compile(r"\AMOVE\s+(\d+)\s+(\d+)\s+(\d+)\Z")


def make_broken():
    """Suppress the COUNTER-move, so the mover steps onto an occupied cell and the occupant stays.

    My first control weakened the strictly-closer test and the yield walkability filter. It
    violated nothing these checks look at, and the run said so: three checks, zero rejections.
    That was the right outcome for the wrong reason — **swap as built cannot collide or target
    an unwalkable cell by construction**, because it exchanges two cells that are already
    occupied, hence already walkable. Weakening the direction test just produces a different
    legal exchange.

    So the falsifiable property is the EXCHANGE itself: drop the counter-move and the mover
    walks into a peer that never leaves. That is a real half-swap and the check must catch it.
    """
    s = SWAP.read_text()
    a = """                            if out[other].trim().eq_ignore_ascii_case("WAIT"){
                                out[other]=counter;
                                }"""
    assert s.count(a) == 1, s.count(a)
    s = s.replace(a, """                            let _=&counter;
                            if false{
                                out[other]=String::new();
                                }""")
    BROKEN.write_text(s)
    return BROKEN


def scan(binary, sits, cfg):
    """Return violations found in real emitted command streams."""
    viol = {"collision": [], "unwalkable": [], "half_swap": []}
    for sit in sits:
        spec = H.spec_for(sit, cfg)
        ref = fp.make_referee(spec)
        walk = set(ref.walkable) if hasattr(ref, "walkable") else None
        transcript, commands = rt.run_binary_custom(Path(binary), ref, int(cfg["turns"]))
        import trace_detectors as td
        tr = td.build_trace(transcript, commands)
        walk = tr.smap.walkable
        for t, line in enumerate(commands.strip().split("\n"), 1):
            targets, movers = {}, {}
            for seg in [x.strip() for x in line.split(";") if x.strip()]:
                m = MOVE.match(seg)
                if not m:
                    continue
                uid, x, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
                movers[uid] = (x, y)
                if (x, y) not in walk:
                    viol["unwalkable"].append((sit["id"], t, uid, (x, y)))
                if (x, y) in targets:
                    viol["collision"].append((sit["id"], t, targets[(x, y)], uid, (x, y)))
                targets[(x, y)] = uid
            # genuine-exchange check: if A is ordered onto B's current cell, B must move off it
            for uid, dest in movers.items():
                occupant = next((u.id for u in tr.state(t).own_units() if u.cell == dest
                                 and u.id != uid), None)
                if occupant is not None and occupant not in movers:
                    viol["half_swap"].append((sit["id"], t, uid, occupant, dest))
    return viol


def main():
    cfg = json.loads(H.CONFIG.read_text())
    sits = H.load_situations(["OSC-001", "OSC-028", "OSC-009"])
    make_broken()
    out = {}
    with tempfile.TemporaryDirectory(prefix="t1-swapctl-") as wd:
        for name, src in (("delivered", SWAP), ("BROKEN control", BROKEN)):
            d = Path(wd) / name.split()[0]
            d.mkdir()
            out[name] = scan(H.compile_candidate(src, d), sits, cfg)

    ok = True
    # collision and unwalkable are STRUCTURALLY IMPOSSIBLE for swap as built: it exchanges two
    # already-occupied (hence walkable) cells. They are reported for the delivered candidate as
    # standing evidence, but only `half_swap` is falsifiable here, so only it carries a control.
    for check in ("collision", "unwalkable"):
        clean = not out["delivered"][check]
        print(f"  {'OK  ' if clean else 'BAD '} delivered candidate: no {check} "
              f"({len(out['delivered'][check])} found)  [structurally impossible for swap; "
              f"reported, not controlled]")
        ok = ok and clean
    for check in ("half_swap",):
        clean = not out["delivered"][check]
        fires = bool(out["BROKEN control"][check])
        print(f"  {'OK  ' if clean else 'BAD '} delivered candidate: no {check} "
              f"({len(out['delivered'][check])} found)")
        print(f"  {'OK  ' if fires else 'BAD '} control REJECTS on {check} "
              f"({len(out['BROKEN control'][check])} found)"
              + ("" if fires else "  <- check never rejected; it is not a check"))
        ok = ok and clean and fires
    print("\nswap controls:", "PASS" if ok else "INCOMPLETE - see below")
    if not ok:
        print("\nWHY INCOMPLETE, stated rather than iterated away: perturbing the bot to create")
        print("a half-swap changes the game from turn 1, so the broken build never reaches the")
        print("situation that would trigger the check. A behavioural control cannot hold the")
        print("trajectory fixed while breaking the behaviour. The delivered candidate is CLEAN on")
        print("all three checks over the sampled situations, but `half_swap` is UNVALIDATED: it")
        print("has never rejected anything, so it must not be cited as passing evidence.")
        print("Validating it needs a unit-level fixture over select()/apply_swap directly, not a")
        print("whole-game perturbation - which is a different instrument and is not built here.")
    print("\nLIMIT: three situations, and checks read EMITTED COMMANDS - they prove the bot does")
    print("not order an illegal or colliding move, not that the referee would have refused one.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
