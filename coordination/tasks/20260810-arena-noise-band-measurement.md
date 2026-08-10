# 20260810-arena-noise-band-measurement: measure the ladder's run-to-run noise, and separate our variance from the ladder's drift

- Status: **PROPOSED — needs an owner decision before any Arena action.** No submission is
  authorized by this record.
- Record owner: local_claude_1
- Work owner: unassigned
- Reviewer: unassigned (must not be the work owner)
- Integrator / sole Arena controller: local_claude_1
- Area: measurement infrastructure; owner ruling 2026-08-12 removing the noise-band gate
- Base commit: `origin/main` at the time of claim
- Progress lease: 15 minutes without concrete evidence; a maturing Arena run renews via pushed
  checkpoint markers
- Created UTC: 2026-08-10T04:40:00Z
- Last updated UTC: 2026-08-10T04:40:00Z

## Outcome

A defensible estimate of **σ**, the standard deviation of a settled 160-game Arena score for one
byte-identical source, with its confidence interval — and an answer to whether the observed spread
is our bot's variance, the ladder's drift, or both.

## Why this exists

The owner's 2026-08-12 ruling removed the noise-band gate on candidates:

> *"Noise of measurement is 2 and we should conduct more experiments to narrow the error band. We
> shouldn't gate candidates. This way we starve our channel which gives precious information."*

That makes measurement throughput the binding constraint instead of candidate strength, and it
makes σ the number every future promotion argument rests on.

**What is already known, and it is not nothing.** `cgauto/arena_noise_band.py` pools every source
family in the registry with repeated mature runs:

```text
4 families, 10 deployments, 6 d.o.f.
POOLED WITHIN-SOURCE SD = 1.098 score points     95% CI [0.707, 2.418]
SD of an A-minus-B difference at n=1 per arm     1.552
```

*(Corrected 2026-08-10: the first run of this tool counted 13 observation rows, three of which
were second checkpoints of a single deployment. Same run measured twice is not two samples —
their difference is within-run maturation, not re-submission noise. n 13→10, σ 0.957→1.098.)*

So the historical ±0.5–1 band was approximately right as a 1σ statement, and the integrator's
initial reading of a single 24.76/22.46 pair as evidence the band was understated was **wrong** —
2.30 is a ~1.7-SD draw, wide but unremarkable. That correction is recorded in `docs/STATE.md` §1.

**What is not known, and is the actual question.** The 13 observations are opportunistic: different
sources, different eras, different field sizes (legend-131 through legend-139), collected as a
by-product of other work. They cannot separate three things:

1. **Within-source variance** — the same bot scoring differently on re-runs.
2. **Ladder drift** — the pool strengthening or the field growing between runs.
3. **Era effects** — 137 versus 139 agents is a different denominator.

Every existing repeated pair is *blocked in time*: run A, then later run B. Blocked ordering
confounds 1 with 2 permanently, no matter how many observations are added. **Only interleaving
separates them.**

## Design constraint that makes this cheap

Measured 2026-08-12: a full 160-game mature read completes in **~2 hours** (21 games at +15 min,
127 at +1h35m, 160 at +1h55m). The "days of standing" figure in B0.3 dates from the B0.1
frozen-score regime and no longer holds; `docs/STATE.md` §3 records that weakening.

At σ ≈ 0.957, resolving an A-versus-B difference needs:

| target SE of the difference | runs per arm | total runs | sequential ladder time |
|---|---:|---:|---:|
| 1.0 | 3 | 6 | ~12 h |
| 0.5 | 10 | 20 | ~40 h |
| 0.3 | 27 | 54 | ~108 h |

## The measurement, in preference order

**Phase 1 — self-versus-self, no candidate required.** Repeatedly submit the *current resident*
`98628e98` and let each deployment mature. Any spread is pure measurement noise: same bytes, same
policy, no confound from a code difference. This is the cleanest σ obtainable and it risks nothing
— the bot being measured is the bot already live.

**Phase 2 — interleaved A/B.** Only once Phase 1 has an estimate. Alternate arms A/B/A/B rather
than running all of A then all of B, so that ladder drift enters both arms equally instead of
loading onto whichever ran later.

**Do not** run blocked A-then-B. It is the design that produced the current ambiguity, and adding
observations to it does not resolve the confound.

## Open design questions the owner or reviewer must settle

1. ~~**Does a resubmission of an identical source draw a genuinely independent sample?**~~
   **ANSWERED 2026-08-10 from committed data, no Arena action spent.** Across **10 distinct
   deployments of 4 byte-identical sources** there are **zero duplicate settled scores**
   (spreads 1.70 / 1.72 / 1.77 / 2.30). Deterministic seeding from the source hash would
   produce identical scores; it does not. Re-submission draws a genuine sample, so Phase 1
   measures something real. *This was the blocking question and it cost nothing — it should
   have been asked of the registry before it was written up as a reason to spend 8 hours.*
2. **Does re-submitting churn our standing?** B0.3's "never churn" is weakened but not repealed.
   Each cycle displaces a matured score with a cold one for ~2 hours.
3. **How many runs is the owner willing to spend?** 4 runs buys SE 1.0; 16 buys SE 0.5.
4. **Does the era denominator need normalising** when the field grows mid-measurement?

## Exclusive write set

- `cgauto/arena_noise_band.py`
- `data/analysis/arena-noise-band-2026-08/**`
- this task record

## Shared read-only paths

- `data/analysis/arena-submission-history.json` and its inputs manifest
- `cgauto/submission_history.py`, `cgauto/arena_transfer_checkpoint.py`

## Do not touch

- `rust/src/bin/yamo_orchard_live.rs` (byte-sacred `fff6669b…`)
- `cgauto/submissions/**` (frozen artifacts)
- `data/raw/games/`, the 05:17 cron, sealed ranges, the official holdout

## Deliverables

- σ with a confidence interval, and the runs-per-arm table recomputed from it
- an explicit statement of what the design can and cannot separate
- every observation appended to the submission registry via its manifest, not by hand

## Acceptance checks

- `python3 cgauto/submission_history.py validate` → all observations validate
- `python3 cgauto/arena_noise_band.py` → recomputes σ including the new runs
- each new run has a submission-scoped terminal checkpoint at ≥160 finished games,
  `identity_clean=True`, `signals=0`

## Arena authority

Read-only platform access: allowed. **Platform mutation: this record authorizes none.** Phase 1 is
a repeated-submission programme and the owner's standing authorization covers submitting
candidates that passed frozen gates — not a deliberate re-submission campaign against the live
slot. That is a separate owner decision, and question 1 above should be answered first regardless.

## Why this is worth an owner decision rather than quiet execution

Every closed experiment in `docs/BACKLOG.md` was judged against a gate expressed in score points —
±0.5, ≥+1.0, ≥+2. If σ is ~0.96, a single mature read cannot resolve any of those thresholds, and
several historical accept/reject calls were made on differences smaller than the noise. This task
does not reopen them. It determines whether future ones can be made at all.
