# progress: 20260802-top-player-final-independent-review

- From: claude_1
- To: local_codex_1
- CC: chatgpt_1, user
- Created UTC: 2026-08-02T12:32:00Z
- Task: 20260802-top-player-final-independent-review
- Branch: agent/claude_1
- Requires acknowledgement: no
- Platform mutation performed: no

## Reproduction pass complete on the committed package

Everything below was recomputed from `sides.csv`, the manifest and the one sanitized
replay/trajectory. No host cache, no credentials, no sealed read.

**The foundation is sound.** Cohort counts, outcome/seat accounting and the whole of rank 1's
association arithmetic reproduce to the digit:

| claim | mine | status |
|---|---|---|
| 5,672 side rows; 153 current; 2,684 top20-source; 2,836 union | identical | `VERIFIED` |
| current record 95W/2T/56L, seats 68/85 | identical | `VERIFIED` |
| opponent ≥3 workers in 46/153, 31 identities, both seats | identical | `VERIFIED` |
| that group 16W/30L, mean −28.91; other 107 79W/2T/26L, +46.41; difference −75.32 | identical | `VERIFIED` |
| game-bootstrap 95% CI [−109.24,−42.28] | my 20k resample [−109.57,−41.87] | `VERIFIED` (within resampling noise) |
| full-game opponent scaling 36/96 | identical | `VERIFIED` |
| t150 cohort: 26/28 lead, 7/28 win, 19 lead→loss, +64.89→−57.29; other 68 +37.19→+55.49 | identical | `VERIFIED`, with the caveat below |
| B3.11 apple 1,263 units in 27/153, 56.2% in five games | identical | `VERIFIED` |
| B3.14 banking 7,003/7,020, 17 unbanked, ceiling 17×4/153 = 0.444 | identical | `VERIFIED` |
| `897781203`: 106 wasted resident PLANTs reject 106 rival PLANTs | 119−13 = 106 ours, 130−24 = 106 theirs | `VERIFIED`, and the symmetry is exact |
| five APPLE conversions at t271, 274, 278, 282, 288 | identical | `VERIFIED` |

That is a strong result and I want it on the record before the defects: the rank-1 case does
not rest on anything I could not check.

## Three concrete defects found so far

**1. The stated decoder boundary does not reproduce its own cohort.** The report says the
turn-150 cohort "is 28 only under the explicit decoder boundary `second_train_turn <= 151`".
As written that yields **29**, and every downstream figure shifts (+62.79/−54.55 instead of
+64.89/−57.29). The boundary that reproduces all of them is
`second_train_turn <= 151 AND roster_final >= 3`. The extra game is `897782434`, where the
opponent issued a second TRAIN at t30 that **never landed** (`train_count=2`,
`roster_final=2`). This is a documentation defect, not an arithmetic one — but it is the one
line the report offers as the reproducibility key for a rank-1 statistic, and the conjunct is
load-bearing for the mechanism too: a TRAIN that failed did not create worker three.

**2. "12 endgame conversion crops" is 11 under the report's own t250 boundary.** Our twelve
PLANT commands in `897780884` are t245, 253, 254, 259, 259, 265, 265, 271, 274, 278, 282, 288.
The t245 one precedes the turn-250 endgame rule the same section invokes
("After turn 250 its PICK/PLANT candidates receive scores 7000/6000"). Eleven are endgame
crops; twelve is the whole-game count.

**3. The 1,268 figure is not reproducible.** The review adopted "successful-two-worker top20
sides are 1,268, not 1,267". Against the 2,853 top20 side rows I get **1,330** under every
natural reading — `roster_final>=3`, `effect_trained>=2`, `train_count>=2`,
`second_train_turn` non-null, and their conjunctions — and 1,256 if restricted to full games.
Nothing yields 1,268 or 1,267. The rubric does not define "successful two-worker". Since this
number was specifically corrected in review, please state the predicate; I cannot mark it
`VERIFIED` and will not mark it `HOST_ONLY` either, because the top20 side data *is* in the
package.

## Reproducibility boundary, as instructed

`HOST_ONLY`, and correctly so — the package contains exactly one trajectory
(`897780884`). The B3.14 turn-level census — 293 bank-progress→diversion transitions in 70
games, eight multi-turn full-WOOD WAIT runs, 41,506 decoded turns, and the three named
incidents `897781302` t189–195, `897781012` t49–54 / t276–280, `897781689` t223–228 — has
**no trajectory in Git for any of those three games**. I can confirm they exist in the cohort
and I can confirm the 7,003/7,020 aggregate; I cannot confirm a single turn-level statement.
The report does not overclaim here, and rank 3 is already gated as replay-only, so this is a
boundary note rather than a defect.

Rank 2's attribution — "Astrobytes fells all five", "capturing seven wood at t275/279/285/
289/294", "harvests zero fruit from resident-created crops", "121 = 79 initial + 42 own" — is
`PARTIAL`. Opponent CHOPs do occur at 275, 279, 285 and 294 (and at 273, 274, 276, 277, 278,
283–289 besides), but resolving *which tree* each CHOP felled and who received the wood needs
the frame/view data, not the command stream. The plant side is exact; the capture side I can
corroborate as consistent, not verify.

## Runnable-now audit, partial

- `chatgpt_1/h3a_pressure_treatment_reconstruction.py --self-test` — **present and I ran it:
  `self-test: ok`, exit 0.** Genuinely runnable now.
- `tests/test_h3a_pressure_treatment_reconstruction.py` and
  `tests/test_tent_banker_commitment_candidate.py` — both present; I cannot execute them
  (no `pytest`/`pip` on this host), so `PARTIAL` from me, and you have already shown the
  project host runs pytest fine.
- The rank-1 **value runner** (6,144 paired tasks, C0/A1/C1 byte-equality prover) and the
  rank-2 **153-game lineage census** do **not exist**. `cgauto/` has no H3a value runner and
  no endgame-conversion census. Both ranked "immediate checks" therefore require
  implementation first. The report is honest that rank 2 has "no source yet"; rank 1 reads as
  though freezing a configuration is the remaining step, and it is not.

## Leakage check

Clean. No sealed map ID (`9844200–9844215`, `9852000–063`), token, secret, session handle,
cookie or private host path appears in the final report.

## Remaining before handoff

Closure-distinctness for all three ideas against the cited families, threshold and
causal-language challenge, projected-headroom arithmetic, and the corrected order and verdict.
Next progress or the handoff itself inside the lease.
