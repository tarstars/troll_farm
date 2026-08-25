#!/usr/bin/env python3
r"""Phase 3 step 2 — the census: which generator route returns the anchor's length-1 list, and why.

Step 1 established the list is exactly the seeded `WAIT`. This names the return path that produced
it, per turn, on both bases, using `make_route_probe.py`'s generator tap.

Three gates run before any route is counted, and each one fails the run rather than degrading it:

1. **Parity** — the instrumented binary's command stream must be byte-identical to the
   uninstrumented candidate's (`coverage.check_parity`). The probe only prints.
2. **Coverage** — the anchor must have exactly one `PS3FINAL` row on every turn of the window. A
   missing or duplicated row makes every rate below wrong.
3. **Cross-probe agreement** — `PS3FINAL n` (the generator's output, read at `by_id.insert`) must
   equal the number of `PS2CAND` rows the SELECTOR probe logged for the same unit and turn. Two
   independent taps, one list. If they disagree, one of them is not measuring what it says and no
   route is reported.

Reported per fixture: the route histogram over the idle turns (list length 1) and over the
employed turns, plus the generator's own predicate values on the idle turns — `carried`,
`free_cap`, `safe_regen`, `idle_regen`, and the sub-generator sizes each route prints. That is the
"why" the deferral card asked for, stated as the source's own control flow.

Scope discipline: this is a measurement. It does not propose, and does not license, any extension
of P1 or P2.

Run:  python3 claude_1/picker2/route_census.py
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
sys.path.insert(0, str(HERE))
import gate_bench as GB         # noqa: E402

RULED = ["OSC-004", "OSC-013", "OSC-017", "OSC-034"]
OUT = HERE / "route-census-2026-08-20.json"

RE_FINAL = re.compile(r"^PS3FINAL unit=(-?\d+) turn=(\d+) n=(\d+) endgame=(\w+) early=(\w+) "
                      r"committed=(\w+) train_now=(\w+)$")
RE_MAIN = re.compile(r"^PS3MAIN unit=(-?\d+) turn=(\d+) carried=(-?\d+) free_cap=(-?\d+) "
                     r"safe_regen=(\w+) idle_regen=(\w+)$")
RE_ROUTE = re.compile(r"^PS3ROUTE unit=(-?\d+) turn=(\d+) fn=(\w+) route=(\w+)(.*)$")
RE_DISCARD = re.compile(r"^PS3DISCARD unit=(-?\d+) turn=(\d+) verb=(\S+) target=(.*?) "
                        r"score=(-?[\d.]+|-?inf|NaN)$")


class GateError(Exception):
    """Anything that would make a route count mean something other than it says."""


def parse(err, uid):
    """Per-turn records for ONE unit. Rows are grouped by the turn each row carries itself."""
    turns = collections.defaultdict(lambda: {"final": None, "main": None, "routes": [],
                                             "discarded": []})
    for line in err.splitlines():
        if not line.startswith("PS3"):
            continue
        m = RE_FINAL.match(line)
        if m:
            if int(m.group(1)) != uid:
                continue
            t = int(m.group(2))
            if turns[t]["final"] is not None:
                raise GateError(f"turn {t}: duplicate PS3FINAL for unit {uid}")
            turns[t]["final"] = {"n": int(m.group(3)), "endgame": m.group(4) == "true",
                                 "early": m.group(5) == "true", "committed": m.group(6) == "true",
                                 "train_now": m.group(7) == "true"}
            continue
        m = RE_MAIN.match(line)
        if m:
            if int(m.group(1)) != uid:
                continue
            turns[int(m.group(2))]["main"] = {
                "carried": int(m.group(3)), "free_cap": int(m.group(4)),
                "safe_regen": m.group(5) == "true", "idle_regen": m.group(6) == "true"}
            continue
        m = RE_DISCARD.match(line)
        if m:
            if int(m.group(1)) != uid:
                continue
            turns[int(m.group(2))]["discarded"].append(
                {"verb": m.group(3), "target": m.group(4), "score": float(m.group(5))})
            continue
        m = RE_ROUTE.match(line)
        if m:
            if int(m.group(1)) != uid:
                continue
            extra = dict(kv.split("=", 1) for kv in m.group(5).split() if "=" in kv)
            turns[int(m.group(2))]["routes"].append({"fn": m.group(3), "route": m.group(4), **extra})
            continue
        raise GateError(f"unrecognised PS3 row (instrument and parser disagree): {line}")
    return turns


def census(sid, sit, uid, rt, sel_turns):
    lo, hi = sit["window"]["turn_start"], sit["window"]["turn_end"]
    sel = {t["turn"]: t for t in sel_turns}
    idle_routes, employed_routes = collections.Counter(), collections.Counter()
    preds = collections.Counter()
    detail = collections.Counter()
    discarded = collections.Counter()
    n_idle = 0
    for t in range(lo, hi + 1):
        rec = rt.get(t)
        if rec is None or rec["final"] is None:
            raise GateError(f"{sid} turn {t}: no PS3FINAL row for unit {uid} — coverage hole.")
        # cross-probe: the selector's own view of the same list
        seen = len(sel[t]["cands"].get(uid, []))
        if seen != rec["final"]["n"]:
            raise GateError(
                f"{sid} turn {t}: generator emitted n={rec['final']['n']} but the selector probe "
                f"logged {seen} PS2CAND rows for unit {uid}. The two taps disagree; no route may "
                f"be reported.")
        if len(rec["routes"]) != 1:
            raise GateError(f"{sid} turn {t}: {len(rec['routes'])} route rows for unit {uid}, "
                            f"need exactly 1 — a unit takes one return path per turn.")
        r = rec["routes"][0]
        tag = f"{r['fn']}:{r['route']}"
        if rec["final"]["n"] == 1:
            n_idle += 1
            idle_routes[tag] += 1
            m = rec["main"]
            if m:
                preds[f"carried={m['carried']} free_cap={m['free_cap']} "
                      f"safe_regen={m['safe_regen']} idle_regen={m['idle_regen']}"] += 1
            detail[" ".join(f"{k}={v}" for k, v in sorted(r.items()) if k not in ("fn", "route"))] += 1
            for d in rec["discarded"]:
                discarded[f"{d['verb']} target={d['target']} score={d['score']}"] += 1
        else:
            employed_routes[tag] += 1
    return {"id": sid, "unit": uid, "window": [lo, hi], "turns": hi - lo + 1,
            "idle_turns": n_idle, "idle_routes": dict(idle_routes),
            "employed_routes": dict(employed_routes),
            "idle_predicates": dict(preds), "idle_route_detail": dict(detail),
            "idle_discarded_candidates": dict(discarded)}


def main():
    units = {r["situation"]: r["unit"] for r in json.loads(
        (REPO / "claude_1/hstarve1/cause-table-pool3-2026-08-17.json").read_text())["table"]}
    rman = json.loads((HERE / "route-probe-manifest-2026-08-20.json").read_text())
    sman = json.loads((HERE / "probe-manifest-2026-08-20.json").read_text())
    cfg = json.loads(H.CONFIG.read_text())
    sits = {s["id"]: s for s in H.load_situations(RULED)}
    report = {}
    for name, meta in rman.items():
        rows = []
        with tempfile.TemporaryDirectory(prefix="ps3-route-") as wd:
            wd = Path(wd)
            for d in ("p", "r", "s"):
                (wd / d).mkdir()
            plain = H.compile_candidate(REPO / meta["source"], wd / "p")
            rprobe = H.compile_candidate(REPO / meta["probe"], wd / "r")
            sprobe = H.compile_candidate(REPO / sman[name]["probe"], wd / "s")
            for sid in RULED:
                sit, uid = sits[sid], units[sid]
                rerr = C.check_parity(sit, cfg, plain, rprobe)   # gate: route probe only prints
                serr = C.check_parity(sit, cfg, plain, sprobe)   # gate: selector probe only prints
                rt = parse(rerr, uid)
                sel_turns = GB.parse(serr)
                GB.check_coverage(sid, sit, sel_turns)
                row = census(sid, sit, uid, rt, sel_turns)
                rows.append(row)
                print(f"  {name:11} {sid}  idle {row['idle_turns']:3}/{row['turns']:3}  "
                      f"idle_routes={row['idle_routes']}  employed={row['employed_routes']}")
                for k, v in row["idle_predicates"].items():
                    print(f"      preds  {k}  x{v}")
                for k, v in row["idle_route_detail"].items():
                    print(f"      detail {k}  x{v}")
                for k, v in row["idle_discarded_candidates"].items():
                    print(f"      DISCARDED {k}  x{v}")
        report[name] = {"source": meta["source"], "source_sha256": meta["source_sha256"],
                        "situations": rows}
    OUT.write_text(json.dumps(
        {"task": "20260820-pair-selector-anti-benching", "phase": 3, "step": "2-generator-route",
         "question": "which return path of main_candidates/endgame_candidates hands back the "
                     "seeded WAIT alone, and what did the generator see when it did?",
         "gates": ["parity vs the uninstrumented candidate, for BOTH probes",
                   "exactly one PS3FINAL row per window turn for the anchor",
                   "PS3FINAL n == the selector probe's PS2CAND row count for the same unit/turn",
                   "exactly one route row per unit per turn"],
         "scope": "measurement only; licenses no extension of P1 or P2",
         "arms": report}, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
