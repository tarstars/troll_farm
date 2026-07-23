# Portfolio prospective execution — 2026-07-16

## Decision

Keep exact live resident. Neither portfolio is promotion-ready and no arena write is justified.

- The banana-5 stack/live portfolio passed its frozen deterministic research gate but failed its
  worst-decile promotion rule.
- Repeated randomized-motion evaluation found no stochastic support for the stack.
- Component diagnosis assigned every deterministic bottom-decile loss to pre-seeding; secure
  orchard was sparse and seed-balanced non-losing.
- A new banana-5 geometry/live portfolio was then built and evaluated on a second untouched seed
  block. It went 5/204/0 W/T/L and passed both tail checks, but formally failed its frozen research
  gate because five-percent trimming removed all five rare wins and yielded exactly zero.

The useful mechanism is exclusive secure-orchard geometry, but its activation is too sparse for
the predeclared robust-central-tendency rule. The useful next research target is increased safe
geometry coverage, not another pre-seed or banana-threshold fit.

## Experiment matrix

| Stage | Independent unit | Games | Main result | Frozen decision |
|---|---:|---:|---|---|
| Stack deterministic prospective gate | 300 new seeds | 6,000 | +1.934 low-branch mean; +0.492 trimmed; CI lower +0.497; worst decile -4.952 | research pass, no promotion |
| Repeated randomized `motion` | 300 seeds, five launches | 6,000 | low -0.070; null -0.030; adjusted -0.039 | no stochastic support |
| Component diagnosis | 208 selected seeds | 6,240 | all 21 tail losses equal pre-seed losses; geometry 11/197/0 | remove pre-seed |
| Geometry deterministic prospective gate | 300 further-new seeds | 8,090 | 5/204/0; +1.474; CI lower +0.103; trim 0 | formal reject |

## 1. Frozen stack gate

The first prospective block used seeds 10,000..10,299, five deterministic opponents, both seats,
and no refitting. The branch split was 208 low-banana and 92 high-banana seeds. The high branch
matched live in 460/460 cells. Every research rule passed on the low branch:

- +1.934 mean and +0.492 five-percent-trimmed mean;
- +1.427 mean after removing the largest result;
- 96 wins / 40 ties / 72 losses;
- positive means from +1.322 to +2.647 against every opponent;
- normal 95% interval [+0.497,+3.370].

The -4.952 worst-decile mean failed the separately frozen promotion rule. The stack remained a
research candidate only.

## 2. Randomized-motion robustness

The historical `motion` source uses process-randomized Rust hash iteration, so five fresh
launches were averaged within each seed/policy. The high-banana exact-live branch supplied an
empirical launch-noise null.

Low-banana mean was -0.070 versus -0.030 for the high null. The adjusted difference was -0.039,
95% interval [-2.343,+2.265]. Low trimmed mean was -0.587, mean without the largest result was
-0.463, and wins did not exceed losses (95/12/101). This provides no evidence that the stack
generalizes to motion.

## 3. Causal component attribution

Pre-seed, secure-orchard, and the original stack parent were run on every activated first-gate
map/opponent. The parent matched the packaged stack in 1,040/1,040 cells. Component effects were
exactly additive in 1,023/1,040 cells; mean interaction was only +0.066.

| Component | Mean | Trimmed | W/T/L seeds | Worst decile | Mean without max |
|---|---:|---:|---:|---:|---:|
| pre-seed | +0.114 | +0.138 | 89/45/74 | -5.038 | +0.070 |
| secure orchard | +1.753 | +0.028 | 11/197/0 | 0.000 | +1.314 |
| interaction | +0.066 | 0.000 | 5/201/2 | -0.176 | +0.009 |
| stack | +1.934 | +0.492 | 96/40/72 | -4.952 | +1.427 |

On the 21 stack bottom-decile seeds, stack and pre-seed deltas are identically -4.952 mean;
geometry and interaction are exactly zero. This is much stronger than correlation: within this
diagnostic matrix, pre-seeding causes the complete deterministic tail while geometry does not
participate.

## 4. Second-iteration geometry portfolio

The pre-seed code was removed. The new single-source portfolio selects broader secure-orchard
geometry only when initial banana fruit is at most five and exact live otherwise:

`candidate-agent6553250-banana5-geometry-portfolio.min.rs`, 90,657 bytes,
SHA-256 `781f35a07cd31f5b344381c0d7e1174f0e655e8076bb3084a4d5b115b5879afe`.

The second frozen block used seeds 10,300..10,599: 209 low and 91 high. Reference equivalence was
1,045/1,045 for low -> geometry and 455/455 for high -> live. On low seeds it scored +1.474 mean,
+1.028 without its largest result, 5/204/0 W/T/L, interval [+0.103,+2.846], worst decile 0, and
positive opponent means from +0.940 to +1.854.

Only five seed-level deltas were nonzero. Five-percent trimming removes ten values from each tail,
so it removes every win and produces 0. The frozen research rule said strictly positive; the
candidate is formally rejected. Its favorable tail statistics cannot be used to waive a rule
after outcomes are known.

## Evaluation and CPU architecture

The original eight-thread evaluator underused the 20-core host because most runtime is the Python
referee loop and the GIL serializes Python bytecode. The prospective runners use
`ProcessPoolExecutor`; the first stack gate resumed from eight to 16 processes after 450 cells,
and all later matrices used 16. Checkpoints are written every 50 cells. Worker count is explicitly
excluded from outcome protocol equality; sources, hashes, seeds, opponents, repetitions, seats,
and gates remain fixed.

## Next research gate

Do not refit another selector on either consumed prospective block. If work continues, alter the
exclusive-geometry mechanism itself so it activates on materially more maps while preserving its
non-losing profile. Screen boundary variants only as discovery, freeze exactly one source, and use
seeds starting at 10,600 for the next prospective result.

A future sparse-mechanism protocol should declare an activation minimum and sign/tail rules before
outcomes. It may use an activation-conditional robust summary; it must not retroactively promote
the rejected geometry artifact under a changed gate. Arena work remains separately blocked by the
degraded same-code A/A control.

## Artifacts

- `portfolio-prospective-gate-2026-07-16.json`
- `portfolio-motion-followup-2026-07-16.json`
- `portfolio-component-decomposition-2026-07-16.json`
- `portfolio-geometry-prospective-gate-2026-07-16.json`
- `docs/portfolio-prospective-gate-2026-07-16.md`
- `docs/portfolio-motion-followup-2026-07-16.md`
- `docs/portfolio-geometry-prospective-gate-2026-07-16.md`

No external write or arena submission occurred in this execution.

## Validation

- Python: 246 tests passed.
- Rust: full `cargo test` passed, including the long oracle size-budget test; only existing
  warnings and intentionally ignored tests remain.
- Both portfolio SHA-256 files verify; the geometry portfolio compiles with optimized Rust.
- All four result JSON files parse and `git diff --check` is clean.
