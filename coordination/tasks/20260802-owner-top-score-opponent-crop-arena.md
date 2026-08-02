# 20260802-owner-top-score-opponent-crop-arena

- Status: complete — submitted once; exact identity; mature repeat observed at 23.12/160
- Record owner: local_codex_1
- Work owner: local_codex_1
- Integrator / sole Arena controller: local_codex_1
- Created UTC: 2026-08-02T07:42:29Z
- Branch: `agent/local_codex_1`
- Area: owner-directed Arena deployment from the submission-history registry

## Owner directive

Check the bot-version query program, find the best scored bot so far, and submit it to the
platform.

## Registry result and selection

The unfiltered, source-level `best --min-finished 100 --evidence mature --scope all` query
ranks `opponent-crop-b100-e6-slim` first at 24.89/160. Exact artifact:

- path: `cgauto/submissions/candidate-agent6553250-opponent-crop-b100-e6-slim.min.rs`;
- bytes: 64,522;
- SHA-256: `6f992a5a4d58e5f3f78478322ab0f3ce6cf8706d5aa9bb57d10f8264b03a3f19`;
- historical agent/submission: `6560269` / `41012399`;
- terminal observation: 24.89, rank 17/107, 160 finished games.

The mandatory preflight reports no higher historical mature median, but raises three
warnings: `REJECTED_SOURCE`, `SINGLE_MATURE_RUN`, and `CROSS_ERA`. Its frozen matched protocol
rejected it because the live score was only about +0.12 over its control. Therefore this is
not a scientific promotion. The owner was explicitly notified of those facts before the
write; the literal top-score directive is treated as an owner-directed live override.

## Pre-mutation baseline

Authenticated read at 2026-08-02T07:41Z: active far-denial agent `6589510` is 19.37 at rank
73/130 with 160 listed, 160 finished, and zero pending battles. `local_codex_1` is the sole
Arena controller. The candidate and sacred source hashes are exact; sacred source remains
`fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.

## Mutation contract

Submit the exact artifact once through `cgauto/api_submit.py`. Record the terminal API
response, submission id, new agent id when observable, exact identity, initial queue, and
first completed health. Never retry an ambiguous response. No other candidate or Arena cycle
may start concurrently.

## Exclusive write set

- this task record;
- `coordination/status/local_codex_1.md` and local_codex_1 messages for this task;
- new immutable execution/checkpoint/log artifacts under
  `data/analysis/live-agent-6553250/`;
- integrator-owned `docs/STATE.md`, `docs/BACKLOG.md`, and the live ledger after the terminal
  platform result.

## Prohibitions

No source edit, formatter, sealed-data read, simulation, model fit, history rewrite, unrelated
branch cleanup, automatic retry, or second submission.

## Platform result

`TestSession/submit` returned HTTP 200 exactly once with submission id `41079653` and
`SUBMIT-OK`; no retry occurred. The platform assigned agent `6589709`. Its first battle-list
read contains exactly ten matching rows, all pending, each identifying agent `6589709` and
submission `41079653`. The displaced leaderboard row remains visible until games complete.

## First health and disposition

The immutable submission-scoped checkpoint at 2026-08-02T07:47:43Z has 22 exact matching
rows: 21 finished and parsed, one pending, no unexpected rows, no fetch failures, and clean
agent/submission identity. Agent `6589709` is 13.58 at rank 123/130 (filtered read 13.01,
rank 126). Battle health is 11W/10L, mean margin +29.667, one catastrophic loss (4.8%),
negative-margin mass 559, and zero validity/runtime signals.

The owner directive is complete because the literal registry leader was submitted exactly
once. The result is an adverse immature first health, not a qualified promotion or evidence
that the historical 24.89 transfers to this era. Monitoring is read-only; no second Arena
cycle is in flight.

## Mature follow-up

The 2026-08-02 catch-up later captured the full 160-game visible window. A fresh immutable
submission-scoped checkpoint confirms 160/160 matching and parsed, zero pending/unexpected/
fetch/runtime faults, score 23.12 at rank 32/130, 101W/2T/57L, mean margin +23.444, ten
catastrophes (6.25%), and negative-margin mass 3,318. This is a clean mature repeat but is
1.77 below the historical run. The two-run cross-era median is 24.005; repeated preseed
evidence now ranks above it at 24.19. No Arena mutation follows automatically.
