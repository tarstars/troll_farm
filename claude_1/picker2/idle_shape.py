#!/usr/bin/env python3
r"""Phase 3 step 1 — WHAT the anchor unit's candidate list actually holds on the idle turns.

`gate_bench.py` reports `IDLE_NO_WORK_OFFERED` on 170 of OSC-013's 187 window turns under P1+P2,
and the Phase-2 handoff called that "the candidate list is empty". Reading the generator shows
that phrasing cannot be right: `main_candidates` and `endgame_candidates` both open with
`let mut out=vec![MoisanBot::wait()]`, so the list is NEVER empty — the question is whether it
holds ANYTHING BESIDES that seeded `WAIT`.

This measures the distinction rather than assuming it, on the rows the Phase-2 probe already
emits. No new instrument, no new definition: the same `PS2CAND` stream, the same parity gate, the
same coverage gate as `gate_bench.py`. For every window turn it records the anchor's list length,
its distinct commands and its distinct targets, and buckets the turn:

    ONLY_SEEDED_WAIT   list is exactly one `WAIT` with `Target::None` — the generator produced
                       nothing at all and the seed is the whole list
    WAIT_PLUS_WAIT     more than one entry, all of them `WAIT` — some branch appended a second
                       seed (the `idle_regeneration` fallback path does exactly this)
    HAS_NON_WAIT       at least one real command — NOT an idle turn by the gate's definition;
                       its presence here would mean the gate and this reader disagree
    EMPLOYED           the selector returned a non-`WAIT` command for the anchor this turn

The `HAS_NON_WAIT`-on-an-idle-turn bucket is the cross-check that makes the other counts mean
something: it must be 0, because `gate_bench.measure` calls a turn idle exactly when that list is
free of non-`WAIT` entries. If it is ever non-zero the two readers disagree and the run fails
rather than reporting a shape.

This answers "what", not "why". The generator branch that produced each list is step 2 and needs
its own probe; nothing here licenses extending P1/P2.

Run:  python3 claude_1/picker2/idle_shape.py
"""
from __future__ import annotations

import collections, json, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for p in ("claude_1/t1", "claude_1/hstarve1", "claude_1/banana-restoration-r2", "claude_1/pipeline"):
    sys.path.insert(0, str(REPO / p))
import coverage as C            # noqa: E402
import fixture_harness as H     # noqa: E402
sys.path.insert(0, str(HERE))
import gate_bench as GB         # noqa: E402   one parser, one chooser, one definition

RULED = ["OSC-004", "OSC-013", "OSC-017", "OSC-034"]
OUT = HERE / "idle-shape-2026-08-20.json"


class GateError(Exception):
    """A disagreement that would make a bucket count mean something other than it says."""


def shape(sid, sit, uid, turns):
    lo, hi = sit["window"]["turn_start"], sit["window"]["turn_end"]
    byturn = {t["turn"]: t for t in turns}
    counts = collections.Counter()
    lens = collections.Counter()
    cmdsets = collections.Counter()
    targetsets = collections.Counter()
    idle_turns = []
    for t in range(lo, hi + 1):
        rec = byturn[t]
        cands = rec["cands"].get(uid, [])
        ch = GB.chosen_for(rec, uid)
        if ch is None:
            raise GateError(f"{sid} turn {t}: no chosen row for unit {uid}")
        nonwait = [c for c in cands if c["cmd"] != "WAIT"]
        if ch["cmd"] != "WAIT":
            counts["EMPLOYED"] += 1
            continue
        # idle by gate_bench's definition iff no non-WAIT candidate was offered
        if nonwait:
            counts["HAS_NON_WAIT"] += 1
            continue
        idle_turns.append(t)
        lens[len(cands)] += 1
        cmdsets[" | ".join(sorted({c["cmd"] for c in cands}))] += 1
        targetsets[" | ".join(sorted({c["target"] for c in cands}))] += 1
        counts["ONLY_SEEDED_WAIT" if len(cands) == 1 else "WAIT_PLUS_WAIT"] += 1
    return {"counts": dict(counts), "list_lengths": {str(k): v for k, v in sorted(lens.items())},
            "distinct_commands": dict(cmdsets), "distinct_targets": dict(targetsets),
            "idle_turn_span": [idle_turns[0], idle_turns[-1]] if idle_turns else None,
            "idle_turns": len(idle_turns)}


def main():
    units = {r["situation"]: r["unit"] for r in json.loads(
        (REPO / "claude_1/hstarve1/cause-table-pool3-2026-08-17.json").read_text())["table"]}
    probes = json.loads((HERE / "probe-manifest-2026-08-20.json").read_text())
    cfg = json.loads(H.CONFIG.read_text())
    sits = {s["id"]: s for s in H.load_situations(RULED)}
    report, ok = {}, True
    for name in ("cureC-p1p2", "door1-p1p2"):
        meta = probes[name]
        rows = []
        with tempfile.TemporaryDirectory(prefix="ps3-shape-") as wd:
            wd = Path(wd)
            (wd / "p").mkdir(); (wd / "i").mkdir()
            plain = H.compile_candidate(REPO / meta["source"], wd / "p")
            probe = H.compile_candidate(REPO / meta["probe"], wd / "i")
            for sid in RULED:
                sit = sits[sid]
                err = C.check_parity(sit, cfg, plain, probe)   # gate: probe only prints
                turns = GB.parse(err)
                GB.check_coverage(sid, sit, turns)             # gate: no gaps, no duplicates
                s = shape(sid, sit, units[sid], turns)
                if s["counts"].get("HAS_NON_WAIT"):
                    ok = False
                    print(f"  {name} {sid}: READER DISAGREEMENT — {s['counts']['HAS_NON_WAIT']} "
                          f"turns the selector benched with non-WAIT work offered. gate_bench "
                          f"would have called these BENCHED, not idle.")
                s["id"], s["unit"] = sid, units[sid]
                rows.append(s)
                print(f"  {name:11} {sid}  {s['counts']}")
                for k, v in s["distinct_commands"].items():
                    print(f"      cmds[{k}] x{v}   lens={s['list_lengths']}")
        report[name] = {"source": meta["source"], "source_sha256": meta["source_sha256"],
                        "situations": rows}
    OUT.write_text(json.dumps(
        {"task": "20260820-pair-selector-anti-benching", "phase": 3, "step": "1-idle-list-shape",
         "question": "on the idle turns, is the anchor's candidate list empty, or does it hold "
                     "only the WAIT that main_candidates/endgame_candidates seed it with?",
         "cross_check": "HAS_NON_WAIT must be 0 on every fixture or the run fails",
         "answers": "what the list holds; NOT which generator branch produced it",
         "arms": report, "readers_agree": ok}, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
