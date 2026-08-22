#!/usr/bin/env python3
r"""20260820-pair-selector-anti-benching Phase 1 — run the picker probe and answer WHY.

Charter question, exactly: for the owner-ruled cases, log per turn WHAT the joint pairing scored
and WHY the benched troll's candidates lost — hard filter vs score preference, which term
dominates, the actual arithmetic, and whether the winning pair's value is even positive.

## Method

`make_picker_probe.py` builds the probe from the pinned Phase-1 subject (cure-C `ad3bfefe…`).
This runner replays each situation from its own provenance through the shared
`fixture_harness.spec_for` / `fuzz_panel.build_skeleton` path, with two gates BEFORE any row is
read:

1. **Parity** — `coverage.check_parity`: the diagnostic loop's command stream must be
   byte-identical to `regression_tests.run_binary_custom` on the UNINSTRUMENTED subject. This is
   what licenses both the custom loop and the claim that the probe only prints.
2. **Coverage** — exactly one `PS1TURN` block per turn of the situation window, no gaps, no
   duplicates. A rate read off a stream with a hole is wrong in a way that looks fine.

## The classification, and what it is allowed to assert

A turn is BENCHED when the selector's chosen command for the situation's unit is `WAIT` while
that unit's own candidate list — the generator's output, not an oracle's opinion — contained at
least one non-WAIT candidate. Every quantity below is read from the selector's own rows:

- `HARD_FILTER` — every pair in which the benched unit takes a real candidate was rejected by
  `compatible` / `stock_compatible`. The work was never scored; it was excluded.
- `SCORE_PREFERENCE` — at least one such pair survived both predicates and lost on sum. The
  probe then names the arithmetic: the winning sum, the best benched-working sum, the margin,
  and the decomposition into the partner's term and the benched unit's term.

- `TIE_ENUMERATION_ORDER` — a pair in which the benched unit works ties the winner exactly. The
  selector's test is `score > best_score`, strictly, so on a tie the FIRST pair enumerated keeps
  the crown, and enumeration runs `ids[0]`'s list in the outer loop with `WAIT` at index 0. The
  benching is then decided by iteration order, not by value. (This class was found by the
  `margin <= 0` guard below firing on OSC-034 and OSC-004 — the first draft asserted it was
  impossible. It is not: strict `>` makes ties reachable.)

A NEGATIVE margin is still impossible by construction, and `IMPOSSIBLE_MARGIN` fails the run
rather than reporting a mechanism.

Run:
    python3 claude_1/picker1/probe.py                 # the four owner-ruled cases
    python3 claude_1/picker1/probe.py --only OSC-017
"""
from __future__ import annotations

import argparse, collections, json, re, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "t1"))
sys.path.insert(0, str(REPO / "claude_1" / "hstarve1"))
sys.path.insert(0, str(REPO / "claude_1" / "banana-restoration-r2"))
sys.path.insert(0, str(REPO / "claude_1" / "pipeline"))
import coverage as C            # noqa: E402
import fixture_harness as H     # noqa: E402
import fuzz_panel as fp         # noqa: E402

PROBE = HERE / "probe-picker1.rs"
SUBJECT = REPO / "cgauto/submissions/submitted-sub41153619-cure-c-quiet.rs"
OWNER_RULED = ["OSC-004", "OSC-013", "OSC-017", "OSC-034"]
OUT = HERE / "mechanism-2026-08-20.json"

RE_TURN = re.compile(r"^PS1TURN turn=(\d+)$")
RE_BRANCH = re.compile(r"^PS1BRANCH n_ids=(\d+) arm=(\w+)$")
RE_CAND = re.compile(r"^PS1CAND unit=(-?\d+) idx=(\d+) score=(-?[\d.]+|-?inf|NaN) target=(.*?) cmd=(.*)$")
RE_PAIR = re.compile(r"^PS1PAIR ai=(\d+) bi=(\d+) compat=(\w+) stock=(\w+) sum=(-?[\d.]+|-?inf|NaN)$")
RE_WIN = re.compile(r"^PS1WIN ai=(\d+) bi=(\d+) sum=(-?[\d.]+|-?inf|NaN)$")
RE_GREEDY = re.compile(r"^PS1GREEDY unit=(-?\d+) cmd=(.*)$")


class ProbeError(Exception):
    """Anything that would make a number mean something other than it says."""


