# Curriculum Level 5 bounded repeated-pressure D10 result — 2026-07-20

## Verdict

**Stop D10 at the fresh control gate.**  On exact unopened seeds 5,000--5,499, teacher/random are
435/500 = **87.00%** and 0/500.  Repeated pressure is active and economically well formed, but the
teacher misses six frozen robustness floors.  The fixed actor remains unopened; no PPO, YT write,
prospective evaluation, checkpoint change, deployment, or Arena action occurred.

## Frozen gate evaluation

| Measure | Teacher | Requirement | Verdict |
|---|---:|---:|---|
| Overall success | **87.00%** | >=90% | **fail** |
| Nontrivial success | **86.28%** | >=90% | **fail** |
| Worst recipe | **81.97%** | >=85% | **fail** |
| Worst height | **80.95%** | >=88% | **fail** |
| Terminal player crop | **87.20%** | >=90% | **fail** |
| Renewable player harvest | **88.60%** | >=95% | **fail** |
| Illegal selections / earliest success | **0 / turn 180** | 0 / >=180 | pass |
| First / third-worker training | **100% / 98.60%** | >=98% / >=85% | pass |
| Fresh receipt before each training event | **100% / 100%** | 100% / 100% | pass |
| Standard-chopper / feeder productivity | **100% / 94.20%** | >=98% / >=80% | pass |
| Rival crop creation / own harvest | **100% / 90.20%** | >=95% / >=80% | pass |
| At least one / two / three destructions | **99.80% / 98.60% / 90.80%** | >=95% / >=90% / >=80% | pass |
| Maximum destructions / workers | **3 / 3** | <=3 / <=3 | pass |
| Random legal | **0/500** | <=5% | pass |

The result is decisive rather than marginal: the overall confidence interval is not the issue,
because terminal crop and renewable-harvest mechanisms independently miss their floors by 2.8 and
6.4 percentage points, and every height is below the 88% requirement except heights 10 and 11.

## Post-decision failure decomposition

All 65 failures reach the 240-turn timeout.  Of them:

- 64/65 end without the tracked player crop;
- 57/65 record no renewable player harvest;
- 32/65 also remain short of the required score gain; and
- no successful episode ends without its crop.

Destruction-count stratification initially suggested censoring around the final attack:

| Confirmed destructions | Episodes | Successes | Success rate | Terminal crop rate |
|---:|---:|---:|---:|---:|
| 0 | 1 | 1 | 100% | 100% |
| 1 | 6 | 6 | 100% | 100% |
| 2 | 39 | 10 | **25.64%** | **25.64%** |
| 3 | 454 | 418 | **92.07%** | **92.29%** |

The 29 failures stopped at two destructions; another 36 completed the third destruction but had
not restored the terminal crop.  This explains why opponent funding, crop production, harvest, and
all three productive roles pass comfortably while the player control fails, but count alone does
not identify the cause.

A post-decision consumed-seed screen then forced pressure to stop at turns 120, 140, 160, 180, 200,
and 220.  Teacher success remained 86.60--87.20%; even the turn-120 cutoff retained 81.40%
three-destruction activation but gained only 0.6 percentage points.  The temporal-window hypothesis
is therefore rejected.  The actual code-path hole is seed reacquisition: after carried and home
banana stocks are empty, the crop-less teacher moves home forever instead of harvesting a reachable
banana source.

## Conclusions at different abstraction levels

### Causal mechanism

Three recoveries are feasible: 418 episodes both complete all three destructions and succeed.  The
failure is not that a third attack is intrinsically impossible or generally late.  Repeated loss
exhausts finite initial seed stock on a subset of maps, and the reference teacher lacks a natural
seed-reacquisition branch.

### Curriculum design

The D10 task can remain unchanged.  Control validity first requires an expert that can reacquire a
real seed from the board rather than treating empty home inventory as an absorbing state.  This is
a teacher-label correction, not a resource gift or easier opponent.

### Actor and learning

Because the reference teacher fails, D10 provides no valid evidence about the fixed neural actor.
Opening actor or PPO would turn an environment-design defect into an apparent learning deficit.
The conditional YT benchmark is therefore not triggered.

### Strategic relevance

Repeated crop loss remains a useful abstraction for Arena resilience.  The newly exposed behavior
is strategically relevant: resilient controllers must rebuild supply chains after inventory
depletion, not merely repeat the last placement command.

## Prioritized next hypotheses

1. **Expert seed reacquisition:** preserve the exact D10 task and add one teacher-only fallback to
   harvest a reachable banana when crop, carried seed, and home seed inventory are all absent.
2. **Seed-reserve planning:** if reacquisition is too slow, test whether the expert should bank a
   real reserve before planting.  This changes more behavior and is therefore second.
3. **Recovery-aware cooldown:** space attacks with productive opponent work only if a stronger
   expert still cannot establish task feasibility.
4. **Broader strategic scheduler:** condition denial on value versus natural production after the
   isolated recurrent-recovery skill is measurable.

Freeze D11 around the smallest expert-only reacquisition rule, prove external-action task parity
with D10, and use a new unopened development interval.  Do not loosen D10 or replay its actor.

## Reproducibility anchors

- D10 protocol: `c52483727f2eee6988ba083a83a50bb8254bbdcab32af8513fa17b4bef4349a4`;
- readiness document: `1a7362b971b49e5e3e4713bf7217a39d70e43ef3d27347c8aa7c3fd6925f383c`;
- post-decision deadline screen:
  `de432830fb16561bb5ab01b176c940133833be6c0aec5b05b2f6f715889dcd58`;
- fresh teacher: `9e1c1bd476ab479bfcecad26ee43e8c655d371264dea3718b0a6003a4bc263f2`;
- fresh random: `0ea4ea71434d06cb5a836edbafcda493f2ab7ec70ce50a8d5dd0d8e149aa1b45`;
- frozen Rust source: `e0914fe1fbbe555b103730134e43e6a01901bb93c51aef76125a5ee0e5634696`;
- frozen release library: `afd1f4fbb405a66f2a260d25181f0025ecd22a584bcb2b648198e0f290c22f21`;
  and
- accepted checkpoint, unchanged:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`.
