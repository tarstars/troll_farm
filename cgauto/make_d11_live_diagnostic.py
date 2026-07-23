#!/usr/bin/env python3
"""Add per-observation-channel hashes to a closed D11 live source for diagnosis only."""

from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise ValueError(f"diagnostic anchor count {source.count(old)} for {old[:40]!r}")
    return source.replace(old, new, 1)


def instrument(source: str) -> str:
    source = replace_once(
        source,
        "struct Audit{oh:u64,mh:u64,action:usize,id:i32,command:String}",
        "struct Audit{oh:u64,mh:u64,action:usize,id:i32,command:String,channels:Vec<u64>}",
    )
    source = replace_once(
        source,
        "self.previous=(action/AREA)as u8;Audit{oh:fnv(&obs),mh:fnv(&mask),action,id:u.id,command}",
        "let channels=(0..OBS_C).map(|c|fnv(&obs[c*AREA..(c+1)*AREA])).collect();"
        "self.previous=(action/AREA)as u8;Audit{oh:fnv(&obs),mh:fnv(&mask),action,id:u.id,command,channels}",
    )
    source = replace_once(
        source,
        'for r in records{write!(out," {} {} {}",r.oh,r.mh,r.action)?;}',
        'for r in records{let channels=r.channels.iter().map(|v|v.to_string()).collect::<Vec<_>>().join(",");'
        'write!(out," {} {} {} {}",r.oh,r.mh,r.action,channels)?;}',
    )
    return source


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = instrument(args.source.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding="utf-8")
    print(len(result.encode("utf-8")))


if __name__ == "__main__":
    main()
