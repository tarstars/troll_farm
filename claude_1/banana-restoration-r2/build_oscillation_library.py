#!/usr/bin/env python3
"""Build the frozen oscillation situation library (manifest item M3a).

M3a is the FIRST HALF of the owner's manifest point 5: *enumerate and freeze*
the situations in which oscillation occurred.  The independent adjudication of
what the best action was (M3b) is a separate, later item and is deliberately
NOT performed here: this builder records no opinion, preference, ranking or
"correct action" anywhere.  Deriving one now from the same scorer that produced
the oscillation would poison M3b with exactly the circularity it exists to
avoid.

Sources harvested
-----------------
1. The fuzz-panel floor -- the arena parent judged against itself over the
   240-game corpus.  D-1 alternation episodes and P4 liveness stall windows.
2. Real-corpus episodes committed under ``data/analysis`` (partial: the raw
   arena games themselves live under the git-ignored ``data/external`` and are
   NOT committed, so those situations are frozen as PARTIAL -- provenance and
   observed window only, no invented world state).

Freezing discipline
-------------------
Every situation is written as literal JSON: the map rows, the plants, the
units of BOTH players, the inventories and the commands are copied verbatim
out of the referee transcript.  Nothing is a call back into the map generator,
so a generator change cannot silently move a situation.  Each file carries the
SHA-256 of its own payload; ``oscillation_library.py`` recomputes it on load
and fails closed.

Usage
-----
    python3 build_oscillation_library.py --games <games.jsonl.gz> \
        --panel-config <cfg.json> --out <oscillation-library/>
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "pipeline"))
sys.path.insert(0, str(HERE))

import fuzz_panel as fp                      # noqa: E402
import trace_detectors as td                 # noqa: E402
from oscillation_library import (            # noqa: E402
    SCHEMA_SITUATION, SCHEMA_INDEX, payload_sha256, library_sha256,
)

# --- classifier constants (published criteria, see the report) --------------
# The idleness criterion is taken verbatim from the mechanism analysis
# `oscillation-attack-claude_1-2026-08-09.md` section 1.5: "the blocking peer
# emits WAIT on >= 95 % of the window and changes cell on 0.00 % of turns".
IDLE_WAIT_FRACTION = 0.95

STENCIL_DX = (-2, -1, 0, 1, 2, 3)
STENCIL_DY = (-2, -1, 0, 1, 2)

# The eight dihedral frames of the square lattice.
DIHEDRAL = (
    (1, 0, 0, 1), (0, -1, 1, 0), (-1, 0, 0, -1), (0, 1, -1, 0),
    (-1, 0, 0, 1), (0, 1, 1, 0), (1, 0, 0, -1), (0, -1, -1, 0),
)


def _apply(frame, dx, dy):
    a, b, c, d = frame
    return (a * dx + b * dy, c * dx + d * dy)


def _inverse_apply(frame, x, y):
    """Frames are orthogonal integer matrices; the inverse is the transpose."""
    a, b, c, d = frame
    return (a * x + c * y, b * x + d * y)


def canonical_stencil(smap, focus, marks):
    """The resolver-relevant neighbourhood, in a canonical orientation.

    `focus` are the cells the situation turns on (the two oscillation cells,
    or the stalled unit's cell).  The stencil covers exactly those cells and
    their orthogonal neighbours -- which is exactly the shipped resolver's
    action space: the direct landing and the detour candidate set are drawn
    from the orthogonal neighbours of the current cell.  Decoration further
    away (other plants, the shacks, the map border) is deliberately excluded:
    it does not enter the decision and would make every episode look unique.

    The rendering is minimised over the eight dihedral frames, so the same
    local shape at any rotation or reflection on any map yields the same
    string.  This is the "geometry" half of the dedupe key; the mechanism and
    the blocker state are the other halves.
    """
    cells = set(focus)
    for c in focus:
        cells |= set(orth(c))
    origin = focus[0]
    best = None
    for frame in DIHEDRAL:
        items = []
        for cell in cells:
            dx, dy = cell[0] - origin[0], cell[1] - origin[1]
            items.append(_apply(frame, dx, dy)
                         + (marks.get(cell,
                                      "." if cell in smap.walkable else "#"),))
        text = "".join("%d,%d%s;" % it for it in sorted(items))
        if best is None or text < best:
            best = text
    return best


def geometry_excerpt(smap, origin, marks):
    """Human-readable, NON-canonical map excerpt.  Documentation only -- the
    dedupe key is `canonical_stencil`."""
    out = []
    for dy in STENCIL_DY:
        row = []
        for dx in STENCIL_DX:
            cell = (origin[0] + dx, origin[1] + dy)
            row.append(marks.get(cell,
                                 "." if cell in smap.walkable else "#"))
        out.append("".join(row))
    return out


# ---------------------------------------------------------------------------
# transcript -> literal world state
# ---------------------------------------------------------------------------

def transcript_rows(transcript_text):
    lines = transcript_text.split("\n")
    parts = lines[0].split()
    width, height = int(parts[0]), int(parts[1])
    return width, height, [lines[1 + y].rstrip("\r") for y in range(height)]


def freeze_state(tr, t):
    """The referee-reported world state at turn `t`, verbatim.

    Field order matches the wire protocol the bot itself reads, so the record
    can be replayed straight into `fuzz_panel.make_referee` without a
    generator call.
    """
    st = tr.state(t)
    return {
        "turn": t,
        "inventories": {
            "own": list(st.inventories[0]),
            "opponent": list(st.inventories[1]),
        },
        "plants": [
            [p.kind, p.cell[0], p.cell[1], p.size, p.health, p.fruits,
             p.cooldown] for p in st.plants
        ],
        "units": [
            [u.id, u.player, u.cell[0], u.cell[1], u.speed, u.capacity,
             u.harvest_power, u.chop_power] + list(u.carry)
            for u in st.units
        ],
    }


def command_lines(commands_text):
    lines = commands_text.split("\n")
    while lines and lines[-1] == "":
        lines.pop()
    return lines


# ---------------------------------------------------------------------------
# classification (mechanism), measured from the transcript only
# ---------------------------------------------------------------------------

def orth(cell):
    x, y = cell
    return ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))


def measure_blocker(tr, episode):
    """Every measured fact about the peer that could be the blocker.

    Returns (blocker_record_or_None, all_peer_records).  A peer qualifies as
    THE blocker when it holds a single cell for the whole window and that cell
    is orthogonally adjacent to one of the two oscillation cells -- the only
    configuration in which the shipped resolver's detour branch can be forced
    (mechanism analysis, Theorem 2 and Theorem 3).
    """
    uid = episode["unit"]
    t0, t1 = episode["turn_start"], episode["turn_end"]
    a, b = tuple(episode["cells"][0]), tuple(episode["cells"][1])
    adj = set(orth(a)) | set(orth(b))
    st0 = tr.state(t0)
    n = t1 - t0 + 1
    peers, blocker = [], None
    for p in st0.own_units():
        if p.id == uid:
            continue
        cells_win = [tr.pos(p.id, t) for t in range(t0, t1 + 1)]
        cells_win = [c for c in cells_win if c is not None]
        waits = sum(1 for t in range(t0, t1 + 1)
                    if tr.cmd_of(p.id, t) is None)
        verbs = sorted({tr.cmd_of(p.id, t).verb
                        for t in range(t0, t1 + 1)
                        if tr.cmd_of(p.id, t) is not None})
        cells_rest = {tr.pos(p.id, t) for t in range(t0, tr.T + 1)
                      if tr.pos(p.id, t) is not None}
        plant = st0.plant_at(p.cell)
        rec = {
            "unit": p.id,
            "cell_at_entry": list(p.cell),
            "stats": {"speed": p.speed, "capacity": p.capacity,
                      "harvest_power": p.harvest_power,
                      "chop_power": p.chop_power},
            "carry_at_entry": list(p.carry),
            "distinct_cells_in_window": len(set(cells_win)),
            "distinct_cells_to_game_end": len(cells_rest),
            "wait_fraction_in_window": round(waits / n, 4),
            "non_wait_verbs_in_window": verbs,
            "plant_on_cell_at_entry": (
                [plant.kind, plant.size, plant.health, plant.fruits,
                 plant.cooldown] if plant else None),
            "orth_adjacent_to_oscillation_cells": p.cell in adj,
        }
        rec["idle_by_analysis_criterion"] = bool(
            rec["wait_fraction_in_window"] >= IDLE_WAIT_FRACTION
            and rec["distinct_cells_in_window"] == 1)
        peers.append(rec)
        if rec["distinct_cells_in_window"] == 1 and rec[
                "orth_adjacent_to_oscillation_cells"]:
            if blocker is None or rec["unit"] < blocker["unit"]:
                blocker = rec
    return blocker, peers


def classify(tr, episode, blocker, peers):
    """Mechanism label.  Purely a function of measured transcript facts.

    M1  corridor block .......... a stationary peer occupies the route and the
                                  resolver's detour invents a retreat.
    M2  stationary occupation ... the stationary peer is IDLE and stands on a
        invisible to planning     live plant: its `WAIT` carries
                                  `Target::None`, which `compatible` treats as
                                  universally compatible, so the peer is a
                                  physical obstacle that planning cannot see.
    M3  scorer cycle ............ no peer can be blocking, so by Theorem 2 the
                                  goal itself must alternate.
    UNCLASSIFIED ................ none of the above discriminators applies.
    """
    if not peers:
        return "M3", ("no other own unit is alive during the window, so the "
                      "resolver's detour branch cannot fire (Theorem 2); the "
                      "alternation must come from the goal selector")
    if blocker is None:
        return "UNCLASSIFIED", (
            "own peers exist but none holds a single cell orthogonally "
            "adjacent to an oscillation cell, so neither the detour branch "
            "nor a stationary occupation is established by the transcript")
    if blocker["idle_by_analysis_criterion"] and blocker[
            "plant_on_cell_at_entry"]:
        return "M2", (
            "peer %d holds cell %s for the whole window (wait fraction %.2f, "
            "1 distinct cell) standing on a live %s -- an idle unit occupying "
            "the plant cell, invisible to `compatible` because `WAIT` carries "
            "`Target::None`"
            % (blocker["unit"], tuple(blocker["cell_at_entry"]),
               blocker["wait_fraction_in_window"],
               blocker["plant_on_cell_at_entry"][0]))
    return "M1", (
        "peer %d holds cell %s for the whole window and is %s -- a stationary "
        "unit on the route rather than an idle occupier of the goal cell "
        "(wait fraction %.2f, plant on its cell: %s)"
        % (blocker["unit"], tuple(blocker["cell_at_entry"]),
           "idle" if blocker["idle_by_analysis_criterion"] else "working",
           blocker["wait_fraction_in_window"],
           blocker["plant_on_cell_at_entry"][0]
           if blocker["plant_on_cell_at_entry"] else "none"))


# ---------------------------------------------------------------------------
# situation construction
# ---------------------------------------------------------------------------

GOAL_UNRESOLVED = (
    "The goal the bot actually held during the window is NOT observable in "
    "the transcript, so the M1 / M2 discriminator (is the blocker's cell the "
    "target, or merely on the route?) is INFERRED from the mechanism "
    "analysis rather than measured. Settled by an instrumented build that "
    "logs the resolver's goal per turn -- out of boundary for M3a, which may "
    "not modify any bot -- or by the Decision Packet.")

M3_UNRESOLVED = (
    "Attribution of this goal two-cycle to the exclusive on-door pricing "
    "branch of `endgame_candidates` is INFERRED from the mechanism analysis "
    "section 1.3, not measured here: the transcript shows the alternation, "
    "not the scores that caused it. Settled by a committed scorer trace for "
    "this exact frozen state.")

UNCLASSIFIED_UNRESOLVED = (
    "No own peer holds a single cell orthogonally adjacent to an oscillation "
    "cell for the whole window, so neither the forced-detour mechanism nor a "
    "stationary occupation is established. Settled by a resolver/goal trace "
    "over this frozen state.")

P4_UNRESOLVED = (
    "Whether this stall shares a mechanism with the D-1 population is NOT "
    "established here. The mechanism analysis section 1.6 argues the terminal "
    "oscillation population and the permanently-idle-worker population are "
    "the same population seen from opposite ends; that is an argument, not a "
    "measurement on this situation. Settled by a goal trace showing what the "
    "stalled unit was selecting.")


def door_evidence(tr, cells):
    """Which oscillation cells are orthogonal neighbours of a shack.

    Recorded because the M3 mechanism named in the manifest is specifically a
    door-pricing discontinuity; this is the observable that supports or
    undermines that reading.  It is evidence, not a verdict.
    """
    own_doors = set(orth(tuple(tr.smap.shacks[0])))
    opp_doors = set(orth(tuple(tr.smap.shacks[1])))
    return {
        "own_shack": list(tr.smap.shacks[0]),
        "opponent_shack": list(tr.smap.shacks[1]),
        "cells_that_are_own_shack_doors": [
            list(c) for c in cells if c in own_doors],
        "cells_that_are_opponent_shack_doors": [
            list(c) for c in cells if c in opp_doors],
    }


def d1_situation(row, tr, episode, prov):
    t0, t1 = episode["turn_start"], episode["turn_end"]
    a, b = tuple(episode["cells"][0]), tuple(episode["cells"][1])
    blocker, peers = measure_blocker(tr, episode)
    mech, why = classify(tr, episode, blocker, peers)
    st0 = tr.state(t0)

    marks = {a: "o", b: "x"}
    if blocker is not None:
        bc = tuple(blocker["cell_at_entry"])
        marks[bc] = "P" if blocker["plant_on_cell_at_entry"] else "B"
    stencil = canonical_stencil(tr.smap, [a, b], marks)
    excerpt_marks = dict(marks)
    for p in st0.plants:
        excerpt_marks.setdefault(p.cell, "T")
    for s, ch in ((tr.smap.shacks[0], "S"), (tr.smap.shacks[1], "s")):
        excerpt_marks.setdefault(tuple(s), ch)
    excerpt = geometry_excerpt(tr.smap, a, excerpt_marks)

    cmds = command_lines(row["artifacts"]["candidate_commands"])
    window_cmds = [{"turn": t, "line": cmds[t - 1]}
                   for t in range(t0, min(t1, len(cmds)) + 1)]

    blocker_state = "NONE"
    if blocker is not None:
        blocker_state = ("IDLE" if blocker["idle_by_analysis_criterion"]
                         else "WORKING")

    p4 = [v["detail"] for v in row["violations"] if v["property"] == "P4"]
    return {
        "kind": "D1_EPISODE",
        "completeness": "FULL",
        "provenance": prov,
        "classification": {
            "mechanism": mech,
            "mechanism_evidence": why,
            "blocker_state": blocker_state,
            "blocker": blocker,
            "all_own_peers_at_entry": peers,
            "geometry_stencil": stencil,
            "geometry_excerpt": excerpt,
            "geometry_excerpt_legend": (
                "5 rows x 6 cols centred on the first oscillation cell "
                "(origin at row 2, col 2); o/x oscillation cells, B blocker, "
                "P blocker standing on a plant, T other plant, S own shack, "
                "s opponent shack, . walkable, # not. Documentation only."),
            "shack_door_evidence": door_evidence(tr, [a, b]),
            "classifier_version": "m3a-observational/1",
        },
        "window": {
            "unit": episode["unit"],
            "turn_start": t0,
            "turn_end": t1,
            "length_turns": t1 - t0 + 1,
            "cells": [list(a), list(b)],
            "k": episode["k"],
            "commands": window_cmds,
        },
        "world_state_at_entry": freeze_state(tr, t0),
        "initial_world_state": freeze_state(tr, 1),
        "static_map_rows": prov.pop("_rows"),
        "detectors": {
            "counts": row["detector_counts"],
            "d1_episodes": [e for e in td.detect_d1(tr)["episodes"]],
            "p4_violations": p4,
            "live_horizon": fp.live_horizon(tr),
            "turns_simulated": tr.T,
        },
        "unresolved": ([GOAL_UNRESOLVED] if mech in ("M1", "M2")
                       else [M3_UNRESOLVED] if mech == "M3"
                       else [UNCLASSIFIED_UNRESOLVED]),
    }


def p4_situation(row, tr, detail, prov):
    t0, t1 = detail["window_start"], detail["window_end"]
    st0 = tr.state(t0)
    own = list(st0.own_units())
    # anchor = the own unit with the longest immobile run inside the window
    def immobile_run(u):
        best = cur = 0
        prev = None
        for t in range(t0, t1 + 1):
            c = tr.pos(u.id, t)
            cur = cur + 1 if c is not None and c == prev else 1
            prev = c
            best = max(best, cur)
        return best
    anchor = max(own, key=lambda u: (immobile_run(u), -u.id)) if own else None
    marks = {}
    if anchor is not None:
        marks[anchor.cell] = "o"
    for u in own:
        marks.setdefault(u.cell, "B")
    for p in st0.plants:
        marks.setdefault(p.cell, "P" if p.cell in marks else "T")
    origin = anchor.cell if anchor is not None else tuple(tr.smap.shacks[0])
    stencil = canonical_stencil(tr.smap, [origin], marks)
    excerpt_marks = dict(marks)
    for s, ch in ((tr.smap.shacks[0], "S"), (tr.smap.shacks[1], "s")):
        excerpt_marks.setdefault(tuple(s), ch)
    excerpt = geometry_excerpt(tr.smap, origin, excerpt_marks)

    cmds = command_lines(row["artifacts"]["candidate_commands"])
    window_cmds = [{"turn": t, "line": cmds[t - 1]}
                   for t in range(t0, min(t1, len(cmds)) + 1)]
    units = [{
        "unit": u.id,
        "cell_at_entry": list(u.cell),
        "stats": {"speed": u.speed, "capacity": u.capacity,
                  "harvest_power": u.harvest_power,
                  "chop_power": u.chop_power},
        "distinct_cells_in_window": len({
            tr.pos(u.id, t) for t in range(t0, t1 + 1)
            if tr.pos(u.id, t) is not None}),
        "wait_fraction_in_window": round(
            sum(1 for t in range(t0, t1 + 1) if tr.cmd_of(u.id, t) is None)
            / (t1 - t0 + 1), 4),
    } for u in own]
    return {
        "kind": "P4_STALL",
        "completeness": "FULL",
        "provenance": prov,
        "classification": {
            "mechanism": "UNCLASSIFIED",
            "mechanism_evidence": (
                "P4 liveness stall with no D-1 alternation in the same game: "
                "the stationary counterpart of the oscillation population "
                "(mechanism analysis 1.6). No mover mechanism is established "
                "by the transcript, so no M1/M2/M3 label is asserted."),
            "blocker_state": "NONE",
            "blocker": None,
            "all_own_peers_at_entry": units,
            "geometry_stencil": stencil,
            "geometry_excerpt": excerpt,
            "geometry_excerpt_legend": (
                "5 rows x 6 cols centred on the stalled anchor unit's cell "
                "(origin at row 2, col 2); o anchor, B other own unit, "
                "P own unit on a plant, T plant, S own shack, s opponent "
                "shack, . walkable, # not. Documentation only."),
            "classifier_version": "m3a-observational/1",
        },
        "window": {
            "unit": anchor.id if anchor is not None else None,
            "turn_start": t0,
            "turn_end": t1,
            "length_turns": t1 - t0 + 1,
            "cells": [list(u.cell) for u in own],
            "k": None,
            "commands": window_cmds,
        },
        "world_state_at_entry": freeze_state(tr, t0),
        "initial_world_state": freeze_state(tr, 1),
        "static_map_rows": prov.pop("_rows"),
        "detectors": {
            "counts": row["detector_counts"],
            "d1_episodes": [],
            "p4_violations": [v["detail"] for v in row["violations"]
                              if v["property"] == "P4"],
            "live_horizon": fp.live_horizon(tr),
            "turns_simulated": tr.T,
        },
        "unresolved": [P4_UNRESOLVED],
    }


# ---------------------------------------------------------------------------
# real-corpus (PARTIAL) situations
# ---------------------------------------------------------------------------

def real_corpus_situations(repo: Path):
    """Real arena episodes whose *evidence* is committed.

    The raw games and trajectories they cite live under `data/external`, which
    is git-ignored (`.gitignore:15`) and absent from this checkout.  The world
    state at the entry turn therefore CANNOT be frozen literally, and is not
    invented: these situations are marked PARTIAL and carry only what the
    committed result files actually state.
    """
    out = []
    src = (repo / "data" / "analysis" / "live-agent-6553250"
           / "elost-same-tree-occupancy-deadlock-result-2026-07-31.json")
    if not src.exists():
        return out
    doc = json.loads(src.read_text())
    g, inc = doc["game"], doc["incident"]
    a = tuple(inc["ping_pong_cells"][0])
    b = tuple(inc["ping_pong_cells"][1])
    out.append({
        "kind": "REAL_CORPUS",
        "completeness": "PARTIAL",
        "provenance": {
            "source": "real-corpus",
            "evidence_file": str(src.relative_to(repo)),
            "evidence_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
            "game_id": g["game_id"],
            "seat": g["resident_seat"],
            "opponent_profile": g["opponent"],
            "turns": g["turns"],
            "raw_game_path": g["raw_path"],
            "raw_game_sha256": g["raw_sha256"],
            "trajectory_path": g["trajectory_path"],
            "trajectory_sha256": g["trajectory_sha256"],
            "bot_source": doc["source_reproduction"]["current"]["source"],
            "bot_source_sha256":
                doc["source_reproduction"]["current"]["source_sha256"],
            "corpus_version": "arena-live-agent-6553250",
            "instrument_version": "cgauto/analyze_elost_same_tree_deadlock.py",
        },
        "classification": {
            "mechanism": "M2",
            "mechanism_evidence": (
                "the committed result records unit %d full of wood standing "
                "on live %s %s emitting %d consecutive WAITs (turns %d-%d) "
                "while unit %d is assigned that same tree on every one of "
                "those turns and alternates between %s and %s -- the idle "
                "on-target occupant that `compatible` cannot see"
                % (inc["occupant_unit_id"], inc["tree_type"],
                   tuple(inc["tree_cell"]), inc["occupant_wait_commands"],
                   inc["occupant_wait_first"], inc["occupant_wait_last"],
                   inc["mover_unit_id"], a, b)),
            "blocker_state": "WORKING",
            "blocker": {
                "unit": inc["occupant_unit_id"],
                "cell_at_entry": list(inc["tree_cell"]),
                "stats_raw": inc["occupant_stats"],
                "distinct_cells_in_window": 1,
                "distinct_cells_to_game_end": "UNKNOWN_NOT_COMMITTED",
                "wait_fraction_in_window": 1.0,
                "non_wait_verbs_in_window": [],
                "plant_on_cell_at_entry": [inc["tree_type"]],
                "orth_adjacent_to_oscillation_cells": True,
                "idle_by_analysis_criterion": True,
                "blocker_state_note": (
                    "recorded WORKING because the committed result states the "
                    "occupant chopped on turns %s and resumed CHOP on turn %d "
                    "-- the episode is bounded by the blocker's own work. Its "
                    "cell mobility over the rest of the game is not committed."
                    % (inc["occupant_chop_before"], inc["occupant_resume_chop"])),
            },
            "all_own_peers_at_entry": [],
            "geometry_stencil": "UNAVAILABLE_NO_COMMITTED_MAP",
            "classifier_version": "m3a-documentary/1",
        },
        "window": {
            "unit": inc["mover_unit_id"],
            "turn_start": inc["ping_pong_state_first"],
            "turn_end": inc["ping_pong_state_last"],
            "length_turns": inc["ping_pong_states"],
            "cells": [list(a), list(b)],
            "k": None,
            "commands": [
                {"turn": p["turn"],
                 "line": ";".join(p["commands_before_collision_resolution"])}
                for p in doc.get("resolver_probe", [])],
            "commands_note": (
                "PRE-collision-resolution commands as committed by the "
                "analyzer; not the resolved command stream."),
        },
        "world_state_at_entry": None,
        "world_state_absent_reason": (
            "the raw game and trajectory (%s, %s) are under data/external, "
            "which is git-ignored (.gitignore:15) and not present in this "
            "checkout. No world state is invented."
            % (g["raw_path"], g["trajectory_path"])),
        "initial_world_state": None,
        "static_map_rows": None,
        "detectors": {
            "counts": {},
            "d1_episodes": [],
            "p4_violations": [],
            "live_horizon": None,
            "turns_simulated": g["turns"],
            "note": ("D-1's predicate needs >= 7 alternating states; the "
                     "committed record states %d ping-pong states, so this "
                     "episode meets the D-1 length threshold, but the "
                     "detector was not run on it (no committed transcript)."
                     % inc["ping_pong_states"]),
        },
        "unresolved": [
            "Whether trace_detectors.detect_d1 would in fact report this "
            "episode: settled by committing "
            "data/external/elost-same-tree-occupancy-deadlock/"
            "trajectory-897556967.jsonl (sha256 %s) and running the detector "
            "over it." % g["trajectory_sha256"],
            "The literal world state at turn %d: settled by the same file."
            % inc["ping_pong_state_first"],
        ],
    })
    return out


# ---------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------

def harvest(games_path: Path, panel_cfg_path: Path, repo: Path):
    cfg = json.loads(panel_cfg_path.read_text())
    bot = Path(cfg["candidate"]["source"])
    bot_sha = hashlib.sha256(bot.read_bytes()).hexdigest()
    cfg_sha = hashlib.sha256(panel_cfg_path.read_bytes()).hexdigest()
    common = {
        "source": "fuzz-panel-floor",
        "panel_config_sha256": cfg_sha,
        "instrument_version": cfg["instrument_version"],
        "corpus_version": cfg["corpus_version"],
        "panel_seeds": cfg["seeds"],
        "panel_maps": cfg["maps"],
        "panel_turns": cfg["turns"],
        "panel_liveness_window": cfg["liveness_window"],
        "bot_source": str(bot.relative_to(repo)) if bot.is_relative_to(repo)
                      else str(bot),
        "bot_source_sha256": bot_sha,
        "note": ("candidate and parent are the SAME source (the arena parent "
                 "judged against itself): this is the panel FLOOR, not a "
                 "candidate regression."),
    }
    sits = []
    rows = [json.loads(line) for line in gzip.open(games_path, "rt")]
    for row in sorted(rows, key=lambda r: (r["map_id"], r["seat"])):
        art = row.get("artifacts") or {}
        if "candidate_transcript" not in art:
            continue
        has_d1 = bool(row["detector_counts"].get("D-1"))
        p4 = [v["detail"] for v in row["violations"]
              if v["property"] == "P4"]
        if not has_d1 and not p4:
            continue
        tr = td.build_trace(art["candidate_transcript"],
                            art["candidate_commands"])
        w, h, mrows = transcript_rows(art["candidate_transcript"])
        prov_base = dict(common)
        prov_base.update({
            "map_id": row["map_id"], "seat": row["seat"],
            "map_class": row["class"], "opponent_profile": row["profile"],
            "seed": row["seed"], "generation_attempt": row["attempt"],
            "map_width": w, "map_height": h,
        })
        if has_d1:
            for ep in td.detect_d1(tr)["episodes"]:
                prov = dict(prov_base)
                prov["_rows"] = list(mrows)
                sits.append(d1_situation(row, tr, ep, prov))
        else:
            for detail in p4:
                prov = dict(prov_base)
                prov["_rows"] = list(mrows)
                sits.append(p4_situation(row, tr, detail, prov))
    sits.extend(real_corpus_situations(repo))
    return sits


def dedupe(sits):
    """Group by mechanism + geometry; keep one representative per group.

    The key deliberately does NOT contain the map id: two episodes on
    different maps with the same mechanism and the same canonical local
    geometry are ONE situation with multiplicity 2, not two near-duplicates.
    """
    groups = {}
    for s in sits:
        key = "|".join([
            s["kind"],
            s["classification"]["mechanism"],
            s["classification"]["blocker_state"],
            s["classification"]["geometry_stencil"],
        ])
        groups.setdefault(key, []).append(s)

    def rank(s):
        return (-s["window"]["length_turns"], s["provenance"].get("map_id", ""),
                s["provenance"].get("seat", 0), s["window"]["unit"] or 0,
                s["window"]["turn_start"])

    out = []
    for key in sorted(groups):
        members = sorted(groups[key], key=rank)
        rep = members[0]
        rep["multiplicity"] = {
            "episodes": len(members),
            "dedupe_key_sha256": hashlib.sha256(
                key.encode("utf-8")).hexdigest(),
            "members": [{
                "source": m["provenance"]["source"],
                "map_id": m["provenance"].get("map_id"),
                "game_id": m["provenance"].get("game_id"),
                "seat": m["provenance"].get("seat"),
                "unit": m["window"]["unit"],
                "turn_start": m["window"]["turn_start"],
                "turn_end": m["window"]["turn_end"],
                "length_turns": m["window"]["length_turns"],
            } for m in members],
            "representative_rule": (
                "longest window; ties broken by (map_id, seat, unit, "
                "turn_start)"),
        }
        out.append(rep)
    out.sort(key=lambda s: (s["kind"], s["classification"]["mechanism"],
                            -s["multiplicity"]["episodes"],
                            -s["window"]["length_turns"]))
    return out


def write_library(sits, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.json"):
        old.unlink()
    entries = []
    for i, s in enumerate(sits, 1):
        sid = "OSC-%03d" % i
        s["schema"] = SCHEMA_SITUATION
        s["id"] = sid
        s.pop("content_sha256", None)
        digest = payload_sha256(s)
        s["content_sha256"] = digest
        path = out_dir / ("%s.json" % sid)
        path.write_text(json.dumps(s, indent=1, sort_keys=True) + "\n")
        entries.append({
            "id": sid,
            "file": path.name,
            "content_sha256": digest,
            "kind": s["kind"],
            "completeness": s["completeness"],
            "mechanism": s["classification"]["mechanism"],
            "blocker_state": s["classification"]["blocker_state"],
            "multiplicity": s["multiplicity"]["episodes"],
            "window_turns": [s["window"]["turn_start"], s["window"]["turn_end"]],
            "length_turns": s["window"]["length_turns"],
            "origin": {
                "source": s["provenance"]["source"],
                "map_id": s["provenance"].get("map_id"),
                "game_id": s["provenance"].get("game_id"),
                "seat": s["provenance"].get("seat"),
                "unit": s["window"]["unit"],
            },
        })
    index = {
        "schema": SCHEMA_INDEX,
        "item": "M3a -- oscillation situation library (enumerate and freeze)",
        "scope_note": (
            "M3a freezes the situations ONLY. No judgement of the best action "
            "is recorded anywhere in this library: that is M3b, which is a "
            "separate item blocked on the Decision Packet, and deriving an "
            "answer here from the same scorer that produced the oscillation "
            "would poison it with circularity."),
        "situation_count": len(entries),
        "episode_count": sum(e["multiplicity"] for e in entries),
        "mechanism_histogram": _hist(entries, "mechanism"),
        "blocker_state_histogram": _hist(entries, "blocker_state"),
        "kind_histogram": _hist(entries, "kind"),
        "completeness_histogram": _hist(entries, "completeness"),
        "situations": entries,
    }
    index["library_sha256"] = library_sha256(entries)
    (out_dir / "index.json").write_text(
        json.dumps(index, indent=1, sort_keys=True) + "\n")
    return index


def _hist(entries, field):
    out = {}
    for e in entries:
        out[e[field]] = out.get(e[field], 0) + 1
    return dict(sorted(out.items()))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--games", required=True)
    ap.add_argument("--panel-config", required=True)
    ap.add_argument("--out", default=str(HERE / "oscillation-library"))
    ap.add_argument("--repo", default=str(REPO))
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()
    sits = harvest(Path(args.games), Path(args.panel_config).resolve(), repo)
    raw = len(sits)
    sits = dedupe(sits)
    index = write_library(sits, Path(args.out))
    print("harvested %d episodes -> %d frozen situations (library_sha256 %s)"
          % (raw, index["situation_count"], index["library_sha256"][:16]))
    print("mechanisms:", index["mechanism_histogram"])
    print("blocker:   ", index["blocker_state_histogram"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
