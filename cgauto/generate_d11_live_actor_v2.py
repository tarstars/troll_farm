#!/usr/bin/env python3
"""Generate the sole frozen post-transition crop-identity D11 live V2 source."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from cgauto.generate_d11_live_actor import generate_live_source


PROTOCOL_SHA256 = "c881c2d0f2a4ed66ec04162d8e0c90d9f822f8f7afef9c29a2ffc403754fb582"


def replace_once(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise ValueError(f"V2 anchor count {source.count(old)} for {old!r}")
    return source.replace(old, new, 1)


def generate_live_source_v2(
    manifest: dict[str, Any], payload: bytes
) -> tuple[str, dict[str, Any]]:
    source, accounting = generate_live_source(manifest, payload)
    source = replace_once(
        source,
        "pending_harvests:Vec<(i32,i32)>",
        "pending_harvests:Vec<(i32,i32,(usize,usize))>",
    )
    source = replace_once(
        source,
        "for (id,before) in self.pending_harvests.drain(..){if state.unit(id).is_some_and(|u|u.carry[3]>before){self.renewable=self.renewable.saturating_add(1);}}",
        "for (id,before,cell) in self.pending_harvests.drain(..){if self.created==Some(cell)&&state.unit(id).is_some_and(|u|u.carry[3]>before){self.renewable=self.renewable.saturating_add(1);}}",
    )
    source = replace_once(
        source,
        "self.pending_harvests.push((u.id,u.carry[3]));",
        "self.pending_harvests.push((u.id,u.carry[3],(u.x,u.y)));",
    )
    encoded = source.encode("utf-8")
    accounting = dict(accounting)
    accounting.update(
        {
            "generator_variant": "referee-facing-fixed-recipe6-live-v2-crop-identity",
            "protocol_sha256": PROTOCOL_SHA256,
            "generated_source_bytes": len(encoded),
            "generated_source_sha256": hashlib.sha256(encoded).hexdigest(),
            "under_100000_bytes": len(encoded) < 100_000,
            "semantic_delta": "pending harvest increments only for the post-transition tracked crop cell",
        }
    )
    return source, accounting


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("payload", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    payload = args.payload.read_bytes()
    source, result = generate_live_source_v2(manifest, payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(source, encoding="utf-8")
    result.update(
        {
            "manifest_path": str(args.manifest.resolve()),
            "manifest_sha256": hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
            "payload_path": str(args.payload.resolve()),
            "output_path": str(args.output.resolve()),
        }
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
