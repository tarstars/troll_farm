#!/usr/bin/env python3
r"""G-b on real games — replay-drive one game and classify the Delta-B evidence.

## What "run G-b on real games" means operationally

Phase 3b design r2 §5 wants *naturally reached* Delta-B states and the two generator variants run
over the same state.  Real ladder games give the states; they do not give the bot's internals.  So
this driver RE-EXECUTES the bot that played the game:

1. `replay_to_trace.adapt` rebuilds our seat's per-turn referee input from the replay (the same
   renderer the ACCEPTED D-1 adapter uses, seat resolved from `--agent-id`, never assumed).
2. The probe binary -- built from the very source that played these games -- is fed that stream.
3. **The parity gate**: the probe's emitted command stream must equal the seat's RECORDED stdout,
   turn for turn, for the whole game.  A game that reproduces is a re-execution whose every
   command matches the real one; a game that does not is REFUSED and contributes no Delta-B state.

The gate is load-bearing because the adapter reconstructs plant clocks rather than observing them
(`replay_to_trace` docstring).  Where the reconstruction is wrong, the bot sees a state the real
bot did not, and the divergence shows up as a command mismatch.  Refusing those games is how a
reconstructed input stream is prevented from manufacturing a Delta-B state that never happened.

## What is classified, and by whom

The probe prints; this module classifies (the Phase 3b convention).

- `GBFALL` -> a fallback entry.  **Delta-B candidate** iff `carried>0` AND `out` carries more than
  the seeded `WAIT` -- i.e. the earlier `carried>0 && is_adjacent(shack)` block already appended
  bank candidates that the fallback is about to append a second time.
- §5 step 3 (`duplicates_only`): the multiset delta between the two variants' returned lists must
  be duplicate, ELEMENT-IDENTICAL bank candidates -- nothing added, removed or altered.  Computed
  from `out` and the incumbent's return, both dumped as `command|score|target` triples.
- §2 mutual exclusion: a fallback entry carrying BOTH `carried>0` and a replant `PICK` in `out`
  refutes §2 and fails the run.
- §5 step 4 (`GBFORK`): `select_recording` + `resolve_move_conflicts` over the identical state with
  only the variant switched.  A differing pair is attributed per unit, and separated into
  differences on the Delta-B unit itself and differences on a sibling (which are Delta-A, not
  Delta-B, and must not be reported as Delta-B non-inertness).

Nothing here grades Phase 3b, claims progress, or takes any Arena action.

Run:  python3 claude_1/gb1/gb_drive.py --game-file F --agent-id N --probe BIN
"""
from __future__ import annotations

import argparse, gzip, json, os, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "adapter1"))

import replay_to_trace as rt                        # noqa: E402

AGENT_ID = 6652424


class DriveError(RuntimeError):
    """Fail-closed refusal."""


