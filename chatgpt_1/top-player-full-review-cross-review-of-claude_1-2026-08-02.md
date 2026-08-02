# Cross-review of `claude_1` full top-player replication

- Task: `20260802-top-player-full-review-replication`
- Reviewer: `chatgpt_1`
- Date: 2026-08-02 UTC
- Reviewed report: `claude_1/top-player-full-review-replication-2026-08-02.md`
- Reviewed handoff commit: `b389c9d7b903d366ea61df8664783f61a6f935c0`
- Reviewed SHA-256, as pinned by the integrator:
  `97286f95b9788b383f53332a8a549e07d34a07b25468389947560f916175ef69`
- Release commit: `43d8aa21008427edc58517968364496d3696ea82`
- Frozen evidence commit: `73718b3fdf9f2dc13359e17cb0ce002f95ea559e`
- Platform mutation: none

## Overall disposition

**`ACCEPT_WITH_CORRECTIONS`.**

Claude's report contains a useful and mostly careful descriptive result: opponent workforce
separation can already be present by turn 150, while the resident's score advantage is erased
later. Its direct-game arithmetic, disclosure of prior exposure, treatment-seam description,
and insistence on the mandatory H3a three-arm contrast are sound.

The ranking is not executable as written, however. The H3a reconstruction self-test is not a
value runner; the conditioned source, byte-equality bridge, and panel runner do not exist.
The frozen package contains per-turn trajectory data for only `897780884`, so neither
Claude's multi-game trigger check nor ChatGPT's earlier multi-game readiness preflight can be
run from the authorized evidence. Rubric hard veto 5 therefore blocks H3a from the
"immediate-check" band in this task. Claude's rank-2 removal-race census has the same, more
severe evidence problem and is rejected.

## 1. Provenance, package accounting, and schema

The report uses the correct frozen cohort and exact current identity:

- 153 current-new open games, 95 wins / 2 ties / 56 losses;
- 68 seat-0 / 85 seat-1 games;
- 96 full 300-turn games and 57 shorter games;
- one direct top-20 game, `897780884`;
- 2,684 open top-20-source benchmark games;
- seven sealed-tagged games excluded.

I found no identity or split substitution in either ranked idea. The direct game and its
command/checkpoint facts are in the frozen package.

Claude is also correct to reject any ratio formed as
`planted_ok_* / plant_cmd_*`. In the supplied schema, aggregate `planted_ok_*` can exceed
`plant_cmd_*`; without a precise counter definition, the numerator is not demonstrably a
subset of the denominator. This is a schema/provenance defect, not evidence of >100% plant
success. No such ratio should enter a mechanism or gate.

I do not use the previously unexplained `1,268` count anywhere in this review.

## 2. Reconciliation of the temporal disagreement

The reports are compatible after one precise wording correction:

> **Opponent workforce divergence can be established by turn 150; the score crossover and
> largest terminal damage occur later.**

Claude's 96-full-game decomposition is broader than ChatGPT's ten-catastrophe tail analysis.
Its final-roster split shows that games ending against three- or four-worker opponents change
from a positive resident net before turn 150 to negative net in `150→200`, then become much
worse in `200→250` and `250→final`. ChatGPT's tail result says the resident is still ahead at
turn 150 in 9/10 catastrophic games but ahead at turn 250 in only 1/10. These are different
views of the same chronology, not contradictory mechanisms.

The correction is important because **final roster is post-outcome and endogenous**. It can
motivate a retrospective cohort but cannot be the deployment trigger or a causal treatment
label. For temporally ordered retrospective counts, use exactly:

```text
second_train_turn <= 151 AND roster_final >= 3
```

This requires a successfully landed second extra TRAIN. Game `897782434` contains a failed
TRAIN and must not be counted as scaled by turn 150. A live policy may instead observe the
outcome-blind public state `opponent_unit_count >= 3`; that trigger is mechanically coherent,
but its value remains untested.

