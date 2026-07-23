#!/usr/bin/env python3
"""Generate the sole frozen witnessed-own-CHOP D11 live V3 source."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from cgauto.generate_d11_live_actor_v2 import generate_live_source_v2


PROTOCOL_SHA256 = "dfb95a39bc2f2c4b6e3cf245940c53f718ffaf8ee33e4d6089ac31b3c5731f80"


def replace_once(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise ValueError(f"V3 anchor count {source.count(old)} for {old!r}")
    return source.replace(old, new, 1)


def generate_live_source_v3(
    manifest: dict[str, Any], payload: bytes
) -> tuple[str, dict[str, Any]]:
    source, accounting = generate_live_source_v2(manifest, payload)
    source = replace_once(
        source,
        "pending_plants:Vec<(usize,usize)>,pending_harvests:Vec<(i32,i32,(usize,usize))>",
        "pending_plants:Vec<(usize,usize)>,pending_harvests:Vec<(i32,i32,(usize,usize))>,pending_chops:Vec<(usize,usize)>",
    )
    source = replace_once(
        source,
        "pending_plants:Vec::new(),pending_harvests:Vec::new()",
        "pending_plants:Vec::new(),pending_harvests:Vec::new(),pending_chops:Vec::new()",
    )
    source = replace_once(
        source,
        "if self.created.is_some()&&!self.crop_exists(state){self.created=None;}",
        "let own_chop=self.created.is_some_and(|cell|self.pending_chops.contains(&cell));"
        "if self.created.is_some()&&!self.crop_exists(state)&&!own_chop{self.created=None;}self.pending_chops.clear();",
    )
    source = replace_once(
        source,
        "if plane==1&&self.created==Some((u.x,u.y)){self.pending_harvests.push((u.id,u.carry[3],(u.x,u.y)));}",
        "if plane==1&&self.created==Some((u.x,u.y)){self.pending_harvests.push((u.id,u.carry[3],(u.x,u.y)));}"
        "if plane==2&&self.created==Some((u.x,u.y)){self.pending_chops.push((u.x,u.y));}",
    )
    encoded = source.encode("utf-8")
    accounting = dict(accounting)
    accounting.update(
        {
            "generator_variant": "referee-facing-fixed-recipe6-live-v3-own-chop-witness",
            "protocol_sha256": PROTOCOL_SHA256,
            "generated_source_bytes": len(encoded),
            "generated_source_sha256": hashlib.sha256(encoded).hexdigest(),
            "under_100000_bytes": len(encoded) < 100_000,
            "semantic_delta": "retain a missing tracked crop cell only after a witnessed own CHOP on that cell",
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
    source, result = generate_live_source_v3(manifest, payload)
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
