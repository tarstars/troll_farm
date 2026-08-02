# Handoff: 20260802-top-player-final-independent-review

- From: claude_1
- To: local_codex_1
- CC: chatgpt_1, user
- Created UTC: 2026-08-02T12:34:00Z
- Task: 20260802-top-player-final-independent-review
- Branch: agent/claude_1
- Handoff commit: see the pushed head of `agent/claude_1`; this message is its child
- Base commit: 228dc1d11a0f9066b737063575832cf4691300b2 (my acknowledgement)
- Requires acknowledgement: yes
- Platform mutation performed: **no**

## Verdict: `ACCEPT_WITH_CORRECTIONS`

Report: `claude_1/top-player-new-games-final-independent-review-2026-08-02.md`,
SHA-256 `78df9d640311cd7a84186e3026be1e4d132ec8ecac213cc8b6a89f7fa84b30dc`, 251 lines.

Reviewed subject `d86016da…`, which matched the task record's hash exactly before I started.

## The headline

**Rank 1 survives intact.** Every statistic underpinning it reproduces to the digit from the
committed package — 46/153, 16W/30L, −28.91 against +46.41, difference −75.32, the bootstrap
interval, 36/96, and the full t150 trajectory. The closure reasoning is correct against
`docs/CONSTRAINTS.md:512` and the causal language is disciplined where it matters. I did not
find a reason to move it.

I also cross-checked the arm identities against the Arena submission registry, independently
of your report: A1 `083107f5…` is submission `41012867`/agent `6560350`, rejected at the
63-game gate at 16.51 against a 24.28 control, −7.77. Your premise that A1 is an
already-tested, already-failed always-on treatment holds at the hash level.

## Five corrections

1. **The stated decoder boundary does not reproduce its own cohort.**
   `second_train_turn <= 151` yields **29**, not 28, and shifts every downstream figure. The
   predicate that reproduces all of them is `second_train_turn <= 151 AND roster_final >= 3`;
   the extra game is `897782434`, whose second TRAIN at t30 never landed. The conjunct is
   load-bearing for the mechanism, not just the count — the C1 trigger reads *visible units*,
   not TRAIN commands issued.
2. **"12 endgame conversion crops" is 11** under the report's own turn-250 boundary; the t245
   plant precedes it.
3. **The rank 2/3 ordering rationale is inverted.** B3.14 is demoted "because terminal bank
   headroom is only +0.444 own points/game", but the removal-race census's headroom is
   +0.033 own / +0.216 margin per game — smaller on either measure. The defensible argument
   is that 0.444 is a *hard cap* while the removal-race ceiling is an unknown-recurrence lower
   bound. I recommend swapping them on the rubric's own tie-break, since B3.14's check is
   three replays with an existing test and the census must be built first.
4. **The rank-2 pass gate is ambiguous by a factor of ~150.** "20 margin/current game" read
   per cohort game needs ~93 games as extreme as the one observed and is pre-committed to
   fail; read per affected game, the direct game's 33 already clears it on n=1. State the
   denominator before the census runs.
5. **"Immediate check" overstates rank 1's readiness.** The self-test is genuinely runnable —
   I ran `chatgpt_1/h3a_pressure_treatment_reconstruction.py --self-test`, `self-test: ok`,
   exit 0. But the **value runner does not exist** (no H3a runner in `cgauto/`), including
   the non-trivial C0/A1/C1 byte-equality prover, and neither does the 153-game census.

## One number I could not verify and could not excuse

"Successful-two-worker top20 sides are 1,268, not 1,267." Against the 2,853 top20 side rows I
get **1,330** under every predicate I can construct — `roster_final>=3`, `effect_trained>=2`,
`train_count>=2`, `second_train_turn` non-null, and conjunctions — and 1,256 restricted to
full games. The rubric does not define "successful two-worker". This one is neither
`VERIFIED` nor fairly `HOST_ONLY`, because the data is in the package. Please state the
predicate.

## Reproducibility boundary, per requirement 2

I did not pretend the B3.14 turn-level census is independently reproducible. It is not: the
package holds exactly one trajectory (`897780884`) and none of the three named incident games
has one. I marked the whole turn-level layer `HOST_ONLY` and verified only the 7,003/7,020
aggregate from the CSV. Rank 2's capture attribution is `PARTIAL` — opponent CHOPs do occur
at the claimed turns, but resolving which tree fell and who took the wood needs frame state I
do not have.

## Corrected ranking

1. H3a conditioned pressure — unchanged.
2. B3.14 sticky-bank three-incident closeout — promoted.
3. Endgame conversion removal-race census — demoted, and **HOLD** until correction 4 lands.

Ranks 2 and 3 are closures, not value routes: both sit inside the ±0.5 arena noise band that
`docs/STATE.md` §3 sets, so even complete success is unmeasurable on the ladder. Worth running
cheaply to stop the questions recurring; not worth expecting anything from.

## Leakage

Clean — no sealed map ID, token, secret, session handle or private host path in the report.

## Scope

Review only. No original track-2 analysis, no source or shared-doc edit, no peer namespace,
no simulation, candidate, build, TestSession, Arena action, raw cache or sealed data. Write
set was exactly the three paths in the task record.

## Requested action

Review and integrate. Corrections 1 and 4 are the two I would not ship without: the first
because it is offered as the reproducibility key for a rank-1 statistic and does not work,
the second because it decides whether the rank-2 census can produce a result at all. You
alone apply corrections to your own files; I have changed nothing outside my namespace.
