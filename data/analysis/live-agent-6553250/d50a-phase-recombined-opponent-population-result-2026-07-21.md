# D50a phase-recombined opponent population — result (2026-07-21)

## Verdict

**Reject fixed phase recombination, but retain it as evidence that opponent-population support is a
productive direction.** The 120-policy population passes every integrity and activation gate. It
also clears the absolute and incremental overall/catastrophic coverage gates. It fails the frozen
worker-rich and rich-immediate conjunctions: confirmation reaches 11/28 worker-rich macro games
instead of 12/28, 3/9 rich-immediate macro games instead of 4/9, and 0/9 rich full games instead of
at least one.

This is consumed-map opponent-domain reconstruction only. No policy was optimized against these
models, no fresh map or platform evidence was exposed, and no candidate or resident conclusion
follows.

## Integrity and activation

- Both 160 x 120 matrices contain 19,200 unique complete cells and are byte-identical.
- All eight current-substrate anchors reproduce their regenerated catalog rows exactly.
- Every switched policy preserves its early component's exact first command.
- 15,665/17,920 switch cells (87.42%) differ from the early anchor in their complete checkpoint /
  terminal signature.
- 108/112 switch policies activate on at least 16/160 maps.
- The two full runs used about 19 effective CPU cores and completed in 4:44 and 4:26 wall time.

An outcome-blind pre-analysis check found deterministic drift between 187/1,280 current anchors
and their July 19 rows. D50 A/B was exact, so the five legacy catalogs were regenerated under the
same current runner before any support result was read. The amendment preserved every absolute
gate and added the equivalent incremental gates. Current anchors then matched 1,280/1,280.

The analyzer's first direct-script invocation also stopped at import time before loading result
data. Adding the repository root to `sys.path` repaired only invocation; all tests passed before
the result was produced.

## Confirmation support

| Cohort | Games | Current legacy macro/full | Augmented macro/full | Increment | Frozen requirement | Result |
|---|---:|---:|---:|---:|---:|:---:|
| Overall | 80 | 50 / 32 | **56 / 41** | +6 / +9 | >=56 / >=36 and >=+5 / >=+3 | pass |
| Catastrophic | 19 | 4 / 2 | **7 / 4** | +3 / +2 | macro >=7 and >=+3 | pass |
| Worker-rich | 28 | 8 / 3 | **11 / 4** | +3 / +1 | macro >=12 and >=+4 | **fail** |
| Rich immediate | 9 | 2 / 0 | **3 / 0** | +1 / 0 | >=4 / >=1 and >=+2 / >=+1 | **fail** |

Six previously uncovered confirmation games gain macro support. Three are catastrophic; three are
worker-rich; one (`Bondo416`, game 896285526) is both catastrophic and rich-immediate and is
covered only by `farm3 -> v2_hp2_late` at turn 100. The population also turns nine additional
legacy macro-only games into full support, explaining the strong +9 full-coverage increment.

Nearest normalized macro distance improves in 40/80 confirmation games:

| Cohort | Legacy mean | Augmented mean | Improved games |
|---|---:|---:|---:|
| Overall | 0.5619 | **0.5154** | 40/80 |
| Catastrophic | 0.8865 | **0.8242** | 8/19 |
| Worker-rich | 0.8155 | **0.7637** | 16/28 |
| Rich immediate | 0.8997 | **0.8358** | 5/9 |

The improvement transfers directionally from discovery: overall macro/full rises 48/35 to 55/43,
but discovery catastrophic support is unchanged and rich support rises only 1/0 to 2/0.

## Multilevel interpretation

- **Population:** recombination adds real, nonredundant support. It is the first reconstructed
  opponent family in this line to hit the overall and catastrophic increments rather than merely
  reduce mean distance.
- **Phase:** a fixed turn boundary is too coarse. The same early/late pair can cover one map and
  miss another because funding completion, renewable stock, and workforce state occur at different
  turns.
- **Opening:** no newly covered rich game also matches the coarse opening. The components contain
  field-supported openings, but their compatible late continuations do not land in the rich macro
  corridor under either fixed cut.
- **Critical tail:** the one-game miss in worker-rich support and one-game incremental miss in rich
  macro support make this a near miss numerically, but the 0/9 rich-full result is structural and
  binding. Widening cut values after observation would be post-result parameter tuning.
- **Research program:** opponent-domain reconstruction is not the dead branch; complete
  hand-written policies and fixed phase clocks are. The next representation should switch or
  allocate roles from observable funding/workforce/supply history inside the scheduler.

## Gate result

All five mechanical gates, no-loss, both overall gates, and both catastrophic gates pass. Six
worker-rich/rich absolute and incremental gates fail. Formal conjunction: **fail**.

Do not add cut 125/175, select the six successful phase policies as a training league, or relax the
rich-full requirement. A new protocol may reuse the eight semantic components only behind
state/history triggers or a procedural job scheduler, and must distinguish calibration from later
fresh policy evidence.

## Evidence

- protocol SHA-256:
  `d04d2b1621d1ea933bbc07b7f3fc5b33b33d0d0be6282d82cc77178d5b583608`;
- current-substrate amendment SHA-256:
  `dd117c80446f4e613b3f1daa35897445ded1b13dcd48ed6b913bbbfcbb0aa536`;
- frozen manifest SHA-256:
  `0fa8c83d345e300983a4d59c92be0ba73d342d324fcdb4c0dc7d338af1e2e9a3`;
- phase A/B SHA-256:
  `8c5c40c11cd7a3d28510be9b57e5f850b72c85ef154513a4fc57fd8b752a8598`;
- result JSON SHA-256:
  `04b8c34988a940a0dd4e051d92e754ad4c8ecaa9d370bdd75b54c210df244349`;
- runner SHA-256:
  `03f640c48b268c4d49d36503dce2cdf7c32ffbfe0775df6d5421641c27ed1b8e`;
- analyzer SHA-256:
  `035fe188256e23fa1421070ff7d20f28f4f679b591a65c6f35e22ab504ca7a5b`;
- focused verification: 12 Rust runner tests and three Python analyzer tests pass.
