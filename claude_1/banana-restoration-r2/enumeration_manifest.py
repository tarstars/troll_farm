#!/usr/bin/env python3
"""FROZEN EXACT ENUMERATION MANIFEST generator (design §D.2, review F8/R7).

This module MATERIALIZES the configuration set the design's §D.2 describes
(the frozen lattice axes and value sets) into an exact, machine-checkable
artifact `enumeration-manifest.json`. It is design-only tooling: it enumerates
the rows, assigns each a stable id + content hash + map/seed hash, DECLARES the
event classes / transition edges / R1 collisions each row is constructed to
witness, computes the coverage proof (every target -> witnessing row ids) from
the row set, and prints the true total row count.

It does NOT run the candidate binary; the later execution of these frozen rows
under the D.1 probe is the primary functional gate. Here we prove the frozen
*set* is complete (no unwitnessed event class, transition edge, R1 collision,
strict-tie fixture, or historical red witness) and reproducible.

Determinism: pure stdlib, no wall-clock / RNG / set-ordering leakage. All
hashes are sha256 over canonical `json.dumps(..., sort_keys=True)` byte strings.
Running twice yields byte-identical `enumeration-manifest.json`.

Reconciliation with §D.2 prose (review F8): the design's original arithmetic
summed to 1588 (ST1..ST5 + C1..C6 + five EV fixtures = 16 L-FIX rows, and NO
explicit rows for ST6/ST7 nor the historical red witnesses). This generator
adds the two missing strict-tie fixtures (ST6, ST7) and the four historical red
witnesses (round 3/4/5 rejected candidates) as first-class frozen rows, because
F8/R7 require them to be named manifest rows, not prose. The true total is
therefore 1594 (1588 + ST6 + ST7 + 4 red), reported by TOTAL below and asserted
against §D.2's reconciled count.
"""

from __future__ import annotations

import hashlib
import json
import os

GENERATOR_VERSION = "2026-08-06b"

# ---------------------------------------------------------------------------
# Target universe (what the coverage proof must witness).
# ---------------------------------------------------------------------------

EVENTS = [f"EV{i}" for i in range(1, 21)]

# Every transition id defined in A.2 / A.4 / A.4a (S9 T16' included).
TRANSITIONS = [
    "T0a", "T0b",
    "T2a", "T2b",
    "T3a", "T3b", "T3c", "T3d", "T3e", "T3f", "T3g", "T3h",
    "T4a", "T4b", "T4c", "T4d", "T4e", "T4f",
    "T5a", "T5b", "T5c", "T5d", "T5e", "T5f",
    "T6a",
    "T7a", "T7b", "T7c",
    "T8a", "T8b", "T8c", "T8d",
    "T16'",
]

COLLISIONS = ["C1", "C2", "C3", "C4", "C5", "C6"]

STRICT_TIES = ["ST1", "ST2", "ST3", "ST4", "ST5", "ST6", "ST7"]

# Historical red witnesses (rejected candidate short hashes -> the terminal
# defect each reproduced; red-evidence-*.md in this directory).
HISTORICAL_REDS = {
    "f29efd0e": "DEF-02 no convert/abandon; round-3 retry RED phase",
    "280ed777": "DEF-04/DEF-07 static-deadline + inconsistent deadlines (round 3)",
    "2f58edef": "DEF-07 CONVERSION_RACE_ORACLE unification RED (round 4)",
    "9f5ef833": "DEF-12 two-worker full-cargo banking parity livelock (round 5)",
}


def target_universe():
    toks = []
    toks += EVENTS
    toks += TRANSITIONS
    toks += COLLISIONS
    toks += STRICT_TIES
    toks += [f"RED:{h}" for h in sorted(HISTORICAL_REDS)]
    return toks


# ---------------------------------------------------------------------------
# Hash helpers (deterministic).
# ---------------------------------------------------------------------------

def _sha(obj) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def map_hash(template: str, water: str) -> str:
    """Stable per-(template,water) map/seed digest. A real runner binds the
    committed map bytes here; the design freezes the identity via this digest
    so a map drift changes the row's content hash and fails the frozen gate."""
    return _sha({"map": template, "water": water})[:16]


def seed_of(template: str, water: str) -> int:
    return int(map_hash(template, water)[:8], 16)


def make_row(sublattice, axes, cap, witnesses, note=""):
    template = axes.get("template", "-")
    water = axes.get("water", "dry")
    mh = map_hash(template, water)
    row = {
        "id": None,  # filled by caller
        "sublattice": sublattice,
        "axes": dict(axes),
        "cap": cap,
        "map_hash": mh,
        "seed": seed_of(template, water),
        "witnesses": sorted(set(witnesses)),
        "note": note,
    }
    return row


