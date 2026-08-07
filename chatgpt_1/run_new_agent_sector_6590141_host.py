#!/usr/bin/env python3
"""Host runner for :mod:`new_agent_sector_6590141_collect`.

Adds the repository session cookie when available and applies one input-normalization shim for
agent index 0. The core collector originally used ``row.get('index') or -1`` in one opponent
lookup, so integer zero was treated as missing. Re-encoding only that index as the truthy string
``"0"`` preserves ``int(index) == 0`` everywhere while avoiding a seat-1 false failure. Raw
responses are never written to Git.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from chatgpt_1 import new_agent_sector_6590141_collect as core

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SESSION = ROOT / "cgauto/cg_session.txt"


def session_cookie() -> str:
    path = Path(os.environ.get("CG_SESSION_FILE", DEFAULT_SESSION))
    if not path.exists():
        return ""
    parts = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if value.strip() and "PASTE" not in value:
            parts.append(f"{name.strip()}={value.strip()}")
    return "; ".join(parts)


def post(service: str, payload: Any, retries: int = 4) -> Any:
    cookie = session_cookie()
    last: Exception | None = None
    for attempt in range(retries):
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "troll-farm-read-only-live-sector-audit/1",
        }
        if cookie:
            headers["Cookie"] = cookie
        request = Request(
            core.BASE + service,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urlopen(request, timeout=90) as response:
                result = json.load(response)
            if service == core.GAME_SERVICE and isinstance(result, dict):
                for agent in result.get("agents") or []:
                    if agent.get("index") == 0:
                        agent["index"] = "0"
            return result
        except (HTTPError, URLError, TimeoutError) as error:
            last = error
            if attempt + 1 == retries:
                break
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"read-only service failed: {service}: {last}")


def main() -> int:
    core.post = post
    return core.main()


if __name__ == "__main__":
    raise SystemExit(main())
