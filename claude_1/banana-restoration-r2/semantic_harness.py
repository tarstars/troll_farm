#!/usr/bin/env python3
"""Semantic test harness skeleton for the banana wood-printer restoration (r2).

Mirrors the house pattern of harness-example-validate_semantics.py: synthetic
GameState construction in Python, serialization through the bot's exact stdin
protocol (static map header + per-turn blocks), one compiled-binary run per
payload, assertions over the emitted command lines.

Two fixture tiers:

* TIER-P (runnable now): parent-dormancy fixtures. States in which no banana
  behavior exists; the frozen parent (parent-a8eb3b2b.min.rs) is executed and
  its outputs are recorded as golden reference streams (tier-p-golden.json).
  Several TIER-C fixtures later assert byte-equality against these goldens.

* TIER-C (implemented now, expected to run once a candidate exists): one
  fixture family per acceptance-check-7 area, asserting the predicates of
  invariant-spec-2026-08-04.md. Run with --candidate <path> to execute them;
  without a candidate they are reported as PENDING_CANDIDATE.

Protocol (verified against the parent's protocol module):
  static: "W H" + H rows ('0' own shack, '1' enemy shack, '.' walkable,
          '+' iron, '~' water, anything else wall; shack/iron/water cells are
          NOT walkable)
  per turn: own inventory (6 ints: PLUM LEMON APPLE BANANA IRON WOOD),
            opponent inventory (6 ints), plant count,
            per plant: KIND x y size health fruits cooldown,
            unit count,
            per unit: id player x y move cap harvest chop carry0..carry5
  output: one line per turn, commands joined by ';'.

Mechanics constants used by fixtures: banana plant cooldown 6 (wet 4),
tree health 2+size, WOOD_POINTS 4, plot = walkable Chebyshev-1 ring of the
own tent, |plot| <= 8, TOTAL_TURNS 300, T_late(dry, chop 1) = 282.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from collections import deque
from pathlib import Path

SCRATCH = Path(
    "/tmp/claude-1000/-home-tarstars-prj-troll-farm/"
    "3b336b91-cd2f-4655-9aaf-31fd6d3d156f/scratchpad/banana"
)
DEFAULT_PARENT = SCRATCH / "parent-a8eb3b2b.min.rs"
HERE = Path(__file__).resolve().parent
DEFAULT_GOLDEN = HERE / "tier-p-golden.json"

CD_DRY = 6
CD_WET = 4
WOOD_POINTS = 4
TOTAL_TURNS = 300
# T_late for a dry cell, chop_power 1: 300 - (2*CD_dry + ceil(health(2)/1) + 2)
T_LATE_DRY = TOTAL_TURNS - (2 * CD_DRY + 4 + 2)  # = 282

VALID_ARITIES = {
    "WAIT": 1,
    "MOVE": 4,
    "CHOP": 2,
    "HARVEST": 2,
    "DROP": 2,
    "PLANT": 3,
    "PICK": 3,
    "MINE": 2,
    "TRAIN": 5,
}


# --------------------------------------------------------------------------
# Compile / run plumbing
# --------------------------------------------------------------------------

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def rustc_env() -> dict:
    env = dict(os.environ)
    cargo_bin = str(Path.home() / ".cargo" / "bin")
    if cargo_bin not in env.get("PATH", ""):
        env["PATH"] = cargo_bin + os.pathsep + env.get("PATH", "")
    return env


def compile_text(source: str, output: Path, crate: str) -> None:
    completed = subprocess.run(
        [
            "rustc",
            "--edition=2021",
            "-O",
            "-Awarnings",
            "--crate-name",
            crate,
            "-",
            "-o",
            str(output),
        ],
        input=source,
        text=True,
        capture_output=True,
        timeout=240,
        env=rustc_env(),
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr[:4000])


def commands(line: str) -> list[str]:
    return [
        command.strip()
        for command in re.split(r"[;\n]", line)
        if command.strip() and not command.strip().upper().startswith("MSG ")
    ]


def validate_command(command: str) -> None:
    parts = command.split()
    verb = parts[0].upper() if parts else ""
    if verb not in VALID_ARITIES or len(parts) != VALID_ARITIES[verb]:
        raise AssertionError(f"malformed command: {command!r}")
    integer_fields = {
        "MOVE": (1, 2, 3),
        "CHOP": (1,),
        "HARVEST": (1,),
        "DROP": (1,),
        "PLANT": (1,),
        "PICK": (1,),
        "MINE": (1,),
        "TRAIN": (1, 2, 3, 4),
    }.get(verb, ())
    for index in integer_fields:
        int(parts[index])


def run(binary: Path, payload: str) -> tuple[list[list[str]], str, str]:
    completed = subprocess.run(
        [str(binary)],
        input=payload,
        text=True,
        capture_output=True,
        timeout=60,
    )
    if completed.returncode:
        raise RuntimeError(
            f"bot exited {completed.returncode}: {completed.stderr[:1000]}"
        )
    lines = completed.stdout.splitlines()
    parsed = [commands(line) for line in lines]
    for row in parsed:
        for command in row:
            validate_command(command)
    return parsed, completed.stdout, completed.stderr


def run_deterministic(binary: Path, payload: str) -> tuple[list[list[str]], str, str]:
    parsed, stdout_a, stderr = run(binary, payload)
    _, stdout_b, _ = run(binary, payload)
    if stdout_a != stdout_b:
        raise AssertionError("nondeterministic output for identical payload")
    return parsed, stdout_a, stderr


# --------------------------------------------------------------------------
# State builders (house pattern: tuples serialized positionally)
# --------------------------------------------------------------------------

def unit(
    unit_id: int,
    player: int,
    x: int,
    y: int,
    *,
    movement: int = 1,
    capacity: int = 2,
    harvest: int = 0,
    chop: int = 1,
    carry: tuple[int, int, int, int, int, int] = (0, 0, 0, 0, 0, 0),
) -> tuple[int, ...]:
    return (unit_id, player, x, y, movement, capacity, harvest, chop, *carry)


def plant(
    kind: str,
    x: int,
    y: int,
    *,
    size: int = 4,
    health: int | None = None,
    fruits: int = 0,
    cooldown: int = 0,
) -> tuple:
    if health is None:
        health = {"PLUM": 4, "LEMON": 4, "APPLE": 8, "BANANA": 2}[kind] + {
            "PLUM": 2,
            "LEMON": 2,
            "APPLE": 3,
            "BANANA": 1,
        }[kind] * size
    return (kind, x, y, size, health, fruits, cooldown)


def turn_text(
    *,
    inventory: tuple[int, int, int, int, int, int] = (0, 0, 0, 0, 0, 0),
    opponent_inventory: tuple[int, int, int, int, int, int] = (0, 0, 0, 0, 0, 0),
    plants: tuple[tuple, ...] = (),
    units: tuple[tuple[int, ...], ...] = (),
) -> str:
    lines = [
        " ".join(map(str, inventory)),
        " ".join(map(str, opponent_inventory)),
        str(len(plants)),
    ]
    lines.extend(" ".join(map(str, row)) for row in plants)
    lines.append(str(len(units)))
    lines.extend(" ".join(map(str, row)) for row in units)
    return "\n".join(lines) + "\n"


def transcript(rows: tuple[str, ...], turns: list[str]) -> str:
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("map rows have inconsistent widths")
    return f"{width} {len(rows)}\n" + "\n".join(rows) + "\n" + "".join(turns)


# --------------------------------------------------------------------------
# Map geometry helpers (mirror of the bot's parse_static_map / bfs / ring)
# --------------------------------------------------------------------------

def parse_rows(rows: tuple[str, ...]) -> dict:
    walkable, iron, water = set(), set(), set()
    shacks = {}
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            cell = (x, y)
            if ch == "0":
                shacks[0] = cell
            elif ch == "1":
                shacks[1] = cell
            elif ch == ".":
                walkable.add(cell)
            elif ch == "+":
                iron.add(cell)
            elif ch == "~":
                water.add(cell)
    return {"walkable": walkable, "shacks": shacks, "iron": iron, "water": water}


def bfs(walkable: set, sources: list) -> dict:
    dist = {}
    queue = deque()
    for cell in sources:
        if cell not in dist:
            dist[cell] = 0
            queue.append(cell)
    while queue:
        cell = queue.popleft()
        for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            nxt = (cell[0] + dx, cell[1] + dy)
            if nxt in walkable and nxt not in dist:
                dist[nxt] = dist[cell] + 1
                queue.append(nxt)
    return dist


def doors(geo: dict) -> list:
    tent = geo["shacks"][0]
    out = [
        (tent[0] + dx, tent[1] + dy)
        for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0))
    ]
    return sorted(cell for cell in out if cell in geo["walkable"])


def ring(geo: dict) -> set:
    tent = geo["shacks"][0]
    return {
        cell
        for cell in geo["walkable"]
        if max(abs(cell[0] - tent[0]), abs(cell[1] - tent[1])) == 1
    }


def orth_ring(geo: dict) -> set:
    return set(doors(geo))


def diag_ring(geo: dict) -> set:
    return ring(geo) - orth_ring(geo)


def door_distance(geo: dict, cell) -> int:
    dist = bfs(geo["walkable"], doors(geo))
    return dist.get(cell, 10_000)


# --------------------------------------------------------------------------
# Command-stream inspection helpers
# --------------------------------------------------------------------------

def banana_tokens(parsed: list[list[str]]) -> list[tuple[int, str]]:
    """(turn, command) pairs for every command mentioning BANANA."""
    return [
        (turn, command)
        for turn, row in enumerate(parsed, 1)
        for command in row
        if "BANANA" in command.upper()
    ]


def unit_commands(parsed: list[list[str]], unit_id: int) -> list[tuple[int, str]]:
    prefix_verbs = ("MOVE", "CHOP", "HARVEST", "DROP", "PLANT", "PICK", "MINE")
    out = []
    for turn, row in enumerate(parsed, 1):
        for command in row:
            parts = command.split()
            if parts[0] in prefix_verbs and int(parts[1]) == unit_id:
                out.append((turn, command))
    return out


def move_dest(command: str) -> tuple[int, int] | None:
    parts = command.split()
    if parts[0] == "MOVE":
        return (int(parts[2]), int(parts[3]))
    return None


def plant_banana_events(
    parsed: list[list[str]], positions: dict[int, tuple[int, int]]
) -> list[tuple[int, int, tuple[int, int]]]:
    """(turn, unit_id, scripted_cell) for every PLANT <id> BANANA command.

    PLANT carries no cell; the plant lands on the unit's cell. In open-loop
    scripted payloads the unit stays where the script puts it, so the scripted
    position of the unit at that turn is the plant cell.
    """
    events = []
    for turn, row in enumerate(parsed, 1):
        for command in row:
            parts = command.split()
            if parts[0] == "PLANT" and parts[2].upper() == "BANANA":
                uid = int(parts[1])
                events.append((turn, uid, positions[uid]))
    return events


def first_train(parsed: list[list[str]]) -> tuple[int, str] | None:
    for turn, row in enumerate(parsed, 1):
        for command in row:
            if command.startswith("TRAIN "):
                return (turn, command)
    return None


def period2_alternation(dests: list) -> bool:
    """True if four consecutive MOVE destinations form a,b,a,b with a != b."""
    for i in range(len(dests) - 3):
        a, b, c, d = dests[i : i + 4]
        if a is not None and b is not None and a != b and a == c and b == d:
            return True
    return False


# --------------------------------------------------------------------------
# Maps
# --------------------------------------------------------------------------

# Tiny corridor with no banana context at all: pure check-4 baseline.
MAP_PLAIN = ("0..........1",)

# Banana-eligible map: full 8-cell Chebyshev-1 ring around the own tent,
# NO water anywhere -> SecureOrchardBot::initialize finds no water-adjacent
# mother door -> orchard geometry None -> per I-28 the banana feature owns
# such maps (parent stays plain Moisan).
MAP_RING = (
    "..............",
    ".0...........1",
    "..............",
    "..............",
    "..............",
)
RING_GEO = parse_rows(MAP_RING)
RING_TENT = (1, 1)

# Orchard-eligible map: >= 2 doors, water (1,0) orthogonally adjacent to door
# (1,1), enemy door distance to that mother door >= 11, one natural lemon with
# home-door distance 12 >= 8 (median test). SecureOrchardBot geometry is Some
# here, so per I-27/I-28 the candidate must be byte-identical to the parent.
MAP_ORCHARD = (
    "#~..............",
    "0..............1",
    "................",
)

MAP_BANK = ("0......1",)
MAP_LATE = ("0.......1",)


# --------------------------------------------------------------------------
# Shared payload builders (used by TIER-P recording and TIER-C equality)
# --------------------------------------------------------------------------

def payload_baseline_plain() -> str:
    state = turn_text(
        plants=(
            plant("LEMON", 5, 0, size=4, health=12, fruits=1),
            plant("PLUM", 8, 0, size=4, health=12, fruits=1),
        ),
        units=(unit(0, 0, 1, 0, harvest=1, chop=1),),
    )
    return transcript(MAP_PLAIN, [state] * 4)


def payload_orchard_eligible() -> str:
    state = turn_text(
        plants=(plant("LEMON", 12, 2, size=4, health=12, fruits=1),),
        units=(unit(0, 0, 2, 1, harvest=1, chop=1),),
    )
    return transcript(MAP_ORCHARD, [state] * 6)


def payload_banana_inventory(worker_count: int, turns: int) -> str:
    units = [unit(0, 0, 3, 1, harvest=1, chop=1)]
    if worker_count >= 2:
        units.append(unit(1, 0, 5, 1, harvest=1, chop=1))
    state = turn_text(
        inventory=(0, 0, 0, 2, 0, 0),
        plants=(plant("PLUM", 10, 2, size=4, health=12, fruits=1),),
        units=tuple(units),
    )
    return transcript(MAP_RING, [state] * turns)


def payload_wood_banking() -> str:
    states = [
        turn_text(units=(unit(0, 0, 5, 0, carry=(0, 0, 0, 0, 0, 1)),)),
        turn_text(units=(unit(0, 0, 3, 0, carry=(0, 0, 0, 0, 0, 1)),)),
        turn_text(units=(unit(0, 0, 1, 0, carry=(0, 0, 0, 0, 0, 1)),)),
    ]
    return transcript(MAP_BANK, states)


def payload_two_worker() -> str:
    state = turn_text(
        plants=(plant("LEMON", 4, 1, size=4, health=12, fruits=1),),
        units=(
            unit(0, 0, 3, 1, harvest=1, chop=1),
            unit(1, 0, 5, 1, harvest=1, chop=1),
        ),
    )
    return transcript(MAP_RING, [state] * 2)


def payload_late_window() -> str:
    state = turn_text(
        inventory=(0, 0, 0, 3, 0, 0),
        plants=(plant("LEMON", 4, 0, size=1, health=6, fruits=0),),
        units=(unit(0, 0, 1, 0, harvest=1, chop=1),),
    )
    return transcript(MAP_LATE, [state] * 105)


def payload_training() -> str:
    state = turn_text(
        inventory=(10, 10, 10, 10, 10, 0),
        plants=(
            plant("PLUM", 2, 0, size=4, health=12, fruits=1),
            plant("LEMON", 5, 0, size=4, health=12, fruits=1),
        ),
        units=(unit(0, 0, 1, 0, harvest=1, chop=1),),
    )
    return transcript(MAP_PLAIN, [state] * 30)


# --------------------------------------------------------------------------
# TIER-P fixtures: parent-dormancy goldens (runnable now)
# --------------------------------------------------------------------------

def record(payload: str, parsed: list[list[str]], stdout: str, **extra) -> dict:
    return {
        "payload_sha256": sha256_bytes(payload.encode()),
        "turns": len(parsed),
        "golden_lines": stdout.splitlines(),
        "stdout_sha256": sha256_bytes(stdout.encode()),
        **extra,
    }


def p_baseline_plain(parent: Path) -> dict:
    """Check-4 baseline / I-1 dormancy default: a no-banana-context corridor.

    No banana in inventory, plants, or carry. The parent's stream is golden;
    TIER-C c_arbitration asserts the candidate is byte-identical on it.
    """
    payload = payload_baseline_plain()
    parsed, stdout, _ = run_deterministic(parent, payload)
    tokens = banana_tokens(parsed)
    if tokens:
        raise AssertionError(f"parent emitted banana commands: {tokens}")
    return record(payload, parsed, stdout)


def p_orchard_eligible(parent: Path) -> dict:
    """I-27/I-28 reference stream: orchard-eligible map (apple priority).

    Map satisfies every SecureOrchardBot::initialize gate (>= 2 doors,
    water-adjacent free door, enemy door distance >= 11, natural-median >= 8),
    so geometry is Some and per I-28 the banana feature must be permanently
    disabled: TIER-C asserts candidate == parent byte-for-byte here.
    """
    payload = payload_orchard_eligible()
    parsed, stdout, _ = run_deterministic(parent, payload)
    tokens = banana_tokens(parsed)
    if tokens:
        raise AssertionError(f"parent emitted banana commands: {tokens}")
    return record(payload, parsed, stdout)


def p_banana_inventory_dormant(parent: Path) -> dict:
    """I-1/I-2 reference: banana-eligible ring map, seeds banked, parent side.

    Two workers, inventory BANANA=2, no water (orchard-ineligible). The parent
    has no banana feature, so its stream defines 'banana-attributable = any
    difference from this golden' for the same payload (attribution seam).
    """
    payload = payload_banana_inventory(2, 5)
    parsed, stdout, _ = run_deterministic(parent, payload)
    tokens = banana_tokens(parsed)
    if tokens:
        raise AssertionError(f"parent emitted banana commands: {tokens}")
    return record(payload, parsed, stdout)


def p_wood_banking(parent: Path) -> dict:
    """B7 (I-19/I-20) parent reference: carried-wood return to the door.

    Scripted 3-turn approach (x=5 -> 3 -> 1) with 1 wood carried. Golden
    records the parent's banking discipline; observation notes whether the
    final adjacent turn banks (DROP).
    """
    payload = payload_wood_banking()
    parsed, stdout, _ = run_deterministic(parent, payload)
    tokens = banana_tokens(parsed)
    if tokens:
        raise AssertionError(f"parent emitted banana commands: {tokens}")
    final_drop = any(c.startswith("DROP ") for c in parsed[-1])
    return record(
        payload, parsed, stdout, observations={"final_turn_drops": final_drop}
    )


def p_two_worker(parent: Path) -> dict:
    """I-22/I-23 parent reference: two workers, one ripe tree.

    Observation records how many workers engage (parent's arbitration
    behavior on a shared candidate target).
    """
    payload = payload_two_worker()
    parsed, stdout, _ = run_deterministic(parent, payload)
    tokens = banana_tokens(parsed)
    if tokens:
        raise AssertionError(f"parent emitted banana commands: {tokens}")
    active = [c for c in parsed[0] if c != "WAIT"]
    return record(
        payload, parsed, stdout, observations={"turn1_active_commands": active}
    )


def p_late_window(parent: Path) -> dict:
    """I-1 activation-deadline reference: 105 turns, bananas banked, 1 worker.

    Single worker (the parent's turn>=100 regeneration PICK branch requires
    >= 2 workers, so it cannot fire): the parent must never mention BANANA
    over the whole 105-turn stream, giving a past-deadline dormancy golden.
    """
    payload = payload_late_window()
    parsed, stdout, _ = run_deterministic(parent, payload)
    tokens = banana_tokens(parsed)
    if tokens:
        raise AssertionError(f"parent emitted banana commands: {tokens}")
    return record(payload, parsed, stdout)


def p_training(parent: Path) -> dict:
    """I-17/I-18 funding reference: rich single-worker state, 30 turns.

    Records the parent's first TRAIN (turn + exact stats tuple). TIER-C
    c_arbitration asserts TRAIN parity; c_eta_suppression asserts funding
    phase byte-equality on this payload.
    """
    payload = payload_training()
    parsed, stdout, _ = run_deterministic(parent, payload)
    tokens = banana_tokens(parsed)
    if tokens:
        raise AssertionError(f"parent emitted banana commands: {tokens}")
    train = first_train(parsed)
    return record(
        payload,
        parsed,
        stdout,
        observations={
            "first_train": {"turn": train[0], "command": train[1]} if train else None
        },
    )


TIER_P = [
    ("p_baseline_plain", p_baseline_plain, ["check-4", "I-1"]),
    ("p_orchard_eligible", p_orchard_eligible, ["I-27", "I-28"]),
    ("p_banana_inventory_dormant", p_banana_inventory_dormant, ["I-1", "I-2"]),
    ("p_wood_banking", p_wood_banking, ["I-19", "I-20", "I-21"]),
    ("p_two_worker", p_two_worker, ["I-22", "I-23"]),
    ("p_late_window", p_late_window, ["I-1"]),
    ("p_training", p_training, ["I-16", "I-17", "I-18"]),
]


# --------------------------------------------------------------------------
# TIER-C fixtures: candidate assertions (implemented, run with --candidate)
# --------------------------------------------------------------------------

def c_bootstrap_budget(candidate: Path, parent: Path, golden: dict) -> dict:
    """Check-7 area: bootstrap. Invariants: I-1, I-2, I-16.

    (a) Single-worker banana-eligible state, 10 turns: activation requires the
        second worker (I-16), so candidate stdout must byte-equal the parent's
        on the identical payload.
    (b) Two-worker state, 40 turns, BANANA=2 banked: every PICK <id> BANANA is
        issued by the starter (min own id, I-2 bootstrap channel); the count of
        distinct PICK-BANANA decision turns is recorded (open-loop re-emission
        makes exact <=1 execution counting a replay-gate concern, not ours).
    """
    single = payload_banana_inventory(1, 10)
    parsed_c, stdout_c, _ = run_deterministic(candidate, single)
    _, stdout_p, _ = run_deterministic(parent, single)
    if stdout_c != stdout_p:
        raise AssertionError(
            "single-worker state is not dormant: candidate diverged from parent"
        )
    double = payload_banana_inventory(2, 40)
    parsed_d, _, _ = run_deterministic(candidate, double)
    picks = [
        (turn, command)
        for turn, command in banana_tokens(parsed_d)
        if command.startswith("PICK ")
    ]
    for turn, command in picks:
        if int(command.split()[1]) != 0:
            raise AssertionError(f"non-starter bootstrap PICK: turn {turn} {command}")
    return {"single_worker_byte_equal": True, "pick_banana_events": picks}


def c_bounded_placement(candidate: Path, parent: Path, golden: dict) -> dict:
    """Check-7 area: bounded placement. Invariants: I-12, I-13, I-15.

    For each scripted starter position: unit carries one banana; any
    PLANT <id> BANANA lands on the unit's scripted cell, so the candidate must
    never emit PLANT BANANA while positioned outside the walkable Chebyshev-1
    tent ring (I-12). Ring positions are controls (planting permitted, not
    required). Full-ring payload: all 8 ring cells planted -> no bank PICK of
    a seed (I-15 no full-ring PICK) and no PLANT at all (I-13 capacity).
    """
    ring_cells = ring(RING_GEO)
    non_ring = [(3, 0), (4, 1), (6, 2), (10, 0), (12, 2)]
    controls = [(2, 1), (0, 2)]
    results = {"non_ring": {}, "ring_controls": {}}
    for pos in non_ring + controls:
        state = turn_text(
            plants=(plant("PLUM", 10, 2, size=4, health=12, fruits=1),),
            units=(
                unit(0, 0, *pos, harvest=1, chop=1, carry=(0, 0, 0, 1, 0, 0)),
                unit(1, 0, 7, 1, harvest=1, chop=1),
            ),
        )
        parsed, _, _ = run_deterministic(candidate, transcript(MAP_RING, [state] * 30))
        events = plant_banana_events(parsed, {0: pos, 1: (7, 1)})
        for turn, uid, cell in events:
            if cell not in ring_cells:
                raise AssertionError(
                    f"PLANT BANANA outside Chebyshev-1 ring at {cell}, turn {turn}"
                )
        key = "ring_controls" if pos in controls else "non_ring"
        results[key][str(pos)] = len(events)
    full_ring_plants = tuple(
        plant("BANANA", *cell, size=2, health=4, fruits=0, cooldown=3)
        for cell in sorted(ring_cells)
    )
    state = turn_text(
        inventory=(0, 0, 0, 2, 0, 0),
        plants=full_ring_plants + (plant("PLUM", 10, 2, size=4, health=12, fruits=1),),
        units=(
            unit(0, 0, 3, 1, harvest=1, chop=1),
            unit(1, 0, 5, 1, harvest=1, chop=1),
        ),
    )
    parsed, _, _ = run_deterministic(candidate, transcript(MAP_RING, [state] * 10))
    for turn, command in banana_tokens(parsed):
        if command.startswith("PICK "):
            raise AssertionError(f"full-ring bank PICK at turn {turn}: {command}")
        if command.startswith("PLANT "):
            raise AssertionError(f"PLANT over full ring at turn {turn}: {command}")
    return results


def c_replant_renewable(candidate: Path, parent: Path, golden: dict) -> dict:
    """Check-7 area: renewable harvest/replant. Invariants: I-3, I-9.

    Diagonal mothers alive, one orthogonal ring vacancy, starter scripted on
    the vacancy carrying one seed, mid-window (turn ~50): within CD_dry = 6
    probe turns a PLANT BANANA must appear (I-3 replant latency when a seed
    exists). Surplus variant: ring full, starter carries two bananas away from
    the tent -> first command must be a door-approach MOVE or DROP (I-9).
    """
    mothers = (
        plant("BANANA", 0, 0, size=4, health=6, fruits=1, cooldown=2),
        plant("BANANA", 2, 2, size=4, health=6, fruits=1, cooldown=2),
    )
    state = turn_text(
        plants=mothers + (plant("PLUM", 10, 2, size=4, health=12, fruits=1),),
        units=(
            unit(0, 0, 2, 1, harvest=1, chop=1, carry=(0, 0, 0, 1, 0, 0)),
            unit(1, 0, 6, 1, harvest=1, chop=1),
        ),
    )
    parsed, _, _ = run_deterministic(
        candidate, transcript(MAP_RING, [state] * (49 + CD_DRY))
    )
    window = parsed[49 : 49 + CD_DRY]
    replants = [
        c for row in window for c in row if c.startswith("PLANT ") and "BANANA" in c
    ]
    if not replants:
        raise AssertionError(
            f"no PLANT BANANA within CD_dry={CD_DRY} probe turns on a ring vacancy"
        )
    ring_cells = sorted(ring(RING_GEO))
    full_ring = tuple(
        plant("BANANA", *cell, size=2, health=4, fruits=0, cooldown=3)
        for cell in ring_cells
    )
    surplus_pos = (10, 1)
    state2 = turn_text(
        plants=full_ring,
        units=(
            unit(0, 0, *surplus_pos, harvest=1, chop=1, carry=(0, 0, 0, 2, 0, 0)),
            unit(1, 0, 6, 3, harvest=1, chop=1),
        ),
    )
    parsed2, _, _ = run_deterministic(candidate, transcript(MAP_RING, [state2] * 60))
    last = [c for t, c in unit_commands(parsed2, 0) if t == 60]
    ok = False
    for command in last:
        if command.startswith("DROP "):
            ok = True
        dest = move_dest(command)
        if dest is not None and door_distance(RING_GEO, dest) < door_distance(
            RING_GEO, surplus_pos
        ):
            ok = True
    if not ok:
        raise AssertionError(f"surplus carrier neither banks nor approaches: {last}")
    return {"replant_commands": replants[:3], "surplus_final": last}


def c_late_conversion(candidate: Path, parent: Path, golden: dict) -> dict:
    """Check-7 area: late conversion. Invariants: I-4, I-5, I-6, I-14.

    (a) Turn ~260, starter standing ON a size-2 orthogonal ring banana (the
        parent's verb model emits CHOP/HARVEST only when unit.cell ==
        plant.cell), diagonal mother fruited one cell away: wood must win
        (I-6/I-4) -> a CHOP appears in the last 5 turns and no HARVEST does.
    (b) 296-turn stream with a seed on a ring vacancy: if any PLANT BANANA
        occurs, its first occurrence is <= 100 (I-1) and never after
        T_late = 282 (I-5, dry cell arithmetic).
    (c) Own-planted mother guard (I-14/D-8), multi-turn scripted narrative:
        invite a plant on diagonal (2,2), then script it grown to size 4 with
        the starter standing on it; if the candidate planted it, it must never
        CHOP that mother (HARVEST is the expected verb). INCONCLUSIVE if the
        candidate never planted.
    """
    state_a = turn_text(
        plants=(
            plant("BANANA", 2, 1, size=2, health=4, fruits=0, cooldown=0),
            plant("BANANA", 2, 2, size=4, health=6, fruits=2, cooldown=0),
            plant("PLUM", 10, 2, size=4, health=12, fruits=1),
        ),
        units=(
            unit(0, 0, 2, 1, harvest=1, chop=1),
            unit(1, 0, 8, 1, harvest=1, chop=1),
        ),
    )
    parsed_a, _, _ = run_deterministic(candidate, transcript(MAP_RING, [state_a] * 260))
    tail = parsed_a[-5:]
    chops = [c for row in tail for c in row if c.startswith("CHOP ")]
    harvests = [c for row in tail for c in row if c.startswith("HARVEST ")]
    if not chops or harvests:
        raise AssertionError(
            f"late wood cut did not dominate: chops={chops} harvests={harvests}"
        )
    seed_pos = (1, 2)
    state_b = turn_text(
        plants=(plant("PLUM", 10, 2, size=4, health=12, fruits=1),),
        units=(
            unit(0, 0, *seed_pos, harvest=1, chop=1, carry=(0, 0, 0, 1, 0, 0)),
            unit(1, 0, 6, 1, harvest=1, chop=1),
        ),
    )
    parsed_b, _, _ = run_deterministic(candidate, transcript(MAP_RING, [state_b] * 296))
    plant_turns = [
        turn
        for turn, command in banana_tokens(parsed_b)
        if command.startswith("PLANT ")
    ]
    if plant_turns and plant_turns[0] > 100:
        raise AssertionError(f"first PLANT BANANA at turn {plant_turns[0]} > 100")
    late = [turn for turn in plant_turns if turn > T_LATE_DRY]
    if plant_turns and late and late[0] != plant_turns[0]:
        # a fresh late decision (not open-loop re-emission of an early one)
        raise AssertionError(f"PLANT BANANA after T_late={T_LATE_DRY}: turns {late}")
    invite = turn_text(
        units=(
            unit(0, 0, 2, 2, harvest=1, chop=1, carry=(0, 0, 0, 1, 0, 0)),
            unit(1, 0, 6, 1, harvest=1, chop=1),
        ),
    )
    grown = turn_text(
        plants=(plant("BANANA", 2, 2, size=4, health=6, fruits=1, cooldown=2),),
        units=(
            unit(0, 0, 2, 2, harvest=1, chop=1),
            unit(1, 0, 6, 1, harvest=1, chop=1),
        ),
    )
    parsed_c, _, _ = run_deterministic(
        candidate, transcript(MAP_RING, [invite] * 10 + [grown] * 30)
    )
    planted = any(
        command.startswith("PLANT ") for _, command in banana_tokens(parsed_c[:10])
    )
    mother_status = "INCONCLUSIVE_NO_PLANT"
    if planted:
        mother_chops = [
            (turn, command)
            for turn, command in unit_commands(parsed_c[10:], 0)
            if command.startswith("CHOP ")
        ]
        if mother_chops:
            raise AssertionError(f"own diagonal mother chopped: {mother_chops}")
        mother_status = "PASS"
    return {
        "late_chops": chops,
        "plant_turns_first": plant_turns[:1],
        "mother_guard": mother_status,
    }


def c_banking(candidate: Path, parent: Path, golden: dict) -> dict:
    """Check-7 area: banking. Invariants: I-7, I-8, I-9.

    Starter on the last free ring door carrying two bananas, other 7 ring
    cells planted, turn ~60: within A = 6 probe turns it must resolve a
    carried banana via DROP (bank) or PLANT (the one replant-priority seed of
    I-9) -- carrying idly past the latency bound violates I-8. Far-carry
    variant: full worker (capacity 2, 2 bananas) far from tent must emit a
    door-approach MOVE (forced-banking analog of I-21). I-7's strict-ETA
    ownership predicate is exercised indirectly (no opponent present -> all
    fruit owned); the contested case needs the replay gate (see report gaps).
    """
    ring_cells = sorted(ring(RING_GEO))
    door_cell = (2, 1)
    others = tuple(
        plant("BANANA", *cell, size=2, health=4, fruits=0, cooldown=3)
        for cell in ring_cells
        if cell != door_cell
    )
    state = turn_text(
        plants=others,
        units=(
            unit(0, 0, *door_cell, harvest=1, chop=1, carry=(0, 0, 0, 2, 0, 0)),
            unit(1, 0, 6, 1, harvest=1, chop=1),
        ),
    )
    parsed, _, _ = run_deterministic(candidate, transcript(MAP_RING, [state] * 66))
    window = [c for t, c in unit_commands(parsed, 0) if t > 60]
    resolved = [
        c
        for c in window
        if c.startswith("DROP ") or (c.startswith("PLANT ") and "BANANA" in c)
    ]
    if not resolved:
        raise AssertionError(
            f"carried bananas neither banked nor planted within A=6: {window}"
        )
    far_pos = (11, 3)
    state2 = turn_text(
        plants=(plant("PLUM", 10, 2, size=4, health=12, fruits=1),),
        units=(
            unit(0, 0, *far_pos, harvest=1, chop=1, carry=(0, 0, 0, 2, 0, 0)),
            unit(1, 0, 6, 1, harvest=1, chop=1),
        ),
    )
    parsed2, _, _ = run_deterministic(candidate, transcript(MAP_RING, [state2] * 60))
    final = [c for t, c in unit_commands(parsed2, 0) if t == 60]
    approach = any(
        (dest := move_dest(c)) is not None
        and door_distance(RING_GEO, dest) < door_distance(RING_GEO, far_pos)
        for c in final
    )
    if not approach:
        raise AssertionError(f"full far carrier does not approach a door: {final}")
    return {"resolution": resolved[:2], "far_carrier_final": final}


def c_eta_suppression(candidate: Path, parent: Path, golden: dict) -> dict:
    """Check-7 area: enemy ETA suppression. Invariants: I-10, I-18 (+I-17).

    (a) Starter on a ring vacancy with a seed; opponent CHOPPER scripted 2 BFS
        moves away: eta_opp_x <= 2 forbids planting (I-10 second clause, a
        health-3 sapling loses that race) -> no PLANT BANANA on any turn.
        Control payload with the chopper 7 moves away records whether planting
        resumes (not asserted).
    (b) Funding phase (I-18/I-17): on the rich single-worker p_training
        payload the candidate must byte-equal the recorded parent golden.
    """
    seed_pos = (1, 2)
    threat = turn_text(
        plants=(plant("PLUM", 10, 2, size=4, health=12, fruits=1),),
        units=(
            unit(0, 0, *seed_pos, harvest=1, chop=1, carry=(0, 0, 0, 1, 0, 0)),
            unit(1, 0, 6, 1, harvest=1, chop=1),
            unit(2, 1, 1, 4, harvest=0, chop=1),
        ),
    )
    parsed, _, _ = run_deterministic(candidate, transcript(MAP_RING, [threat] * 50))
    plants_seen = [
        (turn, command)
        for turn, command in banana_tokens(parsed)
        if command.startswith("PLANT ")
    ]
    if plants_seen:
        raise AssertionError(
            f"PLANT BANANA under opponent chopper ETA<=2: {plants_seen[:3]}"
        )
    control = turn_text(
        plants=(plant("PLUM", 10, 2, size=4, health=12, fruits=1),),
        units=(
            unit(0, 0, *seed_pos, harvest=1, chop=1, carry=(0, 0, 0, 1, 0, 0)),
            unit(1, 0, 6, 1, harvest=1, chop=1),
            unit(2, 1, 8, 4, harvest=0, chop=1),
        ),
    )
    parsed_ctl, _, _ = run_deterministic(candidate, transcript(MAP_RING, [control] * 50))
    control_plants = [
        turn for turn, c in banana_tokens(parsed_ctl) if c.startswith("PLANT ")
    ]
    payload = payload_training()
    if sha256_bytes(payload.encode()) != golden["p_training"]["payload_sha256"]:
        raise AssertionError("p_training payload drifted from golden")
    _, stdout_c, _ = run_deterministic(candidate, payload)
    if stdout_c.splitlines() != golden["p_training"]["golden_lines"]:
        raise AssertionError("funding-phase stream diverged from parent golden")
    return {"threat_plants": 0, "control_plant_turns": control_plants[:3]}


def c_arbitration(candidate: Path, parent: Path, golden: dict) -> dict:
    """Check-7 area: two-worker arbitration. Invariants: I-16, I-17, I-22,
    I-23, I-27, I-28.

    (a) Orchard-eligible payload: candidate stdout must byte-equal the
        p_orchard_eligible golden (I-27/I-28 apple priority).
    (b) No-banana plain payload: byte-equal p_baseline_plain golden (check-4).
    (c) TRAIN parity on p_training: same first-TRAIN turn and stats tuple as
        the parent golden (I-17).
    (d) Ring map, starter standing on (working) one fruited mother, peer one
        cell away: never two HARVESTs on the same plant, simultaneous MOVE
        destinations pairwise distinct, and the peer never orders a MOVE onto
        the working starter's cell on 2+ consecutive turns (I-22/I-23).
    """
    for name, builder in (
        ("p_orchard_eligible", payload_orchard_eligible),
        ("p_baseline_plain", payload_baseline_plain),
    ):
        payload = builder()
        if sha256_bytes(payload.encode()) != golden[name]["payload_sha256"]:
            raise AssertionError(f"{name} payload drifted from golden")
        _, stdout_c, _ = run_deterministic(candidate, payload)
        if stdout_c.splitlines() != golden[name]["golden_lines"]:
            raise AssertionError(f"candidate diverged from parent on {name}")
    parsed_t, _, _ = run_deterministic(candidate, payload_training())
    train_c = first_train(parsed_t)
    train_g = golden["p_training"]["observations"]["first_train"]
    expected = (train_g["turn"], train_g["command"]) if train_g else None
    if train_c != expected:
        raise AssertionError(f"TRAIN displacement: {train_c} != {expected}")
    state = turn_text(
        plants=(plant("BANANA", 2, 2, size=4, health=6, fruits=2, cooldown=0),),
        units=(
            unit(0, 0, 2, 2, harvest=1, chop=1),
            unit(1, 0, 3, 2, harvest=1, chop=1),
        ),
    )
    parsed, _, _ = run_deterministic(candidate, transcript(MAP_RING, [state] * 60))
    for turn, row in enumerate(parsed, 1):
        harvests = [c for c in row if c.startswith("HARVEST ")]
        if len(harvests) > 1:
            raise AssertionError(f"turn {turn}: shared harvest target: {harvests}")
        dests = [d for c in row if (d := move_dest(c)) is not None]
        if len(dests) != len(set(dests)):
            raise AssertionError(f"turn {turn}: identical MOVE destinations: {row}")
    onto_worker = [
        turn
        for turn, command in unit_commands(parsed, 1)
        if move_dest(command) == (2, 2)
    ]
    if any(b == a + 1 for a, b in zip(onto_worker, onto_worker[1:])):
        raise AssertionError(
            f"peer orders MOVE onto working starter cell on consecutive turns: "
            f"{onto_worker[:6]}"
        )
    return {"byte_equal": ["p_orchard_eligible", "p_baseline_plain"], "train": train_c}


def c_target_recovery(candidate: Path, parent: Path, golden: dict) -> dict:
    """Check-7 area: destroyed/occupied target recovery. Invariants: I-24(i),
    I-26, I-23.

    (a) Destroyed: 40 turns with a fruited mother at (2,2) and the starter
        approaching, then 7 turns with the plant gone while alternative tasks
        stay available (a fruited plum for the peer and a fruited lemon near
        the starter, so per-unit arbitration cannot justify a permanent
        starter WAIT). Recovery: a definite non-WAIT
        starter command within 3 turns of destruction (retarget, no None
        fallthrough), and no period-2 MOVE-destination alternation a,b,a,b
        in the post-destruction window (A->B->A guard, I-26/D-1 proxy).
    (b) Occupied: peer u1 scripted standing ON the mother (stationary-working
        in the parent's on-cell verb model); the starter must never order a
        MOVE destination onto the peer's cell for 2+ consecutive turns (I-23).
    """
    others = (
        plant("PLUM", 10, 2, size=4, health=12, fruits=1),
        plant("LEMON", 4, 4, size=4, health=12, fruits=1),
    )
    alive = turn_text(
        plants=(plant("BANANA", 2, 2, size=4, health=6, fruits=2, cooldown=0),)
        + others,
        units=(
            unit(0, 0, 5, 2, harvest=1, chop=1),
            unit(1, 0, 9, 1, harvest=1, chop=1),
        ),
    )
    gone = turn_text(
        plants=others,
        units=(
            unit(0, 0, 5, 2, harvest=1, chop=1),
            unit(1, 0, 9, 1, harvest=1, chop=1),
        ),
    )
    parsed, _, _ = run_deterministic(
        candidate, transcript(MAP_RING, [alive] * 40 + [gone] * 7)
    )
    post = [c for t, c in unit_commands(parsed, 0) if t > 40]
    early = [c for t, c in unit_commands(parsed, 0) if 40 < t <= 43]
    if not any(not c.startswith("WAIT") for c in early):
        raise AssertionError("no definite command within 3 turns of destruction")
    dests = [move_dest(c) for c in post]
    if period2_alternation(dests):
        raise AssertionError(f"period-2 destination alternation after loss: {post}")
    occupied = turn_text(
        plants=(plant("BANANA", 2, 2, size=4, health=6, fruits=2, cooldown=0),),
        units=(
            unit(0, 0, 5, 2, harvest=1, chop=1),
            unit(1, 0, 2, 2, harvest=1, chop=1),
        ),
    )
    parsed2, _, _ = run_deterministic(candidate, transcript(MAP_RING, [occupied] * 40))
    onto_peer = [
        turn
        for turn, command in unit_commands(parsed2, 0)
        if move_dest(command) == (2, 2)
    ]
    consecutive = any(b == a + 1 for a, b in zip(onto_peer, onto_peer[1:]))
    if consecutive:
        raise AssertionError(f"sustained MOVE onto working peer cell: {onto_peer}")
    return {"post_destruction": post[:4], "onto_peer_turns": onto_peer[:4]}


TIER_C = [
    ("c_bootstrap_budget", c_bootstrap_budget, ["I-1", "I-2", "I-16"]),
    ("c_bounded_placement", c_bounded_placement, ["I-12", "I-13", "I-15"]),
    ("c_replant_renewable", c_replant_renewable, ["I-3", "I-9"]),
    ("c_late_conversion", c_late_conversion, ["I-4", "I-5", "I-6", "I-14", "I-1"]),
    ("c_banking", c_banking, ["I-7", "I-8", "I-9", "I-21"]),
    ("c_eta_suppression", c_eta_suppression, ["I-10", "I-18", "I-17"]),
    (
        "c_arbitration",
        c_arbitration,
        ["I-16", "I-17", "I-22", "I-23", "I-27", "I-28"],
    ),
    ("c_target_recovery", c_target_recovery, ["I-24", "I-26", "I-23"]),
]


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent", type=Path, default=DEFAULT_PARENT)
    parser.add_argument(
        "--candidate",
        type=Path,
        default=None,
        help="candidate source; when given, TIER-C fixtures are executed",
    )
    parser.add_argument("--golden-out", type=Path, default=DEFAULT_GOLDEN)
    parser.add_argument(
        "--results-out",
        type=Path,
        default=None,
        help="TIER-C results JSON (only with --candidate)",
    )
    args = parser.parse_args()

    parent_source = args.parent.read_text()
    with tempfile.TemporaryDirectory(prefix="banana-r2-semantics-") as directory:
        temp = Path(directory)
        parent_binary = temp / "parent"
        compile_text(parent_source, parent_binary, "banana_r2_parent")

        golden_fixtures = {}
        for name, fixture, invariants in TIER_P:
            outcome = fixture(parent_binary)
            outcome["invariants"] = invariants
            outcome["status"] = "PASS"
            golden_fixtures[name] = outcome

        golden = {
            "schema": "troll-farm-banana-r2-tier-p-golden/1",
            "parent": {
                "path": str(args.parent),
                "sha256": sha256_file(args.parent),
                "bytes": args.parent.stat().st_size,
            },
            "fixtures": golden_fixtures,
            "tier_c_planned": {
                name: {"invariants": invariants, "status": "PENDING_CANDIDATE"}
                for name, _, invariants in TIER_C
            },
        }
        args.golden_out.parent.mkdir(parents=True, exist_ok=True)
        args.golden_out.write_text(
            json.dumps(golden, indent=2, sort_keys=True) + "\n"
        )
        summary = {
            "tier_p": {name: "PASS" for name in golden_fixtures},
            "golden": str(args.golden_out),
        }

        if args.candidate is not None:
            candidate_binary = temp / "candidate"
            compile_text(
                args.candidate.read_text(), candidate_binary, "banana_r2_candidate"
            )
            results = {}
            failures = 0
            for name, fixture, invariants in TIER_C:
                try:
                    detail = fixture(candidate_binary, parent_binary, golden_fixtures)
                    results[name] = {
                        "status": "PASS",
                        "invariants": invariants,
                        "detail": detail,
                    }
                except AssertionError as error:
                    failures += 1
                    results[name] = {
                        "status": "FAIL",
                        "invariants": invariants,
                        "error": str(error),
                    }
            summary["tier_c"] = {name: results[name]["status"] for name in results}
            if args.results_out:
                args.results_out.write_text(
                    json.dumps(
                        {
                            "schema": "troll-farm-banana-r2-tier-c-results/1",
                            "candidate": {
                                "path": str(args.candidate),
                                "sha256": sha256_file(args.candidate),
                            },
                            "results": results,
                        },
                        indent=2,
                        sort_keys=True,
                    )
                    + "\n"
                )
            if failures:
                print(json.dumps(summary))
                return 1

    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