def load_game(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as fh:
        return json.load(fh)


def items(dump: str):
    return [chunk for chunk in dump.split("~") if chunk]


def parse_kv(line: str, keys):
    """`K=v` fields where every value but the last of each key is space-free."""
    out, rest = {}, line
    for index, key in enumerate(keys):
        token = key + "="
        at = rest.index(token)
        rest = rest[at + len(token):]
        if index + 1 < len(keys):
            nxt = " " + keys[index + 1] + "="
            end = rest.index(nxt)
            out[key], rest = rest[:end], rest[end + 1:]
        else:
            out[key] = rest
    return out


def multiset_delta(base, cand):
    """(added, removed) as multisets, cand relative to base."""
    from collections import Counter
    b, c = Counter(base), Counter(cand)
    added = list((c - b).elements())
    removed = list((b - c).elements())
    return added, removed


def unit_of(command: str):
    """The unit id a command names, or None for `WAIT` (which names no unit)."""
    fields = command.split()
    if len(fields) < 2:
        return None
    try:
        return int(fields[1])
    except ValueError:
        return None


def is_bank(item: str) -> bool:
    """A bank candidate targets the shack: `Bank` target, by the Candidate dump's Debug form."""
    return "|Bank" in item


def drive(game_path, probe, agent_id=AGENT_ID):
    game = load_game(game_path)
    transcript, commands, meta = rt.adapt(game, agent_id=agent_id)
    proc = subprocess.run([str(probe)], input=transcript, capture_output=True, text=True)
    emitted = [line for line in proc.stdout.split("\n") if line != ""]
    recorded = [line for line in commands.split("\n") if line != ""]
    first_div = None
    for index in range(min(len(emitted), len(recorded))):
        if emitted[index] != recorded[index]:
            first_div = index + 1
            break
    if first_div is None and len(emitted) != len(recorded):
        first_div = min(len(emitted), len(recorded)) + 1
    parity = first_div is None and len(emitted) == len(recorded)

    falls, forks, lists = [], [], {}
    for line in proc.stderr.split("\n"):
        if line.startswith("GBFALL "):
            row = parse_kv(line, ["turn", "unit", "carried", "out", "ret"])
            falls.append({
                "turn": int(row["turn"]), "unit": int(row["unit"]),
                "carried": int(row["carried"]),
                "out": items(row["out"]), "ret": items(row["ret"]),
            })
        elif line.startswith("GBFORK "):
            row = parse_kv(line, ["turn", "base", "cand", "same"])
            forks.append({
                "turn": int(row["turn"]),
                "base": [c for c in row["base"].split(";") if c],
                "cand": [c for c in row["cand"].split(";") if c],
                "same": row["same"] == "true",
            })
        elif line.startswith("GBLIST "):
            row = parse_kv(line, ["turn", "unit", "base", "cand"])
            lists[(int(row["turn"]), int(row["unit"]))] = (items(row["base"]), items(row["cand"]))

    delta_b, delta_a, violations = [], [], []
    for fall in falls:
        extra = fall["out"][1:]
        if not extra:
            continue
        has_pick = any(item.startswith("PICK ") for item in extra)
        if has_pick:
            delta_a.append({"turn": fall["turn"], "unit": fall["unit"],
                            "picks": [i for i in extra if i.startswith("PICK ")]})
        if fall["carried"] > 0 and has_pick:
            violations.append({"kind": "delta_a_delta_b_cooccurrence",
                               "turn": fall["turn"], "unit": fall["unit"]})
        if fall["carried"] <= 0:
            continue
        # §5 step 3, on the returned lists of the two variants.
        cand_ret = fall["out"] + fall["ret"][1:]
        added, removed = multiset_delta(fall["ret"], cand_ret)
        delta_b.append({
            "turn": fall["turn"], "unit": fall["unit"], "carried": fall["carried"],
            "extra_from_out": extra,
            "added": added, "removed": removed,
            "duplicates_only": (not removed) and bool(added)
            and all(is_bank(item) for item in added)
            and all(item in fall["ret"] for item in added),
        })

    # §5 step 4, attributed.  A fork difference on a turn is Delta-B's only when the differing
    # command belongs to a unit that was itself in a Delta-B state on that turn.
    db_turns = {(row["turn"], row["unit"]) for row in delta_b}
    fork_rows = []
    for fork in forks:
        differing_units = []
        for base_cmd, cand_cmd in zip(fork["base"], fork["cand"]):
            if base_cmd != cand_cmd:
                differing_units.append((base_cmd, cand_cmd))
        differing_ids = []
        for base_cmd, cand_cmd in differing_units:
            uid = unit_of(base_cmd)
            if uid is None:
                uid = unit_of(cand_cmd)
            differing_ids.append(uid)
        attributed = []
        for turn_unit in sorted(u for (t, u) in db_turns if t == fork["turn"]):
            base_list, cand_list = lists.get((fork["turn"], turn_unit), ([], []))
            attributed.append({"unit": turn_unit,
                               "list_added": multiset_delta(base_list, cand_list)[0],
                               "list_removed": multiset_delta(base_list, cand_list)[1]})
        fork_rows.append({
            "turn": fork["turn"], "same": fork["same"],
            "base": fork["base"], "cand": fork["cand"],
            "differing": differing_units,
            "differing_unit_ids": differing_ids,
            "delta_b_units": sorted(u for (t, u) in db_turns if t == fork["turn"]),
            "delta_b_unit_changed": any(
                uid is not None and (fork["turn"], uid) in db_turns for uid in differing_ids),
            "delta_b_unit_lists": attributed,
            "arity_changed": len(fork["base"]) != len(fork["cand"]),
        })

    return {
        "game_id": meta["game_id"], "seat": meta["seat"],
        "traced_turns": meta["traced_turns"],
        "parity": parity, "first_divergent_turn": first_div,
        "fallback_entries": len(falls),
        "fallback_entries_carrying": sum(1 for f in falls if f["carried"] > 0),
        "delta_a_ticks": delta_a,
        "delta_b_ticks": delta_b,
        "fork_turns": fork_rows,
        "violations": violations,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--game-file", required=True)
    ap.add_argument("--agent-id", type=int, default=AGENT_ID)
    ap.add_argument("--probe", required=True)
    args = ap.parse_args(argv)
    print(json.dumps(drive(args.game_file, args.probe, args.agent_id),
                     indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
