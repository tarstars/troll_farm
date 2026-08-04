# 20260804-orchard-activation-species-audit

- Status: complete_with_method_correction_and_design_spec
- Record owner: chatgpt_1
- Work owner: chatgpt_1
- Integrator: local_codex_1
- Branch: `agent/chatgpt_1-orchard-activation-species-audit`
- Base: `agent/local_codex_1` after the completed eight-leg orchard/no-orchard cycle
- Created UTC: 2026-08-04
- Completed UTC: 2026-08-04

## Outcome

All eight exact one-hour Arena legs were audited: 1,280 sanitized full replays, four no-orchard legs and four current-APPLE-orchard legs. The analysis measured the live activation cases, the already-implemented idle-only alternative, a travel-only and a continuous-attack safety discriminator, and APPLE versus BANANA as an otherwise identical protected mother.

After the result, the owner requested a durable design record. The task now also contains a canonical human-readable and machine-readable specification for:

1. the deployed APPLE secure harvest orchard;
2. the proposed bounded self-sustained BANANA wood orchard;
3. the distinction between a protected mother and a disposable cut/replant tree;
4. the next common-seed comparison programme.

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

## APPLE design disposition

The deployed APPLE orchard is a protected water-adjacent harvest mother on an orthogonal tent door. It is never intended for our bot to chop. Its high health and effective cooldown 2 beside water are direct advantages. The starter owns the mother after activation and follows MOVE/HARVEST/DROP/WAIT; the second worker retains an alternate door and the ordinary Yamo economy.

The next possible APPLE refinement is a prospective opportunity-cost gate comparing guaranteed orchard value with the exact starter task that activation would displace. No threshold may be fit on the current 1,280 outcomes.

## BANANA design disposition

A like-for-like protected BANANA mother is rejected. The surviving BANANA hypothesis is a distinct bounded wood-production architecture:

- one protected diagonal mother, harvested for seeds;
- one orthogonal side-neighbor cut/replant slot, chopped for wood;
- one explicit owner for each role;
- one recovery seed reserved;
- confirmed seed and banking transactions;
- no child fruiting, unbounded planting, same-cell contention, or period-2 movement;
- exact parent commands outside declared activation.

Version 1 is statically limited to one mother and one cut slot. Prior unbounded/ring implementations do not count as valid value evidence for this bounded design.

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

Analysis:

- `chatgpt_1/orchard_activation_species_audit.py`
- `chatgpt_1/patch_orchard_activation_species_audit.py`
- `chatgpt_1/orchard-activation-opportunities-2026-08-04.csv`
- `chatgpt_1/orchard-activation-species-audit-2026-08-04.json`
- `chatgpt_1/orchard-activation-species-audit-final-2026-08-04.json`
- `chatgpt_1/orchard-activation-species-audit-final-2026-08-04.md`

Canonical design records:

- `chatgpt_1/apple-and-banana-orchard-design-2026-08-04.md`
- `chatgpt_1/apple-and-banana-orchard-design-2026-08-04.json`

Coordination:

- exact package hashes, run log, correction scripts, status, and handoff to `local_codex_1`.

## Next eligible experiments

1. `C0`: current APPLE orchard.
2. `C1`: current APPLE orchard plus a mechanics-derived opportunity-cost activation gate, on fresh common seeds.
3. `C2`: bounded BANANA diagonal mother plus one orthogonal cut/replant slot, treated as a distinct wood-production architecture.

Neither candidate was built or submitted in this task. Arena execution remains serialized under `local_codex_1` and requires an explicit release.
