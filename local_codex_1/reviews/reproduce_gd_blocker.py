#!/usr/bin/env python3
"""Independent keyed audit of the Phase-3b G-d hard-gate result."""

import argparse
import json
from collections import Counter
from pathlib import Path


EXPECTED_CANDIDATE = "457360589a65cb2662950761deba817852ea9eb0d2c53b05a3e6fd2ab9dfda8a"
EXPECTED_BASE = "5e1f4df406480f678ff03677cdda0f69d510c5c94efe90d4f0a8231b70c3339e"
IDENTITY_FIELDS = ("map_id", "seat", "seed", "class", "profile", "attempt", "turns")
META_FIELDS = ("corpus_version", "instrument_version", "referee_sha256", "engine_sha256")


def load(path):
    return json.loads(Path(path).read_text())


def keyed(panel):
    rows = {}
    for game in panel["games"]:
        key = (game["map_id"], game["seat"])
        if key in rows:
            raise SystemExit(f"duplicate game key: {key}")
        rows[key] = game
    if len(rows) != 240:
        raise SystemExit(f"expected 240 games, got {len(rows)}")
    return rows


def properties(game):
    return sorted({row["property"] for row in game.get("violations", []) if row.get("property")})


def flags(game):
    return sorted({row["flag"] for row in game.get("flags", []) if row.get("flag")})


def require_clean_execution(label, rows):
    bad = []
    for key, game in rows.items():
        if game.get("execution_status") != "ok" or game.get("command_error_total") != 0:
            bad.append(key)
    if bad:
        raise SystemExit(f"{label} has non-clean executions: {bad[:5]}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--claimed-decomposition", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    candidate = load(args.candidate)
    base = load(args.base)
    if candidate.get("candidate_sha256") != EXPECTED_CANDIDATE:
        raise SystemExit("candidate source identity mismatch")
    if base.get("candidate_sha256") != EXPECTED_BASE:
        raise SystemExit("base source identity mismatch")
    if candidate.get("parent_sha256") != EXPECTED_BASE:
        raise SystemExit("candidate run did not use the exact base as parent")
    meta_mismatches = [field for field in META_FIELDS if candidate.get(field) != base.get(field)]
    if meta_mismatches:
        raise SystemExit(f"panel metadata mismatch: {meta_mismatches}")

    candidate_rows = keyed(candidate)
    base_rows = keyed(base)
    if set(candidate_rows) != set(base_rows):
        raise SystemExit("candidate/base game-key populations differ")
    require_clean_execution("candidate", candidate_rows)
    require_clean_execution("base", base_rows)

    changed = []
    identity_mismatches = []
    de_novo = []
    healed = []
    new_p3 = []
    new_p4 = []
    new_r5 = []
    kinds = Counter()
    for key in sorted(candidate_rows):
        cand = candidate_rows[key]
        parent = base_rows[key]
        if any(cand.get(field) != parent.get(field) for field in IDENTITY_FIELDS):
            identity_mismatches.append(key)
            continue
        cand_properties = properties(cand)
        base_properties = properties(parent)
        cand_flags = flags(cand)
        base_flags = flags(parent)
        cand_block = bool(cand["block"])
        base_block = bool(parent["block"])
        if (cand_block, cand_properties, cand_flags) == (base_block, base_properties, base_flags):
            continue
        row = {
            "map_id": key[0],
            "seat": key[1],
            "base_block": base_block,
            "candidate_block": cand_block,
            "new_properties": sorted(set(cand_properties) - set(base_properties)),
            "new_flags": sorted(set(cand_flags) - set(base_flags)),
        }
        if cand_block and not base_block:
            row["kind"] = "DE_NOVO_BLOCK"
        elif base_block and not cand_block:
            row["kind"] = "HEALED_BLOCK"
        elif cand_block and base_block:
            row["kind"] = "PROPERTY_CHANGE_WITHIN_BLOCKED_GAME"
        else:
            row["kind"] = "PROPERTY_OR_FLAG_CHANGE_IN_CLEAN_GAME"
        kinds[row["kind"]] += 1
        changed.append(row)
        if cand_block and not base_block:
            de_novo.append(key)
        if base_block and not cand_block:
            healed.append(key)
        if "P3" in row["new_properties"]:
            new_p3.append(key)
        if "P4" in row["new_properties"]:
            new_p4.append(key)
        if "r5-horizon" in row["new_flags"]:
            new_r5.append(key)

    if identity_mismatches:
        raise SystemExit(f"matched-panel identity mismatch: {identity_mismatches[:5]}")

    result = {
        "verdict": "BLOCKED_FIRST_FALSIFIER",
        "matched_games": len(candidate_rows),
        "candidate_blocking": sum(bool(row["block"]) for row in candidate_rows.values()),
        "base_blocking": sum(bool(row["block"]) for row in base_rows.values()),
        "de_novo_blocking": len(de_novo),
        "healed_blocking": len(healed),
        "changed_games_count": len(changed),
        "by_kind": dict(kinds),
        "new_p3_games": len(new_p3),
        "new_p4_games": len(new_p4),
        "new_r5_horizon_games": len(new_r5),
        "metadata_match": True,
        "identity_match": True,
        "changed_games": changed,
    }
    if not (
        result["candidate_blocking"] > result["base_blocking"]
        and result["de_novo_blocking"] > 0
        and result["new_p3_games"] > 0
        and result["new_p4_games"] > 0
    ):
        raise SystemExit("the claimed binding G-d falsifier was not reproduced")

    claimed = load(args.claimed_decomposition)
    scalar_checks = {
        "matched_games": result["matched_games"],
        "candidate_blocking": result["candidate_blocking"],
        "base_blocking": result["base_blocking"],
        "new_p3_games": result["new_p3_games"],
        "new_p4_games": result["new_p4_games"],
        "new_r5_horizon_games": result["new_r5_horizon_games"],
    }
    mismatched_scalars = {
        key: {"independent": value, "claimed": claimed.get(key)}
        for key, value in scalar_checks.items()
        if claimed.get(key) != value
    }
    if claimed.get("by_kind") != result["by_kind"]:
        mismatched_scalars["by_kind"] = {
            "independent": result["by_kind"],
            "claimed": claimed.get("by_kind"),
        }
    projection = ("map_id", "seat", "kind", "base_block", "candidate_block", "new_properties", "new_flags")
    claimed_changed = [{field: row.get(field) for field in projection} for row in claimed.get("changed_games", [])]
    independent_changed = [{field: row.get(field) for field in projection} for row in changed]
    if mismatched_scalars or claimed_changed != independent_changed:
        raise SystemExit("committed decomposition differs from independent keyed audit")
    result["claimed_decomposition_match"] = True
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key != "changed_games"}, indent=2))


if __name__ == "__main__":
    main()
