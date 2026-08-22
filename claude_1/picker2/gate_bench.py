#!/usr/bin/env python3
r"""Phase 2 gate 1 — BENCHED, one definition, four arms, with parity and coverage gates.

The card's bar: the four ruled fixtures observed **BENCHED on the unmodified subject** and then
**EMPLOYED under the candidate**, with turn coverage. `gate_employment.py` reads the command
stream, which is what reaches the referee but cannot see whether a `WAIT` had work behind it.
This runs the Phase-1 definition of *benched* on BOTH arms of BOTH bases:

    benched(t) := the selector returned `WAIT` for the anchor unit while that unit's OWN
                  candidate list — the generator's output, not an oracle's — held at least one
                  non-`WAIT` candidate.

Because the same probe builder taps both loop shapes, the word means the same thing on the base
and under P1+P2. Three gates run before any row is read, per situation and per arm:

1. **Parity** — `coverage.check_parity`: the instrumented binary's command stream must be
   byte-identical to `regression_tests.run_binary_custom` on the UNINSTRUMENTED counterpart. This
   is what licenses the diagnostic loop and the claim that the probe only prints.
2. **Coverage** — exactly one `PS2TURN` block per window turn, no gaps, no duplicates.
3. **P1 liveness** — on a candidate arm, `p1drop=true` must be observed at least once across the
   fixtures. A clause that never fires is the inert-check failure this programme has shipped
   before; here it fails the run instead of passing quietly.

Run:  python3 claude_1/picker2/gate_bench.py
"""
from __future__ import annotations

import collections, json, re, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for p in ("claude_1/t1", "claude_1/hstarve1", "claude_1/banana-restoration-r2", "claude_1/pipeline"):
    sys.path.insert(0, str(REPO / p))
import coverage as C            # noqa: E402
import fixture_harness as H     # noqa: E402

RULED = ["OSC-004", "OSC-013", "OSC-017", "OSC-034"]
OUT = HERE / "gate1-bench-2026-08-20.json"

RE_TURN = re.compile(r"^PS2TURN turn=(\d+)$")
RE_BRANCH = re.compile(r"^PS2BRANCH n_ids=(\d+) arm=(\w+)$")
RE_CAND = re.compile(r"^PS2CAND unit=(-?\d+) idx=(\d+) score=(-?[\d.]+|-?inf|NaN) target=(.*?) cmd=(.*)$")
RE_PAIR = re.compile(r"^PS2PAIR ai=(\d+) bi=(\d+) compat=(\w+) stock=(\w+) p1drop=(\w+) "
                     r"waits=(\d+) sum=(-?[\d.]+|-?inf|NaN)$")
RE_WIN = re.compile(r"^PS2WIN ai=(\d+) bi=(\d+) sum=(-?[\d.]+|-?inf|NaN)$")
RE_GREEDY = re.compile(r"^PS2GREEDY unit=(-?\d+) cmd=(.*)$")


class GateError(Exception):
    """Anything that would make a number mean something other than it says."""


def parse(err):
    turns, cur = [], None
    for line in err.splitlines():
        if not line.startswith("PS2"):
            continue
        m = RE_TURN.match(line)
        if m:
            cur = {"turn": int(m.group(1)), "arm": None, "cands": collections.defaultdict(list),
                   "unit_order": [], "pairs": [], "win": None, "nopair": False, "greedy": []}
            turns.append(cur)
            continue
        if cur is None:
            raise GateError(f"row before any PS2TURN: {line}")
        m = RE_BRANCH.match(line)
        if m:
            cur["n_ids"], cur["arm"] = int(m.group(1)), m.group(2)
            continue
        m = RE_CAND.match(line)
        if m:
            uid = int(m.group(1))
            if uid not in cur["unit_order"]:
                cur["unit_order"].append(uid)
            cur["cands"][uid].append({"idx": int(m.group(2)), "score": float(m.group(3)),
                                      "target": m.group(4), "cmd": m.group(5)})
            continue
        m = RE_PAIR.match(line)
        if m:
            cur["pairs"].append({"ai": int(m.group(1)), "bi": int(m.group(2)),
                                 "compat": m.group(3) == "true", "stock": m.group(4) == "true",
                                 "p1drop": m.group(5) == "true", "waits": int(m.group(6)),
                                 "sum": float(m.group(7))})
            continue
        m = RE_WIN.match(line)
        if m:
            cur["win"] = {"ai": int(m.group(1)), "bi": int(m.group(2)), "sum": float(m.group(3))}
            continue
        if line == "PS2NOPAIR":
            cur["nopair"] = True
            continue
        m = RE_GREEDY.match(line)
        if m:
            cur["greedy"].append({"unit": int(m.group(1)), "cmd": m.group(2)})
            continue
        raise GateError(f"unrecognised PS2 row (instrument and parser disagree): {line}")
    return turns


def check_coverage(sid, sit, turns):
    lo, hi = sit["window"]["turn_start"], sit["window"]["turn_end"]
    seen = collections.Counter(t["turn"] for t in turns)
    dupes = [t for t, n in seen.items() if n > 1]
    if dupes:
        raise GateError(f"{sid}: DUPLICATE PS2TURN blocks at {dupes[:5]} — every per-turn number "
                        f"would double-count.")
    missing = [t for t in range(lo, hi + 1) if t not in seen]
    if missing:
        raise GateError(f"{sid}: MISSING PS2TURN blocks at {missing[:5]} ({len(missing)} of "
                        f"{hi - lo + 1}) — a gap makes any rate wrong.")
    return len(seen)


