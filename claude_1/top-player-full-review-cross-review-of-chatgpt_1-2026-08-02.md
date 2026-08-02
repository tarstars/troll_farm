# Cross-review of `chatgpt_1`'s full review replication

Reviewer: `claude_1` · Task: `20260802-top-player-full-review-replication` · 2026-08-02
Subject: `chatgpt_1/top-player-full-review-replication-2026-08-02.md`
SHA-256 `4f6ba9aac259796306942b83d2e2b7f2fd2aa34039048b3d6558c69f542fdb7f` at report commit
`cf51247a5f435d00cc4be95c7d2a310ce61d3897` — hash verified before reading.

## Standing declaration

I am the **non-blind** agent. I had read the integrated local report and reviewed it before
writing my own replication; `chatgpt_1` was blind. Where we agree, their agreement is the
informative half and mine is not. Where we disagree, that is where the integrator should
look hardest. I have applied that asymmetry against my own conclusions below, and it costs
me one of my two ranked ideas.

## Overall disposition: `ACCEPT_WITH_CORRECTIONS`

This is a strong report. **I could not break a single number in it.** Every checkable claim
reproduced exactly from the frozen package on independent recomputation:

| claim | result |
|---|---|
| 10/153 catastrophes at margin ≤ −100, 6.54% | exact — all ten IDs, ranks, margins, rosters |
| total −1,674; mean −167.4 | exact |
| ahead-at-checkpoint 9 / 10 / 9 / 6 / 1 / 0 | exact |
| band rates 0/1, 8/73, 1/52, 1/27 | exact |
| Wilson 95% [3.59%, 11.61%] and [5.66%, 20.16%] | exact to two decimals |
| nine matched-opponent games and their margins | exact |
| direct game: WAITs t4–8, 24 CHOPs t14–29, no PLANT/MINE ≤ t40, opponent TRAIN t1/56/105 | exact |
| projection 1,674 × 20% = 334.8, ÷153 = +2.19 | exact |

Two things deserve explicit credit. They reported **`897781674` (+91, opponent roster 4)** as
a clear counterexample to their own thesis — a blind agent volunteering the datum that
weakens its headline. And they held the line on `UNAVAILABLE_FROM_PACKAGE` for the WAIT
legality question rather than inferring it.

My corrections are about **runnability and scope**, not arithmetic.

---

## Disposition per ranked idea

### Their Rank 1 — H3a three-arm conditioned opponent-crop priority · `ACCEPT`

Unanimous rank 1 across all three reports. Their rubric 84, mine 82; the gap is immaterial.

**I accept their design over my own on one point.** Their **four-gate trigger-readiness
preflight** — predicate true by t150 in ≥8/10; first-true turn precedes the collapse interval
in ≥8/10; ≤20% false activation on matched wins; ≥1 eligible ETA-6 scoring decision after
activation in ≥6/10 — is a genuine improvement my report lacks. It converts "spend a 6,144-task
panel and find out" into "spend a cheap read-only audit that can kill the idea first". Given
that H3a's always-on twin already lost 7.77 rating on the ladder, a cheap kill-gate before an
expensive panel is exactly the right shape. **Adopt it.**

Their panel gates (`PRIMARY = CONDITIONED − ALWAYS_ON > 0` with CI lower bound ≥ 0,
`SECONDARY = CONDITIONED − CONTROL ≥ +5`) are slightly differently parameterised from the
frozen H3a gates cited in the local report (C1−C0 ≥ +2, C1−A1 ≥ +5). **Correction:** the
frozen protocol's numbers govern; where the two differ, the frozen gates win and the report
should say so rather than restate them from memory.

**Correction on readiness, applying equally to my report and theirs:** the value runner does
not exist. `cgauto/` contains no H3a runner and no C0/A1/C1 byte-equality prover. What exists
and runs today is `chatgpt_1/h3a_pressure_treatment_reconstruction.py --self-test`, which I
executed: `self-test: ok`, exit 0. That is a *reconstruction* self-test, not a value run.
Neither report should let "immediate check" cover the gap.

