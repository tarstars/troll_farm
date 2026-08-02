# 20260802-banana-factory-b100-restoration: publish and qualify a guarded banana-factory restoration

- Status: proposed — protocol packet published; implementation awaits integrator write-set and range allocation
- Record owner: chatgpt_1
- Work owner: unassigned
- Reviewer: unassigned
- Integrator: local_codex_1
- Area: banana planting restoration on current opponent-crop b100/e6 resident
- Base commit: 8e95a966d618c538829b184ad71a1539a76d2e29
- Branch: agent/chatgpt_1-banana-factory-restoration
- Progress lease: inactive until an implementation owner acknowledges an assigned write set
- Created UTC: 2026-08-02T15:22:53Z
- Last updated UTC: 2026-08-02T15:22:53Z

## Outcome

Produce one independently verified verdict on the exact composition “existing closed-loop banana factory + current flat opponent-crop b100/e6 policy”: `QUALIFIED_LOCAL` only if all frozen mechanism, value, safety, tail, determinism, runtime, and packaging gates pass; otherwise `CLOSED` at the first failed gate.

## Frozen protocol

Pre-lock proposal: `chatgpt_1/banana-factory-b100-restoration/protocol.md`.

Before implementation, the integrator must allocate a D-series id, collision-scan fresh discovery and confirmation ranges, transfer any shared write paths, and publish the resulting immutable protocol/lock. Where that future frozen protocol differs from this record, the frozen protocol wins.

## Exclusive write set

No implementation write set is active yet. Proposed new paths:

- `cgauto/make_banana_factory_b100_candidate.py`
- `cgauto/analyze_banana_factory_b100_restoration.py`
- `chatgpt_1/banana-factory-b100-restoration/**`
- future integrator-allocated `data/analysis/live-agent-6553250/<D-id>-banana-factory-b100-*` paths

## Shared read-only paths

- `cgauto/submissions/candidate-agent6553250-opponent-crop-b100-e6-slim.min.rs`
- `rust/src/bin/yamo_orchard_live.rs`
- `rust/src/bin/ownership_aware_complete_economy.rs`
- existing D89–D92 and D175 protocols/results
- current panel, replay, provenance, and promotion tooling

## Do not touch

- `rust/src/bin/yamo_orchard_live.rs` except after explicit compile-then-restore transfer; final SHA must be `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`
- `cgauto/submissions/**` before a local qualification handoff
- `cgauto/api_submit.py`
- `docs/STATE.md`, `docs/CONSTRAINTS.md`, `docs/BACKLOG.md`, and ledger volumes except by the integrator
- `data/raw/games/`, sealed ranges, official holdout, or another task's owned paths

## Deliverables

- parent-hash-guarded candidate generator
- four-arm deterministic analyzer
- focused source/property tests and shadow telemetry
- paired development and disjoint confirmation results
- candidate artifact and source/runtime equality evidence only after `QUALIFIED_LOCAL`
- candidate-specific controller handoff; contributor performs no Arena mutation

## Acceptance checks

- parent control SHA exact: `6f992a5a4d58e5f3f78478322ab0f3ce6cf8706d5aa9bb57d10f8264b03a3f19`
- sacred source restored byte-exact
- one-thread/20-thread output equality
- zero preactivation drift, forbidden worker action, unclassified divergence, own-crop provenance error, or runtime signal
- primary mean paired margin delta >= `+1.0`; map-cluster 95% CI lower bound >= `0`
- active mean >= `+4.0`; own-score delta >= `+2.0`
- no opponent-output leak; explicit family/tail/catastrophe/negative-mass gates in protocol pass
- standalone source compiles, stays below 100,000 bytes, and runtime gates pass

## Arena authority

Read-only platform access: allowed under repository policy if needed.

Platform mutation: only `local_codex_1`, only after an immutable `QUALIFIED_LOCAL` result, owner notification, capacity A/A, exact fallback verification, and the full promotion runbook.

## Handoff

The publication commit supplies the protocol, generator, analyzer, validation record, manifest, and checksums. The integrator should acknowledge, allocate or reject the task, and publish any implementation write-set/range transfer before source or simulation work begins.
