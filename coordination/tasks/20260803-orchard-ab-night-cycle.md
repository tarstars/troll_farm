# 20260803-orchard-ab-night-cycle: four repeated orchard/no-orchard live cycles

- Status: running; clean leg 1/8 no-orchard maturity window
- Priority: direct owner assignment
- Owner / Arena controller: local_codex_1
- Created UTC: 2026-08-03T19:07:37Z
- Last updated UTC: 2026-08-03T19:17:00Z
- Branch: `agent/local_codex_1`
- Runtime state: `data/analysis/live-agent-6553250/orchard-ab-night-20260803/state.json`
- Systemd unit: `troll-farm-orchard-ab-night-20260803.service`

## Owner directive and design

Deploy the version with orchard and the version without orchard four times each, wait one hour
for each version, collect its games, and write all results into Git. The serialized sequence is
`N→O` repeated four times: eight fresh submissions, four exact copies of each source, ending with
orchard active. The first live mutation begins only after this task, source rules, tooling, start
message, and controller lock are pushed and remotely verified.

## Exact sources

- no-orchard: `claude_1/no-orchard-arena/candidate-e7a-r28-no-orchard.rs`, 56,200 bytes,
  SHA-256 `d1f32c358d0f7b6a49b988c1b4ad6958a2d8ed84a9e3492632087732aae7e02a`;
- orchard: `cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs`,
  62,820 bytes, SHA-256
  `97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595`.

The no-orchard hash is historically rejected at 23.27/rank 34/137 over 160 games; exact E7a has
two complete rows, 25.26 and 23.56, median 24.41. The owner explicitly requests repeated live
measurement despite that prior disposition.

## Pre-trial state

Pre-cycle resident is exact orchard agent `6592131`, submission `41086057`, source-exact and
runtime-clean. Latest complete checkpoint is 23.56/rank 32/137 over 162 games; immediate start
read is 23.4/rank 33/137. Sacred `rust/src/bin/yamo_orchard_live.rs` remains exact at SHA prefix
`fff6669b`.

## First-launch preflight abort

The first controller launch submitted no-orchard once as `41086801`, but its read-only source
verifier looked for the untracked session file inside the isolated worktree. It therefore stopped
before opening a maturity window and made the declared one-call orchard safety restore,
`6592329`/`41086809`. This approximately 66-second exposure is not an experiment leg. The durable
abort record is `preflight-abort-20260803T191126Z.json`. The correction passes the controller's
explicit credential path to read-only recovery and extends only the propagation-read gate to five
minutes. The clean eight-leg sequence restarts from no-orchard after the correction is tested,
pushed, and the orchard restore is source-verified.

Restore source verification passed at 19:14:40Z: exactly 62,820 bytes and SHA-256 `97bfe71e...`.
All six focused controller/export tests pass after the correction.

The corrected controller restarted at 19:16:14Z. Clean leg 1 is exact no-orchard agent `6592330`,
submission `41086822`; the recovered platform source is byte-exact. Start commit `1ff538c7` is
remote-verified and the one-hour maturity clock is active.

## Per-leg protocol

1. Rehash the named source, generate one fresh IDE session, and call only canonical
   `TestSession/submit` once. There is no endpoint/payload fallback and no automatic retry.
2. Discover the unique new agent ID from exact submission identity and recover the platform source
   against the expected SHA.
3. Commit/push the accepted IDs, then wait 3,600 seconds from the submission call. Push immutable
   T+15, T+30, and T+45 minute phase markers to renew the protocol lease.
4. Require the exact queue to settle with no pending or unexpected rows. Capture one full
   submission-scoped checkpoint, require clean identity and zero runtime signals, then collect
   all visible replay bodies before the next mutation.
5. Export a sanitized deterministic LFS package: full frames/actions/scores retained; pseudonyms
   replaced by positional placeholders; user IDs, avatars, public handles, and TestSession handles
   removed. Commit and push the checkpoint, package, hashes, and result before the next leg.
6. After leg 8, publish the table, variant aggregates, and four orchard-minus-no-orchard pair
   deltas. State explicitly that opponent queues are not paired game-for-game.

## Reliability and stop rules

- A transport-ambiguous or malformed submission response stops immediately without another
  mutation call.
- A non-ambiguous failure while no-orchard is the last known active source triggers exactly one
  safe orchard restore call; an ambiguous mutation never triggers an automatic restore/retry.
- Any identity mix, runtime signal, missing replay, package/checkpoint count mismatch, Git staging
  contamination, push failure, or source mismatch stops the cycle.
- Each Git push is single-attempt. LFS objects are uploaded once; no ambiguous upload retry.
- A local-time network blackout from 05:14 through 05:31 avoids competing with the 05:17 daily
  wide collector. The cron itself is never changed, stopped, or locked.
- One nonblocking process lock prevents a second night controller. No other Arena mutation is
  authorized while the task is running.

## Write set

- `data/analysis/live-agent-6553250/orchard-ab-night-20260803/`;
- `data/shared-lfs/orchard-ab-night-20260803/` under its narrow LFS rule;
- this task, local status, own immutable messages, STATE/ledger start and final reconciliation;
- ignored canonical raw replay cache through the established collector only.

Unrelated simplification artifacts, sealed maps, bot sources, the sacred file, external-storage
roots, and the cron are out of scope.

## Preflight

Exact source hashes pass; canonical one-call submitter and sequence/privacy tests pass 5/5;
submission-history preflight exposes the no-orchard rejection; Git staging is isolated; no Arena
cycle is otherwise in flight. Expected wall time is about eight hours plus checkpoint/collection
overhead and any mandatory cron blackout.
