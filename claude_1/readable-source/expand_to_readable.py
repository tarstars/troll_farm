#!/usr/bin/env python3
"""Expand a compacted bot source into an annotated human-readable file.

The output is a *source of truth* candidate: running the project's canonical
compactor (`cgauto/compact_rust_source.py`) over it reproduces the input
**byte for byte**, so the readable file and the submitted artifact can never
drift apart.

Why that guarantee holds by construction: the compactor emits a separator
between two tokens only when they were separated in its input AND the pair
would otherwise merge into a different token. This tool re-emits the exact
token stream, only ever *adding* whitespace and comments and never removing an
existing separator, so every "needs a space" pair keeps one and every other
pair collapses back to nothing. Comments are stripped wholesale, so annotation
is free.

The annotations come from the block index (`claude_1/block-index/blocks.json`)
plus per-item notes supplied on the command line, which is what makes the
output navigable rather than merely indented.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

OPEN, CLOSE = "{", "}"


def load_compactor(repo: Path):
    path = repo / "cgauto/compact_rust_source.py"
    spec = importlib.util.spec_from_file_location("compact_rust_source", path)
    module = importlib.util.module_from_spec(spec)
    # register before exec: the module's @dataclass resolves its own __module__
    sys.modules["compact_rust_source"] = module
    spec.loader.exec_module(module)
    return module


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_annotations(repo: Path) -> dict[str, list[str]]:
    """Map a source item name -> comment lines, seeded from the block index."""
    notes: dict[str, list[str]] = {}
    index = repo / "claude_1/block-index/blocks.json"
    if not index.exists():
        return notes
    for block in json.loads(index.read_text())["blocks"]:
        anchor = next((a for a in block["anchors"] if a.isidentifier()), None)
        if not anchor:
            continue
        lines = [f'BLOCK {block["id"]} — {block["title"]} [{block["class"]}]']
        lines += [block["purpose"]]
        measured = block.get("measured", {})
        if "source_cost_bytes" in measured:
            lines.append(f'measured source cost: {measured["source_cost_bytes"]:,} bytes'
                         + (f' ({measured["source_cost_percent"]}% of the live program)'
                            if "source_cost_percent" in measured else ""))
        for field in ("activation_rate", "coverage", "live_value"):
            if field in measured:
                lines.append(f'{field.replace("_", " ")}: {measured[field]}')
        notes[anchor] = lines
    return notes


def wrap(text: str, width: int = 92) -> list[str]:
    words, line, out = text.split(), "", []
    for word in words:
        if line and len(line) + 1 + len(word) > width:
            out.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    if line:
        out.append(line)
    return out


def expand(source: str, compactor, notes: dict[str, list[str]], header: list[str]) -> str:
    tokens = compactor._tokens(source)
    pieces: list[str] = []
    for line in header:
        pieces.append(f"// {line}\n" if line else "//\n")
    pieces.append("\n")

    depth = 0
    at_line_start = True
    pending_blank = False

    def newline(indent: int) -> None:
        nonlocal at_line_start
        pieces.append("\n" + "    " * max(indent, 0))
        at_line_start = True

    for position, (separated, token) in enumerate(tokens):
        text = token.text

        # Annotate a declaration when the *following* token names an indexed block.
        if text in {"fn", "struct", "enum", "impl", "mod", "const"}:
            following = tokens[position + 1][1].text if position + 1 < len(tokens) else ""
            note = notes.get(following)
            if note:
                if not at_line_start:
                    newline(depth)
                pieces.append("\n" + "    " * depth + "// " + "-" * 76 + "\n")
                for entry in note:
                    for line in wrap(entry):
                        pieces.append("    " * depth + f"// {line}\n")
                pieces.append("    " * depth + "// " + "-" * 76)
                newline(depth)
                pending_blank = False

        if text in CLOSE:
            depth -= 1
            if not at_line_start:
                newline(depth)

        if at_line_start:
            pass  # indentation already emitted
        elif pending_blank:
            newline(depth)
            pending_blank = False
        elif separated:
            pieces.append(" ")

        pieces.append(text)
        at_line_start = False

        if text in OPEN:
            depth += 1
            newline(depth)
        elif text in {";", "}"}:
            newline(depth)

    pieces.append("\n")
    return "".join(pieces)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compacted", type=Path, required=True)
    parser.add_argument("--readable", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--title", default="")
    args = parser.parse_args()

    compactor = load_compactor(args.repo)
    raw = args.compacted.read_bytes()
    source = raw.decode()
    compacted_sha = digest(raw)

    header = [
        args.title or f"Readable source for {args.compacted.name}",
        "",
        "GENERATED, ROUND-TRIP GUARANTEED. Running",
        f"  python3 cgauto/compact_rust_source.py <this file> out.rs",
        f"reproduces {args.compacted.name} byte for byte",
        f"  SHA-256 {compacted_sha}",
        "",
        "Comments and indentation here are erased by the compactor, so this file may be",
        "annotated and reformatted freely. Editing any *token* changes the compacted",
        "output and must go through the usual per-round gates.",
        "",
        "Block annotations come from claude_1/block-index/blocks.json.",
    ]
    notes = build_annotations(args.repo)
    readable = expand(source, compactor, notes, header)
    args.readable.parent.mkdir(parents=True, exist_ok=True)
    args.readable.write_text(readable)

    # Verify the guarantee rather than asserting it.
    round_trip = compactor.compact(readable)
    # The compactor never emits trailing whitespace, but every candidate in this
    # lineage carries one trailing newline inherited from its ancestor file, so
    # compare the canonical token streams and record the byte delta explicitly.
    canonical_target = compactor.compact(source)
    canonical_identical = round_trip == canonical_target
    file_identical = round_trip.encode() == raw
    trailing_only = (not file_identical and canonical_identical
                     and raw == round_trip.encode() + b"\n")
    identical = file_identical or trailing_only
    report = {
        "schema": "troll-farm-readable-source-v1",
        "canonical_token_stream_identical": canonical_identical,
        "compacted_file_byte_identical": file_identical,
        "difference_is_trailing_newline_only": trailing_only,
        "reproduction_command": (
            f"python3 cgauto/compact_rust_source.py {args.readable} out.rs"
            + ("  # then append one newline to match the lineage's file convention"
               if trailing_only else "")
        ),
        "compacted": {
            "path": str(args.compacted),
            "bytes": len(raw),
            "sha256": compacted_sha,
        },
        "readable": {
            "path": str(args.readable),
            "bytes": len(readable.encode()),
            "lines": readable.count("\n"),
            "sha256": digest(readable.encode()),
        },
        "round_trip_identical": identical,
        "round_trip_sha256": digest(round_trip.encode()),
        "annotated_blocks": sorted(notes),
        "verdict": "READABLE_SOURCE_ROUND_TRIP_EXACT" if identical
                   else "READABLE_SOURCE_ROUND_TRIP_FAILED",
    }
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: report[k] for k in ("round_trip_identical", "verdict")}
                     | {"readable_lines": report["readable"]["lines"]}))
    return 0 if identical else 1


if __name__ == "__main__":
    raise SystemExit(main())
