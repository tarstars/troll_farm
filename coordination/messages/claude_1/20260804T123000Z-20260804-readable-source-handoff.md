---
type: HANDOFF
task_id: 20260804-readable-source
from: claude_1
to: local_codex_1
cc: user, chatgpt_1
created_utc: 2026-08-04T12:30:00Z
requires_ack: true
---

# Readable source for the simplified bot, with a verified compaction round trip

Owner-directed. Branch `agent/claude_1-readable-source`, all under `claude_1/readable-source/`.

## What this is, and what it deliberately is not

A **new file**, `claude_1/readable-source/e7a-r36-readable.rs` (1,778 lines). I did **not**
touch `rust/src/bin/yamo_orchard_live.rs`; it remains byte-exact at `fff6669b…`, per §7 and
because both peers are running work right now. For the record, that sacred file is not the
ancestor of our lineage anyway — it is 275,377 bytes and compacts to 146,421, whereas the
live submission is 62,820, so the readable source for this lineage simply did not exist
before now.

## The guarantee

```bash
python3 cgauto/compact_rust_source.py claude_1/readable-source/e7a-r36-readable.rs out.rs
printf '\n' >> out.rs
```

yields SHA-256 `2caac7c6e71e8dcc613a2275fe8129cdf9aec2c1230e50f7dfdec79908528381` — byte-for-byte
the round-36 candidate. Verified, not asserted (`round-trip-report.json`).

It holds by construction: your compactor is lexical and deletes comments plus whitespace
except where tokens would merge, so the generator re-emits the exact token stream and only
*adds* whitespace and comments. I first tried `rustfmt` and it failed by 130 bytes — rustfmt
inserts trailing commas, which are real tokens that survive compaction. That is why
`expand_to_readable.py` exists rather than a formatter invocation.

## Gates run on the compacted output

- readable file compiles directly under `rustc --edition=2021 -O`; empty input exit 0;
- ten frozen semantic fixtures: `SEMANTIC_FIXTURES_EXACT_PASS`;
- offline live command parity: `LIVE_COMMAND_PARITY_PASS`, 25 games / 7,234 lines / 0
  different / period-2 max 128.

## Two things for your disposition

1. **A provenance detail worth a project decision.** Your compactor CLI writes no trailing
   newline, but every candidate in this lineage carries one inherited from the ancestor file.
   So compaction output differs from the committed candidate by exactly that byte (token
   streams identical). The recipe appends it. It would be cleaner to declare one form
   canonical; I have documented the delta rather than papering over it.
2. **Annotations come from the block index** (`claude_1/block-index/blocks.json`), so a reader
   meeting `force_unique_door_clear` sees inline that it costs 5,991 bytes, 9.5 % of the live
   program, and that its action paths have never been observed executing. If you adopt the
   block index, this file regenerates with richer annotations for free.

Suggested standing rule if you take this on: the readable file is **generated from** the
accepted compacted candidate, never hand-edited alongside it. Editing a token there is a new
candidate and takes the normal per-round gates.
