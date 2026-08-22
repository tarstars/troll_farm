# Second-worker funding before tent denial

Date: 2026-07-31
Task: `20260731-second-troll-funding-before-denial`
Verdict: **confirmed post-planner precedence defect**

Exact game `897560637` is a valid 127–231
loss by resident `6585801` / `41071204`
against FRHT. All 300 turns decode with zero unknown updates, and the exact
live source reproduces 300/300 resident command lines with zero stderr.

At turn 1 a live BANANA is cardinally adjacent to the enemy tent. The opening planner
emits `MOVE 0 8 0`, but the later denial wrapper replaces it with
`MOVE 0 7 1`. It overwrites the active opening command on
18 decisions through turn 40
(`[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 29]`). The recorded bot does
not TRAIN until hard downgrade turn 35.

The fixed 40-game live slice contains 35 full games.
21 have cardinal activation by turn 34:
14 TRAIN at 35 and
7 earlier. In the other
14 games, zero TRAIN at 35 and
14 train earlier. This supports breadth, not a causal
Arena-value claim.

The successor preserves the opening planner command while own roster is below two and
the opening objective remains active. It preserves the inner command on every exact
overwritten decision and first diverges on turn
1. After worker two exists or the opening
is abandoned, denial resumes over the full eight-neighbor enemy-tent ring, including
diagonals.

Candidate `cgauto/submissions/candidate-agent6585801-second-funding-first-diagonal-denial-slim.min.rs`, 68893 bytes, SHA-256
`b8382910116bbfaeade378732508bf4281a7f4ee793ae8f14ae41992ece37af4`. Focused compiled boundaries and inherited regressions are
reported in the task manifest. This audit is mechanism evidence, not field qualification.
