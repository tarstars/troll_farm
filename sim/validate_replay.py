"""Sim-fidelity validation: replay a REAL game through the sim and compare to the
referee, turn by turn.

The bot (built with DEBUG=true) echoes its per-turn state to stderr as @TF lines;
a captured replay also holds both players' commands (stdout). This harness
reconstructs the initial GameState from the @TF init lines, replays both players'
commands through the sim, and checks the sim's per-turn inventories + troll
positions against what the referee actually produced. Any divergence is the sim
disagreeing with the real referee (the thing we must trust before tuning on it).

Run the self-test (no capture needed) to verify the machinery:
    uv run python -m sim.validate_replay
Validate a real captured replay HTML:
    uv run python -m sim.validate_replay docs/plays/<debug_game>.html
"""
import re
import sys
import html as _html

from sim.state import GameState, SimUnit, SimPlant
from sim.engine import step, recompute_scores

ITEMS = ["PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD"]


# ── reconstruction ──────────────────────────────────────────────────────────

def reconstruct(map_lines, init_trees, init_units, inv0, inv1):
    """Build a turn-1 GameState from the bot's @TF init data."""
    walkable, iron, water = set(), set(), set()
    shacks = [(0, 0), (0, 0)]
    width, height = (int(v) for v in map_lines[0].split())
    for y, row in enumerate(map_lines[1:]):
        for x, ch in enumerate(row):
            c = (x, y)
            if ch == "0":
                shacks[0] = c
            elif ch == "1":
                shacks[1] = c
            elif ch == "+":
                iron.add(c)
            elif ch == "~":
                water.add(c)
            elif ch == ".":
                walkable.add(c)
    plants = [SimPlant(t[0], t[1], t[2], t[3], t[4], t[5], t[6]) for t in init_trees]
    units = [SimUnit(u[0], u[1], u[2], u[3], u[4], u[5], u[6], u[7], list(u[8])) for u in init_units]
    next_id = max((u.id for u in units), default=-1) + 1
    g = GameState(width, height, walkable, shacks, [list(inv0), list(inv1)],
                  units, plants, [0, 0], 1, next_id, set(iron), set(water))
    recompute_scores(g)
    return g


def digest(g):
    """The comparable per-turn state: both inventories + every troll's position."""
    return (tuple(g.inventories[0]), tuple(g.inventories[1]),
            tuple(sorted((u.id, u.x, u.y) for u in g.units)))


def replay_and_compare(g, actual, cmds0, cmds1):
    """Replay commands from g; check each step's state equals the recorded actual."""
    n = min(len(actual) - 1, len(cmds0), len(cmds1))
    mismatches = []
    if digest(g) != actual[0]:
        mismatches.append((1, "initial", digest(g), actual[0]))
    for t in range(n):
        step(g, cmds0[t], cmds1[t])
        if digest(g) != actual[t + 1]:
            mismatches.append((t + 2, "post-step", digest(g), actual[t + 1]))
            if len(mismatches) >= 5:
                break
    return n, mismatches


# ── self-test (proves the harness, no capture needed) ───────────────────────

def _serialize_init(g):
    cell = {}
    for c in g.walkable:
        cell[c] = "."
    for c in g.iron:
        cell[c] = "+"
    for c in g.water:
        cell[c] = "~"
    cell[g.shacks[0]] = "0"
    cell[g.shacks[1]] = "1"
    rows = ["{} {}".format(g.width, g.height)]
    for y in range(g.height):
        rows.append("".join(cell.get((x, y), "#") for x in range(g.width)))
    trees = [(p.type, p.x, p.y, p.size, p.health, p.fruits, p.cooldown) for p in g.plants]
    units = [(u.id, u.player, u.x, u.y, u.ms, u.cc, u.hp, u.chop, list(u.carry)) for u in g.units]
    return rows, trees, units, list(g.inventories[0]), list(g.inventories[1])