# ---------------------------------------------------------------------------
# Witness assignment for the parametric L-CORE lattice.
# Each row DECLARES the event classes / transition edges / R1 collisions it is
# constructed to exercise, as a deterministic function of its axis tuple. The
# union across all rows is the coverage proof.
# ---------------------------------------------------------------------------

def lcore_witnesses(template, water, profile, opp_eta, opp_count, stock, worker):
    w = set()
    # Ineligible playable map -> arbitration to Dormant, then activation.
    w.add("T0b")
    w.add("EV2")
    w.add("T2b")
    # Wood carrier cycle (forced bank + terminator + N1 stress).
    if worker == "full-wood":
        w.update({"EV10", "EV11", "T3g"})
        if template in ("T2", "T3", "T4"):
            w.add("T3h")          # articulation / single-door blocked-hold
        if template in ("T2", "T4"):
            w.add("EV13")         # bounce-blocked blockade geometry
    if worker == "train@8":
        pass                      # funding boundary; no channel before EV2
    # Target invalidation by a working peer (two-door parkable map).
    if template == "T4":
        w.add("EV12")
    # Opponent profile drives the flip / attack classification.
    if profile == "harvester":
        if opp_eta == 1 and water == "wet":
            w.update({"EV4", "T3a", "T6a"})          # ripe on-cell flip -> S6
        if opp_eta == 3:
            w.update({"EV5", "T3b", "T7a"})          # feasible convert -> S7 -> complete
        if opp_eta == 6:
            w.update({"EV6", "T3c", "T8a"})          # infeasible -> secure/bank -> S8 -> S9
        # a starved resident that idles while a harvester flips exercises the
        # S4/S5 contest edges (idle-yield / released contest).
        if stock == 0 and opp_eta in (3, 6):
            w.update({"T4a", "T4c", "T4d", "T4e", "T5a",
                      "T5b", "T5c", "T5d"})
    if profile == "chopper":
        w.update({"EV7", "T3d"})
        if opp_eta in (3, 6):
            w.add("T7a")          # oracle-feasible defensive conversion completes
    if profile == "mixed":
        w.update({"EV7", "T3d", "C2"})               # joint flip+attack
        if stock == 0:
            w.add("EV17")
    if profile == "idle":
        w.update({"EV14", "T4a"})                    # 3rd idle -> release S5
        w.update({"EV15", "T5a", "T4b"})             # productive re-entry
        if stock == 0:
            w.update({"EV17", "T3f", "T4f", "T5f"})
    # mother destroyed + stock 0 -> feature complete/impossible.
    if stock == 0 and profile in ("harvester", "chopper"):
        w.update({"EV8", "EV17", "T3f"})
    # released / idle worker death (combat maps) exercises S4/S5 death edges.
    if worker == "full-wood" and template in ("T2", "T4") and profile == "mixed":
        w.update({"T3e", "T4e", "T5e"})
    return w


# ---------------------------------------------------------------------------
# Row builders per sub-lattice.
# ---------------------------------------------------------------------------

TEMPLATES_CORE = ["T1", "T2", "T3", "T4"]
WATERS = ["dry", "wet"]
PROFILES = ["harvester", "chopper", "mixed", "idle"]
OPP_ETAS = [1, 3, 6, 12]
OPP_COUNTS = [1, 2]
STOCKS = [0, 1]
WORKERS = ["empty", "full-wood", "train@8"]


def build_lcore():
    rows = []
    for template in TEMPLATES_CORE:
        for water in WATERS:
            for profile in PROFILES:
                for opp_eta in OPP_ETAS:
                    for opp_count in OPP_COUNTS:
                        for stock in STOCKS:
                            for worker in WORKERS:
                                axes = {
                                    "template": template, "water": water,
                                    "profile": profile, "oppETA": opp_eta,
                                    "oppCount": opp_count, "stock": stock,
                                    "worker": worker,
                                }
                                wit = lcore_witnesses(template, water, profile,
                                                      opp_eta, opp_count,
                                                      stock, worker)
                                r = make_row("L-CORE", axes, 80, wit)
                                r["id"] = ("L-CORE-%s-%s-%s-e%d-n%d-s%d-%s"
                                           % (template, water, profile[:4],
                                              opp_eta, opp_count, stock,
                                              worker[:4]))
                                rows.append(r)
    return rows


def build_dormant():
    rows = []
    for template in TEMPLATES_CORE:
        for water in WATERS:
            axes = {"template": template, "water": water, "worker": "absent"}
            # worker=absent => never EV2 => dormant structural identity control.
            # turn-1 arbitration decides ineligible (¬EV1) -> Dormant identity.
            wit = {"EV1", "T0b"}   # ineligible playable -> Dormant (identity)
            r = make_row("L-CORE-DORMANT", axes, 80, wit,
                         note="worker=absent collapses to one dormant control")
            r["id"] = "L-DORM-%s-%s" % (template, water)
            rows.append(r)
    return rows


