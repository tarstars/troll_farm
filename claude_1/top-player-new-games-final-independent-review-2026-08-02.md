# Independent review — final ranked ideas, top-player new games

Reviewer: `claude_1` (track-2 assignee before the lease takeover; this is a review only)
Task: `20260802-top-player-final-independent-review`
Date: 2026-08-02

## Subject and inputs, hash-verified before review

| artifact | SHA-256 | status |
|---|---|---|
| `local_codex_1/top-player-new-games-final-ranked-ideas-2026-08-02.md` | `d86016da0bf3ec346e6ddd2dfbaf34a1f4dd62640dcbb05ce8f7f7a056b79e94` | matches the task record exactly |
| `…shared-2026-08-02.manifest.json` | `dea2d4b2…` | as published |
| `…shared-2026-08-02.sides.csv` | `e4e49234…` | as published |
| `…shared-2026-08-02.direct-game.json` | `e1a94b84…` | as published |
| `…shared-2026-08-02.direct-trajectory.json` | `c9d77aed…` | as published |
| `…ranking-rubric-2026-08-02.md` | `390cd4bc…` | as published |

Everything below was recomputed from that committed package alone — no host cache, no
credentials, no sealed read, no platform call.

# Verdict: `ACCEPT_WITH_CORRECTIONS`

The report's evidence base is sound and its discipline is better than the situation that
produced it. Rank 1's association arithmetic reproduces to the digit, the closure reasoning
is correct against `docs/CONSTRAINTS.md`, and the report does not overclaim from the n=1
direct game. I found **five corrections**, one of which changes the ranking rationale and one
of which changes what "immediate check" means. None invalidates rank 1.

# 1. Reproduction results

## VERIFIED — reproduced exactly from the package

| claim | independent result |
|---|---|
| 5,672 side rows; 153 current-new; 2,684 top20-source; 2,836 union; 2,853 top20 sides | identical |
| current record 95W/2T/56L; seats 68/85 | identical |
| opponents ≥3 workers in 46/153, 31 identities, both seats | identical |
| that group 16W/30L mean −28.91; other 107 79W/2T/26L mean +46.41; difference −75.32 | identical |
| game-bootstrap 95% CI [−109.24,−42.28] | 20k resample → [−109.57,−41.87]; same interval within resampling noise |
| full-game opponent scaling 36/96 | identical |
| t150 cohort 26/28 lead, 7/28 win, 19 lead→loss, +64.89 → −57.29; other 68 +37.19 → +55.49 | identical (see correction 1 for the definition) |
| B3.11 apple 1,263 units in 27/153 games, 56.2% in five | identical |
| B3.14 banking 7,003 of 7,020 wood; 17 unbanked; ceiling 17×4/153 = 0.444 | identical |
| `897781203` — 106 wasted resident PLANTs reject 106 rival PLANTs | ours 119−13 = 106; theirs 130−24 = 106. The symmetry is exact and is the strongest single safety observation in the report |
| five APPLE conversions at t271, 274, 278, 282, 288 | identical |
| rank-2 headroom: +0.033 conservative own/game, +0.216 optimistic margin/game | 5/153 = 0.0327; (28+5)/153 = 0.2157 |

Arm identities also cross-check against the Arena submission registry independently of this
report: C0 `a8eb3b2b…` is `preseed-orchard-coverage-slim`, four mature runs, median 24.19;
A1 `083107f5…` is `opponent-crop-dual-value-e6-slim`, submission `41012867`/agent `6560350`,
**rejected at the 63-game gate at 16.51 against a 24.28 control, −7.77**. The report's
premise that A1 is an already-tested, already-failed always-on treatment is correct at the
hash level.

## PARTIAL — corroborated, not verified

Rank 2's attribution beyond the plant turns. Opponent CHOPs do occur at t275, 279, 285 and
294 — and also at 273, 274, 276, 277, 278, 283, 284, 286, 287, 288, 289, 292, 293 and
295–300. Establishing that Astrobytes felled *those five specific trees*, that seven wood was
captured *at those turns*, that it harvested *zero* fruit from resident crops, and that its
121 harvested fruit decompose as 79 initial + 42 own all require the frame/view state, not
the command stream. The command stream is consistent with every one of those statements and
contradicts none. I could not close them.

## HOST_ONLY — correctly so

The entire B3.14 turn-level census: 293 bank-progress→diversion transitions across 70 games,
eight multi-turn full-WOOD WAIT runs, 40 WAIT turns, 41,506 decoded turns, and the three
named incidents `897781302` t189–195, `897781012` t49–54 and t276–280, `897781689` t223–228.
**The package contains exactly one trajectory** (`897780884`); none of those three games has
one. I confirmed the games exist in the cohort and confirmed the 7,003/7,020 aggregate from
the CSV, and nothing else. The report does not overclaim here and rank 3 is already gated as
replay-only, so this is a boundary statement, not a fault.

## NOT REPRODUCIBLE — and it should be

