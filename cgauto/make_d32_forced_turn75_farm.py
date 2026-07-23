#!/usr/bin/env python3
"""Generate the D32 TestSession-only forced turn-75 farm source."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "cgauto/submissions/candidate-agent6553250-d29b-spatial-option-critic.min.rs"
OUTPUT = REPO / "cgauto/submissions/diagnostic-agent6553250-d32-forced-turn75-farm.min.rs"
SOURCE_SHA256 = "f074a553804a638d32cf97fe6e2e3cd2c718c4205ad79d6dfb2d6c7dde21c528"
CONTROLLER_PREFIX = "impl Bot for D{fn commands(&mut self,v:&crate::game::GameState)->Vec<String>{"
FROZEN_DECISION = "self.s=d29k::p(&b)"
FORCED_DECISION = "let _=d29k::p(&b);self.s=true"


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def generate(source_path: Path) -> bytes:
    source = source_path.read_bytes()
    if sha256(source) != SOURCE_SHA256:
        raise ValueError("frozen D29b source SHA differs")
    text = source.decode()
    start = text.rfind(CONTROLLER_PREFIX)
    if start < 0 or text.find(CONTROLLER_PREFIX) != start:
        raise ValueError("D29b controller anchor is not unique")
    if not text[start:].startswith(CONTROLLER_PREFIX) or not text[start:].endswith("}"):
        raise ValueError("D29b controller tail differs")
    controller = text[start:]
    if controller.count(FROZEN_DECISION) != 1:
        raise ValueError("D29b controller decision is not unique")
    generated = (text[:start] + controller.replace(FROZEN_DECISION, FORCED_DECISION) + "\n").encode()
    if generated.count(b"v.turn==75") != 1:
        raise ValueError("forced turn-75 switch is not unique")
    if generated.count(b"self.s=true") != 1 or FROZEN_DECISION.encode() in generated:
        raise ValueError("forced decision replacement differs")
    if len(generated) > 100_000:
        raise ValueError(f"D32 diagnostic is {len(generated)} bytes")
    return generated


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    generated = generate(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(generated)
    digest = sha256(generated)
    args.output.with_suffix(args.output.suffix + ".sha256").write_text(
        f"{digest}  {args.output.name}\n"
    )
    print(f"wrote {args.output} bytes={len(generated)} sha256={digest}")


if __name__ == "__main__":
    main()
