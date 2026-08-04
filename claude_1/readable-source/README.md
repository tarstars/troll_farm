# Human-readable source for the simplified E7a bot

`e7a-r36-readable.rs` is a **new file**, not an edit of anything existing. It is the
human-readable form of the current simplified bot, and compacting it reproduces the
compacted artifact exactly.

## The guarantee

```bash
python3 cgauto/compact_rust_source.py \
  claude_1/readable-source/e7a-r36-readable.rs out.rs
printf '\n' >> out.rs      # lineage file convention, see note below
sha256sum out.rs
# 2caac7c6e71e8dcc613a2275fe8129cdf9aec2c1230e50f7dfdec79908528381
```

That is byte-for-byte
`claude_1/e7a-incremental-simplification/candidate-r36-delete-orphaned-carry-total.rs`,
verified — not asserted — in `round-trip-report.json`.

## Why it is guaranteed rather than lucky

The project compactor is lexical: it deletes comments and deletes whitespace *except* where
two adjacent tokens would otherwise merge into a different token. The generator
(`expand_to_readable.py`) re-emits the compacted file's exact token stream and only ever
*adds* whitespace and comments — it never removes an existing separator. So every pair that
needs a space keeps one, every other pair collapses back to nothing, and all comments
disappear. The round trip cannot drift.

A first attempt used `rustfmt` instead and failed by 130 bytes: rustfmt inserts trailing
commas, which are real tokens and survive compaction. That is why this generator exists.

## What you may edit freely

Comments, blank lines and indentation — they are erased by the compactor and cannot change
the artifact. Use them liberally; that is the point of the file.

## What you may not edit casually

Any **token**. Changing one changes the compacted output, so it is a new candidate and must
pass the same per-round gates as any other: byte-identical rebuild, optimized compile,
empty input, the ten frozen semantic fixtures, and the 25-game / 7,234-line offline live
command parity. Regenerate this file from the new compacted candidate rather than
hand-editing both and hoping they agree.

## Annotations

Block comments are injected from `claude_1/block-index/blocks.json`, so a reader meeting
`force_unique_door_clear` sees inline what the block is, what it costs (5,991 bytes, 9.5 %
of the live program), and that its action paths have never been observed executing. Extend
the index, regenerate, and the annotations follow.

## Verification recorded

| Check | Result |
|---|---|
| Canonical token stream identical | yes |
| End-to-end SHA-256 vs the r36 candidate | identical (`2caac7c6…`) |
| Readable file compiles directly (`rustc --edition=2021 -O`) | yes |
| Empty input on the readable build | exit 0, no output |
| Ten frozen semantic fixtures on the compacted output | `SEMANTIC_FIXTURES_EXACT_PASS` |
| Offline live command parity on the compacted output | `LIVE_COMMAND_PARITY_PASS`, 25 games / 7,234 lines / 0 different |

## One provenance note worth keeping

The compactor's CLI writes **no** trailing newline, but every candidate in this lineage
carries one, inherited from the original ancestor file. So the compacted output differs from
the committed candidate by exactly that one byte, which the recipe above appends. The token
streams are identical. Worth deciding project-wide which form is canonical; until then this
file documents the delta rather than hiding it.

## Sizes

| File | Bytes | Lines |
|---|---:|---:|
| Compacted candidate (r36) | 55,799 | 1 |
| This readable source | 92,484 | 1,778 |
