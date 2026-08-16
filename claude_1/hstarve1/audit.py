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
import json, re, subprocess, sys, tempfile, collections, threading
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "claude_1/t1"))
import fixture_harness as H   # noqa: E402
import fuzz_panel as fp       # noqa: E402
import trace_detectors as td  # noqa: E402

INSTR = REPO / "claude_1/hstarve1/instrumented-hstarve1.rs"
HS1 = re.compile(r"HS1 turn=(\d+) unit=(\d+) cell=(-?\d+),(-?\d+) branch=(\w+) "
                 r"endgame=(\w+) committed=(\w+) n=(\d+) all_none=(\w+)")


def run_capturing_stderr(binary, referee, turns):
    """Mirror of regression_tests.run_binary_custom that also captures stderr.

    **stderr is drained on a THREAD, and that is not a detail.** The first version read
    `proc.stderr` only after the turn loop finished. A diagnostic build emits far more than the
    ~64 KB pipe buffer over 200 turns, so the child BLOCKED on its own stderr write partway
    through the game and its command stream was silently truncated. The audit would then have
    described a bot that stopped playing rather than one that was starved.

    Found by strengthening non-interference to every situation instead of only the first: it
    failed on OSC-002 immediately. The weaker check passed because OSC-001 happened to stay
    under the buffer — a limit I had named and, until now, tolerated.
    """
    header = referee.map_header()
    transcript_parts, command_lines = [header], []
    proc = subprocess.Popen([str(binary)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)
    chunks = []
    drain = threading.Thread(target=lambda: chunks.append(proc.stderr.read()), daemon=True)
    drain.start()
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
        proc.wait()
        drain.join(timeout=30)
    return "".join(transcript_parts), "\n".join(command_lines) + "\n", "".join(chunks)


def check_noninterference(sit, cfg, plain_bin, instr_bin):
    spec = H.spec_for(sit, cfg)
    import regression_tests as rt
    _, c_plain = rt.run_binary_custom(Path(plain_bin), fp.make_referee(spec), int(cfg["turns"]))
    _, c_instr, _ = run_capturing_stderr(instr_bin, fp.make_referee(spec), int(cfg["turns"]))
    return c_plain.strip() == c_instr.strip()


def world_offers_work(tr, lo, hi):
    """INCREMENT 2 — the world-state check that increment 1 deliberately lacked.

    `fuzz_panel.work_remaining(tr, t)` (:1756) is the referee-world predicate: True iff the
    world still offers the own player a resource action (own cargo to bank/plant, or a plant
    standing on a reachable cell). It reads the world, NOT the generator's output — which is
    exactly the distinction increment 1 could not make and refused to fake.

    Reused rather than re-derived: a second definition of "there is work" would let the phrase
    mean one thing to the gate and another to this audit.

    **KNOWN IMPRECISION, stated not buried.** `work_remaining` is a PLAYER-level predicate: its
    reachability BFS is multi-source over ALL own units (`fuzz_panel:1774`). So a plant reachable
    only by the DANCER counts as "work remains" even if the parked unit can reach nothing. The
    GENERATOR_GAP label therefore means *the world offered the player a resource action while
    this unit was handed only WAIT* — strong, but not yet *this unit had reachable work*. A
    per-unit refinement (BFS from the parked unit's cell alone) is the next increment and could
    move some rows to NO_WORK_ON_MAP.
    """
    turns = [t for t in range(lo, min(hi, tr.T) + 1)]
    offered = [t for t in turns if fp.work_remaining(tr, t)]
    return len(offered), len(turns)


def unit_offered_work(tr, uid, lo, hi):
    """INCREMENT 3 — the PER-UNIT refinement of `work_remaining`.

    Same two clauses as the authority (`fuzz_panel.work_remaining`, :1756) — own cargo to
    bank/plant, or a standing plant on a reachable cell — with ONE narrowing: reachability is
    BFS from **this unit's cell alone**, not multi-source over every own unit.

    This is deliberately a *narrowing of the authority's predicate*, not a new idea about what
    work is. The clauses are copied so the two cannot drift; only the source set differs, and
    that difference is the entire question increment 2 left open: a plant reachable only by the
    DANCER made the player-level predicate true while telling us nothing about the parked unit.
    """
    offered = 0
    total = 0
    for t in range(lo, min(hi, tr.T) + 1):
        st = tr.state(t)
        u = tr.unit(uid, t)
        if u is None:
            continue
        total += 1
        if sum(u.carry):
            offered += 1
            continue
        if not st.plants:
            continue
        reach = td.bfs_distances(tr.smap.walkable, [u.cell])
        if any(p.cell in reach for p in st.plants):
            offered += 1
    return offered, total


def classify(rows, sit, tr=None):
    """Assign a CAUSE for the idle unit of this situation."""
    w = sit["window"]
    lo, hi = w["turn_start"], w["turn_end"]
    # the parked unit: an own unit that is NOT the dancer named in the window
    per_unit = collections.defaultdict(list)
    for r in rows:
        if lo <= r["turn"] <= hi:
            per_unit[r["unit"]].append(r)
    parked = {u: rs for u, rs in per_unit.items() if u != w["unit"]}
    work_turns, total_turns = world_offers_work(tr, lo, hi) if tr is not None else (0, 0)
    out = []
    for uid, rs in sorted(parked.items()):
        unit_work, unit_total = (unit_offered_work(tr, uid, lo, hi) if tr is not None
                                 else (0, 0))
        empty = [r for r in rs if r["n"] == 0]
        allnone = [r for r in rs if r["all_none"]]
        committed = [r for r in rs if r["committed"]]
        midgame_commit = [r for r in committed if not r["endgame"]]
        if midgame_commit and (empty or allnone):
            cause = "STUCK_COMMITMENT"
        elif empty and not committed:
            cause = "GENERATOR_GAP"
        elif allnone and not empty:
            # Increment 2: now decidable. The generator emitted only WAIT; ask the WORLD
            # whether work was available on those turns.
            if tr is None:
                cause = "ALL_WAIT_CAUSE_UNDETERMINED"
            elif unit_work > 0:
                # THIS unit could itself reach work, and was still handed only WAIT
                cause = "GENERATOR_GAP"
            elif work_turns > 0:
                # the player had work but this unit could reach none of it: the unit is
                # cut off, which is a reachability fact and not a generator defect
                cause = "UNIT_CANNOT_REACH_WORK"
            else:
                cause = "NO_WORK_ON_MAP"
        elif not rs:
            cause = "OTHER"
        else:
            cause = "OTHER"
        out.append({
            "situation": sit["id"], "parked_unit": uid, "cause": cause,
            "turns_observed": len(rs), "turns_empty_candidates": len(empty),
            "turns_all_wait": len(allnone), "turns_committed": len(committed),
            "turns_committed_midgame": len(midgame_commit),
            "turns_world_offered_work": work_turns,
            "turns_this_unit_could_reach_work": unit_work,
            "turns_in_window": total_turns,
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
        # LIMIT CLOSED (was: first situation only). A build that diverged only on a later
        # map would have passed the old check, and every row after it would have described a
        # different bot than the one being audited.
        ni_ok = 0
        for sit in sits:
            if not check_noninterference(sit, cfg, plain, instr):
                print(f"non-interference on {sit['id']}: DIFFERS - TABLE IS VOID")
                return 1
            ni_ok += 1
        print(f"non-interference: IDENTICAL command stream on ALL {ni_ok} situations")

        for sit in sits:
            spec = H.spec_for(sit, cfg)
            transcript, commands, err = run_capturing_stderr(
                instr, fp.make_referee(spec), int(cfg["turns"]))
            rows = parse(err)
            tr = td.build_trace(transcript, commands)
            table.extend(classify(rows, sit, tr))
    counts = collections.Counter(r["cause"] for r in table)
    print(f"\nCAUSE table — {len(table)} parked-unit observations over {len(sits)} situations")
    for r in table:
        print(f"  {r['situation']}  unit {r['parked_unit']}  {r['cause']:<18} "
              f"obs={r['turns_observed']:>3} empty={r['turns_empty_candidates']:>3} "
              f"allWAIT={r['turns_all_wait']:>3} commit(mid)={r['turns_committed_midgame']:>3} "
              f"worldWork={r['turns_world_offered_work']}/{r['turns_in_window']} "
              f"unitWork={r['turns_this_unit_could_reach_work']} "
              f"{r['branches']}")
    print(f"\ntotals: {dict(counts)}")
    out = REPO / "claude_1/hstarve1/cause-table-2026-08-16.json"
    out.write_text(json.dumps({"table": table, "totals": dict(counts)}, indent=1,
                              sort_keys=True) + "\n")
    print(f"wrote {out.relative_to(REPO)}")
    print("\nINCREMENT 3: GENERATOR_GAP now requires that THIS unit could itself reach work")
    print("(BFS from its own cell). If the player had work but this unit could reach none,")
    print("the label is UNIT_CANNOT_REACH_WORK - a reachability fact, not a generator defect.")
    print("\nINCREMENT 2: NO_WORK_ON_MAP vs GENERATOR_GAP is now decided by")
    print("fuzz_panel.work_remaining(tr,t) (:1756) - the referee WORLD state, not the")
    print("generator's output. GENERATOR_GAP = the world offered a resource action and the")
    print("generator still emitted nothing but WAIT.")
    print("\nLABEL: Packet-lite SLICE. Routing branch + candidate count for one unit per turn.")
    print("NOT Decision Packet completeness and must never be cited as such.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
