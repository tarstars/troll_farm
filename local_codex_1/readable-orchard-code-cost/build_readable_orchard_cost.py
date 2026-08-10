#!/usr/bin/env python3
"""Expand exact orchard variants readably while preserving their token streams."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SOURCES = {
    "with_orchard": {
        "path": Path("cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs"),
        "sha256": "97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595",
        "output": "e7a-with-orchard-readable.rs",
    },
    "activation_disabled": {
        "path": Path("claude_1/orchard-code-cost/activation-disabled-reference.rs"),
        "sha256": "8fc1b7f3499a407e5df546bbc688843c56c0f6e7d9382b18ba359592b586693d",
        "output": "e7a-activation-disabled-readable.rs",
    },
    "orchard_stripped": {
        "path": Path("claude_1/orchard-code-cost/e7a-without-orchard-code.rs"),
        "sha256": "102caecde916b03dde0c02d1d8c13c9333b6ee3a26f13df34ad21fbebaae0fd6",
        "output": "e7a-without-orchard-readable.rs",
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_compactor():
    path = REPO / "cgauto/compact_rust_source.py"
    spec = importlib.util.spec_from_file_location("readable_orchard_compactor", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load canonical Rust compactor")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class Unit:
    """One token of the compact stream, with multi-character punctuation merged."""

    text: str
    kind: str
    separated: bool


# Longest first: greedy merging keeps ``..=`` from becoming ``..`` plus a spaced ``=``.
_MERGED_PUNCTUATION = (
    "..=",
    "::",
    "..",
    "=>",
    "->",
    "==",
    "!=",
    "<=",
    ">=",
    "&&",
    "||",
    "+=",
    "-=",
    "*=",
    "/=",
    "%=",
    "^=",
    "&=",
    "|=",
)
# Spaced on both sides.  Single-character arithmetic and ``&``/``*``/``<``/``>`` stay tight
# because a lexer cannot tell binary from unary or comparison from generics.
_SPACED_PUNCTUATION = frozenset(
    {"=", "=>", "->", "==", "!=", "<=", ">=", "&&", "||", "+=", "-=", "*=", "/=", "%=", "^=", "&=", "|="}
)
_TIGHT_BEFORE = frozenset({",", ";", ")", "]", ".", "?", ":", "::", "(", "["})
# Tokens that must stay on the closing brace's line instead of being orphaned.
_GLUED_AFTER_BRACE = frozenset({";", ",", ")", "]", ".", "?", "else"})
_KEYWORDS = frozenset(
    {
        "as",
        "break",
        "const",
        "continue",
        "else",
        "enum",
        "fn",
        "for",
        "if",
        "impl",
        "in",
        "let",
        "loop",
        "match",
        "mod",
        "move",
        "mut",
        "pub",
        "ref",
        "return",
        "static",
        "struct",
        "trait",
        "type",
        "unsafe",
        "use",
        "where",
        "while",
    }
)
_MAX_LINE = 100
_BREAK_NONE = 0
_BREAK_CHAIN = 1
_BREAK_OPERATOR = 2
_BREAK_LIST = 3


def _units(tokens: list[tuple[bool, Any]]) -> list[Unit]:
    units: list[Unit] = []
    index = 0
    while index < len(tokens):
        separated, token = tokens[index]
        if token.kind == "punct":
            for candidate in _MERGED_PUNCTUATION:
                span = tokens[index : index + len(candidate)]
                if len(span) < len(candidate):
                    continue
                if any(piece.kind != "punct" for _, piece in span):
                    continue
                if any(flag for flag, _ in span[1:]):
                    continue
                if "".join(piece.text for _, piece in span) == candidate:
                    units.append(Unit(candidate, "punct", separated))
                    index += len(candidate)
                    break
            else:
                units.append(Unit(token.text, token.kind, separated))
                index += 1
            continue
        units.append(Unit(token.text, token.kind, separated))
        index += 1
    return units


def _spaced(previous: Unit | None, current: Unit) -> bool:
    """Decide the gap.  Never narrower than the compact stream's own separator."""

    if previous is None:
        return False
    if previous.text == "'" or current.text == "'":
        return current.separated  # lifetimes: ``&'static`` must not gain a gap
    if previous.text == "&":
        return current.separated  # ``&mut``, ``&self``: the borrow binds tightly
    if current.text in {")", "]", ";", ",", ".", "?"}:
        return current.separated  # closers and separators never float away from what they follow
    if previous.text in {"(", "["}:
        return current.separated  # nothing floats off an opening bracket
    if previous.text == "|":
        return current.text == "{"  # closure parameters bind tight; a braced body does not
    if current.text == "||" and previous.text in {"(", "["}:
        return current.separated  # ``f(|| ...)``: an argument-less closure, not a logical or
    if previous.text in _SPACED_PUNCTUATION or previous.text in {",", ";", ":"}:
        return True
    if previous.text == "}" or previous.text in _KEYWORDS:
        return True
    if current.text == "{":
        return previous.text != "::"  # ``use path::{`` stays tight
    if current.text in _TIGHT_BEFORE:
        return current.separated
    if current.text in _SPACED_PUNCTUATION or current.text in _KEYWORDS:
        return True
    return current.separated


