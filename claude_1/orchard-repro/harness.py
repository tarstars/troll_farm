#!/usr/bin/env python3
"""Orchard reproduction (card 20260904-orchard-reproduction) -- the two-arm machinery.

Arm A is the champion of record playing a real ladder map to turn 300 through the July
Python referee. Arm B is THE SAME BINARY on THE SAME MAP with one thing interposed between
its emitted command line and the referee: a macro layer that may rewrite the command of one
designated planter troll and nothing else.

There is no planting model here. The referee is the model -- growth release, self-occupancy
of the planting cell, raid, felling, carry and banking are whatever `fuzz_panel.FuzzReferee`
does, because that is what runs. See PREREGISTRATION-2026-09-04.md sec 2.

    python3 claude_1/orchard-repro/harness.py --identity --maps 4
"""
from __future__ import annotations

import argparse
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for _p in ("claude_1/pipeline", "claude_1/banana-restoration-r2"):
    sys.path.insert(0, str(REPO / _p))

import fuzz_panel as fp             # noqa: E402
import semantic_harness as sh       # noqa: E402

CHAMPION = REPO / "readable" / "denial-off-champion.rs"
MAPS = REPO / "data" / "processed" / "maps.jsonl"
MAPS_FALLBACK = Path("/home/tarstars/prj/troll_farm/data/processed/maps.jsonl")

# The verbs the macro layer may emit for its one troll. NO_PLANT is not a verb: it is the
# absence of a rewrite -- the champion's own fragment passes through. WAIT is deliberately
# absent (PREREGISTRATION sec 4).
MACRO_VERBS = ("MOVE", "PICK", "PLANT", "CHOP", "DROP")


def maps_path() -> Path:
    return MAPS if MAPS.exists() else MAPS_FALLBACK


def sample_plan(n: int, seed: int):
    """The map sample, drawn exactly as local_claude_1/the-floor/smoke.py draws it, so the
    population is the same one every other read on this project used."""
    rng = random.Random(seed)
    records = [json.loads(line) for line in open(maps_path())]
    corpus = len(records)
    rng.shuffle(records)
    plan = []
    for i, rec in enumerate(records[:n]):
        draw = [rng.randint(2, 10) for _ in range(5)] + [0]
        plan.append((rec, draw, ["harvester", "chopper_aggressor"][i % 2]))
    return plan, corpus


def make_referee(rec, inventory, profile):
    plants = {}
    for t in rec["trees0"]:
        plants[(t["x"], t["y"])] = {"kind": t["type"], "size": t["size"],
                                    "health": t["health"], "fruits": t["fruits"],
                                    "cd": t["cur_cd"]}
    p0, p1 = tuple(rec["shacks"]["p0"]), tuple(rec["shacks"]["p1"])
    units = {
        0: {"player": 0, "cell": p0, "speed": 1, "cap": 1, "harvest": 1, "chop": 1,
            "carry": [0] * 6},
        1: {"player": 1, "cell": p1, "speed": 1, "cap": 1, "harvest": 1, "chop": 1,
            "carry": [0] * 6},
    }
    ref = fp.FuzzReferee(rec["rows"], list(inventory), plants, units, profile)
    ref.opp_inv = list(inventory)
    return ref


def own_score(inv):
    """The score of record: plum + lemon + apple + banana + 4 * wood (fuzz_panel.score)."""
    return sum(inv[0:4]) + 4 * inv[5]


def split_fragments(line: str):
    return [f for f in line.split(";")]


def fragment_uid(frag: str):
    """The unit a fragment names, or None for TRAIN / MSG / WAIT / junk."""
    tok = frag.split()
    if not tok:
        return None
    verb = tok[0].upper()
    if verb in ("TRAIN", "MSG", "WAIT") or len(tok) < 2:
        return None
    try:
        return int(tok[1])
    except ValueError:
        return None