The six-versus-nine and related t150-conditioned contrasts remain observational. They select
on an existing t150 lead and on opponent policy/economy; they do not identify the effect of
H3a, TRAIN, or any single opponent action.

### Correction to Claude's strongest negative conclusion

The descriptive statement is supported:

- resident own score does not collapse in the selected scaled-opponent games;
- opponent acceleration dominates the late margin reversal.

The stronger statement — that *any* own-economy, harvest, banking, or conversion improvement
must attack the wrong variable — is not identified by this comparison. Stronger opponents,
map composition, shared created resources, duration, and resident opportunities are bundled
with final workforce. Higher resident output in the losing group does not prove that a
marginal own-economy intervention has zero causal value.

Many such branches are independently closed by controlled project evidence and displacement
accounting. Those closures remain binding. The 96-game decomposition should be cited as a
rejection of the simple "resident output collapses" narrative, not as a new causal closure of
every own-economy intervention.

## 3. Explicit disposition of every ranked Claude idea

### Rank 1 — H3a conditioned opponent-crop priority

**Disposition: `ACCEPT_WITH_CORRECTIONS`.**

#### Accepted

- The source seam is narrow and exact: the already reconstructed seven-site operation
  `candidate.score += candidate.score` on tracked existing opponent-created tree targets at
  ETA `<= 6`.
- The proposed runtime trigger `opponent_unit_count >= 3` is public, outcome-blind, and does
  not require final roster, identity, future TRAIN, or score-behind state.
- The only scientifically adequate value design has three arms:
  - `C0`: unchanged fallback;
  - `A1`: the exact treatment always on;
  - `C1`: the identical treatment conditioned on workforce pressure.
- `C1−A1` is load-bearing: it tests whether conditioning adds value rather than merely
  repeating the already rejected always-on opponent-crop policy.
- The stated same-map/both-seat/family/tail gates and stop rules are a defensible future
  protocol. The arithmetic `128 × 2 × 8 × 3 = 6,144` tasks is correct.
- The corrected retrospective evidence should use successful
  `second_train_turn <= 151 AND roster_final >= 3`, not command appearance or final roster
  alone.

#### Required corrections

1. **The self-test is not a value check.**

   The existing commands:

   ```bash
   python3 chatgpt_1/h3a_pressure_treatment_reconstruction.py --self-test
   python3 -m pytest -q tests/test_h3a_pressure_treatment_reconstruction.py
   ```

   validate anchors, exact fallback-to-always-on transformation, inverse equality, target
   semantics, and frozen hashes. The code explicitly returns `panel_authorized: false`.
   It contains no conditioned policy, no game panel, no exact-resident referee run, and no
   terminal-value comparison.

2. **The true first discriminator does not exist.**

   There is no conditioned-source generator, no sticky public-state bridge, no proof that C1
   is byte-equal to C0 before activation and A1 after activation, and no three-arm value
   runner. Claude correctly discloses this later, but the rubric score still grants too much
   immediate decisiveness.

3. **The proposed multi-game trigger check cannot run from the frozen package.**

   `sides.csv` supplies aggregate side/game fields and score checkpoints. Turn-level commands
   are frozen only for direct game `897780884`. The package does not expose the H3a candidate
   states or activation opportunities for the other cited losses or matched wins. Therefore
   a six-game trigger replay, ChatGPT's earlier four-gate trigger preflight, or a proof that
   the predicate fires selectively cannot be reproduced from the authorized package.

4. **Rubric hard veto 5 applies now.**

   The first value discriminator cannot run on the supplied open evidence with exact
   resident/referee semantics. An 82-point "immediate-check" classification is therefore not
   admissible. H3a is **protocol-ready in concept but blocked on a substantial implementation
   and input package**, and this cross-review task explicitly forbids creating that runner.

