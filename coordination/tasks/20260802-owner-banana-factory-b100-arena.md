# 20260802-owner-banana-factory-b100-arena

- Status: submitted once; exact identity; clean but weak 98-game reconvergence checkpoint; read-only
- Record owner: local_codex_1
- Work owner: local_codex_1
- Integrator / sole Arena controller: local_codex_1
- Created UTC: 2026-08-02T15:57:22Z
- Branch: `agent/local_codex_1`
- Area: owner-directed banana-factory + opponent-crop b100/e6 Arena deployment

## Owner directive and evidence status

The owner twice directed publication of the new banana bot. GitHub branch
`agent/chatgpt_1-banana-factory-restoration` supplied a pre-lock generator/analysis packet,
not a qualified candidate. Before acting, the controller surfaced that distinction and that
the live 23.12/160 resident would be replaced. The owner maintained the directive and corrected
the expected reconvergence interval to about 30 minutes. This is an explicit owner-directed
live override, not a `QUALIFIED` promotion and not a reopening of D88--D92.

## Exact composition

The candidate is the existing closed-loop `banana_seed_factory()` composed with the current
flat opponent-crop policy: bonus 100, ETA limit 6, start turn 1, minimum seen 1. It excludes
the D91 selector, source separation, dual-value scoring, and worker-three bridge. Parent hashes:

- sacred research source: `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`;
- deployed b100/e6 control: `6f992a5a4d58e5f3f78478322ab0f3ce6cf8706d5aa9bb57d10f8264b03a3f19`.

## Candidate and local gate

- Arena artifact:
  `local_codex_1/banana-factory-b100-owner-override/banana-factory-b100-e6.arena.rs`;
- bytes: 99,440 (strictly below the 100,000-byte limit);
- SHA-256: `2d164ecbaf8a06092f91fffd253f295ec6d6233f2094ac707eda152b28cb2533`;
- fail-closed slimmer SHA-256:
  `5cfa0009361d0cb68acddd3d608655883767844b935d56adf953ecc5e48991e5`.

Standalone optimized compilation and empty-input exit pass. All 23 embedded semantic tests pass.
The final slim exactly matches the full generated source on eight open games, both seats, 2,400
commands, with zero stderr. Interactive latency is 0.984 ms mean, 1.556 ms p95, and 4.582 ms
maximum. A deliberately mutated compact parent is rejected by the input hash guard.

The first attempted reuse of the old general specialization compiled at 99,656 bytes but failed
the equality gate on all eight streams (first mismatch as early as turn 7). It was rejected and
is not retained as a submission artifact.

## Pre-mutation baseline and contract

Authenticated read at 2026-08-02T15:55Z: resident agent `6589709`, submission `41079653`,
score 23.3, rank 32/131. Fresh IDE recovery is byte-exact to the 64,522-byte control SHA above.
`local_codex_1` is the sole Arena controller. Submit the exact Arena artifact once, preserve the
terminal response and new identity, and never retry an ambiguous response. No other mutation is
in flight. Observe an initial checkpoint and the owner's approximately 30-minute reconvergence
checkpoint read-only; no automatic second candidate follows.

## Exclusive write set

- this task record;
- `coordination/status/local_codex_1.md` and local sender messages;
- the new slimmer and owner-override artifact directory;
- immutable preflight/execution/checkpoint records under
  `data/analysis/live-agent-6553250/`;
- integrator-owned STATE/BACKLOG/live-ledger updates after the terminal platform response.

No sacred-source edit, formatter, sealed-data read, raw-game mutation, automatic retry, or peer
Arena mutation is authorized.

## Platform result

The exact artifact was submitted once. `TestSession/submit` returned HTTP 200 with submission
`41081195` and `SUBMIT-OK`; no retry occurred. The platform assigned agent `6590083` and the
battle endpoint immediately contained only exact agent/submission rows.

## Initial checkpoint

At 2026-08-02T16:00:50Z the immutable checkpoint has 10/10 matching, finished, fetched, and
parsed rows, zero pending/unexpected/fetch/runtime signals, and clean identity. The room read is
score 0.0 at rank 130/131; the filtered ladder read is 13.7 at rank 124. Battle health is 4W/6L,
mean margin -32.3, five catastrophes (50%), and negative-margin mass 749.

This is a weak initialization, not a transfer verdict. The mutation is terminal and the cycle is
now read-only. Do not submit a second candidate or restore automatically.

## Approximately 30-minute checkpoint

The read-only checkpoint observed at 2026-08-02T16:29:58Z contains 99 matching rows: 98
finished/fetched/parsed and one pending, with zero unexpected rows, fetch failures,
validity/runtime signals, or identity faults. The Arena row is score 12.99, rank 127/131.
Battle health is 49W/49L, mean margin +4.642857, 22 catastrophes (22.45%), and negative-margin
mass 4,851.

This improves average margin from the ten-game initialization but remains weak and just below
the registry's 100-finished mature-evidence threshold. It is provisional platform state, not a
scientific promotion or a reason for another automatic Arena mutation. Evidence SHA-256:
`83983d63e671bec97832d1937b14e674cf65f5852c66e053f9488ed516bb452e`.
