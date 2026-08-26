#!/usr/bin/env python3
r"""Swap R-1 — the probe-only per-fire event table required before G-1 rev 2.

Task `20260821-swap-r1-cure`. codex_1's remedy ruling
(`codex_1/reviews/swap-r1-g1-remedy-ruling-2026-08-21.md`) BLOCKS any candidate edit and
authorises exactly this: extend the existing probe with a compact per-fire event table over
OSC-001, 005, 006, 011, 012 and 027, then propose the smallest *stateless* predicate that
separates the two repeated-pair fixtures (006, 011) from the working ones (005, 012, 001).

**Nothing here changes the candidate.** The new seam facts ride on `FIRE_ROW`, which the builder
inserts into the PROBE only; `make_swap_candidate.py` re-emits `cgauto/submissions/candidate-swap-r1.rs`
byte-identical to the G-1 package (build manifest is the check), and this script re-proves probe
parity against the plain candidate before it reads a single row.

## What each column is, and what it is NOT

- `next_from_landing` / `vacates_partner_cell`: `next_cell(walkable, landing, target, speed)` —
  the mover's own next step *after* it takes the partner's cell, and whether that step leaves it.
  This is the seam-visible half of "pass-through viability". It says nothing about the partner.
- `partner_next_base` is read from the BASE run's transcript at turn+1. The base and the
  candidate are the SAME world only strictly before the fixture's first fire, so for every fire
  this column is a DIFFERENT world's answer and is flagged as such (`base_same_world`). It is
  reported because the ruling asked for it, and it must not be used as proof.
- `partner_next_candidate` is the partner's command on the following tick in the probe's own run:
  in-world, but it is a consequence of the swap, not an independent fact about the partner.

## The predicate replay is an UPPER BOUND, not a result

Predicates are replayed against fires recorded under the current candidate. Suppressing a fire
changes every later tick, so "P1 would drop 27/27 fires in OSC-006" means *those* fires cannot
survive P1 — not that OSC-006 ends with zero fires. Only a G-1 rev 2 rerun can say that, and
G-1 rev 2 is blocked until codex_1 rules on the construction.

Run:  python3 claude_1/swap1/g1_event_table.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for p in ("claude_1/t1", "claude_1/hstarve1", "claude_1/banana-restoration-r2", "claude_1/pipeline"):
    sys.path.insert(0, str(REPO / p))
import coverage as C          # noqa: E402
import fixture_harness as H   # noqa: E402
import fuzz_panel as fp       # noqa: E402
import regression_tests as rt  # noqa: E402
import semantic_harness as sh  # noqa: E402

sys.path.insert(0, str(HERE))
import g1_sweep as G          # noqa: E402

FIXTURES = ["OSC-001", "OSC-005", "OSC-006", "OSC-011", "OSC-012", "OSC-027"]
REPEATED_PAIR = {"OSC-006", "OSC-011"}      # must be separated OUT
WORKING = {"OSC-001", "OSC-005", "OSC-012"}  # must be kept

BASE = REPO / "cgauto/submissions/candidate-door1-pure-deletion.rs"
CANDIDATE = REPO / "cgauto/submissions/candidate-swap-r1.rs"
PROBE = HERE / "probe-swap-r1.rs"
OUT_JSON = HERE / "g1-event-table-2026-08-21.json"


def base_commands_by_turn(stream: str) -> dict[int, dict[int, str]]:
    """turn -> {unit id -> command}, from a plain run's one-line-per-turn stdout."""
    out: dict[int, dict[int, str]] = {}
    for line_no, line in enumerate(stream.strip().splitlines(), start=1):
        row: dict[int, str] = {}
        for command in line.split(";"):
            command = command.strip()
            parts = command.split()
            if len(parts) >= 2 and parts[1].lstrip("-").isdigit():
                row[int(parts[1])] = command
        out[line_no] = row
    return out


def cmd_verb(command: str) -> str:
    parts = command.split()
    return parts[0].upper() if parts else ""


# ---------------------------------------------------------------------------------------
# the stateless predicates under test. Each takes one event row and answers: would the swap
# still fire? A predicate is a CONJUNCT — it can only remove fires, never add them.

def p1_pass_through(row) -> bool:
    """Pass-through viability (the ruling's first candidate).

    The mover must have somewhere to go BEYOND the partner's cell, and its own next step from
    that cell must leave it. Stateless: both facts are already at the seam.
    """
    return (not row["target_is_landing"]) and row["vacates_partner_cell"]


def p2_target_beyond(row) -> bool:
    """Weaker half of P1: the landing is not itself the mover's final target."""
    return not row["target_is_landing"]