5. **Current demonstrated value is zero.**

   The 135-margin-per-affected-game calculation is a broad counterfactual ceiling formed by
   replacing late opponent production rates. It is not an expected H3a effect and does not
   price treatment coverage, displacement, opponent benefit, or tail risk. It must not be
   described as a conservative projection. The previous always-on twin's poor Arena result
   strengthens the need for the A1 arm; it does not establish conditioned value.

#### Correct current status

```text
H3a = top future protocol, BLOCKED_PENDING_CONDITIONED_SOURCE_AND_VALUE_RUNNER
```

No build, panel, candidate, or Arena action is authorized by this review.

### Rank 2 — endgame conversion removal race

**Disposition: `REJECT`.**

#### Facts accepted

- Direct game `897780884` contains 12 resident PLANT commands at the cited late turns.
- Eleven, not twelve, occur after turn 250.
- The five cited late APPLE conversions are visible in the direct trajectory.
- The opponent issues substantially more late CHOP commands.

#### Why the proposed mechanism does not survive

1. **The race itself is unavailable from the package.**

   To establish a removal race, the check needs tree identity and provenance, health,
   candidate target, both arrival times, actual feller, harvested fruit, wood recipient,
   and the counterfactual value of keeping the seed banked. Those fields are not present in
   `sides.csv`; only one trajectory is frozen, and even that trajectory does not supply the
   complete causal attribution claimed by the proposed census.

2. **The corpus correlation is confounded.**

   Opponent CHOP count is collinear with opponent workforce and broader opponent policy. A
   negative correlation with resident margin raises a descriptive prior; it does not show
   that post-250 resident conversions feed the opponent or that `KEEP_BANK` would prevent the
   loss.

3. **The first check is explicitly non-runnable.**

   Claude states that the required 153-game lineage census does not exist and is host-only by
   construction. That triggers rubric hard veto 5. The present task also prohibits creating
   an analyzer or simulation.

4. **The source seam is not evidence of value.**

   A pre-PICK `KEEP_BANK` alternative is a concrete seam, but it changes the resident's
   endgame conversion decision and lies adjacent to already closed plant-pacing,
   threatened-crop, seed-carry, and generic conversion families. A materially new
   opponent-arrival representation could distinguish it, but that representation and its
   exact-replay labels are precisely what the package lacks.

5. **The payoff cannot justify a ranked intervention.**

   The one-game conservative ceiling is `+0.033` own points or `+0.216` margin per entire
   cohort game, below the stated measurement noise. The proposed 20-margin gate changes
   meaning by roughly two orders of magnitude depending on whether its denominator is all
   current games or only predicted affected games. A gate with unresolved denominator is not
   preregistered and cannot pass the rubric.

Claude's statement that the idea "suppresses their gain, not ours" is not established because
the package cannot attribute the opponent's late gain to those resident conversions.

### No defensible rank 3

**Disposition: `ACCEPT`.**

Leaving rank 3 empty is better than padding the list with an unavailable or sub-noise audit.
The ranking rubric requires a discriminator that can run now; none remains after H3a and the
removal race are checked against the actual package boundary.

## 4. B3.14, B3.15, and the empty rank 3

Claude's demotion of B3.14 is accepted.

- B3.14 is already documented as an isolated incident correction with focused tests and
  immature monitoring evidence, not a field-value claim.
- Its aggregate own-wood ceiling is too small to justify an Arena cycle.
- The frozen package does not contain the per-turn cargo/role/return-state evidence needed to
  identify fresh B3.14 recurrence across the current cohort.
- Running the suggested three exact replays would require replay inputs and execution outside
  the frozen package and is prohibited in this task.

B3.15 has the same status: a narrow mechanism correction whose existing exact evidence does
not authorize global tree ordering or oscillation work. Its current recurrence is not
established by this package.

Thus neither is a valid rank 3 here. They may remain **future surveillance questions** when
an exact authorized replay package already exists, but not current improvements and not a
reason to build a new analyzer.

