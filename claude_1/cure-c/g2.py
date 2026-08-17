#!/usr/bin/env python3
"""Cure C — GATE G2. Per-game de-novo decomposition of the 240-game panel against the matched floor.

Task `20260817-cure-c-implementation` §3.2: *"the 240-game panel vs the matched floor — ZERO
de-novo D-1 AND ZERO de-novo P4 (both arms), command errors 0, with the per-game decomposition
published."*

Reads the two panel JSONs produced by `claude_1/pipeline/fuzz_panel.py`:

  curec-matched-floor-config.json    -> g2-matched-floor.json   (resident judged against ITSELF)
  curec-acceptance-panel-config.json -> g2-candidate.json       (cure-C candidate vs resident)

## Where P4 actually lives, and the inert comparison that nearly shipped

A game row has no `p4_violations` field. P4 appears inside `violations` as
`{"property": "P4", "detail": {...}}` with **no `detector` key**, while D-1..D-9 appear as
`{"property": "P1", "detector": "D-1", "count": n}`.

My first comparison read `g.get("p4_violations", g.get("p4", 0))`. Both keys are absent, so it
compared `0 > 0` on all 240 rows and reported **zero de-novo P4** — a green on the exact gate that
matters, produced by a field that does not exist. The true figure is not zero. This is the same
disease as every other inert check in this programme, and it was caught by asking what the keys
actually are rather than by trusting a plausible number.

So this module keys violations by `detector or property`, and **refuses to report unless the
comparator is observed firing in BOTH directions** — a de-novo comparison that can only ever
return zero is not evidence of zero.
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CANDIDATE_JSON = HERE / "g2-candidate.json"
FLOOR_JSON = HERE / "g2-matched-floor.json"
GATE_DETECTORS = ("D-1", "P4")     # the charter's absolute pair


class G2Error(Exception):
    """Fail-closed."""


def key(game):
    return (game["map_id"], game["seat"])


def violation_counts(game):
    """-> Counter keyed by `detector` when present, else `property`.

    D-1..D-9 carry `detector`; P2/P3/P4 carry only `property`. Keying on one field alone silently
    drops half the gate.
    """
    out = collections.Counter()
    for v in game.get("violations") or []:
        name = v.get("detector") or v.get("property")
        if name is None:
            raise G2Error(f"violation with neither detector nor property: {v!r}")
        out[name] += v.get("count", 1)
    return out


def main():
    cand = json.loads(CANDIDATE_JSON.read_text())
    floor = json.loads(FLOOR_JSON.read_text())

    if floor["run_identity"] != "floor" or cand["run_identity"] != "candidate":
        raise G2Error(f"run identities wrong: floor={floor['run_identity']!r} "
                      f"candidate={cand['run_identity']!r}")
    for field in ("corpus_version", "instrument_version", "engine_sha256", "referee_sha256"):
        if cand.get(field) != floor.get(field):
            raise G2Error(f"{field} differs between the arms — the two runs are not comparable")

    C = {key(g): violation_counts(g) for g in cand["games"]}
    F = {key(g): violation_counts(g) for g in floor["games"]}
    if set(C) != set(F):
        raise G2Error("the two arms cover different games")

    denovo = collections.defaultdict(list)
    removed = collections.Counter()
    for k in sorted(C):
        for name, n in C[k].items():
            base = F[k].get(name, 0)
            if n > base:
                denovo[name].append({"map_id": k[0], "seat": k[1], "floor": base, "candidate": n})
        for name, base in F[k].items():
            if C[k].get(name, 0) < base:
                removed[name] += 1

    # The comparator must be observed firing in BOTH directions before its zeros mean anything.
    if not removed:
        raise G2Error("the comparator found nothing removed anywhere — it has only ever returned "
                      "one answer, so its de-novo zeros are not evidence")

    cand_err = sum(g.get("command_error_total", 0) for g in cand["games"])
    floor_err = sum(g.get("command_error_total", 0) for g in floor["games"])

    print(f"games compared: {len(C)}   corpus {cand['corpus_version']}")
    print(f"\nreverse-direction control (floor > candidate — proves the comparator fires):")
    for name, n in sorted(removed.items(), key=lambda kv: -kv[1]):
        print(f"    {name:<5} removed in {n} games")

    print("\n=== DE-NOVO (candidate > floor), per game ===")
    if not denovo:
        print("    none")
    for name in sorted(denovo):
        rows = denovo[name]
        mark = "  <== GATE" if name in GATE_DETECTORS else ""
        print(f"    {name:<5} {len(rows):>2} games{mark}")
        for r in rows[:6]:
            print(f"          {r['map_id']} seat {r['seat']}: floor {r['floor']} -> "
                  f"candidate {r['candidate']}")

    d1 = len(denovo.get("D-1", []))
    p4 = len(denovo.get("P4", []))
    print(f"\ncommand errors — floor {floor_err}, candidate {cand_err}")
    print(f"blocking games — floor {floor['stats']['blocking_games']}, "
          f"candidate {cand['stats']['blocking_games']}")
    tot = lambda D: sum(sum(v.values()) for v in D.values())
    print(f"violation instances — floor {tot(F)}, candidate {tot(C)}")

    passed = d1 == 0 and p4 == 0 and cand_err == 0 and floor_err == 0
    verdict = "PASS" if passed else "FAIL"
    print(f"\nG2 gate (ZERO de-novo D-1 AND ZERO de-novo P4, command errors 0): "
          f"D-1={d1}  P4={p4}  errors={cand_err}  ->  {verdict}")
    if not passed:
        print("\nThe aggregate is far better than the floor and that is NOT the gate. The owner's\n"
              "RAW/ABSOLUTE ruling blocks on any de-novo episode, inherited or not. Reporting the\n"
              "aggregate as if it satisfied the gate is the move this gate exists to prevent.")

    out = HERE / "g2-results-2026-08-17.json"
    out.write_text(json.dumps({
        "gate": "G2",
        "task": "20260817-cure-c-implementation",
        "corpus_version": cand["corpus_version"],
        "instrument_version": cand["instrument_version"],
        "games": len(C),
        "denovo": {k: v for k, v in sorted(denovo.items())},
        "denovo_d1_games": d1,
        "denovo_p4_games": p4,
        "removed_by_detector": dict(removed),
        "command_errors": {"floor": floor_err, "candidate": cand_err},
        "blocking_games": {"floor": floor["stats"]["blocking_games"],
                           "candidate": cand["stats"]["blocking_games"]},
        "violation_instances": {"floor": tot(F), "candidate": tot(C)},
        "verdict": verdict,
    }, indent=1, sort_keys=True) + "\n")
    print(f"wrote {out.relative_to(HERE.parent.parent)}")
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except G2Error as e:
        print(f"G2: FAIL — {e}")
        sys.exit(2)
