# 20260810-arena-noise-band-measurement: measure the ladder's run-to-run noise, and separate our variance from the ladder's drift

- Status: **✅ CLOSED 2026-08-13.** Delivered σ = 1.501, CI [1.049, 2.634] (14 mature
  obs / 10 d.o.f.); codex_1 review accepted the registry repair and reproduced every
  number; its one required correction is applied to the living docs: **1.501 is the
  combined operational variability of a sequential campaign — no inequality between
  re-submission variance and drift is established**; runs-per-arm is an IID planning
  approximation. All four owner questions answered (Q4: era effects fold into the
  combined figure; separation requires interleaving, not run counts).
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
| 3 | 2026-08-12T19:30Z | **41128302 / agent 6612307** (`accepted=true ambiguous=false`) | 19:58–20:01Z: room cache flapped (returned prior agent id twice, field count 147↔140); checkpoint correctly refused the mixed pair, then 111/111 parsed, **23.54 / rank 31/147**, cat 10 (9.0%), **signals=0 identity_clean=True** on re-read; live source re-verified exact `98628e98…` mid-flap (`run3-checkpoint-initial{,-v2}.json` — the False read kept as evidence) | **2026-08-13T05:19:48Z: 160/160, 24.90 / rank 21/147**, cat 19 (11.9%), neg_mass 5292, **signals=0 identity_clean=True**, `unexpected_rows=[]`, `fetch_failures=[]` (`run3-checkpoint-terminal.json`, read by claude_1 under the VM lease) |

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

## Lease execution by claude_1 on the VM (from 2026-08-13T05:19Z)

Arena authority delegated by `20260812T201400Z-…-vm-lease-policy.md`, bounded to steps 1–5.
Environment: worktree `/home/tarstars/prj/troll_farm-plan-agent` at `agent/claude_1` merged
current with `origin/main` (`f7069d16`). **The environment gap raised in my ack is resolved and
was never real:** `battle_taxonomy.py:22` and `api_submit_once.py:21` both hardcode the *absolute*
cookie path `/home/tarstars/prj/troll_farm/cgauto/cg_session.txt`, and both tools are stdlib-only,
so the reader runs correctly from any checkout and the cookie is neither copied nor moved.

**Step 1 complete — run-3 terminal read, the cleanest read of the campaign.** 160/160 finished,
0 pending, `unexpected_rows=[]`, `fetch_failures=[]`, `identity_clean=True`, and **`arena` and
`filtered_ladder` agree exactly (both agent 6612307, both 24.90, rank 21/147)** — no flap in this
read. The 118-game interim it replaced is preserved in git history at `2c649a1a^`.

**Maturation is not negligible and should not be treated as settling noise:** the same deployment
read 23.61 (arena) at 118/160 and 24.90 at 160/160, **+1.29 over the last 42 games**. The gap
between the two reads was ~9.3 h (20:02Z → 05:19Z), so this is 118→160 maturation, not drift
measured at a fixed game count. Terminal-only comparison remains the right rule.

### Step 2 — run-4 submit, RECORD WRITTEN BEFORE THE CALL

This row is committed and pushed **before** the mutation call, per the lease. It is the record that
a call was *about to be made*, so that an ambiguous or lost response can never leave the campaign
unable to tell whether a fourth deployment exists.

- **Intent stamped**: 2026-08-13T05:23:45Z (`date -u`, real clock).
- **Source**: `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs`, verified in this
  worktree at sha256 `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29`, in
  three-way agreement with the lease's `--expected-sha256` and the committed `.sha256` sidecar.
- **Budget**: run 4 of 4. **This is the last authorized Arena mutation.** Nothing in the lease
  permits a fifth, and an ambiguous response suspends the lease rather than licensing a retry.
- **Tool guarantees relied on** (`api_submit_once.py`): the source hash is checked *before* any
  network call; there is no endpoint or payload fallback; a non-200, malformed or transport-
  ambiguous response returns `ambiguous=true` as data and makes no second call; `mutation_calls`
  is reported explicitly.
- **Outcome**: recorded in the row below immediately after the call returns, whatever it says.

**Call returned 2026-08-13T05:24Z — ACCEPTED, UNAMBIGUOUS. The budget is now spent.**

```
accepted=true  ambiguous=false  http_status=200  mutation_calls=1
phase=submit  endpoint=TestSession/submit  submission_id=41129543
source_sha256=98628e98…  source_bytes=75634
```