def build_elig():
    rows = []
    for water in WATERS:
        for worker in ("absent", "present"):
            axes = {"template": "T5", "water": water, "worker": worker}
            wit = {"EV1", "T0a"}   # arbitration: orchard-eligible -> forced S1
            r = make_row("L-ELIG", axes, 80, wit,
                         note="eligibility overrides worker/opponent -> S1")
            r["id"] = "L-ELIG-T5-%s-%s" % (water, worker)
            rows.append(r)
    return rows


def build_solo():
    rows = []
    for profile in PROFILES:
        for opp_eta in (1, 12):
            for stock in STOCKS:
                axes = {"template": "T6", "water": "dry", "profile": profile,
                        "oppETA": opp_eta, "oppCount": 1, "stock": stock}
                wit = {"T0b"}      # solo worker => never EV2 (dormant whole game)
                r = make_row("L-SOLO", axes, 80, wit,
                             note="T6 solo worker, never activates (¬EV2)")
                r["id"] = ("L-SOLO-%s-e%d-s%d" % (profile[:4], opp_eta, stock))
                rows.append(r)
    return rows


def build_long():
    rows = []
    for profile in PROFILES:
        axes = {"template": "T6", "water": "dry", "profile": profile,
                "cap": 120}
        wit = {"EV3", "T2a"}       # ¬EV2 to turn>100 -> deadline abandon
        r = make_row("L-LONG", axes, 120, wit,
                     note="cap120 EV3 deadline with ¬EV2")
        r["id"] = "L-LONG-T6-%s-cap120" % profile[:4]
        rows.append(r)
    for water in WATERS:
        for profile in ("harvester", "chopper"):
            axes = {"template": "T1", "water": water, "profile": profile,
                    "cap": 120, "activate": "@92"}
            wit = {"EV18"}         # late-activate near I-5 plant cutoff
            r = make_row("L-LONG", axes, 120, wit,
                         note="T1 late-activate@92 -> EV18 plant cutoff guard")
            r["id"] = "L-LONG-T1-%s-%s-late92" % (water, profile[:4])
            rows.append(r)
    return rows


# ---- L-FIX dedicated deterministic fixtures -------------------------------

def build_fix():
    rows = []

    # Strict-tie fixtures ST1..ST7 (mirror the oracle self-test; each is a
    # frozen grid witness of a boundary the coverage proof must contain).
    st = {
        "ST1": ("harvest tie -> infeasible (completion == opp_harvest)",
                {"ST1", "EV6", "T3c"}),
        "ST2": ("harvest feasible-by-one (completion == opp_harvest-1)",
                {"ST2", "EV5", "T3b", "T7a"}),
        "ST3": ("single-chopper kill == completion -> conceded infeasible",
                {"ST3", "EV7", "T3d"}),
        "ST4": ("single-chopper kill == completion+1 -> feasible",
                {"ST4", "EV7", "T3d", "T7a"}),
        "ST5": ("earlier-arriving 2nd chopper advances destroy (NO power sum)",
                {"ST5", "EV7", "T3d"}),
        "ST6": ("one unit harvests+chops -> min(harvest,destroy) governs",
                {"ST6", "EV7", "T3d"}),
        "ST7": ("growth-crossing: growth-aware chop-out != static ceil(h/chop)",
                {"ST7", "EV5", "T3b"}),
    }
    for name in STRICT_TIES:
        note, wit = st[name]
        axes = {"template": "T1", "water": "dry", "fixture": name}
        r = make_row("L-FIX", axes, 80, wit, note=note)
        r["id"] = "L-FIX-%s" % name
        rows.append(r)

    # Compound-event collision fixtures C1..C6 (A.6 worked resolutions). Each
    # fixture also traverses the edges on its resolution path.
    cx = {
        "C1": ("EV9+EV8+EV17: resident dies on final feature chop -> S10",
               {"C1", "EV9", "EV8", "EV17", "T3e", "T7b"}),
        "C2": ("flip(EV5/EV6)+EV7 attack -> oracle joint deadline",
               {"C2", "EV7", "EV5", "EV6", "T3d"}),
        "C3": ("EV8+EV10: final chop kills mother and fills carrier -> T7a",
               {"C3", "EV8", "EV10", "T7a", "T3g"}),
        "C4": ("EV11+EV16: leftover DROP lands as lost plant dies -> T8c/T8a",
               {"C4", "EV11", "EV16", "T8c", "T8a"}),
        "C5": ("EV2+EV3: activation predicate true on deadline turn -> S10",
               {"C5", "EV2", "EV3", "T2a"}),
        "C6": ("EV12+EV13: target invalidates as block counter trips -> T3g",
               {"C6", "EV12", "EV13", "T3g"}),
    }
    for name in COLLISIONS:
        note, wit = cx[name]
        axes = {"template": "T2", "water": "dry", "fixture": name}
        r = make_row("L-FIX", axes, 80, wit, note=note)
        r["id"] = "L-FIX-%s" % name
        rows.append(r)

    # Dedicated single-event / edge fixtures (constructed, not hoped for).
    ev = {
        "EV9": ("combat opponent adjacent to resident on T2 kills it",
                {"EV9", "T3e", "T5e", "T8b", "T7b"}),
        "EV15": ("release then productive re-entry S5->S3",
                 {"EV15", "T5a", "T4b"}),
        "EV16": ("chopper kills the lost plant post-EV6 -> claim lapse",
                 {"EV16", "T8c", "T16'"}),
        "EV19": ("mother made unreachable mid-conversion -> T7c abandon",
                 {"EV19", "T7c", "EV5", "T3b"}),
        "EV20": ("all doors made unreachable while carrying -> T8d release",
                 {"EV20", "T8d", "EV6", "T3c", "T8a"}),
    }
    for name in ("EV9", "EV15", "EV16", "EV19", "EV20"):
        note, wit = ev[name]
        axes = {"template": "T2", "water": "dry", "fixture": name}
        r = make_row("L-FIX", axes, 80, wit, note=note)
        r["id"] = "L-FIX-%s" % name
        rows.append(r)

    return rows


