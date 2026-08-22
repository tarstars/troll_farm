# Secure orchard activation and species audit — corrected final report

Task: `20260804-orchard-activation-species-audit`  
Analyst: `chatgpt_1`  
Data: eight exact one-hour Arena legs, 1,280 games  
Platform mutation: none

## Final verdict

**Keep the current APPLE secure orchard and its present activation rule.** The replay audit rejects the three simple alternatives tested here:

1. idle-only activation is effectively orchard deletion;
2. blocking whenever an enemy can arrive before the first bank ignores tree health and chop time;
3. replacing the protected APPLE mother with BANANA keeps the same activation support but roughly halves fruit throughput and sharply reduces survival margin.

The next plausible activation improvement is a **prospective opportunity-cost gate**, not another static distance threshold. Before the orchard wrapper overrides the starter, expose the inner task's predicted cycle ETA and expected banked score. Activate only when projected remaining orchard value exceeds the displaced task by a frozen mechanics-derived margin. This value is not present in replay output and must be tested closed-loop on fresh common seeds.

A self-sustained BANANA **wood printer** remains plausible, but it is a separate architecture: one protected mother supplies a distinct cut/replant plot. It is not a like-for-like replacement for the existing harvest mother.

## Repeated live comparison

| Variant | Legs | Games | Mean Arena score | Wins | Catastrophes | Mean game margin |
|---|---:|---:|---:|---:|---:|---:|
| no orchard | 4 | 640 | 23.108 | 343 | 69 | +8.233 |
| current APPLE orchard | 4 | 640 | 23.693 | 381 | 91 | +6.128 |

Adjacent orchard-minus-no-orchard Arena-score deltas were:

```text
+1.60, +2.03, -0.36, -0.93
```

Their mean is `+0.585` and median `+0.620`. Exact enumeration of all `4^4 = 256` ordinary paired-bootstrap resamples gives interval `[-0.645, +1.815]` and probability `0.234375` that the mean is nonpositive. These four queues are not paired game-for-game, so this is repeated live evidence rather than a clean causal rating estimate.

The stable qualitative pattern is polarization: the orchard produced **38 more wins** but also **22 more catastrophic losses** over 640 games. It increased wins in all four adjacent comparisons and catastrophes in all four.

## What the current APPLE orchard actually does

The orchard activated in **54/640 games = 8.44%**. At the activation point, the ordinary inner controller wanted the starter to:

```text
MOVE: 50 games
CHOP:  1 game
WAIT:  3 games
```

Of those 54 activations:

- 52 mothers were successfully planted;
- 51 games banked orchard fruit;
- 5,660 APPLE were harvested;
- 5,615 APPLE were banked;
- median banked APPLE per activated game was 121;
- median activation-to-first-bank delay was 13 turns;
- 32 mothers were still alive at game end.

This is a rare, high-output commitment. It permanently reserves one of two workers and can turn one protected mother into roughly a hundred fruit. Outcomes of activated games themselves are not causal evidence, because activation selects a difficult subset of maps.

## Activation gates tested

### Idle-only / `work_conserving()`

Only **3/54** actual activations occurred when the inner starter command was `WAIT`; **51/54** would be suppressed. On the 640 no-orchard trajectories, the exact idle-only source activated **zero times** before any replay divergence.

Therefore `require_idle_starter = true` is not a modest work-conserving refinement in the current field. It is essentially another no-orchard ablation. Since blanket removal already lost live rating, this gate is rejected as the next candidate.

### Enemy arrival before first bank

A travel-only gate would keep 29 activations and block 25. The allegedly unsafe/blocked group had better descriptive outcomes:

| Stratum | Games | Mean margin | Win rate | Catastrophes |
|---|---:|---:|---:|---:|
| enemy arrives after first bank | 29 | -52.21 | 44.8% | 9 |
| enemy can arrive before first bank | 25 | -10.20 | 60.0% | 6 |

This comparison is selection-biased, but it confirms the mechanical problem: arrival is not destruction. A high-health APPLE continues growing while under attack and can be harvested before the killing chop resolves.

### Continuous-attack kill safety

