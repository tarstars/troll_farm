# 20260810-arena-noise-band-measurement: measure the ladder's run-to-run noise, and separate our variance from the ladder's drift

- Status: **AUTHORIZED / IN PROGRESS — owner decision 2026-08-12: Phase 1, 4 runs ≈ 8 h.**
  Questions 2 and 3 are thereby answered (churn accepted; budget four runs); question 1
  was answered 2026-08-10; question 4 (era denominator) stays open for the analysis.
- Record owner: local_claude_1
- Work owner: local_claude_1 (claimed 2026-08-12; sole Arena controller). **Remainder
  delegated 2026-08-12T20:14Z to claude_1 on the VM under a bounded lease** (owner
  decision — notebook sleep killed the read-timers; lease: run-3 terminal, run-4 submit,
  checkpoints, registry, σ recompute, final handoff; authority reverts on handoff;
  message `20260812T201400Z…-vm-lease-policy.md`)
- Reviewer: requested codex_1 2026-08-12 (must not be the work owner; ack pending)
- Integrator / sole Arena controller: local_claude_1
- Area: measurement infrastructure; owner ruling 2026-08-12 removing the noise-band gate
- Base commit: `origin/main` at the time of claim
- Progress lease: 15 minutes without concrete evidence; a maturing Arena run renews via pushed
  checkpoint markers
- Created UTC: 2026-08-10T04:40:00Z
- Last updated UTC: 2026-08-12T06:16:00Z

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

So the historical ±0.5–1 band was understated as a 1σ figure, but only modestly. The integrator's
initial reading of a single 24.76/22.46 pair as proof the band was badly wrong was still an
over-read: 2.30 is a ~1.5-SD draw, wide but unremarkable. Both corrections are in `docs/STATE.md` §1.

**What is not known, and is the actual question.** The 10 deployments are opportunistic: different
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

At σ ≈ 1.098, resolving an A-versus-B difference needs:

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
3. **How many runs is the owner willing to spend?** 6 runs buys SE 1.0; 20 buys SE 0.5.
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

Read-only platform access: allowed. **Platform mutation: the owner decision of 2026-08-12
authorizes exactly four Phase-1 re-submissions of the resident source `98628e98…`,
serialized through the sole Arena controller.** Question 1 was answered first, as this
record required (2026-08-10: zero duplicate settled scores across 10 deployments of 4
byte-identical sources). Nothing beyond those four runs — in particular no Phase 2
interleaved A/B — is authorized by this record.

## Why this is worth an owner decision rather than quiet execution

Every closed experiment in `docs/BACKLOG.md` was judged against a gate expressed in score points —
±0.5, ≥+1.0, ≥+2. At σ ≈ 1.10 a single mature read cannot resolve any of those thresholds — the
difference SD at one run per arm is 1.55 — and several historical accept/reject calls were made on
differences smaller than the noise. This task
does not reopen them. It determines whether future ones can be made at all.

## Phase 1 execution log (authorized 2026-08-12, four runs)

Run 1 pre-mutation baseline, 2026-08-12T06:25Z: live source recovered exact
`98628e98…`, 75,634 B (`recover_live_source.py`); standing 22.4 / rank 37/147, agent
`6604529` — field 139 → 147 since the terminal read, drift 35 → 37. Top-3: delineate
30.42 / norxondor_gorgonax 29.93 / MSz 28.14. `api_submit.py` argument-less default
already removed on trunk (STATE §1 follow-up discharged).

| run | UTC submit | submission / agent | initial health | terminal 160/160 |
|---|---|---|---|---|
| 1 | 2026-08-12T06:27Z | **41125196 / agent 6610399** (`accepted=true ambiguous=false http=200 mutation_calls=1`; post-submit live recover exact `98628e98…`) | 06:52Z: 89/89 parsed, 17.62 / rank 99/147, cat 8 (9.0%), **signals=0 identity_clean=True** (`run1-checkpoint-initial.json`) | 07:41Z: **160/160, 19.77 / rank 60/147**, cat 12 (7.5%), neg_mass 3871, **signals=0 identity_clean=True** (`run1-checkpoint-terminal.json`) |

| 2 | 2026-08-12T07:44Z | **41125448 / agent 6610636** (`accepted=true ambiguous=false http=200 mutation_calls=1`) | — (matured across host suspend) | read 19:29Z: **160/160, 23.73 / rank 29/147**, cat 17 (10.6%), neg_mass 5463, **signals=0 identity_clean=True** (`run2-checkpoint-terminal.json`) |
| 3 | 2026-08-12T19:30Z | **41128302 / agent 6612307** (`accepted=true ambiguous=false`) | 19:58–20:01Z: room cache flapped (returned prior agent id twice, field count 147↔140); checkpoint correctly refused the mixed pair, then 111/111 parsed, **23.54 / rank 31/147**, cat 10 (9.0%), **signals=0 identity_clean=True** on re-read; live source re-verified exact `98628e98…` mid-flap (`run3-checkpoint-initial{,-v2}.json` — the False read kept as evidence) | pending |

Running spread on `98628e98…` after run 2: mature reads **24.76 / 22.46 / 19.77 / 23.73**
— max−min **4.99**; sample SD of the four ≈ **2.16**. Note for question 4: the 19.77 read
sits in the freshly grown legend-147 era (139 → 147 between reads).
**CAMPAIGN HELD 2026-08-12T20:25Z — run 4 NOT submitted.** Two consecutive session
timers for the run-3 terminal read were killed externally (20:02Z and ~20:25Z);
per the coordinator's stated escalation, that is read as a stop signal pending an
explicit owner word. No Arena mutation follows until then. Run 3 (41128302 / 6612307)
continues maturing platform-side regardless — it is the resident's own bytes, so the
slot is safe wherever it settles; its terminal read can be taken at any time.
Resumption cost: one submit call + reads. Cancellation cost: none — five mature
observations (runs 1–3 plus the two pre-campaign reads) already support a materially
better σ than the record's 10-deployment pooled estimate.

**Clock note (do not silently reconcile):** the project host suspended ~08:00–19:25Z;
run 2 matured somewhere inside that window and was READ at 19:29Z — platform-side
maturation time is not measurable from this side. An earlier draft claimed "~27 minutes";
that was a wall-clock read taken across the suspend and is retracted. Runs 1–2 are also
**not time-adjacent** despite being consecutive: ~11.5 h of ladder evolution separates
their finishes.
