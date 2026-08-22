#!/usr/bin/env python3
r"""PEEK step 0b — the DECLINE census the fire table structurally could not provide.

Task `20260822-peek-planner-target-map`, the coordinator's card of 2026-08-22T19:29:45Z:

> Extend the probe to log **declines**: every turn where a mover's projected landing is an own
> unit's cell and the trigger did not fire, carrying the seam fields already captured. Probe
> only; the delivery candidate never receives it; no candidate edit.

## What this is, and what it is NOT

- **Probe only.** The two census rows (`SW1COLL0`, `SW1COLL1`) are inserted by
  `make_swap_candidate.py::patch_probe`, which the delivery candidate never goes through.
  `cgauto/submissions/candidate-swap-r1.rs` re-emits byte-identical to the G-1 package —
  sha256 `bbbb75d3…`, and the build manifest is the check. Both controls are unchanged too.
  **Probe parity is re-proven per fixture before a single row is read**: the probe's command
  stream must equal the plain candidate's or the run aborts.
- **Two sites, because one cannot see everything.** `reserved` starts as the cells of own units
  that are NOT moving, so a landing held by an own unit that is *itself* a mover is unreserved and
  the seam takes its early `continue` — that collision never reaches the partner block at all. A
  census placed only at the partner block would silently miss that whole class. `SW1COLL0` sits
  before the early exit; `SW1COLL1` sits at the partner decision with `detour` and the BFS
  distances in scope.
- **It answers a counterfactual only in the negative direction.** A decline row proves the seam
  SAW a collision and declined, and names which condition failed. It does not prove a widened
  trigger would have fired: that depends on the widened predicate, which is codex_1's at step 2
  and is not built here. Zero rows inside a window, by contrast, IS decisive — the seam never saw
  a collision there, so no predicate over seam-visible facts could have fired.

Run:  python3 claude_1/peek/decline_census.py [--json OUT] [--only OSC-005,OSC-027]
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for p in ("claude_1/t1", "claude_1/hstarve1", "claude_1/banana-restoration-r2", "claude_1/pipeline",
          "claude_1/swap1"):
    sys.path.insert(0, str(REPO / p))
import coverage as C          # noqa: E402
import fixture_harness as H   # noqa: E402
import fuzz_panel as fp       # noqa: E402
import regression_tests as rt  # noqa: E402
import semantic_harness as sh  # noqa: E402
import g1_sweep as G          # noqa: E402

FIXTURES = ["OSC-001", "OSC-005", "OSC-006", "OSC-011", "OSC-012", "OSC-027"]
CARD_FIXTURES = ["OSC-005", "OSC-027"]
BASE = REPO / "cgauto/submissions/candidate-door1-pure-deletion.rs"
CANDIDATE = REPO / "cgauto/submissions/candidate-swap-r1.rs"
PROBE = REPO / "claude_1/swap1/probe-swap-r1.rs"
OUT_JSON = HERE / "decline-census-2026-08-22.json"


def parse_bool(text: str) -> bool | str:
    if text == "true":
        return True
    if text == "false":
        return False
    return text


def parse_rows(stream: str, tag: str) -> list[dict]:
    """`TAG k=v k=v ...` lines. Values with a comma become a 2-tuple of ints."""
    out = []
    for line in stream.splitlines():
        line = line.strip()
        if not line.startswith(tag + " "):
            continue
        row = {}
        for field in line[len(tag) + 1:].split(" "):
            if "=" not in field:
                continue
            key, _, value = field.partition("=")
            if "," in value and all(part.lstrip("-").isdigit() for part in value.split(",")):
                row[key] = tuple(int(part) for part in value.split(","))
            elif value.lstrip("-").isdigit():
                row[key] = int(value)
            else:
                row[key] = parse_bool(value)
        out.append(row)
    return out


def decline_reason(row: dict, fired_turns: set[int], reached_late: set[tuple[int, int]]) -> str:
    """Why this collision did not fire, from the seam's own fields — first failing condition."""
    if row["turn"] in fired_turns and row.get("_late"):
        return "FIRED"
    if not row.get("_late") and (row["turn"], row["m"]) in reached_late:
        return "reached the partner block — see the late row for this turn"
    if row.get("early_take"):
        return "early_take: landing unreserved, mover simply took it (no swap considered)"
    if row.get("landing_forbidden"):
        return "landing_forbidden"
    if row.get("occupant_is_mover"):
        return "occupant is itself a mover"
    if row.get("occupant_already_swapped"):
        return "occupant already swapped this tick"
    if not row.get("index_ok", True):
        return "own-command index unavailable"
    if not row.get("legal", True):
        return "partner cannot legally step into the mover's cell"
    if not row.get("free", True):
        return "the mover's own cell is already reserved"
    if not row.get("allowed", True):
        return "the mover's cell is forbidden for the non-priority partner"
    if not row.get("yielding", False) and row.get("detour_existed", False):
        return "PREDICATE: partner is not WAIT and a detour existed"
    return "unclassified"


