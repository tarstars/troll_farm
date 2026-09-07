# RESULT — frozen chopup: the rule does fire in the field, and still does not win

**Verdict: PARK.** The prospective gate (whole-panel paired W+0.5D strictly
positive AND zero candidate issues) fails on both clauses.

**Field activation (stored screen games, descriptive).** 12 archived games, both
arms on identical recorded states. The parent binary reproduces the recorded
official stream exactly on all 6 policy-flat games (0 mismatches). The candidate
diverges in **2/12 games (1 of 6 distinct maps)**: tonigineer seat 1, turn 8,
parent `TRAIN 2 2 0 2`+`MOVE`, candidate `MINE 1` — a genuinely deferred first
hire, not a no-op. Instrumented rejections (stderr only; stdout identical to the
frozen candidate 12/12, `COMMAND_NEUTRAL_ALL=True`): 4/6 maps
`cap_or_infinite_eta` (parent already at chop cap 3, eta 2/4/12/12); 1/6
`eta_window` (chop 1→2, up_eta 36 > allowed 15); 1/6 **ACCEPT** (chop 2→3,
base_eta 6→16, felling 90→62, extra_delay 10). "Unreachable" was an artefact of
8 maps, not a property of the rule.

**Broader sample.** 24 maps 426092000..023 (verified unconsumed 01:49Z), 2 seats,
same 12 adaptive opponents, 576 pairs, `ALLOW_ANY_MAP_SEED=1`, 869.5 s.
Baseline 519/14/43 pts **526.0**, own 218.36 opp 102.95 margin 115.41, issues 2,
crit 0. Candidate 518/15/43 pts **525.5**, own 219.83 opp 103.28 margin 116.55,
issues 2, crit 0. **Delta -0.5.** Own +1.47, margin +1.14, t100 +0.15, t200
+0.63. Per-opponent dpts 0.0 except `resident` **-0.5**. Activation 48/576 pairs
(maps ...004, ...010; both seats, all 12 opponents); **all 48 spec changes are
chop +1, movement/carry/harvest 0**; train turn moved in all 48. Outcome changes
3, all vs `resident`: W→L, L→W, W→D. Map-cluster bootstrap **[-3.0, +1.5]**.

**Frozen hashes (unchanged, `hashes.txt`).** `_a.rs` 7a5722e4; `_a.min.rs`
d40ed644; parent 95ee691e; modules aa9c56c4/526cd9cc; `bot.rs` 44e3dace;
`submission.rs` 7f61a6cd; panel binary c30f0e25. No repository file changed.

**Tests.** No unit tests this batch (run artifacts only). Field replay 12/12;
neutrality 12/12; panel 576/576, exit 0.

**Evidence** (`claude-runs/20260907T014717Z-4021423-1/`): `PLAN.md` (frozen
01:52Z, pre-launch), `PROGRESS.md`, `field-activation.json`, `field-reasons.json`,
`panel.tsv`, `summary.txt`, `activation.txt`, `hashes.txt`, `panel.log`.

**Limitations.** Recorded field states are valid only to the first divergence — no
adaptive counterfactual. Both candidate issues are `move_blocked:1` on 426092016,
a zero-divergence map identical in both arms, inherited from the parent; counted,
not excused. Two maps carry the whole signal. Local proxy pool; no rank claim.
No certification (gate negative).

**Next action.** Check the losing `resident` pair on 426092004 at its turn-2
divergence: own score rose 39.2 there yet the pair flipped W→L, so ask whether
the deferred hire buys score while losing tempo.