### Their Rank 2 — read-only late-crossover/pressure discriminator · `ACCEPT_WITH_CORRECTIONS`

**The idea is right; its placement and its "immediate" label are wrong.**

**Correction 1 — it is not runnable by either of us.** Its four gates require evaluating the
frozen predicate and ETA-6 eligibility "from committed trajectories/replays" on the ten
catastrophes plus seven matched wins. The package contains **exactly one trajectory**
(`897780884`), and that game is **not one of the ten** — its margin is −70, above their −100
threshold. **Zero of the seventeen named games has a trajectory in the package.** This is
host-only work. It is the identical defect I found in my own rank 2, and it should be labelled
the same way in both reports.

**Correction 2 — it should not be a separate rank.** Their own text concedes "this audit
itself claims no margin" and its projected value is "the same +2.19 scenario only if Rank 1
later passes". An item with no standalone value that exists solely to gate another item is a
**mandatory preflight of Rank 1**, not a rank of its own. Folding it in also removes the odd
result that a zero-value audit outranks every real candidate.

Answering the release's question directly: it is **distinct and useful, and not subsumed by
H3a** — it is a precondition for H3a — but it is **not immediately checkable**, and it belongs
inside Rank 1.

### Their Rank 3 — direct-game WAIT legality and precedence audit · `REJECT`

They scored it 58, below their own build band, and hedged it heavily. I go further and would
not spend the audit either. Three independent reasons:

1. **No signal in the cohort.** Across the 36 scaled-opponent full games, our WAIT command
   count correlates **−0.046** with margin. That is nothing.
2. **The sequence is almost certainly designed behaviour, not a defect.** The exact trace is
   `t2 HARVEST 1 → t3 DROP 1 → t4–8 WAIT → t9 HARVEST 1 → t10 DROP 1` — same tree, id 1. That
   is camping on a target while it re-ripens, which is the documented resident behaviour:
   `README.md` describes "camp with `WAIT` if already on a not-yet-ripe target", and the
   game's own t1 identity string is `yamo-carry-regen-transit-idle-harvest-rust`. An audit
   asking "was a productive action available?" will most likely answer "yes, and taking it
   would have cost the ripening cycle".
3. **n=1, and the game was led through t200.** Their own report says the WAITs "cannot be
   promoted as the cause" — correct, and it also means the audit has no outcome to explain.

**Disposition: reject as a ranked item; retain at most as a one-line note.** This is a
correction to a blind agent's finding that my non-blind position does not weaken — points 1
and 2 are recomputed and cited, not inherited.

---

## Corrected peer ranking

| Rank | Idea | Change |
|---:|---|---|
| 1 | H3a three-arm conditioned opponent-crop priority, **with their four-gate trigger-readiness preflight folded in as a mandatory, host-only precondition** | merged; frozen protocol gates govern |
| — | *(no rank 2)* | their rank 2 absorbed into rank 1 |
| — | *(no rank 3)* | WAIT audit rejected |

One ranked idea. Both of us independently arrived at a list whose only defensible entry is
H3a, and the honest presentation is a list of one rather than a padded three.

---

## The seven required reconciliations

**1 — H3a unanimous; self-test versus value run; their preflight.** Handled above. Unanimous
rank 1. The self-test runs (verified). The value runner does not exist and neither report
should imply otherwise. Their four-gate preflight is accepted and strengthens the design.

**2 — my 96-game decomposition versus their ten-catastrophe crossover.** These are
**complementary, not competing, and neither subsumes the other.**

- Theirs isolates the *tail*: 10 games carrying −1,674 margin, with an exact ID list and a
  clean temporal ladder. That concentration is what makes a targeted preflight possible.
- Mine describes the *whole distribution*: across all 96 full games, our per-window scoring
  never declines (36.92 → 42.56 against scaling opponents) while theirs multiplies 12×
  (8.64 → 102.19); our mean final score is **higher** in games we lose (234.28) than in games
  we win (198.58); opponent final score by roster runs 29.25 / 156.48 / 232.95 / 334.57.

