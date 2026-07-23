#!/usr/bin/env python3
"""Generate the research-only D11 live V6 target-fallback source."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from cgauto.generate_d11_live_actor_v5 import generate_live_source_v5


def replace_once(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise ValueError(f"V6 anchor count {source.count(old)} for {old[:100]!r}")
    return source.replace(old, new, 1)


def generate_live_source_v6(
    manifest: dict[str, Any], payload: bytes
) -> tuple[str, dict[str, Any]]:
    source, accounting = generate_live_source_v5(manifest, payload)
    source = replace_once(
        source,
        "map:Map,target:[i8;4],actor:Actor",
        "map:Map,target:[i8;4],fallback:Option<([i8;4],usize)>,actor:Actor",
    )
    source = replace_once(
        source,
        "fn new(map:Map,target:[i8;4],state:&State)->Self",
        "fn new(map:Map,target:[i8;4],fallback:Option<([i8;4],usize)>,state:&State)->Self",
    )
    source = replace_once(
        source,
        "map,target,actor:Actor::new()",
        "map,target,fallback,actor:Actor::new()",
    )
    source = replace_once(
        source,
        "fn resolve(&mut self,state:&State){\n        let crop_exists",
        "fn resolve(&mut self,state:&State){\n        if !self.target_built(state){if let Some((target,turn))=self.fallback{if state.turn>=turn{self.target=target;self.fallback=None;}}}\n        let crop_exists",
    )
    source = replace_once(
        source,
        "let recipe=args.get(2).and_then(|s|s.parse::<usize>().ok()).unwrap_or(6).min(7);",
        "let recipe=args.get(2).and_then(|s|s.parse::<usize>().ok()).unwrap_or(6).min(7);let fallback=args.iter().position(|s|s==\"--fallback\").and_then(|i|Some((RECIPES[args.get(i+1)?.parse::<usize>().ok()?.min(7)],args.get(i+2)?.parse::<usize>().ok()?)));",
    )
    source = replace_once(
        source,
        "Controller::new(map,RECIPES[recipe],&first)",
        "Controller::new(map,RECIPES[recipe],fallback,&first)",
    )
    encoded = source.encode("utf-8")
    accounting = dict(accounting)
    accounting.update(
        {
            "generator_variant": "referee-facing-d11-live-v6-research-target-fallback",
            "generated_source_bytes": len(encoded),
            "generated_source_sha256": hashlib.sha256(encoded).hexdigest(),
            "under_100000_bytes": len(encoded) < 100_000,
            "semantic_delta": (
                "optional --fallback RECIPE TURN changes the requested target before "
                "decision inference when the original target is still unbuilt"
            ),
            "production_default_delta": "none when --fallback is absent",
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
    source, result = generate_live_source_v6(manifest, payload)
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
