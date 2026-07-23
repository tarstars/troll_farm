#!/usr/bin/env python3
"""Generate the research-only D11 live V7 resident-worker adoption source."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from cgauto.generate_d11_live_actor_v6 import generate_live_source_v6, replace_once


def generate_live_source_v7(
    manifest: dict[str, Any], payload: bytes
) -> tuple[str, dict[str, Any]]:
    source, accounting = generate_live_source_v6(manifest, payload)
    source = replace_once(
        source,
        "map:Map,target:[i8;4],fallback:Option<([i8;4],usize)>,actor:Actor",
        "map:Map,target:[i8;4],fallback:Option<([i8;4],usize)>,adopt:bool,actor:Actor",
    )
    source = replace_once(
        source,
        "fn new(map:Map,target:[i8;4],fallback:Option<([i8;4],usize)>,state:&State)->Self",
        "fn new(map:Map,target:[i8;4],fallback:Option<([i8;4],usize)>,adopt:bool,state:&State)->Self",
    )
    source = replace_once(
        source,
        "map,target,fallback,actor:Actor::new()",
        "map,target,fallback,adopt,actor:Actor::new()",
    )
    source = replace_once(
        source,
        "fn resolve(&mut self,state:&State){\n        if !self.target_built(state)",
        "fn resolve(&mut self,state:&State){\n        if self.adopt{let own=state.own();if own.len()>1{let u=&state.units[own[1]];self.target=[u.ms as i8,u.cc as i8,u.hp as i8,u.chop as i8];}}\n        if !self.target_built(state)",
    )
    source = replace_once(
        source,
        "let recipe=args.get(2).and_then(|s|s.parse::<usize>().ok()).unwrap_or(6).min(7);let fallback=",
        "let recipe=args.get(2).and_then(|s|s.parse::<usize>().ok()).unwrap_or(6).min(7);let adopt=args.iter().any(|s|s==\"--adopt-worker\");let fallback=",
    )
    source = replace_once(
        source,
        "Controller::new(map,RECIPES[recipe],fallback,&first)",
        "Controller::new(map,RECIPES[recipe],fallback,adopt,&first)",
    )
    encoded = source.encode("utf-8")
    accounting = dict(accounting)
    accounting.update(
        {
            "generator_variant": "referee-facing-d11-live-v7-research-resident-worker-adoption",
            "generated_source_bytes": len(encoded),
            "generated_source_sha256": hashlib.sha256(encoded).hexdigest(),
            "under_100000_bytes": len(encoded) < 100_000,
            "semantic_delta": (
                "optional --adopt-worker replaces the observation target with the actual "
                "lowest-ID trained worker before inference"
            ),
            "production_default_delta": "none when --adopt-worker and --fallback are absent",
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
    source, result = generate_live_source_v7(manifest, payload)
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