The audit simulated the earliest possible kill using enemy movement speed, chop power, tree growth during attack, and referee action order. HARVEST resolves before CHOP, and a newly planted tree cannot be chopped on its planting turn.

**All 54/54 actual APPLE activations survive mechanically through the first harvest.** No activation fails this gate. The current geometry is safe enough for APPLE, but kill safety does not identify a better subset.

## Why the mother is APPLE

The current mother is **protected and harvested**, not chopped by our bot. Once active, the starter does only:

```text
MOVE to mother
DROP carried fruit
HARVEST when ripe
WAIT otherwise
```

Other workers are prevented from occupying or targeting the mother. Therefore APPLE being hard to chop is an advantage.

The mother cell is always water-adjacent. Under that geometry:

| Property | APPLE | BANANA |
|---|---:|---:|
| effective cooldown | 2 | 4 |
| first bank after activation | travel + 11 | travel + 19 |
| mature health | 20 | 6 |
| steady bank interval | 2 turns | 4 turns |

On the 640 no-orchard trajectories, APPLE and BANANA had exactly the same 46 exact-prefix activation states. Both seeds were present in all 46. BANANA therefore unlocked no extra support.

Where both could activate, uninterrupted projected bank output averaged:

```text
APPLE:  133.15 fruit
BANANA:  64.80 fruit
Difference: +68.35 for APPLE
```

With current minimum enemy travel ETA, a continuous chop-2 attacker can kill a water BANANA before its first harvest in a representative boundary case, while APPLE survives through its first harvest and several later opportunities. Species and safety threshold are coupled.

**Conclusion:** replacing only the protected APPLE mother with BANANA is strictly the wrong use of BANANA's properties.

## A self-sustained BANANA orchard is still a valid idea

Easy chopping is useful for a **cut/replant wood plot**, not for the seed mother. A clean bounded design would use:

1. one protected BANANA mother, preferably diagonal to the tent;
2. at most one orthogonal cut/replant slot initially;
3. one explicit chopper owner;
4. harvested seed deposited or routed transactionally to that slot;
5. monotone return-to-bank commitments;
6. zero period-2 movement;
7. exact parent commands outside activation;
8. a fresh closed-loop value panel before Arena.

Earlier banana-factory work demonstrated substantial production potential but also relaxed opponent suppression. The two live banana implementations were implementation-invalid because of unbounded geography, failed collection/banking, and movement oscillation. Those failures do not close the bounded architecture, but they make the safety gates mandatory.

## Recommended next experiment

Freeze three arms on a fresh common-seed panel:

```text
C0: current APPLE orchard
C1: current APPLE orchard + opportunity-cost activation gate
C2: bounded BANANA mother + one cut/replant slot
```

For `C1`, instrument the inner selected starter task before override:

- task class and target;
- predicted cycle ETA;
- expected material and banked score;
- contested-tree or denial value;
- projected remaining APPLE harvests from the mother.

Use a mechanics-derived threshold frozen before terminal outcomes are opened. Do not fit it on these 1,280 games.

For `C2`, require mother survival, successful seed transfer, completed cut cycles, banked wood, zero opponent-favored crop leakage, and zero movement oscillation before considering terminal value.

## Data quality and limitations

- all eight Git LFS packages hash-verified;
- full deployed command parity: 696/1,280 games;
- exact deployed command prefix through turn 100: 911/1,280 games;
- later mismatches are process-dependent equal-choice MOVE/path ties;
- generated variants were interpreted only before first divergence and before any deployed-source drift;
- exact matches on initial state + opponent submission + seat: zero;
- raw replay bodies were not duplicated;
- no Arena/TestSession action was performed.

## Artifacts

- detailed 1,280-row table: `chatgpt_1/orchard-activation-opportunities-2026-08-04.csv`;
- full machine report: `chatgpt_1/orchard-activation-species-audit-2026-08-04.json`;
- corrected final machine verdict: `chatgpt_1/orchard-activation-species-audit-final-2026-08-04.json`;
- analyzer: `chatgpt_1/orchard_activation_species_audit.py`;
- exact-prefix/kill-safety patch: `chatgpt_1/patch_orchard_activation_species_audit.py`.
