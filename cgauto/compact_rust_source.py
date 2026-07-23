#!/usr/bin/env python3
"""Conservatively remove comments and optional whitespace from Rust source.

This is a lexical compactor, not a Rust parser.  It preserves literals exactly and
keeps a separator whenever deleting one could merge word tokens or form a different
punctuation token.  Every generated submission is still compiled and behavior-gated.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Token:
    text: str
    kind: str


_MERGING_PUNCTUATION = {
    "//",
    "/*",
    "*/",
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
    "<<",
    ">>",
}


def _quoted_end(source: str, start: int, quote: str) -> int:
    cursor = start + 1
    while cursor < len(source):
        if source[cursor] == "\\":
            cursor += 2
        elif source[cursor] == quote:
            return cursor + 1
        else:
            cursor += 1
    raise ValueError(f"unterminated {quote} literal")


def _char_end(source: str, start: int) -> int | None:
    """Return a char literal's end, or None when the apostrophe starts a lifetime."""

    cursor = start + 1
    if cursor >= len(source) or source[cursor] in "\r\n'":
        return None
    if source[cursor] == "\\":
        cursor += 1
        if cursor >= len(source):
            return None
        if source[cursor] == "u" and cursor + 1 < len(source) and source[cursor + 1] == "{":
            close = source.find("}", cursor + 2)
            if close < 0:
                return None
            cursor = close + 1
        elif source[cursor] == "x":
            cursor += 3
        else:
            cursor += 1
    else:
        cursor += 1
    return cursor + 1 if cursor < len(source) and source[cursor] == "'" else None


def _raw_string_end(source: str, start: int) -> int | None:
    cursor = start
    if source.startswith("br", cursor) or source.startswith("cr", cursor):
        cursor += 2
    elif source.startswith("r", cursor):
        cursor += 1
    else:
        return None
    hashes = 0
    while cursor < len(source) and source[cursor] == "#":
        hashes += 1
        cursor += 1
    if cursor >= len(source) or source[cursor] != '"':
        return None
    marker = '"' + "#" * hashes
    end = source.find(marker, cursor + 1)
    if end < 0:
        raise ValueError("unterminated raw string literal")
    return end + len(marker)


def _block_comment_end(source: str, start: int) -> int:
    depth = 1
    cursor = start + 2
    while cursor < len(source) and depth:
        if source.startswith("/*", cursor):
            depth += 1
            cursor += 2
        elif source.startswith("*/", cursor):
            depth -= 1
            cursor += 2
        else:
            cursor += 1
    if depth:
        raise ValueError("unterminated block comment")
    return cursor


def _tokens(source: str) -> list[tuple[bool, Token]]:
    """Return ``(had_separator, token)`` pairs."""

    output: list[tuple[bool, Token]] = []
    cursor = 0
    separator = False
    while cursor < len(source):
        char = source[cursor]
        if char.isspace():
            separator = True
            cursor += 1
            continue
        if source.startswith("//", cursor):
            newline = source.find("\n", cursor + 2)
            cursor = len(source) if newline < 0 else newline + 1
            separator = True
            continue
        if source.startswith("/*", cursor):
            cursor = _block_comment_end(source, cursor)
            separator = True
            continue

        raw_end = _raw_string_end(source, cursor)
        if raw_end is not None:
            token = Token(source[cursor:raw_end], "literal")
            cursor = raw_end
        elif char == '"':
            end = _quoted_end(source, cursor, '"')
            token = Token(source[cursor:end], "literal")
            cursor = end
        elif char == "'" and (end := _char_end(source, cursor)) is not None:
            token = Token(source[cursor:end], "literal")
            cursor = end
        elif char.isalnum() or char == "_":
            end = cursor + 1
            while end < len(source) and (source[end].isalnum() or source[end] == "_"):
                end += 1
            token = Token(source[cursor:end], "word")
            cursor = end
        else:
            token = Token(char, "punct")
            cursor += 1
        output.append((separator, token))
        separator = False
    return output


def _needs_space(previous: Token, current: Token) -> bool:
    if previous.kind in {"word", "literal"} and current.kind in {"word", "literal"}:
        return True
    if previous.text + current.text in _MERGING_PUNCTUATION:
        return True
    if previous.text == "r" and current.text == "#":
        return True
    if previous.kind in {"word", "literal"} and current.text == "'":
        return True
    if previous.text == "'" and current.kind in {"word", "literal"}:
        return True
    if previous.text == "." and current.text[:1].isdigit():
        return True
    if previous.text[-1:].isdigit() and current.text == ".":
        return True
    return False


def compact(source: str) -> str:
    pieces: list[str] = []
    previous: Token | None = None
    for separated, token in _tokens(source):
        if separated and previous is not None and _needs_space(previous, token):
            pieces.append(" ")
        pieces.append(token.text)
        previous = token
    return "".join(pieces)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source = args.source.read_text()
    result = compact(source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result)
    print(f"compacted {len(source)} -> {len(result)} bytes")


if __name__ == "__main__":
    main()