def rewrite_line(line: str, uid: int, replacement: str | None) -> str:
    """Replace the designated troll's fragment, keeping every other fragment and their order
    byte-identical. `replacement is None` drops the troll's command entirely.

    The engine keeps only the FIRST non-TRAIN fragment for a unit (engine.rs:717-720), so
    substituting in place -- not appending -- is the only faithful rewrite."""
    out, done = [], False
    for frag in split_fragments(line):
        if not done and fragment_uid(frag) == uid:
            done = True
            if replacement is not None:
                out.append(replacement)
            continue
        out.append(frag)
    if not done and replacement is not None:
        out.append(replacement)
    return ";".join(out)


def run_arm(binary: Path, ref, turns: int, macro=None):
    """One closed-loop game. `macro(turn, ref, line) -> line` sees the champion's emitted
    line and the referee state BEFORE the line is applied, and returns the line to apply.

    The champion always receives the referee's own turn text -- the macro never lies to the
    bot -- so arm B is the champion continuously advanced through a world its planter troll
    has changed, which is what the charter asks for.
    """
    header = ref.map_header()
    emitted, applied = [], []
    with subprocess.Popen([str(binary)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                          text=True) as proc:
        proc.stdin.write(header)
        proc.stdin.flush()
        for turn in range(1, turns + 1):
            proc.stdin.write(ref.turn_text())
            proc.stdin.flush()
            line = proc.stdout.readline()
            if not line:
                raise RuntimeError("the champion closed stdout at turn %d" % turn)
            line = line.rstrip("\n")
            emitted.append(line)
            out = macro(turn, ref, line) if macro is not None else line
            applied.append(out)
            ref.apply(out)
            ref.grow()
        proc.stdin.close()
    return emitted, applied


class PassThrough:
    """The NO_PLANT policy, and the instrument's own control.

    It is a macro layer in every structural respect -- it finds the branch, designates a
    planter, and rewrites that troll's fragment on every turn after the branch -- but the
    fragment it writes is the one the champion emitted. Arm B under this policy must
    therefore be byte-identical to arm A on all 300 turns, not merely through the prefix.
    That is the identity gate: it tests the plumbing, not the policy.

    THE BRANCH POINT, and the reading of the charter it rests on. The charter says
    "byte-identical through the champion's own second TRAIN". On this champion that sentence
    has two faithful readings and they are not the same turn:

      (a) the second TRAIN *event* in the command stream;
      (b) the TRAIN that creates the *second troll*.

    Measured, not assumed: the champion of record emits exactly ONE TRAIN on every map-seat
    tried (see results/train-census.json) and finishes with two own trolls. Under reading (a)
    the branch never arrives and the experiment cannot run at all. Reading (b) is therefore
    the only executable one, and it is also the one the charter's neighbouring sentence --
    "the second troll's specification and turn must never change" -- is written in.

    So: the branch is the first turn after the referee's own roster for player 0 reaches two
    trolls. It is read from the referee's state rather than from the text of the command
    line, so a TRAIN the referee refused cannot be mistaken for one it accepted.
    """

    name = "NO_PLANT"

    def __init__(self):
        self.trains_emitted = 0
        self.branch_turn = None
        self.planter = None

    def __call__(self, turn, ref, line):
        for frag in split_fragments(line):
            tok = frag.split()
            if tok and tok[0].upper() == "TRAIN":
                self.trains_emitted += 1
        if self.branch_turn is None:
            own = sorted(uid for uid, u in ref.units.items() if u["player"] == 0)
            if len(own) >= 2:
                self.branch_turn = turn
                self.planter = own[-1]           # the second troll
            return line
        frag = None
        for f in split_fragments(line):
            if fragment_uid(f) == self.planter:
                frag = f
                break
        return rewrite_line(line, self.planter, frag)


def identity_gate(plan, turns, binary):
    """Gate 1 of the pre-registration: arm B with NO_PLANT reproduces arm A byte for byte,
    and the roster and score are untouched. A failure here is a defect in my machinery."""
    rows = []
    for rec, draw, profile in plan:
        ra = make_referee(rec, draw, profile)
        _, cmds_a = run_arm(binary, ra, turns)
        pol = PassThrough()
        rb = make_referee(rec, draw, profile)
        _, cmds_b = run_arm(binary, rb, turns, pol)
        own_a = sorted(u for u, x in ra.units.items() if x["player"] == 0)
        own_b = sorted(u for u, x in rb.units.items() if x["player"] == 0)
        first_diff = next((i + 1 for i, (x, y) in enumerate(zip(cmds_a, cmds_b)) if x != y),
                          None)
        row = {
            "map_hash": rec["map_hash"], "profile": profile, "start_inventory": draw,
            "turns": turns,
            "branch_turn": pol.branch_turn, "planter": pol.planter,
            "trains_emitted_b": pol.trains_emitted,
            "identical": cmds_a == cmds_b, "first_divergence_turn": first_diff,
            "own_trolls_a": len(own_a), "own_trolls_b": len(own_b),
            "own_score_a": own_score(ra.inv), "own_score_b": own_score(rb.inv),
            "opp_score_a": own_score(ra.opp_inv), "opp_score_b": own_score(rb.opp_inv),
            "referee_errors_a": dict(ra.error_counts), "referee_errors_b": dict(rb.error_counts),
            "answered_a": len(cmds_a), "answered_b": len(cmds_b),
        }
        row["pass"] = bool(row["identical"] and row["planter"] is not None
                           and not row["referee_errors_a"] and not row["referee_errors_b"]
                           and row["own_trolls_a"] == row["own_trolls_b"]
                           and row["answered_a"] == turns)
        rows.append(row)
        print("  %s %s %-18s branch@%s planter %s  own %d vs %d  errs %d/%d  %s"
              % ("PASS" if row["pass"] else "FAIL", rec["map_hash"], profile,
                 row["branch_turn"], row["planter"], row["own_score_a"], row["own_score_b"],
                 len(row["referee_errors_a"]), len(row["referee_errors_b"]),
                 "identical" if row["identical"] else
                 "DIVERGES at turn %s" % row["first_divergence_turn"]))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--maps", type=int, default=4)
    ap.add_argument("--turns", type=int, default=300)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--identity", action="store_true",
                    help="run the identity gate (arm B under NO_PLANT must equal arm A)")
    args = ap.parse_args()

    plan, corpus = sample_plan(args.maps, args.seed)
    print("champion: %s" % CHAMPION.relative_to(REPO))
    print("maps in the corpus: %d; sampled %d (seed %d)" % (corpus, len(plan), args.seed))

    with tempfile.TemporaryDirectory(prefix="orchard-repro-") as wd:
        binary = Path(wd) / "champion.bin"
        sh.compile_text(CHAMPION.read_text(), binary, crate="orchard_repro_champion")
        print("compiled.")
        if not args.identity:
            print("nothing to do: pass --identity")
            return 0
        rows = identity_gate(plan, args.turns, binary)

    good = sum(1 for r in rows if r["pass"])
    report = {
        "what": "identity gate: arm B under NO_PLANT must reproduce arm A byte for byte",
        "champion": str(CHAMPION.relative_to(REPO)),
        "champion_sha256": sh.sha256_text(CHAMPION.read_text())
        if hasattr(sh, "sha256_text") else None,
        "referee_sha256": fp.referee_sha256(),
        "maps_in_corpus": corpus, "maps_played": len(rows), "turns": args.turns,
        "seed": args.seed, "passed": good, "rows": rows,
        "status": "PASS" if good == len(rows) else "FAIL",
    }
    out = HERE / "results" / "identity-gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    print("\n  %s  %d/%d map-seats identical under the pass-through macro  -> %s"
          % (report["status"], good, len(rows), out))
    return 0 if good == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
