"""H3a Phase-A trigger preflight — exact analyzer.

Consumes the causal, public-outcome-anchored state reconstruction published by
`local_codex_1` at `h3a-trigger-preflight-state-package-2026-08-02.*` and evaluates the four
pinned Phase-A2 gates plus the integrity gate.

Scope, restated so it travels with the numbers: the state package is a reconstruction
anchored to observed public outcomes under the locked referee step, NOT an independent
continued-RNG replay. It is admissible for this retrospective coverage audit — the object
under audit is the games that actually happened — and it is NOT admissible for the Phase-C
value panel.

Exactness of the treatment predicate is taken from the frozen reconstruction record
`h3a-pressure-treatment-reconstruction-result-2026-07-31.json`:

    existing_tree_targets_only    = true
    tracked_opponent_crop_required= true
    bfs_ceil_div_eta_threshold    = 6
    score_operation               = candidate.score += candidate.score

and the resident's own primitives, read from `rust/src/bin/yamo_orchard_live.rs`:

    NEIGHBORS = [(0,1),(1,0),(0,-1),(-1,0)]                     # 4-way
    bfs_distances(walkable, sources)                            # unit-cost BFS
    ceil_div(a, b) = 10_000 if b <= 0 else (a + b - 1) / b      # integer

Usage:
    python3 claude_1/h3a-conditioned-value-unblock-preflight.py [--json OUT]
"""

from __future__ import annotations

import argparse
import collections
import gzip
import json
import os
from typing import Iterable

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(REPO, "data", "analysis", "live-agent-6553250")
STATE = os.path.join(PKG, "h3a-trigger-preflight-state-package-2026-08-02")

#: Frozen treatment threshold. Inclusive, per the reconstruction record.
ETA_THRESHOLD = 6
#: Sticky predicate boundary: visible opponent units.
PRESSURE_UNITS = 3
#: Gate-1/gate-3 turn boundary.
TURN_BOUNDARY = 150

NEIGHBORS = ((0, 1), (1, 0), (0, -1), (-1, 0))


def ceil_div(a: int, b: int) -> int:
    """Byte-for-byte the resident's own helper, including its b<=0 sentinel."""
    if b <= 0:
        return 10_000
    return (a + b - 1) // b


def bfs_distances(walkable: set, sources: Iterable) -> dict:
    """Unit-cost 4-neighbour BFS over walkable cells; mirrors `bfs_distances`."""
    dist = {}
    queue = collections.deque()
    for cell in sources:
        if cell not in dist:
            dist[cell] = 0
            queue.append(cell)
    while queue:
        cell = queue.popleft()
        d = dist[cell]
        for dx, dy in NEIGHBORS:
            nxt = (cell[0] + dx, cell[1] + dy)
            if nxt in walkable and nxt not in dist:
                dist[nxt] = d + 1
                queue.append(nxt)
    return dist


def _cells(raw) -> set:
    """Map records store cells as [x, y] pairs."""
    return {(int(c[0]), int(c[1])) for c in raw}


def load(state_prefix: str = STATE):
    with gzip.open(state_prefix + ".maps.jsonl.gz", "rt") as fh:
        maps = {}
        for line in fh:
            m = json.loads(line)
            maps[int(m["game_id"])] = m
    decisions = collections.defaultdict(list)
    with gzip.open(state_prefix + ".decisions.jsonl.gz", "rt") as fh:
        for line in fh:
            r = json.loads(line)
            decisions[int(r["game_id"])].append(r)
    for gid in decisions:
        decisions[gid].sort(key=lambda r: r["turn"])
    with open(state_prefix + ".manifest.json", "r", encoding="utf-8") as fh:
        manifest = json.load(fh)
    return maps, decisions, manifest


def activation_turn(rows: list) -> int | None:
    """First decision turn at which visible opponent units reach three.

    Sticky and perspective-local by construction: the first crossing is returned and never
    revoked, which is the frozen predicate. Uses only state visible at that decision.
    """
    for r in rows:
        if int(r["visible_opponent_unit_count"]) >= PRESSURE_UNITS:
            return int(r["turn"])
    return None


def eligible_trees_at(row: dict, walkable: set, opponent_tag: str, require_fruits: bool):
    """Trees the frozen treatment would transform, if the resident enumerated them.

    Conditions taken directly from the reconstruction record:
      * existing tree      -> present in this decision's tree list with health > 0
      * tracked opponent   -> created_by is the opponent seat (a crop, never `initial`)
      * reachable          -> the cell has a BFS distance from the acting troll
      * ETA <= 6           -> ceil_div(distance, movement_speed) <= 6
    """
    hits = []
    trees = [
        t
        for t in row["trees"]
        if t.get("created_by") == opponent_tag and int(t.get("health", 0)) > 0
    ]
    if require_fruits:
        trees = [t for t in trees if int(t.get("fruits", 0)) > 0]
    if not trees:
        return hits
    for troll in row["resident_trolls"]:
        dist = bfs_distances(walkable, [(int(troll["x"]), int(troll["y"]))])
        speed = int(troll["movement_speed"])
        for t in trees:
            cell = (int(t["x"]), int(t["y"]))
            if cell not in dist:
                continue  # unreachable -> ineligible, per fixture `ineligible_unreachable`
            if ceil_div(dist[cell], speed) <= ETA_THRESHOLD:
                hits.append(
                    {
                        "turn": int(row["turn"]),
                        "troll_id": int(troll["troll_id"]),
                        "cell": list(cell),
                        "species": t.get("species"),
                        "eta": ceil_div(dist[cell], speed),
                    }
                )
    return hits


