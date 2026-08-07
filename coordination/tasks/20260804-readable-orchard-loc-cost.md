# 20260804-readable-orchard-loc-cost: measure orchard cost in canonical readable lines

- Status: complete; 375-line readable orchard cost verified
- Owner / worker / integrator: `local_codex_1`
- Created UTC: 2026-08-04T10:16:15Z
- Updated UTC: 2026-08-04T10:25:03Z
- Branch: `agent/local_codex_1`
- Arena authority: none; source reconstruction and static measurement only

## Objective

Produce readable same-parent copies of the exact live E7a source with and without the apple
orchard, then report the physically deleted readable lines. The existing 6,024-line sacred
`rust/src/bin/yamo_orchard_live.rs` is not assumed to be the parent and remains untouched.

## Exact parents

- with orchard: 62,820 bytes, SHA-256
  `97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595`;
- physically stripped: 47,807 bytes, SHA-256
  `102caecde916b03dde0c02d1d8c13c9333b6ee3a26f13df34ad21fbebaae0fd6`;
- activation-disabled reference: 62,581 bytes, SHA-256
  `8fc1b7f3499a407e5df546bbc688843c56c0f6e7d9382b18ba359592b586693d`.

## Method and acceptance

1. Use one deterministic lexical expander for all three minified sources. It may add only
   whitespace/comments, never tokens.
2. Compact each readable output with `cgauto/compact_rust_source.py`, normalize the documented
   trailing newline, and require byte-exact recovery of its minified parent hash.
3. Compile each readable output optimized, check empty input, and rerun the existing semantic and
   25-game/7,234-command equality gates.
4. Count physical lines, nonblank lines, and code-only lines under this one canonical expansion.
   Report the with-orchard minus stripped delta and distinguish activation-switch lines from the
   physically removable implementation.
5. Explain that readable LOC is formatting-scheme-dependent; the byte/character result remains
   canonical, while this result is reproducible under the recorded expander.

## Write set and hazards

Exclusive writes are `local_codex_1/readable-orchard-code-cost/`, this task, own messages/status,
and compact final documentation if needed. Do not edit or format `rust/src/bin/`, `cgauto/`,
Claude's artifacts, raw games, shared state/ledgers, or sealed evidence. No Arena/TestSession
mutation. Sacred source must remain SHA prefix `fff6669b`.

## Deliverables

- deterministic expander and round-trip verifier;
- readable with-orchard, activation-disabled, and stripped sources;
- manifest with hashes, line counts, exact commands, and gates;
- plain-language report answering the readable LOC question.

## Result

The canonical exact-parent expansion is 1,850 physical / 1,845 code lines with orchard and 1,475
physical / 1,470 code lines after physical stripping: **375 lines removed**. Six lines are the
activation edit and 369 are the subsequently removable implementation. Grouped inventory is
12 lines of types/state, 242 helper/strategy lines, 108 per-turn driver lines, and 13 reservation/
import/main-wiring lines.

All three readable sources compact to their known exact hashes, compile optimized, handle empty
input, and carry 10/10 semantic-fixture evidence. Readable baseline is 25/25 and 7,234/7,234 exact;
activation-disabled differs only in game `897833045` at turn 79; stripped is 25/25 and 7,234/7,234
exact to activation-disabled. Sacred source remains `fff6669b...`; no Arena action occurred.