def selftest():
    from sim.mapgen import generate_bronze
    from sim.views import build_view
    from sim.boss import gatherer_boss_decide
    import bot.main as M

    ok = True
    for seed in (3, 7, 11):
        g = generate_bronze(seed)
        init = _serialize_init(g)               # capture turn-1 state, then play
        actual, cmds0, cmds1 = [], [], []
        for _ in range(300):
            actual.append(digest(g))
            c0 = M.decide(build_view(g, 0), M.PARAMS)
            c1 = gatherer_boss_decide(g, 1)
            cmds0.append(c0)
            cmds1.append(c1)
            step(g, c0, c1)
        actual.append(digest(g))
        g2 = reconstruct(*init)                 # reconstruct + replay + compare
        n, mism = replay_and_compare(g2, actual, cmds0, cmds1)
        status = "OK" if not mism else "MISMATCH"
        print(f"  seed {seed}: replayed {n} turns -> {status}"
              + ("" if not mism else f" first@turn {mism[0][0]}"))
        ok = ok and not mism
    print("SELF-TEST", "PASSED -- reconstruct/replay/compare machinery is correct."
          if ok else "FAILED.")
    return ok


# ── real replay parsing ─────────────────────────────────────────────────────

def _clean(b):
    return _html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", b))).strip()


def validate_html(path):
    data = _html.unescape(open(path, encoding="utf-8", errors="replace").read())
    # Commands: accept the DOM-dump format (subframe.stdout <pre>) OR the
    # plain-text frames export ("Standard Output Stream:" ... until next marker).
    stdout = [_clean(b) for b in re.findall(r'subframe\.stdout[^"]*">(.*?)</pre>', data, re.S)]
    if not stdout:
        stdout = [_clean(b) for b in re.findall(
            r'Standard Output Stream:\s*(.*?)\s*(?=Standard (?:Output|Error) Stream:|Game Summary:|\Z)',
            re.sub(r"<[^>]+>", " ", data), re.S)]
        stdout = ["; ".join(t for t in f.replace(";", "; ").split() if not t.isdigit())
                  for f in stdout]
    msg = next((i for i, f in enumerate(stdout) if "MSG v0.7" in f), 0)
    us, opp = stdout[msg % 2::2], stdout[(msg % 2) ^ 1::2]
    cmds0 = [[c.strip() for c in f.split(";") if c.strip()] for f in us]
    cmds1 = [[c.strip() for c in f.split(";") if c.strip()] for f in opp]

    # @TF debug lines: grab them wherever they sit (stderr <pre> or plain text).
    tf = " ".join(m for m in re.findall(r'@TF[A-Z]* [^<\n@]*', re.sub(r"<[^>]+>", " ", data)))
    maplines = [l for l in re.findall(r'@TFMAP ([^@]*)', tf)]
    map_lines = [maplines[0].strip()] + [m.strip() for m in maplines[1:]]
    trees = [tuple([p[0]] + [int(v) for v in p[1:]])
             for p in (m.split() for m in re.findall(r'@TFI P ([^@]*)', tf))]
    units = []
    for m in re.findall(r'@TFI U ([^@]*)', tf):
        f = [int(v) for v in m.split()]
        units.append((f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8:14]))
    actual = []
    for m in re.findall(r'@TFD ([^@]*)', tf):
        parts = m.split()
        turn = int(parts[0]); i0 = tuple(int(v) for v in parts[1].split(","))
        i1 = tuple(int(v) for v in parts[2].split(","))
        ups = tuple(sorted((int(a.split(",")[0]), int(a.split(",")[2]), int(a.split(",")[3]))
                           for a in parts[3].split(";") if a))
        actual.append((i0, i1, ups))
    if not actual or not map_lines:
        print("No @TF debug lines found -- was the bot built with DEBUG=true?")
        return False
    inv0, inv1 = list(actual[0][0]), list(actual[0][1])
    g = reconstruct(map_lines, trees, units, inv0, inv1)
    n, mism = replay_and_compare(g, actual, cmds0, cmds1)
    print(f"Replayed {n} turns through the sim.")
    if not mism:
        print("PERFECT: the sim reproduces the real game exactly -> faithful to the referee.")
    else:
        print(f"DIVERGENCE at {len(mism)} point(s); first at turn {mism[0][0]} ({mism[0][1]}):")
        _, _, sim_d, real_d = mism[0]
        print(f"  sim : inv0={sim_d[0]} units={sim_d[2]}")
        print(f"  real: inv0={real_d[0]} units={real_d[2]}")
    return not mism


if __name__ == "__main__":
    if len(sys.argv) > 1:
        validate_html(sys.argv[1])
    else:
        selftest()
