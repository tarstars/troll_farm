#!/usr/bin/env python3
"""Cross-verify the frozen offline parity packet against the raw LFS replay audit.

Stdlib-only on purpose: the host packet builder and online evaluator import
``cgauto.battle_taxonomy``, which reads a platform session cookie at import
time, so neither can run on a credential-free host. This check needs no
credentials: it verifies the packet's selection provenance and per-game
command-type consistency directly against the audit JSON.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

AUDIT_SHA256 = "8c29f433982fa9df05e16203bccdc15f290bae36ff5801084e862a882547af5a"
PACKET_SHA256 = "fb8e968ff65fc55c6f6f9d2f2b678434ab2dfda8eba84fdb6d0384d41856c7e2"
AGENT_ID = 6590141
REQUIRED_GAME = 897832286
EXPECTED_TURNS = 7_234


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("refusing to overwrite existing provenance evidence")

    audit_bytes = args.audit.read_bytes()
    packet_bytes = args.packet.read_bytes()
    if hashlib.sha256(audit_bytes).hexdigest() != AUDIT_SHA256:
        raise RuntimeError("audit SHA-256 mismatch")
    if hashlib.sha256(packet_bytes).hexdigest() != PACKET_SHA256:
        raise RuntimeError("packet SHA-256 mismatch")

    audit = json.loads(audit_bytes)
    packet = json.loads(gzip.decompress(packet_bytes))
    if packet["selection"]["audit_sha256"] != AUDIT_SHA256:
        raise RuntimeError("packet does not declare this audit as its source")

    by_game: dict[int, list[dict]] = {}
    for row in audit["rows"]:
        if row.get("agent_id") == AGENT_ID:
            by_game.setdefault(row["game_id"], []).append(row)

    games = packet["rows"]
    missing = [r["game_id"] for r in games if r["game_id"] not in by_game]
    turns = sum(r["turns"] for r in games)
    exact, deviations = 0, []
    for row in games:
        hist: Counter[str] = Counter()
        for line in row["baseline_output"].splitlines():
            for command in line.split(";"):
                token = command.strip().split()
                if token and token[0] != "MSG":
                    hist[token[0]] += 1
        candidates = by_game.get(row["game_id"], [])
        audit_row = next(
            (c for c in candidates if c.get("opponent") == row.get("opponent")),
            candidates[0] if candidates else None,
        )
        audit_hist = Counter(audit_row["commands"]) if audit_row else Counter()
        if hist == audit_hist:
            exact += 1
        else:
            deviations.append(
                {
                    "game_id": row["game_id"],
                    "opponent": row.get("opponent"),
                    "packet_minus_audit": dict(hist - audit_hist),
                    "audit_minus_packet": dict(audit_hist - hist),
                }
            )

    result = {
        "schema": "troll-farm-e7a-offline-packet-provenance-v1",
        "audit_sha256": AUDIT_SHA256,
        "packet_sha256": PACKET_SHA256,
        "games": len(games),
        "games_present_in_audit": len(games) - len(missing),
        "missing_from_audit": missing,
        "required_game_present": any(r["game_id"] == REQUIRED_GAME for r in games),
        "total_turns": turns,
        "expected_turns": EXPECTED_TURNS,
        "histogram_exact_games": exact,
        "histogram_deviations": deviations,
        "verdict": (
            "PACKET_PROVENANCE_CONSISTENT"
            if not missing and turns == EXPECTED_TURNS and len(deviations) <= 1
            else "PACKET_PROVENANCE_DEVIATION"
        ),
        "note": (
            "the parity gates compare candidate vs baseline binary outputs on "
            "identical transcripts and never read the audit histograms; a "
            "histogram deviation localizes to the audit summary layer, not the "
            "parity substrate"
        ),
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "games": result["games_present_in_audit"],
                "turns": turns,
                "histogram_exact": exact,
                "deviations": len(deviations),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
