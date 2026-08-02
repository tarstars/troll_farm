# Final ranked ideas — new games and top-player benchmark

Task: `20260802-top-player-new-games-multiagent-analysis`  
Integrator: `local_codex_1`  
Frozen evidence commit: `73718b3fdf9f2dc13359e17cb0ce002f95ea559e`  
Current bot: agent/submission `6589709`/`41079653`, source SHA `6f992a5a…`

## Result

There is one intervention worth testing now, two cheap audits worth closing in order, and
no evidence for another opening, generic WAIT cleanup, worker-training tweak, or resource
graft.

| Rank | Idea | Decision now | Confidence | Value status |
|---:|---|---|---|---|
| 1 | H3a: pressure only after visible opponent worker 3 | Freeze and run the exact three-arm value protocol | Medium that the test is worth its cost | Causal value unknown |
| 2 | Endgame conversion removal-race precheck | Run a 153-game provenance census; no source yet | Medium on the exact defect, low on recurrence | One-game conservative +5 own; optimistic +33 margin |
| 3 | B3.14 current-source sticky-bank recurrence | Replay only three recurrent runs, then stop or run a tiny pair test | Low | Missing-bank ceiling only +0.444 own points/game |

The ordering reflects intervention readiness and whole-corpus headroom, not narrative
salience. Seven sealed-tagged games were excluded. The only direct current-vs-top20 game is
`897780884`; the 2,684 top20-source games are benchmark context.

## 1. H3a — opponent-worker-pressure-conditioned existing-tree priority

### Why it ranks first

Opponents finish with at least three workers in 46/153 current games, across 31 identities
and both seats. Those games are 16W/30L, mean margin −28.91; the 107 others are
79W/2T/26L, +46.41. The difference is −75.32, game-bootstrap 95% interval
[−109.24,−42.28]. An identity-cluster sensitivity remains directional at approximately
[−115.1,−39.4]; only 2/15 repeated-identity contrasts are positive.

Temporal order is compatible with the mechanism. Among 96 full games, 28 opponents create
worker three by the turn-150 curve boundary. The resident leads at t150 in 26/28, but wins
only 7/28 and converts 19 early leads into losses. Mean margin falls from +64.89 at t150 to
−57.29 terminal. The other 68 games move from +37.19 to +55.49. Both seats show the same
direction. Final roster is endogenous, so these are motivation and coverage—not a causal
effect and never the policy trigger.

The direct Astrobytes game shows the same shape: resident margin +112 at t150, approximately
flat at t250, then −70 terminal after Astrobytes creates workers three/four at t56/t105.
The resident's own production does not collapse; the opponent accelerates.

### Exact seam and immediate check

Use the already reconstructed Phase-21 operation on tracked opponent-created existing trees
at ETA≤6: `candidate.score += candidate.score`. C1 arms permanently on the first live
resident decision whose public state contains at least three opponent units. It never uses
future TRAIN, final roster, identity, score-behind state, or a new threshold.

The mandatory arms remain:

1. C0: stable fallback `a8eb3b2b…`, treatment never active;
2. A1: exact archived treatment `083107f5…`, always active under its original eligibility;
3. C1: the identical treatment, inactive before visible worker three and sticky thereafter.

The active b100 bot motivates this check but is not silently substituted as a fourth or
retuned arm. Before the value run, these existing commands must pass:

```bash
python3 chatgpt_1/h3a_pressure_treatment_reconstruction.py --self-test
python3 -m pytest -q tests/test_h3a_pressure_treatment_reconstruction.py
```

Then freeze the existing proposal's development configuration: 128 fresh unsealed official
map roots × both seats × eight standing families × C0/A1/C1 = 6,144 paired tasks. The
task-private runner must prove C1 byte-equals C0 before live worker three and byte-equals A1
in treatment eligibility/scoring after it.

### Pass and stop

Pass only if every frozen H3a gate holds: C1−C0 ≥+2 mean paired margin and clustered lower
bound >0; C1−A1 ≥+5 and lower bound >0; both seats nonnegative; ≥6/8 families nonnegative;
worst family ≥−1; no worse catastrophes; negative-margin mass ≤1.05× C0; own score loss no
worse than one. Stop on integrity failure, insufficient activation, C1≈A1, failure versus
C0, or any seat/family/tail failure. A pass authorizes confirmation, not Arena submission.

This is distinct from the closed unconditional bonus/distance/focus grids only because the
unchanged and identical-always-on comparators make conditioning itself falsifiable.

## 2. Endgame conversion removal-race precheck

### Exact new evidence

In `897780884`, the resident creates 12 endgame conversion crops. It fells seven itself.
Astrobytes fells all five resident APPLE conversions planted at t271, 274, 278, 282 and 288,
capturing seven wood at t275, 279, 285, 289 and 294. Astrobytes harvests zero fruit from
resident-created crops; its 121 harvested fruit comprise 79 from initial trees and 42 from
its own crops. The defect is tree capture, not enemy harvest of our fruit.

`YamoBot::endgame_candidates` prices resident travel, planting, chopping and return, but no
enemy arrival/removal race. After turn 250 its PICK/PLANT candidates receive scores
7000/6000 and dominate ordinary work. A pre-PICK KEEP_BANK choice would conservatively
retain five own apple points. Denying the observed seven enemy wood adds 28 optimistic
margin, but is replay-conditioned because the enemy may redirect. With recurrence unknown,
the one-game evidence is only +0.033 conservative own points/game or +0.216 optimistic
margin/game over the 153-game cohort.

