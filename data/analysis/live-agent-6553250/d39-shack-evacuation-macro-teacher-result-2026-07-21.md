# D39 shack-evacuation TRAIN-deficit macro teacher — result (2026-07-21)

## Verdict

**Mechanism validated; initializer rejected.** D39 fixes the physical TRAIN blocker and passes 11
of 13 frozen gates, but its mean margin gains are **+38.230 versus random** and **+42.277 versus the
same-seed D38 ablation**, below both +50 floors. Behavior learning remains sealed; no model,
candidate, TestSession, submission, or Arena action is authorized.

## Accepted panel and integrity

Each accepted arm contains the complete 16-seed x 2-seat x 8-opponent = **256-cell** grid for
official seeds 9,650,000--9,650,015. All rows have zero missing/duplicate keys, policy errors,
margin/return identity errors, illegal direct commands, provenance failures, worker-cap errors,
empty episodes, action-count errors, TRAIN-relevant deposit-prediction failures, or runner loops.
Evacuation replicas A and B are byte-identical at
`b17a3af726eb4d2db000cdd1d8209dccc26334f4a68cc003963a09dae82e3ce0`.

An initial concurrent launch allowed old binaries to start while the new release was compiling.
Those files were invalidated and overwritten; all four accepted hashes below come from a clean
post-build rerun.

## Outcome

| metric | evacuation | D38 ablation | random |
|---|---:|---:|---:|
| mean own score | 102.297 | 67.938 | 64.637 |
| mean opponent score | 184.582 | 192.500 | 185.152 |
| mean margin | -82.285 | -124.563 | -120.516 |
| worker-two rate | **98.44%** | 54.69% | 54.30% |
| worker-three rate | **35.94%** | 22.27% | 3.13% |
| own renewable-crop rate | 91.02% | 88.28% | 94.14% |
| median non-idle jobs | 23 | 18 | 21 |
| catastrophes | 119 | 147 | 130 |
| negative-margin mass | 27,963 | 35,977 | 31,811 |

D39 adds +34.359 own score and removes 7.918 opponent score versus the deficit ablation. Versus
random it adds +37.660 own score and removes only 0.570 opponent score. It improves 105/256 paired
cells versus the ablation (86 tie, 65 regress) and 114/256 versus random (one tie, 141 regress).

All family gates pass. Paired margin versus random is positive in seven of eight families:

- `legend_balanced` +61.156;
- `compact_gold` +57.313;
- `script_boss` +55.469;
- `mybot` +48.719;
- `norx_native_three` +33.656;
- `silver_boss` +27.469;
- `gold_adaptive` +26.719; and
- `resident` -4.656.

## Mechanism diagnosis

### 1. Spawn evacuation is causally useful

Worker two rises by **43.75 percentage points** over the same-seed D38 ablation and clears the 90%
absolute gate. Worker three rises by 13.67 points and clears the 15% gate. The change uses the same
actions and game mechanics; it only distinguishes physical shack occupancy from resource deficit.

### 2. Margin value arrives only when the funding ladder reaches worker three

The paired transition decomposition isolates the remaining problem:

| ablation workers -> D39 workers | cells | mean paired margin change |
|---|---:|---:|
| 1 -> 3 | 40 | **+295.50** |
| 1 -> 2 | 72 | -1.33 |
| 2 -> 2 | 83 | +0.77 |
| 3 -> 3 | 52 | -1.25 |
| 3 -> 2 | 5 | **-180.80** |
| 1 -> 1 | 4 | +1.00 |

Evacuating and training only worker two is not enough. D39's 160 two-worker episodes average
**-165.77 margin**, 218.59 idle jobs, and only 19.09 non-idle jobs. Its 92 three-worker episodes
average **+62.09 margin**, only 14.23 idle jobs, and 83.79 non-idle jobs. The split is
selection-biased, but the paired ablation transitions show that the large causal gain is confined
to trajectories that complete the third-worker funding ladder.

### 3. Exact-deficit waiting remains the bottleneck

D39 removes 11,250 idle selections versus the ablation, yet still makes **37,096** idle selections
versus 920 under random. After worker two, exact missing or reserved currency frequently leaves no
immediately deficit-reducing candidate; the policy then waits instead of maintaining renewable
supply or doing productive work. This both stalls worker three and leaves already-trained
two-worker games weaker than random.

TRAIN-relevant prediction telemetry is now clean in all arms. D38's uncertain future wood no longer
invalidates a reservation system whose bill has no wood slot.

## Frozen gates

Passed:

- all three-arm integrity checks and byte-identical repeat;
- worker-two rate >=90% and improvement >=40 percentage points;
- worker-three rate >=15%;
- crop rate and median non-idle activity;
- at least six nonnegative opponent families; and
- no family below -10.

Failed:

- paired margin advantage versus random >=+50 (observed +38.230); and
- paired margin advantage versus D38 ablation >=+50 (observed +42.277).

## Next hypothesis

D40 should keep D39's evacuation and exact positive-deficit priority, but replace the remaining
`IDLE_ONE_TURN` fallback with the frozen D37 rate/provenance ordering. This lexicographic hybrid is
work-conserving: an immediately fundable job always wins; only otherwise does a worker renew,
produce, or suppress instead of waiting. It must be compared on fresh seeds against D39 and random,
with special gates on worker-three conversion and two-worker margin.

## Reproducibility

- protocol: `c5b4637692caed44099d0adf1ea4c5d7cb7f5fb52b69d4f6d0e15043a8e54131`
- macro environment: `912a8b9ed103badf471b90ef35f5ad83bd8a8bb49621ad8c8bf99e0b491ed851`
- panel runner: `69a1c2adbff538e14aa102dc6daecaa70c04f464f5a5f19a2c53d8256d17d153`
- analyzer: `22089fac604f233cceb66180cfc2c1c6963cc68e600cca858276ae3edda6cb83`
- analyzer tests: `f70ab0da137014e953b6a85ee984e5870a79bcc87ec7ec2dc39e5a0a95c89ba2`
- deficit ablation: `18c42b89d7c48c5f4a97ccf22f6fd8682a32598889c5772a617d1b3a033f4714`
- random control: `582e803179a7acf18e984637c974aa936e89de1e682b054eb86084440015b08a`
- analyzer JSON: `cccf74e2495a2fd2fe8023c3229b4fe511f3568f9afedfa564081acbfe88ba56`

Focused verification: 11 Rust macro tests and five D39 analyzer tests pass. Existing unrelated
compiler warnings remain unchanged.
