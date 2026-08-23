#!/usr/bin/env python3
r"""Phase 3b REACH on real games -- replay-drive one game and read both arms.

Same shape as `claude_1/gb1/gb_drive.py` (G-b), on 160 real games instead of 34 fixtures:

1. `replay_to_trace.adapt` rebuilds our seat's per-turn referee input from the replay (the
   ACCEPTED D-1 adapter, seat resolved from `--agent-id`, never assumed).
2. The probe -- built from the very source that PLAYED these games -- is fed that stream.
3. **The re-execution parity gate**: the probe's emitted command stream must equal the seat's
   RECORDED stdout, turn for turn, for the whole game.  A game that reproduces is a re-execution
   whose every command matches the real one; a game that does not is REFUSED and contributes no
   row.  The adapter reconstructs plant clocks rather than observing them, so this gate is what
   stops a wrong reconstruction from manufacturing reach that never happened.
4. **The telemetry identity gate** (this task's addition): the base arm's `(chosen, available)`
   per unit per turn must equal the NARRATE v3 rows the real bot actually PRINTED on the wire in
   that replay.  The base arm is not asserted to be the live bot; it is CHECKED against it.

The probe prints, this module parses, `run_reach_panel.py` classifies.  Nothing here grades
Phase 3b, claims progress, opens a gate, or takes any Arena action.

Run:  python3 claude_1/reach1/reach_drive.py --game-file F --probe BIN [--agent-id N]
"""
from __future__ import annotations

import argparse, gzip, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "adapter1"))

import replay_to_trace as rt                        # noqa: E402

AGENT_ID = 6652642        # the v3 corpus: agent 6652642, submission 41182608

ROW_RE = re.compile(
    r"^RCHROW turn=(-?\d+) unit=(-?\d+) bavail=(\S+) bchosen=(\S+) cavail=(\S+) cchosen=(\S+)$")
SEL_RE = re.compile(r"^RCHSEL turn=(-?\d+) base=(.*) cand=(.*) same=(true|false)$")
NARRATE_RE = re.compile(r"NARRATE v3 t=(-?\d+)((?: u-?\d+=[^;\s]+)*)")
UNIT_RE = re.compile(r"u(-?\d+)=([^/\s]+)/(\S+)")


class DriveError(RuntimeError):
    """Fail-closed refusal."""


def load_game(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as fh:
        return json.load(fh)


def items(dump: str):
    return [chunk for chunk in dump.split("~") if chunk]


def parse_kv(line: str, keys):
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


def recorded_narrate(commands: str):
    """The `(turn, unit) -> (chosen, available)` the real bot PRINTED, from the recorded stdout.

    Refuses rather than guesses: a stdout line carrying `NARRATE` that does not parse as a v3
    payload, or a duplicate `(turn, unit)`, is an error, not a skipped row.
    """
    table, errors = {}, []
    for line in commands.split("\n"):
        if "NARRATE" not in line:
            continue
        # The recorded stdout is one `;`-joined line per turn whose FIRST token is the MSG.
        # The payload therefore ends at the first `;`, not at end of line.
        match = NARRATE_RE.search(line.split(";", 1)[0])
        if not match:
            errors.append("unparsed NARRATE line: %r" % line[:120])
            continue
        turn = int(match.group(1))
        for unit, chosen, available in UNIT_RE.findall(match.group(2)):
            key = (turn, int(unit))
            if key in table:
                errors.append("duplicate telemetry row %r" % (key,))
            table[key] = (chosen, available)
    return table, errors


def drive(game_path, probe, agent_id=AGENT_ID):
    import subprocess
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

    rows, sels, falls, parse_errors = [], [], [], []
    seen = set()
    for line in proc.stderr.split("\n"):
        if line.startswith("RCHROW "):
            match = ROW_RE.match(line)
            if not match:
                parse_errors.append("unparsed RCHROW: %r" % line[:160])
                continue
            turn, unit = int(match.group(1)), int(match.group(2))
            if (turn, unit) in seen:
                parse_errors.append("duplicate RCHROW for (%d,%d)" % (turn, unit))
            seen.add((turn, unit))
            rows.append({"turn": turn, "unit": unit,
                         "bavail": match.group(3), "bchosen": match.group(4),
                         "cavail": match.group(5), "cchosen": match.group(6)})
        elif line.startswith("RCHSEL "):
            match = SEL_RE.match(line)
            if not match:
                parse_errors.append("unparsed RCHSEL: %r" % line[:160])
                continue
            sels.append({"turn": int(match.group(1)),
                         "base": [c for c in match.group(2).split(";") if c],
                         "cand": [c for c in match.group(3).split(";") if c],
                         "same": match.group(4) == "true"})
        elif line.startswith("RCHFALL "):
            row = parse_kv(line, ["turn", "unit", "carried", "out", "ret"])
            falls.append({"turn": int(row["turn"]), "unit": int(row["unit"]),
                          "carried": int(row["carried"]),
                          "out": items(row["out"]), "ret": items(row["ret"])})

    wire, wire_errors = recorded_narrate(commands)
    parse_errors.extend(wire_errors)

    # The telemetry identity gate.  Only meaningful on a parity-verified game: on a refused game
    # the two streams are different plays, so a mismatch there is expected and is not a finding.
    identity_mismatches, identity_checked = [], 0
    if parity:
        probe_table = {(r["turn"], r["unit"]): (r["bchosen"], r["bavail"]) for r in rows}
        if set(probe_table) != set(wire):
            identity_mismatches.append({"kind": "row_set", "probe_only": len(set(probe_table) - set(wire)),
                                        "wire_only": len(set(wire) - set(probe_table))})
        for key in sorted(set(probe_table) & set(wire)):
            identity_checked += 1
            if probe_table[key] != wire[key]:
                identity_mismatches.append({"kind": "value", "turn": key[0], "unit": key[1],
                                            "probe": probe_table[key], "wire": wire[key]})

    return {
        "game_id": meta["game_id"], "seat": meta["seat"],
        "traced_turns": meta["traced_turns"],
        "parity": parity, "first_divergent_turn": first_div,
        "rows": rows, "sels": sels,
        "fallback_entries": len(falls),
        "fallback_entries_with_discard": sum(1 for f in falls if len(f["out"]) > 0),
        "fallback_keys": sorted({(f["turn"], f["unit"]) for f in falls}),
        "fallback_discarded_picks": sum(
            1 for f in falls if any(i.startswith("PICK ") for i in f["out"])),
        "fallback_rows": falls,
        "parse_errors": parse_errors,
        "wire_rows": len(wire),
        "identity_checked": identity_checked,
        "identity_mismatches": identity_mismatches[:20],
        "identity_mismatch_count": len(identity_mismatches),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--game-file", required=True)
    ap.add_argument("--agent-id", type=int, default=AGENT_ID)
    ap.add_argument("--probe", required=True)
    ap.add_argument("--brief", action="store_true")
    args = ap.parse_args(argv)
    out = drive(args.game_file, args.probe, args.agent_id)
    if args.brief:
        out = {k: v for k, v in out.items()
               if k not in ("rows", "sels", "fallback_rows", "fallback_keys")} | {
            "row_count": len(out["rows"]), "sel_count": len(out["sels"])}
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
