---
type: HANDOFF
task_id: 20260804-orchard-activation-species-audit
from: chatgpt_1
to: local_codex_1
cc: user, claude_1
created_utc: 2026-08-04T06:45:00Z
requires_ack: true
---

# Handoff: secure-orchard activation and species audit complete

## Authoritative artifacts

- report: `chatgpt_1/orchard-activation-species-audit-final-2026-08-04.md`
- corrected machine verdict: `chatgpt_1/orchard-activation-species-audit-final-2026-08-04.json`
- detailed 1,280-row table: `chatgpt_1/orchard-activation-opportunities-2026-08-04.csv`
- full machine report: `chatgpt_1/orchard-activation-species-audit-2026-08-04.json`
- analyzer: `chatgpt_1/orchard_activation_species_audit.py`
- exact-prefix/kill-safety patch: `chatgpt_1/patch_orchard_activation_species_audit.py`

## Final disposition

```text
KEEP_CURRENT_APPLE_ORCHARD
IDLE_ONLY_REJECTED_AS_EFFECTIVE_DELETION
TRAVEL_ONLY_SAFETY_REJECTED
KILL_SAFETY_NONDISCRIMINATING
BANANA_MOTHER_SWAP_REJECTED
PROSPECTIVE_OPPORTUNITY_COST_GATE_AND_BOUNDED_BANANA_PRINTER_REMAIN
```

## Main evidence

- eight LFS packages / 1,280 games hash-verify;
- orchard live-score mean 23.693 vs no-orchard 23.108;
- adjacent score deltas +1.60,+2.03,-0.36,-0.93; corrected exhaustive bootstrap interval [-0.645,+1.815];
- orchard adds 38 wins and 22 catastrophes over 640 games;
- current orchard activates 54/640; underlying starter action is MOVE 50, CHOP 1, WAIT 3;
- 51 activated games bank fruit, total 5,615 APPLE, median 121;
- idle-only keeps 3/54 and activates 0/640 no-orchard exact prefixes;
- travel-only safety is descriptively reversed and ignores chop time;
- all 54 APPLE activations survive a conservative continuous attack through first harvest;
- APPLE and BANANA share the same 46 exact-prefix activation states and both seeds are available in all 46;
- projected uninterrupted output is 133.15 APPLE vs 64.80 BANANA;
- zero exact initial-state/opponent-submission/seat game pairs exist across queues.

## Interpretation

The protected mother is harvested rather than chopped. APPLE's high health and water-accelerated cooldown are direct advantages. A like-for-like BANANA mother is inferior. A self-sustained BANANA wood printer remains a distinct hypothesis: one protected mother plus one bounded cut/replant slot, explicit ownership/banking, and zero oscillation/leakage.

The next activation candidate should compare projected orchard value against the inner starter task that would be displaced. Do not use `require_idle_starter=true` or an enemy-arrival threshold as a proxy.

## Method corrections

- Full fresh-process command parity is 696/1,280; exact prefixes through turn 100 are 911/1,280. Later drift is equal-choice MOVE/path tie behavior. Candidate decisions are used only before any drift.
- The original four-pair LCG bootstrap was invalid because low bits modulo four cycled through every pair. The authoritative corrected record enumerates all 256 ordinary resamples exactly.

No candidate was built, no fresh map range was consumed, and no Arena/TestSession mutation was performed. Please integrate the final report and use its two surviving experiment definitions when prioritizing the next task.
