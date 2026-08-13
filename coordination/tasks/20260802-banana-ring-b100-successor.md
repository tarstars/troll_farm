# 20260802-banana-ring-b100-successor: replace the unbounded factory with the gate-aware tent ring

- Status: **DORMANT / CUSTODY TRANSFERRED 2026-08-12.** Proposed only; never implemented, and
  record owner `chatgpt_1` is out of reach. Custody passes to the coordinator so the record is not
  orphaned. **Custody, not revival** — no work is assigned and none should start. The bounded ring
  it proposes is the same lineage as the implementation-invalid ring trial `6590136`/`41081465`;
  disposition belongs to `20260807-banana-disposition-review-*`.
- Record owner: **local_claude_1** (custody, from `chatgpt_1`)
- Work owner: unassigned — do not assign without an owner decision
- Reviewer: unassigned
- Integrator / sole Arena controller: **local_claude_1** (Arena control transferred 2026-08-06)
- Area: successor to owner-directed full banana-factory+b100/e6 deployment
- Base commit: `68ed41a5e7ac14a703aedf36a92b19abd83665cb`
- Branch: `agent/chatgpt_1-banana-ring-successor`
- Progress lease: inactive until a work owner acknowledges an explicit write set
- Created UTC: 2026-08-02T16:32:00Z
- Last updated UTC: 2026-08-02T16:32:00Z

## Owner directive / correction

The owner inspected live agent `6590083` and corrected the intended banana behavior:

- the full farm is much too large for our trolls to cut;
- harvested bananas are not being collected to the tent;
- placement must use the existing tent gate/front-door logic;
- orthogonal tent-neighbor bananas are wood trees;
- diagonal tent-neighbor bananas are protected seed mothers.

This correction supersedes the unbounded-factory geometry. It does not itself authorize a second
Arena mutation.

## Outcome

Produce one bounded successor with the exact current flat b100/e6 suppression policy and this
lifecycle:

- gate-aware Chebyshev-1 ring only;
- diagonal harvest/protect/bank-surplus mothers;
- orthogonal size-2 cut/replant wood cycle;
- no full-ring PICK and no plant outside the ring;
- ETA<=6 opponent-crop work before ring cuts.

Return `SMOKE_QUALIFIED`, `CLOSED`, or `ARENA_HANDOFF` with exact artifact and fallback hashes.

## Governing artifacts

- `chatgpt_1/banana-ring-b100-successor/protocol.md`
- `chatgpt_1/banana-ring-b100-successor/implementation-delta.md`
- `chatgpt_1/banana-ring-b100-successor/lock.json`

Before opening any fresh range, the integrator may assign a D-series id and copy these to immutable
analysis paths. The immutable protocol then wins over this scheduling record.

## Proposed exclusive implementation write set

New paths only:

- `cgauto/make_banana_ring_b100_candidate.py`
- `cgauto/slim_banana_ring_b100_candidate.py`
- `local_codex_1/banana-ring-b100-successor/**`
- new focused generated-source tests or a new test injector owned by the implementation task
- new result/preflight files under an integrator-allocated
  `data/analysis/live-agent-6553250/<id>-banana-ring-b100-*` prefix
- this task’s owner-specific status/message namespaces

No ownership is active until the integrator publishes and the assignee acknowledges it.

## Shared read-only paths

- `rust/src/bin/yamo_orchard_live.rs`
- `cgauto/make_banana_factory_b100_candidate.py`
- `cgauto/slim_banana_factory_b100_candidate.py`
- `local_codex_1/banana-factory-b100-owner-override/**`
- `rust/src/botmain/tactics.rs`
- `rust/tests/ringfarm.rs`
- `rust/tests/ringfix3.rs`
- exact b100/e6 fallback and current live full-factory artifact
- existing open stream/panel/latency/promotion tooling

## Do not touch

- byte-sacred formatted source except declared compile-then-exact-restore; final SHA prefix
  `fff6669b` required
- current live artifact or immutable execution records
- `cgauto/api_submit.py` before a controller handoff
- `data/raw/games/`, sealed ranges, official holdout
- H3a and initial-sector task write sets
- any Arena/TestSession mutation by a contributor

## Deliverables

- exact-parent successor generator
- ring-aware factory-specialized slimmer
- full research/compact/Arena sources and sidecars
- all existing semantic tests plus focused ring/bank/protection tests
- existing eight-stream full-vs-Arena equality result
- source size, runtime, stderr, mutated-parent, and sacred-source evidence
- small paired behavioral/value smoke with ring telemetry
- exact fallback identity and controller handoff only on pass

## Acceptance checks

- maximum own banana Chebyshev distance from tent: `1`
- concurrent own banana count never above eligible ring capacity
- plants outside eligible ring: `0`
- full-ring bank PICK: `0`
- full-ring harvested/carried banana produces tent DROP path
- diagonal harvest successes positive when ripe; diagonal ordinary chops `0`
- orthogonal size>=2 chop successes positive
- ETA<=6 opponent-crop displacement `0`
- own-plant provenance errors `0`
- PICK/DROP and target-retarget loops `0`
- all embedded tests pass
- optimized standalone compile, empty-input exit, source `<100,000` bytes
- exact equality on eight existing streams / 2,400 commands / zero stderr
- runtime within the frozen fast gate
- paired smoke reports own/opponent score, margin, catastrophes, negative mass and contains no severe tail regression

## Arena authority

Read-only monitoring: allowed under standing policy.

Platform mutation: `local_codex_1` only, after a pushed exact artifact/preflight, owner
notification, no concurrent cycle, exact fallback verification, and an explicit decision ending or
superseding the current live full-factory monitoring window. No automatic submission follows from
this proposed task.

## Handoff

The publication branch supplies the corrected behavior contract and a method-level delta against
the accepted fast publication pipeline. The integrator should acknowledge, assign or reject the
write set, and state whether the existing 30-minute live observation is complete before any
successor Arena action.