The corrected count "successful-two-worker top20 sides are 1,268, not 1,267". Against the
2,853 top20 side rows I get **1,330** under every natural predicate — `roster_final>=3`,
`effect_trained>=2`, `train_count>=2`, `second_train_turn` non-null, and their conjunctions —
and 1,256 restricted to full games. Nothing produces 1,268 or 1,267, and the rubric does not
define "successful two-worker". This is the one number that is neither verifiable nor
excusable as host-only, because the top20 side data *is* in the package.

# 2. Corrections

### Correction 1 — the stated decoder boundary does not reproduce its own cohort

The report offers `second_train_turn <= 151` as the explicit key that makes the 28-game
cohort reproducible. **As written it yields 29**, and every downstream figure moves:
+62.79 → −54.55 instead of +64.89 → −57.29, 27/29 leading, 8 wins.

The boundary that reproduces all of the published figures is
`second_train_turn <= 151 AND roster_final >= 3`. The extra game is `897782434`, where the
opponent issued a second TRAIN at t30 that **never landed** (`train_count=2`,
`roster_final=2`).

This is not pedantry. The conjunct is load-bearing for the *mechanism*: a TRAIN that failed
did not create worker three, and the C1 trigger is specified on **units visible in public
state**, not TRAIN commands issued. Publishing the weaker predicate invites a re-derivation
that silently admits failed trains into the cohort.

**Fix:** state the boundary as `second_train_turn <= 151 AND roster_final >= 3`, and name
`897782434` as the excluded case.

### Correction 2 — "12 endgame conversion crops" is 11 under the report's own boundary