Claude correctly notices that a `+0.444` own-points/game ceiling cannot by itself justify
placing B3.14 below a removal-race idea with even smaller stated cohort-wide headroom. The
correct resolution is not to reverse them; it is to remove both from the actionable ranking.

## 5. Direct game and ChatGPT's WAIT-audit proposal

The direct-game chronology is accepted:

- current trains at turn 11 and finishes with two workers;
- Astrobytes trains at turns 1, 56, and 105 and finishes with four;
- current leads through turn 200, is approximately tied by turn 250, and loses 333–403;
- resident WAIT commands at turns 4–8 are visible.

What is **not** in the package is the exact set of legal, non-displacing alternatives after
movement, occupancy, capacity, candidate generation, and command precedence. The trajectory
shows emitted commands, not a complete counterfactual legality surface.

Therefore ChatGPT's earlier rank-3 WAIT legality/precedence audit is **withdrawn from the
immediate ranking**. It would require a new exact legality analyzer or simulation, both
prohibited here. Generic idle cleanup and oscillation are already closed; one visible WAIT
run cannot reopen them or establish causality.

## 6. ChatGPT rank-2 discriminator: distinct or subsumed?

ChatGPT's earlier read-only late-crossover/pressure discriminator is **not a distinct
immediate check** after Claude's window decomposition and the release correction.

The frozen package already supports the descriptive result:

- successful opponent workforce expansion can precede score loss;
- resident leads often survive to turn 150–200;
- the major score reversal is later.

What remains unknown is whether the frozen H3a predicate activates on the right candidate
states and whether the conditioned treatment changes value. Those are H3a runner questions,
not another aggregate discriminator. Because the relevant per-turn candidate states are
absent, the proposed four-gate multi-game preflight cannot run either.

I therefore remove my prior rank 2. It is subsumed by the future H3a readiness/value package
and contributes no separate build authorization.

## 7. Corrected peer ranking

### Rank 1 — H3a exact mandatory three-arm protocol

```text
Disposition: BLOCKED / measurement-only under current task
Reason: exact seam and protocol, but no conditioned source, byte bridge, trigger-state input,
        or value runner; rubric hard veto 5 applies
Current demonstrated value: 0
Next legal state: wait for a separately authorized, pre-existing exact runner/input package;
                  do not build one under this review
```

H3a remains first because it is the only mechanism here with a narrow source seam, an
outcome-blind trigger, an essential always-on comparator, and a plausible relation to the
broad late opponent-acceleration pattern. It is not an immediate experiment today.

### Rank 2 — none

The removal race is rejected, not merely deferred. B3.14/B3.15 are surveillance-only and
package-unavailable. WAIT legality is unavailable and closure-adjacent. No other idea clears
the hard vetoes.

### Rank 3 — none

Leaving the slots empty is the scientifically correct result.

## 8. Final disposition table

| Peer item | Disposition | Correct state |
|---|---|---|
| Rank 1 H3a conditioned opponent-crop priority | `ACCEPT_WITH_CORRECTIONS` | Top future protocol; currently blocked, not immediate |
| Rank 2 endgame conversion removal race | `REJECT` | n=1 mechanism, census unavailable, tiny/ambiguous payoff |
| No rank 3 | `ACCEPT` | Do not pad with B3.14, B3.15, or WAIT audits |
| 96-game opponent-scaling window decomposition | `ACCEPT_WITH_CORRECTIONS` | Strong descriptive chronology, not causal closure of all own-economy work |
| B3.14 demotion | `ACCEPT` | Incident correction / surveillance only |
| `planted_ok / plant_cmd` success ratios | `REJECT` | Schema/provenance defect |

## 9. Scope and safety

This review used only the released peer report, frozen committed package, ranking rubric,
and tracked closure/state documents. I did not access raw or host-only paths, sealed data,
source/shared-document edits, an analyzer, build, simulation, candidate, TestSession,
Arena/API/submission, cron, or platform action. I did not integrate either peer branch.
