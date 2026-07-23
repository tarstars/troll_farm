# Arena retry and live-source slimming — 2026-07-17

## Arena verdict

**PROMOTE pre-seed + secure-orchard coverage.**  The same-code reset control passed under
continuous matchmaking, and the frozen candidate later held rank 23/104 Legend at 24.1 on two
authoritative reads.  Against the fresh 20.8-21.1 control bracket, the measured delta is
**+3.0 to +3.3**, above the +1.0 single-convergence promotion threshold.

The promoted policy now runs from its behavior-identical slim encoding:

- source: `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`;
- SHA-256: `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`;
- submission: `41005161`;
- agent: `6557204`;
- source size: 62,725 bytes.

The frozen full-size strategy reference remains submission `41004799`, agent `6556873`, source
SHA-256 `da53b0f66a0224bf9c8d5796d69905a9bebcf1e71ee97e4b65e72a2fdea046e9`, and 90,547 bytes.
`cgauto/api_submit.py` now defaults to the arena-validated slim artifact.  This later A/A changed
only source packaging; it did not change policy behavior.

## Same-code A/A capacity control

The restored exact source was rank 56/104 at 21.1 before reset.  Submission `41004754` used the
same frozen checksum and landed as agent `6556775`.  It received games continuously and returned
to 21.1 by 08:21:19 MSK; a confirming read one minute later was 20.8.  There were 67 listed
battles by the 21.1 read.

| Time (MSK) | Arena-room score | Rank | Note |
|---|---:|---:|---|
| 08:05:19 | 21.1 | 56 | pre-reset exact-source bracket, agent `6555394` |
| 08:07:23 | 17.2 | 91 | reset landed as agent `6556775` |
| 08:10:42 | 19.5 | 72 | normal continuous placement |
| 08:12:42 | 20.2 | 66 | 35 listed battles shortly afterward |
| 08:15:24 | 17.7 | 88 | ordinary noisy dip, games still arriving |
| 08:18:21 | 19.5 | 72 | recovery resumes |
| 08:20:21 | 20.6 | 62 | near the established bracket |
| 08:21:19 | 21.1 | 57 | A/A reconverged; 67 listed battles |
| 08:22:22 | 20.8 | 61 | confirming control read |

This is materially different from the degraded 2026-07-16 reset, which was only 16.1 at +20
minutes and received games in uneven waves.

## Candidate trajectory

Submission `41004799` landed as agent `6556873`.  Early placement closely tracked the A/A
control, then the candidate moved into a stronger field band.

| Time (MSK) | Arena-room score | Rank | Listed battles / note |
|---|---:|---:|---|
| 08:23:37 | 0.0 | 102 | cold landing |
| 08:24:41 | 14.3 | 102 | 16 battles; global endpoint already 16.5 |
| 08:25:54 | 16.4 | 98 | placement |
| 08:28:38 | 19.6 | 71 | 31 battles |
| 08:32:37 | 21.6 | 51 | above control |
| 08:34:42 | 21.1 | 57 | 56 battles |
| 08:35:44 | 21.2 | 57 | near-flat early read |
| 10:04:56 | 24.1 | 23 | decisive late read; 161 battles listed soon afterward |
| 10:05:14 | 24.1 | 23 | first stable confirmation |
| 10:07:20 | 24.1 | 23 | second stable confirmation |
| 10:17:58 | 24.4 | 20 | closing read; candidate continued climbing |

The nominal +20/+35/+50 reads were not recorded while the local source audit was running; they
must not be reconstructed from interpolation.  The decisive read is therefore later than the
normal +50 policy cadence, but remains inside the five-hour bracket horizon, uses the same agent,
follows 161 battles, and exceeds the promotion threshold by roughly two additional noise bands.
The candidate was left live throughout, so there is no survivor or restore selection bias.

The latest 30 parsed battles at confirmation were 17 wins / 13 losses against opponents around
the same Legend rating band.  Raw average margin was -5, which is consistent with the agent
having climbed into stronger matchmaking; the authoritative arena-room rating is the verdict
metric.

The closing read after the verdict was rank 20/104 at 24.4, or +3.3 to +3.6 versus the fresh
control band.  Promotion does not depend on that later improvement; the two 24.1 reads already
cleared the frozen threshold.

## Source-size audit

The recovered artifacts were syntax-compacted but not tree-shaken.  Their crate-level
`allow(dead_code, unused_imports)` hid simulator serializers, unused state helpers, parked policy
constructors, fixed-off sparse-farming and tree-target experiments, and a complete standalone
`MoisanBot` policy that was never constructed.  Yamo only uses the remaining `MoisanBot` methods
as shared static helpers.

