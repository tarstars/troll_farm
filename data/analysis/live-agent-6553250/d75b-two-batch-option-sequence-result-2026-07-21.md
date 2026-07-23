# D75b horizon-repaired two-batch option-sequence result (2026-07-21)

## Verdict

**Close short fixed ordinary-option sequences before oracle analysis.** D75b repairs D75a's sole
horizon defect and passes every mechanical and execution check. The sequence library nevertheless
fails its frozen activity gate: its 16 fixed mean margins span only **3.455** points versus the
required **15**.

No full-library oracle, prefix oracle, incremental headroom, label fit, selector, candidate,
confirmation, or platform action was opened. The next eligible direction is whole-policy search
with a different controller representation.

## Horizon repair and integrity

D75b changes only manifest eligibility from `turn < 300` to `turn < 299`. The outcome-blind
selection retains 565 identities and replaces all 11 selected turn-299 identities by the next
smallest hashes in their unchanged strata. The repaired 576-state manifest has maximum turn 298
and SHA-256 `e72457111564ea221559548e4a5f5afa59a4b8322ee5d2c6bff2545a9c241deb`.

Both 9,216-row matrices are byte-identical at SHA-256
`d8b7f5240f7826cf87f9402c8887877fbdef25e3887fa50d46a702dc15e85aef`.

- all 576 x 16 rows exist with no duplicates or missing arms;
- every arm reaches and executes its second boundary;
- each of balanced, harvest, renew, and fell executes exactly 2,304 times as second mode;
- no second request is illegal and no renewable fallback is needed;
- task/turn/feature replay and all sequence accounting are exact;
- 329/329 represented balanced tasks have consistent terminal outcomes;
- command, provenance, deposit-prediction, crop, and reward-identity failures are zero;
- concurrent repeats sustain 21.71 and 22.43 continuations/s at 9.54 and 9.93 effective cores
  each, fully occupying the 20-logical-core host.

## Frozen activity gate

Ten of twelve non-prefix sequences change action hash in at least 10% of states, passing the
trajectory-activity requirement. Second actions are universally reached and all modes execute.
The decisive failure is outcome sensitivity:

| Fixed sequence measure | Result | Gate |
|---|---:|---:|
| Highest mean margin | +50.674 (`fell>balanced`) | descriptive |
| Lowest mean margin | +47.219 (`renew>harvest`) | descriptive |
| Mean-margin span | **3.455** | at least 15 — **fail** |

Control `balanced>balanced` averages +50.370. Thus no fixed sequence differs from control by even
three mean points, despite broad action-hash changes. The modes rearrange individual trajectories
but have little stable population-level effect over this two-batch horizon.

## Why this is not repeated again

The generic machine quarantine labels any failed execution/activity gate `repair_only`. Here,
base integrity is fully green and the two runs are byte-identical. The sole failure is a frozen,
deterministic representation-activity threshold; there is no implementation defect an unchanged
repeat could repair. The separate adjudication records this distinction without reading the
sealed oracle or relaxing the gate.

This closes two-batch sequence labels. Adding a third batch, pruning sequences, lowering 15, or
fitting per-state winners on these consumed rows is not allowed.

## Multilevel interpretation

1. **Mechanics:** exact same-state multi-action replay is validated, including second-boundary
   execution and renewable legality.
2. **Horizon:** one batch is sparse (D74); two fixed batches are behaviorally active but globally
   weak. Short open-loop temporal extension is not the missing control abstraction.
3. **Learning:** D73's PPO failure should not be repaired by offline imitation of D75 sequence
   winners; the label interface did not clear activity before value.
4. **Search:** the strongest remaining evidence is D72's broad recurrent whole-policy population
   span and oracle. Optimize complete recurrent policies directly with trajectory-level robust
   objectives instead of assigning local sequence labels.
5. **Deployment:** the live 62,725-byte resident remains unchanged; none of D75a/b updated or
   submitted the program.

## Next experiment

Freeze a black-box whole-policy search preflight over a compact recurrent four-mode controller.
Use fresh development/validation maps, direct complete-episode objectives, explicit crop/workforce
safety, opponent-family robustness, and immutable population seeds. First require that evolution
improves a single fixed policy out of sample; only then consider source export or field
qualification.

## Artifacts

- repair protocol: `d75b-two-batch-option-sequence-repair-protocol-2026-07-21.md`;
- repaired manifest and summary JSON;
- repeated D75b matrices and timing sidecars;
- machine result: `d75b-two-batch-option-sequence-result.json`, SHA-256
  `42def0e5d4c7718b3b5e496c19f7c6a6e0a931f2a7991c7413e5c0c799cbc104`;
- adjudication: `d75b-two-batch-option-sequence-adjudication.json`;
- unchanged runner: `rust/src/bin/d75_two_batch_option_sequences.rs`.
