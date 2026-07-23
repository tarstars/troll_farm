#!/usr/bin/env python3
"""Assemble the exact D29b turn-75 option controller below 100 kB."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from cgauto.compact_rust_source import Token, _needs_space, _tokens


ROOT = Path(__file__).resolve().parents[1]
STABLE = ROOT / "cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs"
FEATURES = ROOT / "rust/src/d29b_live_features.rs"
FARM = ROOT / "rust/src/d29b_exact_farm.rs"
KERNEL = (
    ROOT
    / "data/analysis/live-agent-6553250/d29b-option-critic-rust-kernel-only-2026-07-20.rs"
)
DEFAULT_OUTPUT = (
    ROOT
    / "cgauto/submissions/candidate-agent6553250-d29b-spatial-option-critic.min.rs"
)
STABLE_SHA256 = "a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55"


FEATURE_RENAMES = {
    "SCALAR_COUNT": "S",
    "PLANES": "P",
    "HEIGHT": "Y",
    "WIDTH": "X",
    "AREA": "A",
    "GRID_COUNT": "G",
    "STATE_COUNT": "N",
    "MAP_COUNT": "M",
    "VELOCITY": "V",
    "ITEM_ORDER": "O",
    "UnitAggregate": "U",
    "History": "H",
    "manhattan": "mh",
    "state": "st",
    "canonical": "cn",
    "spatial": "p",
    "observe": "o",
    "scalars": "s",
    "own_distance": "od",
    "other_distance": "ed",
    "maximum": "mx",
    "initialized": "z",
    "snapshot": "sn",
    "states": "ss",
    "output": "q",
    "result": "r",
    "nearest": "nr",
    "closer": "cl",
    "near_fruits": "nf",
    "ripe_closer": "rc",
    "inventory": "iv",
    "rotate": "rt",
    "channel": "ch",
    "target": "tg",
    "offset": "of",
}

FARM_RENAMES = {
    "ExactFarm": "F",
    "History": "H",
    "CycleValue": "V",
    "history": "h",
    "initialized": "z",
    "previous_plants": "pp",
    "own_plant_attempts": "pa",
    "opponent_crops": "oc",
    "own_wood": "w",
    "denied_wood": "d",
    "turns": "t",
    "rate_cmp": "r",
    "reconcile_provenance": "rp",
    "remember_plant_attempts": "ra",
    "ceil_div": "cd",
    "move_to": "mv",
    "home_distance": "hd",
    "cycle_value": "cv",
    "base_tree_target": "bt",
    "override_chopper": "ocp",
    "base_commands": "bc",
    "commands": "c",
    "current": "cu",
    "appeared": "ap",
    "attempts": "at",
    "opponent_shack": "os",
    "inventory": "iv",
    "turns_remaining": "tr",
    "liquidation": "lq",
    "base_trees": "bs",
    "seed_cells": "sc",
    "fell_ok": "fo",
    "own_half": "oh",
    "within_roam": "wr",
    "reserved": "rs",
    "actions": "aa",
    "distance": "ds",
    "nearest_fell": "nf",
    "is_chopper": "ic",
    "free_base": "fb",
    "wanted": "wt",
    "base_plant": "bp",
    "candidate": "ca",
    "denial": "dn",
    "travel": "tv",
    "chop_turns": "ct",
    "our_completion": "cp",
    "completion": "cm",
    "opponent_crops": "oc",
}

KERNEL_RENAMES = {
    "AREA": "A",
    "PLANES": "P",
    "GRID": "G",
    "SCALARS": "S",
    "THRESHOLD": "T",
    "PAYLOAD_LEN": "N",
    "PAYLOAD_B64": "B",
    "META": "M",
    "SCALAR_MEAN_OFFSET": "MO",
    "SCALAR_STD_OFFSET": "SO",
    "PLANE_SCALE_OFFSET": "PO",
    "TARGET_OFFSET": "TO",
    "Layer": "L",
    "Critic": "C",
    "layers": "ls",
    "scalar_mean": "sm",
    "scalar_std": "ss",
    "plane_scale": "ps",
    "target_mean": "tm",
    "target_std": "ts",
    "scalar_input": "si",
    "combined": "co",
    "hidden": "hi",
    "b64_value": "v",
    "decode_payload": "d",
    "read_f32": "r",
    "read_f32s": "rs",
    "convolution": "c",
    "forward": "f",
    "pick": "p",
    "payload": "p0",
    "source": "s0",
    "normalized": "nz",
    "maximum": "mx",
}


def compact_renamed(source: str, renames: dict[str, str]) -> str:
    pieces: list[str] = []
    previous: Token | None = None
    for separated, token in _tokens(source):
        if token.kind == "word" and token.text in renames:
            token = Token(renames[token.text], token.kind)
        if separated and previous is not None and _needs_space(previous, token):
            pieces.append(" ")
        pieces.append(token.text)
        previous = token
    return "".join(pieces)


def assemble() -> tuple[str, dict[str, int]]:
    stable = STABLE.read_text()
    digest = hashlib.sha256(stable.encode()).hexdigest()
    if digest != STABLE_SHA256:
        raise RuntimeError(f"stable source changed: {digest}")
    needle = "let mut bot=SecureOrchardBot::new();"
    if stable.count(needle) != 1:
        raise RuntimeError("stable bot constructor anchor is not unique")
    stable = stable.replace(needle, "let mut bot=D::n();")

    features = FEATURES.read_text()
    features = features[: features.index("pub fn spatial_hash")]
    features = compact_renamed(features, FEATURE_RENAMES)

    farm = compact_renamed(FARM.read_text(), FARM_RENAMES)

    kernel = KERNEL.read_text()
    kernel = "\n".join(
        line for line in kernel.splitlines() if not line.startswith("const PAYLOAD_SHA256:")
    )
    kernel += "\npub fn pick(row:&[u8])->bool{let mut critic=Critic::new();critic.forward(row).1>THRESHOLD}\n"
    kernel = compact_renamed(kernel, KERNEL_RENAMES)

    wrapper = compact_renamed(
        """
        struct D{r:SecureOrchardBot,h:d29f::H,f:d29o::F,s:bool}
        impl D{fn n()->Self{Self{r:SecureOrchardBot::new(),h:d29f::H::new(),f:d29o::F::new(),s:false}}}
        impl Bot for D{fn commands(&mut self,v:&crate::game::GameState)->Vec<String>{
            self.h.o(v);
            if v.turn==75&&v.units.iter().filter(|u|u.player==0).count()==2{
                let s=self.h.s().unwrap();let g=d29f::p(v);let mut b=Vec::with_capacity(19128);
                for x in g{b.extend_from_slice(&x.to_le_bytes())}
                for x in s{b.extend_from_slice(&x.to_le_bytes())}
                self.s=d29k::p(&b)
            }
            if self.s{self.f.c(v)}else{self.r.commands(v)}
        }}
        """,
        {},
    )
    additions = f"mod d29f{{{features}}}mod d29k{{{kernel}}}mod d29o{{{farm}}}{wrapper}"
    result = stable + additions
    sizes = {
        "stable": len(stable),
        "features": len(features),
        "kernel": len(kernel),
        "farm": len(farm),
        "wrapper_and_modules": len(additions) - len(features) - len(kernel) - len(farm),
        "total": len(result),
    }
    return result, sizes


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    source, sizes = assemble()
    if len(source.encode()) >= 100_000:
        raise RuntimeError(f"D29b source is {len(source.encode())} bytes")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(source)
    digest = hashlib.sha256(source.encode()).hexdigest()
    args.output.with_suffix(args.output.suffix + ".sha256").write_text(
        f"{digest}  {args.output.name}\n"
    )
    print(" ".join(f"{key}={value}" for key, value in sizes.items()))
    print(f"sha256={digest} output={args.output}")


if __name__ == "__main__":
    main()
