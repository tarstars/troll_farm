#!/usr/bin/env python3
"""How long an `MSG` payload has ever come BACK from the platform, measured, not assumed.

Task `20260826-champion-instrument-v6`. The arm's v6 payload is ~328 characters on a busy turn.
Nothing is gained by an instrument whose telemetry the platform truncates on the way into the
corpus, and the capability audit that recorded "`MSG` round trip byte-preserved"
(`docs/BACKLOG.md`) did not record at what LENGTH.

So the length is measured on the corpus we actually hold: every `MSG` payload in
`data/raw/games/*.json`, longest first. These are other bots' messages as the platform gave
them back to us, which is exactly the channel our own telemetry has to survive.

This measures the OBSERVED maximum. It is not a platform limit and must not be quoted as one:
no bot in this corpus tried a longer message, so a longer message is untested, not forbidden.

    python3 claude_1/instrument6/wire_budget.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
GAMES = REPO / "data" / "raw" / "games"
OUR_PAYLOAD_MAX = 328          # census `payload_max_chars`, results/parity-panel.json
MSG_RE = re.compile(r"MSG ([^\";]*)")


def main() -> int:
    files = sorted(GAMES.glob("*.json"))
    if not files:
        print(f"REFUSED: no games under {GAMES}", file=sys.stderr)
        return 2
    longest, example, count, unreadable = 0, None, 0, 0
    histogram: dict[int, int] = {}
    for path in files:
        try:
            blob = json.dumps(json.loads(path.read_text()))
        except (ValueError, OSError):
            unreadable += 1
            continue
        for match in MSG_RE.finditer(blob):
            payload = match.group(1)
            count += 1
            bucket = (len(payload) // 32) * 32
            histogram[bucket] = histogram.get(bucket, 0) + 1
            if len(payload) > longest:
                longest, example = len(payload), payload
    report = {
        "probe": "observed MSG payload length in the collected corpus",
        "task": "20260826-champion-instrument-v6",
        "games_scanned": len(files),
        "games_unreadable": unreadable,
        "msg_payloads": count,
        "longest_observed_chars": longest,
        "longest_observed_example": example[:200] if example else None,
        "length_histogram_by_32": {str(k): histogram[k] for k in sorted(histogram)},
        "our_v6_payload_max_chars": OUR_PAYLOAD_MAX,
        "our_payload_exceeds_anything_observed": OUR_PAYLOAD_MAX > longest,
        "reading": "the longest MSG the platform has ever handed back to us is "
                   f"{longest} characters; ours is {OUR_PAYLOAD_MAX}. That is not a limit, it "
                   "is an absence of evidence, and it is why the first collected game after "
                   "submission has to be decoded before any telemetry is read as data.",
    }
    out = HERE / "results" / "wire-budget.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"  {len(files)} games, {count} MSG payloads, longest observed {longest} chars, "
          f"ours {OUR_PAYLOAD_MAX}  -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
