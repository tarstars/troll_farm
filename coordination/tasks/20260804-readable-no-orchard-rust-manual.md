# 20260804-readable-no-orchard-rust-manual: beginner manual and PDF

- Status: in progress — source inventory and beginner skeleton complete
- Priority: direct owner assignment
- Record owner / work owner: `local_codex_1`
- Created UTC: 2026-08-04T11:35:00Z
- Last updated UTC: 2026-08-04T12:00:37Z

## Progress

The first canonical draft is 1,939 words: game orientation, the Rust constructs used by this
source, and the complete turn pipeline. A hash-locked builder verifies the exact source, extracts
106 constants/types/functions/traits with line numbers into `source-index.json`, and renders print
HTML. Detailed algorithm chapters, examples, appendices, and PDF validation remain.

The second checkpoint expands the draft to 8,941 words. Every active policy layer and six worked
turns are line-referenced, and the Rust clinic ties ownership, options, iterators, strings, traits,
and deterministic collections to concrete source behavior. Build/debug, limitations, exhaustive
index, and PDF inspection remain.

## Objective

Create a self-contained, beginner-first manual for the exact readable source currently deployed
on CodinGame. The reader should be able to learn the Rust constructs used by the program and then
understand, in minute detail, how input becomes game state, candidates, a coordinated two-troll
plan, commands, and persistent state updates.

## Exact subject

- Source: `local_codex_1/readable-orchard-code-cost/e7a-without-orchard-readable.rs`
- Size: 75,634 bytes; 1,475 physical lines; 1,470 code lines
- SHA-256: `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29`
- Live identity at claim: agent `6593838`, submission `41089629`

The manual describes this exact orchard-stripped program. Historical orchard behavior may be
explained only as an explicitly absent comparison; it must never be attributed to this source.

## Deliverables

- `docs/manuals/readable-no-orchard-rust-manual-2026-08-04.md` — editable canonical manual;
- `docs/manuals/readable-no-orchard-rust-manual-2026-08-04.pdf` — rendered reader copy;
- narrow build/inspection helpers and generated intermediate files, if needed, under
  `local_codex_1/readable-no-orchard-manual/`.

Required content: zero-assumption game/model orientation; Rust lessons tied to actual snippets;
source map and call graph; input protocol; all structs/enums and persistent fields; preprocessing;
candidate generation and scoring; second-troll training; pair compatibility and reservation;
movement collision resolution; endgame logic; command output; full-turn walkthroughs; failure
modes, limitations, testing instructions, glossary, and a line-referenced function index.

## Validation

- Rehash the exact subject before and after authoring; never modify it.
- Check every named function/type/constants against the source and generate a machine-derived
  symbol index.
- Render the PDF locally, extract its text, inspect representative rendered pages, and ensure no
  overflow, missing glyphs, broken code blocks, or blank pages.
- Record PDF page count, byte size, SHA-256, renderer, and validation commands.

## Write set and exclusions

Exclusive write set: the three deliverable roots above, this task record, and
`local_codex_1`'s own status/messages. No Arena mutation, replay collection, experiment, source
edit, formatting sweep, sealed-data read, raw-game write, or collector/cron change is authorized.
