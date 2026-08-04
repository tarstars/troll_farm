# 20260804-orchard-code-cost-ablation: physically remove apple-orchard implementation

- Status: complete; handoff independently verified and integrated on `agent/local_codex_1`
- Priority: direct owner assignment
- Record owner / integrator: `local_codex_1`
- Work owner: `claude_1`
- Created UTC: 2026-08-04T06:35:15Z
- Updated UTC: 2026-08-04T09:07:13Z
- Required branch: `agent/claude_1-orchard-code-cost`
- Arena authority: none; static source-cost audit only

## Owner objective

Physically strip the apple-orchard feature from the exact current E7a bot and measure how much
source code that feature costs. Its live strength contribution has already been measured; do not
repeat the Arena experiment.

## Why the existing no-orchard file is not the answer

`claude_1/no-orchard-arena/candidate-e7a-r28-no-orchard.rs` disables the activation branch but
leaves orchard code dormant, and its parent also contains unrelated round-28 simplifications.
Therefore its 56,200 versus 62,820 byte comparison cannot attribute the 6,620-byte difference to
orchard code. It is useful behavioral reference material, not the requested size measurement.

## Frozen same-parent baseline

- source: `cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs`;
- bytes/characters: 62,820 / 62,820;
- SHA-256: `97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595`;
- immutable: read and copy only; never edit this file.

## Required method

1. From the exact frozen baseline, create an **activation-disabled reference** whose only semantic
   change is that the secure apple orchard never activates.
2. From that same reference, remove the now-unreachable orchard implementation: orchard-only
   state, types, helpers, scoring/routing branches, activation/maintenance/replanting logic, and
   call sites. Retain generic apple parsing, harvesting, carrying, chopping, banking, and denial
   behavior that is used outside self-reproducing orchard management.
3. Prove that the stripped program and activation-disabled reference produce identical commands
   on every allowed fixture/replay/simulation case used by the audit. This is the central safety
   gate: physical deletion must not introduce behavior beyond disabling orchard activation.
4. Compile the stripped source with the normal optimized Rust gate and test empty-input handling.
   Use only open development evidence; do not open any sealed map/game range.
5. Measure the exact source cost against the 62,820-character baseline:
   - bytes and Unicode characters removed;
   - percentage of the CodinGame 100,000-character allowance;
   - optional logical/token/gzip metrics clearly labelled secondary, because the baseline is a
     one-line minified submission;
   - an itemized inventory of removed symbols/blocks and their individual or grouped sizes where
     mechanically defensible.
6. Distinguish shared infrastructure from orchard-exclusive code. If a helper cannot be removed
   because other policy uses it, count it as shared and explain it rather than estimating.

## Deliverables and write set

Write only under `claude_1/orchard-code-cost/`, plus messages/status owned by `claude_1`:

- `activation-disabled-reference.rs`;
- `e7a-without-orchard-code.rs`;
- `orchard-code-cost-report.md` understandable without project-internal labels;
- `manifest.json` with all source hashes, byte/character counts, exact commands, test counts, and
  pass/fail results;
- a reproducible builder or patch and narrowly scoped tests needed to regenerate both artifacts.

Do not modify `cgauto/submissions/`, `docs/STATE.md`, `docs/CONSTRAINTS.md`, shared ledgers, raw
replays, or another agent's directory. The integrator will reconcile shared documentation after
handoff.

## Acceptance gates

- frozen baseline hash remains exact;
- sacred `rust/src/bin/yamo_orchard_live.rs` remains byte-exact at SHA prefix `fff6669b`;
- no formatter is run across `rust/src/bin/` or `cgauto/`;
- activation-disabled reference and stripped artifact compile and handle empty input;
- stripped/reference command streams are exact across the declared open test panel, with zero
  unexplained mismatches;
- no orchard-only implementation remains except unavoidable generic apple/shared infrastructure,
  which the report inventories explicitly;
- no Arena/TestSession mutation occurs;
- handoff commit is pushed and includes validation evidence; `local_claude_1` renews the 15-minute
  lease with concrete pushed progress.

## Coordination

The owner cancelled the unacknowledged `local_claude_1` assignment at 2026-08-04T06:40:02Z and
reassigned the work to the established `claude_1` agent. Before implementation, acknowledge from
the `claude_1` namespace and claim the explicit write set. This direct owner assignment may begin
at Claude's current idle authorization boundary; do not resume overlapping older work in parallel.

## Result and integrator verification

Claude handoff `7bc3e07a` reports exact orchard cost of **15,013 bytes/characters**, 23.898% of
the 62,820-character baseline and 15.013% of the platform allowance. The stripped source is
47,807 bytes at SHA `102caecd...`; the activation-disabled reference is 62,581 bytes at SHA
`8fc1b7f3...`.

The integrator cherry-picked the acknowledgement and handoff as `bb369a71` and `3561ca3d`, then
independently regenerated the sources, rechecked all hashes, compiled both optimized artifacts,
confirmed empty-input cleanliness, reran 10/10 semantic fixtures for each, and reran both equality
panels. Reference versus baseline is 24/25 exact with only known orchard game `897833045`
diverging; stripped versus reference is 25/25 games and 7,234/7,234 command lines exact. Sacred
source remains SHA `fff6669b...`; no Arena action occurred.
