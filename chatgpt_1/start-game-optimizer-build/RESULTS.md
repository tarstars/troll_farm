# Start-game optimizer build — mechanics result

Date: 2026-09-04  
Task: `20260904-start-game-optimizer-build`  
Candidate: `candidate-start-game-optimizer-v6-instrument.rs`  
Control: unchanged champion of record

## Verdict

**STOPPED AT THE PRE-REGISTERED MECHANICS GATE.** The candidate passes source generation, compilation, exact compacted round trip and the 34-case differential bed, but passes only **19 of 24** real-map smoke cases. Five maps contain a new no-progress stall. The card says to stop immediately on any candidate or control smoke failure, so no timing, budget-quality, development panel, field reading or sealed holdout was run.

This is a failed first implementation, not evidence against every PLANT-aware optimizer. It is evidence against this scheduling model: it evaluates planting trees in isolation but does not charge the resulting delay to the champion's second-troll opening and continuation accurately enough.

## Build facts

- Five model-level falsifiers pass.
- Diagnostics arm, owner-readable source and compacted submission all compile.
- `compact(arm)` round-trips exactly to the generated submission.
- Generated submission SHA-256: `38a604ee278160056577fbf2e2642907e03e154b601aafb5bc2be06648b57b4d`.
- Source size: **77,043 UTF-16 code units**, below the 100,000 limit.
- Third-troll training is disabled in the provisional parameter file. This gate tests explicit planting first.

## Differential bed

Candidate:

- plays 34/34;
- deterministic 34/34;
- compacted command stream equals the diagnostics arm 34/34;
- telemetry errors 0;
- differs from the champion on 28/34.

The first warning appears here: on `OSC-010`, the champion trains its second troll at turn 19 while the candidate never trains within the 200-turn fixture. The bed's formal mechanics status is PASS, but this is the same scheduling displacement seen more broadly in smoke.

Unchanged champion control:

- plays 34/34;
- deterministic 34/34;
- compacted equals arm 34/34;
- byte-identical behavior to the readable champion 34/34;
- telemetry errors 0.

## Real-map smoke

Candidate result:

```text
mechanics: 19 / 24
stalled maps: 5
referee/telemetry errors: 0
own-score sum minus resident: -302
better / worse / equal own score: 7 / 14 / 3 maps
third troll: disabled; 0 / 24
```

Stalled map hashes:

```text
c84154d29ea19fbc
19111bc9b90011bb
33261cf926f7a3eb
d9c8059a3038862e
b64b9915e3f228af
```

The candidate issued legal commands for all 300 turns and emitted no telemetry error. The failure is no-progress behavior, not parsing or command legality.

## What the candidate actually did

- It planted **300 trees over 24 games, 12.5 per game**, with a range of 3–21.
- Its first optimizer plant was at turn 4 or 5 in every smoke game.
- It trained the second troll on turn 1 in 10 games, but delayed it to the hard fallback turn **35 in 14 games**.
- The unchanged resident trained earlier than turn 35 on all of those delayed cases.

This exposes the implementation error. The planter evaluates an explicit tree's seed, travel, growth, felling, banking and raid exposure, but it treats the worker opportunity cost as a fixed points-per-turn scalar. It does not replay the shadow champion deeply enough to price the discrete loss of postponing the second troll. Consequently a locally positive banana planting macro can override the opening that creates the second worker, and repeated locally positive plants can create long idle tails after the orchard is exhausted or protected.

In other words, `PLANT` entered the action vocabulary, but **the baseline comparison did not enter the state transition strongly enough**. The correct design said every candidate sequence must be compared against the champion continuation on the same state and scenario. This first build used a per-tree surrogate instead. The smoke falsified that shortcut before value testing.

## Why no repair follows in this card

The five failures are not a one-line reporter defect:

- two maps show an after-horizon idle run 30 turns longer than the resident;
- three maps show a funding-window idle run 20–27 turns longer than the resident;
- the delayed-second pattern affects 14 of 24 maps;
- the own-score deficit is 302 points on the development slice.

Changing a threshold, forbidding early bananas or exempting the five maps would tune against development data and would not repair the missing paired continuation model. The next valid design would need to make the unchanged champion trajectory an explicit search branch at every irreversible planting decision, not just a scalar opportunity-rate estimate.

## Reproduction

Self-run GitHub Actions execution:

- run `33870972088`;
- source commit `d47279ce7e421147858af6d5267ec4f0c6e48b5f`;
- generated result commit `185950253593928545e2d5a5cf83edc452900807`.

The branch workflow is execution evidence from the author, not independent verification. The coordinator can reproduce from the generated result commit using:

```text
bash chatgpt_1/start-game-optimizer-build/run_mechanics.sh
```

The command stops at the failed candidate smoke exactly as the card requires.

## Disposition

**BLOCKED / candidate dead under this card's mechanics condition.** Keep the action manifest, generator and failed smoke as a falsifier. Do not submit this candidate and do not read a value panel. Reopening requires a new card whose implementation performs an explicit paired champion continuation at planting decisions and first demonstrates that it preserves the second-troll opening.
