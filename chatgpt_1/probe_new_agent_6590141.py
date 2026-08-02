#!/usr/bin/env python3
"""Read-only public CodinGame battle probe for agent 6590141.

The public remote-service endpoint requires only the agent id.  This probe publishes the
response shape before the stricter submission-scoped extractor is locked.  It performs no
Arena/TestSession mutation and uses no session cookie.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

AGENT_ID = 6590141
BASE = "https://www.codingame.com/services/"
ENDPOINT = "gamesPlayersRankingRemoteService/findLastBattlesAndProgressByAgentId"
OUTPUT = Path("chatgpt_1/new-agent-6590141-public-battles-probe.json")


def post(service: str, payload: Any) -> Any:
    request = Request(
        BASE + service,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "troll-farm-read-only-sector-audit/1",
        },
        method="POST",
    )
    with urlopen(request, timeout=60) as response:
        return json.load(response)


def summarize(value: Any, depth: int = 0) -> Any:
    """Preserve enough shape to lock a parser without duplicating a huge response."""
    if depth >= 5:
        if isinstance(value, dict):
            return {"__type__": "dict", "keys": sorted(value)[:40], "size": len(value)}
        if isinstance(value, list):
            return {"__type__": "list", "size": len(value)}
        return value
    if isinstance(value, dict):
        return {key: summarize(child, depth + 1) for key, child in value.items()}
    if isinstance(value, list):
        limit = 8 if depth <= 2 else 3
        return [summarize(child, depth + 1) for child in value[:limit]] + (
            [{"__truncated__": len(value) - limit}] if len(value) > limit else []
        )
    return value


def collect_key_paths(value: Any, prefix: str = "$") -> dict[str, int]:
    counts: dict[str, int] = {}
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}"
            counts[path] = counts.get(path, 0) + 1
            nested = collect_key_paths(child, path)
            for nested_path, amount in nested.items():
                counts[nested_path] = counts.get(nested_path, 0) + amount
    elif isinstance(value, list):
        for child in value:
            nested = collect_key_paths(child, prefix + "[]")
            for nested_path, amount in nested.items():
                counts[nested_path] = counts.get(nested_path, 0) + amount
    return counts


def main() -> int:
    raw = post(ENDPOINT, [AGENT_ID, None])
    encoded = json.dumps(raw, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload = {
        "schema": "troll-farm-public-agent-battle-probe/1",
        "agent_id": AGENT_ID,
        "endpoint": ENDPOINT,
        "request_body": [AGENT_ID, None],
        "response_type": type(raw).__name__,
        "response_bytes_canonical": len(encoded),
        "top_level_keys": sorted(raw) if isinstance(raw, dict) else None,
        "top_level_length": len(raw) if isinstance(raw, (dict, list)) else None,
        "key_paths": collect_key_paths(raw),
        "shape_sample": summarize(raw),
    }
    OUTPUT.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved {OUTPUT}; response bytes={len(encoded)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