def _wrap(
    indent: int, pieces: list[str], depths: list[int], kinds: list[int]
) -> tuple[list[str], int]:
    """Split an over-long line; return its physical lines and the last one's extra indent."""

    prefix = "    " * max(indent, 0)
    flat = prefix + "".join(pieces)
    if len(flat) <= _MAX_LINE:
        return [flat], 0
    base = min(depths)

    def commas(level: int) -> list[int]:
        found = []
        for index in range(len(pieces) - 1):
            if kinds[index] != _BREAK_LIST or depths[index] != level:
                continue
            start = index + 1
            if start < len(pieces) and pieces[start] == " ":
                start += 1
            if start < len(pieces):
                found.append(start)
        return found

    def marked(kind: int) -> list[int]:
        return [index for index in range(1, len(pieces)) if kinds[index] == kind and depths[index] == base]

    # A list splits at its own indent; a chain, a boolean run or a call's arguments hang in.
    hang = 0
    expression = False
    points = commas(base)
    if not points:
        hang = 1
        points = marked(_BREAK_CHAIN) or marked(_BREAK_OPERATOR)
        expression = bool(points)
        points = points or commas(base + 1)
    if not points:
        return [flat], 0
    continuation = prefix + "    " * hang
    bounds = [0, *points, len(pieces)]
    lines = []
    for order in range(len(bounds) - 1):
        chunk = "".join(pieces[bounds[order] : bounds[order + 1]]).rstrip()
        if chunk:
            lines.append((prefix if order == 0 else continuation) + chunk)
    # Only a wrapped expression carries its hanging indent into a block it opens; a split
    # argument or field list still owns its brace at the statement's own indent.
    return lines, (hang if expression and len(lines) > 1 else 0)


def expand(source: str, compactor: Any, label: str, digest: str) -> str:
    lines = [
        f"// Canonical readable expansion: {label}.",
        f"// Compact parent SHA-256: {digest}.",
        "// Generated by build_readable_orchard_cost.py; whitespace and this header are the only additions.",
        "// Compacting this file and restoring the lineage newline reproduces the parent exactly.",
        "",
    ]
    units = _units(compactor._tokens(source))
    pieces: list[str] = []
    depths: list[int] = []
    kinds: list[int] = []
    # Each open brace remembers the indent of the line it opened on, so a closing brace
    # lands under its opener even when the opening line was wrapped.
    openers: list[int] = []
    # Bracket nesting is per block: a ``;`` inside ``[i32; 6]`` is a separator, but a ``;``
    # inside a closure body nested in call parentheses still ends a statement.
    brackets: list[int] = []
    bracket = 0
    angle = 0
    line_indent = 0
    in_attribute = False

    def flush() -> int:
        """Emit the buffered line; return the extra indent its last physical line took."""

        if not pieces:
            return 0
        segments, extra = _wrap(line_indent, pieces, depths, kinds)
        lines.extend(segments)
        pieces.clear()
        depths.clear()
        kinds.clear()
        return extra

    def body_indent() -> int:
        return openers[-1] + 1 if openers else 0

    previous: Unit | None = None
    previous_comparison = False
    for index, unit in enumerate(units):
        text = unit.text
        following = units[index + 1] if index + 1 < len(units) else None
        if text == "}":
            opener = openers.pop() if openers else 0
            bracket = brackets.pop() if brackets else 0
            if previous is None or previous.text != "{":
                flush()
                line_indent = opener
        if text == "#" and not pieces:
            in_attribute = True
        # ``<`` opens generics after a type name or ``::``; anywhere else it compares.
        comparison = False
        if text == "<" and previous is not None and (previous.text == "::" or previous.text[:1].isupper()):
            angle += 1
        elif text == ">" and angle > 0:
            angle -= 1
        elif text in {"<", ">"}:
            comparison = True
        if pieces and (comparison or previous_comparison or _spaced(previous, unit)):
            pieces.append(" ")
            depths.append(bracket)
            kinds.append(_BREAK_NONE)
        chain = (
            text == "."
            and previous is not None
            and (previous.text in {")", "]"} or (previous.kind == "word" and not previous.text[-1:].isdigit()))
            and following is not None
            and following.kind == "word"
            and index + 2 < len(units)
            and units[index + 2].text in {"(", "::"}  # ``.collect::<T>()`` is a call too
        )
        operator = text in {"&&", "||"} and previous is not None and previous.text not in {"(", "[", ",", "{"}
        # Commas inside generics separate type arguments, not list items: never break there.
        listable = text == "," and angle == 0
        pieces.append(text)
        depths.append(bracket)
        kinds.append(
            _BREAK_CHAIN
            if chain
            else _BREAK_OPERATOR
            if operator
            else _BREAK_LIST
            if listable
            else _BREAK_NONE
        )
        if text in {"(", "["}:
            bracket += 1
        elif text in {")", "]"}:
            bracket = max(bracket - 1, 0)
        if text == "{":
            brackets.append(bracket)
            bracket = 0
            if following is not None and following.text == "}":
                openers.append(line_indent)  # empty block stays inline as ``{}``
            else:
                extra = flush()
                openers.append(line_indent + extra)
                line_indent = line_indent + extra + 1
        elif text == ";" and bracket == 0:
            flush()
            line_indent = body_indent()
        elif text == "}" and (following is None or following.text not in _GLUED_AFTER_BRACE):
            flush()
            line_indent = body_indent()
        elif text == "]" and bracket == 0 and in_attribute:
            in_attribute = False
            flush()
            line_indent = body_indent()
        previous = unit
        previous_comparison = comparison
    flush()
    return "\n".join(lines).rstrip() + "\n"


