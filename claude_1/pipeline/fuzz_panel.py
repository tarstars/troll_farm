#!/usr/bin/env python3
"""fuzz_panel — randomized closed-loop property panel (pipeline final gate).

Motivation (round-4/5 pattern analysis): five hand-constructed scenario
suites in a row were green while broader panels found real defects — the
hand-picked geometries never sampled the state regions where the defects
live (ledger class UNSAMPLED_STATE_SPACE). This tool samples game states
mechanically: a seeded map generator produces varied geometries across
declared classes (open fields, choke/articulation corridors — the round-5
killer class — single/multi-door tents, water-adjacent diagonal cells,
orchard-eligible layouts, dense/sparse forests, iron present/absent), runs
REAL closed-loop games of the candidate and the parent on identical
map+opponent, and asserts machine-checkable properties on every candidate
game:

  P1  detectors D-1..D-9 (trace_detectors.run_all, amended D-8 semantics)
      must report zero episodes.  RAW/ABSOLUTE (owner ruling 2026-08-06):
      EVERY detector episode blocks, inherited-from-parent or not, on every
      map.  The two former parent-comparison exemptions are REMOVED — there
      is no D-1 inherited-report-only downgrade and no D-9
      parent-differential gate (the round-6 ROOT-A exemption is retired).
      The parent run is still computed (for the P3 inertness check and the
      diagnostic report) but never exempts a candidate detector episode.
      trace_detectors is unmodified (the base-detector questions go to the
      integrator).
  P2  R-5 class: no full-cargo two-cell alternation >= 6 turns without a
      cargo change (regression_tests.r5_two_worker_full_cargo_banking
      alternation clause).  The R-5 bounded-banking-horizon clause is
      surfaced as a report-tier flag, not a block.
  P3  on orchard-eligible seat views (mirror of SecureOrchardBot's
      initialize gates) the candidate's command stream must byte-equal the
      parent's (dormancy inertness).
  P4  liveness floor: RAW (owner ruling 2026-08-06) — some progress (own
      inventory or own-unit cargo change) in every rolling 60-turn window,
      with NO parent-relative exemption.  The former "unless the parent also
      makes no progress in the same window" clause is removed.  ABSOLUTE
      terminal-state calibration (repair #2): the obligation runs only while
      the referee world still offers a resource action — an own unit
      carrying something to bank/plant, or a plant standing on a cell an own
      unit can walk to (harvest/chop).  Each stall window is trimmed to that
      live prefix and blocks iff >= 60 LIVE turns remain stalled, so a stall
      beginning after the world is exhausted is excused while any stall over
      a non-terminal world — mid-game or running to the sim horizon — blocks.
  P0  protocol liveness: the candidate must emit one command line per turn
      for the whole game (a crash/early-close blocks).

Report-tier findings (flagged, never blocking): margin collapse on
banana-activated maps (candidate margin < parent margin - threshold) and
R-5 horizon misses.  (Under the raw gate there are no inherited-parent D-1
or D-9 report-tier downgrades — those episodes block.)

CLI:
  python3 fuzz_panel.py --config <json> --report <md> --json <out.json>
                        [--save-failures <dir>]
Exit codes: 0 = CLEAR, 1 = BLOCK, 2 = tool/config error.

Determinism: every random draw derives from the config-declared seed list
(seed -> per-map PRNG stream; regeneration on invalid geometry advances the
stream deterministically).  No time- or os-based randomness.  Optional
multiprocessing preserves per-game determinism; results are ordered by map
id before the verdict.  Wall time is measured for reporting only.

Reuses (imports, never modifies): the make_banana_traces referee core
(command application, growth, dynamic opponents), trace_detectors D-1..D-9,
regression_tests' R-5 machinery and closed-loop binary runner, and
semantic_harness's map/protocol/compile helpers.  FuzzReferee below is the
adapter that binds the referee to generated geometry (instance walkable set /
tent / water / iron) without editing the original module.

COMMAND EXECUTION (revision r3, 2026-08-10, corpus c4).  The referee no
longer contains a second, informal command language.  `FuzzReferee.apply`

  1. PARSES the complete line before any mutation
     (`parse_commands`, a pure classmethod mirroring
     `engine.rs::parse_cmds` 683-748, including the per-unit `used` rule at
     717-720 that keeps only the FIRST non-TRAIN command for a unit while
     retaining every TRAIN in parse order);
  2. RETAINS every trust-boundary error -- an unimplemented verb or a
     malformed body is a structured record carrying the raw bytes and the
     turn, the row stays in the denominator, and the aggregate becomes
     GATE_UNREADY (exit 2) with the report and JSON packet still published;
  3. EXECUTES the eight engine phases in engine order,
     MOVE -> HARVEST -> PLANT -> CHOP -> PICK -> TRAIN -> DROP -> MINE
     (`engine.rs::step` 755-806), one applier per phase, each written from
     and citing `rust/src/game/engine.rs`.

Nothing is delegated to `make_banana_traces.Referee.apply` any more.  That
inherited dispatcher was a sequential if/elif fragment executor with a silent
fall-through bottom: TRAIN and MINE fell out of it for the whole life of the
panel, so the panel measured properties on a world that never happened and
its two most pathological games (m040 seats 0/1, which emitted TRAIN on
166/200 and 182/200 turns because the worker count never rose) scored CLEAN.

History of the repair: r1 implemented TRAIN but copied `MoisanBot::can_train`
(`yamo_orchard_live.rs:836`, `n >= 2 || TOTAL_TURNS - view.turn <= 20`) into
referee law -- that is one bot's self-restraint and `engine.rs::apply_train`
enforces neither.  r2 removed it but still executed raw fragments in textual
order with only TRAIN repositioned.  r3 replaces the executor.  Per-rule line
citations: referee-train-repair-r3-2026-08-10.md.

Conformance is checked DIFFERENTIALLY, not by assertion alone: the self-tests
pull `rust/src/game/engine.rs` and `state.rs` byte-for-byte into a throwaway
crate with `#[path]`, run `engine::step` on the same state and command line,
and compare the complete post-turn state (both inventories, every unit field,
next_id, plants/growth, score, turn).  `sim/engine.py` is a second,
independently authored leg.  Neither shares code with this file.

The instrument/corpus version pair (INSTRUMENT_VERSION / CORPUS_VERSION) must
be declared in the RAW config -- a missing declaration fails closed rather
than inheriting the running panel's identity -- and every report and JSON
packet echoes both plus the referee and engine.rs sha256.

Stdlib only (Python 3.12); rustc via semantic_harness (PATH + ~/.cargo/bin).
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import multiprocessing
import random
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BR2 = (HERE.parent / "banana-restoration-r2").resolve()
if str(BR2) not in sys.path:
    sys.path.insert(0, str(BR2))

import semantic_harness as sh        # noqa: E402  (compiler + map helpers)
import trace_detectors as td         # noqa: E402  (D-1..D-9)
import make_banana_traces as mbt     # noqa: E402  (referee core)
import regression_tests as rt        # noqa: E402  (R-5 + binary runner)

EXIT_CLEAR, EXIT_BLOCK, EXIT_ERROR = 0, 1, 2

KINDS = ("PLUM", "LEMON", "APPLE", "BANANA")
ORTH = ((0, 1), (1, 0), (0, -1), (-1, 0))
DIAG = ((1, 1), (1, -1), (-1, 1), (-1, -1))
PLUM, LEMON, APPLE, BANANA, IRON, WOOD = 0, 1, 2, 3, 4, 5
BIG = 10_000

# --- corpus / instrument versioning (requirement 5, 2026-08-09) -------------
# Implementing TRAIN changes the referee and therefore every game the panel
# produces, so results are not comparable across instrument versions.  Both
# strings are declared in the config, asserted by the self-tests and echoed in
# every report and JSON payload.
# r4 (2026-08-11): the opponent is no longer a direct post-phase simulator
# (review B2), parent command failure is fail-closed (B3) and the durable
# error packet keeps verbatim bytes (B4).  All three change the instrument's
# trust envelope, so c4 results cannot enter calibration (B6).
INSTRUMENT_VERSION = "fuzz-panel/5-two-player-phase-merged-referee"
CORPUS_VERSION = "c5-two-player-phase-merged-2026-08-11"

# --- run identity (review B5) ----------------------------------------------
# `floor`     : the parent judged against ITSELF -- the instrument's own
#               baseline.  candidate.source and parent.source must be the
#               same bytes.
# `candidate` : a candidate judged against the parent.  The two sources must
#               differ.
# Declared in the RAW config, machine-checked in load_config, and echoed into
# the report, the JSON packet and every row.  A floor number quoted from a
# candidate config is therefore impossible, not merely discouraged.
RUN_IDENTITY_FLOOR = "floor"
RUN_IDENTITY_CANDIDATE = "candidate"
RUN_IDENTITIES = (RUN_IDENTITY_FLOOR, RUN_IDENTITY_CANDIDATE)

# --- authoritative engine constants (rust/src/game/engine.rs) --------------
# engine.rs:6-15
ITEM_INDEX = {"PLUM": 0, "LEMON": 1, "APPLE": 2, "BANANA": 3,
              "IRON": 4, "WOOD": 5}
PLANTABLE_KINDS = ("PLUM", "LEMON", "APPLE", "BANANA")
MAX_SIZE, MAX_FRUITS, WOOD_POINTS = 4, 3, 4
# engine.rs:29-37 plant_cooldown / 39-47 water_boost / 53-60 tree_health_params
PLANT_COOLDOWN = {"PLUM": 8, "LEMON": 8, "APPLE": 9, "BANANA": 6}
WATER_BOOST = {"PLUM": 5, "LEMON": 5, "APPLE": 7, "BANANA": 2}
TREE_HEALTH_BASE = {"PLUM": 4, "LEMON": 4, "APPLE": 8, "BANANA": 2}
TREE_HEALTH_SLOPE = {"PLUM": 2, "LEMON": 2, "APPLE": 3, "BANANA": 1}

# engine.rs:752-754 (`step` doc comment) and engine.rs:762-801 (the calls).
# This is the COMPLETE turn order, not just TRAIN's position: two command
# lines carrying the same command multiset in different textual order must
# produce the same post-state (frozen contract C4).
PHASE_ORDER = ("MOVE", "HARVEST", "PLANT", "CHOP", "PICK", "TRAIN",
               "DROP", "MINE")

# --- trust-boundary error kinds (frozen contract C2 / C3) ------------------
# DELIBERATE DIVERGENCE FROM engine.rs.  `engine.rs::parse_cmds` (683-748) is
# permissive: it accepts `TRAIN` with >= 5 tokens, coerces unparsable talents
# with `parse().unwrap_or(0)` and drops short commands silently.  That is
# right for a referee reading its own trusted replays and wrong for an
# instrument reading a candidate bot's stdout: a malformed emitted command is
# an instrument/protocol error whose RAW BYTES are the evidence.  A
# fabricated command also fabricates state -- coercing a non-integer movement
# talent to 0 spawns a speed-0 worker on the non-walkable shack, which
# `engine.rs::next_cell` (99-144) can never move.
ERROR_UNSUPPORTED_VERB = "unsupported_verb"
ERROR_MALFORMED = "malformed_command"
EXECUTION_OK = "ok"
# REVIEW B4.  There is NO cap on the retained error stream any more.  The r3
# referee kept at most 50 errors and stripped every fragment before recording
# its `raw` field, so leading/trailing bytes, empty-fragment placement and
# fragment offsets were lost and the full stream survived only in
# `artifacts`, which run_panel drops from the JSON packet: a GATE_UNREADY row
# could not reconstruct every offending raw command from durable evidence.
# Every error now carries the verbatim fragment, its exact [start, end)
# character span, the normalized parse, and the sha256/length of the stdout
# line it came from; the offending lines themselves are retained verbatim.
# `REPORT_ERROR_ROWS` bounds the human-readable markdown TABLE only.
REPORT_ERROR_ROWS = 50

# --- authoritative engine constants ----------------------------------------
# THE AUTHORITY IS rust/src/game/engine.rs.  Deliberately no WORKER_CAP and no
# TRAIN_GUARD_TURNS: `MoisanBot::can_train` (yamo_orchard_live.rs:836
# `if n >= 2 || TOTAL_TURNS - view.turn <= 20 { return false; }`) is one bot's
# SELF-RESTRAINT, and engine.rs::apply_train (525-568) enforces neither.  A
# referee that encodes them forbids what the engine permits.  Line citations
# are reproduced in claude_1/pipeline/referee-train-repair-r2-2026-08-09.md.

MAP_CLASSES = ("open_field", "choke_corridor", "single_door_tent",
               "multi_door", "water_diagonal", "orchard_eligible",
               "forest_dense", "forest_sparse")
OPP_PROFILES = ("idle", "harvester", "chopper_aggressor")

# NOTE (review B7): `instrument_version` / `corpus_version` are deliberately
# ABSENT here.  While they were members of DEFAULTS, `cfg.update(raw)` re-
# supplied them for any config that omitted them, so the equality check in
# load_config could never fail and a config with no declared corpus silently
# inherited the current identity.  They must now be present in the RAW JSON.
DEFAULTS = {
    "maps": 120,
    "turns": 200,
    "processes": 0,               # 0 => min(8, cpu_count)
    "liveness_window": 60,
    "margin_collapse_threshold": 100,
    "max_generation_attempts": 64,
    "class_mix": {
        "choke_corridor": 0.25, "open_field": 0.15, "single_door_tent": 0.10,
        "multi_door": 0.10, "water_diagonal": 0.15, "orchard_eligible": 0.10,
        "forest_dense": 0.08, "forest_sparse": 0.07,
    },
    "opponent_mix": {"idle": 0.30, "harvester": 0.40,
                     "chopper_aggressor": 0.30},
}


class PanelError(Exception):
    """Config / environment / generation error -> exit 2."""


class UnsupportedCommand(PanelError):
    """GATE_UNREADY / unsupported_command.

    RETAINED, NO LONGER RAISED BY THE REFEREE (revision r3, review B6/B7).
    Raising this out of a worker aborted the aggregate before any row was
    written, so the affected row vanished from the denominator -- the packet
    could not distinguish "every command executed" from "the process ended
    before publishing evidence".  An unsupported verb is now a retained
    `unsupported_verb` error on the row, the report and the JSON packet are
    still published with every affected row, and the process still exits 2.
    The class stays for the mutation control (`MUTATIONS` M7) and for callers
    that want to fail hard.

    Historical note:

    Raised by the referee's exhaustive command dispatcher when a bot emits a
    verb the referee does not implement.  A referee that silently discards a
    verb it cannot apply reports a world that never happened, and every
    property built on that world (detectors, liveness, margins) is measuring
    a fiction: the two m040 games below emitted TRAIN on 166/200 and 182/200
    turns and scored CLEAN.  The gate therefore refuses to render ANY verdict
    rather than render an unsound one.

    Deliberately a PanelError: run_pair converts candidate crashes into P0
    violations, but a PanelError propagates all the way to main(), so a
    single unsupported verb on a single turn of a single game terminates the
    whole run.  Single-argument (message-only) so it survives the
    multiprocessing pool's pickling of worker exceptions.
    """


def unsupported_command(verb: str, raw: str, turn: int) -> UnsupportedCommand:
    return UnsupportedCommand(unsupported_reason(verb, raw, turn))


def unsupported_reason(verb: str, raw: str, turn: int) -> str:
    return ("GATE_UNREADY / unsupported_command: the referee implements no "
            "handler for verb %r (turn %d, command %r); the panel cannot "
            "render a verdict on a world it cannot simulate. Implement the "
            "verb in FuzzReferee.VERB_HANDLERS (with conformance tests "
            "against rust/src/game/engine.rs, the sole authority) or "
            "withdraw it from the corpus."
            % (verb, turn, raw))


class _Malformed(Exception):
    """Internal: a fragment that fails the trust boundary (contract C3)."""


def command_error(kind: str, verb: str, raw: str, turn: int,
                  reason: str, span=None, normalized=None, line=None) -> dict:
    """One RETAINED, JSON-serialisable trust-boundary error.

    Contract §8: 'A row with incomplete command execution is counted in the
    denominator and makes the aggregate gate unready. It is never silently
    dropped and never reported as a clean game.'  The raw bytes are the
    evidence, so they are carried verbatim.

    REVIEW B4.  `raw` is now the EXACT character slice of the offending
    fragment -- whitespace included -- and `span` is its `[start, end)` offset
    pair into the stdout line, so `line[start:end] == raw` byte for byte.
    `normalized` carries the whitespace-collapsed form separately (it is what
    the parser tokenized), and `line_sha256` / `line_length` tie the error to
    the exact line retained in `error_lines`."""
    err = {"kind": kind, "verb": verb, "raw": raw, "turn": int(turn),
           "reason": reason,
           "normalized": " ".join(raw.split()) if normalized is None
                         else normalized,
           "span": [int(span[0]), int(span[1])] if span is not None else None}
    if line is not None:
        err["line_sha256"] = hashlib.sha256(line.encode("utf-8")).hexdigest()
        err["line_length"] = len(line)
    else:
        err["line_sha256"] = None
        err["line_length"] = None
    return err


_HASH_CACHE: dict = {}


def referee_sha256() -> str:
    """sha256 of THIS file -- the pinned referee implementation hash the
    frozen contract (§8) requires in every result packet."""
    if "referee" not in _HASH_CACHE:
        _HASH_CACHE["referee"] = sha256_path(Path(__file__).resolve())
    return _HASH_CACHE["referee"]


def engine_sha256() -> str:
    """sha256 of the AUTHORITY, rust/src/game/engine.rs.  A referee result
    that cannot name the engine revision it conforms to is not evidence."""
    if "engine" not in _HASH_CACHE:
        path = HERE.parent.parent / "rust" / "src" / "game" / "engine.rs"
        _HASH_CACHE["engine"] = (sha256_path(path) if path.exists()
                                 else "unavailable")
    return _HASH_CACHE["engine"]


def provenance(run_identity=None) -> dict:
    return {"instrument_version": INSTRUMENT_VERSION,
            "corpus_version": CORPUS_VERSION,
            "referee_sha256": referee_sha256(),
            "engine_sha256": engine_sha256(),
            "engine_authority": "rust/src/game/engine.rs",
            "run_identity": run_identity,
            "phase_order": list(PHASE_ORDER)}


def row_execution_failed(row) -> bool:
    """REVIEW B3.  Either seat's command execution failing makes the row
    instrument-invalid.  r3 consumed only `execution_status` (the candidate),
    so a malformed or unsupported PARENT command left the aggregate at CLEAR
    or BLOCK while P3 and every diagnostic comparison consumed an invalid
    parent trace."""
    return (row.get("execution_status", EXECUTION_OK) != EXECUTION_OK
            or row.get("parent_execution_status",
                       EXECUTION_OK) != EXECUTION_OK)


def aggregate_verdict(rows) -> str:
    """GATE_UNREADY dominates: a corpus containing even one row whose command
    execution was incomplete -- IN EITHER SEAT -- cannot render BLOCK or
    CLEAR, because the properties of the other rows were measured by the same
    instrument."""
    if any(row_execution_failed(r) for r in rows):
        return "GATE_UNREADY"
    return "BLOCK" if any(r.get("block") for r in rows) else "CLEAR"


def training_cost(n: int, talents) -> list:
    """Mirror of engine.rs::training_cost (rust/src/game/engine.rs:514-522).

        let mut cost = [0i32; 6];
        cost[PLUM]  = n + ms   * ms;      // engine.rs:517
        cost[LEMON] = n + cc   * cc;      // engine.rs:518
        cost[APPLE] = n + hp   * hp;      // engine.rs:519
        cost[IRON]  = n + chop * chop;    // engine.rs:520

    where n is the CURRENT own-unit count (engine.rs:527).  BANANA and WOOD
    are never written, so their cost entries stay 0: they sit on the `pay`
    slice (engine.rs:532-536) but the check is `inv[i] < 0` and the deduction
    is `-= 0`."""
    ms, cc, hp, chop = talents
    cost = [0] * 6
    cost[PLUM] = n + ms * ms
    cost[LEMON] = n + cc * cc
    cost[APPLE] = n + hp * hp
    cost[IRON] = n + chop * chop
    return cost


def score(inv) -> int:
    """Mirror of rules::score (research-banana-r2.rs game::rules::score):
    1 point per banked fruit (PLUM/LEMON/APPLE/BANANA), WOOD_POINTS=4 per
    wood, iron worthless."""
    return inv[0] + inv[1] + inv[2] + inv[3] + 4 * inv[5]


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Deterministic mix scheduling
# ---------------------------------------------------------------------------

def schedule(mix: dict, n: int) -> list:
    """Largest-deficit apportionment of a weight mix over n slots.
    Deterministic: sorted keys, deficit-then-name tie-break."""
    items = sorted((k, float(w)) for k, w in mix.items() if w > 0)
    if not items or n <= 0:
        raise PanelError("empty mix or non-positive slot count")
    total = sum(w for _, w in items)
    assigned = {k: 0 for k, _ in items}
    out = []
    for i in range(1, n + 1):
        best = max(items, key=lambda kv: (kv[1] * i / total
                                          - assigned[kv[0]], kv[0]))
        assigned[best[0]] += 1
        out.append(best[0])
    return out


# ---------------------------------------------------------------------------
# Map generation
# ---------------------------------------------------------------------------

def _blank(w, h):
    return [["#"] * w for _ in range(h)]


def _carve(grid, cells):
    for (x, y) in cells:
        grid[y][x] = "."


def _rows(grid):
    return ["".join(r) for r in grid]


def _in(w, h, cell):
    return 0 <= cell[0] < w and 0 <= cell[1] < h


def _manhattan(a, b):
    """engine.rs::manhattan (94-96)."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _orth_neighbors(cell):
    x, y = cell
    return [(x + dx, y + dy) for dx, dy in ORTH]


