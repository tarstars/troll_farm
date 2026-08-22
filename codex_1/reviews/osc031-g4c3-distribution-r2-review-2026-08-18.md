# OSC-031 G-4c.3 distribution r2 review — 2026-08-18

Verdict: **G-4c.3 ACCEPTED**. The measured attribution is accepted for this one pinned
OSC-031 population; bug-versus-correct-caution remains exclusively the owner's ruling.

Pinned artifact: `a658875c337459beb7a521306a3aa21f506470c8` on
`agent/claude_1`.

## Independent reproduction

`g4c3.py` regenerates both committed evidence artifacts byte-for-byte. The run verifies
the owner-pinned manifest SHA-256
`b9eed4c2d66401761845bcb223893cc91a82171806cc43fd1ce4175bae1f21e5`,
retains exact resident/instrument parity, and reconciles all 727 invocations through the
accepted chain validator.

The repaired evidence proves:

- all 167 pinned turns are represented and the per-turn key set equals the manifest;
- 31 observed evaluation turns outside the population are explicitly enumerated;
- 315 lossless terminal records are present and all 315 `(call, turn, unit, plant)`
  identities are unique;
- per-turn counts, record count, and complete clause-distribution sum each equal 315;
- all 315 terminals are `PREDICT_TREE_NONE`;
- no pinned turn contains mixed terminal clauses; and
- the complete eight-row distribution reports explicit zeros for every other clause.

The attached Markdown clause-decision table is present at the pinned commit, states the
population and manifest pin, includes the complete table and exclusion accounting, and
uses neutral one-game wording with all scope boundaries intact.

## Accepted attribution

Across the owner-pinned 167-turn OSC-031 population for unit 0, the chop planner executed
315 per-tree evaluations. Every evaluation terminated at `PREDICT_TREE_NONE`; no other
clause was terminal in this population. This is an attribution measurement, not a
judgment that the clause is defective or correct.

## Gate disposition

- G-4c.1: **ACCEPTED**.
- G-4c.2: **ACCEPTED**.
- G-4c.3: **ACCEPTED**.
- Neutral owner brief: **AUTHORIZED**.
- Bug/caution ruling, any fix charter, harmless stamp, class-wide follow-up, and Arena
  action: not decided or authorized by this review.

The protected resident and dev copy remain untouched.
