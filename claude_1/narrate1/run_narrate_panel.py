#!/usr/bin/env python3
"""NARRATE decoder acceptance panel: full sweep over the supplied corpus + the
controls that must fire.  Writes claude_1/narrate1/results/.

The sweep alone proves nothing; `narrate_controls.py` is what makes 149/149
mean something.  Both run here, and the panel FAILS if either side does.

The corpus is a parameter (`--games-dir`).  It is NOT `data/raw/games/`: that
path is hazard-listed in protocol §7 and owned by the 02:17 UTC collector.

The cross-tab at the end is descriptive instrument coverage -- which intention
shapes actually occur, and against which issued verbs -- so a reviewer can see the
decoder exercised more than one branch.  It grades nothing: no dancing, blocking
or idleness call, no prevalence, no cure claim.  Those are out of this card's scope.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import narrate_decode as nd                       # noqa: E402
import narrate_controls as nc                     # noqa: E402

AGENT_ID = 6652424


def corpus_digest(paths):
    h = hashlib.sha256()
    for path in paths:
        with open(path, "rb") as fh:
            h.update(os.path.basename(path).encode())
            h.update(hashlib.sha256(fh.read()).hexdigest().encode())
    return h.hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--games-dir", required=True)
    ap.add_argument("--agent-id", type=int, default=AGENT_ID)
    ap.add_argument("--out-dir", default=os.path.join(HERE, "results"))
    ap.add_argument("--sample-game", default="900089738")
    ap.add_argument("--corpus-ref", default="agent/local_claude_1@ebd5ebb1:"
                                            "local_claude_1/narrate/games",
                    help="where the supplied corpus came from, recorded verbatim")
    args = ap.parse_args(argv)

    paths = sorted(glob.glob(os.path.join(args.games_dir, "*.json"))
                   + glob.glob(os.path.join(args.games_dir, "*.json.gz")))
    if not paths:
        print("no replays under %s" % args.games_dir, file=sys.stderr)
        return 2

    games, refusals = [], []
    kinds = Counter()
    verbs = Counter()
    cross = Counter()
    seats = Counter()
    sample_rows = None
    for path in paths:
        try:
            rows, meta = nd.decode_file(path, args.agent_id)
        except nd.NarrateError as exc:
            refusals.append({"game_file": os.path.basename(path),
                             "reason": str(exc)})
            continue
        games.append(meta)
        seats[meta["seat"]] += 1
        for row in rows:
            kinds[row["intent_kind"]] += 1
            verb = row["command_verb"] or "(none)"
            verbs[verb] += 1
            cross["%s|%s" % (row["intent_kind"], verb)] += 1
        if str(meta["game_id"]) == str(args.sample_game):
            sample_rows = rows

    controls_rc = None
    try:
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            controls_rc = nc.main([args.games_dir])
        controls = json.loads(buf.getvalue())
    except Exception as exc:                       # noqa: BLE001
        controls = {"error": str(exc)}

    report = {
        "task_id": "20260823-narrate-real-game-telemetry",
        "agent_id": args.agent_id,
        "grammar": "NARRATE %s" % nd.GRAMMAR_VERSION,
        "corpus": {
            "games_dir": args.games_dir,
            "games": len(paths),
            "digest_sha256": corpus_digest(paths),
            "source_ref": args.corpus_ref,
        },
        "sweep": {
            "decoded": len(games),
            "refused": len(refusals),
            "refusals": refusals,
            "traced_turns": sum(g["traced_turns"] for g in games),
            "join_rows": sum(g["join_rows"] for g in games),
            "seats_played": dict(sorted(seats.items())),
            "opponent_narrate_turns_total": sum(
                g["opponent_narrate_turns"] for g in games),
            "unit_id_sets": sorted({",".join(str(i) for i in g["own_unit_ids"])
                                    for g in games}),
        },
        "intent_kinds": dict(kinds.most_common()),
        "command_verbs": dict(verbs.most_common()),
        "intent_by_verb": dict(sorted(cross.items())),
        "controls": controls,
        "per_game": games,
    }
    ok = (report["sweep"]["refused"] == 0
          and controls.get("fired") == controls.get("total")
          and controls_rc == 0)
    report["panel"] = "PASS" if ok else "FAIL"

    os.makedirs(args.out_dir, exist_ok=True)
    out = os.path.join(args.out_dir, "narrate-decode-panel-2026-08-23.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, sort_keys=True)
        fh.write("\n")
    if sample_rows is not None:
        srow = os.path.join(args.out_dir,
                            "narrate-join-sample-%s.json" % args.sample_game)
        with open(srow, "w", encoding="utf-8") as fh:
            json.dump(sample_rows[:400], fh, indent=1, sort_keys=True)
            fh.write("\n")

    summary = {k: report[k] for k in ("panel", "sweep", "intent_kinds",
                                      "command_verbs")}
    summary["controls"] = {"fired": controls.get("fired"),
                           "total": controls.get("total")}
    summary["corpus_digest"] = report["corpus"]["digest_sha256"]
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
