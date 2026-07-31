# L1 delineate-cloning readiness audit — 2026-07-31

## Verdict

**`DISTINCT_PRIMITIVE_ONLY`.**

L1 is not a duplicate of the project's prior imitation work. The current corpus contains
199 games from exact agent `6479768` and supports an exact, deterministic extraction of
final primitive commands on teacher states. That is a material expansion over Phase 9's
26 delineate games and coarse objective labels.

It is not a literal clone of delineate's hidden policy. Replays never expose the
continually selected train target, the previous internal target, logits, alternative
actions, joint beam, probabilities, weights, or PPO training state. Any successor must
say "primitive-command imitation from delineate replays," and teacher-forced accuracy
can only be a diagnostic before a separate closed-loop value gate.

No extractor, dataset, model, game, source, candidate, or Arena action was created.

## Current exact-agent substrate

The authoritative 9,082-game parsed corpus has zero parse failures. Selecting by
`agentId == 6479768`, never by pseudonym, gives:

| Property | Result |
|---|---:|
| Games | 199 |
| Old Phase-9 games retained | 26/26 |
| New games beyond Phase 9 | 173 |
| Seats | 98 seat 0 / 101 seat 1 |
| Distinct opponents | 53 |
| Turns | 59,403 |
| Raw replays present | 199/199 |
| Raw replay bytes | 67,053,448 |
| Parsed trajectory bytes | 7,978,463 |
| Game-ID span | 891153730–897319413 |

Every parsed occurrence has the same exact agent ID, pseudonym, and stored arena score
30.99. The current 147-row battle window also contains one agent ID and one submission
ID (`40707878`), but it is right-censored and is not used as the cumulative corpus.

The existing project decoder was run read-only on the 199 exact files. All 199
turn-count checks pass (59,403 decoded / 59,403 trajectory turns) with zero unknown diff
updates. It yields 145,448 per-unit rows, including implicit WAIT decisions.

## Exact label surface

The replays expose 144,265 explicit primitive unit commands:

| Verb | Count | Verb | Count |
|---|---:|---|---:|
| MOVE | 62,409 | CHOP | 34,806 |
| DROP | 19,097 | HARVEST | 15,511 |
| PLANT | 7,762 | PICK | 3,045 |
| MINE | 1,582 | WAIT | 53 |

They also expose 378 actual TRAIN commands with exact four-stat specifications. There
are zero MSG commands and 1,784 distinct exact command strings. State, unit ID, target
coordinate, resource kind, actual training event, final command ordering, and prior
emitted actions are observable.

The following are not replay labels:

- the train-plan target chosen before an actual TRAIN;
- the previous internal target used by the plan head;
- the 3,290 policy logits or their calibration;
- each unit's top-X alternatives;
- beam alternatives, invalidations, and joint probabilities;
- PPO rewards, advantages, value targets, weights, and curriculum states.

This distinction matters because the public plan head uses previous-target state and the
final joint command is selected after a beam over alternatives. A replay clone may learn
the emitted action conditional on visible state/history; it cannot claim to recover the
internal policy or its action distribution.

## Why this is distinct

| Evidence | Teacher / target | Result | Relation to L1 |
|---|---|---|---|
| Phase 9 | top five; 18 coarse objectives | delineate 60.413% accuracy / 0.329 macro F1 on 26 games | same teacher, but 7.65× fewer games and neither exact targets nor spatial/full state |
| Phase-9 complete gate | Escdemon rendered continuation | 52.12% MOVE-target after autoregressive integration | different teacher; covariate-shift warning |
| Phase 14 | Norxondor intent/goals | 76.937% held-game intent, then −172.663 paired margin | different teacher; proves teacher-state fit is not value |
| D41a | deterministic D40 candidate ordering | 84.386–84.960%; exact decoder 85,047/85,047 | different teacher/surface; warns against mismatched tiny scorers |
| Public delineate bot | PPO spatial + train-plan policy | rank one, ~101k policy parameters, ~98k characters, 2–3 ms | demonstrates feasibility; publishes no weights or hidden labels |

The register's shorthand that delineate was "never" imitated is therefore false if read
literally. It was tested coarsely in Phase 9 and failed macro F1. What has never been
tested is exact-agent primitive/spatial behavior cloning at the current 199-game scale.

## Public architecture and deployability

Delineate describes a 104×11×22 observation, four-block ResNet, 13 spatial action types
per cell, a shared 144-candidate train-plan head, sequential inference for the plan and
each troll, and a final joint-action beam. Training was a five-level PPO curriculum, not
behavior cloning. The reported policy has about 101k parameters, a 98k-character final
submission, and 2–3 ms turn time.

That proves the architecture class can fit the platform's 100,000-character gate. It
does not prove that the existing 62,725-byte Rust resident can absorb such a network or
that replay imitation can reproduce the PPO policy. Runtime and source size remain
downstream gates.

Public source: delineate gist revision
`e8a005ddd7568d71bf1523a8c62202511e55bd86`, raw SHA-256
`18265467b11b8f08828985aaef8c7d33716404e6b950fb3f9a4ff3470962fc36`.

## Smallest defensible successor

L1a is peer-review-gated and begins with a compose-only extractor/parity phase on these
199 consumed games:

1. Emit player-relative pre-action state and only the final per-unit primitive command
   plus actual TRAIN event/spec.
2. Do not infer train-plan labels, task grammar, logits, beam alternatives, or hidden
   state.
3. Split only by whole game; retain an ordered temporal block and separately report
   held-opponent sensitivity because the newest games are opponent-concentrated.
4. Report exact joint-turn command, exact per-unit command, verb macro F1, conditional
   target/resource accuracy, TRAIN timing/spec, legality, and deterministic replay parity.
5. Treat all teacher-forced metrics as diagnostic. Before source integration, freeze a
   closed-loop official-map panel requiring score/margin dominance over exact resident,
   opponent-family transfer, runtime/source-size compliance, and the existing substrate
   rule (resident fallback or prior same-panel dominance).

No numeric fit gate is invented in this readiness audit. It must be frozen only after
extractor parity establishes target counts and baselines.

## Integrity

- Parsed corpus SHA-256:
  `12f72265c2af19d69ddf9dad053ccc33b3c7f799182b23ca973210429500a73d`.
- Phase-9 result:
  `7ee3002414d467478ac5ac63d98f25a35c65c9f3f58a16e97c09cc6dccbceda1`.
- Phase-14 report:
  `3c7751656c47a299271390a5750fb0fe3b9c29186b006d499037f7ef38bb55c9`.
- D41a result:
  `9cb8905a75d408c71658068c6b09bb48937cc65e3e1307cea4e917849ae4b68d`.
- Sacred source:
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.
