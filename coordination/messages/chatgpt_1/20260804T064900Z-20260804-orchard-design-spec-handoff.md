---
type: HANDOFF
task_id: 20260804-orchard-activation-species-audit
from: chatgpt_1
to: local_codex_1
cc: user, claude_1
created_utc: 2026-08-04T06:49:00Z
requires_ack: true
---

# Handoff: canonical APPLE and BANANA orchard designs published

The owner requested that all orchard conclusions be written down with special attention to both designs.

## New authoritative design records

- human-readable specification: `chatgpt_1/apple-and-banana-orchard-design-2026-08-04.md`
- machine-readable specification: `chatgpt_1/apple-and-banana-orchard-design-2026-08-04.json`

These complement, rather than replace, the corrected analysis:

- `chatgpt_1/orchard-activation-species-audit-final-2026-08-04.md`
- `chatgpt_1/orchard-activation-species-audit-final-2026-08-04.json`
- `chatgpt_1/orchard-activation-opportunities-2026-08-04.csv`

## APPLE design

```text
STATUS: DEPLOYED_RETAIN
ROLE: protected persistent harvest mother
LOCATION: water-adjacent orthogonal home-door cell
OWNER: starter
ACTIVE LOOP: MOVE -> HARVEST -> DROP -> WAIT
DO NOT CHOP
```

The document records the exact static geometry, runtime activation predicate, state machine, alternate-door protection, mechanics, evidence, and rejected alternatives.

The next eligible APPLE refinement is not idle-only activation and not an enemy-arrival threshold. It is a prospective opportunity-cost gate:

```text
activate only if V_orchard >= V_displaced + frozen_delta
```

The inner starter task must expose mechanics-based expected banked score before override. No threshold may be fit on the current 1,280 outcomes.

## BANANA design

```text
STATUS: PROPOSED_UNQUALIFIED
ROLE: bounded self-sustained wood production
MOTHER: one protected diagonal near-tent BANANA, harvested for seed
CUT SLOT: one orthogonal side-neighbor BANANA, always chopped for wood
```

The design formalizes the owner's tent-neighbor rule:

- diagonal neighbors are mother/seeding cells and are never chopped;
- orthogonal side-neighbors are cut/banking cells and are chopped for wood.

Version 1 is statically bounded to one mother and one cut slot. It requires an explicit mother worker, wood worker, transactional seed ledger, one recovery seed, confirmed PLANT/HARVEST/DROP deltas, monotone banking, no child fruiting, no opponent leakage, no same-cell contention, no period-2 movement, no training displacement, and exact parent commands outside activation.

A like-for-like BANANA protected-mother swap remains rejected. The bounded wood printer is a distinct architecture and must be compared against the current APPLE orchard.

## Next experiment recorded

```text
C0: current APPLE orchard
C1: APPLE + opportunity-cost activation gate
C2: bounded BANANA mother + one orthogonal cut/replant slot
```

The design memo contains pre-value and terminal-value gates. No source candidate, fresh map panel, TestSession, submission, or Arena action was created or authorized.

Please acknowledge and integrate these design records as the canonical orchard specification for future implementation work.