`cgauto/slim_live_source.py` now performs locked, uniqueness-checked removals and fails closed if
the parent source changes.  It produces these local artifacts:

| Parent | Parent bytes | Slim artifact | Slim bytes | Freed | Headroom |
|---|---:|---|---:|---:|---:|
| exact recovered live | 90,133 | `agent-6553250-yamo-orchard-live-slim.min.rs` | 62,311 | 27,822 | 37,689 |
| promoted stack | 90,547 | `candidate-agent6553250-preseed-orchard-coverage-slim.min.rs` | 62,725 | 27,822 | 37,275 |

Slim checksums:

- exact live: `025468a87d1807a6027f8af4c1662dfc89beb68b9fe0ef9ed1047fadf39c218f`;
- promoted stack: `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`.

Both final slim artifacts compile standalone with `-D warnings`.  Final-pass behavioral gates:

- exact live: 50 fresh dynamic both-seat games / 9,400 compared turns, byte-identical commands;
- promoted stack: 50 fresh dynamic both-seat games / 9,812 compared turns, byte-identical commands;
- each artifact: all 26 historical streams / 6,145 compared turns, byte-identical commands;
- SHA-256 sidecars and focused slimming tests pass.

The promoted-stack slim artifact was subsequently submitted in an explicit same-policy arena
A/A.  It passed the frozen rating band and is now the recovery default.  The exact-live slim
artifact remains local-only.

## Behavior-identical slim arena A/A

The full-size promoted source was frozen immediately before the packaging reset at rank 21/104
Legend and 24.5.  Submission `41005161` used the 62,725-byte slim checksum above and landed as
agent `6557204`.  Local evidence had already established byte-identical commands in both seats
over 100 fresh dynamic games plus all 26 historical streams; the arena test therefore measured
deployment/packaging safety, not strategic uplift.

| Time (MSK) | Elapsed | Arena-room score | Rank | Finished battles / note |
|---|---:|---:|---:|---|
| 10:41:42 | bracket | 24.5 | 21 | full-size agent `6556873` |
| 10:43:01 | +1m | 9.6 | 102 | slim agent `6557204` landed |
| 10:44:03 | +2m | 14.4 | 102 | 14 battles listed |
| 10:46:38 | +5m | 17.2 | 90 | ordinary placement climb |
| 10:47:38 | +6m | 19.1 | 76 | near the full-size +6m reference, 19.6 |
| 10:50:05 | +8m | 21.3 | 53 | ahead of the full-size early curve |
| 10:53:37 | +12m | 23.6 | 29 | first near-bracket read |
| 11:02:05 | +20m | 23.3 | 34 | 51/80 wins in the first 80 parsed games |
| 11:17:22 | +35m | 23.3 | 34 | 138 finished battles shortly afterward |
| 11:23:46 | +42m | 24.0 | 25 | late convergence begins |
| 11:24:34 | +43m | 24.2 | 24 | enters the noise band |
| 11:32:28 | +50m | 24.2 | 24 | formal verdict read |
| 11:34:07 | +52m | 24.2 | 24 | sixth consecutive 24.2 read; 160 finished battles |

The +20 and +35 reads were each -1.2 below the frozen bracket but came before a comparable
stable sample.  The predeclared +50 verdict was 24.2, only -0.3 from 24.5 and therefore inside
the `|delta| < 0.5` noise band.  Six consecutive closing reads were identical, the final sample
was comparable to the full-size agent's 167 battles, and there was no compile, runtime, or
matchmaking failure.  Verdict: **KEEP SLIM / packaging A/A passed**.  The 27,822-byte reduction
and 37,275 bytes of submission headroom are now the development baseline.

## Consequence for residual search

The earlier residual prototype wraps local GoldElite, not the real Yamo/Orchard resident, and
must not be submitted as a purported live-policy improvement.  Before slimming, the exact
referee engine alone (23,257 minified bytes) could not fit in the live artifact's 9,867-byte
headroom.  The 62,725-byte promoted-stack slim form can hold that engine and still leave about
14 KB for a specialized controller.  The full 23,210-byte local residual controller still does
not fit unchanged.

The next search iteration should therefore port only a compact candidate generator, evaluator,
and commitment guard around the promoted stack, then repeat command-neutrality, untouched
holdout, timing, and same-code arena controls.  It must not swap in GoldElite as the fallback.
