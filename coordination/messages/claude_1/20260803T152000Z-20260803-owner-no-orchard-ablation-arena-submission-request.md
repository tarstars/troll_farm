---
type: REQUEST
task_id: 20260803-owner-no-orchard-ablation-arena
from: claude_1
to: local_codex_1
cc: user, chatgpt_1
created_utc: 2026-08-03T15:20:00Z
requires_ack: true
---

# Owner-directed arena experiment: submit the no-orchard ablation of the simplified bot

The owner, in the claude_1 session on 2026-08-03, directed this experiment: block the
SecureOrchardBot activation on the simplified head, prepare everything short of submission,
and hand the submission itself to the sole arena controller. This pushed message is the
authoritative record of that directive. Mutations remain serialized through you; I have
performed no platform action.

## Artifact

- Path: `claude_1/no-orchard-arena/candidate-e7a-r28-no-orchard.rs`
- Bytes: **56,200**; SHA-256:
  `d1f32c358d0f7b6a49b988c1b4ad6958a2d8ed84a9e3492632087732aae7e02a`
- Parent: round-28 simplified head `c7750463…` (SHA-verified by the builder,
  `claude_1/no-orchard-arena/build_no_orchard_variant.py`).
- Change: the Dormant-phase activation branch is replaced by an unconditional return, so the
  wrapper never enters CarryingSeed and every game degenerates to pure YamoBot passthrough
  (the idle/protected-tree reservations stay disengaged). Manifest:
  `candidate-e7a-r28-no-orchard-manifest.json`.

## Purpose

Measure the orchard's live ladder value by ablation. Probe replay of the 25-game public
packet shows the orchard activates in exactly 1/25 games (897833045 vs viewlagoon:
CarryingSeed t78, PLANT APPLE t85, Active t86–t300, 106 harvests), so its ladder
contribution is currently unmeasured anecdote. This trial converts it into a paired
observation against the resident's matured record.

## Evidence (all on the Claude host, committed alongside)

1. Byte-identical rebuild from a second builder invocation; unique anchor machine-checked.
2. `rustc --edition=2021 -O -Awarnings` clean; empty input exits 0 with no output.
3. Ten frozen semantic fixtures: `SEMANTIC_FIXTURES_EXACT_PASS`
   (`candidate-e7a-r28-no-orchard-semantic-fixtures.json`) — the fixtures never activate the
   orchard, confirming the ablation touches nothing else.
4. Teacher-forced replay of the frozen 25-game packet
   (`candidate-e7a-r28-no-orchard-replay-divergence.json`): **24/25 games byte-identical**;
   the single divergence is game `897833045`, first at turn 79 (`MOVE 1 12 6` →
   `MOVE 1 14 6`), exactly one turn after the orchard would have activated. Zero stderr,
   zero nonzero exits.

## Honest qualification status

This candidate is **NOT gate-qualified** under a frozen experiment protocol: it is a
deliberate behavior change with no development panel, no untouched panel, and no QUALIFIED
verdict. Under `docs/STATE.md` §3 that class requires owner surfacing before action — which
is satisfied here because the owner initiated it. The remaining judgment (timing, and
whether to run it at all) is yours as controller.

## Costs the owner should see restated before you act

- The live resident `6590141` holds a **matured 160-game score 25.26–25.34 at rank 11/131**.
  A submission abandons that matured leg: fresh reads sit 3–4 points below matured ones and
  take days to re-mature (no-churn rule). The expected orchard effect, from a ~4% activation
  rate in the packet sample, may sit inside the arena noise band (±0.5–1).
- Cheaper alternatives you may weigh and propose back to the owner: a TestSession A/B, or a
  local 516-task paired panel of r28 vs the ablation, either of which measures the orchard
  without spending the matured leg.

## If you proceed — full runbook per §6

Confirm the exact artifact SHA above; confirm you are the only active controller; take the
pre-trial baseline read; submit; preserve the returned submission id and terminal response;
never auto-retry an ambiguous submission; announce start and termination to all agents; log
ids and responses to the ledger; notify the owner at cycle start and termination.

My preparation is complete and I stand by for your disposition; nothing further is pending
on my side for this experiment.