### Immediate check before source

Run a host-only, read-only lineage census over the 153 exact open IDs from the shared CSV;
do not discover files by scanning directories. For every successful post-t250 resident
conversion PLANT, join:

- the pre-PICK public state and outcome-blind opponent removal ETA/power;
- seed value removed from the resident bank;
- creator, first feller, death turn and actual wood recipient;
- a legal KEEP_BANK/alternate-work action at the same decision;
- resident-won crops that the proposed predicate would falsely veto.

Only if the frozen corpus-wide optimistic ceiling reaches 20 margin/current game across
both seats and multiple exact identities should a source proposal exist. Then reconstruct
the five Astrobytes pre-PICK boundaries and first validate exact A/A. A treatment must run
the live opponent after divergence; recorded post-divergence commands are invalid.

Pass the boundary only if every predicted losing conversion keeps its fruit banked, no
resident-won conversion is vetoed, and paired terminal delta is positive. Stop if the
predicate is nonrecurrent, the optimistic ceiling is below 20/game, A/A fails, or a won crop
is suppressed. Do not tune turn 250 or create a generic plant-pacing/salvage rule. This is
narrower than B3.7, D175a and D78/D85 only as a predecision removal-race feasibility test.

## 3. B3.14 sticky productive banking — three-incident closeout

The 153-game exact decode finds 293 bank-progress→diversion transitions in 70 games, but
those transitions are not automatically bugs. The narrow recurrent symptom is only eight
multi-turn full-WOOD WAIT runs in three games:

- `897781302`, t189–195;
- `897781012`, t49–54 and t276–280;
- `897781689`, t223–228.

Overall banking is already 7,003/7,020 collected wood (99.76%). Only 17 wood remains
unbanked, an own-score ceiling of `17×4/153 = 0.444` per game; the 40 full-WOOD WAIT turns
are 0.096% of 41,506 decoded turns. This cannot support broad routing or cleanup.

Immediate check: reconstruct only those three exact runs on the current source. Backport the
existing B3.14 invariant in a task-private candidate: after a full-WOOD worker has selected
a bank-progress move, keep its current bank commitment until DROP or empty cargo. Re-run:

```bash
python3 -m pytest -q tests/test_tent_banker_commitment_candidate.py
```

and add current-source fixtures that prove byte-identical commands before first bank
progress and outside the sticky interval. In live-opponent re-execution, pass only if each
incident reaches an earlier DROP and terminal own score increases without lost suppression
or worse tail. Stop if moves merely rearrange, deposit/terminal bank is unchanged, command
changes escape the interval, or any tail worsens. No generalization to E2 routing, B3.13
coordination, D176 oscillation, or tree ordering is allowed.

## Cross-review disposition

Three independent read-only tracks completed in parallel: quantitative matchup, economy
and action flow, and exact direct-game postmortem. The completed ring was
economy→matchup, matchup→direct, direct→economy.

- All three accepted H3a at rank 1, with the final-roster/endogeneity qualification and
  mandatory C0/A1/C1 equality gates.
- The direct postmortem initially ranked endgame removal race first. Review demoted it to
  a recurrence precheck because n=1 and the +33 ceiling is replay-conditioned.
- Economy ranked B3.14 second. Review demoted it below the removal-race census because
  terminal bank headroom is only +0.444 own points/game.
- One reviewer retained primitive-only delineate L1 at rank 2. The integrator rejects that
  placement: the shared rubric and constraints call L1 a gated programme, not an immediate
  narrow edit. It remains a legitimate longer-term route.
- Arithmetic corrections adopted: full-game opponent scaling is 36/96, not 37/96;
  successful-two-worker top20 sides are 1,268, not 1,267. The turn-150 temporal cohort is
  28 only under the explicit decoder boundary `second_train_turn <= 151`.

The repository-protocol assignees `claude_1` and `chatgpt_1` did not acknowledge the
corrected fetchable assignment within the 15-minute lease. Their unstarted write sets were
formally taken over at `6477b60`; this report does not attribute work to them.

## Rejected or measurement-only

- B3.11 relative fruit control remains a provenance census only. Aggregate APPLE harvest
  (1,263 units in 27/153 games, 56.2% in five games) is concentrated and post-outcome; it is
  removed from the improvement ranking.
- The direct game's WAITs are productive t4–8 ripening waits or post-bank terminal
  exhaustion. Generic WAIT cleanup is rejected.
- There are zero recorded failed effects, no exact B3.15 on-tree-owner recurrence, and no
  broad banking defect.
- Generic TRAIN retiming, funding ladders, worker-three grafts, farming/mining/harvest
  grafts, crop bonus/focus retuning, collision/oscillation rewrites, and body blocking
  remain closed.
- The t250→251 reversal and one loaded-carrier detour are incident-census observations, not
  ranked edits. D176/B3.1/E2/B3.13 bind unless recurrence proves a new lifecycle invariant.
- Game `897781203` is a safety regression case: 106 apparently wasted resident PLANTs
  reject 106 rival PLANTs. Never “clean it up” without preserving that action contention.
