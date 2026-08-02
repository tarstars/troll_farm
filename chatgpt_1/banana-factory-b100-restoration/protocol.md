# Banana factory + current b100/e6 restoration protocol

- Task: `20260802-banana-factory-b100-restoration`
- Status: pre-lock packet published; implementation not started
- Repository: `tarstars/troll_farm`
- Base: `8e95a966d618c538829b184ad71a1539a76d2e29`
- Branch: `agent/chatgpt_1-banana-factory-restoration`
- Control: `cgauto/submissions/candidate-agent6553250-opponent-crop-b100-e6-slim.min.rs`
- Control SHA-256: `6f992a5a4d58e5f3f78478322ab0f3ce6cf8706d5aa9bb57d10f8264b03a3f19`
- Sacred source: `rust/src/bin/yamo_orchard_live.rs`
- Sacred SHA-256: `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`

## Question

Does restoring the already implemented closed-loop BANANA factory on top of the exact current flat opponent-crop `+100`, ETA `<=6` policy improve margin without recreating D89's opponent-economy leak?

This is not another stateless early-PLANT rule. The treatment restores the whole existing lifecycle: start after worker two, spend initial banked BANANAs, protect one reserve, harvest tracked own ripe bananas, replant harvested seeds, keep trained workers on wood/logistics, and retain current opponent-crop priority.

## Frozen intervention

Add only this research constructor to a temporary copy of the sacred source:

```rust
pub fn banana_seed_factory_opponent_crop_b100_e6() -> Self {
    let mut bot = Self::banana_seed_factory();
    bot.inner.opponent_crop_bonus = 100;
    bot.inner.opponent_crop_eta_limit = 6;
    bot.inner.opponent_crop_start_turn = 1;
    bot.inner.opponent_crop_min_seen = 1;
    bot
}
```

The experiment entry point uses that constructor. Do not enable the D91 selector, source-separated grammar, dual-value scoring, worker-three bridge, new thresholds, map features, or post-result tuning.

## Four-arm design

Run every map, seat, and opponent with:

1. `resident`
2. `opponent_crop_b100_e6` — primary current control
3. `banana_seed_factory`
4. `banana_factory_opponent_crop_b100_e6` — candidate

Primary contrast: candidate minus current b100/e6. Secondary contrasts isolate the factory effect, b100 effect, and factorial interaction.

## Required integrity and side-effect coverage

Every changed command must be classified as one of: direct starter-factory rewrite, direct proven opponent-crop selection, reserve/conflict consequence, or joint-selector collateral. Any unclassified divergence fails integrity.

Tests and telemetry must cover:

- exact command parity before worker two and exact activation boundary;
- natural/own/opponent crop provenance, failed attempts, pruning, and final-command own-plant bookkeeping;
- seed-budget, reserve promotion/loss, failed and successful PICK/HARVEST/PLANT reconciliation;
- at least one harvest-to-replant lifecycle in semantic tests;
- worker births/specs, inventories, bank congestion, shack occupancy, and zero worker-three activity;
- trained-worker command whitelist `MOVE|CHOP|DROP|WAIT` and zero forbidden actions;
- final move legality, collision resolution, door queues, oscillation, repeated failures, stalls, and endgame cargo;
- opponent score split by natural/our/opponent/unknown crop provenance, opponent-created crop output, theft from our crops, and opponent workforce growth;
- one-thread versus 20-thread byte equality, standalone compile, source size, latency, stderr, and research-versus-slim command equality.

## Panels

Consumed D89 maps `9,914,032-9,914,047` are diagnostic only and cannot qualify the candidate.

Before implementation, the integrator allocates and collision-scans a fresh contiguous 32-map discovery range and the adjacent sealed 32-map confirmation range. Each panel is:

```text
32 maps x 2 seats x 8 opponents x 4 profiles = 2,048 games
```

Use unchanged opponents: `compact_gold`, `gold_adaptive`, `gold_elite`, `mybot`, `printer_bot`, `sched_bot`, `script_boss`, `silver_boss`. Run once with one thread and once with 20 threads. Do not tune after seeing discovery.

## Frozen gates

Integrity requires exact hashes, restored sacred source, exact repeats, 2,048 rows/512 complete cells, >=95% fruit and wood provenance, zero preactivation mismatch, zero forbidden trained actions, zero worker-three activity, exact worker counts candidate versus b100, bounded counters, zero unclassified divergence, and all source tests green.

Mechanism requires factory activation in >=320/512 tasks across both seats/all families, >=75% of active tasks bootstrapping at least three seeds, >=128 tasks completing own-crop harvest plus renewable replant, b100 seeing opponent crops in >=32 tasks and selecting them in >=16, with no reserve/budget/role invariant failure.

Primary value candidate versus b100 requires:

- mean paired margin >= `+1.0`;
- map-cluster 95% CI lower bound >= `0`;
- active mean margin >= `+4.0` and own score >= `+2.0`;
- more active improvements than regressions; regression rate <=40%;
- >=6/8 family means nonnegative; worst family >=`-5`;
- p10 >=`-20`; worst task >=`-60`;
- catastrophes do not increase; negative-margin mass ratio <=1.0;
- active wood and own-crop harvest deltas positive.

Competitive safety candidate versus b100 requires opponent score <=`+1.0`, positive own-score delta, opponent delta <=40% of own delta, opponent-created fruit/wood each <=`+2` mean with clustered 95% upper bound <=`+5`. Within factory, adding b100 must reduce opponent score by >=5, cost our score no more than 5, and not increase direct theft from our crops.

Runtime/package requires p95 <=20 ms, max <=100 ms, artifact <100,000 bytes, research/slim command identity, and exact sidecar.

Discovery passes only if every gate passes. Confirmation uses the same code, analyzer, and gates. Any failure closes the exact candidate without retuning.

## Packaging and rollout

The current slimmer may remove factory code because it was dead in the resident. Build and test the activated research source first, then create a factory-aware fail-closed slimmer, compile it, prove research/slim command equality, and freeze source, minified artifact, patch, generator, and SHA sidecars.

Only `local_codex_1` may mutate Arena. After `QUALIFIED_LOCAL`, run exact-current b100 capacity A/A, then one candidate submission. Compare same-window reads around +20/+35/+50 minutes and at 20/50/100/160 battles. Identity mismatch, runtime signal, catastrophe/tail/negative-mass regression, opponent-output leak, or decision-capable delta <=-0.5 triggers exact-control restore. Keep only a mature same-window >=+0.5 improvement with clean safety and attributable mechanism.

## Coordination boundary

This publication is a proposal, not an implementation claim. The integrator must allocate a D-id, reviewer, implementation owner, explicit harness/source write-set transfer, and fresh ranges before source or simulation work starts. No contributor Arena mutation is authorized.
