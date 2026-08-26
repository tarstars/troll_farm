#!/usr/bin/env python3
"""Export the champion's (door 1, sha256 547fa706...) real ladder games that carry a D-1
dancing episode, sanitised, as one deterministic package for the peer agents.

WHY
---
`20260824-real-game-dance-attribution` second pass: claude_1 classifies the champion's dance
episodes with the same instrument it uses on the NARRATE batches. claude_1 runs on the VM and
cannot read `project_host:data/raw/games/` (untracked build products), so the games it needs
travel through the repo -- exactly as the NARRATE batches did.

SANITISING IS NOT RE-IMPLEMENTED HERE
-------------------------------------
`cgauto/export_agent_replays.py` owns it (`docs/METHODS-LEDGER.md`, `shared-runners`: the
coordinator once committed 149 replays carrying other players' account ids by re-implementing
the export). This script IMPORTS that tool's `sanitize_replay`, `assert_private_keys_absent`
and `canonical`, and calls them verbatim. What it cannot reuse is the battle-list path: the
platform's battle window evicted these agents weeks ago, so no battle listing exists and none
is fabricated -- the package carries replays and a manifest, no battle index, and claims no
opponent submission id.

IDENTITY BEFORE PACKAGING
-------------------------
Every sanitised replay is pushed through the accepted adapter (`claude_1/adapter1`, exported
by `git archive` at the pinned commit) and `detect_d1`; its episodes must equal the ones the
lineage grading recorded for that game, tuple for tuple, or the export aborts. A package that
does not reproduce its own episode list is worthless to the classifier.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from cgauto.export_agent_replays import (  # noqa: E402  (the canonical sanitiser)
    FORBIDDEN_KEYS, assert_private_keys_absent, canonical, sanitize_replay)

PACKAGE = "games-door1-episodes.jsonl.gz"
MANIFEST = "manifest.json"
EPISODES = "episodes-door1.json"
COHORT = "door-1"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_modules(export_dir: str):
    """Same import path the lineage grading used (grade_lineage._worker_init)."""
    sys.path.insert(0, os.path.join(export_dir, "claude_1", "adapter1"))
    sys.path.insert(0, os.path.join(export_dir, "claude_1", "banana-restoration-r2"))
    sys.path.insert(0, export_dir)
    import replay_to_trace  # noqa: E402
    import trace_detectors  # noqa: E402
    return replay_to_trace, trace_detectors


def episode_key(ep: dict) -> tuple:
    return (int(ep["unit"]), int(ep["turn_start"]), int(ep["turn_end"]), int(ep["k"]),
            tuple(tuple(int(v) for v in c) for c in ep["cells"]))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results", required=True,
                    help="lineage-grading-2026-08-24.json (the episode list of record)")
    ap.add_argument("--corpus-dir", required=True, help="project_host data/raw/games/")
    ap.add_argument("--export-dir", required=True,
                    help="git-archive export of agent/claude_1 (adapter + detectors)")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--source-commit", required=True,
                    help="commit of the results file, recorded in the manifest")
    args = ap.parse_args(argv)

    results = json.load(open(args.results, encoding="utf-8"))
    episodes = [e for e in results["episodes"] if e["cohort"] == COHORT]
    by_game: dict[int, dict] = {}
    for e in episodes:
        g = by_game.setdefault(int(e["game"]), {"agent": int(e["agent"]),
                                                "seat": int(e["seat"]), "episodes": []})
        if g["agent"] != int(e["agent"]) or g["seat"] != int(e["seat"]):
            raise SystemExit("two agents/seats of ours in one game: %s" % e["game"])
        g["episodes"].append(e)
    games = sorted(by_game)
    print("door-1 episodes %d in %d games" % (len(episodes), len(games)), flush=True)

    rt, td = load_modules(args.export_dir)

    os.makedirs(args.out_dir, exist_ok=True)
    lines: list[bytes] = []
    manifest_games = []
    for game in games:
        path = os.path.join(args.corpus_dir, "%d.json" % game)
        payload = json.load(open(path, encoding="utf-8"))
        clean = sanitize_replay(payload)              # the canonical sanitiser, verbatim
        assert_private_keys_absent(clean)
        agent = by_game[game]["agent"]
        # identity: the sanitised replay must reproduce the recorded episodes exactly
        trace, meta = rt.adapt_to_trace(clean, agent_id=agent)
        d1 = td.detect_d1(trace)
        if d1["count"] != len(d1["episodes"]):
            raise SystemExit("count/episodes mismatch in game %d" % game)
        got = sorted(episode_key(e) for e in d1["episodes"])
        want = sorted(episode_key(e) for e in by_game[game]["episodes"])
        if got != want or meta["seat"] != by_game[game]["seat"]:
            raise SystemExit("IDENTITY FAILURE game %d: recorded %s, package %s (seat %s/%s)"
                             % (game, want, got, by_game[game]["seat"], meta["seat"]))
        line = canonical(clean)
        lines.append(line)
        manifest_games.append({"game_id": game, "agent_id": agent, "seat": meta["seat"],
                               "traced_turns": meta["traced_turns"],
                               "d1_episodes": len(want),
                               "replay_sha256": sha256_bytes(line)})
        if len(lines) % 50 == 0:
            print("  %d/%d verified" % (len(lines), len(games)), flush=True)

    # deterministic gzip: fixed mtime, no filename
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, filename="") as gz:
        for line in lines:
            gz.write(line)
            gz.write(b"\n")
    package_bytes = buf.getvalue()
    pkg_path = os.path.join(args.out_dir, PACKAGE)
    with open(pkg_path, "wb") as fh:
        fh.write(package_bytes)

    eps_path = os.path.join(args.out_dir, EPISODES)
    with open(eps_path, "wb") as fh:
        fh.write(canonical(sorted(episodes, key=lambda e: (e["game"], e["unit"],
                                                            e["turn_start"]))))
        fh.write(b"\n")

    manifest = {
        "schema": "troll-farm-sanitized-episode-games-v1",
        "purpose": "20260824-real-game-dance-attribution, second pass: the champion's (door 1) "
                   "real ladder games carrying at least one D-1 episode",
        "lineage": COHORT,
        "source_sha256": "547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0",
        "episode_list_of_record": {"path": os.path.relpath(args.results, REPO),
                                   "commit": args.source_commit,
                                   "episodes": len(episodes), "games": len(games)},
        "corpus": "project_host:data/raw/games/ (untracked); one replay per line, sorted by "
                  "game id, canonical JSON (sort_keys, compact)",
        "sanitizer": {"tool": "cgauto/export_agent_replays.py", "functions":
                      ["sanitize_replay", "assert_private_keys_absent", "canonical"],
                      "removed_keys": sorted(FORBIDDEN_KEYS),
                      "note": "no battle listing exists for these agents (window evicted); "
                              "no battle index is shipped and no opponent submission id "
                              "is claimed"},
        "identity_check": "every sanitised replay reproduced its recorded D-1 episodes "
                          "(unit, turn_start, turn_end, k, cells) through the accepted "
                          "adapter + detect_d1 before packaging; seat resolved by agent id",
        "package": PACKAGE, "package_bytes": len(package_bytes),
        "package_sha256": sha256_bytes(package_bytes),
        "episodes_file": EPISODES,
        "episodes_file_sha256": sha256_bytes(open(eps_path, "rb").read()),
        "games": manifest_games,
    }
    with open(os.path.join(args.out_dir, MANIFEST), "wb") as fh:
        fh.write(canonical(manifest))
        fh.write(b"\n")
    print("package %s: %d games, %d bytes, sha256 %s" % (
        pkg_path, len(lines), len(package_bytes), manifest["package_sha256"]), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
