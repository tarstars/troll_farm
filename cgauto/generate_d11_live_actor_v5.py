#!/usr/bin/env python3
"""Generate the sole frozen persistent-buffer D11 live V5 source."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from cgauto.generate_d11_live_actor_v4 import generate_live_source_v4


PROTOCOL_SHA256 = "428c2f00a27214d01be73a2c8486f71b4e87acfb92c4c5691238875eb45d288d"


OLD_PHASE = """    fn phase(&mut self,state:&State,ui:usize,phase:u8)->Audit{let mut obs=vec![0u8;OBS_C*AREA];let mut mask=vec![0u8;ACTIONS];self.observe(state,ui,phase,&mut obs,&mut mask);
        let mut logits=vec![0.0f32;ACTIONS];self.actor.forward(&obs,&mut logits);let action=masked_argmax(&logits,&mask);let u=&state.units[ui];let command=Self::command(action,u);
        self.previous=(action/AREA)as u8;Audit{oh:fnv(&obs),mh:fnv(&mask),action,id:u.id,command}
    }
"""

NEW_PHASE = """    fn phase(&mut self,state:&State,ui:usize,phase:u8)->Audit{let mut obs=std::mem::take(&mut self.obs);let mut mask=std::mem::take(&mut self.mask);self.observe(state,ui,phase,&mut obs,&mut mask);
        let mut logits=std::mem::take(&mut self.logits);self.actor.forward(&obs,&mut logits);let action=masked_argmax(&logits,&mask);let u=&state.units[ui];let command=Self::command(action,u);
        let audit=Audit{oh:fnv(&obs),mh:fnv(&mask),action,id:u.id,command};self.obs=obs;self.mask=mask;self.logits=logits;self.previous=(action/AREA)as u8;audit
    }
"""


def replace_once(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise ValueError(f"V5 anchor count {source.count(old)} for {old[:80]!r}")
    return source.replace(old, new, 1)


def generate_live_source_v5(
    manifest: dict[str, Any], payload: bytes
) -> tuple[str, dict[str, Any]]:
    source, accounting = generate_live_source_v4(manifest, payload)
    source = replace_once(
        source,
        "pending_chops:Vec<(usize,usize)>,own_removed_crop:bool",
        "pending_chops:Vec<(usize,usize)>,own_removed_crop:bool,obs:Vec<u8>,mask:Vec<u8>,logits:Vec<f32>",
    )
    source = replace_once(
        source,
        "pending_chops:Vec::new(),own_removed_crop:false",
        "pending_chops:Vec::new(),own_removed_crop:false,obs:vec![0u8;OBS_C*AREA],mask:vec![0u8;ACTIONS],logits:vec![0.0f32;ACTIONS]",
    )
    source = replace_once(source, OLD_PHASE, NEW_PHASE)
    encoded = source.encode("utf-8")
    accounting = dict(accounting)
    accounting.update(
        {
            "generator_variant": "referee-facing-fixed-recipe6-live-v5-persistent-phase-buffers",
            "protocol_sha256": PROTOCOL_SHA256,
            "generated_source_bytes": len(encoded),
            "generated_source_sha256": hashlib.sha256(encoded).hexdigest(),
            "under_100000_bytes": len(encoded) < 100_000,
            "semantic_delta": "none; observation, mask, and logits buffers are allocated once and reused",
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
    source, result = generate_live_source_v5(manifest, payload)
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
