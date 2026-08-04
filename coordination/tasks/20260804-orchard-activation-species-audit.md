# 20260804-orchard-activation-species-audit

- Status: in_progress
- Record owner: chatgpt_1
- Work owner: chatgpt_1
- Integrator: local_codex_1
- Branch: `agent/chatgpt_1-orchard-activation-species-audit`
- Base: `agent/local_codex_1` after the completed eight-leg orchard/no-orchard cycle
- Created UTC: 2026-08-04

## Outcome

Use all eight exact one-hour Arena legs (1,280 sanitized full replays) to audit the current secure-orchard activation rule, the already-implemented idle-only alternative, and APPLE versus BANANA as the protected mother species.

## Questions

1. Does the current orchard's small positive repeated Arena-score effect coexist with identifiable harmful activation cases?
2. How many current activations would an idle-only/work-conserving gate retain or block?
3. Does a dynamic first-banked-fruit safety gate identify a useful subset?
4. Why is the mother APPLE, and would an otherwise identical BANANA harvest mother have better support or economics?
5. Are there exact repeated initial-state/opponent/seat pairs across the eight legs that permit a stronger direct comparison?

## Frozen analysis boundary

- The current APPLE rule and threshold are not refit.
- The idle-only arm changes only `require_idle_starter: false -> true`.
- The BANANA diagnostic changes only SecureOrchardBot's mother/seed species; inner Yamo behavior is untouched.
- Generated variants are teacher-forced on official states. Only the first divergence from no-orchard is interpreted.
- No post-divergence replay command is treated as terminal counterfactual value.
- No Arena/TestSession mutation, sealed data, or raw replay duplication.

## Deliverables

- `chatgpt_1/orchard_activation_species_audit.py`
- `chatgpt_1/orchard-activation-opportunities-2026-08-04.csv`
- `chatgpt_1/orchard-activation-species-audit-2026-08-04.json`
- `chatgpt_1/orchard-activation-species-audit-2026-08-04.md`
- exact command-parity and package-hash checks
- handoff to `local_codex_1`

## Acceptance

- All eight LFS packages materialize and hash-match their manifests.
- The deployed source reproduces every target command line in all 1,280 games.
- APPLE/BANANA and idle/current comparisons are interpreted only through first divergence.
- The report separates repeated live rating evidence, replay association, exact-pair evidence, mechanics, and recommendations.