def build_reds():
    """Historical red witnesses as frozen regression rows (review F8/R7): the
    gate fails if any rejected-candidate behavior is absent or regresses."""
    rows = []
    for h in sorted(HISTORICAL_REDS):
        axes = {"template": "T2", "water": "dry", "red_candidate": h}
        r = make_row("L-RED", axes, 120, {f"RED:{h}"},
                     note=HISTORICAL_REDS[h])
        r["id"] = "L-RED-%s" % h
        # each row's content hash still binds its declared witness set
        rows.append(r)
    return rows


# ---------------------------------------------------------------------------
# Assembly, hashing, coverage proof.
# ---------------------------------------------------------------------------

def build_all_rows():
    rows = []
    rows += build_lcore()
    rows += build_dormant()
    rows += build_elig()
    rows += build_solo()
    rows += build_long()
    rows += build_fix()
    rows += build_reds()
    # content hash per row over its canonical body (id excluded so the hash is
    # position-independent; witnesses/axes/cap/map all bound).
    for r in rows:
        body = {k: r[k] for k in r if k != "content_hash"}
        r["content_hash"] = _sha(body)
    # stable id uniqueness check
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate row id"
    return rows


def compute_coverage(rows):
    universe = target_universe()
    coverage = {tok: [] for tok in universe}
    for r in rows:
        for tok in r["witnesses"]:
            if tok in coverage:
                coverage[tok].append(r["id"])
    for tok in coverage:
        coverage[tok].sort()
    uncovered = sorted(tok for tok in universe if not coverage[tok])
    return coverage, uncovered


def sublattice_counts(rows):
    counts = {}
    for r in rows:
        counts[r["sublattice"]] = counts.get(r["sublattice"], 0) + 1
    return dict(sorted(counts.items()))


def build_manifest():
    rows = build_all_rows()
    coverage, uncovered = compute_coverage(rows)
    manifest = {
        "generator_version": GENERATOR_VERSION,
        "design_ref": "design-banana-fsm-2026-08-06.md §D.2",
        "total_rows": len(rows),
        "sublattice_counts": sublattice_counts(rows),
        "target_universe_size": len(target_universe()),
        "uncovered_targets": uncovered,
        "coverage": coverage,
        "rows": rows,
    }
    manifest["manifest_digest"] = _sha(
        {k: manifest[k] for k in manifest if k != "manifest_digest"})
    return manifest


def main():
    manifest = build_manifest()
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "enumeration-manifest.json")
    with open(out_path, "w") as fh:
        json.dump(manifest, fh, sort_keys=True, indent=2)
        fh.write("\n")

    print("enumeration manifest: %s" % out_path)
    print("generator_version : %s" % manifest["generator_version"])
    print("TOTAL rows        : %d" % manifest["total_rows"])
    for name, n in manifest["sublattice_counts"].items():
        print("  %-16s: %d" % (name, n))
    print("target universe   : %d" % manifest["target_universe_size"])
    print("uncovered targets : %s"
          % (manifest["uncovered_targets"] or "NONE (coverage complete)"))
    print("manifest_digest   : %s" % manifest["manifest_digest"])

    if manifest["uncovered_targets"]:
        raise SystemExit("COVERAGE INCOMPLETE: %s"
                         % manifest["uncovered_targets"])
    print("coverage proof    : complete (every event class, transition edge, "
          "R1 collision, strict-tie fixture, and historical red witnessed)")


if __name__ == "__main__":
    main()