def line_metrics(text: str) -> dict[str, int]:
    lines = text.splitlines()
    blank = sum(not line.strip() for line in lines)
    comment = sum(line.lstrip().startswith("//") for line in lines)
    return {
        "physical_lines": len(lines),
        "blank_lines": blank,
        "comment_only_lines": comment,
        "code_lines": len(lines) - blank - comment,
        "nonblank_lines": len(lines) - blank,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    compactor = load_compactor()
    output_dir = args.output_dir.resolve()
    manifest_path = args.manifest.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    records: dict[str, Any] = {}

    for label, specification in SOURCES.items():
        source_path = REPO / specification["path"]
        raw = source_path.read_bytes()
        if sha256(raw) != specification["sha256"]:
            raise RuntimeError(f"{label}: compact parent hash mismatch")
        source = raw.decode("utf-8")
        readable = expand(source, compactor, label, specification["sha256"])
        output = output_dir / specification["output"]
        if output.exists() and not args.force:
            raise RuntimeError(f"refusing to overwrite {output}")
        output.write_text(readable, encoding="utf-8")

        compacted = compactor.compact(readable).encode("utf-8")
        normalized = compacted + (b"\n" if raw.endswith(b"\n") else b"")
        if normalized != raw:
            raise RuntimeError(f"{label}: readable round trip changed compact parent")
        records[label] = {
            "compact_path": str(specification["path"]),
            "compact_bytes": len(raw),
            "compact_sha256": sha256(raw),
            "readable_path": str(output.relative_to(REPO)),
            "readable_bytes": len(readable.encode("utf-8")),
            "readable_sha256": sha256(readable.encode("utf-8")),
            "round_trip_exact": True,
            **line_metrics(readable),
        }

    baseline = records["with_orchard"]
    disabled = records["activation_disabled"]
    stripped = records["orchard_stripped"]
    result = {
        "schema": "troll-farm-readable-orchard-code-cost-v1",
        "generator": str(Path(__file__).resolve().relative_to(REPO)),
        "sources": records,
        "line_cost": {
            "physical_lines_removed_vs_baseline": baseline["physical_lines"] - stripped["physical_lines"],
            "code_lines_removed_vs_baseline": baseline["code_lines"] - stripped["code_lines"],
            "activation_edit_physical_lines": baseline["physical_lines"] - disabled["physical_lines"],
            "physical_implementation_lines_removed_after_disable": disabled["physical_lines"] - stripped["physical_lines"],
            "formatting_definition": (
                "one statement per line; four-space blocks with each closing brace under its opener; "
                "spaced operators, separators and comparisons, with arithmetic, borrows and generics left "
                f"tight; lines over {_MAX_LINE} columns split at top-level commas, method-chain dots or "
                "boolean operators; common four-line generated header"
            ),
        },
        "canonical_character_cost": 15013,
        "sacred_source_modified": False,
    }
    if manifest_path.exists() and not args.force:
        raise RuntimeError(f"refusing to overwrite {manifest_path}")
    manifest_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["line_cost"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