def parse(err):
    """stderr -> one record per turn. Unrecognised PS1 rows are a hard error, never ignored."""
    turns, cur = [], None
    for line in err.splitlines():
        if not line.startswith("PS1"):
            continue
        m = RE_TURN.match(line)
        if m:
            cur = {"turn": int(m.group(1)), "arm": None, "cands": collections.defaultdict(list),
                   "unit_order": [], "pairs": [], "win": None, "nopair": False, "greedy": []}
            turns.append(cur)
            continue
        if cur is None:
            raise ProbeError(f"row before any PS1TURN: {line}")
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
                                 "sum": float(m.group(5))})
            continue
        m = RE_WIN.match(line)
        if m:
            cur["win"] = {"ai": int(m.group(1)), "bi": int(m.group(2)), "sum": float(m.group(3))}
            continue
        if line == "PS1NOPAIR":
            cur["nopair"] = True
            continue
        m = RE_GREEDY.match(line)
        if m:
            cur["greedy"].append({"unit": int(m.group(1)), "cmd": m.group(2)})
            continue
        raise ProbeError(f"unrecognised PS1 row (instrument and parser disagree): {line}")
    return turns


def check_coverage(sit, turns):
    lo, hi = sit["window"]["turn_start"], sit["window"]["turn_end"]
    seen = collections.Counter(t["turn"] for t in turns)
    dupes = [t for t, n in seen.items() if n > 1]
    if dupes:
        raise ProbeError(f"{sit['id']}: DUPLICATE PS1TURN blocks at {dupes[:5]} — select() ran "
                         f"more than once per turn and every per-turn number would double-count.")
    missing = [t for t in range(lo, hi + 1) if t not in seen]
    if missing:
        raise ProbeError(f"{sit['id']}: MISSING PS1TURN blocks at {missing[:5]} "
                         f"({len(missing)} of {hi - lo + 1}) — a gap makes any rate wrong.")
    return len(seen)


def chosen_for(rec, uid):
    """The command the selector actually returned for `uid`, from the selector's own rows."""
    if rec["arm"] == "PAIR" and rec["win"] is not None:
        a, b = rec["unit_order"][0], rec["unit_order"][1]
        idx = rec["win"]["ai"] if uid == a else rec["win"]["bi"] if uid == b else None
        if idx is None:
            return None
        return rec["cands"][uid][idx]
    if rec["arm"] == "SINGLE":
        best = max(rec["cands"][uid], key=lambda c: c["score"]) if rec["cands"].get(uid) else None
        return best
    for g in rec["greedy"]:                        # GREEDY arm, or PAIR that found no pair
        if g["unit"] == uid:
            for c in rec["cands"].get(uid, []):
                if c["cmd"] == g["cmd"]:
                    return c
            return {"idx": None, "score": None, "target": None, "cmd": g["cmd"]}
    return None


def classify(rec, uid):
    """WHY the benched unit's real candidates lost, on a turn where it was benched."""
    order = rec["unit_order"]
    if rec["arm"] != "PAIR" or rec["win"] is None or len(order) != 2:
        return {"class": "NOT_PAIR_ARM", "arm": rec["arm"]}
    a_id, b_id = order
    mine_first = uid == a_id
    real = {c["idx"] for c in rec["cands"][uid] if c["cmd"] != "WAIT"}
    survived, filtered = [], []
    for p in rec["pairs"]:
        mine = p["ai"] if mine_first else p["bi"]
        if mine not in real:
            continue
        (survived if (p["compat"] and p["stock"]) else filtered).append(p)
    win_sum = rec["win"]["sum"]
    if not survived:
        reasons = collections.Counter(
            "INCOMPATIBLE_TARGET" if not p["compat"] else "STOCK" for p in filtered)
        return {"class": "HARD_FILTER", "pairs_with_my_work": len(filtered),
                "rejections": dict(reasons), "winning_sum": win_sum}
    best = max(survived, key=lambda p: p["sum"])
    # decomposition, from the selector's own per-candidate scores
    my_i = best["ai"] if mine_first else best["bi"]
    par_i = best["bi"] if mine_first else best["ai"]
    par_id = b_id if mine_first else a_id
    win_my_i = rec["win"]["ai"] if mine_first else rec["win"]["bi"]
    win_par_i = rec["win"]["bi"] if mine_first else rec["win"]["ai"]
    my_gain = rec["cands"][uid][my_i]["score"] - rec["cands"][uid][win_my_i]["score"]
    par_loss = rec["cands"][par_id][win_par_i]["score"] - rec["cands"][par_id][par_i]["score"]
    margin = win_sum - best["sum"]
    cls = ("SCORE_PREFERENCE" if margin > 0 else
           "TIE_ENUMERATION_ORDER" if margin == 0 else "IMPOSSIBLE_MARGIN")
    # Whichever predicate rejects (my best real work, the partner's WINNING candidate) is the
    # clause that made the benching necessary at all: with the partner's choice held fixed, a
    # positive-scored candidate of mine that survived both predicates would have beaten WAIT on
    # the sum, so the selector could not have benched me. Naming the clause is the point.
    blocker = None
    for p in rec["pairs"]:
        mine = p["ai"] if mine_first else p["bi"]
        par = p["bi"] if mine_first else p["ai"]
        if mine == my_i and par == win_par_i:
            blocker = ("NONE" if (p["compat"] and p["stock"])
                       else "INCOMPATIBLE_TARGET" if not p["compat"] else "STOCK")
    return {"class": cls, "blocker_at_winner": blocker,
            "winning_sum": win_sum, "best_working_sum": best["sum"], "margin": margin,
            "my_term_gain": my_gain, "partner_term_loss": par_loss,
            "dominating_term": "PARTNER" if par_loss > my_gain else "MINE",
            "my_best_work_cmd": rec["cands"][uid][my_i]["cmd"],
            "my_best_work_score": rec["cands"][uid][my_i]["score"],
            "partner_kept_cmd": rec["cands"][par_id][win_par_i]["cmd"],
            "partner_kept_score": rec["cands"][par_id][win_par_i]["score"],
            "partner_alt_cmd": rec["cands"][par_id][par_i]["cmd"],
            "partner_alt_score": rec["cands"][par_id][par_i]["score"]}


