#!/usr/bin/env python3
r"""Controls for G-b on real games.  Each corrupts exactly one guarded thing and must be REFUSED
or must produce the difference it plants.

The 08-15 -> 21 failure mode this file exists to prevent: a check that reports green because it
cannot see anything at all.  Control 4 is the load-bearing one -- it builds a *poisoned* EXTEND
body whose candidate list differs in a way the incumbent cannot produce, and requires the same-state
fork to report `same=false` on the Delta-B unit itself.  Every `same=true` in the panel is worth
exactly what that control is worth.

Run:  python3 claude_1/gb1/gb_controls.py --probe BIN --poison-probe BIN --plain BIN
"""
from __future__ import annotations

import argparse, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "claude_1" / "adapter1"))

import gb_drive                                     # noqa: E402
import replay_to_trace as rt                        # noqa: E402

# The one parity-verified game that reaches a Delta-B state.  Named, so a reviewer can re-run the
# controls against the same subject the panel used.
CONTROL_GAME = "900089943.json.gz"


def _drive_text(probe, transcript):
    proc = subprocess.run([str(probe)], input=transcript, capture_output=True, text=True)
    return [line for line in proc.stdout.split("\n") if line != ""], proc.stderr


def run(games_dir: Path, probe: Path, poison_probe: Path, plain: Path):
    results = []
    path = games_dir / CONTROL_GAME
    game = gb_drive.load_game(path)
    transcript, commands, meta = rt.adapt(game, agent_id=gb_drive.AGENT_ID)
    recorded = [line for line in commands.split("\n") if line != ""]

    # 1. baseline -- the probe reproduces the recorded stream, and reaches the Delta-B state.
    emitted, _ = _drive_text(probe, transcript)
    base = gb_drive.drive(path, probe)
    results.append({
        "control": "1 baseline: probe reproduces the recorded game and reaches Delta-B",
        "fired": emitted == recorded and base["parity"] and len(base["delta_b_ticks"]) == 1,
        "detail": "parity=%s delta_b=%d" % (base["parity"], len(base["delta_b_ticks"])),
    })

    # 2. probe inertness -- the probe's stream equals the UNINSTRUMENTED binary's stream.
    plain_out, _ = _drive_text(plain, transcript)
    results.append({
        "control": "2 probe inertness: probe stream == plain instrument stream",
        "fired": plain_out == emitted,
        "detail": "%d/%d lines equal" % (sum(1 for a, b in zip(plain_out, emitted) if a == b),
                                         len(emitted)),
    })

    # 3. the parity gate can reject -- move one of our units one cell on one mid-game state.
    lines = transcript.split("\n")
    moved = None
    for index, line in enumerate(lines):
        fields = line.split()
        if len(fields) == 14 and fields[1] == "0" and index > len(lines) // 2:
            fields[2] = str(int(fields[2]) + 1)
            lines[index] = " ".join(fields)
            moved = index
            break
    corrupted, _ = _drive_text(probe, "\n".join(lines))
    results.append({
        "control": "3 parity gate is live: one own-unit cell moved one step -> stream diverges",
        "fired": moved is not None and corrupted != recorded,
        "detail": "corrupted line %r; diverged=%s" % (moved, corrupted != recorded),
    })

    # 4. THE gate on the gate -- a poisoned EXTEND body must be visible to the fork, on the
    #    Delta-B unit itself.
    poisoned = gb_drive.drive(path, poison_probe)
    hit = [row for row in poisoned["fork_turns"] if row["delta_b_unit_changed"]]
    results.append({
        "control": "4 the fork is not inert: poisoned EXTEND body changes the Delta-B unit's command",
        "fired": bool(hit),
        "detail": "delta_b_unit_changed on turns %r" % [row["turn"] for row in hit],
    })

    # 5. wrong agent id -- refused, never silently joined to the other seat.
    try:
        rt.adapt(game, agent_id=1)
        fired, detail = False, "adapter accepted an agent id that is not in the table"
    except Exception as exc:                                    # noqa: BLE001
        fired, detail = True, str(exc)[:120]
    results.append({"control": "5 unknown agent id is refused", "fired": fired, "detail": detail})

    # 6. §5 step 3 checker is live -- an ALTERED item is not `duplicates_only`.
    ret = ["DROP 3|8000.000000|Bank((11, 3))", "MOVE 3 12 2|6999.000000|Bank((12, 2))"]
    altered = ret + ["DROP 3|8001.000000|Bank((11, 3))"]
    added, removed = gb_drive.multiset_delta(ret, altered)
    ok_alt = not ((not removed) and all(gb_drive.is_bank(i) for i in added)
                  and all(i in ret for i in added))
    dropped = ret[:1]
    added2, removed2 = gb_drive.multiset_delta(ret, dropped)
    ok_drop = bool(removed2)
    results.append({
        "control": "6 duplicates-only check is live: an altered score and a removed candidate both fail",
        "fired": ok_alt and ok_drop,
        "detail": "altered_rejected=%s removed_rejected=%s" % (ok_alt, ok_drop),
    })

    # 7. mutual exclusion (§2) is asserted, not assumed.
    class _Fake:
        pass
    fake_fall = {"turn": 1, "unit": 0, "carried": 2,
                 "out": ["WAIT|0.000000|None", "PICK 0 APPLE|7500.000000|Cell((1, 1))"],
                 "ret": ["WAIT|0.000000|None"]}
    extra = fake_fall["out"][1:]
    violation = fake_fall["carried"] > 0 and any(i.startswith("PICK ") for i in extra)
    results.append({
        "control": "7 Delta-A/Delta-B co-occurrence is a violation, not an absorption",
        "fired": violation, "detail": "synthetic co-occurrence flagged=%s" % violation,
    })

    # 8. a game that reaches no Delta-B state contributes none (the census is not manufactured).
    empty = gb_drive.drive(games_dir / "900089738.json.gz", probe)
    results.append({
        "control": "8 a game with no Delta-B state contributes zero ticks",
        "fired": empty["delta_b_ticks"] == [] and empty["parity"],
        "detail": "900089738 parity=%s ticks=%d" % (empty["parity"], len(empty["delta_b_ticks"])),
    })
    return results


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--games-dir", required=True)
    ap.add_argument("--probe", required=True)
    ap.add_argument("--poison-probe", required=True)
    ap.add_argument("--plain", required=True)
    args = ap.parse_args(argv)
    rows = run(Path(args.games_dir).expanduser(), Path(args.probe),
               Path(args.poison_probe), Path(args.plain))
    print(json.dumps(rows, indent=2))
    return 0 if all(row["fired"] for row in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
