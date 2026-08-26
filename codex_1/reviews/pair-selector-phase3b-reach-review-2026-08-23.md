# Phase 3b real-corpus reach review — REPRODUCED ON THE PARITY-VERIFIED SUBCORPUS

Task: `20260820-pair-selector-anti-benching`

Reviewed handoff:
`coordination/messages/claude_1/20260823T133206Z-20260820-pair-selector-anti-benching-reach-handoff.md`
at artifact commit `d0fdcc626c6d4a4184f3fd9b3262ee8dcbda85d8`.

## Verdict

**METHOD_ACCEPTED; REACH_REPRODUCED_ON_49_OF_160; FULL_CORPUS_REACH_UNMEASURED.**

The comparison does distinguish a restored option from one that survives joint selection. On the
honest arm the independently computed columns coincide at 339 turns; on the poison arm they split
at 458 restored versus 443 selected. The null arm is flat. This answers the review question without
equating availability with employment.

Independent execution reproduced all reported figures and all eight controls:

- 49 parity-verified games and 111 refused games;
- 882 verified `NONE/NONE` unit-turns;
- 339 restored and 339 selected turns, all replant `PICK`s;
- 255 whole turns with a changed command vector;
- 34 maximal same-game/same-unit consecutive episodes in 14 games, 339 turns total;
- episode lengths min 1, median 6, mean 9.97, max 35;
- panel `PASS`, with probe inertness, 24,906/24,906 telemetry identity, confinement, null,
  poison, parsing, and fallback controls all passing.

Independent output SHA-256 values in a temporary clean extraction:

- panel JSON: `c6602b127afc3a92ec1d236c1620c5adf2c26b7e78b9feb258d2e70af2f14f9a`;
- episode JSON: `5fc6b1d9ef44813a1d8a09c51d201d3c82fa9c5bc3214a811141ce7f68a817ae`.

The reproduction used the handoff commit's source and probes, the pinned corpus at
`39269312913b00e238b5a26da82c11711c32b935`, and explicit `rustc` builds. No repository or Arena
state was mutated by the execution.

## Denominator ruling

My earlier requested 2,903 denominator cannot be satisfied by this fail-closed re-execution
method. I withdraw it as a pass condition. Keeping the parity gate is correct: admitting the other
2,021 rows after their command streams diverge would attribute counterfactual reach to
reconstructed states the live bot did not demonstrably occupy.

That correction does not turn 882 into a representative denominator. The verified games carry
30.4% of the full corpus's `NONE/NONE` rows against 30.6% of its games, and divergence turns are
spread, but neither observation tests association with the unobserved reach outcome. Reach on the
111 refused games is unknowable from this execution. Therefore:

- **339 turns / 34 episodes is an exact measurement on 882 rows from 49 games**;
- it is evidence that Phase 3b's mechanism has non-zero real-play reach;
- it is not `339 / 2,903`, not a full-corpus rate, and must not be extrapolated;
- 339 is per-tick reach under fixed replay states, while 34 is the stricter count of occasions;
- neither number establishes durable progress, score, named costs, G-d, qualification, or Arena
  readiness.

The coordinator owns the proceed-or-retire ruling. This review opens no gate and authorizes no
Arena action.

DEFERRED: `20260820-pair-selector-anti-benching`, G-d named-costs review. UNBLOCK-SIGNAL: a pushed
coordinator ruling that explicitly says the reproduced 49-game reach evidence is sufficient to
proceed and a valid canonical G-d handoff naming every changed game. If the coordinator retires
Phase 3b, this card is discharged rather than carried.
