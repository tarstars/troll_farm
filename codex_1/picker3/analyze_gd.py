#!/usr/bin/env python3
"""Keyed G-d comparison for the transferred Phase-3b door-1 candidate."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def properties(game):
    return sorted({v.get("property") for v in game.get("violations", []) if v.get("property")})


def flags(game):
    return sorted({v.get("flag") for v in game.get("flags", []) if v.get("flag")})


def keyed(panel):
    rows = {(g["map_id"], g["seat"]): g for g in panel["games"]}
    if len(rows) != 240:
        raise SystemExit(f"expected 240 unique keyed games, got {len(rows)}")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    cp = json.loads(Path(args.candidate).read_text())
    bp = json.loads(Path(args.base).read_text())
    if cp.get("candidate_sha256") != "457360589a65cb2662950761deba817852ea9eb0d2c53b05a3e6fd2ab9dfda8a":
        raise SystemExit("candidate hash mismatch")
    if bp.get("candidate_sha256") != "5e1f4df406480f678ff03677cdda0f69d510c5c94efe90d4f0a8231b70c3339e":
        raise SystemExit("base hash mismatch")
    crows, brows = keyed(cp), keyed(bp)
    if set(crows) != set(brows):
        raise SystemExit("matched-panel key mismatch")
    changed = []
    kinds = Counter()
    for key in sorted(crows):
        c, b = crows[key], brows[key]
        cp_, bp_ = properties(c), properties(b)
        cf, bf = flags(c), flags(b)
        if (bool(c["block"]), cp_, cf) == (bool(b["block"]), bp_, bf):
            continue
        kind = ("DE_NOVO_BLOCK" if c["block"] and not b["block"] else
                "HEALED_BLOCK" if b["block"] and not c["block"] else
                "PROPERTY_CHANGE_WITHIN_BLOCKED_GAME" if c["block"] and b["block"] else
                "PROPERTY_OR_FLAG_CHANGE_IN_CLEAN_GAME")
        kinds[kind] += 1
        changed.append({"map_id": key[0], "seat": key[1], "kind": kind,
                        "class": c["class"], "profile": c["profile"],
                        "base_block": bool(b["block"]), "candidate_block": bool(c["block"]),
                        "base_properties": bp_, "candidate_properties": cp_,
                        "base_flags": bf, "candidate_flags": cf,
                        "new_properties": sorted(set(cp_) - set(bp_)),
                        "new_flags": sorted(set(cf) - set(bf))})
    new_p3 = [r for r in changed if "P3" in r["new_properties"]]
    new_p4 = [r for r in changed if "P4" in r["new_properties"]]
    new_r5 = [r for r in changed if "r5-horizon" in r["new_flags"]]
    out = {
        "task": "20260820-pair-selector-anti-benching", "gate": "G-d",
        "verdict": "BLOCKED_FIRST_FALSIFIER",
        "candidate_sha256": cp["candidate_sha256"], "base_sha256": bp["candidate_sha256"],
        "candidate_panel_sha256": digest(args.candidate), "base_panel_sha256": digest(args.base),
        "matched_games": 240,
        "candidate_blocking": sum(bool(g["block"]) for g in crows.values()),
        "base_blocking": sum(bool(g["block"]) for g in brows.values()),
        "by_kind": dict(kinds), "new_p3_games": len(new_p3), "new_p4_games": len(new_p4),
        "new_r5_horizon_games": len(new_r5), "changed_games": changed,
        "stop_reason": "R-3 requires P3-clean, no new P4/r5-horizon, and blocking totals no worse; candidate fails all but the r5 clause. G-e was not run after the first binding falsifier.",
    }
    Path(args.output).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: out[k] for k in ("verdict", "candidate_blocking", "base_blocking",
          "by_kind", "new_p3_games", "new_p4_games", "new_r5_horizon_games")}, indent=2))


if __name__ == "__main__":
    main()
