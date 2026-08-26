#!/usr/bin/env python3
"""Independent checks behind claude_1's T-G1 / F-G1 review of codex_1's
2026-08-26 first table (commit 8f00a140) — read-only on the processed corpus.

Each check prints one line the review quotes verbatim.  Nothing is written.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import statistics
from pathlib import Path

CORPUS_SHA256 = "150a5507e90c2c00a5d22b34abf19b7a0ad933fc3b31e3abf3521d3bc4dc4d24"
B100_AGENT = 6590083
COHORT = {
    6480541: "yaichi", 6491563: "Stounate", 6480520: "skotz", 6483545: "Escdemon",
    6559862: "therealbeef", 6479814: "yamo", 6479779: "putibuzu", 6479420: "Risen",
    6479657: "Konstant", 6520935: "goq", 6480943: "Dridriun", 6479750: "mehdi_ayari",
    6481252: "DaNinja", 6541379: "GoodDevel", 6483491: "VINCE_MX", 6480951: "0x6E0FF",
    6479388: "Kheopsian", 6541416: "Ticasali", 6479931: "abdelmathin", 6488436: "NOIIICE",
    6505289: "tonigineer", 6481094: "Shun_PI", 6488432: "anuragm", 6499915: "LeRenard",
    6535596: "FRHT",
}
# the two owner-side ladder checkpoints for the b100 submission 41081195
B100_CHECKPOINTS = (
    "data/analysis/live-agent-6553250/owner-banana-factory-b100-reconvergence-checkpoint-20260802T162907Z.json",
    "data/analysis/live-agent-6553250/owner-banana-factory-b100-initial-checkpoint-20260802T1600Z.json",
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=Path("."))
    args = parser.parse_args()

    digest = hashlib.sha256(args.corpus.read_bytes()).hexdigest()
    print(f"[1] corpus sha256 {digest} match={digest == CORPUS_SHA256}")

    names = collections.defaultdict(collections.Counter)
    train_cmd = collections.Counter()
    train_eff = collections.Counter()
    train_mismatch = collections.Counter()
    coh_games = collections.Counter()
    score_exact = score_all = 0
    tass = collections.defaultdict(lambda: {"n": 0, "banana": 0})
    b100_rows = []
    rows = 0
    with args.corpus.open() as source:
        for line in source:
            game = json.loads(line)
            rows += 1
            for seat in (0, 1):
                player = game["players"][seat]
                pp = game["per_player"][str(seat)]
                inv = pp.get("final_inv") or [0] * 6
                score_all += 1
                score_exact += (game["scores"][seat] == sum(inv[:4]) + 4 * inv[5])
                aid, name = player["agentId"], player.get("name")
                if aid in COHORT:
                    names[aid][name] += 1
                    coh_games[aid] += 1
                    train_cmd[aid] += len(pp.get("trains") or [])
                    n_cmd = len(pp.get("trains") or [])
                    n_eff = (pp.get("effects") or {}).get("trained", 0)
                    train_eff[aid] += n_eff
                    train_mismatch[aid] += (n_cmd != n_eff)
                if name == "tass":
                    box = tass[aid]
                    box["n"] += 1
                    box["banana"] += (pp.get("planted_ok") or {}).get("BANANA", 0)
                if aid == B100_AGENT:
                    b100_rows.append(game["gameId"])

    bad = [(aid, COHORT[aid], dict(c)) for aid, c in names.items() if set(c) != {COHORT[aid]}]
    print(f"[2] rows={rows} cohort ids present={len(names)}/25 name mismatches={bad or 'none'}")
    print(f"[3] score == sum(final_inv[:4]) + 4*final_inv[5] on {score_exact}/{score_all} sides "
          f"({100 * score_exact / score_all:.2f}%)")
    worst = max(COHORT, key=lambda a: train_mismatch[a] / max(1, coh_games[a]))
    print(f"[4] TRAIN commands vs referee-confirmed trainings: the two disagree on "
          f"{sum(train_mismatch.values())} of {sum(coh_games.values())} cohort sides; worst agent "
          f"{COHORT[worst]} {train_mismatch[worst]}/{coh_games[worst]} games "
          f"({100 * train_mismatch[worst] / coh_games[worst]:.1f}%), "
          f"{train_cmd[worst]} commands vs {train_eff[worst]} confirmed")
    per = [b["banana"] / b["n"] for b in tass.values() if b["n"] >= 50]
    print(f"[5] occurrences named 'tass' = {sum(b['n'] for b in tass.values())} across "
          f"{len(tass)} distinct agent ids; BANANA plants/game over the {len(per)} lineages with "
          f">=50 games spans {min(per):.2f}..{max(per):.2f}")

    recorded = set()
    for rel in B100_CHECKPOINTS:
        data = json.loads((args.repo / rel).read_text())
        assert data["agent_id"] == B100_AGENT and data["submission_id"] == 41081195, rel
        recorded |= {r["game_id"] for r in data["rows"]}
    scored = [r for r in json.loads((args.repo / B100_CHECKPOINTS[0]).read_text())["rows"]
              if r.get("our_score") is not None]
    margins = [r["margin"] for r in scored]
    print(f"[6] b100 ladder games recorded by the owner-side checkpoints = {len(recorded)}; "
          f"in the corpus = {len(set(b100_rows) & recorded)} ({sorted(set(b100_rows))})")
    print(f"[7] those checkpoints carry final scores for {len(scored)} games; mean margin "
          f"{statistics.mean(margins):+.1f}, losses {sum(1 for m in margins if m < 0)}, "
          f"worst {min(margins):+.0f}")


if __name__ == "__main__":
    main()
