#!/usr/bin/env python3
"""Generate the sole frozen persistent own-removal D11 live V4 source."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from cgauto.generate_d11_live_actor_v3 import generate_live_source_v3


PROTOCOL_SHA256 = "7cef1c1bc8cc5e19a6271e953d2260695279658ab1c029ff38f1d0cb324363d4"


def replace_once(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise ValueError(f"V4 anchor count {source.count(old)} for {old!r}")
    return source.replace(old, new, 1)


def generate_live_source_v4(
    manifest: dict[str, Any], payload: bytes
) -> tuple[str, dict[str, Any]]:
    source, accounting = generate_live_source_v3(manifest, payload)
    source = replace_once(
        source,
        "pending_chops:Vec<(usize,usize)>",
        "pending_chops:Vec<(usize,usize)>,own_removed_crop:bool",
    )
    source = replace_once(
        source,
        "pending_chops:Vec::new()",
        "pending_chops:Vec::new(),own_removed_crop:false",
    )
    source = replace_once(
        source,
        "let own_chop=self.created.is_some_and(|cell|self.pending_chops.contains(&cell));"
        "if self.created.is_some()&&!self.crop_exists(state)&&!own_chop{self.created=None;}self.pending_chops.clear();",
        "let crop_exists=self.crop_exists(state);let own_chop=self.created.is_some_and(|cell|self.pending_chops.contains(&cell));"
        "if crop_exists{self.own_removed_crop=false;}else if own_chop{self.own_removed_crop=true;}"
        "else if self.created.is_some()&&!self.own_removed_crop{self.created=None;}self.pending_chops.clear();",
    )
    source = replace_once(
        source,
        "for (x,y) in self.pending_plants.drain(..){if state.plant_at(x,y).is_some_and(|p|p.k==3){self.created=Some((x,y));}}",
        "for (x,y) in self.pending_plants.drain(..){if state.plant_at(x,y).is_some_and(|p|p.k==3){self.created=Some((x,y));self.own_removed_crop=false;}}",
    )
    encoded = source.encode("utf-8")
    accounting = dict(accounting)
    accounting.update(
        {
            "generator_variant": "referee-facing-fixed-recipe6-live-v4-persistent-own-removal",
            "protocol_sha256": PROTOCOL_SHA256,
            "generated_source_bytes": len(encoded),
            "generated_source_sha256": hashlib.sha256(encoded).hexdigest(),
            "under_100000_bytes": len(encoded) < 100_000,
            "semantic_delta": "persist an own-removed tracked crop coordinate until it exists or is replaced",
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
    source, result = generate_live_source_v4(manifest, payload)
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