def p3_mover_progress(row) -> bool:
    """Mover's BFS distance to its own target strictly decreases by taking the cell."""
    return row["bfs_from_landing"] >= 0 and row["bfs_from_landing"] < row["bfs_from_mover_cell"]


def p4_working_partner_only(row) -> bool:
    """Fire only when the partner is NOT idle — i.e. drop the whole YIELD path."""
    return not row["partner_was_wait"]


def p5_idle_partner_only(row) -> bool:
    """Fire only when the partner's command is WAIT — never displace a working partner.

    This is the inverse of P4 and it drops the whole no-detour path. In the full 34-fixture
    corpus every no-detour fire is one of OSC-006's 27 dance fires, so on the recorded evidence
    it costs nothing measured; it is nevertheless a SCOPE REDUCTION of the accepted G-0
    construction and is codex_1's to rule on, not mine to build.
    """
    return row["partner_was_wait"]


def p6_idle_partner_and_pass_through(row) -> bool:
    """P5 conjoined with the ruling's pass-through viability, for completeness."""
    return p5_idle_partner_only(row) and p1_pass_through(row)


PREDICATES = {
    "P1 pass-through viability (target beyond the cell AND next step vacates it)": p1_pass_through,
    "P2 landing is not the mover's final target": p2_target_beyond,
    "P3 mover BFS distance strictly decreases": p3_mover_progress,
    "P4 partner is not WAIT (drops the yield path entirely)": p4_working_partner_only,
    "P5 partner IS WAIT (drops the no-detour/working-partner path entirely)": p5_idle_partner_only,
    "P6 P5 and pass-through viability": p6_idle_partner_and_pass_through,
}


# the fields a stateless predicate could actually test, with cells and ids reduced to shape.
# Two fires with the same vector are INDISTINGUISHABLE to any predicate over seam-visible facts,
# so if one must fire and the other must not, no such predicate exists and the seam must widen.
SHAPE_FIELDS = ("vacates_partner_cell", "target_is_landing", "partner_was_wait", "partner_verb",
                "path", "detour_existed", "bfs_from_mover_cell", "bfs_from_landing")


def shape(row) -> tuple:
    return tuple(row[field] for field in SHAPE_FIELDS)


def collisions(events):
    """Fires that must be separated but are identical in every seam-visible field."""
    buckets = {}
    for row in events:
        buckets.setdefault(shape(row), []).append(row)
    out = []
    for vector, rows in buckets.items():
        must_drop = sorted({r["fixture"] for r in rows if r["fixture"] in REPEATED_PAIR})
        must_keep = sorted({r["fixture"] for r in rows if r["fixture"] in WORKING})
        if must_drop and must_keep:
            out.append({
                "seam_shape": dict(zip(SHAPE_FIELDS, vector)),
                "must_drop_fixtures": must_drop, "must_keep_fixtures": must_keep,
                "fires": [{"fixture": r["fixture"], "turn": r["turn"], "mover": r["mover"],
                           "partner": r["partner"], "reverse_swap_turn": r["reverse_swap_turn"],
                           "partner_next_candidate": r["partner_next_candidate"]}
                          for r in rows],
            })
    return out


def rows_for(sit, cfg, base_bin, cand_bin, probe_bin):
    spec = H.spec_for(sit, cfg)
    turns = int(cfg["turns"])
    _, base_cmds = rt.run_binary_custom(base_bin, fp.make_referee(spec), turns)
    _, cand_cmds = rt.run_binary_custom(cand_bin, fp.make_referee(spec), turns)
    _, probe_cmds, err = C.run_diagnostic(probe_bin, fp.make_referee(spec), turns)
    if probe_cmds.strip() != cand_cmds.strip():
        raise G.GateError(f"{sit['id']}: PROBE diverges from the plain candidate — the "
                          f"instrumented run is a different bot and no row below means anything.")
    _, fires, _, cmds = G.parse(err)
    base_rows = base_commands_by_turn(base_cmds)
    first_fire = min((f["turn"] for f in fires), default=None)

    events = []
    for position, fire in enumerate(fires):
        seam = fire.get("seam")
        if seam is None:
            raise G.GateError(f"{sit['id']}: fire at turn {fire['turn']} carries no SW1SEAM row")
        pair = tuple(sorted((fire["m"], fire["u"])))
        reverse = next((later["turn"] for later in fires[position + 1:]
                        if tuple(sorted((later["m"], later["u"]))) == pair), None)
        partner_cmd = fire["u_displaced"]
        next_turn = fire["turn"] + 1
        base_next = base_rows.get(next_turn, {}).get(fire["u"])
        cand_next = cmds.get(next_turn, {}).get(fire["u"])
        events.append({
            "fixture": sit["id"], "turn": fire["turn"],
            "mover": fire["m"], "mover_cell": fire["m_from"], "landing": fire["m_to"],
            "mover_target": seam["m_target"],
            "next_from_landing": seam["next_from_landing"],
            "vacates_partner_cell": seam["vacates_partner_cell"],
            "target_is_landing": seam["target_is_landing"],
            "bfs_from_mover_cell": seam["bfs_from_mover_cell"],
            "bfs_from_landing": seam["bfs_from_landing"],
            "partner": fire["u"], "partner_cmd": partner_cmd,
            "partner_was_wait": cmd_verb(partner_cmd) == "WAIT",
            "partner_verb": cmd_verb(partner_cmd),
            "path": fire["path"], "detour_existed": fire["detour_existed"],
            "partner_next_base": base_next,
            "base_same_world": first_fire is not None and next_turn <= first_fire,
            "partner_next_candidate": cand_next,
            "reverse_swap_turn": reverse,
            "reverse_within_4": reverse is not None and 0 < reverse - fire["turn"] <= 4,
        })
    return events