Their finding tells you *where* to intervene. Mine tells you *what cannot possibly work* —
any own-economy improvement, because our own output is already higher in the games we lose.
The integrator should keep both. If only one survives into the final record, keep theirs for
the exact IDs and keep my §3 table as the rejection rationale.

Their rank 2 is **not** subsumed by H3a; it gates H3a. See its disposition.

**3 — their WAIT legality audit.** Rejected, with the three reasons above. No causal claim is
made or implied by me, and their `UNAVAILABLE_FROM_PACKAGE` marking was correct.

**4 — my rank 2 (endgame removal race), absent from their ranking.** **I withdraw it.**

A blind agent working the same package did not surface it at all. My own rubric scored it
**60**, below the 65 "audit first" band. Its tree/feller/wood attribution is
`UNAVAILABLE_FROM_PACKAGE` — I verified only the plant turns — and its census is host-only,
the same defect I am charging against their rank 2. The corpus support I offered
(opponent chops landed correlate −0.379 with margin over 36 games) is collinear with opponent
roster (−0.337) and I could not separate them.

I am not going to defend an idea against that combination merely because I published it.
**Move it to measurement-only.** If the local report's version survives on other grounds,
that is the integrator's call, and correction 4 from my earlier review still applies to it:
its "20 margin/current game" gate must state its denominator before any census runs.

**5 — B3.14 and the empty rank 3.** We agree, from different directions: they find no
reproduced current-source failure trace in the package; I find a hard ceiling of
17 × 4 / 153 = **+0.444 own points per game** in a bot whose own scoring is not the deficit,
inside the ±0.5 noise band regardless. Consensus: **measurement-only, do not promote.**

On empty-versus-audit: a low-cost audit is defensible *only* if it closes a recurring
question. B3.14 qualifies on cost — three replays, existing invariant, existing test at
`tests/test_tent_banker_commitment_candidate.py` — but not on value. My recommendation is to
run it once as an explicit **closure** with no expectation of gain, and to keep rank 3 empty
in the improvement ranking. Padding a ranked list of improvements with a closure exercise is
what produces the "audit outranks the real candidate" inversion seen in their rank 2.

**6 — `planted_ok_* > plant_cmd_*`.** Confirmed as a schema/provenance defect. Over top-20
sides, `planted_ok` **exceeds** commands issued: 86,023 vs 81,280 (105.8%); our opponents
107.1%. `planted_ok_*` is therefore not a subset of `plant_cmd_*`, and **any plant-success
ratio from these columns is unsound.** Neither report published one — I flagged it, they did
not compute it. The manifest needs a column definition; until then, reject any such ratio in
either direction.

**7 — corrected scaled-opponent predicate and the 1,268 count.** No dispute exists. Their
analysis keys on `roster_final` directly and never touches `second_train_turn`, so it is
immune to the boundary defect. My replication used the corrected conjunct
`second_train_turn <= 151 AND roster_final >= 3`, with `897782434` excluded as a failed
TRAIN — a game where the opponent commanded a second TRAIN at t30 that never landed
(`train_count=2`, `roster_final=2`). Neither report relies on 1,268. My earlier search
established that no predicate over the package reproduces 1,268 or 1,267; the nearest
coherent readings are **1,330 sides** and **1,270 games**.

---

## One correction the release did not ask for

Their §1 reports a provenance defect: the task's pinned rubric SHA "is not independently
resolvable as a commit". **This is a category error and no task-record change is needed.**
`390cd4bc85975519b64ae63d4b993614e87ac471c33a670574432470952f5e6f` is the **SHA-256 content
hash** of the rubric file and it verifies exactly. Their reported
`c33f0ad3156ade905dcb106c4d8941ffa74d0973` is the **Git blob hash** of the same file. Two
different hash functions over identical content, both correct. It was never a commit id.

---

## Scope

Committed package, the peer report at its released commit, and tracked repository files only.
No raw cache, host-only path, sealed data, source or shared-document edit, analyzer, build,
simulation, candidate, TestSession, Arena/API/submission action, cron change, or peer
namespace write. I did not integrate either branch.
