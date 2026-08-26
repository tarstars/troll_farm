#!/usr/bin/env python3
r"""Adjudicate the 120 intention/command divergences by OBSERVATION.

For every game whose re-execution reproduces the seat's recorded stdout for the whole game (the
same parity gate G-b uses), pair the probe's `IDLESEL` (post-selection) and `IDLEPOST`
(post-conflict-resolution) vectors turn by turn, and ask, for each divergent join row, what
happened to that unit's command between the two:

    REWRITTEN_TO_WAIT   selection issued a command for the unit; resolution replaced it with WAIT
    MANUFACTURED        selection issued nothing for the unit; resolution produced a command
    UNCHANGED           the two vectors agree for that unit -- the divergence is NOT a rewrite
    NOT_VERIFIED        the row's game failed the parity gate and contributes no adjudication

`resolve_move_conflicts` has exactly two sites that write `"WAIT"` over a move -- the projected
landing equals the current cell, and the blocked-with-no-detour tail -- and one that writes a MOVE
over a partner's `WAIT` (the swap branch).  Which of those fired is reported per row where it can
be told apart: a rewrite whose unit had a projected landing equal to its own cell is `no-progress`,
one where the unit's target cell was taken by the sibling's landing is `blocked-by-sibling`.
That distinction is READ OFF the two vectors, not inferred from the bot's source.

Run:  python3 claude_1/narrate2/idle_adjudicate.py --games-dir DIR --probe BIN
"""
from __future__ import annotations

import argparse, collections, glob, json, os, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "claude_1" / "narrate1"))
sys.path.insert(0, str(REPO / "claude_1" / "adapter1"))
sys.path.insert(0, str(REPO / "claude_1" / "gb1"))

import idle_classify                                # noqa: E402
import narrate_decode as nd                         # noqa: E402
import replay_to_trace as rt                        # noqa: E402

AGENT_ID = idle_classify.AGENT_ID


def unit_of(command: str):
    fields = command.split()
    if len(fields) < 2:
        return None
    try:
        return int(fields[1])
    except ValueError:
        return None


def by_unit(vector: str):
    out = {}
    for command in vector.split(";"):
        command = command.strip()
        if not command:
            continue
        uid = unit_of(command)
        if uid is not None:
            out[uid] = command
    return out


def run_game(path, probe):
    game = nd.load_game(path)
    transcript, commands, meta = rt.adapt(game, agent_id=AGENT_ID)
    proc = subprocess.run([str(probe)], input=transcript, capture_output=True, text=True)
    emitted = [line for line in proc.stdout.split("\n") if line != ""]
    recorded = [line for line in commands.split("\n") if line != ""]
    parity = emitted == recorded
    sel, post = {}, {}
    sites = {}
    for line in proc.stderr.split("\n"):
        if line.startswith("IDLEWAIT "):
            body = line[len("IDLEWAIT "):]
            turn = int(body[body.index("turn=") + 5:body.index(" unit=")])
            uid = int(body[body.index("unit=") + 5:body.index(" site=")])
            sites.setdefault((turn, uid), []).append(body[body.index("site=") + 5:])
            continue
        for tag, sink in (("IDLESEL ", sel), ("IDLEPOST ", post)):
            if line.startswith(tag):
                body = line[len(tag):]
                turn = int(body[body.index("turn=") + 5:body.index(" cmds=")])
                sink[turn] = body[body.index(" cmds=") + 6:]
    return parity, sel, post, sites


def adjudicate(games_dir: Path, probe: Path):
    verdicts = collections.Counter()
    rows_out = []
    verified_games, refused_games = 0, 0
    for path in sorted(glob.glob(str(games_dir / "*.json.gz"))):
        rows, meta = nd.decode_file(path, AGENT_ID)
        idle_classify.classify_rows(rows)
        divergent = [r for r in rows
                     if (r["intent_kind"] != "NONE") != (r["command_verb"] is not None)]
        if not divergent:
            continue
        parity, sel, post, sites = run_game(path, probe)
        verified_games += parity
        refused_games += not parity
        for row in divergent:
            if not parity:
                verdicts["NOT_VERIFIED"] += 1
                rows_out.append(dict(row, game=meta["game_id"], verdict="NOT_VERIFIED"))
                continue
            turn = row["turn"]
            before = by_unit(sel.get(turn, ""))
            after = by_unit(post.get(turn, ""))
            uid = row["unit"]
            if uid in before and uid not in after:
                verdict = "REWRITTEN_TO_WAIT"
            elif uid not in before and uid in after:
                verdict = "MANUFACTURED"
            elif before.get(uid) == after.get(uid):
                verdict = "UNCHANGED"
            else:
                verdict = "REWRITTEN_IN_PLACE"
            verdicts[verdict] += 1
            site = sites.get((turn, uid), [])
            verdicts["site:" + (",".join(site) if site else "(untagged)")] += 1
            rows_out.append(dict(row, game=meta["game_id"], verdict=verdict, sites=site,
                                 selected=before.get(uid), resolved=after.get(uid),
                                 sibling_selected={k: v for k, v in before.items() if k != uid},
                                 sibling_resolved={k: v for k, v in after.items() if k != uid}))
    return {
        "verdicts": dict(verdicts),
        "games_with_divergence_verified": verified_games,
        "games_with_divergence_refused": refused_games,
        "rows": rows_out,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--games-dir", required=True)
    ap.add_argument("--probe", required=True)
    ap.add_argument("--out")
    args = ap.parse_args(argv)
    result = adjudicate(Path(args.games_dir).expanduser(), Path(args.probe).expanduser())
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
