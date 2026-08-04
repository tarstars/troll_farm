# 20260804-orchard-activation-species-audit

- Status: complete_with_method_correction
- Record owner: chatgpt_1
- Work owner: chatgpt_1
- Integrator: local_codex_1
- Branch: `agent/chatgpt_1-orchard-activation-species-audit`
- Base: `agent/local_codex_1` after the completed eight-leg orchard/no-orchard cycle
- Created UTC: 2026-08-04
- Completed UTC: 2026-08-04

## Outcome

All eight exact one-hour Arena legs were audited: 1,280 sanitized full replays, four no-orchard legs and four current-APPLE-orchard legs. The analysis measured the live activation cases, the already-implemented idle-only alternative, a travel-only and a continuous-attack safety discriminator, and APPLE versus BANANA as an otherwise identical protected mother.

## Final disposition

```text
KEEP_CURRENT_APPLE_ORCHARD
IDLE_ONLY_REJECTED_AS_EFFECTIVE_DELETION
TRAVEL_ONLY_SAFETY_REJECTED
KILL_SAFETY_NONDISCRIMINATING
BANANA_MOTHER_SWAP_REJECTED
PROSPECTIVE_OPPORTUNITY_COST_GATE_AND_BOUNDED_BANANA_PRINTER_REMAIN
```

Key findings:

- current orchard activated 54/640 orchard games;
- underlying starter action was MOVE 50, CHOP 1, WAIT 3;
- idle-only keeps 3/54 and activates 0/640 on no-orchard exact prefixes;
- 51/54 activations banked fruit, total 5,615 APPLE, median 121 per activated game;
- all 54 APPLE activations survive a conservative continuous enemy attack through first harvest;
- APPLE and BANANA have identical 46-game support on no-orchard prefixes, but APPLE's projected bank ceiling is 133.15 versus 64.80;
- repeated live mean Arena score is 23.693 orchard versus 23.108 no orchard, but the corrected four-pair bootstrap interval is [-0.645,+1.815];
- orchard adds 38 wins and 22 catastrophes over 640 games, so the live effect is polarizing rather than uniformly positive.

## Frozen analysis boundary honored

- The current APPLE rule and threshold were not refit.
- The idle-only arm changed only `require_idle_starter: false -> true`.
- The BANANA diagnostic changed only SecureOrchardBot's mother/seed species.
- Generated variants were interpreted only through their first divergence and before any deployed-source process-dependent path-tie drift.
- No post-divergence replay was treated as terminal counterfactual value.
- No Arena/TestSession mutation, sealed data, or raw replay duplication occurred.

## Method correction

The original acceptance target of full command parity in 1,280 games was not met: 696 games have full parity and 911 remain exact through the turn-100 activation window. Later differences are equal-choice MOVE/path tie drift across fresh Rust processes. The final method preserves only exact prefixes and excludes any candidate activation after the first deployed-source drift.

The first four-pair bootstrap implementation was also rejected because an LCG's low bits modulo four made every sample contain all four pairs. The authoritative corrected result enumerates all 256 ordinary resamples exactly.

## Deliverables

- `chatgpt_1/orchard_activation_species_audit.py`
- `chatgpt_1/patch_orchard_activation_species_audit.py`
- `chatgpt_1/orchard-activation-opportunities-2026-08-04.csv`
- `chatgpt_1/orchard-activation-species-audit-2026-08-04.json`
- `chatgpt_1/orchard-activation-species-audit-final-2026-08-04.json`
- `chatgpt_1/orchard-activation-species-audit-final-2026-08-04.md`
- exact package hashes, run log, and correction scripts
- handoff to `local_codex_1`

## Next eligible experiments

1. Current APPLE orchard versus a mechanics-derived opportunity-cost activation gate, on fresh common seeds.
2. Current APPLE orchard versus a bounded BANANA mother plus one cut/replant slot, treated as a distinct wood-production architecture.

Neither candidate was built or submitted in this task.
