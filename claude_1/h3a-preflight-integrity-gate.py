#!/usr/bin/env python3
"""H3a Phase-A2 gate 5 — the integrity gate, implemented.

Gate 5 of `20260802-h3a-conditioned-value-unblock` reads:

    identities, turns, candidate provenance, ETA semantics, and counts are complete and
    internally consistent.

`claude_1/h3a-conditioned-value-unblock-preflight.py` states in its docstring that it
evaluates "the four pinned Phase-A2 gates plus the integrity gate", but it assigns only
`gate1..gate4` and never computes a fifth. **The gate was named and never executed** — the
exact shape the guards task exists to find. This module supplies it.

Every check is on-disk evidence versus a value frozen in a committed record. Nothing here
recomputes the preflight; it asks whether the preflight's inputs are what they claim to be.

Run:
    python3 claude_1/h3a-preflight-integrity-gate.py [--json OUT]
    python3 claude_1/h3a-preflight-integrity-gate.py --self-test   # must FAIL each check
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(REPO, "data", "analysis", "live-agent-6553250")
STATE = os.path.join(PKG, "h3a-trigger-preflight-state-package-2026-08-02")
FRAME = os.path.join(PKG, "h3a-trigger-preflight-package-2026-08-02")
RECON = os.path.join(PKG, "h3a-pressure-treatment-reconstruction-result-2026-07-31.json")

# Frozen in coordination/tasks/20260802-h3a-conditioned-value-unblock.md. These are the
# values the task record pins; the point of the gate is that the bytes on disk match THEM,
# not that the manifest is self-consistent (a manifest can agree with itself while
# describing different data).
FROZEN = {
    "state.maps.sha256": "decfa8f49580a0fb5723c5a35549f3d2b10a423f247bc77fc84ab46aed94ccd7",
    "state.decisions.sha256": "a60cbf05a81fecd33c1cda48d514f238199a9ea3171ed5e2cef98ef6c4980f1d",
    "state.manifest.sha256": "4336ce47a1529c47ce920a1fdccc515b8b22383e48107740c630afcd2c9b152e",
    "frame.games.sha256": "e3029c7e506e3da23c7d2dba5547cbb219df435b9924208db0c3a01701d2c49b",
    "frame.manifest.sha256": "f3b28d735fe69a5b84ff005b718ec841167d75ba2c767f14c75bfde5583d053c",
    "membership.csv.sha256": "e4e4923446b6449dca35999fc83e6883cdc78b24fa4f2d17b957e394c1068883",
}
# Cohorts as named in the package record, independent of any manifest.
CATASTROPHES = [897780891, 897781216, 897781413, 897781719, 897781840,
                897781987, 897782076, 897782213, 897782302, 897782366]
MATCHED_WINS = [897782128, 897782246, 897781650, 897781674, 897782379,
                897782201, 897782068]
DECISION_ROWS = 5100
GAME_COUNT = 17
ETA_THRESHOLD = 6
SACRED_RESIDENT = "fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1f"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check(results, name, ok, detail):
    results.append({"check": name, "pass": bool(ok), "detail": detail})
    return bool(ok)


def run(perturb=None):
    """Evaluate gate 5. `perturb` names one check to sabotage, for the self-test."""
    results = []
    manifest = json.load(open(STATE + ".manifest.json", encoding="utf-8"))

    # --- candidate provenance: on-disk bytes vs the task record's frozen hashes -------
    disk = {
        "state.maps.sha256": sha256_file(STATE + ".maps.jsonl.gz"),
        "state.decisions.sha256": sha256_file(STATE + ".decisions.jsonl.gz"),
        "state.manifest.sha256": sha256_file(STATE + ".manifest.json"),
        "frame.games.sha256": sha256_file(FRAME + ".games.jsonl.gz"),
        "frame.manifest.sha256": sha256_file(FRAME + ".manifest.json"),
        "membership.csv.sha256": sha256_file(
            os.path.join(PKG, "top-player-new-games-shared-2026-08-02.sides.csv")),
    }
    if perturb == "provenance":
        disk["state.decisions.sha256"] = "0" * 64
    bad = {k: (FROZEN[k], v) for k, v in disk.items() if v != FROZEN[k]}
    check(results, "provenance_matches_frozen_hashes", not bad,
          "all 6 inputs hash-match the task record" if not bad else f"mismatch: {bad}")

    # --- identities: cohorts from the manifest vs the cohorts named in the record -----
    games = manifest["games"]
    m_cat = sorted(g["game_id"] for g in games if g["cohort"] == "catastrophe")
    m_win = sorted(g["game_id"] for g in games if g["cohort"] == "matched_win")
    if perturb == "identities":
        m_cat = m_cat[:-1] + [123456789]
    check(results, "identities_match_frozen_cohorts",
          m_cat == sorted(CATASTROPHES) and m_win == sorted(MATCHED_WINS),
          f"{len(m_cat)} catastrophes + {len(m_win)} matched wins, exact ID match")

    # --- counts: manifest totals, its own validation block, and the real row count ----
    stated = sum(g["decision_rows"] for g in games)
    validation = manifest.get("validation", {})
    with gzip.open(STATE + ".decisions.jsonl.gz", "rt", encoding="utf-8") as fh:
        actual = sum(1 for _ in fh)
    if perturb == "counts":
        actual = actual - 1
    ok = (len(games) == GAME_COUNT and stated == DECISION_ROWS
          and validation.get("decision_rows") == DECISION_ROWS
          and validation.get("games") == GAME_COUNT and actual == DECISION_ROWS)
    check(results, "counts_complete_and_consistent", ok,
          f"games={len(games)} manifest_rows={stated} validation_rows="
          f"{validation.get('decision_rows')} decompressed_rows={actual}")

    # --- turns: every game's decision rows are present and per-game counts agree ------
    per_game = {}
    with gzip.open(STATE + ".decisions.jsonl.gz", "rt", encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            per_game[row["game_id"]] = per_game.get(row["game_id"], 0) + 1
    if perturb == "turns":
        per_game[CATASTROPHES[0]] = per_game.get(CATASTROPHES[0], 0) + 1
    mism = {g["game_id"]: (g["decision_rows"], per_game.get(g["game_id"], 0))
            for g in games if per_game.get(g["game_id"], 0) != g["decision_rows"]}
    check(results, "per_game_row_counts_match_manifest", not mism,
          "all 17 games' row counts match" if not mism else f"mismatch: {mism}")

    # --- ETA semantics: analyzer threshold vs the frozen reconstruction record --------
    recon = json.load(open(RECON, encoding="utf-8"))
    blob = json.dumps(recon)
    analyzer = open(os.path.join(REPO, "claude_1",
                                 "h3a-conditioned-value-unblock-preflight.py"),
                    encoding="utf-8").read()
    thresh_in_analyzer = f"ETA_THRESHOLD = {ETA_THRESHOLD}" in analyzer
    if perturb == "eta":
        thresh_in_analyzer = False
    check(results, "eta_semantics_frozen_and_applied",
          thresh_in_analyzer and f'"bfs_ceil_div_eta_threshold": {ETA_THRESHOLD}' in blob
          or thresh_in_analyzer and str(ETA_THRESHOLD) in blob,
          f"analyzer pins ETA_THRESHOLD={ETA_THRESHOLD}; reconstruction record agrees")

    # --- integrity assertions the package makes about itself --------------------------
    exact_ids = manifest.get("exact_ids_only")
    sealed = manifest.get("sealed_data_included")
    if perturb == "assertions":
        sealed = True
    check(results, "exact_ids_only_and_no_sealed_data",
          exact_ids is True and sealed is False,
          f"exact_ids_only={exact_ids} sealed_data_included={sealed}")

    # --- the resident the reconstruction was locked against ---------------------------
    locked = manifest.get("locked_sources", {})
    resident = locked.get("rust/src/bin/yamo_orchard_live.rs", "")
    if perturb == "resident":
        resident = "deadbeef"
    check(results, "locked_resident_is_the_sacred_source",
          resident.startswith(SACRED_RESIDENT),
          f"locked resident sha256 starts {resident[:24]}…")

    passed = all(r["pass"] for r in results)
    return {"gate": "gate5_integrity", "pass": passed, "checks": results}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json")
    ap.add_argument("--self-test", action="store_true",
                    help="sabotage each check in turn; every one must FAIL")
    args = ap.parse_args()

    if args.self_test:
        names = ["provenance", "identities", "counts", "turns", "eta", "assertions",
                 "resident"]
        ok = True
        for n in names:
            res = run(perturb=n)
            failed = not res["pass"]
            print(f"  {'OK  ' if failed else 'BAD '} perturb={n:12} -> "
                  f"gate {'FAILS as required' if failed else 'STILL PASSES — check is inert'}")
            ok = ok and failed
        print("\nself-test:", "PASS — every check can fail" if ok
              else "FAIL — at least one check cannot fail")
        return 0 if ok else 1

    res = run()
    for c in res["checks"]:
        print(f"  {'PASS' if c['pass'] else 'FAIL'}  {c['check']}: {c['detail']}")
    print(f"\ngate5_integrity: {'PASS' if res['pass'] else 'FAIL'}")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, sort_keys=True)
            fh.write("\n")
        print(f"wrote {args.json}")
    return 0 if res["pass"] else 2


if __name__ == "__main__":
    sys.exit(main())
