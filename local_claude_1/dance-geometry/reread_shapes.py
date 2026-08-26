#!/usr/bin/env python3
"""Re-read of the two instrumented dance reads by the teammate's position when the dance began.

Deterministic; reads two published fact-row files and writes one JSON plus a text summary.

Inputs (pinned in `local_claude_1/dance-geometry/re-read-2026-08-25.md`):
  --facts80  claude_1/dance1/results/dance-facts-instrument-2026-08-24.json   (agent/claude_1@4c92432f)
             80 D-1 episodes, 469 games, NARRATE v2/v3 instruments (2026-08-23 read)
  --g2       claude_1/cure1/results/g2-grade.json                             (agent/claude_1@22d6b2bb)
             25 D-1 episodes, 160 games, NARRATE v4 instrument (2026-08-25 read), per_game[].episodes[]

Shape of an episode (the peer = the one teammate alive at entry; every episode has exactly one):
  one-cell  : the accepted classification's `mech == BLOCKER_WORKING` — the peer stood on ONE cell,
              orthogonally adjacent to the dance cells, for the whole window, working (r3 test)
  adjacent  : not one-cell, but the peer's cell at entry is orthogonally adjacent to cell_a or cell_b
              (the peer then visited >= 2 cells inside the window)
  nobody    : neither — nobody of ours next to the dance when it began

`ahead` (straight-line test, older read has no resolver letters): the peer stands next to a dance
cell c AND manhattan(peer, target) < manhattan(c, target) for at least one stated target of the
window (targets parsed from `chosen_sequence`; `NONE` ignored). On the v4 read the resolver's own
letters inside the window are counted from `v4_branch_sequence`:
  P forward step · L sideways step no farther · H hold · R backward detour (the landing cell is
  reserved by a STANDING own unit or granted to an earlier mover, and every free neighbour is
  strictly farther) · W forced wait · N no MOVE this turn.

Caveat carried by every count: D-1 off replays is an UPPER BOUND (reconstructed plant clocks invent
dances); the two reads are different days and opponent fields with no randomisation.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from math import comb

CELL_RE = re.compile(r"\((-?\d+),(-?\d+)\)")
SHAPES = ("one-cell", "adjacent", "nobody")


def cell(text):
    m = CELL_RE.search(text or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def load_rows(path, kind):
    data = json.load(open(path))
    if kind == "facts80":
        rows = data if isinstance(data, list) else data["episodes"]
        return [dict(r, _read="older") for r in rows]
    rows = []
    for g in data["per_game"]:
        for e in g["episodes"]:
            rows.append(dict(e, _read="v4", _game=g["game"]))
    return rows


def describe(e):
    w = e["f2_window"]
    a, b = tuple(w["cell_a"]), tuple(w["cell_b"])
    peer = (e.get("f3_peers") or [None])[0]
    tele = e.get("f4_telemetry") or {}
    chosen = [c for c in tele.get("chosen_sequence", []) if c and c != "NONE"]
    targets = [t for t in (cell(c) for c in dict.fromkeys(chosen)) if t]
    shape, ahead, adj = "nobody", None, False
    if peer:
        pc = tuple(peer["cell_at_entry"])
        near = [c for c in (a, b) if manhattan(pc, c) == 1]
        adj = bool(near)
        if e["mech"] == "BLOCKER_WORKING":
            shape = "one-cell"
        elif adj:
            shape = "adjacent"
        if adj and targets:
            ahead = any(manhattan(pc, t) < manhattan(c, t) for c in near for t in targets)
    letters = Counter("".join(e.get("v4_branch_sequence") or []))
    return {
        "read": e["_read"], "game": e.get("game", e.get("_game")), "seat": e.get("seat"),
        "unit": e["f1_dancer"]["unit"], "speed": e["f1_dancer"]["speed"], "class": e["class"],
        "mech": e["mech"], "shape": shape, "peer_adjacent_at_entry": adj, "peer_ahead_manhattan": ahead,
        "k": w["k"], "length_turns": w["window_length_states"], "cell_a": list(a), "cell_b": list(b),
        "targets": list(dict.fromkeys(chosen)), "f4_label": tele.get("label"),
        "peer_cell_at_entry": list(peer["cell_at_entry"]) if peer else None,
        "peer_cells_in_window": peer["distinct_cells_in_window"] if peer else None,
        "peer_cells_to_game_end": peer["distinct_cells_to_game_end"] if peer else None,
        "peer_wait_fraction": peer["wait_fraction_in_window"] if peer else None,
        "peer_on_plant": bool(peer.get("plant_on_cell_at_entry")) if peer else None,
        "peer_verbs": sorted(set(peer["non_wait_verbs_in_window"])) if peer else None,
        "min_dist_dance_cell_to_target": min((manhattan(t, c) for t in targets for c in (a, b)), default=None),
        "letters": {k: letters.get(k, 0) for k in "PLHRWN"} if e["_read"] == "v4" else None,
        "end": e["f7_end"]["label"],
    }


def fisher_two_sided(a, b, c, d):
    n, r1, c1 = a + b + c + d, a + b, a + c

    def p(x):
        return comb(r1, x) * comb(n - r1, c1 - x) / comb(n, c1)

    p0 = p(a)
    return sum(p(x) for x in range(max(0, c1 - (n - r1)), min(r1, c1) + 1) if p(x) <= p0 + 1e-12)


def summarize(rows):
    out = {}
    for shape in SHAPES:
        s = [r for r in rows if r["shape"] == shape]
        lengths = sorted(r["length_turns"] for r in s)
        out[shape] = {
            "episodes": len(s),
            "peer_ahead_manhattan": Counter(str(r["peer_ahead_manhattan"]) for r in s),
            "length_min_med_max": [lengths[0], lengths[len(lengths) // 2], lengths[-1]] if lengths else None,
            "length_ge_12": sum(1 for x in lengths if x >= 12),
            "peer_never_moves_again": sum(1 for r in s if (r["peer_cells_to_game_end"] or 0) <= 1),
            "peer_on_plant": sum(1 for r in s if r["peer_on_plant"]),
            "peer_wait_fraction_le_0_05": sum(1 for r in s if (r["peer_wait_fraction"] or 0) <= 0.05),
            "peer_cells_in_window": Counter(str(r["peer_cells_in_window"]) for r in s),
            "ends": Counter(r["end"] for r in s),
            "f4_label": Counter(str(r["f4_label"]) for r in s),
            "episodes_with_letter_R": sum(1 for r in s if r["letters"] and r["letters"]["R"] > 0),
            "episodes_with_letter_H": sum(1 for r in s if r["letters"] and r["letters"]["H"] > 0),
        }
    out["total"] = len(rows)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--facts80", required=True)
    ap.add_argument("--g2", required=True)
    ap.add_argument("--out", required=True, help="JSON output path")
    args = ap.parse_args(argv)

    older = [describe(e) for e in load_rows(args.facts80, "facts80")]
    v4 = [describe(e) for e in load_rows(args.g2, "g2")]
    batch3 = [r for r in older if r["game"] is not None and r["unit"] is not None]
    # batch 3 = the v3 instrument, agent 6652642 — the 160-game comparator for the v4 read
    older_rows_raw = load_rows(args.facts80, "facts80")
    batch3_ids = {(e["game"], e["seat"], e["f1_dancer"]["unit"], e["f2_window"]["turn_start"])
                  for e in older_rows_raw if e.get("agent") == 6652642}
    batch3 = [r for r, e in zip(older, older_rows_raw)
              if (e["game"], e["seat"], e["f1_dancer"]["unit"], e["f2_window"]["turn_start"]) in batch3_ids]

    summary = {
        "older_read_80": summarize(older),
        "older_read_batch3_v3_160_games": summarize(batch3),
        "v4_read_25": summarize(v4),
        "fisher_two_sided": {
            "nobody_share_batch3_vs_v4": {
                "batch3": [sum(1 for r in batch3 if r["shape"] == "nobody"), len(batch3)],
                "v4": [sum(1 for r in v4 if r["shape"] == "nobody"), len(v4)],
            },
            "nobody_share_older_vs_v4": {
                "older": [sum(1 for r in older if r["shape"] == "nobody"), len(older)],
                "v4": [sum(1 for r in v4 if r["shape"] == "nobody"), len(v4)],
            },
        },
    }
    for key, pair in summary["fisher_two_sided"].items():
        (a, na), (c, nc) = pair.values()
        pair["p"] = round(fisher_two_sided(a, na - a, c, nc - c), 4)

    result = {"summary": summary, "episodes": older + v4}
    with open(args.out, "w") as f:
        json.dump(result, f, indent=1, sort_keys=True, default=lambda o: dict(o))
        f.write("\n")

    for name, rows in (("older read (80)", older), ("batch 3 = v3, 160 games", batch3), ("v4 read (25)", v4)):
        print(f"### {name}")
        for shape in SHAPES:
            s = summary[{"older read (80)": "older_read_80", "batch 3 = v3, 160 games": "older_read_batch3_v3_160_games",
                         "v4 read (25)": "v4_read_25"}[name]][shape]
            print(f"  {shape:<9} n={s['episodes']:>2} ahead={dict(s['peer_ahead_manhattan'])} len={s['length_min_med_max']} "
                  f">=12:{s['length_ge_12']} never-moves:{s['peer_never_moves_again']} plant:{s['peer_on_plant']} "
                  f"working:{s['peer_wait_fraction_le_0_05']} R-eps:{s['episodes_with_letter_R']} H-eps:{s['episodes_with_letter_H']} "
                  f"ends={dict(s['ends'])}")
    for key, pair in summary["fisher_two_sided"].items():
        print(f"Fisher {key}: {pair}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