def episodes_of(sit: dict) -> list[dict]:
    return list(sit.get("detectors", {}).get("d1_episodes", []))


def run_fixture(sit, cfg, base_bin, cand_bin, probe_bin) -> dict:
    spec = H.spec_for(sit, cfg)
    turns = int(cfg["turns"])
    _, cand_cmds = rt.run_binary_custom(cand_bin, fp.make_referee(spec), turns)
    _, probe_cmds, err = C.run_diagnostic(probe_bin, fp.make_referee(spec), turns)
    if probe_cmds.strip() != cand_cmds.strip():
        raise G.GateError(f"{sit['id']}: the PROBE diverges from the plain candidate. The "
                          f"instrumented run is a different bot; no row from it means anything.")

    early = parse_rows(err, "SW1COLL0")
    late = parse_rows(err, "SW1COLL1")
    for row in late:
        row["_late"] = True
    fires = parse_rows(err, "SW1FIRE")
    fired_turns = {row["turn"] for row in fires}

    reached_late = {(row["turn"], row["m"]) for row in late}
    rows = []
    for row in early + late:
        rows.append({**{k: v for k, v in row.items() if k != "_late"},
                     "site": "late" if row.get("_late") else "early",
                     "reason": decline_reason(row, fired_turns, reached_late)})
    rows.sort(key=lambda r: (r["turn"], r["site"], r["m"]))

    eps = episodes_of(sit)
    per_episode = []
    for ep in eps:
        lo, hi = int(ep["turn_start"]), int(ep["turn_end"])
        inside = [r for r in rows if lo <= r["turn"] <= hi]
        per_episode.append({
            "episode": {"unit": ep.get("unit"), "turn_start": lo, "turn_end": hi,
                        "cells": ep.get("cells")},
            "collision_rows_inside": len(inside),
            "distinct_turns_inside": sorted({r["turn"] for r in inside}),
            "fires_inside": sorted(t for t in fired_turns if lo <= t <= hi),
            "rows": inside,
        })
    return {
        "fixture": sit["id"],
        "probe_parity": "PASS",
        "turns": turns,
        "collision_rows": len(rows),
        "early_rows": len(early),
        "late_rows": len(late),
        "fires": len(fires),
        "fire_turns": sorted(fired_turns),
        "episodes": per_episode,
        "all_rows": rows,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", default=",".join(FIXTURES))
    ap.add_argument("--json", default=str(OUT_JSON))
    args = ap.parse_args(argv)

    wanted = args.only.split(",")
    cfg = json.loads(H.CONFIG.read_text())
    sits = H.load_situations(wanted)

    results = []
    with tempfile.TemporaryDirectory(prefix="peek-census-") as wd:
        wd = Path(wd)
        bins = {}
        for name, src in (("base", BASE), ("cand", CANDIDATE), ("probe", PROBE)):
            bins[name] = wd / f"{name}.bin"
            sh.compile_text(src.read_text(), bins[name], crate=f"peek_{name}")
        for sit in sits:
            row = run_fixture(sit, cfg, bins["base"], bins["cand"], bins["probe"])
            results.append(row)
            inside = sum(ep["collision_rows_inside"] for ep in row["episodes"])
            print(f"  {row['fixture']}: {row['collision_rows']} collision rows "
                  f"({row['early_rows']} early / {row['late_rows']} late), "
                  f"{row['fires']} fires, {inside} collision rows INSIDE the recorded episode")

    verdict = {
        "task": "20260822-peek-planner-target-map",
        "step": "0b — decline census (probe only, no candidate edit)",
        "card": "coordination/messages/local_claude_1/20260822T192945Z-"
                "20260822-peek-planner-target-map-policy.md",
        "candidate_sha256_unchanged_from_g1_package": True,
        "probe_parity": "re-proven per fixture before any row was read",
        "what_zero_rows_inside_a_window_means": (
            "decisive negative: the seam never saw an own-unit collision there, so NO predicate "
            "over seam-visible facts — widened or not — could have fired inside that window."),
        "what_a_decline_row_does_NOT_mean": (
            "it does not prove a widened trigger would have fired; that depends on the widened "
            "predicate, which is codex_1's at step 2 and is not built here."),
        "card_fixtures": CARD_FIXTURES,
        "fixtures": results,
    }
    Path(args.json).write_text(json.dumps(verdict, indent=2) + "\n")
    print(f"\n  census -> {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
