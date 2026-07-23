#!/usr/bin/env python3
"""Recover the last saved/submitted CodinGame IDE source without submitting it.

The endpoint is read-only. The remember-me cookie is read from ``cg_session.txt`` and is never
printed. By default an existing output is accepted only when it is byte-identical; a differing
file is never overwritten unless ``--force`` is supplied explicitly.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SESSION_FILE = REPO / "cgauto" / "cg_session.txt"
DEFAULT_TSH = "77167730956ef53402472b3c52474908f5b73026"
ENDPOINT = "https://www.codingame.com/services/TestSession/startTestSession"


def remember_me_cookie(path: Path = SESSION_FILE) -> str:
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith("rememberMe="):
            value = line.split("=", 1)[1].strip()
            if value and "PASTE" not in value:
                return f"rememberMe={value}"
    raise RuntimeError(f"no usable rememberMe cookie in {path}")


def find_source(payload: object) -> str:
    """Return the unique string containing a Rust main function."""

    found: list[str] = []

    def walk(value: object) -> None:
        if isinstance(value, dict):
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)
        elif isinstance(value, str) and "fn main" in value:
            found.append(value)

    walk(payload)
    if len(found) != 1:
        raise RuntimeError(f"expected one source candidate, found {len(found)}")
    return found[0]


def fetch_source(test_session_handle: str) -> str:
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps([test_session_handle]).encode(),
        headers={
            "Content-Type": "application/json",
            "Cookie": remember_me_cookie(),
            "User-Agent": "Mozilla/5.0",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode())
    return find_source(payload)


def write_exact(path: Path, source: str, force: bool = False) -> str:
    encoded = source.encode()
    digest = hashlib.sha256(encoded).hexdigest()
    if path.exists():
        existing = path.read_bytes()
        if existing != encoded and not force:
            raise RuntimeError(f"refusing to overwrite differing source: {path}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded)
    checksum = path.with_name(path.name + ".sha256")
    checksum.write_text(f"{digest}  {path.name}\n")
    return digest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="path for the exact recovered source")
    parser.add_argument("--test-session", default=DEFAULT_TSH)
    parser.add_argument("--expected-sha256", help="abort if the recovered source changed")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = fetch_source(args.test_session)
    digest = hashlib.sha256(source.encode()).hexdigest()
    if args.expected_sha256 and digest != args.expected_sha256:
        raise SystemExit(
            f"source hash changed: expected {args.expected_sha256}, recovered {digest}"
        )
    written = write_exact(args.output, source, force=args.force)
    print(f"recovered {len(source)} bytes -> {args.output}")
    print(f"sha256 {written}")


if __name__ == "__main__":
    main()
