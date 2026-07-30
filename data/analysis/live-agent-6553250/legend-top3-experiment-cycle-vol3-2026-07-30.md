# Legend score-25.40 experiment cycle — volume 3 (opened 2026-07-30)

Objective and live state: `docs/STATE.md`. Closed branches: `docs/CONSTRAINTS.md` —
check before proposing. Volume 2
(`legend-top3-experiment-cycle-vol2-2026-07-23.md`) is frozen after A2-1.

Per-experiment obligations: one entry here; a CONSTRAINTS bullet for anything closed; a
STATE.md §4 update. The first session ending with this file over 100 KB freezes it and
opens volume 4.

<!-- entries below -->

## M1 — rating-system dynamics: broad source support, no recovered update rule

**Question.** Can the seven stored D61p snapshots recover the platform's score update rule
and price a +1 rating move in wins?

**Frozen method.** Exact-agent leaderboard intervals plus source-agent game-score epochs;
manifest and raw-response hash verification; bracketed outcome-completeness; prior- and
next-epoch conventions; affine, net-win, and bounded Elo-like candidates; leave-one-agent-
out validation. Protocol:
`docs/m1-rating-system-dynamics-protocol-v2-2026-07-30.md`.

**Evidence.** 8,014 raw games / 2,564,403,129 bytes hash-verify. The seven collections
contain six unique leaderboard responses. All 2,549 score changes coincide with advancing
`updateTime`. Raw `agents[].score` aligns with the rounded leaderboard in 236/243
comparisons and stays constant across 229 mixed-outcome batches. Of 329 internal score
transitions, 307 (93.31%) are outcome-complete across 45 agents, covering 2,147 wins and
2,511 losses.

**Result.** Source evidence clears the pre-model FULL threshold, but rule recovery fails.
The best held-agent Elo-like model has MAE 0.477313, median absolute error 0.284044, versus
0.478583 for predicting zero change — only 0.27% improvement, against gates of MAE ≤0.05,
median ≤0.02, and ≥50% baseline improvement. Affine and net-win rules are worse. The
next-epoch convention and exclusion of the July 21 snapshot also fail.

**Verdict: PARTIAL / DESCRIPTIVE_ONLY.** No wins-per-+1 number is reported. Keep candidate
decisions in terminal-margin units. Reopen only with exact recomputation membership and
documented pre/post score, or the platform formula. Resident and Arena untouched.

Evidence:
`data/analysis/live-agent-6553250/m1-rating-system-dynamics-result-2026-07-30.md`;
machine bundle `local_codex_1/m1-rating-system-dynamics/`.
