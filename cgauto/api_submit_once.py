#!/usr/bin/env python3
"""Submit one exact source through the canonical endpoint exactly once.

Unlike the historical compatibility submitter, this tool has no endpoint or payload fallback.
Any non-200, malformed, or transport-ambiguous response stops without another mutation call.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


PUZZLE = "spring-challenge-2026-troll-farm"
USER_ID = 1302251
SESSION_FILE = Path("/home/tarstars/prj/troll_farm/cgauto/cg_session.txt")
LANGUAGES = {".go": "Go", ".rs": "Rust"}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cookie() -> str:
    values = []
    for raw in SESSION_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            name, value = line.split("=", 1)
            if name.strip() == "rememberMe" and value.strip() and "PASTE" not in value:
                values.append(f"{name.strip()}={value.strip()}")
    if not values:
        raise RuntimeError("no usable rememberMe cookie")
    return "; ".join(values)


def call(service: str, method: str, payload: Any) -> tuple[int | None, str]:
    request = urllib.request.Request(
        f"https://www.codingame.com/services/{service}/{method}",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Cookie": cookie(),
            "User-Agent": "Mozilla/5.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode()[:400]
    except Exception as error:  # transport ambiguity is data, never a retry trigger
        return None, f"{type(error).__name__}: {error}"[:400]


def submit_once(source: Path, expected_sha256: str) -> dict[str, Any]:
    digest = sha256_file(source)
    size = source.stat().st_size
    if digest != expected_sha256:
        raise ValueError(f"source hash {digest} != expected {expected_sha256}")
    language = LANGUAGES.get(source.suffix)
    if language is None:
        raise ValueError(f"unsupported source extension {source.suffix}")
    code = source.read_text(encoding="utf-8")
    if len(code) > 100_000:
        raise ValueError(f"source has {len(code)} characters; limit is 100000")

    session_status, session_body = call(
        "Puzzle", "generateSessionFromPuzzlePrettyId", [USER_ID, PUZZLE, False]
    )
    if session_status != 200:
        return {
            "accepted": False,
            "ambiguous": session_status is None or session_status >= 500,
            "phase": "session",
            "http_status": session_status,
            "response": session_body,
            "source": str(source),
            "source_sha256": digest,
            "source_bytes": size,
            "mutation_calls": 0,
        }
    try:
        handle = json.loads(session_body)["handle"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return {
            "accepted": False,
            "ambiguous": True,
            "phase": "session-shape",
            "http_status": session_status,
            "response": "session response omitted: malformed handle",
            "source": str(source),
            "source_sha256": digest,
            "source_bytes": size,
            "mutation_calls": 0,
        }

    submit_status, submit_body = call(
        "TestSession",
        "submit",
        [handle, {"code": code, "programmingLanguageId": language}, None],
    )
    try:
        submission_id = int(json.loads(submit_body)) if submit_status == 200 else None
    except (json.JSONDecodeError, TypeError, ValueError):
        submission_id = None
    accepted = submit_status == 200 and submission_id is not None
    return {
        "accepted": accepted,
        "ambiguous": (submit_status is None or submit_status >= 500 or (submit_status == 200 and not accepted)),
        "phase": "submit",
        "http_status": submit_status,
        "response": str(submission_id) if accepted else submit_body[:400],
        "submission_id": submission_id,
        "source": str(source),
        "source_sha256": digest,
        "source_bytes": size,
        "mutation_calls": 1,
        "endpoint": "TestSession/submit",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--expected-sha256", required=True)
    args = parser.parse_args()
    result = submit_once(args.source.resolve(), args.expected_sha256)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
