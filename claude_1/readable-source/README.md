# Human-readable source for the simplified bot

`e7a-r36-readable.rs` is a **new file** (2,552 lines) written to be *read*: idiomatic rustfmt
layout, module overviews, and inline explanations of the major blocks. It is the same program
as the compacted artifact, and that is verified rather than claimed.

## Why you can trust that it is the real program

```bash
python3 cgauto/compact_rust_source.py \
  claude_1/readable-source/e7a-r36-readable.rs out.rs
printf '\n' >> out.rs
sha256sum out.rs
# 2caac7c6e71e8dcc613a2275fe8129cdf9aec2c1230e50f7dfdec79908528381
```

That is byte-for-byte the round-36 candidate. Checked on every generation and recorded in
`round-trip-report.json`.

## What "no garbage" means here concretely

Thirty-six behaviour-exact deletion rounds removed **6,479 bytes (10.4 %)** of code that could
not affect play: configuration records with exactly one possible value, switches permanently
fixed on or off, a risk calculation whose penalty was zero, unused derives, constant local
bindings, a struct field computed every turn and never read, and two helpers that duplicated
an existing method. Nothing that influences a decision was touched — every round had to
reproduce all 7,234 command lines of 25 real ladder games exactly.

What is left is load-bearing policy code. Where a block is *rarely* used rather than dead, the
annotations say so with numbers instead of deleting it.

## How it is generated

`format_readable.py`:

1. runs rustfmt (`reorder_imports = false`, `max_width = 100`) for idiomatic layout;
2. rustfmt makes token-level edits that are meaningless in Rust but would survive compaction —
   it adds and removes trailing commas and wraps multi-line closure bodies in braces. The
   generator diffs the token streams and undoes exactly those, then **asserts** the token
   stream matches the target. Anything beyond inert punctuation aborts the build rather than
   being guessed at;
3. injects the file header, module overviews and block annotations as comments;
4. compacts the result and compares.

An earlier version indented at braces only, which left expressions dense
(`let x=foo(a,b).iter().count();`). This one gives real Rust formatting.

## Reading order suggestion

| Module | What it is |
|---|---|
| `game::types` | The vocabulary: cells, plant kinds, unit stats, the per-turn `GameState`. Start here. |
| `game::rules` | Referee arithmetic: growth cooldowns, tree health, training costs, scoring. |
| `game::nav` | Grid navigation: neighbours, Manhattan distance, breadth-first distance maps. |
| `game::protocol` | Parses the platform's turn protocol from stdin. |
| `bot::moisan` | The policy: candidate generation, scoring, conflict resolution, orchard wrapper. |

Good Rust to study on the way through: `Option` combinators (`and_then`, `filter`,
`unwrap_or`, `is_some_and`), iterator chains with `filter_map` and `min_by_key`, `BTreeMap` /
`BTreeSet` for deterministic ordering, `matches!`, let-else early returns, and closures
capturing borrowed state.

## Editing rules

- **Comments, blank lines, indentation** — free. The compactor erases them; they cannot change
  the program. Annotate as much as you like.
- **Any token** — that is a new candidate. Regenerate this file from the new compacted
  artifact rather than hand-editing both, and put it through the usual gates: compile, empty
  input, ten semantic fixtures, and 25-game / 7,234-line live command parity.

## Verification recorded

| Check | Result |
|---|---|
| Token stream identical to the compacted artifact | yes (asserted during generation) |
| End-to-end SHA-256 after compaction | `2caac7c6…`, identical |
| Compiles directly (`rustc --edition=2021 -O`) | yes |
| Ten frozen semantic fixtures | `SEMANTIC_FIXTURES_EXACT_PASS` |
| Offline live command parity | `LIVE_COMMAND_PARITY_PASS`, 25 games / 7,234 lines / 0 different |

## Provenance note

The compactor's CLI writes no trailing newline, while every candidate in this lineage carries
one inherited from the original ancestor file — hence the `printf '\n'` above. Token streams
are identical; the delta is that single byte, documented rather than hidden.
