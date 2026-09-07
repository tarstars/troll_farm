# RESULT — chopup: one conditional +1 chop on the parent's first hire

**Verdict: PARK — correct and runnable, but zero activation.** 192 pairs: the
candidate command stream is identical to the baseline in **192/192**, delta
**+0.0**. The frozen gate needs a positive delta, so it fails (no regression
either). Both arms 167/6/19, pts 170.0, own 231.35, opp 116.92, margin 114.43,
issues 1, crit 0; every per-opponent and per-map delta +0.0. Spec changes:
movement **0**, carry **0**, chop **0**, train-turn **0**.

**Why.** 96/192 pairs already buy chop 3 — the cap — so the rule is
structurally ineligible there. Elsewhere `opening_key` is monotone in the raw
stat sum, so any chop+1 whose `collection_eta` fits `train_horizon` 15 the
parent *already* bought. The rule can only fire for eta ∈ (15,
min(chosen_eta+15, deadline 35−turn)], and the `n+chop²` iron bill (2→5→10)
priced at one round trip per ore never lands there. Not wrong — unreachable.

**Changed files (all new, sha256).** `claude_candidate_chopup.py` b132a5c2;
`test_claude_candidate_chopup.rs` f587a512; `_a.rs` 7a5722e4; `_a_module.rs`
aa9c56c4; `_a.pruned.rs` f3750e26; `_a.min.rs` d40ed644 (**91,043** UTF-16,
guarded `DEAD_REGIONS` pruning); `_a_tests.rs` b5f7ce42; `_control_module.rs`
526cd9cc (parent verbatim); `.mapping.json` 9003a294. Parent 95ee691e, `bot.rs`,
`submission.rs` unchanged.

**Tests.** rustc 1.90.0 `--test`: **20 passed, 0 failed**, 1 ignored — changed
hire (+1 chop, movement/carry/harvest frozen), real extra ore collected, exact
`training_cost` bill, referee-spawned stats, wood banked (candidate 28 wood/121
pts vs parent 24/105), remote-ore and no-iron and spent-horizon cases retaining
the parent, lost-resource deadline board, stable target, 0 issues/blocked moves.
Bench FIRST, nothing else running: 16 serial streams, 4,312 turns, max 27.0 ms,
over_50ms 0, exact readable-vs-compact equality (`packaging_different_games` 0).
Panel: 9947500..9947507, both seats, 12 opponents, `ALLOW_ANY_MAP_SEED=1`,
273.2 s; all 192 baseline command streams match gap 210944Z exactly.

**Evidence** (run dir 20260907T012354Z-3956144-1): `PLAN.md` (frozen 01:30Z),
`PROGRESS.md`, `tests.log`, `fixture-observations.txt`, `bench/report.json`,
`panel.tsv`, `summary.txt`, `activation.txt`, `hashes.txt`.

**Limitations.** With zero panel activation the fixture win (one synthetic
board) is the *only* superiority evidence and predicts nothing. The deadline
fixture trained in neither arm, so the `opening_fallback` revert is proven by
construction, not by a referee run. Which clause rejects each non-cap pair is
derived from the parent's code, not instrumented. Local pool; no ladder claim.

**Next action.** Do not re-tune these thresholds. Instrument one panel map to
record the eta actually quoted, and decide whether the blocker worth attacking
is `collection_eta` pricing every ore unit as a separate carry-1 round trip.