def analyse(sit, turns):
    uid = None
    lo, hi = sit["window"]["turn_start"], sit["window"]["turn_end"]
    byturn = {t["turn"]: t for t in turns}
    uid = SIT_UNIT[sit["id"]]
    rows, classes = [], collections.Counter()
    win_nonpositive = 0
    for t in range(lo, hi + 1):
        rec = byturn[t]
        ch = chosen_for(rec, uid)
        offered = [c for c in rec["cands"].get(uid, []) if c["cmd"] != "WAIT"]
        if ch is None:
            raise ProbeError(f"{sit['id']} turn {t}: no chosen row for unit {uid}")
        benched = ch["cmd"] == "WAIT"
        if rec["arm"] == "PAIR" and rec["win"] is not None and rec["win"]["sum"] <= 0:
            win_nonpositive += 1
        if not (benched and offered):
            classes["NOT_BENCHED" if not benched else "BENCHED_NO_WORK_OFFERED"] += 1
            continue
        c = classify(rec, uid)
        classes[c["class"]] += 1
        rows.append({"turn": t, "n_offered": len(offered),
                     "best_offered_score": max(o["score"] for o in offered), **c})
    return {"id": sit["id"], "unit": uid, "window": [lo, hi], "kind": sit["kind"],
            "turns": hi - lo + 1, "classes": dict(classes),
            "winning_pair_sum_nonpositive_turns": win_nonpositive, "benched_turns": rows}


SIT_UNIT = {}       # filled from the pool-3 cause table's anchor unit


def load_units():
    tbl = json.loads((REPO / "claude_1/hstarve1/cause-table-pool3-2026-08-17.json").read_text())
    for r in tbl["table"]:
        SIT_UNIT[r["situation"]] = r["unit"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=",".join(OWNER_RULED))
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    load_units()
    cfg = json.loads(H.CONFIG.read_text())
    sits = H.load_situations(args.only.split(","))
    results = []
    with tempfile.TemporaryDirectory(prefix="ps1-") as wd:
        di, dp = Path(wd) / "i", Path(wd) / "p"
        di.mkdir(); dp.mkdir()
        probe = H.compile_candidate(PROBE, di)
        plain = H.compile_candidate(SUBJECT, dp)
        for sit in sits:
            err = C.check_parity(sit, cfg, plain, probe)     # gate 1 — probe only prints
            turns = parse(err)
            n = check_coverage(sit, turns)                   # gate 2 — no gaps, no dupes
            r = analyse(sit, turns)
            r["turn_blocks_observed"] = n
            results.append(r)
            print(f"  {r['id']}  unit {r['unit']}  turns {r['window'][0]}-{r['window'][1]}  "
                  f"{r['classes']}")
    bad = [r for r in results if r["classes"].get("IMPOSSIBLE_MARGIN")]
    if bad:
        raise ProbeError("IMPOSSIBLE_MARGIN observed — impossible if the instrument is faithful; "
                         "no mechanism is reported from this run: " + str([r['id'] for r in bad]))
    out_path = Path(args.out)
    out_path.write_text(json.dumps({
        "task": "20260820-pair-selector-anti-benching",
        "phase": 1,
        "subject": "cgauto/submissions/submitted-sub41153619-cure-c-quiet.rs",
        "subject_sha256": "ad3bfefe4b2326f4f6b4a270dc862ea19a0e319a1cddfde44b96cc6f6d35a5d1",
        "probe": "claude_1/picker1/probe-picker1.rs",
        "gates": ["parity vs regression_tests.run_binary_custom on the uninstrumented subject",
                  "one PS1TURN block per window turn, no gaps or duplicates"],
        "situations": results}, indent=2) + "\n")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
