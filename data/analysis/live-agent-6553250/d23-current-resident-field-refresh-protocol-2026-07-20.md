# D23 current-resident field refresh — frozen protocol (2026-07-20)

## Question

Does the newest exact stable-resident landing still lose through the previously observed late
opponent-compounding mechanism, or has its mature field distribution shifted enough that the next
controlled experiment should target opening/workforce architecture instead?

This is a read-only diagnostic.  It may fetch completed battle and leaderboard records, but it
must not start games, submit source, change the resident, or construct a candidate.

## Frozen identity and data

- Expected resident agent: `6561795`, submission `41015603`.
- Expected source: `candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`, 62,725 bytes,
  SHA-256 `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`.
- Request the most recent 80 finished battles exposed by the current test-session handle.
- Parse referee-confirmed effects, terminal inventories, crop provenance, fixed-turn snapshots,
  and opening geometry with the already-tested `recent_resident_field_census.py` pipeline.
- Compare descriptively with the 80-game restored-resident census for agent `6560353`.  This is
  not a paired causal comparison because opponent and map mixtures may differ.

## Readiness gates

The refresh is interpretable only if:

1. the leaderboard identifies agent `6561795` as the current resident;
2. at least 40 finished games parse;
3. every parsed row belongs to agent `6561795`;
4. there are zero replay-fetch failures and zero unknown replay-diff updates; and
5. terminal scores and effect telemetry are present for every row.

If any gate fails, retain the older field evidence and do not tune a hypothesis on the partial
refresh.

## Frozen decision rule

Report win/loss/tie counts, mean margin, catastrophic-loss frequency (`margin <= -100`), share of
negative margin carried by catastrophes, opponent crop/wood gaps, workforce, planting, harvest,
and turn-50/75/100 observables.

- If catastrophic frequency is at least 10%, catastrophic losses contain at least half of all
  negative-margin mass, span at least three opponents, and have at least +20 opponent wood versus
  non-catastrophic games, prioritize a coherent anti-compounding macro.
- Otherwise, if readiness passes, prioritize the resident's structural production gap: opening
  recipe, renewable supply, and productive workforce scale as one policy-level intervention.
- Do not fit a new early-risk rule on these 80 rows for deployment.  Any observable contrast is
  hypothesis-generation evidence only.

## Outputs

- raw census: `d23-current-resident-field-refresh-2026-07-20.json`;
- result and next-experiment decision:
  `d23-current-resident-field-refresh-result-2026-07-20.md`.

