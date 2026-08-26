# `readable/` — the bot's source in a form a person can read, and the changes as diffs

Owner ruling 2026-08-26: *"I want to see diffs in files."* This directory is where.

## What is here

| file | what it is |
|---|---|
| `door1-champion.rs` | the **champion** (`cgauto/submissions/candidate-door1-pure-deletion.rs`, sha256 `547fa706…`) in the canonical readable format |
| `candidate-1-hold.rs` | Candidate 1 (the *hold* rule + telemetry v4), source `claude_1/cure1/cure1-hold-v4.rs` (`cc4b3087…`) |
| `candidate-2-swap.rs` | Candidate 2 (the *swap* rule + telemetry v5; hold switched off), source `claude_1/cure2/cure2-swap-v5.rs` (`5c678e6a…`) |
| `reports/*.round-trip.json` | the proof that each readable file is the same program as its compact parent (`verdict: READABLE_SOURCE_ROUND_TRIP_EXACT`, `canonical_token_stream_identical: true`) |
| `diffs/candidate-1-hold.diff` | champion → Candidate 1 |
| `diffs/candidate-2-swap.diff` | champion → Candidate 2 |
| `diffs/candidate-2-swap-vs-candidate-1-hold.diff` | Candidate 1 → Candidate 2: **the swap rule itself**, the v5 telemetry letters, the hold switched off |

Every future candidate adds `<candidate>.rs`, its report, and `diffs/<candidate>.diff` (base →
candidate). GitHub renders `.diff` files with colouring: open
`https://github.com/tarstars/troll_farm/blob/main/readable/diffs/<name>.diff`.

## How the readable files are made, and why they can be trusted

`claude_1/readable-source/format_readable.py` runs the pinned `rustfmt` (1.9.0,
`reorder_imports=false`, `max_width=100`), undoes rustfmt's inert token edits, and then
**compacts the result and compares it with the compacted parent** (`cgauto/compact_rust_source.py`).
The two compactions are byte-identical for all three files here — that is the round-trip gate
(`docs/readable-format.md`). The champion's compact file was never fully minified, so a
byte-for-byte comparison against it is not the gate; the canonical-compaction identity is.

## Reading the diffs

- The instrument arms print telemetry every turn (`NARRATE v4` / `v5`): the largest hunks in
  `candidate-1-hold.diff` and `candidate-2-swap.diff` are that printer and its bookkeeping, not
  the rule. The rule is in the resolver: look for `hold_pass` and `resolve_move_conflicts_hold`
  (two-phase reservation; Candidate 1's hold; Candidate 2's exchange with the `S`/`X` letters).
- `candidate-2-swap-vs-candidate-1-hold.diff` is the smallest honest view of Candidate 2: what the
  swap adds on top of the hold machinery, with the hold disabled.
- No formatter ever runs over `cgauto/` or `rust/src/bin/`; these are derived copies.