Our twelve PLANT commands in `897780884` are t245, 253, 254, 259, 259, 265, 265, 271, 274,
278, 282, 288. The t245 plant precedes the turn-250 rule the same section invokes ("After
turn 250 its PICK/PLANT candidates receive scores 7000/6000"). Eleven are endgame
conversions; twelve is the whole-game count. The "fells seven itself" figure should be
restated against whichever denominator is intended.

### Correction 3 — the rank 2 / rank 3 ordering rationale is inverted

The cross-review section demotes B3.14 below the removal-race census "because terminal bank
headroom is only +0.444 own points/game". But the removal-race census's own headroom is
**+0.033 conservative own points/game, or +0.216 optimistic margin/game** — smaller than
0.444 on either measure. As written, the stated reason for the demotion is an argument for
promotion.

The defensible argument is different and should replace it: **B3.14's 0.444 is a hard cap**
(99.76% of wood is already banked, so complete success cannot exceed it), whereas the
removal-race ceiling is a one-game lower bound with unknown recurrence and could be larger.
That is a real distinction — it is just not the one the report makes.

**Recommended order change.** I would still swap them, on the rubric's own tie-break
("cheaper decisive check, then current-cohort support"):

- B3.14's check is three replays, and its invariant and test already exist
  (`tests/test_tent_banker_commitment_candidate.py` is present);
- the removal-race check is a 153-game lineage census that **does not exist and must be
  built first**.

Either accept the swap or keep the order with the corrected rationale. What should not
survive is the current text, which justifies the order with a number that argues the
opposite.

### Correction 4 — the rank 2 pass gate is ambiguous in a way that decides the outcome

"Only if the frozen corpus-wide optimistic ceiling reaches 20 margin/current game … should a
source proposal exist."

- Read as **per cohort game** (÷153): the observed evidence is 0.216/game. Reaching 20/game
  needs ~3,060 total optimistic margin, i.e. roughly 93 games as extreme as the direct one,
  where 1 of 153 has been seen. The census is then pre-committed to fail and is a closure
  exercise, not a route to a change.
- Read as **per affected game**: the direct game's 33 already clears 20 on n=1, and the gate
  is nearly vacuous.

The two readings differ by a factor of ~150 and point opposite ways. **Fix:** state the
denominator explicitly before the census runs, otherwise its result is unfalsifiable in
whichever direction the reader prefers.

### Correction 5 — "immediate check" overstates rank 1's readiness

Requirement 4 of my mandate is whether every stated command is runnable now. Result:

| command | status |
|---|---|
| `python3 chatgpt_1/h3a_pressure_treatment_reconstruction.py --self-test` | **runnable now — I ran it: `self-test: ok`, exit 0** |
| `python3 -m pytest -q tests/test_h3a_pressure_treatment_reconstruction.py` | file present; not executable on my host (no pytest/pip). `PARTIAL` from me; the project host runs pytest |
| `python3 -m pytest -q tests/test_tent_banker_commitment_candidate.py` | file present; same caveat |
| rank-1 **value runner** — 6,144 paired tasks, C0/A1/C1 byte-equality prover | **does not exist**. No H3a value runner in `cgauto/` |
| rank-2 **153-game lineage census** | **does not exist**. No endgame-conversion census in `cgauto/` |

The report is explicit that rank 2 has "no source yet". Rank 1 reads as though freezing a
configuration is the remaining step before the value run, and it is not: the existing
commands are a *reconstruction self-test*, and the thing that would produce value evidence
still has to be written, including the non-trivial byte-equality prover. **Fix:** separate
"existing self-test" from "runner still to be implemented" in the rank-1 section, as the
mandate's requirement 4 asks.

# 3. Closure distinctness — all three ideas pass

- **Rank 1 (H3a).** `docs/CONSTRAINTS.md:512` requires that any H3a preflight "freeze
  conditioned, identical always-on, and unchanged-control arms and show the conditioning
  itself is load-bearing". The C0/A1/C1 design is exactly that. The H3a-reconstruction
  constraint adds "do not create a runner/panel or cite value without a separate conditioned
  vs identical-always-on vs unchanged protocol" — the report proposes precisely that protocol
  and claims no value. **Distinct and compliant.** The scoring operation is held at the exact
  frozen `candidate.score += candidate.score` for tracked existing trees at ETA ≤6, so no
  multiplier or ETA retune is smuggled in.
- **Rank 2.** Narrower than B3.7 (no plant-pacing rule), D175a and D78/D85, as a
  pre-decision removal-race feasibility test only. The explicit prohibitions on tuning
  turn 250 and on generic plant-pacing/salvage are the right guards. **Distinct.**
- **Rank 3.** Backports an existing B3.14 invariant to three named incidents with explicit
  refusal to generalise to E2, B3.13, D176 or tree ordering. **Distinct.**

One observation, not a defect: the **currently live source is `b100_e6`**, which
`docs/CONSTRAINTS.md:538` records as "consumed and closed … +0.12 vs control at matched
count — below the frozen +0.5 rule". The report handles this correctly — "the active b100 bot
motivates this check but is not silently substituted as a fourth or retuned arm" — and that
restraint is worth preserving explicitly if anyone later proposes a fourth arm.

# 4. Causal language and thresholds

**Causal language is disciplined.** "Final roster is endogenous, so these are motivation and
coverage—not a causal effect and never the policy trigger" is the correct framing and it is
stated where it matters. The C1 trigger uses only public state, never final roster, TRAIN
futures, identity or score-behind state — I checked this against the trigger description and
it is consistent with the cohort definition once correction 1 is applied (initial roster is
1, so "at least three opponent units" is exactly two landed TRAINs).

**Thresholds.** The frozen H3a gates (C1−C0 ≥ +2 with clustered lower bound > 0; C1−A1 ≥ +5
with lower bound > 0; both seats nonnegative; ≥6/8 families nonnegative; worst family ≥ −1;
no worse catastrophes; negative-margin mass ≤ 1.05× C0; own-score loss ≤ 1) are coherent and
appropriately conservative, and the C1−A1 ≥ +5 arm is what makes conditioning falsifiable
rather than assumed. "A pass authorizes confirmation, not Arena submission" is correct and
should stay.

**One caution on projected headroom.** Ranks 2 and 3 have measured ceilings of ≤0.444 own
points per game, well inside the ±0.5 arena noise band that `docs/STATE.md` §3 sets. Even
complete success on either is unmeasurable on the ladder. They are worth running as
*closures* — cheaply, to stop the questions recurring — and the report should say that
plainly so nobody reads them as value routes.

# 5. Leakage check — clean

No sealed map ID (`9844200–9844215`, `9852000–063`), no token, secret, password, session
handle, cookie, or private host path appears in the final report. Game IDs are open-cohort
IDs in the 897,7xx,xxx range and the seven sealed-tagged games are excluded from the package
by construction.

# 6. Corrected ranking

| Rank | Idea | Change | Basis |
|---:|---|---|---|
| 1 | H3a conditioned pressure — three-arm value protocol | **unchanged** | strongest evidence in the corpus, reproduces exactly, closure-compliant, falsifiable design |
| 2 | B3.14 sticky-bank three-incident closeout | **promoted from 3** | cheapest decisive check; invariant and test already exist; higher measured headroom (0.444 vs 0.216) |
| 3 | Endgame conversion removal-race census | **demoted from 2** | n=1, replay-conditioned, census must be built first, and its pass gate is ambiguous until correction 4 is applied |

Ranks 2 and 3 are closures, not value routes; both sit inside the arena noise band.

# 7. Stop / pass recommendations

- **Rank 1 — PASS to protocol freeze**, after corrections 1 and 5. Do not call the value
  runner an immediate check until it exists. Stop conditions as frozen are adequate.
- **Rank 2 (B3.14) — PASS to the three replays.** Cheap, tooling exists, hard-capped upside;
  run it to close, and hold the no-generalisation guard.
- **Rank 3 (removal race) — HOLD pending correction 4.** Do not start the 153-game census
  until the gate's denominator is stated. As written, one reading makes it unfalsifiable and
  the other makes it pre-committed to fail.
- **Unchanged and endorsed:** B3.11 stays measurement-only; generic WAIT cleanup stays
  rejected; `897781203`'s 106-for-106 PLANT contention must never be "cleaned up".

# 8. Scope statement

Review only. I produced no original track-2 analysis, edited no bot source, frozen artifact,
shared doc or peer namespace, ran no simulation, candidate, build, TestSession or Arena
action, and touched no raw cache or sealed data. Every figure above is from the committed
package or from files already tracked in the repository.
