#!/usr/bin/env python3
"""Prove that fork F3 IS the as-built arm — not "close to it", byte for byte, game for game.

The revision controls (`revision_controls.py`) claim that flipping `TRANSIENT_ONLY` and
`P3_SCOPING_ENABLED` back to false turns the revised source into the arm the G-1 ruling failed.
That claim is what licenses reading F3's numbers as the as-built numbers, so it is checked rather
than asserted: the as-built arms are extracted from their own commit, run on the identical corpus,
and every one of the 240 command streams is compared with F3's.

The as-built arms are taken from `agent/claude_1@abeda52a` — the commit the G-1 handoff pinned —
with `git show`, so nothing depends on a file left lying around in the worktree.

A difference here would not be a small discrepancy. It would mean the rebuild changed behaviour
somewhere other than the two clauses it was ordered to change, and every "the revision cost X"
number in the report would be uninterpretable.

    python3 claude_1/cure1/asbuilt_reproduction.py
"""
from __future__ import annotations

import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
COMMIT = "abeda52a6f42d6f34e57e5268c9a7188732b98f3"
OUT = HERE / "results" / "as-built-reproduction.json"
SCRATCH = Path("/tmp/claude-1000/cure1")


def streams(path: Path) -> dict:
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return {(g["map_id"], g["seat"]): g["artifacts"]["candidate_commands"]
                for g in (json.loads(l) for l in fh)}


def main() -> int:
    report = {
        "check": "fork F3 (both revisions flipped back) == the as-built arm, byte for byte",
        "as_built_commit": COMMIT,
        "arms": {},
        "verdict": "PASS",
    }
    for arm in ("candidate", "instrument"):
        blob = subprocess.run(["git", "-C", str(REPO), "show",
                               f"{COMMIT}:claude_1/cure1/arm-{arm}.rs"],
                              capture_output=True, text=True, timeout=120)
        if blob.returncode:
            print(f"REFUSED: cannot read arm-{arm}.rs from {COMMIT[:8]}: {blob.stderr[:300]}")
            return 2
        src = HERE / f"asbuilt-{arm}.rs"
        src.write_text(blob.stdout)
        sha = hashlib.sha256(blob.stdout.encode()).hexdigest()
        cfg = json.loads((HERE / f"cure1-{arm}-config.json").read_text())
        cfg["task"] = f"AS-BUILT REPRODUCTION ({COMMIT[:8]}) — not a candidate"
        cfg["candidate"] = {"crate": f"asbuilt_{arm}", "sha256": sha,
                            "source": f"../../claude_1/cure1/asbuilt-{arm}.rs"}
        cfg["games_dir"] = str(SCRATCH / f"asbuilt-{arm}" / "games")
        cfg_path = HERE / f"asbuilt-{arm}-config.json"
        cfg_path.write_text(json.dumps(cfg, indent=2, sort_keys=True) + "\n")
        done = subprocess.run(
            [sys.executable, str(REPO / "claude_1/pipeline/fuzz_panel.py"), "--config",
             str(cfg_path), "--report", f"/tmp/asbuilt-{arm}.md",
             "--json", f"/tmp/asbuilt-{arm}.json"],
            capture_output=True, text=True, timeout=3600)
        print(f"    as-built {arm}: " + (done.stdout.strip().split("\n")[-1]
                                         if done.stdout.strip() else done.stderr[-300:]))
        a = streams(SCRATCH / f"asbuilt-{arm}" / "games" / "games.jsonl.gz")
        b = streams(SCRATCH / f"F3-as-built-policy-{arm}" / "games" / "games.jsonl.gz")
        differing = sorted(k for k in a if a.get(k) != b.get(k))
        report["arms"][arm] = {
            "as_built_sha256": sha, "games": len(a),
            "differing_command_streams": len(differing),
            "differing_games": [{"map_id": k[0], "seat": k[1]} for k in differing[:20]],
            "same_game_set": set(a) == set(b),
        }
        if differing or set(a) != set(b):
            report["verdict"] = "FAIL"
        src.unlink()
        cfg_path.unlink()
        print(f"      {len(a)} games, {len(differing)} differing command streams")
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"\n  as-built reproduction: {report['verdict']}   -> {OUT}")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
