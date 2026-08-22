#!/usr/bin/env python3
"""Produce idiomatic, annotated, *readable* Rust from a compacted bot source.

Built for reading and learning, not for byte-golf, while keeping the property
that makes the file trustworthy: compacting it reproduces the compacted
artifact exactly, so what you read is provably the program that runs.

Pipeline:
  1. rustfmt the compacted source (with `reorder_imports=false`, so imports are
     not moved), giving genuine idiomatic layout — spaces around operators,
     wrapped argument lists, one statement per line;
  2. rustfmt inserts trailing commas, which are real tokens and would survive
     compaction, so diff the token streams and delete exactly those insertions.
     Any other token difference aborts the build rather than being papered over;
  3. inject a file header, module overviews and block annotations as comments,
     which the compactor erases;
  4. verify the round trip by compacting the result and comparing.

Comments and layout are free; changing a token is a new candidate and takes the
normal per-round gates.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MODULE_OVERVIEWS = {
    "types": "Core game vocabulary: cells, plant kinds, unit stats, and the per-turn GameState snapshot.",
    "rules": "Referee arithmetic reproduced exactly: growth cooldowns, tree health, training costs, scoring.",
    "nav": "Grid navigation: orthogonal neighbours, Manhattan distance, and breadth-first distance maps.",
    "protocol": "Reads the platform's turn protocol from stdin into a GameState.",
    "moisan": "The policy itself: candidate generation, scoring, conflict resolution and the orchard wrapper.",
}


def load_compactor(repo: Path):
    path = repo / "cgauto/compact_rust_source.py"
    spec = importlib.util.spec_from_file_location("compact_rust_source", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["compact_rust_source"] = module
    spec.loader.exec_module(module)
    return module


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tokens_with_offsets(source: str, compactor) -> list[tuple[int, int, str]]:
    """Same lexical rules as the compactor, but keeping source offsets."""
    out: list[tuple[int, int, str]] = []
    cursor = 0
    while cursor < len(source):
        char = source[cursor]
        if char.isspace():
            cursor += 1
            continue
        if source.startswith("//", cursor):
            newline = source.find("\n", cursor + 2)
            cursor = len(source) if newline < 0 else newline + 1
            continue
        if source.startswith("/*", cursor):
            cursor = compactor._block_comment_end(source, cursor)
            continue
        raw_end = compactor._raw_string_end(source, cursor)
        if raw_end is not None:
            end = raw_end
        elif char == '"':
            end = compactor._quoted_end(source, cursor, '"')
        elif char == "'" and (char_end := compactor._char_end(source, cursor)) is not None:
            end = char_end
        elif char.isalnum() or char == "_":
            end = cursor + 1
            while end < len(source) and (source[end].isalnum() or source[end] == "_"):
                end += 1
        else:
            end = cursor + 1
        out.append((cursor, end, source[cursor:end]))
        cursor = end
    return out


SAFE_EDITS = {",", "{", "}"}


def repair_token_stream(formatted: str, target_tokens: list[str], compactor) -> str:
    """Restore the target token stream inside rustfmt's layout.

    rustfmt makes semantically inert but token-level changes: it adds and removes
    trailing commas and wraps multi-line closure bodies in braces. Each is undone
    textually — deletions remove the token, insertions splice it in right after
    the preceding token so the surrounding layout is preserved. Only punctuation
    in SAFE_EDITS may be touched; anything else aborts rather than being guessed.
    """
    spans = tokens_with_offsets(formatted, compactor)
    texts = [t for _, _, t in spans]
    edits: list[tuple[int, int, str]] = []  # (start, end, replacement)
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
        None, target_tokens, texts, autojunk=False
    ).get_opcodes():
        if tag == "equal":
            continue
        removed, added = target_tokens[i1:i2], texts[j1:j2]
        if not set(removed) <= SAFE_EDITS or not set(added) <= SAFE_EDITS:
            raise SystemExit(
                "token stream differs beyond inert punctuation — refusing to guess.\n"
                f"  {tag}: target[{i1}:{i2}]={removed!r} formatted[{j1}:{j2}]={added!r}"
            )
        if added:  # drop what rustfmt introduced
            edits.append((spans[j1][0], spans[j2 - 1][1], "".join(removed)))
        else:  # rustfmt dropped a token: splice it back after the previous one
            anchor = spans[j1 - 1][1] if j1 else 0
            edits.append((anchor, anchor, "".join(removed)))
    result = formatted
    for start, end, replacement in sorted(edits, key=lambda e: -e[0]):
        result = result[:start] + replacement + result[end:]
    if [t.text for _, t in compactor._tokens(result)] != target_tokens:
        raise SystemExit("repair did not reproduce the target token stream")
    return result


def build_annotations(repo: Path) -> dict[str, list[str]]:
    notes: dict[str, list[str]] = {}
    index = repo / "claude_1/block-index/blocks.json"
    if not index.exists():
        return notes
    for block in json.loads(index.read_text())["blocks"]:
        anchor = next((a for a in block["anchors"] if a.isidentifier()), None)
        if not anchor:
            continue
        lines = [f'{block["title"]} — indexed block `{block["id"]}` [{block["class"]}]', "",
                 block["purpose"]]
        measured = block.get("measured", {})
        extras = []
        if "source_cost_bytes" in measured:
            extras.append(f'Costs {measured["source_cost_bytes"]:,} bytes of source'
                          + (f' ({measured["source_cost_percent"]}% of the live program).'
                             if "source_cost_percent" in measured else "."))
        for field, label in (("activation_rate", "How often it fires"),
                             ("coverage", "Coverage"),
                             ("live_value", "Measured live value")):
            if field in measured:
                extras.append(f"{label}: {measured[field]}")
        if extras:
            lines += [""] + extras
        notes[anchor] = lines
    return notes


def wrap(text: str, width: int) -> list[str]:
    words, line, out = text.split(), "", []
    for word in words:
        if line and len(line) + 1 + len(word) > width:
            out.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    out.append(line)
    return out


DECL = re.compile(r"^(?P<indent>\s*)(pub(\(crate\))? )?(fn|struct|enum|impl|mod|trait|const) "
                  r"(?P<name>\w+)")


def annotate(formatted: str, notes: dict[str, list[str]], header: list[str]) -> str:
    out: list[str] = [f"// {line}" if line else "//" for line in header] + [""]
    for raw in formatted.splitlines():
        match = DECL.match(raw)
        if match:
            indent = match.group("indent")
            name = match.group("name")
            if name in MODULE_OVERVIEWS and " mod " in f" {raw} ":
                out += ["", f"{indent}// === {name} " + "=" * (70 - len(name) - len(indent)),
                        *[f"{indent}// {line}" for line in wrap(MODULE_OVERVIEWS[name], 88)]]
            elif name in notes:
                out += ["", f"{indent}// " + "-" * 74]
                for entry in notes[name]:
                    if entry:
                        out += [f"{indent}// {line}" for line in wrap(entry, 88)]
                    else:
                        out.append(f"{indent}//")
                out.append(f"{indent}// " + "-" * 74)
        out.append(raw)
    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compacted", type=Path, required=True)
    parser.add_argument("--readable", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--title", default="")
    parser.add_argument("--max-width", type=int, default=100)
    args = parser.parse_args()

    compactor = load_compactor(args.repo)
    raw = args.compacted.read_bytes()
    source = raw.decode()
    target_tokens = [t.text for _, t in compactor._tokens(source)]

    rustfmt = shutil.which("rustfmt") or str(Path.home() / ".cargo/bin/rustfmt")
    with tempfile.TemporaryDirectory(prefix="readable-") as directory:
        work = Path(directory)
        (work / "rustfmt.toml").write_text(
            f"edition = \"2021\"\nreorder_imports = false\nmax_width = {args.max_width}\n"
        )
        scratch = work / "candidate.rs"
        scratch.write_text(source)
        subprocess.run([rustfmt, "--edition", "2021", str(scratch)],
                       check=True, capture_output=True, text=True, cwd=work)
        formatted = scratch.read_text()

    exact = repair_token_stream(formatted, target_tokens, compactor)

    header = [
        args.title or f"Readable source for {args.compacted.name}",
        "",
        "This file is for READING. It is idiomatic rustfmt layout with explanatory",
        "comments, and it is the same program as the compacted artifact:",
        "",
        f"  python3 cgauto/compact_rust_source.py <this file> out.rs",
        f"  -> {args.compacted.name}, SHA-256",
        f"     {digest(raw)}",
        "",
        "The compactor deletes comments and optional whitespace, so comments and layout",
        "here are free and cannot change the program. Changing any *token* produces a new",
        "candidate and must pass the usual gates (compile, empty input, ten semantic",
        "fixtures, 25-game / 7,234-line live command parity).",
        "",
        "Annotated blocks are described in claude_1/block-index/blocks.json.",
    ]
    readable = annotate(exact, build_annotations(args.repo), header)
    args.readable.parent.mkdir(parents=True, exist_ok=True)
    args.readable.write_text(readable)

    round_trip = compactor.compact(readable)
    canonical_identical = round_trip == compactor.compact(source)
    trailing_only = raw == round_trip.encode() + b"\n"
    report = {
        "schema": "troll-farm-readable-source-v2",
        "compacted": {"path": str(args.compacted), "bytes": len(raw), "sha256": digest(raw)},
        "readable": {
            "path": str(args.readable),
            "bytes": len(readable.encode()),
            "lines": readable.count("\n"),
            "sha256": digest(readable.encode()),
        },
        "formatter": "rustfmt (reorder_imports=false, max_width="
                     f"{args.max_width}) + inserted-comma removal",
        "canonical_token_stream_identical": canonical_identical,
        "compacted_file_byte_identical": round_trip.encode() == raw,
        "difference_is_trailing_newline_only": trailing_only and not (round_trip.encode() == raw),
        "verdict": "READABLE_SOURCE_ROUND_TRIP_EXACT"
                   if canonical_identical else "READABLE_SOURCE_ROUND_TRIP_FAILED",
    }
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"verdict": report["verdict"], "lines": report["readable"]["lines"],
                      "canonical_identical": canonical_identical}))
    return 0 if canonical_identical else 1


if __name__ == "__main__":
    raise SystemExit(main())