| run | UTC submit | submission / agent | initial health | terminal 160/160 |
|---|---|---|---|---|
| 4 | 2026-08-13T05:24Z | **41129543 / agent 6614096** (`accepted=true ambiguous=false http=200 mutation_calls=1`, sha `98628e98…` verified pre-call, 75,634 B) | 05:30Z: 26/26 parsed, **20.30 / rank 54/147**, cat 3, **signals=0 identity_clean=True** (first attempt at 05:26Z hit the stale room row and is kept as `run4-checkpoint-initial-flap.json`) | **2026-08-13T06:40:16Z: 160/160, 23.39 / rank 31/147**, cat 22 (13.8%), neg_mass 6538, **signals=0 identity_clean=True**, arena == filtered (`run4-checkpoint-terminal.json`) |

### Step 3 — the terminal read took four attempts, and the gate is why

The room served the stale `6604529 / 140 / 22.46` row on three consecutive reads *after* the games
were already complete:

| UTC | games | rc | identity_clean | arena agent | score |
|---|---|---|---|---|---|
| 06:23Z | 141/160 | 2 | False | 6604529 | 22.46 |
| 06:29Z | **160/160** | 2 | False | 6604529 | 22.46 |
| 06:35Z | **160/160** | 2 | False | 6604529 | 22.46 |
| 06:41Z | **160/160** | **0** | **True** | **6614096** | **23.39** |

**A gate on `matching_finished == 160` alone would have promoted the 06:29Z read** — 160/160,
0 pending, 0 unexpected rows, 0 fetch failures, battle data entirely correct — and recorded
**22.46**, another deployment's score, as run 4's terminal observation. It would have looked
immaculate. The poller gated on `identity_clean` **and** the process exit status
(`arena_transfer_checkpoint.py` returns 2 when unclean), which is the only reason the campaign has
23.39 instead of a second silent 22.46.

Method note against my own error: an earlier invocation of that reader in this session was piped
(`… | tail; echo $?`), which reads *tail's* status and would have reported success on every
unclean read. The poller captures `$?` from the python process directly. Same defect class as the
`lint | tail && push` break; it is easy to reintroduce and worth checking for by eye.

## Steps 4–5 — registry appended and σ recomputed (claude_1, 2026-08-13)

`build` + `validate` green (53 observations validate cleanly); `tests/test_submission_history.py`
**47 passed**. Append script committed at `claude_1/pipeline/append_sigma_runs.py` — the append is
reproducible, not hand-edited JSON.

### Field provenance — which number came from which block of which file

Every value below is `arena.score`, and in every case `arena` and `filtered_ladder` **agree** and
both name the run's own agent, so no field-choice ambiguity survives into the estimate.

| run | submission / agent | source file | arena | filtered | clean | value used |
|---|---|---|---|---|---|---|
| pre-1 | 41089629 / 6593838 | earlier registry entry | 24.76 | 24.76 | — | **24.76** |
| pre-2 | 41113243 / 6604529 | earlier registry entry | 22.46 | 22.46 | — | **22.46** |
| 1 | 41125196 / 6610399 | `run1-checkpoint-terminal.json` | 19.77 | 19.77 | true | **19.77** |
| 2 | 41125448 / 6610636 | **`run2-checkpoint-initial.json`** | 23.73 | 23.73 | true | **23.73** |
| 3 | 41128302 / 6612307 | `run3-checkpoint-terminal.json` | 24.90 | 24.90 | true | **24.90** |
| 4 | 41129543 / 6614096 | `run4-checkpoint-terminal.json` | 23.39 | 23.39 | true | **23.39** |

**Run 2 is read from the file labelled `initial`, deliberately** (coordinator ruling
`20260813T060000Z`). Despite the role string it is a complete terminal observation — 160/160,
`matching_pending: 0`, both blocks agent 6610636 at 23.73, field 147 — captured 19:22:19Z, two
minutes *before* the room went stale at 19:24:29Z. `run2-checkpoint-terminal.json` is the flapped
read and is **not** used for the estimate. Maturity is keyed on content
(`matching_finished`/`matching_pending`/`identity_clean`), never on the role string in a filename.

### Result

