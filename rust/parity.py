"""Parity harness: compare Python bot vs Rust bot outputs turn-by-turn.

Run from repo root:
    uv run python rust/parity.py

Requires:
    - sim/ and bot/ packages installed (via uv / pyproject.toml)
    - Rust bot compiled: rust/target/release/bot
"""

import subprocess
import sys
import time
from pathlib import Path

# Ensure the repo root (parent of this file's directory) is on sys.path so
# that "sim" and "bot" packages are importable regardless of cwd.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from sim.mapgen import generate_bronze
from sim.views import build_view
from sim.engine import step
from bot.main import decide, PARAMS, VERSION


REPO_ROOT = _REPO_ROOT
RUST_BOT = REPO_ROOT / "rust" / "target" / "release" / "bot"
TOTAL_TURNS = 300


def cell_char(game, x, y):
    """Return the grid character for cell (x, y) in the given game state."""
    pos = (x, y)
    if pos == game.shacks[0]:
        return "0"
    if pos == game.shacks[1]:
        return "1"
    if pos in game.iron:
        return "+"
    if pos in game.water:
        return "~"
    if pos in game.walkable:
        return "."
    return "#"


def serialize_grid(game):
    """Serialize the full game grid (once per game) to CG input lines."""
    lines = [f"{game.width} {game.height}"]
    for y in range(game.height):
        row = "".join(cell_char(game, x, y) for x in range(game.width))
        lines.append(row)
    return lines


def serialize_turn(game, player):
    """Serialize per-turn state for the given player as CG input lines."""
    opp = 1 - player
    inv_my = " ".join(str(v) for v in game.inventories[player])
    inv_opp = " ".join(str(v) for v in game.inventories[opp])
    lines = [inv_my, inv_opp]

    # Trees
    lines.append(str(len(game.plants)))
    for p in game.plants:
        lines.append(f"{p.type} {p.x} {p.y} {p.size} {p.health} {p.fruits} {p.cooldown}")

    # Trolls (all units, both players)
    lines.append(str(len(game.units)))
    for u in game.units:
        carry = " ".join(str(c) for c in u.carry)
        lines.append(f"{u.id} {u.player} {u.x} {u.y} {u.ms} {u.cc} {u.hp} {u.chop} {carry}")

    return lines


def build_full_input(seed):
    """Generate a game from seed and play it, collecting all input lines and Python outputs."""
    game = generate_bronze(seed)
    grid_lines = serialize_grid(game)

    all_input_lines = list(grid_lines)  # grid first
    python_outputs = []

    for turn in range(1, TOTAL_TURNS + 1):
        turn_lines = serialize_turn(game, 0)
        all_input_lines.extend(turn_lines)

        # Python bot output for this turn
        view = build_view(game, 0)
        py_cmds = decide(view, PARAMS)
        python_outputs.append(";".join(py_cmds))

        # Step: Python bot for player 0, simple WAIT for player 1
        # (opponent behavior doesn't matter for parity — we just need the same
        #  game state that the Python bot sees each turn, driven by Python's own decisions)
        opp_cmds = ["WAIT"]
        step(game, py_cmds, opp_cmds)

        if game.turn > TOTAL_TURNS:
            break

    return all_input_lines, python_outputs


def run_rust_bot(input_text):
    """Run the Rust bot on the given input text and return its stdout lines."""
    proc = subprocess.run(
        [str(RUST_BOT)],
        input=input_text,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if proc.returncode != 0 and proc.returncode is not None:
        print(f"  [WARN] Rust bot exited with code {proc.returncode}", file=sys.stderr)
        if proc.stderr:
            print(f"  stderr: {proc.stderr[:500]}", file=sys.stderr)
    return proc.stdout.splitlines()


def compare_seed(seed, verbose=True):
    """Run parity check for one seed. Returns (match_count, total, mismatches)."""
    if verbose:
        print(f"  Seed {seed}: generating game + Python outputs...", flush=True)

    all_input_lines, python_outputs = build_full_input(seed)
    input_text = "\n".join(all_input_lines) + "\n"

    if verbose:
        print(f"  Seed {seed}: running Rust bot ({len(python_outputs)} turns)...", flush=True)

    t0 = time.perf_counter()
    rust_outputs = run_rust_bot(input_text)
    elapsed = time.perf_counter() - t0

    total = len(python_outputs)
    rust_total = len(rust_outputs)
    if rust_total != total:
        print(f"  [WARN] Seed {seed}: Python produced {total} lines, Rust produced {rust_total}", file=sys.stderr)

    matches = 0
    mismatches = []
    for i, (py, rs) in enumerate(zip(python_outputs, rust_outputs)):
        if py == rs:
            matches += 1
        else:
            mismatches.append((i + 1, py, rs))

    if verbose:
        rate = 100.0 * matches / total if total else 0
        per_turn_ms = 1000.0 * elapsed / total if total else 0
        print(f"  Seed {seed}: {matches}/{total} = {rate:.1f}% match, "
              f"Rust total {elapsed*1000:.0f}ms ({per_turn_ms:.2f}ms/turn)")

    return matches, total, mismatches


def main():
    seeds = [42, 137, 999, 2024]
    max_mismatches_shown = 10

    if not RUST_BOT.exists():
        print(f"ERROR: Rust bot not found at {RUST_BOT}")
        print("Build it with: cd rust && cargo build --release")
        sys.exit(1)

    print(f"Parity harness — Python bot v{VERSION} vs Rust bot")
    print(f"Seeds: {seeds}")
    print(f"Rust binary: {RUST_BOT}")
    print()

    total_matches = 0
    total_turns = 0
    all_mismatches = []

    for seed in seeds:
        matches, total, mismatches = compare_seed(seed, verbose=True)
        total_matches += matches
        total_turns += total
        all_mismatches.extend((seed, t, py, rs) for t, py, rs in mismatches)

    overall = 100.0 * total_matches / total_turns if total_turns else 0
    print()
    print(f"=== OVERALL: {total_matches}/{total_turns} = {overall:.2f}% match ===")

    if all_mismatches:
        print()
        print(f"First {max_mismatches_shown} mismatches (of {len(all_mismatches)}):")
        for seed, turn, py, rs in all_mismatches[:max_mismatches_shown]:
            print(f"  seed={seed} turn={turn}")
            print(f"    PY:   {py}")
            print(f"    RUST: {rs}")
    else:
        print("All outputs matched!")


if __name__ == "__main__":
    main()
