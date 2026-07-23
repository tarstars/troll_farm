#!/usr/bin/env python3
"""Build the frozen standalone Norxondor three-worker field candidate.

The generated source contains the exact verified Yamo protocol/game module and the shared
submission-oriented policy module.  It deliberately excludes the large resident controller.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.compact_rust_source import compact  # noqa: E402
from cgauto.slim_live_source import _matching_brace  # noqa: E402


DEFAULT_PROTOCOL = REPO / "rust/src/bin/yamo_orchard_live.rs"
DEFAULT_POLICY = REPO / "rust/src/norxondor_three_worker_live_bot.rs"
DEFAULT_OUTPUT = (
    REPO
    / "cgauto/submissions/candidate-agent6553250-norxondor-three-worker-silver.min.rs"
)


def extract_game_module(source: str) -> str:
    marker = "pub mod game {"
    if source.count(marker) != 1:
        raise ValueError(f"expected one standalone game module, found {source.count(marker)}")
    start = source.index(marker)
    opening = source.index("{", start)
    end = _matching_brace(source, opening) + 1
    return source[start:end]


def build_source(protocol_source: str, policy_source: str) -> str:
    game = extract_game_module(protocol_source)
    return (
        "#![allow(dead_code,unused_imports)]\n"
        + game
        + "\nmod norxondor_three_worker_live_bot{\n"
        + policy_source
        + "\n}\n"
        + "use crate::game::protocol::{read_static_map,read_turn};\n"
        + "use crate::norxondor_three_worker_live_bot::NorxondorThreeWorkerBot;\n"
        + "use std::io::{self,Write};\n"
        + "fn main(){let stdin=io::stdin();let stdout=io::stdout();"
        + "let mut reader=io::BufReader::new(stdin.lock());"
        + "let mut out=io::BufWriter::new(stdout.lock());"
        + "let Some(map)=read_static_map(&mut reader)else{return;};"
        + "let mut bot=NorxondorThreeWorkerBot::new();let mut turn=1;"
        + "while let Some(view)=read_turn(&mut reader,&map,turn){"
        + "let commands=bot.commands(&view);"
        + 'writeln!(out,"{}",commands.join(";")).expect("write command line");'
        + 'out.flush().expect("flush command line");turn+=1;}}\n'
    )


def digest(source: str) -> str:
    return hashlib.sha256(source.encode()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--formatted-output", type=Path)
    args = parser.parse_args()

    formatted = build_source(args.protocol.read_text(), args.policy.read_text())
    candidate = compact(formatted)
    if len(candidate.encode()) > 100_000:
        raise SystemExit(f"candidate is {len(candidate.encode())} bytes (>100000)")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(candidate)
    args.output.with_name(args.output.name + ".sha256").write_text(
        f"{digest(candidate)}  {args.output.name}\n"
    )
    if args.formatted_output:
        args.formatted_output.parent.mkdir(parents=True, exist_ok=True)
        args.formatted_output.write_text(formatted)
    print(
        f"candidate {args.output}: {len(candidate.encode())} bytes "
        f"sha256 {digest(candidate)}"
    )


if __name__ == "__main__":
    main()