```
family e7a-readable-no-orchard-code-cost   n=6   [19.77, 22.46, 23.39, 23.73, 24.76, 24.90]   range 5.13
4 families, 14 mature observations, 10 d.o.f.
POOLED WITHIN-SOURCE SD = 1.501 score points      (was 1.098 at 6 d.o.f.)
95% CI for the SD        = [1.049, 2.634]
SD of an A-minus-B difference at n=1 each = 2.123 (was 1.552)

runs per arm:  SE 1.0 -> 5   |  SE 0.5 -> 19  |  SE 0.3 -> 51
```

σ rose **37%** and the CI's lower bound (1.049) now sits *above* the previous point estimate. The
campaign family's range of 5.13 is 2–3× every other family's (1.70–1.77), and it is the only
family with more than four observations — the earlier 1.098 rested on families of n=2 and n=4.
**The ±0.5–1.0 band in `docs/STATE.md` §3 is refuted as an operating assumption**, and the
historical gates (±0.5, ≥+1.0, ≥+2) are less resolvable than the record assumed: a ≥+1.0 call now
needs 5 runs per arm, not 3.

### What Phase 1 cannot separate — stated, not hedged

**Re-deployment noise and ladder drift are confounded in this design and no analysis of these six
observations can separate them.** The runs are strictly sequential — never contemporaneous — and
span 2026-08-04 → 2026-08-13, during which the field grew 139 → 147 and opponents resubmitted
freely. Run 1's 19.77 in particular sits in a freshly grown legend-147 era. So `1.501` is an upper
bound on pure re-submission variance and a lower bound on nothing: it is *the spread you should
expect between two sequential reads of identical bytes*, which is exactly the quantity a
sequential A/B on this ladder faces. Separating the two components needs a design this campaign
does not have (interleaved or contemporaneous arms), and the budget is spent.

**Agent id not yet assigned at 05:25Z:** `cg_rank.py` still reports the arena room at
`agentId=6612307` — run 3's agent, score 24.9, rank 21/147. That is the known room-cache lag, not
a failed submission; the submission id is confirmed. The run-4 agent id will be read from the room
once it propagates, and **no checkpoint will be taken against a guessed agent id** — the checkpoint
tool requires both agent and submission and refuses mixed pairs, which is the behaviour that caught
the run-2/run-3 flaps.

### Field-identity hazard in the inherited four-read baseline — READ BEFORE APPENDING TO THE REGISTRY

The four mature reads **24.76 / 22.46 / 19.77 / 23.73 are individually correct**, and I confirmed
each against its own record. But they are **not all the same field**, and the registry consumes a
single `score` key (`arena_noise_band.py:90`, `obs["score"]`):

| read | submission / agent | `arena.score` | `filtered_ladder.score` | note |
|---|---|---|---|---|
| 24.76 | 41089629 / 6593838 | 24.76 | 24.76 | agree |
| 22.46 | 41113243 / 6604529 | 22.46 | 22.46 | agree |
| 19.77 | run 1, 41125196 / 6610399 | 19.77 | 19.77 | agree |
| 23.73 | run 2, 41125448 / 6610636 | **22.46, agent 6604529** | **23.73, agent 6610636** | **arena block is a stale row for a DIFFERENT agent** |
| 24.90 | run 3, 41128302 / 6612307 | 24.90 | 24.90 | agree |

Run 2's `arena` block reports agent `6604529` — submission 41113243, a different deployment — so
its arena score is not run 2's score at all. The task record correctly took `filtered_ladder`
(23.73). **The trap: the stale value is `22.46`, which is numerically identical to 41113243's own
legitimate terminal score already in the baseline.** Taking run 2's arena field would have silently
entered 41113243's score twice and read as a plausible near-duplicate rather than an error — it
would not look wrong. The same stale-agent row appears in `run3-checkpoint-initial.json`.

**Binding for step 4:** when appending, take `filtered_ladder.score` **only after checking that its
`agent_id` matches the run's own agent**, and record which field each value came from. Runs 1, 3
and the two pre-campaign reads may take either field; run 2 must take `filtered_ladder`.

**Clock note (do not silently reconcile):** the project host suspended ~08:00–19:25Z;
run 2 matured somewhere inside that window and was READ at 19:29Z — platform-side
maturation time is not measurable from this side. An earlier draft claimed "~27 minutes";
that was a wall-clock read taken across the suspend and is retracted. Runs 1–2 are also
**not time-adjacent** despite being consecutive: ~11.5 h of ladder evolution separates
their finishes.