def chosen_for(rec, uid):
    if rec["arm"] == "PAIR" and rec["win"] is not None:
        order = rec["unit_order"]
        idx = rec["win"]["ai"] if uid == order[0] else rec["win"]["bi"] if uid == order[1] else None
        return None if idx is None else rec["cands"][uid][idx]
    if rec["arm"] == "SINGLE":
        cs = rec["cands"].get(uid)
        return max(cs, key=lambda c: c["score"]) if cs else None
    for g in rec["greedy"]:
        if g["unit"] == uid:
            for c in rec["cands"].get(uid, []):
                if c["cmd"] == g["cmd"]:
                    return c
            return {"idx": None, "score": None, "target": None, "cmd": g["cmd"]}
    return None


def measure(sid, sit, uid, turns):
    lo, hi = sit["window"]["turn_start"], sit["window"]["turn_end"]
    byturn = {t["turn"]: t for t in turns}
    counts = collections.Counter()
    drops = 0
    for t in range(lo, hi + 1):
        rec = byturn[t]
        drops += sum(1 for p in rec["pairs"] if p["p1drop"])
        ch = chosen_for(rec, uid)
        if ch is None:
            raise GateError(f"{sid} turn {t}: no chosen row for unit {uid}")
        offered = [c for c in rec["cands"].get(uid, []) if c["cmd"] != "WAIT"]
        if ch["cmd"] == "WAIT":
            counts["BENCHED" if offered else "IDLE_NO_WORK_OFFERED"] += 1
        else:
            counts["EMPLOYED"] += 1
    return dict(counts), drops


def main():
    units = {r["situation"]: r["unit"] for r in json.loads(
        (REPO / "claude_1/hstarve1/cause-table-pool3-2026-08-17.json").read_text())["table"]}
    probes = json.loads((HERE / "probe-manifest-2026-08-20.json").read_text())
    cfg = json.loads(H.CONFIG.read_text())
    sits = {s["id"]: s for s in H.load_situations(RULED)}
    report, ok = {}, True
    for name, meta in probes.items():
        plain_src = REPO / meta["source"]
        probe_src = REPO / meta["probe"]
        rows = []
        with tempfile.TemporaryDirectory(prefix="ps2-bench-") as wd:
            wd = Path(wd)
            (wd / "p").mkdir(); (wd / "i").mkdir()
            plain = H.compile_candidate(plain_src, wd / "p")
            probe = H.compile_candidate(probe_src, wd / "i")
            drops_total = 0
            for sid in RULED:
                sit = sits[sid]
                err = C.check_parity(sit, cfg, plain, probe)      # gate: probe only prints
                turns = parse(err)
                n = check_coverage(sid, sit, turns)               # gate: no gaps, no dupes
                counts, drops = measure(sid, sit, units[sid], turns)
                drops_total += drops
                rows.append({"id": sid, "unit": units[sid],
                             "window": [sit["window"]["turn_start"], sit["window"]["turn_end"]],
                             "turn_blocks": n, "counts": counts, "p1_pairs_dropped": drops})
                print(f"  {name:11} {sid}  turns {n:4}  {counts}  p1drop={drops}")
        live = meta["arm"] == "base" or drops_total > 0
        if not live:
            ok = False
            print(f"  {name}: P1 NEVER FIRED across the four fixtures — an inert clause, "
                  f"not a fix. Gate fails rather than reporting a cure.")
        report[name] = {"arm": meta["arm"], "source": meta["source"],
                        "source_sha256": meta["source_sha256"],
                        "p1_pairs_dropped_total": drops_total, "p1_clause_live": live,
                        "situations": rows}

    # fail-first, per base: RED on the base arm, strictly fewer benched turns under the candidate
    verdicts = {}
    for base in ("cureC", "door1"):
        b = {r["id"]: r for r in report[f"{base}-base"]["situations"]}
        c = {r["id"]: r for r in report[f"{base}-p1p2"]["situations"]}
        vs = []
        for sid in RULED:
            nb = b[sid]["counts"].get("BENCHED", 0)
            nc = c[sid]["counts"].get("BENCHED", 0)
            v = ("NOT_RED_ON_THIS_BASE" if nb == 0 else
                 "REPAIRED" if nc == 0 else
                 "IMPROVED" if nc < nb else
                 "UNCHANGED" if nc == nb else "WORSE")
            vs.append({"id": sid, "base_benched": nb, "cand_benched": nc, "verdict": v})
            print(f"  {base}: {sid}  benched {nb} -> {nc}  {v}")
        verdicts[base] = vs
    OUT.write_text(json.dumps(
        {"task": "20260820-pair-selector-anti-benching", "phase": 2, "gate": "1-benched",
         "definition": "benched(t) := selector returned WAIT for the anchor unit while that "
                       "unit's own candidate list held at least one non-WAIT candidate",
         "gates": ["parity vs regression_tests.run_binary_custom on the uninstrumented arm",
                   "one PS2TURN block per window turn, no gaps or duplicates",
                   "P1 clause observed firing on each candidate arm"],
         "arms": report, "fail_first": verdicts, "instrument_live": ok}, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
