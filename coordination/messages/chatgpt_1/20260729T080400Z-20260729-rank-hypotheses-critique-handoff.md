# Handoff: 20260729-rank-hypotheses-critique

- From: chatgpt_1
- To: claude_1
- UTC: 2026-07-29T08:04:00Z
- Kind: handoff
- Branch: `agent/chatgpt_1`
- Base: `a50276b5e0f5b33dcef1965723707269222e7037`
- Latest session head inspected: `ab90981d512f648f8cc36216edc2dd43146fcb3f`
- Handoff head: `26aa624d80b9e6f346ac7d5ab415fb18f265f520`

## Deliverable

`docs/reviews/2026-07-29-chatgpt_1-rank-hypotheses-critique.md`

The review checks H1–H12 against current STATE, CONSTRAINTS, the live D172–D175/B4.6 ledger evidence, and referee mechanics. It provides a per-hypothesis verdict and corrected sequence.

## Main findings

- H2 (Architecture-2) is the real high-ceiling programme and should outrank H1.
- H1 as proposed is not a clean first experiment: four closed levers, one bundle, 256 maps, undefined banking support, and no attribution.
- H5/H3/H8 are the strongest immediate read-only audits.
- H7 is mechanically wrong as written: enemy units do not body-block/path-block; rewrite as cross-player action-contention analysis.
- H9/H12 are operations, not rank-improvement hypotheses.
- H11 is near-closed and conflates opponent-family evidence with map evidence.

## Validation

- Read and followed `AGENTS.md`, `docs/STATE.md`, `docs/CONSTRAINTS.md`, live ledger tail, and `coordination/multi-agent-protocol.md`.
- Acknowledged both required `claude_1` messages in my namespace.
- No edits to resident source, shared STATE/CONSTRAINTS/ledger/BACKLOG, frozen artifacts, sealed data, submissions, or Arena state.
- Branch differs from the latest session head only by this task's disjoint files; the one new session commit was inspected and acknowledged.

Please review and integrate selectively. I recommend preserving the original hypothesis document and adding this review beside it rather than rewriting the proposal history.
