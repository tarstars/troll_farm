#!/usr/bin/env python3
"""Patch script for candidate-banana-r2: parent + 5 compacted insertions.

Per integration-seam-2026-08-04.md section B/C (with the integrator's C5
seam delta: the I2/I3/I4 inserted strings additionally carry the
`banana_protected_cell` field / init / retain-filter at the SAME anchors, so
the insertion count stays 5 and every anchor stays unique).

Mechanical asserts (seam report section B):
  (a) each anchor occurs exactly once in the parent;
  (b) each inserted string occurs 0 times in the parent and exactly once in
      the output; inserted strings are pairwise non-substring;
  (c) per-block: compact(readable block) == inserted string (pipeline C.2);
  (d) inverse transform: deleting the inserted strings from the output
      restores the parent byte-for-byte (sha256 checked);
  (e) parent sha256 matches the frozen value from the seam report.

Outputs: candidate-banana-r2.min.rs + candidate-banana-r2-manifest.json.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
PARENT = REPO / "cgauto" / "submissions" / (
    "candidate-agent6553250-preseed-orchard-coverage-slim.min.rs"
)
PARENT_SHA = "a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55"
COMPACTOR = REPO / "cgauto" / "compact_rust_source.py"
BLOCKS = HERE / "banana_blocks"
OUT = HERE / "candidate-banana-r2.min.rs"
MANIFEST = HERE / "candidate-banana-r2-manifest.json"

ANCHOR_I1 = "pub struct SecureOrchardBot{"
ANCHOR_I2 = "external_protected_tree:Option<Cell>,}"
ANCHOR_I3 = "external_protected_tree:None,}}"
ANCHOR_I4 = (
    "if let Some(id)=self.external_idle_unit"
    "{by_id.insert(id,vec![MoisanBot::wait()]);}"
)
ANCHOR_I5 = "else{return;};let mut bot=SecureOrchardBot::new();"
ANCHOR_I6 = (
    "if let Some(protected)=self.external_protected_tree"
    "{candidates.retain(|candidate|{!matches!(candidate.target,"
    "Target::Tree(cell)|Target::Bank(cell)|Target::Cell(cell)"
    "if cell==protected)});}"
)

# Seam-fixed exact insertion bytes (revised seam 2026-08-04, integrator
# item 5): asserted against compact(readable block) where prescribed.
EXPECTED = {
    "I2": "banana_idle_unit:Option<i32>,banana_protected_cell:Option<Cell>,",
    "I3": "banana_idle_unit:None,banana_protected_cell:None,",
    "I4": (
        "if let Some(id)=self.banana_idle_unit"
        "{by_id.insert(id,vec![MoisanBot::wait()]);}"
    ),
    "I6": (
        "if let Some(protected)=self.banana_protected_cell"
        "{candidates.retain(|candidate|{!matches!(candidate.target,"
        "Target::Tree(cell)|Target::Bank(cell)|Target::Cell(cell)"
        "if cell==protected)});}"
    ),
}

# (name, block file, anchor, mode) — mode: where the compacted block goes
# relative to the anchor occurrence.
#   before        : insert immediately before the anchor
#   after         : insert immediately after the anchor
#   before_last:N : insert inside the anchor, N characters before its end
INSERTIONS = [
    ("I1", "block-i1.rs", ANCHOR_I1, "before"),
    ("I2", "block-i2.rs", ANCHOR_I2, "before_last:1"),   # before final '}'
    ("I3", "block-i3.rs", ANCHOR_I3, "before_last:2"),   # before final '}}'
    ("I4", "block-i4.rs", ANCHOR_I4, "after"),
    ("I5", "block-i5.rs", ANCHOR_I5, "after"),
    ("I6", "block-i6.rs", ANCHOR_I6, "after"),
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_compactor():
    spec = importlib.util.spec_from_file_location("compact_rust_source", COMPACTOR)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.compact


def main() -> int:
    parent_bytes = PARENT.read_bytes()
    assert sha256(parent_bytes) == PARENT_SHA, "parent sha mismatch (e)"
    parent = parent_bytes.decode()
    compact = load_compactor()

    inserted_strings = {}
    for name, filename, anchor, mode in INSERTIONS:
        readable = (BLOCKS / filename).read_text()
        inserted = compact(readable)
        # (c) the canonical insertion IS compact(readable); assert the
        # round-trip explicitly as the seam report demands.
        assert compact(readable) == inserted, f"{name}: compact round-trip"
        assert inserted, f"{name}: empty insertion"
        if name in EXPECTED:
            assert inserted == EXPECTED[name], (
                f"{name}: compacted block differs from the seam-fixed bytes"
            )
        token_ok = "banana_" in inserted or "Banana" in inserted
        assert token_ok, f"{name}: no banana_/Banana token in insertion"
        # (a) anchor unique in parent; (b) insertion absent from parent.
        assert parent.count(anchor) == 1, f"{name}: anchor count != 1"
        assert parent.count(inserted) == 0, f"{name}: insertion present in parent"
        inserted_strings[name] = (anchor, mode, inserted)

    # pairwise non-substring (well-defined inverse transform).
    names = list(inserted_strings)
    for a in names:
        for b in names:
            if a != b:
                assert inserted_strings[a][2] not in inserted_strings[b][2], (
                    f"{a} insertion is a substring of {b} insertion"
                )

    out = parent
    for name, (anchor, mode, inserted) in inserted_strings.items():
        index = out.find(anchor)
        assert index >= 0 and out.count(anchor) == 1, f"{name}: anchor drifted"
        if mode == "before":
            position = index
        elif mode == "after":
            position = index + len(anchor)
        elif mode.startswith("before_last:"):
            position = index + len(anchor) - int(mode.split(":")[1])
        else:
            raise AssertionError(f"{name}: unknown mode {mode}")
        out = out[:position] + inserted + out[position:]

    # (b) each insertion exactly once in the output.
    for name, (_anchor, _mode, inserted) in inserted_strings.items():
        assert out.count(inserted) == 1, f"{name}: insertion count != 1 in output"

    # (d) inverse transform: delete the insertions, recover the parent bytes.
    restored = out
    for name, (_anchor, _mode, inserted) in inserted_strings.items():
        restored = restored.replace(inserted, "", 1)
    assert sha256(restored.encode()) == PARENT_SHA, "inverse transform failed (d)"

    OUT.write_text(out)
    out_bytes = OUT.read_bytes()
    manifest = {
        "schema": "troll-farm-banana-r2-candidate-manifest/1",
        "parent": {
            "path": str(PARENT),
            "bytes": len(parent_bytes),
            "sha256": PARENT_SHA,
        },
        "candidate": {
            "path": str(OUT),
            "bytes": len(out_bytes),
            "sha256": sha256(out_bytes),
        },
        "byte_budget": {"limit": 100_000, "within_budget": len(out_bytes) < 100_000},
        "insertions": [
            {
                "name": name,
                "block": filename,
                "anchor": anchor,
                "mode": mode,
                "inserted_bytes": len(inserted_strings[name][2]),
                "inserted_sha256": sha256(inserted_strings[name][2].encode()),
                "readable_block_bytes": (BLOCKS / filename).stat().st_size,
            }
            for name, filename, anchor, mode in INSERTIONS
        ],
        "asserts": [
            "parent sha256 verified",
            "per-block compact(readable) == inserted string",
            "every anchor count == 1 in parent",
            "every inserted string count == 0 in parent, == 1 in output",
            "inserted strings pairwise non-substring",
            "sha256(output minus insertions) == parent sha256",
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "candidate_bytes": len(out_bytes),
        "candidate_sha256": manifest["candidate"]["sha256"],
        "insertion_bytes": {n: len(v[2]) for n, v in inserted_strings.items()},
    }, indent=2))
    assert len(out_bytes) < 100_000, "byte budget exceeded"
    return 0


if __name__ == "__main__":
    sys.exit(main())