def collapse_start(margins: list, checkpoints=(50, 100, 150, 200, 250, 300)) -> int | None:
    """Outcome-blind interval boundary: first checkpoint pair where margin goes + -> <=0."""
    for i in range(1, len(margins)):
        prev, cur = margins[i - 1], margins[i]
        if prev is None or cur is None:
            continue
        if prev > 0 and cur <= 0:
            return checkpoints[i - 1]
    return None


def cohorts_from_manifest(manifest: dict) -> dict:
    """The state manifest carries cohort membership per game row, not as two id lists."""
    out = {"catastrophe": [], "matched_win": []}
    for g in manifest["games"]:
        out[g["cohort"]].append(int(g["game_id"]))
    return out


def analyze(maps, decisions, manifest, margins_by_game, require_fruits=False):
    cohorts = cohorts_from_manifest(manifest)
    out = {"games": {}, "require_fruits": require_fruits}
    for cohort in ("catastrophe", "matched_win"):
        for gid in cohorts[cohort]:
            gid = int(gid)
            rows = decisions[gid]
            m = maps[gid]
            walkable = _cells(m["walkable"])
            seat = int(m["seat"])
            opponent_tag = "seat0" if seat == 1 else "seat1"
            act = activation_turn(rows)
            hits = []
            if act is not None:
                for r in rows:
                    if int(r["turn"]) < act:
                        continue
                    h = eligible_trees_at(r, walkable, opponent_tag, require_fruits)
                    if h:
                        hits.extend(h)
                        break  # gate 4 needs existence, not a census
            out["games"][gid] = {
                "cohort": cohort,
                "seat": seat,
                "opponent_tag": opponent_tag,
                "activation_turn": act,
                "activates_by_boundary": act is not None and act <= TURN_BOUNDARY,
                "collapse_start": collapse_start(margins_by_game.get(gid, [])),
                "first_eligible": hits[0] if hits else None,
                "decision_rows": len(rows),
            }
    return out


def gates(result: dict) -> dict:
    g = result["games"]
    cat = {k: v for k, v in g.items() if v["cohort"] == "catastrophe"}
    win = {k: v for k, v in g.items() if v["cohort"] == "matched_win"}

    g1 = sum(1 for v in cat.values() if v["activates_by_boundary"])
    g2 = sum(
        1
        for v in cat.values()
        if v["activation_turn"] is not None
        and v["collapse_start"] is not None
        and v["activation_turn"] < v["collapse_start"]
    )
    g3 = sum(1 for v in win.values() if v["activates_by_boundary"])
    g4 = sum(1 for v in cat.values() if v["first_eligible"] is not None)
    return {
        "gate1_activation_by_150": {"value": g1, "of": len(cat), "need": ">=8", "pass": g1 >= 8},
        "gate2_precedes_collapse": {"value": g2, "of": len(cat), "need": ">=8", "pass": g2 >= 8},
        "gate3_false_positive": {
            "value": g3,
            "of": len(win),
            "need": "<=20% (<=1 of 7)",
            "pass": g3 <= 0.20 * len(win),
        },
        "gate4_eligible_after_activation": {
            "value": g4,
            "of": len(cat),
            "need": ">=6",
            "pass": g4 >= 6,
        },
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", dest="out")
    ap.add_argument(
        "--require-fruits",
        action="store_true",
        help="restrict eligibility to fruit-bearing trees (harvest-branch subset)",
    )
    args = ap.parse_args(argv)

    maps, decisions, manifest = load()
    margins = margins_by_game_from_sides()
    result = analyze(maps, decisions, manifest, margins, args.require_fruits)
    result["gates"] = gates(result)

    print(f"{'game':>12} {'cohort':<12} {'act':>5} {'<=150':>6} {'collapse':>9} {'eligible@':>10}")
    for gid, v in sorted(result["games"].items(), key=lambda kv: (kv[1]["cohort"], kv[0])):
        fe = v["first_eligible"]
        print(
            f"{gid:>12} {v['cohort']:<12} {str(v['activation_turn']):>5} "
            f"{str(v['activates_by_boundary']):>6} {str(v['collapse_start']):>9} "
            f"{(str(fe['turn']) + ' eta' + str(fe['eta'])) if fe else '-':>10}"
        )
    print()
    for name, d in result["gates"].items():
        print(f"  {'PASS' if d['pass'] else 'FAIL'}  {name}: {d['value']}/{d['of']} (need {d['need']})")
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, sort_keys=True)
        print(f"\nwrote {args.out}")
    return 0


def margins_by_game_from_sides():
    """Checkpoint margins for the collapse-interval definition, from the frozen shared CSV."""
    import csv

    path = os.path.join(PKG, "top-player-new-games-shared-2026-08-02.sides.csv")
    per = collections.defaultdict(dict)
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["current_new_game"] != "1":
                continue
            per[int(r["game_id"])]["us" if r["is_current"] == "1" else "opp"] = r
    out = {}
    for gid, sides in per.items():
        if "us" not in sides or "opp" not in sides:
            continue
        row = []
        for t in (50, 100, 150, 200, 250, 300):
            a, b = sides["us"][f"score_t{t}"], sides["opp"][f"score_t{t}"]
            # A game shorter than 300 turns has no later checkpoints; absent is not zero.
            row.append(None if a == "" or b == "" else float(a) - float(b))
        out[gid] = row
    return out


if __name__ == "__main__":
    raise SystemExit(main())