def main() -> int:
    cfg = json.loads(H.CONFIG.read_text())
    sits = H.load_situations(FIXTURES)
    missing = sorted(set(FIXTURES) - {s["id"] for s in sits})
    if missing:
        raise G.GateError(f"the ruling names fixtures that the corpus does not have: {missing}")

    events, per_fixture = [], {}
    with tempfile.TemporaryDirectory(prefix="swap-events-") as wd:
        wd = Path(wd)
        bins = {}
        for name, src in (("base", BASE), ("cand", CANDIDATE), ("probe", PROBE)):
            bins[name] = wd / f"{name}.bin"
            sh.compile_text(src.read_text(), bins[name], crate=f"swap_ev_{name}")
        for sit in sits:
            rows = rows_for(sit, cfg, bins["base"], bins["cand"], bins["probe"])
            events.extend(rows)
            per_fixture[sit["id"]] = len(rows)
            print(f"  {sit['id']}: {len(rows)} fires")

    replay = {}
    for label, predicate in PREDICATES.items():
        kept = {fid: 0 for fid in FIXTURES}
        for row in events:
            if predicate(row):
                kept[row["fixture"]] += 1
        separates = (all(kept[f] == 0 for f in REPEATED_PAIR)
                     and all(kept[f] == per_fixture[f] for f in WORKING))
        replay[label] = {
            "fires_kept": kept,
            "fires_seen": dict(per_fixture),
            "drops_every_repeated_pair_fire": all(kept[f] == 0 for f in REPEATED_PAIR),
            "keeps_every_working_fire": all(kept[f] == per_fixture[f] for f in WORKING),
            "separates_on_the_recorded_fires": separates,
        }

    unseparable = collisions(events)
    verdict = {
        "task": "20260821-swap-r1-cure", "gate": "G-1 diagnostic (probe only, no candidate edit)",
        "ruling": "codex_1/reviews/swap-r1-g1-remedy-ruling-2026-08-21.md",
        "fixtures": FIXTURES,
        "fires_per_fixture": per_fixture,
        "caveat": ("The predicate replay is an UPPER BOUND on the recorded fires only: "
                   "suppressing a fire changes every later tick, so a clean replay is not a "
                   "G-1 result. Only a G-1 rev 2 rerun can produce one."),
        "predicate_replay": replay,
        "seam_shape_collisions": unseparable,
        "no_stateless_predicate_exists_for": sorted(
            {fixture for row in unseparable for fixture in row["must_drop_fixtures"]}),
        "events": events,
    }
    OUT_JSON.write_text(json.dumps(verdict, indent=2) + "\n")

    print()
    for label, row in replay.items():
        mark = "SEPARATES" if row["separates_on_the_recorded_fires"] else "does not separate"
        print(f"  {mark:18}  {label}")
        print(f"                      kept: {row['fires_kept']}  of {row['fires_seen']}")
    print()
    for row in unseparable:
        print(f"  COLLISION  {row['must_drop_fixtures']} vs {row['must_keep_fixtures']} share one "
              f"seam shape: {row['seam_shape']}")
        for fire in row["fires"]:
            print(f"             {fire['fixture']} turn {fire['turn']}  m={fire['mover']} "
                  f"u={fire['partner']}  reverse={fire['reverse_swap_turn']}  "
                  f"u_next_in_world={fire['partner_next_candidate']!r}")
    print(f"\n  event table -> {OUT_JSON.relative_to(REPO)}  ({len(events)} fires)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