def median(values):
    """Mirror of SecureOrchardBot::median (sorted; even count -> mean of the
    two middles)."""
    vs = sorted(values)
    n = len(vs)
    if n == 0:
        return 0.0
    if n % 2 == 1:
        return float(vs[n // 2])
    return (vs[n // 2 - 1] + vs[n // 2]) / 2.0


def orchard_eligible_view(rows, plants) -> bool:
    """Mirror of the candidate's SecureOrchardBot::initialize gates
    (research-banana-r2.rs): >= 2 own doors; at least one live natural
    plant; all naturals reachable from home doors with median home-door
    distance >= 8; and a free own door that is water-adjacent with
    enemy-door BFS distance >= 11."""
    geo = sh.parse_rows(tuple(rows))
    if 0 not in geo["shacks"] or 1 not in geo["shacks"]:
        return False
    walk = geo["walkable"]
    water = geo["water"]
    doors = sorted(c for c in _orth_neighbors(geo["shacks"][0]) if c in walk)
    if len(doors) < 2:
        return False
    natural = [(p[1], p[2]) for p in plants if p[4] > 0]  # health > 0
    if not natural:
        return False
    home = sh.bfs(walk, doors)
    returns = [home.get(c) for c in natural]
    if any(r is None for r in returns) or median(returns) < 8.0:
        return False
    enemy_doors = [c for c in _orth_neighbors(geo["shacks"][1]) if c in walk]
    edist = sh.bfs(walk, enemy_doors)
    plant_cells = {(p[1], p[2]) for p in plants}
    for door in doors:
        if door in plant_cells:
            continue
        if not any(w in water for w in _orth_neighbors(door)):
            continue
        if edist.get(door, BIG) >= 11:
            return True
    return False


def _mk_plant(rng, cell, kind=None, size=None, fruits=None, cd=None,
              health=None):
    kind = kind or rng.choice(KINDS)
    size = size if size is not None else rng.randint(1, 4)
    full = mbt.HEALTH_BASE[kind] + mbt.HEALTH_SLOPE[kind] * size
    if health is None:
        health = full if rng.random() < 0.8 else rng.randint(1, full)
    if fruits is None:
        fruits = rng.randint(0, 3) if size == 4 else 0
    if cd is None:
        cd = rng.randint(0, mbt.COOLDOWN[kind])
    return [kind, cell[0], cell[1], size, health, fruits, cd]


def _geometry(cls, rng):
    """Class geometry: returns dict(w, h, grid, tents=[A, B],
    forced_plants, meta) or None when the draw is degenerate."""
    forced = []
    meta = {}
    if cls == "choke_corridor":
        w, h = rng.randint(11, 14), rng.randint(4, 8)
        cy = rng.randint(2, h - 2) if h > 4 else 2
        grid = _blank(w, h)
        _carve(grid, [(x, cy) for x in range(1, w - 1)])
        ta = (1, cy - 1)
        _carve(grid, [ta, (2, cy - 1)])          # tent cell + orth door
        if rng.random() < 0.5:
            tb = (w - 2, cy - 1)
            _carve(grid, [tb, (w - 3, cy - 1)])
        else:
            tb = (w - 1, cy)
        # the diagonal ring cell (2, cy) is the single articulation cell of
        # every east->door banking route (the round-5 killer geometry)
        if rng.random() < 0.6:
            forced.append(_mk_plant(
                rng, (2, cy), kind="BANANA", size=4,
                fruits=rng.choice([0, 0, 1]), cd=rng.randint(30, 60),
                health=6))
        meta["second_worker_bias"] = 0.75
        meta["full_wood_bias"] = 0.6
        meta["plant_range"] = (0, 2)
    elif cls == "orchard_eligible":
        w, h = 14, rng.randint(4, 8)
        ay = rng.randint(1, h - 2)
        grid = _blank(w, h)
        _carve(grid, [(x, y) for x in range(w) for y in range(h)])
        ta, tb = (0, ay), (13, rng.randint(1, h - 2))
        if ay - 1 >= 0:
            grid[ay - 1][0] = "#"
            grid[ay - 1][1] = "~"               # water on the door's north
        else:
            return None
        for _ in range(rng.randint(0, 6)):      # obstacles never shorten
            grid[rng.randint(0, h - 1)][rng.randint(4, 9)] = "#"
        used = set()
        for _ in range(rng.randint(1, 3)):      # far naturals: median >= 8
            c = (rng.randint(9, 12), rng.randint(0, h - 1))
            if c in used or c in (ta, tb) or grid[c[1]][c[0]] != ".":
                continue
            used.add(c)
            forced.append(_mk_plant(rng, c, size=4,
                                    fruits=rng.randint(1, 3)))
        if not forced:
            return None
        meta["plant_range"] = (0, 0)
        meta["extra_plant_min_x"] = 9
    else:
        w, h = rng.randint(10, 14), rng.randint(5, 8)
        grid = _blank(w, h)
        _carve(grid, [(x, y) for x in range(w) for y in range(h)])
        ta = (rng.randint(1, 2), rng.randint(1, h - 2))
        tb = (w - 1 - rng.randint(1, 2), rng.randint(1, h - 2))
        keep = {ta, tb} | set(_orth_neighbors(ta)) | set(_orth_neighbors(tb))
        for _ in range(rng.randint(0, (w * h) // 10)):
            c = (rng.randrange(w), rng.randrange(h))
            if c not in keep:
                grid[c[1]][c[0]] = "#"
        if cls == "single_door_tent" or cls == "multi_door":
            doors = [c for c in _orth_neighbors(ta) if _in(w, h, c)]
            n_keep = 1 if cls == "single_door_tent" else rng.randint(2, 4)
            kept = doors[:0]
            order = sorted(doors)
            rng.shuffle(order)
            kept = set(order[:n_keep])
            for c in doors:
                if c not in kept:
                    grid[c[1]][c[0]] = "#"
            for dx, dy in DIAG:                 # tent pocket walls
                c = (ta[0] + dx, ta[1] + dy)
                if _in(w, h, c) and c not in kept and rng.random() < 0.7:
                    grid[c[1]][c[0]] = "#"
            meta["plant_range"] = (1, 4)
        elif cls == "water_diagonal":
            placed = False
            for dx, dy in rng.sample(DIAG, 4):
                d = (ta[0] + dx, ta[1] + dy)
                wc = ((ta[0] + 2 * dx, ta[1] + dy) if rng.random() < 0.5
                      else (ta[0] + dx, ta[1] + 2 * dy))
                if not (_in(w, h, d) and _in(w, h, wc)):
                    continue
                if grid[d[1]][d[0]] != "." or grid[wc[1]][wc[0]] != ".":
                    continue
                # keep water OFF door-adjacency: never orchard-eligible by
                # this cell (banana-eligible wet diagonal instead)
                if any(n in _orth_neighbors(ta) for n in _orth_neighbors(wc)):
                    continue
                grid[wc[1]][wc[0]] = "~"
                placed = True
                break
            if not placed:
                return None
            meta["plant_range"] = (1, 4)
            meta["banana_bank_min"] = 1
        elif cls == "forest_dense":
            meta["plant_range"] = (8, 14)
        elif cls == "forest_sparse":
            meta["plant_range"] = (1, 3)
        else:                                   # open_field
            meta["plant_range"] = (0, 5)
    # iron present/absent (all classes): '+' replaces a wall or field cell
    if rng.random() < 0.3:
        for _ in range(rng.randint(1, 2)):
            c = (rng.randrange(w), rng.randrange(h))
            if c not in (ta, tb) and grid[c[1]][c[0]] in "#.":
                grid[c[1]][c[0]] = "+"
    grid[ta[1]][ta[0]] = "."
    grid[tb[1]][tb[0]] = "."
    return {"w": w, "h": h, "grid": grid, "tents": [list(ta), list(tb)],
            "forced_plants": forced, "meta": meta}


def _roster_template(cls, profile, rng, meta):
    second = None
    if rng.random() < meta.get("second_worker_bias", 0.5):
        second = {
            "speed": rng.choice([1, 1, 1, 2]),
            "cap": rng.choice([1, 2, 2, 3]),
            "harvest": rng.choice([0, 1, 1]),
            "chop": rng.choice([0, 1, 1]),
            "full_wood": rng.random() < meta.get("full_wood_bias", 0.25),
            "frac": round(rng.random(), 4),
        }
    opp = []
    n_opp = 1 if profile == "idle" else rng.choice([1, 1, 2])
    for _ in range(n_opp):
        if profile == "harvester":
            opp.append({"speed": rng.choice([1, 2]), "cap": rng.choice([2, 3]),
                        "harvest": 1, "chop": 0})
        elif profile == "chopper_aggressor":
            opp.append({"speed": 1, "cap": rng.choice([2, 3]),
                        "harvest": 0, "chop": rng.choice([1, 2])})
        else:
            opp.append({"speed": 1, "cap": 2, "harvest": 0, "chop": 0})
    return {"second": second, "opp": opp}


def _inventory(cls, rng, meta):
    inv = [0] * 6
    inv[3] = max(meta.get("banana_bank_min", 0),
                 rng.choice([0, 1, 1, 2]))
    for slot in (0, 1, 2):
        if rng.random() < 0.15:
            inv[slot] = 1
    return inv


def build_skeleton(map_index, cls, profile, cfg):
    """Deterministic skeleton for map #map_index: geometry + plants +
    inventory + roster template. Regenerates on invalid draws by advancing
    the seed stream (attempt counter)."""
    seeds = cfg["seeds"]
    base = seeds[map_index % len(seeds)]
    for attempt in range(cfg["max_generation_attempts"]):
        rng = random.Random(base * 1_000_003 + map_index * 8191
                            + attempt * 7919)
        geo = _geometry(cls, rng)
        if geo is None:
            continue
        rows_plain = _rows(geo["grid"])
        parsed = sh.parse_rows(tuple(rows_plain))
        walk = parsed["walkable"]
        ta = tuple(geo["tents"][0])
        tb = tuple(geo["tents"][1])
        doors_a = sorted(c for c in _orth_neighbors(ta) if c in walk)
        doors_b = sorted(c for c in _orth_neighbors(tb) if c in walk)
        if not doors_a or not doors_b:
            continue
        reach = sh.bfs(walk - {ta, tb}, doors_a)
        if doors_b[0] not in reach:
            continue
        plants = list(geo["forced_plants"])
        taken = {(p[1], p[2]) for p in plants}
        if any(c not in reach and c not in (ta, tb) for c in taken):
            continue
        lo, hi = geo["meta"].get("plant_range", (0, 4))
        min_x = geo["meta"].get("extra_plant_min_x", 0)
        candidates = sorted(c for c in reach
                            if c not in taken and c not in (ta, tb)
                            and c[0] >= min_x)
        n_extra = min(rng.randint(lo, hi), len(candidates))
        for c in (rng.sample(candidates, n_extra) if n_extra else []):
            plants.append(_mk_plant(rng, c))
            taken.add(c)
        skel = {
            "id": "m%03d" % map_index,
            "class": cls,
            "profile": profile,
            "seed": base,
            "attempt": attempt,
            "rows_plain": rows_plain,
            "tents": [list(ta), list(tb)],
            "plants": sorted(plants, key=lambda p: (p[1], p[2])),
            "inventory": _inventory(cls, rng, geo["meta"]),
            "roster": _roster_template(cls, profile, rng, geo["meta"]),
        }
        specs = [materialize(skel, 0), materialize(skel, 1)]
        if any(s is None for s in specs):
            continue
        if cls == "orchard_eligible" and not specs[0]["orchard_eligible"]:
            continue
        return skel, specs
    raise PanelError(
        "map %d (%s): no valid geometry within %d attempts"
        % (map_index, cls, cfg["max_generation_attempts"]))


def materialize(skel, seat):
    """Pure seat-variant instantiation: '0' at the seat's tent, own units
    placed relative to it, opponent units at the other tent's doors."""
    ta = tuple(skel["tents"][seat])
    tb = tuple(skel["tents"][1 - seat])
    rows = []
    for y, row in enumerate(skel["rows_plain"]):
        chars = list(row)
        if y == ta[1]:
            chars[ta[0]] = "0"
        if y == tb[1]:
            chars[tb[0]] = "1"
        rows.append("".join(chars))
    geo = sh.parse_rows(tuple(rows))
    walk = geo["walkable"]
    own_doors = sorted(c for c in _orth_neighbors(ta) if c in walk)
    opp_doors = sorted(c for c in _orth_neighbors(tb) if c in walk)
    if not own_doors or not opp_doors:
        return None
    reach = sh.bfs(walk, own_doors)
    if opp_doors[0] not in reach:
        return None
    if any((p[1], p[2]) not in reach for p in skel["plants"]):
        return None
    units = [[0, 0, own_doors[0][0], own_doors[0][1], 1, 2, 1, 1]
             + [0] * 6]
    second = skel["roster"]["second"]
    if second is not None:
        ordered = sorted(reach.items(), key=lambda kv: (kv[1], kv[0]))
        cell = ordered[int(second["frac"] * (len(ordered) - 1))][0]
        carry = [0] * 6
        if second["full_wood"]:
            carry[WOOD] = second["cap"]
        units.append([2, 0, cell[0], cell[1], second["speed"],
                      second["cap"], second["harvest"], second["chop"]]
                     + carry)
    for i, opp in enumerate(skel["roster"]["opp"]):
        door = opp_doors[min(i, len(opp_doors) - 1)]
        units.append([5 + i, 1, door[0], door[1], opp["speed"], opp["cap"],
                      opp["harvest"], opp["chop"]] + [0] * 6)
    return {
        "map_id": skel["id"],
        "seat": seat,
        "class": skel["class"],
        "profile": skel["profile"],
        "seed": skel["seed"],
        "attempt": skel["attempt"],
        "rows": rows,
        "plants": [list(p) for p in skel["plants"]],
        "inventory": list(skel["inventory"]),
        "units": units,
        "orchard_eligible": orchard_eligible_view(rows, skel["plants"]),
    }


# ---------------------------------------------------------------------------
# Referee adapter (thin adapter over the make_banana_traces referee core)
# ---------------------------------------------------------------------------

class ParsedCommands:
    """The result of parsing one command line, in engine phase buckets.

    Mirrors `engine.rs::ParsedCmds` (671-681) field for field, plus the
    RETAINED trust-boundary errors the frozen contract requires (there is no
    such thing in the engine, which trusts its input)."""

    __slots__ = ("moves", "harvest", "plant", "chop", "pick", "train",
                 "drop", "mine", "errors", "used")

    def __init__(self):
        self.moves = {}
        self.harvest = []
        self.plant = []
        self.chop = []
        self.pick = []
        self.train = []
        self.drop = []
        self.mine = []
        self.errors = []
        self.used = set()

    def total(self) -> int:
        return (len(self.moves) + len(self.harvest) + len(self.plant)
                + len(self.chop) + len(self.pick) + len(self.train)
                + len(self.drop) + len(self.mine))

class FuzzReferee(mbt.Referee):
    """make_banana_traces.Referee bound to generated geometry.

    The inherited command application for MOVE/HARVEST/CHOP/PLANT/PICK/DROP
    and growth are reused verbatim; this adapter (a) supplies the instance
    walkable set / tent for the module-global lookups the original referee
    performs (bound before every apply), (b) evaluates water adjacency on the
    instance map so wet-cell cooldown boosts are real, (c) asks the
    deterministic opponent policy for player 1's COMMAND LINE and merges it
    with the candidate's into ONE `engine.rs::step` transition (review B2 --
    r3 ran a direct post-phase mini-simulator instead), and (d) owns an
    EXHAUSTIVE command dispatcher (see `apply`) that implements TRAIN and
    MINE and retains any verb it does not implement as a fail-closed
    trust-boundary error."""

    def __init__(self, rows, inventory, plants, units, profile):
        super().__init__(list(inventory), plants, units)
        self.rows = tuple(rows)
        geo = sh.parse_rows(self.rows)
        self.walk = set(geo["walkable"])
        self.tent = geo["shacks"][0]
        self.opp_tent = geo["shacks"][1]
        self.waters = set(geo["water"])
        self.irons = set(geo["iron"])
        self.profile = profile
        self.opp_doors = sorted(c for c in _orth_neighbors(self.opp_tent)
                                if c in self.walk)
        # 1-based, exactly like the bot's own counter: `let mut turn = 1;
        # while let Some(view) = read_turn(&mut reader, &map, turn)`
        # (yamo_orchard_live.rs:6017-6023).  Turn t is the state block the
        # referee emits before applying C_t.  NOTE: no TRAIN rule reads this
        # -- engine.rs::apply_train (525-568) never touches game.turn.
        self.turn = 1
        # `game.next_id`: a monotone spawn-id counter (engine.rs:555, 567).
        # engine.rs contains no unit-removal path at all, so seeding it at
        # max(id) + 1 over the serialized roster reproduces the engine's
        # counter exactly; a plain max()+1 at spawn time would not, because
        # ids are never reused.
        self.next_id = (max(self.units) + 1) if self.units else 0
        self.shacks = (self.tent, self.opp_tent)
        # --- retained command-execution provenance (contract §8) ----------
        # REVIEW B4: UNCAPPED, and the verbatim stdout line of every
        # offending turn is retained beside the per-fragment errors, so the
        # durable packet alone can reconstruct every offending raw command.
        self.command_errors = []       # every error, raw bytes verbatim
        self.error_counts = {}         # complete counts per error kind
        self.error_lines = []          # {turn, line, sha256, length}
        self.train_events = []         # every TRAIN entry, accepted or not
        # REVIEW B2: the opponent's own command line, one per applied turn.
        self.opponent_commands = []
        self._bfs_cache = {}

    @property
    def execution_status(self) -> str:
        """`ok` iff every emitted command reached an implemented verb with a
        well-formed body.  Anything else makes the row -- and therefore the
        aggregate -- GATE_UNREADY, and the row still counts in the
        denominator."""
        for kind in (ERROR_UNSUPPORTED_VERB, ERROR_MALFORMED):
            if self.error_counts.get(kind):
                return kind
        return EXECUTION_OK

    @property
    def command_error_total(self) -> int:
        return sum(self.error_counts.values())

    def spawn_events(self) -> list:
        """Own-side (player 0) spawns.  The opponent's TRAIN entries stay in
        `train_events` with their `player` field."""
        return [dict(e) for e in self.train_events
                if e["spawned"] and e["player"] == 0]

    def map_header(self):
        return ("%d %d\n" % (len(self.rows[0]), len(self.rows))
                + "\n".join(self.rows) + "\n")

    def near_water(self, cell):
        return any(n in self.waters for n in _orth_neighbors(cell))

    def _nbrs(self, cell):
        return [n for n in _orth_neighbors(cell) if n in self.walk]

    def _bfs_from(self, sources):
        """engine.rs::bfs_distances (72-92).  Sources are seeded at 0
        UNCONDITIONALLY (line 75-80) -- a non-walkable source such as a shack
        cell is in the map -- and expansion is restricted to walkable cells
        (line 85).  Memoised: the walkable set is fixed for a game."""
        key = frozenset(sources)
        hit = self._bfs_cache.get(key)
        if hit is not None:
            return hit
        from collections import deque
        dist = {}
        queue = deque()
        for c in sources:
            if c not in dist:
                dist[c] = 0
                queue.append(c)
        while queue:
            cell = queue.popleft()
            for n in self._nbrs(cell):
                if n not in dist:
                    dist[n] = dist[cell] + 1
                    queue.append(n)
        self._bfs_cache[key] = dist
        return dist

    def next_cell(self, current, target, speed):
        """engine.rs::next_cell (99-144), mirrored line by line.

            let src = bfs_distances(walkable, &[current]);            // 100
            if let Some(&d) = src.get(&target) { if d <= speed {...}} // 103-107
            let tdist = if !src.contains_key(&target) { ... }         // 110-123
            let in_range = src.iter()
                .filter(|(c, d)| **d <= speed && tdist.contains_key(*c))  // 126-130
            if in_range.is_empty() { return current; }                // 132-134
            let best_dist = in_range.iter().map(|c| tdist[c]).min()   // 136
            in_range.filter(tdist == best).min()                      // 138-143

        The r2 mirror carried a hand-written special case for a non-walkable
        source cell that stepped to a walkable neighbour BEFORE applying the
        speed loop, so a speed-0 worker standing on the (non-walkable) shack
        could move one cell.  The engine cannot do that: with `speed == 0`
        the only member of `in_range` is the source itself.  That divergence
        is now gone because the special case is gone -- this is the engine's
        own selection rule and nothing else."""
        src = self._bfs_from([current])
        d = src.get(target)
        if d is not None and d <= speed:
            return target
        if target not in src:
            if not src:
                return current
            best = min(_manhattan(target, c) for c in src)
            goals = tuple(sorted(c for c in src
                                 if _manhattan(target, c) == best))
            tdist = self._bfs_from(goals)
        else:
            tdist = self._bfs_from([target])
        in_range = [c for c, dd in src.items()
                    if dd <= speed and c in tdist]
        if not in_range:
            return current
        best_dist = min(tdist[c] for c in in_range)
        return min(c for c in in_range if tdist[c] == best_dist)

    def step_toward(self, current, target, speed):
        """Retained name (the inherited make_banana_traces referee calls it);
        the engine's own selection rule is the only implementation.  Nothing
        in this module calls it any more: since r4 the opponent policies emit
        MOVE commands and the engine's own `_apply_moves` does the stepping,
        so there is no second navigation path in the panel."""
        return self.next_cell(current, target, speed)

    def _near_shack(self, unit) -> bool:
        """engine.rs::near_shack (205-208)

            let (sx, sy) = game.shacks[unit.player as usize];
            (unit.x - sx).abs() + (unit.y - sy).abs() <= 1

        `<= 1`, so a unit standing ON its own shack cell qualifies.  The
        inherited make_banana_traces referee used `== 1` and therefore
        refused PICK/DROP from the shack cell itself."""
        return _manhattan(unit["cell"], self.shacks[unit["player"]]) <= 1

    def _inv_of(self, player):
        return self.inv if player == 0 else self.opp_inv

    # -- TRAIN ------------------------------------------------------------
    # THE SOLE AUTHORITY IS rust/src/game/engine.rs::apply_train (525-568).
    # Every rule below quotes the line it mirrors, and NOTHING that
    # apply_train does not enforce is encoded here.  In particular there is
    # no worker cap and no final-N-turn guard: those come from
    # MoisanBot::can_train (yamo_orchard_live.rs:836), which is one bot's
    # self-restraint.  The bot may still choose not to train; that is the
    # bot's business.  Full citations in
    # referee-train-repair-r2-2026-08-09.md.

    def own_unit_ids(self, player=0):
        return sorted(uid for uid, u in self.units.items()
                      if u["player"] == player)

    def can_train(self, talents, player=0):
        """The two conditions engine.rs::apply_train rejects on, and only
        those.  Returns None when the TRAIN is legal, otherwise the reason
        string that goes into the retained event ledger.

            engine.rs:527  let n = game.units.iter()
                               .filter(|u| u.player == player).count() as i32;
            engine.rs:528  let cost = training_cost(n, talents);
            engine.rs:539  if pay.iter().any(|&i| inv[i] < cost[i]) {
            engine.rs:540      return;
            engine.rs:544  let shack = game.shacks[p];
            engine.rs:545  if game.units.iter().any(|u| u.pos() == shack) {
            engine.rs:546      return;

        `n` is read at 527 and used at 528 to price the bill -- it is never
        compared to anything.  `game.turn` is not read anywhere in 525-568
        (`step` alone touches it, engine.rs:805).  Anything else the bot's
        own `can_train` refuses is the bot's policy, not a rule.

        `player` is engine.rs:526 `player`: `apply_train(game, 0, ..)` for the
        candidate's stream and `apply_train(game, 1, ..)` for the opponent's
        (engine.rs:786-791).  Every read below is that player's -- roster
        count, inventory and shack."""
        n = len(self.own_unit_ids(player))
        cost = training_cost(n, talents)
        inv = self._inv_of(player)
        for item in self.train_billed_items():
            if inv[item] < cost[item]:
                return "unaffordable"
        # engine.rs:545 iterates game.units -- ALL units, both players -- but
        # tests only THIS player's shack (engine.rs:544 `game.shacks[p]`).
        if any(u["cell"] == self.shacks[player] for u in self.units.values()):
            return "shack_occupied"
        return None

    def train_billed_items(self):
        """The engine's `pay` slice, engine.rs:531-536:

            // IRON (slot 4) only charged if iron terrain present
            let pay: &[usize] = if !game.iron.is_empty() {
                &[0, 1, 2, 3, 4, 5]
            } else {
                &[0, 1, 2, 3, 5]
            };

        BANANA (3) and WOOD (5) stay on the slice even though
        `training_cost` never writes them (engine.rs:516-521), so both the
        check at 539 and the deduction at 550-552 are no-ops for them."""
        if self.irons:
            return [PLUM, LEMON, APPLE, BANANA, IRON, WOOD]
        return [PLUM, LEMON, APPLE, BANANA, WOOD]

    def train(self, talents, player=0) -> bool:
        """Resolve one TRAIN for `player`.  Returns True iff a worker spawned.

            engine.rs:550  for &i in pay {
            engine.rs:551      game.inventories[p][i] -= cost[i];
            engine.rs:554  let (ms, cc, hp, chop) = talents;
            engine.rs:555  let nid = game.next_id;
            engine.rs:556  game.units.push(Unit {
            engine.rs:557      id: nid, player,
            engine.rs:559      x: shack.0, y: shack.1,
            engine.rs:561      ms, cc, hp, chop,
            engine.rs:565      carry: [0; 6],
            engine.rs:567  game.next_id += 1;
        """
        if self.can_train(talents, player) is not None:
            return False
        n = len(self.own_unit_ids(player))
        cost = training_cost(n, talents)
        inv = self._inv_of(player)
        for item in self.train_billed_items():
            inv[item] -= cost[item]
        ms, cc, hp, chop = talents
        nid = self.next_id
        self.next_id += 1
        self.units[nid] = {
            "player": player, "cell": self.shacks[player], "speed": ms,
            "cap": cc, "harvest": hp, "chop": chop, "carry": [0] * 6,
        }
        return True

    def _train_one(self, talents, player=0):
        """Phase 6.  Wraps `train` with the retained provenance event the
        frozen contract (§8) requires: turn, talents, bill, roster size the
        bill was priced at, spawn identity and the inventory either side."""
        n = len(self.own_unit_ids(player))
        cost = training_cost(n, talents)
        reason = self.can_train(talents, player)
        nid = self.next_id
        before = list(self._inv_of(player))
        spawned = self.train(talents, player)
        event = {
            "turn": self.turn,
            "player": player,
            "talents": list(talents),
            "cost": list(cost),
            "roster_before": n,
            "spawned": bool(spawned),
            "reason": reason,
            "inventory_before": before,
            "inventory_after": list(self._inv_of(player)),
            "unit_id": nid if spawned else None,
            "cell": list(self.units[nid]["cell"]) if spawned else None,
            "carry": list(self.units[nid]["carry"]) if spawned else None,
        }
        self.train_events.append(event)
        return spawned

    # -- trust-boundary parser (contract C1/C2/C3/C5/C6) ------------------
    # PARSE THE COMPLETE LINE BEFORE ANY MUTATION.  The r2 referee executed
    # raw fragments one at a time, which made both the per-unit `used` rule
    # and the phase order impossible to express.

    VERB_HANDLERS = {
        # verb -> the phase bucket it feeds (None = no world effect).
        # engine.rs::parse_cmds (683-748).  There is deliberately NO default
        # branch: a verb absent from this table is a retained
        # `unsupported_verb` error, never a silent skip.
        "MSG": None, "WAIT": None,
        "MOVE": "moves", "HARVEST": "harvest", "PLANT": "plant",
        "CHOP": "chop", "PICK": "pick", "TRAIN": "train",
        "DROP": "drop", "MINE": "mine",
    }

    # Exact token counts (verb included).  engine.rs is permissive here
    # (`parts.len() >= 4` etc., 724/735/740); the panel trust boundary is
    # not -- see contract C3 and the ERROR_MALFORMED note above.
    VERB_ARITY = {"MOVE": 4, "HARVEST": 2, "CHOP": 2, "DROP": 2, "MINE": 2,
                  "PLANT": 3, "PICK": 3}

    @staticmethod
    def _int(token, what):
        try:
            return int(token)
        except ValueError:
            raise _Malformed("%s is not an integer: %r" % (what, token))

    @classmethod
    def _parse_fragment(cls, tok):
        """One fragment -> (verb, payload).  Raises `_Malformed`."""
        verb = tok[0].upper()
        if verb == "MSG":
            # engine.rs:696 `"MSG" | "WAIT" => continue` -- MSG carries free
            # text, so its body is unconstrained.
            return "MSG", None
        if verb == "WAIT":
            if len(tok) != 1:
                raise _Malformed("WAIT takes no arguments, got %d"
                                 % (len(tok) - 1))
            return "WAIT", None
        if verb == "TRAIN":
            if len(tok) != 5:
                raise _Malformed(
                    "TRAIN takes exactly four talent fields; got %d. "
                    "engine.rs:698 accepts `parts.len() >= 5` and silently "
                    "drops shorter lines, and engine.rs:699-702 coerces "
                    "unparsable talents with `parse().unwrap_or(0)`; at the "
                    "panel trust boundary (contract C3) a malformed emitted "
                    "command is an instrument error, not a fabricated "
                    "command" % (len(tok) - 1))
            return "TRAIN", tuple(cls._int(t, "talent") for t in tok[1:5])
        arity = cls.VERB_ARITY[verb]
        if len(tok) != arity:
            raise _Malformed("%s takes exactly %d argument(s), got %d"
                             % (verb, arity - 1, len(tok) - 1))
        uid = cls._int(tok[1], "unit id")
        if verb == "MOVE":
            return verb, (uid, (cls._int(tok[2], "target x"),
                                cls._int(tok[3], "target y")))
        if verb in ("HARVEST", "CHOP", "DROP", "MINE"):
            return verb, (uid, None)
        item = tok[2].upper()
        # engine.rs::item_index (17-27) PANICS on an unknown item name, and
        # tree_health (53-60) panics on a non-tree PLANT type.  Fail closed.
        allowed = PLANTABLE_KINDS if verb == "PLANT" else tuple(ITEM_INDEX)
        if item not in allowed:
            raise _Malformed("%s: %r is not one of %s"
                             % (verb, tok[2], " ".join(allowed)))
        return verb, (uid, item)

    @staticmethod
    def split_fragments(command_line):
        """Split on ';' KEEPING the exact character span of each fragment.

        REVIEW B4: `command_line.split(";")` throws away where each fragment
        sat, and `.strip()` throws away its leading/trailing bytes, so the
        retained evidence could not reconstruct the offending output.  The
        empty fragments are yielded too (engine.rs:689 skips them, but their
        PLACEMENT is part of the raw evidence)."""
        out = []
        start = 0
        for i, ch in enumerate(command_line):
            if ch == ";":
                out.append((start, i, command_line[start:i]))
                start = i + 1
        out.append((start, len(command_line), command_line[start:]))
        return out

    @classmethod
    def parse_commands(cls, command_line, turn=0):
        """engine.rs::parse_cmds (683-748), plus the C3 trust boundary.

        Two engine rules that the r2 fragment executor could not express:

          * engine.rs:717-720
                if used.contains(&uid) { continue; }
                used.insert(uid);
            only the FIRST non-TRAIN command for a unit survives;
          * engine.rs:697-706 TRAIN `continue`s before a uid is parsed, so
            TRAIN is not unit-scoped and every entry is kept in parse order.

        Pure: it is a classmethod and touches no referee state, which is
        what 'parse before mutate' has to mean."""
        p = ParsedCommands()
        used = p.used
        for start, end, raw in cls.split_fragments(command_line):
            norm = " ".join(raw.split())
            if not norm:
                continue                       # engine.rs:689 empty fragment
            tok = norm.split()
            verb = tok[0].upper()
            if verb not in cls.VERB_HANDLERS:
                p.errors.append(command_error(
                    ERROR_UNSUPPORTED_VERB, verb, raw, turn,
                    unsupported_reason(verb, norm, turn),
                    span=(start, end), normalized=norm, line=command_line))
                continue
            try:
                verb, payload = cls._parse_fragment(tok)
            except _Malformed as exc:
                p.errors.append(command_error(
                    ERROR_MALFORMED, verb, raw, turn, str(exc),
                    span=(start, end), normalized=norm, line=command_line))
                continue
            bucket = cls.VERB_HANDLERS[verb]
            if bucket is None:
                continue
            if bucket == "train":
                p.train.append(payload)
                continue
            uid, extra = payload
            if uid in used:
                continue
            used.add(uid)
            if bucket == "moves":
                p.moves[uid] = extra
            elif extra is None:
                getattr(p, bucket).append(uid)
            else:
                getattr(p, bucket).append((uid, extra))
        return p

    # -- phase appliers (engine.rs, one function each) ---------------------

    def _apply_moves(self, intents):
        """engine.rs::apply_moves (213-357).  Per-player resolution: highest
        id wins a contested cell (264 `movers.sort_by(|a, b| b.cmp(a))`),
        circular swaps are resolved as a cycle (321-350), and a deadlock is
        broken by forcing one move (352-355).  The intent map is global
        (engine.rs:760-762 merges both players), so a command naming a unit
        of the other player resolves in that player's pass."""
        for player in (0, 1):
            ids = sorted(uid for uid, u in self.units.items()
                         if u["player"] == player)
            pos = {uid: self.units[uid]["cell"] for uid in ids}
            target = {}
            for uid in ids:
                if uid in intents:
                    target[uid] = self.next_cell(
                        pos[uid], intents[uid], self.units[uid]["speed"])
                else:
                    target[uid] = pos[uid]
            occupied = {pos[uid] for uid in ids}
            movers = sorted((uid for uid in ids if target[uid] != pos[uid]),
                            reverse=True)
            progress, resolve_blocking = True, False
            while progress:
                progress = False
                freq = {}
                for uid in movers:
                    freq[target[uid]] = freq.get(target[uid], 0) + 1
                to_remove = []
                for uid in movers:
                    cell = target[uid]
                    cur = self.units[uid]["cell"]
                    if ((resolve_blocking or freq[cell] == 1)
                            and cell not in occupied):
                        occupied.discard(cur)
                        occupied.add(cell)
                        self.units[uid]["cell"] = cell
                        to_remove.append(uid)
                        progress = True
                        resolve_blocking = False
                if to_remove:
                    movers = [u for u in movers if u not in to_remove]
                if progress:
                    continue
                mover_pos = {self.units[uid]["cell"]: uid for uid in movers}
                swap_resolved = False
                for start in movers:
                    path = [start]
                    while True:
                        nxt = mover_pos.get(target[path[-1]])
                        if nxt is None:
                            break
                        if nxt == path[0]:
                            for uid in path:
                                self.units[uid]["cell"] = target[uid]
                            movers = [u for u in movers if u not in path]
                            progress = swap_resolved = True
                            break
                        if nxt in path:
                            break
                        path.append(nxt)
                    if swap_resolved:
                        break
                if not swap_resolved and not resolve_blocking:
                    resolve_blocking = True
                    progress = True

    def _apply_harvest(self, uids):
        """engine.rs::apply_harvest (361-412).  MULTI-ROUND: for i in 1..=3
        every troll with `hp >= i` and free capacity takes one fruit (389-
        410), and the last fruit can be duplicated because the decrement is
        guarded by `if plant.fruits > 0` (405-407).  The inherited
        make_banana_traces referee took at most one fruit per unit per turn
        regardless of harvest power."""
        cells = {}
        for uid in uids:
            u = self.units.get(uid)
            if u is None:
                continue
            plant = self.plants.get(u["cell"])
            if plant is not None and plant["fruits"] > 0:
                cells.setdefault(u["cell"], []).append(uid)
        for cell, troll_ids in cells.items():
            plant = self.plants.get(cell)
            if plant is None:
                continue
            idx = ITEM_INDEX[plant["kind"]]
            for i in range(1, MAX_FRUITS + 1):
                if plant["fruits"] == 0:
                    break
                for uid in troll_ids:
                    u = self.units[uid]
                    if u["harvest"] >= i and sum(u["carry"]) < u["cap"]:
                        u["carry"][idx] += 1
                        if plant["fruits"] > 0:
                            plant["fruits"] -= 1

    def _apply_plant(self, entries):
        """engine.rs::apply_plant (461-511).  Requires a walkable cell (473),
        an empty cell (476) and a seed in carry (479).  Same-cell intents
        resolve simultaneously: same-type merges into ONE tree while every
        planter still spends a seed, mixed types cancel (490-499).  The new
        tree is size 0, health `tree_health(t, 0)`, cooldown 0 (501-509) --
        the same turn's growth tick then takes it to size 1."""
        intents = {}
        for uid, kind in entries:
            u = self.units.get(uid)
            if u is None:
                continue
            pos = u["cell"]
            if pos not in self.walk or pos in self.plants:
                continue
            idx = ITEM_INDEX[kind]
            if u["carry"][idx] <= 0:
                continue
            intents.setdefault(pos, []).append((uid, kind, idx))
        for pos in sorted(intents):                 # engine.rs:462 BTreeMap
            entries_ = intents[pos]
            if len({e[1] for e in entries_}) != 1:
                continue
            for uid, _, idx in entries_:
                self.units[uid]["carry"][idx] -= 1
            kind = entries_[0][1]
            self.plants[pos] = {"kind": kind, "size": 0,
                                "health": TREE_HEALTH_BASE[kind],
                                "fruits": 0, "cd": 0}

    def _apply_chop(self, uids, allowed_cells):
        """engine.rs::apply_chop_on_cells (576-643).  `allowed_cells` is the
        plant-cell snapshot taken BEFORE the plant phase (engine.rs:770), so
        a tree planted this turn cannot be felled this turn.  Damage is
        floored at 0 (608) and the wood loop hands one log per chopper per
        round, so the last log can duplicate (614-632)."""
        cells = {}
        for uid in uids:
            u = self.units.get(uid)
            if u is None or u["chop"] == 0:
                continue
            pos = u["cell"]
            if pos in allowed_cells and pos in self.plants:
                cells.setdefault(pos, []).append(uid)
        dead = []
        for cell, choppers in cells.items():
            plant = self.plants.get(cell)
            if plant is None:
                continue
            for uid in choppers:
                plant["health"] = max(plant["health"]
                                      - self.units[uid]["chop"], 0)
            if plant["health"] <= 0:
                size = plant["size"]
                remaining = size
                i = 0
                while i < size and remaining > 0:
                    for uid in choppers:
                        u = self.units[uid]
                        if u["cap"] - sum(u["carry"]) > 0:
                            u["carry"][WOOD] += 1
                            remaining -= 1
                    i += 1
                dead.append(cell)
        for cell in dead:
            self.plants.pop(cell, None)

    def _apply_pick(self, entries):
        """engine.rs::apply_pick (438-458).  Near-shack (`<= 1`, so the shack
        cell itself counts), free capacity, and the item must be in stock."""
        for uid, kind in entries:
            u = self.units.get(uid)
            if u is None or not self._near_shack(u):
                continue
            if u["cap"] - sum(u["carry"]) <= 0:
                continue
            idx = ITEM_INDEX[kind]
            inv = self._inv_of(u["player"])
            if inv[idx] > 0:
                inv[idx] -= 1
                u["carry"][idx] += 1

    def _apply_drop(self, uids):
        """engine.rs::apply_drop (415-435).  Banks the WHOLE carry."""
        for uid in uids:
            u = self.units.get(uid)
            if u is None or not self._near_shack(u):
                continue
            inv = self._inv_of(u["player"])
            for i in range(6):
                inv[i] += u["carry"][i]
            u["carry"] = [0] * 6

    def _apply_mine(self, uids):
        """engine.rs::apply_mine (646-667): `chop == 0 || free <= 0` skips,
        orthogonal adjacency to an iron cell yields `min(chop, free)`."""
        for uid in uids:
            u = self.units.get(uid)
            if u is None:
                continue
            free = u["cap"] - sum(u["carry"])
            if u["chop"] == 0 or free <= 0:
                continue
            cell = u["cell"]
            if any(_manhattan(cell, i) == 1 for i in self.irons):
                u["carry"][IRON] += min(u["chop"], free)

    def _execute(self, parsed, opp=None):
        """engine.rs::step (755-806), phases 1..8 in engine order, over BOTH
        players' parsed streams merged phase by phase.

            apply_moves   762      apply_pick    783
            apply_harvest 767      apply_train   786-791
            apply_plant   773      apply_drop    796
            apply_chop    778      apply_mine    801

        REVIEW B2.  `engine::step` takes `cmds0` and `cmds1`, parses each
        separately (so the per-unit `used` rule at engine.rs:717-720 is
        PER PLAYER) and then merges the buckets before each applier:

            let mut all_moves = a.moves.clone();
            all_moves.extend(b.moves.iter());        // engine.rs:760-762

        A HashMap `extend` overwrites on a duplicate key, so when both
        streams name the same unit the OPPONENT's intent wins; the list
        buckets concatenate in `a`-then-`b` order.  TRAIN is the one phase
        that is not merged: engine.rs:786-791 runs `a.train` as player 0 and
        `b.train` as player 1, sharing one `next_id`.

        Until r4 the panel applied only `parsed` and then let a scripted
        policy mutate opponent units directly, AFTER every phase.  That
        transition cannot be produced by `step` at all: move contention was
        never resolved across players, a unit could be acted on twice in one
        turn, and opponent harvest/chop/banking used a second, informal set
        of rules.

        The choppable-cell snapshot is taken at engine.rs:770, i.e. BEFORE
        the plant phase."""
        if opp is None:
            opp = ParsedCommands()
        moves = dict(parsed.moves)
        moves.update(opp.moves)
        self._apply_moves(moves)
        self._apply_harvest(list(parsed.harvest) + list(opp.harvest))
        choppable = set(self.plants)
        self._apply_plant(list(parsed.plant) + list(opp.plant))
        self._apply_chop(list(parsed.chop) + list(opp.chop), choppable)
        self._apply_pick(list(parsed.pick) + list(opp.pick))
        for talents in parsed.train:
            self._train_one(talents, 0)
        for talents in opp.train:
            self._train_one(talents, 1)
        self._apply_drop(list(parsed.drop) + list(opp.drop))
        self._apply_mine(list(parsed.mine) + list(opp.mine))

    def grow(self):
        """engine.rs::tick_plants (149-189).  Identical to the inherited
        version except for the `health > 0` guard at engine.rs:156, which the
        inherited referee omits."""
        for cell, plant in self.plants.items():
            if plant["cd"] > 0:
                plant["cd"] -= 1
            if plant["cd"] == 0 and plant["health"] > 0:
                if plant["size"] < MAX_SIZE:
                    plant["size"] += 1
                    plant["health"] += TREE_HEALTH_SLOPE[plant["kind"]]
                    plant["cd"] = self.effective_cd(plant["kind"], cell)
                elif plant["fruits"] < MAX_FRUITS:
                    plant["fruits"] += 1
                    plant["cd"] = self.effective_cd(plant["kind"], cell)

    def effective_cd(self, kind, cell):
        """engine.rs:164-173 / 176-185."""
        cd = PLANT_COOLDOWN[kind]
        return cd - WATER_BOOST[kind] if self.near_water(cell) else cd

    def _retain(self, errors, command_line):
        """Retain the COMPLETE trust-boundary evidence for one turn."""
        if not errors:
            return
        for err in errors:
            self.error_counts[err["kind"]] = self.error_counts.get(
                err["kind"], 0) + 1
            self.command_errors.append(err)
        self.error_lines.append({
            "turn": self.turn,
            "line": command_line,
            "sha256": hashlib.sha256(
                command_line.encode("utf-8")).hexdigest(),
            "length": len(command_line)})

    def apply(self, command_line):
        """One turn: the candidate's line plus the opponent policy's line,
        executed as ONE phase-merged engine transition.

        No fragment is ever handed to `make_banana_traces.Referee.apply`.
        That inherited dispatcher is a sequential if/elif chain with a silent
        fall-through bottom -- the original defect (TRAIN and MINE fell out
        of it for the whole life of the panel, and m040 seats 0/1 emitted
        TRAIN on 166 and 182 of 200 turns while scoring CLEAN).  Keeping a
        delegation path to it would keep a second, informal command language
        inside the panel, which the frozen contract (§1) forbids -- and, per
        review B2, so did the scripted opponent, which is why the policies
        now EMIT COMMANDS instead of mutating the world."""
        return self.apply_two(command_line, opponent_command_line(self))

    def apply_two(self, command_line, opp_command_line):
        """Both players' command lines, one `engine.rs::step` transition."""
        parsed = self.parse_commands(command_line, self.turn)
        self._retain(parsed.errors, command_line)
        opp = self.parse_commands(opp_command_line, self.turn)
        if opp.errors:
            # The opponent line is generated by the panel itself, so an
            # error here is an INSTRUMENT bug, not untrusted bot output.
            raise PanelError(
                "the panel generated an opponent command line its own trust "
                "boundary rejects (turn %d, profile %r, line %r): %s"
                % (self.turn, self.profile, opp_command_line,
                   opp.errors[0]["reason"]))
        self.opponent_commands.append(opp_command_line)
        self._execute(parsed, opp)
        self.turn += 1


# The verbs the referee implements, and the verbs the game's own command
# parser recognises.  The self-tests assert ENGINE_COMMANDS <=
# SUPPORTED_COMMANDS, so adding a verb to the protocol without adding a
# referee handler is a test failure rather than a silent no-op.
SUPPORTED_COMMANDS = frozenset(FuzzReferee.VERB_HANDLERS)
ENGINE_COMMANDS = frozenset({"MSG", "WAIT", "TRAIN", "MOVE", "HARVEST",
                             "DROP", "CHOP", "MINE", "PLANT", "PICK"})


def _opp_ids(ref):
    return sorted(uid for uid, u in ref.units.items() if u["player"] == 1)


def _opp_seek_and_act(ref, want_fruits, verb) -> str:
    """Shared deterministic opponent policy, as a COMMAND LINE.

    REVIEW B2.  Until r4 this function MUTATED the world directly, after all
    of the candidate's phases: it moved units, decremented fruits, subtracted
    tree health and banked carry with its own simplified rules.  That is a
    second informal simulator, and the transition it produced is not one
    `engine.rs::step` can produce.  It now only DECIDES, and the decision is
    expressed as engine commands that go through the same parser and the same
    appliers as the candidate's, merged into one transition.

    The behaviour therefore changes in one visible way, and that change is
    the repair: a unit can no longer step onto a plant AND act on it in the
    same turn, because engine.rs:717-720 keeps only the first non-TRAIN
    command per unit.  Arrival and action are now two turns, as they are for
    every real bot.  Full units bank at the opponent shack; otherwise the
    unit walks to the nearest qualifying plant (BFS from the unit, ties by
    cell) and acts once it is standing on it."""
    cmds = []
    for uid in _opp_ids(ref):
        u = ref.units[uid]
        free = u["cap"] - sum(u["carry"])
        if free <= 0:
            # engine.rs::near_shack (205-208) is `<= 1`, so the shack cell
            # itself counts; apply_drop (415-435) does the banking.
            if _manhattan(u["cell"], ref.opp_tent) <= 1:
                cmds.append("DROP %d" % uid)
                continue
            if not ref.opp_doors:
                continue
            dmap = ref._bfs_from([u["cell"]])
            door = min(ref.opp_doors, key=lambda d: (dmap.get(d, BIG), d))
            cmds.append("MOVE %d %d %d" % (uid, door[0], door[1]))
            continue
        targets = sorted(
            c for c, p in ref.plants.items()
            if (p["fruits"] > 0 if want_fruits else True))
        if not targets:
            continue
        dmap = ref._bfs_from([u["cell"]])
        targets = [c for c in targets if c in dmap]
        if not targets:
            continue
        tgt = min(targets, key=lambda c: (dmap[c], c))
        if u["cell"] == tgt:
            cmds.append("%s %d" % (verb, uid))
        else:
            cmds.append("MOVE %d %d %d" % (uid, tgt[0], tgt[1]))
    return ";".join(cmds)


OPP_POLICIES = {
    "idle": lambda ref: "",
    "harvester": lambda ref: _opp_seek_and_act(ref, True, "HARVEST"),
    "chopper_aggressor": lambda ref: _opp_seek_and_act(ref, False, "CHOP"),
}


def opponent_command_line(ref) -> str:
    """Player 1's command line for this turn.  A profile is a POLICY over
    commands; it has no privileged access to the world."""
    return OPP_POLICIES[ref.profile](ref)


def make_referee(spec) -> FuzzReferee:
    plants = {}
    for k, x, y, size, health, fruits, cd in spec["plants"]:
        plants[(x, y)] = {"kind": k, "size": size, "health": health,
                          "fruits": fruits, "cd": cd}
    units = {}
    for row in spec["units"]:
        uid, player, x, y, speed, cap, harvest, chop = row[:8]
        units[uid] = {"player": player, "cell": (x, y), "speed": speed,
                      "cap": cap, "harvest": harvest, "chop": chop,
                      "carry": list(row[8:14])}
    ref = FuzzReferee(spec["rows"], spec["inventory"], plants, units,
                      spec["profile"])
    # The opponent's bank.  Generated corpus specs start it empty (the
    # inherited referee's default); the two-player differential cases seed
    # it, because engine.rs::apply_train (532-552) bills player 1 from
    # `game.inventories[1]`.
    if spec.get("opp_inventory") is not None:
        ref.opp_inv = list(spec["opp_inventory"])
    return ref


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------

def progress_turns(tr) -> set:
    """Turns t (1..T-1) whose S_t -> S_{t+1} transition changes the own
    inventory or any own unit's cargo (P4 'score credit or cargo change')."""
    out = set()
    for t in range(1, tr.T):
        s0, s1 = tr.state(t), tr.state(t + 1)
        if s0.inventories[0] != s1.inventories[0]:
            out.add(t)
            continue
        if ({u.id: tuple(u.carry) for u in s0.own_units()}
                != {u.id: tuple(u.carry) for u in s1.own_units()}):
            out.add(t)
    return out


def stall_windows(prog: set, T: int, window: int, last_known: int | None = None
                  ) -> list:
    """Maximal runs of >= window consecutive progress-free turns in
    1..last_known.

    `last_known` is the last turn whose OUTCOME is known.  It defaults to
    T-1: the transcript records S_1..S_T, so for t <= T-1 the outcome of turn
    t is read off the recorded transition S_t -> S_{t+1}, while turn T has no
    recorded successor state.  A caller holding the post-C_T referee state
    (see `post_ct_state`) knows the outcome of turn T too and passes
    last_known=T so the final turn can count."""
    n = T - 1 if last_known is None else last_known
    runs = []
    start = None
    for t in range(1, n + 1):
        if t in prog:
            if start is not None and t - start >= window:
                runs.append((start, t - 1))
            start = None
        elif start is None:
            start = t
    if start is not None and n + 1 - start >= window:
        runs.append((start, n))
    return runs


def post_ct_state(ref):
    """The post-C_T referee state: the world AFTER the final turn's commands
    resolve, read from the panel's own referee once the game loop has applied
    C_T (and the referee's own end-of-turn growth / opponent step).

    Returned as the same td.GameState the transcript parser produces for a
    recorded turn, so every world-state predicate reads it exactly as it
    reads S_1..S_T.  Absolute: one candidate referee, no parent reference."""
    text = ref.map_header() + ref.turn_text()
    return td.build_trace(text, "WAIT\n").state(1)


def post_ct_progress(tr, post) -> bool:
    """True iff resolving C_T made own-player progress -- the same predicate
    `progress_turns` applies to every recorded transition (own inventory or
    an own unit's cargo changes), applied to the S_T -> post-C_T transition.

    Opponent inventory/cargo motion and plant growth are world motion, not
    own progress, and are ignored exactly as they are for turns 1..T-1."""
    st = tr.state(tr.T)
    if st.inventories[0] != post.inventories[0]:
        return True
    return ({u.id: tuple(u.carry) for u in st.own_units()}
            != {u.id: tuple(u.carry) for u in post.own_units()})


def work_remaining(tr, t) -> bool:
    """ABSOLUTE terminal-state test on the referee world state S_t: True iff
    the world still offers the own player a resource action.

    Work remains when (a) any own unit still carries something (it can be
    banked at the tent, or planted), or (b) some plant is still standing on a
    cell an own unit can walk to (it can be harvested when it fruits, or
    chopped for wood).  Nothing else can change the own inventory or an own
    unit's cargo through a resource action: PLANT needs a carried fruit and
    HARVEST/CHOP need a reachable plant.  Purely a function of the world state
    the referee reports (static map + plants + own units) — no parent
    reference, no command-pattern heuristic."""
    st = tr.state(t)
    own = st.own_units()
    if any(sum(u.carry) for u in own):
        return True
    if not st.plants:
        return False
    reach = td.bfs_distances(tr.smap.walkable, sorted(u.cell for u in own))
    return any(p.cell in reach for p in st.plants)


def live_horizon(tr) -> int:
    """First turn of the maximal terminal suffix of the game — the turn from
    which `work_remaining` is False for the whole rest of the game (tr.T + 1
    when the world never runs out).  Turns from here on cannot produce
    progress, so they carry no liveness obligation."""
    t = tr.T
    while t >= 1 and not work_remaining(tr, t):
        t -= 1
    return t + 1


def eval_p1(tr_c, tr_p, parent_cmds, parent_d1_failed: bool):
    """RAW detector gate (owner ruling 2026-08-06): every FAIL among
    D-1..D-9 blocks the candidate, inherited-from-parent or not, on every
    map.  Both former parent-comparison exemptions are REMOVED:
      * the D-9 parent-differential gate (round-6 ROOT-A) -- a D-9 episode
        the parent reproduced byte-for-byte used to be downgraded to a
        report-tier flag; under raw it blocks;
      * the D-1 inherited-report-only downgrade -- a D-1 episode on a map
        where the parent also oscillates used to be report-only; under raw
        it blocks.
    tr_p and parent_d1_failed are retained only for signature/diagnostic
    parity and never exempt an episode.  parent_cmds is still forwarded to
    td.run_all because detect_d9's base semantics consume it (the detector
    itself is unmodified).  The returned `inherited`/`d9_dropped` are always
    empty/0 now -- kept so the caller's shape is unchanged."""
    results = td.run_all(tr_c, parent_cmds)
    violations = [r for r in results if r["verdict"] == "FAIL"]
    return results, violations, [], 0


def eval_p2(tr_c):
    rep = rt.r5_two_worker_full_cargo_banking(tr_c)
    alternations = [v for v in rep["violations"] if "alternation" in v["why"]]
    horizon = [v for v in rep["violations"]
               if "banking horizon" in v["why"]]
    return rep, alternations, horizon


def eval_p3(orchard_eligible: bool, commands_c: str, commands_p: str):
    if not orchard_eligible or commands_c == commands_p:
        return []
    lc, lp = commands_c.splitlines(), commands_p.splitlines()
    for i in range(max(len(lc), len(lp))):
        a = lc[i] if i < len(lc) else "<absent>"
        b = lp[i] if i < len(lp) else "<absent>"
        if a != b:
            return [{"first_divergence_turn": i + 1,
                     "candidate": a, "parent": b}]
    return [{"first_divergence_turn": None,
             "candidate": "<trailing bytes differ>", "parent": ""}]


def eval_p4(tr_c, tr_p, window: int, post_state=None):
    """RAW liveness (owner ruling 2026-08-06) with an ABSOLUTE terminal-state
    calibration.  The candidate must make progress (own inventory or own-unit
    cargo change) in every rolling window; every stall window blocks and
    there is NO parent-relative/inherited/aligned-prefix exemption of any
    kind (the former 'unless the parent also makes no progress in the same
    window' clause stays REMOVED; tr_p is accepted for signature/diagnostic
    parity only and is never consulted).

    Calibration (2026-08-06, repair #2): a stall is a liveness failure only
    over turns in which the referee's own world state still offers a resource
    action -- see `work_remaining` / `live_horizon`.  Each stall window is
    trimmed to that live prefix and blocks only if the trimmed part is still
    >= `window` turns.  Rationale: a stall that begins after the world is
    exhausted for the rest of the game (no plant reachable by an own unit and
    no cargo left to bank) is explained by the game being over, not by the
    bot being stuck; a stall while work remains -- mid-game or running to the
    sim horizon -- still blocks.

    Post-C_T rule (2026-08-08).  Every recorded state is the world BEFORE
    that turn's commands resolve, so the outcome of the final command set
    C_T is absent from the transcript and the last turn used to carry no
    liveness obligation in either direction: a do-nothing C_T was never
    counted as a stalled turn and a C_T that banked or planted was never
    counted as progress.  Given the post-C_T referee state (`post_ct_state`
    -- the world after C_T resolves) the final turn is judged like any
    other:

        turn T is a stalled turn  <=>  work remains in S_T (the OBLIGATION
        is set by the pre-state: only a world that still offers a resource
        action can demand one) AND resolving C_T changes neither the own
        inventory nor any own unit's cargo (the OUTCOME is read off the
        post-state).

    That closes the boundary in both directions -- work completed by C_T is
    progress and can no longer be scored as a stall; an idle final turn now
    counts toward the window -- and it never shortens an already-formed
    window: a stall that has already run >= window live turns still blocks
    whatever C_T does.  Absolute: the post state is the candidate's own
    referee world, no parent reference.  post_state=None keeps the pre-rule
    behaviour for callers that cannot supply it (the outcome of C_T is then
    unknown, so the final turn carries no obligation)."""
    pc = progress_turns(tr_c)
    last_known = tr_c.T - 1
    if post_state is not None:
        last_known = tr_c.T
        if post_ct_progress(tr_c, post_state):
            pc = pc | {tr_c.T}
    windows = stall_windows(pc, tr_c.T, window, last_known)
    if not windows:
        return []
    horizon = live_horizon(tr_c)
    violations = []
    for (a, b) in windows:
        live_end = min(b, horizon - 1)
        if live_end - a + 1 < window:
            continue
        violations.append({
            "window_start": a, "window_end": b, "live_end": live_end,
            "terminal_from": horizon,
            "why": "candidate makes no own-inventory/own-cargo progress over "
                   "turns %d-%d while work remains through turn %d (>= %d "
                   "live turns) [RAW liveness: every stall window over a "
                   "non-terminal world blocks]"
                   % (a, b, live_end, window)})
    return violations


# ---------------------------------------------------------------------------
# Per-game job
# ---------------------------------------------------------------------------

def _record_execution(row, ref, seat="candidate"):
    """Copy a referee's retained command-execution ledger onto the row.

    Contract §8 / review B6: the packet must be able to distinguish 'every
    command executed' from 'the process ended before publishing evidence'.
    An `unsupported_command` used to raise out of the worker and abort the
    aggregate before any row existed, so the affected row vanished from the
    denominator entirely.

    REVIEW B3: this now runs for BOTH seats.  r3 recorded only
    `parent_execution_status` -- a bare string, with no ledger -- so a
    malformed parent command left no reconstructable evidence at all, and
    `aggregate_verdict` never read even the string."""
    pre = "" if seat == "candidate" else "parent_"
    row[pre + "execution_status"] = ref.execution_status
    row[pre + "command_errors"] = list(ref.command_errors)
    row[pre + "command_error_counts"] = dict(ref.error_counts)
    row[pre + "command_error_total"] = ref.command_error_total
    row[pre + "error_lines"] = list(ref.error_lines)
    row[pre + "train_events"] = list(ref.train_events)
    row[pre + "spawns"] = ref.spawn_events()
    row[pre + "successful_train_turns"] = [e["turn"]
                                           for e in row[pre + "spawns"]]
    # review B2: player 1's command stream is now real evidence -- it is what
    # the merged transition consumed.  The full text goes into `artifacts`
    # (and the saved failure directory); the row keeps its digest so a
    # reproduction can be checked against the packet.
    stream = "\n".join(ref.opponent_commands) + "\n"
    row[pre + "opponent_commands_sha256"] = hashlib.sha256(
        stream.encode("utf-8")).hexdigest()
    return row


def run_pair(job):
    """One (map, seat): candidate + parent closed-loop games on the
    identical spec, then all properties. Pure function of the job dict."""
    spec = job["spec"]
    turns = job["turns"]
    row = {
        "map_id": spec["map_id"], "seat": spec["seat"],
        "class": spec["class"], "profile": spec["profile"],
        "seed": spec["seed"], "attempt": spec["attempt"],
        "orchard_eligible": spec["orchard_eligible"],
        "violations": [], "flags": [],
        # contract §8 -- present on EVERY row, including aborted ones.
        "execution_status": EXECUTION_OK,
        "command_errors": [], "command_error_counts": {},
        "command_error_total": 0, "error_lines": [],
        "train_events": [], "spawns": [],
        # review B3 -- the parent's ledger is retained in full, not just its
        # status string, and it dominates the aggregate the same way.
        "parent_execution_status": EXECUTION_OK,
        "parent_command_errors": [], "parent_command_error_counts": {},
        "parent_command_error_total": 0, "parent_error_lines": [],
        "parent_train_events": [], "parent_spawns": [],
        "run_identity": job.get("run_identity"),
        "provenance": provenance(job.get("run_identity")),
    }
    try:
        ref_c = make_referee(spec)
        t_c, c_c = rt.run_binary_custom(Path(job["candidate"]), ref_c, turns)
    except (RuntimeError, OSError) as exc:
        row["violations"].append({
            "property": "P0", "detail": "candidate crashed / closed stdout "
            "early: %s" % exc})
        row.update({"block": True, "banana_active": False, "turns": 0,
                    "detector_counts": {}, "candidate": None,
                    "parent": None, "artifacts": {}})
        return row
    _record_execution(row, ref_c)
    try:
        ref_p = make_referee(spec)
        t_p, c_p = rt.run_binary_custom(Path(job["parent"]), ref_p, turns)
    except (RuntimeError, OSError) as exc:
        raise PanelError("parent crashed on %s seat %d: %s"
                         % (spec["map_id"], spec["seat"], exc))
    _record_execution(row, ref_p, seat="parent")
    tr_c = td.build_trace(t_c, c_c)
    tr_p = td.build_trace(t_p, c_p)
    parent_cmds = td.CommandParser().parse(c_p)
    parent_d1 = td.detect_d1(tr_p)

    detectors, p1_viol, inherited, d9_dropped = eval_p1(
        tr_c, tr_p, parent_cmds, parent_d1["verdict"] == "FAIL")
    _, p2_alt, p2_horizon = eval_p2(tr_c)
    p3_viol = eval_p3(spec["orchard_eligible"], c_c, c_p)
    # ref_c has applied C_T (and its end-of-turn growth / opponent step), so
    # it IS the post-C_T referee world state P4's final-turn clause needs.
    p4_viol = eval_p4(tr_c, tr_p, job["liveness_window"],
                      post_ct_state(ref_c))

    margin_c = score(ref_c.inv) - score(ref_c.opp_inv)
    margin_p = score(ref_p.inv) - score(ref_p.opp_inv)
    banana_active = "BANANA" in c_c.upper()

    for r in p1_viol:
        row["violations"].append({
            "property": "P1", "detector": r["detector"],
            "count": r["count"], "episodes": r["episodes"][:5]})
    for v in p2_alt:
        row["violations"].append({"property": "P2", "detail": v["why"],
                                  "unit": v["unit"]})
    for v in p3_viol:
        row["violations"].append({"property": "P3", "detail": v})
    for v in p4_viol:
        row["violations"].append({"property": "P4", "detail": v})

    # RAW gate (owner ruling 2026-08-06): no inherited-parent-D1 /
    # inherited-parent-D9 downgrades exist any more -- eval_p1 returns those
    # channels empty and every detector episode is already a blocking P1
    # violation above.
    assert not inherited and not d9_dropped
    for v in p2_horizon:
        row["flags"].append({"flag": "r5-horizon", "detail": v["why"],
                             "unit": v["unit"]})
    if banana_active and margin_c < margin_p - job["margin_threshold"]:
        row["flags"].append({
            "flag": "margin-collapse",
            "detail": "banana-activated map: candidate margin %d < parent "
                      "margin %d - %d" % (margin_c, margin_p,
                                          job["margin_threshold"])})

    row.update({
        "turns": tr_c.T,
        "banana_active": banana_active,
        "candidate": {"inventory": list(ref_c.inv),
                      "opp_inventory": list(ref_c.opp_inv),
                      "score": score(ref_c.inv),
                      "opp_score": score(ref_c.opp_inv),
                      "margin": margin_c},
        "parent": {"inventory": list(ref_p.inv),
                   "opp_inventory": list(ref_p.opp_inv),
                   "score": score(ref_p.inv),
                   "opp_score": score(ref_p.opp_inv),
                   "margin": margin_p},
        "detector_counts": {r["detector"]: r["count"] for r in detectors},
        "block": bool(row["violations"]),
        "artifacts": {
            "candidate_transcript": t_c, "candidate_commands": c_c,
            "candidate_opponent_commands": "\n".join(
                ref_c.opponent_commands) + "\n",
            "parent_transcript": t_p, "parent_commands": c_p,
            "parent_opponent_commands": "\n".join(
                ref_p.opponent_commands) + "\n",
            "detectors": detectors,
        },
    })
    return row


# ---------------------------------------------------------------------------
# Panel driver
# ---------------------------------------------------------------------------

def load_config(path: Path) -> dict:
    try:
        raw = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise PanelError("cannot load config %s: %s" % (path, exc))
    cfg = dict(DEFAULTS)
    cfg.update(raw)
    cfg["config_dir"] = path.resolve().parent
    if not cfg.get("seeds"):
        raise PanelError("config must declare a non-empty seed list")
    for key in ("candidate", "parent"):
        if key not in cfg or "source" not in cfg[key]:
            raise PanelError("config must declare %s.source" % key)
    unknown = set(cfg["class_mix"]) - set(MAP_CLASSES)
    if unknown:
        raise PanelError("unknown map classes in class_mix: %s"
                         % sorted(unknown))
    unknown = set(cfg["opponent_mix"]) - set(OPP_PROFILES)
    if unknown:
        raise PanelError("unknown opponent profiles: %s" % sorted(unknown))
    # FAIL CLOSED (review B7).  The keys must be present in the RAW json --
    # not merged in from DEFAULTS -- or a config that declares no corpus at
    # all silently inherits the current identity and passes.
    for key, current in (("instrument_version", INSTRUMENT_VERSION),
                         ("corpus_version", CORPUS_VERSION)):
        if key not in raw:
            raise PanelError(
                "config does not declare %s. Every config must state the "
                "corpus/instrument identity its results belong to; a missing "
                "declaration must never inherit the running panel's identity "
                "(this panel is %r)." % (key, current))
        if cfg[key] != current:
            raise PanelError(
                "%s mismatch: config declares %r, this panel is %r. Results "
                "are not comparable across instrument versions -- rerun the "
                "corpus rather than compare across the bump."
                % (key, cfg[key], current))
    _check_run_identity(cfg, raw)
    return cfg


def _check_run_identity(cfg, raw) -> None:
    """REVIEW B5.  A floor claim made from a candidate config must be
    IMPOSSIBLE, not merely discouraged.

    r3's only committed config named the banana candidate against the parent
    -- the 123-blocking CANDIDATE run -- while the report quoted a 119 FLOOR
    obtained by substituting the parent into `candidate.source` in a config
    that was never committed.  The two runs answer different questions and
    are trivially confusable once separated from their config, so the config
    must now DECLARE which run it is, and the declaration is checked against
    the actual bytes of the two sources:

        floor      candidate.source and parent.source are the same bytes
                   (the parent judged against itself);
        candidate  they differ.

    The identity is then carried into the report title, the JSON packet and
    every row, so a published number cannot be relabelled either."""
    identity = raw.get("run_identity")
    if identity not in RUN_IDENTITIES:
        raise PanelError(
            "config must declare run_identity as one of %s (declared: %r). "
            "The floor (the parent judged against itself) and a candidate "
            "run are different measurements; an undeclared config lets one "
            "be quoted as the other."
            % (" / ".join(repr(v) for v in RUN_IDENTITIES), identity))
    digests = {}
    for key in ("candidate", "parent"):
        source = resolve(cfg, cfg[key]["source"])
        if not source.exists():
            raise PanelError("%s source missing: %s" % (key, source))
        digests[key] = sha256_path(source)
    same = digests["candidate"] == digests["parent"]
    if identity == RUN_IDENTITY_FLOOR and not same:
        raise PanelError(
            "run_identity 'floor' requires the parent judged against ITSELF, "
            "but candidate.source (%s) and parent.source (%s) are different "
            "bytes. This config measures a candidate, not the floor."
            % (digests["candidate"][:16], digests["parent"][:16]))
    if identity == RUN_IDENTITY_CANDIDATE and same:
        raise PanelError(
            "run_identity 'candidate' requires two different bots, but both "
            "sources are the same bytes (%s). A parent-versus-parent run is "
            "the floor: declare run_identity 'floor'."
            % digests["candidate"][:16])
    for key in ("candidate", "parent"):
        declared = cfg[key].get("sha256")
        if declared and not digests[key].startswith(declared.rstrip(".")):
            raise PanelError(
                "%s sha256 mismatch: declared %s, actual %s"
                % (key, declared, digests[key]))


def resolve(cfg, path: str) -> Path:
    p = Path(path)
    return p if p.is_absolute() else (cfg["config_dir"] / p).resolve()


def compile_bot(cfg, key: str, workdir: Path) -> Path:
    entry = cfg[key]
    source = resolve(cfg, entry["source"])
    if not source.exists():
        raise PanelError("%s source missing: %s" % (key, source))
    digest = sha256_path(source)
    declared = entry.get("sha256")
    if declared and not digest.startswith(declared.rstrip(".")):
        raise PanelError(
            "%s sha256 mismatch: declared %s, actual %s (%s)"
            % (key, declared, digest, source))
    cache_dir = cfg.get("bin_cache_dir")
    if cache_dir:
        cache = resolve(cfg, cache_dir)
        cache.mkdir(parents=True, exist_ok=True)
        out = cache / ("bot-%s" % digest[:16])
        if not out.exists():
            sh.compile_text(source.read_text(), out,
                            entry.get("crate", "fuzz_bot_" + key))
        return out
    out = workdir / ("bot-%s" % digest[:16])
    if not out.exists():
        sh.compile_text(source.read_text(), out,
                        entry.get("crate", "fuzz_bot_" + key))
    return out


def build_jobs(cfg, candidate: Path, parent: Path):
    n = int(cfg["maps"])
    classes = schedule(cfg["class_mix"], n)
    profiles = schedule(cfg["opponent_mix"], n)
    jobs = []
    for i in range(n):
        skel, specs = build_skeleton(i, classes[i], profiles[i], cfg)
        for spec in specs:
            jobs.append({
                "spec": spec,
                "turns": int(cfg["turns"]),
                "liveness_window": int(cfg["liveness_window"]),
                "margin_threshold": int(cfg["margin_collapse_threshold"]),
                "candidate": str(candidate),
                "parent": str(parent),
                "run_identity": cfg.get("run_identity"),
            })
    return jobs


def save_failure(base: Path, row: dict):
    d = base / ("%s-s%d" % (row["map_id"], row["seat"]))
    d.mkdir(parents=True, exist_ok=True)
    art = row.get("artifacts", {})
    spec = dict(row)
    spec.pop("artifacts", None)
    (d / "properties.json").write_text(
        json.dumps(spec, indent=1, sort_keys=True) + "\n")
    for name, key in (("candidate-transcript.txt", "candidate_transcript"),
                      ("candidate-commands.txt", "candidate_commands"),
                      ("candidate-opponent-commands.txt",
                       "candidate_opponent_commands"),
                      ("parent-transcript.txt", "parent_transcript"),
                      ("parent-commands.txt", "parent_commands"),
                      ("parent-opponent-commands.txt",
                       "parent_opponent_commands")):
        if key in art:
            (d / name).write_text(art[key])
    if "detectors" in art:
        (d / "detectors.json").write_text(
            json.dumps(art["detectors"], indent=1, sort_keys=True) + "\n")


def write_games_archive(cfg, rows):
    games_dir = cfg.get("games_dir")
    if not games_dir:
        return None
    out_dir = resolve(cfg, games_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "games.jsonl.gz"
    with gzip.open(out, "wt", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    return out


def summarize(cfg, rows, wall_time):
    stats = {
        "maps": int(cfg["maps"]),
        "games": len(rows),
        "turns_per_game": int(cfg["turns"]),
        "by_class": {},
        "by_profile": {},
        "banana_activated_games": sum(1 for r in rows if r["banana_active"]),
        "orchard_eligible_games": sum(1 for r in rows
                                      if r["orchard_eligible"]),
        "orchard_inertness_checks_passed": sum(
            1 for r in rows if r["orchard_eligible"]
            and not any(v["property"] == "P3" for v in r["violations"])),
        "blocking_games": sum(1 for r in rows if r["block"]),
        "flagged_games": sum(1 for r in rows if r["flags"]),
        # contract §8: rows with incomplete command execution stay in the
        # denominator and are reported, never dropped.
        "clean_games": sum(1 for r in rows if not r["block"]),
        "instrument_invalid_games": sum(
            1 for r in rows
            if r.get("execution_status", EXECUTION_OK) != EXECUTION_OK),
        # review B3: the parent seat is counted and reported too, and
        # `gate_unready_games` is the union that drives the aggregate.
        "parent_instrument_invalid_games": sum(
            1 for r in rows
            if r.get("parent_execution_status",
                     EXECUTION_OK) != EXECUTION_OK),
        "gate_unready_games": sum(1 for r in rows if row_execution_failed(r)),
        "unsupported_command_games": sum(
            1 for r in rows
            if r.get("execution_status") == ERROR_UNSUPPORTED_VERB),
        "malformed_command_games": sum(
            1 for r in rows if r.get("execution_status") == ERROR_MALFORMED),
        "games_with_a_successful_train": sum(
            1 for r in rows if r.get("spawns")),
        "successful_train_events": sum(
            len(r.get("spawns", [])) for r in rows),
        "wall_time_seconds": round(wall_time, 2),
    }
    for r in rows:
        stats["by_class"][r["class"]] = stats["by_class"].get(
            r["class"], 0) + 1
        stats["by_profile"][r["profile"]] = stats["by_profile"].get(
            r["profile"], 0) + 1
    return stats


def write_report(path: Path, cfg, rows, stats, verdict,
                 extra_sections=None):
    identity = cfg.get("run_identity")
    label = {RUN_IDENTITY_FLOOR: "FLOOR (the parent judged against ITSELF)",
             RUN_IDENTITY_CANDIDATE: "CANDIDATE (candidate vs parent)"}.get(
                 identity, "UNDECLARED")
    lines = []
    lines.append("# fuzz panel report [%s] - %s"
                 % (label, cfg.get("task", "<unnamed>")))
    lines.append("")
    lines.append("- **run identity: `%s` -- %s**. A number from this report "
                 "may only ever be quoted as a %s number (review B5)."
                 % (identity, label, identity))
    lines.append("- instrument: `%s`  |  corpus: `%s`"
                 % (cfg.get("instrument_version", INSTRUMENT_VERSION),
                    cfg.get("corpus_version", CORPUS_VERSION)))
    lines.append("- referee sha256: `%s`  |  engine.rs sha256: `%s`"
                 % (referee_sha256(), engine_sha256()))
    lines.append("- phase order: %s (rust/src/game/engine.rs:755-806)"
                 % " -> ".join(PHASE_ORDER))
    lines.append("- supported commands: %s (an unimplemented verb is a "
                 "retained `unsupported_verb` error: the row stays in the "
                 "denominator and the aggregate is GATE_UNREADY)"
                 % " ".join(sorted(SUPPORTED_COMMANDS)))
    lines.append("- candidate: `%s` (sha256 %s)"
                 % (cfg["candidate"]["source"],
                    cfg["candidate"].get("sha256", "?")))
    lines.append("- parent: `%s` (sha256 %s)"
                 % (cfg["parent"]["source"], cfg["parent"].get("sha256", "?")))
    lines.append("- seeds: %s" % cfg["seeds"])
    lines.append("- maps: %d (x2 seats = %d candidate games + %d parent "
                 "games), %d turns each"
                 % (stats["maps"], stats["games"], stats["games"],
                    stats["turns_per_game"]))
    lines.append("- wall time: %.1f s" % stats["wall_time_seconds"])
    lines.append("")
    lines.append("## Verdict: %s (%s run)" % (verdict, identity))
    lines.append("")
    lines.append("## Coverage")
    lines.append("")
    lines.append("| metric | value |")
    lines.append("|---|---|")
    for k in ("games", "clean_games", "banana_activated_games",
              "orchard_eligible_games", "orchard_inertness_checks_passed",
              "blocking_games", "flagged_games", "instrument_invalid_games",
              "parent_instrument_invalid_games", "gate_unready_games",
              "unsupported_command_games", "malformed_command_games",
              "games_with_a_successful_train", "successful_train_events"):
        lines.append("| %s | %s |" % (k, stats[k]))
    lines.append("")
    invalid = [r for r in rows if row_execution_failed(r)]
    if invalid:
        lines.append("## Instrument-invalid rows (GATE_UNREADY, retained "
                     "in the denominator)")
        lines.append("")
        lines.append("The complete, uncapped error stream for every row -- "
                     "verbatim fragment, exact `[start, end)` span, the "
                     "verbatim stdout line and its sha256 -- is in the JSON "
                     "packet (review B4); this table shows the first %d."
                     % REPORT_ERROR_ROWS)
        lines.append("")
        lines.append("| map | seat | who | status | errors | first raw "
                     "command |")
        lines.append("|---|---|---|---|---|---|")
        shown = 0
        for r in invalid:
            for who, skey, ekey, tkey in (
                    ("candidate", "execution_status", "command_errors",
                     "command_error_total"),
                    ("parent", "parent_execution_status",
                     "parent_command_errors", "parent_command_error_total")):
                if r.get(skey, EXECUTION_OK) == EXECUTION_OK:
                    continue
                if shown >= REPORT_ERROR_ROWS:
                    continue
                shown += 1
                first = r[ekey][0]["raw"] if r[ekey] else "?"
                lines.append("| %s | %d | %s | %s | %d | `%s` |"
                             % (r["map_id"], r["seat"], who, r[skey],
                                r.get(tkey, 0), first))
        lines.append("")
    lines.append("| class | games |")
    lines.append("|---|---|")
    for k, v in sorted(stats["by_class"].items()):
        lines.append("| %s | %d |" % (k, v))
    lines.append("")
    lines.append("| opponent profile | games |")
    lines.append("|---|---|")
    for k, v in sorted(stats["by_profile"].items()):
        lines.append("| %s | %d |" % (k, v))
    lines.append("")
    blocking = [r for r in rows if r["block"]]
    if blocking:
        lines.append("## Blocking violations")
        lines.append("")
        for r in blocking:
            lines.append("### %s seat %d (%s, %s, seed %d)"
                         % (r["map_id"], r["seat"], r["class"], r["profile"],
                            r["seed"]))
            lines.append("")
            for v in r["violations"]:
                lines.append("- **%s**: %s" % (
                    v["property"],
                    json.dumps({k: vv for k, vv in v.items()
                                if k != "property"}, sort_keys=True)[:600]))
            lines.append("")
    flagged = [r for r in rows if r["flags"]]
    if flagged:
        lines.append("## Report-tier flags (non-blocking)")
        lines.append("")
        for r in flagged:
            for f in r["flags"]:
                lines.append("- %s seat %d [%s]: %s"
                             % (r["map_id"], r["seat"], f["flag"],
                                f["detail"]))
        lines.append("")
    # --p4b (2026-08-25, coordinator order 20260825T181413Z): report-tier
    # only, appended after the panel's own sections and before the verdict.
    # With the flag OFF `extra_sections` is None and this file's output is
    # unchanged.
    if extra_sections:
        lines.extend(extra_sections)
    lines.append("---")
    lines.append("")
    lines.append("**VERDICT: %s -- %s**" % (verdict, label))
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


# --- P4b per-troll stall gate (integrated 2026-08-25) ----------------------
# codex_1's accepted G-1 evaluator, claude_1/pipeline/p4b_gate.py, wired in
# BEHIND A FLAG, DEFAULT OFF.  With --p4b absent nothing below runs, nothing
# is imported, and every byte of the report, the JSON packet and the games
# archive is what it was before the flag existed (the sole exceptions are the
# two self-referential fields every edit to this file moves: `referee sha256`
# -- this file's own digest -- and the measured wall time).


def stream_digest(rows) -> str:
    """sha256 of the DECOMPRESSED canonical jsonl stream.  Deliberately not
    the .gz file digest: a gzip member embeds an mtime, so a file digest
    cannot be reproduced from a fresh regeneration (the erratum on the G-1
    provenance table, coordinator order 20260825T181413Z item 2)."""
    h = hashlib.sha256()
    for row in rows:
        h.update((json.dumps(row, sort_keys=True) + "\n").encode("utf-8"))
    return h.hexdigest()


def load_archive_rows(path: Path) -> list:
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh]


def p4b_evaluate(rows, archive_path, baseline_path):
    """Build the embedded P4b packet from the panel's own rows."""
    sys.path[:0] = [str(HERE.parent / "narrate4")]
    import narrate4 as n4                          # noqa: PLC0415
    import p4b_gate                                # noqa: PLC0415
    baseline = None
    if baseline_path is not None:
        b_rows = load_archive_rows(baseline_path)
        baseline = p4b_gate.evaluate_rows(
            b_rows, td, n4, str(baseline_path), stream_digest(b_rows))
    label = str(archive_path) if archive_path else "(panel rows, not archived)"
    return p4b_gate.panel_packet(rows, td, n4, label, stream_digest(rows),
                                 baseline=baseline)


def run_panel(cfg, report_path: Path, json_path: Path | None,
              save_failures: Path | None, p4b: bool = False,
              p4b_baseline: Path | None = None) -> int:
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="fuzz-panel-") as workdir:
        candidate = compile_bot(cfg, "candidate", Path(workdir))
        parent = compile_bot(cfg, "parent", Path(workdir))
        jobs = build_jobs(cfg, candidate, parent)
        procs = int(cfg["processes"]) or min(
            8, multiprocessing.cpu_count())
        if procs > 1 and len(jobs) > 1:
            with multiprocessing.get_context("fork").Pool(procs) as pool:
                rows = pool.map(run_pair, jobs)
        else:
            rows = [run_pair(job) for job in jobs]
    rows.sort(key=lambda r: (r["map_id"], r["seat"]))
    wall_time = time.monotonic() - started

    if save_failures is not None:
        for row in rows:
            if row["block"] or row["flags"]:
                save_failure(save_failures, row)
    archive_path = write_games_archive(cfg, rows)

    stats = summarize(cfg, rows, wall_time)
    verdict = aggregate_verdict(rows)
    p4b_packet, p4b_sections = None, None
    if p4b:
        p4b_packet = p4b_evaluate(rows, archive_path, p4b_baseline)
        import p4b_gate                            # noqa: PLC0415
        p4b_sections = p4b_gate.render_markdown(p4b_packet)
    write_report(report_path, cfg, rows, stats, verdict, p4b_sections)
    if json_path is not None:
        slim = []
        for row in rows:
            r = dict(row)
            r.pop("artifacts", None)
            slim.append(r)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(
            {"task": cfg.get("task"), "verdict": verdict, "stats": stats,
             "run_identity": cfg.get("run_identity"),
             "instrument_version": cfg.get("instrument_version",
                                           INSTRUMENT_VERSION),
             "corpus_version": cfg.get("corpus_version", CORPUS_VERSION),
             "referee_sha256": referee_sha256(),
             "engine_sha256": engine_sha256(),
             "candidate_sha256": sha256_path(resolve(
                 cfg, cfg["candidate"]["source"])),
             "parent_sha256": sha256_path(resolve(
                 cfg, cfg["parent"]["source"])),
             "provenance": provenance(cfg.get("run_identity")),
             **({"p4b": p4b_packet} if p4b_packet is not None else {}),
             "games": slim}, indent=1, sort_keys=True) + "\n")
    print("fuzz_panel: %s [%s run] (%d games, %d blocking, %d flagged, %d "
          "gate-unready, %.1f s; report: %s)"
          % (verdict, cfg.get("run_identity"), stats["games"],
             stats["blocking_games"], stats["flagged_games"],
             stats["gate_unready_games"], wall_time, report_path))
    # GATE_UNREADY is an instrument failure, not a candidate verdict: the
    # evidence packet IS published (every affected row retained) and the
    # process still exits 2 so no caller can mistake it for a verdict.
    if verdict == "GATE_UNREADY":
        return EXIT_ERROR
    return EXIT_CLEAR if verdict == "CLEAR" else EXIT_BLOCK


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="fuzz_panel",
        description="randomized closed-loop property panel (final gate)")
    parser.add_argument("--config", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--json", dest="json_out")
    parser.add_argument("--save-failures", dest="save_failures")
    parser.add_argument(
        "--p4b", action="store_true",
        help="report-tier P4b per-troll stall gate (default OFF; the run's "
             "charter decides the flag, and a P4b failure does NOT change "
             "the panel verdict)")
    parser.add_argument(
        "--p4b-baseline", dest="p4b_baseline",
        help="games.jsonl.gz of the arm to difference against (optional)")
    args = parser.parse_args(argv)
    try:
        cfg = load_config(Path(args.config))
        return run_panel(
            cfg, Path(args.report),
            Path(args.json_out) if args.json_out else None,
            Path(args.save_failures) if args.save_failures else None,
            p4b=args.p4b,
            p4b_baseline=(Path(args.p4b_baseline) if args.p4b_baseline
                          else None))
    except PanelError as exc:
        print("fuzz_panel: tool/config error: %s" % exc, file=sys.stderr)
        return EXIT_ERROR
    except Exception as exc:                        # noqa: BLE001
        print("fuzz_panel: unexpected error: %r" % exc, file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
